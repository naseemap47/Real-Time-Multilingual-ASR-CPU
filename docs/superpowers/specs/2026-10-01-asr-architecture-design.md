# Design Specification: Modular Real-Time Multilingual ASR System on CPU

## 1. Overview & System Architecture
This design establishes a modular, pluggable architecture for real-time speech recognition (ASR) executing on CPU-only infrastructure for multilingual voice call legs (English, Mandarin Chinese, Bahasa Indonesia).

The system decouples **ASR Inference Engines**, **Audio Preprocessing & Chunking Pipelines**, **Streaming Protocol / API Services**, **Telemetry & Benchmarking**, and **Load Test Simulation**.

```
                           +------------------------+
                           |  Web UI / Load Tester  |
                           +-----------+------------+
                                       |
                             WebSocket | (Linear PCM audio chunks)
                                       v
                           +------------------------+
                           | FastAPI WebServer /    |
                           | Call Leg Session Mgr   |
                           +-----------+------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
       +-----------------------+               +-----------------------+
       | Audio Pipeline Layer  |               | Telemetry & Metrics   |
       | (VAD / PCM Chunking)  |               | (CPU/RAM/RTF/Latency) |
       +-----------+-----------+               +-----------------------+
                   |                                       ^
                   v                                       |
       +-----------------------+                           |
       |   Engine Factory &    |---------------------------+
       |   Model Adapters      |
       +-----------+-----------+
                   |
     +-------------+-------------+------------------+-------------------+
     |                           |                  |                   |
     v                           v                  v                   v
+----+---------+        +--------+-------+   +------+--------+  +-------+--------+
| Qwen3-ASR    |        | NVIDIA Parakeet|   | Moonshine     |  | Whisper Large  |
| Engine       |        | TDT 0.6B Engine|   | (Tiny / Base) |  | VAD V3 Turbo   |
+--------------+        +----------------+   +---------------+  +----------------+
```

---

## 2. Model & Engine Architecture (Plugin Pattern)

### Abstract Base Interface (`src/core/interfaces.py`)
All model runtimes implement a standard asynchronous interface `BaseASREngine`:

- `async load_model(config: EngineConfig) -> None`: Pre-loads weight, allocates CPU threads, and initializes session cache.
- `async create_stream_session(session_id: str, language: Optional[str]) -> BaseStreamSession`: Spawns a stateful call-leg recognition context.
- `async process_chunk(session_id: str, audio_pcm: bytes, is_last: bool) -> TranscriptResult`: Processes incoming audio chunk and returns partial/final transcript.
- `async unload_model() -> None`: Cleans up memory and resources.

### Supported Model Engine Adapters (`src/engines/`)
1. **`Qwen3ASREngine`** (`qwen3_engine.py`): Primary candidate supporting multilingual streaming & chunked recognition on CPU.
2. **`ParakeetTDTEngine`** (`parakeet_engine.py`): NVIDIA Parakeet TDT 0.6B (Token-and-Duration Transducer) optimized for low-latency streaming speech recognition.
3. **`MoonshineEngine`** (`moonshine_engine.py`): Moonshine Tiny (27M) & Base (61M) ONNX models tailored for fast, resource-constrained CPU inference.
4. **`WhisperLargeV3TurboEngine`** (`whisper_engine.py`): OpenAI Whisper Large V3 Turbo running via `faster-whisper` (CTranslate2 INT8 CPU backend) or ONNX Runtime.
5. **`MockASREngine`** (`mock_engine.py`): Lightweight dummy engine simulating real-time transcript streaming and latency without requiring heavy ML weights (ideal for CI, UI testing, and load-test framework validation).

---

## 3. Audio & Pipeline Abstraction (`src/pipelines/`)

### Abstract Pipeline Interface (`BaseAudioPipeline`)
Normalizes input PCM streams, manages audio window buffering, handles VAD (Voice Activity Detection), and chunks streams cleanly before feeding model engines.

- **`StreamingPCMPipeline`**: Fixed-window chunking (e.g. 100ms, 200ms, 500ms frames) with linear resampling (converting any sample rate to 16kHz mono 16-bit PCM).
- **`VADBufferedPipeline`**: Silero/WebRTC VAD driven pipeline that isolates speech segments, detects silence/end-of-utterance, and emits finalized text segments at utterance boundaries.

---

## 4. Telemetry, Benchmarking & Capacity Sizing (`src/telemetry/`)

### Metrics Tracked:
- **Latency**:
  - `TTFT` (Time To First Transcript / Partial Result).
  - `Partial Latency`: Delay between chunk submission and partial output.
  - `P50 / P95 / P99 Final Latency`: End-of-utterance final transcript delivery delay.
- **Real-Time Factor (RTF)**: `Processing Duration / Audio Duration`. (RTF < 1.0 indicates faster than real-time).
- **Resource Saturation**: Process CPU % (per physical/logical core), RAM baseline memory, peak RAM, and thread contention.
- **Accuracy**: WER (Word Error Rate for English & Indonesian) and CER (Character Error Rate for Mandarin Chinese) using standard text normalization rules.

### Load Test Engine (`load_test/load_tester.py`)
- Asynchronously spawns 1 to 1,000 parallel audio streaming clients.
- Measures latency percentiles, queue drop rates, RTF degradation, and CPU throughput under high leg counts.
- Outputs sizing matrices and capacity extrapolation reports.

---

## 5. Directory & File Structure Blueprint

```
Real-Time-Multilingual-ASR-CPU/
├── config/
│   ├── default_config.yaml
│   └── models/
│       ├── qwen3_asr.yaml
│       ├── parakeet_tdt.yaml
│       ├── moonshine.yaml
│       └── whisper_turbo.yaml
├── docs/
│   └── architecture.md
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── interfaces.py
│   │   ├── schema.py
│   │   └── config.py
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── qwen3_engine.py
│   │   ├── parakeet_engine.py
│   │   ├── moonshine_engine.py
│   │   ├── whisper_engine.py
│   │   └── mock_engine.py
│   ├── pipelines/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── streaming_pcm.py
│   │   └── vad_pipeline.py
│   ├── telemetry/
│   │   ├── __init__.py
│   │   ├── collector.py
│   │   ├── accuracy.py
│   │   └── reporter.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routes.py
│   │   ├── websocket_handler.py
│   │   └── call_leg_manager.py
│   └── utils/
│       ├── __init__.py
│       ├── audio_utils.py
│       └── logger.py
├── load_test/
│   ├── __init__.py
│   ├── load_tester.py
│   └── scenarios/
├── web_ui/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── tests/
│   ├── test_engines.py
│   ├── test_pipelines.py
│   └── test_websocket.py
├── requirements.txt
└── README.md
```
