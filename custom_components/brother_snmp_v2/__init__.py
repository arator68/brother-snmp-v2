from pysnmp.hlapi.v3arch.asyncio import SnmpEngine

from .const import DOMAIN
from .coordinator import BrotherCoordinator


async def async_setup_entry(hass, entry):
    coordinator = BrotherCoordinator(
        hass,
        entry.data["host"],
        entry.data["community"],
    )

    # 🔥 shared engine (performance!)
    coordinator.engine = SnmpEngine()
    
    # 🔥 HIER EINFÜGEN ↓↓↓
    coordinator.serial_number = entry.data.get("serial")

    # optional (gut!)
    coordinator.model = entry.data.get("model")

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator
    }

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

@property
def device_info(self):
    return DeviceInfo(
        identifiers={(DOMAIN, self.coordinator.serial_number)},
        name=self.coordinator.model or "Brother Device",
        manufacturer="Brother",
        model=self.coordinator.model,
        serial_number=self.coordinator.serial_number,  # 🔥 DAS HIER IST DER FIX
    )