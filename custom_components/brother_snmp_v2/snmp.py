import asyncio
import logging

from pysnmp.hlapi.asyncio import (
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    getCmd,
)

_LOGGER = logging.getLogger(__name__)
_ENGINE = SnmpEngine()


async def snmp_get(host, community, oid):
    try:
        transport = await UdpTransportTarget.create((host, 161))

        error_indication, error_status, _, var_binds = await getCmd(
            _ENGINE,
            CommunityData(community),
            transport,
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
        )

        if error_indication or error_status:
            return None

        return str(var_binds[0][1]) if var_binds else None

    except Exception as err:
        _LOGGER.error("SNMP error: %s", err)
        return None


async def snmp_bulk(host, community, oids):
    tasks = [snmp_get(host, community, oid) for oid in oids]
    results = await asyncio.gather(*tasks)
    return dict(zip(oids, results))