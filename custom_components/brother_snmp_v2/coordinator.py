import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .snmp import snmp_walk
from .const import SCANNER_BASE_OID, GOOD_SCANNER_OIDS

_LOGGER = logging.getLogger(__name__)


class BrotherCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, host, community, device_class):
        super().__init__(
            hass,
            _LOGGER,
            name="Brother SNMP Scanner",
            update_interval=timedelta(seconds=15),
        )

        self.host = host
        self.community = community

    async def _async_update_data(self):
        walk = await snmp_walk(self.host, self.community, SCANNER_BASE_OID)

        return {"walk": self._smart_filter(walk)}

    def _smart_filter(self, walk):
        filtered = {}

        for oid, value in walk.items():

            if value is None or value == "":
                continue

            oid_norm = oid.rstrip(".0")

            for good_oid, name in GOOD_SCANNER_OIDS.items():
                if oid_norm.startswith(good_oid):
                    filtered[oid] = self._convert(value)

        return filtered

    def _convert(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return str(value)

    def friendly_name(self, oid):
        oid_norm = oid.rstrip(".0")

        for good_oid, name in GOOD_SCANNER_OIDS.items():
            if oid_norm.startswith(good_oid):
                return name

        return None