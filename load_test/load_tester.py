import asyncio
import json
import time
import websockets
from typing import Dict, Any, List
from src.utils.audio_utils import generate_synthetic_pcm_wav, parse_wav_header
from src.utils.logger import get_logger

logger = get_logger("LoadTester")


class SingleCallLegRunner:
    """Simulates a single active voice call leg over WebSocket."""

    def __init__(self, server_url: str, session_id: str, model: str = "qwen3_asr", language: str = "en", audio_bytes: bytes = None):
        self.server_url = server_url
        self.session_id = session_id
        self.model = model
        self.language = language
        self.audio_bytes = audio_bytes or generate_synthetic_pcm_wav(duration_seconds=2.0)
        self.latencies_ms: List[float] = []
        self.is_completed = False

    async def run(self, pacing: bool = True):
        parsed = parse_wav_header(self.audio_bytes)
        pcm_data = parsed["pcm_payload"]
        
        # 200ms chunk = 6400 bytes
        chunk_size = 6400
        chunks = [pcm_data[i:i + chunk_size] for i in range(0, len(pcm_data), chunk_size)]

        async with websockets.connect(self.server_url) as ws:
            # Send start configuration frame
            await ws.send(json.dumps({
                "action": "start",
                "session_id": self.session_id,
                "model": self.model,
                "language": self.language
            }))

            # Wait for connection acknowledgment
            init_resp = await ws.recv()

            # Stream audio chunks at real-time pace
            for chunk in chunks:
                start_t = time.time()
                await ws.send(chunk)
                resp_str = await ws.recv()
                lat_ms = (time.time() - start_t) * 1000.0
                self.latencies_ms.append(lat_ms)

                if pacing:
                    # Pace chunk delivery to emulate 200ms real-time audio rate
                    await asyncio.sleep(0.20)

            # Send stop action frame
            await ws.send(json.dumps({"action": "stop", "session_id": self.session_id}))
            
            # Read final transcript and EOS frames
            await ws.recv() # Final transcript
            await ws.recv() # EOS completion frame
            self.is_completed = True


class ConcurrentLoadTester:
    """Orchestrates N concurrent call leg runners and calculates capacity performance metrics."""

    def __init__(self, server_url: str = "ws://localhost:8000/ws/asr", model: str = "qwen3_asr"):
        self.server_url = server_url
        self.model = model

    async def run_concurrency_test(self, num_concurrent_legs: int, audio_duration_sec: float = 2.0) -> Dict[str, Any]:
        audio_bytes = generate_synthetic_pcm_wav(duration_seconds=audio_duration_sec)
        runners = [
            SingleCallLegRunner(
                server_url=self.server_url,
                session_id=f"load_test_leg_{i}",
                model=self.model,
                audio_bytes=audio_bytes
            )
            for i in range(num_concurrent_legs)
        ]

        start_time = time.time()
        tasks = [runner.run(pacing=False) for runner in runners]
        await asyncio.gather(*tasks, return_exceptions=True)
        total_test_duration = time.time() - start_time

        completed = sum(1 for r in runners if r.is_completed)
        all_latencies = []
        for r in runners:
            all_latencies.extend(r.latencies_ms)

        avg_lat = sum(all_latencies) / len(all_latencies) if all_latencies else 0.0
        
        return {
            "requested_legs": num_concurrent_legs,
            "completed_legs": completed,
            "total_test_duration_sec": round(total_test_duration, 2),
            "avg_latency_ms": round(avg_lat, 2),
            "throughput_chunks_per_sec": round(len(all_latencies) / total_test_duration, 2) if total_test_duration > 0 else 0.0
        }
