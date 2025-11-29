# Quick Start Guide - EUC Monitor Integration

## Installation Steps

1. **Copy Integration to Home Assistant**
   ```bash
   # From the hass-euc directory, copy the integration to your HA config:
   cp -r custom_components/euc_monitor /path/to/homeassistant/config/custom_components/
   ```

2. **Restart Home Assistant**
   - Go to Settings → System → Restart
   - Or restart via command line/supervisor

3. **Add Integration**
   - Go to Settings → Devices & Services
   - Click "+ Add Integration"
   - Search for "EUC Monitor"
   - Follow the setup wizard

4. **Configure Device**
   - **Option A**: Select your EUC from the discovered devices list
   - **Option B**: Choose "Enter MAC address manually" if auto-discovery fails

5. **Verify Installation**
   - Check that a device card appears for your EUC
   - Verify sensors are populated (voltage, speed, distance, etc.)
   - Turn off EUC and verify sensors show "unavailable"
   - Turn on EUC and verify sensors reconnect

## Finding Your EUC's MAC Address

If auto-discovery doesn't work, you can find the MAC address:

**Linux/Mac:**
```bash
bluetoothctl
scan on
# Look for "Leaperkim" or "LK" devices
# Format: XX:XX:XX:XX:XX:XX
```

**Home Assistant Terminal:**
```bash
ha bluetooth devices
# Look for your EUC in the list
```

## Enabling Additional Sensors

By default, only core sensors are enabled. To enable more:

1. Go to Settings → Devices & Services → EUC Monitor
2. Click on your device
3. Find disabled sensors (grayed out)
4. Click each sensor you want
5. Click the settings icon
6. Enable "Entity enabled"

**Useful sensors to enable:**
- HPWM (power output percentage)
- Individual BMS cell voltages (for detailed monitoring)
- BMS temperatures (thermal monitoring)
- Ride Mode (pedal firmness setting)

## Creating Your First Automation

**Low Battery Alert:**

1. Go to Settings → Automations & Scenes
2. Click "+ Create Automation"
3. Choose "Start with an empty automation"
4. Add trigger:
   - Type: Numeric state
   - Entity: `sensor.euc_battery_voltage`
   - Below: 100 (or your preferred threshold)
5. Add action:
   - Type: Send notification
   - Message: "EUC battery is low!"
6. Save

## Troubleshooting

**Integration doesn't appear:**
- Check Home Assistant logs for errors
- Verify `custom_components/euc_monitor/` directory exists
- Ensure all files are present (run `ls custom_components/euc_monitor/`)

**No devices found:**
- Power on your EUC
- Ensure Bluetooth is enabled on HA host
- Check you're within BLE range (typically 10-30 feet)
- Try manual MAC address entry

**Sensors show unavailable:**
- This is normal when EUC is off or out of range
- Sensors will automatically reconnect when EUC is back in range
- Check HA logs for connection errors

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check example automations in README
- Customize sensor visibility based on your needs
- Set up dashboards with your favorite sensors
- Create safety automations (speed alerts, low battery, etc.)

## Support

For issues or questions, see the [Troubleshooting section in README.md](README.md#troubleshooting)
