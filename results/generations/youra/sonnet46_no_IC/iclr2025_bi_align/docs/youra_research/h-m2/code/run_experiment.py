import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../..'))
os.chdir(project_root)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CSV_PATH = 'docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv'
FIGURES_DIR = 'docs/youra_research/h-m2/figures'
OUTPUT_PATH = 'docs/youra_research/h-m2/04_validation.md'
N_BOOTSTRAP = 1000
RANDOM_STATE = 42
ALPHA = 0.05
H_E1_R_PARTIAL = 0.9851

from data_loader import load_and_validate
from residualizer import compute_residuals
from spearman_analysis import (spearman_residuals, bootstrap_spearman,
                                fwl_consistency_check, pingouin_cross_validate)
from gate_evaluator import evaluate_gate
from visualizer import save_all_figures
from report_writer import write_validation_report


def main() -> None:
    print("=== H-M2: Residual Capability Signal Confirmation ===")

    # 1. Load data
    df = load_and_validate(CSV_PATH)
    print(f"N_clean = {len(df)}")

    # 2. OLS residualization
    resid = compute_residuals(df)

    # 3. Spearman correlation of residuals
    corr = spearman_residuals(resid['win_rate_resid'], resid['lc_resid'])
    rho, p_value = corr['rho'], corr['p_value']
    print(f"Spearman ρ={rho:.4f}, p={p_value:.4e}")

    # 4. Bootstrap CI
    ci_lower, ci_upper, boot_rhos = bootstrap_spearman(
        resid['win_rate_resid'], resid['lc_resid'], N_BOOTSTRAP, RANDOM_STATE)
    print(f"Bootstrap 95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")

    # 5. FWL consistency check
    fwl = fwl_consistency_check(rho, H_E1_R_PARTIAL)
    print(f"FWL delta={fwl['fwl_delta']:.4f}, consistent={fwl['fwl_consistent']}")

    # 6. Pingouin cross-validation
    pg = pingouin_cross_validate(df)
    print(f"Pingouin r={pg['pingouin_r']:.4f}, p={pg['pingouin_p']:.4e}")

    # 7. Gate evaluation
    gate = evaluate_gate(rho, p_value, ci_lower, fwl['fwl_delta'])
    print(f"Gate: {'PASS' if gate['passes_gate'] else 'FAIL'} — {gate['gate_reason']}")

    # 8. Visualizations
    figure_paths = save_all_figures(
        df, resid['win_rate_resid'], resid['lc_resid'], boot_rhos,
        rho, (ci_lower, ci_upper), fwl['fwl_delta'], FIGURES_DIR)
    print(f"Figures saved: {len(figure_paths)}")

    # 9. Write report
    write_validation_report(
        gate, rho, p_value, (ci_lower, ci_upper),
        fwl, pg, resid, figure_paths, OUTPUT_PATH)
    print(f"Report written: {OUTPUT_PATH}")

    sys.exit(0 if gate['passes_gate'] else 1)


if __name__ == '__main__':
    main()
