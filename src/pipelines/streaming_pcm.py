from typing import List
from src.pipelines.base import BasePipelineAdapter


class StreamingPCMPipeline(BasePipelineAdapter):
    """Real-Time Fixed Window PCM Audio Pipeline."""

    def __init__(self, chunk_duration_ms: int = 200, target_sample_rate: int = 16000):
        self.chunk_duration_ms = chunk_duration_ms
        self.target_sample_rate = target_sample_rate

    def process_raw_audio(self, raw_audio: bytes, input_sample_rate: int = 16000) -> List[bytes]:
        normalized = self.normalize_pcm(raw_audio, input_sample_rate=input_sample_rate)
        return self.chunk_stream(normalized, chunk_duration_ms=self.chunk_duration_ms)
