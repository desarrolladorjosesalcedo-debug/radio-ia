"""
Script de prueba para modo reader
"""
import sys
sys.path.insert(0, 'src')

print("=" * 60)
print("📖 PROBANDO MODO READER")
print("=" * 60)
print()
print("NOTA: Asegúrate de cambiar el modo en settings.yaml:")
print('  mode: "reader"')
print()

from core.radio_loop import start_radio

# Probar modo reader
start_radio(delay_seconds=1.0, skip_intro=True)
