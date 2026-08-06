<#
.SYNOPSIS
  Qwen Code adapter (a Gemini-CLI fork). Ships an extension at ~/.qwen/extensions/comfyui bundling the MCP server
  + the knowledge as QWEN.md. Manifest is qwen-extension.json. Assumes shared/install_shared.ps1 already ran.
#>
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent (Split-Path -Parent $Here)
$Shared = Join-Path $RepoRoot "shared\comfyui"
$Ext = "$env:USERPROFILE\.qwen\extensions\comfyui"
function Ok($m){ Write-Host "  [ok] $m" -ForegroundColor Green }
function Warn($m){ Write-Host "  [!]  $m" -ForegroundColor Yellow }
function Have($c){ return [bool](Get-Command $c -ErrorAction SilentlyContinue) }

Write-Host "`n[qwen] adapter" -ForegroundColor White
if (-not (Have "qwen")) { Warn "qwen CLI not on PATH; install Qwen Code first"; throw "qwen missing" }

New-Item -ItemType Directory -Force -Path $Ext | Out-Null

$skill = Get-Content "$Shared\SKILL.md" -Raw
$body = [regex]::Replace($skill, '(?s)^\s*---.*?---\s*', '')
$qwen = "# ComfyUI media generation (always-on context for Qwen Code)`n`nUse this whenever a task involves generating or rendering images, video, or audio with ComfyUI, or building/`nrunning a ComfyUI workflow. The per-model prompting reference is MODELS.md next to this file.`n`n$body"
Set-Content "$Ext\QWEN.md" $qwen -Encoding utf8
# RESPONSIBLE FOR (2026-08-06 audit): only MODELS.md + the client were copied, so every docs/ and
# NODE_LIBRARY route in the context file pointed at nothing. Ship the BUILT bundle.
$Bundle = Join-Path $RepoRoot "claude-code\skills"
if (-not (Test-Path $Bundle)) { throw "bundle missing at $Bundle - run: python tools/build_plugin.py" }
# MIGRATION (3.0.0): the machine block used to live inside QWEN.md, which this installer regenerates on every
# run. Lift it out first or the upgrade destroys the bootstrap.
$ctxFile = Join-Path $Ext "QWEN.md"
$machineOut = Join-Path $Ext "machine.md"
if ((-not (Test-Path $machineOut)) -and (Test-Path $ctxFile)) {
  $old = Get-Content $ctxFile -Raw
  if ($old -match '(?m)^## Your machine') {
    $buf = @(); $on = $false
    foreach ($l in ($old -split "`r?`n")) {
      if ($l -match '^## Your machine') { $on = $true }
      elseif ($on -and $l -match '^## ') { break }
      if ($on) { $buf += $l }
    }
    if ($buf.Count -gt 1) {
      Set-Content $machineOut ("# Your machine`n`nMigrated out of QWEN.md by the 3.0.0 installer. Created once, never overwritten.`n`n" + ($buf -join "`n")) -Encoding utf8
      Ok "machine block migrated out of QWEN.md -> machine.md"
    }
  }
}
$keep = Join-Path $Ext "machine.md"; $tmpKeep = $null
if (Test-Path $keep) { $tmpKeep = [IO.Path]::GetTempFileName(); Copy-Item $keep $tmpKeep -Force }
Copy-Item (Join-Path $Bundle "comfyui\*") $Ext -Recurse -Force
if ($tmpKeep) { Copy-Item $tmpKeep $keep -Force; Remove-Item $tmpKeep -Force }
foreach ($sk in Get-ChildItem $Bundle -Directory | Where-Object { $_.Name -ne "comfyui" }) {
  $d = Join-Path $Ext $sk.Name; New-Item -ItemType Directory -Force -Path $d | Out-Null
  Copy-Item (Join-Path $sk.FullName "*") $d -Recurse -Force
}
Ok "full kit (docs, NODE_LIBRARY, MODELS/, sibling skills) -> $Ext"

Ok "QWEN.md + MODELS.md + client -> $Ext"

$manifest = @'
{
  "name": "comfyui",
  "version": "1.0.0",
  "description": "Drive a local ComfyUI for image, video, and audio generation. By AI VFX NEWS.",
  "contextFileName": "QWEN.md",
  "mcpServers": {
    "comfyui": {
      "command": "comfyui-mcp",
      "args": [],
      "cwd": "${extensionPath}"
    }
  }
}
'@
Set-Content "$Ext\qwen-extension.json" $manifest -Encoding utf8
Ok "qwen-extension.json written"

Write-Host "[qwen] done. Restart qwen so the extension + MCP load." -ForegroundColor White
