#!/usr/bin/env python3
"""Check what's new in ComfyUI: pull the template library, diff for NEW models/templates, and read the blog RSS.

The Comfy-Org/workflow_templates repo is the canonical "what's new" feed: every new model or workflow Comfy ships
lands there first. This script:
  1. snapshots the current model + template set,
  2. `git pull`s the templates clone and regenerates the quick index,
  3. diffs -> prints NEW models and NEW templates,
  4. fetches the blog.comfy.org RSS for recent announcements (context).

Usage:
    python check_updates.py [templates_dir]
Default templates_dir: $COMFY_TEMPLATES or ~/comfyui-agent-kit-data/workflow_templates

Stdlib only. LinkedIn is intentionally not polled (auth-gated, anti-scraping, against ToS); the same news is in
the blog RSS and the templates repo, both machine-readable.
"""
import json
import os
import sys
import subprocess
import urllib.request
import xml.etree.ElementTree as ET

try:                                              # blog titles contain non-ASCII; never crash on a cp1251 console
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BLOG_FEED = "https://blog.comfy.org/feed"


def _index_path(templates_dir):
    return os.path.join(templates_dir, "templates", "_quick_index.json")


def _load(templates_dir):
    p = _index_path(templates_dir)
    if not os.path.isfile(p):
        return {}, set(), set()
    d = json.load(open(p, encoding="utf-8"))
    models = set()
    for v in d.values():
        for m in (v.get("models") or []):
            models.add(m)
    return d, set(d), models   # templates(names), set of names, set of models


def _regen(templates_dir):
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, here)
    import gen_quick_index
    gen_quick_index.build(os.path.join(templates_dir, "templates"))


def _blog(n=8):
    try:
        req = urllib.request.Request(BLOG_FEED, headers={"User-Agent": "comfyui-agent-kit"})
        with urllib.request.urlopen(req, timeout=30) as r:
            root = ET.fromstring(r.read())
        out = []
        for item in root.iter("item"):
            t = item.findtext("title") or ""
            link = item.findtext("link") or ""
            date = (item.findtext("pubDate") or "")[:16]
            out.append((date, t.strip(), link.strip()))
            if len(out) >= n:
                break
        return out
    except Exception as e:
        return [("", f"(blog feed unavailable: {e})", "")]


def _head(templates_dir):
    r = subprocess.run(["git", "-C", templates_dir, "rev-parse", "HEAD"],
                       capture_output=True, text=True)
    return r.stdout.strip()[:8] if r.returncode == 0 else "?"


def _pull(templates_dir):
    """Pull, and REFUSE to report on stale data when it fails.

    Fail-CLOSED on purpose, and the asymmetry is the whole point. This script used to call
    `git pull` with check=False, so a failed pull did not stop it: it regenerated the index
    from the unchanged tree and printed a confident "NEW TEMPLATES (0)" plus a totals line.
    A dead .git/index.lock did exactly that from 2026-08-03 to 2026-08-09, hiding two core
    releases (v0.30.0 and v0.31.0) and a week of new models behind a clean all-clear. A noisy
    refusal costs one log line and a human's attention; a false all-clear costs a missed week,
    and it leaves no evidence that anything went wrong.

    The return code is checked but is NOT treated as proof the data moved: `git pull` answers 0
    when there was nothing to fetch even with the lock present (verified 2026-08-09), so the
    HEAD before/after pair is printed as the actual evidence.
    """
    before = _head(templates_dir)
    r = subprocess.run(["git", "-C", templates_dir, "pull", "--quiet"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(
            "\nREFUSING TO REPORT: `git pull` failed (exit {}) in {}\n"
            "The template clone was NOT updated, so any diff below would describe stale data.\n"
            "git said:\n{}{}\n"
            "Fix the clone (a stale .git/index.lock is the usual cause), then re-run.\n"
            .format(r.returncode, templates_dir, r.stdout, r.stderr))
        raise SystemExit(3)
    after = _head(templates_dir)
    print("  HEAD {} -> {}{}".format(before, after,
                                     "  (no new commits)" if before == after else ""))


def main(templates_dir):
    _, old_names, old_models = _load(templates_dir)

    print(f"Pulling templates: {templates_dir}")
    _pull(templates_dir)
    _regen(templates_dir)
    _, new_names, new_models = _load(templates_dir)

    new_m = sorted(new_models - old_models)
    gone_m = sorted(old_models - new_models)
    new_t = sorted(new_names - old_names)

    print("\n=== NEW MODELS (no recipe yet -> consider adding one to MODELS.md) ===")
    print("  " + (", ".join(new_m) if new_m else "(none)"))
    if gone_m:
        print("  removed:", ", ".join(gone_m))
    print(f"\n=== NEW TEMPLATES ({len(new_t)}) ===")
    for t in new_t[:40]:
        print("  +", t)
    if len(new_t) > 40:
        print(f"  ... and {len(new_t) - 40} more")
    print(f"\nTotals now: {len(new_names)} templates, {len(new_models)} distinct models")

    print("\n=== blog.comfy.org recent posts ===")
    for date, title, link in _blog():
        print(f"  {date}  {title}")
        if link:
            print(f"            {link}")

    print("\nNext: for each NEW model above, add a recipe to MODELS.md (research its official prompting), then")
    print("regenerate the coverage chart/index and commit. See docs/UPDATING.md.")


if __name__ == "__main__":
    td = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
        "COMFY_TEMPLATES", os.path.expanduser("~/comfyui-agent-kit-data/workflow_templates"))
    main(td)
