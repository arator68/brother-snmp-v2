from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .coordinator import BrotherCoordinator
from . import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = BrotherCoordinator(
        hass,
        entry.data["host"],
        entry.data["community"]
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


# 🔧 Basis-Klasse für alle Sensoren
class BrotherBaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, host):
        super().__init__(coordinator)
        self._host = host

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

    @property
    def available(self):
        return self.coordinator.data.get("online", False)


# 📄 Seitenzähler
class BrotherPagesSensor(BrotherBaseSensor):
    def __init__(self, coordinator, host):
        super().__init__(coordinator, host)
        self._attr_name = "Seiten gesamt"
        self._attr_unique_id = f"{host}_pages_total"
        self._attr_state_class = "total_increasing"

    @property
    def state(self):
        return self.coordinator.data.get("pages_total")


# 🏷️ Modell
class BrotherModelSensor(BrotherBaseSensor):
    def __init__(self, coordinator, host):
        super().__init__(coordinator, host)
        self._attr_name = "Modell"
        self._attr_unique_id = f"{host}_model"

    @property
    def state(self):
        return self.coordinator.data.get("model")


# 🔢 Seriennummer
class BrotherSerialSensor(BrotherBaseSensor):
    def __init__(self, coordinator, host):
        super().__init__(coordinator, host)
        self._attr_name = "Seriennummer"
        self._attr_unique_id = f"{host}_serial"

    @property
    def state(self):
        return self.coordinator.data.get("serial")


# 🔧 Firmware
class BrotherFirmwareSensor(BrotherBaseSensor):
    def __init__(self, coordinator, host):
        super().__init__(coordinator, host)
        self._attr_name = "Firmware"
        self._attr_unique_id = f"{host}_firmware"

    @property
    def state(self):
        return self.coordinator.data.get("firmware")

class BrotherRollerSensor(BrotherBaseSensor):
    def __init__(self, coordinator, host):
        super().__init__(coordinator, host)
        self._attr_name = "Roller Zähler"
        self._attr_unique_id = f"{host}_roller_count"
        self._attr_state_class = "total_increasing"

    @property
    def state(self):
        return self.coordinator.data.get("roller_count")