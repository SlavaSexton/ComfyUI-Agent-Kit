# ComfyUI known issues, fixes, and workarounds (living log)

Maintained weekly by the `comfyui-weekly-cycle` task from ComfyUI + frontend release notes and the issue tracker,
so the kit knows what is broken BEFORE building a workflow instead of wiring around a known-broken path and
repeating the same mistakes. Every row is sourced. Read this (and the "Real limits" section of
[`ADVANCED.md`](ADVANCED.md)) before assembling a non-trivial graph.

**Last updated: 2026-08-15** (statuses are as of this date and move as ComfyUI ships fixes). Current core release:
**v0.33.1** (2026-08-13; v0.32.0 landed 2026-08-11). **The `v0.33.0` TAG exists but no GitHub Release was
published for it** (`gh release view v0.33.0` answers "release not found" while the tag is in the tag list),
and the v0.33.1 notes compare against v0.32.0 directly. A tag and a Release are different objects; do not
read the gap as a missing version. Current frontend: **v1.51.6** (2026-08-16), the sixth 1.51.x point release
in six days.

**Read this first this week: v0.32.0 raised the PyTorch floor to 2.7.** "Minimum officially supported pytorch
is now 2.7" (PR 15413). A portable or hand-built install pinned to an older torch is no longer supported, and
that is the single change most likely to break an environment that has been working for months. Check with
`python -c "import torch; print(torch.__version__)"` before updating core.

**Last week's lead, still worth reading: v0.31.0 opened a MiniMax H3 bug cluster.** Several of these were
addressed in v0.32.0 and v0.33.1 (see Recently fixed); the untriaged ones below have not moved.

**The original note:** **Ten** separate H3 issues were filed
from the release date onward (counted 2026-08-09 by listing every issue whose title names H3 or MiniMax and
filtering to those created on or after 2026-08-08): noise output, sampler RuntimeError, 17-frame artifacts, an
unrecoverable VAE decode OOM, speaker-conditioning leakage, a roughly 2x slowdown, and more. That is more than
everything else in the window combined. The rows are below. If you are running H3 in production, hold at the version you have until this settles.

## Open: bites you when building or running

| Symptom | Cause | Workaround | Source |
|---|---|---|---|
| MiniMax H3 i2v output is pure noise / colour texture, no subject at all, on a 24 GB card | Open, reported 2026-08-08 with conditioning, weights and sampler all verified by the reporter before filing; not yet triaged | No published workaround. Before assuming your graph is wrong, check this issue: the reporter eliminated the usual suspects already | gh Comfy-Org/ComfyUI 15419 |
| MiniMax H3 sampler raises `RuntimeError` after updating to 0.31 | Open, reported 2026-08-08, two independent reports; no root cause published | Stay on the core version that worked for you until it is triaged | gh Comfy-Org/ComfyUI 15427 |
| MiniMax H3 shows periodic dark frames and a visible stutter at exactly 17-frame intervals | Open, reported 2026-08-08. The interval matches the video VAE's `clip_length=17` boundary; the reporter measured a ~30-unit brightness drop on every 17th frame across every sampler / scheduler / step / resolution combination, and MiniMax's own SGLang sample does not show it | None published. Treat H3 output as unsuitable for a hard cut on a 17-frame boundary until fixed | gh Comfy-Org/ComfyUI 15426 |
| MiniMax H3 dies in `VAEDecode` on long clips after paying the full sampling cost, and the tiled-decode retry does not help | Open, reported 2026-08-09. Two causes stack: `MiniMaxH3VideoVAE.decode_tiled()` just calls `decode()` (the VAE sets `handles_tiling = True` and tiles internally), so core's "retrying with tiled VAE decoding" path re-runs the identical decode; and under dynamic VRAM nothing is evicted for the decode, so streamed DiT and text-encoder weights stay resident | On a 16 GB card keep clips under about 209 frames, or decode in segments; do not count on the tiled fallback rescuing a long clip | gh Comfy-Org/ComfyUI 15453 |
| The official MiniMax H3 workflow takes roughly twice as long after updating to 0.31 | Open, reported 2026-08-09 (12 minutes to over 25 for the same 0.5 MP 15 s clip on an RTX 5080); no root cause published | Benchmark before and after updating if H3 throughput matters to you; no workaround yet | gh Comfy-Org/ComfyUI 15445 |
| `ImageUpscaleWithModel` fails on a 4 GB GPU with `Input type (torch.cuda.FloatTensor) and weight type ... should be the same` | Open, reported 2026-08-08; the low-VRAM path leaves the model and the tensor on different devices | Upscale on CPU, or free VRAM before the node runs | gh Comfy-Org/ComfyUI 15433 |
| Memory keeps climbing across runs when Load Checkpoint gets a model too large for the GPU | Open, reported 2026-08-08, two reactions; not yet triaged | Restart between large-model runs; prefer a quant that fits | gh Comfy-Org/ComfyUI 15431 |
| Kling legacy model options and the Kling Virtual Try-On node vanished from an existing graph | Removed on purpose in core **v0.31.0** (retired legacy models and the Virtual Try-On API) | Rebuild on a current Kling model option; Virtual Try-On has no in-core replacement | gh Comfy-Org/ComfyUI PR 15249 ; release v0.31.0 |
| Reve nodes still load but are marked deprecated, and the Reve templates disappeared | Deprecated on purpose in core **v0.31.0**: `ReveImageCreateNode` / `ReveImageEditNode` / `ReveImageRemixNode` all carry `is_deprecated=True`, and the four `api_reve_image_*` templates were deleted from the official library | Do not start new work on Reve; migrate to another image provider | gh Comfy-Org/ComfyUI PR 15331 ; `comfy_api_nodes/nodes_reve.py` on master |
| Mage-Flow output degrades at 2048x2048 on both Base and Turbo | Open, reported 2026-07-27 against the new v0.29.0 Mage-Flow support; the model card advertises native 512-2048, so this is a quality complaint, not a crash | Generate at 1024 to 1536 and upscale; treat 2K as experimental until it is triaged | gh Comfy-Org/ComfyUI 15099 |
| Any Ideogram 4 template dies on Apple Silicon with `NotImplementedError: The operator 'aten::_int_mm' is not currently implemented for the MPS device` | Open, reported 2026-07-29 with custom nodes disabled (M5 Max); the int8 path has no MPS kernel | Use the bf16 / fp8 weights rather than the int8 template on macOS, or run the API node instead of the local model | gh Comfy-Org/ComfyUI 15133 |
| `ImageBlend` in `difference` mode returns pure black wherever image1 is darker than image2 | Confirmed in source: `comfy_extras/nodes_post_processing.py` computes `img1 - img2` with no `abs()`, and the caller clamps to 0..1, so every negative pixel becomes exactly 0. Photoshop / GIMP / Krita all use `abs(img1 - img2)` | Order the inputs so image1 is the brighter one, or compute the difference twice (both orders) and add them | gh Comfy-Org/ComfyUI 15178 (open, reported 2026-07-31) |
| ComfyUI-LTXVideo still will not install or import on master | Same root cause as the row above (`interleaved_freqs_cis` removed by PR 15056); a second report landed 2026-07-29 and the original issue is STILL OPEN as of 2026-08-01 | Unchanged: stay on a stable tag until the pack updates; core LTX nodes work | gh Comfy-Org/ComfyUI 15070 (open), 15145 |
| Your own MCP server dies on `ModuleNotFoundError: No module named 'mcp.server.fastmcp'` after a fresh install, while the already-running instance is fine | The 2026-07-28 spec shipped Python SDK **2.0.0**, which renamed `FastMCP` to `MCPServer` and removed `mcp.server.fastmcp`. An unbounded pin like `mcp>=1.2.0` now resolves to 2.x | Pin `mcp>=1.28,<2`, or migrate: import `mcp.server.mcpserver.MCPServer` and pass `host` / `port` / `transport_security` / `stateless_http` to `run()` (they moved off the constructor and off `mcp.settings`, which now silently no-ops) | py.sdk.modelcontextprotocol.io/migration ; python-sdk release v2.0.0 (2026-07-28) |
| The whole ComfyUI-LTXVideo pack fails to import: `cannot import name 'interleaved_freqs_cis' from 'comfy.ldm.lightricks.model'` | Core commit `7c59a078d` (PR 15056, "use comfy kitchen rope functions in ltx models") removed that symbol; the pack imports it at the top of its `__init__` chain, so ALL its nodes disappear | Stay on the v0.28.0 stable tag rather than master until the pack updates; on master, the core LTX nodes still work, only the custom pack is dead | gh Comfy-Org/ComfyUI 15070 (open) ; 15086 (closed as DUPLICATE 2026-07-26) |
| Black / NaN image from an `int8_convrot` diffusion model on RDNA4 ROCm (gfx1201), while an int8 text encoder on the same box is fine | Open, reported 2026-07-26 against v0.28.0 + ROCm 7.2 / PyTorch 2.9.1; sampling completes, the NaN only surfaces as `invalid value encountered in cast` at save time | Use the fp8 or bf16 weights for the DIFFUSION model on ROCm; int8 text encoders are unaffected | gh Comfy-Org/ComfyUI 15084 |
| ComfyUI exits silently (no traceback) right after the Qwen text encoder loads, on Windows portable with PyTorch cu130 | Open, reported 2026-07-25; the same workflow on the same machine runs fine on a PyTorch cu12 build | Run Qwen Image Edit from a cu12 environment until it is triaged | gh Comfy-Org/ComfyUI 15074 |
| A Custom Combo inside a subgraph updates its string output but NOT its index output | Reported 2026-07-24; the reporter notes it breaks Comfy's own Blueprints and workflow templates, not just user graphs. **Closed as completed on 2026-08-09, but left here rather than promoted to "Recently fixed": the last comment on the issue says the error still reproduces after upgrading to the latest frontend.** Closed is not fixed until someone confirms it | Read the string output and map it to an index yourself, or lift the combo out of the subgraph | gh Comfy-Org/ComfyUI 15060 (closed COMPLETED 2026-08-09, contested in comments) |
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
| ComfyUI v0.33.1 | `Generate Text` ignored `thinking=false` on the Gemma 4 E2B / E4B encoders. This one matters for **LTX-2.5**: the shipped prompt-enhancer subgraph runs `TextGenerateLTX2Prompt` on `gemma4_e2b_it_bf16` with `thinking` off, so on v0.32.0 the enhancer was reasoning when it was told not to, burning its `max_length` budget on a block that gets stripped. | release v0.33.1 (PR 15278) |
| ComfyUI v0.33.1 | `KSamplerAdvanced` with `add_noise` disabled crashed on nested latents (kijai). Nested latents are how packed audio-plus-video latents are carried, so this hit LTX-AV and H3 graphs. | release v0.33.1 (PR 15447) |
| ComfyUI v0.33.1 | `float64` device error in the LTX diffusion decoder. | release v0.33.1 (PR 15516) |
| ComfyUI v0.33.1 | MiniMax Music 3 did not work on non-dynamic-VRAM setups; fixed in the same release that shipped the model. | release v0.33.1 (PR 15588) |
| ComfyUI v0.33.1 | `PreviewAny` escaped non-ASCII text inside dict and list previews, so any non-Latin prompt read back as escape codes. | release v0.33.1 (PR 15513) |
| ComfyUI v0.32.0 | **Three more MiniMax H3 fixes**: kijai's VAE optimisation (chunked encode / decode, so VRAM stops scaling with clip length), a `VAEDecodeTiled` crash on nested-tensor latents, and a peak-memory fix. Together these are the direct answer to the 16 GB "dies in VAEDecode on long clips" row above; if you are still working around it, update. | release v0.32.0 (PRs 15446, 15477, 15486) |
| ComfyUI v0.32.0 | Tiled audio decode was broken and is fixed. | release v0.32.0 (PR 15502) |
| ComfyUI v0.32.0 | Upscale models broke on non-dynamic-VRAM low-VRAM setups. | release v0.32.0 (PR 15437) |
| ComfyUI v0.32.0 | CLIP vision regression fixed. | release v0.32.0 (PR 15506) |
| ComfyUI v0.32.0 | **Minimum supported PyTorch raised to 2.7.** Not a bug fix: a floor change that can break an older environment on update. | release v0.32.0 (PR 15413) |
| ComfyUI v0.32.0 | **Correction to this kit.** Qwen Image 3.0 Pro's partner nodes (`QwenImageTextToImageApi`, `QwenImageEditApi`) shipped here. The kit previously stated they did not exist in open-source ComfyUI, which was true on 2026-08-09 and is false now. | release v0.32.0 (PR 15327) |
| ComfyUI v0.31.0 | **Five MiniMax H3 fixes in one release**: audio corruption when EasyCache was on; wrong noise-mask sampling; full offload broken on the audio VAE; raw parameters not cast to the input device in the H3 VAEs; and sampler failures on audio, which also gained support for more samplers. If you hit any of these on 0.30.x, update rather than working around them. | release v0.31.0 (PRs 15390, 15322, 15377, 15268, 15243) |
| ComfyUI v0.31.0 | MiniMax H3 gained `int8_convrot` VAE support, and asymmetric `w4a8_int` support landed alongside it. | release v0.31.0 (PRs 15334, 15308) |
| ComfyUI v0.31.0 | LTX and Wan sampling sped up (kijai). Not a bug fix, but it changes your timings, so re-benchmark before comparing against older numbers. | release v0.31.0 (PR 15138) |
| ComfyUI v0.30.0 | LTXAV crashed when sampling without an audio latent. | release v0.30.0 (PR 15132) |
| ComfyUI v0.30.0 | `user.css` loading, broken by PR 14734, was fixed again; SVG previews broken by the stored-XSS forced-download were also restored. | release v0.30.0 (PRs 15000, 15149) |
| ComfyUI v0.29.1 | User CSS silently stopped applying: `/api/userdata/user.css` was served as an attachment after PR 14734. | gh Comfy-Org/ComfyUI 15071 (closed COMPLETED) ; PR 15000 |
| ComfyUI v0.29.1 | SVG node outputs and Media Assets previews went blank: the stored-XSS hardening (GHSA-779p-m5rp-r4h4) forced every SVG to `application/octet-stream`. The fix exempts only `<img>` loads via `Sec-Fetch-Dest`, and pins `Vary: Sec-Fetch-Dest` + `Cache-Control: no-store` so a cache cannot replay an inline SVG into document context. | Comfy-Org/ComfyUI PR 15149 ; tag v0.29.1 (tagged, no GitHub Release page) |
| ComfyUI v0.29.0 | Video transcode buffered every frame in RAM (OOM on long clips); it now streams. | Comfy-Org/ComfyUI PR 14813 (CORE-351, CORE-353) ; release v0.29.0 |
| ComfyUI v0.29.0 | Mage-Flow failed on cards without bf16 support. Merged 2026-07-26 and listed in the v0.29.0 notes, so v0.29.0 and later already carry it. | Comfy-Org/ComfyUI PR 15081 ; release v0.29.0 |
| closed 2026-07-29 | Anima generation speed dropped on AMD R9700 after PR 14953. | gh Comfy-Org/ComfyUI 14968 (closed COMPLETED) |
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
