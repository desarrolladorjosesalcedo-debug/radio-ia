"""
piper_tts.py
Cliente para el sistema de síntesis de voz Piper TTS.

Este módulo convierte texto en audio utilizando Piper TTS de forma local.
Genera audio en formato RAW PCM que puede ser reproducido directamente.

Características:
- Síntesis de voz totalmente local (sin APIs externas)
- Soporte para múltiples modelos de voz
- Manejo robusto de errores
- Audio en formato RAW PCM para reproducción inmediata

Uso:
    audio_bytes = synthesize_speech("Hola mundo", "models/piper/es_ES-model.onnx")
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def synthesize_speech(
    text: str,
    model_path: str,
    speaker_id: Optional[int] = None,
    length_scale: float = 1.0,
    noise_scale: float = 0.667,
    noise_w: float = 0.8
) -> bytes:
    """
    Convierte texto en audio usando Piper TTS.
    
    Args:
        text (str): Texto a sintetizar en voz
        model_path (str): Ruta al archivo .onnx del modelo de Piper
        speaker_id (Optional[int]): ID del hablante para modelos multi-speaker
        length_scale (float): Velocidad de habla (1.0 = normal, <1.0 = más rápido, >1.0 = más lento)
        noise_scale (float): Variación en la entonación (default: 0.667)
        noise_w (float): Variación en la duración de fonemas (default: 0.8)
    
    Returns:
        bytes: Audio en formato RAW PCM (16-bit, mono, 22050 Hz)
               Retorna bytes vacíos en caso de error
    
    Examples:
        >>> audio = synthesize_speech("Bienvenidos a Radio IA", "models/piper/voice.onnx")
        >>> # audio contiene los bytes del audio RAW PCM
    """
    # Validar que el modelo existe
    model_file = Path(model_path)
    if not model_file.exists():
        logger.error(f"❌ Modelo Piper no encontrado: {model_path}")
        logger.info(f"💡 Asegúrate de descargar el modelo y colocarlo en: {model_path}")
        return b""
    
    # Validar que hay texto para sintetizar
    if not text or not text.strip():
        logger.warning("⚠️  Texto vacío, no hay nada que sintetizar")
        return b""
    
    logger.info(f"🎤 Sintetizando {len(text)} caracteres con Piper...")
    
    try:
        # Construir comando base
        command = [
            "piper",
            "--model", str(model_file),
            "--output_raw"  # Salida en formato RAW PCM
        ]
        
        # Agregar parámetros opcionales
        if speaker_id is not None:
            command.extend(["--speaker", str(speaker_id)])
        
        if length_scale != 1.0:
            command.extend(["--length_scale", str(length_scale)])
        
        if noise_scale != 0.667:
            command.extend(["--noise_scale", str(noise_scale)])
        
        if noise_w != 0.8:
            command.extend(["--noise_w", str(noise_w)])
        
        # Ejecutar Piper
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Enviar texto y obtener audio
        audio_data, error_output = process.communicate(
            input=text.encode("utf-8"),
            timeout=30  # Timeout de 30 segundos
        )
        
        # Verificar si hubo errores
        if error_output:
            error_msg = error_output.decode('utf-8', errors='ignore').strip()
            if error_msg and "warning" not in error_msg.lower():
                logger.warning(f"⚠️  Piper stderr: {error_msg}")
        
        # Verificar código de retorno
        if process.returncode != 0:
            logger.error(f"❌ Piper terminó con código de error: {process.returncode}")
            return b""
        
        # Validar que se generó audio
        if not audio_data or len(audio_data) < 100:
            logger.error("❌ Piper no generó audio válido")
            return b""
        
        logger.info(f"✅ Audio generado exitosamente ({len(audio_data)} bytes)")
        return audio_data
    
    except subprocess.TimeoutExpired:
        logger.error("⏱️  Timeout al generar audio con Piper")
        process.kill()
        return b""
    
    except FileNotFoundError:
        logger.error("❌ Piper no está instalado o no está en el PATH")
        logger.info("💡 Instala Piper desde: https://github.com/rhasspy/piper")
        return b""
    
    except Exception as e:
        logger.error(f"❌ Error al generar voz con Piper: {e}")
        return b""


def check_piper_available() -> bool:
    """
    Verifica si Piper TTS está instalado y disponible en el sistema.
    
    Returns:
        bool: True si Piper está disponible, False en caso contrario
    """
    try:
        result = subprocess.run(
            ["piper", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        available = result.returncode == 0
        if available:
            version = result.stdout.decode("utf-8", errors="ignore").strip()
            logger.info(f"✅ Piper TTS disponible: {version}")
        return available
    except FileNotFoundError:
        logger.error("❌ Piper no está instalado")
        return False
    except Exception as e:
        logger.error(f"❌ Error verificando Piper: {e}")
        return False


def validate_model(model_path: str) -> bool:
    """
    Valida que un modelo de Piper existe y tiene el formato correcto.
    
    Args:
        model_path (str): Ruta al archivo del modelo
    
    Returns:
        bool: True si el modelo es válido, False en caso contrario
    """
    model_file = Path(model_path)
    
    # Verificar que existe
    if not model_file.exists():
        logger.error(f"❌ Modelo no encontrado: {model_path}")
        return False
    
    # Verificar extensión .onnx
    if model_file.suffix.lower() != ".onnx":
        logger.error(f"❌ El modelo debe ser un archivo .onnx: {model_path}")
        return False
    
    # Verificar que tiene archivo .json asociado (configuración del modelo)
    json_file = model_file.with_suffix(".onnx.json")
    if not json_file.exists():
        logger.warning(f"⚠️  Falta archivo de configuración: {json_file}")
        logger.info("💡 El modelo funcionará, pero es recomendable tener el .json")
    
    logger.info(f"✅ Modelo válido: {model_path}")
    return True


def get_model_info(model_path: str) -> dict:
    """
    Obtiene información sobre un modelo de Piper desde su archivo .json.
    
    Args:
        model_path (str): Ruta al archivo .onnx del modelo
    
    Returns:
        dict: Información del modelo (idioma, calidad, sample_rate, etc.)
    """
    import json
    
    json_file = Path(model_path).with_suffix(".onnx.json")
    
    if not json_file.exists():
        logger.warning(f"⚠️  Archivo de configuración no encontrado: {json_file}")
        return {}
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            info = json.load(f)
        logger.info(f"📋 Información del modelo cargada desde {json_file}")
        return info
    except Exception as e:
        logger.error(f"❌ Error leyendo información del modelo: {e}")
        return {}


# Configuración de audio por defecto para Piper
# Estos valores son estándar para la mayoría de modelos de Piper
AUDIO_CONFIG = {
    "sample_rate": 22050,  # Hz
    "sample_width": 2,      # bytes (16-bit)
    "channels": 1,          # mono
    "format": "PCM"         # Raw PCM
}
