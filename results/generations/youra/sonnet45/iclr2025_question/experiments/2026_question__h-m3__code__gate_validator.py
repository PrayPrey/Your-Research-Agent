"""Gate validation module for H-M3 Bootstrap CI Stability.

Task: T-EPIC-05 (A-5: Gate Validation Logic)
"""

from typing import Dict, Any
import json


def check_ci_width_threshold(
    bootstrap_results: Dict[str, Dict[str, float]],
    threshold: float
) -> Dict[str, Any]:
    """Validate CI width ≤ threshold for all conditions.

    Args:
        bootstrap_results: Dictionary of bootstrap analysis results
        threshold: CI width threshold percentage (default: 50.0)

    Returns:
        Gate result dictionary with pass/fail status
    """
    conditions_passed = []

    for condition, metrics in bootstrap_results.items():
        ci_width_pct = metrics['ci_width_pct']
        passed = ci_width_pct <= threshold
        conditions_passed.append((condition, passed, ci_width_pct))

    all_passed = all([p for _, p, _ in conditions_passed])

    gate_result = {
        "gate_type": "SHOULD_WORK",
        "threshold": threshold,
        "all_conditions_passed": all_passed,
        "gate_result": "PASS" if all_passed else "FAIL",
        "details": {
            condition: {
                "ci_width_pct": ci_width,
                "passed": passed
            }
            for condition, passed, ci_width in conditions_passed
        }
    }

    # Add notes about data availability
    total_expected = 4  # Expected 4 conditions (2 datasets × 2 architectures)
    total_available = len(bootstrap_results)
    if total_available < total_expected:
        gate_result["data_availability_note"] = (
            f"Only {total_available}/{total_expected} conditions available. "
            f"Missing conditions due to h-e1 experiment errors (fashion_mnist data missing)."
        )

    # Add recommendation if failed
    if not all_passed:
        gate_result["recommendation"] = (
            "N=30 insufficient for stable variance estimation. "
            "Add N sensitivity analysis (N=50, 100, 200) to exploration phase."
        )

    return gate_result


def generate_gate_report(
    bootstrap_results: Dict[str, Dict[str, float]],
    gate_result: Dict[str, Any]
) -> str:
    """Generate text report for gate validation.

    Args:
        bootstrap_results: Dictionary of bootstrap analysis results
        gate_result: Gate validation result

    Returns:
        Formatted text report
    """
    report_lines = []

    report_lines.append("\n" + "=" * 70)
    report_lines.append("GATE VALIDATION REPORT - H-M3 BOOTSTRAP CI STABILITY")
    report_lines.append("=" * 70)

    # Gate info
    report_lines.append(f"\nGate Type: {gate_result['gate_type']}")
    report_lines.append(f"Threshold: CI Width ≤ {gate_result['threshold']}%")
    report_lines.append(f"Gate Result: {gate_result['gate_result']}")

    # Per-condition results
    report_lines.append("\n" + "-" * 70)
    report_lines.append("PER-CONDITION RESULTS:")
    report_lines.append("-" * 70)

    for condition, details in gate_result['details'].items():
        ci_width = details['ci_width_pct']
        passed = details['passed']
        status_symbol = "✓" if passed else "✗"

        # Get variance metrics from bootstrap_results
        metrics = bootstrap_results[condition]
        variance_point = metrics['variance_point']
        ci_lower = metrics['ci_lower']
        ci_upper = metrics['ci_upper']

        report_lines.append(f"\n{status_symbol} {condition}")
        report_lines.append(f"  Variance: {variance_point:.6f}")
        report_lines.append(f"  CI: [{ci_lower:.6f}, {ci_upper:.6f}]")
        report_lines.append(f"  CI Width: {ci_width:.2f}% ({'PASS' if passed else 'FAIL'})")

    # Summary
    report_lines.append("\n" + "-" * 70)
    report_lines.append("SUMMARY:")
    report_lines.append("-" * 70)

    passed_count = sum(1 for d in gate_result['details'].values() if d['passed'])
    total_count = len(gate_result['details'])

    report_lines.append(f"Conditions Passed: {passed_count}/{total_count}")
    report_lines.append(f"All Conditions Passed: {gate_result['all_conditions_passed']}")
    report_lines.append(f"Gate Result: {gate_result['gate_result']}")

    # Recommendation if failed
    if 'recommendation' in gate_result:
        report_lines.append("\n" + "-" * 70)
        report_lines.append("RECOMMENDATION:")
        report_lines.append("-" * 70)
        report_lines.append(gate_result['recommendation'])

    report_lines.append("\n" + "=" * 70)

    return "\n".join(report_lines)


def save_gate_result(gate_result: Dict[str, Any], save_path: str) -> None:
    """Save gate result to JSON file.

    Args:
        gate_result: Gate validation result dictionary
        save_path: Path to save JSON file
    """
    with open(save_path, 'w') as f:
        json.dump(gate_result, f, indent=2)

    print(f"✓ Gate result saved to {save_path}")
