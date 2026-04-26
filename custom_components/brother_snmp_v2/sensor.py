from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN


# =========================
# SETUP
# =========================
async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors = []

    # =========================
    # 🖨️ PRINTER
    # =========================
    if coordinator.device_class == "PRINTER":
        sensors.extend([
            BrotherAutoSensor(coordinator, s)
            for s in coordinator.sensors
        ])

    # =========================
    # 📄 SCANNER (nur gute OIDs!)
    # =========================
    elif coordinator.device_class == "SCANNER":
        walk = coordinator.data.get("walk", {})

        for oid, value in walk.items():

            name = coordinator.friendly_name(oid, value)

            # ❌ ignorieren wenn kein sinnvoller Name
            if not name:
                continue

            sensors.append(BrotherWalkSensor(coordinator, oid, name))

    async_add_entities(sensors)


# =========================
# 🖨️ PRINTER SENSOR
# =========================
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
    def icon(self):
        name = self.name.lower()

        if "toner" in name:
            return "mdi:printer"
        if "page" in name:
            return "mdi:file-document"
        return "mdi:printer-outline"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.host)},
            manufacturer="Brother",
        )


# =========================
# 📄 SCANNER SENSOR (CLEAN)
# =========================
class BrotherWalkSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, oid, name):
        super().__init__(coordinator)
        self._oid = oid
        self._name = name

    # 🔥 sauberer Name (aus Whitelist)
    @property
    def name(self):
        return self._name

    # 🔥 eindeutig
    @property
    def unique_id(self):
        return f"{self.coordinator.host}_{self._oid}"

    # 🔥 stabiler State
    @property
    def state(self):
        return self.coordinator.data.get("walk", {}).get(self._oid)

    # 🔥 bessere Icons
    @property
    def icon(self):
        name = self._name.lower()

        if "roller" in name:
            return "mdi:rotate-3d"
        if "scan" in name:
            return "mdi:scanner"
        if "status" in name:
            return "mdi:information"
        return "mdi:chip"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.host)},
            manufacturer="Brother",
        )