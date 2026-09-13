"""End-to-end BCS experiment runner."""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    DATASET_PRIMARY, DATASET_SECONDARY, OUTPUT_DIR, FIGURES_DIR,
    RESULTS_JSON, CHECKPOINT_PATH, N_TARGET, BCS_SD_TARGET
)
from data import load_conversations, filter_min_turns, filter_english, remove_redacted
from bcs import BCSComputer, batch_compute_bcs
from analysis import analyze_bcs_distribution, check_gate
from visualize import plot_bcs_histogram, plot_gate_comparison


def main(max_samples: int = None, use_secondary: bool = False) -> dict:
    """Run full BCS experiment pipeline."""
    start_time = datetime.now()
    print(f"[{start_time}] Starting BCS experiment...")

    dataset = DATASET_SECONDARY if use_secondary else DATASET_PRIMARY
    print(f"Loading dataset: {dataset}")
    conversations = load_conversations(dataset, max_samples)
    print(f"Loaded {len(conversations)} conversations")

    print("Filtering...")
    conversations = filter_english(conversations)
    print(f"After English filter: {len(conversations)}")

    conversations = remove_redacted(conversations)
    print(f"After redaction filter: {len(conversations)}")

    conversations = filter_min_turns(conversations)
    print(f"After 4+ turn filter: {len(conversations)}")

    if len(conversations) < N_TARGET:
        print(f"WARNING: Only {len(conversations)} conversations, below target {N_TARGET}")

    print(f"Computing BCS for {len(conversations)} conversations...")
    bcs_values = batch_compute_bcs(conversations, checkpoint_path=CHECKPOINT_PATH)

    print("Analyzing distribution...")
    stats = analyze_bcs_distribution(bcs_values)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    results = {
        "hypothesis_id": "H-E1",
        "dataset": dataset,
        "run_timestamp": start_time.isoformat(),
        "duration_seconds": duration,
        "raw_conversations": len(conversations),
        "bcs_computed": len(bcs_values),
        "statistics": stats,
        "gate": {
            "type": "MUST_WORK",
            "pass_condition": f"SD > {BCS_SD_TARGET}, n > {N_TARGET}",
            "sd_actual": stats["std"],
            "sd_target": BCS_SD_TARGET,
            "n_actual": stats["n"],
            "n_target": N_TARGET,
            "satisfied": stats["gate_pass"]
        }
    }

    with open(RESULTS_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved: {RESULTS_JSON}")

    print("Generating figures...")
    plot_bcs_histogram(bcs_values, os.path.join(FIGURES_DIR, "bcs_histogram.png"))
    plot_gate_comparison(stats, save_path=os.path.join(FIGURES_DIR, "gate_comparison.png"))

    print(f"\n{'='*50}")
    print(f"BCS EXPERIMENT RESULTS")
    print(f"{'='*50}")
    print(f"Dataset: {dataset}")
    print(f"Sample size (n): {stats['n']}")
    print(f"BCS Mean: {stats['mean']:.4f}")
    print(f"BCS SD: {stats['std']:.4f}")
    print(f"BCS Range: [{stats['min']:.4f}, {stats['max']:.4f}]")
    print(f"Duration: {duration:.1f}s")
    print(f"\nGATE CHECK: {'PASS' if stats['gate_pass'] else 'FAIL'}")
    print(f"  SD > {BCS_SD_TARGET}: {stats['std']:.4f} {'>' if stats['std'] > BCS_SD_TARGET else '<='} {BCS_SD_TARGET}")
    print(f"  n > {N_TARGET}: {stats['n']} {'>' if stats['n'] > N_TARGET else '<='} {N_TARGET}")
    print(f"{'='*50}")

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument("--use-secondary", action="store_true")
    args = parser.parse_args()

    main(max_samples=args.max_samples, use_secondary=args.use_secondary)
