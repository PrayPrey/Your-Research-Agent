"""Main pipeline: load -> filter -> score -> classify -> test -> output."""

import json
import os
import sys

import numpy as np
import pandas as pd

from config import CONFIG
from data import load_battles, filter_valid, prepare_battles
from rm_scoring import RewardModel, score_all_battles, zscore_sigmoid, compute_rm_variance, cache_scores
from mode_classify import compute_pair_entropy, assign_modes, mode_distribution
from stats_test import binomial_test_mode3, sensitivity_analysis


TYPE_MAP = {
    "openassistant": "classifier",
    "pairrm": "pairwise",
    "armorm": "moe",
}


def main():
    print("=" * 60)
    print("H-E1: Mode 3 Existence Experiment")
    print("=" * 60)

    os.makedirs(CONFIG["output_dir"], exist_ok=True)

    print("\n[1/6] Loading dataset...")
    df = load_battles(CONFIG["dataset_id"])
    print(f"  Raw battles: {len(df)}")

    print("\n[2/6] Filtering valid battles...")
    df = filter_valid(df)
    print(f"  Valid battles: {len(df)}")

    df = prepare_battles(df)
    print(f"  With prompt/response: {len(df)}")

    print("\n[3/6] Loading reward models...")
    models = {}
    model_names = []
    for name, model_id in CONFIG["rm_models"].items():
        if name == "armorm" and not CONFIG["use_armorm"]:
            print(f"  Skipping {name} (FR-6 fallback)")
            continue
        print(f"  Loading {name}...")
        try:
            models[name] = RewardModel(model_id, TYPE_MAP[name])
            model_names.append(name)
        except Exception as e:
            print(f"  Failed to load {name}: {e}")
            if name == "armorm":
                print("  Falling back to 2-model mode (FR-6)")

    if len(models) < 2:
        print("ERROR: Need at least 2 reward models")
        sys.exit(1)

    print(f"\n[4/6] Scoring battles with {len(models)} models...")
    df = score_all_battles(df, models)

    print("\n  Normalizing scores...")
    for name in model_names:
        col_a = f"{name}_score_a"
        col_b = f"{name}_score_b"
        if col_a in df.columns:
            df[f"{name}_norm_a"] = zscore_sigmoid(df[col_a].values)
            df[f"{name}_norm_b"] = zscore_sigmoid(df[col_b].values)

    print("  Computing RM variance...")
    df["rm_variance"] = df.apply(lambda r: compute_rm_variance(r.to_dict(), model_names), axis=1)

    print("\n[5/6] Computing entropy and classifying modes...")
    if CONFIG["use_cluster_entropy_fallback"]:
        print("  Using cluster entropy fallback (FR-7)")
        from mode_classify import compute_cluster_entropy_fallback
        df = compute_cluster_entropy_fallback(df)
    else:
        df = compute_pair_entropy(df)

    df = assign_modes(df)

    dist = mode_distribution(df)
    print("\n  Mode Distribution:")
    for mode, info in dist.items():
        print(f"    Mode {mode}: {info['count']:,} ({info['proportion']:.1%})")

    print("\n[6/6] Statistical testing...")
    mode3_count = dist[3]["count"]
    total = len(df)

    stats_result = binomial_test_mode3(mode3_count, total, CONFIG["binomial_p0"])
    stats_result["sensitivity"] = sensitivity_analysis(
        mode3_count, total, CONFIG["sensitivity_thresholds"]
    )
    stats_result["mode_3_count"] = mode3_count
    stats_result["total_count"] = total
    stats_result["hypothesis_id"] = "h-e1"

    print(f"\n  Mode 3 proportion: {stats_result['proportion']:.3f}")
    print(f"  95% CI: [{stats_result['ci_95_lower']:.3f}, {stats_result['ci_95_upper']:.3f}]")
    print(f"  p-value: {stats_result['p_value']:.4f}")
    print(f"  Result: {stats_result['result']}")

    print("\n  Saving outputs...")
    with open(os.path.join(CONFIG["output_dir"], "mode_distribution.json"), "w") as f:
        json.dump({str(k): v for k, v in dist.items()}, f, indent=2)

    with open(os.path.join(CONFIG["output_dir"], "statistical_results.json"), "w") as f:
        json.dump(stats_result, f, indent=2)

    cache_scores(df, CONFIG["scores_cache_path"])

    results_csv = df[["battle_id", "human_entropy", "rm_variance", "mode"]].copy()
    results_csv.to_csv(os.path.join(CONFIG["output_dir"], "results.csv"), index=False)

    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"\nOutputs saved to: {CONFIG['output_dir']}")
    print(f"  - mode_distribution.json")
    print(f"  - statistical_results.json")
    print(f"  - rm_scores.parquet")
    print(f"  - results.csv")

    return stats_result


if __name__ == "__main__":
    main()
