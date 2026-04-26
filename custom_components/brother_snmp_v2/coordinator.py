import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .snmp import snmp_bulk, snmp_walk
from .mib_parser import load_mib
from .const import SCANNER_BASE_OID

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
                "/config/custom_components/brother_snmp_v2/BROTHER-Printer-MIB.json"
            )
        else:
            self.sensors = []

    async def _async_update_data(self):
        data = {}

        # =========================
        # 🖨️ PRINTER
        # =========================
        if self.device_class == "PRINTER":
            oids = [s["oid"] for s in self.sensors]

            raw = await snmp_bulk(self.host, self.community, oids)

            for s in self.sensors:
                val = raw.get(s["oid"])
                data[s["key"]] = self._map_value(s["key"], val)

        # =========================
        # 📄 SCANNER (SMART WALK)
        # =========================
        elif self.device_class == "SCANNER":
            walk = await snmp_walk(self.host, self.community, SCANNER_BASE_OID)
            data["walk"] = self._smart_filter(walk)

        return data

    # =========================
    # 🧠 SMART FILTER
    # =========================
    def _smart_filter(self, walk):
        filtered = {}

        for oid, value in walk.items():

            # ❌ Müll raus
            if value in (None, "", "0"):
                continue

            if isinstance(value, str) and len(value) < 2:
                continue

            # 🔥 relevante OIDs
            if not any(x in oid for x in [
                "5.5",  # counters
                "5.1",  # roller
                "5.2",  # status
                "54",   # scan
            ]):
                continue

            # 🔥 nur Änderungen
            if oid in self._last_walk:
                if self._last_walk[oid] == value:
                    continue

            filtered[oid] = value

        self._last_walk = walk
        return filtered

    # =========================
    # 🧠 VALUE MAPPING
    # =========================
    def _map_value(self, key, value):
        if value is None:
            return None

        if "toner" in key:
            return {
                "0": "OK",
                "1": "LOW",
                "2": "MISSING",
                "3": "EMPTY",
            }.get(value, value)

        if "jam" in key:
            return {
                "0": "OK",
                "1": "TRAY",
                "2": "INSIDE",
                "3": "REAR",
                "4": "DUPLEX",
            }.get(value, value)

        return value

    # =========================
    # 🧠 FRIENDLY NAMES
    # =========================
    def friendly_name(self, oid):
        if "5.5" in oid:
            return "Counter"
        if "5.1" in oid:
            return "Roller"
        if "5.2" in oid:
            return "Status"
        if "54" in oid:
            return "Scan Counter"

        return oid