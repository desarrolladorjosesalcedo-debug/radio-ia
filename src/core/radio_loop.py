"""
radio_loop.py
Motor principal de Radio IA - El "cerebro" del proyecto.

Este módulo coordina todo el flujo de la radio:
1. Selecciona un tema aleatorio
2. Construye el prompt dinámico
3. Genera texto con Ollama LLM
4. Convierte el texto a voz con Piper TTS
5. Reproduce el audio
6. Repite el proceso infinitamente

Es el componente central que orquesta todos los demás módulos para
crear una transmisión de radio continua y automática.

Uso:
    start_radio()  # Inicia la radio (loop infinito)
"""

import time
import logging
import sys
import yaml
from pathlib import Path
from typing import Optional

# Importar módulos del proyecto
from core.topics import get_random_topic
from core.prompt import build_prompt, build_intro_prompt
from llm.ollama_client import generate_text, check_ollama_available
from llm.groq_client import generate_text_groq, check_groq_available
from tts.piper_tts import synthesize_speech, check_piper_available, validate_model
from utils.audio_player import play_audio, check_ffplay_available

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Configuración por defecto
DEFAULT_CONFIG = {
    "provider": "groq",  # "groq" o "ollama"
    "model_name": "llama2-70b-4096",  # Modelo
    "model_path": "models/piper/es_ES-davefx-medium.onnx",  # Modelo de Piper
    "duration_seconds": 20,  # Duración de cada segmento
    "delay_seconds": 1.0,  # Pausa entre segmentos
    "sample_rate": 22050,  # Frecuencia de audio
    "max_retries": 3,  # Reintentos en caso de error
    "api_key": "",  # API key para Groq
    "max_tokens": 500  # Máximo de tokens
}


def load_config() -> dict:
    """
    Carga la configuración desde settings.yaml.
    Si no existe, usa la configuración por defecto.
    
    Returns:
        dict: Diccionario con la configuración
    """
    settings_path = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
    
    if not settings_path.exists():
        logger.warning(f"⚠️  No se encontró {settings_path}, usando configuración por defecto")
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = yaml.safe_load(f)
        
        # Mapear configuración de YAML a formato interno
        config = {
            "provider": settings.get("llm", {}).get("provider", DEFAULT_CONFIG["provider"]),
            "model_name": settings.get("llm", {}).get("model_name", DEFAULT_CONFIG["model_name"]),
            "model_path": settings.get("tts", {}).get("model_path", DEFAULT_CONFIG["model_path"]),
            "duration_seconds": settings.get("radio", {}).get("duration_seconds", DEFAULT_CONFIG["duration_seconds"]),
            "delay_seconds": settings.get("radio", {}).get("delay_seconds", DEFAULT_CONFIG["delay_seconds"]),
            "sample_rate": settings.get("audio", {}).get("sample_rate", DEFAULT_CONFIG["sample_rate"]),
            "max_retries": settings.get("radio", {}).get("max_retries", DEFAULT_CONFIG["max_retries"]),
            "skip_intro": settings.get("radio", {}).get("skip_intro", False),
            "tts_speaker_id": settings.get("tts", {}).get("speaker_id"),
            "tts_length_scale": settings.get("tts", {}).get("length_scale", 1.0),
            "llm_timeout": settings.get("llm", {}).get("timeout", 30),
            "api_key": settings.get("llm", {}).get("api_key", ""),
            "max_tokens": settings.get("llm", {}).get("max_tokens", 500),
        }
        
        logger.info(f"✅ Configuración cargada desde {settings_path}")
        return config
    
    except Exception as e:
        logger.error(f"❌ Error leyendo configuración: {e}")
        logger.info("📋 Usando configuración por defecto")
        return DEFAULT_CONFIG.copy()


def check_dependencies(config: dict) -> bool:
    """
    Verifica que todas las dependencias necesarias estén instaladas.
    
    Args:
        config (dict): Configuración con provider y api_key
    
    Returns:
        bool: True si todas las dependencias están disponibles
    """
    logger.info("🔍 Verificando dependencias...")
    
    all_available = True
    provider = config.get("provider", "ollama")
    
    # Verificar LLM según provider
    if provider == "groq":
        api_key = config.get("api_key", "")
        if not api_key:
            logger.error("❌ Falta API key de Groq")
            logger.info("💡 Configura api_key en settings.yaml")
            all_available = False
        elif not check_groq_available(api_key):
            logger.error("❌ Groq API no está disponible")
            all_available = False
        else:
            logger.info("✅ Groq API disponible")
    else:  # ollama
        if not check_ollama_available():
            logger.error("❌ Ollama no está disponible")
            logger.info("💡 Instala Ollama desde: https://ollama.ai/")
            all_available = False
    
    # Verificar Piper
    if not check_piper_available():
        logger.error("❌ Piper TTS no está disponible")
        logger.info("💡 Instala Piper desde: https://github.com/rhasspy/piper")
        all_available = False
    
    # Verificar ffplay
    if not check_ffplay_available():
        logger.error("❌ ffplay no está disponible")
        logger.info("💡 Instala FFmpeg desde: https://ffmpeg.org/")
        all_available = False
    
    if all_available:
        logger.info("✅ Todas las dependencias están disponibles")
    
    return all_available


def generate_segment(
    model_name: str,
    model_path: str,
    duration_seconds: int = 20,
    topic: Optional[str] = None,
    provider: str = "groq",
    api_key: str = "",
    max_tokens: int = 500,
    llm_timeout: int = 30
) -> tuple[str, bytes]:
    """
    Genera un segmento completo de radio (texto + audio).
    
    Args:
        model_name (str): Nombre del modelo de Ollama
        model_path (str): Ruta al modelo de Piper
        duration_seconds (int): Duración aproximada del segmento
        topic (Optional[str]): Tema específico, o None para aleatorio
    
    Returns:
        tuple[str, bytes]: (texto_generado, audio_bytes)
    """
    # Paso 1: Elegir tema
    if topic is None:
        topic = get_random_topic()
    logger.info(f"🎯 Tema seleccionado: '{topic}'")
    
    # Paso 2: Construir prompt
    prompt = build_prompt(topic, duration_seconds=duration_seconds)
    logger.info("📝 Prompt construido")
    
    # Paso 3: Generar texto con LLM (Groq u Ollama)
    logger.info(f"🤖 Generando texto con {provider.upper()}...")
    
    if provider == "groq":
        texto = generate_text_groq(model_name, prompt, api_key, max_tokens=max_tokens)
    else:  # ollama
        texto = generate_text(model_name, prompt, timeout=llm_timeout)
    
    if not texto or len(texto.strip()) < 10:
        logger.warning("⚠️  Texto generado inválido o vacío")
        return "", b""
    
    logger.info(f"✅ Texto generado ({len(texto)} caracteres)")
    
    # Paso 4: Convertir texto a voz con Piper
    logger.info("🎤 Sintetizando voz con Piper...")
    audio = synthesize_speech(texto, model_path, length_scale=duration_seconds/20.0)
    
    if not audio or len(audio) < 100:
        logger.warning("⚠️  Audio generado inválido o vacío")
        return texto, b""
    
    logger.info(f"✅ Audio sintetizado ({len(audio)} bytes)")
    
    return texto, audio


def play_intro(model_name: str, model_path: str, provider: str = "groq", api_key: str = "", max_tokens: int = 200) -> None:
    """
    Reproduce una introducción de bienvenida a la radio.
    
    Args:
        model_name (str): Nombre del modelo de Ollama
        model_path (str): Ruta al modelo de Piper
    """
    logger.info("🎙️  Generando introducción de Radio IA...")
    
    try:
        intro_prompt = build_intro_prompt()
        
        if provider == "groq":
            intro_text = generate_text_groq(model_name, intro_prompt, api_key, max_tokens=max_tokens)
        else:
            intro_text = generate_text(model_name, intro_prompt)
        
        if intro_text:
            intro_audio = synthesize_speech(intro_text, model_path)
            if intro_audio:
                play_audio(intro_audio)
                logger.info("✅ Introducción reproducida")
                return
        
        logger.warning("⚠️  No se pudo generar la introducción")
    except Exception as e:
        logger.error(f"❌ Error generando introducción: {e}")


def start_radio(
    delay_seconds: float = 1.0,
    max_iterations: Optional[int] = None,
    skip_intro: bool = False
) -> None:
    """
    Inicia el bucle principal de Radio IA.
    
    Esta función ejecuta un ciclo infinito que:
    - Selecciona temas aleatorios
    - Genera contenido con IA
    - Sintetiza voz
    - Reproduce audio continuamente
    
    Args:
        delay_seconds (float): Pausa entre segmentos en segundos (default: 1.0)
        max_iterations (Optional[int]): Número máximo de iteraciones (None = infinito)
        skip_intro (bool): Si True, omite la introducción (default: False)
    
    Raises:
        KeyboardInterrupt: Cuando el usuario presiona Ctrl+C
    """
    logger.info("=" * 60)
    logger.info("🎙️  RADIO IA - INICIANDO TRANSMISIÓN")
    logger.info("=" * 60)
    
    # Cargar configuración
    config = load_config()
    
    # Verificar dependencias
    if not check_dependencies(config):
        logger.error("❌ No se puede iniciar la radio sin las dependencias necesarias")
        logger.info("💡 Instala las herramientas requeridas y vuelve a intentar")
        return
    
    provider = config["provider"]
    model_name = config["model_name"]
    model_path = config["model_path"]
    duration_seconds = config["duration_seconds"]
    sample_rate = config["sample_rate"]
    max_retries = config["max_retries"]
    api_key = config.get("api_key", "")
    max_tokens = config.get("max_tokens", 500)
    
    # Validar modelo de Piper
    if not Path(model_path).exists():
        logger.error(f"❌ Modelo de Piper no encontrado: {model_path}")
        logger.info("💡 Descarga un modelo de voz y colócalo en models/piper/")
        logger.info("   Modelos disponibles en: https://github.com/rhasspy/piper/releases")
        return
    
    logger.info(f"🌐 Proveedor LLM: {provider.upper()}")
    logger.info(f"🤖 Modelo LLM: {model_name}")
    logger.info(f"🎤 Modelo TTS: {model_path}")
    logger.info(f"⏱️  Duración por segmento: {duration_seconds}s")
    logger.info(f"🔊 Sample rate: {sample_rate} Hz")
    logger.info("=" * 60)
    
    # Reproducir introducción
    if not skip_intro:
        play_intro(model_name, model_path, provider=provider, api_key=api_key, max_tokens=200)
        time.sleep(delay_seconds)
    
    # Iniciar bucle principal
    logger.info("🔄 Iniciando bucle de transmisión continua...")
    logger.info("⌨️  Presiona Ctrl+C para detener la transmisión")
    logger.info("=" * 60)
    
    iteration = 0
    consecutive_errors = 0
    
    while True:
        try:
            iteration += 1
            
            # Verificar si se alcanzó el máximo de iteraciones
            if max_iterations is not None and iteration > max_iterations:
                logger.info(f"✅ Alcanzado el máximo de iteraciones: {max_iterations}")
                break
            
            logger.info(f"\n{'=' * 60}")
            logger.info(f"📻 SEGMENTO #{iteration}")
            logger.info(f"{'=' * 60}")
            
            # Generar segmento completo
            texto, audio = generate_segment(
                model_name=model_name,
                model_path=model_path,
                duration_seconds=duration_seconds,
                provider=provider,
                api_key=api_key,
                max_tokens=max_tokens,
                llm_timeout=config.get("llm_timeout", 30)
            )
            
            # Validar que se generó contenido
            if not texto:
                logger.warning("⚠️  No se pudo generar texto. Reintentando...")
                consecutive_errors += 1
                
                if consecutive_errors >= max_retries:
                    logger.error(f"❌ Demasiados errores consecutivos ({max_retries}). Deteniendo.")
                    break
                
                time.sleep(delay_seconds * 2)
                continue
            
            if not audio:
                logger.warning("⚠️  No se pudo generar audio. Reintentando...")
                consecutive_errors += 1
                
                if consecutive_errors >= max_retries:
                    logger.error(f"❌ Demasiados errores consecutivos ({max_retries}). Deteniendo.")
                    break
                
                time.sleep(delay_seconds * 2)
                continue
            
            # Resetear contador de errores si todo salió bien
            consecutive_errors = 0
            
            # Reproducir audio
            logger.info("🔊 Reproduciendo segmento...")
            play_audio(audio, sample_rate=sample_rate)
            
            logger.info(f"✅ Segmento #{iteration} completado exitosamente")
            
            # Pausa antes del siguiente segmento
            if delay_seconds > 0:
                logger.info(f"⏸️  Pausa de {delay_seconds}s antes del siguiente segmento...")
                time.sleep(delay_seconds)
        
        except KeyboardInterrupt:
            logger.info("\n" + "=" * 60)
            logger.info("⏹️  Interrupción recibida (Ctrl+C)")
            logger.info("🎙️  Deteniendo Radio IA...")
            logger.info("=" * 60)
            break
        
        except Exception as e:
            logger.error(f"❌ Error inesperado en el ciclo de radio: {e}")
            consecutive_errors += 1
            
            if consecutive_errors >= max_retries:
                logger.error(f"❌ Demasiados errores consecutivos ({max_retries}). Deteniendo.")
                break
            
            logger.info("⏸️  Esperando 2 segundos antes de reintentar...")
            time.sleep(2)
    
    logger.info("\n" + "=" * 60)
    logger.info(f"📊 ESTADÍSTICAS FINALES")
    logger.info(f"   Segmentos generados: {iteration}")
    logger.info(f"   Errores consecutivos: {consecutive_errors}")
    logger.info("=" * 60)
    logger.info("👋 Gracias por escuchar Radio IA")
    logger.info("=" * 60)


# Función auxiliar para compatibilidad con main.py
def start_radio_loop(delay_seconds: float = 1.0):
    """
    Alias de start_radio() para compatibilidad con versiones anteriores.
    
    Args:
        delay_seconds (float): Pausa entre segmentos
    """
    start_radio(delay_seconds=delay_seconds)
