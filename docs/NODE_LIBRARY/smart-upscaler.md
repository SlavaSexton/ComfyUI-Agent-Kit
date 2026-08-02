# Smart Upscaler (ComfyUI-Smart-Upscaler, our own pack)

**Eleven** menu nodes for tiled upscaling that writes a separate, verified prompt for **every tile**. Pack:
**`ComfyUI-Smart-Upscaler`**, author **Slava Sexton**, MIT, version **1.0.0**. Categories are
`Smart Upscaler/{Prompting, Tiling, Processing, Review, Routing}`.

**Status, stated honestly: not published yet.** There is no public repository or Registry entry as of
2026-08-01 (`gh search repos "ComfyUI-Smart-Upscaler"` returns nothing). Everything below is read from the
pack source and its shipped workflow, so the technique and the graph are usable knowledge now; the install
URL is the one thing that is still missing and this entry will carry it once the pack ships.

## The problem it solves, and why the existing tilers do not

Ultimate SD Upscale and Tiled Diffusion / MultiDiffusion (both already in `ADVANCED.md`) tile the
**sampling**. The prompt is not tiled: every tile receives the same text, or a captioner is asked to
describe each tile in isolation. Isolation is the failure. A crop of roof tiles captions as "brown
texture", a crop of lake as "blue gradient", the sampler renders the guess, and neighbouring tiles that
guessed differently disagree at the seam.

Smart Upscaler inverts the order: read the whole image **once**, build one shared understanding, then
derive a per-tile prompt from it before anything is redrawn. Three rules in the pack keep that honest, and
they are the actual content of the idea:

- **Large flat areas are found by measuring pixels, not by asking a model.** Water, sky and open ground
  are detected geometrically; the whole-image pass must then identify each measured area, or it is asked
  again about that exact spot.
- **Every tile showing the same surface gets the same wording**, so the seams cannot disagree.
- **A tile is never told about an object the whole-image pass placed elsewhere** unless the tile's own
  pixels confirm it. Corrections only ever **remove** unsupported claims; none invent content.

Every prompt is readable on the canvas and written to disk, which makes a bad tile diagnosable instead of
mysterious: read that tile's prompt and the cause is usually right there.

---

## The graph, in pipeline order

Types are read from `RETURN_TYPES` / `INPUT_TYPES` in `nodes/*.py`; the wiring is read from the shipped
`workflow/Smart-Upscaler-Z-Turbo-v1.json` (79 nodes, 84 links).

### 1. SmartUnifiedPromptGuidance  (display: "Prompt Director: Editable Master Instructions")
- **category:** `Smart Upscaler/Prompting` | the master control; everything else inherits from it.
- **inputs:** `instructions`, `user_request`, `known_false_detections`, `prompt_suffix`, `tile_detail`,
  `sampler_prompt_style`, `tile_colors`.
- **outputs:** `global_instruction` (`STRING`), **`prompt_system` (`SMART_PROMPT_SYSTEM`)**,
  `combined_instructions` (`STRING`).
- `SMART_PROMPT_SYSTEM` is the pack's own type and it is the spine of the graph: it carries the detail
  level and the prompt contract into **three** downstream nodes, so they cannot drift apart. Wire it to all
  three or the nodes fall back to their own defaults.
- **`sampler_prompt_style` is the setting people get wrong.** Edit models (Klein, Qwen Edit) need an edit
  command plus a tile description; denoise models (Z-Image Turbo, SDXL, Flux) need a plain description
  only. An instruction model treats appended context as context, a denoise model renders every noun you
  hand it, so the wrong style shows up as invented objects.
- Presets live in `presets/task_presets.json`; a named entry there appears in the dropdown automatically.

### 2. SmartUpscaledTilePlanner  (display: "Output-Scale Tiles: AI or Standard Resize")
- **category:** `Smart Upscaler/Tiling` | enlarges first, then plans the grid **in final output pixels**.
- **inputs:** `image` (`IMAGE`), `upscale_method`, `min_tile_size` (default 1024), `max_tile_size`
  (default 1536), `overlap` (32), `feather` (16), `scale_factor` (default 2.0, max 12.0), `divisible_by`
  (16), `upscale_batch_size`, plus padding / cache / limit controls.
- **outputs:** `upscaled_tiles` (`IMAGE`), `processing_preview` (`IMAGE`), `upscaled_image` (`IMAGE`),
  `blend_masks` (`MASK`), `tile_metadata_json` (`STRING`), `preflight_summary` (`STRING`).
- Tile sizes are **final sampler pixels**, not source pixels. `scale_factor` multiplies tile count
  quadratically: the node's own tooltip warns a 1340x896 source at 12x renders about 90 tiles.
- `tile_metadata_json` is carried by hand to two later nodes (the job director and the finalizer). It is
  the tile geometry; losing it breaks reassembly.

### 3. SmartCachedTextGenerate  (display: "Automatic Whole-Image Analysis + Cache")
- **category:** `Smart Upscaler/Prompting` | the read-the-whole-picture pass. Runs **once**.
- **inputs:** `clip` (`CLIP`, lazy), `image` (`IMAGE`), `prompt` (`STRING`), `max_length` (1024),
  `sampling_mode`, `thinking` (default off), `use_default_template` (default on), `cache_mode`
  (`read_write` / `refresh` / `bypass`), `cache_tag`; optional `key_context`, `prompt_system`,
  `analysis_max_side`.
- **outputs:** `prompt_text`, `cache_status`, `review_text` (all `STRING`).
- Wire `prompt` from the Director's `global_instruction` and `prompt_system` from its `prompt_system`.
- **`cache_tag` is a correctness control, not decoration.** Change it after changing the caption model or
  the caption contract, otherwise the cache serves captions written under the old contract and the change
  you just made appears to do nothing.
- Leave `thinking` off for a caption-only response; leave `use_default_template` on for Qwen3-VL and turn
  it off only for a replacement caption model that wants raw unformatted text.

### 4. SmartTileJobDirector  (display: "Tile Job Director: Exact Local Tiles")
- **category:** `Smart Upscaler/Prompting` | cuts the exact tiles and hands each one its context.
- **inputs:** `upscaled_tiles` (`IMAGE`), `tile_metadata_json` (`STRING`), `global_context` (`STRING`,
  lazy), `prompt_system`, `selection_mode` (`single_tile` / `all_tiles`), `tile_number`, `base_seed`,
  `seed_mode` (`increment` / `fixed` / `hashed`).
- **outputs:** `tile_images` (`IMAGE`), `tile_instructions` (`STRING`), `tile_references` (`STRING`),
  `tile_seeds` (`INT`), **`caption_images` (`IMAGE`)**.
- `global_context` takes `prompt_text` from the whole-image pass. `caption_images` is a **separate** image
  stream: the unpadded crop sent to the vision model, distinct from `tile_images` which goes to the
  sampler. Feeding the sampler stream to the captioner captions the padding.
- `seed_mode` decides whether tiles share a seed (`fixed`), walk (`increment`), or derive from tile
  identity (`hashed`).

### 5. SmartCachedTilePromptGenerator  (display: "Automatic Exact-Tile Prompt + Cache")
- **category:** `Smart Upscaler/Prompting` | one prompt per tile. The heart of the pack.
- **inputs:** `clip` (`CLIP`, lazy), `image` (`IMAGE`), `instruction` (`STRING`), `tile_reference`
  (`STRING`), `prompt_system` (`SMART_PROMPT_SYSTEM`), `caption_generation`, `cache_mode`, `cache_tag`,
  `negative_prompt_fallback` (default `changed geometry, duplicated objects, artifacts, seams`); optional
  `caption_max_side` (default 1344, the longest side of each real unpadded tile sent to the vision model).
- **outputs:** `positive_prompt`, `negative_prompt`, `prompt_audit`, `tile_reference`, `cache_status`
  (all `STRING`).
- Wire `image` from `caption_images`, `instruction` from `tile_instructions`, `tile_reference` from
  `tile_references`. **`prompt_audit` is the debugging output** and it is why a bad tile is diagnosable.

### 6. SmartSamplerTileSelector  (display: "Sampler Tile Test Selector (Optional)")
- **category:** `Smart Upscaler/Processing` | render ONE tile to try a setting instead of the whole grid.
- **inputs:** `tile_images`, `positive_prompts`, `negative_prompts`, `tile_references`, `tile_seeds`,
  `processing_mode`, `tile_number`. **outputs:** the same five, filtered.
- Drop it in front of the sampler while tuning; set `processing_mode` back to all tiles for production.
  This is the cheap iteration loop, and skipping it is how people burn an hour on a 90-tile run to learn
  one setting was wrong.

### 7. SmartModelEngineSwitch  (display: "Model Engine Switch (only selected runs)")
- **category:** `Smart Upscaler/Routing` | the isolated, replaceable image model block.
- **inputs:** `engine` (dropdown), `engine_1..N` (wildcard type, **lazy**), optional `engine_number`
  (`INT`, forceInput, for keeping several switches in sync; 0 or unconnected means use the dropdown).
- **output:** `selected`.
- **The lazy inputs are the whole point:** an unselected chain is never executed, so no model loads, no
  VRAM is taken and no time is spent. Build your model chain, terminate it in a KJNodes `Set_` node, wire
  a matching `Get_` into an `engine_` slot, and only the selected chain runs. This is what lets the pack
  ship a Z-Image Turbo chain while staying model-agnostic.

### 8. SmartTileColorMatch  (display: "Color Match to Original (Optional)")
- **category:** `Smart Upscaler/Processing`
- **inputs:** `generated_tile` (`IMAGE`), `source_tile` (`IMAGE`), `color_match_method`,
  `color_match_strength`, `color_preset`. **output:** `color_matched_tile` (`IMAGE`).
- Pulls each rendered tile back toward the source colours. The shipped workflow uses `rgb_mean_std` at
  strength 50. Related to the standing `KNOWN_ISSUES.md` row on VAE round-trip colour drift, but applied
  per tile rather than per pass.

### 9. SmartTileFinalizer  (display: "Finish and Blend Tiles")
- **category:** `Smart Upscaler/Processing` | stitches everything back into one picture.
- **inputs:** `processed_images`, `tile_references`, `source_tiles`, `tile_metadata_json`, `blend_masks`,
  `reference_mode`, `structure_preservation`, `detail_support`, `fallback_method`,
  `cross_tile_consistency`, `consistency_mode`, `finish_preset`.
- **outputs:** `corrected_tiles` (`IMAGE`), `final_image` (`IMAGE`).
- Needs **both** the `blend_masks` and the `tile_metadata_json` from the planner, plus the original
  `source_tiles`, not only the rendered ones. Shipped values: `Stay close to the original photo`,
  structure 35, `Balanced`, `bilinear`, consistency 35, `Even shift per tile`, `Faithful photo upscale`.

### 10. SmartTileInspector  (display: "Smart Tile Prompt Inspector")
- **category:** `Smart Upscaler/Review` | **no outputs**, a canvas UI node (`web/smart_tile_inspector.js`).
- **inputs:** `source_images`, `generated_images`, `prompts`, `tile_references` (all forceInput).
- Click a tile, read the prompt it was rendered from.

### 11. SmartTilePromptAuditLog  (display: "All Prompts Viewer + Log")
- **category:** `Smart Upscaler/Review`
- **inputs:** `tile_instructions`, `positive_prompts`, `negative_prompts`, `prompt_audits`,
  `tile_references`, `cache_status`, `prompt_system`, `global_instruction`, `global_context`,
  `combined_instructions`, `log_label`.
- **outputs:** `all_prompt_text`, `json_log_path`, `readable_log_path` (all `STRING`).
- Every prompt on screen and on disk. The JSON log is the artifact to diff between runs when a change
  should have altered the prompts and apparently did not (usually a stale `cache_tag`).

**Internal engines are deliberately not menu nodes:** `SmartPromptGuidance`, `SmartTilePromptResolver`,
`SmartTileSeed`, `SmartTileBlender`, `SmartTilePlanner` / `SmartAdaptiveTilePlanner`,
`SmartTileFidelityColorMatch`, `SmartTileMergePartialBatch`. They stay importable from their modules. Do
not wire them by hand; they are implementation, and `nodes/__init__.py` registers only the eleven above.

---

## The shipped reference workflow

`workflow/Smart-Upscaler-Z-Turbo-v1.json`, laid out as six numbered boxes left to right, each with a note.
Values below are read from the file.

- **Vision side:** `CLIPLoader` -> `qwen3vl_4b_fp8_scaled.safetensors`, **type `krea2`**. Qwen3-VL-4B-FP8
  does all the prompt writing and finishes **before** the image model loads, so only one large model is in
  memory at a time. That is the 16 GB VRAM claim's mechanism.
- **Image side:** `UNETLoader` -> `z_image_turbo_int8_convrot.safetensors`; `CLIPLoader` ->
  `qwen_3_4b.safetensors`, **type `lumina2`**; `VAELoader` -> `ae.safetensors`; `ModelSamplingAuraFlow`
  shift 1.5; `KSampler` **8 steps, CFG 1.3, euler / beta, denoise 0.6**.
- **Tile ControlNet:** `ModelPatchLoader` -> `Z-Image-Turbo-Fun-Controlnet-Tile-2.1-lite-2601-8steps.safetensors`,
  applied through **`QwenImageDiffsynthControlnet`** at strength 0.6.
- **Optional AI resize:** `UpscaleModelLoader` -> `4x_UniversalUpscalerV2-Sharp_101000_G.pth`.
- **Planner as shipped:** Lanczos, tiles 1024 to 1536, overlap 32, feather 16, **scale_factor 4**,
  divisible_by 64.
- **Companion packs required:** **ComfyUI-KJNodes** (the `Set_` / `Get_` wires the engine switch depends
  on) and **rgthree-comfy** (the before/after `Image Comparer`). Models total about 13 GB.

**Worth knowing about that ControlNet node.** Applying a **Z-Image** Fun tile ControlNet through the
**Qwen**-named node looks wrong and is not: in core `comfy_extras/nodes_model_patch.py`,
`class ZImageFunControlnet(QwenImageDiffsynthControlnet)` subclasses it and inherits the same
`diffsynth_controlnet` implementation. The only differences are the input arrangement (the Z-Image variant
makes `image` optional and adds `inpaint_image`) and the menu category (`model/patch/z-image` versus
`model/patch/qwen`). Both reach identical code, so the shipped graph is correct; `ZImageFunControlnet` is
simply the better-labelled entry point. Confirmed by reading the class definitions on master, 2026-08-01.

---

## Where it sits against what the kit already documents

Add it to the tiling ladder in `ADVANCED.md` as the **prompt-aware** option, not as another sampler-tiler:

| Approach | Tiles the sampling | Tiles the prompt | When |
|---|---|---|---|
| Ultimate SD Upscale | yes | no | fastest path, uniform subject |
| Tiled Diffusion / MultiDiffusion | yes | no | seam control via overlap, MultiDiffusion part is CC-BY-NC-SA |
| Steudio Divide and Conquer | yes | no | automatic tile sizing rather than hand-set tiles |
| **Smart Upscaler** | yes | **yes, per tile, from a whole-image read** | busy or mixed scenes where a per-tile guess goes wrong, and when you need to see WHY a tile failed |

It is heavier than all three: a full vision pass over the image plus one caption per tile before any
sampling starts. On a uniform subject that cost buys little. It pays on mixed scenes, which is exactly
where the other three produce their confidently wrong tiles.

## Anti-patterns

- **Wiring `tile_images` into the caption generator instead of `caption_images`.** The two streams exist
  for different consumers; the caption stream is the unpadded crop.
- **Changing the caption model or the prompt contract without bumping `cache_tag`.** The cache then serves
  captions written under the old contract, and the change looks inert.
- **Using a denoise `sampler_prompt_style` on an edit model, or the reverse.** Denoise models render every
  noun handed to them, so an edit-shaped prompt grows objects that were never in the picture.
- **Running the full grid while tuning.** That is what `SmartSamplerTileSelector` is for.
- **Wiring the internal engines by hand.** They are not menu nodes for a reason.

## Confirmed vs inferred

- **Confirmed** by reading the pack source on 2026-08-01: all eleven class names and display names
  (`nodes/__init__.py`), every category and `RETURN_TYPES` / `RETURN_NAMES` (AST scan of `nodes/*.py`),
  the input names and defaults quoted above (`INPUT_TYPES`), MIT and version 1.0.0 (`LICENSE`,
  `pyproject.toml`), and every model file, widget value and node census in the shipped workflow JSON.
- **Confirmed** against ComfyUI master: the `ZImageFunControlnet` / `QwenImageDiffsynthControlnet`
  inheritance.
- **Inferred, not measured:** the 16 GB VRAM figure and the quality claim against the other tilers come
  from the pack's own README. **Nothing here was executed** - no run, no benchmark, no A/B against
  Ultimate SD Upscale. Treat the comparison table as a design difference, which it is, and not as a
  measured result, which it is not.
- **Unresolved:** no public repository or Registry entry exists yet, so there is no install URL and no
  community evidence.
