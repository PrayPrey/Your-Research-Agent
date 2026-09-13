"""Orchestrator for H-C1 doctest prevalence scan."""

import os
import sys
import time

# Ensure code dir is on path
sys.path.insert(0, os.path.dirname(__file__))

from config import ScanConfig
from data_loader import load_python_stream, reservoir_sample
from gate import run_gate_check
from results import build_aggregate, write_json, write_jsonl
from scanner import run_all_phases
from token_estimator import sum_tokens
from visualize import generate_all

# Absolute paths (relative to repo root)
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
H_C1_DIR = os.path.join(REPO_ROOT, "h-c1")


def main():
    cfg = ScanConfig()

    results_json = os.path.join(H_C1_DIR, "results.json")
    per_file_jsonl = os.path.join(H_C1_DIR, "per_file_results.jsonl")
    figures_dir = os.path.join(H_C1_DIR, "figures")

    print("=" * 60)
    print("H-C1: Doctest Prevalence Pilot Scanner")
    print("=" * 60)
    print(f"Dataset: {cfg.dataset} ({cfg.data_dir})")
    print(f"Samples: {cfg.n_samples}, Seed: {cfg.seed}")
    print(f"Workers: {cfg.n_workers}, Timeout: {cfg.timeout_sec}s")
    print()

    t0 = time.time()

    # Step 1: Stream and sample
    print("Loading stream...")
    stream = load_python_stream(seed=cfg.seed, buffer_size=cfg.buffer_size)
    print(f"Sampling {cfg.n_samples} quality-passing files...")
    samples = reservoir_sample(stream, n=cfg.n_samples)
    print(f"Sampled {len(samples)} files")

    # Step 2: Run all phases
    per_file = run_all_phases(samples, n_workers=cfg.n_workers)

    duration = time.time() - t0

    # Step 3: Aggregate
    aggregate = build_aggregate(per_file, duration)

    # Step 4: Write outputs
    os.makedirs(os.path.dirname(results_json), exist_ok=True)
    write_json(aggregate, results_json)
    write_jsonl(per_file, per_file_jsonl)
    print(f"Results written to {results_json}")

    # Step 5: Visualize
    os.makedirs(figures_dir, exist_ok=True)
    generate_all(aggregate, per_file, figures_dir)

    # Step 6: Gate check
    gate_status = run_gate_check(aggregate)

    print()
    print("=" * 60)
    print("SCAN COMPLETE")
    print(f"  n_sampled:              {aggregate['n_sampled']}")
    print(f"  n_pattern_positive:     {aggregate['n_pattern_positive']} ({aggregate['doctest_pattern_rate']:.3f})")
    print(f"  n_ast_positive:         {aggregate['n_ast_positive']} ({aggregate['doctest_ast_rate']:.3f})")
    print(f"  n_executable_positive:  {aggregate['n_executable_positive']} ({aggregate['doctest_executable_rate']:.3f})")
    print(f"  estimated_token_pool_M: {aggregate['estimated_token_pool_M']:.2f}M")
    print(f"  duration:               {duration:.1f}s")
    print(f"  gate_status:            {gate_status}")
    print("=" * 60)

    return aggregate, gate_status


if __name__ == "__main__":
    main()
