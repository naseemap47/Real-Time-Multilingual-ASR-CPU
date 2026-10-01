import pytest
import json
from fastapi.testclient import TestClient
from src.api.main import app
from src.utils.audio_utils import parse_wav_header, generate_synthetic_pcm_wav


def test_rest_health_and_models():
    client = TestClient(app)
    
    # Test /api/health
    resp_health = client.get("/api/health")
    assert resp_health.status_code == 200
    assert resp_health.json()["status"] == "ok"

    # Test /api/models
    resp_models = client.get("/api/models")
    assert resp_models.status_code == 200
    models_list = resp_models.json()["models"]
    assert len(models_list) >= 4
    model_ids = [m["id"] for m in models_list]
    assert "qwen3_asr" in model_ids
    assert "parakeet_tdt" in model_ids
    assert "moonshine" in model_ids
    assert "whisper_turbo" in model_ids


def test_websocket_audio_streaming():
    client = TestClient(app)

    with client.websocket_connect("/ws/asr") as websocket:
        # Send start control frame
        websocket.send_text(json.dumps({
            "action": "start",
            "session_id": "test_ws_session_1",
            "model": "qwen3_asr",
            "language": "en"
        }))

        # Receive connection confirmation
        data = websocket.receive_json()
        assert data["event"] == "connected"
        assert data["session_id"] == "test_ws_session_1"

        # Send binary PCM audio chunk (6400 bytes = 200ms)
        dummy_pcm = b"\x00" * 6400
        websocket.send_bytes(dummy_pcm)

        # Receive transcript push
        tx_data = websocket.receive_json()
        assert tx_data["event"] == "transcript"
        assert tx_data["session_id"] == "test_ws_session_1"
        assert tx_data["chunk_index"] == 1
        assert "text" in tx_data

        # Send stop control frame
        websocket.send_text(json.dumps({"action": "stop", "session_id": "test_ws_session_1"}))

        # Receive final transcript push and EOS
        final_data = websocket.receive_json()
        assert final_data["event"] == "transcript"
        assert final_data["is_final"] is True

        eos_data = websocket.receive_json()
        assert eos_data["event"] == "eos"
        assert eos_data["status"] == "completed"


def test_wav_utility_parsing():
    wav_bytes = generate_synthetic_pcm_wav(duration_seconds=1.0, sample_rate=16000)
    parsed = parse_wav_header(wav_bytes)
    assert parsed["sample_rate"] == 16000
    assert parsed["channels"] == 1
    assert parsed["sample_width"] == 2
    assert parsed["duration_seconds"] == 1.0
    assert len(parsed["pcm_payload"]) == 32000
