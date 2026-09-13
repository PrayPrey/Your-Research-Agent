"""H-M2 main: PCA concentration test — Condition A vs Condition D."""
import json
import copy
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA

from data_prep import load_and_flatten, apply_condition_d, train_test_split_fixed
from evaluate import evaluate_pca_concentration, verify_mechanism_preconditions, compare_conditions
from figures import generate_all_figures

K_VALUES = [10, 20, 50]
SEED = 42
_HERE = Path(__file__).parent
FIGURES_DIR = str(_HERE.parent / "figures")
RESULTS_PATH = str(_HERE.parent / "results.json")


def run(
    k_values: list = None,
    seed: int = SEED,
    figures_dir: str = FIGURES_DIR,
    results_path: str = RESULTS_PATH,
    n_boot: int = 1000,
) -> dict:
    if k_values is None:
        k_values = K_VALUES

    # 1. Load
    print("=== H-M2: PCA Concentration Test ===")
    X, Y, label_names = load_and_flatten()

    # 2. Conditions
    X_A = X
    X_D = apply_condition_d(X)

    # 3. Split (consistent with H-M1: 450 train / 50 test, seed=42)
    X_tr_A, X_te_A, Y_tr, Y_te = train_test_split_fixed(X_A, Y, test_size=50, seed=seed)
    X_tr_D, X_te_D, _, _       = train_test_split_fixed(X_D, Y, test_size=50, seed=seed)

    print(f"Train: {X_tr_A.shape}, Test: {X_te_A.shape}")

    # 4. Preconditions
    verify_mechanism_preconditions(X_tr_A, X_tr_D)

    # 5. PCA concentration eval per label
    print("\n--- Evaluating PCA concentration ---")
    results_a, results_d = {}, {}
    for i, lname in enumerate(label_names):
        print(f"  Label: {lname}")
        results_a[lname] = evaluate_pca_concentration(
            X_tr_A, X_te_A, Y_tr[:, i], Y_te[:, i], k_values, n_boot, seed)
        results_d[lname] = evaluate_pca_concentration(
            X_tr_D, X_te_D, Y_tr[:, i], Y_te[:, i], k_values, n_boot, seed)
        for k in k_values:
            r2_a = results_a[lname][k]["r2"]
            r2_d = results_d[lname][k]["r2"]
            print(f"    k={k:2d}: R²_A={r2_a:.4f}, R²_D={r2_d:.4f}, ΔR²={r2_d-r2_a:+.4f}")

    # 6. Gate
    gate = compare_conditions(results_a, results_d, k_gate=20, n_tasks_required=2)
    print(f"\n=== GATE: {'PASS' if gate['gate_pass'] else 'FAIL'} "
          f"({gate['n_pass']}/{gate['n_required']} labels with non-overlapping CI at k=20) ===")
    for lname, det in gate["per_task"].items():
        status = "PASS" if det["pass"] else "FAIL"
        print(f"  {lname}: ΔR²={det['delta_r2']:+.4f}, "
              f"CI_A={det['ci_a']}, CI_D={det['ci_d']}, nonoverlap={det['ci_nonoverlap']} → {status}")

    # 7. Figures
    pca_a_k50 = PCA(n_components=50, random_state=42).fit(X_tr_A)
    pca_d_k50 = PCA(n_components=50, random_state=42).fit(X_tr_D)
    X_te_A_pca = pca_a_k50.transform(X_te_A)
    X_te_D_pca = pca_d_k50.transform(X_te_D)
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    generate_all_figures(results_a, results_d, pca_a_k50, pca_d_k50,
                         X_te_A_pca, X_te_D_pca, Y_te, label_names, figures_dir)

    # 8. Save results (strip non-serializable y_pred)
    output = {
        "gate_pass": gate["gate_pass"],
        "n_pass": gate["n_pass"],
        "n_required": gate["n_required"],
        "gate_details": gate["per_task"],
        "per_label": {"condition_a": results_a, "condition_d": results_d},
    }
    serializable = copy.deepcopy(output)
    for lname in label_names:
        for cond in ["condition_a", "condition_d"]:
            for k in k_values:
                serializable["per_label"][cond][lname][k].pop("y_pred", None)
                # Convert numpy arrays to lists
                ci = serializable["per_label"][cond][lname][k]["ci"]
                serializable["per_label"][cond][lname][k]["ci"] = [float(c) for c in ci]
        for cond_key in ["ci_a", "ci_d"]:
            if cond_key in serializable["gate_details"].get(lname, {}):
                serializable["gate_details"][lname][cond_key] = [
                    float(c) for c in serializable["gate_details"][lname][cond_key]
                ]

    def _to_python(obj):
        if isinstance(obj, dict):
            return {k: _to_python(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_to_python(v) for v in obj]
        if hasattr(obj, "item"):  # numpy scalar
            return obj.item()
        return obj

    serializable = _to_python(serializable)
    Path(results_path).parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, "w") as f:
        json.dump(serializable, f, indent=2)
    print(f"\nResults saved: {results_path}")
    return output


if __name__ == "__main__":
    run()
