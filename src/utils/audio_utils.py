import wave
import io
from typing import Tuple, Dict, Any


def parse_wav_header(wav_bytes: bytes) -> Dict[str, Any]:
    """Parse WAV file binary content and extract sample rate, channels, sample width, and raw PCM payload."""
    with io.BytesIO(wav_bytes) as bio:
        with wave.open(bio, "rb") as wf:
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            sample_rate = wf.getframerate()
            num_frames = wf.getnframes()
            pcm_payload = wf.readframes(num_frames)
            
            return {
                "channels": channels,
                "sample_width": sample_width,
                "sample_rate": sample_rate,
                "num_frames": num_frames,
                "duration_seconds": num_frames / float(sample_rate),
                "pcm_payload": pcm_payload
            }


def generate_synthetic_pcm_wav(duration_seconds: float = 1.0, sample_rate: int = 16000) -> bytes:
    """Generate a clean synthetic 16kHz 16-bit mono PCM WAV file in memory for testing."""
    num_frames = int(sample_rate * duration_seconds)
    pcm_payload = b"\x00\x00" * num_frames
    
    bio = io.BytesIO()
    with wave.open(bio, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_payload)
    return bio.getvalue()
