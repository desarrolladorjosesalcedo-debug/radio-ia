"""
active_session.py
Gestión de sesión activa persistente para Radio IA.

Este módulo permite continuar la misma sesión entre ejecuciones,
evitando repetir contenido y manteniendo coherencia en monólogos.

Características:
- Detecta si hay sesión activa reciente
- Guarda contenido de los últimos N segmentos
- Timeout configurable para crear nueva sesión
- Anti-repetición de temas y conceptos

Uso:
    manager = ActiveSessionManager()
    session_id = manager.get_or_create_session()
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ActiveSessionManager:
    """Gestor de sesión activa persistente"""
    
    def __init__(self, history_dir: str = "history", timeout_hours: int = 24):
        """
        Inicializa el gestor de sesión activa.
        
        Args:
            history_dir (str): Directorio de historial
            timeout_hours (int): Horas antes de crear nueva sesión
        """
        self.history_dir = Path(history_dir)
        self.active_file = self.history_dir / "active_session.json"
        self.timeout_hours = timeout_hours
        
        # Crear directorio si no existe
        self.history_dir.mkdir(parents=True, exist_ok=True)
    
    def get_or_create_session(self, force_new: bool = False) -> tuple[str, bool, List[str]]:
        """
        Obtiene sesión activa o crea una nueva si es necesario.
        
        Args:
            force_new (bool): Forzar creación de nueva sesión
        
        Returns:
            tuple[str, bool, List[str]]: (session_id, is_continuing, previous_content)
        """
        if force_new:
            session_id = self._create_new_session()
            logger.info(f"🆕 Nueva sesión forzada: {session_id}")
            return session_id, False, []
        
        # Intentar cargar sesión activa
        active_data = self._load_active_session()
        
        if not active_data:
            # No hay sesión activa, crear nueva
            session_id = self._create_new_session()
            logger.info(f"🆕 Nueva sesión creada: {session_id}")
            return session_id, False, []
        
        # Verificar si la sesión está vigente (no expiró el timeout)
        last_used = datetime.fromisoformat(active_data["last_used"])
        now = datetime.now()
        time_diff = now - last_used
        
        if time_diff > timedelta(hours=self.timeout_hours):
            # Sesión expirada, crear nueva
            session_id = self._create_new_session()
            logger.info(f"⏰ Sesión anterior expiró ({time_diff.total_seconds() / 3600:.1f}h)")
            logger.info(f"🆕 Nueva sesión creada: {session_id}")
            return session_id, False, []
        
        # Sesión activa válida, continuar
        session_id = active_data["session_id"]
        previous_content = active_data.get("recent_content", [])
        
        logger.info(f"♻️  Continuando sesión existente: {session_id}")
        logger.info(f"⏱️  Última actividad: hace {time_diff.total_seconds() / 60:.0f} minutos")
        logger.info(f"📝 Contenido previo: {len(previous_content)} segmentos")
        
        # Actualizar timestamp de uso
        self._update_last_used(active_data)
        
        return session_id, True, previous_content
    
    def add_content(self, session_id: str, content: str, max_history: int = 5):
        """
        Agrega contenido generado a la sesión activa.
        
        Args:
            session_id (str): ID de la sesión
            content (str): Contenido del segmento
            max_history (int): Número máximo de segmentos a recordar
        """
        active_data = self._load_active_session()
        
        if not active_data or active_data["session_id"] != session_id:
            logger.warning(f"⚠️  Sesión {session_id} no coincide con sesión activa")
            return
        
        # Agregar nuevo contenido
        recent_content = active_data.get("recent_content", [])
        recent_content.append(content)
        
        # Mantener solo los últimos N segmentos
        if len(recent_content) > max_history:
            recent_content = recent_content[-max_history:]
        
        active_data["recent_content"] = recent_content
        active_data["last_used"] = datetime.now().isoformat()
        active_data["total_segments"] = active_data.get("total_segments", 0) + 1
        
        self._save_active_session(active_data)
        logger.info(f"📝 Contenido agregado a sesión activa ({len(recent_content)} en memoria)")
    
    def clear_session(self):
        """Elimina la sesión activa (forzar nueva sesión en próxima ejecución)"""
        if self.active_file.exists():
            self.active_file.unlink()
            logger.info("🗑️  Sesión activa eliminada")
    
    def _create_new_session(self) -> str:
        """Crea una nueva sesión activa"""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        active_data = {
            "session_id": session_id,
            "created": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat(),
            "recent_content": [],
            "total_segments": 0
        }
        
        self._save_active_session(active_data)
        return session_id
    
    def _load_active_session(self) -> Optional[Dict]:
        """Carga datos de sesión activa"""
        if not self.active_file.exists():
            return None
        
        try:
            with open(self.active_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Error leyendo sesión activa: {e}")
            return None
    
    def _save_active_session(self, data: Dict):
        """Guarda datos de sesión activa"""
        try:
            with open(self.active_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Error guardando sesión activa: {e}")
    
    def _update_last_used(self, data: Dict):
        """Actualiza timestamp de última actividad"""
        data["last_used"] = datetime.now().isoformat()
        self._save_active_session(data)
    
    def get_session_info(self) -> Optional[Dict]:
        """Obtiene información de la sesión activa"""
        return self._load_active_session()


def extract_key_concepts(text: str, max_concepts: int = 5) -> List[str]:
    """
    Extrae conceptos clave de un texto.
    
    Args:
        text (str): Texto a analizar
        max_concepts (int): Máximo de conceptos a extraer
    
    Returns:
        List[str]: Lista de conceptos clave
    """
    # Palabras comunes a ignorar
    stop_words = {
        'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
        'de', 'del', 'en', 'y', 'o', 'que', 'por', 'para',
        'con', 'como', 'más', 'pero', 'su', 'sus', 'es', 'son',
        'esta', 'está', 'este', 'estos', 'estas', 'ese', 'esos',
        'se', 'si', 'no', 'al', 'lo', 'ya', 'también', 'muy'
    }
    
    # Tokenizar y limpiar
    words = text.lower().split()
    words = [w.strip('.,;:()[]{}¿?¡!"\'') for w in words]
    
    # Filtrar palabras cortas y stop words
    words = [w for w in words if len(w) > 4 and w not in stop_words]
    
    # Contar frecuencia
    from collections import Counter
    word_freq = Counter(words)
    
    # Obtener las N palabras más frecuentes
    concepts = [word for word, _ in word_freq.most_common(max_concepts)]
    
    return concepts


def build_anti_repetition_context(previous_content: List[str]) -> str:
    """
    Construye contexto de anti-repetición para el prompt.
    
    Args:
        previous_content (List[str]): Lista de contenidos previos
    
    Returns:
        str: Texto de contexto para evitar repeticiones
    """
    if not previous_content:
        return ""
    
    # Extraer conceptos de todos los segmentos previos
    all_concepts = []
    for content in previous_content:
        concepts = extract_key_concepts(content, max_concepts=3)
        all_concepts.extend(concepts)
    
    # Eliminar duplicados manteniendo orden
    unique_concepts = []
    seen = set()
    for concept in all_concepts:
        if concept not in seen:
            unique_concepts.append(concept)
            seen.add(concept)
    
    if not unique_concepts:
        return ""
    
    # Construir texto de contexto
    concepts_text = ", ".join(unique_concepts[:10])  # Máximo 10 conceptos
    
    context = f"""

CONTENIDO YA CUBIERTO (evitar repetir estos conceptos):
{concepts_text}

IMPORTANTE: Explora NUEVOS aspectos, perspectivas o ángulos que NO hayan sido mencionados.
Si debes hablar de conceptos similares, usa palabras diferentes y enfócate en aspectos distintos.
"""
    
    return context
