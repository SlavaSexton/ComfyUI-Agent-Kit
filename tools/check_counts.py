#!/usr/bin/env python3
"""Recompute every headline count from the files and fail when any copy has drifted.

Why this exists. The kit states its size in eight places, and on 2026-08-09 an audit found four of
them stale at once: README and MODEL_INDEX had moved to 160 models while SKILL.md still said 156, the
GitHub About box still advertised numbers from two releases earlier, and a chart PNG rendered correct
bars under a subtitle nobody had updated. None of those failures announced itself. Counts drift in
silence because each place looks right on its own.

**The two numbers use DIFFERENT BASES, and confusing them is the trap this script exists to close.**

  recipe ENTRIES  = every `### ` heading across MODELS/*.md. This is what README, MODEL_INDEX and
                    the cover banner mean by "recipes".
  guided MODELS   = entries OUTSIDE niche.md and utility.md, plus the individual models listed
                    INSIDE niche.md. This is what models_by_modality.html means by "models with
                    dedicated prompting guides", and it is larger, because niche.md holds one
                    heading per modality covering many models, and utility.md holds two headings
                    covering the 18 utility tools counted separately on that chart.

Verified 2026-08-09: 72 entries, 67 of them outside niche/utility, 11 models inside niche, so the
chart's 78 is arithmetic and not invention. Both numbers are correct; neither may be copied into the
other's slot.

Counting the niche models needs two exclusions, and BOTH were discovered by getting them wrong first:
a bold lead-in can be a pointer to an entry that moved to another file, and it can be a patch for the
model above it rather than a model of its own. They are matched explicitly below rather than guessed,
because a heuristic that silently miscounts is worse than no check at all.

Run: python tools/check_counts.py     (exit 0 = every copy agrees, 1 = drift, and it says where)

The chart generators under tools/assets/ are LOCAL and gitignored, so their checks are skipped with a
note when the files are absent. A fresh clone still gets the full check of the public files.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(ROOT, "shared", "comfyui", "MODELS")

# A bold lead-in inside niche.md is NOT a model when the text right after it says one of these.
# "moved to"  -> a pointer left behind when the entry was promoted to a family file.
# "for the "  -> a control/patch belonging to the model above it (e.g. Anima ControlNet-LLLite).
NOT_A_MODEL = ("moved to", "for the ")


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def entries_per_file():
    out = {}
    for name in sorted(os.listdir(MODELS_DIR)):
        if name.endswith(".md"):
            out[name] = len(re.findall(r"^### ", _read(os.path.join(MODELS_DIR, name)), flags=re.M))
    return out


def niche_models():
    text = _read(os.path.join(MODELS_DIR, "niche.md"))
    keep = []
    for name in re.findall(r"^\*\*([^*]+)\*\*", text, flags=re.M):
        after = text.split("**" + name + "**", 1)[1][:80]
        if not any(flag in after for flag in NOT_A_MODEL):
            keep.append(name)
    return keep


def find_all(path, pattern):
    """Every integer captured by pattern in a file, or None when the file is absent."""
    if not os.path.isfile(path):
        return None
    # re.M matters: several of these anchors are at the start of a LINE, not of the file. Without it
    # the scan finds nothing and the check reports itself blind rather than passing, which is the
    # behaviour this script wants, but the blindness is still a bug in the pattern, not in the file.
    return [int(m) for m in re.findall(pattern, _read(path), flags=re.M)]


def main():
    per = entries_per_file()
    entries = sum(per.values())
    outside = entries - per["niche.md"] - per["utility.md"]
    niche = niche_models()
    guided = outside + len(niche)

    print("Computed from the files:")
    print(f"  recipe entries (### across MODELS/) : {entries}   {per}")
    print(f"  entries outside niche/utility       : {outside}")
    print(f"  models listed inside niche.md       : {len(niche)}  {niche}")
    print(f"  guided models (chart basis)         : {guided}")
    print()

    problems = []
    skipped = []

    def check(label, path, pattern, expected):
        found = find_all(os.path.join(ROOT, path), pattern)
        if found is None:
            skipped.append(f"{label} ({path} absent, local-only file)")
            return
        if not found:
            problems.append(f"{label}: pattern never matched in {path}, the check is blind")
            return
        bad = [v for v in found if v != expected]
        status = "ok" if not bad else f"DRIFT {bad} != {expected}"
        print(f"  {status:24} {label}  ({path})")
        if bad:
            problems.append(f"{label} in {path} says {bad}, computed {expected}")

    print("Checking every place the numbers are written down:")
    check("recipe entries", "README.md", r"(\d+) prompt-recipe entries", entries)
    check("recipe entries", "README.md", r"Covered today \((\d+) recipe entries", entries)
    check("recipe entries", "README.md", r"the (\d+)-entry recipe brain", entries)
    check("recipe entries", "docs/MODEL_INDEX.md", r"✅ (\d+) recipe entries", entries)
    check("guided models", "tools/assets/models_by_modality.html",
          r'class="sub">(\d+) models with dedicated', guided)
    check("recipe entries", "tools/assets/cover_gen.py", r"^RECIPES = (\d+)", entries)

    # The per-family entry counts in the MODELS.md router table must match the files they point at.
    router = _read(os.path.join(ROOT, "shared", "comfyui", "MODELS.md"))
    for fname, count in per.items():
        m = re.search(r"MODELS/" + re.escape(fname) + r"\)\s*\|\s*(\d+)\s*\|", router)
        if not m:
            problems.append(f"router row for {fname} not found in MODELS.md")
        elif int(m.group(1)) != count:
            problems.append(f"router says {m.group(1)} for {fname}, the file has {count}")
    print(f"  {'ok' if not any('router' in p for p in problems) else 'DRIFT':24} MODELS.md router rows")

    if skipped:
        print("\nSkipped (not shipped in a clone):")
        for s in skipped:
            print("  -", s)

    if problems:
        print("\nCOUNTS HAVE DRIFTED:")
        for p in problems:
            print("  *", p)
        print("\nFix the copies, then re-render the banners that carry a number.")
        return 1

    print("\nAll counts agree.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
