import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .snmp import snmp_walk
from .const import GOOD_SCANNER_OIDS

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

        # 🔥 bekannte Sensoren
        # self.GOOD_SCANNER_OIDS = {
        #     "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.54.2.2.1.3.3": "Scan Pages",
        #     "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.1.2.63.33.1.1.18": "Pickup Roller",
        #     "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.1.2.63.33.1.1.19": "Separation Roller",
        #     "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.1.2.63.33.1.1.20": "Feed Roller",
        #     "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.1.0": "Serialnumber",
        #     "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.17.0": "Firmware",
        # }
        
        self.GOOD_SCANNER_OIDS = GOOD_SCANNER_OIDS

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
            data["status"] = "online"

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

        return None