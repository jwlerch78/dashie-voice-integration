"""The tablet's STT relay through HA to the add-on (stt_relay_view.py + addon_bridge.call_addon_raw_phased).

Driven against a FAKE add-on over real HTTP (aiohttp), so the request really crosses two sockets. Pins:
  - the add-on's status + body pass through VERBATIM (200 {text}, 402, 503), asked with ?engine=gemini,
    the WAV bytes and the bridge secret;
  - the two failure ARMS are told apart, both over real TCP (O, 10-12, condition 3):
      never sent  → 503 {reason: addon_unavailable}: a REFUSED connection (and "no add-on found");
      sent, then failed → 504 {reason: addon_outcome_unknown}: the add-on READ the request and then dropped the
                          connection, or read it and then took longer than the timeout;
  - EVERY response carries X-Dashie-Stt-Relay: 1 (so the tablet can tell this route's 404 from HA's);
  - bad input → 400 without calling the add-on.

No pytest-homeassistant fixtures are needed, so it also runs directly:
    PYTHONPATH=. <python with homeassistant> tests/test_stt_relay_view.py
"""
from __future__ import annotations

import asyncio
import json
import socket
from unittest.mock import patch

from aiohttp import ClientSession, TCPConnector, ThreadedResolver, web

try:  # Under pytest-homeassistant, pytest_socket blocks sockets; this file's whole point is REAL TCP (two sockets).
    import pytest
    pytestmark = pytest.mark.enable_socket
    # On the RUNNER's loop, not a per-test asyncio.run(): each asyncio.run leaves its executor-shutdown thread
    # alive for a moment, and pytest-homeassistant fails the test at teardown for the lingering thread.
    _async_test = pytest.mark.asyncio
except ImportError:  # run directly without pytest
    def _async_test(fn):
        return fn
from aiohttp.test_utils import TestServer

from custom_components.dashie_voice import addon_bridge, stt_relay_view
from custom_components.dashie_voice.const import BRIDGE_HEADER
from custom_components.dashie_voice.stt_relay_view import DashieVoiceSttRelayView

WAV = b"RIFF\x24\x00\x00\x00WAVEfmt control-audio"
URL = "/api/dashie_voice/voice/stt-relay"


def _session() -> ClientSession:
    """A test client session on aiohttp's THREADED resolver. The default async resolver (pycares) starts a
    process-global shutdown thread when a session closes, and pytest-homeassistant fails the test at teardown
    for that lingering thread. Test harness only: production uses HA's own session."""
    return ClientSession(connector=TCPConnector(resolver=ThreadedResolver()))


def fake_addon(mode: str, seen: list):
    async def stt(request: web.Request):
        body = await request.read()          # the add-on has RECEIVED the request from here on
        seen.append({"body": body, "query": dict(request.query), "secret": request.headers.get(BRIDGE_HEADER)})
        if mode == "200":
            return web.json_response({"text": "turn on the lights"})
        if mode == "402":
            return web.json_response({"error": "insufficient_credits", "message": "Out of Dashie credits."}, status=402)
        if mode == "503_no_key":
            return web.json_response({"error": "gemini_stt_no_key"}, status=503)
        if mode == "drop_after_read":
            request.transport.close()        # read it (and could have billed), then vanished
            await asyncio.sleep(1)
            return web.Response()
        if mode == "slow_after_read":
            await asyncio.sleep(2)           # longer than the relay's (test-shortened) timeout
            return web.json_response({"text": "too late"})
        raise AssertionError(mode)
    app = web.Application()
    app.router.add_post("/api/voice/stt", stt)
    return app


def view_app():
    view = DashieVoiceSttRelayView()

    async def handler(request: web.Request):
        return await view.post(request)
    app = web.Application()
    app["hass"] = object()
    app.router.add_post(view.url, handler)
    return app


def _closed_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()                                # nothing listens here now: a connect is REFUSED
    return port


async def run(mode: str, body: bytes = WAV, *, addon: str = "up"):
    seen: list = []
    server = TestServer(fake_addon(mode, seen))
    await server.start_server()
    front = TestServer(view_app())
    await front.start_server()
    session = _session()
    base = str(server.make_url("")).rstrip("/") if addon == "up" else f"http://127.0.0.1:{_closed_port()}"

    async def secret(_h):
        return "bridge-secret-control"

    async def resolve(_h):
        if addon == "not_installed":
            raise addon_bridge.AddonUnavailable("not installed")
        return base

    async def no_actor(_r):
        return "test"
    try:
        with patch.object(addon_bridge, "_read_bridge_secret", secret), \
             patch.object(addon_bridge, "_resolve_base", resolve), \
             patch.object(addon_bridge, "async_get_clientsession", lambda _h: session), \
             patch.object(stt_relay_view, "RELAY_TIMEOUT_S", 1), \
             patch("custom_components.dashie_voice.voice_view._actor", lambda _r: "test"):
            async with _session() as client:
                async with client.post(front.make_url(URL), data=body, headers={"Content-Type": "audio/wav"}) as r:
                    return r.status, dict(r.headers), await r.read(), seen
    finally:
        await session.close()
        await front.close()
        await server.close()


def _json(b: bytes):
    return json.loads(b.decode())


@_async_test
async def test_200_passes_through_and_asks_gemini_with_the_wav():
    status, headers, data, seen = await (run("200"))
    assert status == 200 and _json(data) == {"text": "turn on the lights"}
    assert headers.get("X-Dashie-Stt-Relay") == "1"
    assert seen[0]["body"] == WAV and seen[0]["query"] == {"engine": "gemini"}
    assert seen[0]["secret"] == "bridge-secret-control"


@_async_test
async def test_402_insufficient_credits_passes_through_verbatim():
    status, headers, data, _ = await (run("402"))
    assert status == 402 and _json(data) == {"error": "insufficient_credits", "message": "Out of Dashie credits."}
    assert headers.get("X-Dashie-Stt-Relay") == "1"


@_async_test
async def test_503_no_key_from_the_addon_is_NOT_addon_unavailable():
    status, headers, data, _ = await (run("503_no_key"))
    assert status == 503 and _json(data) == {"error": "gemini_stt_no_key"}
    assert "reason" not in _json(data)
    assert headers.get("X-Dashie-Stt-Relay") == "1"


@_async_test
async def test_NEVER_SENT_refused_connection_is_503_addon_unavailable():
    status, headers, data, seen = await (run("200", addon="refused"))
    assert status == 503 and _json(data) == {"reason": "addon_unavailable"}
    assert seen == []                        # positive proof nothing reached an add-on
    assert headers.get("X-Dashie-Stt-Relay") == "1"


@_async_test
async def test_NEVER_SENT_no_addon_found_is_503_addon_unavailable():
    status, _h, data, seen = await (run("200", addon="not_installed"))
    assert status == 503 and _json(data) == {"reason": "addon_unavailable"} and seen == []


@_async_test
async def test_SENT_THEN_DROPPED_is_504_outcome_unknown():
    status, headers, data, seen = await (run("drop_after_read"))
    assert len(seen) == 1                    # the add-on DID receive it: this is the may-have-billed arm
    assert status == 504 and _json(data) == {"reason": "addon_outcome_unknown"}
    assert headers.get("X-Dashie-Stt-Relay") == "1"


@_async_test
async def test_SENT_THEN_TIMED_OUT_is_504_outcome_unknown():
    status, _h, data, seen = await (run("slow_after_read"))
    assert len(seen) == 1
    assert status == 504 and _json(data) == {"reason": "addon_outcome_unknown"}


@_async_test
async def test_empty_body_is_400_and_never_calls_the_addon():
    status, headers, data, seen = await (run("200", body=b""))
    assert status == 400 and _json(data)["reason"] == "bad_request" and seen == []
    assert headers.get("X-Dashie-Stt-Relay") == "1"


if __name__ == "__main__":
    import sys
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            asyncio.run(t())
            print(f"✅ {t.__name__}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"❌ {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed} passed, {failed} failed")
    if not failed:
        print("test_stt_relay_view: ALL PASS")
    sys.exit(1 if failed else 0)
