"""Chickadee — an open voice pipeline for Home Assistant.

The integration is the Assist-pipeline surface: conversation + STT + TTS
entities. The Chickadee add-on is the brain and engine router: it owns which
model/engine each entity actually talks to, plus key custody and the console
UI. They meet at the bridge (addon_bridge.py; contract in CONTRACTS.md).
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

PLATFORMS: list[Platform] = [Platform.CONVERSATION, Platform.STT, Platform.TTS]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
