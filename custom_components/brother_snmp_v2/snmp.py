import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from pysnmp.hlapi import *

_LOGGER = logging.getLogger(__name__)


def _walk(host, community, base_oid):
    result = {}

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((host, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(base_oid)),
        lexicographicMode=False,
    ):

        if errorIndication or errorStatus:
            return {}

        for varBind in varBinds:
            oid, value = varBind
            result[str(oid)] = str(value)

    return result


class BrotherCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, host, community):
        super().__init__(
            hass,
            _LOGGER,
            name="Brother SNMP Scanner",
            update_interval=timedelta(seconds=15),
        )

        self.host = host
        self.community = community

    async def _async_update_data(self):
        walk = await self.hass.async_add_executor_job(
            _walk,
            self.host,
            self.community,
            "1.3.6.1.4.1.2435.2.3.9"
        )

        return {"walk": walk}