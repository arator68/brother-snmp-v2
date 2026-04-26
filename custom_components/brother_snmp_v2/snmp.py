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
)

_LOGGER = logging.getLogger(__name__)

# global SNMP engine (performance + reuse)
_ENGINE = SnmpEngine()


async def snmp_get(host: str, community: str, oid: str) -> str | None:
    """Async SNMP GET (pysnmp v7 compatible)."""
    try:
        transport = await UdpTransportTarget.create((host, 161))

        error_indication, error_status, _, var_binds = await get_cmd(
            _ENGINE,
            CommunityData(community),
            transport,
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
        )

        if error_indication:
            _LOGGER.debug("SNMP error (%s): %s", host, error_indication)
            return None

        if error_status:
            _LOGGER.debug("SNMP status error (%s): %s", host, error_status)
            return None

        return str(var_binds[0][1]) if var_binds else None

    except Exception as err:
        _LOGGER.error("SNMP exception (%s): %s", host, err)
        return None


async def snmp_bulk(host: str, community: str, oids: list[str]) -> dict[str, str | None]:
    """Parallel SNMP GET for multiple OIDs."""
    try:
        tasks = [snmp_get(host, community, oid) for oid in oids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        output = {}
        for oid, result in zip(oids, results):
            if isinstance(result, Exception):
                _LOGGER.debug("SNMP bulk error (%s): %s", host, result)
                output[oid] = None
            else:
                output[oid] = result

        return output

    except Exception as err:
        _LOGGER.error("SNMP bulk failed (%s): %s", host, err)
        return {oid: None for oid in oids}