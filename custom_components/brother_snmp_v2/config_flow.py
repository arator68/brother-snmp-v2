import voluptuous as vol
import asyncio
import re

from homeassistant import config_entries
from .snmp import snmp_get

DOMAIN = "brother_snmp_v2"

CONF_HOST = "host"
CONF_COMMUNITY = "community"

TEST_OID = "1.3.6.1.2.1.1.1.0"
MODEL_OID = "1.3.6.1.4.1.2435.2.4.3.99.3.1.6.1.2.1"


class BrotherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            community = user_input[CONF_COMMUNITY]

            try:
                # Verbindung prüfen
                sysdescr = await asyncio.wait_for(
                    snmp_get(host, community, TEST_OID), timeout=5
                )

                if sysdescr is None:
                    errors["base"] = "cannot_connect"
                else:
                    # Brother + Modell prüfen
                    model_raw = await asyncio.wait_for(
                        snmp_get(host, community, MODEL_OID), timeout=5
                    )

                    if model_raw is None:
                        errors["base"] = "not_brother"
                    else:
                        match = re.search(r'"(.+)"', model_raw)
                        model = match.group(1) if match else model_raw

                        return self.async_create_entry(
                            title=f"{model} ({host})",
                            data={
                                CONF_HOST: host,
                                CONF_COMMUNITY: community,
                                "model": model,
                            },
                        )

            except asyncio.TimeoutError:
                errors["base"] = "timeout"
            except Exception:
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_COMMUNITY, default="public"): str,
            }),
            errors=errors,
        )