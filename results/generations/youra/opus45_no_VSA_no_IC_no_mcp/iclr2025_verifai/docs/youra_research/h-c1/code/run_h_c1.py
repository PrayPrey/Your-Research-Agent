#!/usr/bin/env python3
import os
import sys
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CONFIG
from orchestrate import run_all_cells
from stats import compute_all_stats
from visualize_interaction import plot_interaction

def main():
    parser = argparse.ArgumentParser(description="h-c1: Format x Model Scale Interaction Experiment")
    parser.add_argument("--force", action="store_true", help="Force re-run, ignore cache")
    parser.add_argument("--skip-data", action="store_true", help="Skip data collection, use cached results")
    args = parser.parse_args()

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("=" * 60)
    print("h-c1: Format × Model Scale Interaction Experiment")
    print("=" * 60)

    if args.skip_data:
        import pandas as pd
        from dataclasses import asdict
        from orchestrate import get_cache_path, load_cell_cache

        print("\n[1/4] Loading cached cell results...")
        all_results = []
        for model_key in ["7B", "34B", "gpt4"]:
            for fmt in ["raw", "structured"]:
                cache_path = get_cache_path(model_key, fmt)
                if os.path.exists(cache_path):
                    cell_results = load_cell_cache(cache_path)
                    all_results.extend([asdict(r) for r in cell_results])
                    print(f"  Loaded {model_key}/{fmt}: {len(cell_results)} results")

        if not all_results:
            print("No cached results found. Run without --skip-data first.")
            sys.exit(1)

        df = pd.DataFrame(all_results)
        df["passed_int"] = df["passed"].astype(int)
    else:
        print("\n[1/4] Running 2×3 factorial experiment...")
        df = run_all_cells(force=args.force)

    df.to_json(CONFIG["results_path"], orient="records", indent=2)
    print(f"Results saved to {CONFIG['results_path']}")

    print("\n[2/4] Computing statistics...")
    stats_results = compute_all_stats(df)

    stats_path = "outputs/h-c1_stats.json"

    def convert_for_json(obj):
        if hasattr(obj, "tolist"):
            return obj.tolist()
        if hasattr(obj, "item"):
            return obj.item()
        return obj

    stats_serializable = json.loads(json.dumps(stats_results, default=convert_for_json))
    with open(stats_path, "w") as f:
        json.dump(stats_serializable, f, indent=2)
    print(f"Statistics saved to {stats_path}")

    print("\n[3/4] Generating interaction plot...")
    plot_path = os.path.join(CONFIG["figures_dir"], "h-c1_interaction_plot.png")
    plot_interaction(df, stats_results["simple_effects"], plot_path)

    print("\n[4/4] Results Summary")
    print("-" * 40)
    print(f"Interaction p-value: {stats_results['interaction_p']:.4f}")
    print(f"Interaction p-value (BH-adjusted): {stats_results['interaction_p_adj']:.4f}")
    print(f"Interaction η²: {stats_results['interaction_eta2']:.4f}")
    print(f"Interaction partial η²: {stats_results['interaction_partial_eta2']:.4f}")
    print()
    print("Simple Effects (Structured - Raw):")
    for model in ["7B", "34B", "gpt4"]:
        e = stats_results["simple_effects"][model]
        print(f"  {model}: Δ={e['effect']*100:.2f}% [95% CI: {e['ci_low']*100:.2f}, {e['ci_high']*100:.2f}], d={e['d']:.3f}")
    print()
    print(f"Linear trend contrast: L={stats_results['contrast']['contrast_estimate']:.4f}, "
          f"t={stats_results['contrast']['t']:.3f}, p(one-sided)={stats_results['contrast']['p_one_sided']:.4f}")
    print(f"Pattern confirmed (7B > 34B > GPT-4): {stats_results['contrast']['pattern_confirmed']}")
    print()

    pass_criteria = stats_results["pass_criteria"]
    verdict = "PASS" if pass_criteria else "FAIL"
    print("=" * 40)
    print(f"h-c1 VERDICT: {verdict}")
    print("=" * 40)

    validation_summary = {
        "hypothesis_id": "h-c1",
        "type": "CONDITION",
        "gate": "SHOULD_WORK",
        "timestamp": datetime.now().isoformat(),
        "verdict": verdict,
        "criteria": {
            "interaction_p_adj_lt_0.05": stats_results["interaction_p_adj"] < 0.05,
            "interaction_eta2_gt_0.01": stats_results["interaction_eta2"] > 0.01,
            "pattern_confirmed": stats_results["contrast"]["pattern_confirmed"]
        },
        "statistics": {
            "interaction_p": stats_results["interaction_p"],
            "interaction_p_adj": stats_results["interaction_p_adj"],
            "interaction_eta2": stats_results["interaction_eta2"],
            "interaction_partial_eta2": stats_results["interaction_partial_eta2"],
            "simple_effects": stats_results["simple_effects"],
            "contrast": stats_results["contrast"]
        }
    }

    with open("outputs/h-c1_validation_summary.json", "w") as f:
        json.dump(validation_summary, f, indent=2, default=convert_for_json)

    return verdict

if __name__ == "__main__":
    verdict = main()
    print(f"\nEXPERIMENT COMPLETE (verdict={verdict})")
