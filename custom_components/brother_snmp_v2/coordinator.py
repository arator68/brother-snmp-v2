import logging
import re
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .snmp import snmp_walk
from .const import SCANNER_BASE_OID
from .const import GOOD_SCANNER_OIDS

_LOGGER = logging.getLogger(__name__)


def _extract_serial(value):
    match = re.search(r'SERIAL="([^"]+)"', value)
    return match.group(1) if match else None


def _extract_model(value):
    match = re.search(r'MDL:([^;]+)', value)
    return match.group(1) if match else None


class BrotherCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, host, community):
        super().__init__(
            hass,
            _LOGGER,
            name="Brother SNMP",
            update_interval=timedelta(seconds=30),
        )

        self.host = host
        self.community = community

        # 🔥 Multi-device
        self.serial_number = None
        self.model = None

    async def _async_update_data(self):
        data = {}

        walk = await snmp_walk(
            self.engine,
            self.host,
            self.community,
            SCANNER_BASE_OID,
        )

        for oid, value in walk.items():
            value_str = str(value)

            # SERIAL
            # if "SERIAL=" in value_str:
            #    serial = _extract_serial(value_str)
            #    if serial:
            #        self.serial_number = serial

            # MODEL
            if "MDL:" in value_str:
                model = _extract_model(value_str)
                if model:
                    self.model = model

            data[oid] = value

        return {"walk": data}
    
    def friendly_name(self, oid):
        for base, name in GOOD_SCANNER_OIDS.items():
            if oid.startswith(base):
                return name
        
        return None