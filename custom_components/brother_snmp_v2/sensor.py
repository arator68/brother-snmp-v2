from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN


# =========================
# SETUP
# =========================
async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors = []

    # =========================
    # 🖨️ PRINTER
    # =========================
    if coordinator.device_class == "PRINTER":
        for key in coordinator.data.keys():
            sensors.append(BrotherPrinterSensor(coordinator, key))

    # =========================
    # 📄 SCANNER
    # =========================
    elif coordinator.device_class == "SCANNER":
        walk = coordinator.data.get("walk", {})

        for oid, value in walk.items():

            name = coordinator.friendly_name(oid, value)

            # ❌ ignorieren wenn nicht relevant
            if not name:
                continue

            sensors.append(BrotherScannerSensor(coordinator, oid, name))

    async_add_entities(sensors)


# =========================
# 🖨️ PRINTER SENSOR
# =========================
class BrotherPrinterSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key):
        super().__init__(coordinator)
        self._key = key

    @property
    def name(self):
        return self._key

    @property
    def unique_id(self):
        return f"{self.coordinator.host}_{self._key}"

    @property
    def state(self):
        value = self.coordinator.data.get(self._key)

        # 🔥 Prozent normalisieren (falls nötig)
        if self._is_percentage() and isinstance(value, int):
            if value > 100:
                return int((value / 255) * 100)

        return value

    # 🔥 Prozent Anzeige
    @property
    def native_unit_of_measurement(self):
        if self._is_percentage():
            return "%"
        return None

    # 🔥 Prozent-Erkennung
    def _is_percentage(self):
        name = self._key.lower()

        return any(x in name for x in [
            "toner",
            "drum",
            "life",
            "level",
        ])

    # 🔥 Icons
    @property
    def icon(self):
        name = self._key.lower()

        if "toner" in name:
            return "mdi:printer-3d"
        if "drum" in name:
            return "mdi:cog"
        if "page" in name:
            return "mdi:file-document"
        if "error" in name or "jam" in name:
            return "mdi:alert"
        return "mdi:printer"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.host)},
            manufacturer="Brother",
        )


# =========================
# 📄 SCANNER SENSOR
# =========================
class BrotherScannerSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, oid, name):
        super().__init__(coordinator)
        self._oid = oid
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"{self.coordinator.host}_{self._oid}"

    @property
    def state(self):
        return self.coordinator.data.get("walk", {}).get(self._oid)

    @property
    def icon(self):
        name = self._name.lower()

        if "roller" in name:
            return "mdi:rotate-3d"
        if "scan" in name:
            return "mdi:scanner"
        if "status" in name:
            return "mdi:information"
        return "mdi:chip"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.host)},
            manufacturer="Brother",
        )