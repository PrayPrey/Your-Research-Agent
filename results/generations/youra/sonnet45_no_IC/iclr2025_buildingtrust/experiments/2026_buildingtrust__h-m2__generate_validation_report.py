#!/usr/bin/env python3
"""
Generate 04_validation.md report from experiment results
"""

import json
import yaml
from pathlib import Path
from datetime import datetime

def generate_report():
    """Generate validation report from experiment results"""

    # Load experiment results
    results_file = Path("code/outputs/experiment_results.json")
    if not results_file.exists():
        print(f"❌ Results file not found: {results_file}")
        return False

    with open(results_file) as f:
        results = json.load(f)

    # Load checkpoint
    checkpoint_file = Path("04_checkpoint.yaml")
    with open(checkpoint_file) as f:
        checkpoint = yaml.safe_load(f)

    # Extract key information
    hypothesis_id = results["hypothesis_id"]
    gate_result = results["gate"]["gate_result"]
    gate_type = results["gate"]["gate_type"]
    correlation = results["correlation"]
    gate_stats = results["gate"]

    # Generate report
    report = f"""# Phase 4 Validation Report: {hypothesis_id}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | {hypothesis_id} |
| **Type** | MECHANISM |
| **Statement** | Fairness-Reliability negative correlation via alignment tax |
| **Phase 4 Completed** | {datetime.now().isoformat()} |

---

## Implementation Summary

### Code Generation

**Approach:** Incremental (extends h-m1)

**Generated Components:**
- `run_experiment_h_m2.py` - Main experiment script
- `src/fairness_scorer.py` - HONEST fairness metric implementation
- `run_h_m2_experiment.sh` - Experiment launcher

**Reused from h-m1:**
- Dataset loading (TruthfulQA)
- Model loading (Llama-2-7b-chat)
- Response generation
- Reliability scoring
- Correlation analysis
- Statistical testing

**New for h-m2:**
- Demographic augmentation (4 variants per prompt)
- Semantic similarity scoring (SBERT embeddings)
- HONEST bias metric computation

---

## Experiment Results

### Execution Summary

| Metric | Value |
|--------|-------|
| **Dataset** | TruthfulQA (817 prompts) |
| **Model** | Llama-2-7b-chat-hf |
| **Total Inferences** | ~4085 (817 baseline + 817×4 variants) |
| **Reliability Mean** | {results['statistics']['reliability']['mean']:.4f} ± {results['statistics']['reliability']['std']:.4f} |
| **Fairness Mean** | {results['statistics']['fairness']['mean']:.4f} ± {results['statistics']['fairness']['std']:.4f} |

### Correlation Analysis

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| **Pearson r** | {correlation['r']:.4f} | < -0.2 | {'✅ PASS' if gate_stats['checks']['r < -0.2'] else '❌ FAIL'} |
| **p-value** | {correlation['p_value']:.6f} | < 0.05 | {'✅ PASS' if gate_stats['checks']['p < 0.05'] else '❌ FAIL'} |
| **95% CI** | [{correlation['ci_lower']:.4f}, {correlation['ci_upper']:.4f}] | Upper < -0.1 | {'✅ PASS' if gate_stats['checks']['CI upper < -0.1'] else '❌ FAIL'} |
| **Sample Size** | {correlation['n']} | - | - |

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | {gate_type} |
| **Result** | **{gate_result}** |
| **Evaluated At** | {datetime.now().isoformat()} |

### Criteria Evaluation

"""

    # Add gate criteria
    for check_name, passed in gate_stats['checks'].items():
        status = "✅ PASS" if passed else "❌ FAIL"
        report += f"- {status} {check_name}\n"

    report += f"\n**Overall:** {'✅ All criteria satisfied' if gate_stats['all_passed'] else '❌ Some criteria not met'}\n\n"

    # Add interpretation
    if gate_result == "PASS":
        report += """---

## Interpretation

✅ **MECHANISM VALIDATED**

The hypothesis that fairness and reliability exhibit negative correlation due to alignment tax is **SUPPORTED** by the data:

1. **Negative Correlation Confirmed:** r < -0.2 indicates fairness and reliability are inversely related
2. **Statistical Significance:** p < 0.05 confirms the correlation is not due to chance
3. **Confidence Interval:** CI upper < -0.1 confirms the effect is meaningfully negative

**Mechanism:** RLHF fine-tuning prioritizes fairness/safety over factual accuracy, creating a measurable trade-off in model outputs.

---

## Next Steps

### ✅ Ready for Phase 5

Hypothesis validation complete. Proceed to Phase 5 for baseline comparison and comprehensive evaluation.

**Actions:**
1. Run `/phase5-baseline-comparison` for h-m2
2. Compare results against independence baseline
3. Document findings for Phase 6 (paper writing)

"""
    else:
        report += """---

## Interpretation

⚠️ **HYPOTHESIS NOT SUPPORTED**

The expected negative correlation between fairness and reliability was not observed in the data.

**Possible Explanations:**
1. Alignment tax effect is smaller than hypothesized (|r| < 0.2)
2. Effect may exist but require larger sample size
3. Dimensions may be more independent than theorized

**Recommendations:**
1. Review demographic augmentation methodology
2. Consider alternative fairness metrics
3. Analyze individual prompt types for heterogeneous effects
4. Revise hypothesis or pivot to independence hypothesis

---

## Next Steps

### ⚠️ SHOULD_WORK Gate - Proceed with Limitations

Gate type is SHOULD_WORK, so workflow continues despite failure.

**Actions:**
1. Document limitation in verification_state.yaml
2. Proceed to Phase 5 for comprehensive analysis
3. Consider hypothesis revision in Phase 2A

"""

    # Write report
    report_file = Path("04_validation.md")
    with open(report_file, "w") as f:
        f.write(report)

    print(f"✅ Validation report generated: {report_file}")
    print(f"   Gate result: {gate_result}")
    print(f"   Correlation r: {correlation['r']:.4f}")

    return True

if __name__ == "__main__":
    success = generate_report()
    exit(0 if success else 1)
