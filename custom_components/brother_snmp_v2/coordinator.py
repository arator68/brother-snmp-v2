import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .snmp import snmp_bulk, snmp_walk
from .mib_parser import load_mib
from .const import SCANNER_BASE_OID, KNOWN_OIDS

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

        self._last_walk = {}

        if device_class == "PRINTER":
            self.sensors = load_mib(
                "/config/custom_components/brother_snmp_v2/BROTHER-MIB.json"
            )
        else:
            self.sensors = []

    async def _async_update_data(self):
        data = {}

        # 🖨️ PRINTER
        if self.device_class == "PRINTER":
            oids = [s["oid"] for s in self.sensors]
            raw = await snmp_bulk(self.host, self.community, oids)

            for s in self.sensors:
                data[s["key"]] = raw.get(s["oid"])

        # 📄 SCANNER
        elif self.device_class == "SCANNER":
            walk = await snmp_walk(self.host, self.community, SCANNER_BASE_OID)
            data["walk"] = self._smart_filter(walk)

        return data

    # 🔥 SMART FILTER
    def _smart_filter(self, walk):
        filtered = {}

        for oid, value in walk.items():
            if value in (None, "", "0"):
                continue

            if not any(x in oid for x in ["5.5", "5.1", "5.2", "54"]):
                continue

            if oid in self._last_walk and self._last_walk[oid] == value:
                continue

            filtered[oid] = value

        self._last_walk = walk
        return filtered

    # 🔥 CLEAN NAMING
    def friendly_name(self, oid, value=None):

        # 1. Known OIDs
        if oid in KNOWN_OIDS:
            return KNOWN_OIDS[oid]

        # 2. Pattern Mapping
        if "5.5" in oid:
            return "Scan Counter"
        if "5.1" in oid:
            return "Roller Usage"
        if "5.2" in oid:
            return "Device Status"
        if "54" in oid:
            return "Scan Pages"

        # 3. Value based
        if isinstance(value, str):
            if "error" in value.lower():
                return "Error Status"
            if "ready" in value.lower():
                return "Device Ready"

        # 4. fallback
        return f"SNMP {oid.split('.')[-3:]}"