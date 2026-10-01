# Modular Real-Time Multilingual ASR Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a modular, pluggable Real-Time Multilingual ASR system on CPU with support for Qwen3-ASR, NVIDIA Parakeet TDT 0.6B, Moonshine (Tiny/Base), and OpenAI Whisper Large V3 Turbo, including audio streaming pipelines, telemetry collector, load tester, FastAPI WebSocket server, and modern Web UI.

**Architecture:** Unified Plugin-Based Engine Adapter & Pipeline model using abstract base classes (`BaseASREngine`, `BaseAudioPipeline`), YAML configuration loading, FastAPI WebSocket protocol streaming, real-time CPU/RAM/RTF telemetry, and load test simulator.

**Tech Stack:** Python 3.10+, FastAPI, WebSockets, Pydantic v2, PyYAML, NumPy, PyTest, HTML5/CSS3/JavaScript (Vanilla).

**Spec:** [docs/superpowers/specs/2026-10-01-asr-architecture-design.md](file:///home/naseem/Projects/Real-Time-Multilingual-ASR-CPU/docs/superpowers/specs/2026-10-01-asr-architecture-design.md)

## Global Constraints
- Target CPU-only execution (no GPU required for core runtime).
- 16 kHz Mono Linear PCM input baseline audio format.
- Languages supported: English (`en`), Mandarin Chinese (`zh`), Bahasa Indonesia (`id`).
- Strict modular separation between core interfaces, engine plugins, audio pipelines, telemetry, API layer, load testing, and Web UI.

---

### Task 1: Project Environment & Core Interfaces Scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `config/default_config.yaml`
- Create: `config/models/qwen3_asr.yaml`
- Create: `config/models/parakeet_tdt.yaml`
- Create: `config/models/moonshine.yaml`
- Create: `config/models/whisper_turbo.yaml`
- Create: `src/core/schema.py`
- Create: `src/core/interfaces.py`
- Create: `src/core/config.py`
- Test: `tests/test_core.py`

**Interfaces:**
- Produces: `AudioChunk`, `TranscriptResult`, `TelemetryMetrics`, `EngineConfig`, `BaseASREngine`, `BaseAudioPipeline`, `AppConfig`

- [ ] **Step 1: Write requirements.txt**
Create `requirements.txt` with dependencies: `fastapi`, `uvicorn`, `websockets`, `pydantic`, `pyyaml`, `numpy`, `psutil`, `pytest`, `requests`.

- [ ] **Step 2: Create YAML configuration files**
Create `config/default_config.yaml` and model configs under `config/models/`.

- [ ] **Step 3: Define Pydantic Schemas in `src/core/schema.py`**
Implement data models for `AudioChunk`, `TranscriptResult`, `TelemetryMetrics`, `SessionState`, `EngineConfig`.

- [ ] **Step 4: Define Abstract Interfaces in `src/core/interfaces.py`**
Implement `BaseASREngine` and `BaseAudioPipeline` abstract base classes.

- [ ] **Step 5: Define Config Loader in `src/core/config.py`**
Implement YAML configuration parsing and validation.

- [ ] **Step 6: Write unit tests in `tests/test_core.py`**
Verify schemas and config loading with `pytest`.

- [ ] **Step 7: Run tests to verify pass**
Run `pytest tests/test_core.py -v`.

- [ ] **Step 8: Commit**
`git add . && git commit -m "feat: setup project scaffolding, schemas, configs, and abstract interfaces"`

---

### Task 2: Implement ASR Engine Adapters (Plugins)

**Files:**
- Create: `src/engines/base.py`
- Create: `src/engines/mock_engine.py`
- Create: `src/engines/qwen3_engine.py`
- Create: `src/engines/parakeet_engine.py`
- Create: `src/engines/moonshine_engine.py`
- Create: `src/engines/whisper_engine.py`
- Create: `src/engines/__init__.py`
- Test: `tests/test_engines.py`

**Interfaces:**
- Consumes: `BaseASREngine`, `EngineConfig`, `TranscriptResult`
- Produces: `EngineFactory.get_engine(model_name: str) -> BaseASREngine`

- [ ] **Step 1: Write `src/engines/base.py` and `mock_engine.py`**
Implement lightweight Mock Engine for instant local testing and CI without needing 5GB model weights.

- [ ] **Step 2: Implement `qwen3_engine.py`**
Qwen3-ASR engine adapter with CPU streaming & chunking logic.

- [ ] **Step 3: Implement `parakeet_engine.py`**
NVIDIA Parakeet TDT 0.6B engine adapter.

- [ ] **Step 4: Implement `moonshine_engine.py`**
Moonshine (Tiny / Base) engine adapter.

- [ ] **Step 5: Implement `whisper_engine.py`**
OpenAI Whisper Large V3 Turbo engine adapter.

- [ ] **Step 6: Implement Engine Factory in `src/engines/__init__.py`**
Dynamic engine loader supporting model selection by key name.

- [ ] **Step 7: Write unit tests in `tests/test_engines.py`**
Test engine instantiation, session creation, and chunk recognition via Mock and dynamic plugins.

- [ ] **Step 8: Run tests to verify pass**
Run `pytest tests/test_engines.py -v`.

- [ ] **Step 9: Commit**
`git add . && git commit -m "feat: implement pluggable ASR engine adapters (Qwen3, Parakeet TDT, Moonshine, Whisper Turbo, Mock)"`

---

### Task 3: Implement Audio Pipelines & Telemetry Engine

**Files:**
- Create: `src/pipelines/base.py`
- Create: `src/pipelines/streaming_pcm.py`
- Create: `src/pipelines/vad_pipeline.py`
- Create: `src/pipelines/__init__.py`
- Create: `src/telemetry/collector.py`
- Create: `src/telemetry/accuracy.py`
- Create: `src/telemetry/reporter.py`
- Create: `src/telemetry/__init__.py`
- Test: `tests/test_pipelines_and_telemetry.py`

**Interfaces:**
- Consumes: `AudioChunk`, `TranscriptResult`
- Produces: `StreamingPCMPipeline`, `VADBufferedPipeline`, `TelemetryCollector`, `AccuracyEvaluator`

- [ ] **Step 1: Implement Audio Pipelines in `src/pipelines/`**
Implement PCM chunking/resampling pipeline and VAD-buffered utterance pipeline.

- [ ] **Step 2: Implement Telemetry Collector in `src/telemetry/collector.py`**
Track process CPU utilization, thread counts, memory usage (baseline & peak), RTF, and latency percentiles (P50, P95, P99).

- [ ] **Step 3: Implement Accuracy & Report Generator**
WER & CER calculation tools in `accuracy.py` and benchmark summarizer in `reporter.py`.

- [ ] **Step 4: Write unit tests in `tests/test_pipelines_and_telemetry.py`**
Test PCM chunking and telemetry stats calculation.

- [ ] **Step 5: Run tests**
Run `pytest tests/test_pipelines_and_telemetry.py -v`.

- [ ] **Step 6: Commit**
`git add . && git commit -m "feat: add audio pipelines and telemetry collection module"`

---

### Task 4: FastAPI Server, WebSocket Streaming & Call Leg Manager

**Files:**
- Create: `src/utils/logger.py`
- Create: `src/utils/audio_utils.py`
- Create: `src/api/call_leg_manager.py`
- Create: `src/api/websocket_handler.py`
- Create: `src/api/routes.py`
- Create: `src/api/main.py`
- Test: `tests/test_websocket_api.py`

**Interfaces:**
- Consumes: `EngineFactory`, `TelemetryCollector`, `BaseAudioPipeline`
- Produces: FastAPI App with REST endpoints (`/api/health`, `/api/models`) and WebSocket `/ws/asr`

- [ ] **Step 1: Implement Audio Utils & Logger in `src/utils/`**
WAV header parser, 16kHz PCM validator, and logger.

- [ ] **Step 2: Implement Call Leg Session Manager in `src/api/call_leg_manager.py`**
Manage multi-call leg session state, active connections, and lifecycle.

- [ ] **Step 3: Implement WebSocket Handler in `src/api/websocket_handler.py`**
Handle binary PCM chunk streaming, model inference calls, partial/final response delivery, and latency telemetry pushes.

- [ ] **Step 4: Create FastAPI entrypoint `src/api/main.py`**
Assemble routes, WebSocket handlers, static file hosting for Web UI, and CORS middleware.

- [ ] **Step 5: Write unit tests in `tests/test_websocket_api.py`**
Test REST endpoints and WebSocket stream lifecycle.

- [ ] **Step 6: Run tests**
Run `pytest tests/test_websocket_api.py -v`.

- [ ] **Step 7: Commit**
`git add . && git commit -m "feat: implement FastAPI server, call leg session manager, and WebSocket audio streamer"`

---

### Task 5: Load Test Simulator & Capacity Sizing Mechanism

**Files:**
- Create: `load_test/load_tester.py`
- Create: `load_test/scenarios/benchmark_concurrency.py`
- Create: `load_test/__init__.py`
- Test: `tests/test_load_tester.py`

**Interfaces:**
- Consumes: WebSocket API `/ws/asr`
- Produces: Simulated 50 to 1,000 concurrent call legs runner and sizing metrics table generator.

- [ ] **Step 1: Implement Load Tester in `load_test/load_tester.py`**
Asynchronously stream WAV audio chunks at real-time pace across N parallel call leg sessions.

- [ ] **Step 2: Implement Benchmark & Sizing Generator in `load_test/scenarios/benchmark_concurrency.py`**
Run concurrency benchmarks (50, 100, 200, 500, 1000 legs) and format capacity sizing output tables.

- [ ] **Step 3: Test Load Tester**
Run load test simulator against local server running Mock/Qwen3 engine.

- [ ] **Step 4: Commit**
`git add . && git commit -m "feat: add multi-call leg load test simulator and capacity sizing benchmark script"`

---

### Task 6: Modern Interactive Web UI Frontend

**Files:**
- Create: `web_ui/index.html`
- Create: `web_ui/styles.css`
- Create: `web_ui/app.js`

**Interfaces:**
- Consumes: WebSocket `/ws/asr`, REST `/api/models`
- Produces: Web UI for WAV loading, streaming controls, partial/final transcript display, real-time telemetry charts.

- [ ] **Step 1: Create HTML structure in `web_ui/index.html`**
WAV file loader, Model/Language selector, Start/Stop/Reset stream controls, transcript feed container, live latency/CPU dashboard.

- [ ] **Step 2: Create CSS styles in `web_ui/styles.css`**
Modern dark mode, glassmorphism UI, clean typography, badge indicators for stream status (CONNECTED, STREAMING, END_OF_STREAM).

- [ ] **Step 3: Create JS logic in `web_ui/app.js`**
WAV audio parser/chunker, real-time audio chunk streamer over WebSocket, transcript append logic distinguishing partial vs final text, and live metrics renderer.

- [ ] **Step 4: Commit**
`git add . && git commit -m "feat: create modern web UI for real-time WAV streaming and telemetry visualization"`

---

### Task 7: Complete Documentation & Project Verification

**Files:**
- Modify: `README.md`
- Create: `docs/architecture.md`

- [ ] **Step 1: Update `README.md`**
Comprehensive documentation for installation, model downloading, running backend service, using Web UI, running load tests, and capacity sizing.

- [ ] **Step 2: Create `docs/architecture.md`**
Detailed technical architecture report, streaming design, production deployment guide, and capacity model.

- [ ] **Step 3: Run full test suite**
Run `pytest -v` across all test modules.

- [ ] **Step 4: Commit**
`git add . && git commit -m "docs: finalize README, architecture documentation, and complete verification"`
