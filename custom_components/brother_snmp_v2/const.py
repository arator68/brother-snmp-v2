DOMAIN = "brother_snmp_v2"

CONF_HOST = "host"
CONF_COMMUNITY = "community"

IDENTITY_OID = "1.3.6.1.4.1.2435.2.3.9.1.1.7.0"

DEVICE_PROFILES = {
    "SCANNER": {
        "sensors": [
            {
                "key": "pages",
                "name": "Scanned Pages",
                "oid": "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.54.2.2.1.3.3",
            },
            {
                "key": "roller",
                "name": "Roller Counter",
                "oid": "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.1.2.63.33.1.1.18",
            },
        ]
    },

    "PRINTER": {
        "sensors": [
            {
                "key": "pages",
                "name": "Printed Pages",
                "oid": "1.3.6.1.2.1.43.10.2.1.4.1.1",
            }
        ]
    },

    "DEFAULT": {
        "sensors": []
    }
}