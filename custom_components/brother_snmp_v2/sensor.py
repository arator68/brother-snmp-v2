from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors = []

    for oid, value in coordinator.data.get("walk", {}).items():
        name = coordinator.friendly_name(oid)

        if not name:
            continue  # 🔥 unbekannte ignorieren

        sensors.append(BrotherSensor(coordinator, oid, name))

    async_add_entities(sensors)


class BrotherSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, oid, name):
        super().__init__(coordinator)
        self._oid = oid
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        base = self.coordinator.serial_number or self.coordinator.host
        return f"{base}_{self._oid}"

    @property
    def state(self):
        return self.coordinator.data.get("walk", {}).get(self._oid)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.serial_number)},
            name=self.coordinator.model or "Brother Device",
            manufacturer="Brother",
            model=self.coordinator.model,
            serial_number=self.coordinator.serial_number,  # 🔥 DAS MUSS DA SEIN
        )