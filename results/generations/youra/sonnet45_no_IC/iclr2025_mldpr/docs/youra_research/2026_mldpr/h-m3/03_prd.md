# Product Requirements Document (PRD): H-M3 - Performance Variance Analysis

**Version:** 1.0  
**Date:** 2026-07-12  
**Author:** anonymous@anonymous.org  
**Hypothesis:** H-M3 (MECHANISM)  
**Gate Type:** SHOULD_WORK

---

## Executive Summary

This PRD defines requirements for implementing an observational meta-analysis study that validates the causal mechanism: reduced cross-lab protocol ambiguity (via documentation artifacts) leads to lower performance variance across independent ML reproduction attempts.

**Success Criteria:** Statistical evidence (Mann-Whitney p<0.05, Cohen's d>0.5) showing high-artifact benchmarks exhibit lower coefficient of variation (CV) than low-artifact benchmarks.

---

## Problem Statement

### Background
- **H-M1 (PASS):** Documentation artifacts provide implementation details (Quality: 8.30/10, Kappa: 1.000)
- **H-M2 (PASS):** Implementation details reduce cross-lab ambiguity (Spearman ρ=0.711, p=0.021)
- **H-M3 (Current):** Need to validate final causal link: ambiguity reduction → performance variance reduction

### Research Question
Does reduced protocol ambiguity (via artifact quality) lead to measurably lower performance variance across independent reproduction attempts?

### Scope
- **Dataset:** Papers with Code benchmark database (2019-2024, classification tasks)
- **Sample:** 100 benchmarks (50 high-artifact ≥2, 50 low-artifact <2)
- **Method:** Quasi-experimental observational study with propensity weighting
- **Timeline:** Phase 3 → Phase 4 implementation

---

## Functional Requirements

### FR-1: Data Collection Module
**Priority:** P0 (MUST_WORK)  
**Description:** Collect benchmark metadata and performance results from Papers with Code API

**Acceptance Criteria:**
- Query Papers with Code API v1 for classification benchmarks (2019-2024)
- Filter benchmarks with ≥5 reported results
- Extract artifact metadata: GitHub repo, dataset card, badge (binary 0/1 each)
- Collect performance metrics (accuracy OR F1, standardized per benchmark)
- Target: 100 benchmarks (50 high-artifact ≥2, 50 low-artifact <2)

**Dependencies:**
- Papers with Code API v1 (https://paperswithcode.com/api/v1/)
- requests library for HTTP calls
- pandas for data manipulation

**Test Cases:**
- TC1.1: API returns benchmarks with task="classification"
- TC1.2: Date filter excludes benchmarks outside 2019-2024
- TC1.3: Result count filter retains only benchmarks with ≥5 results
- TC1.4: Artifact coding matches H-M1 validated rubric

---

### FR-2: Artifact Quality Assessment
**Priority:** P0 (MUST_WORK)  
**Description:** Binary artifact coding using H-M1 validated quality rubric

**Acceptance Criteria:**
- GitHub repository presence: Binary (0/1)
- Dataset card presence: Binary (0/1)
- Reproducibility badge: Binary (0/1)
- Artifact count: Sum of above (0-3)
- Group assignment: High (≥2) vs Low (<2)
- Manual verification of artifact quality (not empty repos)

**Dependencies:**
- H-M1 artifact quality rubric (Kappa=1.0 validated)
- Manual verification step for quality control

**Test Cases:**
- TC2.1: Artifact count correctly sums binary indicators
- TC2.2: Group assignment threshold at ≥2 artifacts
- TC2.3: Manual verification flags empty or boilerplate artifacts

---

### FR-3: Performance Variance Calculation
**Priority:** P0 (MUST_WORK)  
**Description:** Compute coefficient of variation (CV) per benchmark

**Acceptance Criteria:**
- Extract all reported results per benchmark
- Filter outliers: Remove results >3 SD from benchmark mean
- Compute CV = σ/μ per benchmark
- Validate: Minimum 5 results post-filtering
- Output: CV distribution per artifact group

**Dependencies:**
- numpy for statistical calculations
- pandas for data manipulation

**Test Cases:**
- TC3.1: Outlier filter removes results >3 SD
- TC3.2: CV calculation uses standard deviation / mean
- TC3.3: Benchmarks with <5 results excluded post-filtering

---

### FR-4: Confound Variable Collection
**Priority:** P1 (SHOULD_WORK)  
**Description:** Collect confounding variables for propensity score weighting

**Acceptance Criteria:**
- Benchmark age (years since publication)
- Task domain (CV, NLP, Speech, etc.)
- Metric type (accuracy vs F1)
- Venue prestige (if available via Semantic Scholar API)

**Dependencies:**
- Papers with Code API for metadata
- Optional: Semantic Scholar API for venue prestige

**Test Cases:**
- TC4.1: Benchmark age correctly computed from publication year
- TC4.2: Task domain extracted from Papers with Code taxonomy
- TC4.3: Metric type standardized (accuracy/F1)

---

### FR-5: Statistical Analysis - Mann-Whitney U Test
**Priority:** P0 (MUST_WORK)  
**Description:** Primary hypothesis test comparing CV distributions

**Acceptance Criteria:**
- Null hypothesis: No difference in CV between groups
- Alternative: CV_high < CV_low (one-tailed)
- Significance level: α = 0.05
- Output: test statistic, p-value
- **Pass condition:** p < 0.05

**Dependencies:**
- scipy.stats.mannwhitneyu

**Test Cases:**
- TC5.1: One-tailed test (alternative='less')
- TC5.2: Input validation (two groups, non-empty)
- TC5.3: Output includes statistic and p-value

---

### FR-6: Effect Size - Cohen's d
**Priority:** P0 (MUST_WORK)  
**Description:** Primary effect size metric

**Acceptance Criteria:**
- Formula: d = (μ_low - μ_high) / σ_pooled
- Pooled SD: sqrt((σ_high² + σ_low²) / 2)
- Interpretation: d>0.5 = medium effect
- **Pass condition:** d > 0.5

**Dependencies:**
- numpy for statistical calculations

**Test Cases:**
- TC6.1: Cohen's d correctly computed with pooled SD
- TC6.2: Sign indicates direction (positive = low > high)
- TC6.3: Interpretation thresholds (0.2/0.5/0.8)

---

### FR-7: Dose-Response Analysis - Spearman Correlation
**Priority:** P1 (SECONDARY)  
**Description:** Secondary analysis for dose-response relationship

**Acceptance Criteria:**
- Correlation: artifact count (0-3) vs CV
- Target: ρ < -0.3 (negative correlation)
- Significance: p < 0.05
- Interpretation: More artifacts → lower variance

**Dependencies:**
- scipy.stats.spearmanr

**Test Cases:**
- TC7.1: Spearman correlation handles ordinal artifact count
- TC7.2: Negative ρ indicates inverse relationship
- TC7.3: p-value tests statistical significance

---

### FR-8: Propensity Score Weighting (Conditional)
**Priority:** P2 (OPTIONAL)  
**Description:** Correct sampling bias if detected (>10% coverage difference)

**Acceptance Criteria:**
- Trigger: Coverage difference >10% between groups
- Propensity model: Logistic regression on confounds
- Inverse probability weighting
- Bootstrapped weighted Mann-Whitney test
- Output: Weighted effect size

**Dependencies:**
- sklearn.linear_model.LogisticRegression
- numpy for bootstrap resampling

**Test Cases:**
- TC8.1: Trigger only when coverage diff >10%
- TC8.2: Propensity scores sum to 1.0
- TC8.3: Weighted test produces valid p-value

---

### FR-9: Visualization - CV Distribution Comparison
**Priority:** P0 (MUST_WORK)  
**Description:** Box plot + violin plot showing CV distributions

**Acceptance Criteria:**
- Box plot overlay with violin plot
- Two groups: High-artifact (≥2) vs Low-artifact (<2)
- Median, quartiles, outliers visible
- Legend and axis labels clear

**Dependencies:**
- matplotlib or seaborn

**Test Cases:**
- TC9.1: Two groups displayed side-by-side
- TC9.2: Median lines visible in box plots
- TC9.3: Saved to {hypothesis_folder}/figures/

---

### FR-10: Visualization - Dose-Response Scatter
**Priority:** P1 (SECONDARY)  
**Description:** Scatter plot showing artifact count vs CV correlation

**Acceptance Criteria:**
- X-axis: Artifact count (0-3)
- Y-axis: CV values
- Regression line with Spearman ρ annotation
- Color by domain (if applicable)

**Dependencies:**
- matplotlib or seaborn

**Test Cases:**
- TC10.1: Scatter points plotted correctly
- TC10.2: Regression line overlayed
- TC10.3: Spearman ρ and p-value annotated

---

### FR-11: Gate Metrics Visualization (Mandatory)
**Priority:** P0 (MUST_WORK)  
**Description:** Bar chart comparing actual vs threshold for pass/fail

**Acceptance Criteria:**
- Two bars: [Actual p-value vs α=0.05], [Actual d vs target d=0.5]
- Pass/Fail color coding (green/red)
- Clear threshold lines

**Dependencies:**
- matplotlib

**Test Cases:**
- TC11.1: Actual metrics displayed with thresholds
- TC11.2: Pass/Fail color coding correct
- TC11.3: Saved to {hypothesis_folder}/figures/gate_metrics.png

---

### FR-12: Validation Report Generation
**Priority:** P0 (MUST_WORK)  
**Description:** Generate 04_validation.md with results and gate check

**Acceptance Criteria:**
- Include Mann-Whitney p-value
- Include Cohen's d effect size
- Include Spearman ρ (secondary)
- Gate status: PASS/FAIL based on p<0.05 AND d>0.5
- Figures embedded or linked

**Dependencies:**
- File I/O for markdown generation

**Test Cases:**
- TC12.1: All metrics present in report
- TC12.2: Gate logic correctly evaluates PASS/FAIL
- TC12.3: File saved to {hypothesis_folder}/04_validation.md

---

## Non-Functional Requirements

### NFR-1: Performance
- Data collection completes within 10 minutes (API rate limits considered)
- Statistical analysis completes within 2 minutes
- Total runtime: <15 minutes

### NFR-2: Reliability
- Handle API rate limits gracefully (retry with exponential backoff)
- Validate data quality at each stage
- Minimum 5 results per benchmark enforced

### NFR-3: Reproducibility
- Random seed fixed for bootstrap (if propensity weighting used)
- All data collection parameters logged
- Analysis script outputs reproducible results

### NFR-4: Code Quality
- Type hints for all functions
- Docstrings for statistical methods
- Unit tests for statistical calculations
- Integration test for full pipeline

### NFR-5: Documentation
- README with setup instructions
- API usage examples
- Statistical method references

---

## Data Requirements

### DR-1: Papers with Code Benchmark Database
**Source:** https://paperswithcode.com/api/v1/  
**Access:** Public API (no authentication required)  
**Format:** JSON  
**Fields Required:**
- Benchmark ID
- Benchmark name
- Task type (classification)
- Publication date
- Result count
- Performance metrics (accuracy/F1)
- Artifact metadata (GitHub, dataset card, badge)

**Volume:** 100 benchmarks (target), 500+ results total

### DR-2: Static Baselines
**Description:** No external model baselines required (meta-analysis of existing data)

### DR-3: Confound Variables
**Source:** Papers with Code API + Semantic Scholar (optional)  
**Fields:**
- Benchmark age (derived from publication_date)
- Task domain (from taxonomy)
- Metric type (accuracy/F1)
- Venue prestige (optional, from Semantic Scholar)

---

## Dependencies

### External Dependencies
- Papers with Code API v1 (public, no auth)
- scipy (statistical tests)
- numpy (numerical operations)
- pandas (data manipulation)
- matplotlib/seaborn (visualization)
- requests (HTTP client)

### Optional Dependencies
- sklearn (propensity score weighting, if needed)
- Semantic Scholar API (venue prestige, optional)

### Prerequisite Hypotheses
- **H-M1 (COMPLETED):** Artifact quality rubric validated (Kappa=1.0)
- **H-M2 (COMPLETED):** Ambiguity reduction validated (Spearman ρ=0.711)

---

## Success Criteria

### Primary Criteria (PoC Gate: SHOULD_WORK)
1. **Mann-Whitney U Test:** p < 0.05
2. **Cohen's d Effect Size:** d > 0.5 (medium effect)

### Secondary Criteria
3. **Spearman ρ (Dose-Response):** ρ < -0.3 AND p < 0.05

### Gate Logic
```python
gate_pass = (mann_whitney_p < 0.05) AND (cohens_d > 0.5)
```

**If FAIL:** EXPLORE alternative explanations (venue prestige, author reputation as confounds)

---

## Out of Scope

- Model training (observational study, not implementation experiment)
- Neural network code analysis (statistical analysis only)
- Complex ML architectures (standard scipy/pandas libraries sufficient)
- Real-time data collection (batch API queries)

---

## Risk Assessment

### R1: Sampling Bias (Medium Risk)
**Description:** Papers with Code may overrepresent high-artifact papers  
**Mitigation:** Propensity score weighting (FR-8) if coverage difference >10%

### R2: API Rate Limiting (Low Risk)
**Description:** Papers with Code API may throttle requests  
**Mitigation:** Exponential backoff retry, batch requests

### R3: Insufficient Sample Size (Low Risk)
**Description:** <100 benchmarks meeting criteria  
**Mitigation:** H-E1 validated 150 benchmarks available ✓

### R4: Outlier Contamination (Medium Risk)
**Description:** Extreme performance results inflate CV  
**Mitigation:** >3 SD outlier filter (FR-3)

---

## Appendix: Reference Implementations

### Archon Knowledge Base
1. **PyTorch Reproducibility Documentation** (https://pytorch.org/docs/stable/notes/randomness.html)
2. **arXiv 2312.00858** - ML Benchmark Meta-Analysis
3. **arXiv 2303.08084** - Reproducibility Study

### Statistical Methods
4. **scipy.stats.mannwhitneyu** - Non-parametric test
5. **Cohen's d** - Effect size calculation
6. **Propensity Score Weighting** - Rosenbaum & Rubin (1983)

### Previous Hypotheses
7. **H-M1:** Artifact quality assessment (Quality: 8.30/10, Kappa: 1.000)
8. **H-M2:** Ambiguity reduction (Spearman ρ=0.711, p=0.021)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-12 | Initial PRD generated from Phase 2C experiment brief |

---

**Next Phase:** Step 3 - Architecture Agent (Epic task breakdown)
