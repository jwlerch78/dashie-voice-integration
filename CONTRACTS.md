# Chickadee Cross-Boundary Contracts

Registry of every contract shared between the integration (this repo), the Chickadee
add-on (chickadee-addons), and satellites. Rule inherited from the Dashie postmortems:
before hand-mirroring anything across a boundary, add a row here — and prefer sharing
one copy over mirroring at all.

| Contract | This side | Other side | Notes |
|---|---|---|---|
| Add-on bridge HTTP surface | `const.py` (`ADDON_CONVERSE_PATH=/api/voice/converse`, `ADDON_PING_PATH=/api/ping`, `ADDON_STT_PATH=/api/voice/stt`, `ADDON_TTS_PATH=/api/voice/tts`, port 8099) | add-on HTTP server routes | Change together, never singly |
| STT turn shape | `stt.py` (POST audio/wav body → `{text}`) | add-on `engines.js` handleStt | 16 kHz mono PCM16 WAV in; empty `text` = no speech |
| TTS turn shape | `tts.py` (POST `{text, voice?}` → `audio/wav` bytes) | add-on `engines.js` handleTts | `voice` empty = engine/default voice (add-on `tts_voice` option) |
| Bridge auth | `addon_bridge.py` (`X-Chickadee-Bridge-Secret` header). Secret priority: (1) Supervisor discovery via `config_flow.async_step_hassio` → entry data → `set_bridge_config`; (2) legacy file read `<ha-config>/.chickadee/bridge_secret`, glob `addon_configs/*chickadee/bridge_secret` | add-on publishes `{service:"chickadee", config:{host,port,secret}}` to Supervisor `/discovery` on every start (`discovery.js`; config.yaml `hassio_api`+`discovery`) AND still writes the file copies for pre-discovery integrations; auth ENFORCED from birth | Discovery = the MQTT-broker credential pattern. ⚠️ HA Core canNOT read /addon_configs on HAOS (2026-07-25); file-in-ha-config stays as legacy fallback only. Pattern to back-port to Dashie's bridge auth |
| VoiceRequest / turn shape | `conversation.py` payload build + turn handling (`voice`/`text`/`action`/`steps`/`client_tool`/`unsupported_tool`) | add-on brain runtime | Pass-through philosophy: unknown fields must survive; add-on owns overrides (`retain_mode`, route). `assistant_name` (optional) → brain `{{ASSISTANT_NAME}}` persona; absent = brain default |
| Brain entity shape | `entity_context.py` (`{entity_id, domain, friendly_name, state, area?, aliases?}`) | brain prompt builder | Source contract: Dashie 20260717_HA_ENTITY_EXPOSURE_CONTRACT |
| Add-on slug | `const.py` candidates (`local-chickadee`, `addon_local_chickadee`) | chickadee-addons `config.yaml` `slug: chickadee` | Slugs are immutable once shipped |
