import asyncio
import time
from typing import Optional
from src.engines.base import BaseEngineAdapter
from src.core.schema import EngineConfig, TranscriptResult


class MockASREngine(BaseEngineAdapter):
    """Mock ASR Engine simulating real-time speech recognition on CPU."""

    MOCK_PHRASES = {
        "en": ["Hello world", "Welcome to Tetherfi voice services", "Testing real time ASR on CPU"],
        "zh": ["你好世界", "欢迎使用语音识别服务", "测试 CPU 实时语音识别"],
        "id": ["Halo dunia", "Selamat datang di layanan suara Tetherfi", "Uji coba ASR real time pada CPU"]
    }

    async def process_chunk(self, session_id: str, pcm_bytes: bytes, is_last: bool = False) -> TranscriptResult:
        start_t = time.time()
        session = self.sessions.get(session_id)
        lang = session.language if session else "en"
        
        # Calculate chunk audio duration (16kHz, 16-bit = 32,000 bytes/sec)
        chunk_duration_sec = len(pcm_bytes) / 32000.0
        if session:
            session.processed_chunks += 1
            session.total_audio_seconds += chunk_duration_sec

        phrase_list = self.MOCK_PHRASES.get(lang, self.MOCK_PHRASES["en"])
        chunk_idx = session.processed_chunks if session else 1
        phrase = phrase_list[(chunk_idx - 1) % len(phrase_list)]

        if is_last:
            text = f"{phrase} [Final]"
            is_final = True
        else:
            text = f"{phrase} (part {chunk_idx})"
            is_final = False

        if session:
            session.accumulated_transcript = text

        # Simulate small CPU inference latency (10-20ms)
        await asyncio.sleep(0.01)
        latency_ms = (time.time() - start_t) * 1000.0

        return TranscriptResult(
            session_id=session_id,
            chunk_index=chunk_idx,
            text=text,
            is_final=is_final,
            language=lang,
            confidence=0.95,
            latency_ms=latency_ms,
            timestamp=time.time()
        )
