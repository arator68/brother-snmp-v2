import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from pysnmp.hlapi.v3arch.asyncio import SnmpEngine

from .const import DOMAIN
from .coordinator import BrotherCoordinator

_LOGGER = logging.getLogger(__name__)


# =========================
# SETUP ENTRY
# =========================
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Brother SNMP from a config entry."""

    # 🔥 Coordinator erstellen
    coordinator = BrotherCoordinator(
        hass,
        entry.data["host"],
        entry.data["community"],
    )

    # 🔥 SNMP Engine (shared per device)
    coordinator.engine = SnmpEngine()

    # =========================
    # 🔥 WICHTIG: Werte aus Config Flow setzen
    # =========================
    coordinator.serial_number = entry.data.get("serial")
    coordinator.model = entry.data.get("model")
    coordinator.device_class = entry.data.get("device_class")

    _LOGGER.warning(
        f"INIT → serial={coordinator.serial_number}, "
        f"model={coordinator.model}, "
        f"class={coordinator.device_class}"
    )

    # =========================
    # Daten laden
    # =========================
    await coordinator.async_config_entry_first_refresh()

    # =========================
    # speichern
    # =========================
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator
    }

    # =========================
    # Plattformen laden
    # =========================
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


# =========================
# UNLOAD ENTRY
# =========================
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok