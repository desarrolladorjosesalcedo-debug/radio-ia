"""
cache_manager.py
Sistema de caché inteligente para audios generados por TTS.

Características:
- Almacenamiento basado en hash del texto
- Evita regeneración de audios idénticos
- Limpieza automática de caché antigua
- Soporte para múltiples proveedores TTS
- Compresión opcional para ahorrar espacio

Uso:
    cache = AudioCache()
    audio = cache.get("Hola mundo", provider="edge", voice="es-MX-DaliaNeural")
    if audio is None:
        audio = generate_audio("Hola mundo")
        cache.set("Hola mundo", audio, provider="edge", voice="es-MX-DaliaNeural")
"""

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any
import gzip

logger = logging.getLogger(__name__)


class AudioCache:
    """Gestor de caché para audios TTS."""
    
    def __init__(self, cache_dir: str = "cache/audio", max_age_days: int = 30, compress: bool = True):
        """
        Inicializa el gestor de caché.
        
        Args:
            cache_dir (str): Directorio para almacenar caché
            max_age_days (int): Días antes de limpiar archivos antiguos
            compress (bool): Si True, comprime archivos con gzip
        """
        self.cache_dir = Path(cache_dir)
        self.max_age_seconds = max_age_days * 24 * 60 * 60
        self.compress = compress
        
        # Crear directorio si no existe
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Archivo de índice para metadata
        self.index_file = self.cache_dir / "cache_index.json"
        self.index = self._load_index()
        
        logger.info(f"💾 Caché de audio inicializado: {self.cache_dir}")
    
    def _load_index(self) -> Dict[str, Any]:
        """
        Carga el índice de caché desde disco.
        
        Returns:
            Dict: Índice de caché con metadatos
        """
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Error cargando índice de caché: {e}")
        
        return {}
    
    def _save_index(self):
        """Guarda el índice de caché a disco."""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Error guardando índice de caché: {e}")
    
    def _generate_key(self, text: str, provider: str, voice: str, **kwargs) -> str:
        """
        Genera una clave única para el caché basada en texto y parámetros.
        
        Args:
            text (str): Texto del audio
            provider (str): Proveedor TTS (edge, piper, google, etc.)
            voice (str): Voz utilizada
            **kwargs: Parámetros adicionales (rate, pitch, etc.)
        
        Returns:
            str: Hash SHA256 como clave
        """
        # Crear string con todos los parámetros
        params = {
            "text": text.strip().lower(),
            "provider": provider,
            "voice": voice,
            **kwargs
        }
        
        # Serializar y hashear
        params_str = json.dumps(params, sort_keys=True)
        hash_obj = hashlib.sha256(params_str.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def get(self, text: str, provider: str = "edge", voice: str = "es-MX-DaliaNeural", 
            **kwargs) -> Optional[bytes]:
        """
        Obtiene audio del caché si existe.
        
        Args:
            text (str): Texto del audio
            provider (str): Proveedor TTS
            voice (str): Voz utilizada
            **kwargs: Parámetros adicionales
        
        Returns:
            Optional[bytes]: Audio en bytes o None si no existe en caché
        """
        cache_key = self._generate_key(text, provider, voice, **kwargs)
        
        # Verificar si existe en índice
        if cache_key not in self.index:
            return None
        
        metadata = self.index[cache_key]
        cache_file = self.cache_dir / f"{cache_key}.{'raw.gz' if self.compress else 'raw'}"
        
        # Verificar si el archivo existe
        if not cache_file.exists():
            logger.warning(f"⚠️  Entrada de caché existe en índice pero archivo falta: {cache_key}")
            del self.index[cache_key]
            self._save_index()
            return None
        
        # Verificar edad del archivo
        file_age = time.time() - metadata.get('timestamp', 0)
        if file_age > self.max_age_seconds:
            logger.info(f"🗑️  Caché expirado: {cache_key[:8]}... ({file_age / 86400:.1f} días)")
            self._delete_entry(cache_key)
            return None
        
        # Leer audio
        try:
            if self.compress:
                with gzip.open(cache_file, 'rb') as f:
                    audio_data = f.read()
            else:
                with open(cache_file, 'rb') as f:
                    audio_data = f.read()
            
            # Actualizar estadísticas
            metadata['hits'] = metadata.get('hits', 0) + 1
            metadata['last_accessed'] = time.time()
            self._save_index()
            
            logger.info(f"✅ Audio recuperado del caché: {cache_key[:8]}... ({len(audio_data)} bytes, {metadata['hits']} hits)")
            return audio_data
        
        except Exception as e:
            logger.error(f"❌ Error leyendo caché: {e}")
            self._delete_entry(cache_key)
            return None
    
    def set(self, text: str, audio_data: bytes, provider: str = "edge", 
            voice: str = "es-MX-DaliaNeural", **kwargs):
        """
        Guarda audio en el caché.
        
        Args:
            text (str): Texto del audio
            audio_data (bytes): Datos de audio en bytes
            provider (str): Proveedor TTS
            voice (str): Voz utilizada
            **kwargs: Parámetros adicionales
        """
        if not audio_data:
            logger.warning("⚠️  Intentando cachear audio vacío")
            return
        
        cache_key = self._generate_key(text, provider, voice, **kwargs)
        cache_file = self.cache_dir / f"{cache_key}.{'raw.gz' if self.compress else 'raw'}"
        
        try:
            # Guardar audio
            if self.compress:
                with gzip.open(cache_file, 'wb', compresslevel=6) as f:
                    f.write(audio_data)
            else:
                with open(cache_file, 'wb') as f:
                    f.write(audio_data)
            
            # Actualizar índice
            self.index[cache_key] = {
                'text_preview': text[:100],
                'provider': provider,
                'voice': voice,
                'size_bytes': len(audio_data),
                'timestamp': time.time(),
                'hits': 0,
                'last_accessed': time.time(),
                'params': kwargs
            }
            self._save_index()
            
            logger.info(f"💾 Audio cacheado: {cache_key[:8]}... ({len(audio_data)} bytes)")
        
        except Exception as e:
            logger.error(f"❌ Error guardando en caché: {e}")
    
    def _delete_entry(self, cache_key: str):
        """
        Elimina una entrada del caché.
        
        Args:
            cache_key (str): Clave de caché a eliminar
        """
        # Eliminar archivo
        for ext in ['.raw.gz', '.raw']:
            cache_file = self.cache_dir / f"{cache_key}{ext}"
            if cache_file.exists():
                cache_file.unlink()
        
        # Eliminar del índice
        if cache_key in self.index:
            del self.index[cache_key]
            self._save_index()
    
    def clean_old_entries(self):
        """Limpia entradas antiguas del caché."""
        current_time = time.time()
        keys_to_delete = []
        
        for cache_key, metadata in self.index.items():
            file_age = current_time - metadata.get('timestamp', 0)
            if file_age > self.max_age_seconds:
                keys_to_delete.append(cache_key)
        
        for cache_key in keys_to_delete:
            self._delete_entry(cache_key)
        
        if keys_to_delete:
            logger.info(f"🗑️  Limpiadas {len(keys_to_delete)} entradas antiguas del caché")
    
    def clear_all(self):
        """Limpia completamente el caché."""
        for cache_file in self.cache_dir.glob("*.raw*"):
            cache_file.unlink()
        
        self.index = {}
        self._save_index()
        logger.info("🗑️  Caché completamente limpiado")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del caché.
        
        Returns:
            Dict: Estadísticas del caché
        """
        total_entries = len(self.index)
        total_size = sum(m.get('size_bytes', 0) for m in self.index.values())
        total_hits = sum(m.get('hits', 0) for m in self.index.values())
        
        # Calcular tasa de aciertos (hits)
        total_accesses = sum(m.get('hits', 0) + 1 for m in self.index.values())
        hit_rate = (total_hits / total_accesses * 100) if total_accesses > 0 else 0
        
        # Agrupar por proveedor
        by_provider = {}
        for metadata in self.index.values():
            provider = metadata.get('provider', 'unknown')
            by_provider[provider] = by_provider.get(provider, 0) + 1
        
        return {
            'total_entries': total_entries,
            'total_size_mb': total_size / (1024 * 1024),
            'total_hits': total_hits,
            'hit_rate_percent': hit_rate,
            'by_provider': by_provider,
            'compression': self.compress
        }
    
    def print_stats(self):
        """Imprime estadísticas del caché."""
        stats = self.get_stats()
        logger.info("📊 Estadísticas del caché de audio:")
        logger.info(f"   Entradas totales: {stats['total_entries']}")
        logger.info(f"   Tamaño total: {stats['total_size_mb']:.2f} MB")
        logger.info(f"   Hits totales: {stats['total_hits']}")
        logger.info(f"   Tasa de aciertos: {stats['hit_rate_percent']:.1f}%")
        logger.info(f"   Compresión: {'Sí' if stats['compression'] else 'No'}")
        logger.info(f"   Por proveedor: {stats['by_provider']}")


# Instancia global de caché (singleton)
_global_cache = None

def get_audio_cache() -> AudioCache:
    """
    Obtiene la instancia global del caché de audio.
    
    Returns:
        AudioCache: Instancia del caché
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = AudioCache()
    return _global_cache


# Ejemplo de uso
if __name__ == "__main__":
    cache = AudioCache(cache_dir="cache/audio_test", max_age_days=7)
    
    # Simular guardado
    test_audio = b"fake_audio_data_12345"
    cache.set("Hola mundo", test_audio, provider="edge", voice="es-MX-DaliaNeural")
    
    # Simular recuperación
    cached_audio = cache.get("Hola mundo", provider="edge", voice="es-MX-DaliaNeural")
    print(f"Audio recuperado: {cached_audio == test_audio}")
    
    # Estadísticas
    cache.print_stats()
