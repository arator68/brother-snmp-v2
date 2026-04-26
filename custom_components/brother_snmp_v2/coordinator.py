from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .snmp import snmp_bulk
from .const import PAGE_OID, ROLLER_OID


class BrotherCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, host, community):
        super().__init__(
            hass,
            logger=None,
            name="Brother SNMP",
            update_interval=timedelta(seconds=15),
        )
        self.host = host
        self.community = community

    async def _async_update_data(self):
        data = await snmp_bulk(
            self.host,
            self.community,
            [PAGE_OID, ROLLER_OID],
        )

        return {
            "pages": int(data.get(PAGE_OID)) if data.get(PAGE_OID) else None,
            "roller": int(data.get(ROLLER_OID)) if data.get(ROLLER_OID) else None,
        }