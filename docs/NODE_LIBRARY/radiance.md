# Radiance (fxtdstudios) - reverse-engineered reference

**`fxtdstudios/radiance`** - a professional 32-bit float color-science / HDR / VFX suite for ComfyUI. GPL-3.0, on
the Comfy Registry (PublisherId `fxtdstudios`), docs at radiance.fxtd.org. Two lines: **v2.3.3** (shipped, 78
display-mapped nodes) and **radiance-beta = "radiance3" v3.1.x** (258 py files, an engine + a rewrite). This is
the strongest public reference in OUR domain (the ComfyUI-OCIO pack: OCIO Read/Write + 6 color nodes), and it is
bigger than ours - so it is the pack to learn node-building, color-science, and viewer design from.

**Status: reverse-engineered by READING the source** (both repos cloned + read; every claim below is from the
code, NOT from running it live). GPL-3.0 - learn the technique, do NOT copy code verbatim into our MIT packs.
Where radiance is wrong or approximate, it is flagged; our OCIO-native curves are more correct than several of
theirs by construction.

## What it is + how it is built

- **Language / API:** Python, classic ComfyUI **V1 node API** (`@classmethod INPUT_TYPES` / `RETURN_TYPES` /
  `FUNCTION` / `CATEGORY`) - same API as our OCIO pack. Frontend is raw **WebGL2 + DOM** (no React), bundled with
  **esbuild** (v3); the shipped source is un-minified `js/*.js`, the build is optional.
- **Deps:** numpy + **torch (GPU)**, opencv-python, **OpenEXR + Imath**, opencolorio, imageio-ffmpeg, transformers
  (Depth Anything V2), scipy, defusedxml. NOTE: `colour-science` is a declared dependency but **imported nowhere**
  in v2.3.3 - dead weight (do not assume they use it).
- **Color engine = TWO parallel engines** that do not share a path: (1) a huge **hand-rolled numpy + torch** set
  of curves + gamut matrices (the bulk), each curve written TWICE (a numpy CPU version and a `tensor_*` GPU
  version, so video has no host round-trip); (2) an **OpenColorIO** engine (opt-in, degrades to pass-through if
  `PyOpenColorIO` is absent) for space->space, display/view, and the WebGL viewer's 3D-LUT bake. They bundle a
  real **ACES 2.0 CG config** (`ACES/config.ocio`, cg-config-v4.0.0_aces-v2.0_ocio-v2.5, 678 lines).
- **House style (`CODE_STYLE.md`):** PascalCase `Radiance`-prefixed classes, `◎` prefix on every display name,
  `CATEGORY = "FXTD Studios/Radiance/<Zone>"`, snake_case `verb_noun` utils, SCREAMING_SNAKE constants, type hints
  on interface functions. Mature engineering: CONTRIBUTING, a CI matrix (py3.9-3.12), a tag-triggered publish
  action, a hand-rolled static-site docs generator.

## Color science engine (the part worth knowing cold)

Confirmed in `color_utils.py` + `hdr/color.py` (both read):
- **Log curves (numpy + GPU torch, both):** LogC3 (with a FULL ARRI **Exposure-Index table**, 14 EIs 160-3200 -
  each EI has its own `(cut,a,b,c,d,e,f)`), LogC4, S-Log3, V-Log, Canon Log 3, RED Log3G10, ACEScct, DaVinci
  Intermediate. Plus HDR transfer **PQ (ST.2084)** and **HLG (ARIB B67)**. NO Cineon, NO ACEScc (only ACEScct).
- **Gamut matrices (hardcoded 3x3 float32 -> ACEScg):** ARRI AWG3 / AWG4, Sony S-Gamut3.Cine, Panasonic V-Gamut,
  Canon Cinema, REDWideGamut, DaVinci Wide, + ACES AP0<->AP1, ACEScg<->{sRGB, Rec.2020, P3-D65}. `hdr/color.py`
  can also DERIVE a matrix from xy primaries + white point with Bradford adaptation on the GPU.
- **Float32 hygiene (their headline):** everything stays float32, GPU-first; **no 8-bit clamp anywhere** in the
  processing path; every node has `clamp_output` defaulting to **False** ("scene-linear data has valid negatives");
  a **sign-preserving** sRGB EOTF (abs/sign so values > 1.0 survive - fixes an old `clamp(min=0)` that destroyed
  HDR highlights); NaN/Inf clamped to **65504** (max half-float) before an EXR-HALF write.
- **HONESTLY FLAWED (do not copy):** their **LogC4 is a fitted approximation** (self-labeled "Approximate
  implementation fitted to spec", `A=4296.65,D=11.593`) - NOT the exact ARRI LogC4 spec. Their `aces_*_tonemap`
  are approximations ("NOT the ACES 2.0 RRT" - true RRT only via the OCIO path). And DaVinci Intermediate is
  implemented TWICE with different math (`color_utils.py` log10 vs `hdr/color.py` log2) - a real pre-existing
  inconsistency. Their curve code carries documented BUG-fix histories (operator precedence, wrong `cut_encoded`
  thresholds) - the exact traps a log-curve node must avoid (the decode threshold must be `encode(cut)`, not a
  guessed constant).
- **OCIO usage:** processors are cached in a **thread-safe bounded LRU** (`_BoundedCache`, OrderedDict + RLock,
  8 configs / 128 processors, keyed by display|view|look|context) - the single biggest speedup for sequences,
  since `getProcessor()` costs ~200-500 ms. Config resolution: `$OCIO` -> active -> bundled `ACES/config.ocio`
  -> models dir -> `OCIO.Config.CreateBuiltinConfig("aces_cg")` -> auto-download v4.0.0.
- **EXR I/O:** a robust **cascade** - cv2 first, then real **OpenEXR + Imath** (this is what buys named
  multi-layer channels, metadata attrs, and guaranteed HALF-vs-FLOAT), then a pure-Python `SimpleEXRWriter`, then
  imageio. Reader is OpenEXR + Imath and is genuinely multi-channel (RGB + Y + A + Z/Depth).

## Node catalog (78 nodes, 11 production zones)

Mirrors industry VFX-software topology. Standouts per zone (all display names carry `◎`):
- **Project / Metadata / DNA:** Workspace (project/shot/version hub, saves `.rad` v2 SHA256 containers), Manager
  (cinematic prompt from real ARRI/RED/Sony camera+lens profiles), DNA Reader/Writer/Validator (sign + QC-gate
  images with cinematic metadata).
- **Production I/O + Loaders:** Read (universal cinema reader: video / EXR seq / audio, returns IMAGE+MASK+frame
  ints+fps+AUDIO+meta), Write (12+ formats incl. ProRes / H.265 10-bit / EXR, muxes audio), Save EXR / Save HDR /
  Save 16-bit PNG, **Unified Loader** (auto-detect Flux/SD3/SDXL/Wan/LTX-2.3/Hunyuan/PixArt, LRU cache with
  **mtime+size** fingerprint), LoRA Stack (chainable `LORA_STACK`), Control (ControlNet, Union, None-bypass),
  Cinematic Encoder (arch-aware prompt, real token count).
- **Color / Grade:** Grade (per-channel Lift/Gamma/Gain/Offset + LAB match + JSON export), Apply Grade Info
  (replay a saved grade), **Grade Match** (CIE L*a*b* mean/std shot-to-shot), Log Curve Decode/Encode, OCIO Color
  Transform, OCIO Display/View, CDL Transform (`.cc/.ccc`), Color Matrix, LUT Apply/Blend (trilinear +
  **tetrahedral**, HDR-unclamped), **Nuke Bridge** (stream EXR over TCP into a live Nuke Read).
- **HDR:** Image-To-Float32, Float32 Color Correct (pivots contrast at **0.18** mid-gray, colorspace-aware luma
  weights), Expand Dynamic Range (SDR->HDR), HDR Tone Map (filmic/AgX/Reinhard), HDR Histogram, Exposure Blend
  (bracket merge), **360 Panorama Generate** (equirect HDRI), VAE 4K Encode/Decode/Roundtrip (tiled, 12
  colorspaces), + DaVinci Wide Gamut / ARRI Wide Gamut 4 / ACES 2.0 Output Transform / Shadow-Highlight Recovery.
- **Film:** Film Grain (20+ real stocks: Vision3 / Eterna / CineStill, halation, gate weave), White Balance
  (Kelvin), Depth of Field (T-stop + bokeh from z-depth), Motion Blur, Rolling Shutter, Compression Artifacts.
- **Scopes / QC:** Waveform, Vectorscope (+ skin-tone line), False Color (7-zone IRE), QC Pro (banding/focus/noise
  checks + report), Export QC Report (json/csv/html).
- **Temporal:** Temporal Smooth (motion-aware per-pixel EMA deflicker), Flicker Analyze.
- **Sampler:** Sampler Pro (multi-stage: AYS, PAG, dynamic guidance, tiled inpaint, Wan/LTX/Hunyuan video).
- **Depth / Denoise:** Depth Map (Depth Anything V2, per-frame standardized anti-flicker), 32-bit Denoise
  (HDR-aware bilateral).
- **Mask / Overlay:** Load Image (non-destructive `_radmask.png` sidecar + JS brush editor), Metadata Overlay
  (burn-in slate), Blend Composite (scene-linear, 8 modes, HDR-safe).
- **Viewer / Layout / Upscale:** the **Radiance Viewer** (see below), Reroute/Mux/Gate/Note/Debug-Probe (wildcard
  `"*"` type), Resolution calculator, Pro Upscale / AI Upscale / Bit-Depth Convert / Sharpen-32bit.

## Frontend / Viewer (the design to learn)

- **Real 32-bit WebGL2 viewer.** `radiance_webgl.js` (~4.8k lines) uses `getContext('webgl2')` + **`RGBA32F` /
  `gl.FLOAT`** textures + FBOs (gated on `EXT_color_buffer_float`, with an f32->f16->u8 fallback ladder). The full
  view pipeline runs IN-SHADER: lens distortion -> DoF -> denoise (7x7 bilateral) -> linearize -> input LUT (IDT)
  -> **exposure `pow(2.0, u_exposure)`** -> white balance -> grade (Linear OR ACEScct) -> contrast -> log wheels
  -> shadows/highlights -> tonemap/ODT (Hable / Reinhard / **ACES Narkowicz**) -> sRGB OETF, plus manufacturer
  camera-log encodes (LogC3/4, F-Log2, C-Log3, ...) with cited constants.
- **Mounting:** `app.registerExtension({beforeRegisterNodeDef})` -> `onNodeCreated` mounts a `<div>` via
  **`node.addDOMWidget("viewer", ..., {serialize:false})`** and instantiates a per-node JS class; frames arrive
  through the standard **`onExecuted(message)`** (`message.radiance_images`), live progress via
  `api.addEventListener`. The node is `OUTPUT_NODE=True`, `RETURN_TYPES=()`, returns `{"ui":{"radiance_images":...}}`.
- **HDR frame transport:** a custom binary sidecar - 12-byte header + zlib-compressed IEEE-754 float32/16
  (`.rhdr`) - so the browser gets true HDR pixels, not an 8-bit thumbnail.
- **Terminal HUD + Python REPL:** a Nuke-style command line; non-builtin lines POST to a custom aiohttp route
  **`@PromptServer.instance.routes.post('/radiance/terminal')`** that `exec()`s into a persistent namespace on a
  30 s timeout - **gated behind `RADIANCE_ENABLE_TERMINAL=1`** (it is a real code-execution surface; the env gate
  is the right call). Other routes: `/radiance/deliver`, `/radiance/progress`, `/radiance/ocio/*`.
- **Scopes** render on an HDR-float scope FBO (waveform/vectorscope accumulate in float) + a 2D histogram canvas.
- **Non-destructive mask editor** (`radiance_mask_editor.js`): brush / eraser / polygon / magic-wand, soft brush
  via radial gradient, full undo/redo, writes a `_radmask.png` companion.
- **Client-side 32-bit EXR export:** `readPixels(gl.FLOAT)` -> a pure-JS OpenEXR FLOAT encoder -> download. Lets
  the user preview a view transform and export the graded float EXR with no server round-trip.

## radiance3 (beta) - the architecture rewrite

258 py files vs v2's 51. What v3 adds (for node-building lessons):
- **`core/` engine:** `errors.py` (a `RadianceError` hierarchy + `@handle_node_errors` decorator mapping
  MemoryError->GPUError etc.), `tensor/` (float32 helpers `ensure_4d/5d` for image<->video reshape - NOT a custom
  type; "HDR-ness" lives in the pipeline, not a wrapper), `system/` (traversal-safe `safe_join`; **secrets stored
  as an env-var NAME, not the value**, so workflow JSON never leaks a key), themed logging, SQLite param-history.
- **Declarative node registry** (v2 was a hardcoded import list): `nodes/catalog.py` (11 groups + **feature
  flags** - training gated behind `RADIANCE_DEV`), `nodes/registry.py` (per-group failure isolation +
  duplicate-key detection), and runtime **Gizmos** (user-collapsed node groups saved as reusable nodes).
- **`config/model_map.py` = a single-source-of-truth table for ~19 architectures** (flux/flux2/klein/chroma/
  zimage/qwen/ltx-video/wan/hunyuan/sd3/sdxl/...): per-arch `latent_channels`, scale/shift, `log_curve`,
  compression, VAE spatial/temporal factors, text-embed dims. `model/detect.py` **auto-detects architecture from
  safetensors header keys** (ordered heuristics: Chroma before Flux by `distilled_guidance_layer`; Z-Image vs
  Lumina2 by `cap_embedder` dim) + a VRAM estimator.
- **New capability:** in-pack LoRA training (turbo-decoder + HDR-LoRA + a 9-stage stochastic **SDR-degradation**
  pipeline to synth training pairs), **RUDRA fast_vae** (a TAESD-style distilled latent->scene-linear decoder,
  weights shipped separately on HF `fxtdstudios/RUDRA`), a server-side **`/radiance/deliver`** finishing endpoint
  (grade -> FX bake -> AI upscale -> QC -> encode -> `.amf`/`.cdl`/`_meta.json` sidecars), nodes/video (t2v, dit),
  nodes/ai (scene-cut, auto-grade, CLIP-match, an LLM driver).
- **Honest tech debt (KNOWN_ISSUES.md):** the reorg left ~40 legacy root `nodes_*.py` as re-export SHIMS beside
  the organized `nodes/` tree -> ~39 duplicate keys + aiohttp double-registration, guarded but flagged, with a
  RESTRUCTURE_PLAN toward a v4 `lib/`+`nodes/`+`web/` layout. Lesson: a flat->packaged reorg needs a shim
  retirement plan, not just shims.

## Example workflows they ship

v2 `workflows/` are `.rad` v2 binary containers (magic `RAD!` + a JSON header + a zlib-compressed graph + SHA256 -
their proprietary format, NOT droppable into our library): **FLUX 8k Upscale, FLUX Krea 32-HDRI, LTX T2I, Video
Depth Generator, Video Upscale, WAN 2.2**. v3 ships a plain `start.json` chaining ProjectManager -> Unified Loader
-> Cinematic Prompt Encoder -> Resolution -> Sampler Pro -> HDR VAE Decode -> Depth Map -> Viewer - a clean
reference for how their nodes wire into a full 32-bit pipeline.

## What this makes better in OUR work

**For ComfyUI-OCIO** (our pack), ranked steal-list (technique only, our OCIO-native curves are already more
correct than their approximations):
1. **Thread-safe bounded-LRU processor + config cache** (biggest win - we rebuild `getProcessor()` per frame).
2. **Real 32-bit WebGL2 viewer** with in-shader exposure + the OCIO display/view baked to a 3D-LUT texture -
   replaces our first-frame preview; add HDR waveform/histogram scopes and client-side float-EXR export.
3. **OpenEXR + Imath writer** for metadata + named multi-layer channels + guaranteed HALF/FLOAT (we already do
   cv2 EXR compression as of v1.0.1, so that part is done; OpenEXR adds the rest).
4. **Custom `PromptServer` routes** (`/ocio/config`, `/ocio/displays`) so the JS populates display/view/colorspace
   dropdowns from the ACTUAL loaded `.ocio` config, not a static list.
5. `clamp_output=False` default + sign-preserving EOTF + NaN->65504 guard before EXR-HALF.
6. **LogC3 EI table** (we are EI800-only; their 160-3200 constants are exact) and **LogC4 done EXACTLY** (better
   than their fitted approx) - both already on the OCIO worklist.
7. Bundle/discover an ACES config with `CreateBuiltinConfig("aces_cg")` fallback (removes "no config found").

**For node-building in general** (see BUILDING_NODES.md "Lessons from radiance"): `node.addDOMWidget` + a per-node
JS class; `PromptServer` aiohttp routes for config introspection; a declarative node registry with feature flags;
env-var-NAME secret storage; traversal-safe paths + `weights_only=True`; a model-arch SSOT table + safetensors
header auto-detect; float32-no-clamp hygiene; the log-curve `cut_encoded = encode(cut)` correctness rule.

**Source:** github.com/fxtdstudios/radiance (v2.3.3) ; github.com/fxtdstudios/radiance-beta (radiance3) ;
radiance.fxtd.org ; registry.comfy.org/nodes/radiance. Reverse-engineered from source 2026-07-01; GPL-3.0 (learn,
do not copy code verbatim).
