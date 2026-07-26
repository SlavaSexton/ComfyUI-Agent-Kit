# ComfyUI known issues, fixes, and workarounds (living log)

Maintained weekly by the `comfyui-weekly-cycle` task from ComfyUI + frontend release notes and the issue tracker,
so the kit knows what is broken BEFORE building a workflow instead of wiring around a known-broken path and
repeating the same mistakes. Every row is sourced. Read this (and the "Real limits" section of
[`ADVANCED.md`](ADVANCED.md)) before assembling a non-trivial graph.

**Last updated: 2026-07-25** (statuses are as of this date and move as ComfyUI ships fixes). Current core release:
**v0.28.0** (2026-07-15, unchanged this week); current frontend: **v1.48.5** (2026-07-23).

## Open: bites you when building or running

| Symptom | Cause | Workaround | Source |
|---|---|---|---|
| The whole ComfyUI-LTXVideo pack fails to import: `cannot import name 'interleaved_freqs_cis' from 'comfy.ldm.lightricks.model'` | Core commit `7c59a078d` (PR 15056, "use comfy kitchen rope functions in ltx models") removed that symbol; the pack imports it at the top of its `__init__` chain, so ALL its nodes disappear | Stay on the v0.28.0 stable tag rather than master until the pack updates; on master, the core LTX nodes still work, only the custom pack is dead | gh Comfy-Org/ComfyUI 15086, 15070 (both opened 2026-07-25/26) |
| Black / NaN image from an `int8_convrot` diffusion model on RDNA4 ROCm (gfx1201), while an int8 text encoder on the same box is fine | Open, reported 2026-07-26 against v0.28.0 + ROCm 7.2 / PyTorch 2.9.1; sampling completes, the NaN only surfaces as `invalid value encountered in cast` at save time | Use the fp8 or bf16 weights for the DIFFUSION model on ROCm; int8 text encoders are unaffected | gh Comfy-Org/ComfyUI 15084 |
| ComfyUI exits silently (no traceback) right after the Qwen text encoder loads, on Windows portable with PyTorch cu130 | Open, reported 2026-07-25; the same workflow on the same machine runs fine on a PyTorch cu12 build | Run Qwen Image Edit from a cu12 environment until it is triaged | gh Comfy-Org/ComfyUI 15074 |
| A Custom Combo inside a subgraph updates its string output but NOT its index output | Open, reported 2026-07-24; the reporter notes it breaks Comfy's own Blueprints and workflow templates, not just user graphs | Read the string output and map it to an index yourself, or lift the combo out of the subgraph | gh Comfy-Org/ComfyUI 15060 |
| PC crashes (whole machine) when running an int8 model | Open, unresolved as of 2026-07-18; no root cause published yet | Fall back to fp8 / bf16 for that model until it is triaged; int8 is fast but not yet bulletproof | gh comfyanonymous/ComfyUI 14985 (opened 2026-07-18) |
| Black image on Turing (RTX 20xx) with int4 models | int4-convrot path on Turing | FIXED in v0.28.0 (PR 14864) - update core before blaming the quant | gh Comfy-Org/ComfyUI PR 14864 ; release v0.28.0 |
| Nodes Manager extensions stop working after updating to 0.28.0 | Open, reported 2026-07-17 against the v0.28.0 update | Watch the issue; no published workaround yet | gh comfyanonymous/ComfyUI 14967 |
| SeedVR2 shows no temporal consistency on video | Open, reported 2026-07-17 against the new native SeedVR2 support | Treat native SeedVR2 as image-first for now; for video check the issue before relying on it | gh comfyanonymous/ComfyUI 14970 |
| `IdeogramV1` / `IdeogramV2` nodes missing from an older graph | Both nodes were REMOVED in core v0.28.0 | Rebuild the graph on `IdeogramV3` / `IdeogramV4` | gh Comfy-Org/ComfyUI PR 14712 ; release v0.28.0 |
| StabilityAI partner nodes missing | All StabilityAI nodes were REMOVED in core v0.28.0 | Use another provider's partner nodes, or a local Stable Diffusion checkpoint | gh Comfy-Org/ComfyUI PR 14737 ; release v0.28.0 |
| Black or NaN images after decode | fp16 VAE overflow (esp. SD1.5's fp32-trained VAE; also some fp8 models) | `--fp32-vae` (or `--bf16-vae`); VAE on CPU | gh comfyanonymous/ComfyUI 13116, 2229 ; cli_args.py |
| Color/contrast shift, worse over repeated passes | lossy VAE round-trip; tiled decode auto-triggers under VRAM pressure | encode once, stay in latent, decode once; histogram/LAB match to the source plate | gh 500 |
| A custom node never re-runs | `IS_CHANGED` returning `True` reads as unchanged (`True == True`) | the node must `return float("NaN")` to force a rerun | docs custom-nodes/backend/server_overview |
| Hit Queue, nothing happens (runs in ~0.05s) | stale cache served after a seed change | bust an input, or `--cache-classic` | gh 11905 |
| Per-gen model reload thrash / slower on 4090-5090 | Dynamic VRAM (default since ~Mar 2026) regressions | `--disable-dynamic-vram` still works, but the maintainer now discourages it: prefer switching to a native fp8/int8 model format | Comfy-Org/ComfyUI discussion 12699 ; desktop 1741 ; gh 14577 (v0.26.0) |
| Run button greys out, "workflow contains unsupported nodes", when any non-core node is in a tab | frontend does not re-evaluate node support across tab switches / new tabs | reload the page, or switch to another tab and back; the graph still runs if you copy-paste its nodes into an already-enabled tab | gh Comfy-Org/ComfyUI_frontend 6766 (open, assigned) |
| `--lowvram` / `--novram` still OOM at slightly higher res | offload granularity does not cover peak activations | tiled VAE decode, lower res, `--cache-none` | cli_args.py ; gh 5 |
| Single-digit canvas fps on a big graph | litegraph renders all on Canvas2D | collapse into subgraphs, mute/collapse groups, lower link-render quality | gh 7322, 4017 |
| Nested/linked subgraphs break after a browser refresh | subgraph load order is list- not dependency-resolved | save often, avoid deep nesting, keep a `.json` backup | gh 10522 ; frontend 6639, 9979 |
| Half your custom nodes break after an update | numpy 1.x->2.x ABI, or core moved an internal symbol nodes import | pin `numpy<2`; wait for the node author or roll core back | gh 9156, 11660 |
| pip clobbers a working torch when installing a node | dependency conflicts; node deps overwrite shared versions | per-pack venvs, loosen exact pins, a constraints file | docs/development/core-concepts/dependencies ; gh 8882 ; Manager 1136 |
| Output not reproducible even on one machine | ComfyUI is not fully deterministic | `--deterministic` (slower); pin node versions for cross-machine | gh 375 ; discussion 118 |
| A downloaded workflow fails to load entirely | one missing custom node blocks the whole graph; PNG metadata stripped on re-encode | Manager "Install Missing Custom Nodes"; share the `.json`, not a screenshot | gh 6844 |

## Security

- Real malware has shipped through the custom-node channel (ComfyUI_LLMVISION, ultralytics, and Akira-Stealer registry packages). Install only from verified Registry authors; the Registry scans at publish but coverage is partial. (blog/comfyui-2025-jan-security-update ; gh 11791)

## Recently fixed / changed

| Fixed in | Symptom | Source |
|---|---|---|
| ComfyUI v0.28.0 | **Four security vulnerabilities** closed (advisory GHSA-779p-m5rp-r4h4). Update; do not stay on an older core if you expose ComfyUI beyond localhost. | gh Comfy-Org/ComfyUI PR 14734 ; GHSA-779p-m5rp-r4h4 |
| ComfyUI v0.28.0 | Crash on videos with an undecodable audio stream; crash in `UNetSelfAttentionMultiply`; Load3D path-validation failure from double path resolution; Qwen3-VL tokenizer crash with custom embeddings; wrong HLG inverse-OETF clamp in `hlg_to_linear` (colour-relevant). | release v0.28.0 (PRs 14746, 14823, 14852, 14713, 14762) |
| ComfyUI v0.28.0 | **Dropped PyTorch 2.4 support** (gqa now on all attention backends). Not a bug, but it breaks old environments: upgrade PyTorch before upgrading core. | gh Comfy-Org/ComfyUI PR 14772 ; release v0.28.0 |
| ComfyUI v0.27.0 | INT8 (`*_convrot_simple`) model + LoRA degraded quality / memory leak: on offload the re-quant dropped the convrot per-channel params and re-quantized tensorwise. INT8 support itself landed in v0.27.0; these early bugs were fixed within the same release, so use v0.27.0+ (not the nightlies in between). | gh comfyanonymous/ComfyUI 14642 ; PRs 14650, 14669, 14697 ; release v0.27.0 |
| frontend (closed 2026-06-30) | Comfy Manager button invisible on the canvas since frontend 1.47.3. Fix merged; on the 1.47.x line update to the latest patch, or use the 1.45.20 frontend that stable ComfyUI 0.27.0 pins. | gh Comfy-Org/ComfyUI_frontend 13175 |

## How this file is maintained

The `comfyui-weekly-cycle` task (Saturday) reads new `Comfy-Org/ComfyUI` and `Comfy-Org/ComfyUI_frontend`
releases and recently closed/opened issues since the "Last updated" date, then: moves anything the release notes
mark FIXED into "Recently fixed" (with the version), adds genuinely new high-signal bugs to "Open" with a one-line
workaround, and bumps the date. Every row keeps a source (issue / PR / release URL). Still-open entries are not
deleted; only confirmed bugs are recorded (no speculation).

Two gotchas that cost a cycle each. **`comfyanonymous/ComfyUI` now redirects to `Comfy-Org/ComfyUI`**: `gh issue
list` and `gh release list` follow the redirect, but the SEARCH API does not and answers `422 Validation Failed`.
Query the canonical name. And **a closed issue is not a fixed issue**: check `stateReason`, since
`NOT_PLANNED` (stale-bot or won't-fix) closures are the majority here and must not be promoted into "Recently fixed".
On 2026-07-25 four of the five closures in the window were `NOT_PLANNED`.
