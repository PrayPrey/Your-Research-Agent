# H-M3 Hypothesis Context

**Generated:** 2026-07-12
**Source:** Phase 2B Verification Plan (02b_verification_plan.md)

---

## Hypothesis Information

**ID:** H-M3
**Type:** MECHANISM
**Statement:** Under the scope of classification benchmarks, if cross-lab protocol ambiguity is low (high consistency), then performance variance (CV) is lower because consistent implementations reduce measurement noise across independent attempts.

**Rationale:** This hypothesis validates the final causal link—that ambiguity reduction translates to outcome consistency. This is the primary mechanism test linking artifacts to reproducibility.

---

## Variables

- **Independent:** Documentation artifact count (≥2 vs <2)
- **Dependent:** Performance variance (coefficient of variation = σ/μ)
- **Controlled:** Benchmark age, task domain, metric type

---

## Verification Protocol (from Phase 2B)

1. Sample 100 classification benchmarks (50 high-artifact ≥2, 50 low-artifact <2)
2. Compute CV for each benchmark from reported results (minimum 5 results required)
3. Apply propensity score weighting for sampling bias correction (if coverage differs >10%)
4. Conduct Mann-Whitney U test comparing CV distributions (two-tailed, α=0.05)
5. Calculate Cohen's d effect size (target: d>0.5 medium effect)

---

## Success Criteria (PoC: Direction-based)

- **Primary:** Mann-Whitney p<0.05 AND Cohen's d >0.5 (medium effect size)
- **Secondary:** Spearman ρ<-0.3 for dose-response (artifact count 0→1→2→3 correlates with decreasing CV)

---

## Gate Condition

**Type:** SHOULD_WORK

**If Fail:** EXPLORE alternative explanations (venue prestige, author reputation as confounds)

---

## Prerequisites

**Required:** H-M2 (Implementation details reduce cross-lab ambiguity)

**Dependency Chain:** H-E1 → H-M1 → H-M2 → H-M3

---

## Experimental Setup (from Phase 2A)

### Dataset
- **Source:** Papers with Code Benchmark Results Database (standard)
- **Scope:** Classification benchmarks published 2019-2024
- **API:** https://paperswithcode.com/api/v1/
- **Justification:** Provides 4000+ benchmarks with aggregated results from independent groups, enabling variance calculation at scale

### Model/Framework
- **Type:** Meta-Analysis Statistical Framework
- **Approach:** Observational study with quasi-experimental design
- **Method:** Cross-sectional comparison + propensity score weighting for sampling bias correction

---

## Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| FAIR principles compliance (Gim et al. 2025) | 5% Findable, 0% Reusable in medical imaging datasets | AMD imaging datasets |
| Croissant-RAI metadata format (Jain et al. 2024) | Proposes standard format, 10 citations | General ML datasets |
| Reproducibility barriers framework (Semmelrock et al. 2024) | Comprehensive taxonomy, 101 citations | Survey across ML fields |

---

## Previous Hypothesis Results

### H-E1 (Benchmark Sample Sufficiency)
- **Status:** COMPLETED (PASS)
- **Result:** 150 benchmarks with ≥5 results found (exceeds threshold of 100)
- **Gate:** MUST_WORK ✓

### H-M1 (Documentation Artifacts Provide Details)
- **Status:** COMPLETED (PASS)
- **Result:** Artifact quality score 8.30/10, Inter-rater kappa: 1.000
- **Gate:** MUST_WORK ✓
- **Finding:** Documentation artifacts are informative, not boilerplate

### H-M2 (Details Reduce Ambiguity)
- **Status:** COMPLETED (PASS)
- **Result:** Spearman ρ=0.711, p=0.021 (protocol consistency correlates with artifact quality)
- **Gate:** SHOULD_WORK ✓
- **Finding:** Higher artifact quality → higher protocol consistency (67% consistency achieved)

---

## Key Assumptions for H-M3

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Papers with Code includes benchmarks representatively | Coverage validation needed | Sampling bias inflates effect size |
| A2 | Performance variance (CV) is valid reproducibility proxy | Lower variance indicates procedural consistency | Variance measures noise, not reproducibility |
| A5 | Classification tasks have standardized metrics | Scope restricted to classification tasks | Metric heterogeneity inflates variance artificially |

---

## Risk Analysis for H-M3

| Risk | Source | Severity | Mitigation |
|------|--------|----------|------------|
| R1: Sampling bias | A1 | High | Coverage validation + propensity weighting |
| R2: Variance ≠ validity | A2 | Medium | Frame as consistency, not correctness |
| R5: Metric heterogeneity | A5 | Medium | Stratify by metric type |

---

## Expected Timeline

**Duration:** 1 week (5 FTE-days)
**Position:** Week 5 of 5-week verification plan
**Critical Path:** Final hypothesis test (determines success)

---

*This context file provides experiment design guidance for Phase 2C.*
*Source: 02b_verification_plan.md, verification_state.yaml*
