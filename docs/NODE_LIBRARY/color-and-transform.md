# Color and transform - working in the right space

Nodes and techniques for color-space conversion and manual (non-AI) pixel geometry: scale, rotate, distort,
warp, skew, crop. The headline rule here is a production-color practice from compositing, not a single node.

## TECHNIQUE: do manual transforms in LOG, not linear

**Rule:** any manual, non-AI change to pixels (scale, transform, rotate, distortion, warp, skew, any resample)
should be done in a LOG-encoded space, then converted back, rather than on linear data. Linear resampling
crushes detail in highlights and shadows; log encoding spreads code values perceptually so interpolation
preserves it.

**Flow:**
```
image ──▶ Linear→Log ──▶ [scale / transform / distort / warp / skew] ──▶ Log→Linear ──▶ continue
```

- **Source / status:** *confirmed* as standard practice. This is The Foundry Nuke workflow (OCIO color
  management) and the kit owner's own pipeline: an `OCIOColorConvert` node set to **Operation: Linear to Log**,
  the geometric op, then `OCIOColorConvert` **Log to Linear**.
- **Why it works:** a log curve allocates more code values to darks and compresses brights the way perception
  does. Resampling / filtering in that space keeps fine tonal detail that linear interpolation would average
  away. Same reason film scans and ACEScct grade in log.
- **Where it slots:** wrap the log conversion tightly around the geometry node(s) only. Convert back to linear
  before any node that expects linear / sRGB (diffusion, VAE, most filters).
- **Anti-patterns:**
  - Do NOT run AI / diffusion / VAE steps in log space; those expect linear or sRGB. Log is for the manual
    geometric / resample ops only.
  - Do NOT round-trip at 8-bit. Each conversion is lossy at low bit depth; carry 16 or 32-bit float through
    the log wrap (and save EXR if persisting, see below).
  - Do NOT stack redundant log<->linear pairs; one wrap around the whole transform block, not per node.

### The OCIO node (to confirm on an OCIO-enabled install)
- **class_type / I/O:** *inferred, not yet confirmed here.* `get_node_info OCIO` returned **"No nodes found"**
  on this machine (ComfyUI 0.25.1, 2026-06-30): no OCIO pack is installed. The owner uses `OCIOColorConvert`
  (Nuke-style) on another setup.
- **To wire it for real:** on the install that has OCIO, run `get_node_info <the OCIO class>` to read the exact
  input names (source space, target space, the Linear<->Log operation enum) before composing. To add OCIO
  here: `search_custom_nodes "OCIO"` / `"OpenColorIO"`, install, then document the confirmed I/O in this file.
- **Build-vs-search note:** if no maintained OCIO node fits, a small custom `LinearToLog` / `LogToLinear`
  pair (a fixed log curve, IMAGE in / IMAGE out) is a strong candidate to build ourselves; credit the
  requester per `_SCHEMA.md`.

## Native linear / HDR / EXR I/O (confirmed)

You do not need OCIO just to persist linear or HDR data. **SaveImageAdvanced** (core, category `image`,
confirmed via get_node_info 2026-06-30) writes:
- **PNG** at 8-bit or 16-bit (`input_color_space` sRGB),
- **EXR** at 32-bit float, with `input_color_space` of `sRGB`, `HDR` (HLG Rec.2020 / BT.2100), or `linear`
  (scene-linear Rec.709, written through unchanged). The EXR is always stored scene-linear in the matching
  gamut.

- **inputs:** `images` (IMAGE), `filename_prefix` (STRING), `format` (dynamic combo: png / exr with the
  bit-depth + color-space sub-options above).
- **use it for:** keeping a 16/32-bit float intermediate across a log-space transform, or delivering EXR for a
  compositor. Pair with the log technique above when the manual transform must hold full dynamic range.
- **anti-pattern:** plain `SaveImage` is 8-bit sRGB PNG only; it silently throws away the precision the log
  workflow exists to protect.

## Status

Technique: confirmed (Nuke / OCIO standard + owner pipeline), 2026-06-30. OCIOColorConvert exact I/O: inferred,
confirm via get_node_info on an OCIO install. SaveImageAdvanced I/O: confirmed via get_node_info 2026-06-30.
