#!/usr/bin/env bash
# Codex CLI adapter. Same SKILL.md format as Claude, but user skills live in ~/.agents/skills.
# MCP goes in ~/.codex/config.toml. Assumes shared/install_shared.sh already ran.
set -euo pipefail
COMFY_URL="http://127.0.0.1:8188"
while [ $# -gt 0 ]; do case "$1" in --comfy-url) COMFY_URL="$2"; shift 2;; *) shift;; esac; done
HERE="$(cd "$(dirname "$0")" && pwd)"; REPO_ROOT="$(cd "$HERE/../.." && pwd)"; SHARED="$REPO_ROOT/shared/comfyui"
SKILLS="$HOME/.agents/skills"; CODEX_HOME="$HOME/.codex"; CONFIG="$CODEX_HOME/config.toml"; AGENTS_MD="$CODEX_HOME/AGENTS.md"
ok(){ echo "  [ok] $*"; }; warn(){ echo "  [!]  $*"; }; have(){ command -v "$1" >/dev/null 2>&1; }

echo; echo "[codex] adapter"
have codex || { warn "codex CLI not found; install OpenAI Codex CLI first"; exit 1; }

mkdir -p "$SKILLS/comfyui/workflows"
# RESPONSIBLE FOR (2026-08-06 audit): this copied THREE files, so a fresh install got a SKILL.md whose
# routing table was 21/22 dead. Install the BUILT bundle: claude-code/skills/ is what tools/build_plugin.py
# produces from shared/ + docs/, already flattened the way SKILL.md's routes expect.
BUNDLE="$REPO_ROOT/claude-code/skills"
[ -d "$BUNDLE" ] || { warn "bundle missing at $BUNDLE - run: python tools/build_plugin.py"; exit 1; }
for sk in "$BUNDLE"/*/; do
  name="$(basename "$sk")"; dest="$SKILLS/$name"
  # machine.md carries per-machine state the bootstrap wrote. Never overwrite it on an update.
  # MIGRATION (3.0.0): before 3.0.0 the machine block lived INSIDE SKILL.md, which this installer
  # overwrites. Lift it out BEFORE the copy or the upgrade destroys the bootstrap one last time - which is
  # exactly the defect 3.0.0 exists to fix. Runs once: after this, machine.md exists and the guard below
  # takes over.
  if [ ! -f "$dest/machine.md" ] && [ -f "$dest/SKILL.md" ] && grep -q "^## Your machine" "$dest/SKILL.md" \
     && ! grep -q "machine.md" "$dest/SKILL.md"; then
    { printf '# Your machine\n\nMigrated out of SKILL.md by the 3.0.0 installer, which is why it survived this\nupdate. From here on this file is created once and never overwritten.\n\n'
      awk '/^## Your machine/{f=1} f&&/^## /&&!/^## Your machine/{exit} f' "$dest/SKILL.md"
    } > "$dest/machine.md"
    ok "$name: machine block migrated out of SKILL.md -> machine.md"
  fi
  keep=""; [ -f "$dest/machine.md" ] && { keep="$(mktemp)"; cp "$dest/machine.md" "$keep"; }
  mkdir -p "$dest"; cp -R "$sk". "$dest"/ 2>/dev/null || cp -R "$sk"* "$dest"/
  [ -n "$keep" ] && { cp "$keep" "$dest/machine.md"; rm -f "$keep"; }
  ok "$name skill -> $dest"
done


ok "comfyui skill -> $SKILLS/comfyui"

tmp="$(mktemp -d)"; git clone --depth 1 https://github.com/jtydhr88/comfyui-custom-node-skills.git "$tmp" >/dev/null 2>&1
src="$tmp/plugins/comfyui-custom-nodes/skills"
if [ -d "$src" ]; then for d in "$src"/*/; do dst="$SKILLS/$(basename "$d")"; rm -rf "$dst"; cp -R "$d" "$dst"; done; ok "node-building skills installed"; else warn "node skills not found"; fi
rm -rf "$tmp"

mkdir -p "$CODEX_HOME"
if [ -f "$CONFIG" ] && grep -qF "[mcp_servers.comfyui]" "$CONFIG"; then ok "MCP 'comfyui' already in config.toml"
else
  codex mcp add comfyui -- comfyui-mcp >/dev/null 2>&1 || true
  if [ -f "$CONFIG" ] && grep -qF "[mcp_servers.comfyui]" "$CONFIG"; then ok "MCP registered via 'codex mcp add'"
  else printf '\n[mcp_servers.comfyui]\ncommand = "comfyui-mcp"\nargs = []\n[mcp_servers.comfyui.env]\nCOMFYUI_URL = "%s"\n' "$COMFY_URL" >> "$CONFIG"; ok "MCP appended to config.toml"; fi
fi

if [ -f "$AGENTS_MD" ] && grep -qF "ComfyUI skill (comfyui)" "$AGENTS_MD"; then ok "AGENTS.md pointer present"
else printf '\n## ComfyUI skill (comfyui)\nFor any ComfyUI / image / video / audio generation task, use the `comfyui` skill in ~/.agents/skills/comfyui (SKILL.md + MODELS.md).\n' >> "$AGENTS_MD"; ok "AGENTS.md pointer added"; fi

echo "[codex] done. Restart codex so the skill + MCP load."
