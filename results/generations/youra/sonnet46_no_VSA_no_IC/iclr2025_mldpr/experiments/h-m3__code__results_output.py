import json
from pathlib import Path

from distributional_moments import SegmentMoments
from directional_tests import DirectionalTestResults
from verifier import GateResult


def build_results_dict(
    pre_moments: SegmentMoments,
    post_moments: SegmentMoments,
    test_results: DirectionalTestResults,
    gate: GateResult,
    figure_paths: list,
) -> dict:
    return {
        "n_pre": pre_moments.n,
        "n_post": post_moments.n,
        "skew_pre": pre_moments.skewness,
        "skew_post": post_moments.skewness,
        "kurt_pre": pre_moments.kurtosis,
        "kurt_post": post_moments.kurtosis,
        "p10_pre": pre_moments.p10,
        "p10_post": post_moments.p10,
        "perm_p_skew_diff": test_results.perm_p_skew_diff,
        "mw_pvalue": test_results.mw_pvalue,
        "mw_statistic": test_results.mw_statistic,
        "metric1_pass": test_results.metric1_pass,
        "metric2_pass": test_results.metric2_pass,
        "metric3_pass": test_results.metric3_pass,
        "metric4_pass": test_results.metric4_pass,
        "metrics_passed": gate.metrics_passed,
        "gate_passed": gate.gate_passed,
        "gate_type": gate.gate_type,
        "verdict_message": gate.verdict_message,
        "figure_paths": [str(p) for p in figure_paths],
    }


def save_results(results_dict: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results_dict, f, indent=2)
    print(f"Results saved to {output_path}")
    print(f"Gate verdict: {results_dict['verdict_message']}")
