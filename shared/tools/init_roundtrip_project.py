#!/usr/bin/env python3
"""Initialize a ComfyUI <-> DaVinci Resolve round-trip project scaffold.

Creates a persistent folder contract and starter manifests so storyboard assets, shot chunks,
audio stems, QC reports, and Resolve handoff files stay organized and re-runnable.

Usage:
    python init_roundtrip_project.py --project "my_short"
    python init_roundtrip_project.py --project "my_short" --root "D:/AIStudio" --scenes 3
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def _slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return slug or "project"


def _write_json(path: Path, data: object, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_project(root: Path, project_name: str, scenes: int, force: bool) -> Path:
    project_slug = _slug(project_name)
    base = root / project_slug

    dirs = [
        "storyboards",
        "broll",
        "shots/pending",
        "shots/rejected",
        "approved/video_chunks",
        "approved/audio_dialog",
        "approved/audio_music",
        "approved/audio_sfx",
        "approved/subtitles",
        "qc_reports",
        "manifests",
        "resolve/handoff",
        "final",
        "cache",
    ]
    for rel in dirs:
        (base / rel).mkdir(parents=True, exist_ok=True)

    project_bible = {
        "project": project_slug,
        "title": project_name,
        "naming": {
            "index_base": 0,
            "zero_pad": 3,
            "scene_id": "scene_{scene_idx:03d}",
            "shot_id": "shot_{shot_idx:03d}",
            "take_id": "shot_{shot_idx:03d}_take_{take_idx:03d}",
            "line_id": "line_s{scene_num:03d}_{line_num:03d}",
            "broll_id": "brol_s{scene_num:03d}_{broll_num:03d}",
            "chunk_filename": "sc{scene_idx:03d}_sh{shot_idx:03d}_tk{take_idx:03d}.mp4",
            "dialog_filename": "sc{scene_idx:03d}_sh{shot_idx:03d}_tk{take_idx:03d}_dialog.wav",
            "music_filename": "sc{scene_idx:03d}_sh{shot_idx:03d}_tk{take_idx:03d}_music.wav",
            "sfx_filename": "sc{scene_idx:03d}_sh{shot_idx:03d}_tk{take_idx:03d}_sfx.wav",
            "subtitle_filename": "sc{scene_idx:03d}_sh{shot_idx:03d}_tk{take_idx:03d}.srt",
        },
        "fps": 24,
        "target_resolution": "1280x720",
        "continuity_rules": {
            "persistent_characters": True,
            "persistent_locations": True,
            "allow_costume_changes": False,
        },
        "characters": [
            {
                "character_id": "char_001",
                "name": "Lead",
                "reference_images": [],
                "voice_id": "voice_lead",
                "wardrobe_lock": "Set primary outfit and keep stable unless script change is explicit.",
            }
        ],
        "locations": [
            {
                "location_id": "loc_001",
                "name": "Primary Location",
                "reference_images": [],
                "lighting_profile": "soft cinematic",
            }
        ],
    }
    _write_json(base / "manifests/project_bible.json", project_bible, force)

    scene_plan = {
        "project": project_slug,
        "scenes": [
            {
                "scene_idx": i,
                "scene_id": f"scene_{i:03d}",
                "title": f"Scene {i + 1}",
                "location_id": "loc_001",
                "status": "planned",
            }
            for i in range(0, max(1, scenes))
        ],
    }
    _write_json(base / "manifests/scene_plan.json", scene_plan, force)

    shot_manifest = {
        "project": project_slug,
        "shots": [
            {
                "shot_idx": 0,
                "scene_idx": 0,
                "shot_id": "shot_000",
                "scene_id": "scene_000",
                "order": 0,
                "status": "planned",
                "duration_seconds": 3.0,
                "camera": "medium shot",
                "action": "Describe action",
                "dialog": "Add dialog line",
                "seed": 0,
                "model": "",
                "prompt": "",
                "negative_prompt": "",
                "assets": {
                    "storyboard_image": "storyboards/sc000_sh000_board.png",
                    "video_chunk": "approved/video_chunks/sc000_sh000_tk000.mp4",
                    "dialog_stem": "approved/audio_dialog/sc000_sh000_tk000_dialog.wav",
                    "music_stem": "approved/audio_music/sc000_sh000_tk000_music.wav",
                    "sfx_stem": "approved/audio_sfx/sc000_sh000_tk000_sfx.wav",
                    "subtitle_srt": "approved/subtitles/sc000_sh000_tk000.srt",
                },
                "takes": [
                    {
                        "take_idx": 0,
                        "take_id": "shot_000_take_000",
                        "status": "candidate",
                        "duration_seconds": 3.0,
                        "assets": {
                            "video_chunk": "approved/video_chunks/sc000_sh000_tk000.mp4",
                            "dialog_stem": "approved/audio_dialog/sc000_sh000_tk000_dialog.wav",
                            "music_stem": "approved/audio_music/sc000_sh000_tk000_music.wav",
                            "sfx_stem": "approved/audio_sfx/sc000_sh000_tk000_sfx.wav",
                            "subtitle_srt": "approved/subtitles/sc000_sh000_tk000.srt",
                        },
                        "qc": {
                            "continuity_pass": False,
                            "sync_pass": False,
                            "nsfw_pass": False,
                            "notes": [],
                        },
                    }
                ],
                "qc": {
                    "continuity_pass": False,
                    "sync_pass": False,
                    "nsfw_pass": False,
                    "notes": [],
                },
                "broll_needed": False,
                "broll_notes": "",
            }
        ],
    }
    _write_json(base / "manifests/shot_manifest.json", shot_manifest, force)

    dialog_script = {
        "project": project_slug,
        "lines": [
            {
                "line_idx": 0,
                "line_id": "line_s001_001",
                "scene_idx": 0,
                "scene_id": "scene_000",
                "shot_idx": 0,
                "shot_id": "shot_000",
                "character_id": "char_001",
                "start_timecode": "00:00:00:00",
                "text": "Replace with final dialogue.",
            }
        ],
    }
    _write_json(base / "manifests/dialog_script.json", dialog_script, force)

    broll_manifest = {
        "project": project_slug,
        "requests": [
            {
                "broll_idx": 0,
                "broll_id": "brol_s001_001",
                "scene_idx": 0,
                "scene_id": "scene_000",
                "duration_seconds": 2.0,
                "purpose": "transition",
                "prompt": "Cinematic establishing B-roll for the scene location, matching lighting and mood.",
                "status": "planned",
                "output_video": "broll/brol_s001_001.mp4",
            }
        ],
    }
    _write_json(base / "manifests/broll_manifest.json", broll_manifest, force)

    state = {
        "project": project_slug,
        "stages": {
            "storyboard": "not_started",
            "shot_generation": "not_started",
            "audio_stems": "not_started",
            "qc": "not_started",
            "resolve_edit": "not_started",
            "final_render": "not_started",
        },
    }
    _write_json(base / "manifests/roundtrip_state.json", state, force)

    instructions = (
        "ComfyUI <-> Resolve round-trip\n"
        "=============================\n\n"
        "1. Generate storyboard images into storyboards/ and update manifests/shot_manifest.json.\n"
        "2. Generate video chunks/audio stems into approved/ once each shot passes QC.\n"
        "3. In Resolve, create a project and import approved/video_chunks plus approved/audio_* stems.\n"
        "4. Keep Resolve media linked to this folder. When a shot is regenerated with the same filename,\n"
        "   relink/update in Resolve instead of rebuilding the timeline.\n"
        "5. For outtakes/sync issues, run salvage planner + B-roll request builder:\n"
        "   python shared/tools/salvage_stitch_plan.py --project-root <this project folder>\n"
        "6. Build bridge UI + handoff CSV:\n"
        "   python shared/tools/roundtrip_bridge_ui.py --project-root <this project folder>\n"
        "7. Export review cut to final/, log issues in qc_reports/, regenerate only failing shots.\n"
        "8. Lock cut -> final master render to final/.\n"
    )
    _write_text(base / "resolve/roundtrip_instructions.txt", instructions, force)
    return base


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, help="Project name (used to build folder + manifest ids).")
    ap.add_argument(
        "--root",
        default=str(Path.home() / "comfy-studio-projects"),
        help="Parent folder where the project scaffold will be created.",
    )
    ap.add_argument("--scenes", type=int, default=1, help="How many starter scenes to pre-create in scene_plan.")
    ap.add_argument("--force", action="store_true", help="Overwrite starter manifest/template files if they exist.")
    args = ap.parse_args()

    created = build_project(Path(args.root).expanduser(), args.project, args.scenes, args.force)
    print(f"initialized: {created}")
    print("next: point ComfyUI Save* nodes and Resolve media bins to this project folder.")


if __name__ == "__main__":
    main()
