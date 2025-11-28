# setup_venv.ps1
# Script para crear y configurar entorno virtual de Python

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Radio IA - Configuración de Entorno Virtual" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Cambiar al directorio del proyecto
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptPath "..")

# Verificar Python
Write-Host "1. Verificando Python..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue

if (-not $pythonCmd) {
    Write-Host "❌ Python no está instalado" -ForegroundColor Red
    Write-Host "Instala Python desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

python --version
Write-Host "✅ Python disponible" -ForegroundColor Green

# Verificar si ya existe el entorno virtual
Write-Host ""
Write-Host "2. Configurando entorno virtual..." -ForegroundColor Yellow

if (Test-Path "venv") {
    Write-Host "⚠️  El entorno virtual ya existe" -ForegroundColor Yellow
    $response = Read-Host "¿Deseas recrearlo? (s/n)"
    
    if ($response -eq 's' -or $response -eq 'S') {
        Write-Host "Eliminando entorno virtual existente..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force venv
    } else {
        Write-Host "Usando entorno virtual existente" -ForegroundColor Green
        . venv\Scripts\Activate.ps1
        Write-Host "✅ Entorno virtual activado" -ForegroundColor Green
        
        # Actualizar pip
        Write-Host ""
        Write-Host "3. Actualizando pip..." -ForegroundColor Yellow
        python -m pip install --upgrade pip
        
        # Instalar dependencias
        Write-Host ""
        Write-Host "4. Instalando dependencias..." -ForegroundColor Yellow
        pip install -r requirements.txt
        
        Write-Host ""
        Write-Host "======================================" -ForegroundColor Cyan
        Write-Host "✅ Configuración completada" -ForegroundColor Green
        Write-Host "======================================" -ForegroundColor Cyan
        exit 0
    }
}

# Crear entorno virtual
Write-Host "Creando entorno virtual..." -ForegroundColor Yellow
python -m venv venv

if (-not $?) {
    Write-Host "❌ Error al crear entorno virtual" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Entorno virtual creado" -ForegroundColor Green

# Activar entorno virtual
Write-Host ""
Write-Host "3. Activando entorno virtual..." -ForegroundColor Yellow
. venv\Scripts\Activate.ps1

if (-not $?) {
    Write-Host "❌ Error al activar entorno virtual" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Entorno virtual activado" -ForegroundColor Green

# Actualizar pip
Write-Host ""
Write-Host "4. Actualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Instalar dependencias
Write-Host ""
Write-Host "5. Instalando dependencias Python..." -ForegroundColor Yellow
pip install -r requirements.txt

if (-not $?) {
    Write-Host "❌ Error al instalar dependencias" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Dependencias instaladas" -ForegroundColor Green

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "✅ Entorno virtual configurado exitosamente" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Notas importantes:" -ForegroundColor Yellow
Write-Host "  - El entorno virtual esta en: venv\" -ForegroundColor White
Write-Host "  - Para activarlo manualmente: venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  - Para desactivarlo: deactivate" -ForegroundColor White
Write-Host ""
Write-Host "Proximos pasos:" -ForegroundColor Yellow
Write-Host "  1. Ejecuta: .\scripts\install_dependencies.ps1" -ForegroundColor White
Write-Host "  2. Descarga un modelo de Piper para models/piper/" -ForegroundColor White
Write-Host "  3. Ejecuta: .\scripts\run.ps1" -ForegroundColor White
Write-Host ""
