"""
Session Replay
Reproduce sesiones guardadas de Radio IA sin pausas.
"""

import logging
import time
from pathlib import Path
from typing import Optional

from core.session_history import SessionHistory
from tts.piper_tts import synthesize_speech
from tts.edge_tts_client import synthesize_speech_edge
from tts.gtts_client import synthesize_speech_gtts
from utils.audio_player import play_audio
from core.radio_loop import load_config

logger = logging.getLogger(__name__)


def replay_session(
    session_id: str,
    delay_seconds: float = 2.0,
    history_dir: str = "history"
) -> bool:
    """
    Reproduce una sesión guardada sin pausas largas.
    
    Args:
        session_id: ID de la sesión a reproducir
        delay_seconds: Pausa breve entre segmentos (default: 2s)
        history_dir: Directorio de historial
        
    Returns:
        True si se reprodujo exitosamente, False si hubo errores
    """
    logger.info("=" * 60)
    logger.info(f"🎙️  REPRODUCIENDO SESIÓN: {session_id}")
    logger.info("=" * 60)
    
    # Cargar configuración
    config = load_config()
    sample_rate = config["sample_rate"]
    model_path = config["model_path"]
    edge_voice = config.get("edge_voice", "es-CO-SalomeNeural")
    
    # Cargar sesión
    session_history = SessionHistory(history_dir)
    session = session_history.get_session(session_id)
    
    if not session:
        logger.error(f"❌ Sesión {session_id} no encontrada")
        return False
    
    logger.info(f"📅 Fecha: {session['start_time']}")
    logger.info(f"📊 Segmentos: {len(session['segments'])}")
    logger.info(f"⏱️  Duración total: {session.get('total_duration', 0):.1f}s")
    logger.info("=" * 60)
    
    try:
        # Reproducir introducción si existe
        if session.get("intro"):
            logger.info("🎙️  Reproduciendo introducción...")
            intro_text = session["intro"]["text"]
            intro_audio = _synthesize_with_fallback(
                intro_text, model_path, edge_voice
            )
            
            if intro_audio:
                play_audio(intro_audio, sample_rate=sample_rate)
                logger.info("✅ Introducción reproducida")
                time.sleep(delay_seconds)
            else:
                logger.warning("⚠️  No se pudo generar audio de introducción")
        
        # Reproducir cada segmento
        for i, segment in enumerate(session["segments"], 1):
            logger.info(f"\n{'=' * 60}")
            logger.info(f"📻 SEGMENTO #{i}: {segment['topic']}")
            logger.info(f"{'=' * 60}")
            
            # Sintetizar audio del segmento
            audio = _synthesize_with_fallback(
                segment["text"], model_path, edge_voice
            )
            
            if not audio:
                logger.warning(f"⚠️  No se pudo generar audio del segmento #{i}")
                continue
            
            # Reproducir sin pausa larga
            logger.info("🔊 Reproduciendo...")
            play_audio(audio, sample_rate=sample_rate)
            logger.info(f"✅ Segmento #{i} completado")
            
            # Pausa breve entre segmentos
            if i < len(session["segments"]) and delay_seconds > 0:
                time.sleep(delay_seconds)
        
        logger.info("\n" + "=" * 60)
        logger.info(f"✅ Sesión {session_id} reproducida completamente")
        logger.info("=" * 60)
        return True
        
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("⏹️  Reproducción interrumpida (Ctrl+C)")
        logger.info("=" * 60)
        return False
    
    except Exception as e:
        logger.error(f"❌ Error durante la reproducción: {e}")
        return False


def _synthesize_with_fallback(
    text: str,
    model_path: str,
    edge_voice: str
) -> Optional[bytes]:
    """
    Sintetiza audio con sistema de fallback.
    
    Args:
        text: Texto a sintetizar
        model_path: Ruta al modelo de Piper
        edge_voice: Voz de Edge TTS
        
    Returns:
        Audio en bytes o None si falla
    """
    # Intentar Piper
    try:
        audio = synthesize_speech(text, model_path)
        if audio and len(audio) > 100:
            return audio
    except Exception as e:
        logger.debug(f"Piper falló: {e}")
    
    # Intentar Edge TTS
    try:
        audio = synthesize_speech_edge(text, voice=edge_voice)
        if audio and len(audio) > 100:
            return audio
    except Exception as e:
        logger.debug(f"Edge TTS falló: {e}")
    
    # Intentar Google TTS
    try:
        audio = synthesize_speech_gtts(text)
        if audio and len(audio) > 100:
            return audio
    except Exception as e:
        logger.debug(f"Google TTS falló: {e}")
    
    return None


def show_session_list(history_dir: str = "history", limit: int = 20):
    """
    Muestra lista de sesiones guardadas.
    
    Args:
        history_dir: Directorio de historial
        limit: Número máximo de sesiones a mostrar
    """
    session_history = SessionHistory(history_dir)
    sessions = session_history.list_sessions(limit=limit)
    
    if not sessions:
        print("📭 No hay sesiones guardadas")
        return
    
    print("\n" + "=" * 70)
    print("📻 HISTORIAL DE SESIONES DE RADIO IA")
    print("=" * 70)
    
    for i, session in enumerate(sessions, 1):
        print(f"\n{i}. Sesión: {session['session_id']}")
        print(f"   📅 Inicio: {session['start_time']}")
        if session.get('end_time'):
            print(f"   🏁 Fin: {session['end_time']}")
        print(f"   📊 Segmentos: {session.get('total_segments', 0)}")
        print(f"   ⏱️  Duración: {session.get('total_duration', 0):.1f}s")
    
    print("\n" + "=" * 70)
    print(f"Total: {len(sessions)} sesiones")
    print("=" * 70)
    print("\n💡 Para reproducir: python src/main.py --replay SESSION_ID")
    print("💡 Para ver texto completo: python src/main.py --show SESSION_ID")


def show_session_text(session_id: str, history_dir: str = "history"):
    """
    Muestra el texto completo de una sesión.
    
    Args:
        session_id: ID de la sesión
        history_dir: Directorio de historial
    """
    session_history = SessionHistory(history_dir)
    text = session_history.get_session_text(session_id)
    print(text)
