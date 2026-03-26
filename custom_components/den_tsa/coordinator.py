"""Coordinator for DEN TSA WebSocket updates."""

import asyncio
import json
import logging
from dataclasses import dataclass

import websockets

from homeassistant.core import HomeAssistant, callback

from .const import WS_URL, WS_HEADERS

_LOGGER = logging.getLogger(__name__)


@dataclass
class LaneData:
    """Lane wait time data."""
    checkpoint: str
    lane_type: str
    wait_time: float | None
    closed: bool


def parse_range(wait_time: str) -> float | None:
    """Convert '0-4', '1-5' ranges to midpoint."""
    if not wait_time or wait_time == "unknown":
        return None

    if "-" in wait_time:
        try:
            parts = wait_time.split("-")
            return (float(parts[0]) + float(parts[1])) / 2
        except (ValueError, IndexError):
            return None

    try:
        return float(wait_time)
    except ValueError:
        return None


def extract_lanes(data: dict) -> list[LaneData]:
    """Extract lane data from WebSocket message."""
    lanes = []

    for checkpoint in data.get("data", []):
        checkpoint_name = checkpoint.get("title", "")

        for lane in checkpoint.get("lanes", []):
            if lane.get("hide_lane", False):
                continue

            lane_type = lane.get("title", "")
            wait_time = parse_range(lane.get("wait_time", ""))

            lanes.append(
                LaneData(
                    checkpoint=checkpoint_name,
                    lane_type=lane_type,
                    wait_time=wait_time,
                    closed=lane.get("closed", False),
                )
            )

    return lanes


class DenTSAUpdateCoordinator:
    """WebSocket-based coordinator for DEN TSA wait times."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._data: dict[str, float] = {}
        self._listeners: list[callable] = []
        self._ws_task: asyncio.Task | None = None
        self._stop_requested = asyncio.Event()

    async def _async_listen_websocket(self) -> None:
        """Maintain WebSocket connection and process updates."""
        while not self._stop_requested.is_set():
            try:
                _LOGGER.info("Connecting to DEN TSA WebSocket...")
                async with websockets.connect(
                    WS_URL, additional_headers=WS_HEADERS
                ) as ws:
                    _LOGGER.info("Connected to DEN TSA WebSocket")

                    # Join wait-times channel
                    await ws.send(
                        json.dumps({"action": "joinchannel", "channel": "wait-times"})
                    )

                    # Listen for updates
                    async for message in ws:
                        try:
                            data = json.loads(message)

                            if "data" in data:
                                lanes = extract_lanes(data)

                                # Build key: "East Security Standard" → value
                                self._data = {
                                    f"{lane.checkpoint} {lane.lane_type}": (
                                        lane.wait_time if lane.wait_time is not None else 0
                                    )
                                    for lane in lanes
                                }

                                _LOGGER.debug(
                                    "Updated wait times: %s lanes", len(self._data)
                                )

                                # Notify listeners (sensors)
                                for listener in self._listeners:
                                    listener()

                        except json.JSONDecodeError:
                            _LOGGER.warning("Failed to parse WebSocket message")

            except Exception as err:
                if not self._stop_requested.is_set():
                    _LOGGER.error("WebSocket error: %s. Reconnecting...", err)
                    await asyncio.sleep(5)

    async def async_config_entry_first_refresh(self) -> None:
        """Initial connection setup."""
        # Start WebSocket listener
        self._ws_task = asyncio.create_task(self._async_listen_websocket())

    async def async_shutdown(self) -> None:
        """Cleanup on unload."""
        _LOGGER.info("Shutting down DEN TSA WebSocket connection")
        self._stop_requested.set()

        if self._ws_task:
            self._ws_task.cancel()
            try:
                await self._ws_task
            except asyncio.CancelledError:
                pass

    def get_lane_value(self, checkpoint: str, lane_type: str) -> float | None:
        """Get wait time for specific checkpoint/lane."""
        key = f"{checkpoint} {lane_type}"
        return self._data.get(key)

    @callback
    def async_add_listener(self, listener: callable) -> None:
        """Add a listener for data updates."""
        self._listeners.append(listener)
