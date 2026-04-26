from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .coordinator import BrotherCoordinator
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = BrotherCoordinator(
        hass,
        entry.data["host"],
        entry.data["community"],
    )

    await coordinator.async_config_entry_first_refresh()

    host = entry.data["host"]

    async_add_entities([
        BrotherPagesSensor(coordinator, host),
        BrotherModelSensor(coordinator, host),
        BrotherSerialSensor(coordinator, host),
        BrotherFirmwareSensor(coordinator, host),
        BrotherRollerSensor(coordinator, host),
    ])


class Base(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, host):
        super().__init__(coordinator)
        self._host = host

    @property
    def available(self):
        return self.coordinator.data.get("online", False)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._host)},
            name=self.coordinator.data.get("model") or "Brother Scanner",
            manufacturer="Brother",
            model=self.coordinator.data.get("model"),
            sw_version=self.coordinator.data.get("firmware"),
            serial_number=self.coordinator.data.get("serial"),
        )


class BrotherPagesSensor(Base):
    def __init__(self, c, h):
        super().__init__(c, h)
        self._attr_name = "Brother Seiten gesamt"
        self._attr_unique_id = f"{h}_pages"

    @property
    def state(self):
        return self.coordinator.data.get("pages_total")


class BrotherModelSensor(Base):
    def __init__(self, c, h):
        super().__init__(c, h)
        self._attr_name = "Brother Modell"
        self._attr_unique_id = f"{h}_model"

    @property
    def state(self):
        return self.coordinator.data.get("model")


class BrotherSerialSensor(Base):
    def __init__(self, c, h):
        super().__init__(c, h)
        self._attr_name = "Brother Seriennummer"
        self._attr_unique_id = f"{h}_serial"

    @property
    def state(self):
        return self.coordinator.data.get("serial")


class BrotherFirmwareSensor(Base):
    def __init__(self, c, h):
        super().__init__(c, h)
        self._attr_name = "Brother Firmware"
        self._attr_unique_id = f"{h}_firmware"

    @property
    def state(self):
        return self.coordinator.data.get("firmware")


class BrotherRollerSensor(Base):
    def __init__(self, c, h):
        super().__init__(c, h)
        self._attr_name = "Brother Roller Zähler"
        self._attr_unique_id = f"{h}_roller"

    @property
    def state(self):
        return self.coordinator.data.get("roller")