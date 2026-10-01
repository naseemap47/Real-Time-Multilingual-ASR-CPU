import pytest
import os
from src.core.schema import AudioChunk, TranscriptResult, TelemetryMetrics, EngineConfig
from src.core.config import load_app_config


def test_schema_instantiation():
    chunk = AudioChunk(session_id="session_1", chunk_index=0, data=b"\x00" * 320)
    assert chunk.session_id == "session_1"
    assert chunk.sample_rate == 16000
    assert len(chunk.data) == 320

    transcript = TranscriptResult(session_id="session_1", chunk_index=0, text="Hello world", is_final=False)
    assert transcript.text == "Hello world"
    assert transcript.confidence == 1.0

    telemetry = TelemetryMetrics(session_id="session_1", rtf=0.15, cpu_percent=25.0)
    assert telemetry.rtf == 0.15


def test_config_loading():
    app_config = load_app_config(config_dir="config")
    assert app_config.server.port == 8000
    assert app_config.default_model == "qwen3_asr"
    
    # Check loaded model configs
    assert "qwen3_asr" in app_config.models
    assert "parakeet_tdt" in app_config.models
    assert "moonshine" in app_config.models
    assert "whisper_turbo" in app_config.models

    qwen_cfg = app_config.models["qwen3_asr"]
    assert qwen_cfg.display_name == "Qwen3-ASR Multilingual"
    assert "en" in qwen_cfg.languages
    assert qwen_cfg.device == "cpu"
