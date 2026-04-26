DOMAIN = "brother_snmp_v2"

CONF_HOST = "host"
CONF_COMMUNITY = "community"

IDENTITY_OID = "1.3.6.1.4.1.2435.2.3.9.1.1.7.0"
SCANNER_BASE_OID = "1.3.6.1.4.1.2435.2.3.9"

IMPORTANT_KEYWORDS = [
    "toner",
    "jam",
    "count",
    "page",
    "status",
]

# 🔥 KNOWN OIDS (beste Qualität)
KNOWN_OIDS = {
    "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.1.2.63.33.1.1.18": "Pickup Roller",
    "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.1.2.63.33.1.1.19": "Separation Roller",
    "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.1.2.63.33.1.1.20": "Feed Roller",
    "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.54.2.2.1.3.3": "Scan Pages",
}

GOOD_SCANNER_OIDS = {
    # Scan Counter
    "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.54.2.2.1.3.3": "Scan Pages",

    # Roller Counter
    "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.1.2.63.33.1.1.18": "Pickup Roller",
    "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.1.2.63.33.1.1.19": "Separation Roller",
    "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.1.2.63.33.1.1.20": "Feed Roller",

    # Status (optional – später optimieren)
    "1.3.6.1.4.1.2435.2.3.9.1.1.2.9": "Device Status",
}

GOOD_PRINTER_OIDS = {
    # Seitenzähler
    "1.3.6.1.2.1.43.10.2.1.4.1.1": "Printed Pages",

    # Brother spezifisch
    "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.52": "Total Pages",

    # Toner Status
    "1.3.6.1.4.1.2435.2.3.9.1.1.2.10.1": "Toner Black",
    "1.3.6.1.4.1.2435.2.3.9.1.1.2.10.2": "Toner Cyan",
    "1.3.6.1.4.1.2435.2.3.9.1.1.2.10.3": "Toner Magenta",
    "1.3.6.1.4.1.2435.2.3.9.1.1.2.10.4": "Toner Yellow",

    # Fehler
    "1.3.6.1.4.1.2435.2.3.9.1.1.2.9": "Paper Jam",
}