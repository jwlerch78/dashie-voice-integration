# Chickadee

**An open voice pipeline for Home Assistant.** One integration gives your Assist
pipeline a real brain — backed by whatever you want: your own API keys, a local model
(Ollama / Whisper / Piper / Kokoro), or Chickadee Cloud. Tools, memory, and
personality included. Works with every satellite you already have.

> Named for the bird that says its own name.

**Status: pre-release.** This repo is private while v0.1 comes together. The pieces:

- `custom_components/chickadee` — the Assist-pipeline surface: a conversation entity
  today, STT/TTS provider entities next. Thin by design.
- [chickadee-addons](https://github.com/jwlerch78/chickadee-addons) — the Chickadee
  add-on: the console UI, the brain runtime, and engine routing (cloud / BYOK /
  local, with fallback). The integration talks to it over an authenticated same-box
  bridge (see [CONTRACTS.md](CONTRACTS.md)).

## How it fits together

```
satellite (Voice PE / ESPHome / tablet / browser card)
        │  wake word + mic (on-device)
        ▼
HA Assist pipeline ──► conversation.chickadee ──► Chickadee add-on brain
                                                   ├─ your API keys (BYOK)
                                                   ├─ local models
                                                   └─ Chickadee Cloud (hosted)
```

Wake word is a satellite capability — Chickadee begins where the wake word ends.

## License

[AGPL-3.0](LICENSE). Operated by the makers of [Dashie](https://dashieapp.com).
