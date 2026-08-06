# Audio models

Part of the kit's per-model prompting reference. The routing table and the auto-pull rule live in
[`MODELS.md`](../MODELS.md); this file holds the 5 entries for this family.


### Stable Audio (Stability)
- **Prompt style:** genre + mood + instruments + BPM/tempo, short English phrase ("128 BPM tech house drum loop"). No lyrics, no realistic vocals.
- **Structure:** concise tag-like sound description, then set `seconds_total` (and optional `seconds_start`).
- **Strengths:** SFX, foley, ambiences, drum/instrument loops; precise BPM and instrument naming.
- **Avoid:** vocals/singing, full songs, non-English prompts.
- **Settings:** 44.1kHz stereo; max ~47s (default 47.6s via EmptyLatentAudio); steps in KSampler.
- **Download / license:** GATED on HF, accept the license + use a token to download (requires an HF account + license-agreement form at huggingface.co/stabilityai/stable-audio-open-1.0 before the weights are accessible). License is NON-COMMERCIAL only (stable-audio-community); commercial use requires a separate license from stability.ai/license.
- **Source:** huggingface.co/stabilityai/stable-audio-open-1.0 ; docs.comfy.org/tutorials/audio/stable-audio.

### ACE-Step
- **Prompt style:** two fields. Tags = comma-separated genres/scenes/instruments/vocals/tempo ("electronic, pop, female voice, 110 bpm, melodic"). Lyrics = `[verse]`, `[chorus]`, `[bridge]`, `[outro]`; optional leading language code `[en]`/`[zh]` (19 languages).
- **Structure:** tags describe the sound; lyrics drive sung content and sections.
- **Strengths:** mainstream styles, lyric alignment, fast (~4 min audio in ~20s on A100), lyric editing/remix.
- **Avoid:** less-common languages underperform; lyric edits in small segments; copyright risk.
- **Settings:** duration in EmptyAceStepLatentAudio (-1 random); steps 27 or 60; `denoise` for similarity; vocal prominence via LatentOperationTonemapReinhard `multiplier`.
- **Source:** github.com/ace-step/ACE-Step ; docs.comfy.org/tutorials/audio/ace-step/ace-step-v1.

### ElevenLabs (API via ComfyUI nodes)
- **Prompt style:** TTS = plain text (voice/emotion via parameters). SFX = specific natural-language description (material, size, environment, distance, temporal arc, acoustic space); onomatopoeia helps.
- **Strengths:** natural multilingual voices, instant cloning, precise SFX; node supports `eleven_multilingual_v2` and `eleven_v3`.
- **Avoid:** over-long SFX prompts; expecting prompt words to control tone (use parameters).
- **Settings (built-in TTS node):** `stability` (def 0.5), `similarity_boost` (def 0.75), `style` (def 0.0), `speed` (def 1.0), `use_speaker_boost`. Text-to-Effect: `duration` 0.5-30s, `prompt_influence` 0-1 (def 0.3).
- **Source:** elevenlabs.io/docs ; docs.comfy.org/built-in-nodes/ElevenLabsTextToSpeech.

### ChatterBox (Resemble AI)
- **Prompt style:** literal text to speak (expressiveness via parameters, not words); voice cloning uses a 10s+ reference clip (match language to avoid accent transfer).
- **Strengths:** zero-shot cloning, emotion intensity dial, multilingual (23+ in V3), fast.
- **Avoid:** high `exaggeration` speeds up speech (lower `cfg_weight` to compensate); language mismatch causes accent bleed.
- **Settings:** defaults `exaggeration=0.5`, `cfg_weight=0.5`; dramatic `exaggeration` 0.7+ with `cfg_weight` ~0.3.
- **ComfyUI build:** the cited repo is the Python library; for ComfyUI install `filliptm/ComfyUI_Fill-ChatterBox` (ComfyUI Manager), whose TTS node takes `text` + `reference_audio` + `exaggeration` + `cfg_weight` -> AUDIO.
- **Source:** github.com/resemble-ai/chatterbox (Python library).

### Seed Audio 1.0 (ByteDance)
- **Prompt style (this is the whole game):** write the scene as a SCRIPT and wrap everything that is NOT spoken dialogue in `[square brackets]` - only text in quotes after `says / whispers / replies` gets voiced. Un-bracketed prose is read aloud as narration and bloats the clip. Order: `[Language: ...]` -> `[Environment: ...]` -> `[Background music / SFX: ...]` -> `Name (voice traits) says: "line"` -> `[beats / SFX / Outro]`. Describe each voice (gender, age, accent, emotion, tone, pace) inside the parentheses before `says`.
- **Lock the language:** English + Chinese only, and it mixes them if you don't pin it. Put `[Language: English only.]` (or `Chinese only.`) near the top AND write "speaks English only" into each character's voice traits.
- **Limits (confirmed from the templates):** prompt <=3000 chars, output <=2 min.
- **Strengths:** ONE pass gives a FULL audio scene - ambience + multi-character dialogue (per-voice traits) + background music + SFX - not plain TTS or a music-tag list. Three modes on the same node.
- **Build the graph (confirmed from the official templates):** node **`ByteDanceSeedAudio`** -> **`SaveAudioAdvanced`** (widgets `mp3` / `V0`). Node widgets = prompt, a **mode combo**, `sample_rate` `24000`, seed + control_after_generate (leave the middle toggles at their defaults).
  - **t2a** - mode `text only`, no inputs. (Also the clean way to make a reference clip for ta2a.)
  - **ta2a** - mode `audio reference`; **`LoadAudio`** -> `reference_mode.reference_audio_1` (add `_2`, `_3` in order, no gaps, <=30s each). In the prompt tag each speaker `voiced by @Audio1 / @Audio2 / @Audio3` matching the connected clip - every `@AudioN` used must have a clip, and a speaker reuses the same `@AudioN` on later lines. `@Audio1` = `reference_audio_1`, etc.
  - **ti2a** - mode `image reference`; **`LoadImage`** -> `reference_mode.reference_image`; the image derives ONE character voice, the prompt still drives language + scene. Do NOT use `@AudioN` in this mode.
- **Source:** the official `api_bytedance_seed_audio1_0_{t2a,ta2a,ti2a}.json` templates' own MarkdownNote guides ; volcengine.com / byteplus docs (Seed Audio 1.0). API / paid (Comfy Cloud or a BytePlus key).
