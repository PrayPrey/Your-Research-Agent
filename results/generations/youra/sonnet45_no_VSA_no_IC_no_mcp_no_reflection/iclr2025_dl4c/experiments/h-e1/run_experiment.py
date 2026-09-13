#!/usr/bin/env python3
"""Run fix-impact-ratio experiment: baseline vs strategic agent."""

import json
from pathlib import Path
import numpy as np
from scipy.stats import mannwhitneyu

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dataset import create_synthetic_problems, save_dataset, load_dataset
from baseline_v2 import BaselineSequentialAgentV2
from agent_strategic_v2 import StrategicAgentV2

def run_experiments():
    """Run both baseline and strategic agent on all problems."""

    # Create dataset
    problems = create_synthetic_problems()
    dataset_path = Path(__file__).parent / 'data' / 'problems.json'
    save_dataset(problems, dataset_path)
    print(f"Created {len(problems)} problems")

    # Run baseline
    print("\n=== Running Baseline (Sequential) ===")
    baseline_agent = BaselineSequentialAgentV2()
    baseline_results = []
    for p in problems:
        result = baseline_agent.run(p)
        baseline_results.append(result)
        print(f"{p.problem_id}: ratio={result.fix_impact_ratio:.2f}, pass_rate={result.final_pass_rate:.1f}%")

    # Run strategic agent
    print("\n=== Running Strategic Agent ===")
    strategic_agent = StrategicAgentV2()
    strategic_results = []
    for p in problems:
        result = strategic_agent.run(p)
        strategic_results.append(result)
        print(f"{p.problem_id}: ratio={result.fix_impact_ratio:.2f}, pass_rate={result.final_pass_rate:.1f}%")

    # Statistical analysis
    print("\n=== Statistical Analysis ===")
    baseline_ratios = [r.fix_impact_ratio for r in baseline_results if r.fix_impact_ratio > 0]
    strategic_ratios = [r.fix_impact_ratio for r in strategic_results if r.fix_impact_ratio > 0]

    baseline_mean = np.mean(baseline_ratios)
    strategic_mean = np.mean(strategic_ratios)

    print(f"Baseline mean ratio: {baseline_mean:.2f} (n={len(baseline_ratios)})")
    print(f"Strategic mean ratio: {strategic_mean:.2f} (n={len(strategic_ratios)})")

    if len(baseline_ratios) > 0 and len(strategic_ratios) > 0:
        u_stat, p_value = mannwhitneyu(strategic_ratios, baseline_ratios, alternative='greater')
        print(f"Mann-Whitney U test: p={p_value:.4f}")

        # Cohen's d
        pooled_std = np.sqrt((np.var(strategic_ratios) + np.var(baseline_ratios)) / 2)
        cohens_d = (strategic_mean - baseline_mean) / pooled_std if pooled_std > 0 else 0
        print(f"Cohen's d effect size: {cohens_d:.2f}")

        # Gate assessment
        print("\n=== Gate Assessment (MUST_WORK) ===")
        gate_passed = True
        reasons = []

        if strategic_mean <= 2.0:
            gate_passed = False
            reasons.append(f"Strategic ratio {strategic_mean:.2f} ≤ 2.0 (threshold)")

        if not (0.8 <= baseline_mean <= 1.2):
            gate_passed = False
            reasons.append(f"Baseline ratio {baseline_mean:.2f} not ≈1.0 (metric insensitive)")

        if p_value >= 0.05:
            gate_passed = False
            reasons.append(f"p={p_value:.4f} ≥ 0.05 (not significant)")

        if cohens_d < 0.5:
            gate_passed = False
            reasons.append(f"Cohen's d={cohens_d:.2f} < 0.5 (small effect)")

        if gate_passed:
            print("✓ GATE PASSED")
            print(f"  - Strategic ratio={strategic_mean:.2f} > 2.0")
            print(f"  - Baseline ratio={baseline_mean:.2f} ≈ 1.0")
            print(f"  - p={p_value:.4f} < 0.05")
            print(f"  - Cohen's d={cohens_d:.2f} ≥ 0.5")
        else:
            print("✗ GATE FAILED")
            for r in reasons:
                print(f"  - {r}")

        # Save results
        results_dir = Path(__file__).parent / 'results'
        results_dir.mkdir(exist_ok=True)

        summary = {
            'baseline': {
                'mean_ratio': float(baseline_mean),
                'std_ratio': float(np.std(baseline_ratios)),
                'results': [{'problem_id': r.problem_id, 'ratio': r.fix_impact_ratio, 'pass_rate': r.final_pass_rate} for r in baseline_results]
            },
            'strategic': {
                'mean_ratio': float(strategic_mean),
                'std_ratio': float(np.std(strategic_ratios)),
                'results': [{'problem_id': r.problem_id, 'ratio': r.fix_impact_ratio, 'pass_rate': r.final_pass_rate} for r in strategic_results]
            },
            'statistics': {
                'p_value': float(p_value),
                'cohens_d': float(cohens_d)
            },
            'gate': {
                'passed': gate_passed,
                'reasons': reasons if not gate_passed else []
            }
        }

        with open(results_dir / 'results.json', 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\nResults saved to {results_dir / 'results.json'}")

        return gate_passed
    else:
        print("No valid results to analyze")
        return False

if __name__ == "__main__":
    gate_passed = run_experiments()
    sys.exit(0 if gate_passed else 1)
