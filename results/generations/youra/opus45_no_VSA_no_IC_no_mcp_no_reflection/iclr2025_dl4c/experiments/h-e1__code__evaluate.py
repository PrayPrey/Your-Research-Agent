"""Evaluation pipeline: pass@1, samples-to-threshold, statistical comparison, visualization."""
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from datasets import load_dataset

from config import EvalConfig, REWARD_CONDITIONS, SEEDS


def load_humaneval_test():
    return load_dataset("openai_humaneval", split="test")


def load_mbpp_test():
    return load_dataset("google-research-datasets/mbpp", "sanitized", split="test")


def samples_to_threshold(metric_log: list, threshold: float = 0.3) -> int | None:
    for n_samples, p1 in metric_log:
        if p1 >= threshold:
            return n_samples
    return None


def compare_conditions(results: dict, cfg: EvalConfig) -> dict:
    summary = {}

    for condition in REWARD_CONDITIONS:
        seeds_data = results.get(condition, {})
        final_p1s = [seeds_data[s]["final_pass_at_1"] for s in SEEDS if s in seeds_data]
        thresholds = []

        for s in SEEDS:
            if s in seeds_data:
                t = samples_to_threshold(seeds_data[s].get("metric_log", []), cfg.pass_at_1_threshold)
                if t is not None:
                    thresholds.append(t)

        summary[condition] = {
            "final_pass_at_1_mean": np.mean(final_p1s) if final_p1s else 0.0,
            "final_pass_at_1_std": np.std(final_p1s) if final_p1s else 0.0,
            "samples_to_threshold_mean": np.mean(thresholds) if thresholds else None,
            "samples_to_threshold_std": np.std(thresholds) if thresholds else None,
            "n_reached_threshold": len(thresholds),
            "n_seeds": len(final_p1s)
        }

    binary_p1s = [results["binary"][s]["final_pass_at_1"] for s in SEEDS if s in results.get("binary", {})]
    hb_p1s = [results["high_bandwidth"][s]["final_pass_at_1"] for s in SEEDS if s in results.get("high_bandwidth", {})]

    if len(binary_p1s) >= 2 and len(hb_p1s) >= 2:
        t_stat, p_value = stats.ttest_ind(hb_p1s, binary_p1s)
        cohens_d = (np.mean(hb_p1s) - np.mean(binary_p1s)) / np.sqrt((np.var(hb_p1s) + np.var(binary_p1s)) / 2)
    else:
        t_stat, p_value, cohens_d = None, None, None

    binary_stt = summary["binary"]["samples_to_threshold_mean"]
    hb_stt = summary["high_bandwidth"]["samples_to_threshold_mean"]

    gate_passed = False
    gate_reason = ""

    if binary_stt is not None and hb_stt is not None:
        gate_passed = hb_stt < binary_stt
        gate_reason = f"samples_to_threshold: high_bandwidth={hb_stt:.0f} vs binary={binary_stt:.0f}"
    elif summary["high_bandwidth"]["final_pass_at_1_mean"] > summary["binary"]["final_pass_at_1_mean"]:
        gate_passed = True
        gate_reason = f"pass@1 comparison: high_bandwidth > binary"
    else:
        gate_reason = "Neither threshold reached, high_bandwidth did not outperform binary"

    return {
        "summary": summary,
        "statistical_test": {
            "test": "independent t-test",
            "t_statistic": t_stat,
            "p_value": p_value,
            "cohens_d": cohens_d,
            "significant": p_value < cfg.significance_alpha if p_value else False
        },
        "gate": {
            "passed": gate_passed,
            "reason": gate_reason
        }
    }


def make_figures(results: dict, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    colors = {"binary": "#E74C3C", "categorical": "#F39C12", "high_bandwidth": "#27AE60"}

    fig, ax = plt.subplots(figsize=(10, 6))
    for condition in REWARD_CONDITIONS:
        if condition not in results:
            continue
        all_logs = []
        for s in SEEDS:
            if s in results[condition]:
                all_logs.append(results[condition][s].get("metric_log", []))

        if not all_logs:
            continue

        max_len = max(len(log) for log in all_logs)
        x_vals = [log[i][0] if i < len(log) else None for log in all_logs for i in range(max_len)]

        sample_points = sorted(set(log[i][0] for log in all_logs for i in range(len(log))))

        means, stds = [], []
        for sp in sample_points:
            vals = []
            for log in all_logs:
                for n, p in log:
                    if n == sp:
                        vals.append(p)
                        break
            if vals:
                means.append(np.mean(vals))
                stds.append(np.std(vals))

        if means:
            ax.plot(sample_points[:len(means)], means, label=condition, color=colors[condition], linewidth=2)
            ax.fill_between(
                sample_points[:len(means)],
                np.array(means) - np.array(stds),
                np.array(means) + np.array(stds),
                alpha=0.2,
                color=colors[condition]
            )

    ax.axhline(y=0.3, color='gray', linestyle='--', label='threshold (0.3)')
    ax.set_xlabel('Training Samples')
    ax.set_ylabel('pass@1')
    ax.set_title('Learning Curves: pass@1 vs Training Samples')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.savefig(os.path.join(out_dir, 'learning_curves.png'), dpi=150, bbox_inches='tight')
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 5))
    conditions = REWARD_CONDITIONS
    means = [results.get(c, {}).get(0, {}).get("final_pass_at_1", 0) for c in conditions]
    ax.bar(conditions, means, color=[colors[c] for c in conditions])
    ax.set_ylabel('Final pass@1')
    ax.set_title('Final pass@1 by Reward Condition')
    ax.axhline(y=0.3, color='gray', linestyle='--')
    plt.savefig(os.path.join(out_dir, 'final_pass_at_1.png'), dpi=150, bbox_inches='tight')
    plt.close()

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for idx, condition in enumerate(REWARD_CONDITIONS):
        if condition in results:
            all_rewards = []
            for s in SEEDS:
                if s in results[condition]:
                    all_rewards.extend(results[condition][s].get("rewards", []))
            if all_rewards:
                axes[idx].hist(all_rewards, bins=20, color=colors[condition], alpha=0.7)
                axes[idx].set_title(f'{condition} rewards')
                axes[idx].set_xlabel('Reward')
                axes[idx].set_ylabel('Count')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'reward_distributions.png'), dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Figures saved to {out_dir}/")


def main():
    cfg = EvalConfig()

    results_path = "outputs/results.json"
    if not os.path.exists(results_path):
        print(f"Results file not found: {results_path}")
        return

    with open(results_path) as f:
        results = json.load(f)

    for cond in results:
        results[cond] = {int(k): v for k, v in results[cond].items()}

    comparison = compare_conditions(results, cfg)

    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)

    for condition, stats in comparison["summary"].items():
        print(f"\n{condition}:")
        print(f" pass@1: {stats['final_pass_at_1_mean']:.4f} ± {stats['final_pass_at_1_std']:.4f}")
        if stats['samples_to_threshold_mean']:
            print(f" samples_to_threshold: {stats['samples_to_threshold_mean']:.0f} ± {stats['samples_to_threshold_std']:.0f}")
        else:
            print(f" samples_to_threshold: not reached")

    print(f"\nStatistical Test:")
    st = comparison["statistical_test"]
    if st["p_value"]:
        print(f" p-value: {st['p_value']:.4f}")
        print(f" Cohen's d: {st['cohens_d']:.4f}")
        print(f" Significant: {st['significant']}")

    print(f"\nGate:")
    print(f" Passed: {comparison['gate']['passed']}")
    print(f" Reason: {comparison['gate']['reason']}")

    make_figures(results, "outputs/figures")

    with open("outputs/evaluation.json", "w") as f:
        json.dump(comparison, f, indent=2, default=str)

    return comparison


if __name__ == "__main__":
    main()
