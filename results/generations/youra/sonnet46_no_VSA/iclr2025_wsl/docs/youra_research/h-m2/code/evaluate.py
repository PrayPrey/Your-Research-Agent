"""H-M2: Mechanism verifier, gate check, C0 feature extractor, result saving."""
import csv
import json
import os
import sys

import numpy as np

# H-M1 bootstrap for audit_functional_equivalence
_HERE = os.path.dirname(os.path.abspath(__file__))
_H_M1_CODE = os.path.join(_HERE, '..', '..', 'h-m1', 'code')
sys.path.insert(0, os.path.abspath(_H_M1_CODE))

from permutation import audit_functional_equivalence  # noqa: E402

C0_R2: float = 0.984
C0_TAU: float = 0.915
GATE_RATIO: float = 0.10
RESULTS_DIR: str = "results"


def run_permutation_validator(dataset: list, perm_specs: list) -> dict:
    """
    Wraps audit_functional_equivalence from H-M1.
    Returns {"pass": bool, "max_diff": float}.
    Calls sys.exit(2) if validator fails.
    """
    print("[validator] Running permutation functional equivalence audit...")
    try:
        max_diff = audit_functional_equivalence(
            dataset[0], perm_specs, tol=1e-4, n_checks=3, n_perms=3
        )
        print(f"[validator] PASS — max_diff={max_diff:.2e}")
        return {"pass": True, "max_diff": float(max_diff)}
    except AssertionError as e:
        print(f"[validator] ERROR: Permutation not functional — H-M1 result invalid: {e}")
        sys.exit(2)


def compute_c0_features(state_dicts: list) -> np.ndarray:
    """
    Returns X_c0: (N, 7 * n_layers) — per-layer [mean, var, p0, p25, p50, p75, p100].
    Reference only; C0 R²/τ are fixed constants — no LightGBM retraining.
    """
    results = []
    for sd in state_dicts:
        row = []
        for key, W in sd.items():
            if not hasattr(W, 'dim') or W.dim() != 4:
                continue
            w_flat = W.float().cpu().numpy().flatten()
            row.extend([
                float(np.mean(w_flat)),
                float(np.var(w_flat)),
                float(np.percentile(w_flat, 0)),
                float(np.percentile(w_flat, 25)),
                float(np.percentile(w_flat, 50)),
                float(np.percentile(w_flat, 75)),
                float(np.percentile(w_flat, 100)),
            ])
        results.append(row)
    return np.array(results, dtype=np.float64)


def verify_mechanism(
    orbit_preds: np.ndarray,
    mse_total: float,
    mse_perm: float,
    ratio: float,
) -> dict:
    """
    Returns indicators dict with gate_result.
    Asserts shape (100, 50), nonzero variance, mse_perm > 0, ratio in [0, 1].
    """
    indicators = {}

    indicators["orbit_preds_shape_valid"] = (orbit_preds.shape == (100, 50))
    assert indicators["orbit_preds_shape_valid"], \
        f"Expected orbit_preds.shape==(100, 50), got {orbit_preds.shape}"

    mean_var = float(np.mean(np.var(orbit_preds, axis=1)))
    indicators["nonzero_orbit_variance"] = (mean_var > 1e-10)
    assert indicators["nonzero_orbit_variance"], \
        f"orbit variance effectively zero: mean_var={mean_var:.2e}"

    indicators["mse_perm_positive"] = (mse_perm > 0)
    assert indicators["mse_perm_positive"], f"mse_perm={mse_perm} <= 0"

    indicators["ratio_computed"] = (ratio >= 0.0)
    assert indicators["ratio_computed"], f"ratio={ratio:.4f} < 0 — impossible"

    # Gate: report only, no assert
    indicators["gate_result"] = (ratio >= GATE_RATIO)
    print(f"[verify_mechanism] MSE_perm/MSE_total = {ratio:.4f} (gate: >= {GATE_RATIO})")

    return indicators


def gate_check(results: dict) -> bool:
    """Prints PASS/FAIL lines. Returns True if primary gate passes."""
    ratio = results["ratio"]
    gate_pass = ratio >= GATE_RATIO

    print("\n" + "=" * 60)
    print("H-M2 GATE CHECK (MUST_WORK)")
    print("=" * 60)
    print(f"MSE_perm / MSE_total = {ratio:.4f}  (threshold >= {GATE_RATIO}):  {'PASS' if gate_pass else 'FAIL'}")
    print(f"MSE_total = {results['mse_total']:.6f}")
    print(f"MSE_perm  = {results['mse_perm']:.6f}")
    print(f"MSE_res   = {results['mse_res']:.6f}")
    print(f"R²(C1)    = {results['r2_c1']:.4f}")
    print(f"τ(C1)     = {results['tau_c1']:.4f}")
    print(f"R²(C0 ref)= {C0_R2:.4f}")
    print("=" * 60)
    print(f"OVERALL: {'GATE PASS' if gate_pass else 'GATE FAIL'}")
    return gate_pass


def save_results(results: dict, summary: dict) -> None:
    """Saves results/mse_decomposition.json and results/h_m2_summary.csv."""
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Convert ndarray to list for JSON serialisation
    json_results = {}
    for k, v in results.items():
        if isinstance(v, np.ndarray):
            json_results[k] = v.tolist()
        elif isinstance(v, (np.float32, np.float64)):
            json_results[k] = float(v)
        else:
            json_results[k] = v

    json_path = os.path.join(RESULTS_DIR, "mse_decomposition.json")
    with open(json_path, "w") as f:
        json.dump(json_results, f, indent=2)
    print(f"Results saved: {json_path}")

    csv_path = os.path.join(RESULTS_DIR, "h_m2_summary.csv")
    header = list(summary.keys())
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerow(summary)
    print(f"CSV saved: {csv_path}")
