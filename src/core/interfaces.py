from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from src.core.schema import EngineConfig, TranscriptResult, AudioChunk, SessionState


class BaseASREngine(ABC):
    """Abstract Base Class for all pluggable ASR model engine adapters."""

    @abstractmethod
    def load_model(self, config: EngineConfig) -> None:
        """Pre-load model weights and set up CPU execution context."""
        pass

    @abstractmethod
    async def create_stream_session(self, session_id: str, language: Optional[str] = None) -> SessionState:
        """Initialize a new stateful recognition session for a call leg."""
        pass

    @abstractmethod
    async def process_chunk(self, session_id: str, pcm_bytes: bytes, is_last: bool = False) -> TranscriptResult:
        """Process an incoming audio chunk and return partial/final transcript."""
        pass

    @abstractmethod
    async def unload_session(self, session_id: str) -> None:
        """Clean up call leg session context."""
        pass

    @abstractmethod
    def unload_model(self) -> None:
        """Unload model from RAM."""
        pass


class BaseAudioPipeline(ABC):
    """Abstract Base Class for audio preprocessing and chunking pipelines."""

    @abstractmethod
    def normalize_pcm(self, raw_audio: bytes, input_sample_rate: int = 16000) -> bytes:
        """Normalize raw audio bytes to 16kHz mono 16-bit Linear PCM."""
        pass

    @abstractmethod
    def chunk_stream(self, pcm_bytes: bytes, chunk_duration_ms: int = 200) -> List[bytes]:
        """Split continuous PCM stream into framed chunks."""
        pass
