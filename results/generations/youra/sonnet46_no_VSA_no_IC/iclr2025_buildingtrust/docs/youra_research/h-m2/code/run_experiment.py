"""H-M2 entry point: build data, run analysis, generate figures."""
import argparse
import json
import logging
import sys
from pathlib import Path

# Ensure code/ is on sys.path for relative imports
_CODE_DIR = Path(__file__).parent
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))

from config import DELTA_RHO_GATE, FIGURES_DIR, RESULTS_DIR
from data import build_master_dataframe, verify_preconditions
from analysis import run_full_analysis, evaluate_gate
from visualize import generate_all_figures

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description="H-M2: Differential Rank Stability Analysis")
    parser.add_argument("--skip-figures", action="store_true",
                        help="Skip figure generation (for dry-run / CI)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Run _self_check() only — no real data")
    args = parser.parse_args()

    if args.dry_run:
        _self_check()
        print("✅ Dry run (self-check) passed.")
        return

    print("=" * 60)
    print("H-M2: Differential Rank Stability Analysis")
    print("Fairness vs. Adversarial Robustness (SHOULD_WORK gate)")
    print("=" * 60)

    # Step 1: Build master DataFrame
    print("\n[1/4] Building master DataFrame (h-m1 base + robustness scores)...")
    df = build_master_dataframe()

    # Step 2: Verify preconditions
    print("\n[2/4] Verifying preconditions...")
    n = verify_preconditions(df)
    print(f"  N_common_robust = {n}")

    # Step 3: Run full analysis
    print("\n[3/4] Running statistical analysis...")
    results = run_full_analysis(df)

    # Step 4: Print summary
    print("\n[4/4] Results Summary:")
    print(f"  N models:              {results['n']}")
    print(f"  partial rho_fairness:  {results['rho_fairness']['rho']:.4f}  (p={results['rho_fairness']['p_value']:.4f})")
    print(f"  partial rho_AdvGLUE:   {results['rho_advglue']['rho']:.4f}  (p={results['rho_advglue']['p_value']:.4f})")
    print(f"  partial rho_ANLI:      {results['rho_anli']['rho']:.4f}  (p={results['rho_anli']['p_value']:.4f})")
    print(f"  rho_robust_mean:       {results['rho_robust_mean']:.4f}")
    print(f"  Δρ:                    {results['delta_rho']:.4f}  (threshold: {DELTA_RHO_GATE})")
    print(f"  Fisher z:              z={results['fisher_z']['z_stat']:.4f}, p={results['fisher_z']['p_value_two_tailed']:.4f}")
    print(f"  Gate (Δρ ≥ 0.2):       {'PASS ✅' if results['gate_directional'] else 'FAIL ❌'}")
    print(f"  Secondary (both < fair): {'✅' if results['secondary_both'] else '❌'}")

    if results["sensitivity_wino"]:
        sw = results["sensitivity_wino"]
        print(f"  Sensitivity (Wino Δρ): {sw['delta_rho']:.4f}")
    else:
        print(f"  Sensitivity (Wino):    skipped (N < {8})")

    # Step 5: Figures
    if not args.skip_figures:
        print("\n[5/5] Generating figures...")
        generate_all_figures(df, results, FIGURES_DIR)
        print(f"  Figures saved to: {FIGURES_DIR}")

    # Final status
    gate_pass = results["gate_directional"]
    print("\n" + "=" * 60)
    if gate_pass:
        print("✅ GATE PASSED — Δρ ≥ 0.2 satisfied")
        print("   Hypothesis H-M2 directionally supported.")
    else:
        print("❌ GATE FAILED — Δρ < 0.2")
        print("   Limitation noted. Pipeline continues to H-M3.")
    print("=" * 60)

    print(f"\nResults saved to: {RESULTS_DIR / 'results.json'}")
    print(f"EXPERIMENT COMPLETE")


def _self_check() -> None:
    """10-row synthetic DataFrame smoke test for analysis functions."""
    import numpy as np
    import pandas as pd
    from analysis import (
        compute_raw_rho_all, compute_partial_rho, fisher_z_test_difference
    )

    rng = np.random.default_rng(42)
    n = 12
    df = pd.DataFrame({
        "model_name":    [f"model_{i}" for i in range(n)],
        "bbq_disambig":  rng.uniform(0.4, 0.9, n),
        "bbq_ambig":     rng.uniform(0.3, 0.8, n),
        "mmlu":          rng.uniform(0.3, 0.9, n),
        "winogrande":    rng.uniform(0.4, 0.9, n),
        "glue_score":    rng.uniform(0.4, 0.85, n),
        "advglue_score": rng.uniform(0.2, 0.6, n),
        "anli_r1_score": rng.uniform(0.3, 0.7, n),
        "anli_r3_score": rng.uniform(0.2, 0.6, n),
    })

    raw = compute_raw_rho_all(df)
    assert "rho_fair_raw" in raw, "compute_raw_rho_all failed"

    res = compute_partial_rho(df, "bbq_disambig", "bbq_ambig", "mmlu")
    assert "rho" in res and "p_value" in res, "compute_partial_rho failed"

    fisher = fisher_z_test_difference(rho1=0.6, rho2=0.2, n=12)
    assert "z_stat" in fisher and "p_value_two_tailed" in fisher, "fisher_z_test_difference failed"
    assert fisher["z_stat"] > 0, "Fisher z should be positive when rho1 > rho2"

    print("✅ Self-check passed (all 3 core functions verified)")


if __name__ == "__main__":
    main()
