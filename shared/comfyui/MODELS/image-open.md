# Image models (open / local-runnable)

Part of the kit's per-model prompting reference. The routing table and the auto-pull rule live in
[`MODELS.md`](../MODELS.md); this file holds the 12 entries for this family.


### FLUX.1 (Black Forest Labs)
- **Prompt style:** natural-language sentences, not comma tags. Word order matters (earlier tokens weighted more).
- **Structure:** Subject -> Action/Pose -> Style/Medium -> Context/Environment -> Technical details; most important first. Rendered text in quotes (keep under ~25 chars); hex codes tied to specific objects work.
- **Strengths:** native text rendering, photorealism via real camera/lens/film language, hex color control, multilingual.
- **Avoid:** negative prompts NOT supported on any FLUX.1 version (may add the unwanted element); no named fonts (describe the style).
- **Settings:** Schnell 1-4 steps / guidance ~3.0 / ~1MP; Dev 20-50 steps / guidance 1.5-5.0 / ~2MP; Pro/Ultra API. ComfyUI: FluxGuidance node, euler/simple typical.
- **Source:** docs.bfl.ml ; node template `flux.md`.

### FLUX.2 (Black Forest Labs)
- **Prompt style:** natural language OR JSON structured (natural for iteration, JSON for precise production control).
- **Structure:** main subject -> key action -> critical style -> essential context -> secondary details.
- **Strengths:** photorealism, text rendering, hex color, product shots, native multilingual; multi-reference compositing (pro up to 8, flex ~10, dev ~6) with identity/style/pose typing.
- **Avoid:** negative prompts NOT supported.
- **Settings:** API for pro/max/flex; FLUX.2 [dev] open-weight runs locally (guidance/steps per the dev workflow).
- **Field recipes (community):** **Klein masked inpaint + dual reference** (Flux.2 [Klein]): `InpaintStitchImproved`
  (comfyui-inpaint-cropandstitch) + a mask + two reference images, one prompt-driven and one ref+mask driven, for
  controlled edits. **1-click multi-angle character turnarounds:** a prompt-batcher fans one character into several camera
  angles for consistency. **Multi-reference identity lock, training-free** (Flux.2 [Klein] 9B): the
  `ComfyUI-Flux2Klein-Enhancer` suite (capitan01R, ~510 stars as of 2026-06) does identity-preserving multi-subject
  edits with NO LoRA training. Core node **Identity Feature Transfer Final** patches Klein attention output
  (`set_model_attn1_output_patch`) to transfer features from up to 8 VAE-encoded reference latents (fed via **Multi
  ReferenceLatent**), with per-reference masks (`subject_mask_1..8`), similarity matching, and confidence-gated
  transfer across Klein's 8 double + 24 single blocks, presets HARD/MID/SOFT_LOCK. Companions: **Color Anchor**
  (post-CFG channel-mean color match), **Sectioned Encoder + Detail Controller** (FRONT/MID/END prompt-section
  weights), **Ref / Mask Ref Controllers**, and an experimental resolution-aware Euler sampler. No extra Python deps.
  **License: PolyForm Noncommercial 1.0.0 (personal/research free; commercial use needs a separate license).**
  Community workflows, not official BFL recipes.
- **Community fine-tune - Flux2-Klein-9B-True-V3 (wikeeyang):** an aesthetics / composition fine-tune of
  `black-forest-labs/FLUX.2-klein-9B` (base_model_relation: finetune; card labeled `apache-2.0`, en/zh,
  text-to-image). V3 markedly improves aesthetics and composition over V1/V2 per the card's comparison grids. It
  does text-to-image, prompt-only **instruct editing** (edit an input image from a plain instruction, no
  ControlNet), and with a companion LoRA **face-swap / try-on / try-off** (`bfs_head_v1` at ~0.75) plus **Mask +
  LoRA** regional editing. Prompt it like Flux.2 [Klein]. Ships a wide quant ladder so it fits most cards: `bf16`
  (full), `fp8mixed`, **`int8mixedrow`** (loads with ComfyUI's OFFICIAL / native INT8 loader), **`INT8-ConvRot`**
  (loads NATIVELY as of ComfyUI v0.27.0's int8-convrot support - the Milor123 quant pre-dated that via the now-superseded `ComfyUI-INT8-Fast`; see ADVANCED.md "INT8 acceleration"), `mxfp8`, `nvfp4`, and GGUF
  `Q4_K/Q5_K/Q6_K/Q8_0`; the card claims INT8 is ~2x faster than fp8 at low quality loss (see ADVANCED.md "INT8
  acceleration"). LICENSE CAVEAT (inferred): the card is tagged Apache-2.0, but the weights derive from FLUX.2
  [Klein] - confirm the base Klein license before commercial use rather than trusting the fine-tune's tag alone.
  Mirrors on HF + Modelscope. Source: huggingface.co/wikeeyang/Flux2-Klein-9B-True-V3.
- **360 / VR equirectangular panorama IMAGE (Flux.2 Klein, via panorama-stickers):** turn Flux.2 Klein into a
  360 equirectangular (ERP) panorama generator. The model-agnostic **`nomadoor/ComfyUI-Panorama-Stickers`** pack
  (MIT, Comfy Registry v1.3.0; its four ERP nodes - Stickers / Cutout / Preview / Seam Prep - are broken down in
  `NODE_LIBRARY/custom-author.md`) provides the ERP canvas, cutout, seam-prep and interactive preview. Grow a
  normal image into a seamless 360 sphere with nomadoor's own outpaint LoRAs:
  **`nomadoor/flux-2-klein-4B-360-erp-outpaint-lora`** (`apache-2.0`, base Klein 4B) or **`...-9B-...`**
  (`license: other`, base Klein 9B); ready graphs `flux-2-klein-{4B,9B}-360-erp-outpaint.json` ship in the repo.
  The SAME pack (v1.3.0+ video support) previews the separate LTX-2.3 360 VIDEO route. NOTE - two different
  "Flux.2 Klein" things:
  nomadoor's 360-outpaint LoRA (this entry) is UNRELATED to wikeeyang's Flux2-Klein-9B-True-V3 general fine-tune
  above. Source: github.com/nomadoor/ComfyUI-Panorama-Stickers ; comfyui.nomadoor.net/en/notes/panorama-stickers ;
  huggingface.co/nomadoor/flux-2-klein-9B-360-erp-outpaint-lora.
- **Source:** docs.bfl.ml/guides/prompting_guide_flux2 ; github.com/black-forest-labs/skills ; github.com/capitan01R/ComfyUI-Flux2Klein-Enhancer (Klein enhancer suite, PolyForm NC).

### FLUX.1 Kontext (image edit)
- **Prompt style:** natural-language instructions (tell it what to change, like instructing a person).
- **Structure:** "Change/Replace/Add/Remove [target] to/with [description]"; add preservation language ("keeping the pose unchanged"); one focused edit per instruction; text edits in quotes.
- **Strengths:** outfit/background swaps, object add/remove, text editing (Max = best typography), character identity + style transfer.
- **Avoid:** "don't" instructions (rephrase positively); stacking many complex edits; re-describing the whole image.
- **Settings:** Dev open-weight (local); Pro/Max API.
- **Source:** docs.bfl.ml ; node template `flux_edit.md`.

### Z-Image-Turbo (Tongyi / Alibaba)
- **Prompt style:** natural-language descriptive, subject-first; no special token syntax. Optional LLM prompt-enhancement template in the repo.
- **Strengths:** photorealism, accurate bilingual (EN/CN) text, strong instruction adherence, sub-second on 16GB VRAM.
- **Avoid:** negative prompts not used (CFG-distilled); high CFG (4+) degrades results.
- **Settings:** 9 steps (8 DiT forwards) per the official card; CFG 0.0 per the official card (community ComfyUI guides ~1.5-2.0 if any); torch_dtype bfloat16 (official); 1024x1024 best (2K direct can distort, upscale + second pass at ~0.3 denoise); community sampler euler_ancestral or dpmpp_sde, scheduler sgm_uniform.
- **Source:** huggingface.co/Tongyi-MAI/Z-Image-Turbo ; docs.comfy.org/tutorials/image/z-image/z-image-turbo.
- **ControlNet (Fun-Controlnet-Union, alibaba-pai, Apache-2.0):** union ControlNet for Z-Image-Turbo; modes Canny / Depth / Pose / HED / MLSD (+ Scribble in the 2601 build, + Gray in 2602), plus an inpaint mode. Use the distilled `2.1-2602-8steps` variant at 8 steps (the non-distilled 2.0/2.1 lose Turbo's acceleration and then need more steps + cfg). Main knob `control_context_scale` 0.65-1.00 (higher = stronger control and better detail preservation); a detailed prompt helps stability. ComfyUI wiring: load the weights with `ModelPatchLoader`, apply with a DiffSynth ControlNet node (`QwenImageDiffsynthControlnet` in the reference graph; confirm the exact node/pack against `/object_info`). Source: huggingface.co/alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union-2.1 ; github.com/aigc-apps/VideoX-Fun.
- **Upscale (two options, pick by need):** (1) hires-fix / controlnet-locked: resize up (lanczos 2x) then a Z-Image-Turbo img2img refine with the Union ControlNet locking composition. VERIFIED by testing: the ControlNet holds STRUCTURE (pose, framing, edges) but Z-Image still regenerates content, so at denoise ~0.4-0.7 a real person's face drifts to a similar-but-different identity (structure preserved, identity NOT). Keep denoise ~0.2 to stay faithful (little detail gain), or treat this mode as stylize/enhance, not identity-faithful SR. (2) real super-resolution: the companion `Z-Image-Turbo-Fun-Controlnet-Tile-2.1-2601-8steps` Tile model, trained to 2048x2048 for SR, 8 steps, tiled so structure holds WITHOUT reinterpreting; this is the faithful path. For an identity-locked face upscale, prefer a GAN (Real-ESRGAN) or the Tile model, optionally with a face-ID adapter (PuLID/InstantID). Cost / gotchas: needs the controlnet checkpoint(s) + custom nodes (DiffSynth ControlNet apply node, KJNodes `ImageResizeKJv2`, rgthree Power Lora Loader; core `Canny` or controlnet_aux for the control image); a single high-res pass with the FULL 6.7GB control model is VRAM-heavy and offloads (a ~2.7K refine OOM-crashed a running server on a 24GB card), so cap the target resolution or use the lite control model.

### Qwen-Image (Alibaba)
- **Prompt style:** structured natural language, not tag dumps.
- **Structure:** Subject -> Style -> Details -> Composition -> Lighting; choose ONE primary style; add framing or it defaults centered; exact text in quotes with font/position.
- **Strengths:** commercial-grade text in 26+ languages, posters/infographics/layouts, human realism (2512), natural textures.
- **Avoid:** negatives accepted but inconsistent; long text passages degrade; contradictory styles confuse it.
- **Settings:** base ~20+ steps, sampler euler or res_multistep, CFG 5-7 (text/production), 25-45 steps text-heavy; distilled 15 steps CFG 1.0; 8-step Lightning-LoRA at 8 steps; max prompt ~800 chars.
- **Source:** docs.comfy.org/tutorials/image/qwen/qwen-image ; node template `qwen_image.md`.

### Qwen-Image-Edit (Alibaba)
- **Prompt style:** surgical natural-language instructions, describe only the change.
- **Structure:** "Add/Remove/Change [element + color/size/orientation] [position]"; text edits in English double quotes; reference inputs by number ("Image 1", up to 3 in 2509+); keep 50-200 chars.
- **Strengths:** add/remove/replace, background swap, style transfer, bilingual text editing, portrait/pose edits, multi-image fusion, old-photo restoration.
- **Avoid:** negative prompts NOT supported (use a single space if a field is required); no mask inpainting/outpainting.
- **Settings:** true_cfg_scale 4.0 (4-5), num_inference_steps 50 (20-30 previews), guidance_scale 1.0; node TextEncodeQwenImageEdit + official edit workflow.
- **SDR -> HDR (single image): LumiPic** (`oumoumad/LumiPic`, MIT) - a LoRA that turns any SDR image into a
  scene-linear HDR EXR, the IMAGE analog of the LTX-2.3 HDR IC-LoRA (SAME LumiVid paper, arXiv 2604.11788; see the
  LTX-2.3 HDR entry): the DiT is trained to output an ARRI-LogC-encoded `[0,1]` frame through a frozen VAE, which
  is then inverse-LogC'd to linear HDR (values well past 1.0). Base-model-agnostic; three bases -
  **Qwen-Image-Edit-2511** (mature, production default, 563 MB LoRA, ~54 GB base; default `v5b_step2000`,
  natural-photo alt `v9_step1500`), **FLUX.2 [Klein] 4B** (alpha, 88 MB, apache-2.0 base, fastest;
  `klein4b_alpha_step1750`) and **9B** (alpha, 158 MB, gated base; `klein9b_alpha_step2000`, sweet spot
  `step1250`). Two curves: **LogC3** (stable, linear ceiling ~55, ~8.3 stops) and **LogC4** (V10 alpha, ceiling
  ~470, ~3 extra highlight stops - the `*_logc4_*` files). ComfyUI: ready graphs on the HF repo
  (`SDR_To_HDR_{QE11,klein4b,klein9b,logc4_klein9b}.json`), drop the LoRA in `models/loras/{qwen,flux-2}/hdr/`,
  install **`ComfyUI_Gear`** >= v0.2.0 (its LogC3 / LogC4 Decode + Save EXR node writes the EXR - see
  `NODE_LIBRARY/custom-author.md`), prompt "Convert this image to HDR". MATCH the decode node to the LoRA curve
  (`_logc4_*` -> LogC4 node, everything else -> LogC3) or the absolute luminance is silently wrong. HONEST CAVEAT
  (from the card): V10 LogC4 is alpha - the Qwen V10 gain shows in diffusers but NOT yet in ComfyUI (looks weaker
  than V9); `klein4b_v10_logc4_step1500` is the LogC4 checkpoint that holds up in ComfyUI. For an ACEScg pipeline,
  decode LogC3 with our OCIO `OCIOLogConvert(logc3)` then `OCIOColorSpace(Rec.709 -> ACEScg)` (Gear keeps the
  source primaries; ADVANCED.md has the tie-in). Source: huggingface.co/oumoumad/LumiPic ;
  github.com/oumad/LumiPic ; github.com/oumad/ComfyUI_Gear.
- **Source:** docs.comfy.org/tutorials/image/qwen/qwen-image-edit ; node template `qwen_edit.md`.

### SDXL (Stability)
- **Prompt style:** natural language preferred (dual encoder), short comma tags work as hybrid.
- **Structure:** subject + descriptors + style + quality/medium + lighting.
- **Strengths:** 1024-native coherence, better hands/anatomy than SD1.5, huge LoRA/ControlNet ecosystem.
- **Avoid:** negatives supported and effectively required (no built-in quality filter); never generate at 512x512.
- **Settings:** 1024x1024 (or 832x1216, etc.); ~25-40 steps; CFG ~5-8 (~7); sampler DPM++ 2M / Euler a + Karras; optional base->refiner split at the official 80/20 ratio (`high_noise_frac=0.8`: `denoising_end=0.8` on base, `denoising_start=0.8` on refiner, n_steps=40, per the card example). (Step/CFG are community-standard ComfyUI defaults, not a fixed official spec.)
- **Source:** huggingface.co/stabilityai/stable-diffusion-xl-base-1.0.

### Stable Diffusion 1.5
- **Prompt style:** comma-separated tags / keyword-driven; `(token:1.2)` weighting works.
- **Structure:** subject tags -> descriptor tags -> style/quality tags.
- **Strengths:** speed, low VRAM, massive community models/LoRAs/embeddings.
- **Avoid:** negatives supported and heavily used ("blurry, lowres, bad anatomy, watermark"); don't generate far above 512 natively (use hi-res fix); weak hands/text.
- **Settings:** 512x512 native, guidance ~7 (community default; the official card prescribes NO single CFG, it only evaluates a 1.5-8.0 range), 50 PNDM/PLMS steps (community ~20-30 steps, CFG 7); samplers Euler a / DPM++ 2M Karras.
- **Source:** huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5 (unofficial mirror, not RunwayML-affiliated); canonical weights now live at huggingface.co/sd-legacy/stable-diffusion-v1-5.

### Stable Diffusion 3.5 Large (Stability)
- **Prompt style:** natural-language sentences (trained on natural language; handles them far better than SD1.5/SDXL).
- **Structure:** Style, Subject + Action, Composition/Framing, Lighting/Color, Technical, Text integration, Negative; ~1MP, dimensions divisible by 64.
- **Avoid:** keyword weighting and bracket/emphasis syntax do NOT work, write plain natural language.
- **Settings:** steps 28 (official example; community up to ~40), guidance 3.5-4.5 (4.5 complex); max_sequence_length 512 for the long / quantized-prompt path; SD3-family nodes; ~1MP divisible by 64.
- **Download:** GATED on HF, accept the license + use a token to download (Stability AI Community License form at huggingface.co/stabilityai/stable-diffusion-3.5-large before the weights are accessible). License: free for orgs / individuals under $1M annual revenue, enterprise license required above that.
- **Source:** huggingface.co/stabilityai/stable-diffusion-3.5-large.

### HiDream-I1
- **Prompt style:** natural-language (multi-encoder incl. an LLM text encoder); no prescribed tag format.
- **Strengths:** state-of-the-art prompt adherence and quality (DPG-Bench 85.89, GenEval 0.83), good text rendering.
- **Avoid:** negative-prompt support not documented; Full (CFG-guided) can use them, Dev/Fast run at guidance 0.0 so negatives are inert.
- **Settings:** Full 50 steps guidance 5.0; Dev 28 steps guidance 0.0; Fast 16 steps guidance 0.0; ComfyUI HiDream sampler nodes.
- **Setup:** requires Flash Attention installed (a hard dependency, not optional) + CUDA 12.4 recommended; inference auto-downloads `meta-llama/Meta-Llama-3.1-8B-Instruct` as the LLM text encoder, which needs a separate HF token with Meta Llama access approved at huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct. License: MIT for the transformer weights; the Llama 3.1 Community License governs the text-encoder component.
- **Source:** github.com/HiDream-ai/HiDream-I1 ; huggingface.co/HiDream-ai/HiDream-I1-Full.

### Boogu Image 0.1
- **Prompt style:** natural-language descriptive (Qwen3-VL-8B text encoder); a built-in prompt rewriter (instruction reasoner, Qwen3-VL-32B-Instruct) expands terse inputs, so plain prompts work but detail steers better.
- **Structure:** subject + scene + style + lighting + composition in complete sentences; the VLM encoder favors natural language over tags.
- **Strengths:** open-weight Apache-2.0 (commercial-OK, not gated); three variants - Base (quality), Turbo (few-step distilled, competitive with Z-Image-Turbo), Edit (instruction image edit at 1K/1.5K/2K); rides the Qwen3-VL stack + FLUX VAE.
- **Avoid:** no tag-weighting / bracket syntax (natural language only); negative-prompt support not documented.
- **Settings:** Base ~50 steps, text_guidance 4.0; Turbo is few-step distilled (ships a turbo LoRA `boogu_image_turbo_lora_rank_128`); Edit at 1K / 1.5K / 2K.
- **ComfyUI build:** official templates `image_boogu_image_0_1_turbo_t2i.json` (t2i) and `image_boogu_image_0_1_edit.json` (edit). Comfy-Org repack `huggingface.co/Comfy-Org/Boogu-Image`: `diffusion_models/boogu_image_{base,turbo,edit}_fp8_scaled` (bf16 / nvfp4 also) + `text_encoders/qwen3vl_8b_fp8_scaled` + `vae/flux1_vae` (the FLUX ae). GGUF for low VRAM: `realrebelai/Boogu-Image-{Turbo,Edit}_GGUFs`.
- **License:** Apache-2.0 (commercial use OK), open weights, not gated.
- **Source:** huggingface.co/Boogu (maker) ; huggingface.co/Comfy-Org/Boogu-Image (ComfyUI repack) ; demo-turbo.boogu.org.

### Mage-Flow / Mage-Flow-Edit (Microsoft, 4B, MIT)
- **What it is:** one compact 4B stack that does BOTH text-to-image and instruction editing. Mage-VAE (lightweight tokenizer) + NR-MMDiT, a Native-Resolution Multimodal DiT trained with rectified flow matching, prompts encoded by **Qwen3-VL 4B**. Landed in core **v0.29.0** (PR 15026, kijai, CORE-372). Native resolution means ONE checkpoint covers **512 to 2048** on any aspect ratio, including extreme 4:1 (`2048x512`), with no bucket quantization.
- **Prompt style:** natural-language prose, English recommended by the official templates. Long descriptive paragraphs work (the shipped examples run 80 to 150 words: subject, wardrobe/material detail, setting, light, grade, film/lens vocabulary). No tag weighting, no bracket syntax.
- **Edit structure:** state **what to keep first, then what to change** - "Keep the woman, pose, pink dress, chair and reading unchanged. Replace the background with a wide flat grassland prairie under soft golden sunlight..." (verbatim shape of the official `image_mage_flow_edit_int8` prompt). Handles background replacement, style/light change, localized content edits, restoration and multi-reference blends; **1 to 3 references recommended**, the node accepts up to 16.
- **Negatives:** supported. The node passes a literal single space when you leave `negative_prompt` empty, matching the upstream `neg_prompts=" "` default; negatives only apply while `cfg > 1`, so they are inert on Turbo (CFG 1.0).
- **The one node you need: `TextEncodeMageFlowEdit`** (category `model/conditioning/mage`, from `comfy_extras/nodes_mage.py`). It is used for text-to-image AND edit - the same node, images left unconnected for t2i.
  - **Inputs:** `clip` (CLIP), `prompt` (STRING multiline), `negative_prompt` (STRING multiline, advanced), `vae` (VAE, optional), `images` (Autogrow `image_1`..`image_16`, min 0), `width` (INT, default 0, max 8192, step 16), `height` (same), `batch_size` (INT, default 1, max 4096).
  - **Outputs, in order:** `positive` (CONDITIONING), `negative` (CONDITIONING), `latent` (LATENT). It emits the empty latent itself, so **do not wire an `EmptyLatentImage`** - the sizes would not match.
  - **Size rule (read from the code):** `width`/`height` of 0 fall back per-axis to the FIRST reference image's size, or to 1024x1024 with no references; both are then floored to a multiple of 16. The latent is `[batch, 128, height/16, width/16]`, so the VAE is a 16x downsampler with 128 latent channels.
  - **Two resize paths, and they differ:** every reference is resized to the OUTPUT resolution before VAE encode, because Mage's RoPE aligns reference and target content by position; the copy fed to the VL text encoder is separately capped at a **384px long edge** (training preprocessing, upstream `vl_cond_long_edge=384`). Both branches, positive and negative, carry the same reference latents; only the instruction text differs.
- **Build the graph (confirmed from the official template subgraphs):**
  - **t2i:** `UNETLoader` -> `KSampler.model`; `CLIPLoader` (**`type` = `mage`**) -> `TextEncodeMageFlowEdit.clip`; `VAELoader` -> `TextEncodeMageFlowEdit.vae` and -> `VAEDecode.vae`; `TextEncodeMageFlowEdit` `positive`/`negative`/`latent` -> `KSampler` `positive`/`negative`/`latent_image`; `KSampler` -> `VAEDecode` -> `SaveImageAdvanced`.
  - **edit:** the same chain plus `LoadImage` -> `TextEncodeMageFlowEdit.image_1` (add `image_2`, `image_3` for multi-reference). The official template routes `LoadImage` through `ImageScaleToTotalPixels` (lanczos, `megapixels` 1.0) first and reads the result with `GetImageSize` to drive width/height; that pre-scale is a convenience, not a requirement.
- **Settings (upstream table, cross-checked against the template KSamplers):** Base **30 steps / CFG 5.0**; RL-aligned **20 steps** t2i (**30** for Edit) / CFG 5.0; Turbo **4 steps / CFG 1.0** (Turbo must run CFG 1.0). Sampler `euler`, scheduler `simple` in every shipped template. 1024 longest side for everyday work, 1536 to 2048 when you need detail.
- **Weights, `Comfy-Org/Mage-Flow` (MIT, open, not gated):** `diffusion_models/mage_flow_{base_bf16, bf16, int8_convrot, turbo_bf16, turbo_int8_convrot}` and the same five for `mage_flow_edit_*`; `text_encoders/qwen3vl_4b_bf16.safetensors`; `vae/mage_flow_vae_bf16.safetensors`. **Naming trap:** upstream calls the RL-aligned checkpoint plain `microsoft/Mage-Flow` and the unaligned one `Mage-Flow-Base`, so in the repack **`mage_flow_bf16` is the RL variant and `mage_flow_base_bf16` is Base** (inferred, on two legs: the upstream model zoo in `github.com/microsoft/Mage` names the RL checkpoint plain `Mage-Flow` and the unaligned one `Mage-Flow-Base`, and the repack's own commit history uploaded `mage_flow_bf16` in its initial 2026-07-24 commit and added `mage_flow_base_bf16` separately on 2026-07-29, which only makes sense if the first one was not Base. Not closed: the safetensors headers carry no provenance (`{'format': 'pt'}`, 397 tensors either way), the Comfy-Org card documents only the eight non-`base` files, and the upstream HF repos cannot be checked because none of the six Mage-Flow repos is publicly visible, authenticated or not, as of 2026-08-01). The t2i template ships the RL weights at Base's 30 steps - upstream says 20 for RL.
- **Gotchas:** 2048x2048 output has an open quality complaint on both Base and Turbo (gh 15099, short prompts) - prefer 1024 to 1536 and treat 2K as experimental. `int8_convrot` weights are the fast path but inherit the open int8 bugs (NaN on ROCm gfx1201, gh 15084); bf16 is the safe fallback. Cards without bf16 support needed PR 15081, which is already in v0.29.0 (merged 2026-07-26, listed in that release), so any v0.29.x has it.
- **License:** MIT (Mage-Flow and the ComfyUI repack). Open weights, no gate.
- **Source:** github.com/microsoft/Mage `mage_flow/README.md` (model zoo, parameter table) ; arxiv.org/abs/2607.19064 ; `comfy_extras/nodes_mage.py` on master ; templates `image_mage_flow_{t2i,turbo_t2i,edit,edit_turbo}_int8.json` ; huggingface.co/Comfy-Org/Mage-Flow ; Comfy-Org/ComfyUI PR 15026.
