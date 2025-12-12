"""
ejemplo_uso_tts_mejorado.py
Ejemplos de uso del nuevo sistema TTS mejorado.

Demuestra:
1. Uso básico del TTS Manager
2. Control SSML avanzado
3. Caché de audio
4. Post-procesamiento
5. Estadísticas
"""

import sys
from pathlib import Path

# Agregar src al path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from tts.tts_manager import TTSManager
from tts.ssml_builder import SSMLBuilder, create_enhanced_text
from tts.cache_manager import AudioCache
from tts.audio_processor import AudioProcessor


def ejemplo_1_uso_basico():
    """Ejemplo 1: Uso básico del TTS Manager."""
    print("\n" + "="*60)
    print("EJEMPLO 1: Uso Básico del TTS Manager")
    print("="*60)
    
    # Crear manager con todas las funcionalidades
    manager = TTSManager(
        use_cache=True,
        use_processing=True,
        use_ssml=False
    )
    
    # Sintetizar texto simple
    texto = "Hola, bienvenidos a Radio IA. Este es un ejemplo de síntesis mejorada."
    
    audio = manager.synthesize(
        texto,
        provider="auto",  # Usa fallback automático
        voice="es-MX-DaliaNeural"
    )
    
    print(f"✅ Audio generado: {len(audio)} bytes")
    
    # Ver estadísticas
    stats = manager.get_stats()
    print(f"📊 Solicitudes: {stats['total_requests']}")
    print(f"📊 Caché hits: {stats['cache_hits']}")


def ejemplo_2_ssml_avanzado():
    """Ejemplo 2: Control fino con SSML."""
    print("\n" + "="*60)
    print("EJEMPLO 2: Control SSML Avanzado")
    print("="*60)
    
    # Construir SSML manualmente
    builder = SSMLBuilder(voice="es-MX-DaliaNeural")
    
    ssml_text = (builder
        .add_text("Hola, soy tu asistente de voz.", rate="medium", pitch="medium")
        .add_pause(500)
        .add_emphasis("Este mensaje es importante", level="strong")
        .add_pause(300)
        .add_text("Gracias por escuchar.", rate="slow", volume="loud")
        .build())
    
    print("📝 SSML generado:")
    print(ssml_text[:200] + "...")
    
    # Usar estilos predefinidos
    texto = "En el mundo de la tecnología, la innovación es clave. Los desarrolladores trabajan día a día para crear soluciones."
    
    for estilo in ["standard", "podcast", "news", "storytelling"]:
        ssml = create_enhanced_text(texto, style=estilo)
        print(f"\n📻 Estilo '{estilo}': {len(ssml)} caracteres")


def ejemplo_3_cache():
    """Ejemplo 3: Sistema de caché."""
    print("\n" + "="*60)
    print("EJEMPLO 3: Sistema de Caché")
    print("="*60)
    
    cache = AudioCache(cache_dir="cache/test", max_age_days=7)
    
    # Simular audio
    texto = "Este es un texto de prueba para el caché"
    audio_fake = b"fake_audio_data_12345" * 1000
    
    # Guardar en caché
    cache.set(texto, audio_fake, provider="edge", voice="es-MX-DaliaNeural")
    print(f"💾 Audio guardado en caché: {len(audio_fake)} bytes")
    
    # Recuperar del caché
    audio_cached = cache.get(texto, provider="edge", voice="es-MX-DaliaNeural")
    
    if audio_cached:
        print(f"✅ Audio recuperado del caché: {len(audio_cached)} bytes")
        print(f"🎯 Match: {audio_cached == audio_fake}")
    
    # Estadísticas
    cache.print_stats()


def ejemplo_4_post_procesamiento():
    """Ejemplo 4: Post-procesamiento de audio."""
    print("\n" + "="*60)
    print("EJEMPLO 4: Post-procesamiento de Audio")
    print("="*60)
    
    try:
        import numpy as np
        
        processor = AudioProcessor(sample_rate=22050)
        
        # Simular audio (1 segundo de onda sinusoidal)
        t = np.linspace(0, 1, 22050)
        audio_array = np.sin(2 * np.pi * 440 * t) * 0.5  # 440 Hz
        audio_bytes = processor.array_to_bytes(audio_array)
        
        print(f"🎵 Audio original: {len(audio_bytes)} bytes")
        
        # Analizar calidad original
        audio_float = processor.bytes_to_array(audio_bytes)
        quality_before = processor.analyze_quality(audio_float)
        print(f"📊 Calidad original: RMS={quality_before['rms_db']}dB, Peak={quality_before['peak_db']}dB")
        
        # Procesar
        audio_processed = processor.process(
            audio_bytes,
            normalize=True,
            compress=True,
            highpass=False,  # Sin filtro para mantener la señal de prueba
            target_db=-20.0
        )
        
        print(f"✨ Audio procesado: {len(audio_processed)} bytes")
        
        # Analizar calidad final
        audio_float_processed = processor.bytes_to_array(audio_processed)
        quality_after = processor.analyze_quality(audio_float_processed)
        print(f"📊 Calidad final: RMS={quality_after['rms_db']}dB, Peak={quality_after['peak_db']}dB")
        
    except ImportError:
        print("⚠️  NumPy no disponible - ejemplo omitido")


def ejemplo_5_integracion_completa():
    """Ejemplo 5: Integración completa con todas las funcionalidades."""
    print("\n" + "="*60)
    print("EJEMPLO 5: Integración Completa")
    print("="*60)
    
    # Manager con todo activado
    manager = TTSManager(
        use_cache=True,
        use_processing=True,
        use_ssml=True,
        fallback_chain=["edge", "piper", "gtts"]
    )
    
    textos = [
        "Este es el primer segmento de prueba.",
        "Este es el segundo segmento.",
        "Este es el primer segmento de prueba.",  # Repetido - debe usar caché
    ]
    
    for i, texto in enumerate(textos, 1):
        print(f"\n🎤 Sintetizando segmento #{i}...")
        
        audio = manager.synthesize(
            texto,
            provider="auto",
            voice="es-MX-DaliaNeural",
            style="podcast"
        )
        
        print(f"   ✅ Generado: {len(audio)} bytes")
    
    # Estadísticas finales
    print("\n📊 ESTADÍSTICAS FINALES:")
    manager.print_stats()


if __name__ == "__main__":
    print("\n🎙️  EJEMPLOS DE USO - TTS MEJORADO\n")
    
    try:
        ejemplo_1_uso_basico()
        ejemplo_2_ssml_avanzado()
        ejemplo_3_cache()
        ejemplo_4_post_procesamiento()
        ejemplo_5_integracion_completa()
        
        print("\n" + "="*60)
        print("✅ Todos los ejemplos completados")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Ejemplos interrumpidos por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
