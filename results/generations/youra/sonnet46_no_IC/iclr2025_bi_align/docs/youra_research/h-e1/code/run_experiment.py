import sys
import os

# Change to project root so relative paths work
project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../..'))
os.chdir(project_root)

CSV_PATH    = 'docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv'
FIGURES_DIR = 'docs/youra_research/h-e1/figures'
OUTPUT_PATH = 'docs/youra_research/h-e1/04_validation.md'

N_BOOTSTRAP  = 1000
RANDOM_STATE = 42
ALPHA        = 0.05
R_THRESHOLD  = 0.15
VIF_WARN     = 5.0
N_MIN        = 200

from data_loader import load_and_validate
from statistical_analysis import compute_vif, spearman_partial_corr, bootstrap_partial_corr
from gate_evaluator import evaluate_gate
from visualizer import save_all_figures
from report_writer import write_validation_report


def main():
    print(f"Loading data from {CSV_PATH}...")
    df = load_and_validate(CSV_PATH)
    print(f"N_clean = {len(df)}")

    print("Computing VIF...")
    vif = compute_vif(df)
    print(f"VIF: win_rate={vif['win_rate']:.3f}, avg_length={vif['avg_length']:.3f}, any_high={vif['any_high_vif']}")

    print("Computing Spearman partial correlation...")
    corr_result = spearman_partial_corr(df)
    print(f"r_partial={corr_result['r_partial']:.4f}, p_val={corr_result['p_val']:.6f}, n={corr_result['n']}")

    print(f"Running bootstrap ({N_BOOTSTRAP} resamples)...")
    ci_lower, ci_upper, boot_rs = bootstrap_partial_corr(df, N_BOOTSTRAP, RANDOM_STATE)
    print(f"Bootstrap CI: [{ci_lower:.4f}, {ci_upper:.4f}]")

    gate_result = evaluate_gate(corr_result['r_partial'], corr_result['p_val'], ci_lower)
    print(f"Gate: {'PASS' if gate_result['passes_gate'] else 'FAIL'}")

    print("Generating figures...")
    figure_paths = save_all_figures(df, boot_rs, vif, corr_result, FIGURES_DIR)
    print(f"Figures saved: {len(figure_paths)}")

    print(f"Writing report to {OUTPUT_PATH}...")
    write_validation_report(gate_result, corr_result, (ci_lower, ci_upper), vif, figure_paths, OUTPUT_PATH)

    print(f"\nGate: {'PASS' if gate_result['passes_gate'] else 'FAIL'}")
    sys.exit(0 if gate_result['passes_gate'] else 1)


if __name__ == '__main__':
    main()
