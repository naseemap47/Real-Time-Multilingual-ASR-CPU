import time
import psutil
import numpy as np
from typing import List, Dict, Optional
from src.core.schema import TelemetryMetrics


class TelemetryCollector:
    """Collects runtime CPU, memory, RTF, and latency percentiles (P50, P95, P99)."""

    def __init__(self, active_legs: int = 1):
        self.active_legs = active_legs
        self.latencies_ms: List[float] = []
        self.processing_times_sec: List[float] = []
        self.audio_durations_sec: List[float] = []
        self.process = psutil.Process()

    def record_chunk_processed(self, latency_ms: float, processing_time_sec: float, audio_duration_sec: float) -> None:
        self.latencies_ms.append(latency_ms)
        self.processing_times_sec.append(processing_time_sec)
        self.audio_durations_sec.append(audio_duration_sec)

    def get_rtf(self) -> float:
        total_audio = sum(self.audio_durations_sec)
        if total_audio <= 0:
            return 0.0
        return sum(self.processing_times_sec) / total_audio

    def get_latency_percentiles(self) -> Dict[str, float]:
        if not self.latencies_ms:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "avg": 0.0}
        arr = np.array(self.latencies_ms)
        return {
            "p50": float(np.percentile(arr, 50)),
            "p95": float(np.percentile(arr, 95)),
            "p99": float(np.percentile(arr, 99)),
            "avg": float(np.mean(arr)),
        }

    def collect_snapshot(self, session_id: str = "global") -> TelemetryMetrics:
        cpu_pct = self.process.cpu_percent(interval=None)
        mem_info = self.process.memory_info()
        ram_mb = mem_info.rss / (1024.0 * 1024.0)

        lat_stats = self.get_latency_percentiles()
        return TelemetryMetrics(
            session_id=session_id,
            ttft_ms=lat_stats["p50"],
            partial_latency_ms=lat_stats["avg"],
            final_latency_ms=lat_stats["p95"],
            rtf=self.get_rtf(),
            cpu_percent=cpu_pct,
            ram_mb=ram_mb,
            active_legs=self.active_legs,
            timestamp=time.time()
        )
