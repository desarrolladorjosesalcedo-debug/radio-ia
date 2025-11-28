"""
Session History Manager
Guarda y reproduce sesiones completas de radio con todos sus segmentos.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class SessionHistory:
    """Gestiona el historial de sesiones de radio."""
    
    def __init__(self, history_dir: str = "history"):
        """
        Inicializa el gestor de historial.
        
        Args:
            history_dir: Directorio donde guardar las sesiones
        """
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(exist_ok=True)
        self.current_session = None
        self.session_file = None
    
    def start_session(self) -> str:
        """
        Inicia una nueva sesión de radio.
        
        Returns:
            ID de la sesión (timestamp)
        """
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session = {
            "session_id": session_id,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "intro": None,
            "segments": []
        }
        self.session_file = self.history_dir / f"session_{session_id}.json"
        self._save_current_session()
        return session_id
    
    def add_intro(self, intro_text: str, voice: str, duration: float):
        """
        Agrega la introducción de la sesión.
        
        Args:
            intro_text: Texto de la introducción
            voice: Voz utilizada
            duration: Duración del audio en segundos
        """
        if self.current_session:
            self.current_session["intro"] = {
                "text": intro_text,
                "voice": voice,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
            self._save_current_session()
    
    def add_segment(self, topic: str, text: str, voice: str, 
                    duration: float, tts_provider: str = "edge"):
        """
        Agrega un segmento a la sesión actual.
        
        Args:
            topic: Tema del segmento
            text: Contenido del segmento
            voice: Voz utilizada
            duration: Duración del audio en segundos
            tts_provider: Proveedor de TTS usado (edge, gtts, piper)
        """
        if self.current_session:
            segment = {
                "number": len(self.current_session["segments"]) + 1,
                "topic": topic,
                "text": text,
                "voice": voice,
                "duration": duration,
                "tts_provider": tts_provider,
                "timestamp": datetime.now().isoformat()
            }
            self.current_session["segments"].append(segment)
            self._save_current_session()
    
    def end_session(self):
        """Finaliza la sesión actual."""
        if self.current_session:
            self.current_session["end_time"] = datetime.now().isoformat()
            total_duration = sum(
                seg["duration"] for seg in self.current_session["segments"]
            )
            if self.current_session["intro"]:
                total_duration += self.current_session["intro"]["duration"]
            
            self.current_session["total_duration"] = total_duration
            self.current_session["total_segments"] = len(
                self.current_session["segments"]
            )
            self._save_current_session()
            self.current_session = None
            self.session_file = None
    
    def _save_current_session(self):
        """Guarda la sesión actual en el archivo JSON."""
        if self.session_file and self.current_session:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_session, f, indent=2, ensure_ascii=False)
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Obtiene una sesión por su ID.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Datos de la sesión o None si no existe
        """
        session_file = self.history_dir / f"session_{session_id}.json"
        if session_file.exists():
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def list_sessions(self, limit: int = 10) -> List[Dict]:
        """
        Lista las últimas sesiones guardadas.
        
        Args:
            limit: Número máximo de sesiones a listar
            
        Returns:
            Lista de metadatos de sesiones
        """
        sessions = []
        session_files = sorted(
            self.history_dir.glob("session_*.json"),
            reverse=True
        )[:limit]
        
        for session_file in session_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sessions.append({
                        "session_id": data["session_id"],
                        "start_time": data["start_time"],
                        "end_time": data.get("end_time"),
                        "total_segments": data.get("total_segments", len(data["segments"])),
                        "total_duration": data.get("total_duration", 0)
                    })
            except Exception as e:
                print(f"Error leyendo {session_file}: {e}")
        
        return sessions
    
    def delete_old_sessions(self, keep_last: int = 20):
        """
        Elimina sesiones antiguas, manteniendo solo las más recientes.
        
        Args:
            keep_last: Número de sesiones a mantener
        """
        session_files = sorted(
            self.history_dir.glob("session_*.json"),
            reverse=True
        )
        
        for session_file in session_files[keep_last:]:
            try:
                session_file.unlink()
                print(f"Sesión eliminada: {session_file.name}")
            except Exception as e:
                print(f"Error eliminando {session_file}: {e}")
    
    def get_session_text(self, session_id: str) -> str:
        """
        Obtiene todo el texto de una sesión en formato legible.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Texto completo de la sesión
        """
        session = self.get_session(session_id)
        if not session:
            return f"Sesión {session_id} no encontrada"
        
        lines = []
        lines.append("=" * 60)
        lines.append(f"SESIÓN DE RADIO: {session['session_id']}")
        lines.append(f"Inicio: {session['start_time']}")
        if session.get('end_time'):
            lines.append(f"Fin: {session['end_time']}")
        lines.append(f"Segmentos: {session.get('total_segments', 0)}")
        lines.append(f"Duración total: {session.get('total_duration', 0):.1f}s")
        lines.append("=" * 60)
        lines.append("")
        
        if session.get("intro"):
            lines.append("🎙️ INTRODUCCIÓN:")
            lines.append("-" * 60)
            lines.append(session["intro"]["text"])
            lines.append("")
        
        for i, segment in enumerate(session["segments"], 1):
            lines.append(f"📻 SEGMENTO {i}: {segment['topic']}")
            lines.append("-" * 60)
            lines.append(segment["text"])
            lines.append("")
        
        return "\n".join(lines)
