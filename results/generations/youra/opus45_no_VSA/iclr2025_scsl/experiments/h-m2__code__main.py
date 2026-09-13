import os
import json
import torch

from config import CONFIG
from train import train_one_variant
from stats import aggregate_across_seeds, sr_significance_test
from visualize import (
    plot_sr_trajectory,
    plot_group_accuracy_trajectories,
    plot_update_norm_boxplot,
    plot_wga_comparison,
)


def check_success_criteria(agg: dict, sig_test: dict, cfg) -> dict:
    baseline_sr = agg.get("baseline", {}).get("sr_mean")
    parity_sr = agg.get("full_parity", {}).get("sr_mean")
    baseline_wga = agg.get("baseline", {}).get("wga_mean", 0)
    parity_wga = agg.get("full_parity", {}).get("wga_mean", 0)

    sr_pass = False
    if parity_sr is not None and baseline_sr is not None:
        sr_pass = parity_sr <= cfg.SR_THRESHOLD_PASS and baseline_sr > cfg.SR_THRESHOLD_BASELINE

    wga_pass = parity_wga >= baseline_wga
    p_pass = sig_test.get("significant", False)

    return {
        "sr_pass": sr_pass,
        "wga_pass": wga_pass,
        "p_pass": p_pass,
        "overall_pass": sr_pass and wga_pass and p_pass,
        "baseline_sr": baseline_sr,
        "parity_sr": parity_sr,
        "baseline_wga": baseline_wga,
        "parity_wga": parity_wga,
        "p_value": sig_test.get("p_value"),
    }


def run_ablation(cfg, device: torch.device) -> dict:
    all_results = {v: [] for v in cfg.variants}

    os.makedirs("results", exist_ok=True)

    for variant in cfg.variants:
        for seed in cfg.seeds:
            result = train_one_variant(variant, seed, cfg, device)
            with open(f"results/{variant}_seed{seed}.json", "w") as f:
                json.dump(result, f, indent=2, default=str)
            all_results[variant].append(result)

    return all_results


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    print("\n" + "="*60)
    print("H-M2: Update-Norm Parity Intervention Experiment")
    print("="*60)

    all_results = run_ablation(CONFIG, device)

    agg = {}
    for variant, results in all_results.items():
        agg[variant] = aggregate_across_seeds(results)
        print(f"\n{variant}: SR={agg[variant]['sr_mean']:.4f}±{agg[variant]['sr_std']:.4f}, "
              f"WGA={agg[variant]['wga_mean']:.4f}±{agg[variant]['wga_std']:.4f}")

    baseline_srs = [r["sr"] for r in all_results["baseline"] if r.get("sr") is not None]
    parity_srs = [r["sr"] for r in all_results["full_parity"] if r.get("sr") is not None]
    sig_test = sr_significance_test(baseline_srs, parity_srs)
    print(f"\nSignificance test: t={sig_test['t_stat']:.4f}, p={sig_test['p_value']:.4f}, sig={sig_test['significant']}")

    criteria = check_success_criteria(agg, sig_test, CONFIG)
    print("\n" + "="*60)
    print("SUCCESS CRITERIA CHECK")
    print("="*60)
    print(f"  SR Pass (parity≤1.1, baseline>1.2): {criteria['sr_pass']}")
    print(f"  WGA Pass (parity≥baseline): {criteria['wga_pass']}")
    print(f"  P-value Pass (p<0.05): {criteria['p_pass']}")
    print(f"  OVERALL: {'PASS' if criteria['overall_pass'] else 'FAIL'}")

    os.makedirs(CONFIG.figure_dir, exist_ok=True)
    plot_sr_trajectory(all_results, os.path.join(CONFIG.figure_dir, "sr_comparison.png"))
    plot_group_accuracy_trajectories(all_results, os.path.join(CONFIG.figure_dir, "group_accuracy.png"))
    plot_update_norm_boxplot(all_results, os.path.join(CONFIG.figure_dir, "update_norms.png"))
    plot_wga_comparison(all_results, os.path.join(CONFIG.figure_dir, "wga_comparison.png"))
    print(f"\nFigures saved to {CONFIG.figure_dir}")

    summary = {
        "aggregated": agg,
        "significance_test": sig_test,
        "success_criteria": criteria,
        "config": {
            "epochs": CONFIG.epochs,
            "batch_size": CONFIG.batch_size,
            "lr": CONFIG.lr,
            "seeds": CONFIG.seeds,
            "sr_eval_epoch": CONFIG.sr_eval_epoch,
        }
    }
    with open(CONFIG.results_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"Summary saved to {CONFIG.results_path}")

    print("\nEXPERIMENT COMPLETE")
    return criteria


if __name__ == "__main__":
    main()
