import argparse
import json
import os
import sys
import numpy as np

from config import load_config
from train import main as train_main
from analyze import run_analysis, check_gate
from visualize import generate_all_figures


def main(config_path: str, device: str = "cuda:0", skip_train: bool = False) -> dict:
    cfg = load_config(config_path)

    os.makedirs(cfg.results_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)

    # Step 1: ERM Training with gradient logging
    if not skip_train:
        print(f"\n{'='*60}")
        print("STEP 1: ERM Training with Gradient Logging")
        print(f"{'='*60}")
        seed_results = train_main(cfg.train, device)
    else:
        # Load cached results
        cached = os.path.join(cfg.results_dir, "summary.json")
        if os.path.exists(cached):
            with open(cached) as f:
                summary = json.load(f)
            print(f"Loaded cached results from {cached}")
            return summary
        else:
            print("ERROR: skip_train=True but no cached results found")
            sys.exit(1)

    # Step 2: Statistical Analysis
    print(f"\n{'='*60}")
    print("STEP 2: Statistical Analysis (GDR + Wilcoxon + Pearson)")
    print(f"{'='*60}")
    analysis = run_analysis(
        seed_results,
        cfg.gdr,
        delta_path=cfg.gdr.he1_delta_path,
    )

    # Step 3: Gate Evaluation
    print(f"\n{'='*60}")
    print("STEP 3: Gate Evaluation")
    print(f"{'='*60}")
    gate_pass = check_gate(analysis, cfg.gdr)
    gate_str = "PASS" if gate_pass else "FAIL"

    # Step 4: Figures
    print(f"\n{'='*60}")
    print("STEP 4: Generating Figures")
    print(f"{'='*60}")
    delta_series = None
    if cfg.gdr.he1_delta_path and os.path.exists(cfg.gdr.he1_delta_path):
        from analyze import load_he1_delta
        delta_series = load_he1_delta(cfg.gdr.he1_delta_path)
    generate_all_figures(seed_results, analysis, delta_series, cfg.figures_dir)
    print(f"Figures saved to {cfg.figures_dir}")

    # Step 5: Write summary.json
    seeds = sorted(seed_results.keys())
    mean_gdr_vals = [analysis["mean_early_gdr_per_seed"][s] for s in seeds]

    per_seed_out = {}
    for s in seeds:
        res = seed_results[s]
        per_seed_out[str(s)] = {
            "gdr_series": res["gdr_series"],
            "spurious_grad_norms": res["spurious_grad_norms"],
            "core_grad_norms": res["core_grad_norms"],
            "mean_early_gdr": analysis["mean_early_gdr_per_seed"][s],
            "wilcoxon_stat": analysis["wilcoxon_results"][s]["stat"],
            "wilcoxon_p": analysis["wilcoxon_results"][s]["p_value"],
        }

    summary = {
        "hypothesis": "H-M1",
        "gate": gate_str,
        "mean_early_gdr": analysis["mean_early_gdr"],
        "std_early_gdr": analysis["std_early_gdr"],
        "mean_early_gdr_per_seed": {str(k): v for k, v in analysis["mean_early_gdr_per_seed"].items()},
        "wilcoxon_results": {str(k): v for k, v in analysis["wilcoxon_results"].items()},
        "pearson_correlation": {str(k): v for k, v in analysis.get("pearson_correlation", {}).items()},
        "per_seed": per_seed_out,
        "figures": ["mean_early_gdr_bar.png", "gdr_timeline.png", "grad_norm_dual_axis.png", "early_late_violin.png"],
        "seeds_passed_gdr": sum(1 for v in mean_gdr_vals if v > 1.0),
        "seeds_passed_wilcoxon": sum(
            1 for r in analysis["wilcoxon_results"].values() if r["p_value"] < cfg.gdr.p_threshold
        ),
        "gate_criteria": {
            "min_seeds_pass": cfg.gdr.min_seeds_pass,
            "p_threshold": cfg.gdr.p_threshold,
            "gdr_threshold": 1.0,
        },
    }

    summary_path = os.path.join(cfg.results_dir, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults written to {summary_path}")

    # Gate assertion (hard fail logs clearly but doesn't crash pipeline)
    early_gdr_per_seed = mean_gdr_vals
    mean_val = float(np.mean(early_gdr_per_seed))

    print(f"\n{'='*60}")
    print(f"[H-M1] Gate: {gate_str} | mean_early_GDR={mean_val:.3f} | "
          f"Wilcoxon p={analysis['wilcoxon_results'][seeds[0]]['p_value']:.4f}")
    print(f"{'='*60}")
    print("EXPERIMENT COMPLETE")

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--skip-train", action="store_true")
    args = parser.parse_args()
    main(args.config, args.device, args.skip_train)
