DOMAIN = "brother_snmp_v2"

CONF_HOST = "host"
CONF_COMMUNITY = "community"

SCANNER_BASE_OID = "1.3.6.1.4.1.2435.2.3.9"

GOOD_SCANNER_OIDS = {
    "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.54.2.2.1.3.3": "Scan Pages",
    "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.1.2.63.33.1.1.18": "Pickup Roller",
    "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.1.2.63.33.1.1.19": "Separation Roller",
    "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.1.2.63.33.1.1.20": "Feed Roller",
    "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.1.0": "Serialnumber",
    "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.17.0": "Firmware",  
}

GOOD_PRINTER_OIDS = {
    "1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.52.1.1.3": "Printed Pages",
    "1.3.6.1.2.1.43.11.1.1.9.1.7": "Remaining pages of the cyan drum",
}