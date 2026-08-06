#!/usr/bin/env bash
# Gemini CLI adapter. Ships an extension at ~/.gemini/extensions/comfyui bundling the MCP + GEMINI.md context.
# Assumes shared/install_shared.sh already ran.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; REPO_ROOT="$(cd "$HERE/../.." && pwd)"; SHARED="$REPO_ROOT/shared/comfyui"
EXT="$HOME/.gemini/extensions/comfyui"
ok(){ echo "  [ok] $*"; }; warn(){ echo "  [!]  $*"; }; have(){ command -v "$1" >/dev/null 2>&1; }

echo; echo "[gemini] adapter"
have gemini || { warn "gemini CLI not found; install Gemini CLI first"; exit 1; }
mkdir -p "$EXT"

# GEMINI.md = SKILL.md body with YAML frontmatter stripped
{ printf '# ComfyUI media generation (always-on context for Gemini CLI)\n\nUse this whenever a task involves generating images, video, or audio with ComfyUI, or building/running a workflow. The per-model prompting reference is MODELS.md next to this file.\n\n'
  awk 'BEGIN{n=0} /^---[[:space:]]*$/{n++; next} n>=2{print}' "$SHARED/SKILL.md"
} > "$EXT/GEMINI.md"
# RESPONSIBLE FOR (2026-08-06 audit): only MODELS.md + the client were copied, so every docs/ and
# NODE_LIBRARY route in the context file pointed at nothing. Ship the BUILT bundle.
BUNDLE="$REPO_ROOT/claude-code/skills"
[ -d "$BUNDLE" ] || { warn "bundle missing at $BUNDLE - run: python tools/build_plugin.py"; exit 1; }
# MIGRATION (3.0.0): the machine block used to live inside GEMINI.md, which this installer regenerates on
# every run. Lift it out first or the upgrade destroys the bootstrap.
if [ ! -f "$EXT/machine.md" ] && [ -f "$EXT/GEMINI.md" ] && grep -q "^## Your machine" "$EXT/GEMINI.md"; then
  { printf '# Your machine\n\nMigrated out of GEMINI.md by the 3.0.0 installer. Created once, never overwritten.\n\n'
    awk '/^## Your machine/{f=1} f&&/^## /&&!/^## Your machine/{exit} f' "$EXT/GEMINI.md"
  } > "$EXT/machine.md"
  ok "machine block migrated out of GEMINI.md -> machine.md"
fi
keep=""; [ -f "$EXT/machine.md" ] && { keep="$(mktemp)"; cp "$EXT/machine.md" "$keep"; }
cp -R "$BUNDLE"/comfyui/* "$EXT"/
[ -n "$keep" ] && { cp "$keep" "$EXT/machine.md"; rm -f "$keep"; }
for sk in "$BUNDLE"/*/; do
  name="$(basename "$sk")"; [ "$name" = "comfyui" ] && continue
  mkdir -p "$EXT/$name"; cp -R "$sk"* "$EXT/$name"/
done
ok "full kit (docs, NODE_LIBRARY, MODELS/, sibling skills) -> $EXT"

ok "GEMINI.md + MODELS.md + client -> $EXT"

cat > "$EXT/gemini-extension.json" <<'JSON'
{
  "name": "comfyui",
  "version": "1.0.0",
  "description": "Drive a local ComfyUI for image, video, and audio generation. By AI VFX NEWS.",
  "contextFileName": "GEMINI.md",
  "mcpServers": {
    "comfyui": {
      "command": "comfyui-mcp",
      "args": [],
      "cwd": "${extensionPath}"
    }
  }
}
JSON
ok "gemini-extension.json written"
echo "[gemini] done. Restart gemini so the extension + MCP load (/extensions list to confirm)."
