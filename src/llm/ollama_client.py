"""
ollama_client.py
Cliente para interactuar con Ollama LLM local.

Este módulo permite generar contenido de radio mediante modelos de lenguaje
ejecutados localmente con Ollama. Es compatible con Windows, Linux y Mac.

Funcionalidades:
- Generación de texto mediante subprocess
- Manejo robusto de errores y timeouts
- Limpieza automática de la salida
- Logs informativos para debugging

Uso:
    text = generate_text("llama2", "Genera una introducción para la radio")
"""

import subprocess
import logging
import re

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_text(model_name: str, prompt: str, timeout: int = 180) -> str:
    """
    Envía un prompt al modelo local de Ollama y devuelve el texto generado.
    
    Args:
        model_name (str): Nombre del modelo de Ollama a utilizar (ej: "llama2", "mistral")
        prompt (str): El prompt o instrucción para el modelo
        timeout (int): Tiempo máximo de espera en segundos (default: 60)
    
    Returns:
        str: Texto generado por el modelo, o mensaje de error por defecto
    
    Raises:
        No lanza excepciones, devuelve texto por defecto en caso de error
    """
    logger.info(f"🤖 Generando contenido con modelo: {model_name} (timeout: {timeout}s)")
    
    try:
        # Ejecutar Ollama mediante subprocess
        result = subprocess.run(
            ["ollama", "run", model_name],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        
        # Decodificar la salida
        output = result.stdout.decode("utf-8", errors="ignore")
        stderr_output = result.stderr.decode("utf-8", errors="ignore")
        
        # Log de errores si los hay
        if stderr_output and result.returncode != 0:
            logger.warning(f"⚠️  Ollama stderr: {stderr_output}")
        
        # Limpieza del texto generado
        output = _clean_output(output)
        
        # Validar que hay contenido
        if not output or len(output.strip()) < 10:
            logger.warning("⚠️  Respuesta vacía o muy corta de Ollama")
            return "La locutora está tomando una breve pausa…"
        
        logger.info(f"✅ Texto generado exitosamente ({len(output)} caracteres)")
        return output
    
    except subprocess.TimeoutExpired:
        logger.error(f"⏱️  Timeout al generar texto (>{timeout}s)")
        return "Lo siento, la generación está tomando más tiempo del esperado."
    
    except FileNotFoundError:
        logger.error("❌ Ollama no está instalado o no está en el PATH")
        return "Hubo un problema técnico con el sistema de generación de contenido."
    
    except Exception as e:
        logger.error(f"❌ Error generando texto con Ollama: {e}")
        return "Hubo un problema técnico generando la locución."


def _clean_output(text: str) -> str:
    """
    Limpia el texto generado eliminando tokens recurrentes y basura.
    
    Args:
        text (str): Texto crudo de Ollama
    
    Returns:
        str: Texto limpio y procesado
    """
    if not text:
        return ""
    
    # Eliminar espacios en blanco extras
    text = text.strip()
    
    # Eliminar líneas vacías múltiples
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Eliminar posibles prefijos de sistema (ajustar según necesidad)
    text = re.sub(r'^(Assistant:|AI:|Bot:)\s*', '', text, flags=re.IGNORECASE)
    
    # Eliminar caracteres de control no deseados
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)
    
    return text.strip()


def check_ollama_available() -> bool:
    """
    Verifica si Ollama está instalado y disponible en el sistema.
    
    Returns:
        bool: True si Ollama está disponible, False en caso contrario
    """
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        available = result.returncode == 0
        if available:
            version = result.stdout.decode("utf-8", errors="ignore").strip()
            logger.info(f"✅ Ollama disponible: {version}")
        return available
    except Exception as e:
        logger.error(f"❌ Ollama no disponible: {e}")
        return False


def list_available_models() -> list:
    """
    Lista los modelos disponibles en Ollama.
    
    Returns:
        list: Lista de nombres de modelos disponibles
    """
    try:
        result = subprocess.run(
            ["ollama", "list"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10
        )
        
        if result.returncode == 0:
            output = result.stdout.decode("utf-8", errors="ignore")
            # Parsear la salida (formato puede variar)
            lines = output.strip().split('\n')[1:]  # Saltar encabezado
            models = [line.split()[0] for line in lines if line.strip()]
            logger.info(f"📋 Modelos disponibles: {models}")
            return models
        return []
    except Exception as e:
        logger.error(f"❌ Error listando modelos: {e}")
        return []
