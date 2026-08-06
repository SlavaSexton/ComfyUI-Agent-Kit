# Image models (API / closed)

Part of the kit's per-model prompting reference. The routing table and the auto-pull rule live in
[`MODELS.md`](../MODELS.md); this file holds the 12 entries for this family.


### Ideogram (2.x to 4.0, plus P-Image)
- **Nodes available (ComfyUI v0.29.2):** **`IdeogramV3`**, **`IdeogramV4`** and, new in v0.29.2, **`IdeogramPImage`**. The old **`IdeogramV1` and `IdeogramV2` nodes were REMOVED in v0.28.0** (Comfy-Org PR #14712), so an older graph that loads them will fail to resolve the node; rebuild it on V3 / V4. Confirmed from `comfy_api_nodes/nodes_ideogram.py` on master (the extension registers exactly those three) plus the v0.28.0 and v0.29.2 release notes.
- **Prompt style:** natural-language sentences (no tags, no `--ar`/`::` flags); typography specialist.
- **Structure:** describe as to a person; important elements and text early; exact text in quotes (under ~25 chars), describe font style/position/color, don't name fonts.
- **Strengths:** quoted-text rendering, posters/logos/signage; `DESIGN` style for typography, `REALISTIC` for photos.
- **Avoid:** long text strings, burying text mid-prompt, naming fonts. Negative prompts ARE supported (`negative_prompt`; positive takes precedence).
- **Settings (API):** `style_type`, `rendering_speed` (TURBO/DEFAULT/QUALITY), `magic_prompt`, aspect ratios, seed, up to 4 images/call, character & style refs.
- **Structured / JSON prompting (Ideogram 4) - two real paths:**
  - **Base node:** **`IdeogramV4`** ("Ideogram V4") takes a plain multiline `prompt` (+ a `resolution` combo, `rendering_speed` = `DEFAULT` / `TURBO` / `QUALITY`, and `seed`) -> `SaveImage` (confirmed from `comfy_api_nodes/nodes_ideogram.py`). The official `api_ideogram_v4_t2i` template expands a short idea into a longer caption with a **`GeminiNode`** "magic prompt" that feeds `IdeogramV4`.
  - **Spatial structured-control path (new core nodes, confirmed from `comfy_extras/nodes_bounding_boxes.py` + `nodes_json_prompt.py` + `nodes_ideogram4.py`):** **`CreateBoundingBoxes`** ("Create Bounding Boxes", category `utilities`) is a visual region editor (drag boxes, grid-snap, colour-pick) with outputs `preview` (IMAGE), `bboxes` (BOUNDING_BOX), `elements` (ARRAY). Wire `elements` into **`BuildJsonPromptIdeogram`** ("Build JSON Prompt (Ideogram)", category `text`) along with `high_level_description`, `background`, `style` (`none` / `photo` / `art_style`), `aesthetics`, `lighting`, `medium`, and a `color_palette` (COLORS, up to 16 hex); it outputs a `prompt` (DICT) caption (`high_level_description` / `style_description` / `compositional_deconstruction`) for Ideogram 4. **`Ideogram4Scheduler`** ("Ideogram 4 Scheduler") is the paired scheduler. Use this to PLACE elements spatially instead of hoping prose lands the layout. These nodes are experimental and very new (the `CreateBoundingBoxes` widget landed in frontend v1.48.2, 2026-07-11), so no official template ships them yet.
- **P-Image (new in core v0.29.2, PR 15154) - the fast tier that still does typography.** Node **`IdeogramPImage`** ("Ideogram P-Image", category `partner/image/Ideogram`), confirmed from `comfy_api_nodes/nodes_ideogram.py` on master.
  - **Widgets:** `prompt` (multiline), `quality` (`VERY_LOW` / `LOW` / `MEDIUM` / `HIGH`, default `MEDIUM`), `resolution` (`1K` / `2K`, default `1K`), `aspect_ratio` (the V3 ratio list, default `1:1`), `prompt_upsampling` (`AUTO` / `ON` / `OFF`, default `AUTO`), `seed`.
  - **Two outputs:** `IMAGE` and **`final_prompt` (STRING)** - the caption the image was actually generated from. This is the reproducibility handle: with upsampling ON or AUTO the rewrite varies per run, so to reproduce a result feed `final_prompt` back in with `prompt_upsampling` = `OFF` and the same seed. Wire `final_prompt` to `PreviewAny` to read it.
  - **Build the graph (official `api_ideogram_p_image_t2i` template):** `CreateBoundingBoxes` -> `BuildJsonPromptIdeogram` -> `IdeogramPImage.prompt`, then `IdeogramPImage.IMAGE` -> `SaveImageAdvanced` and `final_prompt` -> `PreviewAny`. That is the same structured-caption path as Ideogram 4 above, so the spatial layout tooling carries straight over. Plain prose into `prompt` also works.
  - **Rules that matter:** the node's own tooltips say difficult text renders poorly **below `MEDIUM`**, and to prefer **`HIGH` + `2K`** for crisp typography; set `prompt_upsampling` = `OFF` whenever you supply your own JSON caption or exact wording, otherwise the rewrite overwrites it. Resolution is a size CLASS, not pixels: 16:9 gives 1280x720 at 1K and 2560x1440 at 2K. A blocked generation raises a content-safety error rather than returning an image.
- **Source:** docs.ideogram.ai/using-ideogram/prompting-guide ; developer.ideogram.ai ; ComfyUI v0.27.0 (CORE-292, PR 14537) ; `comfy_api_nodes/nodes_ideogram.py` + Comfy-Org/ComfyUI PR 15154 (P-Image, v0.29.2) ; template `api_ideogram_p_image_t2i.json`.

### Nano Banana Pro (Gemini 3 Pro Image)
- **Prompt style:** natural-language, rich descriptive paragraphs (describe the scene, don't list keywords).
- **Structure:** prose covering subject, spatial relationships, lighting/mood, woven-in camera language; exact text in quotes; label each reference by role ("Image 1 is the product").
- **Strengths:** internal reasoning before render, multilingual text + in-image translation, character consistency, reference blending, Google Search grounding (add "using current data"), world-knowledge physics. Up to 11 refs.
- **Avoid:** keyword lists, bracket templates, telegraphic language, vague praise. Negatives not used, phrase positively ("an empty street", not "no cars").
- **Source:** ai.google.dev/gemini-api/docs/image-generation.

### Nano Banana 2 (Gemini 3.1 Flash Image)
- **Prompt style:** natural-language descriptive prose (same as Pro), speed-optimized (<~20s).
- **Structure:** six elements - subject, composition/camera, action, aspect ratio (state when non-standard), lighting (photographic terms), style; exact text in quotes; label refs; request resolution above default 1K.
- **Strengths:** fast iteration, extended ratios (1:4, 4:1, 1:8, 8:1), tiers 0.5K/1K/2K/4K, web+image Search grounding, up to 14 refs, 360-degree character sheets.
- **Avoid:** keyword dumps, bracket templates, negative phrasing, temperature below 1.0 (loops). Small CJK text and data-viz error-prone; knowledge cutoff Jan 2025 (use grounding).
- **Source:** ai.google.dev/gemini-api/docs/image-generation.

### Nano Banana 2 Lite (Gemini Flash Image, fast tier)
- **Prompt style:** the same descriptive prose as Nano Banana 2, at a lower quality ceiling; built for volume, not the last 5% of fidelity.
- **Strengths:** the fastest / cheapest Nano Banana tier. Vendor claims from the ComfyUI launch post (treat as marketing): ~4 s per image, ~$0.034 per 1K images. Aimed at high-volume iteration and batch variations (ad-asset batches, 50 concept variants before the brief changes).
- **Run it:** official Comfy partner API nodes / templates `api_nano_banana_2_lite_t2i` (text-to-image) and `api_nano_banana_2_lite_image_edit` (edit), both confirmed in the Comfy-Org/workflow_templates index (a sibling `api_google_nano_banana2_image_edit` also ships). Cloud / paid (Comfy Cloud or a Gemini API key), NOT a local model.
- **Source:** ai.google.dev/gemini-api/docs/image-generation ; Comfy-Org/workflow_templates (`api_nano_banana_2_lite_*`).

### Seedream 4.0 / 4.5 (ByteDance)
- **Prompt style:** structured (technical specifications, direct over narrative - the exception among modern models).
- **Structure:** explicit identity-lock descriptors (face, hair, build, clothing) for series; state what's consistent vs variable; exact text in quotes; 50-100 words (range 30-300; cap ~600 EN words / 300 CN chars).
- **Strengths:** up to 15-image sequential batch with identity locking, up to 14 refs, facial-landmark consistency, sharp small-text/logo typography.
- **Avoid:** keyword dumps, flowery language, missing identity-lock descriptors. Describe positively (no explicit negative guidance).
- **Source:** volcengine.com/docs (BytePlus/Volcengine Seedream) ; node template `seedream.md`.

### Seedream 5.0 Lite (ByteDance)
- **Prompt style:** natural-language sentences REPLACE keyword lists; relationship-first; CoT reasoning model.
- **Structure:** `[subject + key trait] [action/pose] [environment with spatial relationship] [optional one-phrase style anchor]`; state object relationships; for series state count + consistency; text in double quotes; refs as Figure 1, 2.
- **Strengths:** coherent from short/abstract prompts, web search, stronger identity lock than 4.x, 2560x1440 to 3072x3072 (`auto_2K`/`auto_3K`).
- **Avoid:** CRITICAL - quality boosters ("masterpiece", "8K", "best quality") HARM output (distract the CoT pipeline); no `(word:1.3)` weights; negatives NOT supported; no guidance-scale param.
- **Source:** volcengine.com/docs (Seedream 5.0 Lite) ; node template `seedream_5_lite.md`.

### Seedream 5.0 Pro (ByteDance)
- **Prompt style:** same natural-language, CoT-reasoning family as 5.0 Lite (relationship-first sentences, NOT keyword lists); state object relationships and, for a series, count + consistency; exact text in double quotes; label refs as Figure 1, 2.
- **Strengths:** ByteDance's latest image model - **multi-modal in ONE node** (text-to-image, precise image editing, multi-image inputs); strong **character + product consistency** (portrait identity / lighting / realism held across style changes and edits); **region-precise editing** (edit a target area, leave lighting / depth / texture elsewhere untouched); **structured layouts** (infographics, flowcharts, mixed text+image with legible small text). Up to ~2048x2048.
- **Avoid:** quality boosters ("masterpiece", "8K", "best quality") HARM output (they distract the CoT pipeline); no `(word:1.3)` weights; negatives NOT supported; no guidance-scale param.
- **Thinking toggle (ComfyUI v0.28.0):** the Seedream node gained a widget to **disable thinking** (Comfy-Org PR #14853). Leave it ON for the CoT behaviour this recipe assumes (relationship reasoning, layout planning); turn it OFF for a faster, more literal pass when the prompt is already explicit and you do not want the model re-planning the composition.
- **Build the graph (confirmed from the official templates):** ONE node **`ByteDanceSeedreamNodeV2`** -> **`SaveImageAdvanced`** (its `IMAGE` out -> `SaveImageAdvanced.images`). Node widgets = prompt, `model` = `seedream 5.0 pro`, a **size-preset combo** (e.g. `(1K) 1024x1024 (1:1)`) + width / height (up to 2048), seed + control_after_generate (leave the remaining toggles at their template defaults).
  - **t2i** - just the node, its `model.images.image_1` input left unconnected.
  - **edit / multi-image** - **`LoadImage`** -> `model.images.image_1` (add `image_2`, `image_3`... for more refs) -> node -> `SaveImageAdvanced`. To constrain the edit to a drawn region, route `LoadImage` through a **`Painter`** node first (draw marks; its `IMAGE` out feeds `image_1`) - the official edit template does exactly this.
  - Templates `api_bytedance_seedream_5_0_pro_{t2i,image_edit}.json`. API / paid (Comfy Cloud or a BytePlus key).
- **Source:** blog.comfy.org/p/seedream-50-pro ; volcengine.com / byteplus docs (Seedream 5.0) ; Comfy-Org/workflow_templates `api_bytedance_seedream_5_0_pro_*`.

### Recraft (V3, and V4 / V4.1)
- **Prompt style:** natural-language, specific over vague; long-text + vector design specialist.
- **Structure:** "A `<style>` of `<main content>`. `<detailed description>`. `<background>`. `<style description>`." general -> specific; exact text in quotes.
- **Strengths:** long multi-word text with exact positioning/sizing; `style` param (`realistic_image`, `digital_illustration`, `vector_illustration`, `icon`) + 100+ presets + custom style refs; true scalable vector/SVG.
- **Avoid:** negative phrasing confuses it (just omit unwanted elements, no negative field); ambiguous nouns; vague plurals.
- **Two generations of nodes ship side by side** (confirmed from the `RecraftExtension` node list in `comfy_api_nodes/nodes_recraft.py` on master). V3 keeps the style/substyle system: `RecraftTextToImageNode`, `RecraftImageToImageNode`, `RecraftImageInpaintingNode`, `RecraftTextToVectorNode`, plus the utilities (`RecraftVectorizeImageNode`, `RecraftRemoveBackgroundNode`, `RecraftReplaceBackgroundNode`, `RecraftCrispUpscaleNode`, `RecraftCreativeUpscaleNode`) and the style helpers (`RecraftStyleV3*`, `RecraftCreateStyleNode`, `RecraftControlsNode`, `RecraftColorRGBNode`). **V4 / V4.1 add exactly two nodes: `RecraftV4TextToImageNode` and `RecraftV4TextToVectorNode`** - there is no V4 image-to-image or inpainting node, so an edit still routes through the V3 nodes.
- **V4.1, new in core v0.29.0 (PR 15105):** both V4 nodes take a **`model` DynamicCombo** whose options are `recraftv4_1`, `recraftv4_1_utility`, `recraftv4_1_pro`, `recraftv4_1_utility_pro`, `recraftv4`, `recraftv4_pro` (the vector node appends `_vector` to the four V4.1 names and keeps `recraftv4` / `recraftv4_pro`). Picking an option swaps the `size` list with it: the standard tiers offer 14 sizes with `1024x1024` as the default (the widest is `1536x768`), and each `_pro` tier offers the same 14 shapes at exactly double the dimensions, default `2048x2048`, widest `3072x1536`.
- **`negative_prompt` on the V4 nodes is a dead input.** Its own tooltip says so ("This input is ignored: negative prompt is not supported by Recraft V4 and V4.1 models") and `execute()` never reads it. Prompt cap is **10,000 characters**, `n` is 1 to 6 images per call, and the `seed` widget only decides whether the node re-runs - results are nondeterministic regardless.
- **Build the graph (official `api_recraft_v4_1_t2i` / `api_recraft_v4_1_text_to_vector` templates):** `RecraftV4TextToImageNode` -> `SaveImage`, or `RecraftV4TextToVectorNode` -> `SaveSVGNode` (the vector node returns SVG, not IMAGE, so a plain `SaveImage` will not accept it). For colour control, chain **`RecraftColorRGB` -> `RecraftControls`** and feed `RecraftControls` into the optional `recraft_controls` input; multiple `RecraftColorRGB` nodes chain together to pass a palette.
- **Source:** recraft.ai/docs (prompting + styles) ; recraft.ai/api ; `comfy_api_nodes/nodes_recraft.py` + `comfy_api_nodes/apis/recraft.py` on master ; Comfy-Org/ComfyUI PR 15105 (v0.29.0) ; templates `api_recraft_v4_1_t2i.json`, `api_recraft_v4_1_text_to_vector.json`.

### GPT-Image (gpt-image-2, OpenAI)
- **Prompt style:** structured natural-language ("structure beats length"), a labeled five-slot brief.
- **Structure:** Scene -> Subject -> Important Details (lighting, camera, materials, exact text in quotes) -> Use Case -> Constraints (don'ts/preservation); include literal "photorealistic"; spell unusual names letter-by-letter + "render text verbatim".
- **Strengths:** accurate dense/multi-font text, identity consistency, any size, up to 10 refs; `low` quality is production-grade.
- **Avoid:** vague praise, generic style tags, one giant rewrite, negative subject phrasing. No negative field, state avoidances in Constraints.
- **Settings (API):** `quality` (low/medium/high/auto), edges multiple of 16, max edge 3840px, <=3:1, reliable up to 2560x1440; `background`, `output_format`.
- **Source:** platform.openai.com/docs/guides/image-generation.

### Grok Image (Grok Imagine Image, xAI)
- **Prompt style:** natural-language scene description, six-part formula.
- **Structure:** Subject -> Style -> Mood -> Lighting -> Camera/Framing -> Finishing; subject in the first words; 60-80 words (cut past 120); one style; in-image text ALL CAPS + quotes, 1-3 words.
- **Strengths:** behavior-based light, concrete camera/lens, named aesthetics; `-quality` tier adds i2i (1-3 refs) and better non-English text.
- **Avoid:** negatives IGNORED (rephrase positive); keyword stacking; mixed styles; buried subject.
- **ComfyUI (partner node):** the Grok Image node exposes a `resolution` combo of **`1K` / `2K`** (confirmed from `comfy_api_nodes/nodes_grok.py`), plus an `aspect_ratio` combo.
- **Source:** docs.x.ai/docs/guides/image-generations.

### Reve
- **Prompt style:** natural-language, descriptive/conversational; high prompt adherence so be concrete and complete.
- **Avoid:** negative prompts NOT supported (single `prompt` param); no documented weighting syntax (don't rely on `(red:1.3)`).
- **Settings (API):** single `prompt`; aspect ratios 16:9/9:16/3:2(def)/2:3/4:3/3:4/1:1; 4K output (Reve 2.x); edit-image endpoint.
- **Source:** app.reve.com ; docs.aimlapi.com/api-references/image-models/reve. (Official prompt-engineering page is thin.)

### Kandinsky (3.x, Sber / FusionBrain)
- **Prompt style:** natural-language; built-in beautifier LLM expands plain prompts, so describe simply.
- **Structure:** subject + setting + style in natural language; select a `style` preset; pass excluded elements via the negative field.
- **Strengths:** built-in prompt enhancement, style presets, inpainting/i2i, fully open checkpoints.
- **Avoid:** over-long prompts. Negative prompts ARE supported (dedicated field).
- **Settings (FusionBrain API):** `query` + negative field, `style`, 1024x1024 default, sizes multiples of 64.
- **Source:** fusionbrain.ai/docs/en ; ai-forever.github.io/Kandinsky-3.
