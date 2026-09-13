#!/usr/bin/env python3
"""
Generate Phase 4 Validation Report for H-M1
"""
import json
from pathlib import Path
from datetime import datetime

def generate_validation_report():
    """Generate 04_validation.md from experiment results"""

    results_file = Path("outputs/results.json")
    if not results_file.exists():
        print(f"ERROR: {results_file} not found. Run experiment first.")
        return 1

    with open(results_file) as f:
        results = json.load(f)

    # Extract metrics
    overall_rate = results['overall_detection_rate']
    gate_threshold = results['gate_threshold']
    gate_satisfied = results['gate_satisfied']
    task_count = results['task_count']
    total_mypy_errors = results['total_mypy_errors']
    total_iterations = results['total_iterations']

    # Generate report
    report = f"""# Phase 4 Validation Report
# Hypothesis H-M1: MECHANISM

**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Author:** Claude (Phase 4 Validation)
**Hypothesis Type:** MECHANISM
**Gate Type:** MUST_WORK

---

## Executive Summary

**Hypothesis Statement:** Under dual-sensitive programming task conditions (N=20 from H-E1), if mypy --strict static analysis is applied before execution feedback in cascade routing, then ~30-40% of errors are caught instantly with zero execution cost, because mypy provides compositional type safety guarantees (type errors, null safety, signature mismatches) without requiring test execution.

**Validation Result:** {'✅ **PASS**' if gate_satisfied else '❌ **FAIL**'}
- Mypy error detection rate: **{overall_rate:.1f}%**
- Gate threshold: **{gate_threshold:.1f}%**
- **Gate {'satisfied' if gate_satisfied else 'NOT satisfied'}:** MUST_WORK gate criteria {'met' if gate_satisfied else 'NOT met'}

---

## Methodology

### Dataset
- **Source:** HumanEval+ (evalplus package)
- **Qualified tasks:** N={task_count} dual-sensitive tasks from h-e1 validation
- **Samples per task:** K=20 (seed-controlled generation)

### Code Generation
- **Model:** CodeLlama-7B (base model, NOT instruction-tuned)
- **Configuration:**
  - Temperature: 0.8
  - Top-p: 0.95
  - Top-k: 40
  - Max length: 256 tokens
  - Device: Auto (H100 GPU)

### Verification
- **Static analysis:** mypy --strict (timeout: 10s per sample)
- **Execution testing:** pytest with HumanEval+ tests via evalplus (timeout: 120s per sample)
- **Total verifications:** {task_count} tasks × 20 samples = {total_iterations} total sample evaluations

### Mechanism Testing
- **Cascade routing:** Mypy first → if clean, then pytest
- **Detection rate:** Proportion of iterations where mypy caught errors before execution

---

## Results

### Summary Statistics

| Metric | Value |
|--------|-------|
| **Qualified tasks processed** | {task_count} |
| **Total samples evaluated** | {total_iterations} |
| **Mypy errors caught** | {total_mypy_errors} |
| **Mypy detection rate** | **{overall_rate:.1f}%** |
| **Gate threshold (MUST_WORK)** | {gate_threshold:.1f}% |
| **Gate result** | {'✅ **PASS**' if gate_satisfied else '❌ **FAIL**'} |

### Detection Rate Analysis

**Mypy Early Detection:**
- Total mypy failures: {total_mypy_errors} / {total_iterations} samples
- Detection rate: {overall_rate:.1f}%
- {'Hypothesis confirmed: Mypy catches ≥30% of errors early' if gate_satisfied else 'Hypothesis rejected: Mypy detection rate below 30% threshold'}

**Per-Task Statistics:**
"""

    # Add per-task breakdown
    task_results = results.get('task_results', [])
    if task_results:
        report += "\n**Sample Task Results (First 10):**\n\n"
        report += "| Task ID | Mypy Failures | Pytest Failures | Detection Rate |\n"
        report += "|---------|--------------|-----------------|----------------|\n"
        for task in task_results[:10]:
            tid = task['task_id']
            mypy_fail = task['mypy_failed']
            pytest_fail = task['pytest_failed']
            rate = task['mypy_detection_rate']
            report += f"| {tid} | {mypy_fail}/20 | {pytest_fail}/20 | {rate:.1f}% |\n"

        if len(task_results) > 10:
            report += f"\n*(Full results: {len(task_results)} tasks - see outputs/results.json)*\n"

    report += f"""

---

## Gate Validation

### MUST_WORK Gate Criteria

**Threshold:** Mypy error detection rate ≥ {gate_threshold:.1f}%

**Measured:** {overall_rate:.1f}%

**Result:** {'✅ PASS - Gate threshold exceeded' if gate_satisfied else '❌ FAIL - Gate threshold not met'}

{'**Analysis:** The hypothesis is validated. Static analysis (mypy --strict) successfully catches ≥30% of errors before execution, demonstrating that cascade routing can reduce computational cost while maintaining early error detection.' if gate_satisfied else '**Analysis:** The hypothesis is NOT validated. Static analysis detection rate falls below the 30% threshold, suggesting cascade routing may not provide sufficient early error detection to justify the approach.'}

---

## Visualization

**Generated Figures:**
1. `fig1_gate_metrics.png` - Gate threshold vs actual detection rate
2. `fig2_task_breakdown.png` - Per-task mypy detection rates
3. `fig3_distribution.png` - Distribution of detection rates across tasks

**Location:** `h-m1/figures/`

---

## Conclusion

**Hypothesis H-M1:** {'✅ **VALIDATED**' if gate_satisfied else '❌ **REJECTED**'}

{'The mechanism hypothesis is confirmed. Mypy --strict static analysis provides sufficient early error detection (≥30%) to justify cascade routing in dual-sensitive programming tasks.' if gate_satisfied else 'The mechanism hypothesis is rejected. Static analysis alone does not provide sufficient early error detection to meet the 30% threshold required for cascade routing justification.'}

**Implications:**
{'- Cascade routing (mypy → pytest) is a viable strategy for reducing execution cost' if gate_satisfied else '- Cascade routing may need refinement or higher detection thresholds'}
{'- Static analysis catches ~{overall_rate:.0f}% of errors instantly without execution overhead' if gate_satisfied else '- Alternative routing strategies should be explored'}
{'- Next steps: Test adaptive aggregation (h-m2) and efficiency comparison (h-m3)' if gate_satisfied else '- Consider pivoting to execution-first or hybrid routing approaches'}

---

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Data Source:** outputs/results.json
**Experiment:** Phase 4 Real Data Implementation (Mock Data Fixed)
"""

    # Write report
    report_path = Path("../04_validation.md")
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"✅ Validation report generated: {report_path}")
    print(f"   Detection rate: {overall_rate:.1f}%")
    print(f"   Gate status: {'PASS' if gate_satisfied else 'FAIL'}")

    return 0 if gate_satisfied else 1

if __name__ == "__main__":
    import sys
    sys.exit(generate_validation_report())
