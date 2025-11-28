# Test Session History
# Genera una sesión corta de prueba para validar el sistema de historial

Write-Host "🧪 Iniciando prueba del sistema de historial..." -ForegroundColor Cyan
Write-Host "="*60

# Verificar que no hay sesiones
Write-Host "`n📋 Estado inicial:" -ForegroundColor Yellow
& C:/programacion/radio-ia/venv/Scripts/python.exe c:/programacion/radio-ia/src/main.py --list-sessions

Write-Host "`n🎙️ Generando sesión de prueba (espera ~45 segundos)..." -ForegroundColor Yellow
Write-Host "💡 La radio se detendrá automáticamente después de 2 segmentos`n"

# Crear script temporal de Python para generar 2 segmentos
$testScript = @"
import sys
sys.path.insert(0, 'src')
from core.radio_loop import start_radio
start_radio(delay_seconds=2.0, max_iterations=2, skip_intro=False)
"@

$testScript | Out-File -FilePath "test_session.py" -Encoding UTF8

# Ejecutar radio con 2 segmentos
& C:/programacion/radio-ia/venv/Scripts/python.exe test_session.py

# Limpiar
Remove-Item "test_session.py" -ErrorAction SilentlyContinue

Write-Host "`n📊 Sesiones guardadas:" -ForegroundColor Yellow
& C:/programacion/radio-ia/venv/Scripts/python.exe c:/programacion/radio-ia/src/main.py --list-sessions

Write-Host "`n✅ Prueba completada!" -ForegroundColor Green
Write-Host "💡 Comandos disponibles:" -ForegroundColor Cyan
Write-Host "   python src/main.py --list-sessions"
Write-Host "   python src/main.py --show SESSION_ID"
Write-Host "   python src/main.py --replay SESSION_ID"
