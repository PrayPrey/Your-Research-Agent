import sys
import json
import pathlib
import time

import torch

from data_loader import load_zoo, sample_models
from orbit_construction import build_all_orbits
from distance_metrics import compute_distances
from statistics import aggregate, evaluate_gate
from visualization import (
    fig_gate_metrics,
    fig_orbit_distribution,
    fig_l2_vs_cosine,
    fig_scale_vs_diameter,
)


def run(n_models=500, K=5, seed=42, results_path="docs/youra_research/h-e1/results.json"):
    t0 = time.time()

    # 1. Load zoo
    zoo = load_zoo()
    print(f"Zoo size: {len(zoo)} models")

    # 2. Sample
    weights = sample_models(zoo, n=n_models, seed=seed)
    print(f"Sampled weights shape: {weights.shape}")

    # 3. Build orbits
    print(f"Building orbits (K={K})...")
    orbits = build_all_orbits(weights, K=K, base_seed=seed)

    # 4. Compute distances
    print("Computing distances...")
    distances = compute_distances(weights, orbits)
    # attach max_scale (per-model, from orbit construction)
    if "_max_scale_scaling" in orbits:
        distances["scaling"]["max_scale"] = orbits["_max_scale_scaling"]

    # 5. Aggregate stats
    stats = {}
    for sym_type in ("scaling", "signflip", "combined"):
        stats[sym_type] = aggregate(distances[sym_type]["cosine"])
        print(f"[{sym_type}] mean={stats[sym_type]['mean']:.4f} "
              f"frac_above_0.05={stats[sym_type]['frac_above']:.4f} "
              f"CI=[{stats[sym_type]['ci_lower']:.4f}, {stats[sym_type]['ci_upper']:.4f}]")

    # 6. Evaluate gate
    gate = evaluate_gate(stats)
    print(f"\nGATE: {'PASS' if gate['pass'] else 'FAIL'}")
    print(f"  {gate['gate_condition']}")

    # 7. Visualize
    out_dir = "docs/youra_research/h-e1/figures"
    fig_gate_metrics(stats, out_dir)
    fig_orbit_distribution(distances, out_dir)
    fig_l2_vs_cosine(distances, out_dir)
    fig_scale_vs_diameter(distances, out_dir)
    print(f"Figures saved to {out_dir}")

    # 8. Write results
    results = {
        "config": {"n_models": n_models, "K": K, "seed": seed},
        "stats": stats,
        "gate": gate,
        "elapsed_s": round(time.time() - t0, 1),
    }
    # distances too large to serialize fully — include summary only
    results["distance_summary"] = {
        sym: {
            "n_pairs": len(distances[sym]["cosine"]),
            "cosine_min": min(distances[sym]["cosine"]),
            "cosine_max": max(distances[sym]["cosine"]),
        }
        for sym in ("scaling", "signflip", "combined")
    }

    path = pathlib.Path(results_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results written to {results_path}")

    if not gate["pass"]:
        print("GATE FAILED — pipeline blocked.", file=sys.stderr)
        sys.exit(1)

    return results


if __name__ == "__main__":
    run()
