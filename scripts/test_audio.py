"""
test_audio.py
Script de prueba simple para verificar que TTS y reproducción funcionan.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tts.piper_tts import synthesize_speech
from utils.audio_player import play_audio

print("=" * 60)
print("🧪 PRUEBA DE AUDIO")
print("=" * 60)

# Texto de prueba
texto = "Hola, esta es una prueba de audio. Si escuchas esto, el sistema funciona correctamente."

print(f"\n📝 Texto a sintetizar: {texto}")
print("\n🎤 Generando audio con Piper...")

# Generar audio
audio = synthesize_speech(
    texto, 
    "models/piper/es_ES-davefx-medium.onnx"
)

if not audio:
    print("❌ Error: No se generó audio")
    sys.exit(1)

print(f"✅ Audio generado: {len(audio)} bytes")

# Guardar audio a archivo para debug
with open("test_audio.raw", "wb") as f:
    f.write(audio)
print("💾 Audio guardado en: test_audio.raw")

print("\n🔊 Reproduciendo audio...")
print("(Deberías escuchar el mensaje de prueba)\n")

# Reproducir
play_audio(audio, sample_rate=22050)

print("\n✅ Prueba completada")
print("=" * 60)
