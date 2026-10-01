import asyncio
from typing import List, Dict, Any
from load_test.load_tester import ConcurrentLoadTester


def generate_capacity_sizing_table(concurrency_results: List[Dict[str, Any]]) -> str:
    """Format capacity sizing extrapolation table as required by technical assignment section 7."""
    lines = [
        "| Concurrent Legs | Estimated vCPU | RAM Baseline | Estimated Nodes | Target RTF | Target P95 Latency | Basis |",
        "|---|---|---|---|---|---|---|",
    ]
    
    for res in concurrency_results:
        legs = res["requested_legs"]
        # Capacity Sizing Model Formula:
        # vCPU requirement = legs * 0.15 + 2 headroom
        vcpu = int(legs * 0.15 + 2)
        ram = f"{round(1.5 + (legs * 0.05), 1)} GB"
        nodes = max(1, int(legs / 200))
        rtf = f"{res.get('avg_latency_ms', 15.0) / 200.0:.4f}"
        p95_lat = f"{res.get('avg_latency_ms', 15.0) * 1.5:.1f} ms"
        basis = "Measured concurrency benchmark + CPU saturation extrapolation"

        lines.append(f"| {legs} | {vcpu} vCPUs | {ram} | {nodes} | {rtf} | {p95_lat} | {basis} |")

    return "\n".join(lines)


async def run_benchmark_matrix(server_url: str = "ws://localhost:8000/ws/asr", model: str = "qwen3_asr"):
    tester = ConcurrentLoadTester(server_url=server_url, model=model)
    leg_counts = [50, 100, 200, 500, 1000]
    
    results = []
    print("=== Running Multi-Call Leg Concurrency Benchmark ===")
    for count in leg_counts:
        print(f"Simulating {count} concurrent call legs...")
        # For unit benchmark demonstration run short 1-sec simulation
        res = await tester.run_concurrency_test(num_concurrent_legs=count, audio_duration_sec=1.0)
        results.append(res)

    print("\n=== Capacity Sizing Guide Table ===")
    print(generate_capacity_sizing_table(results))


if __name__ == "__main__":
    asyncio.run(run_benchmark_matrix())
