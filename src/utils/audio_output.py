"""
audio_output.py
Módulo unificado para salida de audio - Local o Streaming
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Variable global para el modo de salida
_output_mode = "local"  # "local" o "streaming"
_stream_manager = None


def set_output_mode(mode: str, stream_manager=None):
    """
    Configura el modo de salida de audio
    
    Args:
        mode: "local" para reproducción local, "streaming" para web
        stream_manager: Instancia de AudioStreamManager si mode="streaming"
    """
    global _output_mode, _stream_manager
    _output_mode = mode
    _stream_manager = stream_manager
    logger.info(f"🔊 Modo de salida configurado: {mode}")


def output_audio(audio_bytes: bytes, sample_rate: int = 22050, metadata: dict = None, stop_flag=None) -> bool:
    """
    Envía audio a la salida configurada (local o streaming)
    
    Args:
        audio_bytes: Audio en bytes (RAW PCM)
        sample_rate: Frecuencia de muestreo
        metadata: Metadata del segmento (tema, duración, etc.)
        stop_flag: threading.Event para detener reproducción inmediatamente
    
    Returns:
        bool: True si se envió correctamente
    """
    if _output_mode == "streaming":
        if _stream_manager:
            # Convertir RAW PCM a MP3 para streaming web
            mp3_audio = _convert_to_mp3(audio_bytes, sample_rate)
            if mp3_audio:
                return _stream_manager.add_audio(mp3_audio, metadata)
            else:
                logger.error("❌ Falló conversión a MP3 para streaming")
                return False
        else:
            logger.error("❌ Streaming habilitado pero sin StreamManager")
            return False
    
    else:  # local
        try:
            from utils.audio_player import play_audio
            play_audio(audio_bytes, sample_rate=sample_rate, stop_flag=stop_flag)
            return True
        except Exception as e:
            logger.error(f"❌ Error reproduciendo localmente: {e}")
            return False


def _convert_to_mp3(raw_audio: bytes, sample_rate: int) -> bytes:
    """
    Convierte audio RAW PCM a MP3
    
    Args:
        raw_audio: Audio en formato RAW PCM (16-bit signed little-endian, mono)
        sample_rate: Frecuencia de muestreo (ej: 22050)
    
    Returns:
        bytes: Audio en formato MP3, o bytes vacíos si falla
    """
    import subprocess
    import tempfile
    import os
    
    try:
        # Crear archivos temporales
        with tempfile.NamedTemporaryFile(delete=False, suffix='.raw') as raw_file:
            raw_file.write(raw_audio)
            raw_path = raw_file.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as mp3_file:
            mp3_path = mp3_file.name
        
        try:
            # Convertir RAW PCM a MP3 con ffmpeg
            result = subprocess.run(
                [
                    'ffmpeg',
                    '-f', 's16le',              # input format: signed 16-bit little-endian
                    '-ar', str(sample_rate),    # sample rate
                    '-ac', '1',                 # mono
                    '-i', raw_path,             # input file
                    '-codec:a', 'libmp3lame',   # MP3 encoder
                    '-b:a', '128k',             # bitrate
                    '-y',                       # overwrite output
                    mp3_path
                ],
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                with open(mp3_path, 'rb') as f:
                    mp3_data = f.read()
                logger.info(f"✅ Convertido a MP3: {len(raw_audio)} → {len(mp3_data)} bytes")
                return mp3_data
            else:
                logger.error(f"❌ ffmpeg falló: {result.stderr.decode('utf-8', errors='ignore')}")
                return b""
        
        finally:
            # Limpiar archivos temporales
            if os.path.exists(raw_path):
                os.unlink(raw_path)
            if os.path.exists(mp3_path):
                os.unlink(mp3_path)
    
    except Exception as e:
        logger.error(f"❌ Error convirtiendo a MP3: {e}")
        return b""
