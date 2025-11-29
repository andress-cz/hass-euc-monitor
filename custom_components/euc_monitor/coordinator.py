"""Data update coordinator for EUC Monitor."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

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
                await self._connect()

            # Return the latest decoded data
            data = self.decoder.get_data()
            if data is None:
                # No data received yet, return empty dict
                return {}
            return data

        except BleakError as err:
            # Disconnect and raise UpdateFailed
            if self.client:
                try:
                    await self.client.disconnect()
                except Exception:
                    pass
                self.client = None
            raise UpdateFailed(f"BLE connection failed: {err}") from err

    async def _connect(self) -> None:
        """Connect to the EUC device."""
        device = None

        if self.mac_address:
            # Connect to specific MAC address
            _LOGGER.debug("Connecting to device at %s", self.mac_address)
            try:
                self.client = BleakClient(self.mac_address)
                await self.client.connect()
                self._device_name = self.client.address
            except BleakError as err:
                raise UpdateFailed(f"Failed to connect to {self.mac_address}") from err
        else:
            # Scan for device
            _LOGGER.debug("Scanning for EUC device...")
            async with BleakScanner() as scanner:
                async for d, a in scanner.advertisement_data():
                    if d.name and ("Leaperkim" in d.name or d.name.startswith("LK")):
                        _LOGGER.debug("Found %s (%s)", d.name, d.address)
                        device = d
                        break
                    if EUC_SERVICE_UUID in a.service_uuids:
                        _LOGGER.debug("Found device with EUC Service (%s)", d.address)
                        device = d
                        break

            if not device:
                raise UpdateFailed("No EUC device found")

            self._device_name = device.name or device.address
            self.client = BleakClient(device)
            await self.client.connect()

        # Subscribe to notifications
        await self.client.start_notify(
            EUC_CHARACTERISTIC_UUID, self._notification_handler
        )
        _LOGGER.info("Connected to EUC device: %s", self._device_name)

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
