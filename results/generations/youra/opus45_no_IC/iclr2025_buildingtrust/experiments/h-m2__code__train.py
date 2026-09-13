"""H-M2 Main Orchestrator: Per-cluster temperature scaling variation experiment."""

import os
import sys
import json
import torch
import numpy as np
from datetime import datetime
from pathlib import Path

# Import h-m2 modules FIRST (current directory already in path)
from config import (
    SEED, N_CLUSTERS, N_FOLDS, T_BOUNDS, T_INIT, N_BOOTSTRAP,
    CV_GATE_THRESHOLD, RANGE_GATE_THRESHOLD, RESULTS_JSON, VALIDATION_MD, FIGURES_DIR,
    CLUSTER_NAMES,
)
from data_loader import collect_logits_by_cluster, pad_and_stack_cluster, stratified_kfold_splits
from temperature_optim import optimize_temperature_per_cluster, cross_validate_temperatures
from metrics import compute_cv_and_range, bootstrap_ci, evaluate_gate
from ablations import run_bounds_ablation, run_init_ablation
from visualize import plot_temperature_bar, plot_temperature_boxplot, plot_t_vs_cluster_line, plot_cv_bootstrap_hist

# Now add h-e1 for data/model modules (append to not override h-m2 modules)
_he1_path = str(Path(__file__).parent.parent.parent / "h-e1" / "code")
if _he1_path not in sys.path:
    sys.path.append(_he1_path)
from data import load_truthfulqa_mc, assign_clusters, validate_cluster_sizes
from model import load_model_and_tokenizer


def save_results_json(results, path):
    """Save experiment results to JSON."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    def convert(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, dict):
            return {str(k): convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert(v) for v in obj]
        return obj

    with open(path, 'w') as f:
        json.dump(convert(results), f, indent=2)


def save_validation_md(results, gate_passed, path):
    """Generate 04_validation.md report."""
    cv = results["cv"]
    t_range = results["range"]
    primary_pass, secondary_pass = results["primary_pass"], results["secondary_pass"]
    optimal_temps = results["optimal_temps"]

    status = "PASS" if gate_passed else "FAIL"

    md = f"""# H-M2 Validation Report

**Hypothesis:** Different confidence distributions require different temperature parameters for optimal calibration
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** {status}

## Gate Evaluation

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| CV(optimal T) | {cv:.4f} | > {CV_GATE_THRESHOLD} | {'PASS' if primary_pass else 'FAIL'} |
| Range(optimal T) | {t_range:.4f} | > {RANGE_GATE_THRESHOLD} | {'PASS' if secondary_pass else 'FAIL'} |

**Overall Gate:** {status}

## Optimal Temperatures per Cluster

| Cluster | Name | Optimal T |
|---------|------|-----------|
"""
    for cid in sorted(optimal_temps.keys()):
        name = CLUSTER_NAMES.get(cid, f"Cluster {cid}")
        md += f"| {cid} | {name} | {optimal_temps[cid]:.4f} |\n"

    md += f"""
## Statistics

- **Mean T:** {np.mean(list(optimal_temps.values())):.4f}
- **Std T:** {np.std(list(optimal_temps.values())):.4f}
- **CV:** {cv:.4f}
- **Range:** {t_range:.4f}
- **Bootstrap CI (CV):** [{results['cv_ci'][0]:.4f}, {results['cv_ci'][1]:.4f}]

## Cross-Validation Results

{N_FOLDS}-fold CV was performed per cluster to assess temperature stability.

## Ablation Studies

### A1: Bounds Sensitivity
"""
    for key, val in results.get("ablations_bounds", {}).items():
        md += f"- {key}: CV={val['cv']:.4f}, Range={val['range']:.4f}\n"

    md += "\n### A2: Initialization Sensitivity\n"
    for key, val in results.get("ablations_init", {}).items():
        md += f"- {key}: CV={val['cv']:.4f}, Range={val['range']:.4f}\n"

    md += f"""
## Figures

- `figures/temperature_bar.png` - Bar chart of optimal T per cluster
- `figures/temperature_boxplot.png` - CV fold distribution
- `figures/temperature_line.png` - T across clusters
- `figures/cv_bootstrap_hist.png` - Bootstrap CV distribution

## Conclusion

{'The hypothesis is **supported**: optimal temperatures vary meaningfully across semantic clusters (CV > 0.1, Range > 0.3).' if gate_passed else 'The hypothesis is **not supported**: temperature variation across clusters is insufficient.'}

This {'validates' if gate_passed else 'does not validate'} the theoretical foundation for cluster-specific calibration.
"""

    with open(path, 'w') as f:
        f.write(md)


def main():
    """Main experiment orchestration."""
    print("=" * 60)
    print("H-M2: Per-cluster Temperature Scaling Variation")
    print("=" * 60)

    np.random.seed(SEED)
    torch.manual_seed(SEED)

    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # Step 1: Load model and data
    print("\n[1/9] Loading model and tokenizer...")
    model, tokenizer = load_model_and_tokenizer()
    device = next(model.parameters()).device
    print(f"Model loaded on device: {device}")

    print("\n[2/9] Loading TruthfulQA dataset...")
    dataset = load_truthfulqa_mc()
    dataset = assign_clusters(dataset)
    cluster_sizes = validate_cluster_sizes(dataset)
    print(f"Dataset size: {len(dataset)}")
    print(f"Cluster sizes: {cluster_sizes}")

    # Step 2: Collect logits by cluster
    print("\n[3/9] Collecting logits by cluster...")
    logits_by_cluster_raw, labels_by_cluster_raw = collect_logits_by_cluster(
        dataset, model, tokenizer, device
    )

    # Pad and stack for each cluster
    logits_by_cluster = {}
    labels_by_cluster = {}
    for cid in range(1, N_CLUSTERS + 1):
        logits, labels = pad_and_stack_cluster(
            logits_by_cluster_raw[cid], labels_by_cluster_raw[cid]
        )
        logits_by_cluster[cid] = logits
        labels_by_cluster[cid] = labels
        print(f"Cluster {cid}: {len(labels)} samples, max_choices={logits.shape[1] if len(logits) > 0 else 0}")

    # Step 3: Create CV splits
    print("\n[4/9] Creating stratified CV splits...")
    splits_by_cluster = stratified_kfold_splits(labels_by_cluster_raw)

    # Step 4: Cross-validate temperatures
    print("\n[5/9] Cross-validating temperatures...")
    fold_temps = cross_validate_temperatures(
        logits_by_cluster, labels_by_cluster, splits_by_cluster
    )
    for cid, temps in fold_temps.items():
        print(f"Cluster {cid}: T = {temps} (mean={np.mean(temps):.3f})")

    # Step 5: Optimize temperatures on full data
    print("\n[6/9] Optimizing temperatures on full data...")
    optimal_temps = optimize_temperature_per_cluster(logits_by_cluster, labels_by_cluster)
    for cid, T in optimal_temps.items():
        print(f"Cluster {cid}: T_opt = {T:.4f}")

    # Step 6: Compute metrics
    print("\n[7/9] Computing metrics...")
    cv, t_range = compute_cv_and_range(optimal_temps)
    temps_array = np.array(list(optimal_temps.values()))

    def cv_statistic(x, axis=None):
        return np.std(x, axis=axis) / np.mean(x, axis=axis)

    cv_ci = bootstrap_ci(temps_array, cv_statistic)
    primary_pass, secondary_pass = evaluate_gate(cv, t_range)
    gate_passed = primary_pass and secondary_pass

    print(f"CV = {cv:.4f} (threshold: > {CV_GATE_THRESHOLD}) -> {'PASS' if primary_pass else 'FAIL'}")
    print(f"Range = {t_range:.4f} (threshold: > {RANGE_GATE_THRESHOLD}) -> {'PASS' if secondary_pass else 'FAIL'}")
    print(f"Bootstrap CI for CV: [{cv_ci[0]:.4f}, {cv_ci[1]:.4f}]")
    print(f"Overall Gate: {'PASS' if gate_passed else 'FAIL'}")

    # Step 7: Ablation studies
    print("\n[8/9] Running ablation studies...")
    ablations_bounds = run_bounds_ablation(logits_by_cluster, labels_by_cluster)
    ablations_init = run_init_ablation(logits_by_cluster, labels_by_cluster)

    for key, val in ablations_bounds.items():
        print(f"A1 {key}: CV={val['cv']:.4f}, Range={val['range']:.4f}")
    for key, val in ablations_init.items():
        print(f"A2 {key}: CV={val['cv']:.4f}, Range={val['range']:.4f}")

    # Step 8: Generate visualizations
    print("\n[9/9] Generating visualizations...")
    plot_temperature_bar(optimal_temps, fold_temps)
    plot_temperature_boxplot(fold_temps)
    plot_t_vs_cluster_line(optimal_temps)

    bootstrap_cvs = []
    rng = np.random.RandomState(SEED)
    for _ in range(N_BOOTSTRAP):
        idx = rng.choice(len(temps_array), size=len(temps_array), replace=True)
        sample = temps_array[idx]
        bootstrap_cvs.append(np.std(sample) / np.mean(sample))
    bootstrap_cvs = np.array(bootstrap_cvs)
    plot_cv_bootstrap_hist(bootstrap_cvs)

    # Assemble results
    results = {
        "hypothesis_id": "h-m2",
        "timestamp": datetime.now().isoformat(),
        "optimal_temps": optimal_temps,
        "fold_temps": {str(k): v for k, v in fold_temps.items()},
        "cv": cv,
        "range": t_range,
        "cv_ci": list(cv_ci),
        "primary_pass": primary_pass,
        "secondary_pass": secondary_pass,
        "gate_passed": gate_passed,
        "ablations_bounds": {k: {"cv": v["cv"], "range": v["range"]} for k, v in ablations_bounds.items()},
        "ablations_init": {k: {"cv": v["cv"], "range": v["range"]} for k, v in ablations_init.items()},
        "cluster_sizes": cluster_sizes,
        "n_folds": N_FOLDS,
        "t_bounds": list(T_BOUNDS),
        "t_init": T_INIT,
    }

    # Save outputs
    save_results_json(results, RESULTS_JSON)
    save_validation_md(results, gate_passed, VALIDATION_MD)

    print("\n" + "=" * 60)
    print(f"EXPERIMENT COMPLETE: Gate {'PASS' if gate_passed else 'FAIL'}")
    print(f"Results: {RESULTS_JSON}")
    print(f"Report: {VALIDATION_MD}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
