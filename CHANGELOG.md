# Changelog

All notable changes to **comfyui-agent-kit** are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow
[Semantic Versioning](https://semver.org/). Dates are YYYY-MM-DD. The raw, per-commit history lives in git;
this file is the curated summary.

## [Unreleased]

Nothing yet.

## [1.0.0] - 2026-06-21

The auto-start and session-protocol release: the agent can now run ComfyUI itself, and never loses your work.

### Added
- **Auto-start the ComfyUI server.** When `:8188` is down, the agent launches the headless server in the
  background and generates, no GUI required. The per-machine launch command is captured in the skill's machine
  block; the owner views a running server via `http://127.0.0.1:8188` in a browser.
- **Session protocol.** Ask the owner how to start ComfyUI (open it themselves vs agent starts headless), with a
  remembered preference; ALWAYS save every built or run workflow to `<ComfyUI>/user/default/workflows/` so it
  persists and the owner can open it later from the Workflows sidebar; hand over name, outputs, and how to view.
- **Configurable start policy for projects and pipelines.** Resolution order: env vars (`COMFY_HOST` /
  `COMFYUI_START_POLICY` / `COMFYUI_LAUNCH_CMD`) > project `.comfyui-agent.json` > skill machine block > ask.
  Ships `.comfyui-agent.example.json`.

### Fixed
- **Headless launch crash.** A custom node logs an emoji; under a non-UTF-8 console codepage (Windows cp1251) the
  server died on startup with a `UnicodeEncodeError`. Set `PYTHONUTF8=1` on the launch. Verified live.

### Changed
- README "What it can do" now lists auto-start and workflow persistence. Reconciled the "do not MCP-restart
  Desktop" gotcha with the new self-start capability (start the server yourself; the Desktop shortcut would start
  a conflicting second server on `:8188`).

## [0.3.0] - 2026-06-20

### Added
- **Workflow composition.** Assemble a new graph from templates and blueprint subgraphs, and wire the nodes
  correctly (output-to-input by type, with converters), validated against `/object_info`.
- **Shared-workflow fetch + model shootout.** `fetch_workflow.py` pulls any ComfyHub workflow by hash; the
  image-edit comparison grid runs a prompt through many models to pick the best. `docs/EXAMPLE_WORKFLOWS.md`.
- **MotionDeblur (restoration) IC-LoRA** and the **OpenRouter in-graph LLM node** (any model via one key).
- **Self-update mechanism.** `check_updates.py` diffs the template repo and reads the ComfyUI blog RSS; an
  optional weekly scheduled task adds recipes for new models. `docs/UPDATING.md`.
- Upscaler-choice and restore-chain ordering guidance (GAN vs diffusion; denoise before upscale).

### Changed
- README capabilities overview added; tagline byline on its own line; coverage tables merged and aligned.
- Stripped all em-dashes repo-wide (house writing canon: 0 long dashes).

## [0.2.0] - 2026-06-19

### Changed
- **Restructured into a multi-agent kit and renamed `comfyui-claude-kit` to `comfyui-agent-kit`** (the old URL
  redirects). One shared core (`shared/`) plus a thin adapter per agent (`agents/{claude,codex,gemini,qwen}`);
  GLM is covered through Claude Code. Per-agent matrix in `docs/AGENTS.md`.

## [0.1.0] - 2026-06-19

### Added
- Initial kit: the `comfyui` skill + stdlib `comfy_client.py`, the `comfyui-mcp` driver, the sparse-cloned 500+
  workflow-template library + quick index, the in-graph Claude nodes, and the node-building skills.
- **Per-model "mega-brain" (`MODELS.md`):** prompt recipes from official sources (grew to 65 models across
  image / video / audio / 3D) plus 17 enhancement and utility tools, auto-pulled when a model is named.
- **Full model index (`docs/MODEL_INDEX.md`):** all 147 library models classified (recipe / utility / template-only).
- **Hardware-aware model selection:** detect VRAM, RAM, and free disk, recommend the variant that fits, refuse a
  download that will not.
- House-style cover, real-data coverage charts, gracious credits, MIT, and full attribution.
