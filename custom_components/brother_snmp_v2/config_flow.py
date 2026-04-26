import voluptuous as vol
import asyncio

from homeassistant import config_entries

from .snmp import snmp_get

DOMAIN = "brother_snmp_v2"

CONF_HOST = "host"
CONF_COMMUNITY = "community"

TEST_OID = "1.3.6.1.2.1.1.1.0"  # sysDescr
BROTHER_TEST_OID = "1.3.6.1.4.1.2435.2.4.3.99.3.1.6.1.2.1"  # MODEL


class BrotherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            community = user_input[CONF_COMMUNITY]

            try:
                # 🔹 1. Gerät erreichbar?
                sysdescr = await asyncio.wait_for(
                    snmp_get(host, community, TEST_OID),
                    timeout=5
                )

                if sysdescr is None:
                    errors["base"] = "cannot_connect"
                else:
                    # 🔹 2. Ist es ein Brother?
                    brother_check = await asyncio.wait_for(
                        snmp_get(host, community, BROTHER_TEST_OID),
                        timeout=5
                    )

                    if brother_check is None:
                        errors["base"] = "not_brother"
                    else:
                        return self.async_create_entry(
                            title=f"Brother ({host})",
                            data=user_input,
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