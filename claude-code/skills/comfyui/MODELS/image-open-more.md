# More open image models

Part of the kit's per-model prompting reference. The routing table and the auto-pull rule live in
[`MODELS.md`](../MODELS.md); this file holds the 6 entries for this family.


### BRIA 3.x
- **Prompt style:** natural-language descriptive sentences.
- **Structure:** plain descriptive sentence; for text-in-image name the literal words + style/placement ("the words 'BRIA 3.2' in bold yellow 3D letters"). FLUX-derived MMDiT + T5-XXL.
- **Strengths:** commercial-safe (licensed-data only), short 1-6 word text rendering, photorealism, prompt adherence.
- **Avoid:** long text passages (optimized for 1-6 words). Negatives ARE supported (`negative_prompt`, active when guidance_scale > 1).
- **Settings:** FlowMatchEulerDiscrete; guidance_scale 5.0; ~30-50 steps; 1024x1024; true CFG (not distilled); T5 precision-sensitive (bf16 + final layer fp32), VAE fp32; gated.
- **Source:** huggingface.co/briaai/BRIA-3.2 (GATED - fill the form + `hf auth login` to download; commercial Bria license, free trial at bria.ai) ; github.com/Bria-AI/BRIA-3.2 (pipeline source + API; no ComfyUI nodes in the repo) ; huggingface.co/docs/diffusers/api/pipelines/bria_3_2 (`BriaPipeline`, public, no gate - recipe verified here). **ComfyUI:** no native node ships; build via the diffusers BriaPipeline or an API node.

### OmniGen (v1 / v2) - unified gen + edit
- **Prompt style:** instruction + inline image placeholders.
- **Structure:** v1 refs inline `<img><|image_1|></img>` (one per image), place the image BEFORE the instruction for edits. v2 edit template "Edit the first image: add/replace ... the [object] from the second image. [target]"; name sources explicitly; longer/detailed prompts beat short, English best.
- **Avoid:** vague cross-image references. Negatives supported in v2 ("blurry, low quality, text, watermark").
- **Settings:** v1 guidance_scale 2-3, img_guidance_scale ~1.6, output divisible by 16, 1024x1024; v2 text_guidance_scale + image_guidance_scale ~1.2-2.0 (edit) / ~2.5-3.0 (in-context), 50 steps, refs >512x512.
- **ComfyUI build (v2):** official templates `image_omnigen2_t2i.json` (t2i) and `image_omnigen2_image_edit.json` (editing) in the Comfy-Org template library. v1 has no native ComfyUI node (use diffusers).
- **Source:** github.com/VectorSpaceLab/OmniGen ; github.com/VectorSpaceLab/OmniGen2.

### Chroma
- **Prompt style:** natural-language.
- **Structure:** descriptive sentence(s): subject, style, lighting, palette.
- **Strengths:** Apache-2.0 open-weight 8.9B from FLUX.1-schnell; broad/less-censored aesthetic range; Chroma1-HD is the higher-quality variant.
- **Avoid:** no official prompt-recipe doc (maker says users figure settings out), treat numbers as examples. Negatives supported (card example: "low quality, ugly, unfinished, out of focus, deformed, blurry, flat colors").
- **Settings:** card example ~40 steps, CFG 3.0, bfloat16; ChromaPipeline; same optimizations as Flux.
- **ComfyUI setup:** put the checkpoint in `diffusion_models/` (NOT `checkpoints/`); needs a T5 XXL text encoder (`t5xxl_fp16.safetensors`) in `models/clip/` and the FLUX VAE (`ae.safetensors`) in `models/vae/` as separate downloads. Official workflow JSON: huggingface.co/lodestones/Chroma1-HD/resolve/main/ComfyUI_Chroma1-HD_T2I-workflow.json. Worked card example: "A high-fashion close-up portrait of a blonde woman in clear sunglasses ... bold teal and red color split ... designed for viewing with anaglyph 3D glasses." Sister model `Chroma1-Flash` is the fast CFG-baked variant if throughput matters.
- **Source:** huggingface.co/lodestones/Chroma1-HD.

### Krea 1 (FLUX.1 Krea [dev])
- **Prompt style:** natural-language, no weighting syntax.
- **Structure:** subject + style + scene + lighting + colors; short imaginative prompts work.
- **Strengths:** photorealism without the "AI look" (no plastic texture / blurred-bg artifacts); drop-in for FLUX.1 [dev].
- **Avoid:** filler ("beautiful", "amazing"); ignores `(best quality:1.3)` / `[[masterpiece]]` brackets/colons; guidance-distilled so no true CFG/negative (like FLUX.1 [dev]).
- **Settings:** guidance_scale 4.5 (official example); 1024x1024; FLUX.1 [dev] pipeline.
- **Download / license:** GATED on HF, accept the license + use a token to download (must accept the FluxDev Non-Commercial License Agreement + Acceptable Use Policy on the model page first). License is NON-COMMERCIAL only (flux-1-dev-non-commercial-license).
- **Source:** huggingface.co/black-forest-labs/FLUX.1-Krea-dev ; docs.krea.ai.

### Krea 2 (Krea AI, open weights)
- **Prompt style:** natural language; long detailed prompts give the best results, but minimal prompts also work;
  put words in quotes for text rendering. Built-in prompt enhancement is on by default in the ComfyUI template (swap
  it for OpenAI / Gemini nodes, or use the repo's `expansion.txt` as an LLM system prompt).
- **Example (official prompt guide):** minimal works (`immense rocket launch exhaust as seen from extremely close
  up`), but detail wins. Stack natural-language clauses for subject, composition, lighting, color, texture, and
  medium, e.g. `stylized digital painting of a dark convertible on a winding coastal cliff road, high-angle
  perspective, blocky painterly brushstrokes, golden hour sunlight hitting rocky orange terrain and green
  vegetation, ... vibrant warm color palette, sharp graphic shadows`.
- **Style-suffix pattern (from ~15 of the 20 official Raw/Turbo gallery prompts):** append a comma-separated style
  tag at the END of the scene description to steer style: `<scene>, <style tag>`. Example tags from the cards:
  `halftone texture`, `thermal imaging style`, `impressionist painting, visible brushstrokes`, `black and white
  photography` (others in the galleries: low-poly 3D models, anime, vintage collage, dark fantasy concept art).
- **Two models that pair:** **RAW** (base, undistilled, diverse and malleable) is for fine-tuning and LoRA training;
  **Turbo** (8-step distilled) is for fast inference. Train LoRAs on RAW, then apply them on Turbo (compatible).
- **Strengths:** from-scratch MMDiT; the most aesthetic open-weight image model and the #1 text-to-image model from
  an independent lab (Artificial Analysis); 2K-native on Turbo, strong text rendering. Architecture rides the Qwen
  stack: a Qwen3-VL-4B text encoder + the Qwen-Image VAE.
- **Settings:** RAW = full sampler, 52 steps, CFG 3.5, up to 1K. Turbo = 8 steps, CFG 0.0 (disabled), mu 1.15 (the
  flow shift), 1K to 2K (2048x2048).
- **Run it (ComfyUI, day-0 native, no custom nodes):** official template `image_krea2_turbo_t2i` in the Comfy-Org
  template library. Comfy-Org repackaged the weights at `huggingface.co/Comfy-Org/Krea-2`:
  `diffusion_models/krea2_turbo_fp8_scaled` (plus BF16 / NVFP4 variants), `text_encoders/qwen3vl_4b_fp8_scaled`,
  `vae/qwen_image_vae`. NINE official style LoRAs (`Comfy-Org/Krea-2/loras`), each with its trigger word at strength
  1.0 (put the trigger phrase in the prompt): `krea2_darkbrush` "monochrome ink wash style", `krea2_dotmatrix`
  "Monochrome stippling style", `krea2_kidsdrawing` "naive expressive sketch style", `krea2_neondrip` "Textured abstract
  style", `krea2_rainywindow` "rainy window style", `krea2_retroanime` "Purple retro anime style", `krea2_softwatercolor`
  "Art Deco watercolor style", `krea2_sunsetblur` "ethereal motion blur style", `krea2_vintagetarot` "vintage tarot style".
- **Community style LoRAs (fal, ~1503):** beyond the 9 official LoRAs, `ilkerzgi/fal-Krea-2-Style-LoRAs` indexes ~1503
  community style LoRAs for Krea 2 Turbo (Krea-2 Community License), each its own repo (e.g. `ilkerzgi/krea-2-airy-porcelain-blue-lora`).
  Put the style trigger at the END of the prompt, LoRA scale 1.0-1.25; run on fal `fal-ai/krea-2/turbo/lora` or download the individual LoRA.
- **Weak VAE, much better decode (RECOMMENDED, big quality jump):** Krea 2's stock Qwen-Image VAE is the weak link;
  swapping the decoder is a large, clearly visible jump (practitioner-confirmed, not subtle). Use **NVIDIA PiD** (Pixel
  Diffusion Decoder: latent-conditioned pixel-diffusion decode + super-res in one pass) via **`Merserk/ComfyUI-PiD`**
  (MIT, Comfy-Org/PixelDiT loading; prefer over `tsolful/ComfyUI-PiD`, which is thinner + license "other"). **Build it:**
  PiD needs the latent AND its sigma, so replace the stock `KSampler -> VAEDecode` tail with `PiD KSampler Capture` (a
  drop-in sampler, outputs `pid_latent` + `pid_sigma`) -> `PiD Decode` (latent + caption + sigma -> `IMAGE`), caption from
  `PiD Text Prompt`. Krea 2 rides the Qwen-Image VAE latent, so use PiD's Qwen-Image path at `model_precision=bf16` (fp8 is
  Flux-only); weights auto-download (`auto_download=true`) into `models/vae/nvidia_pid/`. Simpler alternative: swap the VAE
  node for the **WAN 2.1 VAE**. (PiD's official backbones are flux/flux2/sd3/zimage; Krea 2 is community-applied, works very
  well.) Sources: github.com/Merserk/ComfyUI-PiD ; github.com/nv-tlabs/PiD ; Reddit r/StableDiffusion 1ue8rns ; t.me/GreenNeuralRobots/12656.
- **Reference-image control (image+mask), buildable:** `ComfyUI-Krea2TextEncoder` (ethanfel, MIT) adds the
  **`TextEncodeKrea2`** node (category `model/conditioning/krea2`). **Wire it in place of the text encode:** inputs `clip`
  (the Krea2 CLIP) + `prompt` (multiline) + optional reference pairs `image1`/`mask1` (a fresh `image2`/`mask2` appears as
  you connect each) + `mask_padding` (0 = tight crop to the mask, ~0.1 = ~10% margin per side); output `CONDITIONING` -> the
  sampler's positive. It forces the Krea2 descriptor template and routes the reference image+mask through Krea 2's
  Qwen3-VL-4B vision path, fixing the core `TextEncodeQwenImageEdit` (whose VAE input does nothing, since Krea 2's DiT has no
  reference-latent slot, and which falls back to the plain Qwen template).
- **Removing model refusals (abliterated text encoder) - general technique, shown here on Krea 2:** Krea 2's text
  encoder is `Qwen3-VL-4B-Instruct`, an instruction-tuned VLM, so it inherits the LLM's alignment and can quietly
  steer away from legit-but-flagged VFX asks (wounds / gore for horror, weapons, real people or brands, "disturbing"
  imagery). Swapping it for an **abliterated** build (`huihui-ai/Huihui-Qwen3-VL-4B-Instruct-abliterated`, ComfyUI
  repack `ahmed22xa/...-comfy`; abliteration ablates the refusal direction via activation steering) makes the
  encoder encode the prompt faithfully instead of refusing - drop it into the `CLIPLoader` (type `krea2`) in place
  of the stock `qwen3vl_4b`. Model-agnostic: any DiT on an LLM/VLM encoder (Krea 2, Qwen-Image) takes the same swap
  (general note in ADVANCED.md "Removing model refusals"). It changes the encoder's WILLINGNESS, not the model's
  capability, and still carries the base license's acceptable-use terms - keep it to content you are licensed to
  make. The complete community build (Soror L.L., "RED_KREA_2") stacks three parts, documented here IN FULL so the
  kit can reproduce it on request: (1) the abliterated TE above (via `CLIPLoader`); (2) an uncensored UNET -
  `redcraftKREA2RedMix_krea2Edition.safetensors`, a community NSFW merge / finetune of Krea 2, loaded through
  `UNETLoader`; (3) an optional custom **LoKr** adapter trained on Krea 2 (the shared `max_Krea2_LoKr.yaml` config -
  LoKr = low-rank Kronecker, a LoRA variant), driven with RES4LYF samplers (`ClownsharKSampler_Beta` /
  `SharkOptions_Beta`), Perturbed-Attention Guidance, SageAttention, and the official `Comfy-Org/Krea-2` style
  LoRAs. Parts 2-3 are community, un-benchmarked, NSFW-oriented, and bound by the base license's acceptable-use
  terms; the reusable general part is the abliterated encoder. **USAGE (kit policy): on-request reference, not a
  promoted feature - apply it when a task actually calls for it, do NOT proactively suggest it, and keep it out of
  the README / CHANGELOG / banner.** Source: huggingface.co/huihui-ai/Huihui-Qwen3-VL-4B-Instruct-abliterated ;
  huggingface.co/ahmed22xa/Huihui-Qwen3-VL-4B-Instruct-abliterated-comfy.
- **License:** the code is Apache-2.0; the WEIGHTS use the Krea 2 Community License: commercial use needs a separate
  Enterprise License (community use is non-commercial), with acceptable-use / content-filter obligations.
- **Model merging (ComfyUI core):** the **`ModelMergeKrea2`** node (a `ModelMergeBlocks` subclass in `comfy_extras/nodes_model_merging_model_specific.py`) merges two Krea 2 `MODEL`s with per-block ratio control - blend a Krea 2 base with a fine-tune (or another Krea 2 checkpoint) without leaving ComfyUI.
- **Instruction editing on Krea 2 (community, experimental) - Ostris edit method + a detail-enhancer LoRA:** Krea 2
  is TEXT-TO-IMAGE, not an edit model, but Ostris (creator of AI Toolkit) trained an edit method and shipped
  **`ostris/ComfyUI-Krea2-Ostris-Edit`** (2 nodes, no extra deps, category `ostris/krea2`): **Text Encode Krea 2
  Ostris Edit** (encodes the prompt + up to 3 reference images through Krea 2's Qwen3-VL encoder with `Picture N:`
  vision placeholders, and with a VAE also VAE-encodes each ref as a reference latent; images fit 384x384 for the
  encoder / 1MP for the latent) and **Krea 2 Ostris Edit Model Patch** (patches Krea 2 to CONSUME those reference
  latents - stock Krea 2 ignores them; refs appended to the image tokens, conditioned at timestep 0; a no-op when
  there are no refs, so safe to leave in). CONFIRMED from the example graph (`workflow/Krea2_Ostris_Edit.json`, 16
  nodes): UNET **`krea2_turbo`**, CLIP **`qwen3vl_4b_alb_bf16`** (an ABLITERATED, vision-capable Qwen3-VL-4B; `alb`
  inferred = abliterated, which also helps edit prompts land - the vision weights are what encode the refs), VAE **`qwen_image_vae`**;
  the input image runs through core **`FluxKontextImageScale`** and then feeds both the **Text Encode Krea 2 Ostris
  Edit** image input AND a **`FluxKontextMultiReferenceLatentMethod`** set to `index_timestep_zero`; the edit LoRA
  loads via `LoraLoaderModelOnly` into the **Model Patch**; sampler is Turbo (euler / simple, **10 steps, cfg 1,
  denoise 1**, 1024x1024); the prompt is an edit instruction (the example: "make this person a cyclops"). Edit
  LoRAs are trained with ai-toolkit (`krea2` arch, `model_kwargs.edit: true`). One published edit LoRA: **`reverentelusarca/krea2-detail-enhancer-edit-lora`**
  (`krea-detail-enhancer-exp.safetensors`, **krea2-community-license** = non-commercial) - a DETAIL enhancer,
  trigger **"enhance this image"** (full prompt: high-res, rich fine detail, sharpen textures, add microdetail +
  natural grain, preserve the original composition / lighting / style). HONEST (author's own caveats): highly
  experimental, NOT Flux.2 Klein / Qwen-Image-Edit precision - it alters the image, shifts lighting / color
  slightly, and can fault on horizontal aspect ratios. Needs a Krea 2 text encoder that INCLUDES the Qwen3-VL
  vision weights (the vision-less encoder cannot encode the reference images). **Best results (how to drive it):**
  load the detail-enhancer at strength ~1 and use the author's FULL prompt, trigger first - "enhance this image.
  Enhance this image to high resolution with rich fine details. Sharpen all textures and surfaces, add microdetails
  and natural grain. Increase clarity and definition across all elements while preserving the original composition,
  lighting, and atmosphere. Image can be illustration or real photo, keep the original input style." Feed a SQUARE
  or vertical input (~1MP; the encoder downscales refs to 384x384 and the ref latent to 1MP anyway) and AVOID
  horizontal aspect ratios (the author reports faults there). Because the method shifts lighting / color slightly,
  if you need fidelity, color / luminance-match the output back to the source (our OCIO `Grade Match`, or an
  `ImageColorMatch`) - a cheap fix for the drift. Keep it to the detail / enhance job it was trained for; for
  precise object or text edits reach for Flux.2 [Klein] or Qwen-Image-Edit (Krea 2 is a t2i model bent into
  editing, not a native edit model). The shipped example is the Turbo path (10 steps, cfg 1); RAW (52 steps, CFG
  3.5) MAY lift fidelity but is untested with these edit LoRAs (inferred - would need a real run to confirm).
  Source: github.com/ostris/ComfyUI-Krea2-Ostris-Edit ; huggingface.co/reverentelusarca/krea2-detail-enhancer-edit-lora.
- **Style reference from an image (Turbo, core nodes, NO custom node needed):** `krea2_style_reference.safetensors`
  is a LoRA by ostris that makes Krea 2 Turbo generate in the STYLE of a reference image. **No trigger word** (the
  card says so outright); it was trained for 1-2 reference images.
  **Read the card against the template here.** The HF card tells you to install `ComfyUI-Krea2-Ostris-Edit` to run
  it. The official Comfy-Org template `image_krea2_turbo_int8_image_style_reference` does it with CORE nodes only,
  so the custom node is no longer required for this LoRA (confirmed by reading the template's node list, 2026-07-25).
  Build it: `UNETLoader` (`krea2_turbo_int8_convrot.safetensors`) -> `LoraLoaderModelOnly`
  (`krea2_style_reference.safetensors`, strength 1.0) -> `ModelSamplingFlux` (1.15, 0.5, 1024, 1024) -> `CFGGuider`
  (cfg **1.0**) -> `SamplerCustomAdvanced`; `CLIPLoader` (`qwen3vl_4b_fp8_scaled.safetensors`, **type `krea2`**) plus
  the reference `LoadImage` -> **`TextEncodeQwenImageEditPlus`** (this is the node that carries the reference image
  into conditioning) -> `CFGGuider`; **`FluxKontextMultiReferenceLatentMethod`** set to **`index_timestep_zero`** on
  the conditioning; `KSamplerSelect` `euler` + `BasicScheduler` (`simple`, **8 steps**, denoise 1.0) + `RandomNoise`
  into `SamplerCustomAdvanced`; `VAELoader` (`qwen_image_vae.safetensors`) -> `VAEDecode` -> `SaveImage`. A
  `ResolutionSelector` drives the output size, and the template leaves the built-in `TextGenerate` prompt-expander
  switched OFF for this graph.
  Weights: `Comfy-Org/Krea-2` `loras/krea2_style_reference.safetensors` (confirmed present by listing the repo), or
  the author's `ostris/krea2_turbo_style_reference`. Licence flag: **krea-2-community-license** (same as the base
  Turbo weights). Worked example from the card's `widget:` gallery: `a white yeti with horns reading a book that is
  titled "Ostris + Krea2 Style Reference"`.
  Source: huggingface.co/ostris/krea2_turbo_style_reference (full card incl. frontmatter) ;
  Comfy-Org/workflow_templates `image_krea2_turbo_int8_image_style_reference`.
- **Everything Krea that is NOT this local graph lives in the sibling `krea` skill** (invoke by name; beside the comfyui skill on disk): the
  hosted API nodes `Krea2ImageNode` / `Krea2StyleReferenceNode` with their price matrix and the 1K cap, the
  FLUX.1 Krea Dev graph, Krea Realtime 14B, and the community packs that add ControlNet, identity-preserving
  editing and per-layer conditioning control to Krea 2. This entry stays the source of truth for the local
  Raw / Turbo graph itself.
- **Source:** github.com/krea-ai/krea-2 (incl. `docs/prompting.md`) ; huggingface.co/Comfy-Org/Krea-2 (ComfyUI repackaged) ;
  huggingface.co/krea/Krea-2-Raw + huggingface.co/krea/Krea-2-Turbo ;
  blog.comfy.org/p/krea-2-open-source-models-are-now ; krea.ai/blog/krea-2-technical-report.

### ERNIE-Image (Baidu)
- **Prompt style:** instruction / natural-language; built-in 3B Prompt Enhancer expands terse inputs.
- **Structure:** describe the scene + exact text strings and their layout; handles multi-object relations and knowledge-intensive descriptions; EN/CN + mixed-language text in one image.
- **Strengths:** layout-sensitive typography, multilingual text, complex/structured compositions (posters, storyboards, multi-panel); Apache-2.0 8B single-stream DiT.
- **Avoid:** no official CFG/negative/resolution recipe published; lean on the prompt enhancer for terse inputs.
- **Settings:** base ~50 steps; ERNIE-Image-Turbo 8 steps; Comfy repack needs ernie-image[-turbo], ernie-image-prompt-enhancer, ministral-3-3b, flux2-vae.
- **Source:** docs.comfy.org/tutorials/image/ernie-image/ernie-image ; github.com/baidu/ERNIE-Image. (Baidu's text-to-image DiT, NOT the ERNIE-4.5-VL understanding models.)
