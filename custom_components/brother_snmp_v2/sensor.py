from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo, EntityCategory

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([
        BrotherPagesSensor(coordinator),
        BrotherModelSensor(coordinator),
        BrotherSerialSensor(coordinator),
        BrotherFirmwareSensor(coordinator),
        BrotherRollerSensor(coordinator),
    ])


class Base(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def available(self):
        return self.coordinator.data.get("online", False)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.data.get("serial"))},
            name=self.coordinator.data.get("model") or "Brother Scanner",
            manufacturer="Brother",
            model=self.coordinator.data.get("model"),
            sw_version=self.coordinator.data.get("firmware"),
            serial_number=self.coordinator.data.get("serial"),
        )


class BrotherPagesSensor(Base):
    _attr_name = "Brother Seiten gesamt"
    _attr_state_class = "measurement"

    @property
    def unique_id(self):
        return f"{self.coordinator.data.get('serial')}_pages"

    @property
    def state(self):
        return self.coordinator.data.get("pages_total")


class BrotherModelSensor(Base):
    _attr_name = "Brother Modell"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self):
        return f"{self.coordinator.data.get('serial')}_model"

    @property
    def state(self):
        return self.coordinator.data.get("model")


class BrotherSerialSensor(Base):
    _attr_name = "Brother Seriennummer"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self):
        return f"{self.coordinator.data.get('serial')}_serial"

    @property
    def state(self):
        return self.coordinator.data.get("serial")


class BrotherFirmwareSensor(Base):
    _attr_name = "Brother Firmware"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self):
        return f"{self.coordinator.data.get('serial')}_firmware"

    @property
    def state(self):
        return self.coordinator.data.get("firmware")


class BrotherRollerSensor(Base):
    _attr_name = "Brother Roller Zähler"

    @property
    def unique_id(self):
        return f"{self.coordinator.data.get('serial')}_roller"

    @property
    def state(self):
        return self.coordinator.data.get("roller")