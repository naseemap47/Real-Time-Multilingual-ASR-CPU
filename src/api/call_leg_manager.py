from typing import Dict, Optional
import time
from src.core.schema import SessionState
from src.engines import EngineFactory
from src.engines.base import BaseEngineAdapter
from src.telemetry import TelemetryCollector
from src.utils.logger import get_logger

logger = get_logger("CallLegManager")


class CallLegManager:
    """Manages active call leg streaming sessions and engine context routing."""

    def __init__(self):
        self.active_sessions: Dict[str, SessionState] = {}
        self.engines: Dict[str, BaseEngineAdapter] = {}
        self.telemetry_collector = TelemetryCollector(active_legs=0)

    def get_or_create_engine(self, model_name: str) -> BaseEngineAdapter:
        if model_name not in self.engines:
            logger.info(f"Instantiating engine adapter for model: {model_name}")
            engine = EngineFactory.create_engine(model_name)
            from src.core.config import load_app_config
            app_cfg = load_app_config()
            if model_name in app_cfg.models:
                engine.load_model(app_cfg.models[model_name])
            else:
                engine.is_loaded = True
            self.engines[model_name] = engine
        return self.engines[model_name]


    async def start_call_leg(self, session_id: str, model_name: str = "qwen3_asr", language: str = "en") -> SessionState:
        engine = self.get_or_create_engine(model_name)
        session = await engine.create_stream_session(session_id=session_id, language=language)
        self.active_sessions[session_id] = session
        self.telemetry_collector.active_legs = len(self.active_sessions)
        logger.info(f"Started call leg session '{session_id}' [model={model_name}, lang={language}]")
        return session

    async def end_call_leg(self, session_id: str) -> None:
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            if session.model_name in self.engines:
                await self.engines[session.model_name].unload_session(session_id)
            del self.active_sessions[session_id]
            self.telemetry_collector.active_legs = len(self.active_sessions)
            logger.info(f"Ended call leg session '{session_id}'")

    def get_active_legs_count(self) -> int:
        return len(self.active_sessions)
