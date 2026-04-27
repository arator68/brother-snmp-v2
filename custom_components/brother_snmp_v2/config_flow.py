import voluptuous as vol
import asyncio
import logging

from homeassistant import config_entries

from .const import DOMAIN, CONF_HOST, CONF_COMMUNITY
from .snmp import snmp_get

_LOGGER = logging.getLogger(__name__)

# 🔥 DEINE SERIAL OID
SERIAL_OID = "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.1.0"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            community = user_input[CONF_COMMUNITY]

            try:
                # 🔥 Engine lokal erstellen (safe)
                from pysnmp.hlapi.v3arch.asyncio import SnmpEngine
                engine = SnmpEngine()

                # 🔥 SERIAL holen
                serial = await asyncio.wait_for(
                    snmp_get(engine, host, community, SERIAL_OID),
                    timeout=5,
                )

                if not serial:
                    errors["base"] = "no_serial"
                else:
                    serial = serial.strip()

                    # 🔥 UNIQUE ID = SERIAL
                    await self.async_set_unique_id(serial)
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"Brother ({serial})",
                        data={
                            CONF_HOST: host,
                            CONF_COMMUNITY: community,
                            "serial": serial,
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