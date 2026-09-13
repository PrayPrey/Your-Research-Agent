"""H-M1 experiment entry point: partial Spearman BBQ fairness analysis."""
import argparse
import sys
from pathlib import Path

# Ensure code dir is on path
sys.path.insert(0, str(Path(__file__).parent))


def main() -> None:
    parser = argparse.ArgumentParser(description="H-M1: Partial Spearman BBQ analysis")
    parser.add_argument("--skip-figures", action="store_true", help="Skip figure generation")
    parser.add_argument("--dry-run", action="store_true", help="Self-check only (synthetic data)")
    args = parser.parse_args()

    if args.dry_run:
        _self_check()
        return

    from data import build_score_dataframe, verify_n_common
    from analysis import run_full_analysis
    from visualize import generate_all_figures
    from config import FIGURES_DIR

    df = build_score_dataframe()
    verify_n_common(df)
    results = run_full_analysis(df)

    if not args.skip_figures:
        generate_all_figures(df, results, FIGURES_DIR)

    status = "PASS" if results["gate_pass"] else "FAIL"
    print(f"Gate: {status} | partial_rho={results['partial_rho']:.3f} | p={results['p_value']:.4f} | n={results['n']}")
    print("EXPERIMENT COMPLETE")


def _self_check() -> None:
    """Synthetic 5-row DataFrame self-check."""
    import pandas as pd
    sys.path.insert(0, str(Path(__file__).parent))
    from analysis import compute_raw_spearman, compute_partial_spearman, evaluate_gate

    df = pd.DataFrame({
        "model_name":   ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
        "bbq_disambig": [0.9, 0.8, 0.7, 0.6, 0.5, 0.85, 0.75, 0.65, 0.55, 0.45],
        "bbq_ambig":    [0.85, 0.75, 0.65, 0.55, 0.45, 0.80, 0.70, 0.60, 0.50, 0.40],
        "mmlu":         [0.80, 0.70, 0.60, 0.50, 0.40, 0.75, 0.65, 0.55, 0.45, 0.35],
        "winogrande":   [0.82, 0.72, 0.62, 0.52, 0.42, 0.77, 0.67, 0.57, 0.47, 0.37],
    })

    raw = compute_raw_spearman(df)
    assert "raw_rho" in raw and "raw_p" in raw
    assert raw["n"] == 10

    partial = compute_partial_spearman(df, covar="mmlu")
    assert "partial_rho" in partial and "p_value" in partial

    gate = evaluate_gate(partial["partial_rho"], partial["p_value"])
    assert isinstance(gate, bool)

    print("Self-check PASSED")
    print("EXPERIMENT COMPLETE")


if __name__ == "__main__":
    main()
