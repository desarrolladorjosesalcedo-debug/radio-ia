"""
elevenlabs_tts.py
Cliente para síntesis de voz usando ElevenLabs API.

Este módulo usa las voces de alta calidad de ElevenLabs para generar
audio realista y natural.

Características:
- Voces ultrarrealistas con emociones
- Soporte multilingüe incluido español
- Alta calidad de audio
- API key requerida

Uso:
    audio_bytes = synthesize_speech_elevenlabs("Hola mundo", api_key="tu_api_key")
"""

import logging
import os
from typing import Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_elevenlabs_available(api_key: Optional[str] = None) -> bool:
    """
    Verifica si ElevenLabs está disponible.
    
    Args:
        api_key: API key de ElevenLabs (opcional, se puede obtener de variable de entorno)
    
    Returns:
        bool: True si ElevenLabs está disponible
    """
    try:
        from elevenlabs.client import ElevenLabs
        
        # Verificar API key
        key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not key:
            logger.warning("⚠️  ElevenLabs API key no encontrada")
            return False
        
        # Intentar crear cliente
        client = ElevenLabs(api_key=key)
        
        logger.info("✅ ElevenLabs TTS disponible")
        return True
    
    except ImportError:
        logger.warning("⚠️  Librería elevenlabs no instalada")
        logger.info("💡 Instala con: pip install elevenlabs")
        return False
    except Exception as e:
        logger.warning(f"⚠️  ElevenLabs no disponible: {e}")
        return False


def synthesize_speech_elevenlabs(
    text: str, 
    voice_id: str = "pNInz6obpgDQGcFmaJgB",  # Adam - voz masculina en inglés
    model_id: str = "eleven_multilingual_v2",
    api_key: Optional[str] = None
) -> Optional[bytes]:
    """
    Sintetiza voz usando ElevenLabs API.
    
    Args:
        text (str): Texto a sintetizar
        voice_id (str): ID de la voz (default: Adam)
        model_id (str): ID del modelo (default: eleven_multilingual_v2 para español)
        api_key (str): API key de ElevenLabs (opcional, usa variable de entorno si no se proporciona)
    
    Returns:
        Optional[bytes]: Audio en formato MP3, o None si falla
    
    Voces recomendadas para español:
    - "pNInz6obpgDQGcFmaJgB" - Adam (voz masculina clara)
    - "21m00Tcm4TlvDq8ikWAM" - Rachel (voz femenina)
    - "JBFqnCBsd6RMkjVDRZzb" - George (voz masculina profunda)
    """
    try:
        from elevenlabs.client import ElevenLabs
        import io
        
        # Obtener API key
        key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not key:
            logger.error("❌ ElevenLabs API key no encontrada")
            return None
        
        # Crear cliente
        client = ElevenLabs(api_key=key)
        
        logger.info(f"🎤 Generando audio con ElevenLabs (voice: {voice_id[:8]}...)")
        
        # Generar audio
        audio_generator = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            output_format="mp3_44100_128"
        )
        
        # Convertir el generador a bytes
        audio_bytes = b""
        for chunk in audio_generator:
            audio_bytes += chunk
        
        if audio_bytes:
            logger.info(f"✅ Audio generado con ElevenLabs ({len(audio_bytes)} bytes)")
            return audio_bytes
        else:
            logger.error("❌ ElevenLabs retornó audio vacío")
            return None
    
    except ImportError:
        logger.error("❌ Librería elevenlabs no instalada")
        logger.info("💡 Instala con: pip install elevenlabs")
        return None
    
    except Exception as e:
        logger.error(f"❌ Error generando audio con ElevenLabs: {e}")
        return None


# Voces disponibles en ElevenLabs (algunas populares)
ELEVENLABS_VOICES = {
    "pNInz6obpgDQGcFmaJgB": "Adam - Voz masculina clara (Inglés/Multilingüe)",
    "21m00Tcm4TlvDq8ikWAM": "Rachel - Voz femenina suave (Inglés/Multilingüe)",
    "JBFqnCBsd6RMkjVDRZzb": "George - Voz masculina profunda (Inglés/Multilingüe)",
    "EXAVITQu4vr4xnSDxMaL": "Sarah - Voz femenina joven (Inglés/Multilingüe)",
    "onwK4e9ZLuTAKqWW03F9": "Daniel - Voz masculina madura (Inglés/Multilingüe)",
}


if __name__ == "__main__":
    """
    Prueba del módulo ElevenLabs TTS
    """
    print("=" * 60)
    print("🎤 PRUEBA DE ELEVENLABS TTS")
    print("=" * 60)
    
    # Verificar disponibilidad
    if check_elevenlabs_available():
        # Texto de prueba en español
        texto = "Hola, soy una prueba de la síntesis de voz de ElevenLabs. Esta tecnología genera voces muy naturales."
        
        print(f"\n📝 Texto: {texto}")
        print("\n🎤 Generando audio...")
        
        audio = synthesize_speech_elevenlabs(texto)
        
        if audio:
            # Guardar audio en archivo temporal
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                f.write(audio)
                temp_path = f.name
            
            print(f"✅ Audio generado: {len(audio)} bytes")
            print(f"💾 Guardado en: {temp_path}")
            print(f"🔊 Reproduce con: ffplay {temp_path}")
        else:
            print("❌ No se pudo generar audio")
    else:
        print("❌ ElevenLabs TTS no está disponible")
        print("💡 Configura ELEVENLABS_API_KEY en tu entorno")
    
    print("\n" + "=" * 60)
