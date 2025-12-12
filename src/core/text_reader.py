"""
text_reader.py
Lector de textos personalizados para Radio IA.

Este módulo permite cargar y dividir textos desde archivos para
leerlos de forma natural en la radio.

Características:
- Carga texto desde archivos .txt
- División inteligente por párrafos
- División por tiempo estimado
- Respeta puntos y comas naturales

Uso:
    segments = load_and_split_text("input/texto.txt", max_duration=15)
"""

import logging
from pathlib import Path
from typing import List, Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_text_file(file_path: str) -> Optional[str]:
    """
    Carga el contenido de un archivo de texto.
    
    Args:
        file_path (str): Ruta al archivo de texto
    
    Returns:
        Optional[str]: Contenido del archivo o None si hay error
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"❌ Archivo no encontrado: {file_path}")
            return None
        
        if not path.is_file():
            logger.error(f"❌ La ruta no es un archivo: {file_path}")
            return None
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            logger.warning(f"⚠️  Archivo vacío: {file_path}")
            return None
        
        logger.info(f"✅ Texto cargado desde {file_path} ({len(content)} caracteres)")
        return content
    
    except Exception as e:
        logger.error(f"❌ Error leyendo archivo {file_path}: {e}")
        return None


def estimate_speech_duration(text: str, words_per_minute: int = 150) -> float:
    """
    Estima la duración de habla de un texto en segundos.
    
    Args:
        text (str): Texto a estimar
        words_per_minute (int): Palabras por minuto (default: 150)
    
    Returns:
        float: Duración estimada en segundos
    """
    words = len(text.split())
    minutes = words / words_per_minute
    seconds = minutes * 60
    return seconds


def split_by_paragraphs(text: str) -> List[str]:
    """
    Divide el texto en párrafos.
    
    Args:
        text (str): Texto completo
    
    Returns:
        List[str]: Lista de párrafos
    """
    # Dividir por líneas en blanco (doble salto de línea)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    # Si no hay párrafos, dividir por saltos de línea simples
    if len(paragraphs) <= 1:
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    logger.info(f"📄 Texto dividido en {len(paragraphs)} párrafos")
    return paragraphs


def split_by_sentences(text: str) -> List[str]:
    """
    Divide el texto en oraciones.
    
    Args:
        text (str): Texto completo
    
    Returns:
        List[str]: Lista de oraciones
    """
    import re
    # Dividir por puntos, signos de exclamación o interrogación
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    logger.info(f"📝 Texto dividido en {len(sentences)} oraciones")
    return sentences


def split_text_by_duration(
    text: str,
    max_duration_seconds: int = 15,
    words_per_minute: int = 150
) -> List[str]:
    """
    Divide el texto en segmentos según duración estimada.
    
    Args:
        text (str): Texto completo
        max_duration_seconds (int): Duración máxima por segmento
        words_per_minute (int): Velocidad de habla
    
    Returns:
        List[str]: Lista de segmentos
    """
    # Primero intentar dividir por párrafos
    paragraphs = split_by_paragraphs(text)
    
    segments = []
    current_segment = ""
    
    for paragraph in paragraphs:
        # Estimar duración del párrafo
        para_duration = estimate_speech_duration(paragraph, words_per_minute)
        
        # Si el párrafo solo cabe en su propio segmento
        if para_duration > max_duration_seconds:
            # Guardar segmento actual si existe
            if current_segment:
                segments.append(current_segment.strip())
                current_segment = ""
            
            # Dividir el párrafo largo en oraciones
            sentences = split_by_sentences(paragraph)
            temp_segment = ""
            
            for sentence in sentences:
                test_segment = temp_segment + " " + sentence if temp_segment else sentence
                test_duration = estimate_speech_duration(test_segment, words_per_minute)
                
                if test_duration <= max_duration_seconds:
                    temp_segment = test_segment
                else:
                    if temp_segment:
                        segments.append(temp_segment.strip())
                    temp_segment = sentence
            
            if temp_segment:
                segments.append(temp_segment.strip())
        
        else:
            # Intentar agregar al segmento actual
            test_segment = current_segment + "\n\n" + paragraph if current_segment else paragraph
            test_duration = estimate_speech_duration(test_segment, words_per_minute)
            
            if test_duration <= max_duration_seconds:
                current_segment = test_segment
            else:
                # Guardar segmento actual y empezar uno nuevo
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = paragraph
    
    # Agregar último segmento
    if current_segment:
        segments.append(current_segment.strip())
    
    logger.info(f"✂️  Texto dividido en {len(segments)} segmentos")
    for i, seg in enumerate(segments, 1):
        duration = estimate_speech_duration(seg, words_per_minute)
        logger.info(f"   Segmento {i}: {len(seg)} chars, ~{duration:.1f}s")
    
    return segments


def load_and_split_text(
    file_path: str,
    max_duration_seconds: int = 15,
    words_per_minute: int = 150
) -> Optional[List[str]]:
    """
    Carga un archivo de texto y lo divide en segmentos.
    
    Args:
        file_path (str): Ruta al archivo
        max_duration_seconds (int): Duración máxima por segmento
        words_per_minute (int): Velocidad de habla
    
    Returns:
        Optional[List[str]]: Lista de segmentos o None si hay error
    """
    # Cargar texto
    text = load_text_file(file_path)
    
    if not text:
        return None
    
    # Dividir en segmentos
    segments = split_text_by_duration(text, max_duration_seconds, words_per_minute)
    
    if not segments:
        logger.error("❌ No se pudieron crear segmentos del texto")
        return None
    
    logger.info(f"✅ Texto procesado: {len(segments)} segmentos listos")
    return segments


def validate_text_file(file_path: str) -> bool:
    """
    Valida que un archivo de texto sea válido para lectura.
    
    Args:
        file_path (str): Ruta al archivo
    
    Returns:
        bool: True si es válido
    """
    path = Path(file_path)
    
    if not path.exists():
        logger.error(f"❌ Archivo no existe: {file_path}")
        return False
    
    if not path.is_file():
        logger.error(f"❌ No es un archivo: {file_path}")
        return False
    
    if path.suffix.lower() not in ['.txt', '.md']:
        logger.warning(f"⚠️  Extensión no recomendada: {path.suffix}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            logger.error(f"❌ Archivo vacío: {file_path}")
            return False
        
        logger.info(f"✅ Archivo válido: {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error validando archivo: {e}")
        return False
