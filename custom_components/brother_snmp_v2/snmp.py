import asyncio
import logging

from pysnmp.hlapi.asyncio import nextCmd, SnmpEngine
from pysnmp.hlapi.asyncio import (
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
)

_LOGGER = logging.getLogger(__name__)


async def snmp_walk(host, community, base_oid):
    result = {}

    try:
        async for (errorIndication,
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

            if errorIndication:
                _LOGGER.error(f"SNMP error: {errorIndication}")
                return {}

            if errorStatus:
                _LOGGER.error(f"SNMP error: {errorStatus}")
                return {}

            for varBind in varBinds:
                oid, value = varBind
                result[str(oid)] = str(value)

    except Exception as e:
        _LOGGER.error(f"SNMP WALK failed: {e}")
        return {}

    return result