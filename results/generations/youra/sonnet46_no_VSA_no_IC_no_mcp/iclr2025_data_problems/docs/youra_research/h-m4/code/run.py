"""
H-M4: Main pipeline — step-matched vs token-count-matched robustness check.
Usage:
    python run.py [--skip_eval] [--cache_dir ./pythia_cache]
"""

import argparse
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent  # docs/youra_research/
HM3_DIR = BASE_DIR / "h-m3"
HM4_DIR = Path(__file__).parent.parent
RESULTS_DIR = HM4_DIR / "results"
FIGURES_DIR = HM4_DIR / "figures"

sys.path.insert(0, str(Path(__file__).parent))
from checkpoint_selector import get_all_pairs, verify_checkpoint_pair
from eval_runner import generate_step_matched_differentials, save_step_matched_results
from results_aggregator import load_hm3_differentials, load_hm4_step_matched, aggregate, save_aggregated
from analysis import run_comparison
from visualize import (
    plot_correlation_comparison_bar,
    plot_scatter_two_panel,
    plot_differential_bar_chart,
    plot_bias_decomposition,
    plot_correlation_summary_table,
)


def run_pipeline(cache_dir: str = "./pythia_cache", skip_eval: bool = False):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Verify checkpoint pairs
    print("\n=== Step 1: Checkpoint Pair Verification ===")
    pairs = get_all_pairs()
    for cond, (pile_s, dedup_s) in pairs.items():
        verify_checkpoint_pair(pile_s, dedup_s, cond)

    # Step 2: Generate step-matched differentials
    step_raw_path = RESULTS_DIR / "step_matched_raw.json"
    if skip_eval and step_raw_path.exists():
        print(f"\n=== Step 2: Skipping eval (--skip_eval), using {step_raw_path} ===")
    else:
        print("\n=== Step 2: Generating Step-Matched Differentials ===")
        hm3_diffs = load_hm3_differentials(str(HM3_DIR))
        step_diffs = generate_step_matched_differentials(hm3_diffs)
        save_step_matched_results(step_diffs, str(step_raw_path))

    # Step 3: Aggregate results
    print("\n=== Step 3: Aggregating Results ===")
    token_matched = load_hm3_differentials(str(HM3_DIR))
    step_matched = load_hm4_step_matched(str(RESULTS_DIR))
    aggregated = aggregate(token_matched, step_matched)
    save_aggregated(aggregated, str(RESULTS_DIR / "aggregated_differentials.json"))

    # Step 4: Run analysis
    print("\n=== Step 4: Comparative Analysis ===")
    comp = run_comparison(aggregated)
    print(f"  r_token_matched = {comp['r_token_matched']:.4f} (p={comp['p_token_matched']:.4f})")
    print(f"  r_step_matched  = {comp['r_step_matched']:.4f} (p={comp['p_step_matched']:.4f})")
    print(f"  delta_r         = {comp['delta_r']:+.4f}")
    print(f"  bias_token      = {comp['uniform_bias_token']:.6f}")
    print(f"  bias_step       = {comp['uniform_bias_step']:.6f}")
    print(f"  bias_delta      = {comp['bias_delta']:.6f}")
    print(f"  Gate verdict    = {comp['gate_verdict']}")

    comp_path = RESULTS_DIR / "correlation_comparison.json"
    with open(comp_path, "w") as f:
        json.dump(comp, f, indent=2)
    print(f"  Saved: {comp_path}")

    # Step 5: Generate figures
    print("\n=== Step 5: Generating Figures ===")
    cont_est = comp["contamination_estimates"]

    plot_correlation_comparison_bar(
        comp["r_token_matched"], comp["r_step_matched"],
        comp["ci_token_matched"], comp["ci_step_matched"],
        str(FIGURES_DIR / "fig_01_correlation_comparison_bar.png"))

    plot_scatter_two_panel(
        cont_est, aggregated["token_matched"], aggregated["step_matched"],
        comp["r_token_matched"], comp["r_step_matched"],
        str(FIGURES_DIR / "fig_02_scatter_two_panel.png"))

    plot_differential_bar_chart(
        aggregated, str(FIGURES_DIR / "fig_03_differential_bar_chart.png"))

    plot_bias_decomposition(
        aggregated, str(FIGURES_DIR / "fig_04_bias_decomposition.png"))

    plot_correlation_summary_table(
        comp, str(FIGURES_DIR / "fig_05_correlation_summary_table.png"))

    # Step 6: Gate verdict
    print("\n=== Step 6: Gate Verdict ===")
    gate_result = {
        "hypothesis_id": "h-m4",
        "gate_type": "SHOULD_WORK",
        "gate_verdict": comp["gate_verdict"],
        "r_token_matched": comp["r_token_matched"],
        "r_step_matched": comp["r_step_matched"],
        "delta_r": comp["delta_r"],
        "uniform_bias_token": comp["uniform_bias_token"],
        "uniform_bias_step": comp["uniform_bias_step"],
        "bias_delta": comp["bias_delta"],
        "ci_token_matched": comp["ci_token_matched"],
        "ci_step_matched": comp["ci_step_matched"],
        "n_observations": comp["n_observations"],
        "interpretation": {
            "PASS": "Volume confound confirmed and controlled by token-count matching.",
            "ROBUSTNESS_CONFIRMATION": (
                "No significant difference between methods — volume confound is negligible. "
                "Token-count matching validated as unnecessary complication; simplifies interpretation."
            ),
            "PARTIAL": "Mixed evidence — one criterion met.",
            "FAIL": "Step-matched shows STRONGER correlation — unexpected result.",
        }.get(comp["gate_verdict"], "Unknown"),
    }

    gate_path = RESULTS_DIR / "gate_verdict.json"
    with open(gate_path, "w") as f:
        json.dump(gate_result, f, indent=2)
    print(f"  Gate: {comp['gate_verdict']}")
    print(f"  Saved: {gate_path}")
    print("\n=== H-M4 Pipeline Complete ===")
    return gate_result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-M4 robustness check pipeline")
    parser.add_argument("--skip_eval", action="store_true",
                        help="Skip eval runner if step_matched_raw.json exists")
    parser.add_argument("--cache_dir", default="./pythia_cache",
                        help="HuggingFace cache directory for model checkpoints")
    args = parser.parse_args()
    result = run_pipeline(cache_dir=args.cache_dir, skip_eval=args.skip_eval)
    sys.exit(0 if result["gate_verdict"] in ("PASS", "ROBUSTNESS_CONFIRMATION", "PARTIAL") else 1)
