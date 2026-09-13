from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import TypedDict

# Ensure code/ is on sys.path regardless of CWD
_CODE_DIR = Path(__file__).parent
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))

import numpy as np
import pandas as pd

from config import load_config
from ingest_pwc import fetch_pwc_benchmarks, fetch_pwc_results_via_evaluations
from derive import compute_result_cov
from pipeline import run_pelt_changepoint
from evaluate import (
    run_permutation_test,
    run_bootstrap_ci,
    run_piecewise_ftest,
    verify_mechanism_activated,
)
from visualize import save_all_figures


class ExperimentResults(TypedDict):
    permutation_p: float
    paper_count_star: float | None
    bootstrap_ci_lower: float
    bootstrap_ci_upper: float
    bootstrap_ci_width: float
    n_bkps_detected: int
    piecewise_f_p: float
    ols_rho: float
    ols_r2: float
    gate_passed: bool
    gate_reason: str
    n_benchmarks: int
    bic_penalty_used: float
    breakpoint_idx: int | None


def save_results(results: ExperimentResults, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    # Convert numpy types for JSON serialisation
    def _convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj
    serializable = {k: _convert(v) for k, v in results.items()}
    with open(path, "w") as f:
        json.dump(serializable, f, indent=2)
    print(f"Results saved → {path}")


def main() -> None:
    cfg = load_config()

    # Create output directories
    Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("H-E1: PELT Change-Point Detection on PwC CoV Series")
    print("=" * 60)

    # 1. Load benchmarks
    pwc_df = fetch_pwc_benchmarks(min_papers=cfg.min_papers)
    if pwc_df.empty or len(pwc_df) < 10:
        print(f"EARLY FAIL: Only {len(pwc_df)} benchmarks (< 10). Check MIN_PAPERS.")
        sys.exit(1)

    # 2. Load results
    results_df = fetch_pwc_results_via_evaluations(pwc_df)
    if results_df.empty:
        print("EARLY FAIL: No result rows loaded.")
        sys.exit(1)

    # 3. Compute CoV
    cov_series = compute_result_cov(results_df)
    merged = pwc_df.set_index("name").join(cov_series, how="inner").dropna(subset=["result_CoV"])
    merged = merged.reset_index()
    N = len(merged)
    print(f"Benchmarks with CoV: N={N}")

    if N < 10:
        print(f"EARLY FAIL: N={N} < 10 after CoV filter.")
        sys.exit(1)

    paper_counts = merged["paper_count"].values.astype(float)
    cov_values = merged["result_CoV"].values.astype(float)

    if cov_values.std() == 0:
        print("EARLY FAIL: Zero variance in CoV.")
        sys.exit(1)

    # 4. PELT change-point detection
    print("\n--- PELT Change-Point Detection ---")
    pelt_results = run_pelt_changepoint(paper_counts, cov_values)

    # 5. Permutation test
    print("\n--- Permutation Test (N=1000) ---")
    perm_results = run_permutation_test(
        paper_counts, cov_values,
        n_permutations=cfg.n_permutations,
        seed=cfg.seed,
    )

    # 6. Bootstrap CI
    print("\n--- Bootstrap CI (N=1000) ---")
    boot_results = run_bootstrap_ci(
        paper_counts, cov_values,
        n_resamples=cfg.n_bootstrap,
        seed=cfg.seed,
    )

    # 7. Piecewise F-test (only if breakpoint detected)
    print("\n--- Piecewise F-test ---")
    pcs = pelt_results["paper_count_star"]
    if pcs is not None:
        ftest_results = run_piecewise_ftest(paper_counts, cov_values, pcs)
    else:
        ftest_results = {"piecewise_f_p": float("nan"), "f_statistic": float("nan")}
        print("Skipped (no breakpoint detected)")

    # 8. Mechanism verification
    all_results = {
        "paper_count_star": pcs,
        "n_bkps_detected": pelt_results["n_bkps"],
        "permutation_p": perm_results["permutation_p"],
    }
    gate_passed, indicators = verify_mechanism_activated(all_results)

    # 9. Figures
    print("\n--- Saving Figures ---")
    save_all_figures(
        paper_counts, cov_values,
        pelt_results,
        {**perm_results, **boot_results},
        cfg.figures_dir,
    )

    # 10. Gate reason
    p = perm_results["permutation_p"]
    if gate_passed:
        gate_reason = (
            f"permutation_p={p:.4f} < {cfg.p_threshold} AND "
            f"paper_count_star={pcs:.0f} in [{cfg.paper_count_star_min}, {cfg.paper_count_star_max}]"
        )
    else:
        parts = []
        if not indicators["permutation_p_significant"]:
            parts.append(f"permutation_p={p:.4f} >= {cfg.p_threshold}")
        if not indicators["pelt_detected_breakpoint"]:
            parts.append("no breakpoint detected")
        if not indicators["paper_count_star_in_range"]:
            parts.append(f"paper_count_star={pcs} NOT in [{cfg.paper_count_star_min}, {cfg.paper_count_star_max}]")
        gate_reason = "FAIL: " + "; ".join(parts)

    # 11. Build results dict
    experiment_results: ExperimentResults = {
        "permutation_p": float(p),
        "paper_count_star": float(pcs) if pcs is not None else None,
        "bootstrap_ci_lower": float(boot_results["bootstrap_ci_lower"]),
        "bootstrap_ci_upper": float(boot_results["bootstrap_ci_upper"]),
        "bootstrap_ci_width": float(boot_results["bootstrap_ci_width"]),
        "n_bkps_detected": int(pelt_results["n_bkps"]),
        "piecewise_f_p": float(ftest_results["piecewise_f_p"]),
        "ols_rho": float(pelt_results["ols_metrics"]["rho"]),
        "ols_r2": float(pelt_results["ols_metrics"]["r2"]),
        "gate_passed": bool(gate_passed),
        "gate_reason": gate_reason,
        "n_benchmarks": int(N),
        "bic_penalty_used": float(pelt_results["pen_used"]),
        "breakpoint_idx": int(pelt_results["breakpoint_idx"]) if pelt_results["breakpoint_idx"] is not None else None,
    }

    # 12. Save JSON
    save_results(experiment_results, cfg.results_json)

    # 13. Gate summary
    print("\n" + "=" * 60)
    print(f"GATE: {'PASS ✓' if gate_passed else 'FAIL ✗'}")
    print(f"Reason: {gate_reason}")
    print(f"N_benchmarks: {N}")
    print(f"paper_count*: {pcs}")
    print(f"permutation_p: {p:.4f}")
    print(f"Bootstrap CI: [{boot_results['bootstrap_ci_lower']:.1f}, {boot_results['bootstrap_ci_upper']:.1f}]")
    print("=" * 60)

    if not gate_passed:
        sys.exit(2)


if __name__ == "__main__":
    main()
