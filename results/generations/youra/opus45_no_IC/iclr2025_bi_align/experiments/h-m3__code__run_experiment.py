#!/usr/bin/env python3
import os
import sys
import json
import numpy as np
from datetime import datetime


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)

from config import ExperimentConfig, FormalityScorerConfig, FIGURES_DIR, RESULTS_PATH, CACHE_DIR
from data_loader import load_conversations, filter_multiturn, extract_turn_pairs
from formality_scorer import FormalityScorer
from delta_analysis import build_analysis_frame
from tercile_stats import tercile_continuation_analysis, verify_mechanism
from visualize import (
    plot_tercile_bar_chart,
    plot_delta_histogram,
    plot_delta_vs_continuation_scatter,
    plot_bootstrap_distribution
)


def main():
    print("=" * 60)
    print("H-M3: Lower Delta Signals Accommodation")
    print("=" * 60)
    start_time = datetime.now()

    cfg = ExperimentConfig()
    scorer_cfg = FormalityScorerConfig()
    np.random.seed(cfg.seed)

    print("\n[1/6] Loading dataset...")
    conversations = load_conversations(split="train")
    print(f"  Loaded {len(conversations):,} conversations")

    print("\n[2/6] Filtering multi-turn conversations...")
    filtered = filter_multiturn(conversations, min_turns=cfg.min_turns)
    print(f"  Filtered to {len(filtered):,} conversations (≥{cfg.min_turns} turns/side)")

    print("\n[3/6] Extracting turn pairs...")
    turn_pairs = extract_turn_pairs(filtered)
    print(f"  Extracted {len(turn_pairs):,} turn pairs")

    if len(turn_pairs) < cfg.min_sample_size:
        print(f"ERROR: Insufficient samples ({len(turn_pairs)} < {cfg.min_sample_size})")
        sys.exit(1)

    print("\n[4/6] Scoring formality...")
    cache_path = os.path.join(CACHE_DIR, "formality_scores.json")
    scorer = FormalityScorer(model_name=scorer_cfg.model_name, device="cuda")

    cached = scorer.load_cache(cache_path)
    if cached and len(cached.get("human_scores", [])) == len(turn_pairs):
        print("  Using cached scores")
        human_scores = cached["human_scores"]
        ai_scores = cached["ai_scores"]
    else:
        print("  Computing fresh scores...")
        human_texts = [p["human_text"] for p in turn_pairs]
        ai_texts = [p["ai_text"] for p in turn_pairs]
        human_scores = scorer.score_batch(human_texts, batch_size=scorer_cfg.batch_size)
        ai_scores = scorer.score_batch(ai_texts, batch_size=scorer_cfg.batch_size)
        scorer.save_cache({"human_scores": human_scores, "ai_scores": ai_scores}, cache_path)
        print("  Scores cached")

    print("\n[5/6] Building analysis frame and running tercile analysis...")
    df = build_analysis_frame(turn_pairs, human_scores, ai_scores)

    deltas = df["delta"].values
    continuations = df["continuation"].values
    conversation_ids = df["conversation_id"].values

    results = tercile_continuation_analysis(
        deltas, continuations, conversation_ids,
        n_boot=cfg.n_boot, seed=cfg.seed
    )

    mechanism = verify_mechanism(results["tercile_rates"], results["p_robust"], cfg.alpha)

    print("\n[6/6] Generating figures...")
    os.makedirs(FIGURES_DIR, exist_ok=True)

    plot_tercile_bar_chart(
        results["tercile_rates"],
        results["tercile_counts"],
        os.path.join(FIGURES_DIR, "tercile_bar_chart.png")
    )
    print("  - tercile_bar_chart.png")

    plot_delta_histogram(
        deltas,
        results["tercile_thresholds"]["t1"],
        results["tercile_thresholds"]["t2"],
        os.path.join(FIGURES_DIR, "delta_histogram.png")
    )
    print("  - delta_histogram.png")

    plot_delta_vs_continuation_scatter(
        deltas, continuations,
        os.path.join(FIGURES_DIR, "scatter_delta_continuation.png")
    )
    print("  - scatter_delta_continuation.png")

    plot_bootstrap_distribution(
        results["boot_rhos"],
        results["spearman_rho"],
        os.path.join(FIGURES_DIR, "bootstrap_distribution.png")
    )
    print("  - bootstrap_distribution.png")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    output = {
        "hypothesis": "H-M3",
        "title": "Lower Delta Signals Accommodation",
        "timestamp": end_time.isoformat(),
        "duration_seconds": duration,
        "dataset": {
            "name": cfg.dataset_name,
            "n_conversations": len(filtered),
            "n_turn_pairs": len(turn_pairs)
        },
        "tercile_analysis": {
            "thresholds": results["tercile_thresholds"],
            "rates": {f"T{k}": v for k, v in results["tercile_rates"].items()},
            "counts": {f"T{k}": v for k, v in results["tercile_counts"].items()},
            "monotonic": results["monotonic"]
        },
        "statistics": {
            "spearman_rho": results["spearman_rho"],
            "p_naive": results["p_naive"],
            "p_robust": results["p_robust"],
            "n_bootstrap": cfg.n_boot
        },
        "mechanism_verification": mechanism,
        "gate": {
            "type": "SHOULD_WORK",
            "condition": "Monotonic trend T1 > T2 > T3, p_robust < 0.05",
            "passed": mechanism["passes_gate"],
            "verdict": "PASS" if mechanism["passes_gate"] else "FAIL"
        }
    }

    with open(RESULTS_PATH, "w") as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to: {RESULTS_PATH}")

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Tercile Rates:")
    print(f"  T1 (Low Δ):  {results['tercile_rates'][1]:.4f} (n={results['tercile_counts'][1]:,})")
    print(f"  T2 (Mid Δ):  {results['tercile_rates'][2]:.4f} (n={results['tercile_counts'][2]:,})")
    print(f"  T3 (High Δ): {results['tercile_rates'][3]:.4f} (n={results['tercile_counts'][3]:,})")
    print(f"\nMonotonic Trend: {results['monotonic']}")
    print(f"Spearman ρ: {results['spearman_rho']:.4f}")
    print(f"p_robust: {results['p_robust']:.4f}")
    print(f"Effect Size (T1-T3): {mechanism['effect_size']:.4f}")
    print(f"\n{'='*60}")
    print(f"GATE VERDICT: {output['gate']['verdict']}")
    print(f"{'='*60}")
    print(f"Duration: {duration:.1f}s")

    return output


if __name__ == "__main__":
    main()
