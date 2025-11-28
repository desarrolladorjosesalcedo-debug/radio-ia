# run.ps1
# Script para ejecutar Radio IA en Windows PowerShell

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "       🎙️  Iniciando Radio IA" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Cambiar al directorio del proyecto
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptPath "..")

# Verificar que existe el código fuente
if (-not (Test-Path "src/main.py")) {
    Write-Host "Error: No se encuentra src/main.py" -ForegroundColor Red
    exit 1
}

# Activar entorno virtual si existe
if (Test-Path "venv/Scripts/Activate.ps1") {
    Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
    . venv/Scripts/Activate.ps1
}

# Ejecutar la aplicación
Write-Host "Iniciando Radio IA..." -ForegroundColor Green
Write-Host ""
python src/main.py

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "   Radio IA finalizada" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
