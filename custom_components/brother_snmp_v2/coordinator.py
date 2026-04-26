import logging
import os
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

        # 🔥 MIB laden (nur Printer)
        if device_class == "PRINTER":
            try:
                base = os.path.dirname(__file__)
                mib_path = os.path.join(base, "BROTHER-MIB.json")
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

            for s in self.sensors:
                val = raw.get(s["oid"])
                data[s["key"]] = self._convert(val)

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

            # ❌ nur wirklich leere Werte ignorieren
            if value is None or value == "":
                continue

            # 🔥 relevante Bereiche
            if not any(x in oid for x in ["5.5", "5.1", "5.2", "54"]):
                continue

            # 🔥 nur Änderungen (Delta)
            if oid in self._last_walk:
                if self._last_walk[oid] == value:
                    continue

            # 🔧 konvertieren
            val = self._convert(value)

            # 🔍 DEBUG (optional aktivieren)
            # _LOGGER.warning(f"{oid} → {val}")

            filtered[oid] = val

        self._last_walk = walk
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

        # 🔥 OID normalisieren (.0 entfernen)
        oid_norm = oid.rstrip(".0")

        # 🔥 KNOWN OIDS MATCH (FIX!)
        for known_oid, name in KNOWN_OIDS.items():
            if oid_norm.startswith(known_oid):
                return name

        # =========================
        # Pattern Mapping
        # =========================
        if "5.5" in oid:
            return "Scan Counter"

        if "5.1" in oid:
            return "Roller Usage"

        if "5.2" in oid:
            return "Device Status"

        if "54" in oid:
            return "Scan Pages"

        # =========================
        # Value-based
        # =========================
        if isinstance(value, str):
            v = value.lower()
            if "error" in v:
                return "Error Status"
            if "ready" in v:
                return "Device Ready"

        # =========================
        # Fallback
        # =========================
        parts = oid.split(".")
        return f"SNMP {parts[-2:]}"