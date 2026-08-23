#!/usr/bin/env python3
"""Analyze shot takes, salvage best candidates, and build a stitch + B-roll plan.

Reads:
  manifests/project_bible.json
  manifests/scene_plan.json
  manifests/shot_manifest.json

Writes:
  resolve/handoff/salvage_edit_plan.json
  resolve/handoff/salvage_take_scores.csv
  resolve/handoff/broll_requests.json

Usage:
  python salvage_stitch_plan.py --project-root "D:/comfy-studio-projects/my-short"
  python salvage_stitch_plan.py --project-root "D:/comfy-studio-projects/my-short" --min-score 55
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ASSET_KEYS = ("video_chunk", "dialog_stem", "music_stem", "sfx_stem", "subtitle_srt")


@dataclass
class TakeScore:
    shot_id: str
    take_id: str
    status: str
    score: float
    continuity_pass: bool
    sync_pass: bool
    nsfw_pass: bool
    has_video: bool
    has_dialog: bool
    notes: str
    video_chunk: str


def _load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _safe(value: Any) -> str:
    return "" if value is None else str(value)


def _exists(root: Path, rel: str) -> bool:
    return bool(rel) and (root / rel).is_file()


def _idx(value: Any, default: int = 0) -> int:
    if isinstance(value, int):
        return value
    s = _safe(value)
    m = re.search(r"(\d+)$", s)
    return int(m.group(1)) if m else default


def _score_take(project_root: Path, shot: dict[str, Any], take: dict[str, Any]) -> TakeScore:
    shot_id = _safe(shot.get("shot_id"))
    take_id = _safe(take.get("take_id")) or f"{shot_id}_take_master"
    status = _safe(take.get("status") or shot.get("status") or "candidate")

    assets = take.get("assets") or {}
    qc = take.get("qc") or {}
    notes = "; ".join(_safe(x) for x in (qc.get("notes") or []))

    has_video = _exists(project_root, _safe(assets.get("video_chunk")))
    has_dialog = _exists(project_root, _safe(assets.get("dialog_stem")))
    has_music = _exists(project_root, _safe(assets.get("music_stem")))
    has_sfx = _exists(project_root, _safe(assets.get("sfx_stem")))
    has_sub = _exists(project_root, _safe(assets.get("subtitle_srt")))

    continuity_pass = bool(qc.get("continuity_pass"))
    sync_pass = bool(qc.get("sync_pass"))
    nsfw_pass = bool(qc.get("nsfw_pass"))

    score = 0.0
    if has_video:
        score += 25
    if has_dialog:
        score += 10
    if has_music:
        score += 4
    if has_sfx:
        score += 4
    if has_sub:
        score += 2

    if continuity_pass:
        score += 25
    if sync_pass:
        score += 20
    if nsfw_pass:
        score += 15

    target_dur = float(shot.get("duration_seconds", 0.0) or 0.0)
    take_dur = float(take.get("duration_seconds", target_dur) or target_dur)
    drift = abs(target_dur - take_dur)
    score -= min(15.0, drift * 5.0)

    if status.lower() in {"rejected", "outtake"}:
        score -= 25
    if not has_video:
        score -= 40

    return TakeScore(
        shot_id=shot_id,
        take_id=take_id,
        status=status,
        score=round(score, 2),
        continuity_pass=continuity_pass,
        sync_pass=sync_pass,
        nsfw_pass=nsfw_pass,
        has_video=has_video,
        has_dialog=has_dialog,
        notes=notes,
        video_chunk=_safe(assets.get("video_chunk")),
    )


def _iter_takes(shot: dict[str, Any]) -> list[dict[str, Any]]:
    takes = shot.get("takes")
    if isinstance(takes, list) and takes:
        return takes

    # Backward compatibility with older single-asset shot manifest.
    return [
        {
            "take_id": f"{_safe(shot.get('shot_id'))}_take_master",
            "status": shot.get("status", "candidate"),
            "duration_seconds": shot.get("duration_seconds"),
            "assets": shot.get("assets", {}),
            "qc": shot.get("qc", {}),
        }
    ]


def _broll_prompt(scene_title: str, location_name: str, shot: dict[str, Any], reason: str) -> str:
    action = _safe(shot.get("action"))
    camera = _safe(shot.get("camera"))
    return (
        f"Cinematic B-roll for {scene_title} at {location_name}. "
        f"Match established lighting and character continuity. Camera: {camera}. "
        f"Action cue: {action}. Purpose: {reason}. No subtitles, no logos."
    )


def build(project_root: Path, min_score: float) -> dict[str, Any]:
    manifests = project_root / "manifests"
    handoff = project_root / "resolve" / "handoff"
    handoff.mkdir(parents=True, exist_ok=True)

    bible = _load_json(manifests / "project_bible.json")
    scene_plan = _load_json(manifests / "scene_plan.json")
    shot_manifest = _load_json(manifests / "shot_manifest.json")

    locations = {
        _safe(loc.get("location_id")): _safe(loc.get("name"))
        for loc in (bible.get("locations") or [])
    }
    scene_map = {
        _safe(s.get("scene_id")): {
            "title": _safe(s.get("title") or s.get("scene_id")),
            "location_id": _safe(s.get("location_id")),
        }
        for s in (scene_plan.get("scenes") or [])
    }

    all_scores: list[TakeScore] = []
    timeline: list[dict[str, Any]] = []
    broll_requests: list[dict[str, Any]] = []
    broll_counter = 0

    shots = sorted((shot_manifest.get("shots") or []), key=lambda x: int(x.get("order", 0) or 0))
    for shot in shots:
        shot_id = _safe(shot.get("shot_id"))
        scene_id = _safe(shot.get("scene_id"))
        shot_idx = int(shot.get("shot_idx", _idx(shot_id, 0)) or 0)
        scene_idx = int(shot.get("scene_idx", _idx(scene_id, 0)) or 0)
        shot_order = int(shot.get("order", 0) or 0)
        target_dur = float(shot.get("duration_seconds", 0.0) or 0.0)
        scene_meta = scene_map.get(scene_id, {"title": scene_id or "scene", "location_id": ""})
        location_name = locations.get(scene_meta["location_id"], scene_meta["location_id"] or "the location")

        take_scores = [_score_take(project_root, shot, t) for t in _iter_takes(shot)]
        all_scores.extend(take_scores)
        best = max(take_scores, key=lambda t: t.score)

        if best.score >= min_score and best.has_video and best.nsfw_pass and best.continuity_pass:
            mode = "use_take"
            if not best.sync_pass:
                mode = "use_take_retime_audio"
            timeline.append(
                {
                    "shot_id": shot_id,
                    "shot_idx": shot_idx,
                    "scene_id": scene_id,
                    "scene_idx": scene_idx,
                    "order": shot_order,
                    "duration_seconds": target_dur,
                    "mode": mode,
                    "selected_take_id": best.take_id,
                    "video_chunk": best.video_chunk,
                    "notes": best.notes,
                }
            )
            continue

        # No usable take: request B-roll salvage.
        reason = "salvage replacement for unusable/out-of-sync take"
        broll_idx = broll_counter
        broll_counter += 1
        scene_num = scene_idx + 1
        broll_num = broll_idx + 1
        broll_id = f"brol_s{scene_num:03d}_{broll_num:03d}"
        broll_rel = f"broll/{broll_id}.mp4"
        broll_requests.append(
            {
                "broll_idx": broll_idx,
                "broll_id": broll_id,
                "shot_idx": shot_idx,
                "shot_id": shot_id,
                "scene_idx": scene_idx,
                "scene_id": scene_id,
                "duration_seconds": max(1.0, target_dur),
                "purpose": "salvage_replacement",
                "prompt": _broll_prompt(scene_meta["title"], location_name, shot, reason),
                "status": "planned",
                "output_video": broll_rel,
            }
        )
        timeline.append(
            {
                "shot_id": shot_id,
                "shot_idx": shot_idx,
                "scene_id": scene_id,
                "scene_idx": scene_idx,
                "order": shot_order,
                "duration_seconds": target_dur,
                "mode": "replace_with_broll",
                "selected_take_id": "",
                "video_chunk": broll_rel,
                "notes": f"no take met min_score={min_score}",
            }
        )

    timeline = sorted(timeline, key=lambda x: x["order"])
    for i, entry in enumerate(timeline):
        entry["edit_seq"] = i
    plan = {
        "project": _safe(bible.get("project")),
        "title": _safe(bible.get("title")),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "min_score": min_score,
        "timeline": timeline,
        "summary": {
            "shots_total": len(timeline),
            "take_reuse": sum(1 for t in timeline if t["mode"] in {"use_take", "use_take_retime_audio"}),
            "broll_replacements": sum(1 for t in timeline if t["mode"] == "replace_with_broll"),
        },
    }

    (handoff / "salvage_edit_plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    (handoff / "broll_requests.json").write_text(
        json.dumps({"project": plan["project"], "requests": broll_requests}, indent=2) + "\n",
        encoding="utf-8",
    )

    with (handoff / "salvage_take_scores.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "shot_id",
                "take_id",
                "status",
                "score",
                "continuity_pass",
                "sync_pass",
                "nsfw_pass",
                "has_video",
                "has_dialog",
                "video_chunk",
                "notes",
            ]
        )
        for row in sorted(all_scores, key=lambda s: (s.shot_id, -s.score, s.take_id)):
            w.writerow(
                [
                    row.shot_id,
                    row.take_id,
                    row.status,
                    row.score,
                    row.continuity_pass,
                    row.sync_pass,
                    row.nsfw_pass,
                    row.has_video,
                    row.has_dialog,
                    row.video_chunk,
                    row.notes,
                ]
            )

    return {
        "plan_path": str((handoff / "salvage_edit_plan.json").resolve()),
        "scores_csv_path": str((handoff / "salvage_take_scores.csv").resolve()),
        "broll_requests_path": str((handoff / "broll_requests.json").resolve()),
        "summary": plan["summary"],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", required=True, help="Path to a scaffolded round-trip project root.")
    ap.add_argument("--min-score", type=float, default=55.0, help="Minimum score for take reuse.")
    args = ap.parse_args()

    out = build(Path(args.project_root).expanduser().resolve(), args.min_score)
    print(f"plan: {out['plan_path']}")
    print(f"scores: {out['scores_csv_path']}")
    print(f"broll: {out['broll_requests_path']}")
    print(f"summary: {out['summary']}")


if __name__ == "__main__":
    main()
