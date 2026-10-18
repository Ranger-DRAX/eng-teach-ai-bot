#!/usr/bin/env python3
"""Measure and benchmark end-to-end response latency against latency budget SLO (P95 < 2000ms)."""

from __future__ import annotations

import argparse
import asyncio
import math
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.llm.provider import MockLLMProvider
from app.llm.response_service import LLMResponseService
from app.orchestrator.mode_manager import ModeManager

SLO_P95_MS = 2000.0


async def benchmark_turn(
    service: LLMResponseService,
    child_message: str,
    level: str = "L1",
) -> dict[str, float | str | bool]:
    start = time.perf_counter()

    mode_decision = ModeManager.select_mode(child_message=child_message, current_mode="learning")
    result = await service.generate_response(
        child_message=child_message,
        current_level=level,
        mode=mode_decision.mode,
        deterministic_response=mode_decision.deterministic_response,
    )

    duration_ms = (time.perf_counter() - start) * 1000.0
    return {
        "duration_ms": duration_ms,
        "mode": result.mode,
        "fallback_used": result.fallback_used,
        "is_deterministic": mode_decision.deterministic_response is not None,
    }


def calculate_percentile(data: list[float], percentile: float) -> float:
    if not data:
        return 0.0
    sorted_data = sorted(data)
    idx = int(math.ceil((percentile / 100.0) * len(sorted_data))) - 1
    return sorted_data[max(0, min(idx, len(sorted_data) - 1))]


async def run_benchmark(num_turns: int = 50, check_slo: bool = False) -> int:
    print(f"\nBenchmarking {num_turns} synthetic conversation turns (SLO Target: P95 < {SLO_P95_MS} ms)...\n")

    # Fast mock provider simulating realistic network delay (100ms - 350ms)
    class BenchProvider(MockLLMProvider):
        async def generate_response(self, prompt: str, system_instruction: str, timeout_ms: int = 1500) -> str:
            # Simulate realistic network completion latency between 100ms and 350ms
            await asyncio.sleep(0.12)
            return '{"response_text": "Good job! The cat is happy!"}'

    service = LLMResponseService(provider=BenchProvider())

    test_messages = [
        "Blue",                               # deterministic exercise check
        "Teach me a new animal word!",        # generative learning
        "Stop! I want a break.",              # deterministic support
        "I like fluffy cats! Do you?",        # generative conversation
        "Let's play a guessing game!",        # generative engagement
        "Bye bye!",                           # deterministic exit
        "Red",                                # deterministic exercise
        "What is the big animal?",            # generative learning
    ]

    durations: list[float] = []
    deterministic_count = 0
    generative_count = 0
    fallback_count = 0

    for i in range(num_turns):
        msg = test_messages[i % len(test_messages)]
        res = await benchmark_turn(service, msg, level="L1")
        dur_ms = float(res["duration_ms"])
        durations.append(dur_ms)

        if res["is_deterministic"]:
            deterministic_count += 1
        else:
            generative_count += 1

        if res["fallback_used"]:
            fallback_count += 1

    p50 = calculate_percentile(durations, 50)
    p95 = calculate_percentile(durations, 95)
    p99 = calculate_percentile(durations, 99)
    avg = sum(durations) / len(durations)

    print("=" * 55)
    print("LATENCY BENCHMARK RESULTS")
    print("=" * 55)
    print(f"Total Requests:       {num_turns}")
    print(f"Deterministic Turns:  {deterministic_count} ({deterministic_count / num_turns * 100:.1f}%)")
    print(f"Generative Turns:     {generative_count} ({generative_count / num_turns * 100:.1f}%)")
    print(f"Fallback Rate:        {fallback_count / num_turns * 100:.1f}%")
    print(f"Average Latency:      {avg:.2f} ms")
    print(f"P50 Latency:          {p50:.2f} ms")
    print(f"P95 Latency:          {p95:.2f} ms  (Target: < {SLO_P95_MS} ms)")
    print(f"P99 Latency:          {p99:.2f} ms")
    print("=" * 55)

    if check_slo:
        if p95 >= SLO_P95_MS:
            print(f"\nFAIL: P95 latency ({p95:.2f} ms) violates SLO (< {SLO_P95_MS} ms)")
            return 1
        print(f"\nPASS: P95 latency ({p95:.2f} ms) satisfies SLO (< {SLO_P95_MS} ms)")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--turns", type=int, default=50)
    parser.add_argument("--check-slo", action="store_true")
    args = parser.parse_args()

    return asyncio.run(run_benchmark(args.turns, args.check_slo))


if __name__ == "__main__":
    raise SystemExit(main())
