"""Compute trade-off metrics and generate plots."""
import yaml
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict


def load_config(config_path: str = "config/experiment_config.yaml") -> dict:
    """Load experiment config."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def compute_tradeoff_metrics(
    scores_df: pd.DataFrame,
    timings: Dict[str, float],
    config: dict
) -> Dict[str, float]:
    """
    Compute stage-mismatch penalty, quality bound, cost ratio.
    Returns: {metric_name: value, pass_X: bool}
    """
    # Extract baseline
    baseline_mmlu = scores_df[scores_df["condition"] == "baseline"]["mmlu"].values[0]

    # Extract k=5000 scores (for stage-mismatch penalty)
    early_k5000_mmlu = scores_df[scores_df["condition"] == "early_k5000"]["mmlu"].values[0]
    late_k5000_mmlu = scores_df[scores_df["condition"] == "late_k5000"]["mmlu"].values[0]

    # Extract k=10000 scores (for quality bound)
    late_k10000_mmlu = scores_df[scores_df["condition"] == "late_k10000"]["mmlu"].values[0]

    # Compute metrics
    stage_mismatch_penalty = (late_k5000_mmlu - early_k5000_mmlu) / late_k5000_mmlu
    quality_bound = abs(late_k10000_mmlu - baseline_mmlu) / baseline_mmlu
    cost_ratio = timings["late"] / timings["early"]

    # Gate checks
    pass_penalty = stage_mismatch_penalty >= config["success_criteria"]["stage_mismatch_penalty_threshold"]
    pass_speed = cost_ratio >= config["success_criteria"]["speed_advantage_threshold"]
    pass_quality = quality_bound <= config["success_criteria"]["quality_bound_threshold"]

    return {
        "stage_mismatch_penalty": stage_mismatch_penalty,
        "quality_bound": quality_bound,
        "cost_ratio": cost_ratio,
        "pass_penalty": pass_penalty,
        "pass_speed": pass_speed,
        "pass_quality": pass_quality,
        "gate_result": "PASS" if (pass_penalty and pass_speed and pass_quality) else "FAIL"
    }


def plot_pareto_frontier(scores_df: pd.DataFrame, costs: Dict[str, float], output_path: str) -> None:
    """Plot performance vs. curation cost."""
    plt.figure(figsize=(10, 6))

    for condition in scores_df["condition"]:
        if condition == "baseline":
            cost = 0.0
        else:
            stage = condition.split("_")[0]
            cost = costs[stage]

        mmlu = scores_df[scores_df["condition"] == condition]["mmlu"].values[0]

        if condition == "baseline":
            plt.scatter(cost, mmlu, s=150, c="red", marker="*", label="Baseline", zorder=10)
        elif "early" in condition:
            plt.scatter(cost, mmlu, s=80, c="blue", alpha=0.7, label="Early" if "k2000" in condition else "")
        elif "mid" in condition:
            plt.scatter(cost, mmlu, s=80, c="green", alpha=0.7, label="Mid" if "k2000" in condition else "")
        elif "late" in condition:
            plt.scatter(cost, mmlu, s=80, c="orange", alpha=0.7, label="Late" if "k2000" in condition else "")

        plt.text(cost + 1, mmlu + 0.001, condition, fontsize=8)

    plt.xlabel("Curation Cost (seconds)", fontsize=12)
    plt.ylabel("MMLU Accuracy", fontsize=12)
    plt.title("Pareto Frontier: Performance vs. Curation Cost", fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"✓ Saved Pareto frontier to {output_path}")


def plot_convergence_curves(scores_df: pd.DataFrame, output_path: str) -> None:
    """Plot performance vs. subset size k."""
    plt.figure(figsize=(10, 6))

    k_values = [2000, 5000, 10000]

    for stage in ["early", "mid", "late"]:
        mmlu_scores = []
        for k in k_values:
            condition = f"{stage}_k{k}"
            mmlu = scores_df[scores_df["condition"] == condition]["mmlu"].values[0]
            mmlu_scores.append(mmlu)

        plt.plot(k_values, mmlu_scores, marker="o", label=stage.capitalize())

    # Baseline
    baseline_mmlu = scores_df[scores_df["condition"] == "baseline"]["mmlu"].values[0]
    plt.axhline(y=baseline_mmlu, color="red", linestyle="--", label="Baseline (full dataset)")

    plt.xlabel("Subset Size k", fontsize=12)
    plt.ylabel("MMLU Accuracy", fontsize=12)
    plt.title("Convergence Curves: Performance vs. Subset Size", fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"✓ Saved convergence curves to {output_path}")


def generate_metrics_table(metrics: Dict[str, float], output_path: str) -> None:
    """Save metrics to CSV."""
    df = pd.DataFrame([metrics])
    df.to_csv(output_path, index=False)
    print(f"✓ Saved metrics table to {output_path}")


def analyze_results(config: dict, timings: Dict[str, float]) -> Dict[str, float]:
    """
    Load scores, compute metrics, generate plots.
    Returns: metrics dict
    """
    # Load scores
    scores_path = f"{config['paths']['results_dir']}scores.csv"
    scores_df = pd.read_csv(scores_path)

    print("\n=== Scores ===")
    print(scores_df.to_string(index=False))

    # Compute metrics
    metrics = compute_tradeoff_metrics(scores_df, timings, config)

    print("\n=== Trade-off Metrics ===")
    print(f"Stage-mismatch penalty: {metrics['stage_mismatch_penalty']:.4f} (threshold: {config['success_criteria']['stage_mismatch_penalty_threshold']})")
    print(f"Quality bound: {metrics['quality_bound']:.4f} (threshold: {config['success_criteria']['quality_bound_threshold']})")
    print(f"Cost ratio: {metrics['cost_ratio']:.2f}x (threshold: {config['success_criteria']['speed_advantage_threshold']})")
    print(f"\nPass penalty: {metrics['pass_penalty']}")
    print(f"Pass speed: {metrics['pass_speed']}")
    print(f"Pass quality: {metrics['pass_quality']}")
    print(f"\nGate result: {metrics['gate_result']}")

    # Generate plots
    plot_pareto_frontier(
        scores_df,
        timings,
        f"{config['paths']['analysis_dir']}figures/pareto_frontier.png"
    )

    plot_convergence_curves(
        scores_df,
        f"{config['paths']['analysis_dir']}figures/convergence_curves.png"
    )

    # Save metrics
    generate_metrics_table(
        metrics,
        f"{config['paths']['analysis_dir']}metrics.csv"
    )

    return metrics


if __name__ == "__main__":
    # Example timings (replace with actual values from embedding + selection)
    timings = {
        "early": 10.0,  # embedding + selection time in seconds
        "mid": 30.0,
        "late": 75.0
    }

    config = load_config()
    metrics = analyze_results(config, timings)

    print(f"\n✓ Analysis complete")
