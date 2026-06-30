# Node Library - index (start here)

The kit's per-node knowledge base: for every node, what it is for, what each input/output is for, how it
behaves, its strengths, bugs + fixes, anti-patterns, and where it slots in a graph. Built so a future agent
**remembers what is where** instead of rediscovering it. New to this? Read `_SCHEMA.md` for the format and the
rules (live-vs-curated I/O, confirmed-vs-inferred, add-on-encounter, custom-node authorship).

**Live I/O is never frozen here.** For a node's exact current inputs/outputs/defaults, query
`get_node_info <ClassType>` (MCP) or `/object_info`. This library holds the durable layer on top: semantics,
gotchas, fixes, placement, build-vs-search calls.

## Documented nodes

### `core.md` - the minimal text-to-image chain (all I/O confirmed 2026-06-30)
| Node | Purpose |
|------|---------|
| CheckpointLoaderSimple | load a checkpoint -> MODEL / CLIP / VAE |
| LoraLoader | apply a LoRA to model + CLIP (stackable, negative ok) |
| CLIPTextEncode | prompt -> CONDITIONING (use the model-specific encoder for Flux/SD3/SDXL) |
| EmptyLatentImage | blank latent canvas, sets output resolution |
| KSampler | the denoiser (seed/steps/cfg/sampler/scheduler/denoise) |
| VAEDecode | latent -> IMAGE (tiled / loop variants for big or video) |
| SaveImage | write 8-bit sRGB PNG (output node) |

### `color-and-transform.md` - color space + manual geometry
| Entry | Purpose |
|-------|---------|
| TECHNIQUE: transform in log | do manual scale/distort/warp in log space to preserve detail (Nuke/OCIO practice) |
| OCIOColorConvert | Linear<->Log conversion (I/O to confirm on an OCIO-enabled install) |
| SaveImageAdvanced | PNG 16-bit / EXR 32-bit float, linear / HDR / sRGB (confirmed) |

## Reverse lookup (by task)
- **Generate an image from text** -> the `core.md` graph.
- **Apply a style / subject LoRA** -> LoraLoader (`core.md`).
- **Preserve detail through a manual scale / distort / warp** -> log-space technique (`color-and-transform.md`).
- **Save HDR / linear / EXR / 16-bit** -> SaveImageAdvanced (`color-and-transform.md`).
- **Big image OOMs on decode** -> VAEDecodeTiled (noted under VAEDecode, `core.md`).
- **Video loop seam artifacts on decode** -> VAEDecodeLoopKJ (noted under VAEDecode, `core.md`).
- **Base + refiner staged sampling** -> KSamplerAdvanced (noted under KSampler, `core.md`).

## Where other node knowledge lives (no orphan corners)
- **kijai ecosystem** (Wan / Hunyuan / Florence2 / KJNodes / SUPIR / SAM2 / DepthAnythingV2 ...) -> `docs/KIJAI.md` (per-tool node I/O + supersede map).
- **In-graph LLM nodes** (Anthropic Claude / OpenRouter prompt enrichment) -> `docs/NODES.md`.
- **Live bugs / broken paths** -> `docs/KNOWN_ISSUES.md` (read before building).
- **Core-node cheat-sheet + the /object_info discipline** -> `SKILL.md`.
- **Building your OWN node** (V3 API: basics / inputs / outputs / datatypes / lifecycle / packaging) -> the `comfyui-node-*` skills.

## Status
Started 2026-06-30 (ComfyUI 0.25.1). Grows on encounter: use or meet an undocumented node, add its entry before
finishing (see `_SCHEMA.md`). Entries carry their own confirmed/inferred + date.
