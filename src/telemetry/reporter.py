from typing import Dict, Any, List
from src.telemetry.collector import TelemetryCollector


class BenchmarkReporter:
    """Formats raw performance telemetry and accuracy results into summary tables and reports."""

    @staticmethod
    def generate_summary(collector: TelemetryCollector, model_name: str, active_legs: int) -> Dict[str, Any]:
        lat_stats = collector.get_latency_percentiles()
        rtf = collector.get_rtf()
        snapshot = collector.collect_snapshot()

        return {
            "model_name": model_name,
            "concurrent_legs": active_legs,
            "rtf": round(rtf, 4),
            "latency_p50_ms": round(lat_stats["p50"], 2),
            "latency_p95_ms": round(lat_stats["p95"], 2),
            "latency_p99_ms": round(lat_stats["p99"], 2),
            "avg_latency_ms": round(lat_stats["avg"], 2),
            "cpu_percent": round(snapshot.cpu_percent, 2),
            "ram_mb": round(snapshot.ram_mb, 2),
        }

    @staticmethod
    def format_markdown_table(summary_list: List[Dict[str, Any]]) -> str:
        lines = [
            "| Model | Concurrent Legs | Target RTF | P50 Latency (ms) | P95 Latency (ms) | CPU % | RAM (MB) |",
            "|---|---|---|---|---|---|---|",
        ]
        for item in summary_list:
            lines.append(
                f"| {item['model_name']} | {item['concurrent_legs']} | {item['rtf']} | "
                f"{item['latency_p50_ms']} | {item['latency_p95_ms']} | {item['cpu_percent']}% | {item['ram_mb']} |"
            )
        return "\n".join(lines)
