# Changelog

All notable changes to **ComfyUI-Agent-Kit** are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow
[Semantic Versioning](https://semver.org/). Dates are YYYY-MM-DD. The raw, per-commit history lives in git;
this file is the curated summary.

**How the numbers work (`MAJOR.MINOR.PATCH`):** bump **PATCH** for backward-compatible bug fixes, **MINOR** for
new backward-compatible features (most updates here, e.g. new model recipes or a new agent adapter), and **MAJOR**
for a breaking change (e.g. renaming a config key or the install layout). `0.x` was pre-release development;
`1.0.0` is the first stable public release. To cut a release: decide the bump from what sits under `[Unreleased]`,
rename it to `[x.y.z] - <date>`, tag the commit (`git tag -a vx.y.z -m ...`), and push the tag (`git push origin
vx.y.z`), which can become a GitHub Release.

## [Unreleased]

## [2.7.0] - 2026-08-02

### Added
- **A second shipped skill: `seedance`.** ByteDance's Seedance video models run on Dreamina, Jimeng AI,
  Doubao and the BytePlus API as well as inside ComfyUI, so their prompting knowledge could not live
  inside a ComfyUI skill without being wrong half the time. It ships as its own skill in three layers:
  `SKILL.md` routes, `reference.md` is normative and carries only ByteDance primary sources plus
  parameters read from ComfyUI's node code, and `supplementary.md` holds third-party observations in a
  subordinate layer with an explicit conflict ledger. Bundled for the Claude Code plugin by
  `tools/build_plugin.py`.
- **The official Seedance 2.5 mechanics**, from the Dreamina Seedance 2.5 User Guide (ByteDance, last
  modified 2026-07-31). The 2.5 prompt formula is `[creatives description] + [one-sentence summary] +
  [specific plot description] + [overall supplement]`. The three-module long-video formula includes an
  explicit anti-collapse block whose "prohibited" slot is where sound, subtitle and known-fragile items
  go. The real-person character formula runs seven dimensions with a sub-formula each, including the
  official anti-plastic trick: the literal suffix "retaining the true micro pores and skin texture".
- **Timestamp direction, which reverses the 2.0 advice.** Seedance 2.0's official guide calls precise
  timing unstable and tells you not to force it. **2.5 shipped timestamp control as a headline feature,
  built for exactly that request**, with the documented syntax `0s-3s:` / `3s-8s:`. Both versions are
  now stated separately so an agent does not apply 2.0's warning to 2.5.
- **Exact 2.5 limits and the official stability guidance that contradicts "more references is better":**
  30 images, 10 videos and 10 audio clips (single 2 to 30s, 30s total each), audio-only input now allowed
  where 2.0 required at least one image or video, duration [4, 30] which is 97 to 721 frames, and output
  at **480p or 720p** (the third-party "native 4K" claim is refuted; 4K is an input resolution only).
  ByteDance's own numbers: 1-5 subjects work well, 6-10 lose stability, and above 5 subjects you should
  split viewpoints into separate images rather than supply one multi-view image.
- **The modes, with the ceiling that is easy to get wrong.** Long Video generates 30 to 180 seconds in
  one shot. Extend Video accepts only sources under 30s, adds 4 to 30s per operation and nests, so the
  extreme case is a 30s original extended by 30s for **60s, and that is the ceiling on that path**.
- **The Blender route, which turned out to be official.** Clay Renderer is a Dreamina plugin for Maya and
  Blender: set the camera route in your DCC, export the white-model video, upload through the plugin, and
  Seedance references the white-model action and camera movement.

### Fixed
- **Two plugin manifests had drifted and nobody was watching them.** `.claude-plugin/marketplace.json`
  and `claude-code/.claude-plugin/plugin.json` both advertised **67 model prompt recipes** against an
  actual 75, and `plugin.json` still declared **version 1.9.0** while the repo shipped 2.6.0. Same class
  as the GitHub About box: a surface that no file edit touches and no count sync reached. Both corrected,
  and the manifest counts are now part of the release checklist.

### Added
- **Seedance 1.5 Pro, a whole tier the recipe had been silent about.** `docs/MODEL_INDEX.md` already listed
  it; `MODELS.md` did not mention it once, so an agent reading the recipe would never reach it. The weekly
  cycle could not catch this because `check_updates.py` reports only the delta since the last run and 1.5
  predates the window. Now documented with the parameters read from `comfy_api_nodes/nodes_bytedance.py`,
  including three facts no prompt guide carries: the node enforces a **4 second minimum** even though the
  slider allows 3, `generate_audio` is honoured **only** for 1.5 Pro and **doubles the price**, and
  `raise_if_text_params` **rejects settings written into the prompt text**.
- **Seedance 2.5 status, recorded so nobody builds against it.** It launched 2026-07-31 and has **no
  ComfyUI nodes**; the recipe now says so explicitly and points at 2.0 as the newest available in ComfyUI.
  The 2.5 deltas that are confirmed (30 images + 10 video + 10 audio per pass, 30s per generation with
  multi-round extension, against 9+3+3 and 15s for 2.0) come from the official ByteDance Seed blog.
- **Routing to the new `seedance` skill** for the family's full prompting mechanics: the three task types
  and the one word that switches between them, the `@Image 1` label syntax, the `（）<>{}【】` symbols,
  shot sequencing, the counterintuitive official rule to use 4 to 5 assets rather than the 50-asset
  ceiling, and the failure table for face drift, duplicate characters, unwanted subtitles and extension
  seams. Distilled from the official BytePlus ModelArk prompt guide.


## [2.6.0] - 2026-08-01

### Added
- **Smart Upscaler taught to the kit** (`docs/NODE_LIBRARY/smart-upscaler.md`), our own eleven-node pack for
  tiled upscaling that writes a separate verified prompt for EVERY tile. This is the gap the kit's existing
  tiling ladder had: Ultimate SD Upscale, Tiled Diffusion / MultiDiffusion and Steudio Divide and Conquer all
  tile the SAMPLING but not the PROMPT, so every tile gets the same text or a captioner describes each tile in
  isolation, which is why a crop of roof captions as "brown texture" and neighbouring tiles disagree at the
  seam. Smart Upscaler reads the whole image once, then derives each tile's prompt from that shared reading,
  finds flat regions by MEASURING pixels rather than asking a model, and never tells a tile about an object
  its own pixels do not confirm. The entry is buildable: all eleven class names and display names, every
  category and I/O type, the full chain (Prompt Director -> Output-Scale Tiles -> Whole-Image Analysis -> Tile
  Job Director -> Exact-Tile Prompt -> engine switch -> Color Match -> Finish and Blend, with the two review
  nodes hanging off it), and the shipped Z-Image Turbo reference values. Carries the traps that cost real time:
  `caption_images` is a SEPARATE stream from `tile_images` and feeding the wrong one captions the padding; a
  stale `cache_tag` makes a caption-model change look inert; the `SMART_PROMPT_SYSTEM` wire must reach all
  three consumers or they fall back to their own defaults; and an edit-model prompt style on a denoise model
  grows objects that were never in the picture. **Marked honestly as not yet published** - no repository or
  Registry entry exists, so the entry carries no install URL, and nothing in it was executed or benchmarked.
- **A core detail worth knowing beyond this pack:** applying a **Z-Image** Fun tile ControlNet through the
  **Qwen**-named `QwenImageDiffsynthControlnet` is correct, not a mistake. In
  `comfy_extras/nodes_model_patch.py`, `ZImageFunControlnet` subclasses it and inherits the same
  `diffsynth_controlnet` implementation; only the input arrangement and the menu category differ.
- **Mage-Flow / Mage-Flow-Edit - new official recipe (Microsoft, 4B, MIT).** One compact stack that does both
  text-to-image and instruction editing, and **one node does both jobs**: `TextEncodeMageFlowEdit`
  (`model/conditioning/mage`) takes `clip` + `prompt` + optional `vae` + an Autogrow `image_1..image_16` group and
  returns `positive` / `negative` / **`latent`**, so you must NOT wire an `EmptyLatentImage` - the sizes would not
  match. Width/height of 0 fall back per-axis to the first reference's size (1024x1024 with no reference) and are
  floored to a multiple of 16; the latent is `[batch, 128, h/16, w/16]`. Two separate resize paths, read from the
  code: every reference is resized to the OUTPUT resolution before VAE encode (Mage's RoPE aligns reference and
  target by position), while the copy fed to the VL text encoder is capped at a 384px long edge. Graph:
  `UNETLoader` -> `KSampler.model`, `CLIPLoader` (**type `mage`**) -> the encoder, `VAELoader` -> the encoder and
  `VAEDecode`, encoder outputs -> `KSampler` -> `VAEDecode` -> `SaveImageAdvanced`; edit adds
  `LoadImage` -> `image_1`. Settings from the upstream table: Base 30 steps / CFG 5.0, RL 20 (30 for Edit),
  Turbo 4 / CFG 1.0, euler + simple. Carries the naming trap that `mage_flow_bf16` is the **RL** checkpoint and
  `mage_flow_base_bf16` is Base (upstream calls the RL model plain `microsoft/Mage-Flow`), the open 2K quality
  complaint (gh 15099), and the int8 caveats.
- **MiniMax H3 (Hailuo 03) - three new partner nodes**, folded into the existing MiniMax recipe:
  `MinimaxHailuo03TextToVideoNode`, `MinimaxHailuo03FirstLastFrameNode` and `MinimaxHailuo03ReferenceNode`. All
  three nest their widgets inside a `model` DynamicCombo (so they read `model.prompt`, `model.duration`, ...),
  resolution is `2K` only, duration 5 to 15s. First-last-frame validates each image at 2:5 to 5:2 aspect and
  256x256 minimum BEFORE spending anything; the reference node takes up to 9 images / 3 videos / 3 audio clips and
  audio cannot be used without an image or video. Prompting is by connection order in the prose ("Image 1",
  "Video 1"), and the official template shape is a technical header, then the scene, then a second-by-second beat
  sheet, then a bracketed VFX list, then exclusions. Cost is duration x $0.1859, read from the node's own price
  badge.
- **Recraft V4 and V4.1**, folded into the Recraft recipe (which said "V3" only, and was therefore silent about a
  whole model generation). Exactly two new nodes ship, `RecraftV4TextToImageNode` and `RecraftV4TextToVectorNode`;
  there is no V4 image-to-image or inpainting node, so edits still route through V3. Their `model` DynamicCombo
  swaps the `size` list with the tier (14 sizes from 1024x1024 standard, the same 14 shapes doubled from 2048x2048
  on `_pro`). Records that **`negative_prompt` on the V4 nodes is a dead input** - the tooltip says it is ignored
  and `execute()` never reads it - plus the 10,000-character prompt cap and the SVG output needing `SaveSVGNode`.
- **Ideogram P-Image**, the new fast tier (`IdeogramPImage`). Documents the `quality` / `resolution` /
  `prompt_upsampling` widgets and the second output that actually matters: **`final_prompt`**, the caption the
  image was really generated from. Feed it back with `prompt_upsampling` = `OFF` and the same seed to reproduce a
  result. The node's own tooltips supply the rules the kit now repeats: text renders poorly below `MEDIUM`, prefer
  `HIGH` + `2K` for typography, and switch upsampling OFF whenever you pass your own JSON caption. The Ideogram
  entry's "nodes available" line was stale at v0.28.0 and now reads v0.29.2.
- **Uni3C camera-trajectory ControlNet for Wan** (`ModelPatchLoader` -> `WanUni3CControlnetApply`, EXPERIMENTAL),
  in the Wan recipe. The apply node patches the MODEL, so it sits between the model loader and the KSampler, not
  on the conditioning. The part that is easy to get wrong: `render_video` is not footage, it is the guidance video
  rendered from the camera trajectory (warped point-cloud renders of the input image). Two guards will stop you -
  the patch must be a Uni3C controlnet, and its hidden dim must equal the loaded Wan model's `dim`. No Comfy-Org
  repack exists yet, so the weights pointer is marked inferred.
- **The MCP 2026-07-28 specification, and what it means for this kit** (`docs/LAYERS.md`, Layer 2). MCP's
  protocol core went **stateless**: the `initialize` handshake and `Mcp-Session-Id` are retired, every request
  is self-describing, so any request can land on any instance behind a plain load balancer. Server-to-client
  calls become Multi Round-Trip Requests, `Mcp-Method` / `Mcp-Name` headers allow body-free gateway routing, and
  list responses carry `ttlMs` / `cacheScope`. Roots, Sampling, Logging and legacy HTTP+SSE are deprecated on a
  twelve-month window. Documented honestly for a kit user: **`comfyui-mcp` rides the SDK's 1.x line**
  (`@modelcontextprotocol/sdk ^1.12.1`), so the driver you run speaks the previous revision, that stays
  supported, and there is nothing for you to change; the v2 TypeScript line ships as separate scoped packages,
  so adopting it is the driver author's migration, not a version bump.
- **The dependency trap for anyone maintaining their own MCP server** (`docs/LAYERS.md` + `KNOWN_ISSUES.md`).
  An unbounded pin like `mcp>=1.2.0` now resolves to Python SDK **2.0.0**, which renamed `FastMCP` to
  `MCPServer` and removed `mcp.server.fastmcp`, so fresh installs die on the first import while running
  instances carry on. Fix: pin `mcp>=1.28,<2` or migrate. The migration note carries the part that fails
  SILENTLY: every transport parameter moved off the constructor and off `mcp.settings` onto `run()`, so
  `mcp.settings.host = ...` no-ops instead of erroring. Learned first-hand, our own AI VFX MCP server hit it.

### Changed
- **`docs/KNOWN_ISSUES.md` refreshed to core v0.29.2 / frontend v1.49.3.** New open rows: Mage-Flow quality
  degradation at 2048x2048 (gh 15099), Ideogram 4 int8 templates dying on Apple Silicon MPS with
  `aten::_int_mm` unimplemented (gh 15133), and `ImageBlend` `difference` mode clamping every negative pixel to
  black because `comfy_extras/nodes_post_processing.py` computes `img1 - img2` with no `abs()` (gh 15178,
  verified in source, not taken from the report). The ComfyUI-LTXVideo import break is still open with a second
  report (gh 15070, 15145). Moved to "Recently fixed": the v0.29.1 `user.css` regression, the v0.29.1 SVG
  preview restore after the stored-XSS hardening, the v0.29.0 streaming video transcode, the Mage-Flow fix for
  cards without bf16, and the Anima AMD R9700 speed regression.
- **Counts synced across every surface:** 74 -> **75 recipes** (Mage-Flow is a new family; MiniMax H3,
  Recraft V4.1, Ideogram P-Image and Uni3C extend existing entries), 578 -> **583 templates**. The template
  library's distinct-model count stays 157: Mage-Flow and MiniMax H3 arrived, Kling 1.6 and Kling 2.0 were
  archived out of the library along with the retired Runway Gen3a templates. Image also overtook Video as the
  largest template category (157 vs 149), so the category chart was reordered.

## [2.5.0] - 2026-07-25

### Added
- **HeyGen - new official recipe (avatar video, talking photo, video translate, TTS).** A presenter/avatar stack,
  not a scene generator, and the five nodes each do one job: **`HeyGenTalkingPhotoNode`** (`LoadImage` -> `image`,
  VIDEO out), **`HeyGenAvatarVideoNode`** (standalone, VIDEO out), **`HeyGenCreateAvatarNode`** (`avatar_id` STRING
  + `preview` IMAGE out; feed the ID into Avatar Video's `custom_avatar_id`), **`HeyGenVideoTranslateNode`**
  (`LoadVideo` -> `video`, VIDEO out) and **`HeyGenTextToSpeechNode`** (AUDIO out). Documented the two DynamicCombo
  widgets that decide what you can even see: `speech` (`script` exposes `text` / `voice` / `custom_voice_id` /
  `voice_speed`; `audio` replaces them with an AUDIO input) and `engine` on Avatar Video (`auto` / `avatar_iv` /
  `avatar_iii` / `avatar_v`, each filtering the avatar list, with the per-second price of each). Also the traps: a
  voice is required on Talking Photo but optional on Avatar Video, `background_color` must carry a leading `#`, the
  2000px auto-downscale, the 5000-character script cap, and `seed` being a re-run trigger that HeyGen never
  receives. Confirmed from `comfy_api_nodes/nodes_heygen.py` on master plus templates
  `api_heygen_{avatar_video,talking_photo,text_to_speech,video_translate}`.
- **JoyAI Image Edit (JD, Apache-2.0) - new official recipe.** Native core support via
  `comfy_extras/nodes_joyimage.py`: one node, **`TextEncodeJoyImageEdit`**, which tokenizes the instruction WITH
  the reference images and appends their `reference_latents` when a VAE is connected. Full graph documented
  (`CLIPLoader` at type **`joyimage`**, the **Wan 2.1 VAE**, `ImageScaleToTotalPixels` at 1 MP feeding both the
  node and `GetImageSize` -> `EmptySD3LatentImage`, `CFGNorm` on the MODEL line rather than the conditioning,
  40 steps / CFG 4.0 / euler / normal), plus the `images` Autogrow socket (`images.image0`, zero-based and
  namespaced, up to six slots) for multi-reference edits and the 49 fixed ~1MP aspect buckets. **Flagged a broken source:** the `Comfy-Org/JoyAI-Image-Edit` card body was copy-pasted from the
  *Plus* release and lists `joyai_image_edit_plus_*` filenames the repo does not host; the real files were
  confirmed by listing the repo.
- **Anima ControlNet-LLLite - control and inpainting for the existing Anima recipe.** Loads as a **MODEL_PATCH**,
  so `ControlNetApply` is the wrong node entirely: `ModelPatchLoader` (from `models/model_patches/`) ->
  **`AnimaLLLiteApply`** (`model` + `model_patch` + `image` control map + optional `mask`, knobs `strength` /
  `start_percent` / `end_percent`) -> sampler. Documented all ten published patch files (any / depth / lineart /
  pose / scribble / inpainting), the rule that a mask only applies to a 4-channel inpainting patch and is silently
  discarded otherwise, the Depth Anything 3 chain that builds the depth map
  (`LoadDA3Model` -> `DA3Inference` -> `DA3Render`), and the template settings. **Licence flag: non-commercial.**
- **Krea 2 Turbo image style reference on CORE nodes.** The `krea2_style_reference` LoRA (ostris) generates in the
  style of a reference image with no trigger word. The HF card says a custom node is required; the official
  template `image_krea2_turbo_int8_image_style_reference` does it with core nodes only, and that full chain is now
  documented (`LoraLoaderModelOnly` -> `ModelSamplingFlux` -> `CFGGuider` at cfg 1.0,
  `TextEncodeQwenImageEditPlus` carrying the reference, `FluxKontextMultiReferenceLatentMethod` at
  `index_timestep_zero`, 8 steps). Licence flag: krea-2-community-license.

### Changed
- **Credits and licensing brought up to date.** `ATTRIBUTION.md` and the README "Credits and thanks" now name
  kohya-ss for Anima ControlNet-LLLite (non-commercial), ostris for the Krea 2 style-reference LoRA, and JD
  (jd-opensource) for JoyAI Image Edit. Two pre-existing gaps were closed at the same time: ostris's
  `ComfyUI-Krea2-Ostris-Edit` nodes and reverentelusarca's detail-enhancer LoRA had been documented in
  `MODELS.md` since an earlier release with no attribution row.
- **Counts refreshed for the 2026-07-25 template sync:** 74 recipes (was 72), 157 indexed models (was 153),
  578 templates (was 562, +16 this week); 94 Subgraph Blueprints unchanged. README, `docs/MODEL_INDEX.md`, the
  GitHub About box, the three chart generators and `tools/assets/cover_gen.py` were all updated and the four
  banner PNGs re-rendered and visually verified.
- **`docs/KNOWN_ISSUES.md` refreshed to 2026-07-25.** Four new open bugs: the core commit `7c59a078d` that removed
  `interleaved_freqs_cis` and kills the whole ComfyUI-LTXVideo pack on master, `int8_convrot` NaN/black output on
  RDNA4 ROCm, Qwen Image Edit silently exiting on PyTorch cu130, and Custom Combos not updating their index output
  inside subgraphs (which breaks Comfy's own Blueprints). Nothing moved to "Recently fixed": four of the five
  closures in the window were `NOT_PLANNED`, not fixes. Also recorded two maintenance gotchas: the
  `comfyanonymous/ComfyUI` -> `Comfy-Org/ComfyUI` redirect that the GitHub search API refuses to follow, and the
  need to read `stateReason` before calling a closed issue fixed.

## [2.4.0] - 2026-07-18

### Added
- **Sync 3 (sync.so) - new official recipe.** A dedicated LIP-SYNC model, not a general video generator:
  re-sync the mouth of existing footage to new speech (**`SyncLipSyncNode`**, "sync.so Lip Sync": `video` +
  `audio` -> VIDEO), or animate a single still portrait from an audio track (**`SyncTalkingImageNode`**,
  "sync.so Talking Image": `image` + `audio` + an OPTIONAL text prompt -> VIDEO, output length matching the
  audio). Documented the knobs that actually matter: `sync_mode` (`bounce` / `cut_off` / `loop` / `silence` /
  `remap`, which also sets the output length), face location by `default` / `auto-detect` / `coordinates` for
  multi-face shots, the 4K input ceiling and the constant-24/25/30-fps preference, and the node's own warning
  that results are non-deterministic regardless of seed. Confirmed from `comfy_api_nodes/nodes_sync_so.py` plus
  templates `api_sync_so_{lip_sync_video,talking_image}`.

### Changed
- **ComfyUI core v0.28.0 swept (released 2026-07-15).** Two BREAKING removals now flagged in the docs:
  **`IdeogramV1` and `IdeogramV2` nodes were removed** (an older graph loading them will not resolve, rebuild on
  `IdeogramV3` / `IdeogramV4`), and **all StabilityAI partner nodes were removed**. Also folded in: the Seedream
  node's new **disable-thinking widget** (leave it on for the CoT behaviour this kit's recipe assumes, turn it
  off for a faster literal pass), and **native INT4 convrot** with its same-release fix for black images on
  Turing - so the ADVANCED.md quantization note now covers int4, the official int8 TEMPLATES that shipped across
  the library, and the open `int8 model cause PC crash` report.
- **Counts: 71 -> 72 recipes, 152 -> 153 models, 549 -> 562 templates.** Synced across README, MODEL_INDEX,
  SKILL.md and all four banners (re-rendered and checked pixel by pixel). Template category counts recomputed
  from the official manifest, where **Video (149) has now overtaken Image (145)**.

### Fixed
- **KNOWN_ISSUES.md refreshed to 2026-07-18** (it had drifted to 2026-07-01). New open entries: whole-machine
  crashes on int8 models (#14985), Nodes Manager extensions broken after the 0.28.0 update (#14967), SeedVR2
  showing no temporal consistency on video (#14970), plus the two node removals above. New fixed entries: four
  security vulnerabilities closed in v0.28.0 (GHSA-779p-m5rp-r4h4), crashes on undecodable audio streams /
  `UNetSelfAttentionMultiply` / Load3D path validation / Qwen3-VL tokenizer, the HLG inverse-OETF clamp fix, and
  the **dropped PyTorch 2.4 support** (upgrade PyTorch before upgrading core).
- Stale counts caught while syncing: the SKILL.md routing line still called our OCIO pack "eight nodes" (it has
  been nine since OCIO v1.2.0), and README still advertised a "545-template library".

## [2.3.1] - 2026-07-12

### Fixed
- **Ideogram 4 structured-control nodes restored (they are real).** v2.3.0 wrongly claimed the
  `Create Bounding Boxes -> Build JSON Prompt (Ideogram)` flow had "no dedicated bounding-box or JSON-builder
  node." Those nodes exist in current ComfyUI core: **`CreateBoundingBoxes`** (`comfy_extras/nodes_bounding_boxes.py`;
  outputs `preview` / `bboxes` (BOUNDING_BOX) / `elements` (ARRAY)), **`BuildJsonPromptIdeogram`** ("Build JSON
  Prompt (Ideogram)", `nodes_json_prompt.py`; the ARRAY plus `high_level_description` / `background` / `style` /
  `aesthetics` / `lighting` / `medium` / `color_palette` COLORS -> a DICT caption), and **`Ideogram4Scheduler`**
  (`nodes_ideogram4.py`). The v2.3.0 note was written after checking only `nodes_ideogram.py` (V3 / V4 only)
  against a local core (0.25.1) that predated these modules, and no template uses them yet; the
  `CreateBoundingBoxes` widget landed in frontend v1.48.2 (2026-07-11). MODELS.md now documents the real
  buildable chain (`CreateBoundingBoxes` -> `BuildJsonPromptIdeogram` -> Ideogram 4), confirmed from the node
  source. The Grok `1K` / `2K`, `ModelMergeKrea2` and `quant_int8_convrot.py` corrections from v2.3.0 stand.

## [2.3.0] - 2026-07-11

### Added
- **Seedream 5.0 Pro (ByteDance) - new official recipe.** ByteDance's latest image model: multi-modal in ONE node
  (`ByteDanceSeedreamNodeV2` - text-to-image + precise image editing + multi-image inputs), strong character /
  product consistency, region-precise editing, and structured layouts (legible small text); official templates
  `api_bytedance_seedream_5_0_pro_{t2i,image_edit}`. Shares the Seedream 5.0 CoT prompt style (no quality boosters).
- **Seed Audio 1.0 (ByteDance) - new official recipe.** A new audio model: generates a full audio SCENE (sound
  design + named-character dialogue + background music) in one pass, three modes t2a / ta2a / ti2a
  (`ByteDanceSeedAudio` -> `SaveAudioAdvanced`); official templates `api_bytedance_seed_audio1_0_{t2a,ta2a,ti2a}`.
- **INT8-ConvRot is native in ComfyUI v0.27.0 (ADVANCED.md refresh).** ComfyUI v0.27.0 shipped native int8-convrot
  weight quantization - the **ConvRot** rotation-based method (arXiv 2512.03673): ~half the FP16 size, faster than
  FP16, matches or beats FP8, faster + cleaner than FP8 on Turing / Ampere, and small enough to bring big models
  to 8-12 GB (and Pascal) cards (LTXV 2.3 1920x1088: 268 s -> 140 s). Refreshed the ADVANCED.md INT8 note (native
  path + the ConvRot paper + the `comfy-model-tools` `quant_int8_convrot.py` converter + Comfy-Org's HF weight
  uploads for Wan 2.2 Animate / Z-Image / SeedVR2; extends to INT4, covers DiT / LLM / multimodal / UNet), and
  updated the Flux2-Klein entry (its `INT8-ConvRot` quant now loads natively). The third-party `ComfyUI-INT8-Fast`
  is now fully superseded.
- **Comfy-MSS - music source separation pack (`NODE_LIBRARY/audio.md`).** Documented `pymss-project/comfy-mss`
  (ComfyUI nodes for the `pymss` library): split an `AUDIO` stream into instrument / vocal stems via MSS and
  VR/UVR models, with ensemble / normalize / phase-invert utilities - a fuller-featured alternative to the
  single-purpose MelBandRoFormer stem step.
- **ComfyUI-OCIO reference bumped to v1.2.2** (`NODE_LIBRARY/ocio.md` + ADVANCED.md + README). No node changes
  since v1.2.0 (still nine nodes on the native VIDEO wire); v1.2.1 / v1.2.2 add a reproducible Dockerized CI
  round-trip test and an honest accuracy write-up. Corrected the accuracy story: the headline is per-transform
  bit-exact parity (**0.000e+00**), the end-to-end `ACEScg -> LogC -> Rec.709 -> back` round-trip is **4.5e-6**
  max (single-precision LUT residual - NOT bit-for-bit lossless, but ~100x below a half-float EXR delivery grid),
  and the histogram chart is a distribution-shape sanity check, not an accuracy proof. The Docker / CI round-trip
  harness is credited to **Sam Hodge** (PR #1); the nodes + accuracy suite are Slava Sexton's. Also fixed the
  stale "eight nodes" README / BUILDING_NODES count to **nine** (OCIO Player shipped in v1.2.0).
- **ComfyUI v0.27.0 coverage swept.** Beyond INT8-ConvRot: added an **Ideogram 4 JSON-prompt note** to the Ideogram
  entry (write the `IdeogramV4` prompt itself as a structured JSON-style caption; the official `api_ideogram_v4_t2i`
  template builds it with a `GeminiNode` magic-prompt - there is no dedicated bounding-box or JSON-builder node),
  a **Grok Image `1K` / `2K` resolution** note, and the core **`ModelMergeKrea2`** block-merge node. Verified the rest of
  v0.27.0 is already in the kit (Seedance 2.0 Mini + 4K, HappyHorse 1.1, the Nano Banana 2 Lite + Gemini Video Omni
  partner nodes, and the v0.27.0 INT8 / frontend-Manager bugs already in KNOWN_ISSUES).
- **Instruction editing on Krea 2 (community, experimental).** Added to the Krea 2 entry: `ostris/ComfyUI-Krea2-Ostris-Edit`
  (Ostris / AI Toolkit - a Text Encode + Model Patch node pair that feeds reference latents into Krea 2, a
  text-to-image model, so it can edit an input image) and the community edit LoRA
  `reverentelusarca/krea2-detail-enhancer-edit-lora` (a detail enhancer, trigger "enhance this image",
  krea2-community-license). Flagged with the author's own honest caveats - not Flux.2 Klein / Qwen-Image-Edit
  precision (alters the image, shifts lighting/color, can fault on horizontal aspect ratios).

Count change: **69 -> 71 recipes, 150 -> 152 models, 545 -> 549 templates** - from the two new official ByteDance
recipes (Seedream 5.0 Pro image + Seed Audio 1.0 audio) picked up by the Saturday weekly-update check; INT8-ConvRot,
Comfy-MSS, the v0.27.0 doc sweep and the Krea 2 edit method do not change the counts. All count places synced
(README, MODEL_INDEX, and the cover / models_by_modality / architecture / templates banners re-rendered; chip now
`152 models · 71 recipes`).

## [2.2.0] - 2026-07-06

### Added
- **General ComfyUI node-authoring lessons from the ComfyUI-OCIO v1.2.0 video pipeline.** Folded 9 universal,
  pack-agnostic lessons into `BUILDING_NODES.md` (+ VIDEO specifics in `NODE_LIBRARY/video.md`): the
  mutually-exclusive IMAGE-or-VIDEO dual socket (`VideoFromComponents`), the reload-safety `app.configuringGraph`
  guard (a mishandled `onConnectionsChange` wipes the whole graph's links), why an OUTPUT slot cannot be safely
  hidden, the Vue-nodes `RETURN_NAMES` fix, the servable-temp-file video-preview contract, `VALIDATE_INPUTS` for
  renamed combo values, the Windows temp-file ffmpeg decode (12-25x faster than a subprocess pipe), the on-node
  float/HDR WebGL viewport pattern, and the limits of scripting a live-ComfyUI screenshot.
- **ComfyUI-OCIO reference refreshed to v1.2.0** (`NODE_LIBRARY/ocio.md` + the ADVANCED.md mention). Was pinned at
  v1.0.1 (eight nodes); now documents nine nodes, the native ComfyUI VIDEO pipeline (mutually-exclusive
  IMAGE-or-VIDEO sockets on all nine), the new **OCIO Player** on-node viewport, and the bit-exact accuracy proof
  (0.000e+00 max-abs error across 9 transforms x 4 fixtures). Historical CHANGELOG entries left untouched.
- **LumiPic - single-image SDR -> HDR LoRA.** Documented `oumoumad/LumiPic` (MIT) under Qwen-Image-Edit in
  MODELS.md: the IMAGE analog of the LTX-2.3 HDR IC-LoRA (same LumiVid paper, arXiv 2604.11788), a LoRA that emits
  an ARRI-Log-encoded frame decoding to scene-linear HDR EXR. Covered the three bases (Qwen-Image-Edit-2511
  mature; Flux.2 Klein 4B / 9B alpha), the LogC3 (ceiling ~55) vs LogC4 (V10 alpha, ceiling ~470) curves and which
  checkpoints to pick, the ComfyUI route (ready HF graphs + the ComfyUI_Gear decode node), and the honest V10
  caveat (Qwen V10 gain shows in diffusers but not yet in ComfyUI; `klein4b_v10_logc4_step1500` is the one that
  holds up). Cross-linked from the LTX-2.3 HDR entry and ADVANCED.md.
- **ComfyUI_Gear (oumad) node pack.** Added to `NODE_LIBRARY/custom-author.md`: LogC3 / LogC4 Decode + Save EXR
  (also decodes our LTX-2 HDR IC-LoRA) and a full ACEScct Color Grade panel. Flagged the honest relation to our
  ComfyUI-OCIO - Gear decodes but keeps the source primaries, so for an ACEScg master use our OCIO's
  `OCIOLogConvert(logc3)` + `OCIOColorSpace(Rec.709 -> ACEScg)`; Gear's edge is LogC4 (a curve our OCIO lacks) plus
  the grade panel.
- **Nano Banana 2 Lite - new official recipe (68 -> 69 recipes, 149 -> 150 models).** Its own MODELS.md entry:
  the fast / cheap Nano Banana tier, official Comfy partner API nodes / templates `api_nano_banana_2_lite_t2i` /
  `_image_edit` (confirmed in the Comfy-Org templates index, not just the launch post). Vendor speed / price
  claims (~4 s, ~$0.034 / 1K) marked as marketing; cloud / paid. Counted as a buildable official recipe AND a
  distinct model per the same rule that counted Gemini Omni Flash.
- **Divide and Conquer tiled upscale (`Steudio/ComfyUI_Steudio`).** Auto-tile-sizing upscaler (computes the optimal
  resolution, splits into seamless tiles, merges back) added to ADVANCED.md as an alternative to Ultimate SD
  Upscale / Tiled Diffusion. Surfaced by community field research; credit to the pack author, Steudio.

Count change: **68 -> 69 recipes, 149 -> 150 models**, from Nano Banana 2 Lite only. LumiPic, ComfyUI_Gear, and the
Divide and Conquer tiler do NOT change the counts - community LoRAs / techniques / tools, on already-counted bases.
All count places synced: README, MODEL_INDEX, and the cover +
models_by_modality banners re-rendered (chip now `150 models · 69 recipes`); the models_by_modality chart's stale
per-modality alt text (37/20/66) was corrected to the real 39/21/69 in the same pass.

## [2.1.4] - 2026-07-01

### Added
- **360 / VR equirectangular panorama - Flux.2 Klein AND LTX-2.3 (two separate routes).** The shared
  `nomadoor/ComfyUI-Panorama-Stickers` pack (MIT, Comfy Registry v1.3.0; four ERP nodes: Panorama Stickers /
  Cutout / Preview / Seam Prep) is documented model-agnostically in `NODE_LIBRARY/custom-author.md` - it is a
  360 projection tool, not a model-specific pack - and referenced from BOTH recipes. (1) **Flux.2 Klein 360
  IMAGE** (under FLUX.2 in MODELS.md): nomadoor's 360-ERP-outpaint LoRAs (`flux-2-klein-4B-...` apache-2.0,
  `...-9B-...` license:other). (2) **LTX-2.3 360 VIDEO** (under LTX-2.3): text-to-360 via the public CivitAI LoRA
  `360-degree panoramic shot - LTX-2.3` by Ragamuffin20 / Aitrepreneur (`civitai.com/models/2327337`, direct
  download `api/download/models/2816797?fileId=2702793`) - the LoRA the Floyo template wraps, which CORRECTS the
  prior "source unconfirmed" note - and flat-to-360 outpaint via `TheBurgstall/VR-360-Outpaint-LTX2.3-IC-LoRA`
  (`cc-by-nc-4.0`, v0.1 POC). Full card detail folded in from the CivitAI page: License **LTXV2** (not the blanket
  "commercial-OK" I first wrote), trigger `A 360-degree panoramic video`, weight 0.6-1, aspect 2:1, the wrap-seam
  artifact the author reports fixed (civitai article 25291), plus true-VR finishing steps (mono->stereo via
  `SamSeenX/ComfyUI_SSStereoscope`, VR metadata via Google `spatial-media`). The Flux (image) and LTX (video)
  routes are unrelated and kept in their own model sections; neither cross-references the other for the pack.
- **Flux2-Klein-9B-True-V3 (community fine-tune) recipe.** A wikeeyang aesthetics / composition fine-tune of
  FLUX.2 [Klein] 9B (text-to-image + prompt-only instruct edit + LoRA face-swap / try-on + Mask+LoRA regional
  edit), with its full quant ladder (`bf16` / `fp8mixed` / `int8mixedrow` / `INT8-ConvRot` / `mxfp8` / `nvfp4` /
  GGUF `Q4_K..Q8_0`). Added under FLUX.2 in MODELS.md, with a license caveat: the card is tagged Apache-2.0 but
  the weights derive from FLUX.2 [Klein], so verify the base license before commercial use. Distinct from
  nomadoor's 360-outpaint Klein LoRA above.
- **INT8 inference acceleration note (ADVANCED.md).** INT8 weight quantization is now native in ComfyUI
  (~1.5-2x over fp8 on 40-series+ per the source pack), which largely supersedes the `ComfyUI-INT8-Fast` pack;
  documented when to use the native loader vs the pack, the loader/naming mismatch, and `convert_to_comfy.py`
  for old quants, using the Flux2-Klein-V3 dual INT8 quants as the worked example.
- **OCIO node docs refreshed to ComfyUI-OCIO v1.0.1** (`NODE_LIBRARY/ocio.md`, + a note in ADVANCED.md).
  Documented the v1.0.1 OCIO Write additions - `colorspace_in_name` (colorspace before the frame number,
  `name_acescg.0086.exr`), `auto_colorspace` (auto Rec.709 -> ACEScg when wired from LTX's HDR decode), and
  Nuke-style EXR `compression` - plus the new `logc3` (ARRI LogC3) curve on OCIOLogConvert and a worked LTX-2
  HDR -> ACEScg EXR-sequence recipe (automatic + manual). Confirmed from the shipped v1.0.1 source; flagged that
  the pack's `pyproject.toml` still reads 1.0.0 at the v1.0.1 tag (a version-bump miss in the pack, not the docs).

Recipe / model counts are unchanged (still 68 recipes / 149 models). These are community fine-tunes / LoRAs / a
tool built on base models the count already includes (FLUX.2 Klein, LTX-2.3), so they add NO new official model -
the same double-counting reason the (fully PUBLIC) kijai ecosystem is documented in KIJAI.md rather than folded
into the 149. That is a SEPARATE exclusion from private / client-trained models, which is about IP, not
public-vs-not: kijai is fully public. The cover banner does not change.

## [2.1.3] - 2026-07-01

### Fixed
- **Installer catches a partial template clone instead of reporting success.** `shared/install_shared.ps1` now checks the exit code of each `git` step of the workflow-template clone (clone / sparse-checkout / checkout) and only prints "cloned + index built" when all three succeeded; a non-zero exit now falls through to the "template clone incomplete" warning. Previously it relied on a `Test-Path index.json` check alone, which could report success when the sparse-checkout or checkout failed after a partial clone. (Hardening suggested by the installing user's own fix.)
- **The per-agent installers had the same NativeCommandError bug as the shared one.** `agents/claude/install.ps1` and `agents/codex/install.ps1` clone the node-building skills (and codex registers its MCP) with `& git clone ... 2>&1 | Out-Null` / `& codex mcp add ... 2>&1 | Out-Null` under `$ErrorActionPreference = "Stop"`, so the same non-fatal stderr could abort the adapter install. Both now route those calls through the `Native` helper. The gemini / qwen adapters make no native calls and were unaffected.

## [2.1.2] - 2026-07-01

### Fixed
- **Windows installer no longer aborts on a harmless npm warning.** With `$ErrorActionPreference = "Stop"`, PowerShell 5.1 turns a native command's stderr (piped as `2>&1 | Out-Null`) into a terminating `NativeCommandError`. So a non-fatal npm deprecation warning (`prebuild-install@7.1.3 deprecated`) during `npm install -g comfyui-mcp` aborted the whole install. `shared/install_shared.ps1` now runs npm / git / python through a `Native` helper that drops `$ErrorActionPreference` to `Continue` for the call and gates success on the real exit code (so genuine failures still stop the install), and passes npm `--loglevel=error`. Reproduced on PowerShell 5.1 (`& ... 1>&2 ... 2>&1 | Out-Null` under Stop threw `NativeCommandError`) and confirmed the fix tolerates the warning while still catching a non-zero exit. Reported by an installing user.

## [2.1.1] - 2026-06-30

### Fixed
- **Corrected the Gemini Omni Flash entry - v2.1.0 described the integration wrong.** v2.1.0 claimed there was no official Comfy partner node or template for Gemini Omni Flash. That was wrong: it leaned on a stale local server (ComfyUI 0.25.1, which does not have the node yet) plus a *summarized* read of the templates index instead of the raw JSON. A direct read of `Comfy-Org/workflow_templates` confirms the official partner node **`GeminiVideoOmni`** with three shipped templates (`api_google_gemini_omni_flash_t2v` / `_i2v` / `_video_edit`). MODELS.md now documents the real buildable graphs (node I/O, up to 3 reference images for I2V, a source video for edits); MODEL_INDEX reflects it. Recipe count corrected **67 -> 68** (it is a buildable official recipe), and the modality chart was re-rendered. The "replaces Veo entirely" note stands - Veo templates (`api_veo2_i2v`, `api_veo3`) are still shipped, so that launch claim remains overstated.

### Changed
- **Cover banner surfaces breadth, not just recipes.** The chip now reads `149 models · 68 recipes` (was `68 model recipes`), so the header reflects the full official model library the kit routes to, not only the hand-written prompt recipes. The kijai ecosystem (62 packs, `KIJAI.md`) stays documented separately to avoid double-counting models it wraps; private / client-trained models are intentionally not counted in the public number.

## [2.1.0] - 2026-06-30

### Added
- **Gemini Omni Flash (Google) documented.** Google's any-to-any generative video model (text-to-video, image-to-video, conversational video editing, native audio; model card 2026-05-19). Added a MODELS.md recipe entry and a MODEL_INDEX row. Grounded in the DeepMind model card plus a live ComfyUI 0.25.1 `/object_info` check and the Comfy-Org/workflow_templates `index.json`: there is NO official Comfy Google partner node or local template for it, so the entry says so plainly and points to the real routes (Comfy Cloud, or the third-party `Anil-matcha/gemini-omni-comfyui` pack via muapi.ai). The recipe count is unchanged (67), since this is a cloud / third-party model, not a buildable local recipe.

### Changed
- **Corrected the "replaces Veo entirely" launch claim.** Google's own model card lists Veo and Gemini Omni Flash as separate models, and ComfyUI's Veo 2 / Veo 3 partner nodes are live and not deprecated (confirmed via `/object_info`). The kit documents Omni Flash as an addition, not a Veo replacement.

## [2.0.1] - 2026-06-30

### Fixed
- **Claude Code plugin bundle is now truly self-contained.** `tools/build_plugin.py` copied only nine core files, so `/plugin install comfyui@comfyui-agent-kit` shipped without the node library, the node-building guide, and most routed docs, the exact knowledge v2.0.0 added. The builder now mirrors the full installed-skill layout: every doc `SKILL.md` routes to (`BUILDING_NODES.md`, `EXAMPLE_WORKFLOWS.md`, `NODES.md`, `LAYERS.md`, `BOOTSTRAP.md`, `AGENTS.md`, `UPDATING.md`), `workflow_layout.py`, and the whole `NODE_LIBRARY/` directory (incl. `ocio.md`) as a subdir. The bundle went from 9 files to 17 files plus `NODE_LIBRARY/` (21 files).

### Changed
- README tagline split across two lines: the local-first / every-agent line, then "Your GPU, your models, no cloud, no account."
- Positioning line now leads with experts: "for experts and everyday users" (README and the 2.0.0 notes).

## [2.0.0] - 2026-06-30

Mega release. The kit grows from a local-first ComfyUI driver into a driver **plus** a documented node library, a
published pro-color node pack (**ComfyUI-OCIO**), and a field guide to building nodes - local-first, for experts
and everyday users alike.

### Added
- **Node knowledge library (`docs/NODE_LIBRARY/`).** A per-node reference in the spirit of The Foundry's Nuke node docs: for each node, what each input / output is for, how it behaves, strengths, bugs + fixes, anti-patterns, and where it slots in a graph. Live I/O stays sourced from `get_node_info` / `/object_info`; the library holds the durable curated layer on top. Ships the index (`_INDEX.md`), the format + rules (`_SCHEMA.md`), the core text-to-image chain (`core.md`, all I/O confirmed on ComfyUI 0.25.1), and color / transform (`color-and-transform.md`). Routed from `SKILL.md`; grows on encounter (use or meet an undocumented node, add its entry).
- **Log-space transform technique.** Manual (non-AI) pixel geometry (scale, rotate, distort, warp, skew, any resample) should be done in a log-encoded space (Linear->Log, transform, Log->Linear) to preserve highlight / shadow detail, a Nuke / OCIO production practice. We ship the node for it as `OCIOLogConvert` in our new ComfyUI-OCIO pack (ACEScct, HDR-safe, reversible). Documented in `docs/ADVANCED.md`, `docs/NODE_LIBRARY/color-and-transform.md`, and `docs/NODE_LIBRARY/ocio.md`, with the native EXR / linear path via `SaveImageAdvanced`.
- **Node inventory (`docs/NODE_LIBRARY/_INVENTORY.md`) + generator (`tools/node_inventory.py`).** The master catalog of every node type used across the kit's workflow library: 552 distinct types across 448 workflows (official template bundles + our saved workflows), classified against a live ComfyUI (185 core, 194 API / cloud partner, 9 custom-author, 3 missing-but-used, 161 subgraph ids). Regenerable, so a future agent sees the full universe before documenting or building.
- **Custom-author node entries (`docs/NODE_LIBRARY/custom-author.md`).** The two author packs whose nodes appear in our workflows, I/O confirmed via get_node_info: ComfyUI-LTXVideo (HDR decode postprocess, IC-LoRA guide + loader, Gemma API encode). kijai packs stay in `docs/KIJAI.md`.
- **Node library: full category reference (183 entries).** Per-node documentation for every core node used across the kit's workflows, one file per category (loaders, samplers, conditioning x2, image x2, latent, advanced, 3d, video, audio, text, utilities, experimental): purpose, per-input/output semantics, strengths, bugs, anti-patterns, placement. I/O confirmed via get_node_info; built by a subagent-per-category fan-out and validated (0 dashes, no leaked filenames, node-count match). API / cloud-partner nodes (194) are catalogued in `_INVENTORY.md`; per-node entries are the next wave.
- **ComfyUI-OCIO documented in full (`docs/NODE_LIBRARY/ocio.md`), all eight shipped nodes.** Our OpenColorIO pack (Slava Sexton) is documented at buildable depth against the PUBLISHED v1.0.0 source: the two IO nodes **OCIO Read / OCIO Write** (load a still / sequence / video, color-manage, write EXR / TIFF / PNG / JPEG or ProRes / DNxHR / h264 / hevc, with alpha, missing-frame fill, and auto frame range over the wire) plus the six color operators (ColorSpace, LogConvert, Display, CDLTransform, FileTransform, LookTransform), each with correct current INPUT_TYPES / RETURN_TYPES, how to wire, gotchas, and a worked Read -> grade -> ProRes example. Corrects the earlier entry that described an outdated schema. Runtime-verified via the ComfyUI `/prompt` API against OpenColorIO 2.5.2.
- **Workflow auto-layout + code inspector (`shared/comfyui/workflow_layout.py`).** A layered (Sugiyama) layout so a node graph you build never overlaps: `auto_layout(wf)` ranks nodes left-to-right by dependency depth, left-aligns each column, stacks parallel branches vertically with gaps sized to each node's REAL height (including the big preview area of image nodes like PreviewImage / LoadImage, which render ~230px taller than their widgets imply), centers a shared input/output on the middle of the nodes it connects to (barycenter coordinate assignment, no downward drift), and reduces edge crossings; `inspect(wf)` reports overlaps / crossings / bounds from the coordinates alone. Layout is verified in CODE, never from a screenshot. Routed from `SKILL.md` as the pre-save step for any workflow.
- **ComfyUI-OCIO published and credited.** The companion node pack [ComfyUI-OCIO](https://github.com/SlavaSexton/ComfyUI-OCIO) (Slava Sexton; eight Nuke-style OpenColorIO nodes - Read / Write plus the six color operators: ColorSpace, LogConvert, Display, CDLTransform, FileTransform, LookTransform) is now public at v1.0.0. `ATTRIBUTION.md` gains a **Companion pack** section that credits it to **Slava Sexton** wherever this kit uses, recommends, or builds on it - in full or in part, as a derivative or as the design.
- **Node-building field guide (`docs/BUILDING_NODES.md`).** The hard-won lessons from shipping ComfyUI-OCIO, so an agent that writes or modifies a custom node does not re-pay them: the node shape (INPUT_TYPES, widget-order = widgets_values-order), the combo-validation trap (a value outside a combo's list is an HTTP 400, so use STRING + a browse button for arbitrary paths), the JS front end (buttons, `setWSilent` to tell auto from manual, conditional widget visibility, on-node labels via `onDrawForeground`, post-run `onExecuted`, cross-node auto by walking the wire), server routes (upload / browse / detect), the ComfyUI facts that shape a color / sequence node (naive sRGB `0..1`, no timeline, alpha as MASK, the `IS_CHANGED` footgun), the IO libraries + the EXR / ffmpeg env traps, and the verify-on-REAL-files discipline (compile is not "works"; test the entry path the user actually uses). Routed from `SKILL.md` beside the `comfyui-node-*` skills.
- **Positioning: local-first, for experts and everyday users.** README now states the kit scales from one-command generation to a professional VFX color pipeline (the OCIO pack), and routes agents to the OCIO pack for any color / VFX-color task.

## [1.9.0] - 2026-06-29

### Added
- **Claude Code plugin + marketplace.** The kit now installs as a Claude Code plugin:
  `/plugin marketplace add SlavaSexton/ComfyUI-Agent-Kit` then `/plugin install comfyui@comfyui-agent-kit`. The
  plugin (`claude-code/`) bundles the full `comfyui` skill + a `.mcp.json` that launches the local `comfyui-mcp`
  driver via `npx` (no manual npm step, no setup hook needed - the skill self-bootstraps the machine block).
  Additive: the multi-agent installer is unchanged and stays the path for Codex / Gemini CLI / Qwen Code (plugins
  are Claude Code only). `tools/build_plugin.py` assembles the bundled skill from the canonical sources so it never
  drifts. This is the local-first counterpart to the official Comfy Cloud MCP, installable the same way.

### Changed
- **README repositioned** to lead with local-first / your-GPU / multi-agent / cloud-independent, framing the kit
  as the deliberate local counterpart to the official Comfy Cloud MCP (gracious, not a knock).

## [1.8.0] - 2026-06-29

### Added
- **Task-recipe layer (`docs/TASKS.md`).** A shortcut over the operating manual: each common job (generate
  image / video / audio / 3D, upscale, remove background) mapped to its local end-to-end flow (find a template,
  hardware-aware model pick, read the MODELS.md dialect, validate, run small, save). Local-first; complements the
  model-centric MODELS.md and is wired into the SKILL.md routing map.
- **Multi-reference identity-compositing technique (`docs/ADVANCED.md`).** Combining two specific faces into one
  image: two real references + `ImageBatch` + explicit "the first image is X" prompting + the face-accuracy
  ranking (Nano Banana 2 HIGH thinking > Nano Banana Pro > Kling O3 > FLUX Kontext > SDXL).

### Changed
- **SKILL.md validation now checks for an output/save node.** Before running, confirm the graph has an input AND
  an output/save node; API and partner nodes (Kling, Nano Banana, Veo, Gemini, ...) often emit a tensor but include
  no save node by default, so the job runs and produces nothing retrievable.

The task-layer shape, the save-node guard, and the compositing technique are adapted from `Comfy-Org/comfy-skills`
(MIT) for the local stack, credited in README + ATTRIBUTION. No files vendored.

## [1.7.0] - 2026-06-27

### Added
- **Four new models from the official Comfy source sweep** (the pre-release check that the v1.6.x cuts had skipped; run now against the live `Comfy-Org/workflow_templates` + blog):
  - **Boogu Image 0.1** - new open-weight (Apache-2.0, not gated) image recipe: Base / Turbo (few-step distilled) / Edit variants, Qwen3-VL-8B text encoder + FLUX VAE, official Comfy-Org templates, GGUF for low VRAM. Recipe families 66 -> 67.
  - **Seedance 2.0 Mini** - faster, cheaper variant noted in the Seedance entry (same `ByteDance2*Node`, `api_seedance2_0_mini_{t2v,r2v}` templates).
  - **Luma Ray 3.3** - added to the Luma entry via `LumaRay32TextToVideoNode` (+ the extend node, chained by `generation_id`).
  - **Qwen3-VL TextGenerate** - in-graph local VLM (caption / VQA / prompt generation), the no-API counterpart to the Claude prompt nodes.
  Counts refreshed everywhere (67 recipes, 545 templates, 149 models) including the cover and both breakdown charts, recomputed from the official template manifest. The community-fix triage was already current.

## [1.6.1] - 2026-06-27

### Fixed
- **Bernini-R ComfyUI tutorial URL** corrected to `docs.comfy.org/tutorials/video/bytedance/bernini-r`
  (it had pointed at the Anima tutorial). Caught by the post-release completeness re-check.
- **HappyHorse reference-image count** clarified: the official ComfyUI template wires 3 slots
  (image1-3), now noted alongside the API's "up to 9".

## [1.6.0] - 2026-06-27

### Added
- **ComfyUI build paths for entries that were missing them.** Cited the verified ComfyUI graph for
  model/tool entries that named the model + repo but no build path: official Comfy-Org templates
  (ChronoEdit, FireRed, Capybara, Bernini-R, VOID, OmniGen2), community nodes (HuMo, SCAIL-2,
  ChatterBox, Tripo `TripoAPIDraft`, Rodin `mRodin3D_Gen2`, Meshy), and kijai WanVideoWrapper
  (FlashVSR). Every node class was read from the repo's `NODE_CLASS_MAPPINGS`, not invented.
- **Krea 2 community ecosystem + LTX-2.3 3DREAL.** Enriched the Krea 2 entry: fal's ~1503 community style LoRAs
  (`ilkerzgi/fal-Krea-2-Style-LoRAs`, trigger at prompt end, scale 1.0-1.25), the weak-VAE workaround (swap the
  Qwen-Image VAE for the WAN 2.1 VAE or NVIDIA PiD / Pixel Diffusion Decoder, `nv-tlabs/PiD`), and reference image+mask
  control via `ComfyUI-Krea2TextEncoder` (ethanfel, MIT, the `TextEncodeKrea2` node). Added `fal/LTX-2.3-3DREAL-LoRA`
  (trigger `3DREAL`) to the LTX-2.3 IC-LoRA list: a 3D viewport / Blender render to photoreal video LoRA (run via fal
  render-to-real or as an LTX V2V IC-LoRA). All read from the real cards / repos and credited in ATTRIBUTION.
- **LTX-2.3 Water Simulation IC-LoRA.** Documented `Lightricks/LTX-2.3-22b-IC-LoRA-Water-Simulation` (file
  `ltx-2.3-22b-ic-lora-water-simulation-0.9.safetensors`, gated `license:other`, video-to-video, published
  2026-06-25) in the LTX-2.3 IC-LoRA list: adds realistic water / seawater to a clip. No dedicated workflow ships in
  ComfyUI-LTXVideo yet (pack last updated 2026-06-17), so it runs via the generic
  `LTX-2.3_V2V_ICLoRA_Single_Stage_Distilled.json` + `LTXICLoRALoaderModelOnly`. Full recipe read from the (authenticated)
  gated model card: the `ADD WATER` trigger in a dual-panel reference/edited prompt, strength sweet spot 1.2, and the
  critical "distilled stage-1 only at native resolution" recipe (the two-stage upscaler drifts subject identity), plus
  the 6 official gallery example prompts (read from the card's `widget:` frontmatter).

### Fixed
- **Full-kit audit: 206 entries across 15 sections, adversarially verified.** Each error was
  re-checked at the primary source before fixing (additive/corrective, no degradation): removed a
  fabricated "+ ComfyUI nodes" claim (BRIA) and unverified Krea-1 gallery prompts; corrected Grok
  (five-part to six-part), Seedance (`_real_human` only on r2v/flf2v), ElevenLabs (`duration`
  0.5-30s), SeedVR2 (4n+1 adds 17), the four Krea-2 LoRA trigger capitalizations, and Meshy
  (negatives ARE supported); fixed three licenses against the GitHub API (Marigold GPL-3.0, StableX
  no-LICENSE, Veevee GPL-3.0); Wan2.1-VACE `--model_name` (not `--task`); the LBM weight filename;
  the DDColor maintained fork; the LivePortrait repo move; and several stale source URLs. Four of
  the fixes were errors in this release's own new build paths (Bernini-R URL, HuMo modes, SCAIL-2
  masks, FlashVSR GPU list). The audit also flagged 17 `node template X.md` refs as phantom; they
  were left untouched, being valid pointers to the external `alexmunteanu/comfyui-anthropic-claude`
  templates (a false positive, verified present at source).
- **HF model-card corrections (token-authenticated).** Re-read the full gated cards (frontmatter
  `widget:` prompts + body) and fixed the entries that had drifted from them.

## [1.5.0] - 2026-06-25

### Added
- **kijai ecosystem mega-brain (`docs/KIJAI.md`).** Deep-researched all 62 of kijai's ComfyUI repos (read live from
  github.com/kijai on 2026-06-24, dated) into a structured reference: a "pick a tool by task" table, a supersede map
  (old to better, e.g. HunyuanVideoWrapper to native HunyuanVideo, SUPIR to core SUPIR, CogVideoXWrapper to
  WanVideoWrapper), per-tool node I/O + usage + compat for the 28 active tools, legacy one-liners, and a "what to
  disable now" list. Built by a 62-agent deep-research workflow; every node list read from the real repo code.
- **SKILL.md routing map ("Files in this kit").** SKILL.md now lists every supporting doc with a "when to read it"
  trigger, so MODEL_INDEX / ADVANCED / KNOWN_ISSUES / KIJAI / LTX2_TRAINING / EXAMPLE_WORKFLOWS are pulled on demand
  instead of sitting unread (four were previously orphaned with no pointer in SKILL.md).
- **Crop-and-stitch inpainting technique + HallettVisual Smart Image Crop and Stitch.** New ADVANCED.md section on
  detailed inpainting of a high-res image: crop the masked region, size it to the model's native resolution, generate,
  stitch back. Documents the established `comfyui-inpaint-cropandstitch` and the auto-sizing alternative
  `SmartImageCrop` / `SmartImageStitcher` (HallettVisual, Apache-2.0, ships a Flux Klein workflow), flagged as new.
  Credited in ATTRIBUTION + README. Verified against the repo and its shipped workflow.

### Changed
- **HappyHorse recipe upgraded 1.0 -> 1.1 (synchronized audio).** Native in-pass audio (dialogue / SFX / music),
  up to 9 reference images with no cross-contamination, long-context prompts (2,500+ chars, 6-8 scenes), full
  cinematic language, and the shipped ComfyUI nodes (`HappyHorseTextToVideoApi` / `ImageToVideoApi` /
  `ReferenceVideoApi`) plus the official `api_happyhorse1_1_{t2v,i2v,r2v}` templates. Verified against the
  templates and blog.comfy.org/p/happyhorse-11-is-now-available-in.
- **Seedance 2.0 now does 4K.** Added 4K to the Seedance recipe (smoother gradients, richer tones, detail that
  holds through motion and into post) plus the shipped official ComfyUI templates and modes: T2V, R2V, and
  first/last-frame (FLF2V), each with a `_real_human` variant. Verified against the `api_seedance2_0_*` templates.

## [1.4.0] - 2026-06-24

### Added
- **Flux.2 Klein identity-transfer suite (community field recipe).** Documented `capitan01R/ComfyUI-Flux2Klein-Enhancer`
  in the FLUX.2 entry: training-free multi-reference identity-preserving editing for FLUX.2 Klein 9B via the Identity
  Feature Transfer Final node (attention-output patch, up to 8 reference latents + per-subject masks, HARD/MID/SOFT_LOCK
  presets), plus Color Anchor, Sectioned Encoder, and reference controllers. Credited capitan01R in README and
  ATTRIBUTION and flagged the PolyForm Noncommercial 1.0.0 license.
- **Workflow layout discipline in the skill.** Expanded SKILL.md with a "Lay the graph out cleanly" section:
  columns by stage, a per-column y-cursor for zero node overlap, one Group box per stage, Reroute for long wires,
  and a tidy pass, so assembled graphs read as a structured pipeline instead of a pile of overlapping nodes.
- **Subgraphs guidance in the skill.** Added a "Collapse a stage into one reusable node (Subgraphs)" section to
  SKILL.md: collapse a selection into one super-node, expose only the needed widgets, publish it as a reusable
  Subgraph Blueprint (the kit's `blueprints/` bricks), nest and unpack. Notes that Subgraphs (official 2025-08)
  supersede the legacy Group Nodes. Verified against docs.comfy.org/interface/features/subgraph.
- **Creator-level reference: `docs/ADVANCED.md`.** A new deep reference distilled from primary sources (multi-agent
  research, each tool verified against its real page): ComfyUI's genuine strengths; the real limits and gotchas with
  workarounds (Dynamic VRAM regressions, VAE black/NaN + color shift, the IS_CHANGED footgun, canvas lag, custom-node
  malware/version-hell); temporal stability / anti-flicker for sequences (native video models + VACE + context windows
  + FreeNoise, structure-lock ControlNet, deflicker/interpolation as finishers); the honest state of PBR/material-pass
  generation from footage (not solved temporally in 2026; the realistic per-frame + optical-flow path, with license
  flags); and max-detail/precision + sequence-native EXR I/O. SKILL.md now points to it and carries the top gotchas.
- **High-detail matting recipe in `docs/ADVANCED.md`.** Multi-stage hair/fur/semi-transparent/motion-blur matting:
  coarse select (SAM3/BiRefNet) -> trimap -> alpha matte (ViTMatte / SDMatte / Matte-Anything) -> edge refine
  (LayerStyle), and video temporal matting (MatAnyone2 + a SAM2/SAM3/SeC keyframe, or RVM for clean humans). Notes
  that the official template library ships image BiRefNet bg-removal + SAM3 segmentation but NO free local temporal
  video matte (the video-matte templates are paid Bria API), and flags licenses (RMBG-2.0 CC-BY-NC, MatAnyone NTU
  research-only, RVM GPL). Each model verified against its real page.
- **Living bug log `docs/KNOWN_ISSUES.md` + weekly bug tracking.** A sourced table of ComfyUI's open bugs (with
  workarounds), security notes, and a "Recently fixed" section, so the kit knows what is broken before building a
  workflow. The `comfyui-weekly-update` task now also reads ComfyUI + frontend release notes and the issue tracker
  each week and updates this log (moves fixed items, adds new bugs, bumps the date). SKILL.md and ADVANCED.md point
  to it.
- **Node I/O cheat-sheet in SKILL.md.** The common nodes' exact input/output types (CheckpointLoader, LoraLoader,
  CLIPTextEncode, KSampler, VAEDecode/Encode, ControlNet apply, etc.) so graphs are wired with valid connections
  (no feeding text into a LoRA input or a MODEL into a text box); anything unfamiliar is still read from `/object_info`.
- **Counted the official Subgraph Blueprints (94).** README and MODEL_INDEX now note the library also ships 94
  official Subgraph Blueprints (reusable subgraph bricks) alongside the 534 templates.
- **LTX-2 LoRA training guide `docs/LTX2_TRAINING.md`.** Documents the official Lightricks trainer + their
  `train-model` skill for training a custom LTX-2 LoRA (modes, LoRA-rank guidance, the plan-gated flow, and the
  Linux + >= 32 GB VRAM requirement), credits Lightricks, and tells the kit to offer training when a user works with
  LTX-2 and wants something a LoRA captures. The trained LoRA loads back into ComfyUI here.

### Changed
- **GitHub language stats now reflect the Python tooling.** Marked the per-OS install scripts
  (`*.ps1` Windows, `*.sh` Unix) as `linguist-vendored` so the repo's language bar shows the Python
  tooling, not whichever installer set was larger by bytes. No code change: the kit is a Markdown
  skill with Python tooling.

## [1.3.1] - 2026-06-23

### Changed
- **Krea 2 recipe: added a worked example.** Folded a representative prompt from the official `krea-ai/krea-2`
  prompt guide (`docs/prompting.md`) into the recipe so the "long, detailed, natural language" structure is concrete,
  and cited that doc as a source.

### Fixed
- **Stale coverage-table descriptions.** The README coverage table labeled the Krea row "Krea 1" where the
  shipped recipe is Krea 2; corrected to "Krea 2 / FLUX.1 Krea Dev". Refreshed the stale "Updated:" date in the
  README and MODEL_INDEX to 2026-06-23.

## [1.3.0] - 2026-06-23

### Added
- **Krea 2 (open weights) recipe.** Added a Krea 2 entry: RAW (52 steps, CFG 3.5, for LoRA training) and Turbo
  (8 steps, CFG 0, up to 2K, for inference), built on a Qwen3-VL-4B text encoder + the Qwen-Image VAE. Day-0 native
  ComfyUI via the official `image_krea2_turbo_t2i` template (Comfy-Org repackaged weights + four style LoRAs).
  Recipe families 65 -> 66. Noted the Krea 2 Community License (commercial use needs an Enterprise License). Sources:
  krea-ai/krea-2, Comfy-Org/Krea-2.
- **Reference source: Comfy-Org Creative Campus.** Pointed the SKILL.md shared-workflows section at
  `Comfy-Org/creative-campus`, the official Comfy Education Initiative case-study workflows from award-winning
  artists (e.g. Xindi Zhang's Student Academy Award film) to open and study. Link-and-study only (no license file).

### Changed
- **Coverage charts refreshed to a uniform 2560x1440.** The four `docs/assets` images now share one resolution
  (matching the cover) so the README rows stay aligned. `models_by_modality` updated to 66 with the corrected
  modality and local/API split.
- **Repo renamed to `ComfyUI-Agent-Kit` (capitals).** Capitalized the README title, clone URLs, the installer banners, the changelog header, and the
  directory-tree label so they match the renamed repo; the old lowercase URL still redirects. The cover image
  chip now reads "66 model recipes" (was 65).

### Fixed
- **Utility-tool count 17 -> 18.** The Z-Image Fun-ControlNet-Tile super-res model was added to the enhancement
  section, but the totals in the README and MODEL_INDEX still read 17. Corrected to 18 across the README, MODEL_INDEX, and the coverage chart.

## [1.2.0] - 2026-06-22

### Added
- **Credits for the v1.1.0 sources.** Named Prompt Relay (Gordon Chen, Ziqi Huang, Ziwei Liu), kijai's
  ComfyUI-PromptRelay and ComfyUI-SUPIR, WhatDreamsCost LTX Director 2.0, alibaba-pai Z-Image ControlNet,
  Lightricks LTX-2.3 / HDR, and Real-ESRGAN in the README "Credits and thanks", plus a new ATTRIBUTION.md
  "Optional components" table with licenses. Flagged that SUPIR's weights are non-commercial.
- **Field techniques in wide community use (LTX-2.3 + Flux.2).** Added attribution-verified findings: LTX-2.3
  external-audio sync, GGUF loading to fit the 22B on a 24GB card, CacheDiT speed, NAG quality, chunked feed-forward +
  multi-guide (KJNodes), the GAP LTX 2.3 Motion pack (lipsync / storyboard, with the storyboard-audio caveat), and
  Flux.2 Klein masked-inpaint + multi-angle recipes. Credited KJNodes/kijai, Jasonzzt (CacheDiT), MelBandRoFormer,
  Fannovel16 (Frame-Interpolation), and GeekatplayStudio. Attribution taken from the workflows' own embedded node-pack
  ids, not guessed.

## [1.1.0] - 2026-06-22

### Added
- **Multi-shot / timeline video direction (Prompt Relay + LTX Director 2.0).** Documented the Prompt Relay method
  (arXiv 2604.10030; training-free, inference-time temporal prompt routing via a cross-attention penalty), its
  ComfyUI port `kijai/ComfyUI-PromptRelay` (Smart segment syntax, ready LTX-2.3 + Wan 2.2 graphs), and
  `WhatDreamsCost` LTX Director 2.0 (timeline-editor node for LTX 2.3, GPL-3.0) in the LTX-2.3 entry, plus a Prompt
  Relay note in the Wan 2.1/2.2 entry. Caveats noted: needs current ComfyUI-LTXVideo + KJNodes, a cross-attention
  monkeypatch, and the kijai port ships no license file.
- **Z-Image-Turbo ControlNet + upscale options.** Documented the alibaba-pai Fun-Controlnet-Union (Canny / Depth /
  Pose / HED / MLSD, + Scribble/Gray builds, `control_context_scale` 0.65-1.00, 8-step distilled) in the
  Z-Image-Turbo entry, plus two upscale paths: the hires-fix "controlnet-locked upscale" and the companion
  Fun-ControlNet-Tile super-res model (also added to the upscaler list). Verified against the official HF model card.
- **LTX-2.3 HDR IC-LoRA (SDR -> HDR video).** Documented `Lightricks/LTX-2.3-22b-IC-LoRA-HDR` in the LTX-2.3 entry:
  gated `license:other` weights, the ready `LTX-2.3_ICLoRA_HDR_Distilled.json` workflow in the ComfyUI-LTXVideo pack,
  the arXiv 2604.11788 method, the `LTXICLoRALoaderModelOnly` requirement, and the HDR-format-out caveat.

### Fixed
- **Corrected the controlnet-locked upscale claim.** Live testing showed the Union-ControlNet img2img refine holds
  STRUCTURE but Z-Image regenerates a real subject's IDENTITY at denoise 0.4+ (the earlier "denoise ~0.7 without
  drift" wording was misleading). Reworded to keep denoise ~0.2 for fidelity, or use the Tile model / a GAN / a
  face-ID adapter for an identity-locked face upscale; also flagged the full control model's high-res VRAM/OOM cost.

## [1.0.0] - 2026-06-21

The auto-start and session-protocol release: the agent can now run ComfyUI itself, and never loses your work.

### Added
- **Auto-start the ComfyUI server.** When `:8188` is down, the agent launches the headless server in the
  background and generates, no GUI required. The per-machine launch command is captured in the skill's machine
  block; the owner views a running server via `http://127.0.0.1:8188` in a browser.
- **Session protocol.** Ask the owner how to start ComfyUI (open it themselves vs agent starts headless), with a
  remembered preference; ALWAYS save every built or run workflow to `<ComfyUI>/user/default/workflows/` so it
  persists and the owner can open it later from the Workflows sidebar; hand over name, outputs, and how to view.
- **Configurable start policy for projects and pipelines.** Resolution order: env vars (`COMFY_HOST` /
  `COMFYUI_START_POLICY` / `COMFYUI_LAUNCH_CMD`) > project `.comfyui-agent.json` > skill machine block > ask.
  Ships `.comfyui-agent.example.json`.

### Fixed
- **Headless launch crash.** A custom node logs an emoji; under a non-UTF-8 console codepage (Windows cp1251) the
  server died on startup with a `UnicodeEncodeError`. Set `PYTHONUTF8=1` on the launch. Verified live.

### Changed
- README "What it can do" now lists auto-start and workflow persistence. Reconciled the "do not MCP-restart
  Desktop" gotcha with the new self-start capability (start the server yourself; the Desktop shortcut would start
  a conflicting second server on `:8188`).

## [0.3.0] - 2026-06-20

### Added
- **Workflow composition.** Assemble a new graph from templates and blueprint subgraphs, and wire the nodes
  correctly (output-to-input by type, with converters), validated against `/object_info`.
- **Shared-workflow fetch + model shootout.** `fetch_workflow.py` pulls any ComfyHub workflow by hash; the
  image-edit comparison grid runs a prompt through many models to pick the best. `docs/EXAMPLE_WORKFLOWS.md`.
- **MotionDeblur (restoration) IC-LoRA** and the **OpenRouter in-graph LLM node** (any model via one key).
- **Self-update mechanism.** `check_updates.py` diffs the template repo and reads the ComfyUI blog RSS; an
  optional weekly scheduled task adds recipes for new models. `docs/UPDATING.md`.
- Upscaler-choice and restore-chain ordering guidance (GAN vs diffusion; denoise before upscale).

### Changed
- README capabilities overview added; tagline byline on its own line; coverage tables merged and aligned.
- Stripped all em-dashes repo-wide (house writing canon: 0 long dashes).

## [0.2.0] - 2026-06-19

### Changed
- **Restructured into a multi-agent kit and renamed `comfyui-claude-kit` to `comfyui-agent-kit`** (the old URL
  redirects). One shared core (`shared/`) plus a thin adapter per agent (`agents/{claude,codex,gemini,qwen}`);
  GLM is covered through Claude Code. Per-agent matrix in `docs/AGENTS.md`.

## [0.1.0] - 2026-06-19

### Added
- Initial kit: the `comfyui` skill + stdlib `comfy_client.py`, the `comfyui-mcp` driver, the sparse-cloned 500+
  workflow-template library + quick index, the in-graph Claude nodes, and the node-building skills.
- **Per-model "mega-brain" (`MODELS.md`):** prompt recipes from official sources (grew to 65 models across
  image / video / audio / 3D) plus 17 enhancement and utility tools, auto-pulled when a model is named.
- **Full model index (`docs/MODEL_INDEX.md`):** all 147 library models classified (recipe / utility / template-only).
- **Hardware-aware model selection:** detect VRAM, RAM, and free disk, recommend the variant that fits, refuse a
  download that will not.
- House-style cover, real-data coverage charts, gracious credits, MIT, and full attribution.
