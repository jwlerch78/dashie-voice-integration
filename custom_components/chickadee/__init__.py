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

from .addon_bridge import set_bridge_config
from .const import CONF_BRIDGE_HOST, CONF_BRIDGE_PORT, CONF_BRIDGE_SECRET
from .pipeline import async_ensure_pipeline

PLATFORMS: list[Platform] = [Platform.CONVERSATION, Platform.STT, Platform.TTS]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Bridge credentials from Supervisor discovery (primary channel; empty on
    # pre-discovery installs → file-read fallback stays in charge). Discovery
    # refreshes update the entry → reload → this re-primes with the new secret.
    set_bridge_config(
        entry.data.get(CONF_BRIDGE_SECRET),
        entry.data.get(CONF_BRIDGE_HOST),
        entry.data.get(CONF_BRIDGE_PORT),
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    # After platform setup so the entities exist in the registry. Best-effort:
    # a failure DROP-warns inside, never blocks voice.
    await async_ensure_pipeline(hass, entry)
    # Options-flow edits (assistant rename) apply via reload.
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
