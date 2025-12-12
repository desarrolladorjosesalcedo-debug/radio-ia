"""
prompt.py
Plantillas y generación de prompts para el LLM de Radio IA.

Este módulo define el estilo, tono y personalidad de la locutora de radio.
Construye prompts dinámicos que guían la generación de contenido espontáneo,
entretenido y profesional durante toda la transmisión.

Características:
- Prompt base con personalidad de locutora profesional
- Inserción dinámica de temas
- Control de duración y estilo
- Preparado para ajustes de energía y humor

Uso:
    prompt = build_prompt("programación moderna", duration_seconds=30)
    # Enviar este prompt a Ollama para generar contenido
"""

import logging
from typing import Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Plantilla base del prompt que define la personalidad de la locutora
# Este prompt establece el estilo, tono y reglas de improvisación
BASE_PROMPT = """
Eres una locutora profesional de radio. Tu tono es natural, variado y agradable.
Eres capaz de improvisar de manera fluida, con transiciones suaves entre ideas.

Reglas de estilo:
- No hagas respuestas cortas.
- No repitas ideas.
- No hagas preguntas al oyente.
- Mantén un ritmo dinámico, como una radio en vivo.
- Mezcla suavemente historia, explicación y entretenimiento.
- Cambia tu tono después de cada bloque (más animado, calmado, reflexivo o humorístico).
- Usa un lenguaje cercano pero profesional.
- Evita frases cliché o robóticas.

Objetivo:
Producir un bloque de locución continuo, entretenido y espontáneo que mantenga
al oyente interesado y comprometido con el contenido.
"""


def build_prompt(
    topic: str,
    duration_seconds: int = 20,
    energy_level: Optional[str] = None,
    style: Optional[str] = None
) -> str:
    """
    Construye el prompt final que será enviado al modelo LLM.
    Combina el mensaje base con el tema seleccionado y parámetros adicionales.
    
    Args:
        topic (str): Tema del bloque de radio
        duration_seconds (int): Duración aproximada del segmento (default: 20)
        energy_level (Optional[str]): Nivel de energía: "alto", "medio", "bajo", "relajado"
        style (Optional[str]): Estilo específico: "informativo", "entretenido", "reflexivo", "humorístico"
    
    Returns:
        str: Prompt completo listo para enviar a Ollama
    
    Examples:
        >>> build_prompt("inteligencia artificial")
        # Genera un prompt básico de 20 segundos
        
        >>> build_prompt("chistes de programadores", duration_seconds=15, energy_level="alto", style="humorístico")
        # Genera un prompt corto, energético y con humor
    """
    # Sanitizar el tema (eliminar espacios extra)
    topic_clean = topic.strip()
    
    if not topic_clean:
        logger.warning("⚠️  Tema vacío, usando tema por defecto")
        topic_clean = "un tema interesante"
    
    logger.info(f"🎯 Construyendo prompt para tema: '{topic_clean}' ({duration_seconds}s)")
    
    # Construir instrucciones adicionales según parámetros
    additional_instructions = []
    
    # Agregar nivel de energía si se especifica
    if energy_level:
        energy_map = {
            "alto": "Usa un tono muy energético y entusiasta, con ritmo rápido.",
            "medio": "Mantén un tono equilibrado, ni muy animado ni muy calmado.",
            "bajo": "Usa un tono suave y tranquilo, sin prisa.",
            "relajado": "Habla con calma, como en una charla nocturna relajante."
        }
        energy_instruction = energy_map.get(energy_level.lower(), "")
        if energy_instruction:
            additional_instructions.append(energy_instruction)
            logger.info(f"⚡ Nivel de energía: {energy_level}")
    
    # Agregar estilo específico si se especifica
    if style:
        style_map = {
            "informativo": "Enfócate en datos, explicaciones claras y contenido educativo.",
            "entretenido": "Prioriza el entretenimiento, historias curiosas y anécdotas.",
            "reflexivo": "Adopta un tono más profundo, invita a la reflexión y contemplación.",
            "humorístico": "Incluye humor ligero, juegos de palabras y comentarios divertidos."
        }
        style_instruction = style_map.get(style.lower(), "")
        if style_instruction:
            additional_instructions.append(style_instruction)
            logger.info(f"🎨 Estilo: {style}")
    
    # Construir sección de instrucciones adicionales
    additional_section = ""
    if additional_instructions:
        additional_section = "\nInstrucciones de estilo adicionales:\n- " + "\n- ".join(additional_instructions)
    
    # Construir el prompt completo
    prompt = f"""
{BASE_PROMPT}

Tema del bloque:
- {topic_clean}

Instrucciones específicas:
- Genera un bloque de locución de aproximadamente {duration_seconds} segundos.
- Mantén un estilo cálido, fluido y profesional.
- No uses formato markdown ni asteriscos.
- Habla directamente, como si estuvieras en vivo en la radio.{additional_section}

Comienza ahora:
"""
    
    # Limpiar espacios en blanco innecesarios
    prompt = prompt.strip()
    
    logger.info(f"✅ Prompt construido ({len(prompt)} caracteres)")
    return prompt


def build_intro_prompt() -> str:
    """
    Construye un prompt especial para la introducción de la radio.
    
    Returns:
        str: Prompt para generar una introducción atractiva
    """
    logger.info("🎙️  Construyendo prompt de introducción")
    
    prompt = """
Eres una locutora profesional de radio iniciando una transmisión en vivo.

Genera una introducción breve y atractiva (10-15 segundos) que incluya:
- Saludo cálido a los oyentes
- Mención de que esto es Radio IA
- Invitación a disfrutar del contenido
- Tono energético y profesional

No uses formato markdown. Habla de manera natural y directa.

Comienza ahora:
"""
    
    return prompt.strip()


def build_transition_prompt(previous_topic: str, next_topic: str) -> str:
    """
    Construye un prompt para transiciones suaves entre temas.
    
    Args:
        previous_topic (str): Tema anterior
        next_topic (str): Tema siguiente
    
    Returns:
        str: Prompt para generar una transición
    """
    logger.info(f"🔄 Construyendo transición: '{previous_topic}' → '{next_topic}'")
    
    prompt = f"""
Eres una locutora profesional de radio haciendo una transición entre temas.

Genera una transición breve (5-8 segundos) que:
- Cierre suavemente el tema anterior: {previous_topic}
- Introduzca naturalmente el siguiente tema: {next_topic}
- Mantenga el ritmo dinámico de la transmisión
- Sea fluida y profesional

No uses formato markdown. Habla naturalmente.

Comienza:
"""
    
    return prompt.strip()


def build_outro_prompt() -> str:
    """
    Construye un prompt especial para el cierre de la radio.
    
    Returns:
        str: Prompt para generar una despedida elegante
    """
    logger.info("👋 Construyendo prompt de despedida")
    
    prompt = """
Eres una locutora profesional de radio cerrando la transmisión.

Genera una despedida breve y cálida (8-10 segundos) que incluya:
- Agradecimiento a los oyentes
- Despedida profesional
- Invitación a volver pronto
- Tono positivo y amable

No uses formato markdown. Habla de manera natural.

Comienza:
"""
    
    return prompt.strip()


def validate_prompt(prompt: str) -> bool:
    """
    Valida que un prompt tenga el contenido mínimo necesario.
    
    Args:
        prompt (str): Prompt a validar
    
    Returns:
        bool: True si el prompt es válido, False en caso contrario
    """
    if not prompt or len(prompt.strip()) < 50:
        logger.error("❌ Prompt demasiado corto o vacío")
        return False
    
    if "Comienza" not in prompt and "comienza" not in prompt:
        logger.warning("⚠️  Prompt sin instrucción de inicio clara")
    
    logger.info("✅ Prompt válido")
    return True


# Presets de personalidad para diferentes estilos de radio
PERSONALITY_PRESETS = {
    "standard": {
        "energy": "medio",
        "style": "informativo",
        "description": "Locutora estándar, equilibrada y profesional"
    },
    "morning_show": {
        "energy": "alto",
        "style": "entretenido",
        "description": "Energética y animada, ideal para mañanas"
    },
    "night_talk": {
        "energy": "bajo",
        "style": "reflexivo",
        "description": "Calmada y contemplativa, ideal para noches"
    },
    "comedy": {
        "energy": "alto",
        "style": "humorístico",
        "description": "Divertida y ligera, enfocada en humor"
    },
    "educational": {
        "energy": "medio",
        "style": "informativo",
        "description": "Educativa y clara, enfocada en enseñar"
    }
}


def get_personality_preset(preset_name: str) -> dict:
    """
    Obtiene un preset de personalidad predefinido.
    
    Args:
        preset_name (str): Nombre del preset
    
    Returns:
        dict: Configuración de personalidad
    """
    preset = PERSONALITY_PRESETS.get(preset_name, PERSONALITY_PRESETS["standard"])
    logger.info(f"🎭 Usando personalidad '{preset_name}': {preset['description']}")
    return preset


def build_monologue_prompt(
    theme: str,
    previous_content: Optional[str] = None,
    duration_seconds: int = 20,
    anti_repetition_context: str = ""
) -> str:
    """
    Construye un prompt para generar monólogos profundos y autoexpandidos.
    El monólogo explora un tema en profundidad, genera preguntas y las responde,
    creando un flujo continuo de exploración intelectual.
    
    Args:
        theme (str): Tema central del monólogo
        previous_content (Optional[str]): Contenido previo para continuidad
        duration_seconds (int): Duración aproximada del segmento
    
    Returns:
        str: Prompt completo para generar el monólogo
    """
    theme_clean = theme.strip()
    
    if not theme_clean:
        logger.warning("⚠️  Tema vacío, usando tema por defecto")
        theme_clean = "el conocimiento humano"
    
    logger.info(f"🧠 Construyendo monólogo sobre: '{theme_clean}' ({duration_seconds}s)")
    
    # Prompt base para monólogos naturales y conversacionales
    base_monologue = f"""
Eres un locutor de radio profesional hablando con tu audiencia sobre un tema interesante.

Tema: {theme_clean}

REGLAS DE ESTILO (MUY IMPORTANTE):
- Usa lenguaje SENCILLO Y NATURAL, como si hablaras con un amigo
- Escribe como si estuvieras hablando en persona, NO leas un texto académico
- EVITA frases filosóficas o académicas como "cabría preguntarse", "esto nos lleva a reflexionar", "cabe destacar"
- NO repitas estructuras en cada frase
- NO uses frases largas; marca respiraciones naturales con puntos
- Añade variación: preguntas, ejemplos, comparaciones, pausas
- Hazlo cálido, dinámico y CONVERSACIONAL
- Suena como un locutor de radio hablando de manera NATURAL

ESTRUCTURA:
- Explora el tema desde diferentes ángulos
- Usa ejemplos concretos y situaciones reales
- Conecta ideas de forma simple y directa
- Si mencionas una pregunta, intégrala naturalmente: "Y te preguntarás...", "Quizás te estés preguntando...", "Ahora, lo interesante es..."

IMPORTANTE:
- NO uses formato markdown ni asteriscos
- NO hagas preguntas directas al oyente que requieran respuesta
- Duración aproximada: {duration_seconds} segundos de habla
- Varía tu tono: a veces más animado, a veces más reflexivo
- Habla CON la audiencia, no A la audiencia"""
    
    # Agregar contexto anti-repetición si existe
    if anti_repetition_context:
        base_monologue += anti_repetition_context
    
    # Si hay contenido previo, agregar contexto de continuidad
    if previous_content:
        continuity_section = f"""

CONTEXTO PREVIO (último segmento):
{previous_content[-300:]}  # Últimos 300 caracteres para contexto

Continúa expandiendo el tema desde donde quedó el segmento anterior.
NO repitas ideas ya mencionadas. Profundiza en nuevos aspectos o preguntas derivadas."""
        base_monologue += continuity_section
    
    # Instrucción final
    base_monologue += """

Comienza tu monólogo ahora (habla directamente, sin introducción):
"""
    
    prompt = base_monologue.strip()
    logger.info(f"✅ Prompt de monólogo construido ({len(prompt)} caracteres)")
    return prompt
