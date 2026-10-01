import pytest
from src.core.config import load_app_config
from src.engines import EngineFactory, MockASREngine, Qwen3ASREngine, ParakeetTDTEngine, MoonshineEngine, WhisperLargeV3TurboEngine


@pytest.mark.asyncio
async def test_engine_factory_registration():
    available = EngineFactory.list_available_engines()
    assert "mock" in available
    assert "qwen3_asr" in available
    assert "parakeet_tdt" in available
    assert "moonshine" in available
    assert "whisper_turbo" in available


@pytest.mark.asyncio
async def test_engine_lifecycle_and_recognition():
    app_config = load_app_config()

    for model_name in ["mock", "qwen3_asr", "parakeet_tdt", "moonshine", "whisper_turbo"]:
        engine = EngineFactory.create_engine(model_name)
        cfg = app_config.models.get(model_name)
        if cfg:
            engine.load_model(cfg)
            assert engine.is_loaded is True

        session = await engine.create_stream_session(session_id=f"test_session_{model_name}", language="en")
        assert session.session_id == f"test_session_{model_name}"

        # 200ms of 16kHz 16-bit mono PCM = 6400 bytes
        dummy_pcm = b"\x00" * 6400

        # Process partial chunk
        res_partial = await engine.process_chunk(session_id=session.session_id, pcm_bytes=dummy_pcm, is_last=False)
        assert res_partial.is_final is False
        assert res_partial.chunk_index == 1
        assert len(res_partial.text) > 0

        # Process final chunk
        res_final = await engine.process_chunk(session_id=session.session_id, pcm_bytes=dummy_pcm, is_last=True)
        assert res_final.is_final is True
        assert res_final.chunk_index == 2

        await engine.unload_session(session.session_id)
        engine.unload_model()
        assert engine.is_loaded is False
