# ---------------------------------------------------------------------------------------------
# Runtime (tools/installer/runtime.ps1). Windows PowerShell 5.1 or PowerShell 7, no Python for
# the core and the packs. $PO_Data above this line comes from install/spec.json and packs/.
# The manifest has the same columns as install.sh: owner, kind, path, hash, extra.
# ---------------------------------------------------------------------------------------------

$script:Utf8 = New-Object System.Text.UTF8Encoding($false)
$script:HarnessMark = 'prompt-orchestrator-harness'
$script:Sep = [System.IO.Path]::DirectorySeparatorChar

function Write-PoSay([string]$Text) { Write-Host $Text }
function Write-PoWarn([string]$Text) { Write-Host "warning: $Text" -ForegroundColor Yellow }
function Stop-Po([string]$Text) { throw "error: $Text" }
function Add-PoChange { $script:Changes++ }

# ------------------------------------------------------------------ locations

function Expand-PoPath([string]$Text) {
    $out = $Text
    foreach ($m in [regex]::Matches($Text, '\{([A-Z_]+)\}')) {
        $name = $m.Groups[1].Value
        if (-not $script:Loc.Contains($name)) { Stop-Po "location {$name} is not set" }
        $out = $out.Replace($m.Value, [string]$script:Loc[$name])
    }
    return $out.Replace('/', $script:Sep)
}

function Initialize-PoLocations {
    $script:Loc = [ordered]@{}
    foreach ($name in $PO_Data['locations'].Keys) {
        $value = $null
        foreach ($alt in $PO_Data['locations'][$name]) {
            if ($alt.Contains('env')) {
                $v = [Environment]::GetEnvironmentVariable($alt['env'])
                if ($v) {
                    if ($alt.Contains('join')) { $value = Join-Path $v $alt['join'] } else { $value = $v }
                    break
                }
            } elseif ($alt.Contains('if_dir')) {
                if (Test-Path -LiteralPath (Expand-PoPath $alt['if_dir']) -PathType Container) { $value = Expand-PoPath $alt['path']; break }
            } else {
                $value = Expand-PoPath $alt['path']
                break
            }
        }
        if (-not $value) { Stop-Po "cannot resolve the $name location" }
        $script:Loc[$name] = $value
    }
}

# ------------------------------------------------------------------ hashing and text

function Get-PoTextHash([string]$Text) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = $sha.ComputeHash($script:Utf8.GetBytes($Text))
    return (($bytes | ForEach-Object { $_.ToString('x2') }) -join '')
}

function Get-PoFileHash([string]$Path) { return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }

function Read-PoText([string]$Path) { return [System.IO.File]::ReadAllText($Path, $script:Utf8) }

function Write-PoText([string]$Path, [string]$Text) { [System.IO.File]::WriteAllText($Path, $Text, $script:Utf8) }

function Split-PoLines([string]$Text) { return ,([regex]::Split($Text.Replace("`r`n", "`n"), "`n")) }

function Join-PoTrimmed($Lines) {  # drop trailing blank lines, join with LF
    $list = @($Lines)
    $n = $list.Count
    while ($n -gt 0 -and $list[$n - 1].Trim() -eq '') { $n-- }
    if ($n -eq 0) { return '' }
    return (($list[0..($n - 1)]) -join "`n")
}

function Get-PoMarkedParts([string]$Text, [string]$Marker) {  # returns @(outside, block)
    $start = "<!-- ${Marker}:start -->"
    $end = "<!-- ${Marker}:end -->"
    $outside = New-Object System.Collections.Generic.List[string]
    $block = New-Object System.Collections.Generic.List[string]
    $on = $false
    foreach ($line in (Split-PoLines $Text)) {
        if ($line -ceq $start) { $on = $true }
        if ($on) { $block.Add($line) } else { $outside.Add($line) }
        if ($line -ceq $end) { $on = $false }
    }
    return @((Join-PoTrimmed $outside), ($block -join "`n"))
}

function Get-PoDocHash([string]$Path) {
    $parts = Get-PoMarkedParts (Read-PoText $Path) $script:HarnessMark
    return Get-PoTextHash $parts[0]
}

# ------------------------------------------------------------------ manifest

function Read-PoManifest {
    $list = New-Object System.Collections.Generic.List[object]
    if (Test-Path -LiteralPath $script:Manifest -PathType Leaf) {
        foreach ($line in [System.IO.File]::ReadAllLines($script:Manifest, $script:Utf8)) {
            if (-not $line) { continue }
            $p = $line.Split("`t")
            if ($p.Count -lt 5) { continue }
            $list.Add([pscustomobject]@{ Owner = $p[0]; Kind = $p[1]; Path = $p[2]; Hash = $p[3]; Extra = $p[4] })
        }
    }
    return ,$list
}

function Format-PoRecord($R) { return "$($R.Owner)`t$($R.Kind)`t$($R.Path)`t$($R.Hash)`t$($R.Extra)" }

function Save-PoManifest($List) {
    if ($script:Dry) { return }
    $lines = New-Object System.Collections.Generic.List[string]
    $seen = @{}
    foreach ($r in $List) {
        $line = Format-PoRecord $r
        if (-not $seen.ContainsKey($line)) { $seen[$line] = $true; $lines.Add($line) }
    }
    if ($lines.Count -eq 0) {
        if (Test-Path -LiteralPath $script:Manifest) { Remove-Item -LiteralPath $script:Manifest -Force }
        return
    }
    New-PoDir $script:DataHome
    foreach ($d in $script:DirsNew) { $line = Format-PoRecord $d; if (-not $seen.ContainsKey($line)) { $seen[$line] = $true; $lines.Add($line) } }
    $script:DirsNew.Clear()
    [System.IO.File]::WriteAllLines($script:Manifest, $lines, $script:Utf8)
}

function New-PoRecord($Owner, $Kind, $Path, $Hash, $Extra) {
    if (-not $Hash) { $Hash = '-' }
    if (-not $Extra) { $Extra = '-' }
    return [pscustomobject]@{ Owner = $Owner; Kind = $Kind; Path = $Path; Hash = $Hash; Extra = $Extra }
}

function Add-PoRecord($Kind, $Path, $Hash, $Extra) { $script:New.Add((New-PoRecord $script:Owner $Kind $Path $Hash $Extra)) }

function Test-PoKnownHash([string]$Path, [string]$Hash) {
    foreach ($r in (Read-PoManifest)) { if ($r.Path -eq $Path -and $r.Hash -eq $Hash) { return $true } }
    return $false
}

function New-PoDir([string]$Dir) {
    if (-not $Dir -or (Test-Path -LiteralPath $Dir -PathType Container)) { return }
    if (Test-Path -LiteralPath $Dir) { Stop-Po "$Dir exists and is not a folder" }
    New-PoDir (Split-Path -Parent $Dir)
    if ($script:Dry) { return }
    New-Item -ItemType Directory -Path $Dir | Out-Null
    $script:DirsNew.Add((New-PoRecord '@dirs' 'D' $Dir '-' '-'))
}

function Start-PoOwner([string]$Owner) {
    $script:Owner = $Owner
    $script:New = New-Object System.Collections.Generic.List[object]
    $script:Old = @((Read-PoManifest) | Where-Object { $_.Owner -ceq $Owner })
}

function Complete-PoOwner {
    $owner = $script:Owner
    if ($script:Dry) { $script:Owner = ''; return }
    $live = @{}
    foreach ($r in $script:New) { if ($r.Kind -ne 'k') { $live[$r.Path] = $true } }
    foreach ($r in $script:Old) {
        if ($r.Kind -ne 'k') { continue }
        $inside = $live.ContainsKey($r.Path)
        if (-not $inside) { $prefix = $r.Path.TrimEnd('\', '/') + $script:Sep; foreach ($l in $live.Keys) { if ($l.StartsWith($prefix)) { $inside = $true; break } } }
        if ($inside) { $script:New.Add($r) }
    }
    $keys = @{}
    foreach ($r in $script:New) { $keys["$($r.Kind)`t$($r.Path)"] = $true }
    $stale = @($script:Old | Where-Object { -not $keys.ContainsKey("$($_.Kind)`t$($_.Path)") })
    $all = New-Object System.Collections.Generic.List[object]
    foreach ($r in (Read-PoManifest)) { if ($r.Owner -cne $owner) { $all.Add($r) } }
    foreach ($r in $script:New) { $all.Add($r) }
    Save-PoManifest $all
    if ($stale.Count -gt 0) {
        Remove-PoRecords $stale ''
        Clear-PoDirs
    }
    $script:Owner = ''
}

# ------------------------------------------------------------------ file operations

function Backup-PoItem([string]$Path) {
    $rel = $Path -replace '^[A-Za-z]:', '' -replace '^[\\/]+', ''
    $dest = Join-Path (Join-Path (Join-Path $script:DataHome 'backups') $script:Stamp) $rel
    New-PoDir (Split-Path -Parent $dest)
    Move-Item -LiteralPath $Path -Destination $dest
    Add-PoRecord 'k' $Path $dest
    Write-PoSay "  backed up $Path -> $dest"
}

function Copy-PoFile([string]$Src, [string]$Dst, [string]$SrcHash) {
    $dh = '-'
    if (Test-Path -LiteralPath $Dst -PathType Leaf) { $dh = Get-PoFileHash $Dst }
    if ($SrcHash -eq $dh) { Add-PoRecord 'f' $Dst $SrcHash; return }
    Add-PoChange
    if ($script:Dry) { Write-PoSay "  would write $Dst"; return }
    if ($dh -ne '-' -and -not (Test-PoKnownHash $Dst $dh)) { Backup-PoItem $Dst }
    New-PoDir (Split-Path -Parent $Dst)
    Copy-Item -LiteralPath $Src -Destination $Dst -Force
    Add-PoRecord 'f' $Dst $SrcHash
}

function Get-PoFiles([string]$Dir) {  # relative paths, sorted, without caches
    $base = (Resolve-Path -LiteralPath $Dir).ProviderPath.TrimEnd('\', '/')
    $items = Get-ChildItem -LiteralPath $base -Recurse -File -Force | Where-Object {
        $_.Name -notlike '*.pyc' -and $_.Name -ne '.DS_Store' -and $_.FullName -notmatch '[\\/]__pycache__[\\/]'
    }
    $rel = @($items | ForEach-Object { $_.FullName.Substring($base.Length + 1) })
    [System.Array]::Sort($rel, [System.StringComparer]::Ordinal)
    return ,$rel
}

function Copy-PoTree([string]$Src, [string]$Dst) {
    if (-not (Test-Path -LiteralPath $Src -PathType Container)) { Stop-Po "missing source folder $Src (run: python tools\generate_integrations.py)" }
    foreach ($rel in (Get-PoFiles $Src)) {
        $from = Join-Path $Src $rel
        Copy-PoFile $from (Join-Path $Dst $rel) (Get-PoFileHash $from)
    }
}

function Copy-PoSingle([string]$Src, [string]$Dst) {
    if (-not (Test-Path -LiteralPath $Src -PathType Leaf)) { Stop-Po "missing source file $Src (run: python tools\generate_integrations.py)" }
    Copy-PoFile $Src $Dst (Get-PoFileHash $Src)
}

function Copy-PoDoc([string]$Src, [string]$Dst) {
    if (-not (Test-Path -LiteralPath $Src -PathType Leaf)) { Stop-Po "missing source file $Src (run: python tools\generate_integrations.py)" }
    $text = Join-PoTrimmed (Split-PoLines (Read-PoText $Src))
    $sh = Get-PoTextHash $text
    $dh = '-'
    $block = ''
    if (Test-Path -LiteralPath $Dst -PathType Leaf) {
        $parts = Get-PoMarkedParts (Read-PoText $Dst) $script:HarnessMark
        $dh = Get-PoTextHash $parts[0]
        $block = $parts[1]
    }
    if ($sh -eq $dh) { Add-PoRecord 'd' $Dst $sh; return }
    Add-PoChange
    if ($script:Dry) { Write-PoSay "  would write $Dst"; return }
    if ($dh -ne '-' -and -not (Test-PoKnownHash $Dst $dh)) { Backup-PoItem $Dst }
    New-PoDir (Split-Path -Parent $Dst)
    $out = $text + "`n"
    if ($block) { $out += "`n" + $block + "`n" }
    Write-PoText $Dst $out
    Add-PoRecord 'd' $Dst $sh
}

function Add-PoBlock([string]$Dst, [string]$Marker, [string]$Text) {
    $start = "<!-- ${Marker}:start -->"
    if ((Test-Path -LiteralPath $Dst -PathType Leaf) -and (Read-PoText $Dst).Contains($start)) {
        $made = 'old'
        foreach ($r in $script:Old) { if ($r.Kind -eq 'b' -and $r.Path -eq $Dst) { $made = $r.Extra } }
        Add-PoRecord 'b' $Dst $Marker $made
        return
    }
    Add-PoChange
    if ($script:Dry) { Write-PoSay "  would add the $Marker block to $Dst"; return }
    $made = 'old'
    if (-not (Test-Path -LiteralPath $Dst)) { $made = 'new' }
    New-PoDir (Split-Path -Parent $Dst)
    $current = ''
    if ($made -eq 'old') { $current = Read-PoText $Dst }
    Write-PoText $Dst ($current + "`n$start`n$Text`n<!-- ${Marker}:end -->`n")
    Add-PoRecord 'b' $Dst $Marker $made
}

function Remove-PoMarkedBlock([string]$Text, [string]$Marker) {
    $start = "<!-- ${Marker}:start -->"
    $end = "<!-- ${Marker}:end -->"
    $out = New-Object System.Collections.Generic.List[string]
    $skip = $false
    foreach ($line in (Split-PoLines $Text)) {
        if ($line -ceq $start) {
            $skip = $true
            if ($out.Count -gt 0 -and $out[$out.Count - 1] -eq '') { $out.RemoveAt($out.Count - 1) }
            continue
        }
        if ($skip) { if ($line -ceq $end) { $skip = $false }; continue }
        $out.Add($line)
    }
    return ($out -join "`n")
}

function Get-PoSnapshot($Paths) {  # path -> hash for every file under the tracked paths
    $map = [ordered]@{}
    foreach ($p in $Paths) {
        if (Test-Path -LiteralPath $p -PathType Container) {
            foreach ($f in (Get-ChildItem -LiteralPath $p -Recurse -File -Force)) { $map[$f.FullName] = Get-PoFileHash $f.FullName }
        } elseif (Test-Path -LiteralPath $p -PathType Leaf) {
            $map[$p] = Get-PoFileHash $p
        }
    }
    return $map
}

function Get-PoDirSnapshot($Paths) {
    $set = @{}
    foreach ($p in $Paths) {
        $d = $p
        if ($d -match '\.json$|[\\/]\.gitconfig$') { $d = Split-Path -Parent $d }
        while ($d -and -not (Test-Path -LiteralPath $d)) { $set["missing:$d"] = $true; $d = Split-Path -Parent $d }
        if (Test-Path -LiteralPath $p -PathType Container) {
            $set[$p] = $true
            foreach ($f in (Get-ChildItem -LiteralPath $p -Recurse -Directory -Force)) { $set[$f.FullName] = $true }
        }
    }
    return $set
}

function Start-PoTrack($Paths) {
    $script:Track = @($Paths)
    $script:TrackBefore = Get-PoSnapshot $script:Track
    $script:TrackDirs = Get-PoDirSnapshot $script:Track
}

function Complete-PoTrack {
    $after = Get-PoSnapshot $script:Track
    $changed = $after.Count -ne $script:TrackBefore.Count
    foreach ($f in $after.Keys) {
        $h = $after[$f]
        if (-not $script:TrackBefore.Contains($f)) { Add-PoRecord 'x' $f $h; $changed = $true; continue }
        if ($script:TrackBefore[$f] -ne $h) { $changed = $true }
        foreach ($r in $script:Old) { if ($r.Kind -eq 'x' -and $r.Path -eq $f) { Add-PoRecord 'x' $f $h; break } }
    }
    foreach ($key in $script:TrackDirs.Keys) {
        if ($key.StartsWith('missing:')) {
            $d = $key.Substring(8)
            if (Test-Path -LiteralPath $d -PathType Container) { $script:DirsNew.Add((New-PoRecord '@dirs' 'D' $d '-' '-')) }
        }
    }
    foreach ($p in $script:Track) {
        if (Test-Path -LiteralPath $p -PathType Container) {
            foreach ($f in (Get-ChildItem -LiteralPath $p -Recurse -Directory -Force)) {
                if (-not $script:TrackDirs.ContainsKey($f.FullName)) { $script:DirsNew.Add((New-PoRecord '@dirs' 'D' $f.FullName '-' '-')) }
            }
        }
    }
    if ($changed) { Add-PoChange }
}

function Find-PoPython([int]$Major, [int]$Minor) {  # returns @(exe, prefix args) or $null
    foreach ($c in @('py', 'python3', 'python')) {
        $cmd = Get-Command $c -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }
        $prefix = @()
        if ($c -eq 'py') { $prefix = @('-3') }
        & $cmd.Source @prefix -c "import sys; sys.exit(0 if sys.version_info >= ($Major, $Minor) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) { return @($cmd.Source, $prefix) }
    }
    return $null
}

function Invoke-PoAttribution([string]$Script, [string]$HooksPath, $Tracks) {
    $py = Find-PoPython 3 0
    if (-not $py -or -not (Test-Path -LiteralPath $Script)) {
        if ($script:Dry -and $py) { Write-PoSay "  would run $Script"; return }
        Write-PoWarn "Python or $Script missing: AI attribution not forced off"
        return
    }
    if ($script:Dry) { Write-PoSay "  would run $($py[0]) $Script"; return }
    Start-PoTrack $Tracks
    $prefix = $py[1]
    & $py[0] @prefix $Script --quiet | Out-Host
    if ($LASTEXITCODE -ne 0) { Write-PoWarn 'ensure_attribution_off.py exited with an error' }
    Complete-PoTrack
    Add-PoRecord 'u' $HooksPath '-' 'git-hooks'
    Add-PoRecord 'u' @($Tracks)[0] '-' 'json-strip:no-ai-trailer'
}

function Install-PoPlugin([string]$Src, [string]$Mirror, [string]$Dst, [string]$Backups) {
    if (-not (Test-Path -LiteralPath (Join-Path $Src 'plugin.json')) -or -not (Test-Path -LiteralPath (Join-Path $Src 'skills') -PathType Container)) {
        Stop-Po "missing $Src (run: python tools\generate_integrations.py)"
    }
    $a = Get-PoFiles (Join-Path $Src 'skills')
    $b = Get-PoFiles $Mirror
    $same = ($a -join "`n") -eq ($b -join "`n")
    if ($same) {
        foreach ($rel in $a) {
            if ((Get-PoFileHash (Join-Path (Join-Path $Src 'skills') $rel)) -ne (Get-PoFileHash (Join-Path $Mirror $rel))) { $same = $false; break }
        }
    }
    if (-not $same) { Stop-Po "$Src\skills differs from $Mirror; regenerate with python tools\generate_integrations.py" }
    $item = Get-Item -LiteralPath $Dst -Force -ErrorAction SilentlyContinue
    if ($item -and (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -or -not $item.PSIsContainer)) {
        Stop-Po "refusing to replace a link or file: $Dst"
    }
    if ($item) {
        $ours = $false
        $prefix = $Dst.TrimEnd('\', '/') + $script:Sep
        foreach ($r in (Read-PoManifest)) { if ($r.Kind -eq 'f' -and $r.Path.StartsWith($prefix)) { $ours = $true; break } }
        if (-not $ours) {
            Add-PoChange
            $kept = Join-Path $Backups "prompt-orchestrator-$($script:Stamp)"
            if ($script:Dry) { Write-PoSay "  would move the existing plugin $Dst to $Backups" }
            else {
                New-PoDir $Backups
                Move-Item -LiteralPath $Dst -Destination $kept
                Add-PoRecord 'k' $Dst $kept
                Write-PoSay "  previous plugin kept at $kept"
            }
        }
    }
    Copy-PoTree $Src $Dst
}

# ------------------------------------------------------------------ JSON hook edits

function Test-PoJsonHas([string]$File, [string]$Needle) {
    if (-not (Test-Path -LiteralPath $File -PathType Leaf)) { return $false }
    $text = (Read-PoText $File).Replace('\\', '/').Replace('\', '/')
    return $text.Contains($Needle.Replace('\', '/'))
}

function Remove-PoJsonHooks([string]$File, [string]$Needle) {
    if (-not (Test-PoJsonHas $File $Needle)) { return }
    $data = (Read-PoText $File) | ConvertFrom-Json
    if (-not $data.hooks) { return }
    $removed = 0
    foreach ($prop in @($data.hooks.PSObject.Properties)) {
        $groups = @()
        foreach ($g in @($prop.Value)) {
            $entries = @($g.hooks)
            $kept = @($entries | Where-Object { -not ([string]$_.command).Replace('\', '/').Contains($Needle) })
            $removed += $entries.Count - $kept.Count
            if ($kept.Count -gt 0) { $g.hooks = $kept; $groups += $g }
        }
        if ($groups.Count -gt 0) { $prop.Value = $groups } else { $data.hooks.PSObject.Properties.Remove($prop.Name) }
    }
    if ($removed -gt 0) { Write-PoText $File (($data | ConvertTo-Json -Depth 32) + "`n"); Add-PoChange }
}

function Add-PoJsonHooks([string]$File, [string]$Command, $Hooks) {
    if (Test-PoJsonHas $File $Command) { return $false }
    if (Test-Path -LiteralPath $File) { $data = (Read-PoText $File) | ConvertFrom-Json } else { $data = [pscustomobject]@{} }
    if (-not $data.PSObject.Properties['hooks']) { $data | Add-Member -NotePropertyName hooks -NotePropertyValue ([pscustomobject]@{}) }
    foreach ($h in $Hooks) {
        $entry = [ordered]@{}
        if ($h['matcher']) { $entry['matcher'] = $h['matcher'] }
        $entry['hooks'] = @([ordered]@{ type = 'command'; command = $Command; timeout = $h['timeout']; statusMessage = $h['status'] })
        $existing = $data.hooks.PSObject.Properties[$h['event']]
        if ($existing) { $existing.Value = @($existing.Value) + @([pscustomobject]$entry) }
        else { $data.hooks | Add-Member -NotePropertyName $h['event'] -NotePropertyValue @([pscustomobject]$entry) }
    }
    New-PoDir (Split-Path -Parent $File)
    Write-PoText $File (($data | ConvertTo-Json -Depth 32) + "`n")
    return $true
}

# ------------------------------------------------------------------ removal

function Remove-PoRecords($Records, [string]$Removing) {
    $ref = @{}
    foreach ($r in (Read-PoManifest)) {
        if ($r.Owner -ne '@dirs' -and $r.Owner -cne $Removing -and @('k', 'u', 'h', 'm', 'n') -notcontains $r.Kind) { $ref[$r.Path] = $true }
    }
    foreach ($r in @($Records | Where-Object { $_.Kind -eq 'h' })) { Uninstall-PoHarness $r.Path }
    foreach ($r in $Records) {
        if ($ref.ContainsKey($r.Path) -and @('m', 'n') -notcontains $r.Kind) { continue }
        $path = $r.Path
        switch ($r.Kind) {
            { $_ -in @('f', 'x') } {
                if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { break }
                if ((Get-PoFileHash $path) -eq $r.Hash) { Remove-Item -LiteralPath $path -Force; Add-PoChange }
                else { Write-PoWarn "kept ${path}: changed since install" }
            }
            'd' {
                if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { break }
                $parts = Get-PoMarkedParts (Read-PoText $path) $script:HarnessMark
                if ((Get-PoTextHash $parts[0]) -eq $r.Hash) {
                    if ($parts[1]) { Write-PoText $path ($parts[1] + "`n") } else { Remove-Item -LiteralPath $path -Force }
                    Add-PoChange
                } else { Write-PoWarn "kept ${path}: changed since install" }
            }
            'b' {
                if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { break }
                $text = Remove-PoMarkedBlock (Read-PoText $path) $r.Hash
                if ($r.Extra -eq 'new' -and -not $text.Trim()) { Remove-Item -LiteralPath $path -Force } else { Write-PoText $path $text }
                Add-PoChange
            }
            'm' { Unregister-PoMcp $path $r.Hash $r.Extra }
        }
    }
    foreach ($r in $Records) {
        if ($r.Kind -ne 'u') { continue }
        if ($r.Extra -eq 'git-hooks') {
            if (Get-Command git -ErrorAction SilentlyContinue) {
                $cur = (& git config --global --get core.hooksPath 2>$null)
                if ($cur -and ($cur.Replace('/', $script:Sep) -eq $r.Path)) { & git config --global --unset core.hooksPath | Out-Null; Add-PoChange }
            }
        } elseif ($r.Extra.StartsWith('json-strip:')) {
            Remove-PoJsonHooks $r.Path $r.Extra.Substring(11)
        } elseif ($r.Extra.StartsWith('npm-rm:')) {
            Remove-PoNpmPackage $r.Path $r.Extra.Substring(7)
        }
    }
    foreach ($r in $Records) {
        if ($r.Kind -ne 'n') { continue }
        $root = (Join-Path $script:DataHome 'packages') + $script:Sep
        if (-not $r.Path.StartsWith($root)) { Write-PoWarn "kept $($r.Path): not inside $root"; continue }
        if (Test-Path -LiteralPath $r.Path) { Remove-Item -LiteralPath $r.Path -Recurse -Force; Add-PoChange }
    }
    foreach ($r in $Records) {
        if ($r.Kind -ne 'k') { continue }
        if ((Test-Path -LiteralPath $r.Path -PathType Container) -and (Test-Path -LiteralPath $r.Hash) -and
            -not (Get-ChildItem -LiteralPath $r.Path -Recurse -File -Force | Select-Object -First 1)) {
            Remove-Item -LiteralPath $r.Path -Recurse -Force
        }
        if (-not (Test-Path -LiteralPath $r.Path) -and (Test-Path -LiteralPath $r.Hash)) {
            $parent = Split-Path -Parent $r.Path
            if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
            Move-Item -LiteralPath $r.Hash -Destination $r.Path
            Write-PoSay "  restored $($r.Path)"
            Add-PoChange
        }
    }
}

function Clear-PoDirs {  # remove folders the installer created once they are empty
    $all = Read-PoManifest
    $dirs = @($all | Where-Object { $_.Owner -eq '@dirs' } | ForEach-Object { $_.Path } | Sort-Object -Descending)
    $gone = @{}
    foreach ($d in $dirs) {
        if (-not (Test-Path -LiteralPath $d -PathType Container)) { $gone[$d] = $true; continue }
        if ($d -eq $script:DataHome) { continue }
        if (-not (Get-ChildItem -LiteralPath $d -Force | Select-Object -First 1)) { Remove-Item -LiteralPath $d -Force; $gone[$d] = $true }
    }
    $keep = New-Object System.Collections.Generic.List[object]
    foreach ($r in $all) { if (-not ($r.Owner -eq '@dirs' -and $gone.ContainsKey($r.Path))) { $keep.Add($r) } }
    if (@($keep | Where-Object { $_.Owner -ne '@dirs' }).Count -eq 0) {
        if (Test-Path -LiteralPath $script:Manifest) { Remove-Item -LiteralPath $script:Manifest -Force }
        foreach ($r in @($keep | Sort-Object Path -Descending)) {
            if ((Test-Path -LiteralPath $r.Path -PathType Container) -and -not (Get-ChildItem -LiteralPath $r.Path -Force | Select-Object -First 1)) {
                Remove-Item -LiteralPath $r.Path -Force
            }
        }
        return
    }
    [System.IO.File]::WriteAllLines($script:Manifest, [string[]]@($keep | ForEach-Object { Format-PoRecord $_ }), $script:Utf8)
}

function Get-PoOwners {
    $seen = New-Object System.Collections.Generic.List[string]
    foreach ($r in (Read-PoManifest)) { if ($r.Owner -ne '@dirs' -and -not $seen.Contains($r.Owner)) { $seen.Add($r.Owner) } }
    return $seen.ToArray()
}

function Remove-PoOwner([string]$Owner) {
    $records = @((Read-PoManifest) | Where-Object { $_.Owner -ceq $Owner })
    if ($records.Count -eq 0) { return }
    Write-PoSay "--- removing $Owner"
    if ($script:Dry) { foreach ($r in $records) { Write-PoSay "  would remove $($r.Path)" }; return }
    Remove-PoRecords $records $Owner
    $keep = @((Read-PoManifest) | Where-Object { $_.Owner -cne $Owner })
    [System.IO.File]::WriteAllLines($script:Manifest, [string[]]@($keep | ForEach-Object { Format-PoRecord $_ }), $script:Utf8)
    Clear-PoDirs
}

# ------------------------------------------------------------------ tools and projects

function Get-PoTool([string]$Id) { foreach ($t in $PO_Data['tools']) { if ($t['id'] -eq $Id) { return $t } }; return $null }
function Get-PoPack([string]$Id) { foreach ($p in $PO_Data['packs']) { if ($p['id'] -eq $Id) { return $p } }; return $null }
function Get-PoSet($Pack, [string]$Id) { foreach ($s in $Pack['sets']) { if ($s['id'] -eq $Id) { return $s } }; return $null }

function Invoke-PoSteps($Steps) {
    foreach ($s in $Steps) {
        switch ($s['op']) {
            'tree' { Copy-PoTree (Join-Path $PO_Root $s['src']) (Expand-PoPath $s['dest']) }
            'file' { Copy-PoSingle (Join-Path $PO_Root $s['src']) (Expand-PoPath $s['dest']) }
            'doc' { Copy-PoDoc (Join-Path $PO_Root $s['src']) (Expand-PoPath $s['dest']) }
            'block' { Add-PoBlock (Expand-PoPath $s['dest']) $s['marker'] $s['text'] }
            'attribution' { Invoke-PoAttribution (Expand-PoPath $s['script']) (Expand-PoPath $s['hooks_path']) @($s['track'] | ForEach-Object { Expand-PoPath $_ }) }
            'plugin' { Install-PoPlugin (Join-Path $PO_Root $s['src']) (Join-Path $PO_Root $s['mirror']) (Expand-PoPath $s['dest']) (Expand-PoPath $s['backups']) }
            default { Stop-Po "unknown step $($s['op'])" }
        }
    }
}

function Install-PoCore([string]$Tool) {
    $t = Get-PoTool $Tool
    if (@($t['steps']).Count -eq 0) { return }
    Write-PoSay "=== core: $($t['label'])"
    Start-PoOwner "core:$Tool"
    Invoke-PoSteps $t['steps']
    Complete-PoOwner
}

function Install-PoProject([string]$Kind, [string]$Dir) {
    if (-not (Test-Path -LiteralPath $Dir -PathType Container)) { Stop-Po "project folder does not exist: $Dir" }
    $Dir = (Resolve-Path -LiteralPath $Dir).ProviderPath
    if ($Dir.TrimEnd('\', '/') -eq $PO_Root.TrimEnd('\', '/')) { Write-PoSay "==> $Dir is the prompt-orchestrator source; nothing to copy"; return }
    $project = $null
    foreach ($p in $PO_Data['projects']) { if ($p['id'] -eq $Kind) { $project = $p } }
    $script:Loc['PROJECT'] = $Dir
    Write-PoSay "=== $($project['label']): $Dir"
    Start-PoOwner "${Kind}:$Dir"
    Invoke-PoSteps $project['steps']
    Complete-PoOwner
}

# ------------------------------------------------------------------ harness

function Install-PoHarness([string]$Tool) {
    $t = Get-PoTool $Tool
    if (-not $t['harness']) { return }
    $h = $PO_Data['harness']
    $py = Find-PoPython $h['python'][0] $h['python'][1]
    if (-not $py) { Write-PoSay "  harness skipped for ${Tool}: needs Python $($h['python'][0]).$($h['python'][1]) or later"; return }
    $argv = @((Join-Path $PO_Root $h['script']), 'install', '--tool', $Tool)
    $family = $h['profile_tools'][$Tool]
    if ($family -eq 'claude' -and $script:ProfileClaude) { $argv += @('--profile', $script:ProfileClaude) }
    if ($family -eq 'codex' -and $script:ProfileCodex) { $argv += @('--profile', $script:ProfileCodex) }
    foreach ($o in $script:HarnessOff) { $argv += "--no-$o" }
    Write-PoSay "=== harness: $($t['label'])"
    Write-PoSay "  `$ $($py[0]) $($argv -join ' ')"
    if ($script:Dry) { return }
    $prefix = $py[1]
    & $py[0] @prefix @argv | Out-Host
    if ($LASTEXITCODE -ne 0) { $script:Failed += "harness:$Tool"; return }
    Start-PoOwner "harness:$Tool"
    Add-PoRecord 'h' $Tool
    Complete-PoOwner
}

function Uninstall-PoHarness([string]$Tool) {
    $h = $PO_Data['harness']
    $py = Find-PoPython $h['python'][0] $h['python'][1]
    if (-not $py) { Write-PoWarn "harness for $Tool not removed: needs Python $($h['python'][0]).$($h['python'][1])"; return }
    $prefix = $py[1]
    & $py[0] @prefix (Join-Path $PO_Root $h['script']) uninstall --tool $Tool | Out-Host
    if ($LASTEXITCODE -ne 0) { Write-PoWarn "harness uninstall failed for $Tool" }
}

# ------------------------------------------------------------------ packs

function Add-PoSets([string]$Spec) {
    $cur = $null
    foreach ($tok in $Spec.Split(',')) {
        if (-not $tok) { continue }
        if ($tok.Contains(':')) {
            $p, $s = $tok.Split(':', 2)
            $pack = Get-PoPack $p
            if (-not $pack) { Stop-Po "unknown pack: $p (see: install.ps1 packs list)" }
            $cur = $pack
            if (-not $s -or $s -eq '*') { foreach ($x in (Get-PoBaseSets $pack)) { Add-PoSel "${p}:$x" } }
            elseif (Get-PoSet $pack $s) { Add-PoSel "${p}:$s" }
            else { Stop-Po "pack $p has no set $s" }
        } elseif (Get-PoPack $tok) {
            $cur = Get-PoPack $tok
            foreach ($x in (Get-PoBaseSets $cur)) { Add-PoSel "${tok}:$x" }
        } elseif ($cur -and (Get-PoSet $cur $tok)) {
            Add-PoSel "$($cur['id']):$tok"
        } else {
            Stop-Po "unknown pack or set: $tok"
        }
    }
}

function Add-PoSel([string]$Item) { if ($script:SelSets -notcontains $Item) { $script:SelSets += $Item } }

function Get-PoPackTools {
    if ($script:ToolsGiven) { return ,@($script:SelTools) }
    $out = @()
    foreach ($o in (Get-PoOwners)) { if ($o -like 'core:*') { $out += $o.Substring(5) } }
    if ($script:DoCore) { foreach ($t in $script:SelTools) { if ($out -notcontains $t) { $out += $t } } }
    if ($out.Count -eq 0) { $out = @($script:SelTools) }
    return ,$out
}

function Install-PoSet([string]$PackId, [string]$SetId, $Tools) {
    $pack = Get-PoPack $PackId
    $set = Get-PoSet $pack $SetId
    Write-PoSay "=== pack $PackId, set $SetId ($($set['count']) skills)"
    if ($pack['kind'] -eq 'release') { Install-PoRelease $pack $set $Tools; return }
    $mcp = [bool]($pack['mcp'] -and $pack['mcp']['set'] -eq $SetId)
    if (Get-PoNpmPackage $pack $SetId) { Test-PoNodeReady $pack $true; Install-PoNpm $pack $SetId }
    elseif ($mcp) { Test-PoNodeReady $pack $false }
    $packsDir = Join-Path $PO_Root $PO_Data['packs_rel']
    foreach ($tool in $Tools) {
        $t = Get-PoTool $tool
        $withMcp = [bool]($mcp -and $t['mcp'])
        if (-not $withMcp -and (@($t['skills']).Count -eq 0 -or @($set['skills']).Count -eq 0)) { continue }
        Start-PoOwner "pack:${PackId}:${SetId}:$tool"
        foreach ($skill in $set['skills']) {
            foreach ($dir in $t['skills']) {
                Copy-PoTree (Join-Path (Join-Path (Join-Path $packsDir $PackId) 'skills') $skill) (Join-Path (Expand-PoPath $dir) $skill)
            }
        }
        if ($withMcp) { Register-PoMcp $pack $t }
        Complete-PoOwner
    }
    if ($pack['kind'] -eq 'package') {
        Start-PoOwner "pack:${PackId}:payload"
        Copy-PoTree (Join-Path (Join-Path $packsDir $PackId) $pack['payload']) (Join-Path (Join-Path $script:DataHome 'packages') $PackId)
        Complete-PoOwner
    }
}

function Remove-PoPackSpec([string]$Spec) {  # a set takes the sets that require it along
    $p, $s = $Spec.Split(':', 2)
    $pack = Get-PoPack $p
    if (-not $pack) { Stop-Po "unknown pack: $p" }
    $sets = @('*')
    if ($s) {
        if (-not (Get-PoSet $pack $s)) { Stop-Po "pack $p has no set $s" }
        $sets = @($pack['sets'] | Where-Object { @($_['requires']) -contains $s } | ForEach-Object { $_['id'] }) + @($s)
    }
    foreach ($one in $sets) {
        foreach ($owner in @(Get-PoOwners)) {
            if (-not $owner.StartsWith("pack:${p}:")) { continue }
            $rest = $owner.Substring("pack:${p}:".Length)
            if (@('payload', 'npm') -contains $rest) { continue }
            if ($one -ne '*' -and $rest.Split(':')[0] -ne $one) { continue }
            Remove-PoOwner $owner
        }
    }
    $left = @(Get-PoOwners | Where-Object { $_.StartsWith("pack:${p}:") -and $_ -ne "pack:${p}:payload" -and $_ -ne "pack:${p}:npm" })
    if ($left.Count -eq 0) { Remove-PoOwner "pack:${p}:payload"; Remove-PoOwner "pack:${p}:npm" }
}

# ------------------------------------------------------------------ npm and MCP packs

function Get-PoTmp {
    if (-not $script:Tmp) {
        $script:Tmp = Join-Path ([System.IO.Path]::GetTempPath()) "po-install-$PID"
        New-Item -ItemType Directory -Force -Path $script:Tmp | Out-Null
    }
    return $script:Tmp
}

function Get-PoPrefix($Pack) { return Join-Path (Join-Path $script:DataHome 'packages') $Pack['id'] }

function Get-PoNpmPackage($Pack, [string]$SetId) {
    if (-not $Pack['npm']) { return $null }
    foreach ($p in $Pack['npm']['packages']) { if ($p['set'] -eq $SetId) { return $p } }
    return $null
}

function Get-PoBaseSets($Pack) { return @($Pack['sets'] | Where-Object { -not $_['requires'] } | ForEach-Object { $_['id'] }) }

function Test-PoNodeReady($Pack, [bool]$Npm) {
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) { Stop-Po "pack $($Pack['id']) needs Node.js on PATH" }
    if (-not $Npm) { return }
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { Stop-Po "pack $($Pack['id']) needs npm on PATH" }
    $out = & node $script:Helper node-check $Pack['npm']['node']
    if ($LASTEXITCODE -ne 0) { Stop-Po "pack $($Pack['id']): $out" }
}

function Invoke-PoNpm([string[]]$NpmArgs) {  # npm with a throwaway cache and without notifier, audit and funding messages
    $vars = [ordered]@{ NO_UPDATE_NOTIFIER = '1'; npm_config_update_notifier = 'false'; npm_config_audit = 'false'
        npm_config_fund = 'false'; npm_config_cache = (Join-Path (Get-PoTmp) 'npm-cache') }
    $old = @{}
    foreach ($k in $vars.Keys) { $old[$k] = [Environment]::GetEnvironmentVariable($k); [Environment]::SetEnvironmentVariable($k, $vars[$k]) }
    try { & npm @NpmArgs | Out-Host; return $LASTEXITCODE }
    finally { foreach ($k in $vars.Keys) { [Environment]::SetEnvironmentVariable($k, $old[$k]) } }
}

function Test-PoNpmPinned([string]$Prefix, $Pkg) {
    $out = & node $script:Helper npm-check $Prefix $Pkg['name'] $Pkg['version'] $Pkg['integrity']
    return [pscustomobject]@{ Ok = ($LASTEXITCODE -eq 0); Text = (@($out) -join ' ') }
}

function Install-PoNpm($Pack, [string]$SetId) {  # the set's pinned npm package in <data_home>/packages/<pack>
    $pkg = Get-PoNpmPackage $Pack $SetId
    $prefix = Get-PoPrefix $Pack
    if ($SetId -ne @($Pack['npm']['packages'])[0]['set']) { Install-PoNpmAddon $Pack $pkg $prefix; return }
    $spec = "$($pkg['name'])@$($pkg['version'])"
    Start-PoOwner "pack:$($Pack['id']):npm"
    if ((Test-PoNpmPinned $prefix $pkg).Ok) {
        Add-PoRecord 'n' $prefix $spec
        Assert-PoNpmAbsent $Pack $prefix
        Complete-PoOwner
        return
    }
    Add-PoChange
    if ($script:Dry) { Write-PoSay "  would run npm install --prefix $prefix $spec --omit=optional --ignore-scripts and check its integrity"; Complete-PoOwner; return }
    $ours = $false
    foreach ($r in $script:Old) { if ($r.Kind -eq 'n' -and $r.Path -eq $prefix) { $ours = $true } }
    if ((Test-Path -LiteralPath $prefix) -and -not $ours) { Backup-PoItem $prefix }
    New-PoDir $prefix
    Write-PoSay "  `$ npm install --prefix $prefix $spec --omit=optional --ignore-scripts --save-exact"
    $code = Invoke-PoNpm @('install', '--prefix', $prefix, $spec, '--omit=optional', '--ignore-scripts', '--save-exact', '--no-audit', '--no-fund')
    if ($code -ne 0) { Remove-Item -LiteralPath $prefix -Recurse -Force -ErrorAction SilentlyContinue; Stop-Po "npm install of $spec failed" }
    $check = Test-PoNpmPinned $prefix $pkg
    if (-not $check.Ok) {
        Remove-Item -LiteralPath $prefix -Recurse -Force -ErrorAction SilentlyContinue
        Stop-Po "$spec in $prefix fails the pinned check ($($check.Text)); refusing to install"
    }
    Write-PoSay "  $spec matches the pinned integrity"
    Add-PoRecord 'n' $prefix $spec
    Assert-PoNpmAbsent $Pack $prefix
    Complete-PoOwner
}

function Assert-PoNpmAbsent($Pack, [string]$Prefix) {  # packages of sets that are not installed must be absent
    $id = $Pack['id']
    $base = @($Pack['npm']['packages'])[0]['set']
    foreach ($p in $Pack['npm']['packages']) {
        if ($p['set'] -eq $base -or $script:SelSets -contains "${id}:$($p['set'])") { continue }
        if (@(Get-PoOwners | Where-Object { $_.StartsWith("pack:${id}:$($p['set']):") }).Count -gt 0) { continue }
        if (Test-Path -LiteralPath (Join-Path (Join-Path $Prefix 'node_modules') $p['name'])) {
            Stop-Po "$Prefix holds $($p['name']), but set ${id}:$($p['set']) is not installed; remove $Prefix and install again"
        }
    }
}

function Install-PoNpmAddon($Pack, $Pkg, [string]$Prefix) {  # an npm package and its pinned native binding
    $id = $Pack['id']
    $name = $Pkg['name']
    $spec = "$name@$($Pkg['version'])"
    $b = $Pkg['binding']
    $basePkg = @($Pack['npm']['packages'])[0]
    if (-not $script:Dry -and -not (Test-PoNpmPinned $Prefix $basePkg).Ok) {
        Stop-Po "set ${id}:$($Pkg['set']) needs a verified install of set ${id}:$($basePkg['set']) in $Prefix; run: install.ps1 packs install ${id}:$($basePkg['set'])"
    }
    Start-PoOwner "pack:${id}:$($Pkg['set']):all"
    $binding = $null
    $have = ''
    if ($b) {
        $binding = Join-Path (Join-Path (Join-Path $Prefix 'node_modules') $name) $b['member'].Replace('/', $script:Sep)
        foreach ($r in $script:Old) { if ($r.Kind -eq 'x' -and $r.Path -eq $binding) { $have = $r.Hash } }
    }
    if ((Test-PoNpmPinned $Prefix $Pkg).Ok -and (-not $b -or ((Test-Path -LiteralPath $binding -PathType Leaf) -and (Get-PoFileHash $binding) -eq $have))) {
        if ($b) { Add-PoRecord 'x' $binding $have }
        Add-PoRecord 'u' $Prefix '-' "npm-rm:$name"
        Complete-PoOwner
        return
    }
    Add-PoChange
    if ($b) {
        $plat = ((& node $script:Helper platform) | Out-String).Trim()
        $want = $b['sha256'][$plat]
        if (-not $want) { Stop-Po "no pinned digest for the $name binding on $plat; refusing to install ${id}:$($Pkg['set'])" }
        $url = $b['url'].Replace('{version}', $Pkg['version']).Replace('{platform}', $plat)
        $file = $url.Substring($url.LastIndexOf('/') + 1)
    }
    if ($script:Dry) {
        if ($b) { Write-PoSay "  would download $url and check its sha256 against $want" }
        Write-PoSay "  would run npm install --prefix $Prefix $spec --ignore-scripts and check its integrity"
        Complete-PoOwner
        return
    }
    if ($b) {
        $src = $script:Bundles[$id]
        if ($src) {
            $asset = Join-Path $src $file
            if (-not (Test-Path -LiteralPath $asset -PathType Leaf)) { Stop-Po "bundle folder has no ${file}: $src" }
        } else {
            $asset = Join-Path (Get-PoTmp) $file
            Write-PoSay "  get $url"
            Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $asset
        }
        $got = Get-PoFileHash $asset
        if ($got -ne $want) { Stop-Po "$file has sha256 $got, but $id pins $want; refusing to install ${id}:$($Pkg['set'])" }
        Write-PoSay "  $file matches the pinned sha256"
        $out = Join-Path (Get-PoTmp) 'binding'
        if (Test-Path -LiteralPath $out) { Remove-Item -LiteralPath $out -Recurse -Force }
        New-Item -ItemType Directory -Path $out | Out-Null
        & tar -xzf $asset -C $out $b['member'] | Out-Host
        $extracted = Join-Path $out $b['member'].Replace('/', $script:Sep)
        if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $extracted -PathType Leaf)) { Stop-Po "cannot extract $($b['member']) from $file" }
    }
    Write-PoSay "  `$ npm install --prefix $Prefix $spec --ignore-scripts --save-exact"
    $code = Invoke-PoNpm @('install', '--prefix', $Prefix, $spec, '--omit=optional', '--ignore-scripts', '--save-exact', '--no-audit', '--no-fund')
    if ($code -ne 0) { Stop-Po "npm install of $spec failed" }
    $check = Test-PoNpmPinned $Prefix $Pkg
    if (-not $check.Ok) {
        $null = Invoke-PoNpm @('uninstall', '--prefix', $Prefix, $name, '--ignore-scripts', '--no-audit', '--no-fund')
        Stop-Po "$spec in $Prefix fails the pinned check ($($check.Text)); refusing to install"
    }
    Write-PoSay "  $spec matches the pinned integrity"
    if ($b) {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $binding) | Out-Null
        Copy-Item -LiteralPath $extracted -Destination $binding -Force
        Add-PoRecord 'x' $binding (Get-PoFileHash $binding)
        Write-PoSay "  binding -> $binding"
    }
    Add-PoRecord 'u' $Prefix '-' "npm-rm:$name"
    Complete-PoOwner
}

function Remove-PoNpmPackage([string]$Prefix, [string]$Name) {  # undo an add-on npm install
    if (-not (Test-Path -LiteralPath (Join-Path (Join-Path $Prefix 'node_modules') $Name))) { return }
    $code = 1
    if (Get-Command npm -ErrorAction SilentlyContinue) { $code = Invoke-PoNpm @('uninstall', '--prefix', $Prefix, $Name, '--ignore-scripts', '--no-audit', '--no-fund') }
    if ($code -eq 0) { Add-PoChange } else { Write-PoWarn "could not run npm uninstall $Name in $Prefix; remove it by hand" }
}

function Register-PoMcp($Pack, $Tool) {  # add the pack's MCP server to the tool's config
    $file = Expand-PoPath $Tool['mcp']['file']
    $name = $Pack['mcp']['name']
    $old = '-'
    foreach ($r in $script:Old) { if ($r.Kind -eq 'm') { $old = $r.Extra } }
    if ($script:Dry) { Write-PoSay "  would register the MCP server $name in $file"; Add-PoChange; return }
    New-PoDir (Split-Path -Parent $file)
    $out = & node $script:Helper mcp-add $Tool['mcp']['format'] $file $name $Pack['mcp']['spec_b64'] (Get-PoPrefix $Pack) $old
    if ($LASTEXITCODE -ne 0) { Stop-Po "MCP registration failed for $file" }
    $parts = ([string](@($out) | Select-Object -Last 1)).Split("`t")
    switch ($parts[0]) {
        'added' { Add-PoChange; Write-PoSay "  MCP server $name -> $($parts[1])"; Add-PoRecord 'm' $parts[1] $name $parts[2] }
        'present' { Add-PoRecord 'm' $parts[1] $name $parts[2] }
        'foreign' { Write-PoSay "  $($parts[1]) already has the same $name entry; the installer leaves it unmanaged" }
        default { Write-PoWarn "MCP server $name not registered in $($parts[1])" }
    }
}

function Unregister-PoMcp([string]$Path, [string]$Name, [string]$Record) {
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) { Write-PoWarn "Node.js not found: remove the $Name entry from $Path by hand"; return }
    $verdict = ((& node $script:Helper mcp-remove $Record) | Out-String).Trim()
    switch ($verdict) {
        'removed' { Add-PoChange }
        'absent' { }
        'changed' { Write-PoWarn "kept the $Name entry in ${Path}: changed since install" }
        default { Write-PoWarn "could not remove the $Name entry from $Path" }
    }
}

function Switch-PoSel([string]$Key) {  # toggle "pack:set" and keep required sets with it
    $p, $s = $Key.Split(':', 2)
    $pack = Get-PoPack $p
    if ($script:SelSets -contains $Key) {
        $drop = @($Key) + @($pack['sets'] | Where-Object { @($_['requires']) -contains $s } | ForEach-Object { "${p}:$($_['id'])" })
        $script:SelSets = @($script:SelSets | Where-Object { $drop -notcontains $_ })
    } else {
        foreach ($r in @((Get-PoSet $pack $s)['requires'])) { if ($r) { Add-PoSel "${p}:$r" } }
        Add-PoSel $Key
    }
}

function Get-PoNeedsNote($Set) { if ($Set['requires']) { return " Needs set $(@($Set['requires']) -join ', ')." }; return '' }

function Test-PoRequires {  # refuse a set whose required set is neither selected nor installed
    foreach ($w in $script:SelSets) {
        $p, $s = $w.Split(':', 2)
        foreach ($r in @((Get-PoSet (Get-PoPack $p) $s)['requires'])) {
            if (-not $r -or $script:SelSets -contains "${p}:$r") { continue }
            if (@(Get-PoOwners | Where-Object { $_.StartsWith("pack:${p}:${r}:") }).Count -gt 0) { continue }
            Stop-Po "set $w needs set ${p}:$r; install both, for example --packs ${p}:$r,$s"
        }
    }
}

# ------------------------------------------------------------------ release packs (procable)

function Get-PoPlatform {
    $arch = 'x64'
    if ([System.Environment]::OSVersion.Platform -eq [System.PlatformID]::Win32NT) { return @('windows', 'x64') }
    $machine = (& uname -m)
    if ($machine -in @('arm64', 'aarch64')) { $arch = 'arm64' }
    if ((& uname -s) -eq 'Darwin') { return @('darwin', $arch) }
    return @('linux', $arch)
}

function Install-PoRelease($Pack, $Set, $Tools) {
    $rel = $Pack['release']
    $packsDir = Join-Path $PO_Root $PO_Data['packs_rel']
    $lockPath = Join-Path (Join-Path $packsDir $Pack['id']) $rel['lock']
    $lock = (Read-PoText $lockPath) | ConvertFrom-Json
    if (-not $lock.version -or -not $lock.repo -or -not $lock.sha256sums) { Stop-Po "$lockPath does not pin version, repo and sha256sums" }
    $os, $arch = Get-PoPlatform
    $engine = $rel['engine'].Replace('{os}', $os).Replace('{arch}', $arch)
    if ($os -eq 'windows') { $engine += '.exe' }
    $skill = @($Set['skills'])[0]
    $providers = @()
    foreach ($t in $Tools) { $p = $rel['providers'][$t]; if ($p -and $providers -notcontains $p) { $providers += $p } }
    if ($providers.Count -eq 0) { Write-PoSay "  no selected tool is supported by $($Pack['id'])"; return }
    $providers = @($providers | Sort-Object)
    $tag = $rel['tag'].Replace('{version}', $lock.version)
    $base = "https://github.com/$($lock.repo)/releases/download/$tag"
    $bundleDir = $script:Bundles[$Pack['id']]
    if ($bundleDir) {
        if (-not (Test-Path -LiteralPath $bundleDir -PathType Container)) { Stop-Po "bundle folder does not exist: $bundleDir" }
        $src = (Resolve-Path -LiteralPath $bundleDir).ProviderPath
    } else {
        $src = Join-Path (Join-Path (Join-Path $script:DataHome 'packages') $Pack['id']) $lock.version
    }
    Write-PoSay "  $($Pack['id']) $($lock.version) for $($providers -join ',') ($os-$arch) from $src"
    if ($script:Dry) {
        Write-PoSay "  would verify SHA256SUMS against $($lock.sha256sums) and run $engine install --global --yes --providers=$($providers -join ',')"
        Add-PoChange
        return
    }
    Start-PoOwner "pack:$($Pack['id']):$($Set['id']):all"
    if (-not $bundleDir) {
        New-PoDir $src
        foreach ($name in @('SHA256SUMS', $rel['bundle'], $engine)) {
            $file = Join-Path $src $name
            if (-not (Test-Path -LiteralPath $file)) {
                Write-PoSay "  get $base/$name"
                Invoke-WebRequest -UseBasicParsing -Uri "$base/$name" -OutFile "$file.part"
                Move-Item -LiteralPath "$file.part" -Destination $file -Force
            }
            Add-PoRecord 'x' $file (Get-PoFileHash $file)
        }
    }
    if ((Get-PoFileHash (Join-Path $src 'SHA256SUMS')) -ne $lock.sha256sums) {
        Stop-Po "$src\SHA256SUMS does not match the digest pinned in $lockPath; refusing to install"
    }
    $sums = @{}
    foreach ($line in [System.IO.File]::ReadAllLines((Join-Path $src 'SHA256SUMS'))) {
        $parts = $line -split '\s+'
        if ($parts.Count -ge 2) { $sums[$parts[1].TrimStart('*')] = $parts[0].ToLowerInvariant() }
    }
    foreach ($name in @($rel['bundle'], $engine)) {
        if (-not $sums.ContainsKey($name)) { Stop-Po "SHA256SUMS lists no $name" }
        if ((Get-PoFileHash (Join-Path $src $name)) -ne $sums[$name]) { Stop-Po "$src\$name fails its checksum; refusing to install" }
    }
    $track = @()
    foreach ($r in $rel['skill_roots']) { $track += (Join-Path (Expand-PoPath $r) $skill) }
    foreach ($f in $rel['hook_files']) { $track += (Expand-PoPath $f) }
    Start-PoTrack $track
    $engineFile = Join-Path $src $engine
    $argv = @('install', '--global', '--yes', "--providers=$($providers -join ',')")
    if ($script:ReleaseNoHooks) { $argv += '--no-hooks' }
    Write-PoSay "  `$ $engineFile $($argv -join ' ')"
    $old = [Environment]::GetEnvironmentVariable($rel['bundle_env'])
    [Environment]::SetEnvironmentVariable($rel['bundle_env'], (Join-Path $src $rel['bundle']))
    try { & $engineFile @argv | Out-Host; $code = $LASTEXITCODE } finally { [Environment]::SetEnvironmentVariable($rel['bundle_env'], $old) }
    if ($code -ne 0) { Stop-Po "the $($Pack['id']) installer exited with $code" }
    $bin = $skill
    if ($os -eq 'windows') { $bin += '.exe' }
    foreach ($r in $rel['skill_roots']) {
        $dir = Join-Path (Expand-PoPath $r) $skill
        if (-not (Test-Path -LiteralPath (Join-Path $dir 'SKILL.md'))) { continue }
        $binDir = Join-Path (Join-Path (Join-Path $dir 'scripts') 'bin') "$os-$arch"
        $dest = Join-Path $binDir $bin
        if (-not (Test-Path -LiteralPath $dest) -or (Get-PoFileHash $dest) -ne (Get-PoFileHash $engineFile)) {
            New-PoDir $binDir
            Copy-Item -LiteralPath $engineFile -Destination $dest -Force
        }
        Write-PoSay "  engine -> $dest"
    }
    $codexDir = Join-Path (Join-Path (Join-Path $script:Loc['HOME'] '.agents') 'skills') $skill
    if ($providers -contains 'codex' -and -not $script:ReleaseNoHooks -and (Test-Path -LiteralPath (Join-Path $codexDir 'SKILL.md'))) {
        $launcher = Join-Path (Join-Path $codexDir 'scripts') $skill
        if ($os -eq 'windows') { $launcher += '.cmd' }
        $hooksFile = Join-Path $script:Loc['CODEX_HOME'] 'hooks.json'
        if (Add-PoJsonHooks $hooksFile "`"$launcher`" hook" $rel['codex_hooks']) { Write-PoSay "  codex hooks added to $hooksFile" }
    }
    Complete-PoTrack
    foreach ($f in $rel['hook_files']) { Add-PoRecord 'u' (Expand-PoPath $f) '-' "json-strip:$skill/scripts/$skill" }
    Complete-PoOwner
    Write-PoSay "==> $($Pack['id']) $($lock.version) installed; it runs offline."
}

# ------------------------------------------------------------------ reports

function Get-PoCoreWhere($Tools) {
    $lines = @()
    foreach ($tool in $Tools) {
        foreach ($s in (Get-PoTool $tool)['steps']) {
            switch ($s['op']) {
                { $_ -in @('tree', 'file', 'doc', 'plugin') } { $lines += "    ${tool}: $(Expand-PoPath $s['dest'])" }
                'block' { $lines += "    ${tool}: $(Expand-PoPath $s['dest']) (marker block)" }
                'attribution' { $lines += "    ${tool}: AI attribution off (settings.json, global git hooks)" }
            }
        }
    }
    return $lines
}

function Get-PoSkillDirs($Tools) {
    $out = @()
    foreach ($tool in $Tools) { foreach ($d in (Get-PoTool $tool)['skills']) { $e = Expand-PoPath $d; if ($out -notcontains $e) { $out += $e } } }
    return $out
}

function Show-PoPacks {
    $owners = Get-PoOwners
    foreach ($p in $PO_Data['packs']) {
        Write-PoSay "$($p['id']): $($p['label']) [$($p['kind']), $($p['license'])]"
        Write-PoSay "  $($p['description'])"
        foreach ($s in $p['sets']) {
            $mark = ' '
            foreach ($o in $owners) { if ($o.StartsWith("pack:$($p['id']):$($s['id']):")) { $mark = 'x' } }
            Write-PoSay "  [$mark] $($p['id']):$($s['id']) ($($s['count']) skills) $($s['description'])$(Get-PoNeedsNote $s)"
        }
    }
}

function Show-PoStatus {
    Write-PoSay "source: $PO_Root"
    Write-PoSay "data home: $($script:DataHome)"
    if (-not (Test-Path -LiteralPath $script:Manifest)) { Write-PoSay "nothing installed (no manifest at $($script:Manifest))"; return }
    Write-PoSay "manifest: $($script:Manifest)"
    $all = Read-PoManifest
    foreach ($o in (Get-PoOwners)) {
        $n = @($all | Where-Object { $_.Owner -ceq $o -and @('f', 'd', 'x', 'b', 'm', 'n') -contains $_.Kind }).Count
        Write-PoSay ("  {0,-48} {1} files" -f $o, $n)
    }
    Write-PoSay "created folders: $(@($all | Where-Object { $_.Owner -eq '@dirs' }).Count)"
}

# ------------------------------------------------------------------ text menu

function Read-PoAnswer {
    $line = [Console]::In.ReadLine()
    if ($null -eq $line) { Write-PoSay ''; Write-PoSay 'cancelled (end of input)'; throw 'cancelled' }
    return $line.Trim().ToLowerInvariant()
}

function Get-PoSelCount {
    $total = 0
    foreach ($w in $script:SelSets) { $p, $s = $w.Split(':', 2); $total += (Get-PoSet (Get-PoPack $p) $s)['count'] }
    return $total
}

function Step-PoCycle([string]$Current, $Values) {
    $list = @('') + @($Values)
    $i = [array]::IndexOf($list, $Current)
    return $list[($i + 1) % $list.Count]
}

function Invoke-PoTui {
    $screen = 1
    $h = $PO_Data['harness']
    while ($true) {
        Write-PoSay ''
        switch ($screen) {
            1 {
                Write-PoSay 'prompt-orchestrator installer. Step 1 of 5: tools'
                $i = 0
                foreach ($t in $PO_Data['tools']) {
                    $i++
                    $mark = ' '; if ($script:SelTools -contains $t['id']) { $mark = 'x' }
                    Write-PoSay ("  {0,2}. [{1}] {2}" -f $i, $mark, $t['label'])
                }
                Write-PoSay 'Next step installs the core for the checked tools into:'
                Get-PoCoreWhere $script:SelTools | ForEach-Object { Write-PoSay $_ }
                Write-PoSay 'Keys: number toggles a tool, a all, n none, Enter next, q quit'
                $a = Read-PoAnswer
                if ($a -eq '') { $screen = 2 }
                elseif ($a -eq 'q') { throw 'cancelled' }
                elseif ($a -eq 'a') { $script:SelTools = @($PO_Data['tools'] | ForEach-Object { $_['id'] }) }
                elseif ($a -eq 'n') { $script:SelTools = @() }
                elseif ($a -match '^\d+$' -and [int]$a -ge 1 -and [int]$a -le @($PO_Data['tools']).Count) {
                    $id = @($PO_Data['tools'])[[int]$a - 1]['id']
                    if ($script:SelTools -contains $id) { $script:SelTools = @($script:SelTools | Where-Object { $_ -ne $id }) } else { $script:SelTools += $id }
                } else { Write-PoSay 'unknown choice' }
            }
            2 {
                Write-PoSay 'Step 2 of 5: core skills and workflows'
                Write-PoSay "  [c] core: $(if ($script:DoCore) { 'yes' } else { 'no' })"
                Write-PoSay 'Next step installs the core skills and workflows into:'
                Get-PoCoreWhere $script:SelTools | ForEach-Object { Write-PoSay $_ }
                Write-PoSay 'Keys: c toggles the core, Enter next, b back, q quit'
                $a = Read-PoAnswer
                switch ($a) { '' { $screen = 3 } 'b' { $screen = 1 } 'q' { throw 'cancelled' } 'c' { $script:DoCore = -not $script:DoCore } default { Write-PoSay 'unknown choice' } }
            }
            3 {
                Write-PoSay 'Step 3 of 5: harness (tiered agents, plan profiles, hooks)'
                $note = ''
                if (-not (Find-PoPython $h['python'][0] $h['python'][1])) { $note = " (needs Python $($h['python'][0]).$($h['python'][1]); skipped on this machine)" }
                Write-PoSay "  [h] harness: $(if ($script:DoHarness) { 'yes' } else { 'no' })$note"
                Write-PoSay "  [pc] Claude plan profile: $(if ($script:ProfileClaude) { $script:ProfileClaude } else { 'not set' })"
                Write-PoSay "  [px] Codex plan profile: $(if ($script:ProfileCodex) { $script:ProfileCodex } else { 'not set' })"
                $i = 0
                foreach ($o in $h['options']) {
                    $i++
                    $mark = 'x'; if ($script:HarnessOff -contains $o['id']) { $mark = ' ' }
                    Write-PoSay "  g$i. [$mark] $($o['label'])"
                }
                Write-PoSay "Next step runs $($h['script']) for each checked tool. It writes agents, overlays and hooks into each tool's folder and keeps its own manifest."
                Write-PoSay 'Keys: h toggles, pc or px cycles a profile, g<number> toggles an option, Enter next, b back, q quit'
                $a = Read-PoAnswer
                if ($a -eq '') { $screen = 4 }
                elseif ($a -eq 'b') { $screen = 2 }
                elseif ($a -eq 'q') { throw 'cancelled' }
                elseif ($a -eq 'h') { $script:DoHarness = -not $script:DoHarness }
                elseif ($a -eq 'pc') { $script:ProfileClaude = Step-PoCycle $script:ProfileClaude $h['profiles']['claude'] }
                elseif ($a -eq 'px') { $script:ProfileCodex = Step-PoCycle $script:ProfileCodex $h['profiles']['codex'] }
                elseif ($a -match '^g(\d+)$' -and [int]$Matches[1] -ge 1 -and [int]$Matches[1] -le @($h['options']).Count) {
                    $id = @($h['options'])[[int]$Matches[1] - 1]['id']
                    if ($script:HarnessOff -contains $id) { $script:HarnessOff = @($script:HarnessOff | Where-Object { $_ -ne $id }) } else { $script:HarnessOff += $id }
                } else { Write-PoSay 'unknown choice' }
            }
            4 {
                Write-PoSay 'Step 4 of 5: packs (opt-in skill sets)'
                $n = 0; $i = 0; $index = @()
                foreach ($p in $PO_Data['packs']) {
                    $i++
                    Write-PoSay "  p$i. $($p['label']) ($($p['id'])): $($p['description'])"
                    foreach ($s in $p['sets']) {
                        $n++
                        $key = "$($p['id']):$($s['id'])"
                        $index += $key
                        $mark = ' '; if ($script:SelSets -contains $key) { $mark = 'x' }
                        Write-PoSay ("    {0,3}. [{1}] {2}, {3} skills: {4}{5}" -f $n, $mark, $s['label'], $s['count'], $s['description'], (Get-PoNeedsNote $s))
                    }
                }
                Write-PoSay "Next step installs $(Get-PoSelCount) skills from the checked sets into:"
                Get-PoSkillDirs (Get-PoPackTools) | ForEach-Object { Write-PoSay "    $_" }
                Write-PoSay 'A set that needs another set selects both. Keys: number toggles a set, p<number> toggles a whole pack, Enter next, b back, q quit'
                $a = Read-PoAnswer
                if ($a -eq '') { $screen = 5 }
                elseif ($a -eq 'b') { $screen = 3 }
                elseif ($a -eq 'q') { throw 'cancelled' }
                elseif ($a -match '^p(\d+)$' -and [int]$Matches[1] -ge 1 -and [int]$Matches[1] -le @($PO_Data['packs']).Count) {
                    $p = @($PO_Data['packs'])[[int]$Matches[1] - 1]
                    $keys = @($p['sets'] | ForEach-Object { "$($p['id']):$($_['id'])" })
                    if ($script:SelSets -contains $keys[0]) { $script:SelSets = @($script:SelSets | Where-Object { $keys -notcontains $_ }) }
                    else { foreach ($k in (Get-PoBaseSets $p)) { Add-PoSel "$($p['id']):$k" } }
                } elseif ($a -match '^\d+$' -and [int]$a -ge 1 -and [int]$a -le $index.Count) {
                    Switch-PoSel $index[[int]$a - 1]
                } else { Write-PoSay 'unknown choice' }
            }
            5 {
                Write-PoSay 'Step 5 of 5: review'
                Write-PoSay "  tools: $(if ($script:SelTools) { $script:SelTools -join ' ' } else { 'none' })"
                Write-PoSay "  core: $(if ($script:DoCore) { 'yes' } else { 'no' })"
                Write-PoSay "  harness: $(if ($script:DoHarness) { 'yes' } else { 'no' })"
                Write-PoSay "  packs: $(if ($script:SelSets) { $script:SelSets -join ' ' } else { 'none' })"
                Write-PoSay "Next step installs the items above. The manifest goes to $($script:Manifest)."
                Write-PoSay 'Keys: Enter installs, b back, q quit'
                $a = Read-PoAnswer
                switch ($a) { '' { return } 'b' { $screen = 4 } 'q' { throw 'cancelled' } default { Write-PoSay 'unknown choice' } }
            }
        }
    }
}

# ------------------------------------------------------------------ commands

function Show-PoUsage {
    $tools = (@($PO_Data['tools'] | ForEach-Object { $_['id'] })) -join ','
    $opts = (@($PO_Data['harness']['options'] | ForEach-Object { $_['id'] })) -join ','
    Write-PoSay @"
prompt-orchestrator installer (generated from install/spec.json)

Usage:
  install.ps1                                  menu in a console, defaults otherwise
  install.ps1 [install] [options]              install the core, the harness and packs
  install.ps1 tui                              menu, also with scripted input
  install.ps1 status                           what the manifest records
  install.ps1 packs list                       packs and sets with skill counts
  install.ps1 packs install SPEC...            install packs or sets (no core, no harness)
  install.ps1 packs remove SPEC...             remove packs or sets
  install.ps1 uninstall [--tools LIST] [--project DIR]
  install.ps1 project [DIR]                    every tool inside one project folder
  install.ps1 windsurf [DIR]                   Windsurf workflows and rules inside one project

Options:
  --tools LIST            comma-separated tool ids: $tools
  --core | --no-core      install the core skills and workflows (default: yes)
  --core-only             core without the harness
  --harness | --no-harness  run the harness installer (default: yes, needs Python 3.11)
  --harness-only          harness without the core
  --profile NAME          plan profile for Claude and Codex tools where it applies
  --profile-claude NAME   $($PO_Data['harness']['profiles']['claude'] -join ',')
  --profile-codex NAME    $($PO_Data['harness']['profiles']['codex'] -join ',')
  --no-OPTION             turn off a harness option: $opts
  --packs SPEC            pack[:set][,set...] and more packs. A bare pack name skips sets
                          that need another set (rea-frida); name those: --packs rea:rea,rea-frida
  --sets SPEC             same as --packs
  --bundle PACK=DIR       read a release pack or a pinned binding from a local folder
  --procable-bundle DIR   same as --bundle procable=DIR
  --no-release-hooks      install release packs without their hooks
  --dry-run               print the plan and change nothing
  --yes, -y               no menu
"@
}

function Install-PoAll {
    Test-PoRequires
    if ($script:Dry) { Write-PoSay 'dry run: nothing is written' }
    if ($script:DoCore) { foreach ($t in $script:SelTools) { Install-PoCore $t } }
    if ($script:DoHarness) { foreach ($t in $script:SelTools) { Install-PoHarness $t } }
    if ($script:SelSets.Count -gt 0) {
        $tools = Get-PoPackTools
        $ordered = @($script:SelSets | Where-Object { $p, $s = $_.Split(':', 2); -not (Get-PoSet (Get-PoPack $p) $s)['requires'] }) +
            @($script:SelSets | Where-Object { $p, $s = $_.Split(':', 2); [bool](Get-PoSet (Get-PoPack $p) $s)['requires'] })
        foreach ($w in $ordered) { $p, $s = $w.Split(':', 2); Install-PoSet $p $s $tools }
    }
    Write-PoReport
}

function Write-PoReport {
    if ($script:Failed.Count -gt 0) { Write-PoSay "==> finished with failures: $($script:Failed -join ' ')"; $script:Exit = 1; return }
    if ($script:Changes -eq 0) { Write-PoSay '==> no change: everything is already in place' }
    elseif ($script:Dry) { Write-PoSay "==> dry run: $($script:Changes) changes planned" }
    else { Write-PoSay "==> done: $($script:Changes) changes" }
}

function Invoke-PoUninstall {
    $owners = @(Get-PoOwners)
    if ($script:ProjectDir) {
        $dir = $script:ProjectDir
        if (Test-Path -LiteralPath $dir) { $dir = (Resolve-Path -LiteralPath $dir).ProviderPath }
        foreach ($o in $owners) { if ($o -ceq "project:$dir" -or $o -ceq "windsurf:$dir") { Remove-PoOwner $o } }
    } elseif ($script:ToolsGiven) {
        foreach ($t in $script:SelTools) {
            foreach ($o in $owners) { if ($o -ceq "harness:$t" -or $o -ceq "core:$t" -or ($o -like 'pack:*' -and $o.EndsWith(":$t"))) { Remove-PoOwner $o } }
        }
    } else {
        foreach ($prefix in @('harness:', 'pack:', 'core:', '')) {
            foreach ($o in @(Get-PoOwners)) { if ($o.StartsWith($prefix)) { Remove-PoOwner $o } }
        }
    }
    Write-PoReport
}

function Invoke-PoMain($Argv) {
    $script:Dry = $false; $script:Yes = $false; $script:DoCore = $true
    $script:DoHarness = [bool]$PO_Data['harness']['default']
    $script:ToolsGiven = $false
    $script:SelTools = @($PO_Data['tools'] | Where-Object { $_['default'] } | ForEach-Object { $_['id'] })
    $script:SelSets = @(); $script:ProfileClaude = ''; $script:ProfileCodex = ''; $script:HarnessOff = @()
    $script:Bundles = @{}; $script:ReleaseNoHooks = $false; $script:ProjectDir = ''; $script:Failed = @()
    $script:Changes = 0; $script:Exit = 0; $script:Owner = ''; $script:Tmp = ''
    $script:DirsNew = New-Object System.Collections.Generic.List[object]
    $script:Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $cmd = ''; $sub = ''; $rest = @(); $packsSpec = @()
    $toolIds = @($PO_Data['tools'] | ForEach-Object { $_['id'] })
    $optIds = @($PO_Data['harness']['options'] | ForEach-Object { $_['id'] })
    try {
        $i = 0
        $a = @($Argv)
        while ($i -lt $a.Count) {
            $arg = [string]$a[$i]
            $next = $null
            if ($i + 1 -lt $a.Count) { $next = [string]$a[$i + 1] }
            switch -regex ($arg) {
                '^--tools$' {
                    if (-not $next) { Stop-Po '--tools needs a value' }
                    $script:ToolsGiven = $true; $script:SelTools = @($next.Split(',') | Where-Object { $_ })
                    foreach ($t in $script:SelTools) { if ($toolIds -notcontains $t) { Stop-Po "unknown tool: $t" } }
                    $i++; break
                }
                '^--core$' { $script:DoCore = $true; break }
                '^--no-core$' { $script:DoCore = $false; break }
                '^--core-only$' { $script:DoCore = $true; $script:DoHarness = $false; break }
                '^--(harness|with-harness)$' { $script:DoHarness = $true; break }
                '^--no-harness$' { $script:DoHarness = $false; break }
                '^--harness-only$' { $script:DoCore = $false; $script:DoHarness = $true; break }
                '^--profile$' {
                    if ($PO_Data['harness']['profiles']['claude'] -contains $next) { $script:ProfileClaude = $next }
                    if ($PO_Data['harness']['profiles']['codex'] -contains $next) { $script:ProfileCodex = $next }
                    if (-not ($script:ProfileClaude + $script:ProfileCodex)) { Stop-Po "unknown profile: $next" }
                    $i++; break
                }
                '^--profile-claude$' { if ($PO_Data['harness']['profiles']['claude'] -notcontains $next) { Stop-Po "unknown Claude profile: $next" }; $script:ProfileClaude = $next; $i++; break }
                '^--profile-codex$' { if ($PO_Data['harness']['profiles']['codex'] -notcontains $next) { Stop-Po "unknown Codex profile: $next" }; $script:ProfileCodex = $next; $i++; break }
                '^--(packs|sets)$' { if (-not $next) { Stop-Po "$arg needs a value" }; $packsSpec += $next; $i++; break }
                '^--bundle$' { if ($next -notmatch '=') { Stop-Po '--bundle needs PACK=DIR' }; $k, $v = $next.Split('=', 2); $script:Bundles[$k] = $v; $i++; break }
                '^--procable-bundle$' { $script:Bundles['procable'] = $next; $i++; break }
                '^--no-(release|procable)-hooks$' { $script:ReleaseNoHooks = $true; break }
                '^--project$' { $script:ProjectDir = $next; $i++; break }
                '^--dry-run$' { $script:Dry = $true; break }
                '^(--yes|-y)$' { $script:Yes = $true; break }
                '^(-h|--help|help)$' { Show-PoUsage; return 0 }
                '^--no-' {
                    $opt = $arg.Substring(5)
                    if ($optIds -notcontains $opt) { Stop-Po "unknown option: $arg" }
                    $script:HarnessOff += $opt; break
                }
                '^-' { Stop-Po "unknown option: $arg (see --help)" }
                default {
                    if (-not $cmd) { $cmd = $arg } elseif ($cmd -eq 'packs' -and -not $sub) { $sub = $arg } else { $rest += $arg }
                }
            }
            $i++
        }
        Initialize-PoLocations
        $script:DataHome = $script:Loc['DATA_HOME']
        $script:Manifest = Join-Path $script:DataHome $PO_Data['manifest']
        $script:Helper = Join-Path $PO_Root $PO_Data['pack_helper']
        if (-not $cmd) { $cmd = 'install' }
        switch ($cmd) {
            { $_ -in @('install', 'tui') } {
                foreach ($s in $packsSpec) { Add-PoSets $s }
                if ($cmd -eq 'tui' -or (-not $script:Yes -and -not $script:Dry -and -not [Console]::IsInputRedirected)) { Invoke-PoTui }
                Install-PoAll
            }
            'status' { Show-PoStatus }
            'packs' {
                switch ($sub) {
                    { $_ -in @('', 'list') } { Show-PoPacks }
                    { $_ -in @('install', 'add') } {
                        foreach ($s in $rest) { Add-PoSets $s }
                        if ($script:SelSets.Count -eq 0) { Stop-Po 'name a pack or set, see: install.ps1 packs list' }
                        $script:DoCore = $false; $script:DoHarness = $false
                        Install-PoAll
                    }
                    { $_ -in @('remove', 'rm', 'uninstall') } {
                        if ($rest.Count -eq 0) { Stop-Po 'name a pack or set to remove' }
                        foreach ($s in $rest) { Remove-PoPackSpec $s }
                        Write-PoReport
                    }
                    default { Stop-Po "unknown packs command: $sub" }
                }
            }
            { $_ -in @('uninstall', 'remove') } { Invoke-PoUninstall }
            { $_ -in @('project', 'windsurf') } {
                $dir = (Get-Location).ProviderPath
                if ($rest.Count -gt 0) { $dir = $rest[0] }
                Install-PoProject $cmd $dir
                Write-PoReport
            }
            default { Stop-Po "unknown command: $cmd (see --help)" }
        }
    } catch {
        if ("$_" -eq 'cancelled') { Write-PoSay 'cancelled'; return 1 }
        Write-Host "$_" -ForegroundColor Red
        return 1
    } finally {
        if ($script:Tmp -and (Test-Path -LiteralPath $script:Tmp)) { Remove-Item -LiteralPath $script:Tmp -Recurse -Force -ErrorAction SilentlyContinue }
    }
    return $script:Exit
}
