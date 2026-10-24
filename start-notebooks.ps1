# Sync the uv project and open JupyterLab for one language/module (Windows PowerShell).
# Usage: .\start-notebooks.ps1 -Language en -Module capstone [-DryRun]
param(
    [ValidateSet('en', 'zh-CN')]
    [string]$Language = 'zh-CN',
    [ValidateSet('foundations', 'capstone', 'frontiers')]
    [string]$Module = 'foundations',
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'

# One uv project for the whole course: this repository root. Both language
# editions share the root .venv, so `uv sync` once and every module runs.
# scripts/course_map.py is the single source of truth for module directories.
function Invoke-CourseUv {
    param([string[]]$UvArguments)
    $uvCommand = Get-Command uv -ErrorAction SilentlyContinue
    if ($uvCommand) { & $uvCommand.Source @UvArguments } else { & python -m uv @UvArguments }
    if ($LASTEXITCODE -ne 0) { throw 'uv failed. Read the preceding error message.' }
}

Push-Location $PSScriptRoot
try {
    $mapScript = Join-Path $PSScriptRoot 'scripts/course_map.py'
    if (-not (Test-Path -LiteralPath $mapScript -PathType Leaf)) { throw "Missing $mapScript" }
    $target = (& python $mapScript --module-dir $Language $Module).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $target) { throw "Cannot resolve module '$Module' for language '$Language'." }
    if ($DryRun) {
        [pscustomobject]@{
            Language = $Language
            Module = $Module
            ProjectRoot = $PSScriptRoot
            NotebookDir = $target
        }
        return
    }
    if (-not (Test-Path -LiteralPath $target -PathType Container)) {
        throw "No courseware at $target. The English mirror of this module may not be translated yet."
    }
    if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'uv.lock') -PathType Leaf)) {
        throw 'Missing uv.lock in the repository root. Restore it with git checkout, see README.md.'
    }
    Invoke-CourseUv -UvArguments @('sync', '--locked')
    Invoke-CourseUv -UvArguments @('run', '--locked', 'jupyter', 'lab', '--notebook-dir', $target)
} finally {
    Pop-Location
}
