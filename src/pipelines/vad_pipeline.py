from typing import List
import numpy as np
from src.pipelines.base import BasePipelineAdapter


class VADBufferedPipeline(BasePipelineAdapter):
    """Voice Activity Detection (VAD) driven buffering audio pipeline."""

    def __init__(self, silence_threshold_energy: float = 100.0, chunk_duration_ms: int = 200):
        self.silence_threshold_energy = silence_threshold_energy
        self.chunk_duration_ms = chunk_duration_ms

    def is_speech(self, pcm_chunk: bytes) -> bool:
        if len(pcm_chunk) < 2:
            return False
        audio_samples = np.frombuffer(pcm_chunk, dtype=np.int16)
        energy = float(np.mean(np.abs(audio_samples)))
        return energy > self.silence_threshold_energy

    def process_raw_audio_with_vad(self, raw_audio: bytes, input_sample_rate: int = 16000) -> List[dict]:
        normalized = self.normalize_pcm(raw_audio, input_sample_rate=input_sample_rate)
        chunks = self.chunk_stream(normalized, chunk_duration_ms=self.chunk_duration_ms)
        
        results = []
        for idx, chunk in enumerate(chunks):
            has_speech = self.is_speech(chunk)
            results.append({
                "chunk_index": idx,
                "data": chunk,
                "is_speech": has_speech
            })
        return results
