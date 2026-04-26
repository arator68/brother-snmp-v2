from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors = [
        BrotherSensor(coordinator, s)
        for s in coordinator.profile["sensors"]
    ]

    async_add_entities(sensors)


class BrotherSensor(CoordinatorEntity, SensorEntity):
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
            name=self.coordinator.device_class,
        )