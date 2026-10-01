import asyncio
import time
from typing import Optional
from src.engines.base import BaseEngineAdapter
from src.core.schema import EngineConfig, TranscriptResult


class MoonshineEngine(BaseEngineAdapter):
    """Engine adapter for Moonshine ASR (Tiny 27M / Base 61M) models."""

    def load_model(self, config: EngineConfig) -> None:
        super().load_model(config)
        self.variant = config.version or "base"

    async def process_chunk(self, session_id: str, pcm_bytes: bytes, is_last: bool = False) -> TranscriptResult:
        start_t = time.time()
        session = self.sessions.get(session_id)
        lang = session.language if session else "en"

        chunk_duration_sec = len(pcm_bytes) / 32000.0
        if session:
            session.processed_chunks += 1
            session.total_audio_seconds += chunk_duration_sec

        chunk_idx = session.processed_chunks if session else 1
        text = f"[Moonshine {self.variant.capitalize()} ({lang})] Frame {chunk_idx}"
        if is_last:
            text += " [Final]"

        if session:
            session.accumulated_transcript = text

        # Moonshine fast CPU inference simulation (~8ms on CPU for Tiny/Base)
        await asyncio.sleep(0.008)
        latency_ms = (time.time() - start_t) * 1000.0

        return TranscriptResult(
            session_id=session_id,
            chunk_index=chunk_idx,
            text=text,
            is_final=is_last,
            language=lang,
            confidence=0.94,
            latency_ms=latency_ms,
            timestamp=time.time()
        )
