param(
    [switch]$SkipInstall,
    [switch]$NoBackend,
    [switch]$NoFrontend,
    [switch]$UseDevProfile
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[PlateRate] $Message" -ForegroundColor Cyan
}

function Test-Command {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Wait-Backend {
    param(
        [int]$TimeoutSeconds = 120,
        [System.Diagnostics.Process]$BackendProcess
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $url = "http://127.0.0.1:8080/api/restaurants"

    while ((Get-Date) -lt $deadline) {
        if ($BackendProcess -and $BackendProcess.HasExited) {
            throw "Backend process exited before startup completed. Check the backend terminal window for errors."
        }

        try {
            $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return
            }
        } catch {
            # Keep waiting while backend is starting.
        }

        Start-Sleep -Seconds 2
    }

    throw "Backend did not become ready within $TimeoutSeconds seconds at $url"
}

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $repoRoot "backend"
$frontendDir = Join-Path $repoRoot "frontend"
$venvDir = Join-Path $repoRoot ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"
$backendWrapper = Join-Path $backendDir "mvnw.cmd"

Write-Step "Repository root: $repoRoot"

if (-not (Test-Path $backendWrapper) -and -not $NoBackend) {
    throw "Missing backend Maven wrapper at: $backendWrapper"
}

if (-not (Test-Command "java") -and -not $NoBackend) {
    throw "Java was not found in PATH. Install JDK 17+ and retry."
}

if (-not (Test-Command "python")) {
    throw "Python was not found in PATH. Install Python 3.8+ and retry."
}

if (-not $NoFrontend) {
    if (-not (Test-Path $venvPython)) {
        Write-Step "Creating Python virtual environment..."
        Set-Location $repoRoot
        python -m venv .venv
    }

    if (-not $SkipInstall) {
        Write-Step "Installing frontend Python dependencies..."
        & $venvPython -m pip install --upgrade pip
        & $venvPython -m pip install -r (Join-Path $frontendDir "requirements.txt")
    }
}

if (-not $NoBackend) {
    $backendCmd = if ($UseDevProfile) {
        "Set-Location '$backendDir'; `$env:SPRING_PROFILES_ACTIVE='dev'; .\mvnw.cmd spring-boot:run"
    } else {
        "Set-Location '$backendDir'; .\mvnw.cmd spring-boot:run"
    }

    Write-Step "Starting backend in a new PowerShell window..."
    $backendProcess = Start-Process powershell -PassThru -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-Command", $backendCmd
    )

    if (-not $NoFrontend) {
        Write-Step "Waiting for backend to become ready before starting frontend..."
        Wait-Backend -TimeoutSeconds 150 -BackendProcess $backendProcess
        Write-Step "Backend is ready."
    }
}

if (-not $NoFrontend) {
    $frontendCmd = "Set-Location '$repoRoot'; & '$venvPython' 'frontend/app.py'"

    Write-Step "Starting frontend in a new PowerShell window..."
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-Command", $frontendCmd
    ) | Out-Null
}

Write-Step "Startup commands launched."
Write-Host "Frontend: http://127.0.0.1:5000" -ForegroundColor Green
Write-Host "Backend:  http://127.0.0.1:8080" -ForegroundColor Green
Write-Host ""
Write-Host "Options:" -ForegroundColor Yellow
Write-Host "  -SkipInstall        Skip pip install"
Write-Host "  -UseDevProfile      Run backend with dev profile (H2)"
Write-Host "  -NoBackend          Start only frontend"
Write-Host "  -NoFrontend         Start only backend"
