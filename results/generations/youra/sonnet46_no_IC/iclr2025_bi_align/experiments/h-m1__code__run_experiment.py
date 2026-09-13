import sys
import os

# Change to project root so relative paths work
project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../..'))
os.chdir(project_root)

# Module-level constants
CSV_PATH = "docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv"
FIGURES_DIR = "docs/youra_research/h-m1/figures/"
OUTPUT_PATH = "docs/youra_research/h-m1/04_validation.md"
RANDOM_STATE = 42
ALPHA = 0.05
VIF_THRESHOLD = 5.0
N_REPEATS = 30
N_MIN = 200

from data_loader import load_and_validate, standardize
from ols_analysis import (
    compute_vif, fit_baseline_ols, fit_full_ols,
    run_ols_diagnostics, run_permutation_fallback
)
from gate_evaluator import evaluate_gate
from visualizer import save_all_figures
from report_writer import write_validation_report


def main() -> None:
    print("=== h-m1: Standardized OLS Dominance Analysis ===")

    df = load_and_validate(CSV_PATH)
    print(f"Loaded N={len(df)} models")

    df = standardize(df)
    print(f"Standardized: win_rate_std mean={df['win_rate_std'].mean():.2e}, std={df['win_rate_std'].std():.4f}")

    vif = compute_vif(df)
    print(f"VIF: win_rate_std={vif['win_rate']:.3f}, avg_length_std={vif['avg_length']:.3f}, any_high={vif['any_high_vif']}")

    baseline = fit_baseline_ols(df)
    print(f"Baseline OLS (verbosity-only): beta_avg_length={baseline['beta_avg_length']:.4f}, R2={baseline['r2']:.4f}")

    ols = fit_full_ols(df)
    print(f"Full OLS: beta_win={ols['beta_win']:.4f}, beta_len={ols['beta_len']:.4f}, R2={ols['r2']:.4f}")

    diagnostics = run_ols_diagnostics(ols, df)
    print(f"Breusch-Pagan: stat={diagnostics['bp_stat']:.4f}, p={diagnostics['bp_pvalue']:.4f}, heteroscedastic={diagnostics['heteroscedastic']}")

    perm = None
    if vif['any_high_vif']:
        perm = run_permutation_fallback(df)
        print(f"Permutation fallback: imp_win={perm['imp_win']:.4f}, imp_len={perm['imp_len']:.4f}")

    gate = evaluate_gate(ols, vif, perm)
    print(f"Gate: {'PASS' if gate['passes_gate'] else 'FAIL'} via {gate['path']}")
    print(f"  |beta_win|={abs(ols['beta_win']):.4f}, |beta_len|={abs(ols['beta_len']):.4f}, p_win={ols['p_win']:.4e}")

    fig_paths = save_all_figures(df, ols, vif, gate, FIGURES_DIR)
    print(f"Figures saved: {len(fig_paths)} files")

    write_validation_report(gate, ols, baseline, vif, diagnostics, fig_paths, OUTPUT_PATH)
    print(f"Report written: {OUTPUT_PATH}")

    sys.exit(0 if gate['passes_gate'] else 1)


if __name__ == '__main__':
    # Integration smoke test
    print("Running integration self-check...")
    df_test = load_and_validate(CSV_PATH)
    df_test = standardize(df_test)
    assert 'win_rate_std' in df_test.columns
    assert 'avg_length_std' in df_test.columns
    vif_test = compute_vif(df_test)
    assert vif_test['win_rate'] < 10, f"VIF too high: {vif_test['win_rate']}"
    assert vif_test['avg_length'] < 10, f"VIF too high: {vif_test['avg_length']}"
    print(f"Self-check OK: N={len(df_test)}, VIF_win={vif_test['win_rate']:.3f}")
    main()
