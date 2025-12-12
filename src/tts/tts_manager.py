"""
tts_manager.py
Gestor unificado de múltiples proveedores TTS.

Gestiona:
- Microsoft Edge TTS (principal)
- Piper TTS (local)
- Google TTS (fallback)
- [Preparado para] ElevenLabs
- [Preparado para] OpenAI TTS

Características:
- Sistema de fallback automático
- Caché inteligente
- Post-procesamiento opcional
- Soporte SSML
- Estadísticas de uso

Uso:
    manager = TTSManager()
    audio = manager.synthesize("Hola mundo", provider="edge")
"""

import logging
from typing import Optional, Dict, Any, List
from enum import Enum

# Importar módulos TTS existentes
from tts.edge_tts_client import synthesize_speech_edge, check_edge_tts_available
from tts.piper_tts import synthesize_speech as synthesize_piper, check_piper_available
from tts.gtts_client import synthesize_speech_gtts, check_gtts_available

# Importar nuevos módulos
from tts.cache_manager import get_audio_cache
from tts.audio_processor import get_audio_processor
from tts.ssml_builder import SSMLBuilder, create_enhanced_text

logger = logging.getLogger(__name__)


class TTSProvider(Enum):
    """Proveedores TTS disponibles."""
    EDGE = "edge"
    PIPER = "piper"
    GOOGLE = "gtts"
    ELEVENLABS = "elevenlabs"  # Futuro
    OPENAI = "openai"  # Futuro


class TTSManager:
    """Gestor unificado de Text-to-Speech."""
    
    def __init__(self, 
                 use_cache: bool = True,
                 use_processing: bool = True,
                 use_ssml: bool = False,
                 fallback_chain: Optional[List[str]] = None):
        """
        Inicializa el gestor TTS.
        
        Args:
            use_cache (bool): Activar sistema de caché
            use_processing (bool): Activar post-procesamiento
            use_ssml (bool): Usar SSML por defecto
            fallback_chain (List[str]): Orden de fallback (default: edge → piper → google)
        """
        self.use_cache = use_cache
        self.use_processing = use_processing
        self.use_ssml = use_ssml
        
        # Cadena de fallback por defecto
        self.fallback_chain = fallback_chain or ["edge", "piper", "gtts"]
        
        # Inicializar componentes
        self.cache = get_audio_cache() if use_cache else None
        self.processor = get_audio_processor() if use_processing else None
        
        # Verificar disponibilidad de proveedores
        self.available_providers = self._check_providers()
        
        # Estadísticas de uso
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "by_provider": {provider: 0 for provider in self.fallback_chain},
            "errors": 0
        }
        
        logger.info(f"🎙️  TTS Manager inicializado")
        logger.info(f"   Proveedores disponibles: {list(self.available_providers.keys())}")
        logger.info(f"   Caché: {'Activado' if use_cache else 'Desactivado'}")
        logger.info(f"   Post-procesamiento: {'Activado' if use_processing else 'Desactivado'}")
    
    def _check_providers(self) -> Dict[str, bool]:
        """
        Verifica qué proveedores están disponibles.
        
        Returns:
            Dict[str, bool]: Estado de cada proveedor
        """
        providers = {
            "edge": check_edge_tts_available(),
            "piper": check_piper_available(),
            "gtts": check_gtts_available(),
            "elevenlabs": False,  # No implementado aún
            "openai": False  # No implementado aún
        }
        
        return {k: v for k, v in providers.items() if v}
    
    def synthesize(self,
                   text: str,
                   provider: str = "auto",
                   voice: Optional[str] = None,
                   style: str = "standard",
                   use_cache: Optional[bool] = None,
                   use_processing: Optional[bool] = None,
                   **kwargs) -> bytes:
        """
        Sintetiza texto a voz usando el proveedor especificado.
        
        Args:
            text (str): Texto a sintetizar
            provider (str): Proveedor TTS ("auto" usa fallback chain)
            voice (str): Voz específica a usar
            style (str): Estilo SSML (standard/podcast/audiobook/news/storytelling)
            use_cache (bool): Anular configuración global de caché
            use_processing (bool): Anular configuración global de procesamiento
            **kwargs: Parámetros adicionales para el proveedor
        
        Returns:
            bytes: Audio en formato RAW PCM
        """
        self.stats["total_requests"] += 1
        
        # Validar texto
        if not text or not text.strip():
            logger.warning("⚠️  Texto vacío, no se puede sintetizar")
            return b""
        
        # Determinar configuración
        _use_cache = use_cache if use_cache is not None else self.use_cache
        _use_processing = use_processing if use_processing is not None else self.use_processing
        
        # Generar clave de caché
        cache_params = {
            "provider": provider,
            "voice": voice or "default",
            "style": style,
            **kwargs
        }
        
        # Intentar obtener del caché
        if _use_cache and self.cache:
            cached_audio = self.cache.get(text, **cache_params)
            if cached_audio:
                self.stats["cache_hits"] += 1
                logger.info(f"⚡ Audio recuperado del caché ({len(cached_audio)} bytes)")
                return cached_audio
            self.stats["cache_misses"] += 1
        
        # Aplicar SSML si está activado y el proveedor lo soporta
        processed_text = text
        if self.use_ssml and provider in ["edge", "auto"]:
            processed_text = create_enhanced_text(text, style)
            logger.debug(f"📝 SSML aplicado (estilo: {style})")
        
        # Determinar lista de proveedores a intentar
        if provider == "auto":
            providers_to_try = self.fallback_chain
        else:
            providers_to_try = [provider] + [p for p in self.fallback_chain if p != provider]
        
        # Intentar sintetizar con cada proveedor
        audio_data = None
        used_provider = None
        
        for prov in providers_to_try:
            if prov not in self.available_providers:
                logger.debug(f"⏭️  Proveedor {prov} no disponible, saltando")
                continue
            
            try:
                logger.info(f"🎤 Sintetizando con {prov.upper()}...")
                
                if prov == "edge":
                    audio_data = self._synthesize_edge(processed_text, voice, **kwargs)
                elif prov == "piper":
                    audio_data = self._synthesize_piper(text, voice, **kwargs)
                elif prov == "gtts":
                    audio_data = self._synthesize_gtts(text, **kwargs)
                elif prov == "elevenlabs":
                    audio_data = self._synthesize_elevenlabs(text, voice, **kwargs)
                elif prov == "openai":
                    audio_data = self._synthesize_openai(text, voice, **kwargs)
                
                if audio_data and len(audio_data) > 100:
                    used_provider = prov
                    self.stats["by_provider"][prov] += 1
                    logger.info(f"✅ Audio generado con {prov.upper()} ({len(audio_data)} bytes)")
                    break
            
            except Exception as e:
                logger.error(f"❌ Error con {prov}: {e}")
                self.stats["errors"] += 1
        
        # Si no se pudo generar audio con ningún proveedor
        if not audio_data or len(audio_data) < 100:
            logger.error("❌ No se pudo generar audio con ningún proveedor")
            return b""
        
        # Aplicar post-procesamiento
        if _use_processing and self.processor:
            try:
                audio_data = self.processor.process(audio_data)
                logger.debug("✨ Post-procesamiento aplicado")
            except Exception as e:
                logger.warning(f"⚠️  Error en post-procesamiento: {e}")
        
        # Guardar en caché
        if _use_cache and self.cache:
            cache_params["provider"] = used_provider
            self.cache.set(text, audio_data, **cache_params)
        
        return audio_data
    
    def _synthesize_edge(self, text: str, voice: Optional[str], **kwargs) -> bytes:
        """Sintetiza con Microsoft Edge TTS."""
        voice = voice or "es-MX-DaliaNeural"
        return synthesize_speech_edge(text, voice=voice, **kwargs)
    
    def _synthesize_piper(self, text: str, voice: Optional[str], **kwargs) -> bytes:
        """Sintetiza con Piper TTS."""
        model_path = kwargs.get("model_path", "models/piper/es_ES-davefx-medium.onnx")
        return synthesize_piper(text, model_path=model_path)
    
    def _synthesize_gtts(self, text: str, **kwargs) -> bytes:
        """Sintetiza con Google TTS."""
        return synthesize_speech_gtts(text, **kwargs)
    
    def _synthesize_elevenlabs(self, text: str, voice: Optional[str], **kwargs) -> bytes:
        """
        Sintetiza con ElevenLabs (preparado para implementación futura).
        
        Implementar:
        1. pip install elevenlabs
        2. from elevenlabs import generate, set_api_key
        3. set_api_key("tu-api-key")
        4. audio = generate(text=text, voice=voice or "Bella")
        5. Convertir audio a formato RAW PCM 22050Hz
        """
        logger.warning("⚠️  ElevenLabs no implementado aún")
        raise NotImplementedError("ElevenLabs TTS no implementado")
    
    def _synthesize_openai(self, text: str, voice: Optional[str], **kwargs) -> bytes:
        """
        Sintetiza con OpenAI TTS (preparado para implementación futura).
        
        Implementar:
        1. pip install openai
        2. from openai import OpenAI
        3. client = OpenAI(api_key="tu-api-key")
        4. response = client.audio.speech.create(
               model="tts-1",
               voice=voice or "alloy",
               input=text
           )
        5. Convertir audio a formato RAW PCM 22050Hz
        """
        logger.warning("⚠️  OpenAI TTS no implementado aún")
        raise NotImplementedError("OpenAI TTS no implementado")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de uso del gestor.
        
        Returns:
            Dict: Estadísticas completas
        """
        cache_stats = self.cache.get_stats() if self.cache else {}
        
        stats = {
            **self.stats,
            "cache_hit_rate": (self.stats["cache_hits"] / self.stats["total_requests"] * 100) 
                              if self.stats["total_requests"] > 0 else 0,
            "cache_stats": cache_stats
        }
        
        return stats
    
    def print_stats(self):
        """Imprime estadísticas de uso."""
        stats = self.get_stats()
        logger.info("📊 Estadísticas TTS Manager:")
        logger.info(f"   Total de solicitudes: {stats['total_requests']}")
        logger.info(f"   Aciertos de caché: {stats['cache_hits']} ({stats['cache_hit_rate']:.1f}%)")
        logger.info(f"   Fallos de caché: {stats['cache_misses']}")
        logger.info(f"   Errores: {stats['errors']}")
        logger.info(f"   Uso por proveedor: {stats['by_provider']}")
        
        if self.cache:
            self.cache.print_stats()
    
    def clear_cache(self):
        """Limpia el caché de audio."""
        if self.cache:
            self.cache.clear_all()
            logger.info("🗑️  Caché limpiado")


# Instancia global (singleton)
_global_manager = None

def get_tts_manager(**kwargs) -> TTSManager:
    """
    Obtiene la instancia global del gestor TTS.
    
    Args:
        **kwargs: Parámetros para inicializar el manager
    
    Returns:
        TTSManager: Instancia del gestor
    """
    global _global_manager
    if _global_manager is None:
        _global_manager = TTSManager(**kwargs)
    return _global_manager


# Ejemplo de uso
if __name__ == "__main__":
    # Crear gestor con todas las funcionalidades
    manager = TTSManager(
        use_cache=True,
        use_processing=True,
        use_ssml=True,
        fallback_chain=["edge", "piper", "gtts"]
    )
    
    # Sintetizar texto
    audio = manager.synthesize(
        "Hola, bienvenidos a Radio IA. Este es un ejemplo de síntesis de voz mejorada.",
        provider="auto",
        voice="es-MX-DaliaNeural",
        style="podcast"
    )
    
    print(f"Audio generado: {len(audio)} bytes")
    
    # Ver estadísticas
    manager.print_stats()
