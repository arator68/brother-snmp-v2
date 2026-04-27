from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors = []

    walk = coordinator.data.get("walk", {})

    for oid, value in walk.items():
        name = coordinator.friendly_name(oid)

        if not name:
            continue

        sensors.append(BrotherScannerSensor(coordinator, oid, name))

    async_add_entities(sensors)


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
        return "mdi:chip"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.host)},
            manufacturer="Brother",
        )