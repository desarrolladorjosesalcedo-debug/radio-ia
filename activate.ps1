# activate.ps1
# Script para configurar entorno de Radio IA

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "   Configurando Radio IA" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host "[1/3] Actualizando PATH del sistema..." -ForegroundColor Yellow
$machinePath = [System.Environment]::GetEnvironmentVariable("Path","Machine")
$userPath = [System.Environment]::GetEnvironmentVariable("Path","User")
$env:Path = $machinePath + ";" + $userPath
Write-Host "      OK - PATH actualizado" -ForegroundColor Green

Write-Host ""
Write-Host "[2/3] Activando entorno virtual..." -ForegroundColor Yellow
if (Test-Path "venv/Scripts/Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
    Write-Host "      OK - Virtual environment activo" -ForegroundColor Green
} else {
    Write-Host "      ERROR: venv no encontrado" -ForegroundColor Red
    return
}

Write-Host ""
Write-Host "[3/3] Verificando dependencias..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "      Python: $pythonVersion" -ForegroundColor Green

$ffplayPath = Get-Command ffplay -ErrorAction SilentlyContinue
if ($ffplayPath) {
    Write-Host "      FFmpeg: OK" -ForegroundColor Green
} else {
    Write-Host "      FFmpeg: No encontrado" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "   LISTO" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Comandos:" -ForegroundColor Cyan
Write-Host "  python src/main.py              # Iniciar radio"
Write-Host "  python src/main.py --help       # Ver ayuda"
Write-Host ""
