# EUC Monitor for Home Assistant

Home Assistant custom integration for monitoring Leaperkim Veteran Lynx electric unicycles via Bluetooth Low Energy (BLE).

## Features

- **Automatic Discovery**: Automatically discovers your Leaperkim Lynx EUC when in BLE range
- **Manual Configuration**: Option to manually enter MAC address if auto-discovery fails
- **Real-time Telemetry**: Monitors 100+ data points including:
  - Core metrics: Battery voltage, speed, current, temperature
  - Distance tracking: Trip and total distance (odometer)
  - Advanced data: Pitch angle, HPWM, ride mode, firmware version
  - Dual SmartBMS: Individual cell voltages (72 cells), min/max/avg/delta, temperatures, currents
- **Smart Availability**: Sensors automatically become available/unavailable based on BLE connectivity
- **Automation Ready**: All sensors support state change triggers for powerful automations

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/sulco/hass-euc`
6. Select category: "Integration"
7. Click "Add"
8. Find "EUC Monitor" in HACS and click "Download"
9. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/euc_monitor` directory to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "EUC Monitor"
4. Select your EUC from the discovered devices, or choose manual entry to enter MAC address
5. Click Submit

The integration will create a device with all available sensors.

## Available Sensors

### Enabled by Default

**Core Sensors:**
- Battery Voltage (V)
- Speed (km/h)
- Current (A)
- Temperature (°C)
- Pitch Angle (°)
- Trip Distance (km)
- Total Distance (km)

**BMS Sensors (for each BMS 1 & 2):**
- BMS Voltage (V) - sum of all cells
- BMS Min Cell (V)
- BMS Max Cell (V)
- BMS Avg Cell (V)
- BMS Delta (V) - difference between min and max

### Disabled by Default

These sensors are created but disabled. You can enable them in the entity settings:

- HPWM (%)
- Ride Mode
- Speed Alert (km/h)
- Tiltback Speed (km/h)
- Auto Off Timer (s)
- Charge Mode
- Firmware Version
- BMS Currents (A) - for each BMS
- BMS Temperatures (°C) - 6 per BMS (12 total)
- Individual Cell Voltages (V) - 36 per BMS (72 total)

## Example Automations

### Low Battery Alert

```yaml
automation:
  - alias: "EUC Low Battery Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.euc_battery_voltage
        below: 100
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "EUC Low Battery"
          message: "Battery is at {{ states('sensor.euc_battery_voltage') }}V"
```

### Speed Warning

```yaml
automation:
  - alias: "EUC Speed Warning"
    trigger:
      - platform: numeric_state
        entity_id: sensor.euc_speed
        above: 50
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Slow Down!"
          message: "You're going {{ states('sensor.euc_speed') }} km/h"
          data:
            priority: high
```

### BMS Cell Balance Alert

```yaml
automation:
  - alias: "EUC Cell Imbalance Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.euc_bms_1_delta
        above: 0.05
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "BMS Cell Imbalance"
          message: "BMS 1 delta is {{ states('sensor.euc_bms_1_delta') }}V - consider balancing"
```

### Daily Distance Tracker

```yaml
automation:
  - alias: "EUC Daily Distance Report"
    trigger:
      - platform: time
        at: "23:00:00"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Daily Riding Summary"
          message: >
            Today you rode {{ states('sensor.euc_trip_distance') }} km.
            Total odometer: {{ states('sensor.euc_total_distance') }} km.
```

### Connection Status Notification

```yaml
automation:
  - alias: "EUC Connected"
    trigger:
      - platform: state
        entity_id: sensor.euc_battery_voltage
        from: "unavailable"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "EUC Connected"
          message: "Your EUC is now in range and connected"

  - alias: "EUC Disconnected"
    trigger:
      - platform: state
        entity_id: sensor.euc_battery_voltage
        to: "unavailable"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "EUC Disconnected"
          message: "Your EUC is out of range"
```

## Troubleshooting

### Device Not Found During Setup

1. Make sure your EUC is powered on
2. Ensure Bluetooth is enabled on your Home Assistant host
3. Check that you're within BLE range (typically 10-30 feet)
4. Try using manual MAC address entry
5. Check Home Assistant logs for BLE scanning errors

### Sensors Show "Unavailable"

- The EUC is out of BLE range or powered off
- This is normal behavior - sensors will automatically reconnect when the device comes back in range
- Check Home Assistant logs for connection errors

### No Data Updates

1. Verify the EUC is powered on and in range
2. Check Home Assistant logs for errors
3. Try reloading the integration: Settings → Devices & Services → EUC Monitor → Three dots → Reload

### Finding MAC Address

On most systems, you can find your EUC's MAC address by:
1. Running `bluetoothctl` in terminal
2. Type `scan on`
3. Look for your device (usually starts with "Leaperkim" or "LK")
4. Note the MAC address (format: XX:XX:XX:XX:XX:XX)

## Technical Details

### Protocol

This integration uses the Leaperkim Veteran protocol over BLE:
- Service UUID: `0000ffe0-0000-1000-8000-00805f9b34fb`
- Characteristic UUID: `0000ffe1-0000-1000-8000-00805f9b34fb`
- Data is decoded according to the Veteran protocol specification
- CRC32 validation ensures data integrity

### Update Frequency

- Sensors update approximately every 1 second when connected
- BLE notifications trigger immediate updates when new data arrives

## Credits

Based on reverse engineering of the Leaperkim Android app and Veteran protocol.

## License

MIT License - feel free to use and modify as needed.

## Support

For issues, feature requests, or questions, please open an issue on GitHub.
