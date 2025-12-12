"""
audio_stream_manager.py
Gestor de streaming de audio para Radio IA
Permite transmitir audio en tiempo real sin reproducción local
"""

import logging
import threading
import queue
import time
from typing import Optional, Generator
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioStreamManager:
    """
    Gestiona el streaming de audio en tiempo real
    """
    def __init__(self):
        self.audio_queue = queue.Queue(maxsize=10)
        self.is_streaming = False
        self.current_segment = None
        self._lock = threading.Lock()
        
    def start_streaming(self):
        """Inicia el streaming"""
        with self._lock:
            self.is_streaming = True
            logger.info("🎵 Streaming de audio iniciado")
    
    def stop_streaming(self):
        """Detiene el streaming"""
        with self._lock:
            self.is_streaming = False
            # Limpiar cola
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except queue.Empty:
                    break
            logger.info("⏹️  Streaming de audio detenido")
    
    def add_audio(self, audio_bytes: bytes, metadata: dict = None):
        """
        Añade audio a la cola de streaming
        
        Args:
            audio_bytes: Audio en formato bytes
            metadata: Metadata opcional (tema, duración, etc.)
        """
        if not self.is_streaming:
            logger.warning("⚠️  Intento de añadir audio sin streaming activo")
            return False
        
        try:
            segment_info = {
                "audio": audio_bytes,
                "metadata": metadata or {},
                "timestamp": time.time()
            }
            
            # Añadir a la cola (bloqueante si está llena)
            self.audio_queue.put(segment_info, timeout=5.0)
            logger.info(f"✅ Segmento añadido a streaming (cola: {self.audio_queue.qsize()})")
            return True
        
        except queue.Full:
            logger.error("❌ Cola de streaming llena - descartando segmento")
            return False
    
    def get_audio_stream(self) -> Generator[bytes, None, None]:
        """
        Generador de streaming de audio
        
        Yields:
            bytes: Chunks de audio para streaming HTTP
        """
        logger.info("🎧 Cliente conectado al stream")
        
        try:
            while self.is_streaming:
                try:
                    # Obtener siguiente segmento (timeout 1s)
                    segment_info = self.audio_queue.get(timeout=1.0)
                    audio_bytes = segment_info["audio"]
                    
                    # Enviar metadata como headers HTTP personalizados
                    # (El cliente puede leerlos para mostrar "Ahora: tema X")
                    metadata = segment_info.get("metadata", {})
                    if metadata:
                        logger.info(f"📻 Streaming: {metadata.get('topic', 'Desconocido')}")
                    
                    # Yield del audio en chunks (para streaming progresivo)
                    chunk_size = 4096
                    for i in range(0, len(audio_bytes), chunk_size):
                        chunk = audio_bytes[i:i+chunk_size]
                        yield chunk
                    
                    self.audio_queue.task_done()
                
                except queue.Empty:
                    # No hay audio disponible, enviar silencio pequeño
                    # (mantiene conexión viva)
                    continue
        
        except GeneratorExit:
            logger.info("🔌 Cliente desconectado del stream")
        
        except Exception as e:
            logger.error(f"❌ Error en streaming: {e}")
    
    def get_current_info(self) -> dict:
        """
        Obtiene información del segmento actual
        
        Returns:
            dict: Información del segmento en reproducción
        """
        with self._lock:
            if self.current_segment:
                return {
                    "is_streaming": self.is_streaming,
                    "queue_size": self.audio_queue.qsize(),
                    "current_topic": self.current_segment.get("metadata", {}).get("topic", "Desconocido"),
                    "timestamp": self.current_segment.get("timestamp", 0)
                }
            else:
                return {
                    "is_streaming": self.is_streaming,
                    "queue_size": self.audio_queue.qsize(),
                    "current_topic": None,
                    "timestamp": None
                }


# Instancia global del stream manager
stream_manager = AudioStreamManager()
