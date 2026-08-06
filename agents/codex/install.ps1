<#
.SYNOPSIS
  Codex CLI adapter. Codex has the SAME skill format as Claude (SKILL.md frontmatter, progressive disclosure),
  but user skills live in ~/.agents/skills (NOT ~/.codex/skills). MCP goes in ~/.codex/config.toml.
  Assumes shared/install_shared.ps1 already ran (comfyui-mcp global, templates cloned).
#>
param([string]$ComfyUrl = "http://127.0.0.1:8188")
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent (Split-Path -Parent $Here)
$Shared = Join-Path $RepoRoot "shared\comfyui"
$SkillsDest = "$env:USERPROFILE\.agents\skills"   # Codex user skills (verified path)
$CodexHome = "$env:USERPROFILE\.codex"
$ConfigToml = "$CodexHome\config.toml"
$AgentsMd = "$CodexHome\AGENTS.md"
function Ok($m){ Write-Host "  [ok] $m" -ForegroundColor Green }
function Warn($m){ Write-Host "  [!]  $m" -ForegroundColor Yellow }
function Have($c){ return [bool](Get-Command $c -ErrorAction SilentlyContinue) }
# Run a native command so its stderr (e.g. git clone progress) does not trip $ErrorActionPreference='Stop'
# into a terminating NativeCommandError. Real failures are still detectable via the returned exit code.
function Native([scriptblock]$cmd){
  $prev = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
  try { & $cmd 2>&1 | Out-Null } finally { $ErrorActionPreference = $prev }
  return $LASTEXITCODE
}

Write-Host "`n[codex] adapter" -ForegroundColor White
if (-not (Have "codex")) { Warn "codex CLI not on PATH; install OpenAI Codex CLI first"; throw "codex missing" }

# 1. skill (same SKILL.md) -> ~/.agents/skills/comfyui
New-Item -ItemType Directory -Force -Path "$SkillsDest\comfyui\workflows" | Out-Null
# RESPONSIBLE FOR (2026-08-06 audit): this block copied THREE files, so a fresh install got a SKILL.md
# whose routing table was 21/22 dead - no docs/, no NODE_LIBRARY, no workflow_layout.py, none of the other
# skills. Only the plugin path shipped a working kit. Install the BUILT bundle instead: claude-code/skills/
# is exactly what tools/build_plugin.py produces from shared/ + docs/, already flattened the way SKILL.md's
# routes expect, so there is ONE definition of what ships.
$Bundle = Join-Path $RepoRoot "claude-code\skills"
if (-not (Test-Path $Bundle)) { throw "bundle missing at $Bundle - run: python tools/build_plugin.py" }
foreach ($sk in Get-ChildItem $Bundle -Directory) {
  $dest = Join-Path $SkillsDest $sk.Name
  # machine.md carries per-machine state the bootstrap wrote. Never overwrite it on an update.
  $keep = Join-Path $dest "machine.md"; $tmpKeep = $null
  # MIGRATION (3.0.0): before 3.0.0 the machine block lived INSIDE SKILL.md, which this installer
  # overwrites. Lift it out BEFORE the copy or the upgrade destroys the bootstrap one last time - which is
  # exactly the defect 3.0.0 exists to fix. Runs once: after this, machine.md exists and the guard below
  # takes over.
  $oldSkill = Join-Path $dest "SKILL.md"
  if ((-not (Test-Path $keep)) -and (Test-Path $oldSkill)) {
    $old = Get-Content $oldSkill -Raw
    if ($old -match '(?m)^## Your machine' -and $old -notmatch 'machine\.md') {
      $lines = $old -split "`r?`n"; $buf = @(); $on = $false
      foreach ($l in $lines) {
        if ($l -match '^## Your machine') { $on = $true }
        elseif ($on -and $l -match '^## ') { break }
        if ($on) { $buf += $l }
      }
      if ($buf.Count -gt 1) {
        $hdr = "# Your machine`n`nMigrated out of SKILL.md by the 3.0.0 installer, which is why it survived this`nupdate. From here on this file is created once and never overwritten.`n`n"
        Set-Content $keep ($hdr + ($buf -join "`n")) -Encoding utf8
        Ok "$($sk.Name): machine block migrated out of SKILL.md -> machine.md"
      }
    }
  }
  if (Test-Path $keep) { $tmpKeep = [IO.Path]::GetTempFileName(); Copy-Item $keep $tmpKeep -Force }
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  Copy-Item (Join-Path $sk.FullName "*") $dest -Recurse -Force
  if ($tmpKeep) { Copy-Item $tmpKeep $keep -Force; Remove-Item $tmpKeep -Force }
  Ok "$($sk.Name) skill -> $dest"
}


Ok "comfyui skill -> $SkillsDest\comfyui"

# 2. node-building skills
$tmp = Join-Path $env:TEMP ("cns_" + [guid]::NewGuid().ToString("N").Substring(0,8))
Native { git clone --depth 1 https://github.com/jtydhr88/comfyui-custom-node-skills.git $tmp } | Out-Null
$src = Join-Path $tmp "plugins\comfyui-custom-nodes\skills"
if (Test-Path $src) { Get-ChildItem $src -Directory | ForEach-Object { $d="$SkillsDest\$($_.Name)"; if (Test-Path $d){Remove-Item $d -Recurse -Force -EA SilentlyContinue}; Copy-Item $_.FullName $d -Recurse -Force }; Ok "node-building skills installed" } else { Warn "node skills not found" }
Remove-Item $tmp -Recurse -Force -EA SilentlyContinue

# 3. MCP -> ~/.codex/config.toml  (prefer `codex mcp add`, fallback to TOML append)
New-Item -ItemType Directory -Force -Path $CodexHome | Out-Null
$toml = ""; if (Test-Path $ConfigToml) { $toml = Get-Content $ConfigToml -Raw }
if ($toml -match "\[mcp_servers\.comfyui\]") { Ok "MCP 'comfyui' already in config.toml" }
else {
  Native { codex mcp add comfyui -- comfyui-mcp } | Out-Null
  $toml2 = ""; if (Test-Path $ConfigToml) { $toml2 = Get-Content $ConfigToml -Raw }
  if ($toml2 -match "\[mcp_servers\.comfyui\]") { Ok "MCP registered via 'codex mcp add'" }
  else {
    $block = "`n[mcp_servers.comfyui]`ncommand = `"comfyui-mcp`"`nargs = []`n[mcp_servers.comfyui.env]`nCOMFYUI_URL = `"$ComfyUrl`"`n"
    Add-Content $ConfigToml $block; Ok "MCP appended to config.toml"
  }
}

# 4. optional pointer in ~/.codex/AGENTS.md
$marker = "ComfyUI skill (comfyui)"
$am = ""; if (Test-Path $AgentsMd) { $am = Get-Content $AgentsMd -Raw }
if ($am -match [regex]::Escape($marker)) { Ok "AGENTS.md pointer present" }
else { Add-Content $AgentsMd "`n## $marker`nFor any ComfyUI / image / video / audio generation task, use the ``comfyui`` skill in ~/.agents/skills/comfyui (SKILL.md + MODELS.md).`n"; Ok "AGENTS.md pointer added" }

Write-Host "[codex] done. Restart codex so the skill + MCP load." -ForegroundColor White
