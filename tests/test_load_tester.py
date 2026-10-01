import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from load_test.load_tester import ConcurrentLoadTester
from load_test.scenarios.benchmark_concurrency import generate_capacity_sizing_table


def test_capacity_sizing_table_generation():
    sample_results = [
        {"requested_legs": 50, "completed_legs": 50, "avg_latency_ms": 12.5},
        {"requested_legs": 100, "completed_legs": 100, "avg_latency_ms": 18.2},
        {"requested_legs": 200, "completed_legs": 200, "avg_latency_ms": 25.0},
        {"requested_legs": 500, "completed_legs": 500, "avg_latency_ms": 45.0},
        {"requested_legs": 1000, "completed_legs": 1000, "avg_latency_ms": 95.0},
    ]

    table = generate_capacity_sizing_table(sample_results)
    assert "| 50 |" in table
    assert "| 100 |" in table
    assert "| 200 |" in table
    assert "| 500 |" in table
    assert "| 1000 |" in table
    assert "vCPUs" in table
