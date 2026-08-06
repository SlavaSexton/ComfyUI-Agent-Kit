<#
.SYNOPSIS
  Claude Code adapter: install the comfyui skill, register the MCP, append the auto-activation block.
  Assumes shared/install_shared.ps1 already ran (comfyui-mcp global, templates cloned).
  Note: GLM (z.ai) run through Claude Code uses this same adapter, since it reads ~/.claude/skills.
.PARAMETER TemplatesDir
  Templates location to record in the activation pointer. Default matches the shared installer.
#>
param([string]$TemplatesDir = "$env:USERPROFILE\comfyui-agent-kit-data\workflow_templates")
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent (Split-Path -Parent $Here)
$Shared = Join-Path $RepoRoot "shared\comfyui"
$SkillsDest = "$env:USERPROFILE\.claude\skills"
$ClaudeMd = "$env:USERPROFILE\.claude\CLAUDE.md"
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

Write-Host "`n[claude] adapter" -ForegroundColor White
if (-not (Have "claude")) { Warn "claude CLI not on PATH; install Claude Code first"; throw "claude missing" }

# 1. skill (shared knowledge) -> ~/.claude/skills/comfyui
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
  if (Test-Path $keep) { $tmpKeep = [IO.Path]::GetTempFileName(); Copy-Item $keep $tmpKeep -Force }
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  Copy-Item (Join-Path $sk.FullName "*") $dest -Recurse -Force
  if ($tmpKeep) { Copy-Item $tmpKeep $keep -Force; Remove-Item $tmpKeep -Force }
  Ok "$($sk.Name) skill -> $dest"
}




# 2. node-building skills (Layer 4)
$tmp = Join-Path $env:TEMP ("cns_" + [guid]::NewGuid().ToString("N").Substring(0,8))
Native { git clone --depth 1 https://github.com/jtydhr88/comfyui-custom-node-skills.git $tmp } | Out-Null
$src = Join-Path $tmp "plugins\comfyui-custom-nodes\skills"
if (Test-Path $src) { Get-ChildItem $src -Directory | ForEach-Object { $d="$SkillsDest\$($_.Name)"; if (Test-Path $d){Remove-Item $d -Recurse -Force -EA SilentlyContinue}; Copy-Item $_.FullName $d -Recurse -Force }; Ok "node-building skills installed" } else { Warn "node skills not found" }
Remove-Item $tmp -Recurse -Force -EA SilentlyContinue

# 3. register MCP
$already = $false; try { & claude mcp get comfyui *> $null; if ($LASTEXITCODE -eq 0) { $already = $true } } catch {}
if ($already) { Ok "MCP 'comfyui' already registered" }
else { & claude mcp add comfyui --scope user -- comfyui-mcp; if ($LASTEXITCODE -eq 0) { Ok "MCP registered" } else { Warn "register manually: claude mcp add comfyui --scope user -- comfyui-mcp" } }

# 4. auto-activation block in CLAUDE.md
$marker = "### ComfyUI media generation (auto-activation)"
$existing = ""; if (Test-Path $ClaudeMd) { $existing = Get-Content $ClaudeMd -Raw }
if ($existing -match [regex]::Escape($marker)) { Ok "activation block present" }
else { $s = (Get-Content "$Here\claude_md_activation.md" -Raw).Replace("__TEMPLATES_DIR__", $TemplatesDir); Add-Content $ClaudeMd "`n$s"; Ok "activation block appended" }

Write-Host "[claude] done. Start ComfyUI, then run the BOOTSTRAP once (docs/BOOTSTRAP.md)." -ForegroundColor White
