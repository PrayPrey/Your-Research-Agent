"""H-M4 Experiment: Bidirectional Tasks Show Miscalibrated Confidence.

Tests correlation between bidirectional features and calibration inversion clusters.
Gate: (r > 0.4) OR (d > 0.3 AND partial_r > 0.3)
"""

import os
import sys
import json
import random
import numpy as np

# Add current dir to path FIRST (before any imports that might add other paths)
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from config import H_M4_Config
from data_loader import load_e1_results, load_task_texts, build_dataset

# Re-insert current dir at position 0 to shadow h-e1 modules after data_loader import
sys.path.insert(0, _THIS_DIR)

from features import score_all
from confounds import build_confound_matrix
from correlation import compute_correlations, check_gate
from cross_model import per_model_consistency
import visualize as viz


def set_seed(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)


def main():
    cfg = H_M4_Config()
    set_seed(cfg.seed)

    print("=" * 60)
    print("H-M4: Bidirectional Tasks Show Miscalibrated Confidence")
    print("=" * 60)

    # Load data
    print("\n[1] Loading H-E1 results...")
    e1_results = load_e1_results(cfg.e1_results_path)
    print(f"  Total H-E1 tasks: {len(e1_results['per_task'])}")

    print("\n[2] Loading task texts from H-E1 data loaders...")
    task_texts = load_task_texts()

    print("\n[3] Building dataset (joining on task_id)...")
    records = build_dataset(e1_results, task_texts)

    print("\n[4] Scoring bidirectional features...")
    records = score_all(records)

    # Feature prevalence summary
    total_with_features = sum(1 for r in records if r["bidirectional_score"] > 0)
    print(f"  Tasks with any bidirectional feature: {total_with_features}/{len(records)} "
          f"({100*total_with_features/len(records):.1f}%)")

    print("\n[5] Building confound matrix...")
    confounds = build_confound_matrix(records)
    print(f"  Confound matrix shape: {confounds.shape}")

    print("\n[6] Computing correlations...")
    cluster_labels = np.array([r["cluster_label"] for r in records])
    scores = np.array([r["bidirectional_score"] for r in records])

    metrics = compute_correlations(cluster_labels, scores, confounds)

    print(f"  Point-biserial r: {metrics['point_biserial_r']:.4f} (p={metrics['point_biserial_p']:.4e})")
    print(f"  Cohen's d: {metrics['cohens_d']:.4f}")
    print(f"  Partial r: {metrics['partial_r']:.4f} (p={metrics['partial_p']:.4e})")

    print("\n[7] Checking gate condition...")
    gate_passed = check_gate(metrics)
    print(f"  Gate condition: (r > 0.4) OR (d > 0.3 AND partial_r > 0.3)")
    print(f"  Gate result: {'PASS' if gate_passed else 'FAIL'}")

    print("\n[8] Cross-model consistency...")
    cross_model = per_model_consistency(records, e1_results["aggregate"]["models_evaluated"])
    print(f"  {cross_model['note']}")

    # Cluster distribution
    n_cluster_0 = sum(1 for r in records if r["cluster_label"] == 0)
    n_cluster_1 = sum(1 for r in records if r["cluster_label"] == 1)

    # Feature prevalence by cluster
    feat_by_cluster = {0: {}, 1: {}}
    for c in [0, 1]:
        cluster_records = [r for r in records if r["cluster_label"] == c]
        for f in ["user_belief_reference", "context_dependent", "hedged_answer"]:
            feat_by_cluster[c][f] = sum(r[f] for r in cluster_records) / len(cluster_records)

    print("\n[9] Saving results...")
    os.makedirs(cfg.output_dir, exist_ok=True)

    results = {
        "metrics": metrics,
        "gate_passed": gate_passed,
        "thresholds": {
            "r_threshold": cfg.r_threshold,
            "d_threshold": cfg.d_threshold,
            "partial_r_threshold": cfg.partial_r_threshold
        },
        "cross_model": cross_model,
        "n_tasks": len(records),
        "cluster_distribution": {"cluster_0": n_cluster_0, "cluster_1": n_cluster_1},
        "feature_prevalence_by_cluster": feat_by_cluster,
        "seed": cfg.seed
    }

    with open(os.path.join(cfg.output_dir, "results.json"), "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Saved: {cfg.output_dir}/results.json")

    print("\n[10] Generating visualizations...")
    os.makedirs(cfg.figures_dir, exist_ok=True)

    viz.plot_gate_metrics(metrics, os.path.join(cfg.figures_dir, "gate_metrics.png"))
    viz.plot_score_by_cluster(records, os.path.join(cfg.figures_dir, "score_by_cluster.png"))
    viz.plot_feature_breakdown(records, os.path.join(cfg.figures_dir, "feature_breakdown.png"))

    print("\n" + "=" * 60)
    print(f"EXPERIMENT COMPLETE - Gate: {'PASS' if gate_passed else 'FAIL'}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
