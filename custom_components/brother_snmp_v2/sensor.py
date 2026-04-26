from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors = []

    # 🖨️ Printer
    if coordinator.device_class == "PRINTER":
        sensors.extend([
            BrotherAutoSensor(coordinator, s)
            for s in coordinator.sensors
        ])

    # 📄 Scanner
    elif coordinator.device_class == "SCANNER":
        walk = coordinator.data.get("walk", {})

        for oid in list(walk.keys())[:20]:
            sensors.append(BrotherWalkSensor(coordinator, oid))

    async_add_entities(sensors)


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
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.host)},
            manufacturer="Brother",
        )


class BrotherWalkSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, oid):
        super().__init__(coordinator)
        self._oid = oid

    @property
    def name(self):
        value = self.coordinator.data["walk"].get(self._oid)
        return self.coordinator.friendly_name(self._oid, value)

    @property
    def unique_id(self):
        return f"{self.coordinator.host}_{self._oid}"

    @property
    def state(self):
        return self.coordinator.data["walk"].get(self._oid)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.host)},
            manufacturer="Brother",
        )