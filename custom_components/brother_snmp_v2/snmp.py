import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from pysnmp.hlapi import *

from pysnmp.hlapi.v3arch.asyncio import (
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    get_cmd,
    walk_cmd,
)

_LOGGER = logging.getLogger(__name__)

# global SNMP engine (performance + reuse)
_ENGINE = SnmpEngine()


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

# =========================
# WALK 🔥 (FEHLT BEI DIR)
# =========================
async def snmp_walk(host, community, base_oid):
    results = {}

    try:
        transport = await UdpTransportTarget.create((host, 161))

        async for (
            error_indication,
            error_status,
            _,
            var_binds,
        ) in walk_cmd(
            SnmpEngine(),
            CommunityData(community),
            transport,
            ContextData(),
            ObjectType(ObjectIdentity(base_oid)),
            lexicographicMode=False,
        ):
            if error_indication or error_status:
                break

            for oid, value in var_binds:
                results[str(oid)] = str(value)

    except Exception as err:
        _LOGGER.error("SNMP WALK error: %s", err)

    return results


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