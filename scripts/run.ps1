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

# Refrescar PATH para incluir FFmpeg y otras herramientas del sistema
# Esto es necesario porque FFmpeg puede estar en PATH de máquina pero no en sesión actual
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
Write-Host "✅ PATH actualizado con variables de sistema" -ForegroundColor Green

# Activar entorno virtual si existe
if (Test-Path "venv/Scripts/Activate.ps1") {
    Write-Host "✅ Activando entorno virtual..." -ForegroundColor Yellow
    . venv/Scripts/Activate.ps1
}

# Verificar que FFmpeg está disponible
$ffplayPath = Get-Command ffplay -ErrorAction SilentlyContinue
if ($ffplayPath) {
    Write-Host "✅ FFmpeg encontrado: $($ffplayPath.Source)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Advertencia: FFmpeg no encontrado en PATH" -ForegroundColor Yellow
    Write-Host "   La reproducción de audio puede fallar" -ForegroundColor Yellow
}

# Ejecutar la aplicación
Write-Host ""
Write-Host "Iniciando Radio IA..." -ForegroundColor Green
Write-Host ""
python src/main.py

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "   Radio IA finalizada" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
