"""
Script de prueba para modo monólogo
"""
import sys
sys.path.insert(0, 'src')
from core.radio_loop import start_radio

# Probar modo monólogo con 2 segmentos
print("=" * 60)
print("🧠 PROBANDO MODO MONÓLOGO")
print("=" * 60)
start_radio(delay_seconds=1.0, max_iterations=2, skip_intro=True)
