#!/usr/bin/env python3
"""Run H-M1 experiment: NFN equivariant feature extraction vs statistics baseline."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import numpy as np
from pathlib import Path
from datetime import datetime

import config
from data import download_model_zoo, load_checkpoints, split_test_set
from features import build_feature_matrix
from baseline_model import fit_ridge, evaluate as evaluate_baseline
from nfn_model import NFNAccuracyPredictor
from train import train_nfn, evaluate_nfn, set_seed
from equivariance import equivariance_pass_rate, generate_neuron_permutation, verify_equivariance
from nfn_model import extract_weight_tensors
import evaluate as viz


def main():
    cfg = config.CONFIG
    results_all = []

    print("=" * 60)
    print("H-M1 Experiment: NFN Equivariant Feature Extraction")
    print("=" * 60)

    # Setup directories
    code_dir = Path(__file__).parent
    figures_dir = code_dir / cfg.figures_dir
    figures_dir.mkdir(exist_ok=True)

    # Load data (reuse H-E1 synthetic zoo)
    print("\n[1/6] Loading Model Zoo...")
    zoo_path = download_model_zoo(dest_dir=str(code_dir / cfg.data.zoo_dir))
    items = load_checkpoints(zoo_path)
    train_pool, test_items = split_test_set(items, test_size=cfg.data.n_test, seed=cfg.data.split_seed)

    # Use full train set
    train_items = train_pool[:cfg.data.n_train]
    print(f"Train: {len(train_items)}, Test: {len(test_items)}")

    # Run baseline
    print("\n[2/6] Running Statistics Baseline...")
    X_train, y_train = build_feature_matrix(train_items)
    X_test, y_test = build_feature_matrix(test_items)
    ridge = fit_ridge(X_train, y_train)
    baseline_r2 = evaluate_baseline(ridge, X_test, y_test)
    print(f"Baseline R²: {baseline_r2:.4f}")

    # Train NFN with multiple seeds
    print("\n[3/6] Training NFN (multiple seeds)...")
    nfn_results = []

    for seed in cfg.train.seeds:
        print(f"\n--- Seed {seed} ---")
        set_seed(seed)

        # Create validation split from train
        val_size = min(500, len(train_items) // 10)
        val_items = train_items[:val_size]
        train_subset = train_items[val_size:]

        model = NFNAccuracyPredictor(
            hidden_dim=cfg.model.hidden_dim,
            num_layers=cfg.model.num_layers
        )

        history = train_nfn(model, train_subset, val_items, cfg=cfg)

        # Evaluate on test set
        metrics = evaluate_nfn(model, test_items)
        print(f"Seed {seed}: R² = {metrics['r2']:.4f}, MAE = {metrics['mae']:.4f}")

        nfn_results.append({
            "seed": seed,
            "r2": metrics["r2"],
            "mae": metrics["mae"],
            "history": history,
            "y_true": metrics["y_true"],
            "y_pred": metrics["y_pred"],
            "model": model,
        })

    # Aggregate NFN results
    nfn_r2_mean = np.mean([r["r2"] for r in nfn_results])
    nfn_r2_std = np.std([r["r2"] for r in nfn_results])
    nfn_mae_mean = np.mean([r["mae"] for r in nfn_results])

    print(f"\nNFN R² (mean±std): {nfn_r2_mean:.4f} ± {nfn_r2_std:.4f}")

    # Equivariance verification
    print("\n[4/6] Verifying Equivariance...")
    best_model = max(nfn_results, key=lambda x: x["r2"])["model"]
    pass_rate, max_err = equivariance_pass_rate(best_model, test_items, n_trials=5, atol=cfg.eval.equivariance_tol, device="cpu")
    print(f"Equivariance pass rate: {pass_rate*100:.1f}%")
    print(f"Max equivariance error: {max_err:.2e}")

    # Generate figures
    print("\n[5/6] Generating Figures...")
    best_result = max(nfn_results, key=lambda x: x["r2"])

    viz.plot_gate_comparison(nfn_r2_mean, baseline_r2, str(figures_dir / "gate_comparison.png"))
    viz.plot_prediction_scatter(best_result["y_true"], best_result["y_pred"],
                                 best_result["r2"], str(figures_dir / "prediction_scatter.png"))
    viz.plot_equivariance(pass_rate, max_err, str(figures_dir / "equivariance_test.png"))
    viz.plot_training_curve(best_result["history"], str(figures_dir / "training_curve.png"))
    viz.plot_residuals(best_result["y_true"], best_result["y_pred"], str(figures_dir / "residuals.png"))

    # Gate verdict
    print("\n[6/6] Gate Evaluation...")
    gate_passed = (
        pass_rate >= 0.95 and  # 95%+ equivariance tests pass
        nfn_r2_mean >= cfg.eval.r2_target  # R² >= 0.85
    )

    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "baseline": {
            "r2": baseline_r2,
            "method": "RidgeCV on layer statistics",
        },
        "nfn": {
            "r2_mean": nfn_r2_mean,
            "r2_std": nfn_r2_std,
            "mae_mean": nfn_mae_mean,
            "seeds": cfg.train.seeds,
            "per_seed": [{"seed": r["seed"], "r2": r["r2"], "mae": r["mae"]} for r in nfn_results],
        },
        "equivariance": {
            "pass_rate": pass_rate,
            "max_error": max_err,
            "tolerance": cfg.eval.equivariance_tol,
        },
        "gate": {
            "type": "MUST_WORK",
            "r2_target": cfg.eval.r2_target,
            "result": "PASSED" if gate_passed else "FAILED",
            "criteria": {
                "equivariance_pass_rate": bool(pass_rate >= 0.95),
                "r2_above_target": bool(nfn_r2_mean >= cfg.eval.r2_target),
            }
        },
        "config": {
            "n_train": cfg.data.n_train,
            "n_test": cfg.data.n_test,
            "hidden_dim": cfg.model.hidden_dim,
            "num_layers": cfg.model.num_layers,
        }
    }

    results_path = code_dir / "results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Statistics Baseline R²: {baseline_r2:.4f}")
    print(f"NFN R² (mean±std):      {nfn_r2_mean:.4f} ± {nfn_r2_std:.4f}")
    print(f"Equivariance Pass Rate: {pass_rate*100:.1f}%")
    print(f"Gate Result:            {'PASSED' if gate_passed else 'FAILED'}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    results = main()
    print("\nEXPERIMENT COMPLETE")
