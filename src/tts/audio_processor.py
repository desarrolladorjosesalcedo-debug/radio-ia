"""
audio_processor.py
Post-procesamiento de audio para mejorar calidad de TTS.

Características:
- Normalización de volumen
- Reducción de ruido
- Compresión dinámica ligera
- Filtro paso-alto (elimina frecuencias bajas)
- Análisis de calidad

Requiere: numpy, scipy (opcional)

Uso:
    processor = AudioProcessor()
    audio_mejorado = processor.process(audio_crudo)
"""

import logging
import struct
import numpy as np
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Procesador de audio para mejorar calidad de TTS."""
    
    def __init__(self, sample_rate: int = 22050):
        """
        Inicializa el procesador de audio.
        
        Args:
            sample_rate (int): Frecuencia de muestreo en Hz
        """
        self.sample_rate = sample_rate
        
        # Verificar si numpy está disponible
        try:
            import numpy as np
            self.numpy_available = True
        except ImportError:
            self.numpy_available = False
            logger.warning("⚠️  NumPy no disponible - post-procesamiento limitado")
    
    def bytes_to_array(self, audio_bytes: bytes) -> np.ndarray:
        """
        Convierte bytes de audio a array numpy.
        
        Args:
            audio_bytes (bytes): Audio en formato s16le (16-bit signed)
        
        Returns:
            np.ndarray: Array de audio normalizado [-1.0, 1.0]
        """
        # Convertir bytes a int16
        audio_int16 = np.frombuffer(audio_bytes, dtype=np.int16)
        
        # Normalizar a float32 [-1.0, 1.0]
        audio_float = audio_int16.astype(np.float32) / 32768.0
        
        return audio_float
    
    def array_to_bytes(self, audio_array: np.ndarray) -> bytes:
        """
        Convierte array numpy a bytes de audio.
        
        Args:
            audio_array (np.ndarray): Array de audio [-1.0, 1.0]
        
        Returns:
            bytes: Audio en formato s16le (16-bit signed)
        """
        # Limitar valores a [-1.0, 1.0]
        audio_clipped = np.clip(audio_array, -1.0, 1.0)
        
        # Convertir a int16
        audio_int16 = (audio_clipped * 32767).astype(np.int16)
        
        return audio_int16.tobytes()
    
    def normalize_volume(self, audio_array: np.ndarray, target_db: float = -20.0) -> np.ndarray:
        """
        Normaliza el volumen del audio a un nivel objetivo.
        
        Args:
            audio_array (np.ndarray): Audio de entrada
            target_db (float): Nivel objetivo en dB (-20 es estándar)
        
        Returns:
            np.ndarray: Audio normalizado
        """
        # Calcular RMS actual
        rms = np.sqrt(np.mean(audio_array ** 2))
        
        if rms < 1e-6:  # Audio casi silencioso
            logger.warning("⚠️  Audio muy silencioso, normalizando con precaución")
            return audio_array
        
        # Calcular ganancia necesaria
        current_db = 20 * np.log10(rms)
        gain_db = target_db - current_db
        gain_linear = 10 ** (gain_db / 20)
        
        # Limitar ganancia extrema
        gain_linear = np.clip(gain_linear, 0.1, 10.0)
        
        # Aplicar ganancia
        normalized = audio_array * gain_linear
        
        # Limitar a [-1.0, 1.0]
        normalized = np.clip(normalized, -1.0, 1.0)
        
        logger.debug(f"🔊 Normalización: {current_db:.1f}dB → {target_db:.1f}dB (ganancia: {gain_db:.1f}dB)")
        
        return normalized
    
    def apply_compressor(self, audio_array: np.ndarray, 
                        threshold: float = 0.7, 
                        ratio: float = 2.0) -> np.ndarray:
        """
        Aplica compresión dinámica ligera.
        
        Args:
            audio_array (np.ndarray): Audio de entrada
            threshold (float): Umbral de compresión (0.0-1.0)
            ratio (float): Ratio de compresión (1.0 = sin compresión)
        
        Returns:
            np.ndarray: Audio comprimido
        """
        # Obtener envolvente del audio
        abs_audio = np.abs(audio_array)
        
        # Aplicar compresión solo a valores sobre el umbral
        mask = abs_audio > threshold
        
        # Calcular ganancia de compresión
        excess = abs_audio[mask] - threshold
        compressed_excess = excess / ratio
        
        # Aplicar compresión manteniendo la polaridad
        compressed = audio_array.copy()
        compressed[mask] = np.sign(audio_array[mask]) * (threshold + compressed_excess)
        
        logger.debug(f"🎚️  Compresión aplicada: threshold={threshold}, ratio={ratio}")
        
        return compressed
    
    def apply_highpass_filter(self, audio_array: np.ndarray, cutoff_hz: float = 80.0) -> np.ndarray:
        """
        Aplica filtro paso-alto para eliminar frecuencias bajas (ruido).
        
        Args:
            audio_array (np.ndarray): Audio de entrada
            cutoff_hz (float): Frecuencia de corte en Hz
        
        Returns:
            np.ndarray: Audio filtrado
        """
        try:
            from scipy import signal
        except ImportError:
            logger.warning("⚠️  SciPy no disponible - filtro paso-alto omitido")
            return audio_array
        
        # Diseñar filtro Butterworth
        nyquist = self.sample_rate / 2
        normalized_cutoff = cutoff_hz / nyquist
        
        if normalized_cutoff >= 1.0:
            logger.warning(f"⚠️  Frecuencia de corte inválida: {cutoff_hz}Hz")
            return audio_array
        
        b, a = signal.butter(2, normalized_cutoff, btype='high')
        
        # Aplicar filtro
        filtered = signal.filtfilt(b, a, audio_array)
        
        logger.debug(f"🎛️  Filtro paso-alto aplicado: {cutoff_hz}Hz")
        
        return filtered
    
    def remove_silence(self, audio_array: np.ndarray, 
                      threshold: float = 0.01, 
                      min_silence_ms: int = 500) -> np.ndarray:
        """
        Elimina silencios prolongados al inicio y final.
        
        Args:
            audio_array (np.ndarray): Audio de entrada
            threshold (float): Umbral de silencio
            min_silence_ms (int): Duración mínima de silencio a eliminar
        
        Returns:
            np.ndarray: Audio sin silencios
        """
        # Calcular ventana de silencio
        min_silence_samples = int(min_silence_ms * self.sample_rate / 1000)
        
        # Encontrar inicio del audio
        abs_audio = np.abs(audio_array)
        start_idx = 0
        for i in range(len(abs_audio) - min_silence_samples):
            if np.mean(abs_audio[i:i+min_silence_samples]) > threshold:
                start_idx = i
                break
        
        # Encontrar final del audio
        end_idx = len(abs_audio)
        for i in range(len(abs_audio) - 1, min_silence_samples, -1):
            if np.mean(abs_audio[i-min_silence_samples:i]) > threshold:
                end_idx = i
                break
        
        # Recortar
        trimmed = audio_array[start_idx:end_idx]
        
        removed_ms = (len(audio_array) - len(trimmed)) * 1000 / self.sample_rate
        if removed_ms > 100:
            logger.debug(f"✂️  Silencio eliminado: {removed_ms:.0f}ms")
        
        return trimmed
    
    def analyze_quality(self, audio_array: np.ndarray) -> dict:
        """
        Analiza la calidad del audio.
        
        Args:
            audio_array (np.ndarray): Audio a analizar
        
        Returns:
            dict: Métricas de calidad
        """
        # RMS (volumen promedio)
        rms = np.sqrt(np.mean(audio_array ** 2))
        rms_db = 20 * np.log10(rms + 1e-10)
        
        # Pico
        peak = np.max(np.abs(audio_array))
        peak_db = 20 * np.log10(peak + 1e-10)
        
        # Crest factor (relación pico/RMS)
        crest_factor = peak / (rms + 1e-10)
        
        # Duración
        duration_sec = len(audio_array) / self.sample_rate
        
        # Detección de clipping
        clipping = np.sum(np.abs(audio_array) > 0.99) / len(audio_array) * 100
        
        quality = {
            'rms_db': round(rms_db, 2),
            'peak_db': round(peak_db, 2),
            'crest_factor': round(crest_factor, 2),
            'duration_sec': round(duration_sec, 2),
            'clipping_percent': round(clipping, 3),
            'sample_rate': self.sample_rate,
            'samples': len(audio_array)
        }
        
        return quality
    
    def process(self, audio_bytes: bytes, 
                normalize: bool = True,
                compress: bool = True,
                highpass: bool = True,
                remove_silence: bool = False,
                target_db: float = -20.0) -> bytes:
        """
        Aplica post-procesamiento completo al audio.
        
        Args:
            audio_bytes (bytes): Audio crudo de TTS
            normalize (bool): Normalizar volumen
            compress (bool): Aplicar compresión ligera
            highpass (bool): Aplicar filtro paso-alto
            remove_silence (bool): Eliminar silencios
            target_db (float): Nivel objetivo en dB
        
        Returns:
            bytes: Audio procesado
        """
        if not self.numpy_available:
            logger.warning("⚠️  NumPy no disponible - devolviendo audio sin procesar")
            return audio_bytes
        
        if not audio_bytes:
            return audio_bytes
        
        try:
            # Convertir a array
            audio_array = self.bytes_to_array(audio_bytes)
            
            # Analizar calidad inicial
            quality_before = self.analyze_quality(audio_array)
            logger.debug(f"📊 Calidad inicial: RMS={quality_before['rms_db']}dB, Peak={quality_before['peak_db']}dB")
            
            # Aplicar filtros según configuración
            if highpass:
                audio_array = self.apply_highpass_filter(audio_array)
            
            if remove_silence:
                audio_array = self.remove_silence(audio_array)
            
            if compress:
                audio_array = self.apply_compressor(audio_array)
            
            if normalize:
                audio_array = self.normalize_volume(audio_array, target_db)
            
            # Analizar calidad final
            quality_after = self.analyze_quality(audio_array)
            logger.debug(f"📊 Calidad final: RMS={quality_after['rms_db']}dB, Peak={quality_after['peak_db']}dB")
            
            # Convertir de vuelta a bytes
            processed_bytes = self.array_to_bytes(audio_array)
            
            logger.info(f"✨ Post-procesamiento completado: {len(audio_bytes)} → {len(processed_bytes)} bytes")
            
            return processed_bytes
        
        except Exception as e:
            logger.error(f"❌ Error en post-procesamiento: {e}")
            return audio_bytes  # Devolver audio original en caso de error


# Instancia global
_global_processor = None

def get_audio_processor(sample_rate: int = 22050) -> AudioProcessor:
    """
    Obtiene instancia global del procesador de audio.
    
    Args:
        sample_rate (int): Frecuencia de muestreo
    
    Returns:
        AudioProcessor: Instancia del procesador
    """
    global _global_processor
    if _global_processor is None:
        _global_processor = AudioProcessor(sample_rate)
    return _global_processor


# Ejemplo de uso
if __name__ == "__main__":
    processor = AudioProcessor(sample_rate=22050)
    
    # Simular audio (1 segundo de onda sinusoidal)
    import numpy as np
    t = np.linspace(0, 1, 22050)
    audio_array = np.sin(2 * np.pi * 440 * t) * 0.5  # 440 Hz
    audio_bytes = processor.array_to_bytes(audio_array)
    
    # Procesar
    processed = processor.process(audio_bytes, normalize=True, compress=True)
    
    print(f"Audio original: {len(audio_bytes)} bytes")
    print(f"Audio procesado: {len(processed)} bytes")
