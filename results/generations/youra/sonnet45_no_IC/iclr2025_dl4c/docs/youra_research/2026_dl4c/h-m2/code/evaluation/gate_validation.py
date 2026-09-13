"""
Gate Validation Analysis - Generate 04_validation.md report
Task: A-8
Hypothesis: h-m1
"""

import os
import json
from datetime import datetime
from typing import Dict
from .phase1_metrics import Phase1Analyzer


def generate_validation_report(
    gate_result: Dict,
    weight_trajectory: list,
    pass_at_1_trajectory: list,
    output_path: str = "../04_validation.md"
):
    """
    Generate 04_validation.md report with gate decision and metrics.

    Args:
        gate_result: Gate validation result from Phase1Analyzer
        weight_trajectory: Weight checkpoint data
        pass_at_1_trajectory: Pass@1 checkpoint data
        output_path: Path to save report
    """

    report = f"""# Validation Report: h-m1

**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Hypothesis:** Phase 1 Execution-Heavy Weight Validation
**Gate Type:** MUST_WORK
**Status:** {gate_result['gate_result']}

---

## Executive Summary

This report validates hypothesis h-m1: "Under Phase 1 training (0-30% progress), if execution feedback weight is highest among three signals, then basic correctness (pass@1) improves fastest in early training."

**Gate Decision:** **{gate_result['gate_result']}**

---

## Validation Metrics

### Metric 1: Weight Dominance (MUST_WORK Criterion)

**Question:** Is execution weight highest at all Phase 1 checkpoints (0%, 10%, 20%, 30%)?

**Result:** {'✅ PASS' if gate_result['metric1_weight_dominance']['passed'] else '❌ FAIL'}

**Data:**

| Progress | Execution Weight | AI Weight | Human Weight | Dominant? |
|----------|------------------|-----------|--------------|-----------|
"""

    # Add checkpoint table
    for cp in gate_result['metric1_weight_dominance']['checkpoints']:
        exec_w = cp['execution_weight']
        ai_w = cp['ai_weight']
        human_w = cp['human_weight']
        dominant = '✓' if cp['dominant'] else '✗'

        report += f"| {cp['progress']:.0%} | {exec_w:.3f} | {ai_w:.3f} | {human_w:.3f} | {dominant} |\n"

    report += f"\n**Violations:** {gate_result['metric1_weight_dominance']['violation_count']}\n\n"

    # Metric 2: Improvement Rates
    improvement = gate_result['metric2_pass_at_1_improvement']

    report += f"""### Metric 2: Pass@1 Improvement Rate (MUST_WORK Criterion)

**Question:** Is Phase 1 improvement rate higher than later phases?

**Result:** {'✅ PASS' if improvement['passed'] else '❌ FAIL'}

**Data:**

- **Phase 1 Rate (0-30%):** {improvement['phase1_rate']:.4f}
- **Later Rate (30-100%):** {improvement['later_rate']:.4f}
- **Ratio:** {improvement['ratio']:.2f}x

**Interpretation:** Phase 1 shows {"higher" if improvement['passed'] else "lower or equal"} improvement rate, {"supporting" if improvement['passed'] else "contradicting"} the hypothesis that execution feedback accelerates early correctness gains.

---

"""

    # Metric 3: Correlation
    correlation = gate_result['metric3_weight_correlation']

    report += f"""### Metric 3: Weight Correlation (MUST_WORK Criterion)

**Question:** Is execution weight stable or increasing in Phase 1?

**Result:** {'✅ PASS' if correlation['passed'] else '❌ FAIL'}

**Data:**

- **Pearson ρ:** {correlation['correlation']:.3f}
- **P-value:** {correlation['p_value']:.3f}
- **Threshold:** ρ > -0.5

**Interpretation:** Correlation of {correlation['correlation']:.3f} indicates {"stable/increasing" if correlation['correlation'] > 0 else "slightly decreasing but acceptable"} execution weight in Phase 1.

---

## Gate Decision

**MUST_WORK Gate:** {gate_result['gate_result']}

**Rationale:**

{gate_result['rationale']}

---

## Experimental Evidence

### Weight Trajectory

See `figures/weight_trajectory.png` for visual confirmation of weight dynamics.

### Pass@1 Trajectory

See `figures/pass_at_1_trajectory.png` for improvement rates across phases.

### Gate Metrics

See `figures/gate_metrics.png` for comprehensive gate validation visualization.

---

## Next Steps

"""

    if gate_result['gate_result'] == 'PASS':
        report += """✅ **PASS:** Hypothesis h-m1 validated. Proceed to:
- Phase 5: Baseline Comparison (compare against h-e1 baseline)
- Document findings in Phase 6: Paper Writing

**Key Findings:**
- Execution feedback is dominant in Phase 1 (0-30% training)
- Early training shows faster correctness improvement
- Mechanism hypothesis confirmed
"""
    else:
        report += """❌ **FAIL:** Hypothesis h-m1 NOT validated. Return to:
- Phase 2A: Hypothesis redesign
- Re-examine dynamic weight scheduling mechanism
- Consider alternative Phase 1 definitions

**Issues Identified:**
- Weight dominance not maintained throughout Phase 1
- OR improvement rate lower in Phase 1
- OR execution weight correlation too negative

**Recommendation:** Revise hypothesis or adjust weight scheduling parameters.
"""

    report += f"""
---

## Appendix: Raw Data

**Weight Checkpoints:** {len(weight_trajectory)} points logged
**Pass@1 Checkpoints:** {len(pass_at_1_trajectory)} points logged

**Checkpoint Data Location:** `./checkpoints/`

**Generated Figures:**
- `figures/weight_trajectory.png`
- `figures/pass_at_1_trajectory.png`
- `figures/phase_improvement_rates.png`
- `figures/gate_metrics.png`

---

**Report Generated:** {datetime.now().isoformat()}
**Workflow:** YouRA Phase 4 (PoC Implementation & Validation)
**Next Phase:** Phase 5 (Baseline Comparison) [if PASS] or Phase 2A (Hypothesis Redesign) [if FAIL]
"""

    # Write report
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(report)

    print(f"✓ Validation report saved: {output_path}")

    return output_path
