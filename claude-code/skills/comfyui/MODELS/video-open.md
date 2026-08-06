# Video models (open / local-runnable)

Part of the kit's per-model prompting reference. The routing table and the auto-pull rule live in
[`MODELS.md`](../MODELS.md); this file holds the 7 entries for this family.


### Wan 2.1 & 2.2 (Alibaba)
- **Prompt style:** concise cinematic shot description; camera-sees-first, then action, then one camera move; specific descriptors. I2V = motion + camera only (image is the anchor).
- **Structure:** shot type -> subject -> primary action -> one camera move -> environment (3-5) -> lighting -> style -> color.
- **Strengths:** 2.2 better prompt adherence, negative enforcement, camera control, temporal consistency; sequential "first... then...".
- **Avoid:** multiple actions/conflicting camera moves, keyword stuffing, vague descriptors. Negatives ARE supported (best on 2.2): "blurry, low quality, watermark, jittery motion, deformed hands, extra limbs, distorted face, morphing".
- **Settings:** ~5s; native fps 16 (24 for 5B TI2V); ~480-720p by VRAM; prompt ~256 tokens; 14B loads BOTH high-noise + low-noise experts sequentially; 5B TI2V single hybrid (8GB-friendly). Use the official ComfyUI Wan2.2 workflow defaults; run a short low-res test first.
- **Multi-shot temporal control (Prompt Relay):** Wan 2.2 is the NATIVE target of Prompt Relay (arXiv 2604.10030):
  route timed `local_prompts` to their segments via a cross-attention penalty for multi-event clips without
  entanglement (often beats base Wan 2.2 on temporal alignment, near Kling 3.0). Official Wan2.2 implementation +
  ComfyUI port `kijai/ComfyUI-PromptRelay`; node + Smart-syntax details in the LTX-2.3 entry. Source: gordonchen19.github.io/Prompt-Relay.
- **Camera-trajectory control via Uni3C (native since core v0.29.0, PR 14946, CORE-365).** Two nodes, both confirmed from `comfy_extras/nodes_model_patch.py` on master:
  - **`ModelPatchLoader`** ("Load Model Patch") reads from `ComfyUI/models/model_patches/` and auto-detects the Uni3C controlnet by the `controlnet_patch_embedding.weight` key in the state dict. No type widget to set: the same loader also serves Anima LLLite, Qwen DiffSynth, Z-Image Fun and SUPIR, and it picks the architecture from the keys. Its output type is `MODEL_PATCH`.
  - **`WanUni3CControlnetApply`** ("Apply Wan Uni3C ControlNet", category `model/patch/wan`, marked **EXPERIMENTAL**). Inputs: `model` (MODEL), `model_patch` (MODEL_PATCH from the loader), `vae` (VAE), `render_video` (IMAGE), `strength` (FLOAT, default 1.0, -10 to 10), `start_percent` / `end_percent` (0.0 / 1.0). Output: a patched MODEL - so it sits **between the Wan model loader and the KSampler**, not on the conditioning.
  - **`render_video` is the whole point and it is not a normal video.** The tooltip is explicit: it is "the guidance video rendered from the camera trajectory, most commonly warped point cloud renders of the input image". You produce that outside ComfyUI (or with a depth/point-cloud pack) and feed it as an IMAGE batch; the node only takes the first three channels.
  - **Two guards that will stop you:** the patch must actually be a Uni3C controlnet, and its hidden dim must equal the loaded Wan model's `dim`, else the node raises with both numbers. A Uni3C trained against Wan 2.1 will therefore refuse a Wan model of a different width.
  - **Weights:** no Comfy-Org repack exists yet as of 2026-08-01 (checked the Comfy-Org HF author listing: only `Wan_2.1_ComfyUI_repackaged`, `Wan_2.2_ComfyUI_Repackaged`, `Wan-Dancer`). Upstream is `ewrfcas/Uni3C` on HF; community single-file repacks exist. Which Wan widths a given file matches is **inferred, not confirmed** - the honest test is to load it and read the dim mismatch error.
- **Source:** docs.comfy.org/tutorials/video/wan/wan2_2 ; node template `wan_2-1_2-2.md` ; `comfy_extras/nodes_model_patch.py` + `comfy/ldm/wan/uni3c.py` on master, Comfy-Org/ComfyUI PR 14946 (v0.29.0).

### Wan 2.5 / 2.6 (Alibaba, API)
- **Prompt style:** cinematic visual first, then layer audio; multi-shot uses a global style line + timed blocks ("Shot 1 [0-3s]: ..."); I2V describes temporal change only.
- **Structure:** shot -> subject -> action -> one camera move -> environment -> lighting -> style -> `Audio: [dialogue / SFX / ambient / music]`; R2V tags `@Video1/@Video2/@Video3`.
- **Strengths:** synchronized multilingual lip-sync dialogue, ambient/SFX/music, multi-person timbre, multi-shot; make audio specific.
- **Avoid:** audio overpowering visual instruction; vague audio. Negatives supported (~500 chars); LLM prompt expansion on by default.
- **Settings:** API; 720p/1080p; 5/10/15s (R2V 5/10s); aspect 16:9/9:16/1:1/4:3/3:4; audio in WAV/MP3 3-30s. Use API-wrapper/partner nodes.
- **Source:** fal.ai/learn/devs/wan-2-6-prompt-guide ; DashScope/Alibaba Cloud Wan docs ; node template `wan_2-5_2-6.md`.

### Wan 2.7 (Alibaba)
- **Prompt style:** generation formula Subject + Scene + Motion + Aesthetic control (light, shot size, angle, lens, move) + Stylization + `Sound description`. Editing uses imperative commands instead.
- **Structure:** subject (appearance) -> scene -> motion (amplitude + speed) -> aesthetic control -> stylization -> audio; R2V uses numbered indices ("the character in Video 1"), NOT `@Video1`; FLF2V = first -> bridging motion -> end.
- **Strengths:** first+last-frame control, 3x3 image input for cross-shot consistency, up to 5 refs, subject+voice cloning, instruction edits, multi-shot.
- **Avoid:** multiple actions/camera moves per shot, mixing description with edit commands, `@VideoN` tags. Negatives supported.
- **Settings:** API (open Apache-2.0 weights expected Q2 2026); 720p/1080p; 2-15s; ~80-120 words; ComfyUI partner nodes v0.18.5+.
- **Source:** node template `wan_2-7.md` ; fal.ai / Replicate / WaveSpeedAI / Alibaba Cloud DashScope.

#### Wan 3.0: SHIPPED as a hosted beta on 2026-08-06, and you cannot run it (updated the day it landed)
It stopped being a rumour. Alibaba opened a public beta the same day this kit was still calling it unconfirmed.
**What that means for a ComfyUI job, which is the only part that changes your work:**

- **No open weights.** Verified 2026-08-06 by listing the `Wan-AI` org (24 repositories, not one of them a 3.x)
  and searching the whole hub for `Wan3.0` (zero results). Every 3.0 route is hosted.
- **No ComfyUI node, core or API.** Verified against `comfy_api_nodes/nodes_wan.py` on **master**, not the
  local build: ten Wan API nodes, all `Wan2*` or version-neutral (`WanTextToVideoApi`, `WanImageToVideoApi`,
  `WanReferenceVideoApi`, `WanImageToImageApi`, `WanTextToImageApi`). The two "3.0" strings in that file are
  `validate_audio_duration(audio, 3.0, 29.0)`, a float. Control: a known-present sibling file read fine, so the
  absence is the file's, not the probe's.
- **So: if a request says "Wan 3.0 in ComfyUI", the answer is that 2.2 is the newest you can wire.** Point the
  user at Alibaba's own surfaces, or use `Wan2*` nodes for the hosted 2.x API.

**Reported by the vendor and press on launch day, NOT verified here** (the sites are JavaScript apps, so the
numbers below come from the announcement rather than from a page this kit read): native synchronised audio, up
to **30 s**, at 480p / 720p / 1080p. API `wan3.0-video` listed in the Beijing and Singapore regions but still
invitation-only. Pricing around **$0.04 / $0.08 / $0.17 per second** for 480p / 720p / 1080p, and Alibaba bills
the **input reference duration as well as the output**, so a 10 s reference plus 30 s of 1080p lands near
**$6.70** for one clip. Rollout through Alibaba Cloud Model Studio, Wanjing Yike, the Chinese Wanxiang site and
the Qwen Creation desktop app. Early users report speech dropping out, ambience degrading into white noise,
unstable lip-sync, and characters briefly vanishing mid-shot. Treat the price line as the load-bearing one: at
$0.17/s plus input billing this is not a model to iterate on casually.

**What the earlier rumour was conflating it with**, all three real and still worth knowing:
- **Wan Dancer** - shipped, weights `Wan-AI/Wan-Dancer-14B` on HF under **Apache-2.0** (2026-07-10). The
  official template `video_wan_dancer` is in the library. Image plus audio driven character animation.
- **WanSong v1.0** - real technical report, arXiv **2607.14749**.
- **Wan Streamer** - real, `wan-streamer.com` resolves and serves.

**Correction, recorded on purpose:** until 2026-08-06 this block called Wan 3.0 unconfirmed and named a
`Wan-Video` org that hosts zero models, plus a `Wan-skills` repository that does not exist. The right org is
`Wan-AI`. A dated "checked" line does not make a claim durable; a model announced hours later turns it stale.

### LTX-2.3 (Lightricks)
- **Prompt style (official guide):** ONE flowing cinematography paragraph, not tag dumps. Order: shot/framing ->
  scene (lighting, color, texture, atmosphere) -> action (present-tense verbs) -> character (age, clothing,
  features) -> camera move(s) -> audio. Match prompt length to clip length (a 10-word prompt for a 10s clip
  underperforms; longer beats shorter). Dialogue in quotation marks, short phrases with acting beats between them;
  describe performance physically ("pauses, looks aside"), not emotionally ("sad"). Lens/optics terms land
  ("macro lens", "shallow depth of field", "golden hour", "handheld tracking").
- **I2V:** prompt the MOTION / transition only, do not re-describe what is already in the image. Audio-to-video:
  the audio anchors timing, the prompt describes the visual interpretation.
- **Strengths:** native synced audio (more impactful in 2.3), multilingual dialogue (9 langs), smooth I2V, 9:16.
- **Avoid:** internal emotions, readable text/logos (unreliable), chaotic physics, overloaded or self-contradicting
  scenes, numerical over-specification. Negatives: the official guide does not cover them, but templates expose a
  negative conditioning input (works on Dev/CFG>1; Distilled at CFG=1 ignores it).
- **Settings:** width/height divisible by 32; frame count 8k+1 (9, 17, ... 121, 193, 257); fps up to 50; up to
  ~10s; two-stage 2x upsample (official spatial x2/x1.5 + temporal x2 upscalers pair with the base); Dev ~30-40
  steps CFG ~3.0 STG ~1.0; Distilled (8-step, CFG 1) for speed.
- **Run it (ComfyUI):** base t2v/i2v/flf2v/ia2v run on NATIVE ComfyUI core (no extra nodes, just keep ComfyUI
  updated). The IC-LoRA / id-LoRA / lipdub / control workflows REQUIRE the `ComfyUI-LTXVideo` node pack (Manager:
  search "LTXVideo") and its `LTXICLoRALoaderModelOnly`; a generic LoRA loader silently will NOT apply IC-LoRA
  conditioning. Useful IC-LoRAs (into `models/loras`, run via the ic_lora workflow): **Ingredients** (official,
  cross-clip character/prop consistency; two-part prompt "Reference sheet: ... / Generated video: ...", strength
  ~1.4); **MotionDeblur** (oumoumad, community, KEY for RESTORATION: reduces/removes motion blur and reconstructs
  sharper frames; file `ltx-2.3-22b-ic-lora-motiondeblur.safetensors`). Pair MotionDeblur with the LTX-2.3 restore
  templates (restore_archival_footage, remove_watermark) and the SeedVR2/SUPIR upscalers for a restoration chain.
- **HDR IC-LoRA (SDR -> HDR video):** `Lightricks/LTX-2.3-22b-IC-LoRA-HDR` (files `ltx-2.3-22b-ic-lora-hdr-0.9.safetensors`
  + `ltx-2.3-22b-ic-lora-hdr-scene-emb.safetensors`; `license:other`, GATED on HF, so accept the license + use a token
  to download). Per the paper (arXiv 2604.11788, "HDR Video Generation via Latent Alignment with Logarithmic Encoding")
  a logarithmic encoding maps HDR into the model's latent so a light IC-LoRA adapts it without retraining the encoder.
  READY workflow ships in the pack: `ComfyUI-LTXVideo/example_workflows/2.3/LTX-2.3_ICLoRA_HDR_Distilled.json` (with the
  `hdr.py` node + an `hdr_input_video.mp4` example); needs a CURRENT ComfyUI-LTXVideo with BOTH required nodes,
  `LTXICLoRALoaderModelOnly` (loads the LoRA + extracts the downscale factor) AND `LTXAddVideoICLoRAGuide` (adds the small
  latent as a guide), both absent in older installs. Save to an HDR-capable format (EXR / 16-bit / HDR video), NOT 8-bit PNG.
  The single-IMAGE analog of this (same LumiVid paper) is **LumiPic** on Qwen-Image-Edit / Flux.2 Klein - see the Qwen-Image-Edit section. Source:
  huggingface.co/Lightricks/LTX-2.3-22b-IC-LoRA-HDR ; hdr-lumivid.github.io ; github.com/Lightricks/ComfyUI-LTXVideo.
- **Water Simulation IC-LoRA (add water to a live shot):** `Lightricks/LTX-2.3-22b-IC-LoRA-Water-Simulation` (file
  `ltx-2.3-22b-ic-lora-water-simulation-0.9.safetensors`; gated LTX-2-community-license; v2v reference-conditioned).
  Adds rivers / surf / rain / waterfalls / floods / splashes / wet specularities to a "dry" reference clip while keeping
  identity, clothing, pose, camera framing and background geometry identical. Control = the dry video VAE-encoded (24 fps,
  no mask, whole-frame, downscale 1), conditioning on the first `F` frames where `(F-1) % 8 == 0` (e.g. 121 / 153 / 185,
  ~7.7s max). Prompt is dual-panel and MUST contain the trigger `ADD WATER`: "Reference shows <dry scene>. Edited shows the
  same scene with water added. ADD WATER <concrete water: type, motion, how it interacts with the subject>. Subject
  identity, clothing, framing and background are identical to the reference." Worked gallery examples (vary the subject +
  the ADD-WATER clause, keep the wrapper): brown rabbit on mossy rocks -> fast river with white foam over the rocks; hands
  drawing lines in dry sand -> clear shallow water filling the lines; goats on a dirt path -> shallow clear stream
  splashing around their hooves; a hand over dry sand -> calm rippling water, hand dipping and dripping; people and a cart
  in a narrow alley -> murky flood submerging the cart wheels and splashing legs; dogs on a dry pine-needle forest floor ->
  calm reflective flood, dogs in a shallow marsh. Run via a V2V IC-LoRA workflow from the
  `ComfyUI-LTXVideo` pack (`LTX-2.3_V2V_ICLoRA_Single_Stage_Distilled.json` + `LTXICLoRALoaderModelOnly`); no water-specific
  workflow ships yet. **Strength sweet spot 1.2** (1.0-1.05 natural / identity-safe; 1.1-1.5 hard surface replacement like
  ground -> sea; >= 1.5 maximizes drama but warps faces). **CRITICAL recipe:** render the distilled **stage-1 ONLY at native
  resolution** (1920x1088 / 1088x1920, 24 fps), CFG 1.0, 8 fixed sigmas, no negative - the two-stage path applies the
  reference only in stage 1, and the stage-2 upscaler drifts the subject's identity; lowering strength does NOT fix it
  (structural). Trained on real water, so other liquids (lava / slime / paint) generalize only loosely. **Higher res without the
  stage-2 identity drift (kit tip, inferred, not card-tested):** the drift comes from the LTX stage-2 upscaler
  re-diffusing the subject from the prompt, so render the identity-safe stage-1 at native, then upscale OUTSIDE the LTX
  two-stage with a NON-re-diffusing / identity-preserving upscaler (SeedVR2, a tile-GAN like 4x-UltraSharp, or SUPIR at
  low denoise). Resolution rises and the subject stays put. Source:
  huggingface.co/Lightricks/LTX-2.3-22b-IC-LoRA-Water-Simulation ; docs.ltx.video IC-LoRA guide ; github.com/Lightricks/ComfyUI-LTXVideo.
- **3D render to photoreal (3DREAL IC-LoRA):** `fal/LTX-2.3-3DREAL-LoRA`, trigger `3DREAL` (license:other, base LTX-Video).
  An in-context LoRA that turns a rough grey 3D viewport animation (Blender blockouts, game-engine viewports, CG / synthetic
  renders) into photoreal cinematic video, with the 3D render as the reference. Run on fal `fal-ai/ltx-2.3-quality/render-to-real`
  (LoRA built in), or load it as an LTX-2.3 V2V IC-LoRA. Built for CG / synthetic-data to photoreal and viewport-driven final renders.
  Source: huggingface.co/fal/LTX-2.3-3DREAL-LoRA.
- **Multi-shot / timeline direction (Prompt Relay + LTX Director 2.0):** several TIMED events in ONE clip without
  temporal entanglement (one paragraph for many events smears them). **Prompt Relay** (arXiv 2604.10030, S-Lab NTU)
  is a training-free, inference-time method: it routes each prompt to its time segment via a distance penalty in
  cross-attention. Input = a `global_prompt` (persistent character/scene) + ordered `local_prompts` + optional
  `segment_lengths` (latent-frame budget per prompt, summing to (frames-1)//4+1). ComfyUI port:
  `kijai/ComfyUI-PromptRelay` (nodes `PromptRelayEncodeTimeline` + a "Smart" encoder: one field, segments split by
  `|` or `Scene N:` headers, weights `[0-50]`/ranges, auto frame distribution); ready graph
  `prompt_relay_ltx23_test_02.json`; works on LTX 2.3 AND Wan 2.2; WIP, NO license file (use ok, do not
  redistribute). **LTX Director 2.0** (`WhatDreamsCost/WhatDreamsCost-ComfyUI`, GPL-3.0) wraps Prompt Relay into a
  full timeline-editor node for LTX 2.3: trim/split/combine, IC-LoRA track, keyframes, audio inpaint, Retake
  (regenerate a shot segment), save/load timeline; ready graph `LTX_Director_2_Workflow_Hotfix.json` (nodes
  `LTXDirector`/`LTXDirectorGuide` + 2-stage `LTXVLatentUpsampler` + audio). Both REQUIRE current
  `ComfyUI-LTXVideo` + `ComfyUI-KJNodes`, and Prompt Relay monkeypatches cross-attention (version-sensitive).
  Source: gordonchen19.github.io/Prompt-Relay ; github.com/kijai/ComfyUI-PromptRelay ; github.com/WhatDreamsCost/WhatDreamsCost-ComfyUI.
- **Field techniques (community, surfaced from production users; NOT in the official LTXVideo pack unless noted):**
  - **External-audio sync (official nodes, field wiring):** drive video from an external audio track (image + audio ->
    motion/lip-synced clip) with `LTXVAudioVAEEncode/Decode`, `LTXVConcatAVLatent` / `LTXVSeparateAVLatent`,
    `LTXVEmptyLatentAudio`, `LoadAudio`, `TrimAudioDuration` (all official ComfyUI-LTXVideo). Tip: run the source through
    `ComfyUI-MelBandRoFormer` (stem separation) first to feed clean vocals.
  - **Fit the 22B on a 24GB card: GGUF.** `GGUFLoaderKJ` (KJNodes) loads a GGUF-quantized LTX-2.3, shrinking the ~25GB
    fp8 transformer to fit one 24GB GPU (the exact wall this kit hit sizing a 22B run). VRAM win for a small quality cost.
  - **Speed / quality / long clips (KJNodes + CacheDiT):** `CacheDiT_LTX2_Optimizer` (Jasonzzt/ComfyUI-CacheDiT) caches
    diffusion steps to accelerate inference; `LTX2_NAG` (KJNodes) adds Normalized Attention Guidance as a quality/adherence
    lever; `LTXVChunkFeedForward` (KJNodes) chunks the feed-forward to cut memory on long clips; `LTXVAddGuideMulti`
    (KJNodes) drives multi-keyframe (first / middle / last and more) guided motion.
  - **Lipsync + storyboard + long audio: GAP LTX 2.3 Motion** (`github.com/GeekatplayStudio/LTX-2-3-LipSync`, MIT) adds
    nodes for audio-segment render loops, storyboard scheduling, and motion transfer for long-form audio-driven video.
    CAVEAT: users report the storyboard variant's custom-audio path can produce noise, so test the audio leg on a short
    clip first. Status: community-endorsed (widely used in production), NOT independently benchmarked by this kit.
  - **Text / footage to 360 VR video (equirectangular panorama):** LTX-2.3 renders a full 360 equirectangular
    video (2:1, look-around VR) with synced audio. Two community routes, NEITHER official Lightricks: (a) **text
    -> 360** via the public CivitAI LoRA **`360-degree panoramic shot - LTX-2.3`** by Ragamuffin20 / Aitrepreneur
    (`civitai.com/models/2327337`, version 2816797, 643 MB; direct file
    `civitai.com/api/download/models/2816797?fileId=2702793`; base LTXV 2.3; **License: LTXV2** - Lightricks' LTX-2
    license governs, so verify it for your use; the uploader's CivitAI flags separately allow image / rent / sell).
    Trigger phrase **"A 360-degree panoramic video"**, weight **0.6-1** (even ~0.2 can work), aspect **2:1**, over
    the base t2v graph, optionally stacked with the distilled speed LoRA. A ready graph
    `LTX-2.3_360vr_distilled_3stage.json` ships in the panorama-stickers repo; this CivitAI LoRA is the one the
    public Floyo template wraps (corrects my earlier "source unconfirmed" note). KNOWN ISSUE: early versions left a
    visible vertical SEAM where the sphere wraps - the author reports it FIXED (civitai.com/articles/25291), and
    panorama-stickers' Seam Prep node is the in-graph fallback. (b) **flat footage -> 360 outpaint** via
    `TheBurgstall/VR-360-Outpaint-LTX2.3-IC-LoRA` (public, `cc-by-nc-4.0`, **v0.1 proof-of-concept**, file
    `ltx-2.3-22b-ic-lora-360-equirect-poc-step3500.safetensors`): an IC-LoRA that takes a flat 2.39:1 clip + a
    masked equirect reference and fills the unknown regions into a plausible 360 sphere (ready graphs
    `Equirect-Outpaint.json` / `Burgstall-VR-Outpaint.json` in the repo); rough edges outside its sweet spot,
    noncommercial only. Preview either in-canvas with the **`panorama-stickers`** pack (nomadoor, MIT;
    model-agnostic 360 tool, its four nodes are in `NODE_LIBRARY/custom-author.md`); prompt a "seamless
    equirectangular 2:1 360 panorama", keep width/height divisible by 32. **True-VR finishing (both routes,
    optional):** the raw output is MONO 360 - it plays in any 360 / VR player as-is, but for real depth add
    stereoscopic 3D with **`SamSeenX/ComfyUI_SSStereoscope`** (mono equirect -> stereo VR; CAVEAT: it has an upload
    size limit, ~500 MB clips fail, so split or downstream-process long shots), then inject VR metadata so headsets
    auto-detect it with Google's free Spatial Media tool (`github.com/google/spatial-media`). Source:
    civitai.com/models/2327337 ; github.com/SamSeenX/ComfyUI_SSStereoscope ; github.com/google/spatial-media ;
    github.com/nomadoor/ComfyUI-Panorama-Stickers ; huggingface.co/TheBurgstall/VR-360-Outpaint-LTX2.3-IC-LoRA.
- **Train a custom LTX-2 LoRA (own character / style / motion / control):** that is the official Lightricks trainer
  (`Lightricks/LTX-2`, `packages/ltx-trainer`) + their `train-model` Claude skill, NOT ComfyUI; the trained
  `.safetensors` LoRA loads back here via the ComfyUI-LTXVideo loader. Needs Linux + CUDA + >= 32 GB VRAM per GPU
  (a 24 GB or Windows box cannot run it). When a user works with LTX-2 and wants a recurring custom subject/style or
  cross-shot consistency a prompt or the Ingredients IC-LoRA does not give, mention they can train a LoRA and offer
  the setup (one offer, not a nag). Full guide + the offer trigger: `docs/LTX2_TRAINING.md`.
- **Source:** https://ltx.io/blog/ltx-2-3-prompt-guide (official prompt guide) ; docs.comfy.org/tutorials/video/ltx/ltx-2-3 ; huggingface.co/Lightricks/LTX-2.3 ; github.com/Lightricks/ComfyUI-LTXVideo.

### LTX-2 Pro (Lightricks)
- **Prompt style:** single flowing paragraph (4-8 sentences), not tag lists (the model resists keyword dumps); a shot list a camera operator could execute.
- **Structure:** scene anchor (location/time/atmosphere) -> subject + action verb -> camera + lens (movement, focal length, aperture, framing) -> style/color science -> motion/time cue; start with the action.
- **Strengths:** physically plausible camera work, lens/aperture realism, multi-keyframe interpolation, beat-matched audio, camera presets.
- **Avoid:** tag/adjective lists, multiple actions/characters, contradictory shots. Negatives weak at CFG=1 (describe what you WANT).
- **Settings:** 24GB+ -> 720p24/4s/~20 steps; 8-16GB -> 540p24/4s/~20 steps; width/height divisible by 32; frame count divisible by 8 then +1; max prompt ~200 words.
- **Source:** github.com/Lightricks/LTX-2 ; node template `ltx2pro.md`.

### Hunyuan Video (Tencent)
- **Prompt style:** detailed English natural language (MLLM text encoder); include dynamic motion descriptors and explicit camera cues; built-in Prompt Rewrite (Normal vs Master mode).
- **Structure:** subject + appearance -> action/motion (speed/intensity) -> camera movement -> scene -> lighting/style.
- **Strengths:** motion quality and physical realism, instruction following, subject consistency across camera moves.
- **Avoid:** leans on positive description + Prompt Rewrite rather than negatives; FP8 the diffusion model if OOM.
- **Settings (ComfyUI native T2V):** 1280x720x129f, 24 fps; steps ~20-30; sampler euler (default); scheduler simple; CFG ~6.0; denoise 1.0; encoders clip_l + llava_llama3 (fp8_scaled); VAE hunyuan_video_vae; flow-shift 7.0 is the card's scheduler shift value when configuring advanced sampler nodes.
- **VRAM floor (card):** 720p (720x1280x129f) needs ~60GB GPU memory, 540p (544x960x129f) needs ~45GB; a single consumer 24GB GPU CANNOT run 720p even with FP8 (FP8 saves only ~10GB) - use 540p or multi-GPU xDiT.
- **Source:** huggingface.co/tencent/HunyuanVideo ; docs.comfy.org/tutorials/video/hunyuan/hunyuan-video.

### SVD (Stable Video Diffusion, Stability)
- **Prompt style:** NONE (image-conditioned only); motion controlled by numeric parameters, not words.
- **Structure:** provide a conditioning image; tune motion/fps via parameters.
- **Strengths:** animate a strong still into smooth short motion; `motion_bucket_id` is the main dial (higher = more motion).
- **Avoid:** no text-prompt control, no negative prompt; high `noise_aug_strength` drifts away from the input image.
- **Settings:** motion_bucket_id 127 (0-255); fps 7 (5-30); min/max_guidance_scale 1.0/3.0 (interpolated first->last frame); noise_aug_strength 0-1; svd = 14 frames, svd-xt = 25, both 576x1024.
- **Source:** huggingface.co/docs/diffusers/using-diffusers/svd ; stabilityai/stable-video-diffusion-img2vid-xt.
