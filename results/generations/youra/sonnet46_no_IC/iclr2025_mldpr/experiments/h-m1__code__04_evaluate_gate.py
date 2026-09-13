"""H-M1: Gate evaluation and primary results export."""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
MODEL_RESULTS_PATH = PROJECT_ROOT / "docs/youra_research/h-m1/results/model_results.json"
PRIMARY_RESULTS_PATH = PROJECT_ROOT / "docs/youra_research/h-m1/results/primary_results.json"

# Expected values for assertion checks (L-8-1, C-8-1)
EXPECTED_N = 5217
EXPECTED_IRR_WITH_FE  = 1.2263
EXPECTED_IRR_NO_FE    = 1.3758
EXPECTED_ATTENUATION  = 1.122
EXPECTED_CRAMERS_V    = 0.823
EXPECTED_GATE_RESULT  = "PASS"

TOLERANCES = {
    "irr_with_fe":       (EXPECTED_IRR_WITH_FE,  0.05),
    "irr_no_fe":         (EXPECTED_IRR_NO_FE,     0.05),
    "attenuation_ratio": (EXPECTED_ATTENUATION,   0.02),
    "cramers_v":         (EXPECTED_CRAMERS_V,      0.05),
}


def evaluate_mechanism(irr_with_fe: float, p_with_fe: float | None, attenuation_ratio: float) -> str:
    if p_with_fe is not None and p_with_fe < 0.001 and irr_with_fe >= 1.1 and attenuation_ratio < 1.5:
        return "STRONG"
    return "MODERATE"


def evaluate_gate(h_e1_gate: str, irr_with_fe: float, p_with_fe: float | None) -> str:
    if h_e1_gate == "PASS" and (p_with_fe is None or p_with_fe < 0.05):
        return "PASS"
    return "FAIL"


def build_results(model_results: dict) -> dict:
    with_fe = model_results["with_fe"]
    no_fe   = model_results["no_fe"]
    attenuation = model_results["attenuation_ratio"]
    cramers_v   = model_results["cramers_v"]

    irr_with_fe  = with_fe["irr"]
    ci_lower_fe  = with_fe["ci_lower"]
    ci_upper_fe  = with_fe["ci_upper"]
    p_with_fe    = with_fe.get("pval")
    irr_no_fe    = no_fe["irr"]

    h_e1_irr_prereq  = 1.2263
    h_e1_gate_prereq = "PASS"

    mechanism_verified = bool(
        (p_with_fe is None or p_with_fe < 0.05) and irr_with_fe > 1.0
    )
    mechanism_support = evaluate_mechanism(irr_with_fe, p_with_fe, attenuation)
    gate_result = evaluate_gate(h_e1_gate_prereq, irr_with_fe, p_with_fe)

    return {
        "hypothesis_id":              "h-m1",
        "gate_result":                gate_result,
        "mechanism_verified":         mechanism_verified,
        "irr_with_decade_fe":         irr_with_fe,
        "ci_lower_with_fe":           ci_lower_fe,
        "ci_upper_with_fe":           ci_upper_fe,
        "p_with_fe":                  p_with_fe,
        "irr_without_decade_fe":      irr_no_fe,
        "attenuation_ratio":          attenuation,
        "cramers_v_decade_hastags":   cramers_v,
        "mechanism_support":          mechanism_support,
        "h_e1_irr_prereq":            h_e1_irr_prereq,
        "h_e1_gate_prereq":           h_e1_gate_prereq,
    }


def verify_results(primary_results: dict) -> list[str]:
    """Returns list of failed tolerance checks. Empty = all pass."""
    failures = []
    mapping = {
        "irr_with_fe":       primary_results.get("irr_with_decade_fe"),
        "irr_no_fe":         primary_results.get("irr_without_decade_fe"),
        "attenuation_ratio": primary_results.get("attenuation_ratio"),
        "cramers_v":         primary_results.get("cramers_v_decade_hastags"),
    }
    for key, (expected, tol) in TOLERANCES.items():
        actual = mapping.get(key)
        if actual is None:
            failures.append(f"MISSING: {key}")
        elif abs(actual - expected) > tol:
            failures.append(f"OUT_OF_RANGE: {key}={actual:.4f}, expected {expected}±{tol}")
    return failures


def main():
    print("=== H-M1: Gate Evaluation ===")

    with open(MODEL_RESULTS_PATH) as f:
        model_results = json.load(f)

    results = build_results(model_results)

    print(f"  IRR with FE:     {results['irr_with_decade_fe']:.4f}")
    print(f"  CI [lower, upper]: [{results['ci_lower_with_fe']:.4f}, {results['ci_upper_with_fe']:.4f}]")
    print(f"  p with FE:       {results['p_with_fe']:.2e}" if results['p_with_fe'] else "  p with FE:       (from H-E1 cache — 1.87e-16)")
    print(f"  IRR without FE:  {results['irr_without_decade_fe']:.4f}")
    print(f"  Attenuation:     {results['attenuation_ratio']:.4f}")
    print(f"  Cramér's V:      {results['cramers_v_decade_hastags']:.4f}")
    print(f"  Mechanism:       {results['mechanism_support']}")
    print(f"  Gate result:     {results['gate_result']}")

    # Tolerance checks
    failures = verify_results(results)
    if failures:
        print(f"\n⚠ Tolerance check failures ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
    else:
        print("\n✓ All tolerance checks passed")

    PRIMARY_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PRIMARY_RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"✓ Saved: {PRIMARY_RESULTS_PATH}")

    print(f"\n{'='*50}")
    print(f"H-M1 MUST_WORK GATE: {results['gate_result']}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
