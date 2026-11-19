$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
Set-Location -LiteralPath $projectRoot

$pythonLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
if (-not $pythonLauncher) {
    throw "Install Python 3.14 (64-bit) and enable the Python launcher."
}

$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $venvPython)) {
    & $pythonLauncher.Source -3.14 -m venv (Join-Path $projectRoot ".venv")
    if ($LASTEXITCODE -ne 0) {
        throw "Could not create the build environment."
    }
}

& $venvPython -m pip install -r (Join-Path $projectRoot "requirements-build.txt")
if ($LASTEXITCODE -ne 0) {
    throw "Could not install build dependencies."
}

$compiler = Get-Command ISCC.exe -ErrorAction SilentlyContinue
$compilerPath = if ($compiler) { $compiler.Source }
if (-not $compilerPath) {
    $compilerCandidates = @(
        (Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe")
    )
    $compilerPath = $compilerCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (-not $compilerPath) {
        throw "Install Inno Setup 6 to compile installer.iss."
    }
}

$buildId = [guid]::NewGuid().ToString("N")
$tempRoot = Join-Path $env:TEMP "ConfigGeneratorBuild_$buildId"
$stagedDist = Join-Path $tempRoot "dist"
$stagedWork = Join-Path $tempRoot "work"
$stagedInstaller = Join-Path $tempRoot "installer"
$distRoot = Join-Path $projectRoot "dist"
$releaseDir = Join-Path $distRoot "ConfigGenerator"
$nextReleaseDir = Join-Path $distRoot "ConfigGenerator_next_$buildId"
$previousReleaseDir = Join-Path $distRoot "ConfigGenerator_previous_$buildId"
$installerOutputDir = Join-Path $projectRoot "installer"

New-Item -ItemType Directory -Path $stagedDist, $stagedWork, $stagedInstaller -Force | Out-Null

try {
    & $venvPython -m PyInstaller --clean --noconfirm `
        --distpath $stagedDist --workpath $stagedWork `
        (Join-Path $projectRoot "ConfigGenerator.spec")
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed."
    }

    $stagedApp = Join-Path $stagedDist "ConfigGenerator"
    if (-not (Test-Path -LiteralPath (Join-Path $stagedApp "ConfigGenerator.exe"))) {
        throw "PyInstaller did not produce ConfigGenerator.exe."
    }

    New-Item -ItemType Directory -Path $distRoot -Force | Out-Null
    if (Test-Path -LiteralPath $nextReleaseDir) {
        throw "The staged release directory already exists."
    }
    Copy-Item -LiteralPath $stagedApp -Destination $nextReleaseDir -Recurse

    $stagedHash = (Get-FileHash -LiteralPath (Join-Path $stagedApp "ConfigGenerator.exe")).Hash
    $copiedHash = (Get-FileHash -LiteralPath (Join-Path $nextReleaseDir "ConfigGenerator.exe")).Hash
    if ($stagedHash -ne $copiedHash) {
        throw "The staged application copy failed verification."
    }

    $runningApp = Get-CimInstance Win32_Process -Filter "Name = 'ConfigGenerator.exe'"
    if ($runningApp) {
        throw "Close Config Generator before replacing the installed build."
    }

    if (Test-Path -LiteralPath $releaseDir) {
        Move-Item -LiteralPath $releaseDir -Destination $previousReleaseDir
    }
    try {
        Move-Item -LiteralPath $nextReleaseDir -Destination $releaseDir
    } catch {
        if (
            (Test-Path -LiteralPath $previousReleaseDir) -and
            -not (Test-Path -LiteralPath $releaseDir)
        ) {
            Move-Item -LiteralPath $previousReleaseDir -Destination $releaseDir
        }
        throw
    }

    & $compilerPath ("/O" + $stagedInstaller) (Join-Path $projectRoot "installer.iss")
    if ($LASTEXITCODE -ne 0) {
        throw "Inno Setup compilation failed."
    }

    $setupFile = Get-ChildItem -LiteralPath $stagedInstaller -Filter "ConfigGenerator_Setup_*.exe" |
        Select-Object -First 1
    if (-not $setupFile) {
        throw "Inno Setup did not produce a setup executable."
    }

    New-Item -ItemType Directory -Path $installerOutputDir -Force | Out-Null
    $finalSetupPath = Join-Path $installerOutputDir $setupFile.Name
    Copy-Item -LiteralPath $setupFile.FullName -Destination $finalSetupPath -Force
    $stagedSetupHash = (Get-FileHash -LiteralPath $setupFile.FullName).Hash
    $finalSetupHash = (Get-FileHash -LiteralPath $finalSetupPath).Hash
    if ($stagedSetupHash -ne $finalSetupHash) {
        throw "The setup executable copy failed verification."
    }

    if (Test-Path -LiteralPath $previousReleaseDir) {
        Remove-Item -LiteralPath $previousReleaseDir -Recurse -Force
    }

    Write-Output "Application built in dist\ConfigGenerator."
    Write-Output "Installer created at $finalSetupPath."
} finally {
    if (Test-Path -LiteralPath $nextReleaseDir) {
        Remove-Item -LiteralPath $nextReleaseDir -Recurse -Force
    }
    if (Test-Path -LiteralPath $tempRoot) {
        Remove-Item -LiteralPath $tempRoot -Recurse -Force
    }
}
