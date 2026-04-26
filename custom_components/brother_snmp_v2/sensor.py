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
    # 🖨️ PRINTER (MIB)
    # =========================
    if coordinator.device_class == "PRINTER":
        sensors.extend([
            BrotherAutoSensor(coordinator, s)
            for s in coordinator.sensors
        ])

    # =========================
    # 📄 SCANNER (WALK)
    # =========================
    elif coordinator.device_class == "SCANNER":
        walk = coordinator.data.get("walk", {})

        for oid in list(walk.keys())[:20]:  # limit für UI
            sensors.append(BrotherWalkSensor(coordinator, oid))

    async_add_entities(sensors)


# =========================
# 🖨️ PRINTER SENSOR
# =========================
class BrotherAutoSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, config):
        super().__init__(coordinator)
        self._config = config

    @property
    def name(self):
        return self._config["name"]

    @property
    def unique_id(self):
        return f"{self.coordinator.host}_{self._config['key']}"

    @property
    def state(self):
        return self.coordinator.data.get(self._config["key"])

    @property
    def icon(self):
        name = self.name.lower()

        if "toner" in name:
            return "mdi:printer"
        if "page" in name:
            return "mdi:file-document"
        if "error" in name:
            return "mdi:alert"
        return "mdi:printer-outline"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.host)},
            manufacturer="Brother",
        )


# =========================
# 📄 SCANNER SENSOR
# =========================
class BrotherWalkSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, oid):
        super().__init__(coordinator)
        self._oid = oid

    # 🔥 CLEAN NAME
    @property
    def name(self):
        value = self.coordinator.data.get("walk", {}).get(self._oid)
        return self.coordinator.friendly_name(self._oid, value)

    # 🔥 WICHTIG: eindeutig!
    @property
    def unique_id(self):
        return f"{self.coordinator.host}_{self._oid}"

    # 🔥 STATE FIX (kein "Unbekannt" mehr)
    @property
    def state(self):
        return self.coordinator.data.get("walk", {}).get(self._oid)

    # 🔥 ICONS (nice UI)
    @property
    def icon(self):
        name = self.name.lower()

        if "roller" in name:
            return "mdi:rotate-3d"
        if "scan" in name:
            return "mdi:scanner"
        if "status" in name:
            return "mdi:information"
        if "error" in name:
            return "mdi:alert"
        return "mdi:chip"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.host)},
            manufacturer="Brother",
        )