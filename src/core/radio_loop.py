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
import threading
from pathlib import Path
from typing import Optional, Tuple

# Importar módulos del proyecto
from core.topics import get_random_topic
from core.prompt import build_prompt, build_intro_prompt
from core.session_history import SessionHistory
from llm.ollama_client import generate_text, check_ollama_available
from llm.groq_client import generate_text_groq, check_groq_available
from tts.piper_tts import synthesize_speech, check_piper_available, validate_model
from tts.edge_tts_client import synthesize_speech_edge, check_edge_tts_available
from tts.gtts_client import synthesize_speech_gtts, check_gtts_available
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
            "mode": settings.get("radio", {}).get("mode", "topics"),
            "monologue_theme": settings.get("radio", {}).get("monologue_theme", "inteligencia artificial"),
            "tts_speaker_id": settings.get("tts", {}).get("speaker_id"),
            "tts_length_scale": settings.get("tts", {}).get("length_scale", 1.0),
            "edge_voice": settings.get("tts", {}).get("edge_voice", "es-CO-SalomeNeural"),
            "llm_timeout": settings.get("llm", {}).get("timeout", 30),
            "api_key": settings.get("llm", {}).get("api_key", ""),
            "max_tokens": settings.get("llm", {}).get("max_tokens", 500),
            "history_dir": settings.get("history", {}).get("dir", "history"),
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
    llm_timeout: int = 30,
    edge_voice: str = "es-CO-SalomeNeural",
    mode: str = "topics",
    previous_content: Optional[str] = None
) -> tuple[str, bytes, str, str]:
    """
    Genera un segmento completo de radio (texto + audio).
    
    Args:
        model_name (str): Nombre del modelo de Ollama
        model_path (str): Ruta al modelo de Piper
        duration_seconds (int): Duración aproximada del segmento
        topic (Optional[str]): Tema específico, o None para aleatorio
        mode (str): "topics" o "monologue"
        previous_content (Optional[str]): Contenido previo para modo monólogo
    
    Returns:
        tuple[str, bytes, str, str]: (texto_generado, audio_bytes, topic, tts_provider)
    """
    # Importar build_monologue_prompt
    from core.prompt import build_monologue_prompt
    
    # Paso 1: Elegir tema o usar tema de monólogo
    if topic is None:
        topic = get_random_topic()
    logger.info(f"🎯 Tema seleccionado: '{topic}'")
    
    # Paso 2: Construir prompt según modo
    if mode == "monologue":
        prompt = build_monologue_prompt(topic, previous_content=previous_content, duration_seconds=duration_seconds)
        logger.info("🧠 Prompt de monólogo construido")
    else:
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
        return "", b"", topic, "none"
    
    logger.info(f"✅ Texto generado ({len(texto)} caracteres)")
    
    # Paso 4: Convertir texto a voz (Piper → Edge TTS → Google TTS)
    logger.info("🎤 Sintetizando voz...")
    audio = synthesize_speech(texto, model_path, length_scale=duration_seconds/20.0)
    tts_provider = "piper"
    
    # Si Piper falla, intentar con Edge TTS (mejor calidad)
    if not audio or len(audio) < 100:
        logger.warning("⚠️  Piper falló, intentando con Edge TTS...")
        audio = synthesize_speech_edge(texto, voice=edge_voice)
        tts_provider = "edge"
    
    # Si Edge TTS falla, usar Google TTS como último recurso
    if not audio or len(audio) < 100:
        logger.warning("⚠️  Edge TTS falló, usando Google TTS...")
        audio = synthesize_speech_gtts(texto)
        tts_provider = "gtts"
    
    if not audio or len(audio) < 100:
        logger.warning("⚠️  Audio generado inválido o vacío")
        return texto, b"", topic, "none"
    
    logger.info(f"✅ Audio sintetizado ({len(audio)} bytes)")
    
    return texto, audio, topic, tts_provider


def play_intro(model_name: str, model_path: str, provider: str = "groq", api_key: str = "", max_tokens: int = 200, edge_voice: str = "es-CO-SalomeNeural") -> Optional[str]:
    """
    Reproduce una introducción de bienvenida a la radio.
    
    Args:
        model_name (str): Nombre del modelo de Ollama
        model_path (str): Ruta al modelo de Piper
    
    Returns:
        Optional[str]: Texto de la introducción generada, o None si falla
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
            # Si Piper falla, intentar con Edge TTS
            if not intro_audio or len(intro_audio) < 100:
                logger.warning("⚠️  Piper falló, usando Edge TTS para intro...")
                intro_audio = synthesize_speech_edge(intro_text, voice=edge_voice)
            # Si Edge TTS falla, usar Google TTS
            if not intro_audio or len(intro_audio) < 100:
                logger.warning("⚠️  Edge TTS falló, usando Google TTS para intro...")
                intro_audio = synthesize_speech_gtts(intro_text)
            
            if intro_audio:
                play_audio(intro_audio)
                logger.info("✅ Introducción reproducida")
                return intro_text
        
        logger.warning("⚠️  No se pudo generar la introducción")
        return None
    except Exception as e:
        logger.error(f"❌ Error generando introducción: {e}")
        return None


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
    mode = config.get("mode", "topics")
    monologue_theme = config.get("monologue_theme", "inteligencia artificial")
    
    # Validar modelo de Piper
    if not Path(model_path).exists():
        logger.error(f"❌ Modelo de Piper no encontrado: {model_path}")
        logger.info("💡 Descarga un modelo de voz y colócalo en models/piper/")
        logger.info("   Modelos disponibles en: https://github.com/rhasspy/piper/releases")
        return
    
    logger.info(f"🌐 Proveedor LLM: {provider.upper()}")
    logger.info(f"🤖 Modelo LLM: {model_name}")
    logger.info(f"🎤 Modelo TTS: {model_path}")
    logger.info(f"🎭 Modo: {mode.upper()}")
    if mode == "monologue":
        logger.info(f"🧠 Tema del monólogo: {monologue_theme}")
    logger.info(f"⏱️  Duración por segmento: {duration_seconds}s")
    logger.info(f"🔊 Sample rate: {sample_rate} Hz")
    logger.info("=" * 60)
    
    # Inicializar historial de sesión
    history_dir = config.get("history_dir", "history")
    session_history = SessionHistory(history_dir)
    session_id = session_history.start_session()
    logger.info(f"📝 Sesión iniciada: {session_id}")
    logger.info("=" * 60)
    
    # Reproducir introducción
    if not skip_intro:
        intro_text = play_intro(model_name, model_path, provider=provider, api_key=api_key, max_tokens=200, edge_voice=config.get("edge_voice", "es-CO-SalomeNeural"))
        if intro_text:
            session_history.add_intro(intro_text, config.get("edge_voice", "es-CO-SalomeNeural"), 15.0)
        time.sleep(delay_seconds)
    
    # Iniciar bucle principal
    logger.info("🔄 Iniciando bucle de transmisión continua...")
    logger.info("⌨️  Presiona Ctrl+C para detener la transmisión")
    logger.info("=" * 60)
    
    iteration = 0
    consecutive_errors = 0
    previous_content = None  # Para modo monólogo
    
    # Variables para generación en paralelo
    next_segment = None  # (texto, audio, topic, tts_provider)
    generation_thread = None
    
    def generate_next_segment(prev_content=None):
        """Genera el siguiente segmento en segundo plano"""
        # En modo monólogo, siempre usar el tema configurado
        segment_topic = monologue_theme if mode == "monologue" else None
        
        return generate_segment(
            model_name=model_name,
            model_path=model_path,
            duration_seconds=duration_seconds,
            topic=segment_topic,
            provider=provider,
            api_key=api_key,
            max_tokens=max_tokens,
            llm_timeout=config.get("llm_timeout", 30),
            edge_voice=config.get("edge_voice", "es-CO-SalomeNeural"),
            mode=mode,
            previous_content=prev_content
        )
    
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
            
            # Si hay un segmento pre-generado, usarlo
            if next_segment is not None and generation_thread is not None:
                logger.info("⚡ Usando segmento pre-generado (sin espera)")
                generation_thread.join()  # Esperar a que termine si aún no lo hizo
                texto, audio, topic, tts_provider = next_segment
                next_segment = None
            else:
                # Primera iteración: generar normalmente
                # En modo monólogo, siempre usar el tema configurado
                segment_topic = monologue_theme if mode == "monologue" else None
                
                texto, audio, topic, tts_provider = generate_segment(
                    model_name=model_name,
                    model_path=model_path,
                    duration_seconds=duration_seconds,
                    topic=segment_topic,
                    provider=provider,
                    api_key=api_key,
                    max_tokens=max_tokens,
                    llm_timeout=config.get("llm_timeout", 30),
                    edge_voice=config.get("edge_voice", "es-CO-SalomeNeural"),
                    mode=mode,
                    previous_content=previous_content
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
            
            # INICIAR GENERACIÓN DEL SIGUIENTE SEGMENTO EN PARALELO
            # Mientras se reproduce el actual, generar el siguiente
            if max_iterations is None or iteration < max_iterations:
                logger.info("🔄 Generando siguiente segmento en segundo plano...")
                
                def generate_and_store():
                    nonlocal next_segment
                    try:
                        # Pasar contenido previo solo en modo monólogo
                        prev = previous_content if mode == "monologue" else None
                        next_segment = generate_next_segment(prev_content=prev)
                    except Exception as e:
                        logger.error(f"❌ Error generando siguiente segmento: {e}")
                        next_segment = None
                
                generation_thread = threading.Thread(target=generate_and_store, daemon=True)
                generation_thread.start()
            
            # Reproducir audio (mientras el siguiente se genera en paralelo)
            logger.info("🔊 Reproduciendo segmento...")
            play_audio(audio, sample_rate=sample_rate)
            
            # Guardar segmento en historial
            session_history.add_segment(
                topic=topic,
                text=texto,
                voice=config.get("edge_voice", "es-CO-SalomeNeural"),
                duration=duration_seconds,
                tts_provider=tts_provider
            )
            
            # Actualizar contenido previo para modo monólogo
            if mode == "monologue":
                previous_content = texto
            
            logger.info(f"✅ Segmento #{iteration} completado exitosamente")
            
            # Pausa mínima (el siguiente segmento ya debería estar listo)
            if delay_seconds > 0:
                if generation_thread and generation_thread.is_alive():
                    logger.info(f"⏳ Esperando que termine generación del siguiente segmento...")
                else:
                    logger.info(f"⚡ Siguiente segmento ya listo - sin pausa")
                time.sleep(delay_seconds)
        
        except KeyboardInterrupt:
            logger.info("\n" + "=" * 60)
            logger.info("⏹️  Interrupción recibida (Ctrl+C)")
            logger.info("🎙️  Deteniendo Radio IA...")
            session_history.end_session()
            logger.info(f"💾 Sesión guardada: {session_id}")
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
    
    # Asegurar que se guarde la sesión al finalizar
    session_history.end_session()
    
    logger.info("\n" + "=" * 60)
    logger.info(f"📊 ESTADÍSTICAS FINALES")
    logger.info(f"   Sesión ID: {session_id}")
    logger.info(f"   Segmentos generados: {iteration}")
    logger.info(f"   Errores consecutivos: {consecutive_errors}")
    logger.info("=" * 60)
    logger.info("💾 Para ver el historial: python src/main.py --list-sessions")
    logger.info(f"💾 Para reproducir esta sesión: python src/main.py --replay {session_id}")
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
