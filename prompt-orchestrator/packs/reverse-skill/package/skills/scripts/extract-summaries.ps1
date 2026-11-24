#Requires -Version 5.1
# Generates skills/INDEX.md: extracts name+description from the frontmatter of each module SKILL.md and builds a navigation index.
# Idempotent: repeated runs produce the same output (CI checks for drift with git diff).
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File skills/scripts/extract-summaries.ps1
#   powershell -File skills/scripts/extract-summaries.ps1 -Check   # check only, no write (CI mode, exit 1 on mismatch)
param(
    [switch] $Check
)
$ErrorActionPreference = 'Stop'

$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path }
$skillsRoot = Split-Path -Parent $scriptDir
$indexPath = Join-Path $skillsRoot 'INDEX.md'

# Scan the module SKILL.md files in the repository (excluding local ignored/private trees, so a clean clone and a dev machine give the same result).
$skipDirs = @('ops', 'scripts', 'config', 'tests', 'field-journal', 'references')
$packageRoot = Split-Path -Parent $skillsRoot
$trackedSkillFiles = @()
$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) {
    $trackedPaths = @(& $git.Source -C $packageRoot ls-files -- 'skills/**/SKILL.md')
    if ($LASTEXITCODE -eq 0) {
        $trackedSkillFiles = @($trackedPaths | ForEach-Object {
            $fullPath = Join-Path $packageRoot ($_ -replace '/', [IO.Path]::DirectorySeparatorChar)
            if (Test-Path -LiteralPath $fullPath -PathType Leaf) { Get-Item -LiteralPath $fullPath }
        })
    }
}
$candidateSkillFiles = if ($trackedSkillFiles.Count -gt 0) {
    $trackedSkillFiles
} else {
    @(Get-ChildItem -Path $skillsRoot -Recurse -Filter 'SKILL.md')
}
$skillFiles = $candidateSkillFiles | Where-Object {
    $rel = $_.FullName.Substring($skillsRoot.Length + 1)
    $rel -ne 'SKILL.md' -and -not ($skipDirs | Where-Object { $rel.StartsWith($_ + '\') -or $rel.StartsWith($_ + '/') })
} | Sort-Object { $_.FullName.Substring($skillsRoot.Length + 1) }

$rows = New-Object System.Collections.ArrayList
foreach ($sf in $skillFiles) {
    $rel = $sf.FullName.Substring($skillsRoot.Length + 1)
    # Handles both Windows (\) and Linux/macOS (/) path separators
    $dir = $rel.Split(@('\', '/'))[0]
    $head = Get-Content -LiteralPath $sf.FullName -TotalCount 15 -Encoding UTF8
    $name = ''; $desc = ''; $blockMode = $false; $inFm = $false
    foreach ($line in $head) {
        if ($line -match '^---') {
            if ($inFm) { break }   # the second --- ends the frontmatter
            $inFm = $true; continue
        }
        if (-not $inFm) { continue }
        if ($line -match '^name:\s*(.+)$') { $name = $Matches[1].Trim(); continue }
        if ($line -match '^description:\s*\|') { $blockMode = $true; continue }
        if ($line -match '^description:\s*(.+)$') { $desc = $Matches[1].Trim(); continue }
        if ($blockMode) {
            # YAML block: join the indented text lines (take the first line, truncate when too long)
            if ($line -match '^\s{2,}(.+)$') {
                if (-not $desc) { $desc = $Matches[1].Trim() }
            } elseif ($line -match '^\S') { $blockMode = $false }
        }
    }
    if (-not $name) { $name = $dir }
    if (-not $desc) { $desc = '(no summary)' }
    if ($desc.Length -gt 160) { $desc = $desc.Substring(0, 157) + '...' }
    [void]$rows.Add([pscustomobject]@{
        Dir  = $dir
        Name = $name
        Desc = $desc
        Path = $rel
    })
}

$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine('# reverse-skill Skill Navigation Index')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('> `skills/scripts/extract-summaries.ps1` generates this file automatically. **Do not edit it by hand.**')
[void]$sb.AppendLine('> To change a summary, edit the frontmatter `description` of the module `SKILL.md`, then rerun the script.')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## Module overview')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('| Module | Summary |')
[void]$sb.AppendLine('|------|------|')
foreach ($r in $rows) {
    $esc = $r.Desc -replace '\|', '\|'
    [void]$sb.AppendLine(("| [{0}]({1}) | {2} |" -f $r.Name, ($r.Path -replace '\\', '/'), $esc))
}
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## Directory tree')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('```')
foreach ($r in $rows) {
    # Emit module directories, not SKILL.md file paths (see issue #151).
    # Normalize to forward slashes: Windows Split-Path returns backslashes.
    $path = $r.Path -replace '\\', '/'
    $dir = Split-Path -Parent $path
    if ([string]::IsNullOrEmpty($dir)) { $dir = $r.Name }
    $dir = $dir -replace '\\', '/'
    [void]$sb.AppendLine(("skills/{0}/" -f $dir))
}
[void]$sb.AppendLine('```')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## Routing')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('`skills/config/routing.json` (the single source of truth) drives PRIMARY routing; platform-native entry points: `master-route.ps1` (Windows) / `master-route.sh` (Linux, macOS, Kali).')
[void]$sb.AppendLine('For ambiguous cases read the full matrix in `skills/routing.md`; multi-type CTF tasks go to `CTF-Sandbox-Orchestrator/`.')

$newContent = $sb.ToString()
# Use LF line endings consistently: matches .gitattributes (*.md eol=lf) so -Check is idempotent after clone
$newContent = $newContent -replace "`r`n", "`n"
$utf8 = New-Object System.Text.UTF8Encoding $true

if ($Check) {
    if (-not (Test-Path -LiteralPath $indexPath)) {
        Write-Host '[CHECK] INDEX.md missing' -ForegroundColor Red
        exit 1
    }
    # Line-ending immunity: on machines with autocrlf=true the worktree may be CRLF, so normalize before comparing
    $old = ([System.IO.File]::ReadAllText($indexPath)) -replace "`r`n", "`n"
    if ($old -eq $newContent) {
        Write-Host '[CHECK] INDEX.md up to date' -ForegroundColor Green
        exit 0
    }
    Write-Host '[CHECK] INDEX.md out of date (run extract-summaries.ps1)' -ForegroundColor Red
    exit 1
}

[System.IO.File]::WriteAllText($indexPath, $newContent, $utf8)
Write-Host ("INDEX.md regenerated: {0} modules" -f $rows.Count) -ForegroundColor Green
