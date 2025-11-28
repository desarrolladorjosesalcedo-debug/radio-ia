"""
test_ollama.py
Script de prueba para verificar que Ollama genera texto correctamente.
"""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm.ollama_client import generate_text

print("=" * 60)
print("🧪 PRUEBA DE OLLAMA")
print("=" * 60)

# Prompt simple para prueba
prompt = """Genera una frase corta y simple sobre tecnología, máximo 20 palabras. 
No uses formato markdown ni asteriscos. Habla directamente.

Comienza:"""

print(f"\n📝 Prompt de prueba: {prompt[:100]}...")
print("\n🤖 Generando texto con Ollama (llama2)...")
print("⏱️  Esto puede tardar 1-3 minutos en la primera ejecución...")
print("    (Las siguientes serán más rápidas)\n")

# Medir tiempo
inicio = time.time()

# Generar texto
texto = generate_text("llama2", prompt, timeout=180)

fin = time.time()
tiempo_total = fin - inicio

print("\n" + "=" * 60)
print("📊 RESULTADOS")
print("=" * 60)
print(f"⏱️  Tiempo de generación: {tiempo_total:.2f} segundos")
print(f"📝 Texto generado ({len(texto)} caracteres):")
print("-" * 60)
print(texto)
print("-" * 60)

if tiempo_total > 180:
    print("\n❌ PROBLEMA: Generación superó el timeout")
    print("💡 Solución: Usa un modelo más rápido como 'tinyllama'")
elif tiempo_total > 60:
    print("\n⚠️  ADVERTENCIA: Generación lenta")
    print(f"   Tomó {tiempo_total:.0f} segundos (más de 1 minuto)")
    print("💡 Considera usar un modelo más rápido")
else:
    print(f"\n✅ ÉXITO: Generación completada en {tiempo_total:.0f} segundos")

print("=" * 60)
