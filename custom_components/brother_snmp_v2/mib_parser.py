import json
from .const import IMPORTANT_KEYWORDS


def is_useful(name):
    name = name.lower()
    return any(k in name for k in IMPORTANT_KEYWORDS)


def load_mib(path):
    with open(path, "r") as f:
        data = json.load(f)

    sensors = []

    for obj in data.values():
        if not isinstance(obj, dict):
            continue

        if obj.get("class") != "objecttype":
            continue

        if obj.get("maxaccess") != "read-only":
            continue

        name = obj.get("name")
        oid = obj.get("oid")

        if not name or not oid:
            continue

        if not is_useful(name):
            continue

        sensors.append({
            "key": name.lower(),
            "name": name,
            "oid": oid,
        })

    return sensors