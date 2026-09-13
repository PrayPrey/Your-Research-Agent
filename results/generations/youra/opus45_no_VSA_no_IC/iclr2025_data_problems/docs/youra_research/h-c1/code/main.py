"""Main orchestrator for h-c1: Mode Profile Reliability Analysis."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from data_loader import load_attribution_scores, validate_scores, build_mode_profile_df
from reliability import analyze_all_methods
from visualization import plot_alpha_bar_chart, plot_reliability_heatmap, plot_alpha_if_dropped


def main() -> bool:
    print("=" * 60)
    print("h-c1: Mode Profile Reliability Analysis")
    print("=" * 60)

    cfg = Config()

    print(f"\n[1/4] Loading attribution scores from {cfg.npz_path}...")
    try:
        scores = load_attribution_scores(cfg.npz_path)
        validate_scores(scores, cfg.methods, cfg.modes, cfg.min_samples)
        n_probes = len(scores[f"{cfg.methods[0]}_{cfg.modes[0]}"])
        print(f"  Loaded {len(scores)} score arrays, {n_probes} probes each")
    except FileNotFoundError as e:
        print(f"  ERROR: {e}")
        print("  GATE RESULT: BLOCKED (prerequisite h-m1 not complete)")
        return False

    print("\n[2/4] Building mode profile matrices...")
    profiles = {}
    for method in cfg.methods:
        df = build_mode_profile_df(scores, method, cfg.modes)
        profiles[method] = df
        print(f"  {method}: shape {df.shape}")

    print(f"\n[3/4] Computing Cronbach's alpha (threshold={cfg.alpha_threshold})...")
    results = analyze_all_methods(profiles, cfg.alpha_threshold)

    for method in cfg.methods:
        r = results[method]
        status = "PASS" if r["pass"] else "FAIL"
        print(f"  {method.upper()}: α={r['alpha']:.4f} [{r['ci_lower']:.4f}, {r['ci_upper']:.4f}] -> {status}")

    print("\n[4/4] Generating figures...")
    plot_alpha_bar_chart(results, cfg.alpha_threshold, os.path.join(cfg.fig_dir, "alpha_bar_chart.png"))
    plot_reliability_heatmap(results, cfg.modes, os.path.join(cfg.fig_dir, "reliability_heatmap.png"))
    plot_alpha_if_dropped(results, cfg.modes, os.path.join(cfg.fig_dir, "alpha_if_dropped.png"))
    print(f"  Saved to {cfg.fig_dir}/")

    gate_results = {
        "hypothesis_id": "h-c1",
        "gate_type": "SHOULD_WORK",
        "success": results["gate_pass"],
        "criteria": {
            "code_runs": True,
            "all_alphas_computed": all(results[m]["alpha"] is not None for m in cfg.methods),
            "all_alphas_above_threshold": results["gate_pass"]
        },
        "details": {
            method: {
                "alpha": results[method]["alpha"],
                "ci_lower": results[method]["ci_lower"],
                "ci_upper": results[method]["ci_upper"],
                "n_probes": results[method]["n_probes"],
                "item_total_correlations": results[method]["item_total_correlations"],
                "pass": results[method]["pass"]
            }
            for method in cfg.methods
        },
        "threshold": cfg.alpha_threshold
    }

    with open(cfg.results_path, "w") as f:
        json.dump(gate_results, f, indent=2)
    print(f"\nResults saved to {cfg.results_path}")

    print("\n" + "=" * 60)
    print(f"GATE RESULT: {'PASS' if results['gate_pass'] else 'FAIL'}")
    print("=" * 60)

    return results["gate_pass"]


if __name__ == "__main__":
    success = main()
    print("EXPERIMENT COMPLETE")
    sys.exit(0 if success else 1)
