import voluptuous as vol
import asyncio

from homeassistant import config_entries

from .const import DOMAIN, CONF_HOST, CONF_COMMUNITY
from .discovery import detect_device


class BrotherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                device = await asyncio.wait_for(
                    detect_device(
                        user_input[CONF_HOST],
                        user_input[CONF_COMMUNITY],
                    ),
                    timeout=5,
                )

                if not device:
                    errors["base"] = "not_brother"
                else:
                    await self.async_set_unique_id(user_input[CONF_HOST])
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"{device['model']} ({user_input[CONF_HOST]})",
                        data={
                            **user_input,
                            "device_class": device["device_class"],
                            "model": device["model"],
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