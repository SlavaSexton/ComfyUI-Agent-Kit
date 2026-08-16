# Video models (open / local-runnable)

Part of the kit's per-model prompting reference. The routing table and the auto-pull rule live in
[`MODELS.md`](../MODELS.md); this file holds the 10 entries for this family.


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

### Wan Animate 2 (Alibaba, open weights, native since core v0.31.0)
Character animation, end to end: a reference image says WHO, a driving video says WHAT MOTION, and the prompt
says what the background and camera do. **No pose or keypoint extraction.** Unlike Wan 2.2 Animate (v1), the raw
driving frames go in directly, so there is no DWPose / OpenPose / skeleton preprocessing stage in the graph at
all. Confirmed from `comfy_extras/nodes_wan.py` on master and the official template `video_wan_animate2.json`.

- **Prompt style:** two prompts, and they do different jobs. The character prompt describes LOOKS ONLY (no motion
  words); the pose prompt describes the MOTION in the driving video. The template's own text is
  `Character Description: ...` newline `Background description: ...` for the first, and a plain motion sentence
  for the second (its shipped example is Chinese: a reference video of a kitten in uniform performing an action).
- **Structure:** `positive` = character appearance + background; `positive_pose` = the motion, e.g. "a person
  dancing". Background is decoupled from BOTH the reference image and the driving video, so it comes only from
  the prompt. The shipped negative is the standard Wan Chinese quality-negative string.
- **The graph** (node ids exactly as registered; the template wraps it in a `Motion Transfer (Wan Animate 2)`
  subgraph, but every node below is core):
  - `UNETLoader` (`wan_animate_2_int8_convrot.safetensors`, weight_dtype `default`) -> `LoraLoaderModelOnly`
    (`lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors`, strength 1.0) -> `ContextWindowsManual`
    -> `WanAnimate2Cache` -> `ModelSamplingSD3` (shift 5) -> `SamplerCustom.model`.
  - `CLIPLoader` (`umt5_xxl_fp8_e4m3fn_scaled.safetensors`, type `wan`) feeds three `CLIPTextEncode`: character,
    negative, and pose.
  - `CLIPVisionLoader` (`clip_vision_h.safetensors`) -> two `CLIPVisionEncode`: one on the resized reference
    image, one on the driving video's first frame (`ImageFromBatch` 0,1).
  - `LoadVideo` -> `GetVideoComponents` -> `ResizeImageMaskNode` -> the pose branch; `LoadImage` ->
    `ResizeImageMaskNode` -> the reference branch. `GetImageSize` on the resized pose frames drives both the
    reference resize and `WanAnimate2ToVideo`'s width/height, so the reference is matched to the driving video.
  - **`WanAnimate2ToVideo`** (category `model/conditioning/wan/animate`, marked EXPERIMENTAL) is the hub.
    Inputs: `positive`, `negative`, `vae`, `width` (832), `height` (480), `length` (81, step 4), `batch_size`,
    plus optional `reference_image` (IMAGE), `pose_video` (IMAGE), `clip_vision_output`, `positive_pose`,
    `clip_vision_output_pose`, `continue_motion` (IMAGE), `video_frame_offset` (INT), `pose_strength` (1.0,
    0 to 10), `pose_start_percent` (0.0), `pose_end_percent` (1.0), `reference_image_strength` (1.0, 0 to 10).
    Outputs, in order: `positive`, `negative`, `latent`, `trim_latent` (INT), `trim_image` (INT),
    `video_frame_offset` (INT).
  - `SamplerCustom` takes `model` from `ModelSamplingSD3`, `positive`/`negative` from `WanAnimate2ToVideo`,
    `sampler` from `KSamplerSelect` (`lcm`), `sigmas` from `BasicScheduler` (`simple`, steps 6, denoise 1),
    `latent_image` from `WanAnimate2ToVideo`. Its LATENT goes to `TrimVideoLatent`, whose second input is
    `trim_latent`, then `VAEDecode` fed by a **`VAELoader`** (`Wan2_1_VAE_bf16.safetensors`) -> IMAGE ->
    `CreateVideo` -> `SaveVideo`.
  - **Two `ComfySwitchNode` (core, `comfy_extras/nodes_logic.py`, display name "If/Else Switch") do the two
    toggles, and you will not find them by reading the happy path.** Its inputs are `switch` (BOOLEAN),
    `on_false` and `on_true`, and it returns `on_true if switch else on_false`. The first instance sits between
    the LoRA and `WanAnimate2Cache`: `on_false` is the model straight from `LoraLoaderModelOnly`, `on_true` is
    the same model through `ContextWindowsManual`, so one boolean turns context windows on and off without
    rewiring. The second sits after `VAEDecode`: `on_false` is the full decoded batch, `on_true` is that batch
    with its first frame removed by `ImageFromBatch(start=1, length=4096)`, driven by a `PrimitiveBoolean`.
    That second switch is the seam trim described below, already wired rather than manual. **Both ship set to
    false**, so out of the box you get no context windows and no seam trim.
  - **The rest of the top level is scaffolding, not generation:** a `ComfyMathExpression` plus `PreviewAny`
    compute and display how many subgraph copies your driving video needs; `BatchImagesNode` concatenates the
    segments; and a second subgraph, `Video Stitch`, builds the side-by-side comparison against the driving
    clip out of `GetVideoComponents`, `GetImageSize`, `ResizeImageMaskNode`, `ImageFromBatch`,
    `ComfyMathExpression` and **`ImageStitch`**, ending in its own `CreateVideo` -> `SaveVideo`. Delete that
    subgraph and you lose only the comparison video, not the result.
- **Settings (read off the shipped template, not guessed):** 832x480, 81 frames, `SamplerCustom` cfg **1**,
  add_noise true, 6 steps, sampler `lcm`, scheduler `simple`, `ModelSamplingSD3` shift 5. cfg 1 and 6 steps are
  only sane because the **lightx2v cfg-step-distill LoRA** is loaded; drop the LoRA and you are back to normal
  Wan step counts. Index metadata puts it at **24 GB** size and 24 GB VRAM.
- **`WanAnimate2Cache` is the speed knob, and it is a RAM tradeoff.** It caches the pose branch's per-block
  activations so the pose video runs once instead of once per sampling step, which the node's own description
  calls roughly half the generation time. Cost: about **12.5 GB of system RAM at 480x832 / 81 frames in bf16**,
  scaling with resolution and length. `device` is `cpu` or `gpu` (`cpu` is the node default), `dtype` is
  `default` / `int8` / `int4` (int8 halves the cache, int4 quarters it). **With context windows use the
  `standard_static` schedule**: uniform schedules shift the windows every step so nothing ever recurs and the
  cache never hits. Naming trap: the cache node's own description tells you to use "static_standard", which is
  the Python constant name (`ContextSchedules.STATIC_STANDARD`); the string the combo actually offers is
  **`standard_static`**, confirmed in `comfy/context_windows.py` and in the shipped template's widget value. The shipped template sets `device=gpu, dtype=int8` while the template's own tip text says to
  use `cpu` to avoid VRAM spikes. Those disagree; on a 24 GB card start at `cpu` and only move to `gpu` if it
  fits.
- **Extending past 81 frames is manual today.** Each subgraph makes 81 frames (about 3.4 s at 24 fps). To go
  longer: duplicate the subgraph (Ctrl-C then Ctrl-Shift-V), wire the previous subgraph's IMAGE into the new
  one's `continue_motion` and the previous `video_frame_offset` into the new `video_frame_offset`, then feed each
  segment's IMAGE into `BatchImagesNode`. Segments overlap by one frame by design; `trim_image` tells you how
  many to drop at the seam. Roughly `driving frames / 81` subgraphs are needed. Native loop support is
  **PR Comfy-Org/ComfyUI 13180, still under review** as of this template, so there is no loop node yet.
- **Gotchas:** framing mismatch between reference and driving video (close-up against full-body) is the
  template's stated number one cause of bad results. Frames are consumed 1:1 with no fps resampling, so resample
  the driving clip to about 16 to 24 fps if the motion reads too slow. `pose_start_percent` / `pose_end_percent`
  also buy speed: outside that window the pose branch is skipped entirely, and since motion is established early,
  an end around 0.7 loosens fine detail while keeping the choreography.
- **Weights: `Comfy-Org/Wan-Animate-2` on HF (Apache-2.0), repackaged from `Wan-AI/Wan2.2-Animate-2-14B`.** All
  filenames below verified present in the repo file listing on 2026-08-09. The template loads
  `diffusion_models/wan_animate_2_int8_convrot.safetensors`,
  `loras/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors`,
  `text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors`, `clip_vision/clip_vision_h.safetensors`,
  `vae/Wan2_1_VAE_bf16.safetensors`. The repo ships **four** diffusion checkpoints, not one:
  `wan_animate_2_bf16` and `wan_animate_2_int8_convrot`, each with a `_distill_` variant. Sizes, read from the
  HF blob listing: bf16 pair **32.79 GB** each (30.5 GiB), int8_convrot pair **16.65 GB** each (15.5 GiB).
  - **The card lists a `text_encoders/umt5_xxl_fp16.safetensors` that does not exist in the repository.** The
    file listing has exactly one text encoder, the fp8_scaled one. Confirmed 2026-08-09 against the API file
    list; the card's own storage table is wrong. Do not go looking for the fp16 encoder here.
  - **The `_distill_` checkpoints replace the lightx2v LoRA, they do not stack with it.** Three pieces of
    evidence: the distill file is byte-for-byte the same size as the base (a remap of the same checkpoint, not
    an adapter); upstream `Wan-AI` publishes Base and Distillation as two separate weight releases; and the
    upstream README runs them differently, base at **40 steps / guidance 3.0**, distillation at **10 steps /
    guidance 1.0**, with the diffusers example commented "no classifier-free guidance". **Still inferred at the
    last step:** no source says in words "do not attach the LoRA to distill". Note the fork this opens: the
    ComfyUI template runs base plus LoRA at **6** steps while upstream runs native distill at **10**, so
    swapping is not automatically faster. Only a run settles it.
- **Four capabilities the paper and the project page advertise that you CANNOT reach from ComfyUI today.** This
  matters because community write-ups list them as features of the release. Each checked against the node
  schema, the ComfyUI template, the upstream inference code and the weight listings on 2026-08-09.
  - **Multi-character animation: no.** `WanAnimate2ToVideo` has one `reference_image` slot, no masks and no
    autogrow, and the execute path takes `reference_image[:1]`, one frame. It is not a ComfyUI gap either:
    upstream's demo script takes a single `--refer-img-file`, and the arXiv paper (2608.06009) does not contain
    the words multi-character or multi-person at all. Only the project page mentions it, as
    "single-to-multiple and multiple-to-multiple", with no described binding mechanism.
  - **Text-driven viewpoint control: no, and the "Viewpoint LoRA" file does not exist anywhere.** The paper
    describes it as a LoRA on the cross-attention projections trained on 48 Unreal Engine camera positions
    (12 azimuths x 4 elevations), with prompt strings shaped like "Right 60-degree View, Top View". **The
    weights are unpublished:** absent from `Wan-AI/Wan2.2-Animate-2-14B` (which holds only base and
    distillation), from the whole `Wan-AI` org listing, from the Comfy-Org repack, from ModelScope, and from
    HF search. Upstream's own inference has no LoRA-loading code and no camera argument. An open upstream issue
    asks for it and has no answer. Treat any recipe that tells you to load a Wan Animate 2 viewpoint LoRA as
    fiction.
  - **Wan-Animate-2-Lite, the real-time streaming variant: no weights exist.** The paper reports 24 fps at
    400x720 on a **4x H100** cluster, split one GPU for VAE encode, **two for a 3-step DiT**, one for decode.
    The abstract promises to release only the Base weights. Distilled and Lite are different things and the
    community already conflates them.
  - **Character replacement is a REGRESSION against v1, not a feature.** The v1 node `WanAnimateToVideo` has
    `background_video`, `character_mask` and `face_video`; `WanAnimate2ToVideo` has none of the three. To drop a
    character into existing footage keeping the plate, you stay on **Wan 2.2 Animate v1**, template
    `video_wan2_2_14B_animate.json`, which needs `ComfyUI-segment-anything-2`, `comfyui-kjnodes` and
    `comfyui_controlnet_aux` and does the DWPose plus SAM2 preprocessing that v2 exists to avoid. Animate 2
    does motion transfer onto a prompt-generated background, and that is all.
- **Gotcha with real teeth: `positive_pose` silently keeps only the first conditioning entry.** The node reads
  `pose_cond[0][0]`, so a `ConditioningCombine` fed into the pose branch loses everything after the first item
  with no warning. A reviewer asked for a warning on the merging PR and it was not added.
- **Hardware, and the honest version for a 24 GB card.** Upstream tunes its defaults for **8x A800 at 720p** and
  reports testing **2x A800 at 480p**; there is no VRAM table and no single-GPU path in the upstream repo. In
  ComfyUI the template's index entry claims 24 GiB, which puts a 3090 or 4090 exactly on the line. The
  arithmetic that matters: `wan_animate_2_distill_int8_convrot` is 15.5 GiB, and the template ships
  `WanAnimate2Cache` at `device=gpu, dtype=int8`, which the node's own numbers put near 5.8 GiB, so **21.3 GiB
  is committed before a single activation**. The template's own tip text says to set the cache to `cpu`. Take
  the tip, not the default, especially with 128 GB of system RAM available. **Inferred:** sampler activations
  at 81 frames were not measured here, so the remaining headroom is a subtraction, not a benchmark. Note also
  that two 24 GB cards do not add up: ComfyUI does not shard one diffusion model across GPUs.
- **Source:** `comfy_extras/nodes_wan.py` on master (classes `WanAnimate2ToVideo`, `WanAnimate2Cache`, both
  registered in `WanExtension`) ; official template `video_wan_animate2.json` including its four MarkdownNote
  guides ; ComfyUI core release **v0.31.0** (2026-08-08), PR 15362 "feat: Support Wan-Animate2 (CORE-358)" by
  kijai, merged 2026-08-07, plus its review thread ; blog.comfy.org "Wan Animate 2 is now available in ComfyUI"
  (2026-08-08) ; upstream `Wan-Video/Wan-Animate-2` (README, `wan_animate_2_demo.py`, pipeline and model code),
  `Wan-AI/Wan2.2-Animate-2-14B` card and file listing, and arXiv **2608.06009v1**. Read 2026-08-09.

### SCAIL-2 (zai-org / Zhipu, open weights, NATIVE in core since 2026-06-09)
Character animation and **character replacement** driven by raw video plus a colored per-identity mask. Built on
**Wan 2.1 I2V 14B** (dense, `in_dim 20`, `mask_dim 28`, and it still loads the Wan 2.1 CLIP vision, which Wan 2.2
dropped), so it is a Wan 2.1 derivative, not a Wan 2.2 one.

**Correction, recorded on purpose:** until 2026-08-09 this kit said the ComfyUI path was the community pack
`collbroGTR/comfyui-scail2-infinity`. That was wrong. Core merged `Comfy-Org/ComfyUI` PR **14373** (kijai) on
2026-06-09 and multi-reference PR **14509** on 2026-06-17. The nodes are in `comfy_extras/nodes_scail.py`, two
official templates ship (`video_wan21_scail2_character_replacement.json` and its `_int8` twin) plus subgraph
blueprints, and detection is by the `patch_embedding_mask.weight` key, so **plain `UNETLoader` recognises the
checkpoint with no special loader**. Community packs are now an optional layer, not the road in.

- **Where it beats Wan Animate 2, which is the fork that actually matters.** Both eat raw driving video with no
  skeleton. But SCAIL-2 keeps the three things Animate 2 does NOT have in ComfyUI: **multi-character** (6
  identities), **character replacement into an existing plate**, and a **Relighting LoRA**, replacement mode
  only. In the ComfyUI repack that file is `loras/wan2.1_SCAIL_2_relight_lora_bf16.safetensors` (1.23 GB), not
  the `model/relighting-lora.pt` name the upstream repo uses; take the repack name. The same repack also ships
  `loras/wan2.1_SCAIL_2_DPO_lora_bf16.safetensors` (1.23 GB), which is the one the official template loads.
  Community write-ups that put those in the
  Animate 2 column are reading Wan Animate **v1**. Conversely Animate 2 needs no mask at all, and SCAIL-2 needs
  one always, even in Animation Mode. That mask is the real cost of this model.
- **The graph** (node names and every widget value below read off the official template
  `video_wan21_scail2_character_replacement.json`, which wraps the work in a `Character Replacement (SCAIL-2
  Base)` subgraph):
  - **Model side:** `UNETLoader` (`wan2.1_14B_SCAIL_2_fp16.safetensors`) -> **two** `LoraLoaderModelOnly` in
    series, first `lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors` at **0.8**, then
    **`wan2.1_SCAIL_2_DPO_lora_bf16.safetensors` at 1.0** (a DPO preference LoRA shipped with the model, easy
    to miss and not mentioned in any community write-up) -> `ModelSamplingSD3` shift 5 -> `SamplerCustom`.
    `CLIPLoader` (`umt5_xxl_fp8_e4m3fn_scaled.safetensors`, type `wan`) and `VAELoader`
    (`Wan2_1_VAE_bf16.safetensors`) as usual.
  - **Do not misread the loaders:** there is also a `CheckpointLoaderSimple` in this graph, and it loads
    **`sam3.1_multiplex_fp16.safetensors`**, the SAM3 tracker, not the diffusion model.
  - **Mask side:** `CheckpointLoaderSimple` (SAM3) feeds **two** `SAM3_VideoTrack` nodes, one for the driving
    video and one for the reference image, and both go into `SCAIL2ColoredMask`. Same on a plain MASK if you
    already have one -> its optional `reference_masks` input.
  - **`SCAIL2ColoredMask`** ("Create SCAIL-2 Colored Mask", category `model/conditioning/wan/scail`) has
    `object_indices` (comma-separated, e.g. `0,2,3`, empty = all), `sort_by` (`none` / `left_to_right` /
    `area`, default `left_to_right`) and `replacement_mode`. Outputs `pose_video_mask` and
    `reference_image_mask`.
  - **`sort_by` IS the character binding.** There are no named slots. The node paints a fixed 6-colour palette
    onto tracked objects in that order and uses **the same order on both outputs**, which is what ties an
    identity in the reference to the same identity in the driving video. Objects appearing in earlier frames
    always sort first.
  - **`WanAnimate2ToVideo`'s counterpart here is `WanSCAILToVideo`** (same category, EXPERIMENTAL). Inputs:
    `positive`, `negative`, `vae`, `width` 512, `height` 896 (**both step 32**), `length` 81 (step 4),
    `batch_size`, then optional `pose_video` (**downscaled to half the main resolution by the node**),
    `pose_video_mask`, `replacement_mode`, `pose_strength` 1.0 (0 to 10), `pose_start` 0.0, `pose_end` 1.0,
    `reference_image`, `reference_image_mask`, `clip_vision_output`, `video_frame_offset`,
    `previous_frame_count` 5, `previous_frames`. Outputs: `positive`, `negative`, `latent`,
    `video_frame_offset`.
  - Then the tail: `SamplerCustom` -> `VAEDecode` -> **`ColorTransfer`** -> `CreateVideo` -> `SaveVideo`, with a
    second `CreateVideo` / `SaveVideo` pair and `PreviewImage` for the comparison view, and
    `BatchImagesNode` + `ComfyMathExpression` + `PreviewAny` doing the chunk bookkeeping at the top level.
  - **`ColorTransfer`** ("Transfer Color", core `comfy_extras/nodes_post_processing.py`, category
    `image/filters`) is not decoration in a replacement graph: it matches the generated character's colours
    back to the plate. Inputs `image_target`, `image_ref`, `method` (`reinhard_lab` / `mkl_lab` / `histogram`)
    and a `source_stats` DynamicCombo (`per_frame` / `uniform` / `target_frame`, the last revealing a
    `target_index`). For a locked-off plate `uniform` avoids the per-frame flicker `per_frame` can introduce.
  - **Shipped sampling settings:** `SamplerCustom` add_noise true, cfg **1**, `KSamplerSelect` **`euler`**,
    `BasicScheduler` `simple` at **6** steps, `ModelSamplingSD3` shift 5. cfg 1 at 6 steps is the lightx2v
    distill LoRA doing its job, same trick as Wan Animate 2. The `PrimitiveInt` / `PrimitiveFloat` nodes in the
    subgraph expose 6 and 40 steps and cfg 1 and 5 as switchable presets, which is the un-distilled fallback.
  - **Template resolution is 512x896 at length 65**, not the node defaults, so do not assume 81 here.
- **The palette is not decorative.** Core hardcodes `DEFAULT_PALETTE` as exactly blue, red, green, magenta,
  cyan, yellow with the comment that the model was trained on these exact colours, and assigns them `i % 6`.
  **Six identities is the ceiling**, and a seventh silently reuses the first colour. White is background.
- **`replacement_mode` must match in BOTH nodes or you get garbage.** It flips the mask background on each
  output in opposite directions: Animation Mode = driving mask on black, reference mask on white; Replacement
  Mode = the reverse. `WanSCAILToVideo` also turns it into the `ref_mask_flag` on the conditioning, so the two
  nodes disagreeing means the model is told one thing and shown another.
- **Multi-reference:** the first `reference_image` in the batch is the primary (composite every identity onto
  it); extra batch images are additional views (back view, close-up, occluded background), each needing a
  matching entry in the `reference_image_mask` batch in that identity's colour.
- **Long video is chunked, and this is a real streaming path**, contrary to comparisons that say it has none:
  feed the previous chunk's full decoded output into `previous_frames` and its `video_frame_offset` into the
  next chunk. Trained at `previous_frame_count` **5** with 81-frame chunks and a 76-frame step. The node
  subtracts the anchor frames from the offset itself.
- **Weights** (`Comfy-Org/SCAIL-2`): fp16 32.79 GB, fp8_scaled 17.69 GB, int8_convrot 16.65 GB, mxfp8 17.15 GB,
  and an nvfp4 mix whose filename carries a typo (`mxpf8`) that you must copy verbatim. Community GGUF quants
  exist. **No author has ever published a VRAM requirement** for this model, in the card, either README, the
  ComfyUI docs or the issue tracker; numbers circulating online are file sizes relabelled as requirements.
- **Licence is split:** the code repo `zai-org/SCAIL-2` carries Apache-2.0 with a LICENSE file; the weights are
  marked `license: mit` in the HF card frontmatter with no licence text shipped alongside them.
- **Two things this entry used to get wrong besides the pack:** `pose_strength` was described as "exact-copy vs
  style adaptation"; it is a ComfyUI-side multiplier whose tooltip reads "Strength of the pose latent", and the
  string does not appear in the upstream repo at all. And the mask preprocessor was called "the bundled
  SCAIL-Pose"; on the native path masks come from **SAM3**, and the kijai `ComfyUI-SCAIL-Pose` pack targets
  SCAIL-Preview (v1) and predates this model.
- **Source:** `comfy_extras/nodes_scail.py` on master (`WanSCAILToVideo`, `SCAIL2ColoredMask`, `DEFAULT_PALETTE`,
  registered in `SCAILExtension`) ; `Comfy-Org/ComfyUI` PRs 14373 and 14509 ; official templates
  `video_wan21_scail2_character_replacement{,_int8}.json` ; `zai-org/SCAIL-2` repo and config `config-14b.json` ;
  `Comfy-Org/SCAIL-2` file listing. Read 2026-08-09.

### LTX-2.5 (Lightricks, open weights, native in core v0.32.0, day-0 2026-08-12)
- **What changed from 2.3.** Pixel Diffusion (keyframe-grid generation), a diffusion video decoder (sharper faces
  and legible text in fast motion), native multishot in a single generation, a **custom Gemma 4 12B text
  encoder** in place of the previous encoder, a dedicated **Prompt Enhancer** model, Auto Duration, and a much
  stronger distilled variant. Synchronized audio and 4K carry over from 2.3. Confirmed from the official
  `video_ltx2_5_t2v.json` MarkdownNote. The kit's LTX-2.3 entry below is NOT superseded: the IC-LoRA, Director
  and 360 tooling all target 2.3 and does not carry over.
- **Gate first.** The weights are gated. Accept access at huggingface.co/Lightricks/LTX-2.5 BEFORE downloading,
  or every link 403s (stated in the template's own note).
- **Files (exact names, from the template's Model Links note):**
  - `diffusion_models/ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors`
  - `vae/ltx-2.5-video-vae-bf16.safetensors` and `vae/ltx-2.5-audio-vae-bf16.safetensors` (two separate VAEs)
  - `text_encoders/gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors` (the conditioning encoder)
  - `text_encoders/gemma4_e2b_it_bf16.safetensors` (a SECOND, small Gemma 4 that only drives the Prompt Enhancer)
  - `latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors`
- **Build the t2v graph (every node confirmed by parsing `video_ltx2_5_t2v.json`, subgraph "Text to Video
  (LTX-2.5)"; the shipped template hides all of this inside a subgraph, so "Enter subgraph" to see it):**
  - Loaders: `UNETLoader` (weight_dtype `default`) -> MODEL. `VAELoader` x2, one per VAE. `CLIPLoader` with
    **type `ltxv`** for the 12B encoder, and a second `CLIPLoader` type `ltxv` for the E2B enhancer model.
    `LatentUpscaleModelLoader` -> LATENT_UPSCALE_MODEL.
  - Prompt path: `PrimitiveStringMultiline` (your prompt) -> `TextGenerateLTX2Prompt.prompt`, with the E2B
    `CLIPLoader` -> its `clip`. `ComfySwitchNode` picks `on_true` = enhanced text, `on_false` = your raw text,
    switched by a `PrimitiveBoolean`. The switch output goes to `CLIPTextEncode.text` (positive). A second
    `CLIPTextEncode` holds the negative (template ships `pc game, console game, video game, cartoon, childish,
    ugly`). Both use the 12B `CLIPLoader`.
  - `CLIPTextEncode` (pos, neg) -> `LTXVConditioning` (`frame_rate`, template 24) -> positive/negative out.
  - Latents: `EmptyLTXVLatentVideo(width, height, length, batch_size)` and
    `LTXVEmptyLatentAudio(frames_number, frame_rate, batch_size, audio_vae)` -> both into
    `LTXVConcatAVLatent(video_latent, audio_latent)` -> one packed AV latent.
  - Stage 1: `SamplerCustomAdvanced` with `RandomNoise` (user seed), `LTXVDualCFGGuider(model, positive,
    negative, video_cfg, audio_cfg)`, `KSamplerSelect` = **`euler_ancestral`**, and `ManualSigmas` =
    `1.0, 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421875, 0.0` (8 steps).
  - Upscale: `LTXVSeparateAVLatent` -> video latent into `LTXVLatentUpsampler(samples, upscale_model, vae)`
    (x2, video VAE), audio latent passes through untouched -> a second `LTXVConcatAVLatent`.
  - Stage 2: a second `SamplerCustomAdvanced`, `RandomNoise` seed **42 fixed**, its own `LTXVDualCFGGuider`,
    `euler_ancestral`, `ManualSigmas` = `0.85, 0.7250, 0.4219, 0.0` (3 steps).
  - Decode: `LTXVSeparateAVLatent` -> video into `VAEDecodeTiled` (video VAE; widgets `512, 64, 64, 16`), audio
    into `LTXVAudioVAEDecode` (audio VAE) -> both into `CreateVideo(images, audio, fps)` -> `SaveVideo`.
- **The half-resolution trap, and it is the one thing that breaks a hand-built copy.** The template runs stage 1
  at HALF the target size. `ComfyMathExpression` `a/2` sits on both width and height into
  `EmptyLTXVLatentVideo`; the x2 latent upsampler restores full size before stage 2. Feed the full width into
  the empty latent and you render at 2x the intended resolution and pay for it. Frame count is a third
  `ComfyMathExpression` `a * b + 1` (duration x frame_rate + 1), which lands on LTX's 8k+1 frame grid: 5 s at
  24 fps = 121 frames. The same value feeds `LTXVEmptyLatentAudio.frames_number`, so video and audio stay aligned.
- **Resolution.** A top-level `ResolutionSelector` (`16:9 (Widescreen)`, `0.9` megapixels, multiple `32`) drives
  the subgraph's width/height. That combination computes to **1280x736**, not the 1280x720 sitting in the
  subgraph's own widgets: the link overrides the widget, so the widget value is dead. Verified by running the
  node's arithmetic (`round(16*sqrt(0.9*1024*1024/144)/32)*32`) and against the template's own megapixel table.
- **Settings that are not obvious:** the distilled transformer runs at **`video_cfg` 1.0 and `audio_cfg` 1.0**
  (both `LTXVDualCFGGuider` instances in every shipped template). `LTXVDualCFGGuider` exists precisely to give
  the audio half of the packed latent a different scale from the video half; at equal scales it falls back to
  plain single-CFG (read from `Guider_LTXAVDualCFG.predict_noise` in `comfy_extras/nodes_lt.py`). Raising
  `audio_cfg` alone is the supported way to push audio adherence.
- **Prompt Enhancer, what it actually does.** `TextGenerateLTX2Prompt` detects `gemma4` in the loaded clip name
  and switches to the LTX 2.4 system prompts, wraps your text in Gemma 4 turn markers, strips any `<think>`
  block, and **falls back to your original prompt if the model returns nothing** (all four behaviours read from
  `comfy_extras/nodes_textgen.py`). Template widgets: `max_length` 600, sampling on, temperature 0.7, top_k 64,
  top_p 0.95, min_p 0.05, repetition_penalty 1.15, thinking off, use_default_template on. Turn it OFF when you
  have already written a full cinematography paragraph; it is for expanding short prompts.
- **Auto Duration is real but NOT wired in any LTX-2.5 template.** `LTXVDurationPredictor` lives in
  `comfy_extras/nodes_lt.py` and needs a separate LTX 2.4 duration head loaded through `ModelPatchLoader` into
  its `duration_head` input; it outputs `num_frames` (snapped to the 8k+1 grid) and raw `seconds`. Nothing in
  the three shipped graphs uses it, so treat it as an opt-in extra, not part of the default recipe.
- **i2v differences (from `video_ltx2_5_i2v.json`):** `LoadImage` -> `ResizeImageMaskNode` (`scale longer
  dimension`, 1536, `lanczos`) -> `LTXVPreprocess` (`img_compression` **18**) -> `LTXVImgToVideoInplace`. That
  node appears TWICE: strength **1.0** on the stage-1 latent, strength **0.7** on the upsampled stage-2 latent.
  It rewrites the latent in place rather than producing conditioning, so it sits between the concat and the
  sampler, not next to `CLIPTextEncode`.
- **flf2v differences (from `video_ltx2_5_flf2v.json`), and they are larger than they look:** there is **no
  upsampler and no second stage**. One `SamplerCustomAdvanced` only, driven by `SamplerEulerAncestral`
  (eta 0, s_noise 1) instead of `KSamplerSelect`, on the 8-step sigma list. Both frames go
  `LoadImage` -> `ResizeImageMaskNode` (`scale dimensions`, **640x360 fixed**, `center`, `nearest-exact`) ->
  `LTXVPreprocess` (18) -> `LTXVAddGuide`, first frame at `frame_idx` **0** and last at **-1**, both strength
  **0.7**, then `LTXVCropGuides` before sampling. There is no `ResolutionSelector` in this template.
- **Prompting.** The 2.3 guidance below still applies (one flowing cinematography paragraph, dialogue in
  quotes, physical performance not emotions). The shipped 2.5 prompts confirm the style and add one habit worth
  copying: they state the constraint explicitly at the end, for example `No text, no black frames.` in the i2v
  example, and they name in-image text as a full sentence about the lettering rather than a bare string.
- **Ecosystem, week of 2026-08-12 (reported, NOT verified against the files):** Lightricks published a
  texture-preserving spatial upscale LoRA and a community NVFP4 quantization around 18 GB aimed at Blackwell
  cards. Neither is referenced by any official template and neither filename has been read here, so do not
  build a graph on them from this line; treat it as a pointer to go check.
- **Source:** official templates `video_ltx2_5_{t2v,i2v,flf2v}.json` (nodes, links and widget values parsed, not
  eyeballed) and their MarkdownNote guides ; `comfy_extras/nodes_lt.py`, `nodes_lt_audio.py`,
  `nodes_lt_upsampler.py`, `nodes_textgen.py`, `nodes_resolution.py` on master ;
  blog.comfy.org/p/ltx-25-day-0-support-in-comfyui ; huggingface.co/Lightricks/LTX-2.5. Read 2026-08-15.

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
    public Floyo template wraps (corrects the earlier "source unconfirmed" note). KNOWN ISSUE: early versions left a
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
- **Status, 2026-08-15: the API nodes for this generation are DEPRECATED.** Both `LtxvApiTextToVideo` and
  `LtxvApiImageToVideo` carry `is_deprecated=True` in `comfy_api_nodes/nodes_ltxv.py` on master, and the
  official `api_ltxv_text_to_video.json` / `api_ltxv_image_to_video.json` templates were **deleted** from the
  library in the same week LTX-2.5 landed (verified by diffing the template repo). Build new hosted graphs on
  the LTX-2.5 partner nodes in [`video-api.md`](video-api.md). The local weights and everything below still
  work; only the hosted path moved.
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
