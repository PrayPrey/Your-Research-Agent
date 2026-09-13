import argparse
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from config import GRPOConfig, load_config

FIGURES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "figures"
)


def load_grad_norms(csv_path: str) -> pd.DataFrame:
    """Load CSV with columns: global_step, grad_norm, mean_reward, std_reward."""
    return pd.read_csv(csv_path)


def bootstrap_ci(
    binary_norms: np.ndarray,
    ratio_norms: np.ndarray,
    n_bootstrap: int = 1000,
    ci: float = 0.95,
) -> dict:
    """Bootstrap CI on mean(ratio_norms - binary_norms)."""
    diff = ratio_norms - binary_norms
    boot_means = np.empty(n_bootstrap)
    rng = np.random.default_rng(42)
    for i in range(n_bootstrap):
        sample = rng.choice(diff, size=len(diff), replace=True)
        boot_means[i] = sample.mean()
    alpha = (1 - ci) / 2
    ci_lower = float(np.percentile(boot_means, 100 * alpha))
    ci_upper = float(np.percentile(boot_means, 100 * (1 - alpha)))
    return {
        "mean_diff": float(diff.mean()),
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "excludes_zero": not (ci_lower <= 0 <= ci_upper),
    }


def plot_bar_humaneval(binary_score: float, ratio_score: float, out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(["Binary", "Ratio"], [binary_score * 100, ratio_score * 100],
                  color=["#4C72B0", "#DD8452"], width=0.5)
    ax.bar_label(bars, fmt="%.2f%%", padding=3)
    ax.set_ylabel("HumanEval pass@1 (%)")
    ax.set_title("HumanEval pass@1 at Step 200\nBinary vs Ratio Reward")
    ax.set_ylim(0, max(binary_score, ratio_score) * 100 * 1.15 + 1)
    ax.axhline(52.0, color="grey", linestyle="--", linewidth=1, label="Pre-RLEF baseline (~52%)")
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_grad_norm_trajectory(
    df_binary: pd.DataFrame, df_ratio: pd.DataFrame, ci_result: dict, out_path: str
) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df_binary["global_step"], df_binary["grad_norm"], label="Binary", color="#4C72B0", alpha=0.8)
    ax.plot(df_ratio["global_step"], df_ratio["grad_norm"], label="Ratio", color="#DD8452", alpha=0.8)

    # Mark CI region (steps 100-500)
    ax.axvspan(100, 500, alpha=0.08, color="green", label="CI analysis window [100,500]")

    diff_mean = ci_result["mean_diff"]
    ci_lo = ci_result["ci_lower"]
    ci_hi = ci_result["ci_upper"]
    excludes = ci_result["excludes_zero"]
    title_suffix = " ✓ CI excludes 0" if excludes else " ✗ CI includes 0"
    ax.set_title(f"Gradient Norm Trajectory (steps 1–500)\nMean diff={diff_mean:.4f} 95%CI=[{ci_lo:.4f},{ci_hi:.4f}]{title_suffix}")
    ax.set_xlabel("Training Step")
    ax.set_ylabel("Gradient Norm")
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_reward_histograms(
    df_binary: pd.DataFrame, df_ratio: pd.DataFrame, steps: list, out_path: str
) -> None:
    fig, axes = plt.subplots(1, len(steps), figsize=(4 * len(steps), 4))
    if len(steps) == 1:
        axes = [axes]
    for ax, step in zip(axes, steps):
        b = df_binary[df_binary["global_step"] <= step]["mean_reward"].dropna()
        r = df_ratio[df_ratio["global_step"] <= step]["mean_reward"].dropna()
        ax.hist(b.values, bins=20, alpha=0.6, label="Binary", color="#4C72B0")
        ax.hist(r.values, bins=20, alpha=0.6, label="Ratio", color="#DD8452")
        ax.set_title(f"Rewards up to step {step}")
        ax.set_xlabel("Mean group reward")
        ax.legend(fontsize=8)
    plt.suptitle("Reward Distribution by Training Stage")
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_mean_reward(df_binary: pd.DataFrame, df_ratio: pd.DataFrame, out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df_binary["global_step"], df_binary["mean_reward"], label="Binary", color="#4C72B0", alpha=0.8)
    ax.plot(df_ratio["global_step"], df_ratio["mean_reward"], label="Ratio", color="#DD8452", alpha=0.8)
    ax.set_xlabel("Training Step")
    ax.set_ylabel("Mean Group Reward")
    ax.set_title("Mean Group Reward over Training")
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=None)
    args = parser.parse_args()

    cfg = load_config(args.config)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    binary_csv = os.path.join(cfg.output_dir, "gradient_norms_binary.csv")
    ratio_csv = os.path.join(cfg.output_dir, "gradient_norms_ratio.csv")

    if not os.path.exists(binary_csv) or not os.path.exists(ratio_csv):
        print(f"ERROR: Missing gradient norm CSVs. Expected:\n  {binary_csv}\n  {ratio_csv}")
        sys.exit(1)

    df_binary = load_grad_norms(binary_csv)
    df_ratio = load_grad_norms(ratio_csv)
    print(f"Binary: {len(df_binary)} steps, Ratio: {len(df_ratio)} steps")

    # Bootstrap CI on steps 100-500
    b_window = df_binary[df_binary["global_step"].between(100, 500)]["grad_norm"].dropna().values
    r_window = df_ratio[df_ratio["global_step"].between(100, 500)]["grad_norm"].dropna().values
    min_len = min(len(b_window), len(r_window))
    ci_result = {"mean_diff": float("nan"), "ci_lower": float("nan"), "ci_upper": float("nan"), "excludes_zero": False}
    if min_len >= 10:
        ci_result = bootstrap_ci(b_window[:min_len], r_window[:min_len])
    else:
        print(f"WARNING: Not enough steps for bootstrap CI (need ≥10, got {min_len})")

    print(f"\nBootstrap CI (steps 100-500):")
    print(f"  Mean diff (ratio - binary): {ci_result['mean_diff']:.4f}")
    print(f"  95% CI: [{ci_result['ci_lower']:.4f}, {ci_result['ci_upper']:.4f}]")
    print(f"  Excludes zero: {ci_result['excludes_zero']}")

    # HumanEval scores
    binary_score = None
    ratio_score = None
    for cond in ["binary", "ratio"]:
        path = os.path.join(cfg.output_dir, f"humaneval_{cond}.json")
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            if cond == "binary":
                binary_score = data["pass_at_1"]
            else:
                ratio_score = data["pass_at_1"]

    humaneval_diff = None
    if binary_score is not None and ratio_score is not None:
        humaneval_diff = abs(ratio_score - binary_score)
        print(f"\nHumanEval pass@1:")
        print(f"  Binary: {binary_score:.4f} ({binary_score*100:.2f}%)")
        print(f"  Ratio:  {ratio_score:.4f} ({ratio_score*100:.2f}%)")
        print(f"  Diff:   {humaneval_diff:.4f} ({humaneval_diff*100:.2f}pp)")

    # Gate evaluation
    print("\n=== GATE EVALUATION (MUST_WORK) ===")
    primary_passed = ci_result["excludes_zero"]
    secondary_passed = (humaneval_diff is not None and humaneval_diff >= 0.01)
    gate_satisfied = primary_passed or secondary_passed

    print(f"PRIMARY (grad norm CI excludes 0): {'PASS' if primary_passed else 'FAIL'}")
    print(f"SECONDARY (HumanEval ≥1pp diff):   {'PASS' if secondary_passed else ('FAIL' if humaneval_diff is not None else 'N/A')}")
    print(f"GATE RESULT: {'SATISFIED' if gate_satisfied else 'NOT SATISFIED'}")

    # Save summary
    summary = {
        "gate_type": "MUST_WORK",
        "gate_satisfied": gate_satisfied,
        "primary_criterion": {
            "name": "gradient_norm_ci_excludes_zero",
            "passed": primary_passed,
            "mean_diff": ci_result["mean_diff"],
            "ci_lower": ci_result["ci_lower"],
            "ci_upper": ci_result["ci_upper"],
        },
        "secondary_criterion": {
            "name": "humaneval_directional_diff_1pp",
            "passed": secondary_passed,
            "binary_score": binary_score,
            "ratio_score": ratio_score,
            "diff": humaneval_diff,
        },
    }
    summary_path = os.path.join(cfg.output_dir, "gate_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nGate summary saved: {summary_path}")

    # Figures
    fig_dir = FIGURES_DIR
    plot_grad_norm_trajectory(df_binary, df_ratio, ci_result,
                               os.path.join(fig_dir, "grad_norm_trajectory.png"))
    plot_mean_reward(df_binary, df_ratio,
                     os.path.join(fig_dir, "mean_reward.png"))
    plot_reward_histograms(df_binary, df_ratio, [50, 100, 200, 500],
                           os.path.join(fig_dir, "reward_histograms.png"))
    if binary_score is not None and ratio_score is not None:
        plot_bar_humaneval(binary_score, ratio_score,
                           os.path.join(fig_dir, "humaneval_bar.png"))

    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()
