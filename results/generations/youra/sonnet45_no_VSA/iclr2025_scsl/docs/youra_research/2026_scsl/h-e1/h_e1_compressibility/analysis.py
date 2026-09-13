"""Statistical analysis and visualization for h-e1."""

import argparse
from pathlib import Path
from typing import Tuple
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns


ANALYSIS_CONFIG = {
    "primary_test": "wilcoxon",
    "secondary_test": "cohens_d",
    "alpha": 0.05,
    "effect_size_thresholds": {
        "small": 0.2,
        "medium": 0.5,
        "large": 0.8
    },
    "auc_integration_method": "trapezoidal",
    "sparsity_threshold": 0.6,
    "accuracy_threshold": 0.7
}

VISUALIZATION_CONFIG = {
    "figure_format": "pdf",
    "figure_dpi": 300,
    "figure_size": (8, 6),
    "line_width": 2,
    "marker_size": 6,
    "error_bar_type": "std",
    "color_palette": "Set2",
    "show_grid": True,
    "legend_loc": "best"
}


def compute_auc(df: pd.DataFrame, method: str, seed: int) -> float:
    """Compute AUC for a single method-seed combination."""
    subset = df[(df["method"] == method) & (df["seed"] == seed)].sort_values("sparsity")
    if len(subset) == 0:
        return 0.0
    return np.trapz(subset["worst_group_acc"], subset["sparsity"])


def wilcoxon_test(df: pd.DataFrame, method1: str, method2: str) -> Tuple[float, float]:
    """Wilcoxon signed-rank test on pruning curve AUC."""
    seeds = df["seed"].unique()
    auc1 = [compute_auc(df, method1, seed) for seed in seeds]
    auc2 = [compute_auc(df, method2, seed) for seed in seeds]

    if len(auc1) < 2:
        return 1.0, 0.0

    stat, p_value = stats.wilcoxon(auc1, auc2)
    return p_value, np.mean(auc1) - np.mean(auc2)


def cohens_d(df: pd.DataFrame, method1: str, method2: str, sparsity: float) -> float:
    """Cohen's d effect size at specific sparsity level."""
    subset1 = df[(df["method"] == method1) & (df["sparsity"] == sparsity)]
    subset2 = df[(df["method"] == method2) & (df["sparsity"] == sparsity)]

    if len(subset1) == 0 or len(subset2) == 0:
        return 0.0

    mean1 = subset1["worst_group_acc"].mean()
    mean2 = subset2["worst_group_acc"].mean()
    std1 = subset1["worst_group_acc"].std()
    std2 = subset2["worst_group_acc"].std()

    pooled_std = np.sqrt((std1**2 + std2**2) / 2)
    if pooled_std == 0:
        return 0.0

    return (mean1 - mean2) / pooled_std


def plot_pruning_curves(df: pd.DataFrame, output_path: str):
    """Plot pruning curves with mean ± std per method."""
    plt.figure(figsize=VISUALIZATION_CONFIG["figure_size"])

    methods = df["method"].unique()
    palette = sns.color_palette(VISUALIZATION_CONFIG["color_palette"], len(methods))

    for method, color in zip(methods, palette):
        subset = df[df["method"] == method]
        grouped = subset.groupby("sparsity")["worst_group_acc"]

        mean = grouped.mean()
        std = grouped.std()

        plt.plot(mean.index, mean.values, label=method, color=color,
                linewidth=VISUALIZATION_CONFIG["line_width"],
                marker='o', markersize=VISUALIZATION_CONFIG["marker_size"])
        plt.fill_between(mean.index, mean - std, mean + std, alpha=0.2, color=color)

    plt.axhline(y=ANALYSIS_CONFIG["accuracy_threshold"], color='red',
                linestyle='--', label='70% threshold')
    plt.axvline(x=ANALYSIS_CONFIG["sparsity_threshold"], color='gray',
                linestyle='--', label='60% sparsity')

    plt.xlabel("Sparsity", fontsize=12)
    plt.ylabel("Worst-Group Accuracy", fontsize=12)
    plt.title("Pruning Curves: Worst-Group Accuracy vs Sparsity", fontsize=14)
    plt.legend(loc=VISUALIZATION_CONFIG["legend_loc"])
    plt.grid(VISUALIZATION_CONFIG["show_grid"])

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, format=VISUALIZATION_CONFIG["figure_format"],
                dpi=VISUALIZATION_CONFIG["figure_dpi"], bbox_inches='tight')
    plt.close()


def plot_statistical_tests(df: pd.DataFrame, output_path: str):
    """Plot AUC comparison with significance markers."""
    methods = df["method"].unique()
    seeds = df["seed"].unique()

    auc_values = []
    for method in methods:
        aucs = [compute_auc(df, method, seed) for seed in seeds]
        auc_values.append({
            "method": method,
            "mean": np.mean(aucs),
            "std": np.std(aucs)
        })

    auc_df = pd.DataFrame(auc_values)

    plt.figure(figsize=VISUALIZATION_CONFIG["figure_size"])
    plt.bar(auc_df["method"], auc_df["mean"], yerr=auc_df["std"], capsize=5)
    plt.xlabel("Method", fontsize=12)
    plt.ylabel("AUC (Worst-Group Accuracy)", fontsize=12)
    plt.title("AUC Comparison Across Methods", fontsize=14)
    plt.grid(VISUALIZATION_CONFIG["show_grid"], axis='y')

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, format=VISUALIZATION_CONFIG["figure_format"],
                dpi=VISUALIZATION_CONFIG["figure_dpi"], bbox_inches='tight')
    plt.close()


def evaluate_gate(df: pd.DataFrame) -> Dict[str, Any]:
    """Evaluate MUST_WORK gate decision."""
    sam_60 = df[(df["method"] == "SAM") & (df["sparsity"] == 0.6)]["worst_group_acc"]
    erm_60 = df[(df["method"] == "ERM") & (df["sparsity"] == 0.6)]["worst_group_acc"]

    sam_mean_60 = sam_60.mean() if len(sam_60) > 0 else 0.0
    erm_mean_60 = erm_60.mean() if len(erm_60) > 0 else 0.0

    p_value, auc_diff = wilcoxon_test(df, "SAM", "ERM")
    effect_size = cohens_d(df, "SAM", "ERM", 0.6)

    gate_pass = (
        sam_mean_60 >= 0.7 and
        p_value < 0.05 and
        effect_size > 0.5
    )

    return {
        "gate_result": "PASS" if gate_pass else "FAIL",
        "sam_acc_60": sam_mean_60,
        "erm_acc_60": erm_mean_60,
        "wilcoxon_p": p_value,
        "cohens_d": effect_size,
        "auc_diff": auc_diff
    }


def main(
    pruning_logs: str,
    output_dir: str = "results/figures/",
    format: str = "pdf"
):
    """Analysis CLI entry point."""
    df = pd.read_csv(pruning_logs)

    print("Generating pruning curves...")
    plot_pruning_curves(df, f"{output_dir}/h_e1_pruning_curves.{format}")

    print("Generating statistical test plots...")
    plot_statistical_tests(df, f"{output_dir}/h_e1_statistical_tests.{format}")

    print("\n" + "="*60)
    print("STATISTICAL ANALYSIS RESULTS")
    print("="*60)

    gate_results = evaluate_gate(df)
    print(f"\nGate Result: {gate_results['gate_result']}")
    print(f"SAM Worst-Group Accuracy at 60% sparsity: {gate_results['sam_acc_60']:.4f}")
    print(f"ERM Worst-Group Accuracy at 60% sparsity: {gate_results['erm_acc_60']:.4f}")
    print(f"Wilcoxon p-value: {gate_results['wilcoxon_p']:.4f}")
    print(f"Cohen's d at 60% sparsity: {gate_results['cohens_d']:.4f}")
    print(f"AUC difference (SAM - ERM): {gate_results['auc_diff']:.4f}")
    print("="*60)

    return gate_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pruning-logs", type=str, required=True,
                        help="Path to pruning logs CSV")
    parser.add_argument("--output-dir", type=str, default="results/figures/",
                        help="Directory to save figures")
    parser.add_argument("--format", type=str, default="pdf",
                        choices=["pdf", "png", "svg"])

    args = parser.parse_args()

    main(
        pruning_logs=args.pruning_logs,
        output_dir=args.output_dir,
        format=args.format
    )
