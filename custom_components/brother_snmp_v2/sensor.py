from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


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
        return self.coordinator.data.get(self.oid)

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
        # 🔥 wichtig → nie None anzeigen
        return self.coordinator.device_class or "unknown"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.serial_number)},
        )


# =========================
# STATUS SENSOR (optional)
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

    sensors = []

    # =========================
    # OID SENSOR GENERATION
    # =========================
    for oid, value in coordinator.data.items():

        # 🔥 interne keys überspringen
        if oid in ["status"]:
            continue

        name = coordinator.friendly_name(oid)

        # fallback → OID anzeigen
        if not name:
            name = f"OID {oid}"

        sensors.append(BrotherSensor(coordinator, oid, name))

    # =========================
    # EXTRA SENSOR
    # =========================
    sensors.append(BrotherDeviceClassSensor(coordinator))
    sensors.append(BrotherStatusSensor(coordinator))

    async_add_entities(sensors)