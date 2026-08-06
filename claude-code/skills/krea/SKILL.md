---
name: krea
description: Use when a task names Krea or Krea 2, when choosing between Krea's hosted API and its open weights, when wiring the Krea 2 Image or Krea 2 Style Reference API nodes, when building with FLUX.1 Krea Dev, when someone asks about Krea Realtime or realtime or streaming video generation, or when a Krea 2 job needs ControlNet, instruction editing, identity preservation or per-layer conditioning control that core ComfyUI does not provide.
---

# Krea

Krea ships two completely separate things under one brand, and picking the wrong one wastes the job.

**The fork, decide it first.**
- **Hosted API.** Nodes `Krea2ImageNode` and `Krea2StyleReferenceNode`, category `partner/image/Krea`, billed per
  image, capped at **1K output**, and the only path that reads a **Krea moodboard** from the website.
- **Open weights.** Krea 2 Raw and Turbo run locally on core nodes, free, any resolution, no moodboard.

**Who owns what, so you open one file, not three.** THIS file owns the fork, the hosted graph, the FLUX.1 Krea
Dev graph and the ecosystem map. `reference.md` next to it owns full node I/O, the price matrix, weight files
with measured sizes, and the custom-node packs. **The kit's `MODELS.md` already owns the local Krea 2 graph in
depth** (Raw vs Turbo settings, the `qwen3vl_4b` encoder and its `krea2` CLIP type, the Ostris edit method, the
style-reference LoRA on core nodes, the nine official style LoRAs, the abliterated-encoder swap, licence).
Do not restate it here, route to it.

## Which Krea for which job

| Job | Path | Why this one |
|---|---|---|
| A look you already built on krea.ai as a **moodboard** | hosted `Krea2ImageNode` | moodboard UUIDs exist only on their service |
| Style from 1 to 10 **reference images**, no local weights | hosted, chain `Krea2StyleReferenceNode` | up to 10 refs, each with its own strength |
| Same style locally, one reference | local Krea 2 Turbo + `krea2_style_reference` LoRA | free, no cap at 1K, see `MODELS.md` |
| Output above 1K | local only | the hosted node's `resolution` combo has exactly one option, `1K` |
| Photoreal stills, opinionated photographic look, low VRAM | **FLUX.1 Krea Dev** (graph below) | 11.90 GB (11.09 GiB) fp8, ordinary FLUX graph |
| Instruction editing that keeps a face | local Krea 2 + `comfyui-krea2edit` | see the ecosystem map below |
| Depth / canny / pose control on Krea 2 | local Krea 2 + `comfyui-krea2-controlnet` | core has no Krea 2 ControlNet |
| Realtime or streaming video, interactive prompt changes | their own server, DiffSynth-Studio or LightX2V | the one ComfyUI pack has 0 stars and is unproven, see below |

## The hosted graph, buildable

Two nodes, one optional chain. Confirmed against the shipped templates `api_krea2_t2i` and
`api_krea2_style_reference` on 2026-08-06.

```
                    LoadImage -> Krea2StyleReferenceNode ---(KREA_STYLE_REF)--+
                    LoadImage -> Krea2StyleReferenceNode <--(chain in)--------+
                                          |
                                          +--(KREA_STYLE_REF)-> Krea2ImageNode -> SaveImage
```

Style references **chain node to node**: each `Krea2StyleReferenceNode` takes an optional incoming
`style_reference` and appends one more, so the last node in the chain is the one you wire to `Krea2ImageNode`.
Ten is a hard ceiling and the node raises rather than truncating.

`Krea2ImageNode` widget order, which is what you fill when you build the graph in code:

```
[0] prompt   [1] model   [2] aspect_ratio   [3] resolution
[4] creativity   [5] moodboard_id   [6] moodboard_strength   [7] seed   [8] control_after_generate
```

The official template ships `"Krea 2 Medium"`, `"1:1"`, `"1K"`, `"medium"`, `""`, `0.35`.

**Three model tiers, and the source states what each is for:** Medium for expressive illustrations, Large for
expressive photorealism, Medium Turbo for speed. Prices differ 4x between Turbo and Large, so the tier is a
budget decision as much as a look decision. Full matrix in `reference.md`.

**Things that will bite you here:**
- `creativity` is a **combo of `raw` / `low` / `medium` / `high`**, not a number. The embedded node docs shipped
  with ComfyUI say FLOAT, which is wrong; they carry their own "AI-generated" disclaimer. The node source wins.
- `resolution` accepts **only `1K`**. There is no 2K option to find.
- `moodboard_id` must be a real UUID copied from the Krea website or the node raises before spending anything.
  Only one moodboard per request.
- Style-reference `strength` runs **-2.0 to 2.0**, and negative values invert the style influence rather than
  disabling it. Set 0 to neutralise, not a negative.
- Billing follows the most expensive feature you switched on: a moodboard costs more than a style reference,
  which costs more than plain text, and setting both charges the moodboard rate.

## FLUX.1 Krea Dev, buildable

Black Forest Labs' Krea-tuned FLUX, aimed at a photographic look with less of the plastic "AI sheen".
It is an ordinary FLUX dev graph, which is the whole point: no new node types.

```
UNETLoader(flux1-krea-dev_fp8_scaled.safetensors, default)
DualCLIPLoader(clip_l.safetensors, t5xxl_fp16.safetensors, type=flux) -> CLIPTextEncode -> KSampler.positive
                                                            -> ConditioningZeroOut -> KSampler.negative
EmptySD3LatentImage(1024, 1024, 1) -> KSampler.latent_image
KSampler(steps 20, cfg 1.0, euler, simple, denoise 1.0) -> VAEDecode <- VAELoader(ae.safetensors) -> SaveImage
```

Confirmed by reading the official template `flux1_krea_dev.json` and expanding its subgraph, 2026-08-06.
**Note what is absent:** the template carries **no `FluxGuidance` node at all**, and the negative branch is a
`ConditioningZeroOut` off the same encode. Verified by string search on the template, not by eye. If you add
`FluxGuidance` you are departing from the shipped recipe, so change one thing and compare.

Weights: `Comfy-Org/FLUX.1-Krea-dev_ComfyUI`, one file, `split_files/diffusion_models/flux1-krea-dev_fp8_scaled.safetensors`,
**11.90 GB (11.09 GiB) measured**, ungated. The original `black-forest-labs/FLUX.1-Krea-dev` is gated, so reach for the
repack unless you need the reference weights. Licence flag: `flux-1-dev-non-commercial-license`.

## Krea Realtime 14B, and why ComfyUI is not the road most travelled

Real, open, Apache-2.0. A ComfyUI pack exists but is unproven; the paths with users behind them are elsewhere.

- Distilled from `Wan-AI/Wan2.1-T2V-14B` with **Self-Forcing**, which converts a diffusion video model into an
  autoregressive one. Their own figure is **11 fps at 4 steps on a single B200**, with roughly one second to the
  first frame. Text to video and video to video, including webcam and canvas input, with the prompt changeable
  mid-generation.
- The parts that are the actual contribution: **KV Cache Recomputation** and **KV Cache Attention Bias** to hold
  off error accumulation over a long autoregressive roll.
- **There IS a ComfyUI pack, and it is unproven.** `eliteprox/ComfyUI-Krea` ships
  `KreaRealtimeVideoLoader` and `KreaRealtimeVideoGenerate` and loads the 14B checkpoint. **0 stars, last push
  2025-11-04.** Treat it as a lead, not a route, and read its source before wiring anything.
  **This entry previously said no ComfyUI node existed.** That was wrong: the search behind it looked for the
  checkpoint FILENAME in code across GitHub and this pack does not name it the same way. A negative claim needs
  several differently-shaped searches before it is worth stating.
- What to run instead: their own FastAPI server (`github.com/krea-ai/realtime-video`, web app on port 8000),
  DiffSynth-Studio, or LightX2V.
- **Fit on a 24 GB card:** the official single file is **28.58 GB (26.61 GiB) measured**, so it does not fit. The community
  fp8 repack `6chan/krea-realtime-video-fp8` is **14.29 GB (13.31 GiB)** in both `e4m3fn` and `e5m2`, which does. That repack
  makes no ComfyUI claim and the card is frontmatter only.

## The Krea 2 custom-node ecosystem worth knowing

Core plus what `MODELS.md` documents covers text to image, the Ostris edit path and the style-reference LoRA.
These three fill jobs none of that covers. Adoption numbers read on 2026-08-06; none of the three ships a
licence file.

- **`lbouaraba/comfyui-krea2edit`** (over 400 stars, last push 2026-07-29). Instruction editing that holds a face,
  built around the Krea 2 Identity Edit LoRA. Node `Krea2EditModelPatch` injects the source image twice, as VAE
  latent tokens for appearance and through the Qwen3-VL encoder for semantics, which is how the LoRA was
  trained. Takes a second reference for person-plus-scene edits. Its trainer is public too.
- **`facok/comfyui-krea2-controlnet`** (162 stars, 2026-07-04). Depth, canny, pose and lineart control for
  Krea 2 through a Control LoRA: `Krea2 Control LoRA Loader` -> `Krea2 Control Image Encode` (feed it a
  `comfyui_controlnet_aux` preprocessor output) -> `Krea2 Control Apply` -> sampler. It fails loudly when the
  loader runs without an attached control latent instead of silently sampling half-patched, which is the
  behaviour you want.
- **Per-layer conditioning control, and it is a genuine two-horse choice.** The upstream is
  **`nova452/Rebalance-Pack` (formerly `ComfyUI-ConditioningKrea2Rebalance`)** (**477 stars**, pushed 2026-07-29), which introduced
  reweighting Krea 2's twelve Qwen3-VL conditioning taps. The fork
  **`huwhitememes/comfyui-krea2-conditioning`** (**126 stars**, 2026-06-26) argues the upstream multiplies the
  whole tensor by 4 on top of the per-layer gains, inflating conditioning magnitude by roughly 8.7x, and
  RMS-renormalises instead so the ratios shift while total magnitude holds. **The upstream is the more adopted
  of the two by a wide margin**, so the fork is a minority position that makes a technical case, not the
  consensus. Reach for either when a Krea 2 job shows skin artifacts or likeness drift; nobody here has run
  an A/B.

Not adopted and not recommended yet, listed so nobody re-finds them and assumes they are missing knowledge:
`comfyui-krea2-nunchaku`, `comfyui-krea2-sageattention-guard`, `comfyui-krea2-fal-lora-converter`,
`comfyui-krea2-controlnetPlus`, `ComfyUI_Krea_Nodes`. All at 0 to 2 stars.

## When it goes wrong

| Symptom | Most likely cause |
|---|---|
| The API node errors before generating anything | `moodboard_id` is not a UUID, or the prompt is empty; both are validated locally |
| Style reference seems to fight the prompt | `strength` is negative, which inverts rather than weakens |
| Cannot find a 2K option on the hosted node | There is none. `resolution` has exactly one entry |
| Bill is higher than the tier suggests | A moodboard is set, and its rate overrides the style and text rates |
| `creativity` will not take a number | It is a combo of `raw` / `low` / `medium` / `high`. The embedded doc is wrong |
| Krea 2 edit shifts the face | Wrong pack for the job; the identity path is `comfyui-krea2edit`, not the Ostris detail enhancer |
| Looking for Krea Realtime nodes in ComfyUI | One pack exists (`eliteprox/ComfyUI-Krea`, 0 stars, unproven). The trodden paths are their server, DiffSynth-Studio, LightX2V |
| FLUX.1 Krea Dev download is gated | Use the ungated Comfy-Org repack, one 11.90 GB (11.09 GiB) file |
