# Chickadee — the integration

> **Just want Chickadee?** Head to the main repo:
> **[github.com/jwlerch78/chickadee](https://github.com/jwlerch78/chickadee)** —
> the add-on there installs and updates this integration for you, one URL,
> no HACS needed. This repository is the engine room: integration source,
> architecture, and the manual/HACS install path for people who prefer to
> manage components themselves.

**Chickadee gives your Assist pipeline a real brain.** One integration provides a
conversation agent, STT, and TTS for Home Assistant — backed by whatever you want:
your own API keys, a local box (Ollama / Whisper / Piper / Kokoro), or a hosted
option. Works with every satellite you already have.

> Named for the bird that says its own name.

Wake word is a satellite capability — your Voice PE, ESPHome satellite, tablet, or
browser card does its own wake detection and streams into the pipeline. **Chickadee
begins where the wake word ends**: it turns the audio that arrives into
transcription, understanding, real smart-home actions, and speech back out.

## What you get

Two pieces, installed together:

- **This integration** (`chickadee`) — the Assist-pipeline surface: a
  `conversation` entity, an `stt` entity, and a `tts` entity. Thin by design; it
  contains no engine logic.
- **The [Chickadee add-on](https://github.com/jwlerch78/chickadee)** — the
  brain runtime. It routes each stage of the pipeline to any OpenAI-compatible
  endpoint you configure: a local model server, a cloud provider with your own key,
  or a mix (local STT + cloud LLM is a great combination). The integration talks to
  it over an authenticated same-box bridge (see [CONTRACTS.md](CONTRACTS.md)).

```
satellite (Voice PE / ESPHome / tablet / browser card)
        │  wake word + mic (on-device)
        ▼
HA Assist pipeline
        │
        ├── stt.chickadee ───────► Chickadee add-on ──► your STT engine
        ├── conversation.chickadee ► Chickadee add-on ──► your LLM  ──► HA actions
        └── tts.chickadee ───────► Chickadee add-on ──► your TTS engine
```

The conversation brain sees your Assist-**exposed** entities (and only those),
executes multi-step smart-home commands, and answers in plain speech.

## Status — what works today

This is a young project. Here's the honest line between shipped and planned:

**Verified, end-to-end on a real HAOS box:**

- Full audio-in → action → audio-out Assist pipeline through all three Chickadee
  entities (measured **~8 s** wake-to-response with LAN-hosted engines: Whisper
  STT ≈ 1.5 s, LLM ≈ 3 s, Kokoro TTS ≈ 3 s).
- Bring-your-own engines over the OpenAI-compatible API: Ollama, llama.cpp, vLLM,
  whisper.cpp / faster-whisper servers, Kokoro-FastAPI, and cloud compat endpoints
  (Gemini, OpenRouter, OpenAI) with your own key.
- Real smart-home actions against exposed entities ("turn on the dining room
  light"), including multi-step commands.

**Planned / in progress (not promised dates):**

- A hosted engine option for people who don't want to run or key their own models.
- Assistant personality (beyond the assistant's name), memory, and extra tools
  (the brain core supports them; the open runtime doesn't expose them yet).
- Streaming responses; better answers to open questions ("which lights are on?")
  on audio-only satellites.

## Compatibility matrix

Chickadee is pipeline-side, so it works with any satellite that can run an Assist
pipeline. What differs is what each satellite itself brings:

| Satellite | Assist pipeline (Chickadee) | Native wake word (screen-off) | Kiosk management | Realtime speech-to-speech |
|---|---|---|---|---|
| **HA Voice PE / ESPHome satellites** | ✅ | ✅ on-device (microWakeWord / openWakeWord) | — | ❌ |
| **Dashie app** (Android tablets / TV) | ✅ | ✅ on-device wake | ✅ built-in | ✅ (the only satellite we know of with realtime audio today) |
| **Fully Kiosk Browser** | ✅ via browser satellite cards (e.g. Voice Satellite — interop, not rivalry) | ⚠️ browser-based, card-dependent | ✅ via Fully Kiosk's own app/REST | ❌ |
| **Browser / wall dashboard** | ✅ via the Assist dialog or satellite cards | ⚠️ browser-based, card-dependent | — | ❌ |

Two honest notes:

- **Realtime speech-to-speech** (continuous conversation, barge-in) cannot ride
  Assist's cascade protocol for *anyone* — it needs a satellite that supports
  realtime audio end-to-end. Today that's the Dashie app; we'd love to see more.
- **Kiosk management** is out of scope for Chickadee itself — the column shows
  what the satellite provides on its own.

## Installation

### The easy way (recommended)

Follow the [main repo](https://github.com/jwlerch78/chickadee): install the
add-on, and it installs this integration automatically, keeps it updated with
add-on releases, and walks you through the one restart + one click of setup.
(The auto-installer marks its copy and will never touch a HACS or manual
install it didn't create.)

### The manual way (HACS)

1. Install the [add-on](https://github.com/jwlerch78/chickadee) (the brain) and
   set `install_integration: false` in its configuration if you want HACS to
   own the integration.
2. HACS → **⋮ → Custom repositories** → add
   `https://github.com/jwlerch78/chickadee-integration`, type **Integration**
3. Install **Chickadee**, restart Home Assistant.

*(No HACS? Copy `custom_components/chickadee/` into your
`config/custom_components/` and restart.)*

### Add the integration

Settings → Devices & Services → **Add integration → Chickadee**. The flow checks
the add-on is reachable and asks what to call your assistant. If you installed the
integration first, choose "Set up anyway" and it will find the add-on when it's up.

Setup creates a ready-to-use Assist pipeline wired to the Chickadee
conversation/STT/TTS entities — point your satellites at it and talk. It's never
marked as your preferred pipeline, and an existing Chickadee pipeline is left
untouched.

### 4. Or assemble the pipeline yourself

Prefer to mix stages? Settings → Voice assistants → **Add assistant**:

- **Conversation agent:** Chickadee
- **Speech-to-text:** Chickadee (or keep Whisper/HA Cloud if you prefer)
- **Text-to-speech:** Chickadee (or keep Piper/HA Cloud)

Each stage is independent — local Whisper with a Chickadee brain is a fine
pipeline.

## Configuring engines

All engine configuration lives in the **add-on** (Settings → Add-ons → Chickadee →
Configuration) — the integration stays thin. Quick reference; full details in the
add-on's [Documentation tab](https://github.com/jwlerch78/chickadee/blob/main/chickadee/DOCS.md):

| Stage | Options | Examples |
|---|---|---|
| LLM | `llm_url`, `llm_model`, `llm_api_key` | Ollama on a LAN box: `http://192.168.1.50:11434` · Gemini: full compat URL + key |
| STT | `stt_url`, `stt_model`, `stt_api_key` | whisper.cpp server, faster-whisper/speaches, or a provider endpoint |
| TTS | `tts_url`, `tts_voice`, `tts_api_key` | Kokoro-FastAPI (`af_heart` is lovely), or a provider endpoint |

**Model choice matters.** The brain sends real prompts — a few thousand tokens once
your exposed entities are included — and asks the model to hold a structured
action schema. In our testing, very small local models (1.5B–7B class) misroute
or emit placeholder JSON; current fast cloud models (e.g. Gemini Flash) and
well-run larger local models handle it reliably. And run your model server on
capable hardware: a GPU or Apple-silicon box on your LAN answers in seconds,
while a 4-core CPU HA box can take minutes per turn on prompt prefill alone.

## Privacy

- The integration and add-on talk only over the local bridge on your box.
- Audio and text go only to the engine endpoints **you** configure — point
  everything at LAN servers and nothing leaves your network.
- The brain sees only your Assist-exposed entities.
- Conversation logging stays on-box.

## Contributing

Issues and PRs welcome — bug reports and satellite compatibility reports
especially. See the [issue templates](.github/ISSUE_TEMPLATE). Cross-boundary
changes (integration ↔ add-on) must update [CONTRACTS.md](CONTRACTS.md).

## License

[AGPL-3.0](LICENSE). Operated by the makers of [Dashie](https://dashieapp.com).
