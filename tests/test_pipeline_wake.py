"""Wiring the wake word into an existing Dashie Voice pipeline.

When the wake-word entity appears after the pipeline was created, the integration sets
the pipeline's wake word. Home Assistant's pipeline store treats an update as a full
replacement (every field is required), so sending only the two wake keys failed with
KeyError 'stt_engine' on every attempt, was logged as a DROP, and the wake word was never
set. These tests use the real pipeline store and pin that the wake word is stored AND that
nothing else about the pipeline changes.
"""
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from homeassistant.components.assist_pipeline.pipeline import PipelineStorageCollection
from homeassistant.helpers.storage import Store

from custom_components.dashie_voice import pipeline as dv_pipeline, satellite_wake

ENGINES = {
    "conversation_engine": "conversation.dashie_voice",
    "stt_engine": "stt.dashie_voice",
    "tts_engine": "tts.dashie_voice",
}
SETTINGS = {
    **ENGINES,
    "conversation_language": "en",
    "language": "en",
    "name": "Dashie",
    "stt_language": "en-US",
    "tts_language": "en-US",
    "tts_voice": "nova",
    "wake_word_entity": None,
    "wake_word_id": None,
    "prefer_local_intents": False,
}


STORE_KEY = "assist_pipeline.pipelines.test"


@pytest.fixture
def make_store(hass, hass_storage):
    """A real pipeline store holding the given pipeline, served where HA reads it."""
    patches = []

    async def _make(settings: dict):
        item = {**settings, "id": "01DASHIEVOICETEST"}
        hass_storage[STORE_KEY] = {
            "version": 1, "minor_version": 1, "key": STORE_KEY,
            "data": {"items": [item], "preferred_item": item["id"]},
        }
        collection = PipelineStorageCollection(Store(hass, 1, STORE_KEY))
        await collection.async_load()
        data = SimpleNamespace(pipeline_store=collection)
        hass.data["assist_pipeline"] = data

        async def _setup_store(_hass):
            return data

        for p in (
            patch("homeassistant.components.assist_pipeline.pipeline.async_setup_pipeline_store",
                  _setup_store),
            patch.object(dv_pipeline, "_our_entity_ids", return_value=set(ENGINES.values())),
        ):
            p.start()
            patches.append(p)
        return collection, collection.data[item["id"]]

    yield _make
    for p in patches:
        p.stop()


async def test_wake_word_is_stored_and_nothing_else_changes(hass, make_store, caplog):
    store, before = await make_store(SETTINGS)

    done = await dv_pipeline._apply_wake_to_pipeline(hass, "wake_word.dashie", "hey_dashie")

    assert done is True
    assert not [r for r in caplog.records if "DROP:" in r.getMessage()]
    after = store.data[before.id]
    assert after.wake_word_entity == "wake_word.dashie"
    assert after.wake_word_id == "hey_dashie"
    unchanged = {k: v for k, v in before.to_json().items() if not k.startswith("wake_word")}
    assert {k: v for k, v in after.to_json().items() if not k.startswith("wake_word")} == unchanged


async def test_an_already_wired_pipeline_is_left_alone(hass, make_store):
    store, wired = await make_store(
        {**SETTINGS, "wake_word_entity": "wake_word.users_choice", "wake_word_id": "okay_nabu"}
    )

    with patch.object(store, "async_update_item") as update:
        done = await dv_pipeline._apply_wake_to_pipeline(hass, "wake_word.dashie", "hey_dashie")

    assert done is True
    update.assert_not_called()
    assert store.data[wired.id].wake_word_entity == "wake_word.users_choice"


async def test_wake_is_wired_when_the_wake_entity_already_exists_at_setup(hass, make_store):
    """The self-heal must also cover the case where nothing is left to wait for.

    A pipeline is only given a wake word when it is CREATED, so an existing pipeline with
    wake unset relies on the watcher. The watcher used to give up whenever a wake_word
    entity was already present ("already wired at creation"), which is exactly the state of
    a box whose wake service starts before the integration: nothing ever wired it.
    """
    store, before = await make_store(SETTINGS)
    hass.states.async_set("wake_word.openwakeword", "2026-09-17T00:00:00+00:00")
    wake_id = next(iter(satellite_wake.WAKE_MODELS))
    entry = MockConfigEntry(domain="dashie_voice", data={})
    entry.add_to_hass(hass)

    await dv_pipeline.async_wire_wake_when_ready(hass, entry, wake_id)
    await hass.async_block_till_done()

    after = store.data[before.id]
    assert after.wake_word_entity == "wake_word.openwakeword"
    assert after.wake_word_id == wake_id
