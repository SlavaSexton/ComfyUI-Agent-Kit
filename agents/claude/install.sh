#!/usr/bin/env bash
# Claude Code adapter: install the comfyui skill, register the MCP, append the auto-activation block.
# Assumes shared/install_shared.sh already ran. GLM via Claude Code reuses this adapter (~/.claude/skills).
set -euo pipefail
TEMPLATES_DIR="$HOME/comfyui-agent-kit-data/workflow_templates"
while [ $# -gt 0 ]; do case "$1" in --templates-dir) TEMPLATES_DIR="$2"; shift 2;; *) shift;; esac; done
HERE="$(cd "$(dirname "$0")" && pwd)"; REPO_ROOT="$(cd "$HERE/../.." && pwd)"; SHARED="$REPO_ROOT/shared/comfyui"
SKILLS="$HOME/.claude/skills"; CLAUDE_MD="$HOME/.claude/CLAUDE.md"
ok(){ echo "  [ok] $*"; }; warn(){ echo "  [!]  $*"; }; have(){ command -v "$1" >/dev/null 2>&1; }

echo; echo "[claude] adapter"
have claude || { warn "claude CLI not found; install Claude Code first"; exit 1; }

mkdir -p "$SKILLS/comfyui/workflows"
# RESPONSIBLE FOR (2026-08-06 audit): this copied THREE files, so a fresh install got a SKILL.md whose
# routing table was 21/22 dead. Install the BUILT bundle: claude-code/skills/ is what tools/build_plugin.py
# produces from shared/ + docs/, already flattened the way SKILL.md's routes expect.
BUNDLE="$REPO_ROOT/claude-code/skills"
[ -d "$BUNDLE" ] || { warn "bundle missing at $BUNDLE - run: python tools/build_plugin.py"; exit 1; }
for sk in "$BUNDLE"/*/; do
  name="$(basename "$sk")"; dest="$SKILLS/$name"
  # machine.md carries per-machine state the bootstrap wrote. Never overwrite it on an update.
  keep=""; [ -f "$dest/machine.md" ] && { keep="$(mktemp)"; cp "$dest/machine.md" "$keep"; }
  mkdir -p "$dest"; cp -R "$sk". "$dest"/ 2>/dev/null || cp -R "$sk"* "$dest"/
  [ -n "$keep" ] && { cp "$keep" "$dest/machine.md"; rm -f "$keep"; }
  ok "$name skill -> $dest"
done




tmp="$(mktemp -d)"; git clone --depth 1 https://github.com/jtydhr88/comfyui-custom-node-skills.git "$tmp" >/dev/null 2>&1
src="$tmp/plugins/comfyui-custom-nodes/skills"
if [ -d "$src" ]; then for d in "$src"/*/; do dst="$SKILLS/$(basename "$d")"; rm -rf "$dst"; cp -R "$d" "$dst"; done; ok "node-building skills installed"; else warn "node skills not found"; fi
rm -rf "$tmp"

if claude mcp get comfyui >/dev/null 2>&1; then ok "MCP 'comfyui' already registered"
else claude mcp add comfyui --scope user -- comfyui-mcp && ok "MCP registered" || warn "register manually: claude mcp add comfyui --scope user -- comfyui-mcp"; fi

marker="### ComfyUI media generation (auto-activation)"
if [ -f "$CLAUDE_MD" ] && grep -qF "$marker" "$CLAUDE_MD"; then ok "activation block present"
else mkdir -p "$(dirname "$CLAUDE_MD")"; sed "s|__TEMPLATES_DIR__|$TEMPLATES_DIR|g" "$HERE/claude_md_activation.md" >> "$CLAUDE_MD"; ok "activation block appended"; fi

echo "[claude] done. Start ComfyUI, then run the BOOTSTRAP once (docs/BOOTSTRAP.md)."
