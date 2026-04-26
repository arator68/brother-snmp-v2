from datetime import timedelta
import logging
import re

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .snmp import snmp_bulk
from .const import *

_LOGGER = logging.getLogger(__name__)


class BrotherCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, host, community):
        super().__init__(
            hass,
            _LOGGER,
            name="Brother SNMP",
            update_interval=timedelta(seconds=15),
        )
        self.host = host
        self.community = community

    async def _async_update_data(self):
        data = await snmp_bulk(
            self.host,
            self.community,
            [PAGE_OID, MODEL_OID, SERIAL_OID, FIRMWARE_OID, ROLLER_OID],
        )

        def clean(val):
            if not val:
                return None
            match = re.search(r'"(.+)"', val)
            return match.group(1) if match else val

        return {
            "online": data.get(PAGE_OID) is not None,
            "pages_total": int(data.get(PAGE_OID)) if data.get(PAGE_OID) else None,
            "model": clean(data.get(MODEL_OID)),
            "serial": clean(data.get(SERIAL_OID)),
            "firmware": clean(data.get(FIRMWARE_OID)),
            "roller": int(data.get(ROLLER_OID)) if data.get(ROLLER_OID) else None,
        }