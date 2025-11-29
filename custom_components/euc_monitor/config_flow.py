"""Config flow for EUC Monitor integration."""
from __future__ import annotations

import logging
from typing import Any

from bleak import BleakScanner
from bleak.exc import BleakError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_MAC
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_MAC_ADDRESS, DOMAIN, EUC_SERVICE_UUID

_LOGGER = logging.getLogger(__name__)


class EUCMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EUC Monitor."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_devices: dict[str, str] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Check if user selected a device or wants manual entry
            if user_input.get("device") == "manual":
                return await self.async_step_manual()

            # Get the MAC address from selected device
            mac_address = user_input.get("device")
            if mac_address:
                # Set unique ID based on MAC address
                await self.async_set_unique_id(mac_address.lower().replace(":", ""))
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=self._discovered_devices.get(mac_address, mac_address),
                    data={CONF_MAC_ADDRESS: mac_address},
                )

        # Scan for devices
        self._discovered_devices = await self._discover_devices()

        if not self._discovered_devices:
            # No devices found, offer manual entry
            return await self.async_step_manual()

        # Build device list with manual option
        device_list = {mac: name for mac, name in self._discovered_devices.items()}
        device_list["manual"] = "Enter MAC address manually"

        data_schema = vol.Schema(
            {
                vol.Required("device"): vol.In(device_list),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual MAC address entry."""
        errors = {}

        if user_input is not None:
            mac_address = user_input[CONF_MAC_ADDRESS]

            # Validate MAC address format
            if not self._is_valid_mac(mac_address):
                errors[CONF_MAC_ADDRESS] = "invalid_mac"
            else:
                # Set unique ID based on MAC address
                await self.async_set_unique_id(mac_address.lower().replace(":", ""))
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"EUC {mac_address}",
                    data={CONF_MAC_ADDRESS: mac_address},
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_MAC_ADDRESS): str,
            }
        )

        return self.async_show_form(
            step_id="manual", data_schema=data_schema, errors=errors
        )

    async def _discover_devices(self) -> dict[str, str]:
        """Discover EUC devices via BLE."""
        devices = {}
        try:
            _LOGGER.debug("Scanning for EUC devices...")
            scanner = BleakScanner()
            discovered = await scanner.discover(timeout=5.0)

            for device in discovered:
                # Check if device name matches or has the service UUID
                if device.name and ("Leaperkim" in device.name or device.name.startswith("LK")):
                    devices[device.address] = device.name
                    _LOGGER.debug("Found device: %s (%s)", device.name, device.address)
                # Note: service_uuids might not be available in all BLE advertisements
                # so we primarily rely on name matching

        except BleakError as err:
            _LOGGER.error("Error during BLE scan: %s", err)

        return devices

    @staticmethod
    def _is_valid_mac(mac: str) -> bool:
        """Validate MAC address format."""
        import re
        # MAC address can be in format XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX
        mac_pattern = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")
        return bool(mac_pattern.match(mac))
