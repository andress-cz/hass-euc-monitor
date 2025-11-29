"""Constants for the EUC Monitor integration."""

DOMAIN = "euc_monitor"

# BLE UUIDs
EUC_SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
EUC_CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

# Configuration
CONF_MAC_ADDRESS = "mac_address"

# Update interval
UPDATE_INTERVAL = 1  # seconds

# Device info
MANUFACTURER = "Leaperkim"
MODEL = "Veteran Lynx"

# Sensor definitions with entity_enabled_default flag
SENSOR_TYPES = {
    # Core sensors (enabled by default)
    "voltage": {
        "name": "Battery Voltage",
        "unit": "V",
        "icon": "mdi:battery",
        "device_class": "voltage",
        "state_class": "measurement",
        "enabled_default": True,
    },
    "speed": {
        "name": "Speed",
        "unit": "km/h",
        "icon": "mdi:speedometer",
        "device_class": "speed",
        "state_class": "measurement",
        "enabled_default": True,
    },
    "current": {
        "name": "Current",
        "unit": "A",
        "icon": "mdi:current-ac",
        "device_class": "current",
        "state_class": "measurement",
        "enabled_default": True,
    },
    "temperature": {
        "name": "Temperature",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "state_class": "measurement",
        "enabled_default": True,
    },
    "pitch_angle": {
        "name": "Pitch Angle",
        "unit": "°",
        "icon": "mdi:angle-acute",
        "state_class": "measurement",
        "enabled_default": True,
    },
    "trip_distance": {
        "name": "Trip Distance",
        "unit": "km",
        "icon": "mdi:map-marker-distance",
        "device_class": "distance",
        "state_class": "total_increasing",
        "enabled_default": True,
    },
    "total_distance": {
        "name": "Total Distance",
        "unit": "km",
        "icon": "mdi:counter",
        "device_class": "distance",
        "state_class": "total_increasing",
        "enabled_default": True,
    },
    # BMS aggregated sensors (enabled by default)
    "bms1_voltage": {
        "name": "BMS 1 Voltage",
        "unit": "V",
        "icon": "mdi:battery-high",
        "device_class": "voltage",
        "state_class": "measurement",
        "enabled_default": True,
    },
    "bms1_min_cell": {
        "name": "BMS 1 Min Cell",
        "unit": "V",
        "icon": "mdi:battery-low",
        "device_class": "voltage",
        "state_class": "measurement",
        "enabled_default": True,
    },
    "bms1_max_cell": {
        "name": "BMS 1 Max Cell",
        "unit": "V",
        "icon": "mdi:battery-high",
        "device_class": "voltage",
        "state_class": "measurement",
        "enabled_default": True,
    },
    "bms1_avg_cell": {
        "name": "BMS 1 Avg Cell",
        "unit": "V",
        "icon": "mdi:battery-medium",
        "device_class": "voltage",
        "state_class": "measurement",
        "enabled_default": True,
    },
    "bms1_delta": {
        "name": "BMS 1 Delta",
        "unit": "V",
        "icon": "mdi:delta",
        "device_class": "voltage",
        "state_class": "measurement",
        "enabled_default": True,
    },
    "bms2_voltage": {
        "name": "BMS 2 Voltage",
        "unit": "V",
        "icon": "mdi:battery-high",
        "device_class": "voltage",
        "state_class": "measurement",
        "enabled_default": True,
    },
    "bms2_min_cell": {
        "name": "BMS 2 Min Cell",
        "unit": "V",
        "icon": "mdi:battery-low",
        "device_class": "voltage",
        "state_class": "measurement",
        "enabled_default": True,
    },
    "bms2_max_cell": {
        "name": "BMS 2 Max Cell",
        "unit": "V",
        "icon": "mdi:battery-high",
        "device_class": "voltage",
        "state_class": "measurement",
        "enabled_default": True,
    },
    "bms2_avg_cell": {
        "name": "BMS 2 Avg Cell",
        "unit": "V",
        "icon": "mdi:battery-medium",
        "device_class": "voltage",
        "state_class": "measurement",
        "enabled_default": True,
    },
    "bms2_delta": {
        "name": "BMS 2 Delta",
        "unit": "V",
        "icon": "mdi:delta",
        "device_class": "voltage",
        "state_class": "measurement",
        "enabled_default": True,
    },
    # Advanced sensors (disabled by default)
    "hpwm": {
        "name": "HPWM",
        "unit": "%",
        "icon": "mdi:gauge",
        "state_class": "measurement",
        "enabled_default": False,
    },
    "ride_mode": {
        "name": "Ride Mode",
        "icon": "mdi:cog",
        "enabled_default": False,
    },
    "speed_alert": {
        "name": "Speed Alert",
        "unit": "km/h",
        "icon": "mdi:alarm-light",
        "enabled_default": False,
    },
    "speed_tiltback": {
        "name": "Tiltback Speed",
        "unit": "km/h",
        "icon": "mdi:angle-acute",
        "enabled_default": False,
    },
    "auto_off": {
        "name": "Auto Off Timer",
        "unit": "s",
        "icon": "mdi:timer",
        "device_class": "duration",
        "enabled_default": False,
    },
    "charge_mode": {
        "name": "Charge Mode",
        "icon": "mdi:battery-charging",
        "enabled_default": False,
    },
    "version": {
        "name": "Firmware Version",
        "icon": "mdi:chip",
        "entity_category": "diagnostic",
        "enabled_default": False,
    },
    "bms1_current": {
        "name": "BMS 1 Current",
        "unit": "A",
        "icon": "mdi:current-ac",
        "device_class": "current",
        "state_class": "measurement",
        "enabled_default": False,
    },
    "bms2_current": {
        "name": "BMS 2 Current",
        "unit": "A",
        "icon": "mdi:current-ac",
        "device_class": "current",
        "state_class": "measurement",
        "enabled_default": False,
    },
}

# BMS Temperature sensors (disabled by default)
for bms in [1, 2]:
    for temp_idx in range(6):
        SENSOR_TYPES[f"bms{bms}_temp{temp_idx}"] = {
            "name": f"BMS {bms} Temperature {temp_idx + 1}",
            "unit": "°C",
            "icon": "mdi:thermometer",
            "device_class": "temperature",
            "state_class": "measurement",
            "enabled_default": False,
        }

# Individual cell voltages (disabled by default)
for bms in [1, 2]:
    for cell_idx in range(36):
        SENSOR_TYPES[f"bms{bms}_cell{cell_idx}"] = {
            "name": f"BMS {bms} Cell {cell_idx + 1}",
            "unit": "V",
            "icon": "mdi:battery",
            "device_class": "voltage",
            "state_class": "measurement",
            "enabled_default": False,
        }
