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

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator
    }

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True