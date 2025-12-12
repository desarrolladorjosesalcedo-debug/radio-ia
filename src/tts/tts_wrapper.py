"""
tts_wrapper.py
Wrapper de compatibilidad para integrar el nuevo TTS Manager con el código existente.

Mantiene la API existente pero usa el nuevo sistema internamente.
"""

import logging
from typing import Optional
from tts.tts_manager import get_tts_manager

logger = logging.getLogger(__name__)

# Instancia global del manager
_manager = None


def init_tts_manager(config: dict):
    """
    Inicializa el TTS Manager con configuración.
    
    Args:
        config (dict): Configuración de TTS desde settings.yaml
    """
    global _manager
    
    tts_config = config.get("tts", {})
    
    # Verificar si el nuevo sistema está activado
    use_manager = tts_config.get("use_tts_manager", True)
    
    if use_manager:
        _manager = get_tts_manager(
            use_cache=tts_config.get("use_cache", True),
            use_processing=tts_config.get("use_processing", True),
            use_ssml=tts_config.get("use_ssml", False),
            fallback_chain=tts_config.get("fallback_chain", ["edge", "piper", "gtts"])
        )
        logger.info("✨ TTS Manager avanzado activado")
    else:
        _manager = None
        logger.info("📻 Usando sistema TTS clásico")


def synthesize_with_manager(
    text: str,
    provider: str = "edge",
    voice: Optional[str] = None,
    config: Optional[dict] = None
) -> bytes:
    """
    Sintetiza texto usando el TTS Manager o el sistema clásico.
    
    Compatibilidad total con el código existente.
    
    Args:
        text (str): Texto a sintetizar
        provider (str): Proveedor TTS
        voice (str): Voz a usar
        config (dict): Configuración completa
    
    Returns:
        bytes: Audio en formato RAW PCM
    """
    global _manager
    
    # Si no hay manager inicializado, usar sistema clásico
    if _manager is None:
        logger.debug("🔄 Usando sistema TTS clásico (fallback)")
        return _synthesize_classic(text, provider, voice, config)
    
    # Usar TTS Manager avanzado
    tts_config = config.get("tts", {}) if config else {}
    style = tts_config.get("ssml_style", "standard")
    
    try:
        audio = _manager.synthesize(
            text=text,
            provider=provider,
            voice=voice,
            style=style
        )
        return audio
    except Exception as e:
        logger.error(f"❌ Error con TTS Manager: {e}")
        logger.info("🔄 Fallback a sistema clásico")
        return _synthesize_classic(text, provider, voice, config)


def _synthesize_classic(
    text: str,
    provider: str,
    voice: Optional[str],
    config: Optional[dict]
) -> bytes:
    """
    Sistema clásico de síntesis (compatibilidad).
    
    Args:
        text (str): Texto a sintetizar
        provider (str): Proveedor TTS
        voice (str): Voz a usar
        config (dict): Configuración
    
    Returns:
        bytes: Audio en formato RAW PCM
    """
    if provider == "edge":
        from tts.edge_tts_client import synthesize_speech_edge
        return synthesize_speech_edge(text, voice=voice or "es-MX-DaliaNeural")
    
    elif provider == "piper":
        from tts.piper_tts import synthesize_speech
        model_path = config.get("tts", {}).get("model_path") if config else None
        return synthesize_speech(text, model_path=model_path or "models/piper/es_ES-davefx-medium.onnx")
    
    elif provider == "gtts":
        from tts.gtts_client import synthesize_speech_gtts
        return synthesize_speech_gtts(text)
    
    else:
        logger.warning(f"⚠️  Proveedor desconocido '{provider}', usando Edge TTS")
        from tts.edge_tts_client import synthesize_speech_edge
        return synthesize_speech_edge(text, voice=voice or "es-MX-DaliaNeural")


def get_manager_stats() -> dict:
    """
    Obtiene estadísticas del TTS Manager.
    
    Returns:
        dict: Estadísticas o None si no está activado
    """
    global _manager
    if _manager:
        return _manager.get_stats()
    return None


def print_manager_stats():
    """Imprime estadísticas del TTS Manager."""
    global _manager
    if _manager:
        _manager.print_stats()
    else:
        logger.info("📻 TTS Manager no activado")


def clear_cache():
    """Limpia el caché de audio."""
    global _manager
    if _manager:
        _manager.clear_cache()
    else:
        logger.warning("⚠️  TTS Manager no activado, no hay caché que limpiar")
