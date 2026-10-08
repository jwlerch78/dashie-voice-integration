"""The Gemini STT entity names its engine in the request (D5).

HA's /api/stt carries no caller identity, so a tablet's per-device engine choice can
only reach the add-on as the entity it targets. These tests pin that the Gemini entity
posts to /api/voice/stt?engine=gemini, that the default entity still posts to the bare
path (so the add-on keeps choosing from its own config), and that both behave the same
apart from that.
"""
from unittest.mock import AsyncMock, patch

from homeassistant.components import stt

from custom_components.dashie_voice import stt as dv_stt
from custom_components.dashie_voice.const import (
    ADDON_STT_PATH,
    UNIQUE_ID_STT,
    UNIQUE_ID_STT_GEMINI,
)

META = stt.SpeechMetadata(
    language="en",
    format=stt.AudioFormats.WAV,
    codec=stt.AudioCodecs.PCM,
    bit_rate=stt.AudioBitRates.BITRATE_16,
    sample_rate=stt.AudioSampleRates.SAMPLERATE_16000,
    channel=stt.AudioChannels.CHANNEL_MONO,
)


async def _stream():
    yield b"\x00\x01" * 1600


async def _run(hass, entity):
    entity.hass = hass
    call = AsyncMock(return_value=(200, b'{"text": "lights on"}', "application/json"))
    with patch.object(dv_stt, "call_addon_raw", call):
        result = await entity.async_process_audio_stream(META, _stream())
    return result, call


async def test_gemini_entity_posts_with_engine_query(hass):
    result, call = await _run(hass, dv_stt.DashieVoiceGeminiSttEntity())
    assert call.await_count == 1
    assert call.await_args.args[1] == ADDON_STT_PATH + "?engine=gemini"
    body = call.await_args.args[2]
    assert body[:4] == b"RIFF" and body[8:12] == b"WAVE"  # same WAV wrapping as the default entity
    assert result.result == stt.SpeechResultState.SUCCESS
    assert result.text == "lights on"


async def test_default_entity_path_unchanged(hass):
    _result, call = await _run(hass, dv_stt.DashieVoiceSttEntity())
    assert call.await_args.args[1] == ADDON_STT_PATH  # no query: the add-on picks the engine


async def test_unique_ids_are_distinct_and_stable(hass):
    # The Android app resolves the Gemini entity by this unique_id (a user may rename the
    # entity_id), so it is a cross-repo contract.
    assert dv_stt.DashieVoiceGeminiSttEntity().unique_id == UNIQUE_ID_STT_GEMINI == "dashie_voice_stt_gemini"
    assert dv_stt.DashieVoiceSttEntity().unique_id == UNIQUE_ID_STT
    assert UNIQUE_ID_STT != UNIQUE_ID_STT_GEMINI


async def test_gemini_entity_reports_add_on_error_as_error(hass):
    entity = dv_stt.DashieVoiceGeminiSttEntity()
    entity.hass = hass
    call = AsyncMock(return_value=(503, b'{"error": "gemini_stt_no_key"}', "application/json"))
    with patch.object(dv_stt, "call_addon_raw", call):
        result = await entity.async_process_audio_stream(META, _stream())
    assert result.result == stt.SpeechResultState.ERROR
