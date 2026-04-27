import asyncio
import logging

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


# =========================
# GET
# =========================
async def snmp_get(engine, host, community, oid):
    try:
        transport = await UdpTransportTarget.create((host, 161))

        error_indication, error_status, _, var_binds = await get_cmd(
            engine,
            CommunityData(community),
            transport,
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
        )

        if error_indication or error_status:
            return None

        return str(var_binds[0][1]) if var_binds else None

    except Exception as err:
        _LOGGER.error("SNMP GET error: %s", err)
        return None


# =========================
# BULK
# =========================
async def snmp_bulk(engine, host, community, oids):
    tasks = [snmp_get(engine, host, community, oid) for oid in oids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    output = {}
    for oid, result in zip(oids, results):
        output[oid] = None if isinstance(result, Exception) else result

    return output


# =========================
# WALK
# =========================
async def snmp_walk(engine, host, community, base_oid):
    results = {}

    try:
        transport = await UdpTransportTarget.create((host, 161))

        async for (
            error_indication,
            error_status,
            _,
            var_binds,
        ) in walk_cmd(
            engine,
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