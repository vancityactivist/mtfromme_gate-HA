"""Config flow for the Mt Fromme Gate integration."""
from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN


class MtFrommeGateConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mt Fromme Gate.

    There's nothing to configure — DNV's page is a fixed public URL — so
    this just confirms setup and creates a single entry.
    """

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="Mt Fromme Gate", data={})

        return self.async_show_form(step_id="user")
