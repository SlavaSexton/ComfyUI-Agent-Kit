#!/usr/bin/env python3
"""Build a local bridge UI between ComfyUI outputs and DaVinci Resolve handoff.

Reads round-trip manifests, computes per-shot readiness/QC status, writes:
  - resolve/handoff/dashboard.html
  - resolve/handoff/resolve_shot_handoff.csv
  - resolve/handoff/bridge_summary.json

Optional --serve starts a local static server so the dashboard can stay open while you edit.

Usage:
  python roundtrip_bridge_ui.py --project-root "D:/comfy-studio-projects/my-short"
  python roundtrip_bridge_ui.py --project-root "D:/comfy-studio-projects/my-short" --serve --port 8787
"""
from __future__ import annotations

import argparse
import csv
import html
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any
import os


REQUIRED_RENDER_ASSETS = ("video_chunk", "dialog_stem")
QC_KEYS = ("continuity_pass", "sync_pass", "nsfw_pass")


@dataclass
class ShotRow:
    shot_idx: int
    scene_idx: int
    shot_id: str
    scene_id: str
    order: int
    status: str
    duration_seconds: float
    model: str
    video_chunk: str
    dialog_stem: str
    music_stem: str
    sfx_stem: str
    subtitle_srt: str
    storyboard_image: str
    continuity_pass: bool
    sync_pass: bool
    nsfw_pass: bool
    ready_for_resolve: bool
    notes: str


def _load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing required file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def _asset_exists(project_root: Path, rel: str) -> bool:
    if not rel:
        return False
    return (project_root / rel).is_file()


def _emoji(flag: bool) -> str:
    return "✅" if flag else "❌"


def _safe_str(value: Any) -> str:
    return "" if value is None else str(value)


def _normalize_shot(project_root: Path, shot: dict[str, Any]) -> ShotRow:
    assets = shot.get("assets") or {}
    qc = shot.get("qc") or {}
    notes = qc.get("notes") or []
    notes_text = "; ".join(_safe_str(n) for n in notes)

    required_ok = all(_asset_exists(project_root, _safe_str(assets.get(k))) for k in REQUIRED_RENDER_ASSETS)
    qc_ok = all(bool(qc.get(k)) for k in QC_KEYS)
    ready = required_ok and qc_ok

    return ShotRow(
        shot_idx=int(shot.get("shot_idx", 0) or 0),
        scene_idx=int(shot.get("scene_idx", 0) or 0),
        shot_id=_safe_str(shot.get("shot_id", "")),
        scene_id=_safe_str(shot.get("scene_id", "")),
        order=int(shot.get("order", 0) or 0),
        status=_safe_str(shot.get("status", "")),
        duration_seconds=float(shot.get("duration_seconds", 0.0) or 0.0),
        model=_safe_str(shot.get("model", "")),
        video_chunk=_safe_str(assets.get("video_chunk", "")),
        dialog_stem=_safe_str(assets.get("dialog_stem", "")),
        music_stem=_safe_str(assets.get("music_stem", "")),
        sfx_stem=_safe_str(assets.get("sfx_stem", "")),
        subtitle_srt=_safe_str(assets.get("subtitle_srt", "")),
        storyboard_image=_safe_str(assets.get("storyboard_image", "")),
        continuity_pass=bool(qc.get("continuity_pass")),
        sync_pass=bool(qc.get("sync_pass")),
        nsfw_pass=bool(qc.get("nsfw_pass")),
        ready_for_resolve=ready,
        notes=notes_text,
    )


def _render_dashboard(project_title: str, project_slug: str, stages: dict[str, Any], rows: list[ShotRow]) -> str:
    total = len(rows)
    ready = sum(1 for r in rows if r.ready_for_resolve)
    blocked = total - ready
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    stage_rows = "\n".join(
        f"<tr><td>{html.escape(k)}</td><td>{html.escape(_safe_str(v))}</td></tr>" for k, v in stages.items()
    )
    shot_rows = "\n".join(
        (
            "<tr>"
            f"<td>{r.shot_idx}</td>"
            f"<td>{r.scene_idx}</td>"
            f"<td>{html.escape(r.shot_id)}</td>"
            f"<td>{html.escape(r.scene_id)}</td>"
            f"<td>{r.order}</td>"
            f"<td>{html.escape(r.status)}</td>"
            f"<td>{r.duration_seconds:.2f}</td>"
            f"<td>{html.escape(r.model)}</td>"
            f"<td>{_emoji(bool(r.storyboard_image))}</td>"
            f"<td>{_emoji(bool(r.video_chunk))}</td>"
            f"<td>{_emoji(bool(r.dialog_stem))}</td>"
            f"<td>{_emoji(bool(r.subtitle_srt))}</td>"
            f"<td>{_emoji(r.continuity_pass)}</td>"
            f"<td>{_emoji(r.sync_pass)}</td>"
            f"<td>{_emoji(r.nsfw_pass)}</td>"
            f"<td>{_emoji(r.ready_for_resolve)}</td>"
            f"<td>{html.escape(r.notes)}</td>"
            "</tr>"
        )
        for r in rows
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta http-equiv="refresh" content="15" />
  <title>Round-trip Bridge UI - {html.escape(project_title)}</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 20px; background: #111; color: #ddd; }}
    h1, h2 {{ margin: 0 0 10px 0; }}
    .meta {{ margin-bottom: 12px; color: #aaa; }}
    .cards {{ display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }}
    .card {{ background: #1b1b1b; border: 1px solid #2a2a2a; border-radius: 8px; padding: 10px 14px; min-width: 170px; }}
    .card .k {{ color: #9aa0a6; font-size: 12px; }}
    .card .v {{ font-size: 24px; font-weight: 600; }}
    table {{ border-collapse: collapse; width: 100%; background: #171717; }}
    th, td {{ border: 1px solid #2b2b2b; padding: 8px; font-size: 12px; vertical-align: top; }}
    th {{ background: #202124; text-align: left; position: sticky; top: 0; }}
    .section {{ margin-top: 22px; }}
  </style>
</head>
<body>
  <h1>Bridge UI: ComfyUI -> Resolve</h1>
  <div class="meta">Project: <b>{html.escape(project_title)}</b> ({html.escape(project_slug)}) | Last build: {now}</div>

  <div class="cards">
    <div class="card"><div class="k">Total shots</div><div class="v">{total}</div></div>
    <div class="card"><div class="k">Ready for Resolve</div><div class="v">{ready}</div></div>
    <div class="card"><div class="k">Blocked / needs fixes</div><div class="v">{blocked}</div></div>
  </div>

  <div class="section">
    <h2>Pipeline stage status</h2>
    <table><thead><tr><th>Stage</th><th>Status</th></tr></thead><tbody>{stage_rows}</tbody></table>
  </div>

  <div class="section">
    <h2>Shot handoff matrix</h2>
    <table>
      <thead>
        <tr>
          <th>shot_idx</th><th>scene_idx</th><th>shot_id</th><th>scene</th><th>order</th><th>status</th><th>sec</th><th>model</th>
          <th>storyboard</th><th>video</th><th>dialog</th><th>sub</th>
          <th>continuity</th><th>sync</th><th>nsfw</th><th>ready</th><th>notes</th>
        </tr>
      </thead>
      <tbody>
        {shot_rows}
      </tbody>
    </table>
  </div>
</body>
</html>
"""


def build_ui(project_root: Path) -> dict[str, Any]:
    manifests = project_root / "manifests"
    handoff = project_root / "resolve" / "handoff"
    handoff.mkdir(parents=True, exist_ok=True)

    bible = _load_json(manifests / "project_bible.json")
    shot_manifest = _load_json(manifests / "shot_manifest.json")
    state = _load_json(manifests / "roundtrip_state.json")

    shots_raw = shot_manifest.get("shots") or []
    rows = sorted((_normalize_shot(project_root, s) for s in shots_raw), key=lambda x: (x.order, x.shot_id))

    csv_path = handoff / "resolve_shot_handoff.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "shot_idx",
                "scene_idx",
                "shot_id",
                "scene_id",
                "order",
                "status",
                "duration_seconds",
                "model",
                "video_chunk",
                "dialog_stem",
                "music_stem",
                "sfx_stem",
                "subtitle_srt",
                "storyboard_image",
                "continuity_pass",
                "sync_pass",
                "nsfw_pass",
                "ready_for_resolve",
                "notes",
            ]
        )
        for r in rows:
            w.writerow(
                [
                    r.shot_idx,
                    r.scene_idx,
                    r.shot_id,
                    r.scene_id,
                    r.order,
                    r.status,
                    r.duration_seconds,
                    r.model,
                    r.video_chunk,
                    r.dialog_stem,
                    r.music_stem,
                    r.sfx_stem,
                    r.subtitle_srt,
                    r.storyboard_image,
                    r.continuity_pass,
                    r.sync_pass,
                    r.nsfw_pass,
                    r.ready_for_resolve,
                    r.notes,
                ]
            )

    summary = {
        "project": _safe_str(bible.get("project")),
        "title": _safe_str(bible.get("title")),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_shots": len(rows),
        "ready_for_resolve": sum(1 for r in rows if r.ready_for_resolve),
        "blocked_shots": sum(1 for r in rows if not r.ready_for_resolve),
        "stages": state.get("stages") or {},
        "dashboard_html": str((handoff / "dashboard.html").resolve()),
        "resolve_handoff_csv": str(csv_path.resolve()),
    }
    (handoff / "bridge_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    html_text = _render_dashboard(
        project_title=summary["title"] or "project",
        project_slug=summary["project"] or "project",
        stages=summary["stages"],
        rows=rows,
    )
    (handoff / "dashboard.html").write_text(html_text, encoding="utf-8")
    return summary


def serve(project_root: Path, port: int) -> None:
    os.chdir(project_root)
    server = ThreadingHTTPServer(("127.0.0.1", port), SimpleHTTPRequestHandler)
    print(f"serving: http://127.0.0.1:{port}/resolve/handoff/dashboard.html")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", required=True, help="Path to a scaffolded round-trip project root.")
    ap.add_argument("--serve", action="store_true", help="Serve the project folder for live dashboard viewing.")
    ap.add_argument("--port", type=int, default=8787, help="Port for --serve mode (default: 8787).")
    args = ap.parse_args()

    project_root = Path(args.project_root).expanduser().resolve()
    summary = build_ui(project_root)
    print(f"dashboard: {summary['dashboard_html']}")
    print(f"handoff_csv: {summary['resolve_handoff_csv']}")

    if args.serve:
        serve(project_root, args.port)


if __name__ == "__main__":
    main()
