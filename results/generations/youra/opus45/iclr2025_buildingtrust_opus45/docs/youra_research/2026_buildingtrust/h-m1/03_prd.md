# Product Requirements Document: H-M1 Conditional Margin Inflation Analysis

**Document ID:** PRD-H-M1-001
**Version:** 1.0
**Date:** 2026-03-24
**Author:** Phase 3 Implementation Planning
**Hypothesis:** H-M1 (MECHANISM)
**Status:** COMPLETE

---

## Executive Summary

This PRD defines the requirements for validating hypothesis H-M1: that RLHF instruction tuning inflates logit margins uniformly including for incorrect predictions, measurable as E[margin|incorrect]_instruct > E[margin|incorrect]_base. This is a MUST_WORK gate hypothesis that builds on H-E1's established AUROC degradation by investigating the underlying mechanism.

The experiment reanalyzes cached inference results from H-E1 (Qwen and Mistral families, ~14,000 MMLU samples) using conditional margin analysis and permutation testing. Success criteria require E[margin|incorrect]_instruct > E[margin|incorrect]_base with p < 0.05 for both tested families.

**Key Insight:** H-M1 is a statistical reanalysis hypothesis - no new model inference is required. It leverages H-E1's cached margins and correctness arrays.

---

## Problem Statement

### Background

H-E1 established that instruction-tuned LLMs exhibit significantly lower AUROC for margin-based correctness prediction. The observed margin inflation was non-uniform: Mistral showed ~8x inflation for correct predictions but ~17x for incorrect predictions. This suggests the mechanism driving AUROC degradation is disproportionate margin inflation for incorrect predictions.

### Problem

**Research Question:** Does RLHF instruction tuning inflate margins disproportionately for incorrect predictions, thereby explaining the AUROC degradation established in H-E1?

**Hypothesis Statement:** RLHF instruction tuning inflates logit margins uniformly including for incorrect predictions, measurable as E[margin|incorrect]_instruct > E[margin|incorrect]_base.

### Impact

- **If validated:** Confirms mechanism hypothesis, enabling investigation of calibration decoupling (H-M2)
- **If falsified:** PIVOT required - alternative mechanism must be identified

---

## Functional Requirements

### FR-1: Load Cached H-E1 Results

**FR-1.1:** Load cached margin arrays from H-E1
- Source: `h-e1/code/results/` directory
- Files: `{model_name}_margins.npy`, `{model_name}_correctness.npy`
- Models: Qwen base/instruct, Mistral base/instruct

**FR-1.2:** Validate cached data integrity
- Check array shapes match (N samples)
- Validate correctness is binary (0/1)
- Validate margins are positive floats

**FR-1.3:** Load experiment results JSON
- Source: `h-e1/experiment_results.json`
- Extract sample counts and model metadata

### FR-2: Conditional Margin Computation

**FR-2.1:** Partition samples by correctness
- Correct mask: `correctness == 1`
- Incorrect mask: `correctness == 0`

**FR-2.2:** Compute conditional means
- E[margin|correct] for each model
- E[margin|incorrect] for each model

**FR-2.3:** Compute standard errors
- SE = std / sqrt(n) for each condition
- Use for confidence interval calculation

### FR-3: Statistical Comparison

**FR-3.1:** Implement permutation test
```python
from scipy.stats import permutation_test

result = permutation_test(
    (margins_inst_incorrect, margins_base_incorrect),
    statistic=lambda x, y: np.mean(x) - np.mean(y),
    permutation_type='independent',
    alternative='greater',
    n_resamples=9999
)
```

**FR-3.2:** Compute effect sizes
- Raw difference: E[margin|incorrect]_inst - E[margin|incorrect]_base
- Inflation ratio: E[margin|incorrect]_inst / E[margin|incorrect]_base
- Cohen's d for standardized effect size

**FR-3.3:** Compute 95% confidence intervals
- Bootstrap CI for mean difference
- N = 1000 bootstrap iterations

### FR-4: Cross-Family Comparison

**FR-4.1:** Compute per-family results
- Qwen: base vs instruct incorrect margin comparison
- Mistral: base vs instruct incorrect margin comparison

**FR-4.2:** Compute aggregate statistics
- Mean inflation ratio across families
- Direction consistency check

### FR-5: Secondary Analysis

**FR-5.1:** Compare correct vs incorrect inflation ratios
- Ratio_correct = E[margin|correct]_inst / E[margin|correct]_base
- Ratio_incorrect = E[margin|incorrect]_inst / E[margin|incorrect]_base
- Test if Ratio_incorrect > Ratio_correct

**FR-5.2:** Distribution comparison
- KL divergence between base and instruct margin distributions
- Per-condition (correct/incorrect) analysis

### FR-6: Visualization

**FR-6.1:** Generate gate metrics comparison bar chart (REQUIRED)
- X-axis: Model families (Qwen, Mistral)
- Y-axis: E[margin|incorrect]
- Grouped bars: base vs instruct
- Include 95% CI error bars

**FR-6.2:** Generate margin distribution KDE plots
- 4-panel figure: base-correct, base-incorrect, inst-correct, inst-incorrect
- Overlay for visual comparison

**FR-6.3:** Generate box plots
- Margin distributions by condition (correct/incorrect) and model variant (base/instruct)

**FR-6.4:** Generate inflation ratio comparison
- Bar chart: correct_ratio vs incorrect_ratio per family
- Show disproportionate inflation

**FR-6.5:** Generate forest plot
- Effect sizes with 95% CIs across families
- Pooled estimate

**FR-6.6:** Save all figures to `h-m1/figures/` directory

### FR-7: Results Reporting

**FR-7.1:** Generate structured results file
- YAML format: `h-m1/experiment_results.yaml`
- Include all computed metrics and p-values

**FR-7.2:** Generate validation report
- Summary statistics per model family
- Gate evaluation (MUST_WORK criteria)
- Recommendation for hypothesis outcome

---

## Non-Functional Requirements

### NFR-1: Performance

**NFR-1.1:** Complete analysis within 5 minutes
- No model inference required
- Permutation test is primary computation

**NFR-1.2:** Memory efficiency
- Load one family's arrays at a time
- No GPU required

### NFR-2: Reproducibility

**NFR-2.1:** Fixed random seeds
- Seed = 42 for permutation test and bootstrap
- Numpy random state preserved

**NFR-2.2:** Deterministic outputs
- All random operations seeded
- Results exactly reproducible

### NFR-3: Reliability

**NFR-3.1:** Input validation
- Verify H-E1 cache files exist
- Validate data formats before analysis

**NFR-3.2:** Error handling
- Graceful handling of missing data
- Clear error messages

### NFR-4: Observability

**NFR-4.1:** Logging
- Log data loading events
- Log statistical computation progress
- Log final results

**NFR-4.2:** Timing
- Track total analysis duration

---

## Success Criteria

### Primary Gate Criteria (MUST_WORK)

**SC-1:** E[margin|incorrect]_instruct > E[margin|incorrect]_base for tested families
- Qwen: E[margin|incorrect]_inst > E[margin|incorrect]_base
- Mistral: E[margin|incorrect]_inst > E[margin|incorrect]_base

**SC-2:** Statistical significance
- p-value < 0.05 (one-tailed permutation test) for each family

### Secondary Criteria (Informational)

**SC-3:** Effect consistency
- Both families show same direction
- Similar inflation ratios

**SC-4:** Mechanism support
- Inflation ratio for incorrect > inflation ratio for correct
- This explains AUROC degradation

---

## Dependencies

### External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| numpy | >=1.24.0 | Numerical operations |
| scipy | >=1.11.0 | Statistical tests |
| matplotlib | >=3.7.0 | Visualization |
| seaborn | >=0.12.0 | Statistical plots |
| pyyaml | >=6.0 | Results serialization |

### Internal Dependencies

| Dependency | Source |
|------------|--------|
| H-E1 Cached Results | `h-e1/code/results/` |
| H-E1 Experiment Results | `h-e1/experiment_results.json` |
| Phase 2C Experiment Brief | `h-m1/02c_experiment_brief.md` |
| verification_state.yaml | Pipeline state tracking |

### Prerequisite Hypothesis

- **H-E1:** COMPLETED with PASS (AUROC degradation established)
- Required outputs: margin arrays, correctness arrays per model

---

## Data Specifications

### Input Data

**H-E1 Cached Arrays:**
- Source: `h-e1/code/results/` or similar cache location
- Format: NumPy `.npy` files
- Contents:
  - `*_margins.npy`: (N,) float array of logit margins
  - `*_correctness.npy`: (N,) binary array of correctness labels

**Models Covered:**
- Qwen2.5-7B (base), Qwen2.5-7B-Instruct
- Mistral-7B-v0.1 (base), Mistral-7B-Instruct-v0.2

### Output Data

**Primary Outputs:**
- `h-m1/experiment_results.yaml` - Structured results
- `h-m1/04_validation.md` - Validation report
- `h-m1/figures/gate_metrics.png` - Main gate figure

**Metrics Schema:**
```yaml
results:
  per_family:
    qwen:
      mean_base_incorrect: float
      mean_inst_incorrect: float
      inflation_ratio: float
      p_value: float
      gate_pass: bool
    mistral:
      mean_base_incorrect: float
      mean_inst_incorrect: float
      inflation_ratio: float
      p_value: float
      gate_pass: bool
  aggregate:
    all_families_pass: bool
    mean_inflation_ratio: float
gate_result: PASS | FAIL
```

---

## Constraints

### Technical Constraints

- CPU-only execution (no GPU required)
- Reuses H-E1 cached data (no new inference)
- Python 3.9+ required

### Scope Constraints

- Qwen and Mistral families only (Llama skipped due to H-E1 gating)
- Zero-shot MMLU results only
- Analysis scope: conditional margin comparison only

### Budget Constraints

- Task budget: 30 tasks maximum (FULL tier for MECHANISM hypothesis)
- Epic range: 6-12 epics

---

## Risks and Mitigations

### Risk 1: H-E1 Cache Not Found
- **Probability:** Low (H-E1 completed successfully)
- **Impact:** High (cannot run analysis)
- **Mitigation:** Re-run H-E1 inference if needed; verify cache path

### Risk 2: Margin Inflation Not Significant
- **Probability:** Low (H-E1 data shows large effect)
- **Impact:** High (hypothesis fails, need PIVOT)
- **Mitigation:** This is valid scientific outcome; record failure for Serena memory

### Risk 3: Opposite Direction (base > instruct)
- **Probability:** Very low (contradicts H-E1 observations)
- **Impact:** Critical (invalidates mechanism theory)
- **Mitigation:** Verify H-E1 data loading correctness

---

## Appendix: Phase 2C Traceability

| PRD Requirement | Phase 2C Source |
|-----------------|-----------------|
| FR-1 (Load Cache) | Implementation Research - H-E1 Code Assets |
| FR-2 (Conditional Margins) | Core Mechanism Implementation pseudo-code |
| FR-3 (Statistical Test) | scipy.stats.permutation_test reference |
| FR-4 (Cross-Family) | Models section table |
| FR-5 (Secondary Analysis) | Continuation Context insights |
| FR-6 (Visualization) | Visualization Requirements section |
| Success Criteria | Gate Condition and PoC Success Check |

---

## Appendix: H-E1 Context

**H-E1 Results Summary (Prerequisite):**
- Qwen: AUROC degradation +0.0222 (base 0.8298 vs instruct 0.8076)
- Mistral: AUROC degradation +0.0385 (base 0.7797 vs instruct 0.7413)
- Key observation: Mean margins inflate dramatically after instruction tuning
- Mistral: correct margins ~8x, incorrect margins ~17x

**Why This Matters for H-M1:**
The disproportionate inflation for incorrect predictions (17x vs 8x) suggests margins become less informative about correctness - this is the mechanism H-M1 tests directly.

---

*Generated by Phase 3 Implementation Planning Workflow*
*Source: h-m1/02c_experiment_brief.md*
*Next: Architecture Design (03_architecture.md)*
