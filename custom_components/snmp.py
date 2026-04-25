from pysnmp.hlapi.v3arch.asyncio import *
import asyncio

_SNMP_ENGINE = None
_LOCK = asyncio.Lock()

async def get_engine():
    global _SNMP_ENGINE
    async with _LOCK:
        if _SNMP_ENGINE is None:
            _SNMP_ENGINE = SnmpEngine()
    return _SNMP_ENGINE


async def snmp_get(host, community, oid):
    engine = await get_engine()
    transport = await UdpTransportTarget.create((host, 161))

    error_indication, error_status, _, var_binds = await get_cmd(
        engine,
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