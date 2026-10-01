from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np
from src.core.interfaces import BaseAudioPipeline



class BasePipelineAdapter(BaseAudioPipeline):
    """Common implementation wrapper for Audio Pipelines."""

    def normalize_pcm(self, raw_audio: bytes, input_sample_rate: int = 16000) -> bytes:
        """Baseline normalization for 16kHz 16-bit mono PCM."""
        if input_sample_rate != 16000:
            # Simple downsampling / upsampling ratio logic if sample rates differ
            ratio = 16000 / input_sample_rate
            # Ensure 16-bit alignment (2 bytes per sample)
            sample_count = len(raw_audio) // 2
            indices = (np.arange(int(sample_count * ratio)) / ratio).astype(int)
            indices = np.clip(indices, 0, sample_count - 1)
            audio_array = np.frombuffer(raw_audio, dtype=np.int16)
            resampled_array = audio_array[indices]
            return resampled_array.tobytes()
        return raw_audio

    def chunk_stream(self, pcm_bytes: bytes, chunk_duration_ms: int = 200) -> List[bytes]:
        """Split continuous 16kHz mono PCM (32 bytes per ms) into fixed chunks."""
        bytes_per_ms = 32  # 16000 samples/sec * 2 bytes/sample / 1000 ms
        chunk_bytes_size = chunk_duration_ms * bytes_per_ms
        
        chunks = []
        for i in range(0, len(pcm_bytes), chunk_bytes_size):
            chunks.append(pcm_bytes[i:i + chunk_bytes_size])
        return chunks
