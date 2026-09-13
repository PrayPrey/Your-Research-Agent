"""H-M3 experiment entry point."""
import argparse
import logging
import sys

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)


def _self_check() -> None:
    from analysis import compute_partial_spearman, count_rank_reversals, evaluate_gate, verify_mechanism_activated
    np.random.seed(42)
    df = pd.DataFrame({
        "model_name": [f"m{i}" for i in range(12)],
        "glue_score": np.random.uniform(0.5, 0.9, 12),
        "advglue_score": np.random.uniform(0.3, 0.7, 12),
        "anli_r1_score": np.random.uniform(0.4, 0.8, 12),
        "anli_r3_score": np.random.uniform(0.2, 0.6, 12),
        "mmlu": np.random.uniform(0.4, 0.9, 12),
    })
    r = compute_partial_spearman(df, "glue_score", "advglue_score")
    assert "rho" in r and "n" in r
    rev = count_rank_reversals(df, "glue_score", "advglue_score")
    assert isinstance(rev, int)
    results = {"rho_AdvGLUE": r["rho"], "rho_ANLI": 0.1, "reversals_AdvGLUE": rev, "reversals_ANLI": 2}
    mech_ok, indicators = verify_mechanism_activated(df, results)
    assert isinstance(mech_ok, bool)
    gate = evaluate_gate(0.2, 0.3, 0.15, 0.4)
    assert gate is True
    log.info("Self-check passed.")


def main() -> None:
    parser = argparse.ArgumentParser(description="H-M3 experiment")
    parser.add_argument("--skip-figures", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        _self_check()
        return

    from analysis import run_full_analysis
    from config import FIGURES_DIR
    from data import load_rho_fairness, load_scores
    from visualize import generate_all_figures

    df = load_scores()
    rho_fairness = load_rho_fairness()
    results = run_full_analysis(df, rho_fairness)

    print(f"\n=== H-M3 Results ===")
    print(f"N models: {results['n']}")
    print(f"rho_AdvGLUE = {results['rho_AdvGLUE']:.4f}, p = {results['p_AdvGLUE']:.4f}, CI = {results['ci_AdvGLUE']}")
    print(f"rho_ANLI    = {results['rho_ANLI']:.4f}, p = {results['p_ANLI']:.4f}, CI = {results['ci_ANLI']}")
    print(f"Fisher z AdvGLUE: z={results['z_AdvGLUE']:.3f}, p={results['p_z_AdvGLUE']:.4f}, sig={results['sig_AdvGLUE']}")
    print(f"Fisher z ANLI:    z={results['z_ANLI']:.3f}, p={results['p_z_ANLI']:.4f}, sig={results['sig_ANLI']}")
    print(f"Rank reversals AdvGLUE: {results['reversals_AdvGLUE']}")
    print(f"Rank reversals ANLI:    {results['reversals_ANLI']}")
    print(f"Mechanism OK: {results['mechanism_ok']}")
    print(f"Gate PASSED: {results['gate_passed']}")

    if not args.skip_figures:
        generate_all_figures(df, results, rho_fairness, FIGURES_DIR)

    sys.exit(0 if results["gate_passed"] else 1)


if __name__ == "__main__":
    main()
