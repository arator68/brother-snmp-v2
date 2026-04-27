import voluptuous as vol
import asyncio
import logging
import re

from homeassistant import config_entries

from .const import DOMAIN, CONF_HOST, CONF_COMMUNITY
from .snmp import snmp_get

_LOGGER = logging.getLogger(__name__)

# 🔥 OIDs
SERIAL_OID = "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.1.0"
INFO_OID = "1.3.6.1.4.1.2435.2.3.9.1.1.7.0"


# =========================
# PARSER
# =========================
def _extract_model(value):
    match = re.search(r"MDL:([^;]+)", value)
    return match.group(1) if match else None


def _extract_class(value):
    try:
        return value.split("CLS:")[1].split(";")[0].strip().lower()
    except Exception:
        return None

def parse_device_info(value: str) -> dict:
    """Parse Brother SNMP device info string."""

    if not value:
        return {}

    result = {}

    try:
        parts = value.split(";")

        for part in parts:
            if ":" not in part:
                continue

            key, val = part.split(":", 1)

            key = key.strip().upper()
            val = val.strip()

            if key == "MFG":
                result["manufacturer"] = val

            elif key == "MDL":
                result["model"] = val

            elif key == "CLS":
                result["class"] = val.lower()

    except Exception as err:
        # optional debug
        # _LOGGER.warning(f"Parser error: {err}")
        pass

    return result


# =========================
# CONFIG FLOW
# =========================
class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            community = user_input[CONF_COMMUNITY]

            try:
                # 🔥 SNMP Engine lokal
                from pysnmp.hlapi.v3arch.asyncio import SnmpEngine
                engine = SnmpEngine()

                # =========================
                # SERIAL holen
                # =========================
                serial = await asyncio.wait_for(
                    snmp_get(engine, host, community, SERIAL_OID),
                    timeout=5,
                )

                if not serial:
                    errors["base"] = "no_serial"
                else:
                    serial = serial.strip()

                    # =========================
                    # MODEL + CLASS holen
                    # =========================
                    info = await asyncio.wait_for(
                        snmp_get(engine, host, community, INFO_OID),
                        timeout=5,
                    )

                    model = None
                    device_class = None

                    if info:
                        parsed = parse_device_info(info_str)

                        model = parsed.get("model")
                        device_class = parsed.get("class")
                        
                        # 🔥 DEBUG HIER
                        _LOGGER.warning(f"PARSED CLASS: {device_class}")

                        _LOGGER.warning(
                            f"DEVICE INFO: model={model}, class={device_class}"
                        )

                    # =========================
                    # UNIQUE ID = SERIAL
                    # =========================
                    await self.async_set_unique_id(serial)
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"{model or 'Brother'} ({serial})",
                        data={
                            CONF_HOST: host,
                            CONF_COMMUNITY: community,
                            "serial": serial,
                            "model": model,
                            "device_class": device_class,
                        },
                    )

            except asyncio.TimeoutError:
                errors["base"] = "timeout"

            except Exception as err:
                _LOGGER.exception("Config flow error: %s", err)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_COMMUNITY, default="public"): str,
            }),
            errors=errors,
        )