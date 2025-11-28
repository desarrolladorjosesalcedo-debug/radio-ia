"""
groq_client.py
Cliente para interactuar con Groq API.

Este módulo permite generar contenido de radio mediante modelos de lenguaje
en la nube de Groq. Es mucho más rápido que Ollama local.

Funcionalidades:
- Generación de texto ultra-rápida (1-3 segundos)
- Múltiples modelos disponibles
- API gratuita con límites generosos
- Manejo robusto de errores

Uso:
    text = generate_text_groq("llama2-70b-4096", "Genera una introducción para la radio")
"""

import logging
from groq import Groq

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_text_groq(model_name: str, prompt: str, api_key: str, max_tokens: int = 500) -> str:
    """
    Genera texto usando Groq API.
    
    Args:
        model_name (str): Nombre del modelo ('llama2-70b-4096', 'mixtral-8x7b-32768', etc.)
        prompt (str): El prompt o instrucción para el modelo
        api_key (str): API key de Groq
        max_tokens (int): Máximo de tokens a generar (default: 500)
    
    Returns:
        str: Texto generado por el modelo
    """
    logger.info(f"🌐 Generando contenido con Groq: {model_name}")
    
    try:
        # Inicializar cliente de Groq
        client = Groq(api_key=api_key)
        
        # Generar texto
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model_name,
            max_tokens=max_tokens,
            temperature=0.7,
        )
        
        # Extraer texto generado
        texto = chat_completion.choices[0].message.content
        
        if not texto or len(texto.strip()) < 10:
            logger.warning("⚠️  Respuesta vacía o muy corta de Groq")
            return "La locutora está tomando una breve pausa…"
        
        logger.info(f"✅ Texto generado exitosamente ({len(texto)} caracteres)")
        return texto.strip()
    
    except Exception as e:
        logger.error(f"❌ Error generando texto con Groq: {e}")
        return "Hubo un problema técnico generando la locución."


def check_groq_available(api_key: str) -> bool:
    """
    Verifica si Groq API está disponible y la API key es válida.
    
    Args:
        api_key (str): API key de Groq
    
    Returns:
        bool: True si Groq está disponible
    """
    try:
        client = Groq(api_key=api_key)
        
        # Prueba simple
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "test"}],
            model="llama-3.3-70b-versatile",
            max_tokens=5,
        )
        
        logger.info("✅ Groq API disponible y funcionando")
        return True
    except Exception as e:
        logger.error(f"❌ Groq API no disponible: {e}")
        return False


# Modelos disponibles en Groq
GROQ_MODELS = {
    "llama2-70b": "llama2-70b-4096",
    "mixtral": "mixtral-8x7b-32768",
    "gemma": "gemma-7b-it",
}
