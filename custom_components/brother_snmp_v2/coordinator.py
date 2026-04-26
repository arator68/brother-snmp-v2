import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .snmp import snmp_bulk
from .const import DEVICE_PROFILES

_LOGGER = logging.getLogger(__name__)


class BrotherCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, host, community, device_class):
        super().__init__(
            hass,
            _LOGGER,
            name="Brother SNMP",
            update_interval=timedelta(seconds=15),
        )
        self.host = host
        self.community = community
        self.device_class = device_class

        self.profile = DEVICE_PROFILES.get(device_class, DEVICE_PROFILES["DEFAULT"])

    async def _async_update_data(self):
        oids = [s["oid"] for s in self.profile["sensors"]]

        raw = await snmp_bulk(self.host, self.community, oids)

        data = {}
        for sensor in self.profile["sensors"]:
            val = raw.get(sensor["oid"])
            data[sensor["key"]] = int(val) if val and val.isdigit() else val

        return data