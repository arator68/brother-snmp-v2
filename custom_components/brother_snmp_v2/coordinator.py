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


# 🔥 Brother interne HEX OIDs
BROTHER_HEX_OIDS = [
    "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.10",
]


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

        # optional MIB
        if device_class == "PRINTER":
            try:
                base = os.path.dirname(__file__)
                mib_path = os.path.join(base, "BROTHER-MIB.json")
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

            # 🔥 Basis-OIDs (funktionieren IMMER)
            base_oids = [
                "1.3.6.1.2.1.43.10.2.1.4.1.1",  # Printed Pages
                "1.3.6.1.2.1.25.3.2.1.3.1",     # Device Name
            ]

            oids = base_oids + list(GOOD_PRINTER_OIDS.keys()) + BROTHER_HEX_OIDS

            raw = await snmp_bulk(self.host, self.community, oids)

            _LOGGER.warning(f"PRINTER RAW: {raw}")

            for oid, value in raw.items():

                if value is None or value == "":
                    continue

                oid_norm = oid.rstrip(".0")

                # 🔥 Standard MIB (immer nehmen)
                if oid.startswith("1.3.6.1.2.1.43.10"):
                    data["Printed Pages"] = self._convert(value)
                    continue

                if oid.startswith("1.3.6.1.2.1.25.3"):
                    data["Device Name"] = value
                    continue

                # 🔥 Brother HEX Daten
                if any(oid_norm.startswith(x) for x in BROTHER_HEX_OIDS):
                    parsed = self._parse_brother_hex(value)

                    for k, v in parsed.items():
                        data[k] = v

                    continue

                # 🔥 Erweiterte OIDs (Whitelist)
                for good_oid, name in GOOD_PRINTER_OIDS.items():
                    if oid_norm.startswith(good_oid):
                        data[name] = self._convert(value)

        # =========================
        # 📄 SCANNER
        # =========================
        elif self.device_class == "SCANNER":

            walk = await snmp_walk(self.host, self.community, SCANNER_BASE_OID)

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
    # 🔥 HEX PARSER (BASIC)
    # =========================
    def _parse_brother_hex(self, value):
        try:
            if not value:
                return {}

            # String → Bytes
            data = bytes.fromhex(value.replace(" ", ""))

            result = {}

            # 🔥 heuristische Positionen (modellabhängig!)
            if len(data) > 20:
                result["Toner Black"] = data[10]
                result["Toner Cyan"] = data[11]
                result["Toner Magenta"] = data[12]
                result["Toner Yellow"] = data[13]

            return result

        except Exception as e:
            _LOGGER.warning(f"HEX parse failed: {e}")
            return {}

    # =========================
    # 🧠 NAMING (Scanner)
    # =========================
    def friendly_name(self, oid, value=None):
        oid_norm = oid.rstrip(".0")

        for good_oid, name in GOOD_SCANNER_OIDS.items():
            if oid_norm.startswith(good_oid):
                return name

        return None