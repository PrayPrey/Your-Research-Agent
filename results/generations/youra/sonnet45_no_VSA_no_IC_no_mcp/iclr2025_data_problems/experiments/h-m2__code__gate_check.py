"""Gate check for h-m2 SHOULD_WORK criteria."""

import yaml

def main():
    # Load gate criteria
    with open("config/gate_criteria.yaml") as f:
        gate_config = yaml.safe_load(f)

    # Load statistical analysis
    with open("results/statistical_analysis.yaml") as f:
        stats = yaml.safe_load(f)

    # Extract values
    indep_delta = stats["transfer_deltas"]["independent"]["average"]
    dep_delta = stats["transfer_deltas"]["dependent"]["average"]
    indep_ci = stats["confidence_intervals"]["independent"]
    dep_ci = stats["confidence_intervals"]["dependent"]
    p_value = stats["statistical_tests"]["welch_t_test"]["p_value"]
    cohens_d = stats["statistical_tests"]["cohens_d"]

    # Check primary criteria
    primary = gate_config["should_work"]["primary"]
    indep_ok = indep_delta <= primary["objective_independent_delta_max"]
    dep_ok = dep_delta > primary["objective_dependent_delta_min"]

    # Check secondary criteria
    secondary = gate_config["should_work"]["secondary"]
    ci_separation = indep_ci["upper"] < dep_ci["lower"]

    # Check statistical criteria
    statistical = gate_config["should_work"]["statistical"]
    significance_ok = p_value < statistical["min_significance"]
    effect_ok = cohens_d > statistical["min_effect_size"]

    # Overall status
    passed = indep_ok and dep_ok and ci_separation

    print("\n=== GATE CHECK (SHOULD_WORK) ===")
    print(f"\nPrimary Criteria:")
    print(f"  Independent delta ≤ {primary['objective_independent_delta_max']}%: {indep_delta:.2f}% [{indep_ok}]")
    print(f"  Dependent delta > {primary['objective_dependent_delta_min']}%: {dep_delta:.2f}% [{dep_ok}]")

    print(f"\nSecondary Criteria:")
    print(f"  CI separation: [{ci_separation}]")
    print(f"    Independent CI: [{indep_ci['lower']:.2f}%, {indep_ci['upper']:.2f}%]")
    print(f"    Dependent CI: [{dep_ci['lower']:.2f}%, {dep_ci['upper']:.2f}%]")

    print(f"\nStatistical Criteria (P2):")
    print(f"  p < {statistical['min_significance']}: {p_value:.4f} [{significance_ok}]")
    print(f"  Cohen's d > {statistical['min_effect_size']}: {cohens_d:.3f} [{effect_ok}]")

    print(f"\n{'='*35}")
    print(f"GATE STATUS: {'PASS' if passed else 'FAIL'}")
    print(f"{'='*35}\n")

    # Save result
    gate_result = {
        "status": "PASS" if passed else "FAIL",
        "primary_criteria": {
            "independent_delta": {"value": float(indep_delta), "threshold": primary["objective_independent_delta_max"], "passed": indep_ok},
            "dependent_delta": {"value": float(dep_delta), "threshold": primary["objective_dependent_delta_min"], "passed": dep_ok}
        },
        "secondary_criteria": {
            "ci_separation": ci_separation
        },
        "statistical_criteria": {
            "p_value": {"value": float(p_value), "threshold": statistical["min_significance"], "passed": significance_ok},
            "cohens_d": {"value": float(cohens_d), "threshold": statistical["min_effect_size"], "passed": effect_ok}
        },
        "overall_passed": passed
    }

    with open("results/gate_check.yaml", "w") as f:
        yaml.dump(gate_result, f, default_flow_style=False)

    print("Saved gate_check.yaml")

if __name__ == "__main__":
    main()
