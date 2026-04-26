import logging
import os
from datetime import timedelta
from .const import GOOD_SCANNER_OIDS
from .const import GOOD_PRINTER_OIDS

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

        # 🔥 MIB laden (nur Printer)
        if device_class == "PRINTER":
            try:
                base = os.path.dirname(__file__)
                mib_path = os.path.join(base, "BROTHER-Printer-MIB.json")
                self.sensors = load_mib(mib_path)
            except Exception as e:
                _LOGGER.warning(f"MIB load failed: {e}")
                self.sensors = []
        else:
            self.sensors = []

    # =========================
    # 🔄 UPDATE LOOP
    # =========================
    async def _async_update_data(self):
        data = {}

        # =========================
        # 🖨️ PRINTER (MIB)
        # =========================
        if self.device_class == "PRINTER":
            oids = [s["oid"] for s in self.sensors]

            raw = await snmp_bulk(self.host, self.community, oids)

            for oid, value in raw.items():
                if value is None or value == "":
                    continue
                data[oid] = self._convert(value)

            oid_norm = oid.rstrip(".0")

            for good_oid, name in GOOD_PRINTER_OIDS.items():
                if oid_norm.startswith(good_oid):
                    data[name] = self._convert(value)

        # =========================
        # 📄 SCANNER (WALK)
        # =========================
        elif self.device_class == "SCANNER":
            walk = await snmp_walk(self.host, self.community, SCANNER_BASE_OID)
            data["walk"] = self._smart_filter(walk)

        return data

    # =========================
    # 🔥 SMART FILTER (FIXED)
    # =========================
    def _smart_filter(self, walk):
        filtered = {}

        for oid, value in walk.items():

            if value is None or value == "":
                continue

            oid_norm = oid.rstrip(".0")

            # 🔥 NUR bekannte gute OIDs!
            for good_oid, name in GOOD_SCANNER_OIDS.items():
                if oid_norm.startswith(good_oid):
                    filtered[oid] = self._convert(value)

        return filtered

    # =========================
    # 🔧 VALUE CONVERSION
    # =========================
    def _convert(self, value):
        if value is None:
            return None

        try:
            return int(value)
        except (ValueError, TypeError):
            return str(value)

    # =========================
    # 🧠 CLEAN NAMING
    # =========================
    def friendly_name(self, oid, value=None):
        oid_norm = oid.rstrip(".0")

        for good_oid, name in GOOD_SCANNER_OIDS.items():
            if oid_norm.startswith(good_oid):
                return name

        return None  # nichts anzeigen