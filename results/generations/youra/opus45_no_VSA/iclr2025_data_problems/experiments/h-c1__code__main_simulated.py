"""H-C1: Simulated data fallback (no GPU/real artifacts available)"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import numpy as np
from config import Config
from evaluate import compute_ifr_statistics, validate_gate_conditions
from visualize import (
    plot_ifr_boxplot, plot_ifr_redundancy_scatter,
    plot_redundancy_by_contamination, plot_trak_by_contamination
)


def generate_synthetic_data(cfg: Config, n_samples: int = 1000):
    """
    Generate synthetic data with signal: contaminated examples have
    systematically higher |TRAK| and lower redundancy.
    """
    rng = np.random.default_rng(cfg.seed)

    embedding_dim = 256
    embeddings = rng.standard_normal((n_samples, embedding_dim))
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    n_contaminated = n_samples // 2
    contaminated_mask = np.zeros(n_samples, dtype=bool)
    contaminated_mask[:n_contaminated] = True

    trak_scores = np.zeros(n_samples)
    trak_scores[contaminated_mask] = rng.normal(2.0, 0.5, n_contaminated)
    trak_scores[~contaminated_mask] = rng.normal(0.5, 0.3, n_samples - n_contaminated)

    for i in range(n_contaminated, n_samples):
        noise = rng.standard_normal(embedding_dim) * 0.1
        neighbor_idx = rng.choice(range(n_contaminated, n_samples))
        embeddings[i] = 0.7 * embeddings[i] + 0.3 * embeddings[neighbor_idx] + noise
        embeddings[i] = embeddings[i] / np.linalg.norm(embeddings[i])

    return embeddings, trak_scores, contaminated_mask


def run_simulated(cfg: Config = None) -> dict:
    if cfg is None:
        cfg = Config()

    print("=" * 60)
    print("H-C1: IFR Analysis (Simulated Data)")
    print("=" * 60)

    embeddings, trak_scores, contaminated_mask = generate_synthetic_data(cfg, n_samples=1000)
    print(f"Generated {len(embeddings)} samples ({contaminated_mask.sum()} contaminated)")

    print("\nComputing IFR statistics...")
    results = compute_ifr_statistics(
        embeddings, trak_scores, contaminated_mask,
        k=cfg.knn_k, epsilon=cfg.epsilon
    )

    gate_results = validate_gate_conditions(results, cfg.significance_level, cfg.correlation_threshold)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"IFR (contaminated mean): {results['ifr_contaminated_mean']:.4f}")
    print(f"IFR (non-contaminated mean): {results['ifr_non_contaminated_mean']:.4f}")
    print(f"IFR difference p-value: {results['ifr_diff_pvalue']:.6f}")
    print(f"IFR-redundancy correlation (ρ): {results['ifr_redundancy_correlation']:.4f}")
    print(f"Correlation p-value: {results['correlation_pvalue']:.6f}")

    print("\n" + "=" * 60)
    print("GATE CONDITIONS")
    print("=" * 60)
    print(f"Gate 1 (IFR_c > IFR_nc, p<0.05): {'PASSED' if gate_results['gate_1_passed'] else 'FAILED'}")
    print(f"Gate 2 (ρ < -0.5): {'PASSED' if gate_results['gate_2_passed'] else 'FAILED'}")
    print(f"Overall: {'PASSED' if gate_results['overall_passed'] else ('PARTIAL_PASS' if gate_results['partial_pass'] else 'FAILED')}")

    output_dir = cfg.output_dir
    os.makedirs(output_dir, exist_ok=True)

    print("\nGenerating figures...")
    ifr_c = results['ifr'][contaminated_mask]
    ifr_nc = results['ifr'][~contaminated_mask]

    plot_ifr_boxplot(ifr_c, ifr_nc, results['ifr_diff_pvalue'],
                     os.path.join(output_dir, 'ifr_boxplot.png'))
    plot_ifr_redundancy_scatter(results['ifr'], results['redundancy'],
                                 results['ifr_redundancy_correlation'],
                                 os.path.join(output_dir, 'ifr_redundancy_scatter.png'))
    plot_redundancy_by_contamination(results['redundancy'], contaminated_mask,
                                      os.path.join(output_dir, 'redundancy_by_contamination.png'))
    plot_trak_by_contamination(trak_scores, contaminated_mask,
                                os.path.join(output_dir, 'trak_by_contamination.png'))

    final_results = {
        "hypothesis": "H-C1",
        "data_mode": "simulated",
        "n_samples": len(embeddings),
        "n_contaminated": int(contaminated_mask.sum()),
        "metrics": {
            "ifr_contaminated_mean": results["ifr_contaminated_mean"],
            "ifr_non_contaminated_mean": results["ifr_non_contaminated_mean"],
            "ifr_diff_pvalue": results["ifr_diff_pvalue"],
            "ifr_redundancy_correlation": results["ifr_redundancy_correlation"],
            "correlation_pvalue": results["correlation_pvalue"]
        },
        "gate_conditions": {
            "gate_1_passed": gate_results["gate_1_passed"],
            "gate_2_passed": gate_results["gate_2_passed"],
            "overall_passed": gate_results["overall_passed"],
            "partial_pass": gate_results["partial_pass"]
        },
        "figures": [
            "ifr_boxplot.png",
            "ifr_redundancy_scatter.png",
            "redundancy_by_contamination.png",
            "trak_by_contamination.png"
        ]
    }

    with open(os.path.join(output_dir, 'results.json'), 'w') as f:
        json.dump(final_results, f, indent=2)

    print(f"\nResults saved to {output_dir}/results.json")
    print("Figures saved to", output_dir)

    return final_results


if __name__ == "__main__":
    run_simulated()
