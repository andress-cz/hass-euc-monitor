"""Data update coordinator for EUC Monitor."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

from bleak import BleakClient
from bleak_retry_connector import establish_connection
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, EUC_CHARACTERISTIC_UUID, EUC_SERVICE_UUID, UPDATE_INTERVAL
from .lynx_protocol import LynxDecoder

_LOGGER = logging.getLogger(__name__)


class EUCDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching EUC data from the device."""

    def __init__(
        self,
        hass: HomeAssistant,
        mac_address: str | None = None,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.mac_address = mac_address
        self.client: BleakClient | None = None
        self.decoder = LynxDecoder()
        self._device_name: str | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from EUC device."""
        try:
            # Ensure we're connected
            if not self.client or not self.client.is_connected:
                # Use a smaller timeout for connection attempts to avoid blocking
                # the coordinator update cycle for too long when device is off
                try:
                    async with asyncio.timeout(30):
                        await self._connect()
                except (asyncio.TimeoutError, Exception) as err:
                    _LOGGER.debug("Device not available (expected if off): %s", err)
                    # When device is off, we want to clear data so entities show as unavailable
                    self.decoder.clear_data()
                    return {}

            # Return the latest decoded data
            data = self.decoder.get_data()
            if data is None:
                return {}
            return data

        except Exception as err:
            _LOGGER.debug("Update failed: %s", err)
            self._handle_disconnect()
            raise UpdateFailed(f"BLE connection failed: {err}") from err

    def _handle_disconnect(self) -> None:
        """Helper to handle disconnection state."""
        if self.client:
            try:
                # Fire and forget disconnect
                self.hass.async_create_task(self.client.disconnect())
            except Exception:
                pass
            self.client = None
        self.decoder.clear_data()

    async def _connect(self) -> None:
        """Connect to the EUC device."""
        if not self.mac_address:
            raise UpdateFailed("No MAC address provided")

        _LOGGER.debug("Connecting to device at %s", self.mac_address)
        
        # Get the BLE device from Home Assistant's bluetooth integration
        device = bluetooth.async_ble_device_from_address(
            self.hass, self.mac_address, connectable=True
        )
        
        if not device:
            raise UpdateFailed(f"Could not find device with MAC address {self.mac_address}")

        self._device_name = device.name or device.address
        
        try:
            self.client = await establish_connection(
                BleakClient,
                device,
                self._device_name,
                disconnected_callback=self._on_disconnect,
            )
        except Exception as err:
            raise UpdateFailed(f"Failed to connect to {self.mac_address}: {err}") from err

        # Subscribe to notifications
        await self.client.start_notify(
            EUC_CHARACTERISTIC_UUID, self._notification_handler
        )
        _LOGGER.info("Connected to EUC device: %s", self._device_name)

    def _on_disconnect(self, client: BleakClient) -> None:
        """Handle disconnection."""
        _LOGGER.info("Disconnected from %s", self.mac_address)
        self._handle_disconnect()
        # Notify coordinator that data is now empty
        self.async_set_updated_data({})

    def _notification_handler(self, sender, data: bytearray) -> None:
        """Handle BLE notifications."""
        self.decoder.process_data(data)
        # Trigger a state update when new data arrives
        self.async_set_updated_data(self.decoder.get_data() or {})

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        if self.client and self.client.is_connected:
            try:
                await self.client.disconnect()
            except Exception as err:
                _LOGGER.debug("Error disconnecting: %s", err)
            finally:
                self.client = None

    @property
    def device_name(self) -> str:
        """Return the device name."""
        return self._device_name or "EUC"
