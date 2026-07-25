# Chickadee Cross-Boundary Contracts

Registry of every contract shared between the integration (this repo), the Chickadee
add-on (chickadee-addons), and satellites. Rule inherited from the Dashie postmortems:
before hand-mirroring anything across a boundary, add a row here — and prefer sharing
one copy over mirroring at all.

| Contract | This side | Other side | Notes |
|---|---|---|---|
| Add-on bridge HTTP surface | `const.py` (`ADDON_CONVERSE_PATH=/api/voice/converse`, `ADDON_PING_PATH=/api/ping`, port 8099) | add-on HTTP server routes | Change together, never singly |
| Bridge auth | `const.py` (`X-Chickadee-Bridge-Secret` header, secret file `addon_configs/chickadee/bridge_secret`) | add-on writes the secret file at startup | Pattern: Dashie 20260702_BRIDGE_AUTH_HARDENING |
| VoiceRequest / turn shape | `conversation.py` payload build + turn handling (`voice`/`text`/`action`/`steps`/`client_tool`/`unsupported_tool`) | add-on brain runtime | Pass-through philosophy: unknown fields must survive; add-on owns overrides (`retain_mode`, route) |
| Brain entity shape | `entity_context.py` (`{entity_id, domain, friendly_name, state, area?, aliases?}`) | brain prompt builder | Source contract: Dashie 20260717_HA_ENTITY_EXPOSURE_CONTRACT |
| Add-on slug | `const.py` candidates (`local-chickadee`, `addon_local_chickadee`) | chickadee-addons `config.yaml` `slug: chickadee` | Slugs are immutable once shipped |
