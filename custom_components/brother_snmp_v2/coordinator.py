import logging
import os
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .snmp import snmp_bulk, snmp_walk
from .mib_parser import load_mib
from .const import (
    SCANNER_BASE_OID,
    GOOD_SCANNER_OIDS,
    GOOD_PRINTER_OIDS,
)

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

        # =========================
        # 🖨️ MIB laden (optional)
        # =========================
        if device_class == "PRINTER":
            try:
                base = os.path.dirname(__file__)
                mib_path = os.path.join(base, "BROTHER-Printer-MIB.json")
                self.sensors = load_mib(mib_path)
                _LOGGER.warning(f"MIB sensors loaded: {len(self.sensors)}")
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
        # 🖨️ PRINTER
        # =========================
        if self.device_class == "PRINTER":

            # 🔥 immer diese Basis-OIDs
            base_oids = [
                "1.3.6.1.2.1.43.10.2.1.4.1.1",  # pages
                "1.3.6.1.2.1.25.3.2.1.3.1",     # name
            ]

            # 🔥 plus deine erweiterten
            oids = base_oids + list(GOOD_PRINTER_OIDS.keys())

            raw = await snmp_bulk(self.host, self.community, oids)

            _LOGGER.warning(f"PRINTER RAW: {raw}")

            data = {}

            for oid, value in raw.items():

                if value is None or value == "":
                    continue

                oid_norm = oid.rstrip(".0")

                # 🔥 STANDARD OIDs (immer nehmen!)
                if oid.startswith("1.3.6.1.2.1.43.10"):
                    data["Printed Pages"] = self._convert(value)
                    continue

                if oid.startswith("1.3.6.1.2.1.25.3"):
                    data["Device Name"] = value
                    continue

                # 🔥 OPTIONAL OIDs (nur wenn Daten da sind)
                for good_oid, name in GOOD_PRINTER_OIDS.items():
                    if oid_norm.startswith(good_oid):
                        data[name] = self._convert(value)

            return data

        # =========================
        # 📄 SCANNER
        # =========================
        elif self.device_class == "SCANNER":

            walk = await snmp_walk(self.host, self.community, SCANNER_BASE_OID)

            # 🔍 DEBUG
            _LOGGER.warning(f"SCANNER WALK: {len(walk)} OIDs")

            data["walk"] = self._smart_filter(walk)

        return data

    # =========================
    # 🔥 SCANNER FILTER
    # =========================
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

    # =========================
    # 🔧 VALUE CONVERT
    # =========================
    def _convert(self, value):
        if value is None:
            return None

        try:
            return int(value)
        except (ValueError, TypeError):
            return str(value)

    # =========================
    # 🧠 NAMING (Scanner)
    # =========================
    def friendly_name(self, oid, value=None):
        oid_norm = oid.rstrip(".0")

        for good_oid, name in GOOD_SCANNER_OIDS.items():
            if oid_norm.startswith(good_oid):
                return name

        return None