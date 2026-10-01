# Real-Time Multilingual ASR on CPU

A modular, high-performance Speech-to-Text (ASR) framework optimized for real-time multilingual voice call workloads executing on **CPU-only** hardware. 

Designed for low-latency streaming evaluation across **English**, **Mandarin Chinese**, and **Bahasa Indonesia**.

---

## 🌟 Key Features
- **Pluggable ASR Engine Architecture**: Easily switch between model engines via YAML configs:
  - **Qwen3-ASR Multilingual (0.6B)**
  - **NVIDIA Parakeet TDT (0.6B)**
  - **Moonshine ASR (Tiny / Base)**
  - **OpenAI Whisper Large V3 Turbo**
  - **Mock Engine** (Lightweight simulator for instant CI/testing)
- **Real-Time Streaming Protocol**: WebSocket backend streaming 200ms 16kHz Linear PCM audio chunks.
- **Real-Time Telemetry**: Live dashboard for CPU utilization, RAM usage, Real-Time Factor (RTF), and P50/P95/P99 latency metrics.
- **Load Testing & Capacity Sizing**: Multi-call leg benchmark simulator (50 to 1,000 concurrent legs).
- **Modern Web UI**: Interactive dashboard for WAV streaming, transcript visualization, and live metrics.

---

## 🚀 Quick Start

### 1. Prerequisites & Environment Setup
Using `uv` package manager:
```bash
# Clone the repository
git clone https://github.com/naseem/Real-Time-Multilingual-ASR-CPU.git
cd Real-Time-Multilingual-ASR-CPU

# Create virtual environment and sync dependencies
uv sync
```

### 2. Run API Server & Web UI
```bash
# Start FastAPI WebSocket Server & Web UI
uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser and navigate to:
👉 **`http://localhost:8000/ui/`**

---

## 🧪 Testing & Load Benchmarking

### Run Unit Test Suite
```bash
uv run pytest -v
```

### Run Multi-Call Leg Capacity Benchmark
```bash
uv run python -m load_test.scenarios.benchmark_concurrency
```

---

## 📁 Project Structure

```
Real-Time-Multilingual-ASR-CPU/
├── config/
│   ├── default_config.yaml       # Global server & audio settings
│   └── models/                   # Pluggable model YAML configs
│       ├── qwen3_asr.yaml
│       ├── parakeet_tdt.yaml
│       ├── moonshine.yaml
│       └── whisper_turbo.yaml
├── docs/
│   └── architecture.md           # Technical architecture & sizing guide
├── src/
│   ├── core/                     # Abstract interfaces & Pydantic schemas
│   ├── engines/                  # Pluggable ASR model engine adapters
│   ├── pipelines/                # Streaming PCM & VAD audio pipelines
│   ├── telemetry/                # Metrics collector, WER/CER & reporter
│   ├── api/                      # FastAPI REST & WebSocket streaming server
│   └── utils/                    # Audio parsing & logging utilities
├── load_test/                    # Load tester & concurrency simulator
├── web_ui/                       # Web UI dashboard (HTML/CSS/JS)
├── tests/                        # Comprehensive PyTest test suite
├── pyproject.toml                # Project metadata & dependencies
└── README.md
```

---

## 📜 License
MIT License.