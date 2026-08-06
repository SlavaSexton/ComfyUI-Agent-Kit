# Krea reference: node I/O, prices, weights, ecosystem

Everything here is read from a primary source, named per section. Read `SKILL.md` first for the fork and the
graphs; this file is the lookup table.

---

## `Krea2ImageNode` full I/O

Source: `comfy_api_nodes/nodes_krea.py` on the local ComfyUI install, read 2026-08-06. Category
`partner/image/Krea`, display name **Krea 2 Image**, `is_api_node=True`, output **IMAGE**.

| Input | Type | Default | Range / options |
|---|---|---|---|
| `prompt` | STRING multiline | `""` | validated, at least 1 character |
| `model` | DynamicCombo | (none) | `Krea 2 Medium`, `Krea 2 Medium Turbo`, `Krea 2 Large` |
| `seed` | INT | 0 | 0 to 2147483647, `control_after_generate` on |

Nested under whichever `model` option is picked, identical for all three:

| Sub-input | Type | Default | Range / options |
|---|---|---|---|
| `aspect_ratio` | Combo | (first) | `1:1`, `4:3`, `3:2`, `16:9`, `2.35:1`, `4:5`, `2:3`, `9:16` |
| `resolution` | Combo | `1K` | **`1K` only** |
| `creativity` | Combo | `medium` | `raw`, `low`, `medium`, `high`. Raw stays closest to the prompt |
| `moodboard_id` | STRING optional | `""` | must match a UUID regex; one moodboard per request |
| `moodboard_strength` | FLOAT optional | 0.35 | -0.5 to 1.5, step 0.05; ignored when the id is empty |
| `style_reference` | `KREA_STYLE_REF` optional | (none) | chain from `Krea2StyleReferenceNode`, max 10 |

**Correction to the shipped docs:** `comfyui_embedded_docs` lists `creativity` as FLOAT. It is a string combo.
That doc carries its own "This documentation was AI-generated" line; the node source is authoritative.

**Transport, for anyone debugging a failure:** the node POSTs to
`/proxy/krea/generate/image/krea/krea-2/{medium|medium-turbo|large}`, then polls `/proxy/krea/jobs/{job_id}`.
Queue states it waits on are `backlogged`, `queued`, `scheduled`. A job that finishes with no image URLs raises
rather than returning a blank.

## `Krea2StyleReferenceNode` full I/O

Same source and category, display name **Krea 2 Style Reference**. Output is a `KREA_STYLE_REF` list, not an
image.

| Input | Type | Default | Range |
|---|---|---|---|
| `image` | IMAGE | (required) | uploaded to `/proxy/krea/assets`, downscaled to fit 2048x2048, sent as PNG |
| `strength` | FLOAT | 1.0 | **-2.0 to 2.0**, step 0.05. Negative inverts the style influence |
| `style_reference` | `KREA_STYLE_REF` optional | (none) | the incoming chain; this node appends one entry |

The node raises when the incoming chain already holds 10 entries, so an eleventh reference is an error, not a
silent drop. Each entry is `{url, strength}`.

## Price matrix

Read from the node's `price_badge` expression in the same file, USD per image.

| Tier | Text only | With style reference | With moodboard |
|---|---|---|---|
| Krea 2 Medium Turbo | 0.015 | 0.0175 | 0.02 |
| Krea 2 Medium | 0.03 | 0.035 | 0.04 |
| Krea 2 Large | 0.06 | 0.065 | 0.07 |

The expression picks the moodboard rate first, then the style rate, then text. Setting both a moodboard and
style references bills the moodboard rate, not the sum. Turbo to Large is a **4x** spread on the same prompt.

---

## Weights, measured

Sizes read from the Hugging Face blob API on 2026-08-06, not estimated from parameter counts.

| File | Repo | Size | Notes |
|---|---|---|---|
| `flux1-krea-dev_fp8_scaled.safetensors` | `Comfy-Org/FLUX.1-Krea-dev_ComfyUI` | **11.09 GB** | ungated, the only file in the repo |
| (reference weights) | `black-forest-labs/FLUX.1-Krea-dev` | n/a | **gated**; metadata reads fine, file downloads return 403 without accepting terms |
| `krea-realtime-video-14b.safetensors` | `krea/krea-realtime-video` | **26.61 GB** | single file, does not fit a 24 GB card |
| `krea-realtime-video-14b-fp8-e4m3fn.safetensors` | `6chan/krea-realtime-video-fp8` | **13.31 GB** | community repack, no usage text on the card |
| `krea-realtime-video-14b-fp8-e5m2.safetensors` | `6chan/krea-realtime-video-fp8` | **13.31 GB** | same |

Licences: FLUX.1 Krea Dev is `flux-1-dev-non-commercial-license` (from the repack's frontmatter, which links to
the BFL licence file). Krea Realtime is **Apache-2.0**. Krea 2's own licence is covered in `MODELS.md`.

## The `krea` org on Hugging Face, complete

Listed exhaustively through the API on 2026-08-06 rather than searched by guess, so an absence here is a real
absence.

- `krea/Krea-2-Raw`, `krea/Krea-2-Turbo` (the base models, documented in `MODELS.md`)
- Nine official style LoRAs: `Krea-2-LoRA-` + `darkbrush`, `retroanime`, `kidsdrawing`, `softwatercolor`,
  `vintagetarot`, `neondrip`, `dotmatrix`, `rainywindow`, `sunsetblur`. Already covered by the kit.
- `krea/krea-realtime-video`
- `krea/aesthetic-controlnet`, from 2023 and unrelated to the current lineup
- `krea/14b_sf`, `krea/sf_14b`, both empty of downloads and look like staging repos

There is no Krea image model on the hub other than Krea 2 and the LoRAs above.

## Krea Realtime 14B details

Source: the model card read in full including frontmatter, 2026-08-06.

- Base `Wan-AI/Wan2.1-T2V-14B`, distilled with **Self-Forcing** into an autoregressive model. Tags include
  `diffusion-single-file`, `text-to-video`, `video-to-video`, `realtime`; `library_name: diffusers`.
- Their claim: **11 fps at 4 inference steps on one NVIDIA B200**, about one second to the first frame, prompts
  editable mid-generation, restyle on the fly. Vendor figure on vendor hardware, not reproduced here.
- Their stated contributions: KV Cache Recomputation and KV Cache Attention Bias against error accumulation,
  plus memory optimisations specific to autoregressive video diffusion.
- Their install path needs `ffmpeg`, `uv sync`, `flash_attn` built without isolation, and a download of
  `Wan-AI/Wan2.1-T2V-1.3B` **alongside** the 14B checkpoint, then `uvicorn release_server:app` on port 8000.
- The repo also carries a `transformer/` diffusers layout in three shards, so it is usable from diffusers code
  as well as the single file.
- Third-party ports found by content search: `IPostYellow/krea-realtime-video-diffusers`,
  `felipesztutman/krea-realtime-video-14b-w4a4`, `SceneWorks/krea-realtime-14b-mlx`, plus DiffSynth-Studio and
  LightX2V configs. **None of them is a ComfyUI node.**

## Ecosystem packs, what each actually does

Read from each repository's README, 2026-08-06. Star and push dates from the GitHub API. Note that GitHub's
search `updatedAt` moves on metadata touches; the dates below are real code pushes.

### `lbouaraba/comfyui-krea2edit` (410 stars, 22 forks, pushed 2026-07-29, no licence file)
Powers the **Krea 2 Identity Edit** LoRA. Node `Krea2EditModelPatch` wraps the model so the VAE-encoded source
is prepended as clean in-context tokens at RoPE frame 1, and the same image also goes through the Qwen3-VL text
encoder, matching the LoRA's training. Key inputs: `model` (LoRA already applied), `source_latent`, optional
`source_latent_b` for a second reference at RoPE frame 2 (person plus scene), optional `vae` + `source_image`
for the pixel path that avoids blur, and `target_latent` which should be the same latent you feed
`KSampler.latent_image` so the source can be encoded up front instead of on the first sampling step. `fit_mode`
defaults to `fit`. Works with Raw or Turbo. Needs a ComfyUI with native Krea 2 support and no extra Python deps.
The author recommends LoRA v1.2 and publishes the trainer as `lbouaraba/krea2edit-trainer`.

### `facok/comfyui-krea2-controlnet` (162 stars, 12 forks, pushed 2026-07-04, no licence file)
Three nodes, wired in this order: `Krea2 Control LoRA Loader` loads a Krea2 Control LoRA from `models/loras`,
applies the block weights, prepares the expanded input projection and registers a sampling wrapper;
`Krea2 Control Image Encode` encodes a control IMAGE with the Krea2 or Qwen VAE (feed it Depth Anything, canny,
OpenPose, lineart or normal maps from `comfyui_controlnet_aux`, which it does not import), keeping the default
`match_latent_size` and taking the sampler latent on its `latent` input; `Krea2 Control Apply` converts that to
Krea2 latent space and attaches it to the model. Apply is **required** after the loader: loading the Control
LoRA with no control latent attached fails outright rather than sampling a half-patched model.

### `huwhitememes/comfyui-krea2-conditioning` (126 stars, 9 forks, pushed 2026-06-26, Apache-2.0 badge, no licence file)
**Adoption check first, because it cuts against the fork:** its upstream
`nova452/ComfyUI-ConditioningKrea2Rebalance` sits at **477 stars, pushed 2026-07-29**, well ahead of this fork
and still actively maintained. The fork's argument below is its author's, is technically specific, and is
untested here. Treat this as two live options, not a supersede.

A fork of `nova452/ComfyUI-ConditioningKrea2Rebalance` that disputes its central default. The original reweights
Krea 2's twelve Qwen3-VL conditioning taps and then multiplies the whole tensor by 4, which compounds with the
roughly 2.2x from the per-layer gains into about **8.7x** inflated conditioning magnitude. The fork
RMS-renormalises, shifting the ratios between taps while holding total magnitude constant. The author is careful
about the symptom: others report oversaturation, their own Turbo tests showed skin artifacts and likeness drift
with no saturation shift, same root cause. Reach for it when a Krea 2 output has those symptoms, not by default.

---

## Status of the claims in this file

**Confirmed by reading a primary source:** every node input, type, default and range (node source on disk); the
price matrix (the price-badge expression); the hosted wiring and widget order (the two shipped API templates);
the FLUX.1 Krea Dev graph including the absence of `FluxGuidance` (the shipped template, expanded through its
subgraph and checked by string search); all file sizes (HF blob API); the complete `krea` org listing (HF API);
the Realtime facts (the model card in full); each ecosystem pack's node names and behaviour (its README);
star counts and push dates (GitHub API).

**Not confirmed here:** nothing in this file was run on a GPU, and no hosted generation was billed. Krea's
11 fps figure is theirs on a B200. The three ecosystem packs are described from their own documentation, not
from a test run, so treat their behaviour claims as the authors' until someone runs them.
