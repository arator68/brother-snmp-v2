import asyncio
import subprocess
import logging

_LOGGER = logging.getLogger(__name__)


async def snmp_walk(host, community, base_oid):
    loop = asyncio.get_event_loop()

    def run():
        try:
            result = subprocess.check_output(
                ["snmpwalk", "-v2c", "-c", community, host, base_oid],
                stderr=subprocess.DEVNULL,
                timeout=10,
            ).decode()

            data = {}

            for line in result.splitlines():
                if "=" not in line:
                    continue

                oid, val = line.split("=", 1)
                oid = oid.strip()
                val = val.split(":", 1)[-1].strip()

                data[oid] = val

            return data

        except Exception as e:
            _LOGGER.error(f"SNMP WALK failed: {e}")
            return {}

    return await loop.run_in_executor(None, run)