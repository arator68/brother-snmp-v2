from datetime import timedelta
import logging
import re

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .snmp import snmp_bulk

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=15)

# 📊 OIDs
PAGE_OID = "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.54.2.2.1.3.3"
MODEL_OID = "1.3.6.1.4.1.2435.2.4.3.99.3.1.6.1.2.1"
SERIAL_OID = "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.1.0"
FIRMWARE_OID = "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.17.0"
ROLLER_OID = "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.1.2.63.33.1.1.18"


class BrotherCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, host, community):
        super().__init__(
            hass,
            _LOGGER,
            name="Brother SNMP V2",
            update_interval=SCAN_INTERVAL,
        )
        self.host = host
        self.community = community

    async def _async_update_data(self):
        try:
            data = await snmp_bulk(
                self.host,
                self.community,
                [
                    PAGE_OID,
                    MODEL_OID,
                    SERIAL_OID,
                    FIRMWARE_OID,
                    ROLLER_OID,
                ]
            )

            # 📄 Seiten sicher parsen
            pages_raw = data.get(PAGE_OID)
            pages = int(pages_raw) if pages_raw and pages_raw.isdigit() else None

            # 🏷️ Modell bereinigen
            raw_model = data.get(MODEL_OID)
            model = None
            if raw_model:
                match = re.search(r'"(.+)"', raw_model)
                model = match.group(1) if match else raw_model

            # 🔢 Seriennummer bereinigen (falls nötig)
            raw_serial = data.get(SERIAL_OID)
            serial = None
            if raw_serial:
                match = re.search(r'"(.+)"', raw_serial)
                serial = match.group(1) if match else raw_serial

            # 🔧 Firmware bereinigen
            raw_fw = data.get(FIRMWARE_OID)
            firmware = None
            if raw_fw:
                match = re.search(r'"(.+)"', raw_fw)
                firmware = match.group(1) if match else raw_fw

            # 🔧 Roller Counter
            roller_raw = data.get(ROLLER_OID)
            roller = int(roller_raw) if roller_raw and roller_raw.isdigit() else None

            return {
                "online": pages is not None,
                "pages_total": pages,
                "model": model,
                "serial": serial,
                "firmware": firmware,
                "roller_count": roller,
            }

        except Exception as e:
            _LOGGER.error(f"SNMP Fehler: {e}")
            return {
                "online": False,
                "pages_total": None,
                "model": None,
                "serial": None,
                "firmware": None,
                "roller_count": None,
            }