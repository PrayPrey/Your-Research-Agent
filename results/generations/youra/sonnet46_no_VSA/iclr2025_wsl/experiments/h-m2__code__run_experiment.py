"""H-M2: OrbitVar Propagation to LightGBM Prediction Space.

Entry: python run_experiment.py
Returns exit code 0 on GATE PASS, 1 on GATE FAIL.
"""
import json
import os
import sys

import numpy as np

# ── Paths ────────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))

# H-M1 code on sys.path (needed by embeddings.py, evaluate.py)
_H_M1_CODE = os.path.join(_HERE, '..', '..', 'h-m1', 'code')
sys.path.insert(0, os.path.abspath(_H_M1_CODE))
sys.path.insert(0, _HERE)

DATA_PATH = os.path.join(_HERE, '..', '..', '..', '..', 'data', 'cifar10_gs',
                         'dataset_cifar_small_hyp_rand.pt')
H1_RESULTS_PATH = os.path.join(_HERE, '..', '..', 'h-m1', 'results', 'orbit_var_ratios.json')
RESULTS_DIR = os.path.join(_HERE, 'results')
FIGURES_DIR = os.path.join(_HERE, 'figures')

from embeddings import load_or_compute_embeddings, verify_orbit_var  # noqa: E402
from lgbm_trainer import run_cv_lgbm, compute_orbit_preds, decompose_mse  # noqa: E402
from evaluate import run_permutation_validator, verify_mechanism, gate_check, save_results  # noqa: E402
from visualize import (  # noqa: E402
    plot_mse_decomposition,
    plot_orbit_var_histogram,
    plot_r2_comparison,
    plot_orbitvar_vs_pred_var,
    plot_orbit_fan,
)
from data_loader import load_dataset  # noqa: E402


def main() -> int:
    print("=" * 60)
    print("H-M2: OrbitVar Propagation → LightGBM Prediction Variance")
    print("=" * 60)
    print(f"Data:    {DATA_PATH}")
    print(f"H1 res:  {H1_RESULTS_PATH}")

    os.chdir(_HERE)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    # ── Step 1: Load embeddings ───────────────────────────────────────────────
    print("\n[Step 1] Loading/computing CISE embeddings...")
    X_cise, permuted_X, y_acc, perm_specs, orbit_var_h1 = load_or_compute_embeddings(
        pt_path=DATA_PATH,
        h1_results_path=H1_RESULTS_PATH,
        n_models=100,
        K=50,
        embed_dim=64,
        seed=1,
    )
    print(f"  X_cise:     {X_cise.shape}  (dtype={X_cise.dtype})")
    print(f"  permuted_X: {permuted_X.shape}")
    print(f"  y_acc:      {y_acc.shape}  range=[{y_acc.min():.3f}, {y_acc.max():.3f}]")
    print(f"  orbit_var (H-M1): {orbit_var_h1:.6f}")

    # ── Step 2: Verify orbit_var prerequisite ────────────────────────────────
    print("\n[Step 2] Verifying H-M1 orbit_var prerequisite...")
    verify_orbit_var(orbit_var_h1)

    # ── Step 3: Permutation validator ────────────────────────────────────────
    print("\n[Step 3] Permutation validator audit...")
    dataset, _ = load_dataset(DATA_PATH, n_models=100)
    val_result = run_permutation_validator(dataset, perm_specs)
    print(f"  Validator: {val_result}")

    # ── Step 4: 5-fold CV LightGBM ───────────────────────────────────────────
    print("\n[Step 4] 5-fold CV LightGBM on C1 embeddings...")
    fold_preds, full_model = run_cv_lgbm(X_cise, y_acc, n_splits=5, random_state=42)

    # ── Step 5: Orbit predictions (K=50 permuted embeddings) ─────────────────
    print("\n[Step 5] Computing orbit predictions...")
    orbit_preds = compute_orbit_preds(full_model, permuted_X)

    # ── Step 6: MSE decomposition ─────────────────────────────────────────────
    print("\n[Step 6] MSE decomposition...")
    results = decompose_mse(y_acc, fold_preds, orbit_preds)

    # ── Step 7: Mechanism verification ───────────────────────────────────────
    print("\n[Step 7] Mechanism verification...")
    indicators = verify_mechanism(
        orbit_preds=results["orbit_preds"],
        mse_total=results["mse_total"],
        mse_perm=results["mse_perm"],
        ratio=results["ratio"],
    )
    results["indicators"] = {k: bool(v) for k, v in indicators.items()}

    # ── Step 8: Gate check ───────────────────────────────────────────────────
    gate_passed = gate_check(results)

    # ── Step 9: Save results ─────────────────────────────────────────────────
    print("\n[Step 9] Saving results...")
    summary = {
        "hypothesis_id": "h-m2",
        "gate_passed": gate_passed,
        "mse_total": results["mse_total"],
        "mse_perm": results["mse_perm"],
        "mse_res": results["mse_res"],
        "ratio": results["ratio"],
        "r2_c1": results["r2_c1"],
        "tau_c1": results["tau_c1"],
        "r2_c1_avg": results["r2_c1_avg"],
        "tau_c1_avg": results["tau_c1_avg"],
        "orbit_var_h1": orbit_var_h1,
    }
    save_results(results, summary)

    # Save experiment_results.json at hypothesis level
    exp_json_path = os.path.join(_HERE, '..', 'experiment_results.json')
    exp_results = dict(summary)
    exp_results["orbit_preds_shape"] = list(results["orbit_preds"].shape)
    exp_results["per_model_orbit_var"] = results["per_model_orbit_var"].tolist()
    with open(exp_json_path, "w") as f:
        json.dump(exp_results, f, indent=2)
    print(f"experiment_results.json saved: {os.path.abspath(exp_json_path)}")

    # ── Step 10: Figures ─────────────────────────────────────────────────────
    print("\n[Step 10] Generating figures...")

    # Load h-m1 per-model orbit vars for scatter (Figure 4)
    h1_per_model_vars = None
    if os.path.exists(H1_RESULTS_PATH):
        with open(H1_RESULTS_PATH) as f:
            h1_data = json.load(f)
        if "per_model" in h1_data and "orbit_vars_C1" in h1_data["per_model"]:
            h1_per_model_vars = h1_data["per_model"]["orbit_vars_C1"]

    plot_mse_decomposition(
        mse_total=results["mse_total"],
        mse_perm=results["mse_perm"],
        mse_res=results["mse_res"],
        ratio=results["ratio"],
    )
    plot_orbit_var_histogram(results["per_model_orbit_var"])
    plot_r2_comparison(r2_c1=results["r2_c1"], r2_c1_avg=results["r2_c1_avg"])

    if h1_per_model_vars is not None:
        plot_orbitvar_vs_pred_var(h1_per_model_vars, results["per_model_orbit_var"])
    else:
        plot_orbitvar_vs_pred_var(
            results["per_model_orbit_var"].tolist(), results["per_model_orbit_var"]
        )
    plot_orbit_fan(results["orbit_preds"])

    print(f"\nEXPERIMENT COMPLETE (exit={'0' if gate_passed else '1'})")
    return 0 if gate_passed else 1


if __name__ == "__main__":
    sys.exit(main())
