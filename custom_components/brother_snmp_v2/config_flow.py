import voluptuous as vol
import asyncio
import re

from homeassistant import config_entries

from .snmp import snmp_get
from .const import DOMAIN, CONF_HOST, CONF_COMMUNITY, MODEL_OID, SERIAL_OID

TEST_OID = "1.3.6.1.2.1.1.1.0"


class BrotherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            host = user_input.get(CONF_HOST)
            community = user_input.get(CONF_COMMUNITY)

            if not host:
                errors["host"] = "invalid_host"
            else:
                try:
                    sysdescr = await asyncio.wait_for(
                        snmp_get(host, community, TEST_OID), timeout=5
                    )

                    if sysdescr is None:
                        errors["base"] = "cannot_connect"
                    else:
                        model_raw = await asyncio.wait_for(
                            snmp_get(host, community, MODEL_OID), timeout=5
                        )
                        serial = await asyncio.wait_for(
                            snmp_get(host, community, SERIAL_OID), timeout=5
                        )

                        if model_raw is None:
                            errors["base"] = "not_brother"
                        else:
                            match = re.search(r'"(.+)"', model_raw)
                            model = match.group(1) if match else model_raw

                            await self.async_set_unique_id(serial or host)
                            self._abort_if_unique_id_configured()

                            return self.async_create_entry(
                                title=f"{model} ({host})",
                                data={
                                    CONF_HOST: host,
                                    CONF_COMMUNITY: community,
                                    "model": model,
                                    "serial": serial,
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