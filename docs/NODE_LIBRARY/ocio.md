# OCIO color management (ComfyUI-OCIO, our own pack)

**Nine** OpenColorIO nodes we build and maintain, modelled 1:1 on The Foundry Nuke's node set. Pack:
**`ComfyUI-OCIO`**, author **Slava Sexton** (https://github.com/SlavaSexton/ComfyUI-OCIO), MIT, **released v1.2.0
2026-07-06** (v1.0.0 was 2026-06-30). Category `OCIO`. Built to fill a real gap: the ComfyUI registry had no OCIO
pack (`search_custom_nodes "OCIO"` / `"OpenColorIO"` both return nothing).

**New in v1.2.0 - native ComfyUI VIDEO pipeline + an on-node viewer.**
- **All nine nodes are on the native VIDEO wire.** Each of the six color nodes (ColorSpace, LogConvert, Display,
  CDLTransform, FileTransform, LookTransform) plus Write and Player carries a **mutually-exclusive IMAGE-or-VIDEO
  input pair**: connect one and the other auto-disconnects, and the socket matching the live input carries the
  data (VIDEO in -> VIDEO out, IMAGE in -> IMAGE out). VIDEO uses ComfyUI's native `comfy_api`
  `VideoFromComponents` - the SAME type Load Video emits - so the nodes drop straight into a native video graph
  (`Load Video -> OCIO color node -> Video Combine / Save Video`) and interop with Load / Save Video, Video
  Combine, Get Video Components, VHS. Slot labels read `OCIO Img/Seq/Vid` (image) and `ComfyUI Video` (video).
- **OCIO Player (the 9th node)** - an on-node WebGL viewport: exposure + the OCIO display transform run in the
  fragment shader on the real HALF-float values (a 3D LUT baked server-side from `getProcessor`), with a
  **scene-linear HDR log shaper** so highlights above 1.0 do NOT clip flat in the display LUT.
- **LogConvert curves now carry readable labels** ("Sony S-Log3", "ARRI LogC3", "Linear to Log", ...).
- **Bit-exact accuracy, measured:** worst max-abs error **0.000e+00** across 9 transforms x 4 fixtures (OCIO
  parity), plus a full color-accuracy suite (`tools/accuracy`) and charts (`docs/assets/accuracy/`, incl. a 3D
  gamut-volume chart of sRGB / ACEScg / ACES2065-1 / ARRI Wide Gamut 3 in CIE Lab).
- **Since v1.0.1** (still current): OCIO Write can write LTX-2 HDR straight to an **ACEScg EXR sequence** -
  automatically (`auto_colorspace` from LTX's HDR decode) or by hand (the `logc3` ARRI LogC3 curve on
  OCIOLogConvert); **colorspace in the file name** (`name_acescg.0086.exr`, `colorspace_in_name`); Nuke-Write-style
  **EXR compression** (`compression`: zip / zips / piz / pxr24 / dwaa / dwab / rle / none). `pyproject.toml` is now
  correctly `1.2.0` (the earlier v1.0.1 version-string lag is fixed). Full node I/O for Player / the video sockets:
  the pack README + `io_nodes.py` / `nodes.py` at tag `v1.2.0`.

**The two that make it a pipeline:** **OCIO Read** and **OCIO Write** - load a still / image sequence / video
off disk, color-manage it, and write it back out in EXR / TIFF / PNG / JPEG or ProRes / DNxHR / h264 / hevc. The
other six are the color operators. Every node uses standard ComfyUI types (`IMAGE` / `MASK` / `FLOAT` /
`STRING`), so they interoperate with the whole ecosystem: pipe **OCIO Read** into any node, and any node into
**OCIO Write** (confirmed: OCIO Read -> core `ImageScaleBy` -> core `SaveImage` runs; core `LoadImage` -> OCIO
Write runs).

**Install:** `git clone https://github.com/SlavaSexton/ComfyUI-OCIO` into `custom_nodes`, then
`pip install -r ComfyUI-OCIO/requirements.txt` (`opencolorio`, `opencv-python-headless`, `tifffile`, `Pillow`,
`numpy`). `OCIOLogConvert` is the one node that is dependency-free (no OCIO needed).

**Two environment notes that bite:**
- **EXR:** OpenCV reads/writes EXR only with `OPENCV_IO_ENABLE_OPENEXR=1` set in the environment **before**
  ComfyUI starts (set it in the launcher). Without it, EXR read/write fails.
- **Video:** OCIO Read / Write shell out to **ffmpeg** (the codec engine for ProRes / DNxHR / h264 / hevc); it
  must be a full ffmpeg on `PATH`. Stills and sequences need no ffmpeg. Missing ffmpeg -> a clear "install
  ffmpeg" error, stills still work.

**Color model.** ComfyUI has no color management: it holds images as plain gamma-encoded **sRGB** in `0..1`
(LoadImage does `x/255`, no linearisation). This pack adds the pipeline. Working space = **`sRGB - Display`**;
OCIO Read converts files *into* it, OCIO Write converts *out* of it. Defaults follow the file type: **EXR ->
ACEScg** (scene-linear render space), **JPEG / PNG / TIFF -> sRGB - Display**. Colorspace names come from the
active config (built-in ACES **studio-config**, ~55 spaces incl. ARRI / RED / Sony camera spaces); drop a `.ocio`
in the input folder for a custom config.

**I/O status:** confirmed from the shipped pack source (we wrote it), verified at runtime via the ComfyUI
`/prompt` API against OpenColorIO 2.5.2 + the built-in ACES studio config. Read/Write exercised on a real
12-frame EXR sequence -> jpg (all 12 written), a ProRes clip round-trip (8 frames, fps preserved), missing-frame
fill (black / hold / error), alpha round-trip (RGBA 4-channel preserved), and the full example workflow
(all 8 nodes) end-to-end. **v1.0.1 additions** (`auto_colorspace`, `colorspace_in_name`, `compression`, the
`logc3` curve) re-confirmed from the shipped source this pass (io_nodes.py:599-604, nodes.py:245/261); the LTX
HDR -> ACEScg path + LogC3 round-trip were runtime-verified when v1.0.1 shipped (live `/prompt`:
`LTXVHDRDecodePostprocess` -> OCIO Write, HDR peak preserved; EXR compression across all 8 options; LogC3
round-trip max error ~5e-5).

---

## The IO pair

### OCIO Read  (display: "OCIO Read")
- **pack:** `ComfyUI-OCIO` | **category:** `OCIO` | **outputs:** `image/video` (IMAGE batch), `alpha` (MASK), `fps` (FLOAT), `info` (STRING)
- **purpose:** load a still / image sequence / video off disk and color-manage it on the way in (Nuke: Read).
- **inputs (widgets, no IMAGE input - it reads from disk):**
  - `source` (STRING) - a path to a file, a sequence **folder**, a frame **pattern** (`shot.####.exr`), or a video, ANYWHERE on disk (absolute like `D:\shots\shot.v01`, or relative to the ComfyUI input folder). A **browse-source** button (disk file/folder picker) and an **upload** button are added by the pack's JS.
  - `frame_mode` (combo `auto`/`single`/`sequence`) - auto: a numbered file with siblings loads the whole sequence (Nuke "grab sequence"); single: just that file; sequence: force-collapse siblings. A folder is always a sequence; a video is always its full clip.
  - `input_colorspace` (combo) - the colorspace the FILE is in (auto-suggested: EXR -> ACEScg, else sRGB - Display).
  - `output_colorspace` (combo) - the working space the IMAGE comes out in (default `sRGB - Display`).
  - `raw_data` (BOOLEAN) - skip the conversion, pass file values through untouched (Nuke Raw Data).
  - `start_frame` / `end_frame` (INT) - the frame-NUMBER range to load (auto-filled to the detected range; frames outside it are filled by `edge_mode`).
  - `frame_shift` (INT) - re-base: the number the FIRST frame becomes downstream (e.g. a 1001-start sequence -> 1). Flows to OCIO Write.
  - `missing_frames` (combo `black`/`hold`/`error`) - fill a gap inside the sequence: black frame / hold the previous / stop. Missing frames are auto-detected and listed on the node + in `info`.
  - `edge_mode` (combo `hold`/`loop`/`bounce`/`black`) - Nuke before/after: frames requested outside the original range.
  - `fps` (FLOAT) - taken from video metadata (24 for stills); flows to OCIO Write.
- **how it works:** detects single vs sequence, assembles a contiguous batch (fills missing/edge frames), reads via cv2 (EXR/DPX), tifffile (TIFF), PIL (PNG/JPG) or ffmpeg (video), splits RGB + alpha, then `config.getProcessor(input, output)` per frame unless `raw_data`.
- **anti-patterns:** the source combo is a STRING (any path) BY DESIGN - a real sequence lives at an absolute disk path, not the input folder; do not expect an input-folder dropdown. Setting `output_colorspace` to a linear space (e.g. ACEScg) can emit values > 1, which stock ComfyUI nodes clip - keep the default `sRGB - Display` for downstream stock nodes.
- **placement:** the start of a graph, in place of `LoadImage`, when you need a sequence / video / color-managed load.

### OCIO Write  (display: "OCIO Write")
- **pack:** `ComfyUI-OCIO` | **category:** `OCIO` | **OUTPUT_NODE** | **output:** `path` (STRING)
- **purpose:** color-manage an IMAGE batch and write it to disk (Nuke: Write).
- **inputs:**
  - `images` (IMAGE) - the frame batch. `alpha` (MASK, optional) - wire OCIO Read's alpha (or any MASK) to write RGBA. `fps` (FLOAT, optional) - wire OCIO Read's fps.
  - `from_colorspace` (combo) - the working space of the incoming image (default `sRGB - Display`).
  - `output_colorspace` (combo) - the file's colorspace. Format picks the default (EXR -> ACEScg, PNG/TIFF/JPEG -> sRGB); stamped into the file metadata where the format allows.
  - `container` (combo `still image`/`sequence`/`video`).
  - `still_format` (combo `exr`/`tiff`/`png`/`jpeg`) - for still/sequence. `video_codec` (combo `prores_4444`/`prores_422hq`/`prores_422`/`dnxhr_hq`/`h264`/`hevc`) - for video. The pack's JS shows only the relevant one per container.
  - `bit_depth` (combo) - narrows to the format: JPEG 8; PNG 8/16; TIFF 8/16/32f; EXR 16f/32f.
  - `auto_range` (BOOLEAN) - pull `first_frame`/`last_frame`/`start_number`/`fps` automatically from the OCIO Read at the far end of the wire (through any number of nodes). Editing them by hand turns it off.
  - `first_frame`/`last_frame` (INT) - which frames to write. `start_number` (INT) - the number on the first output file. `source_start` (INT, hidden, set by the wire) - maps frame numbers to batch indices.
  - `raw_data` (BOOLEAN) - write as-is, no conversion. `output_folder` (STRING, browse button) + `filename` (STRING).
  - `colorspace_in_name` (BOOLEAN, default ON, **v1.0.1**) - put the output colorspace in the file name, BEFORE the frame number: `name_acescg.0086.exr`. Uses a short sanitized tag of `output_colorspace` (e.g. `acescg`, `rec709`, `srgb`, `logc`), or `raw` when Raw Data is on. Off -> plain `name.0086.exr`.
  - `auto_colorspace` (BOOLEAN, default ON, **v1.0.1**, front-end only) - when the input is wired from LTX's `LTXVHDRDecodePostprocess` (their SDR->HDR decode), auto-sets `from_colorspace = "Linear Rec.709 (sRGB)"` and `output_colorspace = "ACEScg"` for you. Editing either colorspace by hand still wins.
  - `compression` (combo, default `zip`, **v1.0.1**, EXR only) - Nuke-Write-style EXR compression: `zip` / `zips` = lossless (default), `piz` = lossless and good for grain, `dwaa` / `dwab` = smaller but lossy, plus `pxr24` / `rle` / `none`.
- **how it works:** converts from->out (unless raw_data), then writes: EXR via cv2 (half/float, RGBA, chosen `compression`), TIFF via tifffile, PNG/JPEG via cv2/PIL, video via ffmpeg (rgb48le pipe -> the codec). Returns a preview of the first written frame (a wrong colorspace pick looks visibly wrong) + "wrote N frames". A Render button queues the graph.
- **naming:** with `colorspace_in_name` ON (default) the colorspace tag sits before the number - still `<name>_<cs>.<ext>`; sequence `<name>_<cs>.0086.<ext>, <name>_<cs>.0087.<ext>, ...`; video `<name>_<cs>.mov` / `.mp4`. OFF -> `<name>.<ext>` / `<name>.0086.<ext>` / `<name>.mov`.
- **anti-patterns:** EXR needs the OPENCV env var (above); video needs ffmpeg; JPEG ignores alpha. It writes to the SERVER disk, not the browser - the browse button lists server folders.
- **placement:** the end of a graph, in place of `SaveImage`, when you need a color-managed / sequence / video / RGBA / ProRes save.

---

## The six color operators

### OCIOColorSpace  (display: "OCIO ColorSpace")
- **inputs:** `image` (IMAGE); `in_colorspace` / `out_colorspace` (combo of the config's spaces); `mix` (FLOAT 0..1, blend with the original); `config_path` (combo, optional). A **swap** button flips in/out.
- **purpose / how:** convert between two OCIO colorspaces; `config.getProcessor(in, out)` per frame, blended by `mix`.
- **anti-patterns:** the names must exist in the active config; a typo or a name from another config errors. Needs OpenColorIO + a config.
- **placement:** anywhere a colorspace change is needed - the OCIO workhorse.

### OCIOLogConvert  (display: "OCIO LogConvert")  -- the log-space transform node, dependency-free
- **inputs:** `image` (IMAGE); `operation` (combo `lin_to_log`/`log_to_lin`); `curve` (combo `cineon`/`acescct`/`acescc`/`logc3`, **`logc3` new in v1.0.1**); `mix` (FLOAT). A **swap** button flips the direction.
- **purpose:** linear <-> log so manual geometry (scale, rotate, warp, resample) preserves highlight/shadow detail instead of crushing it in linear light. **This is the node for the log-space technique in `color-and-transform.md`.**
- **curves (published specs, verified by round-trip):** `cineon` = Nuke's flat film log, black `0 -> 0.0928` (matches Nuke's default); `acescct` = ACES log with a toe (black `0.0729`, S-2016-001); `acescc` = pure ACES log (S-2014-003); **`logc3` = ARRI LogC3 EI800**, the tonal curve LTX-2's HDR IC-LoRA uses (black `0 -> 0.0928`). Use `log_to_lin` with `logc3` to decode an LTX LogC3 HDR plate to linear, KEEP the Rec.709 primaries, then convert Rec.709 -> ACEScg with OCIO ColorSpace (do NOT use a config "ARRI LogC3" space - that assumes ARRI Wide Gamut and shifts the gamut).
- **anti-patterns:** do NOT run AI / diffusion / VAE in log; do not round-trip at 8-bit; wrap once around the whole transform block; feed LINEAR for `lin_to_log` (linearize sRGB first).
- **placement:** wrap tightly around manual geometry.

### OCIODisplay  (display: "OCIO Display")
- **inputs:** `image` (IMAGE); `in_colorspace` (combo); `display` (combo of the config's displays, e.g. "sRGB - Display"); `view` (combo, e.g. "ACES 2.0 - SDR 100 nits (Rec.709)"); `invert_direction` (BOOLEAN); `mix` (FLOAT); `config_path` (optional).
- **purpose / how:** apply a display + view transform (scene-referred -> display-referred, e.g. ACEScg -> the ACES SDR view on an sRGB monitor). `OCIO.DisplayViewTransform` per frame.
- **anti-patterns:** a viewing/output transform, not a working-space convert - do not feed its output back into a linear pipeline; `display`/`view` must be valid for the config.
- **placement:** near the end, before save/preview, to bake a display look.

### OCIOCDLTransform  (display: "OCIO CDLTransform")
- **inputs:** `image` (IMAGE); `slope_r/g/b`, `offset_r/g/b`, `power_r/g/b` (FLOAT); `saturation` (FLOAT); `direction` (combo forward/inverse); `mix` (FLOAT).
- **purpose / how:** an ASC CDL primary grade (per-channel slope/offset/power + saturation); `OCIO.CDLTransform`, config-independent.
- **anti-patterns:** CDL math assumes a defined working space (usually log or a grade space); on raw linear it looks different than a colorist expects.
- **placement:** the primary-grade step in a color chain.

### OCIOFileTransform  (display: "OCIO FileTransform")
- **inputs:** `image` (IMAGE); `file_path` (combo of LUTs in the input folder - `.cube`/`.3dl`/`.spi1d`/`.spi3d`/`.csp`/`.ccc`/`.cdl`/`.clf`; an **upload** button adds one); `interpolation` (combo linear/nearest/tetrahedral/best); `direction` (forward/inverse); `mix` (FLOAT).
- **purpose:** apply an external LUT / CCC / CDL file (a show or camera LUT).
- **anti-patterns:** the LUT expects a specific input space - the wrong space gives wrong color; `tetrahedral` for 3D LUTs, `linear` for 1D; the file must exist in the input folder (or upload it).
- **placement:** wherever a show/camera LUT belongs in the chain.

### OCIOLookTransform  (display: "OCIO LookTransform")
- **inputs:** `image` (IMAGE); `in_colorspace` / `out_colorspace` (combo); `look` (combo of the config's looks, e.g. "ACES 1.3 Reference Gamut Compression"); `invert_direction` (BOOLEAN); `mix` (FLOAT); `config_path` (optional). A **swap** button flips in/out.
- **purpose / how:** apply a named OCIO "look" (a creative grade defined in the config); `OCIO.LookTransform`.
- **anti-patterns:** the look name(s) must be defined in the active config.
- **placement:** the creative-look step, after primaries, before display.

---

## Worked example - color-managed sequence to ProRes

An EXR render sequence to a graded ProRes, the Nuke way:

```
OCIO Read (source=D:\shots\beauty.####.exr, input=ACEScg, output=sRGB - Display, frame_mode=auto)
  -> [any ComfyUI work, or a color operator, e.g. OCIO CDLTransform for a primary grade]
  -> OCIO Write (from=sRGB - Display, output=Rec.1886 Rec.709 - Display, container=video,
                 video_codec=prores_4444, auto_range=ON, filename=beauty_graded)
```

`auto_range=ON` pulls the frame range + fps from OCIO Read through the wire, so the ProRes carries the right
count and rate. The example workflow `example_workflows/OCIO_Nodes.json` in the repo shows the pre-Player eight
nodes on one image (copy its `nyc_skyline.png` + `warm_demo.cube` into ComfyUI's input folder, then open it); the
9th node **OCIO Player** and the native VIDEO sockets (v1.2.0) are covered in "New in v1.2.0" above.

## Worked example (v1.0.1) - LTX-2 HDR video to an ACEScg EXR sequence

LTX-2's HDR IC-LoRA emits an HDR plate on a Rec.709 gamut with an ARRI LogC3 tonal curve. To land it in a VFX
master format (scene-linear ACEScg EXR), two ways - both write `name_acescg.####.exr`:

**Method A - automatic (fewest nodes):** wire OCIO Write straight to LTX's HDR decode.
```
[LTX-2 HDR sampler -> VAE Decode] -> LTXVHDRDecodePostprocess (hdr_linear out)
  -> OCIO Write (auto_colorspace=ON -> auto-sets from="Linear Rec.709 (sRGB)", output="ACEScg";
                 container=sequence, still_format=exr, compression=zip, colorspace_in_name=ON)
```
`auto_colorspace` detects the LTX HDR decode upstream and fills the two colorspaces, so Write converts
Rec.709 -> ACEScg on the way out.

**Method B - manual (explicit, full control):** decode the LogC3 curve yourself, then set the gamut.
```
[VAE Decode of the HDR plate]
  -> OCIO LogConvert (operation=log_to_lin, curve=logc3)   # LogC3 -> linear, KEEP Rec.709 primaries
  -> OCIO ColorSpace (in="Linear Rec.709 (sRGB)", out="ACEScg")   # gamut Rec.709 -> ACEScg
  -> OCIO Write (from="ACEScg", output="ACEScg", container=sequence, still_format=exr)
```
Both need `OPENCV_IO_ENABLE_OPENEXR=1` (EXR write) and produce an ACEScg-tagged 16f/32f EXR sequence. Do NOT
route through a config "ARRI LogC3" colorspace - that assumes ARRI Wide Gamut and shifts the gamut; the LTX plate
is Rec.709.

**Building a graph with these nodes:** lay it out with `workflow_layout.py` like any other (see SKILL.md) - OCIO
Read has no input and four outputs, OCIO Write is an output node; a linear Read -> operators -> Write chain lays
out cleanly left to right.
