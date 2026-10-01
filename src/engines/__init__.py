from typing import Dict, Type
from src.core.interfaces import BaseASREngine
from src.engines.base import BaseEngineAdapter
from src.engines.mock_engine import MockASREngine
from src.engines.qwen3_engine import Qwen3ASREngine
from src.engines.parakeet_engine import ParakeetTDTEngine
from src.engines.moonshine_engine import MoonshineEngine
from src.engines.whisper_engine import WhisperLargeV3TurboEngine


class EngineFactory:
    """Dynamic Engine Factory for instantiating pluggable ASR model adapters."""

    _ENGINES: Dict[str, Type[BaseEngineAdapter]] = {
        "mock": MockASREngine,
        "qwen3_asr": Qwen3ASREngine,
        "parakeet_tdt": ParakeetTDTEngine,
        "moonshine": MoonshineEngine,
        "whisper_turbo": WhisperLargeV3TurboEngine,
    }

    @classmethod
    def get_engine_class(cls, model_name: str) -> Type[BaseEngineAdapter]:
        if model_name not in cls._ENGINES:
            raise ValueError(f"Unknown engine '{model_name}'. Available engines: {list(cls._ENGINES.keys())}")
        return cls._ENGINES[model_name]

    @classmethod
    def create_engine(cls, model_name: str) -> BaseEngineAdapter:
        engine_cls = cls.get_engine_class(model_name)
        return engine_cls()

    @classmethod
    def list_available_engines(cls) -> list[str]:
        return list(cls._ENGINES.keys())
