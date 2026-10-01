from abc import ABC, abstractmethod
from typing import Optional, Dict
import time
from src.core.interfaces import BaseASREngine
from src.core.schema import EngineConfig, TranscriptResult, SessionState


class BaseEngineAdapter(BaseASREngine):
    """Common implementation wrapper for all ASR engine adapters."""

    def __init__(self, config: Optional[EngineConfig] = None):
        self.config = config
        self.is_loaded = False
        self.sessions: Dict[str, SessionState] = {}

    def load_model(self, config: EngineConfig) -> None:
        self.config = config
        self.is_loaded = True

    async def create_stream_session(self, session_id: str, language: Optional[str] = None) -> SessionState:
        session_lang = language or (self.config.languages[0] if self.config and self.config.languages else "en")
        model_name = self.config.name if self.config else "unknown"
        
        session = SessionState(
            session_id=session_id,
            language=session_lang,
            model_name=model_name,
            start_time=time.time(),
            total_audio_seconds=0.0,
            processed_chunks=0,
            accumulated_transcript="",
            is_active=True
        )
        self.sessions[session_id] = session
        return session

    async def unload_session(self, session_id: str) -> None:
        if session_id in self.sessions:
            self.sessions[session_id].is_active = False
            del self.sessions[session_id]

    def unload_model(self) -> None:
        self.is_loaded = False
        self.sessions.clear()
