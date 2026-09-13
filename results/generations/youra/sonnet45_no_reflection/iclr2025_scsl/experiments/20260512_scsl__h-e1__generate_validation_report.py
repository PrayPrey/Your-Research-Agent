#!/usr/bin/env python3
"""Generate Phase 4 validation report from experiment results."""
import json
import os
from datetime import datetime


def load_results():
    """Load experiment results."""
    results = {}

    # Load baseline results
    baseline_path = "results/baseline_poc_results.json"
    if os.path.exists(baseline_path):
        with open(baseline_path, 'r') as f:
            results['baseline'] = json.load(f)

    # Load proposed results
    proposed_path = "results/proposed_poc_results.json"
    if os.path.exists(proposed_path):
        with open(proposed_path, 'r') as f:
            results['proposed'] = json.load(f)

    # Load gate validation
    gate_path = "results/gate_validation.json"
    if os.path.exists(gate_path):
        with open(gate_path, 'r') as f:
            results['gate'] = json.load(f)

    return results


def generate_report(results):
    """Generate markdown validation report."""

    baseline = results.get('baseline', {})
    proposed = results.get('proposed', {})
    gate = results.get('gate', {})

    # Extract metrics
    baseline_sr = baseline.get('mean_stable_rank', 0)
    proposed_sr = proposed.get('mean_stable_rank', 0)
    baseline_ppl = baseline.get('perplexity', 0)
    proposed_ppl = proposed.get('perplexity', 0)
    layer_variance = proposed.get('layer_variance', 0)
    measurement_cv = proposed.get('measurement_cv', 0)

    sr_reduction = gate.get('sr_reduction', 0)
    ppl_deviation = gate.get('ppl_deviation', 0)
    gate_pass = gate.get('gate_pass', False)

    # Generate report
    report = f"""# Phase 4 Validation Report: h-e1
# Jacobian Stable Rank Regularization - EXISTENCE PoC

**Hypothesis ID:** h-e1
**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Gate Type:** MUST_WORK
**Status:** {'PASS ✓' if gate_pass else 'FAIL ✗'}

---

## Executive Summary

**Hypothesis Statement:**
Under pretraining with explicit residual-corrected Jacobian stable rank (sr_ℓ^res) regularization, if models are trained to minimize sr_ℓ^res = ||J̃_ℓ||_F^2 / ||J̃_ℓ||_2^2 per layer, then mean stable rank reduces by ≥20% relative to baseline while maintaining iso-perplexity (≤1% deviation).

**Implementation Approach:**
- PoC validation with 5000 training steps (~320M tokens)
- Baseline vs Regularized GPT-2 comparison
- Residual-corrected Jacobian stable rank regularization
- Adaptive lambda tuning for iso-perplexity

**Gate Result:** {'PASS ✓' if gate_pass else 'FAIL ✗'}

---

## Experimental Results

### Training Configuration

| Parameter | Baseline | Proposed |
|-----------|----------|----------|
| Model | GPT-2 125M | GPT-2 125M + Regularization |
| Training Steps | 5000 | 5000 |
| Total Tokens | ~320M | ~320M |
| Batch Size | 32 (effective 128) | 32 (effective 128) |
| Learning Rate | 3e-4 | 3e-4 |
| Lambda Init | 0.0 | 0.01 (adaptive) |
| Seed | 42 | 42 |

### Gate Metrics

| Metric | Target | Baseline | Proposed | Result | Pass/Fail |
|--------|--------|----------|----------|--------|-----------|
| Mean Stable Rank Reduction | ≥20% | {baseline_sr:.2f} | {proposed_sr:.2f} | {sr_reduction*100:.1f}% | {'✓' if sr_reduction >= 0.20 else '✗'} |
| Perplexity Deviation | ≤1% | {baseline_ppl:.2f} | {proposed_ppl:.2f} | {ppl_deviation*100:.2f}% | {'✓' if ppl_deviation <= 0.01 else '✗'} |
| Layer Variance (CV) | <2.0× | N/A | {layer_variance:.3f} | {layer_variance:.3f} | {'✓' if layer_variance < 2.0 else '✗'} |
| Measurement CV | <15% | N/A | {measurement_cv:.3f} | {measurement_cv*100:.1f}% | {'✓' if measurement_cv < 0.15 else '✗'} |

### Detailed Results

**Baseline Model:**
- Final Perplexity: {baseline_ppl:.2f}
- Mean Stable Rank: {baseline_sr:.2f}
- Training: Completed 5000 steps

**Proposed Model:**
- Final Perplexity: {proposed_ppl:.2f}
- Mean Stable Rank: {proposed_sr:.2f}
- Layer Variance: {layer_variance:.3f}
- Measurement CV: {measurement_cv:.3f}
- Training: Completed 5000 steps with adaptive lambda

---

## Gate Validation

**Gate Type:** MUST_WORK

**Criteria:**
1. {'✓' if sr_reduction >= 0.20 else '✗'} Mean sr_ℓ^res reduction ≥20% vs baseline ({sr_reduction*100:.1f}%)
2. {'✓' if ppl_deviation <= 0.01 else '✗'} Perplexity deviation ≤1% from baseline ({ppl_deviation*100:.2f}%)
3. {'✓' if layer_variance < 2.0 else '✗'} Layer variance <2× mean stable rank ({layer_variance:.3f})
4. {'✓' if measurement_cv < 0.15 else '✗'} Measurement CV <15% ({measurement_cv*100:.1f}%)

**Gate Decision:** {'PASS ✓' if gate_pass else 'FAIL ✗'}

**Rationale:**
"""

    if gate_pass:
        report += """The hypothesis is validated in PoC setting. Residual-corrected Jacobian stable rank regularization successfully reduces stable rank by the target amount while maintaining iso-perplexity. Layer variance and measurement precision are within acceptable bounds. The regularization mechanism is controllable and effective.

**Recommendation:** Proceed to Phase 5 for baseline comparison against standard compression methods.
"""
    else:
        report += """The hypothesis failed validation. Analysis of failure mode:
"""
        if sr_reduction < 0.20:
            report += f"- Stable rank reduction insufficient ({sr_reduction*100:.1f}% < 20%)\n"
        if ppl_deviation > 0.01:
            report += f"- Perplexity deviation too large ({ppl_deviation*100:.2f}% > 1%)\n"
        if layer_variance >= 2.0:
            report += f"- Layer variance indicates capacity redistribution ({layer_variance:.3f} ≥ 2.0)\n"
        if measurement_cv >= 0.15:
            report += f"- Measurement precision insufficient ({measurement_cv*100:.1f}% ≥ 15%)\n"

        report += "\n**Recommendation:** Stop pipeline. Stable rank not controllable via gradient-based regularization. Consider pivoting to SVD-based rank methods or alternative Jacobian estimation.\n"

    report += """
---

## Visualizations

Generated figures saved to `h-e1/figures/`:

1. **gate_metrics.png** - Gate criteria comparison (mandatory)
2. **layer_evolution.png** - Training loss trajectory
3. **stable_rank_distribution.png** - Per-layer stable rank
4. **perplexity_trajectory.png** - Perplexity vs baseline
5. **measurement_precision.png** - Measurement CV over time

---

## Artifacts

### Code Files
- All source code in `h-e1/code/`
- Tests in `h-e1/tests/`
- Checkpoints in `h-e1/checkpoints/{baseline,proposed}/`

### Results Files
- `h-e1/results/baseline_poc_results.json`
- `h-e1/results/proposed_poc_results.json`
- `h-e1/results/gate_validation.json`

### Logs
- `h-e1/experiment.log` - Full experiment output
- `h-e1/checkpoints/*/training_logs.json` - Per-variant training logs

---

## Sign-off

**Implementation Status:** ✓ Complete
**Experiment Status:** ✓ Complete
**Gate Validation:** """ + ('✓ PASS' if gate_pass else '✗ FAIL') + """
**Ready for Phase 5:** """ + ('✓ Yes' if gate_pass else '✗ No (Stop Pipeline)') + """

---

**Validation Date:** """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
**Validated By:** YouRA Phase 4 Pipeline
**Next Phase:** """ + ('Phase 5 - Baseline Comparison' if gate_pass else 'Pipeline Stop') + """
"""

    return report


def main():
    """Main entry point."""
    print("Loading experiment results...")
    results = load_results()

    if not results:
        print("ERROR: No results found. Experiment may not have completed.")
        return False

    print("Generating validation report...")
    report = generate_report(results)

    # Save report
    output_path = "04_validation.md"
    with open(output_path, 'w') as f:
        f.write(report)

    print(f"✓ Validation report saved: {output_path}")

    # Print summary
    gate = results.get('gate', {})
    gate_pass = gate.get('gate_pass', False)

    print(f"\nGate Status: {'PASS ✓' if gate_pass else 'FAIL ✗'}")

    return gate_pass


if __name__ == "__main__":
    gate_pass = main()
    exit(0 if gate_pass else 1)
