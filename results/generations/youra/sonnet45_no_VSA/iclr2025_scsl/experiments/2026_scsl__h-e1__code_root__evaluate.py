"""
Statistical analysis and validation report generation for H-E1
"""

import json
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import bootstrap
from pathlib import Path
from typing import Dict, List


def statistical_analysis(
    joint_scores: List[float],
    sam_scores: List[float],
    swa_scores: List[float],
    alpha: float = 0.0125
) -> Dict:
    """
    Perform statistical tests for hypothesis validation.

    Args:
        joint_scores: Joint SAM+SWA worst-group accuracies (n=5 seeds)
        sam_scores: SAM-only worst-group accuracies (n=5 seeds)
        swa_scores: SWA-only worst-group accuracies (n=5 seeds)
        alpha: Significance level (Bonferroni-corrected)

    Returns:
        Statistical test results
    """
    # Best baseline per seed
    best_baseline_scores = [max(sam, swa) for sam, swa in zip(sam_scores, swa_scores)]

    # Differences
    differences = np.array(joint_scores) - np.array(best_baseline_scores)

    # Paired t-test (one-sided: Joint > Baseline + 0.5%)
    t_stat, p_value = stats.ttest_1samp(
        differences,
        popmean=0.005,  # 0.5% threshold
        alternative='greater'
    )

    # Bootstrap 95% CIs
    ci_joint = bootstrap(
        (np.array(joint_scores),),
        np.mean,
        n_resamples=1000,
        confidence_level=0.95,
        random_state=42
    )
    ci_baseline = bootstrap(
        (np.array(best_baseline_scores),),
        np.mean,
        n_resamples=1000,
        confidence_level=0.95,
        random_state=42
    )

    # Check CI non-overlap
    non_overlapping = (ci_joint.confidence_interval.low > ci_baseline.confidence_interval.high)

    # Cohen's d effect size
    pooled_std = np.sqrt((np.var(joint_scores) + np.var(best_baseline_scores)) / 2)
    cohens_d = np.mean(differences) / pooled_std if pooled_std > 0 else 0.0

    return {
        "mean_joint": float(np.mean(joint_scores)),
        "mean_sam": float(np.mean(sam_scores)),
        "mean_swa": float(np.mean(swa_scores)),
        "mean_best_baseline": float(np.mean(best_baseline_scores)),
        "mean_difference": float(np.mean(differences)),
        "std_joint": float(np.std(joint_scores)),
        "std_baseline": float(np.std(best_baseline_scores)),
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "significant": bool(p_value < alpha),
        "ci_joint_low": float(ci_joint.confidence_interval.low),
        "ci_joint_high": float(ci_joint.confidence_interval.high),
        "ci_baseline_low": float(ci_baseline.confidence_interval.low),
        "ci_baseline_high": float(ci_baseline.confidence_interval.high),
        "ci_non_overlapping": bool(non_overlapping),
        "cohens_d": float(cohens_d),
        "alpha": alpha
    }


def generate_validation_report(
    results_csv: str,
    output_file: str
):
    """
    Generate validation report (04_validation.md) from experiment results.

    Args:
        results_csv: Path to results CSV file
        output_file: Output markdown file path
    """
    # Load results
    df = pd.read_csv(results_csv)

    # Separate by dataset
    df_cmnist = df[df["dataset"] == "ColoredMNIST"]
    df_celeba = df[df["dataset"] == "CelebA"]

    report_lines = []
    report_lines.append("# Validation Report: H-E1 SAM+SWA Joint Training\n")
    report_lines.append("**Hypothesis ID**: h-e1")
    report_lines.append("**Gate Type**: MUST_WORK")
    report_lines.append("**Generated**: 2026-07-10\n")
    report_lines.append("---\n")

    # ColoredMNIST Results
    report_lines.append("## ColoredMNIST Results\n")
    report_lines.append("### Worst-Group Accuracy by Method\n")
    report_lines.append("| Method | Mean ± Std | Seeds |\n")
    report_lines.append("|--------|-----------|-------|\n")

    for method in ["ERM", "SAM", "SWA", "Joint", "Sequential"]:
        scores = df_cmnist[df_cmnist["method"] == method]["test_wg_acc"].values
        if len(scores) > 0:
            mean = np.mean(scores) * 100
            std = np.std(scores) * 100
            seeds_str = ", ".join([f"{s*100:.1f}" for s in scores])
            report_lines.append(f"| {method} | {mean:.2f} ± {std:.2f} | {seeds_str} |\n")

    # Statistical analysis ColoredMNIST
    joint_cmnist = df_cmnist[df_cmnist["method"] == "Joint"]["test_wg_acc"].values
    sam_cmnist = df_cmnist[df_cmnist["method"] == "SAM"]["test_wg_acc"].values
    swa_cmnist = df_cmnist[df_cmnist["method"] == "SWA"]["test_wg_acc"].values

    if len(joint_cmnist) == 5 and len(sam_cmnist) == 5 and len(swa_cmnist) == 5:
        stats_cmnist = statistical_analysis(
            joint_cmnist.tolist(),
            sam_cmnist.tolist(),
            swa_cmnist.tolist()
        )

        report_lines.append("\n### Statistical Analysis\n")
        report_lines.append(f"- **Mean Difference (Joint - Best Baseline)**: {stats_cmnist['mean_difference']*100:.2f}%\n")
        report_lines.append(f"- **Paired t-test p-value**: {stats_cmnist['p_value']:.4f}\n")
        report_lines.append(f"- **Significant (α=0.0125)**: {stats_cmnist['significant']}\n")
        report_lines.append(f"- **95% CI Joint**: [{stats_cmnist['ci_joint_low']*100:.2f}%, {stats_cmnist['ci_joint_high']*100:.2f}%]\n")
        report_lines.append(f"- **95% CI Baseline**: [{stats_cmnist['ci_baseline_low']*100:.2f}%, {stats_cmnist['ci_baseline_high']*100:.2f}%]\n")
        report_lines.append(f"- **CI Non-Overlapping**: {stats_cmnist['ci_non_overlapping']}\n")
        report_lines.append(f"- **Cohen's d**: {stats_cmnist['cohens_d']:.3f}\n")

    # CelebA Results
    report_lines.append("\n---\n")
    report_lines.append("## CelebA Results\n")
    report_lines.append("### Worst-Group Accuracy by Method\n")
    report_lines.append("| Method | Mean ± Std | Seeds |\n")
    report_lines.append("|--------|-----------|-------|\n")

    for method in ["ERM", "SAM", "SWA", "Joint", "Sequential"]:
        scores = df_celeba[df_celeba["method"] == method]["test_wg_acc"].values
        if len(scores) > 0:
            mean = np.mean(scores) * 100
            std = np.std(scores) * 100
            seeds_str = ", ".join([f"{s*100:.1f}" for s in scores])
            report_lines.append(f"| {method} | {mean:.2f} ± {std:.2f} | {seeds_str} |\n")

    # Statistical analysis CelebA
    joint_celeba = df_celeba[df_celeba["method"] == "Joint"]["test_wg_acc"].values
    sam_celeba = df_celeba[df_celeba["method"] == "SAM"]["test_wg_acc"].values
    swa_celeba = df_celeba[df_celeba["method"] == "SWA"]["test_wg_acc"].values

    if len(joint_celeba) == 5 and len(sam_celeba) == 5 and len(swa_celeba) == 5:
        stats_celeba = statistical_analysis(
            joint_celeba.tolist(),
            sam_celeba.tolist(),
            swa_celeba.tolist()
        )

        report_lines.append("\n### Statistical Analysis\n")
        report_lines.append(f"- **Mean Difference (Joint - Best Baseline)**: {stats_celeba['mean_difference']*100:.2f}%\n")
        report_lines.append(f"- **Paired t-test p-value**: {stats_celeba['p_value']:.4f}\n")
        report_lines.append(f"- **Significant (α=0.0125)**: {stats_celeba['significant']}\n")
        report_lines.append(f"- **95% CI Joint**: [{stats_celeba['ci_joint_low']*100:.2f}%, {stats_celeba['ci_joint_high']*100:.2f}%]\n")
        report_lines.append(f"- **95% CI Baseline**: [{stats_celeba['ci_baseline_low']*100:.2f}%, {stats_celeba['ci_baseline_high']*100:.2f}%]\n")
        report_lines.append(f"- **CI Non-Overlapping**: {stats_celeba['ci_non_overlapping']}\n")
        report_lines.append(f"- **Cohen's d**: {stats_celeba['cohens_d']:.3f}\n")

    # Gate Decision
    report_lines.append("\n---\n")
    report_lines.append("## Gate Decision\n")

    if len(joint_cmnist) == 5 and len(joint_celeba) == 5:
        cmnist_pass = stats_cmnist["significant"] and stats_cmnist["ci_non_overlapping"] and stats_cmnist["mean_difference"] >= 0.005
        celeba_pass = stats_celeba["significant"] and stats_celeba["ci_non_overlapping"] and stats_celeba["mean_difference"] >= 0.005

        if cmnist_pass and celeba_pass:
            report_lines.append("**Result**: PASS\n")
            report_lines.append("- Joint SAM+SWA exceeds best baseline by ≥0.5% on BOTH datasets\n")
            report_lines.append("- Statistical significance confirmed (p < 0.0125, CIs non-overlapping)\n")
            report_lines.append("- Proceed to H-M1, H-M2, H-M3 (mechanism hypotheses)\n")
        elif cmnist_pass or celeba_pass:
            report_lines.append("**Result**: PARTIAL\n")
            dataset_passed = "ColoredMNIST" if cmnist_pass else "CelebA"
            report_lines.append(f"- Hypothesis confirmed on {dataset_passed} only\n")
            report_lines.append("- Route to Phase 2A-Dialogue for hypothesis refinement\n")
        else:
            report_lines.append("**Result**: FAIL\n")
            report_lines.append("- No statistically significant gains on either dataset\n")
            report_lines.append("- Route to Phase 0 for fundamental approach revision\n")
    else:
        report_lines.append("**Result**: INCOMPLETE\n")
        report_lines.append("- Not all experiments completed (< 5 seeds per method)\n")

    # Computational Budget
    total_time = df["training_time_hours"].sum()
    report_lines.append("\n---\n")
    report_lines.append("## Computational Budget\n")
    report_lines.append(f"- **Total GPU-hours**: {total_time:.2f}h\n")
    report_lines.append(f"- **Budget limit**: 35.0h\n")
    report_lines.append(f"- **Within budget**: {total_time <= 35.0}\n")

    # Write report
    with open(output_file, "w") as f:
        f.writelines(report_lines)

    print(f"Validation report written to {output_file}")
