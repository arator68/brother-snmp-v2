from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([
        BrotherPages(coordinator),
        BrotherRoller(coordinator),
    ])


class Base(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.host)},
            manufacturer="Brother",
        )


class BrotherPages(Base):
    _attr_name = "Pages"

    @property
    def unique_id(self):
        return f"{self.coordinator.host}_pages"

    @property
    def state(self):
        return self.coordinator.data["pages"]


class BrotherRoller(Base):
    _attr_name = "Roller"

    @property
    def unique_id(self):
        return f"{self.coordinator.host}_roller"

    @property
    def state(self):
        return self.coordinator.data["roller"]