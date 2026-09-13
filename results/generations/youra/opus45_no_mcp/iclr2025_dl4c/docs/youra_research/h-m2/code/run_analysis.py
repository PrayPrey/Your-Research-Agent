#!/usr/bin/env python3
"""Main runner for H-M2 error localization analysis."""
import os
import sys
import json
from typing import List, Dict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    get_config, U_LINE_ERRORS, U_IGNORE_ERRORS, SEED
)
from ground_truth import annotate_ground_truth, spot_check_sample
from localization_analysis import (
    compute_category_accuracy, compute_distance_distribution,
    compute_per_exception_breakdown
)
from stats_tests import chi_square_test, mann_whitney_test
from visualization import (
    plot_accuracy_bar, plot_distance_distribution, plot_exception_breakdown
)
from apps_data_loader import collect_failing_samples_from_apps


def recategorize_sample(sample: Dict) -> str:
    """Recategorize using h-m2's U_LINE_ERRORS set."""
    tb = sample.get("traceback", "")
    for err in U_LINE_ERRORS:
        if err in tb:
            return "U_line"
    for err in U_IGNORE_ERRORS:
        if err in tb:
            return "U_ignore"
    return "unknown"


def load_or_generate_samples(
    n_samples: int = 500,
    reuse_h_m1: bool = True,
    checkpoint_path: str = "results/samples.json"
) -> List[Dict]:
    """Load existing samples or collect fresh from APPS dataset."""
    config = get_config()

    # Check for existing checkpoint with real data
    if os.path.exists(checkpoint_path):
        print(f"Loading checkpoint: {checkpoint_path}")
        with open(checkpoint_path, 'r') as f:
            samples = json.load(f)

        # Validate not mock data (mock has problem_id 0,1,2... sequentially)
        is_mock = all(s.get("problem_id") == i for i, s in enumerate(samples[:20]))
        if not is_mock and len(samples) >= n_samples // 2:
            for s in samples:
                s["error_type"] = recategorize_sample(s)
            return samples
        else:
            print("  Checkpoint contains mock data, regenerating...")

    # Check h-m1 samples
    h_m1_path = os.path.join(config.samples.h_m1_results_dir, "samples.json")
    if reuse_h_m1 and os.path.exists(h_m1_path):
        print(f"Checking h-m1 samples: {h_m1_path}")
        with open(h_m1_path, 'r') as f:
            samples = json.load(f)

        is_mock = all(s.get("problem_id") == i for i, s in enumerate(samples[:20]))
        if not is_mock and len(samples) >= n_samples // 2:
            for s in samples:
                s["error_type"] = recategorize_sample(s)
            return samples

    # Generate fresh samples from APPS dataset
    print(f"Collecting {n_samples} samples from APPS dataset...")
    samples = collect_failing_samples_from_apps(
        n_target=n_samples,
        max_problems=n_samples * 4,
        split="train",
        seed=SEED
    )

    for s in samples:
        s["error_type"] = recategorize_sample(s)

    # Save checkpoint
    os.makedirs(os.path.dirname(checkpoint_path) if os.path.dirname(checkpoint_path) else '.', exist_ok=True)
    with open(checkpoint_path, 'w') as f:
        json.dump(samples, f, indent=2)
    print(f"Saved samples to {checkpoint_path}")

    return samples


def main() -> Dict:
    """Run complete H-M2 analysis."""
    config = get_config()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)

    print("=== H-M2: Error Localization Analysis ===\n")

    print("Step 1: Loading/generating samples...")
    samples = load_or_generate_samples(
        n_samples=config.analysis.n_samples,
        reuse_h_m1=config.samples.reuse_h_m1,
        checkpoint_path=os.path.join(config.output_dir, "samples.json")
    )
    print(f"  Loaded {len(samples)} samples")

    print("\nStep 2: Annotating ground truth...")
    samples = annotate_ground_truth(samples)
    valid_samples = [s for s in samples if s.get("actual_bug_line") is not None]
    print(f"  Valid samples with ground truth: {len(valid_samples)}")

    print("\nStep 3: Computing category accuracy...")
    cat_acc = compute_category_accuracy(samples)
    print(f"  U_line: {cat_acc['U_line']['accuracy']*100:.1f}% (n={cat_acc['U_line']['n']})")
    print(f"  U_ignore: {cat_acc['U_ignore']['accuracy']*100:.1f}% (n={cat_acc['U_ignore']['n']})")

    print("\nStep 4: Computing distance distributions...")
    dist = compute_distance_distribution(samples)
    print(f"  U_line distances: {len(dist['U_line'])} samples")
    print(f"  U_ignore distances: {len(dist['U_ignore'])} samples")

    print("\nStep 5: Computing per-exception breakdown...")
    breakdown = compute_per_exception_breakdown(samples)
    for exc, stats in list(breakdown.items())[:5]:
        print(f"  {exc}: {stats['accuracy']*100:.1f}% (n={stats['n']})")

    print("\nStep 6: Running statistical tests...")
    chi2_result = chi_square_test(
        cat_acc['U_line']['correct'], cat_acc['U_line']['n'],
        cat_acc['U_ignore']['correct'], cat_acc['U_ignore']['n']
    )
    print(f"  Chi-square: chi2={chi2_result['chi2']:.2f}, p={chi2_result['p_value']:.4f}, significant={chi2_result['significant']}")

    mw_result = mann_whitney_test(dist['U_line'], dist['U_ignore'])
    print(f"  Mann-Whitney: U={mw_result['u_statistic']:.2f}, p={mw_result['p_value']:.4f}, significant={mw_result['significant']}")

    print("\nStep 7: Generating visualizations...")
    plot_accuracy_bar(cat_acc, os.path.join(config.figures_dir, "accuracy_bar.png"))
    plot_distance_distribution(dist, os.path.join(config.figures_dir, "distance_distribution.png"))
    plot_exception_breakdown(breakdown, os.path.join(config.figures_dir, "exception_breakdown.png"))
    print("  Saved 3 figures to figures/")

    print("\nStep 8: Determining verdict...")
    u_line_acc = cat_acc['U_line']['accuracy']
    u_ignore_acc = cat_acc['U_ignore']['accuracy']
    significant = chi2_result['significant']
    acc_diff_correct = u_line_acc > u_ignore_acc

    if significant and acc_diff_correct:
        verdict = "PASS"
        verdict_reason = f"U_line ({u_line_acc*100:.1f}%) > U_ignore ({u_ignore_acc*100:.1f}%) with p < 0.05"
    else:
        verdict = "FAIL"
        reasons = []
        if not acc_diff_correct:
            reasons.append(f"U_line ({u_line_acc*100:.1f}%) not > U_ignore ({u_ignore_acc*100:.1f}%)")
        if not significant:
            reasons.append(f"p={chi2_result['p_value']:.4f} >= 0.05")
        verdict_reason = "; ".join(reasons)

    print(f"\n  VERDICT: {verdict}")
    print(f"  Reason: {verdict_reason}")

    results = {
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "category_accuracy": cat_acc,
        "chi_square": chi2_result,
        "mann_whitney": mw_result,
        "per_exception_breakdown": breakdown,
        "sample_count": len(samples),
        "valid_sample_count": len(valid_samples)
    }

    results_path = os.path.join(config.output_dir, "results.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")

    spot_check = spot_check_sample(samples, n=config.analysis.spot_check_n)
    spot_check_path = os.path.join(config.output_dir, "spot_check.json")
    with open(spot_check_path, 'w') as f:
        json.dump(spot_check, f, indent=2)
    print(f"Spot-check samples saved to {spot_check_path}")

    return results


if __name__ == "__main__":
    results = main()
    print(f"\n=== Analysis Complete: {results['verdict']} ===")
