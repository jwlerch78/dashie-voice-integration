"""Path K: the tablet's Gemini TTS streamed through HA from the add-on (tts_stream_view.py).

Driven against a FAKE add-on over real HTTP (aiohttp), so the bytes really cross two sockets. Pins:
  - 200: the add-on's PCM arrives in order and IS STREAMED: the first chunk reaches the tablet before
    the add-on has sent the last one (a buffering view would deliver nothing until the end);
  - only the audio-describing headers cross;
  - 409 no_key / key_failed pass through VERBATIM (the tablet routes on the body);
  - the add-on is asked with stream:true and the tablet's voice;
  - add-on unreachable → 503 {reason: addon_unavailable}; bad input → 400 without calling the add-on.

No pytest-homeassistant fixtures are needed, so it also runs directly:
    PYTHONPATH=. <python with homeassistant> tests/test_tts_stream_view.py
"""
from __future__ import annotations

import asyncio
import json
import time
from unittest.mock import patch

from aiohttp import ClientSession, TCPConnector, ThreadedResolver, web

try:  # Under pytest-homeassistant, pytest_socket blocks sockets; this file's whole point is REAL TCP (two sockets).
    import pytest
    pytestmark = pytest.mark.enable_socket
except ImportError:  # run directly without pytest
    pass
from aiohttp.test_utils import TestServer

from custom_components.dashie_voice import addon_bridge
from custom_components.dashie_voice.const import BRIDGE_HEADER
from custom_components.dashie_voice.tts_stream_view import DashieVoiceTtsStreamView

CHUNKS = [b"\x01\x02\x03\x04", b"\x05\x06\x07\x08", b"\x09\x0a"]
GAP_S = 0.3


def _session() -> ClientSession:
    """A test client session on aiohttp's THREADED resolver. The default async resolver (pycares) starts a
    process-global shutdown thread when a session closes, and pytest-homeassistant fails the test at teardown
    for that lingering thread. Test harness only: production uses HA's own session."""
    return ClientSession(connector=TCPConnector(resolver=ThreadedResolver()))


def fake_addon(mode: str, seen: list):
    async def tts(request: web.Request):
        seen.append({"body": await request.json(), "secret": request.headers.get(BRIDGE_HEADER)})
        if mode == "409_no_key":
            return web.json_response({"reason": "no_key"}, status=409)
        if mode == "409_key_failed":
            return web.json_response({"reason": "key_failed", "provider": "gemini", "status": "invalid_key"}, status=409)
        resp = web.StreamResponse(headers={
            "Content-Type": "audio/pcm", "X-Audio-Format": "pcm_24000", "X-Streaming": "1",
            "X-Tts-Payer": "key", "X-Secret-Internal": "must-not-cross",
        })
        await resp.prepare(request)
        for c in CHUNKS:
            await resp.write(c)
            await asyncio.sleep(GAP_S)
        await resp.write_eof()
        return resp
    app = web.Application()
    app.router.add_post("/api/voice/tts", tts)
    return app


def view_app():
    view = DashieVoiceTtsStreamView()

    async def handler(request: web.Request):
        return await view.post(request)
    app = web.Application()
    app["hass"] = object()
    app.router.add_post(view.url, handler)
    return app


async def run(mode: str, body: dict, *, addon_up: bool = True):
    seen: list = []
    addon = TestServer(fake_addon(mode, seen))
    await addon.start_server()
    front = TestServer(view_app())
    await front.start_server()
    session = _session()
    base = str(addon.make_url("")).rstrip("/")

    async def secret(_h):
        return "bridge-secret-control"

    async def resolve(_h):
        if not addon_up:
            raise addon_bridge.AddonUnavailable("not installed")
        return base
    try:
        with patch.object(addon_bridge, "_read_bridge_secret", secret), \
             patch.object(addon_bridge, "_resolve_base", resolve), \
             patch.object(addon_bridge, "async_get_clientsession", lambda _h: session):
            async with _session() as client:
                t0 = time.monotonic()
                async with client.post(front.make_url("/api/dashie_voice/voice/tts-stream"), json=body) as r:
                    arrivals = []
                    data = b""
                    async for c in r.content.iter_any():
                        arrivals.append(time.monotonic() - t0)
                        data += c
                    return r.status, dict(r.headers), data, arrivals, seen
    finally:
        await session.close()
        await front.close()
        await addon.close()


def test_streams_pcm_through_without_buffering():
    status, headers, data, arrivals, seen = asyncio.run(run("200", {"text": "hi", "voice": "Aoede"}))
    assert status == 200
    assert data == b"".join(CHUNKS)
    assert headers["Content-Type"] == "audio/pcm" and headers["X-Audio-Format"] == "pcm_24000"
    assert headers.get("X-Tts-Payer") == "key"
    assert "X-Secret-Internal" not in headers
    # STREAMED: the first bytes arrive well before the add-on finished (it takes len(CHUNKS)*GAP_S).
    assert arrivals[0] < GAP_S * (len(CHUNKS) - 1), arrivals
    assert seen[0]["body"] == {"text": "hi", "stream": True, "voice": "Aoede"}
    assert seen[0]["secret"] == "bridge-secret-control"


def test_409_no_key_passes_through_verbatim():
    status, _h, data, _a, _s = asyncio.run(run("409_no_key", {"text": "hi"}))
    assert status == 409 and json.loads(data) == {"reason": "no_key"}


def test_409_key_failed_passes_through_verbatim():
    status, _h, data, _a, _s = asyncio.run(run("409_key_failed", {"text": "hi"}))
    assert status == 409
    assert json.loads(data) == {"reason": "key_failed", "provider": "gemini", "status": "invalid_key"}


def test_addon_unavailable_is_503_reason():
    status, _h, data, _a, seen = asyncio.run(run("200", {"text": "hi"}, addon_up=False))
    assert status == 503 and json.loads(data) == {"reason": "addon_unavailable"} and seen == []


def test_bad_input_never_calls_the_addon():
    status, _h, _d, _a, seen = asyncio.run(run("200", {"voice": "Aoede"}))
    assert status == 400 and seen == []


if __name__ == "__main__":
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
    print(f"{len(tests) - failed} passed, {failed} failed")
    raise SystemExit(1 if failed else 0)
