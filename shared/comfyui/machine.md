# Your machine

**This file is yours, not the kit's.** It holds the facts about THIS install: where ComfyUI lives, what GPUs
are in the box, how to start the server when it is down. The installer creates it once and then never touches
it again, so a `git pull` plus a reinstall cannot wipe what the bootstrap learned. Nothing here ships back to
the repo.

**If the values below are still angle brackets, the bootstrap has not run.** Run it on the first ComfyUI task:
call the MCP `health_check` (or `comfy_client.alive()` plus `GET /system_stats` and `/object_info`) and rewrite
this file with the real values. See `BOOTSTRAP.md`. Do not assume another machine matches an example.

- **ComfyUI**: `<Desktop or source install>`, core path `<detect>`, API at **`http://127.0.0.1:8188`**
  (alive when the server or app is running). Check: `GET /system_stats` -> 200.
- **GPUs**: `<N>x <model>` (`cuda:0`, `cuda:1`, ...). VRAM per card `<detect>`.
- **Models installed** (query live, never hardcode): `GET /object_info/UNETLoader`,
  `/object_info/CheckpointLoaderSimple`, `/object_info/CLIPLoader`, `/object_info/VAELoader`.
- **Shared models dir / extra_model_paths**: `<detect from the startup log or extra_model_paths.yaml>`.
- **GUI workflows folder** (the bridge back to the app): `<ComfyUI>/user/default/workflows/`.
- **Template library**: `<path to the workflow_templates clone>`. This one is load-bearing and easy to skip:
  `TASKS.md` opens every job by reading `templates/_quick_index.json` under this path, so leaving it blank
  makes step 1 of every recipe dead. The installer's default target is
  `~/comfyui-agent-kit-data/workflow_templates`; if you cloned it somewhere else, write that path here.
- **Launch command** (to start the server headlessly when :8188 is down): `<detect>`. For a source install
  that is `python main.py` in the ComfyUI dir; for Desktop it is the venv python plus `main.py` plus
  `--base-directory` or `--extra-model-paths-config`.
- **Known local quirks**: `<anything this machine does that the docs do not predict>`. Record them as you hit
  them. This is the half of the file that saves the most time later.
