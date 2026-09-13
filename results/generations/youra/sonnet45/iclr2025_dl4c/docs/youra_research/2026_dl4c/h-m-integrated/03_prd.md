# Product Requirements Document: H-M-integrated

**Hypothesis ID:** H-M-integrated
**Type:** MECHANISM
**Date:** 2026-03-18
**Author:** Phase 3 Implementation Planning

---

## Executive Summary

This PRD defines requirements for implementing H-M-integrated, a mechanistic analysis testing the causal explanation for alignment method objective function signatures observed in H-E1. The experiment performs post-hoc statistical analysis on H-E1 profiling results to validate three mechanistic predictions: (M1) execution-focused models dominate correctness dimension (top 15% pass@k rank), (M2) preference-focused models show balanced performance (top 30% across all dimensions), and (M3) training dynamics create consistent within-method clustering (intracluster variance < intercluster distance).

**Core Question:** WHY do alignment methods produce detectable signatures? Does feedback signal theory (models optimize what they're trained on) explain the clustering patterns?

**Success Criteria:** M1 AND M2 must pass (MUST_WORK gate). M3 should pass for complete mechanistic validation.

---

## Problem Statement

### Context
H-E1 successfully demonstrated that alignment methods create distinguishable performance clusters (Cohen's d = 7.835). However, EXISTENCE proof alone doesn't explain WHY clustering occurs. Understanding the mechanistic explanation is critical for:
1. Validating the feedback signal theory (implicit optimization during alignment)
2. Predicting model behavior from alignment method choice
3. Designing targeted alignment strategies for specific objectives

### Hypothesis Statement
If alignment methods shape model output distributions through implicit optimization (3-step causal chain: feedback signal selection → repeated training exposure → observable signatures), then we will observe: (M1) execution-focused models dominate correctness dimension (top 15% pass@k rank), (M2) preference-focused models show balanced performance (top 30% across all dimensions), (M3) training dynamics create consistent within-method clustering (intracluster variance < intercluster distance), because feedback signals define what models optimize during alignment training.

### Gate Condition
**MUST_WORK**: M1 AND M2 must both pass. If either fails:
- M1 failure → EXPLORE: Check if baseline model differences explain clustering
- M2 failure → PIVOT: Revise feedback signal theory
- M3 failure → ABANDON: Clustering is noise, not signal

---

## Functional Requirements

### FR-1: Load H-E1 Profiling Results
**Priority:** CRITICAL
**Complexity:** Low

Load existing profiling results from H-E1 experiment (correctness, complexity, efficiency metrics for 4 models).

**Acceptance Criteria:**
- Read profiling data from `/docs/youra_research/20260317_dl4c/h-e1/` output artifacts
- Data structure: {model_name: {correctness: float, complexity: float, efficiency: float, alignment_method: str}}
- Models: microsoft/phi-2 (execution), Salesforce/codegen-350M-mono (preference), Salesforce/codegen-350M-nl (baseline), microsoft/CodeGPT-small-py (baseline)
- Alignment method labels applied according to H-E1 classification

**Dependencies:** H-E1 completion (validation.status = COMPLETED)

---

### FR-2: Compute Percentile Rankings
**Priority:** CRITICAL
**Complexity:** Medium

Compute percentile rank for each model on each dimension (correctness, complexity, efficiency).

**Acceptance Criteria:**
- Use `scipy.stats.percentileofscore` for ranking
- Ranking method: 'rank' (lower percentile = better performance)
- Dimensions: correctness (pass@k), complexity (cyclomatic + AST depth), efficiency (runtime + memory)
- Output: Percentile rank per model per dimension (0-100 scale)
- Lower percentile = higher rank (top 15% = ≤15th percentile)

**Dependencies:** FR-1 (data loaded)

**Implementation Pattern:**
```python
from scipy.stats import percentileofscore

def compute_percentile_ranks(data: Dict, dimensions: List[str]) -> Dict:
    """Compute percentile rank for each model on each dimension."""
    ranks = {}
    for dim in dimensions:
        scores = [data[m][dim] for m in data]
        for model in data:
            score = data[model][dim]
            percentile = percentileofscore(scores, score, kind='rank')
            ranks.setdefault(model, {})[dim] = percentile
    return ranks
```

---

### FR-3: Test M1 - Execution Dominance
**Priority:** CRITICAL
**Complexity:** Medium

Validate that execution-focused models dominate correctness dimension (top 15% percentile rank).

**Acceptance Criteria:**
- Filter models by alignment_method == "execution"
- Compute mean correctness percentile rank across execution models
- Success condition: mean_rank ≤ 15.0 (top 15%)
- Store M1 pass/fail result for gate validation

**Dependencies:** FR-2 (rankings computed)

**Implementation Pattern:**
```python
def test_m1_execution_dominance(data: Dict, ranks: Dict) -> tuple:
    """M1: Execution models dominate correctness (top 15%)."""
    execution_models = [m for m in data if data[m]["alignment_method"] == "execution"]
    mean_correctness_rank = np.mean([ranks[m]["correctness"] for m in execution_models])
    passed = mean_correctness_rank <= 15.0
    return passed, mean_correctness_rank
```

---

### FR-4: Test M2 - Preference Balance
**Priority:** CRITICAL
**Complexity:** Medium

Validate that preference-focused models show balanced performance across all three dimensions (top 30% mean rank).

**Acceptance Criteria:**
- Filter models by alignment_method == "preference"
- Compute mean rank across correctness, complexity, efficiency for each preference model
- Compute overall mean across all preference models
- Success condition: overall_mean ≤ 30.0 (top 30% balanced performance)
- Store M2 pass/fail result for gate validation

**Dependencies:** FR-2 (rankings computed)

**Implementation Pattern:**
```python
def test_m2_preference_balance(data: Dict, ranks: Dict, dimensions: List[str]) -> tuple:
    """M2: Preference models balanced across dimensions (top 30%)."""
    preference_models = [m for m in data if data[m]["alignment_method"] == "preference"]
    mean_ranks = [np.mean([ranks[m][dim] for dim in dimensions]) for m in preference_models]
    overall_mean = np.mean(mean_ranks)
    passed = overall_mean <= 30.0
    return passed, overall_mean
```

---

### FR-5: Test M3 - Clustering Consistency
**Priority:** HIGH
**Complexity:** Medium

Validate that within-method variance < between-method variance using statistical testing.

**Acceptance Criteria:**
- Group scores by alignment method (execution, preference, baseline)
- Apply Mann-Whitney U test comparing method groups
- Test statistic: p-value < 0.05 indicates significant separation
- Success condition: p < 0.05 (statistically significant clustering)
- Store M3 pass/fail result and p-value

**Dependencies:** FR-1 (data loaded)

**Implementation Pattern:**
```python
from scipy.stats import mannwhitneyu

def test_m3_clustering_consistency(data: Dict) -> tuple:
    """M3: Within-method variance < between-method variance (p<0.05)."""
    # Group correctness scores by alignment method
    method_groups = {}
    for model, model_data in data.items():
        method = model_data["alignment_method"]
        method_groups.setdefault(method, []).append(model_data["correctness"])

    # Mann-Whitney U test between first two method groups
    methods = list(method_groups.keys())
    if len(methods) < 2:
        return False, 1.0

    stat, pvalue = mannwhitneyu(
        method_groups[methods[0]],
        method_groups[methods[1]],
        alternative='two-sided'
    )
    passed = pvalue < 0.05
    return passed, pvalue
```

---

### FR-6: Gate Validation
**Priority:** CRITICAL
**Complexity:** Low

Evaluate MUST_WORK gate condition: M1 AND M2 must both pass.

**Acceptance Criteria:**
- Primary gate: M1_passed AND M2_passed
- Secondary check: M3_passed (clustering consistency)
- Overall success: All three mechanisms validated
- Gate result stored for verification_state.yaml update

**Dependencies:** FR-3, FR-4, FR-5 (all tests complete)

---

### FR-7: Results Logging
**Priority:** HIGH
**Complexity:** Low

Log all test results, metrics, and gate validation outcomes.

**Acceptance Criteria:**
- M1 result: {passed: bool, mean_correctness_rank: float, threshold: 15.0}
- M2 result: {passed: bool, overall_mean_rank: float, threshold: 30.0}
- M3 result: {passed: bool, pvalue: float, threshold: 0.05}
- Gate result: {M1_passed: bool, M2_passed: bool, M3_passed: bool, overall: bool}
- All results saved to validation report (04_validation.md)

**Dependencies:** FR-6 (gate validated)

---

### FR-8: Visualization - Dimension-wise Rankings
**Priority:** HIGH
**Complexity:** Medium

Generate bar chart showing percentile ranks for each model across three dimensions.

**Acceptance Criteria:**
- X-axis: Model names (grouped by alignment method)
- Y-axis: Percentile rank (0-100)
- Three bars per model (correctness, complexity, efficiency)
- Color coding: execution (blue), preference (green), baseline (gray)
- Horizontal lines at 15th and 30th percentiles for reference
- Saved to `{hypothesis_folder}/figures/dimension_rankings.png`

**Dependencies:** FR-2 (rankings computed)

---

### FR-9: Visualization - M1 Validation Plot
**Priority:** HIGH
**Complexity:** Medium

Generate visualization showing execution models' correctness ranks with 15th percentile threshold.

**Acceptance Criteria:**
- Plot type: Horizontal bar chart
- X-axis: Correctness percentile rank
- Y-axis: Execution model names
- Vertical line at 15th percentile threshold
- Pass/fail annotation for M1 condition
- Saved to `{hypothesis_folder}/figures/m1_execution_dominance.png`

**Dependencies:** FR-3 (M1 tested)

---

### FR-10: Visualization - M2 Validation Plot
**Priority:** HIGH
**Complexity:** Medium

Generate visualization showing preference models' balanced performance across dimensions.

**Acceptance Criteria:**
- Plot type: Grouped bar chart or spider plot
- Axes: Three dimensions (correctness, complexity, efficiency)
- One trace per preference model
- Horizontal line at 30th percentile threshold
- Mean rank annotation
- Saved to `{hypothesis_folder}/figures/m2_preference_balance.png`

**Dependencies:** FR-4 (M2 tested)

---

### FR-11: Visualization - M3 Variance Analysis
**Priority:** HIGH
**Complexity:** Medium

Generate box plots showing within-method vs between-method score distributions.

**Acceptance Criteria:**
- Plot type: Box plots
- X-axis: Alignment method groups (execution, preference, baseline)
- Y-axis: Correctness scores
- Statistical annotation: Mann-Whitney U p-value
- Saved to `{hypothesis_folder}/figures/m3_variance_analysis.png`

**Dependencies:** FR-5 (M3 tested)

---

### FR-12: Validation Report Generation
**Priority:** CRITICAL
**Complexity:** Low

Generate comprehensive validation report (04_validation.md) with all results and visualizations.

**Acceptance Criteria:**
- Report structure: Executive Summary, Methodology, Results (M1/M2/M3), Gate Validation, Figures
- All test results included with metrics and thresholds
- Gate pass/fail clearly stated
- Figures embedded or referenced
- Lessons learned section for failure cases

**Dependencies:** FR-3, FR-4, FR-5, FR-6, FR-8, FR-9, FR-10, FR-11 (all tests and visualizations complete)

---

## Non-Functional Requirements

### NFR-1: Data Reuse
**Priority:** CRITICAL

Reuse H-E1 profiling results without re-running model inference.

**Acceptance Criteria:**
- No new model loading or inference required
- All data loaded from H-E1 artifacts
- Execution time: < 5 minutes (statistical analysis only)

---

### NFR-2: Statistical Rigor
**Priority:** HIGH

Use established statistical methods with appropriate libraries.

**Acceptance Criteria:**
- `scipy.stats.percentileofscore` for ranking
- `scipy.stats.mannwhitneyu` for variance testing
- `numpy` for mean/variance calculations
- Reproducible results (fixed random seeds where applicable)

---

### NFR-3: Failure Diagnostics
**Priority:** HIGH

Provide detailed diagnostics for gate failures to inform routing decisions.

**Acceptance Criteria:**
- If M1 fails: Report which execution models failed to dominate, suggest exploring baseline model differences
- If M2 fails: Report preference model imbalance patterns, suggest revising feedback signal theory
- If M3 fails: Report high intracluster variance metrics, suggest noise hypothesis
- All diagnostics included in validation report

---

## Success Criteria

### Primary Success (Gate Pass)
1. M1 passes: Execution models' mean correctness rank ≤ 15th percentile
2. M2 passes: Preference models' mean rank ≤ 30th percentile across all dimensions

### Secondary Success (Complete Validation)
3. M3 passes: Within-method variance < between-method variance (p < 0.05)

### Deliverables
- 04_validation.md report with all results
- 4 visualization figures (dimension rankings, M1, M2, M3)
- Gate validation result for verification_state.yaml update

---

## Dependencies

### Prerequisites
- H-E1 validation completed (status = COMPLETED, gate.satisfied = true)
- H-E1 profiling results available in `/docs/youra_research/20260317_dl4c/h-e1/`

### External Dependencies
- Python libraries: scipy, numpy, matplotlib
- H-E1 data artifacts (no regeneration)

---

## Risk Assessment

### Risk 1: H-E1 Data Format Changes
**Likelihood:** Low
**Impact:** High
**Mitigation:** Verify data schema before analysis, implement schema validation

### Risk 2: Insufficient Model Diversity
**Likelihood:** Medium (only 4 models from H-E1)
**Impact:** Medium
**Mitigation:** Small sample size acceptable for PoC; percentile rankings still valid

### Risk 3: Statistical Power
**Likelihood:** Medium
**Impact:** Medium
**Mitigation:** Use non-parametric tests (Mann-Whitney U) robust to small samples

---

## Phase 4 Implementation Notes

### Complexity Tier: FULL (MECHANISM hypothesis)
- Budget: 30 tasks maximum
- Epic range: 6-12 tasks
- Infrastructure: Standard (YAML config, structured logging, unit tests)

### Key Implementation Guidance
1. **Data Loading**: Read H-E1 profiling results from standardized JSON or CSV format
2. **Statistical Libraries**: Use scipy.stats for all statistical operations
3. **Visualization**: matplotlib for all plots, consistent style across figures
4. **Gate Validation**: Clear boolean checks for M1, M2, M3 with detailed logging

### Code Reuse from H-E1
- Data loader structure (if H-E1 saved intermediate results)
- Visualization utilities (plotting style, figure saving)
- Configuration management patterns

---

*Generated by Phase 3 Implementation Planning*
*Based on Phase 2C Experiment Design (02c_experiment_brief.md)*
