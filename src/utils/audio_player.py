"""
audio_player.py
Reproductor de audio para transmisión continua en Radio IA.

Este módulo reproduce audio RAW PCM en tiempo real usando ffplay.
Recibe bytes de audio generados por Piper TTS y los reproduce inmediatamente,
simulando una transmisión de radio real.

Características:
- Reproducción en tiempo real sin archivos temporales
- Usa ffplay (parte de FFmpeg) para máxima compatibilidad
- Sin ventanas ni logs visuales (modo headless)
- Configuración optimizada para audio de Piper TTS

Uso:
    audio_bytes = synthesize_speech("Hola Radio IA", model_path)
    play_audio(audio_bytes)
"""

import subprocess
import logging
from typing import Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def play_audio(
    audio_data: bytes,
    sample_rate: int = 22050,
    channels: int = 1,
    volume: Optional[float] = None
) -> None:
    """
    Reproduce audio RAW PCM generado por Piper usando ffplay.
    
    Args:
        audio_data (bytes): Audio en formato RAW PCM (signed 16-bit little-endian)
        sample_rate (int): Frecuencia de muestreo en Hz (default: 22050)
        channels (int): Número de canales (1=mono, 2=estéreo) (default: 1)
        volume (Optional[float]): Volumen (0.0 a 1.0). None = volumen por defecto
    
    Returns:
        None
    
    Raises:
        No lanza excepciones, registra errores en el log
    
    Examples:
        >>> play_audio(audio_bytes)  # Reproducción básica
        >>> play_audio(audio_bytes, sample_rate=44100, volume=0.8)  # Personalizada
    """
    # Validar que hay audio para reproducir
    if not audio_data:
        logger.warning("⚠️  Audio vacío recibido, no se reproduce")
        return
    
    if len(audio_data) < 100:
        logger.warning("⚠️  Audio muy corto, posiblemente corrupto")
        return
    
    logger.info(f"🔊 Reproduciendo audio ({len(audio_data)} bytes, {sample_rate} Hz)...")
    
    try:
        # Construir comando ffplay
        command = [
            "ffplay",
            "-autoexit",              # Cerrar automáticamente al terminar
            "-nodisp",                # Sin ventana gráfica
            "-loglevel", "quiet",     # Sin logs
            "-f", "s16le",            # Formato: signed 16-bit little-endian PCM
            "-ar", str(sample_rate),  # Sample rate (frecuencia de muestreo)
            # Nota: No especificamos canales, ffplay los detecta automáticamente
        ]
        
        # Agregar control de volumen si se especifica
        if volume is not None:
            volume_db = max(0.0, min(1.0, volume))  # Clamp entre 0.0 y 1.0
            command.extend(["-volume", str(int(volume_db * 100))])
        
        # Leer desde stdin
        command.append("-")
        
        # Ejecutar ffplay
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,  # Suprimir salida estándar
            stderr=subprocess.DEVNULL   # Suprimir errores (modo silencioso)
        )
        
        # Enviar el audio al reproductor
        try:
            process.stdin.write(audio_data)
            process.stdin.flush()
            process.stdin.close()
        except BrokenPipeError:
            logger.warning("⚠️  Pipe cerrado inesperadamente durante escritura")
        
        # Esperar a que termine la reproducción
        try:
            return_code = process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            logger.warning("⚠️  Timeout esperando fin de reproducción")
            process.kill()
            return_code = -1
        
        if return_code == 0:
            logger.info("✅ Audio reproducido exitosamente")
        else:
            logger.warning(f"⚠️  ffplay terminó con código: {return_code}")
    
    except FileNotFoundError:
        logger.error("❌ ffplay no está instalado o no está en el PATH")
        logger.info("💡 Instala FFmpeg desde: https://ffmpeg.org/download.html")
    
    except BrokenPipeError:
        logger.warning("⚠️  Reproducción interrumpida (pipe roto)")
    
    except Exception as e:
        logger.error(f"❌ Error reproduciendo audio: {e}")


def play_audio_async(
    audio_data: bytes,
    sample_rate: int = 22050,
    channels: int = 1
) -> subprocess.Popen:
    """
    Reproduce audio de forma asíncrona (no bloqueante).
    Retorna el proceso para control externo.
    
    Args:
        audio_data (bytes): Audio en formato RAW PCM
        sample_rate (int): Frecuencia de muestreo en Hz (default: 22050)
        channels (int): Número de canales (default: 1)
    
    Returns:
        subprocess.Popen: Proceso de reproducción activo
    
    Note:
        El llamador es responsable de gestionar el proceso retornado
    """
    if not audio_data:
        logger.warning("⚠️  Audio vacío, no se reproduce")
        return None
    
    logger.info(f"🔊 Iniciando reproducción asíncrona ({len(audio_data)} bytes)...")
    
    try:
        command = [
            "ffplay",
            "-autoexit",
            "-nodisp",
            "-f", "s16le",
            "-ar", str(sample_rate),
            # Nota: No especificamos canales, ffplay los detecta automáticamente
            "-"
        ]
        
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Enviar audio
        try:
            process.stdin.write(audio_data)
            process.stdin.flush()
            process.stdin.close()
        except BrokenPipeError:
            logger.warning("⚠️  Error enviando audio")
        
        logger.info("✅ Reproducción asíncrona iniciada")
        return process
    
    except Exception as e:
        logger.error(f"❌ Error en reproducción asíncrona: {e}")
        return None


def check_ffplay_available() -> bool:
    """
    Verifica si ffplay está instalado y disponible en el sistema.
    
    Returns:
        bool: True si ffplay está disponible, False en caso contrario
    """
    try:
        result = subprocess.run(
            ["ffplay", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        available = result.returncode == 0
        if available:
            # Extraer versión de la primera línea
            output = result.stdout.decode("utf-8", errors="ignore")
            version_line = output.split('\n')[0] if output else "versión desconocida"
            logger.info(f"✅ ffplay disponible: {version_line}")
        return available
    except FileNotFoundError:
        logger.error("❌ ffplay no está instalado")
        return False
    except Exception as e:
        logger.error(f"❌ Error verificando ffplay: {e}")
        return False


def stop_audio(process: subprocess.Popen) -> None:
    """
    Detiene un proceso de reproducción activo.
    
    Args:
        process (subprocess.Popen): Proceso de ffplay a detener
    """
    if process and process.poll() is None:
        try:
            process.terminate()
            process.wait(timeout=2)
            logger.info("⏹️  Reproducción detenida")
        except subprocess.TimeoutExpired:
            process.kill()
            logger.warning("⚠️  Reproducción forzada a terminar")
        except Exception as e:
            logger.error(f"❌ Error deteniendo reproducción: {e}")


# Configuraciones de audio predefinidas para diferentes calidades
# Pueden ser usadas según el modelo de Piper y las necesidades
AUDIO_PRESETS = {
    "piper_default": {
        "sample_rate": 22050,
        "channels": 1,
        "description": "Configuración estándar para modelos Piper"
    },
    "high_quality": {
        "sample_rate": 44100,
        "channels": 1,
        "description": "Alta calidad (si el modelo lo soporta)"
    },
    "low_bandwidth": {
        "sample_rate": 16000,
        "channels": 1,
        "description": "Baja calidad para ahorro de recursos"
    }
}


def get_preset(preset_name: str) -> dict:
    """
    Obtiene una configuración de audio predefinida.
    
    Args:
        preset_name (str): Nombre del preset (ej: "piper_default")
    
    Returns:
        dict: Configuración de audio o preset por defecto si no existe
    """
    preset = AUDIO_PRESETS.get(preset_name, AUDIO_PRESETS["piper_default"])
    logger.info(f"📋 Usando preset '{preset_name}': {preset['description']}")
    return preset
