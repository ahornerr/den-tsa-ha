"""Config flow for DEN TSA Wait Times integration."""

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow
from homeassistant.data_entry_flow import FlowResultType, FlowResult
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN


class DenTSAConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for DEN TSA."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="Denver Airport TSA Wait Times")

        return self.async_show_form(step_id="user")
