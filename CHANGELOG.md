# Changelog

All notable changes to the Chickadee integration.

## 0.6.0 — 2026-07-29

### Added
- **Satellite wake word** — ships two custom microWakeWord models (`chickadee`,
  `hey_dashie`) and deploys the selected one to `/share/microwakeword/` so the
  standard `wyoming-microwakeword` add-on can serve it. Community words (Okay
  Nabu, Hey Jarvis, Alexa) are referenced by name and deploy nothing. The Assist
  pipeline's wake stage is wired automatically, and self-heals if the
  wyoming-microwakeword add-on is installed *after* Chickadee.
  Model provenance + license: `custom_components/chickadee/wake_models/README.md`.

### Security
- **Brain-issued HA service calls are now gated.** `conversation.py` passed the
  brain's `{domain, service}` straight into `hass.services.async_call`, with only
  the action category and command name checked — so a response naming
  `shell_command.*`, `hassio.host_reboot` or `homeassistant.stop` would execute,
  as would a call against an entity you had deliberately not exposed. Model
  output is untrusted input (it can be prompt-injected through a calendar title,
  a media title, or an entity's own `friendly_name`), so two layers now apply:
  a domain allowlist, and an Assist-exposure check on every target entity.
  Rejections log a `DROP:` marker. This makes "the brain sees your Assist-exposed
  entities (and only those)" true for *actions* as well as context.

### Fixed
- This repo is once again the true source of the shipped integration: the
  satellite-wake modules had been authored directly in the add-on repo's
  vendored copy, so they existed in no commit here — and `sync-integration.sh`
  (`rm -rf` + `git archive origin/main`) would have deleted them from the add-on
  at the next release. Re-converged, with the add-on copy's stale
  `addon_bridge.py` dropped in favour of this repo's dev-slug fix.

## 0.5.0 — 2026-07-27

### Added
- **Canonical `/api/chickadee/voice/*` paths** — every gateway view now serves
  `/api/chickadee/voice/status|converse|session|live-token` and
  `/api/chickadee/account/authorize`; the `/api/dashie/...` paths remain as
  legacy aliases for shipped Dashie apps (same handlers).
- `X-Chickadee-Brain-Route` response header (canonical twin of
  `X-Dashie-Brain-Route`, which stays for compatibility).
- SPDX license headers on every module + LICENSE shipped inside
  `custom_components/chickadee/` (so auto-installed copies carry it).

### Changed
- Cloud brain / STT-token URLs are no longer hardcoded to one environment:
  the add-on reports its configured environment's base URL
  (`cloud_url` on `/api/internal/sharing-status`, add-on ≥0.9) and the
  gateway derives its edge-function URLs from it. Older add-ons fall back
  to the previous behavior.

## 0.3.0 — 2026-07-25

### Added
- **Add-on auto-discovery** — the add-on announces itself (and its bridge
  credentials) via Supervisor discovery; existing installs pick up refreshed
  credentials silently, and fresh installs get a one-tap confirm flow.
- **Native voice picker** — the TTS entity exposes the engine's voice catalog,
  so pipeline voice selection is a dropdown instead of a text field.
- TTS audio format now follows the engine (hosted Chickadee Cloud voices are
  MP3; BYO servers stay WAV).

## 0.2.0 — 2026-07-25

### Added
- **Auto-created Assist pipeline** — setting up the integration creates a
  ready-to-use pipeline wired to the Chickadee conversation/STT/TTS entities.
  Idempotent (an existing pipeline referencing a Chickadee entity is left
  untouched), never marked preferred, and failures warn loudly without blocking
  setup — the manual assembly path always works.
- **Options flow** — rename the assistant after setup; the form surfaces add-on
  reachability.
- **STT entity** (`stt.chickadee`) — streams pipeline audio to the add-on's
  configured transcription engine (16 kHz mono PCM WAV).
- **TTS entity** (`tts.chickadee`) — synthesizes responses via the add-on's
  configured speech engine, with per-pipeline voice override.
- **Assistant-name persona** — the configured assistant name is passed to the
  brain and rendered into its persona; absent, the brain default applies.

### Notes
- Full audio→action→audio Assist pipeline verified end-to-end on a HAOS box
  (~8 s with LAN-hosted engines).
- Bridge turn timeout is 300 s — a backstop for slow local models on modest
  hardware, not a UX budget. Run your model server on a capable LAN box.

## 0.1.0 — 2026-07-25

First working version (not separately released).

### Added
- **Conversation entity** (`conversation.chickadee`) — routes Assist turns to
  the Chickadee add-on brain; executes real smart-home actions against your
  Assist-exposed entities, including multi-step commands.
- **Add-on bridge** — same-box discovery of the Chickadee add-on with
  shared-secret auth enforced from birth (`X-Chickadee-Bridge-Secret`); secret
  provisioned by the add-on at `<ha-config>/.chickadee/bridge_secret`.
- **Exposed-entity context** — the brain sees exactly your Assist-exposed
  entities (id, domain, name, state, area, aliases), nothing else.
- **Config flow** — single-instance setup: add-on reachability probe (warn,
  don't block — install order doesn't matter) + assistant name.
- **CONTRACTS.md** — registry of every integration↔add-on contract; changes to
  a contract must touch both sides and the registry together.
