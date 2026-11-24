param(
    [Parameter(Mandatory = $true)]
    [string]$TargetPath,

    [int]$StringsLimit = 40,

    [int]$ImportsLimit = 80,

    [switch]$RunAnalysis
)

# Force UTF-8 output for this script to reduce garbled section titles.
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot '..\..\scripts\lib\ToolDiscovery.ps1')

$bootstrapScript = Join-Path $PSScriptRoot '..\..\scripts\bootstrap-reverse.ps1'

function Get-RequiredToolSpec {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    $spec = Resolve-ReverseToolSpec -Name $Name
    if (-not $spec.Available) {
        # Attempt auto-bootstrap
        if (Test-Path -LiteralPath $bootstrapScript) {
            Write-Output "INFO: $Name not found, attempting auto-bootstrap..."
            & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $bootstrapScript -Capability @($Name) -SkipRefresh
            $spec = Resolve-ReverseToolSpec -Name $Name
        }
        if (-not $spec.Available) {
            throw "Missing command: $Name; automatic install failed, install it manually. Reference: https://github.com/radareorg/radare2"
        }
    }
    return $spec
}

function Write-Section {
    param(
        [Parameter(Mandatory = $true)]
    [string]$Title
    )

    # Fixed section titles are easy to read and easy to grep later.
    ""
    "=== $Title ==="
}

$rabin2 = Get-RequiredToolSpec -Name 'rabin2'
$r2 = $null
if ($RunAnalysis) {
    $r2 = Get-RequiredToolSpec -Name 'r2'
}

# Normalize the input path to an absolute path so r2/rabin2 do not resolve relative paths ambiguously.
$resolvedPath = Resolve-Path -LiteralPath $TargetPath
$target = $resolvedPath.Path

"Target file: $target"

Write-Section -Title 'Basic information'
& $rabin2.Command @($rabin2.PrefixArgs + @('-I', '--', $target))

Write-Section -Title 'Sections'
& $rabin2.Command @($rabin2.PrefixArgs + @('-S', '--', $target))

Write-Section -Title 'Imports'
& $rabin2.Command @($rabin2.PrefixArgs + @('-i', '--', $target)) | Select-Object -First $ImportsLimit

Write-Section -Title 'Exports'
& $rabin2.Command @($rabin2.PrefixArgs + @('-E', '--', $target))

Write-Section -Title 'Strings'
& $rabin2.Command @($rabin2.PrefixArgs + @('-zz', '--', $target)) | Select-Object -First $StringsLimit

if ($RunAnalysis) {
    Write-Section -Title 'Functions and entry analysis'
    & $r2.Command @($r2.PrefixArgs + @('-A', '-q', '-c', 's entry0;afl;iz;ii;q', '--', $target))
}
