"""
Compute peakedness from H-E1 cached aggregation scores without re-running inference.

Derivation:
  H-E1 stores: min_scores = -min(logprobs), mean_scores = -mean(logprobs)
  Since all logprobs <= 0:
    max(|logprobs|) = -min(logprobs) = min_scores
    mean(|logprobs|) = -mean(logprobs) = mean_scores
  So: peakedness = min_scores / mean_scores  (exact, no approximation)
"""
import os
import sys
import json
import numpy as np

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)
import config as cfg

from peakedness import test_peakedness_difference
from visualization import save_all_figures


def load_peakedness_from_h_e1_cache(model_key: str, dataset_name: str):
    """Compute peakedness from H-E1 npz aggregation scores."""
    cache_file = os.path.join(cfg.H_E1_RESULTS_DIR, f"scores_{model_key}_{dataset_name}.npz")
    if not os.path.exists(cache_file):
        raise FileNotFoundError(f"H-E1 cache not found: {cache_file}")

    data = np.load(cache_file)
    min_scores = data["min_scores"]   # = -min(logprobs) = max(|logprobs|)
    mean_scores = data["mean_scores"] # = -mean(logprobs) = mean(|logprobs|)
    labels = data["labels"]

    # Guard: mean_scores should all be > 0; handle degenerate case
    with np.errstate(divide='ignore', invalid='ignore'):
        peakedness = np.where(mean_scores > 0, min_scores / mean_scores, 1.0)

    hallucinated = peakedness[labels == 0].tolist()
    correct = peakedness[labels == 1].tolist()
    return hallucinated, correct, peakedness, labels


def main():
    os.makedirs(cfg.RESULTS_DIR, exist_ok=True)
    os.makedirs(cfg.FIGURES_DIR, exist_ok=True)

    # Dataset name mapping: h-m1 uses "trivia_qa", "nq"; h-e1 has trivia_qa and truthful_qa
    # For NQ: h-e1 doesn't have a cached nq file — fall back to trivia_qa only from cache
    available = {}
    for model_key in cfg.MODELS_TO_RUN:
        for dataset_name in cfg.DATASETS:
            fname = os.path.join(cfg.H_E1_RESULTS_DIR, f"scores_{model_key}_{dataset_name}.npz")
            if os.path.exists(fname):
                available[(model_key, dataset_name)] = fname
                print(f"  Found cache: {fname}")
            else:
                print(f"  No cache for {model_key}/{dataset_name}: {fname}")

    if not available:
        print("No H-E1 caches found. Cannot compute peakedness without re-running inference.")
        sys.exit(1)

    all_results = {}

    for (model_key, dataset_name), _ in available.items():
        key = f"{model_key}_{dataset_name}"
        print(f"\n--- {key} (from H-E1 cache) ---")

        hallucinated, correct, peakedness, labels = load_peakedness_from_h_e1_cache(model_key, dataset_name)
        print(f"  n_hallucinated={len(hallucinated)}, n_correct={len(correct)}")
        print(f"  mean peakedness: h={np.mean(hallucinated):.4f}, c={np.mean(correct):.4f}")

        stats = test_peakedness_difference(hallucinated, correct)
        print(f"  p={stats['p_value']:.6f}, direction={stats['direction']}")

        # Save peakedness arrays
        np.savez(
            os.path.join(cfg.RESULTS_DIR, f"peakedness_{model_key}_{dataset_name}.npz"),
            hallucinated=np.array(hallucinated),
            correct=np.array(correct),
            labels=labels,
        )

        all_results[key] = {
            "dataset": dataset_name,
            "model": model_key,
            "stats": stats,
            "hallucinated": hallucinated,
            "correct": correct,
            "n_samples": len(hallucinated) + len(correct),
        }

    # Save summary JSON
    summary = {k: {
        "p_value": v["stats"]["p_value"],
        "direction": v["stats"]["direction"],
        "mean_hallucinated": v["stats"]["mean_hallucinated"],
        "mean_correct": v["stats"]["mean_correct"],
        "n_hallucinated": v["stats"]["n_hallucinated"],
        "n_correct": v["stats"]["n_correct"],
    } for k, v in all_results.items()}

    with open(os.path.join(cfg.RESULTS_DIR, "results_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary saved to {cfg.RESULTS_DIR}/results_summary.json")

    # Gate check
    gate_pass = any(
        v["stats"]["p_value"] < cfg.P_VALUE_THRESHOLD
        for v in all_results.values()
    )

    # Figures
    print("Generating figures...")
    save_all_figures(all_results, cfg.FIGURES_DIR)
    print(f"Figures saved to {cfg.FIGURES_DIR}")

    print("\n" + "=" * 60)
    print(f"GATE RESULT: {'PASS' if gate_pass else 'FAIL'}")
    for k, v in summary.items():
        sig = "PASS p<0.05" if v["p_value"] < cfg.P_VALUE_THRESHOLD else "FAIL p>=0.05"
        print(f"  {k}: {sig}, p={v['p_value']:.6f}, direction={v['direction']}, "
              f"n_h={v['n_hallucinated']}, n_c={v['n_correct']}, "
              f"mean_h={v['mean_hallucinated']:.4f}, mean_c={v['mean_correct']:.4f}")
    print("=" * 60)
    return gate_pass, all_results


if __name__ == "__main__":
    main()
