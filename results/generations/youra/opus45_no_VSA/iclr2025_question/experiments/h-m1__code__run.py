#!/usr/bin/env python3
# run.py - h-m1 MECHANISM: Combined model [H_L + NTI + CMI] vs H_L baseline
import os
import sys
import json
import random
import numpy as np
import torch

# Setup paths - h-m1 code dir first, then h-e1 for data/model reuse
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
H_E1_CODE_DIR = os.path.join(CODE_DIR, "../../h-e1/code")
sys.path.insert(0, CODE_DIR)

# Import local h-m1 modules
from config import CONFIG
from cmi import compute_cmi
from evaluate import build_feature_matrices, run_cv_lrt, check_gate
from visualize import (
    plot_gate_metrics,
    plot_lrt_pvalue,
    plot_roc_overlay,
    plot_fold_auroc_bars,
    plot_coefficients,
    plot_nti_cmi_scatter,
)

# Import h-e1 modules explicitly via importlib
import importlib.util

def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    # Inject CONFIG for h-e1 modules
    mod.__dict__["CONFIG"] = CONFIG
    spec.loader.exec_module(mod)
    return mod

h_e1_data = _load_module("h_e1_data", os.path.join(H_E1_CODE_DIR, "data.py"))
h_e1_model = _load_module("h_e1_model", os.path.join(H_E1_CODE_DIR, "model.py"))

load_truthfulqa_mc1 = h_e1_data.load_truthfulqa_mc1
build_prompts = h_e1_data.build_prompts
load_model = h_e1_model.load_model
extract_all_scores = h_e1_model.extract_all_scores


def set_seed(seed):
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def main():
    print("=" * 60)
    print("h-m1 MECHANISM PoC: Combined Model vs H_L Baseline")
    print("=" * 60)

    # Setup
    set_seed(CONFIG["seed"])
    os.makedirs(CONFIG["figures_dir"], exist_ok=True)
    os.makedirs(CONFIG["outputs_dir"], exist_ok=True)

    # Step 1: Load data
    print("\n[1/6] Loading TruthfulQA MC1 dataset...")
    samples = load_truthfulqa_mc1()
    prompts, labels = build_prompts(samples)
    print(f"  Loaded {len(samples)} questions -> {len(prompts)} prompt-choice pairs")
    print(f"  Label distribution: {sum(labels)} correct, {len(labels) - sum(labels)} incorrect")

    # Step 2: Load model
    print("\n[2/6] Loading LLaMA-2-7B via TransformerLens...")
    model = load_model()
    print(f"  Model loaded on {CONFIG['device']} with dtype={CONFIG['dtype']}")

    # Step 3: Extract scores (reuse h-e1 extraction)
    print("\n[3/6] Extracting NTI, trajectory, baseline_entropy...")
    print(f"  Processing {len(prompts)} prompts in batches of {CONFIG['batch_size']}...")
    scores = extract_all_scores(model, prompts)
    print(f"  NTI shape: {scores['nti'].shape}")
    print(f"  Trajectory shape: {scores['trajectory'].shape}")
    print(f"  H_L (baseline_entropy) shape: {scores['baseline_entropy'].shape}")

    # Step 4: Compute CMI from trajectory
    print("\n[4/6] Computing CMI from trajectory...")
    cmi = compute_cmi(scores["trajectory"])
    print(f"  CMI shape: {cmi.shape}")
    print(f"  CMI range: [{cmi.min():.4f}, {cmi.max():.4f}]")

    # Step 5: Build feature matrices and run CV with LRT
    print("\n[5/6] Running 5-fold CV: Null (H_L) vs Full (H_L+NTI+CMI)...")
    h_l = scores["baseline_entropy"]
    nti = scores["nti"]
    X_null, X_full = build_feature_matrices(h_l, nti, cmi)
    print(f"  X_null shape: {X_null.shape}")
    print(f"  X_full shape: {X_full.shape}")

    cv_results = run_cv_lrt(X_null, X_full, labels)
    passed, reason, verdict = check_gate(cv_results)

    print(f"\n  Results:")
    print(f"    Null AUROC (H_L only):  {cv_results['mean_auroc_null']:.4f}")
    print(f"    Full AUROC (H_L+NTI+CMI): {cv_results['mean_auroc_full']:.4f}")
    print(f"    AUROC Gain:  {cv_results['mean_auroc_gain']:.4f} (threshold: {CONFIG['auroc_gain_threshold']})")
    print(f"    Combined p-value: {cv_results['combined_p_value']:.4e} (threshold: {CONFIG['lrt_pvalue_threshold']})")
    fold_gains = [f"{r['auroc_gain']:.4f}" for r in cv_results["fold_results"]]
    fold_pvals = [f"{r['p_value']:.4e}" for r in cv_results["fold_results"]]
    print(f"\n  Per-fold gains: {fold_gains}")
    print(f"  Per-fold p-values: {fold_pvals}")
    print(f"\n  Gate Verdict: {verdict}")
    print(f"  Reason: {reason}")

    # Step 6: Visualize
    print("\n[6/6] Generating figures...")
    fig_paths = []
    fig_paths.append(plot_gate_metrics(cv_results))
    fig_paths.append(plot_lrt_pvalue(cv_results))
    fig_paths.append(plot_roc_overlay(cv_results))
    fig_paths.append(plot_fold_auroc_bars(cv_results))
    fig_paths.append(plot_coefficients(cv_results))
    fig_paths.append(plot_nti_cmi_scatter(nti, cmi, labels))
    for p in fig_paths:
        print(f"  Saved: {p}")

    # Save results
    results_path = os.path.join(CONFIG["outputs_dir"], "results.json")
    results = {
        "hypothesis_id": "h-m1",
        "gate_type": "SHOULD_WORK",
        "gate_passed": passed,
        "verdict": verdict,
        "reason": reason,
        "metrics": {
            "mean_auroc_null": float(cv_results["mean_auroc_null"]),
            "mean_auroc_full": float(cv_results["mean_auroc_full"]),
            "mean_auroc_gain": float(cv_results["mean_auroc_gain"]),
            "std_auroc_gain": float(cv_results["std_auroc_gain"]),
            "combined_p_value": float(cv_results["combined_p_value"]),
            "fold_results": [
                {
                    "fold": r["fold"],
                    "auroc_null": float(r["auroc_null"]),
                    "auroc_full": float(r["auroc_full"]),
                    "auroc_gain": float(r["auroc_gain"]),
                    "G": float(r["G"]),
                    "p_value": float(r["p_value"]),
                }
                for r in cv_results["fold_results"]
            ],
        },
        "thresholds": {
            "auroc_gain_threshold": CONFIG["auroc_gain_threshold"],
            "lrt_pvalue_threshold": CONFIG["lrt_pvalue_threshold"],
            "falsify_gain": CONFIG["falsify_gain"],
            "falsify_pvalue": CONFIG["falsify_pvalue"],
        },
        "dataset": {
            "name": "TruthfulQA MC1",
            "n_samples": len(samples),
            "n_prompts": len(prompts),
        },
        "model": CONFIG["model_id"],
        "figures": fig_paths,
    }

    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved: {results_path}")

    print("\n" + "=" * 60)
    print(f"EXPERIMENT COMPLETE: {verdict}")
    print("=" * 60)

    return passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
