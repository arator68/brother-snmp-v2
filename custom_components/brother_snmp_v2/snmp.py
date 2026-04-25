import asyncio
from pysnmp.hlapi.v3arch.asyncio import (
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    get_cmd,
)

_ENGINE = SnmpEngine()


async def snmp_get(host, community, oid):
    transport = await UdpTransportTarget.create((host, 161))

    error_indication, error_status, _, var_binds = await get_cmd(
        _ENGINE,
        CommunityData(community, mpModel=1),
        transport,
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
    )

    if error_indication or error_status:
        return None

    return str(var_binds[0][1]) if var_binds else None


async def snmp_bulk(host, community, oids):
    tasks = [snmp_get(host, community, oid) for oid in oids]
    results = await asyncio.gather(*tasks)
    return dict(zip(oids, results))