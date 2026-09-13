from pathlib import Path
import sys

_CODE_DIR = Path(__file__).parent
_H_M3_DIR = _CODE_DIR.parent
_H_E1_DIR = _H_M3_DIR.parent / "h-e1"

CSV_PATH = _CODE_DIR / "data" / "pwc_cov_computed.csv"
H_E1_JSON = _H_E1_DIR / "experiment_results.json"
RESULTS_PATH = _H_M3_DIR / "experiment_results.json"
FIGURES_DIR = _H_M3_DIR / "figures"

from data_loader import load_residual_cov, load_paper_count_star_idx
from distributional_moments import compute_both_segments
from directional_tests import run_directional_tests
from verifier import verify_directional_specificity
from visualization import save_all_figures
from results_output import build_results_dict, save_results


def main() -> int:
    print("=== H-M3: Post-Breakpoint CoV Directional Skewness Analysis ===")

    print(f"\n[1] Loading data from {CSV_PATH}")
    paper_counts, residual_cov = load_residual_cov(CSV_PATH)
    print(f"    Loaded N={len(residual_cov)} observations")

    print(f"\n[2] Loading breakpoint index from {H_E1_JSON}")
    breakpoint_idx = load_paper_count_star_idx(H_E1_JSON, paper_counts, residual_cov)
    print(f"    breakpoint_idx={breakpoint_idx}, paper_count*={paper_counts[breakpoint_idx]}")

    print("\n[3] Computing distributional moments")
    pre_moments, post_moments, pre_arr, post_arr = compute_both_segments(
        paper_counts, residual_cov, breakpoint_idx
    )

    print("\n[4] Running directional tests")
    test_results = run_directional_tests(pre_arr, post_arr, pre_moments, post_moments)

    print("\n[5] Verifying gate")
    gate = verify_directional_specificity(test_results)

    print("\n[6] Saving figures")
    figure_paths = save_all_figures(
        pre_arr, post_arr, pre_moments, post_moments, test_results, gate, FIGURES_DIR
    )

    print("\n[7] Saving results")
    results_dict = build_results_dict(pre_moments, post_moments, test_results, gate, figure_paths)
    save_results(results_dict, RESULTS_PATH)

    print(f"\n=== COMPLETE: gate={gate.gate_type}, metrics_passed={gate.metrics_passed}/4 ===")
    return 0 if gate.gate_passed else 1


if __name__ == "__main__":
    sys.exit(main())
