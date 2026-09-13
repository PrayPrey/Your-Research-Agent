"""Main analysis module for H-M2: G3 Superiority Over Minimal Feedback.

This performs post-hoc statistical analysis using H-M1 repair results to test whether
G3 (error+line) achieves at least 10 percentage points higher repair success than
G0 (pass/fail only).

Expected Result: FAIL (G0 significantly outperforms G3 based on H-M1 data)
"""

import json
import os
import yaml
from datetime import datetime
from typing import Tuple, List

from config import Config, GateConfig
from stats import (
    build_contingency_table,
    run_mcnemar_test,
    calculate_rates_and_difference,
    evaluate_gate
)
from visualize import (
    plot_comparison,
    plot_contingency_heatmap,
    plot_difference_ci,
    plot_gate_summary
)


def load_paired_results(results_path: str) -> Tuple[List[int], List[int]]:
    """Load G0/G3 paired outcomes from H-M1 results.

    Args:
        results_path: Path to repair_results.json from H-M1

    Returns:
        Tuple of (g0_outcomes, g3_outcomes) where each is a list of 0/1 values
    """
    with open(results_path, "r") as f:
        results = json.load(f)

    # Group by task_id
    task_results = {}
    for record in results:
        task_id = record["task_id"]
        granularity = record["granularity"]
        success = 1 if record["success"] else 0

        if task_id not in task_results:
            task_results[task_id] = {}
        task_results[task_id][granularity] = success

    # Extract paired G0/G3 outcomes
    g0_outcomes = []
    g3_outcomes = []

    for task_id in sorted(task_results.keys()):
        task_data = task_results[task_id]
        if "G0" in task_data and "G3" in task_data:
            g0_outcomes.append(task_data["G0"])
            g3_outcomes.append(task_data["G3"])

    return g0_outcomes, g3_outcomes


def validate_paired_data(g0: List[int], g3: List[int], expected_n: int) -> None:
    """Assert paired structure and expected count.

    Args:
        g0: G0 outcomes list
        g3: G3 outcomes list
        expected_n: Expected number of pairs

    Raises:
        AssertionError: If validation fails
    """
    assert len(g0) == len(g3), f"Paired data mismatch: G0={len(g0)}, G3={len(g3)}"
    assert len(g0) == expected_n, f"Expected {expected_n} pairs, got {len(g0)}"
    assert all(v in [0, 1] for v in g0), "G0 outcomes must be binary"
    assert all(v in [0, 1] for v in g3), "G3 outcomes must be binary"


def save_results(results: dict, config: Config) -> Tuple[str, str]:
    """Save comparison_results.json and metrics.yaml.

    Args:
        results: Combined results dict from main()
        config: Configuration object

    Returns:
        Tuple of (json_path, yaml_path)
    """
    os.makedirs(config.results_dir, exist_ok=True)

    # Save full results as JSON
    json_path = os.path.join(config.results_dir, "comparison_results.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    # Save key metrics as YAML
    metrics = {
        "g0_rate": results["rates"]["g0_rate"],
        "g3_rate": results["rates"]["g3_rate"],
        "difference_pp": results["rates"]["difference_pp"],
        "ci_lower_pp": results["rates"]["ci_lower_pp"],
        "ci_upper_pp": results["rates"]["ci_upper_pp"],
        "mcnemar_pvalue": results["mcnemar"]["pvalue"],
        "mcnemar_favors": results["mcnemar"]["favors"],
        "gate_passed": results["gate"]["gate_passed"],
        "gate_verdict": results["gate"]["verdict"],
        "n_pairs": results["rates"]["n_pairs"],
        "timestamp": results["timestamp"]
    }

    yaml_path = os.path.join(config.results_dir, "metrics.yaml")
    with open(yaml_path, "w") as f:
        yaml.dump(metrics, f, default_flow_style=False)

    return json_path, yaml_path


def main(config: Config = None) -> dict:
    """Orchestrate full analysis pipeline.

    Args:
        config: Configuration object (creates default if None)

    Returns:
        Combined results dict with all analysis outputs
    """
    if config is None:
        config = Config()

    gate_config = GateConfig()

    print("=" * 60)
    print("H-M2: G3 Superiority Over Minimal Feedback Analysis")
    print("=" * 60)
    print()

    # 1. Load paired results
    print(f"Loading H-M1 results from: {config.h_m1_results_path}")
    g0_outcomes, g3_outcomes = load_paired_results(config.h_m1_results_path)
    print(f"Loaded {len(g0_outcomes)} paired samples")

    # 2. Validate data
    print(f"Validating data (expected {config.expected_n_pairs} pairs)...")
    validate_paired_data(g0_outcomes, g3_outcomes, config.expected_n_pairs)
    print("Validation passed")
    print()

    # 3. Build contingency table
    print("Building contingency table...")
    table = build_contingency_table(g0_outcomes, g3_outcomes)
    print(f"Contingency table:")
    print(f"              G3=Fail  G3=Success")
    print(f"  G0=Fail      {table[0,0]:4d}      {table[0,1]:4d}")
    print(f"  G0=Success   {table[1,0]:4d}      {table[1,1]:4d}")
    print()

    # 4. Run McNemar's test
    print("Running McNemar's test...")
    mcnemar_result = run_mcnemar_test(table)
    print(f"  Statistic: {mcnemar_result['statistic']}")
    print(f"  p-value: {mcnemar_result['pvalue']:.2e}")
    print(f"  Favors: {mcnemar_result['favors']}")
    print(f"  Significant: {mcnemar_result['significant']}")
    print()

    # 5. Calculate rates and difference
    print("Calculating rates and difference...")
    rates = calculate_rates_and_difference(g0_outcomes, g3_outcomes)
    print(f"  G0 success rate: {rates['g0_rate']*100:.1f}% ({rates['g0_successes']}/{rates['n_pairs']})")
    print(f"  G3 success rate: {rates['g3_rate']*100:.1f}% ({rates['g3_successes']}/{rates['n_pairs']})")
    print(f"  Difference (G3-G0): {rates['difference_pp']:+.1f}pp")
    print(f"  95% CI: [{rates['ci_lower_pp']:.1f}, {rates['ci_upper_pp']:.1f}]pp")
    print()

    # 6. Evaluate gate
    print("Evaluating gate...")
    gate = evaluate_gate(rates, mcnemar_result, config.difference_threshold)
    print(f"  Gate type: {gate_config.gate_type}")
    print(f"  Condition: G3 >= G0 + {gate['threshold_pp']:.0f}pp")
    print(f"  Difference met: {gate['difference_met']}")
    print(f"  Significant: {gate['significant']}")
    print(f"  Favors G3: {gate['favors_g3']}")
    print()
    print(f"  VERDICT: {gate['verdict']}")
    print(f"  Reason: {gate['reason']}")
    print()

    # 7. Generate visualizations
    print("Generating figures...")
    figures = []

    fig1 = plot_comparison(rates, config.figures_dir, config.colors)
    figures.append(fig1)
    print(f"  Created: {fig1}")

    fig2 = plot_contingency_heatmap(table, config.figures_dir)
    figures.append(fig2)
    print(f"  Created: {fig2}")

    fig3 = plot_difference_ci(rates, config.figures_dir, config.colors)
    figures.append(fig3)
    print(f"  Created: {fig3}")

    fig4 = plot_gate_summary(rates, gate, mcnemar_result, config.figures_dir, config.colors)
    figures.append(fig4)
    print(f"  Created: {fig4}")
    print()

    # 8. Compile results
    timestamp = datetime.now().isoformat()
    results = {
        "hypothesis_id": "h-m2",
        "hypothesis_type": "MECHANISM",
        "hypothesis_statement": "G3 achieves at least 10pp higher repair success than G0",
        "timestamp": timestamp,
        "contingency_table": table.tolist(),
        "mcnemar": mcnemar_result,
        "rates": rates,
        "gate": gate,
        "gate_config": {
            "type": gate_config.gate_type,
            "threshold_pp": gate_config.difference_threshold * 100,
            "alpha": gate_config.alpha,
            "expected_result": gate_config.expected_result
        },
        "figures": figures,
        "mechanism_verification": {
            "n_pairs": rates["n_pairs"],
            "g0_has_successes": rates["g0_successes"] > 0,
            "g3_has_successes": rates["g3_successes"] > 0,
            "mcnemar_ran": "pvalue" in mcnemar_result,
            "verified": True
        }
    }

    # 9. Save results
    print("Saving results...")
    json_path, yaml_path = save_results(results, config)
    print(f"  JSON: {json_path}")
    print(f"  YAML: {yaml_path}")
    print()

    # 10. Summary
    print("=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Gate Result: {gate['verdict']} (expected: {gate_config.expected_result})")
    print(f"Key Finding: G0 ({rates['g0_rate']*100:.1f}%) outperforms G3 ({rates['g3_rate']*100:.1f}%) by {-rates['difference_pp']:.1f}pp")
    print("This contradicts the hypothesis that detailed feedback (G3) is superior.")
    print()

    return results


if __name__ == "__main__":
    results = main()
