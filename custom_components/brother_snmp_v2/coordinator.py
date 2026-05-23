import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .snmp import snmp_walk
from .const import GOOD_SCANNER_OIDS
from .const import GOOD_PRINTER_OIDS

_LOGGER = logging.getLogger(__name__)


# =========================
# PARSER
# =========================
def parse_device_info(value: str) -> dict:
    """Parse Brother device info string."""
    if not value:
        return {}

    result = {}

    try:
        for part in value.split(";"):
            if ":" not in part:
                continue

            key, val = part.split(":", 1)

            key = key.strip().upper()
            val = val.strip()

            if key == "MFG":
                result["manufacturer"] = val
            elif key == "MDL":
                result["model"] = val
            elif key == "CLS":
                result["class"] = val.lower()

    except Exception as err:
        _LOGGER.warning(f"Parser error: {err}")

    return result


# =========================
# COORDINATOR
# =========================
class BrotherCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, host, community):
        super().__init__(
            hass,
            _LOGGER,
            name="Brother SNMP",
            update_interval=timedelta(seconds=30),
        )

        self.host = host
        self.community = community

        # 🔥 wird in __init__.py gesetzt
        self.engine = None

        # 🔥 Geräte-Infos
        self.serial_number = None
        self.model = None
        self.device_class = None

        # 🔥 bekannte Sensoren Scanner  
        self.GOOD_SCANNER_OIDS = GOOD_SCANNER_OIDS
        self.GOOD_PRINTER_OIDS = GOOD_PRINTER_OIDS

        self.data = {}

    # =========================
    # UPDATE
    # =========================
    async def _async_update_data(self):
        """Fetch data via SNMP."""

        data = {}

        try:
            walk = await snmp_walk(
                self.engine,
                self.host,
                self.community,
                "1.3.6.1.4.1.2435",
            )
            

            _LOGGER.warning(f"SNMP WALK: {len(walk)} values")
            
            if not self.device_class:
                self.device_class = self.detect_device_class(walk)

            for oid, value in walk.items():
                value_str = str(value)

                # =========================
                # DEVICE INFO PARSEN
                # =========================
                parsed = parse_device_info(value_str)

                if parsed:
                    if parsed.get("model") and not self.model:
                        self.model = parsed["model"]

                    if parsed.get("class") and not self.device_class:
                        self.device_class = parsed["class"]

                    _LOGGER.warning(f"PARSED DEVICE: {parsed}")
                   
                

                # =========================
                # OID speichern
                # =========================
                data[oid] = value_str

            # =========================
            # STATUS setzen
            # =========================
            if walk:
                data["status"] = "online"
            else:
                data["status"] = "error"

        except Exception as err:
            _LOGGER.error(f"SNMP update failed: {err}")
            data["status"] = "error"

        # 🔥 Debug
        _LOGGER.warning(f"FINAL DATA KEYS: {list(data.keys())[:5]} ...")

        return data


    # =========================
    # FRIENDLY NAME
    # =========================
    def friendly_name(self, oid):
        """Return friendly name for OID."""

        if oid in self.GOOD_SCANNER_OIDS:
            return self.GOOD_SCANNER_OIDS[oid]
        
        # if oid in self.GOOD_PRINTER_OIDS:
        #     return self.GOOD_PRINTER_OIDS[oid]
        
        for base_oid, name in self.GOOD_PRINTER_OIDS.items():
            if oid.startswith(base_oid):
                return name

        return None
    
    def detect_device_class(self, walk: dict):
        """Robuste Geräteerkennung (Brother zuverlässig)."""

        # =========================
        # 1. PRINTER OIDs (BEST)
        # =========================
        PRINTER_OIDS = [
            "1.3.6.1.2.1.43.10.2.1.4.1.1",  # Page counter
        ]

        for oid in PRINTER_OIDS:
            if oid in walk:
                return "printer"

        # =========================
        # 2. SCANNER OIDs
        # =========================
        SCANNER_HINTS = [
            "scan",
            "adf",
        ]

        for value in walk.values():
            value_str = str(value).lower()
            if any(hint in value_str for hint in SCANNER_HINTS):
                return "scanner"

        # =========================
        # 3. MODEL CHECK
        # =========================
        if self.model:
            model = self.model.upper()

            if model.startswith(("HL-", "DCP-", "MFC-")):
                return "printer"

            if model.startswith(("ADS-",)):
                return "scanner"

        # =========================
        # 4. FALLBACK
        # =========================
        return "unknown"