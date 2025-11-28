"""
edge_tts_client.py
Cliente para síntesis de voz usando Microsoft Edge TTS.

Este módulo usa las voces neuronales de Microsoft Edge para generar
audio de alta calidad de forma gratuita e ilimitada.

Características:
- Voces neuronales muy naturales (similares a Gemini)
- 100% gratuito e ilimitado
- Múltiples voces en español
- Conversión automática a formato RAW PCM

Uso:
    audio_bytes = synthesize_speech_edge("Hola mundo")
"""

import logging
import asyncio
import tempfile
import os
import subprocess
from pathlib import Path
import edge_tts

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Voces disponibles en español (neuronales de alta calidad)
SPANISH_VOICES = {
    "es-MX-DaliaNeural": "México, Mujer (Recomendada) ⭐",
    "es-MX-JorgeNeural": "México, Hombre",
    "es-ES-ElviraNeural": "España, Mujer",
    "es-ES-AlvaroNeural": "España, Hombre",
    "es-AR-ElenaNeural": "Argentina, Mujer",
    "es-AR-TomasNeural": "Argentina, Hombre",
    "es-CO-SalomeNeural": "Colombia, Mujer",
    "es-CO-GonzaloNeural": "Colombia, Hombre",
}


async def _generate_speech_async(text: str, voice: str, output_file: str):
    """
    Función asíncrona para generar el audio con Edge TTS.
    """
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)


def synthesize_speech_edge(
    text: str,
    voice: str = "es-MX-DaliaNeural",
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0Hz"
) -> bytes:
    """
    Convierte texto en audio usando Microsoft Edge TTS.
    
    Args:
        text (str): Texto a sintetizar en voz
        voice (str): Voz a usar (default: "es-MX-DaliaNeural")
        rate (str): Velocidad de habla (ej: "+10%", "-10%")
        volume (str): Volumen (ej: "+50%", "-20%")
        pitch (str): Tono de voz (ej: "+5Hz", "-10Hz")
    
    Returns:
        bytes: Audio en formato RAW PCM (16-bit, mono, 22050 Hz)
               Retorna bytes vacíos en caso de error
    """
    # Validar que hay texto para sintetizar
    if not text or not text.strip():
        logger.warning("⚠️  Texto vacío, no hay nada que sintetizar")
        return b""
    
    logger.info(f"🎤 Sintetizando {len(text)} caracteres con Edge TTS ({voice})...")
    
    try:
        # Crear archivo temporal para MP3
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as mp3_file:
            mp3_path = mp3_file.name
        
        try:
            # Generar audio con Edge TTS (asíncrono)
            asyncio.run(_generate_speech_async(text, voice, mp3_path))
            
            # Convertir MP3 a RAW PCM usando ffmpeg
            # 22050 Hz, mono, 16-bit signed little-endian
            result = subprocess.run(
                [
                    'ffmpeg',
                    '-i', mp3_path,
                    '-f', 's16le',      # signed 16-bit little-endian
                    '-ar', '22050',     # 22050 Hz
                    '-ac', '1',         # mono
                    '-'                 # output to stdout
                ],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                raw_data = result.stdout
                logger.info(f"✅ Audio generado exitosamente ({len(raw_data)} bytes)")
                return raw_data
            else:
                logger.error(f"❌ ffmpeg falló: {result.stderr.decode('utf-8', errors='ignore')}")
                return b""
        
        finally:
            # Limpiar archivo temporal
            if os.path.exists(mp3_path):
                os.unlink(mp3_path)
        
    except Exception as e:
        logger.error(f"❌ Error al generar voz con Edge TTS: {e}")
        return b""


def check_edge_tts_available() -> bool:
    """
    Verifica si Edge TTS está disponible.
    
    Returns:
        bool: True si Edge TTS está disponible
    """
    try:
        import edge_tts
        logger.info("✅ Microsoft Edge TTS disponible")
        return True
    except ImportError:
        logger.error("❌ Edge TTS no está instalado")
        logger.info("💡 Instala con: pip install edge-tts")
        return False


def list_available_voices():
    """
    Lista todas las voces disponibles en español.
    """
    logger.info("🎤 Voces disponibles en Edge TTS:")
    for voice_id, description in SPANISH_VOICES.items():
        logger.info(f"   - {voice_id}: {description}")
