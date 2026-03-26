"""Sensor entities for DEN TSA Wait Times."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DenTSAUpdateCoordinator


@dataclass(frozen=True)
class DenTSASensorEntityDescription(SensorEntityDescription):
    checkpoint: str = ""
    lane_type: str = ""


SENSORS: tuple[DenTSASensorEntityDescription, ...] = (
    DenTSASensorEntityDescription(
        key="east_standard_wait",
        name="DEN TSA East Standard Wait",
        icon="mdi:shield-account",
        native_unit_of_measurement="min",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        checkpoint="East Security",
        lane_type="Standard",
    ),
    DenTSASensorEntityDescription(
        key="east_precheck_wait",
        name="DEN TSA East PreCheck Wait",
        icon="mdi:shield-star",
        native_unit_of_measurement="min",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        checkpoint="East Security",
        lane_type="PreCheck",
    ),
    DenTSASensorEntityDescription(
        key="west_standard_wait",
        name="DEN TSA West Standard Wait",
        icon="mdi:shield-account",
        native_unit_of_measurement="min",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        checkpoint="West Security",
        lane_type="Standard",
    ),
    DenTSASensorEntityDescription(
        key="west_precheck_wait",
        name="DEN TSA West PreCheck Wait",
        icon="mdi:shield-star",
        native_unit_of_measurement="min",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        checkpoint="West Security",
        lane_type="PreCheck",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: DenTSAUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        DenTSASensor(coordinator, description) for description in SENSORS
    )


class DenTSASensor(SensorEntity):
    """A single TSA wait time sensor."""

    entity_description: DenTSASensorEntityDescription

    def __init__(
        self,
        coordinator: DenTSAUpdateCoordinator,
        description: DenTSASensorEntityDescription,
    ) -> None:
        self._coordinator = coordinator
        self.entity_description = description
        self._attr_unique_id = f"den_tsa_{description.key}"

    async def async_added_to_hass(self) -> None:
        """Register listener when entity is added."""
        self._coordinator.async_add_listener(self._handle_coordinator_update)

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()

    @property
    def native_value(self) -> float | None:
        return self._coordinator.get_lane_value(
            self.entity_description.checkpoint,
            self.entity_description.lane_type,
        )
