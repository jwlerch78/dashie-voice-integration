# Changelog

All notable changes to the Chickadee integration.

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
