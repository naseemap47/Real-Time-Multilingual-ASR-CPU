import asyncio
import time
from typing import Optional
from src.engines.base import BaseEngineAdapter
from src.core.schema import EngineConfig, TranscriptResult


class Qwen3ASREngine(BaseEngineAdapter):
    """Engine adapter for Qwen3-ASR model family executing on CPU."""

    def __init__(self, config: Optional[EngineConfig] = None):
        super().__init__(config)
        self.runtime_variant = "0.6b"
        self.cpu_threads = 4
        if config:
            self.load_model(config)

    def load_model(self, config: EngineConfig) -> None:
        super().load_model(config)
        self.runtime_variant = config.model_params.get("variant", "0.6b")
        self.cpu_threads = config.cpu_threads


    async def process_chunk(self, session_id: str, pcm_bytes: bytes, is_last: bool = False) -> TranscriptResult:
        start_t = time.time()
        session = self.sessions.get(session_id)
        lang = session.language if session else "en"
        
        chunk_duration_sec = len(pcm_bytes) / 32000.0
        if session:
            session.processed_chunks += 1
            session.total_audio_seconds += chunk_duration_sec

        chunk_idx = session.processed_chunks if session else 1
        
        # Qwen3 multilingual stream processing simulation
        prefix = f"[Qwen3-{self.runtime_variant} ({lang})]"
        text = f"{prefix} Chunk {chunk_idx} transcribed"
        if is_last:
            text += " [EOS Final]"
            
        if session:
            session.accumulated_transcript = text

        # Simulated real-time CPU batch inference delay
        await asyncio.sleep(0.015)
        latency_ms = (time.time() - start_t) * 1000.0

        return TranscriptResult(
            session_id=session_id,
            chunk_index=chunk_idx,
            text=text,
            is_final=is_last,
            language=lang,
            confidence=0.92,
            latency_ms=latency_ms,
            timestamp=time.time()
        )
