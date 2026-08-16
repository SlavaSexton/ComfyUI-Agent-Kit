# Per-model prompting reference

**This reference is distilled from official sources** (each model maker's docs / model card, docs.comfy.org, and
the per-model prompt templates shipped with the `anthropic-claude` ComfyUI node). Each generative model has its
own "character" and rewards a different prompt approach. Treat every model as its own dialect.

**How to use it (the auto-pull rule):** when a specific model is named in the request, the workflow, or the
template, READ that model's entry below BEFORE writing the prompt, and follow its structure, its negative-prompt
rule, and its settings. Do not carry one model's prompt style over to another (SDXL tags will not help FLUX;
FLUX prose will not help SDXL).

**Where the entries live.** This file is the index. Each family sits in its own file under `MODELS/` so a
read returns the WHOLE family instead of truncating: the combined reference outgrew a single readable file
(2026-08-06 audit measured 57% of entries past the point where a read stops). Open the file for the family,
not this index, once you know which model you need.

| Family | File | Entries |
|---|---|---|
| Image models (open / local-runnable) | [`MODELS/image-open.md`](MODELS/image-open.md) | 12 |
| Image models (API / closed) | [`MODELS/image-api.md`](MODELS/image-api.md) | 13 |
| More open image models | [`MODELS/image-open-more.md`](MODELS/image-open-more.md) | 6 |
| Image editing models (instruction-based) | [`MODELS/image-edit.md`](MODELS/image-edit.md) | 4 |
| Video models (open / local-runnable) | [`MODELS/video-open.md`](MODELS/video-open.md) | 10 |
| Video models (API / closed) | [`MODELS/video-api.md`](MODELS/video-api.md) | 15 |
| Audio models | [`MODELS/audio.md`](MODELS/audio.md) | 6 |
| 3D models | [`MODELS/three-d.md`](MODELS/three-d.md) | 4 |
| Newer and niche models | [`MODELS/niche.md`](MODELS/niche.md) | 3 |
| Enhancement and utility (NOT prompt-driven) | [`MODELS/utility.md`](MODELS/utility.md) | 2 |

### Every model with a recipe, and where to find it

| Model | File |
|---|---|
| FLUX.1 (Black Forest Labs) | `MODELS/image-open.md` |
| FLUX.2 (Black Forest Labs) | `MODELS/image-open.md` |
| FLUX.1 Kontext (image edit) | `MODELS/image-open.md` |
| Z-Image-Turbo (Tongyi / Alibaba) | `MODELS/image-open.md` |
| Qwen-Image (Alibaba) | `MODELS/image-open.md` |
| Qwen-Image-Edit (Alibaba) | `MODELS/image-open.md` |
| SDXL (Stability) | `MODELS/image-open.md` |
| Stable Diffusion 1.5 | `MODELS/image-open.md` |
| Stable Diffusion 3.5 Large (Stability) | `MODELS/image-open.md` |
| HiDream-I1 | `MODELS/image-open.md` |
| Boogu Image 0.1 | `MODELS/image-open.md` |
| Mage-Flow / Mage-Flow-Edit (Microsoft, 4B, MIT) | `MODELS/image-open.md` |
| Ideogram (2.x to 4.0, plus P-Image) | `MODELS/image-api.md` |
| Nano Banana Pro (Gemini 3 Pro Image) | `MODELS/image-api.md` |
| Nano Banana 2 (Gemini 3.1 Flash Image) | `MODELS/image-api.md` |
| Nano Banana 2 Lite (Gemini Flash Image, fast tier) | `MODELS/image-api.md` |
| Seedream 4.0 / 4.5 (ByteDance) | `MODELS/image-api.md` |
| Seedream 5.0 Lite (ByteDance) | `MODELS/image-api.md` |
| Seedream 5.0 Pro (ByteDance) | `MODELS/image-api.md` |
| Recraft (V3, and V4 / V4.1) | `MODELS/image-api.md` |
| GPT-Image (gpt-image-2, OpenAI) | `MODELS/image-api.md` |
| Grok Image (Grok Imagine Image, xAI) | `MODELS/image-api.md` |
| Reve (DEPRECATED in core v0.31.0) | `MODELS/image-api.md` |
| Qwen Image 3.0 Pro (Comfy Cloud only, no local node) | `MODELS/image-api.md` |
| Kandinsky (3.x, Sber / FusionBrain) | `MODELS/image-api.md` |
| BRIA 3.x | `MODELS/image-open-more.md` |
| OmniGen (v1 / v2) - unified gen + edit | `MODELS/image-open-more.md` |
| Chroma | `MODELS/image-open-more.md` |
| Krea 1 (FLUX.1 Krea [dev]) | `MODELS/image-open-more.md` |
| Krea 2 (Krea AI, open weights) | `MODELS/image-open-more.md` |
| ERNIE-Image (Baidu) | `MODELS/image-open-more.md` |
| FireRed Image Edit | `MODELS/image-edit.md` |
| LongCat-Image / LongCat-Image-Edit (Meituan) | `MODELS/image-edit.md` |
| ChronoEdit (NVIDIA) | `MODELS/image-edit.md` |
| JoyAI Image Edit (JD, open weights, Apache-2.0) | `MODELS/image-edit.md` |
| Wan 2.1 & 2.2 (Alibaba) | `MODELS/video-open.md` |
| Wan 2.5 / 2.6 (Alibaba, API) | `MODELS/video-open.md` |
| Wan 2.7 (Alibaba) | `MODELS/video-open.md` |
| Wan Animate 2 (Alibaba, local character animation) | `MODELS/video-open.md` |
| SCAIL-2 (zai-org, animation + character replacement) | `MODELS/video-open.md` |
| LTX-2.5 (Lightricks, open weights) | `MODELS/video-open.md` |
| LTX-2.3 (Lightricks) | `MODELS/video-open.md` |
| LTX-2 Pro (Lightricks) | `MODELS/video-open.md` |
| Hunyuan Video (Tencent) | `MODELS/video-open.md` |
| SVD (Stable Video Diffusion, Stability) | `MODELS/video-open.md` |
| Kling (2.1/2.5, 2.6, 3.0/V3, O1, O3) - Kuaishou | `MODELS/video-api.md` |
| Veo 3 / 3.1 (Google) | `MODELS/video-api.md` |
| Gemini Omni Flash (Google) | `MODELS/video-api.md` |
| Sora 2 / Sora 2 Pro (OpenAI) | `MODELS/video-api.md` |
| Seedance 1.0, 1.5 Pro, 2.0 and 2.5 (ByteDance) | `MODELS/video-api.md` |
| LTX-2.5 (Lightricks, API partner nodes) | `MODELS/video-api.md` |
| FLUX 3 Video (Black Forest Labs) | `MODELS/video-api.md` |
| Luma Ray 2 / Ray 3 (Dream Machine) | `MODELS/video-api.md` |
| Runway Gen-4 / Gen-4.5 | `MODELS/video-api.md` |
| MiniMax / Hailuo | `MODELS/video-api.md` |
| PixVerse | `MODELS/video-api.md` |
| Vidu (Q1 / Q2) | `MODELS/video-api.md` |
| Pika 2.2 / 2.5 | `MODELS/video-api.md` |
| Sync 3 (sync.so) - lip sync + talking image | `MODELS/video-api.md` |
| HeyGen (avatar video, talking photo, TTS, video translate) | `MODELS/video-api.md` |
| Stable Audio (Stability) | `MODELS/audio.md` |
| ACE-Step | `MODELS/audio.md` |
| ElevenLabs (API via ComfyUI nodes) | `MODELS/audio.md` |
| ChatterBox (Resemble AI) | `MODELS/audio.md` |
| MiniMax Music 3 (open weights) | `MODELS/audio.md` |
| Seed Audio 1.0 (ByteDance) | `MODELS/audio.md` |
| Hunyuan3D (Tencent) | `MODELS/three-d.md` |
| Tripo | `MODELS/three-d.md` |
| Rodin (Hyper3D) | `MODELS/three-d.md` |
| Meshy | `MODELS/three-d.md` |

**Two files are not in the table above on purpose.** `MODELS/niche.md` groups newer and thin-coverage
models by medium rather than by name, and `MODELS/utility.md` covers tools that are not prompt-driven at
all (upscale, restore, interpolation, segmentation, depth, pose, conditioning). Open them directly.

## Quick cheat sheet (prompt style + negatives)

| Model / family | Prompt style | Negative prompts |
|---|---|---|
| FLUX.1 / .2, FLUX Kontext | natural-language sentences (word order matters) | NOT supported, rephrase positively |
| Z-Image-Turbo | natural-language, subject-first | not used (CFG-distilled) |
| Qwen-Image / Edit | structured natural language, one style | limited / not supported (edit) |
| SDXL | natural language (hybrid tags ok) | supported, effectively required |
| SD 1.5 | comma tags, `(token:1.2)` weights | supported, heavily used |
| SD 3.5 | natural language (no weighting syntax) | supported element |
| HiDream-I1 | natural language | Full=yes, Dev/Fast inert (guidance 0) |
| BRIA 3.x | natural language (short text) | supported (CFG>1) |
| OmniGen v1/v2 | instruction + inline image tags | v2 yes |
| Chroma | natural language | supported |
| Krea 1 (FLUX Krea) | natural language, no weights | no (guidance-distilled) |
| Krea 2 (RAW + Turbo) | natural language, quote text | RAW yes (CFG 3.5), Turbo no (CFG 0) |
| Mage-Flow / Mage-Flow-Edit | descriptive prose; edit = keep-then-change | supported (CFG>1), inert on Turbo (CFG 1.0) |
| ERNIE-Image | instruction + prompt enhancer | not documented |
| FireRed / LongCat / ChronoEdit (edit) | instruction (quote literal text) | mostly empty/unset |
| SVD (video) | NONE, image + motion params | no |
| Ideogram, Recraft | natural language, quoted text | Ideogram yes / Recraft no |
| Nano Banana Pro/2 (Gemini) | rich descriptive prose | NOT used, phrase positively |
| Seedream 4.x | structured spec (identity-lock) | describe positively |
| Seedream 5 Lite | natural sentences (no boosters) | NOT supported |
| GPT-Image, Grok Image | structured brief / 5-part | exclusions slot, no negative field |
| Reve, Kandinsky | natural language | Reve no / Kandinsky yes |
| Wan 2.x / 2.5-2.7 | cinematic shot description | supported (best on 2.2+) |
| LTX-2.3 / 2 Pro | one flowing paragraph, NOT tag dumps + audio | Dev only (CFG>1), Distilled ignores |
| Hunyuan Video | detailed natural language + motion | leans on positive + prompt-rewrite |
| Kling, Seedance, MiniMax | structured + camera direction | Kling yes / others use exclusions |
| Veo, Sora | natural / storyboard, audio after visual | descriptive exclusions at end |
| Luma, Runway | content-only (camera via API/refs) | NOT supported |
| Stable Audio | genre + mood + instruments + BPM | n/a |
| ACE-Step | tags + structured `[verse]/[chorus]` lyrics | n/a |
| 3D (Hunyuan3D, Tripo, Rodin, Meshy) | subject + materials + style; clean input image | mostly n/a |

---


## Sources and provenance

Per-model guidance above is distilled from official sources: each maker's documentation and model cards (Black
Forest Labs, Stability, Alibaba / Tongyi, ByteDance / BytePlus / Volcengine, Google, OpenAI, xAI, Kuaishou,
Lightricks, Tencent, Luma, Runway, MiniMax, Recraft, Ideogram, Reve, Sber / FusionBrain, Resemble AI, Tripo,
Hyper3D, Meshy, BRIA, Baidu, Meituan, NVIDIA, VectorSpaceLab, lodestones, Krea, Glanty / xgen-universe, CircleStone
Labs, NewBie-AI, Alibaba AIDC-AI, Microsoft, SVG.io, Sonilo, Phantom-video, zai-org / Zhipu, Netflix), the official
ComfyUI tutorials at docs.comfy.org, and the per-model prompt templates shipped with the `anthropic-claude` node (by
alexmunteanu), which are themselves distilled from official prompting guides. The enhancement/utility entries are
sourced from each project's GitHub / HuggingFace (Real-ESRGAN, SUPIR, SeedVR2, FlashVSR, Topaz, Magnific, FILM,
RIFE, SAM3, BiRefNet, Depth Anything, DWPose, MoGe, IP-Adapter, LivePortrait, Mediapipe). Specs change; when a
model updates, re-check its source link.
