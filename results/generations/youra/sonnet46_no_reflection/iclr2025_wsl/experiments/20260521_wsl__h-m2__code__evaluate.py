"""
Evaluate pipeline for H-M2: runs variance decomposition on CNN Zoo trajectories.
Computes Var_perm / (Var_perm + Var_GL) across CIFAR-10-GS and SVHN-GS subsets.
"""
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from tqdm import tqdm


def run_zoo_analysis(
    dataset,
    decomposer,
    subset_name: str,
    min_models: int = 200,
    orbit_basis_dim: int = 64,
) -> Dict:
    """Run variance decomposition on all trajectories.

    Returns: {ratios, ratio_mean, ratio_std, n_models, subset_name,
              epoch_ratios, layer_stats, var_perm_mean, var_gl_mean, orbit_basis_dim}
    """
    ratios = []
    epoch_ratios_all = []
    layer_stats_all = {}

    print(f"\n📊 Analyzing {subset_name}...")
    n_available = len(dataset)
    print(f"   Models available: {n_available}")

    if n_available < min_models:
        print(f"   ⚠️  Only {n_available} models available (required: {min_models})")

    for model_id, trajectory in tqdm(
        dataset.iter_trajectories(),
        desc=f"{subset_name}",
        total=n_available
    ):
        try:
            result = decomposer.compute_trajectory_variance_ratio(trajectory)
            if result["n_checkpoints"] == 0:
                continue

            ratios.append(result["ratio"])

            # Collect epoch ratios (use first model only for performance)
            if len(epoch_ratios_all) < 10:
                er = decomposer.compute_epoch_ratios(trajectory)
                epoch_ratios_all.append(er)

            # Layer breakdown (sample every 10th model for performance)
            if len(ratios) % 10 == 1:
                lb = decomposer.compute_layer_breakdown(trajectory)
                for ltype, stats in lb.items():
                    if ltype not in layer_stats_all:
                        layer_stats_all[ltype] = {"var_perm": [], "var_gl": [], "ratio": []}
                    layer_stats_all[ltype]["var_perm"].append(stats["var_perm"])
                    layer_stats_all[ltype]["var_gl"].append(stats["var_gl"])
                    layer_stats_all[ltype]["ratio"].append(stats["ratio"])
        except Exception as e:
            print(f"   ⚠️  Error on {model_id}: {e}")
            continue

    if not ratios:
        print(f"   ❌ No valid trajectories found")
        return {
            "ratios": [],
            "ratio_mean": 0.0,
            "ratio_std": 0.0,
            "n_models": 0,
            "subset_name": subset_name,
            "epoch_ratios": [],
            "layer_stats": {},
            "var_perm_mean": 0.0,
            "var_gl_mean": 0.0,
            "orbit_basis_dim": orbit_basis_dim,
        }

    ratio_mean = float(np.mean(ratios))
    ratio_std = float(np.std(ratios))

    # Aggregate layer stats
    layer_stats_summary = {}
    for ltype, arrays in layer_stats_all.items():
        layer_stats_summary[ltype] = {
            "var_perm": float(np.mean(arrays["var_perm"])),
            "var_gl": float(np.mean(arrays["var_gl"])),
            "ratio": float(np.mean(arrays["ratio"])),
        }

    print(f"   ✓ Analyzed {len(ratios)} models")
    print(f"   Var_perm/(Var_perm+Var_GL) = {ratio_mean:.4f} ± {ratio_std:.4f}")

    return {
        "ratios": ratios,
        "ratio_mean": ratio_mean,
        "ratio_std": ratio_std,
        "n_models": len(ratios),
        "subset_name": subset_name,
        "epoch_ratios": epoch_ratios_all,
        "layer_stats": layer_stats_summary,
        "var_perm_mean": float(np.mean([r * 1000 for r in ratios])),  # proportional
        "var_gl_mean": float(np.mean([(1 - r) * 1000 for r in ratios])),
        "orbit_basis_dim": orbit_basis_dim,
    }


def compute_cross_dataset_stability(
    ratio_cifar10: float, ratio_svhn: float
) -> Dict[str, float]:
    """Compute |ratio_CIFAR10 - ratio_SVHN| stability gap.
    Returns: {stability_gap, ratio_cifar10, ratio_svhn}
    """
    stability_gap = abs(ratio_cifar10 - ratio_svhn)
    return {
        "stability_gap": float(stability_gap),
        "ratio_cifar10": float(ratio_cifar10),
        "ratio_svhn": float(ratio_svhn),
    }


def check_gate(
    results_cifar10: Dict,
    results_svhn: Dict,
    threshold: float = 0.60,
    stability_threshold: float = 0.10,
) -> Dict[str, bool]:
    """Evaluate MUST_WORK gate conditions.
    Returns: {primary_pass, n_models_pass, non_degenerate_pass, stability_pass, all_pass}
    """
    ratio_mean = results_cifar10.get("ratio_mean", 0.0)
    ratio_std = results_cifar10.get("ratio_std", 0.0)
    n_models = results_cifar10.get("n_models", 0)
    ratio_svhn = results_svhn.get("ratio_mean", 0.0)

    primary_pass = ratio_mean > threshold
    n_models_pass = n_models >= 200
    non_degenerate_pass = ratio_std > 0.01
    stability_gap = abs(ratio_mean - ratio_svhn)
    stability_pass = stability_gap < stability_threshold

    all_pass = primary_pass and n_models_pass and non_degenerate_pass

    print(f"\n🔍 MUST_WORK Gate Evaluation:")
    print(f"   Primary (ratio > {threshold}): {ratio_mean:.4f} > {threshold} → {'✅ PASS' if primary_pass else '❌ FAIL'}")
    print(f"   N models (>= 200): {n_models} → {'✅ PASS' if n_models_pass else '❌ FAIL'}")
    print(f"   Non-degenerate (std > 0.01): {ratio_std:.4f} → {'✅ PASS' if non_degenerate_pass else '❌ FAIL'}")
    print(f"   Stability (|CIFAR-SVHN| < {stability_threshold}): {stability_gap:.4f} → {'✅ PASS' if stability_pass else '⚠️ WARN'}")
    print(f"   Overall: {'✅ PASS' if all_pass else '❌ FAIL'}")

    return {
        "primary_pass": primary_pass,
        "n_models_pass": n_models_pass,
        "non_degenerate_pass": non_degenerate_pass,
        "stability_pass": stability_pass,
        "all_pass": all_pass,
        "ratio_mean": ratio_mean,
        "ratio_std": ratio_std,
        "n_models": n_models,
        "stability_gap": stability_gap,
    }


def save_results_json(results: Dict, output_path: str) -> None:
    """Save results dict to JSON file."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Serialize: convert numpy/torch to native Python types
    def _convert(obj):
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: _convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_convert(x) for x in obj]
        return obj

    serializable = _convert(results)
    with open(output_path, "w") as f:
        json.dump(serializable, f, indent=2)
    print(f"✓ Results saved: {output_path}")
