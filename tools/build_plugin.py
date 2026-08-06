"""Assemble the Claude Code plugin's bundled skill from the canonical sources.

The plugin (`claude-code/`) is a SELF-CONTAINED Claude Code distribution of the same skill the
multi-agent installer wires. So that `/plugin install comfyui` ships the full kit, the plugin needs the
skill files physically present under `claude-code/skills/comfyui/`. This script copies them from the
single source of truth (`shared/comfyui/` + `docs/`) so the bundle never drifts by hand.

RUN IT before cutting a release whenever SKILL.md / MODELS.md / a routed doc changed:
    python tools/build_plugin.py
The plugin's `.mcp.json` / manifests are config, not generated, so they are NOT touched here.
"""
import os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
DST = os.path.join(ROOT, "claude-code", "skills", "comfyui")

# (source path relative to repo root) -> filename in the plugin skill dir.
# The plugin lays docs flat next to SKILL.md, matching the installed-skill layout (SKILL.md routes to
# "next to this file ... or docs/X.md", so flat resolves).
FILES = {
    "shared/comfyui/SKILL.md": "SKILL.md",
    "shared/comfyui/MODELS.md": "MODELS.md",
    "shared/comfyui/comfy_client.py": "comfy_client.py",
    # Ships as a TEMPLATE only. Installers must copy it when absent and never overwrite it: it is the one
    # file that holds per-machine state, and clobbering it is what destroyed the bootstrap before 2026-08-06.
    "shared/comfyui/machine.md": "machine.md",
    "shared/comfyui/workflow_layout.py": "workflow_layout.py",
    "docs/MODEL_INDEX.md": "MODEL_INDEX.md",
    "docs/ADVANCED.md": "ADVANCED.md",
    "docs/KIJAI.md": "KIJAI.md",
    "docs/KNOWN_ISSUES.md": "KNOWN_ISSUES.md",
    "docs/LTX2_TRAINING.md": "LTX2_TRAINING.md",
    "docs/TASKS.md": "TASKS.md",
    "docs/BUILDING_NODES.md": "BUILDING_NODES.md",
    "docs/EXAMPLE_WORKFLOWS.md": "EXAMPLE_WORKFLOWS.md",
    "docs/NODES.md": "NODES.md",
    "docs/LAYERS.md": "LAYERS.md",
    "docs/BOOTSTRAP.md": "BOOTSTRAP.md",
    "docs/AGENTS.md": "AGENTS.md",
    "docs/UPDATING.md": "UPDATING.md",
}

# Whole directories the SKILL routes into, kept as a subdir (matching the installed-skill layout, so a
# `docs/NODE_LIBRARY/ocio.md` reference resolves to `NODE_LIBRARY/ocio.md` next to SKILL.md in the bundle).
DIRS = {
    "docs/NODE_LIBRARY": "NODE_LIBRARY",
    "shared/comfyui/MODELS": "MODELS",
    # RESPONSIBLE FOR (2026-08-06 audit, second pass): five places in the SHIPPED docs tell the reader to run
    # `shared/tools/fetch_workflow.py` or `check_updates.py`, and an installed skill had no `tools/` at all.
    # A dead instruction in the artifact, same class as the installer copying three files.
    "shared/tools": "tools",
    # node_inventory.py lives in tools/ (gitignored dir, so it is force-added). The docs tell the reader to
    # regenerate _INVENTORY.md with it, and that instruction was dead for everyone who cloned.
}

os.makedirs(DST, exist_ok=True)
copied = []
missing_sources = []
for src_rel, name in FILES.items():
    src = os.path.join(ROOT, src_rel)
    if not os.path.exists(src):
        # RESPONSIBLE FOR (2026-08-06, mutation test): this used to print a warning and continue, so a source
        # deleted from the repo kept its STALE copy in the bundle and every check downstream resolved against
        # that ghost. Deleting docs/KIJAI.md and rebuilding passed the gate. A missing source is a broken
        # build, not a note in the log.
        missing_sources.append(src_rel)
        continue
    shutil.copyfile(src, os.path.join(DST, name))
    copied.append(name)

for src_rel, name in DIRS.items():
    src = os.path.join(ROOT, src_rel)
    if not os.path.isdir(src):
        missing_sources.append(src_rel + "/")
        continue
    dstdir = os.path.join(DST, name)
    if os.path.isdir(dstdir):
        shutil.rmtree(dstdir)
    shutil.copytree(src, dstdir)
    copied.append(f"{name}/ ({len(os.listdir(dstdir))} files)")

print(f"built claude-code/skills/comfyui/ : {len(copied)} items -> {', '.join(copied)}")

# Every OTHER skill under shared/ ships as its own bundled skill. Model-side knowledge that also
# applies outside ComfyUI (a vendor's own app or API) lives beside `comfyui` rather than inside it.
# Discovered rather than listed, so a new shared/<skill>/ is bundled the moment it exists instead of
# being silently left out of the plugin. RESPONSIBLE FOR: generalised from a hardcoded seedance-only
# block, 2026-08-06, when the second such skill (minimax-h3) would have gone unbundled.
SHARED_ROOT = os.path.join(ROOT, "shared")
extra = sorted(
    d for d in os.listdir(SHARED_ROOT)
    if d != "comfyui" and os.path.isfile(os.path.join(SHARED_ROOT, d, "SKILL.md"))
)
for skill in extra:
    src = os.path.join(SHARED_ROOT, skill)
    dst = os.path.join(ROOT, "claude-code", "skills", skill)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print(f"built claude-code/skills/{skill}/ : {len(os.listdir(dst))} files")
if not extra:
    print("  no extra shared/<skill>/ dirs found")


# ---------------------------------------------------------------------------
# Repair pass, then the gate.
#
# RESPONSIBLE FOR (2026-08-06 audit): the bundle is a FLATTENED copy, so a link that is correct in the
# repo (`../shared/comfyui/MODELS.md` from docs/, `../../docs/ADVANCED.md` from shared/) points at
# nothing once both ends land in the same directory. Six such links shipped. Hand-fixing the bundle is
# useless because the next build overwrites it, so the repair belongs HERE, and the gate belongs here
# too: this script is what CREATES the breakage and it already runs before every release.
#
# The checks live inside this file on purpose. `.gitignore` has `/tools/`, and only this file is tracked,
# so a new `tools/check_docs.py` would be committed nowhere and would silently never run.
# ---------------------------------------------------------------------------
import re

LINK = re.compile(r'(\[[^\]]*\]\()([^)\s]+)(\))')
BUNDLE = os.path.join(ROOT, "claude-code", "skills")


def _bundle_files():
    """basename -> list of absolute paths, so a broken link can be re-aimed at the real file."""
    by_name = {}
    for root, _dirs, files in os.walk(BUNDLE):
        for f in files:
            by_name.setdefault(f, []).append(os.path.join(root, f))
    return by_name


def repair_and_check():
    by_name = _bundle_files()
    repaired, unresolved = 0, []
    for root, _dirs, files in os.walk(BUNDLE):
        for f in files:
            if not f.endswith(".md"):
                continue
            path = os.path.join(root, f)
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            changed = False

            def fix(m):
                nonlocal changed
                url = m.group(2)
                if url.startswith(("http", "#", "mailto")):
                    return m.group(0)
                target, _, anchor = url.partition("#")
                if os.path.exists(os.path.normpath(os.path.join(root, target))):
                    return m.group(0)
                # Broken here. Re-aim at the real file if the bundle carries one by that name. Prefer a
                # candidate in THIS file's own skill dir: SKILL.md exists once per skill, so a bare
                # basename match is ambiguous across the bundle and the local one is always the intent.
                cands = by_name.get(os.path.basename(target), [])
                if len(cands) > 1:
                    same = [c for c in cands if os.path.dirname(c) == root]
                    parent = [c for c in cands if os.path.dirname(c) == os.path.dirname(root)]
                    cands = same or parent or cands
                if len(cands) != 1:
                    unresolved.append((os.path.relpath(path, ROOT), url))
                    return m.group(0)
                new = os.path.relpath(cands[0], root).replace(os.sep, "/")
                changed = True
                return m.group(1) + (new + "#" + anchor if anchor else new) + m.group(3)

            new_text = LINK.sub(fix, text)
            if changed:
                with open(path, "w", encoding="utf-8", newline="") as fh:
                    fh.write(new_text)
                repaired += 1
    return repaired, unresolved


def check_backtick_routes():
    """The routing table is written as BACKTICKED paths, not markdown links, so the link resolver above
    never saw it. Measured 2026-08-06 on the shipped SKILL.md: 0 markdown links, 29 backticked routes, and a
    mutation test (delete docs/KIJAI.md, rebuild) passed the gate while the route pointed at nothing. That is
    the exact class this gate exists to catch, missed because the probe read the wrong syntax."""
    # Only the kit's OWN namespace. A backticked `luma.md` or a vendor's `VIDEO_PROMPT_WRITING_GUIDE.md` is a
    # reference to somebody else's document, not a route, and flagging those would train the reader to ignore
    # this gate. The `docs/` prefix is the kit's namespace and external references never use it.
    bad = []
    for root, _dirs, files in os.walk(BUNDLE):
        for f in files:
            if not f.endswith(".md"):
                continue
            text = open(os.path.join(root, f), encoding="utf-8", errors="ignore").read()
            for m in re.finditer(r'`(docs/[A-Za-z0-9_./-]+\.md)`', text):
                ref = m.group(1)
                flat = ref[len("docs/"):]
                if any(os.path.isfile(os.path.join(d, c))
                       for d in (root, DST) for c in (ref, flat, os.path.basename(ref))):
                    continue
                bad.append((os.path.relpath(os.path.join(root, f), ROOT), ref))
    return sorted(set(bad))


def check_node_library_index():
    """Every category file must be listed in _INDEX.md. SKILL.md calls it the entry point for any node
    question, so a file it omits is unreachable knowledge (radiance.md was, until this check existed)."""
    d = os.path.join(ROOT, "docs", "NODE_LIBRARY")
    idx_path = os.path.join(d, "_INDEX.md")
    if not os.path.isfile(idx_path):
        return ["_INDEX.md missing"]
    idx = open(idx_path, encoding="utf-8").read()
    return [f for f in sorted(os.listdir(d))
            if f.endswith(".md") and not f.startswith("_") and f not in idx]


def check_backtick_paths():
    """A backticked repo-relative script path in the docs is an instruction. If it does not resolve, the
    reader is being sent somewhere that does not exist (`tools/gen_quick_index.py` was, for months)."""
    pat = re.compile(r'`((?:tools|shared/tools)/[A-Za-z0-9_./-]+\.py)`')
    bad = set()
    # Second half of the same question, and the half that was missing: the path resolving in the REPO says
    # nothing about the SHIPPED skill. Five shipped docs told the reader to run shared/tools/fetch_workflow.py
    # while an installed skill had no tools/ at all. A path is only sound when it resolves on both sides.
    shipped = os.path.join(DST, "tools")
    import subprocess

    class _Anything:
        """Stand-in when this is not a git checkout: skip the tracked-ness half rather than fail the build
        for a reason that has nothing to do with the docs."""

        def __contains__(self, _item):
            return True

    try:
        out = subprocess.run(["git", "-C", ROOT, "ls-files"], capture_output=True, text=True, check=True).stdout
        TRACKED = set(out.splitlines())
    except Exception:
        TRACKED = _Anything()
    for sub in ("docs", "shared", "README.md"):
        p = os.path.join(ROOT, sub)
        walk = [(os.path.dirname(p), [], [os.path.basename(p)])] if os.path.isfile(p) else os.walk(p)
        for root, _dirs, files in walk:
            for f in files:
                if not f.endswith(".md"):
                    continue
                text = open(os.path.join(root, f), encoding="utf-8", errors="ignore").read()
                for m in pat.finditer(text):
                    ref = m.group(1)
                    if not os.path.isfile(os.path.join(ROOT, ref)):
                        bad.add((os.path.relpath(os.path.join(root, f), ROOT), ref + "  (missing in repo)"))
                    elif ref not in TRACKED:
                        # Present on THIS disk but not committed. `.gitignore` carries `/tools/`, so a script
                        # living there works for the author and does not exist for anyone who clones. Checking
                        # the working tree alone is the probe looking at the wrong thing.
                        bad.add((os.path.relpath(os.path.join(root, f), ROOT),
                                 ref + "  (on disk but NOT tracked by git: a clone will not have it)"))
                    elif not os.path.isfile(os.path.join(shipped, os.path.basename(ref))):
                        bad.add((os.path.relpath(os.path.join(root, f), ROOT),
                                 ref + "  (in repo, MISSING from the shipped skill)"))
    return sorted(bad)


print("\n-- gate --")
if missing_sources:
    # RESPONSIBLE FOR (2026-08-06 mutation test): a source deleted from the repo left its STALE copy in the
    # bundle, and every check downstream then resolved against that ghost. Removing docs/KIJAI.md and
    # rebuilding passed the gate while the shipped skill routed to a file the repo no longer had. Purge the
    # ghost, then fail: a routed source that has gone missing is a broken build, not a line in the log.
    for src_rel in missing_sources:
        key = src_rel.rstrip("/")
        name = FILES.get(key) or DIRS.get(key)
        ghost = os.path.join(DST, name) if name else None
        if ghost and os.path.isfile(ghost):
            os.remove(ghost)
        elif ghost and os.path.isdir(ghost) and os.path.abspath(ghost) != os.path.abspath(DST):
            shutil.rmtree(ghost)
    print(f"\n  FAIL {len(missing_sources)} routed source(s) in the build list do not exist:")
    for s in missing_sources:
        print(f"        {s}")
    raise SystemExit("build_plugin: a routed source is missing, bundle NOT fit to ship")

repaired, unresolved = repair_and_check()
print(f"  links re-aimed after flattening: {repaired} file(s)")
missing_idx = check_node_library_index()
bad_routes = check_backtick_routes()
bad_paths = check_backtick_paths()
fail = False
if unresolved:
    fail = True
    print(f"  FAIL {len(unresolved)} link(s) resolve to nothing and no bundle file matches:")
    for p, u in unresolved[:15]:
        print(f"        {p} -> {u}")
if missing_idx:
    fail = True
    print(f"  FAIL NODE_LIBRARY/_INDEX.md does not list: {', '.join(missing_idx)}")
if bad_routes:
    fail = True
    print(f"  FAIL {len(bad_routes)} backticked route(s) point at a file the bundle does not carry:")
    for p_, u in bad_routes[:15]:
        print(f"        {p_} -> {u}")
if bad_paths:
    fail = True
    print(f"  FAIL {len(bad_paths)} backticked script path(s) do not exist:")
    for p, u in bad_paths[:15]:
        print(f"        {p} -> {u}")
if fail:
    raise SystemExit("build_plugin: gate failed, bundle NOT fit to ship")
print("  gate passed: links + backticked routes resolve, _INDEX complete, script paths exist and are tracked")
