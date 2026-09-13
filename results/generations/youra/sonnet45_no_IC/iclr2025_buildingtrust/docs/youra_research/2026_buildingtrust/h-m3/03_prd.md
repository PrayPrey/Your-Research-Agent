# Product Requirements Document: h-m3

**Date:** 2026-07-12
**Author:** Anonymous
**Hypothesis:** h-m3 - Stratified Correlation Comparison
**Type:** MECHANISM
**Gate:** SHOULD_WORK

---

## Executive Summary

### Purpose
Validate whether reliability-robustness correlation strength differs significantly across prompt types (factual vs. misinformation), testing the hypothesis that retrieval-based processing (factual prompts) shows stronger coupling than reasoning-based processing (misinformation prompts).

### Core Hypothesis
Under stratified prompt types (factual vs. misinformation), if reliability-robustness correlations are computed separately per stratum, then correlation magnitudes differ significantly (Fisher z-test p<0.05), because factual prompts show stronger coupling (r>0.4) than reasoning/misinformation prompts (r<0.3) due to different retrieval vs. computation mechanisms.

### Success Criteria (SHOULD_WORK Gate)
1. **Primary:** Fisher z-test p < 0.05 (significant difference between strata)
2. **Secondary:** |r_factual - r_misinfo| ≥ 0.1 (meaningful difference magnitude)
3. **Tertiary:** r_factual > 0.4 AND r_misinfo < 0.3 (directional pattern matches theory)

---

## Problem Statement

### Research Question
Does the strength of reliability-robustness correlation vary significantly by prompt type, and does this variation support a dual-mechanism theory (retrieval vs. reasoning)?

### Prerequisites
- **h-m2:** COMPLETED (PASS) - Fairness-reliability trade-off validated
- **h-m1:** COMPLETED (PASS) - Reliability-robustness coupling validated (r=0.7233 on factual stratum)
- **h-e1:** COMPLETED (PASS) - Multi-dimensional measurement feasibility validated

### Context from Previous Hypotheses
- H-M1 demonstrated r=0.7233 (p<0.001) on factual stratum
- H-M1 supplementary analysis showed r=0.2798 on misinformation stratum (not formally tested)
- All model outputs (817 prompts × 3 models = 2,451 samples) already cached from H-E1
- All reliability/robustness scores already computed in H-M1

---

## Functional Requirements

### FR-1: Data Loading and Stratification
**Priority:** MUST_HAVE
**Description:** Load cached evaluation data and stratify by prompt type
**Acceptance Criteria:**
- Load 817 TruthfulQA prompts with category metadata
- Stratify into factual (~400) vs. misinformation (~417) based on question category
- Load cached model outputs from H-E1 (3 model sizes: 7B, 13B, 70B)
- Load cached reliability/robustness scores from H-M1
- Verify sample sizes: n_factual ≥ 350, n_misinfo ≥ 350

**Dependencies:** H-E1 cached outputs, H-M1 cached scores

### FR-2: Correlation Computation per Stratum
**Priority:** MUST_HAVE
**Description:** Compute Pearson correlation between reliability and robustness for each stratum
**Acceptance Criteria:**
- Compute r_factual, p_factual on factual stratum samples
- Compute r_misinfo, p_misinfo on misinformation stratum samples
- Return correlation coefficients with 95% confidence intervals
- Validate against H-M1 result: r_factual ≈ 0.7233

**Dependencies:** FR-1

### FR-3: Fisher z-Test Implementation
**Priority:** MUST_HAVE
**Description:** Test significance of correlation difference using Fisher z-transformation
**Acceptance Criteria:**
- Transform correlations: z1 = arctanh(r_factual), z2 = arctanh(r_misinfo)
- Compute standard error: se_diff = sqrt(1/(n1-3) + 1/(n2-3))
- Compute test statistic: z_stat = (z1 - z2) / se_diff
- Compute two-tailed p-value from standard normal distribution
- Return: z_stat, p_value, significant (boolean)

**Dependencies:** FR-2

### FR-4: Effect Size Calculation
**Priority:** SHOULD_HAVE
**Description:** Quantify magnitude of correlation difference
**Acceptance Criteria:**
- Compute correlation difference: delta_r = r_factual - r_misinfo
- Compute Cohen's q effect size for correlation difference
- Classify effect size: small (q < 0.1), medium (0.1 ≤ q < 0.3), large (q ≥ 0.3)
- Return 95% CI for both correlations (Fisher z back-transform)

**Dependencies:** FR-2, FR-3

### FR-5: Visualization Generation
**Priority:** MUST_HAVE
**Description:** Generate publication-ready visualizations
**Acceptance Criteria:**
- **Figure 1 (Forest Plot):** Correlations per stratum with 95% CI error bars, r-values, p-values annotated
- **Figure 2 (Scatter Plots):** Side-by-side reliability vs. robustness for factual/misinformation strata, colored by model size, regression lines overlaid
- **Figure 3 (Gate Metrics):** Target vs. actual metrics bar chart (Fisher p-value, correlation difference)
- Save all figures to `{hypothesis_folder}/figures/`

**Dependencies:** FR-2, FR-3, FR-4

### FR-6: Validation Report Generation
**Priority:** MUST_HAVE
**Description:** Generate 04_validation.md with gate evaluation
**Acceptance Criteria:**
- Document Fisher z-test results (z_stat, p_value)
- Document correlation coefficients per stratum with 95% CI
- Evaluate SHOULD_WORK gate: p < 0.05, |delta_r| ≥ 0.1, directional pattern
- Report gate result: PASS/PARTIAL/FAIL
- Include all visualization references
- Save to `{hypothesis_folder}/04_validation.md`

**Dependencies:** FR-3, FR-4, FR-5

---

## Non-Functional Requirements

### NFR-1: Data Reuse
**Priority:** MUST_HAVE
**Description:** 100% reuse of cached outputs from H-E1/H-M1
**Metric:** Zero new model inference calls required

### NFR-2: Execution Speed
**Priority:** SHOULD_HAVE
**Description:** Fast statistical analysis (no model training)
**Metric:** Total runtime < 2 minutes (pure statistical computation)

### NFR-3: Reproducibility
**Priority:** MUST_HAVE
**Description:** Deterministic results for same cached inputs
**Metric:** Fixed random seed for any sampling operations, identical results across runs

### NFR-4: Statistical Validity
**Priority:** MUST_HAVE
**Description:** Correct application of Fisher z-test methodology
**Metric:** Implementation matches standard statistical references (Cohen & Cohen 1983)

---

## Data Requirements

### Input Data

#### Dataset: TruthfulQA (Stratified)
- **Source:** HuggingFace Datasets (`truthful_qa`, config: `generation`)
- **Total samples:** 817 prompts
- **Stratification variable:** Question category from dataset metadata
- **Factual stratum:** ~400 prompts (questions with factual ground truth)
- **Misinformation stratum:** ~417 prompts (questions testing common misconceptions)
- **Preprocessing:** None required (stratification only)

#### Cached Model Outputs (from H-E1)
- **Location:** H-E1 output directory
- **Format:** JSON/pickle containing model responses for all 817 prompts × 3 models
- **Models:** Llama-2-chat (7B, 13B, 70B)
- **Generation parameters:** temperature=0.7, top_p=0.9, max_tokens=256, seed_per_prompt=true

#### Cached Dimension Scores (from H-M1)
- **Location:** H-M1 output directory
- **Metrics:** Reliability (GPT-4-as-judge factual accuracy), Robustness (paraphrase consistency)
- **Format:** Aligned with model outputs (817 × 3 = 2,451 score pairs)

### Output Data

#### Correlation Results
- **Format:** JSON/YAML with r_factual, r_misinfo, p_factual, p_misinfo, CI_factual, CI_misinfo
- **Location:** `{hypothesis_folder}/correlation_results.json`

#### Statistical Test Results
- **Format:** JSON/YAML with z_stat, p_value, delta_r, cohens_q, significant (boolean)
- **Location:** `{hypothesis_folder}/fisher_test_results.json`

#### Figures
- **Format:** PNG (300 DPI) or SVG
- **Location:** `{hypothesis_folder}/figures/`
- **Files:** `forest_plot.png`, `scatter_comparison.png`, `gate_metrics.png`

---

## Dependencies

### External Dependencies
- **Python packages:** scipy, numpy, pandas, matplotlib, seaborn
- **Standard library:** json, pathlib

### Internal Dependencies
- **H-E1 outputs:** Model generations for all 817 prompts
- **H-M1 outputs:** Reliability and robustness scores aligned with generations
- **TruthfulQA metadata:** Category labels for stratification

### MCP Services
- **Archon:** Project and task management
- **Serena:** Not required (no codebase analysis needed for statistical workflow)

---

## Evaluation Metrics

### Primary Metrics

#### Fisher z-test p-value
- **Target:** p < 0.05 (SHOULD_WORK gate threshold)
- **Expected:** p < 0.001 (highly significant based on H-M1 supplementary results)
- **Measurement:** Two-tailed test from standard normal distribution

### Secondary Metrics

#### Correlation Difference Magnitude
- **Target:** |r_factual - r_misinfo| ≥ 0.1 (meaningful effect)
- **Expected:** 0.44 (based on r_factual=0.7233, r_misinfo≈0.28)
- **Measurement:** Absolute difference

#### Directional Pattern Validation
- **Target:** r_factual > 0.4 AND r_misinfo < 0.3
- **Expected:** r_factual ≈ 0.72, r_misinfo ≈ 0.28
- **Measurement:** Boolean check

### Tertiary Metrics

#### Effect Size (Cohen's q)
- **Target:** q ≥ 0.3 (large effect)
- **Measurement:** Cohen's q for correlation difference

#### Confidence Interval Non-Overlap
- **Target:** 95% CIs for r_factual and r_misinfo do not overlap
- **Measurement:** Boolean check on Fisher z back-transformed CIs

---

## Constraints and Assumptions

### Constraints
1. No new model inference allowed (100% data reuse)
2. Stratification based on TruthfulQA metadata categories
3. Must use H-M1 cached scores (not re-compute metrics)
4. Fisher z-test assumes independent samples per stratum

### Assumptions
1. TruthfulQA category labels accurately distinguish factual vs. misinformation prompts
2. H-M1 reliability/robustness scores are valid and correctly aligned with outputs
3. Factual and misinformation strata are independent (no prompt overlap)
4. Correlation coefficients are approximately normally distributed after Fisher z-transformation

### Risks
1. **Sample size imbalance:** Factual and misinformation strata may have unequal sizes
   - **Mitigation:** Fisher z-test accounts for unequal sample sizes via standard error formula
2. **Category labeling ambiguity:** Some prompts may not clearly fit factual vs. misinformation
   - **Mitigation:** Use TruthfulQA official category labels; document any ambiguous cases
3. **Dependency violation:** Samples not independent if same prompt appears in both strata
   - **Mitigation:** Verify stratification produces disjoint sets

---

## Success Criteria

### Gate Evaluation (SHOULD_WORK)

#### PASS Conditions
1. Fisher z-test p < 0.05 (significant correlation difference)
2. |r_factual - r_misinfo| ≥ 0.1 (meaningful effect magnitude)
3. r_factual > 0.4 AND r_misinfo < 0.3 (directional pattern matches theory)

#### PARTIAL Conditions
1. Fisher z-test p < 0.10 (marginal significance) OR
2. |r_factual - r_misinfo| ≥ 0.08 (near-meaningful effect) OR
3. One directional criterion met but not both

#### FAIL Conditions
1. Fisher z-test p ≥ 0.10 (no significant difference)
2. |r_factual - r_misinfo| < 0.08 (negligible effect)
3. Directional pattern reversed (r_factual < r_misinfo)

### Deliverables Checklist
- [ ] `correlation_results.json` with per-stratum correlations and CIs
- [ ] `fisher_test_results.json` with test statistic, p-value, effect size
- [ ] `figures/forest_plot.png` - Correlation comparison with error bars
- [ ] `figures/scatter_comparison.png` - Side-by-side reliability vs. robustness
- [ ] `figures/gate_metrics.png` - Target vs. actual gate metrics
- [ ] `04_validation.md` - Gate evaluation report with results summary

---

## Implementation Notes

### Pseudo-code Reference (from Phase 2C)
```python
def test_correlation_difference(r1, n1, r2, n2, alpha=0.05):
    """Compare two independent correlations using Fisher z-test."""
    import numpy as np
    from scipy import stats
    
    # Fisher z-transformation
    z1 = np.arctanh(r1)
    z2 = np.arctanh(r2)
    
    # Standard error of difference
    se_diff = np.sqrt(1/(n1-3) + 1/(n2-3))
    
    # Test statistic
    z_stat = (z1 - z2) / se_diff
    
    # Two-tailed p-value
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
    
    significant = p_value < alpha
    
    return z_stat, p_value, significant
```

### Data Flow
1. Load TruthfulQA metadata → Stratify by category
2. Load H-E1 cached outputs → Filter by stratum
3. Load H-M1 cached scores → Filter by stratum
4. Compute r_factual, r_misinfo → Pearson correlation per stratum
5. Apply Fisher z-test → Test significance
6. Generate visualizations → Save to figures/
7. Evaluate gate criteria → Write 04_validation.md

### Expected Runtime
- Stratification: < 1 second
- Correlation computation: < 5 seconds
- Fisher z-test: < 1 second
- Visualization: < 30 seconds
- **Total:** < 1 minute

---

## Appendix: Phase 2C Completeness Checklist

### Dataset Coverage
- [x] TruthfulQA (stratified: factual vs. misinformation)
- [x] Cached outputs from H-E1
- [x] Cached scores from H-M1

### Model Coverage
- [x] Llama-2-chat (7B, 13B, 70B) - All outputs cached

### Metric Coverage
- [x] Fisher z-test p-value (primary)
- [x] Correlation difference magnitude (secondary)
- [x] Directional pattern validation (tertiary)
- [x] Effect size (Cohen's q)
- [x] Confidence intervals

### Visualization Coverage
- [x] Forest plot (correlations with CI)
- [x] Scatter plots (reliability vs. robustness per stratum)
- [x] Gate metrics bar chart

### Ablation/Variant Coverage
- N/A - No ablation variants required for statistical hypothesis test

---

**Document Status:** COMPLETE
**Next Phase:** Phase 3 - Architecture Design (Step 3)
