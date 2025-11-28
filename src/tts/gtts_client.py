"""
gtts_client.py
Cliente alternativo para síntesis de voz usando Google Text-to-Speech (gTTS).

Este módulo es una alternativa cuando Piper TTS no funciona correctamente.
Usa la API de Google para convertir texto a voz.

Características:
- Síntesis de voz con Google TTS
- Soporte para español
- Conversión automática a formato RAW PCM usando ffmpeg
- Fácil de usar

Uso:
    audio_bytes = synthesize_speech_gtts("Hola mundo")
"""

import logging
import io
import subprocess
import tempfile
import os
from gtts import gTTS
from pathlib import Path
from typing import Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def synthesize_speech_gtts(
    text: str,
    lang: str = "es",
    slow: bool = False
) -> bytes:
    """
    Convierte texto en audio usando Google TTS.
    
    Args:
        text (str): Texto a sintetizar en voz
        lang (str): Código de idioma (default: "es" para español)
        slow (bool): Si True, habla más lentamente
    
    Returns:
        bytes: Audio en formato RAW PCM (16-bit, mono, 22050 Hz)
               Retorna bytes vacíos en caso de error
    """
    # Validar que hay texto para sintetizar
    if not text or not text.strip():
        logger.warning("⚠️  Texto vacío, no hay nada que sintetizar")
        return b""
    
    logger.info(f"🎤 Sintetizando {len(text)} caracteres con Google TTS...")
    
    try:
        # Generar audio con gTTS
        tts = gTTS(text=text, lang=lang, slow=slow)
        
        # Crear archivo temporal para MP3
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as mp3_file:
            mp3_path = mp3_file.name
            tts.write_to_fp(mp3_file)
        
        try:
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
        logger.error(f"❌ Error al generar voz con Google TTS: {e}")
        return b""


def check_gtts_available() -> bool:
    """
    Verifica si gTTS está disponible.
    
    Returns:
        bool: True si gTTS está disponible
    """
    try:
        # Intentar importar
        from gtts import gTTS
        logger.info("✅ Google TTS disponible")
        return True
    except ImportError:
        logger.error("❌ Google TTS no está instalado")
        logger.info("💡 Instala con: pip install gtts pydub")
        return False
