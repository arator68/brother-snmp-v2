from .snmp import snmp_get
from .const import IDENTITY_OID


def parse_identity(raw: str):
    data = {}
    for part in raw.split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            data[k] = v
    return data


async def detect_device(host, community):
    raw = await snmp_get(host, community, IDENTITY_OID)

    if not raw:
        return None

    data = parse_identity(raw)

    if data.get("MFG", "").lower() != "brother":
        return None

    return {
        "model": data.get("MDL"),
        "device_class": data.get("CLS"),
    }