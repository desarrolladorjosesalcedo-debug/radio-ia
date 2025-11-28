# install_dependencies.ps1
# Script de instalación para Windows PowerShell
# IMPORTANTE: Ejecuta setup_venv.ps1 primero para crear el entorno virtual

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Radio IA - Instalación de Dependencias" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Cambiar al directorio del proyecto
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptPath "..")

# Verificar si existe entorno virtual
if (Test-Path "venv") {
    Write-Host "✅ Entorno virtual detectado, activando..." -ForegroundColor Green
    . venv\Scripts\Activate.ps1
} else {
    Write-Host "⚠️  No se detectó entorno virtual" -ForegroundColor Yellow
    Write-Host "Se recomienda crear uno primero con: .\scripts\setup_venv.ps1" -ForegroundColor Yellow
    $response = Read-Host "¿Continuar sin entorno virtual? (s/n)"
    if ($response -ne 's' -and $response -ne 'S') {
        exit 0
    }
}
Write-Host ""

# Función para verificar comandos
function Test-Command {
    param($Command)
    $exists = $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
    if ($exists) {
        Write-Host "✓ $Command está instalado" -ForegroundColor Green
        return $true
    } else {
        Write-Host "✗ $Command no está instalado" -ForegroundColor Red
        return $false
    }
}

# 1. Verificar Python
Write-Host "1. Verificando Python..." -ForegroundColor Yellow
if (Test-Command python) {
    python --version
} else {
    Write-Host "Error: Python no está instalado" -ForegroundColor Red
    Write-Host "Instala Python desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# 2. Verificar pip
Write-Host ""
Write-Host "2. Verificando pip..." -ForegroundColor Yellow
if (Test-Command pip) {
    pip --version
} else {
    Write-Host "Instalando pip..." -ForegroundColor Yellow
    python -m ensurepip --upgrade
}

# 3. Instalar/Actualizar dependencias Python
Write-Host ""
Write-Host "3. Instalando/Actualizando dependencias Python..." -ForegroundColor Yellow
pip install --upgrade -r requirements.txt

# 4. Verificar Ollama
Write-Host ""
Write-Host "4. Verificando Ollama..." -ForegroundColor Yellow
if (Test-Command ollama) {
    ollama --version
    Write-Host "Ollama instalado correctamente" -ForegroundColor Green
} else {
    Write-Host "Ollama no encontrado" -ForegroundColor Yellow
    Write-Host "Instala Ollama desde: https://ollama.ai/" -ForegroundColor Yellow
    Write-Host "Luego ejecuta: ollama pull llama2" -ForegroundColor Yellow
}

# 5. Verificar Piper
Write-Host ""
Write-Host "5. Verificando Piper TTS..." -ForegroundColor Yellow
if (Test-Command piper) {
    piper --version
    Write-Host "Piper instalado correctamente" -ForegroundColor Green
} else {
    Write-Host "Piper no encontrado" -ForegroundColor Yellow
    Write-Host "Instala Piper desde: https://github.com/rhasspy/piper" -ForegroundColor Yellow
}

# 6. Verificar FFmpeg
Write-Host ""
Write-Host "6. Verificando FFmpeg..." -ForegroundColor Yellow
if (Test-Command ffplay) {
    ffplay -version | Select-Object -First 1
    Write-Host "FFmpeg instalado correctamente" -ForegroundColor Green
} else {
    Write-Host "FFmpeg no encontrado" -ForegroundColor Yellow
    Write-Host "Instala FFmpeg desde: https://ffmpeg.org/download.html" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Instalación completada" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Proximos pasos:" -ForegroundColor Yellow
Write-Host "1. Descarga un modelo de voz de Piper:"
Write-Host "   https://github.com/rhasspy/piper/releases"
Write-Host "2. Colocalo en: models/piper/"
Write-Host "3. Actualiza config/settings.yaml con la ruta del modelo"
Write-Host "4. Ejecuta: python src/main.py"
Write-Host ""
