#!/usr/bin/env python3
"""Build templates/_quick_index.json from the official templates/index.json.

The Comfy-Org workflow_templates repo ships a large index.json (a list of category groups, each with a
templates array). This flattens it into a compact name -> summary map so Claude can pick the right template
fast without reading the whole catalog.

Usage:
    python gen_quick_index.py <path-to-templates-dir>
    # e.g. python gen_quick_index.py D:/comfy-templates/templates
If no path is given, it looks for ./templates next to this script's parent, then the COMFY_TEMPLATES env var.
"""
import json
import os
import sys

DESC_MAX = 180  # truncate descriptions to keep the index small


def build(templates_dir):
    src = os.path.join(templates_dir, "index.json")
    if not os.path.isfile(src):
        raise SystemExit(f"index.json not found in {templates_dir}")
    with open(src, "r", encoding="utf-8") as f:
        groups = json.load(f)

    out = {}
    for group in groups:
        category = group.get("title") or group.get("category") or group.get("moduleName") or ""
        for t in group.get("templates", []):
            name = t.get("name")
            if not name:
                continue
            desc = (t.get("description") or "").strip()
            if len(desc) > DESC_MAX:
                desc = desc[:DESC_MAX]
            out[name] = {
                "title": t.get("title", ""),
                "category": category,
                "models": t.get("models", []),
                "tags": t.get("tags", []),
                "mediaType": t.get("mediaType", ""),
                "openSource": t.get("openSource", False),
                "vram": t.get("vram", 0),
                "description": desc,
            }

    # Blueprints are reusable subgraph bricks, shipped in a SIBLING directory that has no index.json of its
    # own. RESPONSIBLE FOR (2026-08-06 audit): they were absent from the index entirely, so the one blueprint
    # TASKS.md names by example (`text_to_image_z_image_turbo`) could not be found by the lookup the same file
    # tells you to use. The installer already sparse-checks them out; only the index skipped them.
    bp_dir = os.path.join(os.path.dirname(os.path.abspath(templates_dir)), "blueprints")
    blueprints = 0
    if os.path.isdir(bp_dir):
        for fn in sorted(os.listdir(bp_dir)):
            # blueprints/ carries its own index.json alongside the bricks. It is a catalogue, not a
            # blueprint, and counting it is what turned the documented 94 into 95.
            if not fn.endswith(".json") or fn == "index.json":
                continue
            name = fn[:-5]
            entry = {"title": name.replace("_", " "), "category": "Blueprints", "models": [],
                     "tags": ["blueprint", "subgraph"], "mediaType": "", "openSource": True, "vram": 0,
                     "description": "Reusable subgraph blueprint. Lives in blueprints/, not templates/.",
                     "kind": "blueprint", "path": f"blueprints/{fn}"}
            try:
                with open(os.path.join(bp_dir, fn), "r", encoding="utf-8") as bf:
                    data = json.load(bf)
                entry["title"] = data.get("name") or data.get("title") or entry["title"]
            except Exception as exc:
                # Report it. A blueprint that will not parse is worth knowing about, and swallowing the
                # error would put a fabricated title into the index.
                print(f"  warn: could not read {fn}: {exc}")
            out.setdefault(name, entry)
            blueprints += 1

    dst = os.path.join(templates_dir, "_quick_index.json")
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=0)
    print(f"wrote {dst}  ({len(out)} entries: {len(out) - blueprints} templates + {blueprints} blueprints)")


def _default_dir():
    if len(sys.argv) > 1:
        return sys.argv[1]
    env = os.environ.get("COMFY_TEMPLATES")
    if env:
        return env
    # ./templates relative to this file's repo root
    here = os.path.dirname(os.path.abspath(__file__))
    guess = os.path.join(os.path.dirname(here), "templates")
    return guess


if __name__ == "__main__":
    build(_default_dir())
