"""Config flow for Chickadee.

Deliberately thin: engine configuration (cloud / BYOK / local, keys, fallbacks)
lives in the Chickadee add-on's console — the integration is the Assist-pipeline
surface. The flow checks the add-on is reachable and names the assistant.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .addon_bridge import ping_addon
from .const import CONF_ASSISTANT_NAME, DEFAULT_ASSISTANT_NAME, DOMAIN

_USER_SCHEMA = vol.Schema(
    {vol.Optional(CONF_ASSISTANT_NAME, default=DEFAULT_ASSISTANT_NAME): str}
)


class ChickadeeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Single-instance flow: reachability probe + assistant name."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        errors: dict[str, str] = {}
        if user_input is not None:
            # Warn-don't-block: the add-on may be installed after the integration.
            # The conversation entity DROP-logs loudly per turn until it appears.
            if not await ping_addon(self.hass):
                errors["base"] = "addon_unreachable"
            if not errors or user_input.get("ignore_addon"):
                name = (user_input.get(CONF_ASSISTANT_NAME) or DEFAULT_ASSISTANT_NAME).strip()
                return self.async_create_entry(
                    title=name, data={CONF_ASSISTANT_NAME: name}
                )

        schema = _USER_SCHEMA
        if errors:
            schema = _USER_SCHEMA.extend({vol.Optional("ignore_addon", default=False): bool})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
