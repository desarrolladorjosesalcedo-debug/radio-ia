"""
topics.py
Gestión de temas y contenidos para Radio IA.

Este módulo define y gestiona los temas que la radio tratará en cada segmento.
Proporciona funciones para seleccionar temas aleatorios y expandir el catálogo
de contenido dinámicamente.

Características:
- Lista central de temas predefinidos
- Selección aleatoria de temas
- Capacidad de agregar nuevos temas dinámicamente
- Validación y manejo de listas vacías

Uso:
    topic = get_random_topic()
    # topic puede ser "programación moderna", "chistes", etc.
"""

import random
import logging
from typing import Optional, List

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lista central de temas por defecto para la radio
# Estos temas serán usados para generar contenido variado y entretenido
DEFAULT_TOPICS = [
    "programación moderna",
    "desarrollo web actual",
    "productividad personal",
    "desarrollo personal y mentalidad",
    "historias motivacionales",
    "noticias tecnológicas recientes",
    "curiosidades del mundo digital",
    "un chiste ligero para relajar",
    "tendencias en inteligencia artificial",
    "reflexiones breves sobre la vida",
    "consejos de programación",
    "herramientas útiles para desarrolladores",
    "anécdotas del mundo tech",
    "datos curiosos de ciencia",
    "tips de carrera profesional"
]


def get_random_topic(topics: Optional[List[str]] = None) -> str:
    """
    Devuelve un tema aleatorio para que la locutora hable en la radio.
    
    Args:
        topics (Optional[List[str]]): Lista personalizada de temas.
                                      Si no se proporciona, usa DEFAULT_TOPICS.
    
    Returns:
        str: Un tema seleccionado aleatoriamente
    
    Examples:
        >>> get_random_topic()
        'programación moderna'
        
        >>> custom_topics = ["música", "deportes", "cocina"]
        >>> get_random_topic(custom_topics)
        'deportes'
    
    Note:
        Si la lista proporcionada está vacía, automáticamente usa DEFAULT_TOPICS
    """
    # Determinar qué lista de temas usar
    pool = topics if topics else DEFAULT_TOPICS
    
    # Validar que la lista no esté vacía
    if not pool:
        logger.warning("⚠️  Lista de temas vacía, usando temas por defecto")
        pool = DEFAULT_TOPICS
    
    # Seleccionar tema aleatorio
    selected_topic = random.choice(pool)
    logger.info(f"🎯 Tema seleccionado: '{selected_topic}'")
    
    return selected_topic


def get_random_topics(count: int = 3, topics: Optional[List[str]] = None) -> List[str]:
    """
    Devuelve múltiples temas aleatorios sin repetición.
    
    Args:
        count (int): Cantidad de temas a seleccionar (default: 3)
        topics (Optional[List[str]]): Lista personalizada de temas
    
    Returns:
        List[str]: Lista de temas seleccionados aleatoriamente
    
    Examples:
        >>> get_random_topics(2)
        ['programación moderna', 'chiste ligero para relajar']
    """
    pool = topics if topics else DEFAULT_TOPICS
    
    if not pool:
        logger.warning("⚠️  Lista de temas vacía, usando temas por defecto")
        pool = DEFAULT_TOPICS
    
    # Ajustar count si es mayor que el tamaño del pool
    actual_count = min(count, len(pool))
    
    if actual_count < count:
        logger.warning(f"⚠️  Solo hay {len(pool)} temas disponibles, se devolverán {actual_count}")
    
    selected_topics = random.sample(pool, actual_count)
    logger.info(f"🎯 Temas seleccionados: {selected_topics}")
    
    return selected_topics


def add_topic(topic: str, topics: Optional[List[str]] = None) -> None:
    """
    Agrega un tema nuevo a la lista especificada.
    
    Si no se especifica una lista, agrega el tema a DEFAULT_TOPICS.
    Evita duplicados automáticamente.
    
    Args:
        topic (str): Tema a agregar
        topics (Optional[List[str]]): Lista de temas a modificar.
                                      Si es None, modifica DEFAULT_TOPICS.
    
    Returns:
        None
    
    Examples:
        >>> add_topic("astronomía")
        # Agrega "astronomía" a DEFAULT_TOPICS
        
        >>> my_topics = ["tema1", "tema2"]
        >>> add_topic("tema3", my_topics)
        # my_topics ahora es ["tema1", "tema2", "tema3"]
    """
    # Validar que el tema no esté vacío
    if not topic or not topic.strip():
        logger.warning("⚠️  Tema vacío, no se puede agregar")
        return
    
    topic = topic.strip()
    
    # Determinar a qué lista agregar
    if topics is None:
        target_list = DEFAULT_TOPICS
        logger.info(f"➕ Agregando '{topic}' a DEFAULT_TOPICS")
    else:
        target_list = topics
        logger.info(f"➕ Agregando '{topic}' a lista personalizada")
    
    # Evitar duplicados
    if topic in target_list:
        logger.warning(f"⚠️  El tema '{topic}' ya existe en la lista")
        return
    
    target_list.append(topic)
    logger.info(f"✅ Tema agregado exitosamente. Total de temas: {len(target_list)}")


def remove_topic(topic: str, topics: Optional[List[str]] = None) -> bool:
    """
    Elimina un tema de la lista especificada.
    
    Args:
        topic (str): Tema a eliminar
        topics (Optional[List[str]]): Lista de temas a modificar.
                                      Si es None, modifica DEFAULT_TOPICS.
    
    Returns:
        bool: True si se eliminó, False si no se encontró
    """
    target_list = topics if topics is not None else DEFAULT_TOPICS
    
    if topic in target_list:
        target_list.remove(topic)
        logger.info(f"🗑️  Tema '{topic}' eliminado. Temas restantes: {len(target_list)}")
        return True
    else:
        logger.warning(f"⚠️  Tema '{topic}' no encontrado en la lista")
        return False


def list_topics(topics: Optional[List[str]] = None) -> List[str]:
    """
    Devuelve una copia de la lista de temas actual.
    
    Args:
        topics (Optional[List[str]]): Lista de temas a listar.
                                      Si es None, lista DEFAULT_TOPICS.
    
    Returns:
        List[str]: Copia de la lista de temas
    """
    target_list = topics if topics is not None else DEFAULT_TOPICS
    logger.info(f"📋 Lista de temas ({len(target_list)} temas)")
    return target_list.copy()


def get_topics_count(topics: Optional[List[str]] = None) -> int:
    """
    Devuelve la cantidad de temas disponibles.
    
    Args:
        topics (Optional[List[str]]): Lista de temas a contar
    
    Returns:
        int: Cantidad de temas
    """
    target_list = topics if topics is not None else DEFAULT_TOPICS
    count = len(target_list)
    logger.info(f"📊 Cantidad de temas disponibles: {count}")
    return count


def clear_topics(topics: Optional[List[str]] = None) -> None:
    """
    Limpia todos los temas de la lista especificada.
    
    ADVERTENCIA: Esta operación es destructiva.
    
    Args:
        topics (Optional[List[str]]): Lista de temas a limpiar.
                                      Si es None, limpia DEFAULT_TOPICS.
    """
    if topics is None:
        logger.warning("⚠️  Limpiando DEFAULT_TOPICS - operación destructiva")
        DEFAULT_TOPICS.clear()
    else:
        topics.clear()
        logger.info("🗑️  Lista de temas personalizada limpiada")


def reset_default_topics() -> None:
    """
    Restaura DEFAULT_TOPICS a su estado original.
    Útil para resetear después de modificaciones.
    """
    global DEFAULT_TOPICS
    DEFAULT_TOPICS = [
        "programación moderna",
        "desarrollo web actual",
        "productividad personal",
        "desarrollo personal y mentalidad",
        "historias motivacionales",
        "noticias tecnológicas recientes",
        "curiosidades del mundo digital",
        "un chiste ligero para relajar",
        "tendencias en inteligencia artificial",
        "reflexiones breves sobre la vida",
        "consejos de programación",
        "herramientas útiles para desarrolladores",
        "anécdotas del mundo tech",
        "datos curiosos de ciencia",
        "tips de carrera profesional"
    ]
    logger.info(f"🔄 DEFAULT_TOPICS restaurado ({len(DEFAULT_TOPICS)} temas)")
