from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import time


class AudioChunk(BaseModel):
    """Represents a chunk of raw linear PCM audio data."""
    session_id: str
    chunk_index: int
    data: bytes
    sample_rate: int = 16000
    channels: int = 1
    sample_width: int = 2
    is_last: bool = False
    timestamp: float = Field(default_factory=time.time)


class TranscriptResult(BaseModel):
    """Represents recognition output emitted by an ASR engine."""
    session_id: str
    chunk_index: int
    text: str
    is_final: bool = False
    language: Optional[str] = None
    confidence: float = 1.0
    latency_ms: float = 0.0
    timestamp: float = Field(default_factory=time.time)


class TelemetryMetrics(BaseModel):
    """Telemetry data capturing runtime resource usage and latencies."""
    session_id: str
    ttft_ms: Optional[float] = None  # Time To First Transcript
    partial_latency_ms: float = 0.0
    final_latency_ms: Optional[float] = None
    rtf: float = 0.0  # Real-Time Factor
    cpu_percent: float = 0.0
    ram_mb: float = 0.0
    active_legs: int = 1
    timestamp: float = Field(default_factory=time.time)


class SessionState(BaseModel):
    """State descriptor for an active streaming call leg."""
    session_id: str
    language: str = "en"
    model_name: str = "qwen3_asr"
    pipeline_name: str = "streaming_pcm"
    start_time: float = Field(default_factory=time.time)
    total_audio_seconds: float = 0.0
    processed_chunks: int = 0
    accumulated_transcript: str = ""
    is_active: bool = True


class EngineConfig(BaseModel):
    """Configuration structure for instantiating an ASR Engine adapter."""
    name: str
    display_name: str
    version: str
    languages: List[str] = Field(default_factory=lambda: ["en", "zh", "id"])
    streaming_supported: bool = True
    cpu_threads: int = 4
    quantization: str = "int8"
    device: str = "cpu"
    context_window_ms: int = 3000
    model_params: Dict[str, Any] = Field(default_factory=dict)
