# Image editing models (instruction-based)

Part of the kit's per-model prompting reference. The routing table and the auto-pull rule live in
[`MODELS.md`](../MODELS.md); this file holds the 4 entries for this family.


Edit models take an input image + a change instruction, not a from-scratch prompt. Also see FLUX.1 Kontext,
Qwen-Image-Edit, OmniGen (above), Seedream Edit, and Nano Banana edit, which are instruction-based too.

### FireRed Image Edit
- **Prompt style:** instruction, bilingual CN-EN; state the change directly.
- **Structure:** direct edit command; text edits name the literal string + placement ("add '2nd Edition' below 'Python'"); makeup/style transfer, virtual try-on, old-photo restoration, multi-element edits; no rigid template.
- **Strengths:** precise instruction following, identity preservation, high-fidelity text-in-image (open-source SOTA edit).
- **Avoid:** no official CFG/negative/resolution spec; Lightning-8steps variant for speed.
- **Settings:** sparse official numbers (~4.5s/sample, ~30GB VRAM optimized); official ComfyUI workflow + quantized weights (v1.0/v1.1).
- **Source:** github.com/FireRedTeam/FireRed-Image-Edit.
- **ComfyUI build:** official template `image_firered_image_edit1_1.json` (Comfy-Org template library).

### LongCat-Image / LongCat-Image-Edit (Meituan)
- **Prompt style:** natural-language (T2I) / instruction (edit), bilingual; 6B.
- **Structure:** CRITICAL text rule - enclose literal target text in quotes ('...' / "..."); a character-level encoder handles quoted content, unquoted text renders poorly. Edit instructions are direct ("turn the cat into a dog").
- **Strengths:** multilingual text in images, photorealism, efficient (6B beats larger on several benchmarks).
- **Avoid:** forgetting quotes around target text. Negative prompt can be empty.
- **Settings (T2I):** guidance_scale 4.0, 50 steps, 768x1344 canonical resolution, `enable_cfg_renorm=True`, `enable_prompt_rewrite=True` (LLM prompt-refine flag, improves quality), bf16, ~17GB VRAM with CPU offload.
- **Settings (edit):** guidance_scale 4.5, 50 steps, bf16, ~18GB VRAM with CPU offload.
- **ComfyUI build:** no official Comfy-Org template; run via diffusers, or a community repack/wrapper if one is installed.
- **Source:** huggingface.co/meituan-longcat/LongCat-Image-Edit ; huggingface.co/meituan-longcat/LongCat-Image.

### ChronoEdit (NVIDIA)
- **Prompt style:** instruction; optional Prompt Enhancer rewrites it.
- **Structure:** image + short imperative ("Add sunglasses to the cat's face"); reframes the edit as a short video between input and edited frame so changes respect physics; up to ~300 tokens.
- **Strengths:** physically/temporally consistent edits, action-conditioned "world simulation"; can output the reasoning frames.
- **Avoid:** gated card, sparse on CFG/negatives; use `--use-prompt-enhancer` for terse instructions.
- **Settings:** RGB input recommended <=1024x1024; Upscaler LoRA published; ComfyUI + diffusers (nvidia/ChronoEdit-14B-Diffusers).
- **Source:** github.com/nv-tlabs/ChronoEdit.
- **ComfyUI build:** official template `image_chrono_edit_14B.json` (Comfy-Org template library) - open it and wire per the template-reading note in SKILL.md.

### JoyAI Image Edit (JD, open weights, Apache-2.0)
- **What it is:** an instruction edit model with NATIVE core support since the `comfy_extras/nodes_joyimage.py` extension landed. One node only, `TextEncodeJoyImageEdit`, which does the whole conditioning job: it tokenizes the prompt WITH the reference images attached and, when a VAE is connected, also appends their encoded latents as `reference_latents`. Runs fully local; Apache-2.0, so no gated or non-commercial flag.
- **Prompt style:** a plain imperative edit instruction, English, no template and no trigger word. The official template's worked example is exactly `Change the background to a glacial scene.` A second, EMPTY `TextEncodeJoyImageEdit` supplies the negative conditioning, so leave the negative blank unless you have a reason.
- **Build the graph (confirmed from `comfy_extras/nodes_joyimage.py` on master + the official template `image_joyai_image_edit`):**
  - `UNETLoader` (`joyai_image_edit_int8_convrot.safetensors`, weight_dtype `default`) -> **`CFGNorm`** -> `KSampler.model`. Note the position: `CFGNorm` patches the MODEL, it is NOT a conditioning node, and putting it on the positive branch is the easiest way to get this graph wrong.
  - `CLIPLoader` (`qwen3vl_8b_joyimage_edit_int8_convrot.safetensors`, **type `joyimage`**, device `default`) -> `clip` on BOTH `TextEncodeJoyImageEdit` nodes. The `joyimage` CLIP type is what the official template sets (confirmed from its widget values); that a wrong type is what breaks reference handling is inferred, but it is the first thing to check when the edit ignores the reference.
  - `VAELoader` (`wan_2.1_vae.safetensors`) -> `vae` on BOTH `TextEncodeJoyImageEdit` nodes AND -> `VAEDecode.vae`. JoyAI Image Edit uses the **Wan 2.1 VAE**, not a Qwen or FLUX one.
  - `LoadImage` -> `ImageScaleToTotalPixels` (`nearest-exact`, **1.0 megapixels**) -> the reference input of **both** encode nodes, and the same resized image -> `GetImageSize` -> `EmptySD3LatentImage` width / height, so the latent matches the normalized input instead of a fixed square. The official template feeds the positive AND the negative encoder the same image and vae; only the prompt differs.
  - positive `TextEncodeJoyImageEdit` -> `KSampler.positive`; the empty-prompt one -> `KSampler.negative`; `EmptySD3LatentImage` -> `KSampler.latent_image`; `KSampler` -> `VAEDecode` -> `SaveImageAdvanced`.
  - `images` is an **Autogrow** input, so the socket on the NODE is named **`images.image0`** (zero-based, namespaced), growing to at most six slots. Multi-reference edits are wired by adding slots, not by stacking nodes. Two different names for the same wire, do not confuse them: the official template wraps this in a subgraph whose OUTER port is called `image1`, and that port feeds `images.image0` on both encode nodes (confirmed by tracing the subgraph's boundary links). `vae` is optional: without it you get text-plus-image conditioning but no `reference_latents`, which is the weaker path.
- **Settings (from the official template):** 40 steps, CFG **4.0**, sampler `euler`, scheduler `normal`, denoise 1.0, latent 1024x1024 (driven by `GetImageSize`), `CFGNorm` strength 1.0 enabled.
- **Resolution buckets:** the node snaps every reference image to the nearest of 49 fixed ~1MP buckets by aspect ratio, from `512x2048` through `1024x1024` to `2048x512`. Feeding a wilder aspect than 1:4 / 4:1 means it gets letterboxed into the closest bucket. Each reference input must be a SINGLE image; a batch raises `JoyImage reference inputs must contain one image each`.
- **Weights:** `Comfy-Org/JoyAI-Image-Edit` hosts `diffusion_models/joyai_image_edit_{bf16,int8_convrot}.safetensors`, `text_encoders/qwen3vl_8b_joyimage_edit_{bf16,int8_convrot}.safetensors` and `vae/wan_2.1_vae.safetensors` (confirmed by listing the repo's files, 2026-07-25). **Broken card, work around it:** that repo's README body was copy-pasted from the multi-image *Plus* release and tells you to fetch `joyai_image_edit_plus_bf16` / `qwen3vl_8b_joyimage_edit_plus_*`, filenames the repo does not contain. Trust the file listing and the template, not the card. The separate Plus (multi-image) weights live at `jdopensource/JoyAI-Image-Edit-Plus-ComfyUI`.
- **Avoid:** the `_plus_` filenames from the card; putting `CFGNorm` on the conditioning instead of the model; a non-`joyimage` CLIP type; skipping the 1MP normalize step and feeding a 4K plate straight in; batching several images into one reference slot.
- **Source:** `comfy_extras/nodes_joyimage.py` (schema, buckets, encode path, read on master 2026-07-25) ; Comfy-Org/workflow_templates `image_joyai_image_edit` ; huggingface.co/Comfy-Org/JoyAI-Image-Edit ; github.com/jd-opensource/JoyAI-Image.
