# MiniMax H3 reference: weights, quants, acceleration, tooling

Everything verified against the source repositories on **2026-08-06**. Sizes are read from the HuggingFace repo
trees, node facts from the node code, not from summaries.

## What ships, and what does not

The open release is **H3-Base only**, generating at **768p**. Two of the three official modules stay hosted:
**H3-Context-IR** (the multi-stage prompt and context refiner MiniMax calls "critical to the quality of the final
output") and **H3-Regenerate-2K** (the 2K pass). Locally you replace the first with your own prompt discipline
(the three-field format in SKILL.md, optionally expanded by a local LLM) and the second with an ordinary
upscaler or the two-pass latent route below. A hosted result looking more finished than your local one is the
missing IR, not your settings.

Architecture, from the official card: the text and visual encoder is the **full Qwen3-VL-32B**, tapped at its
**50th layer**; video and audio have separate VAEs; the Omni-Transformer predicts video and **stereo** audio
latents jointly.

## Official weights (`Comfy-Org/MiniMax-H3`, `diffusion_models/`)

Two task families. **FL2VA** covers text-to-video, image-to-video and first/last frame. **Ref2VA** is the
omni-reference variant.

| File | Size |
|---|---|
| `minimax_h3_{fl2va,ref2va}_bf16.safetensors` | 66.3 GB |
| `minimax_h3_{fl2va,ref2va}_int8_convrot.safetensors` | 34.0 GB |
| `minimax_h3_{fl2va,ref2va}_pruned_int8_convrot.safetensors` | 21.0 GB |
| `minimax_h3_{fl2va,ref2va}_pruned_fp8_scaled.safetensors` | 21.0 GB |

Plus `text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`,
`vae/minimax_h3_video_vae_fp16.safetensors` and `vae/minimax_h3_audio_vae_fp32.safetensors`.

**Where they go on disk.** The repo paths mirror the ComfyUI model tree, so under your ComfyUI base directory:
`models\diffusion_models\` for the fl2va / ref2va checkpoint, `models	ext_encoders\` for the Qwen3-VL
encoder, `modelsae\` for both VAEs. On a Desktop install the base directory is the one in Settings > Server
Config, not necessarily next to `main.py`. **The fastest first run is not hand-wiring the graph**: open the
shipped template `video_minimax_h3_t2v` from the template browser and swap the checkpoint if needed.

The **pruned fp8 variant is the same 21 GB as the pruned int8** and is worth trying when int8 misbehaves on a
given card. These are Comfy-Org's own conversions.

## Community quants (`Abiray/MiniMax-H3-GGUF`)

GGUF builds for both task families, sizes read from the repo tree:

| Quant | UNet size |
|---|---|
| Q3_K_S / Q3_K_M | **15.6 GB** |
| Q4_0 | 18.6 GB |
| Q4_K_S / Q4_K_M | 19.9 GB |
| Q5_0 | 22.8 GB |

Paired text encoder `text_encoders/qwen3vl_32b_minimax_h3-Q4_K_M.gguf` at **14.6 GB**, and a non-GGUF
`qwen3vl_32b_minimax_h3_int4_convrot.safetensors` at 15.0 GB. Q3 plus the Q4_K_M encoder is the smallest
credible full stack. **GGUF needs a loader that core does not have**: install `city96/ComfyUI-GGUF` and use its
UNet / CLIP loaders in place of `UNETLoader` and `CLIPLoader`. Two things this repo does not answer, so test
before committing a download: whether that pack has been updated for the H3 architecture, and whether the Turbo
LoRA below key-matches a GGUF UNet at all, since it was converted for the pruned safetensors layout. Wanting
both "fits in VRAM" and "runs in 4 steps" may not be satisfiable on the same stack today. Other community authors publishing H3 quants: Merserk, DeepBeepMeep, Gluttony10,
lilcheaty, tsolful, ethanfel. kijai publishes no H3 *weights* (checked all 73 of his HF repos), so credit for the
official conversions belongs to Comfy-Org, but he **does** ship an H3 node inside KJNodes, see below.

## Turbo LoRA: four steps instead of twenty

Original by **larryvrh** (`larryvrh/MiniMax-H3-Turbo-Lora`), converted for ComfyUI's pruned/curve-form
checkpoint by **drbaph** (`drbaph/MiniMax-H3-Turbo-Lora-ComfyUI`, Apache-2.0). The conversion exists because the
original tensor keys target the full-model layout, not the pruned one.

**Four files, not two.** The `ckpt500` pair is further-trained beyond the initial preview and is what the
converter recommends starting from:
- `minimax_h3_turbo_4step_ckpt500_pruned_comfyui.safetensors` - start here
- `minimax_h3_turbo_4step_ema_ckpt500_pruned_comfyui.safetensors` - EMA, for comparison
- `minimax_h3_turbo_4step_pruned_comfyui.safetensors` and its `_ema_` twin - the earlier preview versions

**non-EMA** is described as sharper with stronger fast-motion behaviour; **EMA** as smoother, time-averaged, and
in the initial release softer because the EMA had not matured. A ready workflow ships alongside:
`fl_minimax_h3_turbo_lora_example_workflow.json`, wired for first-and-last-frame with the LoRA attached.

**Read the original author's own caveat before trusting the speedup.** The Turbo LoRA is an *early preview from
an in-progress training run*: under-trained, EMA not fully matured, "quality is not representative of a
completed run". The claim is roughly **4 sampling steps instead of ~20, about a 5x cut in sampling wall-clock**.
Treat it as a fast draft mode, not a free quality-neutral win.

## kijai's VRAM patch (KJNodes)

`kijai/ComfyUI-KJNodes` ships **`MiniMaxH3MemoryEfficientSageAttentionPatch`** ("MiniMax H3 Mem Eff Sage
Attention Patch", category `KJNodes/minimax`, **EXPERIMENTAL**). A **MODEL patcher** like Spectrum, so the two
chain in one graph: this one swaps a custom SageAttention into H3's self-attention across every transformer
block **to reduce peak VRAM**, while Spectrum reduces step count. It hard-errors rather than degrading if
sageattention is too old, if the ComfyUI build has no H3 support, or if the model is not a `MiniMaxH3Model`.
This is the "kijai patch" that shows up in community reference-to-video test configs.

**Name collision:** `MiniMaxRemover` (`zibojia/minimax-remover`) is an unrelated video object-removal model that
kijai wires into `ComfyUI-WanVideoWrapper`. Searching his repositories for "minimax" returns it, which is why a
quick search can wrongly suggest either that he has H3 weights or that he has nothing H3 at all.

## Spectrum: forecast solver steps instead of computing them

`xmarre/ComfyUI-Spectrum-MiniMax-H3` (GPL-3.0). One node, **`SpectrumApplyMiniMaxH3`**, category
`sampling/spectrum`. It is a **MODEL patcher, not a replacement sampler**: MODEL in, MODEL out, so it sits
between `UNETLoader` and everything downstream. Widely repeated instructions to "replace the sampler with a
Spectrum Sampler" are wrong; the pack contains exactly one node class.

What it does, in the author's own accounting over 20 steps:

| Sampler | Actual steps | Forecast | Forecast at | Fewer transformer calls |
|---|---|---|---|---|
| Euler | 13 | 7 | 5, 7, 9, 11, 13, 15, 17 | ~35% |
| RES multistep / CFG++ | 14 | 6 | 5, 7, 9, 11, 13, 15 | ~30% |

Those are **solver-step counts, not wall clock**. The README is explicit that end-to-end gain also depends on
output-head cost, CPU transfers, offload, references, CFG branching, latent size and hardware, so circulating
"1.5x" figures describe one machine.

- **Supported:** `sample_euler`, `sample_res_multistep`, `sample_res_multistep_cfg_pp`.
- **Deliberate fallbacks to native:** ancestral samplers (injected noise breaks the smooth trajectory the
  forecaster fits) and multi-GPU parallel sampling. RES also **keeps its last three solver steps native**, a
  floor that overrides a smaller `tail_actual_steps`.
- **Knobs:** `blend_weight` 0.5, `degree` 4, `ridge_lambda` 0.1, `window_size` 2.0, `flex_window` 0.75,
  `warmup_steps` 5, `tail_actual_steps` 1, `max_history` 8, `debug`, optional `history_storage` =
  `system_ram` (default) or `vram`. VRAM history measured at **~2.2 GiB more peak** for a small, variable
  timing gain, so it is an option for spare VRAM, not a guaranteed win.
- **The version trap.** It pins to ComfyUI a ComfyUI build newer than the v0.30.0 release. Release **v0.30.0 was
  tagged the same day at 03:48 UTC, about 17 hours earlier, and does not contain it** (a commit comparison puts
  the release two commits behind). As of 2026-08-06 no tagged release carries the API, so the pack needs a
  master build. "Update to 0.30.0 or newer" is the advice going around and it leaves you on a build that fails.
  The node validates the contract at apply time and errors loudly rather than drifting.
- **Author's quality note:** fast action can follow a different trajectory, and fast-moving or briefly visible
  detail can degrade. Qualitative, varies with prompt, motion, sampler, resolution and references.

## Latent upscaler: a real two-pass at higher resolution

`Tr1dae/ComfyUI-MiniMaxH3_LatentUpscaler` (no licence file). Node **`MiniMaxH3LatentUpscaleCombined`**, category
`latent/minimax_h3`. It exists because stock `LatentUpscaleBy` and `AddNoise` **break on H3's packed
`NestedTensor` latent**, which carries video `[B,24,T,H/16,W/16]` and audio `[B,32,2,T_audio]` together. This is
interpolation plus correct re-noising of that structure, not a learned upscaler.

**Wiring.** First split the schedule: one `BasicScheduler` into a **`SplitSigmas`**, HIGH half to pass 1, LOW
half to both the Combined node and pass 2. Nothing else produces the "high" and "low" sets this recipe needs.
Then `SamplerCustomAdvanced` #1 runs the high half at low resolution, take its **`denoised_output`** (not the
plain output), feed the Combined node with the same conditioning as pass 1 plus `RandomNoise`, the LOW sigmas
and the model, build a **new `BasicGuider` from its returned `positive` / `negative`**, then
`SamplerCustomAdvanced` #2 with **DisableNoise**, the low sigmas and the Combined latent.

- **`audio_denoise` defaults to 1.0**, a full audio re-noise at `sigmas[0]`. `0` locks pass-1 audio; the author
  recommends **0.25 to 0.5**. If audio garbles above 0, **run more of the schedule in pass 1, because audio
  settles late**. Poor results at defaults are the expected behaviour of that default, not a broken node. **Inferred, not tested
  here:** that this is the cause of the poor community results is the most likely reading, not a measurement.
- **Why the conditioning outputs matter:** `minimax_refs` carry per-reference `latent_h` / `latent_w`. Grow the
  canvas 2x and references sized for the old canvas sit at the wrong relative scale and RoPE row layout, which is
  the classic identity warp. The node rescales reference latents and metadata together, so the guider must be
  rebuilt from its outputs.
- **Constraint:** MiniMax's DiT patch size is `(1, 2, 2)` and the conditioning patchify does not pad, so upscaled
  **height and width must stay even**. Avoid forced cache-empty or model-unload nodes between the two passes,
  especially with `--disable-dynamic-vram` plus a quantized H3 and SageAttention.

## Where to look for what is new

`github.com/wildminder/awesome-minimax-H3` is a maintained index of checkpoints, LoRAs, quants, VAE splits,
custom node packs and guides, updated daily during the current burst. Community workflow collections:
`reverentelusarca/minimax-h3-comfyui-workflows` on HuggingFace. Prefer these over chasing individual posts,
but verify any node or file name against its own repository before wiring it.

## Community performance reports (anecdote, not measured here)

- RTX 4090 Laptop, 16 GB VRAM + 32 GB RAM: 960x540, 5 s, 20 steps, pruned INT8 + NVFP4, **~182 s**.
- RTX 4080: 608x352, ~5.2 s of video, **~157 s**, peak VRAM **~9.5 GiB** with offload plus pruned INT8.
- RTX 5090 + 96 GB RAM running `ref2va_pruned_int8_convrot` with SageAttention for reference-to-video.
- Repeated reports that **20 steps can drop to 15** with little visible loss.

Low VRAM peaks depend on offload settings that trade speed for memory; none of this was measured here.

## Content behaviour

The safety guardrails described on the model card are part of the **hosted** pipeline (automated moderation of
submitted material and enhanced prompts). The open weights carry no such filter, and anatomical fidelity holds
in the image and reference paths. The licence's acceptable-use terms still govern what you generate; MiniMax
claims no rights over outputs and places responsibility on the user.
