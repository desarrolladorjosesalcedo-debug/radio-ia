"""
api_server.py
Servidor web FastAPI para controlar Radio IA desde el navegador.

Este módulo expone endpoints REST que permiten controlar la radio
sin modificar la lógica existente de radio_loop.py

Endpoints:
- POST /api/start      - Iniciar radio
- POST /api/pause      - Pausar radio
- POST /api/resume     - Reanudar radio
- POST /api/stop       - Detener radio
- POST /api/set_mode   - Cambiar modo (topics/monologue)
- GET  /api/status     - Estado actual
- GET  /api/list_sessions - Listar sesiones guardadas
- POST /api/play_session/{session_id} - Reproducir sesión

Uso:
    python api_server.py
    # Abre http://localhost:8000 en tu navegador
"""

import sys
import logging
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

# Agregar src/ al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.radio_loop import start_radio, load_config
from core.replay import show_session_list, replay_session
from utils.audio_output import set_output_mode
from audio_stream_manager import stream_manager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== FASTAPI APP ==========

app = FastAPI(
    title="Radio IA API",
    description="API REST para controlar Radio IA",
    version="1.0.0"
)

# Configurar CORS para permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar carpeta estática para servir el frontend
web_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=web_dir / "static"), name="static")

# ========== ESTADO GLOBAL ==========

class RadioState:
    """Estado global de la radio"""
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.current_mode = "topics"
        self.current_theme = ""
        self.radio_thread: Optional[threading.Thread] = None
        self.stop_flag = threading.Event()
        self.pause_flag = threading.Event()
        self.status = "stopped"  # stopped, running, paused, generating, playing
        
    def reset(self):
        """Resetea el estado pero mantiene las instancias de los flags"""
        self.is_running = False
        self.is_paused = False
        self.stop_flag.clear()
        self.pause_flag.clear()
        self.status = "stopped"
        # NO crear nuevos flags, mantener las mismas instancias

radio_state = RadioState()

# ========== MODELOS PYDANTIC ==========

class StartRequest(BaseModel):
    mode: str = "topics"  # topics, monologue, reader
    theme: Optional[str] = None
    skip_intro: bool = False
    enable_streaming: bool = True  # Por defecto streaming para Render.com

class SetModeRequest(BaseModel):
    mode: str  # topics, monologue, reader

class StatusResponse(BaseModel):
    status: str
    mode: str
    is_running: bool
    is_paused: bool
    theme: Optional[str] = None

# ========== FUNCIONES DE CONTROL ==========

def radio_worker(mode: str, theme: Optional[str], skip_intro: bool, stop_flag: threading.Event, pause_flag: threading.Event, enable_streaming: bool = False):
    """
    Worker que ejecuta la radio en un thread separado
    """
    try:
        logger.info(f"🎙️ Iniciando radio - Modo: {mode}, Tema: {theme}, Streaming: {enable_streaming}")
        radio_state.status = "running"
        
        # Configurar modo de salida de audio
        if enable_streaming:
            set_output_mode("streaming", stream_manager)
            stream_manager.start_streaming()
        else:
            set_output_mode("local", None)
        
        # Configuración
        config = load_config()
        
        # Actualizar configuración según parámetros
        if mode == "monologue" and theme:
            # Guardar tema en configuración temporal
            # (start_radio no acepta tema directamente, se usa de settings.yaml)
            # Aquí podrías modificar settings.yaml temporalmente o pasar el tema
            pass
        
        # Iniciar radio con flags de control
        start_radio(
            delay_seconds=config.get("delay_seconds", 2.0),
            skip_intro=skip_intro,
            stop_flag=stop_flag,
            pause_flag=pause_flag
        )
        
    except Exception as e:
        logger.error(f"❌ Error en radio worker: {e}")
        radio_state.status = "stopped"
        radio_state.is_running = False
    finally:
        if enable_streaming:
            stream_manager.stop_streaming()
        radio_state.reset()

# ========== ENDPOINTS ==========

@app.get("/")
async def root():
    """Sirve la página principal"""
    return FileResponse(web_dir / "index.html")

@app.post("/api/start")
async def start(request: StartRequest):
    """
    Inicia la radio
    """
    if radio_state.is_running:
        raise HTTPException(status_code=400, detail="Ya hay una transmisión en curso. Deténla primero.")
    
    try:
        # Limpiar flags antes de iniciar (por si quedaron activos de ejecuciones anteriores)
        radio_state.stop_flag.clear()
        radio_state.pause_flag.clear()
        
        # Actualizar estado
        radio_state.current_mode = request.mode
        radio_state.current_theme = request.theme or ""
        radio_state.is_running = True
        radio_state.status = "running"
        
        # Crear y lanzar thread de radio
        radio_state.radio_thread = threading.Thread(
            target=radio_worker,
            args=(
                request.mode, 
                request.theme, 
                request.skip_intro, 
                radio_state.stop_flag, 
                radio_state.pause_flag,
                request.enable_streaming  # Pasar flag de streaming
            ),
            daemon=True
        )
        radio_state.radio_thread.start()
        
        logger.info(f"✅ Radio iniciada - Modo: {request.mode}")
        
        return {
            "success": True,
            "message": f"Radio iniciada en modo {request.mode.upper()}",
            "mode": request.mode,
            "theme": request.theme
        }
    
    except Exception as e:
        logger.error(f"❌ Error al iniciar radio: {e}")
        radio_state.reset()
        raise HTTPException(status_code=500, detail=f"Error al iniciar: {str(e)}")

@app.post("/api/pause")
async def pause():
    """
    Pausa la radio
    """
    if not radio_state.is_running:
        raise HTTPException(status_code=400, detail="La radio no está en ejecución")
    
    if radio_state.is_paused:
        raise HTTPException(status_code=400, detail="La radio ya está en pausa")
    
    # Activar flag de pausa
    radio_state.is_paused = True
    radio_state.pause_flag.set()
    radio_state.status = "paused"
    
    logger.info("⏸️  Radio pausada")
    
    return {
        "success": True,
        "message": "Radio pausada",
        "status": "paused"
    }

@app.post("/api/resume")
async def resume():
    """
    Reanuda la radio
    """
    if not radio_state.is_running:
        raise HTTPException(status_code=400, detail="La radio no está en ejecución")
    
    if not radio_state.is_paused:
        raise HTTPException(status_code=400, detail="La radio no está en pausa")
    
    # Desactivar flag de pausa
    radio_state.is_paused = False
    radio_state.pause_flag.clear()
    radio_state.status = "running"
    
    logger.info("▶️  Radio reanudada")
    
    return {
        "success": True,
        "message": "Radio reanudada",
        "status": "running"
    }

@app.post("/api/stop")
async def stop():
    """
    Detiene la radio
    """
    if not radio_state.is_running:
        raise HTTPException(status_code=400, detail="La radio no está en ejecución")
    
    try:
        # Señalizar detención (activar flag)
        radio_state.stop_flag.set()
        
        # Si está en pausa, también desbloquear
        if radio_state.is_paused:
            radio_state.pause_flag.clear()
        
        radio_state.status = "stopped"
        
        # Esperar a que el thread termine (con timeout)
        if radio_state.radio_thread:
            radio_state.radio_thread.join(timeout=5.0)
        
        radio_state.reset()
        
        logger.info("⏹️  Radio detenida")
        
        return {
            "success": True,
            "message": "Radio detenida",
            "status": "stopped"
        }
    
    except Exception as e:
        logger.error(f"❌ Error al detener radio: {e}")
        radio_state.reset()
        raise HTTPException(status_code=500, detail=f"Error al detener: {str(e)}")

@app.post("/api/set_mode")
async def set_mode(request: SetModeRequest):
    """
    Cambia el modo de operación
    """
    valid_modes = ["topics", "monologue", "reader"]
    
    if request.mode not in valid_modes:
        raise HTTPException(
            status_code=400,
            detail=f"Modo inválido. Opciones: {', '.join(valid_modes)}"
        )
    
    radio_state.current_mode = request.mode
    
    logger.info(f"🔄 Modo cambiado a: {request.mode}")
    
    return {
        "success": True,
        "message": f"Modo cambiado a {request.mode.upper()}",
        "mode": request.mode
    }

@app.get("/api/status")
async def get_status():
    """
    Obtiene el estado actual de la radio
    """
    return StatusResponse(
        status=radio_state.status,
        mode=radio_state.current_mode,
        is_running=radio_state.is_running,
        is_paused=radio_state.is_paused,
        theme=radio_state.current_theme if radio_state.current_theme else None
    )

@app.get("/api/list_sessions")
async def list_sessions():
    """
    Lista todas las sesiones guardadas
    """
    try:
        config = load_config()
        history_dir = Path(config.get("history_dir", "history"))
        
        if not history_dir.exists():
            return {"sessions": []}
        
        # Buscar archivos de sesión
        session_files = sorted(history_dir.glob("session_*.json"), reverse=True)
        
        sessions = []
        for session_file in session_files:
            try:
                # Extraer ID de sesión del nombre del archivo
                session_id = session_file.stem.replace("session_", "")
                
                # Leer el archivo JSON para obtener los segmentos reales
                import json
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                # Obtener metadata
                stats = session_file.stat()
                date = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M")
                
                # Contar segmentos desde el JSON
                segments_count = len(session_data.get("segments", []))
                total_duration = sum(seg.get("duration", 20) for seg in session_data.get("segments", []))
                
                sessions.append({
                    "id": session_id,
                    "date": date,
                    "segments": segments_count,
                    "duration": f"{total_duration}s"
                })
            
            except Exception as e:
                logger.warning(f"⚠️  Error procesando sesión {session_file}: {e}")
                continue
        
        logger.info(f"📋 Listadas {len(sessions)} sesiones")
        
        return {
            "success": True,
            "sessions": sessions,
            "total": len(sessions)
        }
    
    except Exception as e:
        logger.error(f"❌ Error listando sesiones: {e}")
        raise HTTPException(status_code=500, detail=f"Error listando sesiones: {str(e)}")

@app.post("/api/play_session/{session_id}")
async def play_session_endpoint(session_id: str):
    """
    Reproduce una sesión guardada
    """
    # Verificar que no haya nada corriendo
    if radio_state.is_running:
        raise HTTPException(
            status_code=400, 
            detail="Ya hay una transmisión en curso. Deténla antes de reproducir una sesión."
        )
    
    try:
        config = load_config()
        history_dir = config.get("history_dir", "history")
        
        # Validar que la sesión existe
        session_path = Path(history_dir) / f"session_{session_id}.json"
        if not session_path.exists():
            raise HTTPException(status_code=404, detail=f"Sesión {session_id} no encontrada")
        
        # Limpiar flags antes de iniciar (por si quedaron activos de ejecuciones anteriores)
        radio_state.stop_flag.clear()
        radio_state.pause_flag.clear()
        
        # Actualizar estado - ahora es una reproducción activa
        radio_state.is_running = True
        radio_state.is_paused = False
        radio_state.status = "playing"
        radio_state.current_mode = "replay"
        
        # Lanzar replay en thread separado con flags de control
        def replay_worker():
            try:
                logger.info(f"🔊 Reproduciendo sesión {session_id}")
                replay_session(
                    session_id, 
                    delay_seconds=2.0, 
                    history_dir=history_dir,
                    stop_flag=radio_state.stop_flag,
                    pause_flag=radio_state.pause_flag
                )
            except Exception as e:
                logger.error(f"❌ Error reproduciendo sesión: {e}")
            finally:
                # Resetear estado al terminar
                radio_state.reset()
        
        radio_state.radio_thread = threading.Thread(target=replay_worker, daemon=True)
        radio_state.radio_thread.start()
        
        logger.info(f"✅ Reproducción de sesión {session_id} iniciada")
        
        return {
            "success": True,
            "message": f"Reproduciendo sesión {session_id}",
            "session_id": session_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al reproducir sesión: {e}")
        radio_state.reset()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ========== ENDPOINTS DE STREAMING ==========

@app.get("/api/stream/audio")
async def stream_audio():
    """
    Endpoint de streaming de audio en tiempo real
    Los clientes se conectan aquí para recibir el audio de la radio
    """
    logger.info("🎧 Nuevo cliente conectado al stream de audio")
    
    return StreamingResponse(
        stream_manager.get_audio_stream(),
        media_type="audio/mpeg",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Content-Type-Options": "nosniff"
        }
    )

@app.get("/api/stream/info")
async def stream_info():
    """
    Obtiene información del stream actual
    """
    return stream_manager.get_current_info()

# ========== MAIN ==========

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🎙️  RADIO IA - SERVIDOR WEB")
    print("=" * 60)
    print()
    print("📡 Servidor iniciando en http://localhost:8000")
    print("🌐 Abre tu navegador en: http://localhost:8000")
    print()
    print("Presiona Ctrl+C para detener el servidor")
    print("=" * 60)
    print()
    
    # Iniciar servidor
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
