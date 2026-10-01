import pytest
from src.pipelines import PipelineFactory
from src.telemetry import TelemetryCollector, AccuracyEvaluator, BenchmarkReporter


def test_streaming_pcm_pipeline():
    pipeline = PipelineFactory.create_pipeline("streaming_pcm", chunk_duration_ms=200)
    # 1 second of 16kHz 16-bit mono PCM = 32,000 bytes
    dummy_audio = b"\x00" * 32000
    chunks = pipeline.process_raw_audio(dummy_audio, input_sample_rate=16000)
    # 1000ms / 200ms = 5 chunks
    assert len(chunks) == 5
    assert len(chunks[0]) == 6400  # 200ms * 32 bytes/ms


def test_vad_pipeline():
    pipeline = PipelineFactory.create_pipeline("vad_buffered", chunk_duration_ms=200)
    dummy_audio = b"\x00" * 32000
    results = pipeline.process_raw_audio_with_vad(dummy_audio, input_sample_rate=16000)
    assert len(results) == 5
    assert results[0]["is_speech"] is False


def test_telemetry_collector_and_reporter():
    collector = TelemetryCollector(active_legs=1)
    collector.record_chunk_processed(latency_ms=15.0, processing_time_sec=0.015, audio_duration_sec=0.200)
    collector.record_chunk_processed(latency_ms=25.0, processing_time_sec=0.020, audio_duration_sec=0.200)

    rtf = collector.get_rtf()
    assert rtf > 0.0
    assert rtf < 1.0

    percentiles = collector.get_latency_percentiles()
    assert percentiles["p50"] >= 15.0
    assert percentiles["p95"] <= 25.0

    summary = BenchmarkReporter.generate_summary(collector, model_name="qwen3_asr", active_legs=1)
    assert summary["model_name"] == "qwen3_asr"
    assert summary["concurrent_legs"] == 1
    table = BenchmarkReporter.format_markdown_table([summary])
    assert "qwen3_asr" in table


def test_accuracy_evaluator():
    # WER test English
    ref_en = "The quick brown fox jumps over the lazy dog"
    hyp_en = "The quick brown fox jumped over the lazy dog"
    wer = AccuracyEvaluator.calculate_wer(ref_en, hyp_en, language="en")
    assert wer > 0.0 and wer < 0.3

    # CER test Mandarin
    ref_zh = "欢迎使用语音识别服务"
    hyp_zh = "欢迎使用语音识别服务"
    cer = AccuracyEvaluator.calculate_cer(ref_zh, hyp_zh)
    assert cer == 0.0
