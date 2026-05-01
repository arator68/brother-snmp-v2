from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

from .const import GOOD_SCANNER_OIDS
from .const import GOOD_PRINTER_OIDS


# =========================
# STANDARD SENSOR
# =========================
class BrotherSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, oid, name):
        super().__init__(coordinator)
        self.oid = oid
        self._attr_name = name

    @property
    def unique_id(self):
        return f"{self.coordinator.serial_number}_{self.oid}"

    @property
    def state(self):
        # 🔥 wichtig: kein None → HA zeigt sonst nichts
        return self.coordinator.data.get(self.oid, "unknown")

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.serial_number)},
            name=self.coordinator.model or "Brother Device",
            manufacturer="Brother",
            model=self.coordinator.model,
            serial_number=self.coordinator.serial_number,
        )


# =========================
# DEVICE TYPE SENSOR
# =========================
class BrotherDeviceClassSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Device Type"

    @property
    def unique_id(self):
        return f"{self.coordinator.serial_number}_device_type"

    @property
    def state(self):
        return self.coordinator.device_class or "unknown"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.serial_number)},
        )


# =========================
# STATUS SENSOR
# =========================
class BrotherStatusSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Status"

    @property
    def unique_id(self):
        return f"{self.coordinator.serial_number}_status"

    @property
    def state(self):
        return self.coordinator.data.get("status", "unknown")

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.serial_number)},
        )


# =========================
# SETUP
# =========================
async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    
    device_class = coordinator.device_class

    if not device_class:
        device_class = "scanner"

    sensors = []
    
   
    # =========================
    # 🔥 AUTO ROUTING
    # =========================
    if device_class == "scanner":
        oid_map = GOOD_SCANNER_OIDS

    elif device_class == "printer":
        oid_map = GOOD_PRINTER_OIDS

    else:
        # fallback → nichts oder minimal
        oid_map = {}

    # =========================
    # 🔥 NUR BEKANNTE SENSORN
    # =========================
    for oid, name in oid_map.items():
        # 🔥 WICHTIG: KEIN data-check!
        sensors.append(BrotherSensor(coordinator, oid, name))

    # =========================
    # 🔥 IMMER hinzufügen
    # =========================
    sensors.append(BrotherDeviceClassSensor(coordinator))
    sensors.append(BrotherStatusSensor(coordinator))

    async_add_entities(sensors)