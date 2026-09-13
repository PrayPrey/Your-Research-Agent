from dataclasses import dataclass
from directional_tests import DirectionalTestResults


@dataclass
class GateResult:
    metrics_passed: int
    gate_passed: bool
    gate_type: str
    verdict_message: str


def verify_directional_specificity(results: DirectionalTestResults) -> GateResult:
    metrics_passed = sum([
        results.metric1_pass,
        results.metric2_pass,
        results.metric3_pass,
        results.metric4_pass,
    ])
    gate_passed = metrics_passed >= 2
    gate_type = "PASS" if gate_passed else "EXPLORE"
    verdict_message = (
        f"GATE: {gate_type} — {metrics_passed}/4 directional metrics consistent with H1"
    )
    print(verdict_message)
    if not gate_passed:
        print("Scope limitation: insufficient directional evidence for ceiling compression skewness")
    return GateResult(
        metrics_passed=metrics_passed,
        gate_passed=gate_passed,
        gate_type=gate_type,
        verdict_message=verdict_message,
    )
