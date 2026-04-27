import asyncio
import logging

from pysnmp.hlapi import (
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    nextCmd,
)

_LOGGER = logging.getLogger(__name__)


async def snmp_walk(host, community, base_oid):
    result = {}

    def _walk():
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

    return await asyncio.get_event_loop().run_in_executor(None, _walk)