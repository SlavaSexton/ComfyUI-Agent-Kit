# Newer and niche models

Part of the kit's per-model prompting reference. The routing table and the auto-pull rule live in
[`MODELS.md`](../MODELS.md); this file holds the 3 entries for this family.


Recently added to the template library. Most now have official docs.comfy.org pages or model cards (researched from
those); a few are thin on prompt specifics and say so.

### Image

**Capybara** (unified image + video, gen + edit), Glanty / xgen-universe, built on HunyuanVideo-1.5. The card defines
exactly four `--task_type` values: t2i, t2v, ti2i (instruction image edit), tv2v (instruction video edit); there is no
I2V task. Natural language for generation, imperative instruction for edits ("Change the time to night"); optional
Qwen3-VL-8B auto-rewrite expands short prompts (separate Qwen/Qwen3-VL-8B-Instruct download). Image 720p / 50 steps,
video 480p / 50 steps (frames 81/101/121). guidance_scale default is 1.0 (the card's parameter-table default); the 4.0
seen in the T2V/T2I example commands is a per-command override, not the default. FP8 available but requires NVIDIA
compute capability >= 8.9 (Ada Lovelace / Hopper: RTX 4090 / L40 / H100), so an RTX 3090 (cc 8.6) cannot use FP8.
Negatives not documented. Source: huggingface.co/xgen-universe/Capybara. **ComfyUI build:** official templates `Image_capybara_v0_1_image_edit.json` and `Image_capybara_v0_1_text_to_image.json` (Comfy-Org template library).

**Bernini-R** (image/video relighting edit), ByteDance, Wan2.2-based (also a 1.3B Wan2.1 fine-tune ~2.6GB). No official
prompt guide; prompt like a Wan/Qwen-edit relight: describe target lighting (direction, temperature, intensity, mood)
+ what to preserve ("keep subject and pose; relight as warm sunset key from camera-left"); use a reference image to
carry lighting across a set. Treat steps/CFG like a Wan2.2 edit workflow. Quantized variants for VRAM-constrained
setups (in the repo beyond the fp16 high/low-noise files): `wan2.2_bernini_r_high_noise_fp8_scaled.safetensors`,
`wan2.2_bernini_r_high_noise_mxfp8.safetensors`, `wan2.2_bernini_r_low_noise_fp8_scaled.safetensors`,
`wan2.2_bernini_r_low_noise_mxfp8.safetensors`. Source: huggingface.co/Comfy-Org/Bernini-R. **ComfyUI build:** official tutorial docs.comfy.org/tutorials/video/bytedance/bernini-r; the Comfy-Org repack runs on the standard Wan2.2 graph (the high-noise / low-noise UNETLoader pair).

**Anima** (anime t2i), CircleStone Labs, 2B (Qwen-3 0.6B encoder). Danbooru tags, natural language, or mix; order
`[quality/meta/year/safety] [char count] [character] [series] [artist] [general]`; positive prefix `masterpiece,
best quality, score_7, safe,`, negative `worst quality, low quality, score_1..3, artist name`; lowercase tags with
spaces, artists prefixed `@`. 512-1536px, 30-50 steps, CFG 4-5, sampler er_sde / euler_a / dpmpp_2m_sde_gpu;
negatives supported; weak at realism and text. Source: docs.comfy.org/tutorials/image/anima/anima.

**Anima ControlNet-LLLite** (control + inpainting for the Anima base model above). ControlNet-LLLite by kohya-ss,
repacked by Comfy-Org; it loads as a **MODEL_PATCH**, not as a ControlNet, so none of the `ControlNetApply` nodes are
involved. **Licence flag: circlestone-labs NON-COMMERCIAL** (inherited from the Anima base model).
- **Build the graph (confirmed from `comfy_extras/nodes_model_patch.py` on master + the three official templates
  `image_anima_lllite_{any_control_to_image,depth_control_to_image,image_inpainting}`):** take the normal Anima
  text-to-image graph (`UNETLoader` `anima-base-v1.0.safetensors` + `CLIPLoader` `qwen_3_06b_base.safetensors` type
  `stable_diffusion` + `VAELoader` `qwen_image_vae.safetensors`) and insert ONE node on the MODEL line:
  **`ModelPatchLoader`** (category `model/loaders`, reads `ComfyUI/models/model_patches/`) -> `MODEL_PATCH` ->
  **`AnimaLLLiteApply`** ("Apply Anima LLLite", category `model_patches/anima`, EXPERIMENTAL). `AnimaLLLiteApply`
  takes `model` (MODEL), `model_patch` (MODEL_PATCH), `image` (IMAGE, the control map), optional `mask` (MASK), and
  returns a patched `MODEL` that goes on to the sampler. The control image is the node's own input, so there is no
  conditioning-side hookup at all.
- **Its three knobs:** `strength` (default 1.0, range -10..10), `start_percent` (0.0) and `end_percent` (1.0), the
  usual "hold the control over this slice of the schedule" pair, converted internally to sigmas.
- **Which patch file for which control** (all in `Comfy-Org/Anima-LLLite` under `model_patches/`, confirmed by
  listing the repo 2026-07-25): `anima-lllite-any-test-like-v2.safetensors` (generic "any" control, what the
  any-control template ships), `anima-lllite-depth-1`, `anima-lllite-lineart-1`, `anima-lllite-pose-1`,
  `anima-lllite-scribble-1`, `anima-lllite-inpainting-v2` (plus older `-v1` / `-step1000` / `-step2000` /
  `-v2-beta-epoch-03` variants). The lineart, pose and scribble patches have NO template of their own; they drop into
  the same any-control graph with the matching preprocessor.
- **Inpainting is the same node, driven by the mask.** The loader detects a 4-channel-conditioning patch and only
  then is `mask` used; with a 4-channel patch and no mask connected the node silently substitutes an all-zero mask
  (confirmed in the code; that this means "edits nothing" is inferred, not run), and with a 3-channel control patch
  any mask you connect is set to `None` and DISCARDED (confirmed). So a mask that appears to do
  nothing means you loaded the wrong patch file. Template `image_anima_lllite_image_inpainting` draws the mask with
  the `Painter` node and warns to resize inputs past 1024x1024.
- **Feeding the control map:** the any-control template uses `Canny` and notes you can swap in any other
  preprocessor (Node Library -> Comfy Blueprints -> Conditioning & Preprocessors). The depth template builds its map
  with **Depth Anything 3**: `LoadDA3Model` (`depth_anything_3_mono_large.safetensors`, in `models/geometry_estimation/`)
  -> `DA3Inference` (`resolution` 504, `upper_bound_resize`, `mode` `mono`) -> `DA3Render` (`output` `depth`,
  `v2_style`, colored off) -> IMAGE into `AnimaLLLiteApply.image`. Normalize the source first with
  `ResizeImageMaskNode` (`scale total pixels`, 1 MP, `lanczos`).
- **Settings (from all three templates):** 1024x1024, 30 steps, CFG 4.0, sampler `euler`, scheduler `simple`,
  `AnimaLLLiteApply` at strength 1.0 / 0.0 / 1.0, plus `anima-turbo-lora-v0.2.safetensors` on a
  `LoraLoaderModelOnly` at 1.0. Negative stays the standard Anima one (`worst quality, low quality, score_1,
  score_2, score_3, blurry, jpeg artifacts, sepia`).
- **Avoid:** reaching for `ControlNetApply` (wrong node class entirely); putting the patch in `models/controlnet/`
  instead of `models/model_patches/`; expecting the mask to work on a non-inpainting patch.
- **Source:** `comfy_extras/nodes_model_patch.py` (`ModelPatchLoader` detection key `lllite_conditioning1.conv1.weight`,
  `AnimaLLLiteApply` schema) ; `comfy_extras/nodes_depth_anything_3.py` ; huggingface.co/Comfy-Org/Anima-LLLite ;
  original huggingface.co/kohya-ss/Anima-LLLite.

**NewBie (Exp0.1)** (anime t2i), 3.5B Next-DiT (Gemma3-4B + Jina-CLIP-v2, FLUX VAE). Danbooru tags or natural
language, but trained on XML structured prompts that bind attributes per character. Use per-character XML blocks
(`<character_1><gender>1girl</gender><appearance>...</appearance><clothing>...</clothing><action>...</action>
<position>center_left</position></character_1>`) + a `<general_tags>` block for multi-character scenes; flat tags fine
for single subjects. 1024x1024, ~28 steps. Source: docs.comfy.org/tutorials/image/newbie-image/newbie-image-exp-0-1.

**PixelDiT** (t2i), NVIDIA, VAE-free pixel-space DiT (~1.3B, Gemma-2-2B-IT encoder). Plain natural-language positive +
negative (both exposed), no special syntax. No VAE means no reconstruction artifacts, fine texture preserved; 1024px
multi-aspect; steps/CFG not documented. Source: docs.comfy.org/tutorials/image/pixeldit/pixeldit.

**Ovis-Image** (t2i, text rendering), Alibaba AIDC-AI, 7B optimized for legible text. Natural language, put literal
text in quotes inside the description (`[scene/style] + "EXACT TEXT" + [typography/material/lighting]`); best for
posters/banners/logos/UI. 1024px, 50 steps, CFG 5.0; negatives supported. Source: docs.comfy.org/tutorials/image/ovis/ovis-image.

**Lens / Lens Turbo** (t2i), Microsoft, 3.8B MMDiT (GPT-OSS-20B encoder, FLUX.2 VAE); Turbo is the few-step distill.
Clear descriptive natural-language sentences (FLUX/MMDiT conventions); the encoder favors prompt following over tags.
1024px multi-aspect; Lens ~50 steps, Lens Turbo ~4-8 steps; CFG/negatives not documented; encoder can sit on CPU to
fit 24GB. Source: docs.comfy.org/tutorials/image/lens/lens.

**Quiver** (text/image to SVG), API partner node (SVG.io Arrow 1.1 / Max). Natural-language description in `prompt` +
style hints in `instructions` ("minimalist unicorn icon for a SaaS dashboard" / "flat monochrome, rounded corners,
clean geometry"); optional references (up to 4 / 16 on Max) + viewBox attributes. Lower temperature (~0.4) for clean
geometry; output is real editable vector paths. Source: docs.quiver.ai ; blog.comfy.org/p/quiver-structured-svg-generation.

### Video

**HappyHorse 1.1**, Alibaba, cinematic video model with native synchronized audio, API (muapi.ai / Model Studio
partner nodes; ComfyUI nodes `HappyHorseTextToVideoApi` / `HappyHorseImageToVideoApi` / `HappyHorseReferenceVideoApi`):
T2V, I2V, reference-to-video (up to 9 reference images, no cross-contamination; the official ComfyUI template wires 3, image1-3); 3-15s at 720p/1080p, aspect
16:9 / 9:16 / 1:1 / 4:3 / 3:4 / 21:9. **Audio generates in the same render pass** (dialogue, sound effects and
background music synced to the video, no stitching in post). Long-context prompts (2,500+ chars, 6-8 consecutive
scenes in one prompt) and full cinematic language (shot-reverse-shot, tracking shots, transitions); natural skin
holds up for close-up commercial work. Prompt formula still `subject + environment + camera move + motion behavior +
lighting + style`; keep each motion small and specific ("subtle wind in hair", not "dancing in a chaotic crowd"),
ONE camera move per beat (slow pan / dolly-in / handheld push-in). Worked example: "young woman in red jacket on
rainy neon street, medium shot, slow handheld push-in, slight head turn and blinking, wet pavement reflections,
cinematic lighting, consistent face, stable background." R2V: feed identity/outfit/style refs into the
`model.reference_images.image1..9` slots to lock them across cuts (more refs = more consistency). Negatives not
documented (hosted API); settings are API fields (resolution, duration, aspect, audio), no sampler knobs. Official
templates: `api_happyhorse1_1_t2v.json` / `_i2v.json` / `_r2v.json` (Comfy-Org/workflow_templates).
Source: blog.comfy.org/p/happyhorse-11-is-now-available-in ; docs.comfy.org/tutorials/partner-nodes/happyhorse.

**HuMo**, ByteDance + Tsinghua, human-centric video (HuMo-1.7B in ComfyUI): lip-synced video from text + image +
audio. Text describes appearance/action/scene, image conditions identity, audio drives lip-sync; modes Text+Audio and Text+Image+Audio (TIA = most control, best
lip-sync; standalone Text+Image is marked not-implemented for 1.7B in the repo Todo). Up to 97 frames @ 25fps, 720p (~3.9s); TIA wants
>=24GB; negatives not documented. Source: github.com/Phantom-video/HuMo. **ComfyUI build:** HuMo-1.7B runs natively and lip-sync is built into TIA mode; `ckinpdx/comfyui-humo-audio-motion` adds the `HuMoAudioAttentionControlV4` node (audio cross-attention patch; inputs `model` + `audio_blocks`) as an optional experimental audio-driven body-motion enhancement, not the lip-sync itself.

**SCAIL-2**, zai-org (Zhipu/GLM), Wan-based end-to-end character animation: animates a reference character with a
driving video (also replacement, multi-character). Control by inputs, not text: 1 reference image
+ 1 driving video + a per-frame driving mask (generated by the bundled SCAIL-Pose preprocessor; the mask is a required input even in Animation Mode); tune `pose_strength` (exact-copy vs style adaptation).
Source: github.com/zai-org/SCAIL-2. **ComfyUI build:** community all-in-one node `collbroGTR/comfyui-scail2-infinity` (also `TTPlanetPig/comfyui_scail2_multi_cond`); open its example workflow and feed the reference image + driving video + `pose_strength`.

### Audio

**Sonilo**, AI music, ComfyUI partner node: primarily video-to-music (scores a video frame-synced), plus a
text-to-music path. Video-to-music is promptless (analyzes visuals/pacing/emotion); optional brief mood+genre+
instrument phrase refines ("Dreamy ambient electronic", "Lazy jazz instrumental"); output auto-matches the video's
duration, ~20s, multiple variations. Not a lyric/structure tool. Source: docs.comfy.org/tutorials/partner-nodes/sonilo/video-to-music.
