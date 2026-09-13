# Verification Plan: Benchmark Concentration and Epistemic Lock-in in ML Research

**Date:** 2026-08-10
**Hypothesis ID:** H-BenchmarkConcentration-v1
**Confidence:** 0.75
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under conditions of high benchmark dataset concentration (HHI > venue median) in major ML venues (NeurIPS, ICML, ICLR),
if HHI increases year-over-year,
then evaluation diversity (normalized entropy) decreases in the subsequent year,
because researchers collectively optimize for established benchmarks and reduce exploration of alternative evaluation paths.

### 1.2 Alternative Hypothesis (H0)
There is no significant relationship between year-over-year HHI changes and subsequent year evaluation entropy changes (β = 0, p > 0.05).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Papers With Code Dataset-Paper Links (standard) | PWC provides dataset tags for papers in target venues at 80%+ coverage |
| **Model** | N/A - Econometric Analysis | Panel regression with fixed effects is standard for this analysis |

**Dataset Details:**
- Source: Papers With Code API/CSV Export
- Path: https://paperswithcode.com/api/v1/

**Model Details:**
- Type: statistical
- Source: Standard econometrics (statsmodels, R)

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Engdahl (2024) qualitative analysis | Identified alignment processes qualitatively | Interview/ethnographic data |
| Olszewski et al. (2023) reproducibility measurement | 93 papers analyzed, no AE committee effect found | Security conference papers |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Papers With Code dataset tags accurately reflect paper evaluation practices | PWC has manual curation; 200K+ papers tagged | Measurement noise could mask true concentration effects |
| A2 | HHI and entropy are valid proxies for concentration and diversity | Standard metrics in economics and information theory | Alternative concentration/diversity measures might show different patterns |
| A3 | The 2018-2024 period captures meaningful variation in concentration | Period spans pre/post artifact evaluation requirements | Insufficient temporal variation could limit statistical power |
| A4 | Major venues (NeurIPS/ICML/ICLR) are representative of ML research | These are the top-3 general ML venues by citation impact | Findings might not generalize to domain-specific venues |
| A5 | One-year lag is appropriate temporal scale for concentration effects | Publication cycle typically ~1 year from submission to influence | Different lag structures might reveal different patterns |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First quantitative application of economic concentration metrics (HHI) to ML benchmark usage patterns

**Key Innovation:** Temporal-causal design with lagged panel regression to test epistemic lock-in theory

**Differentiation:**
- Engdahl (2024): Qualitative ethnographic study vs our quantitative longitudinal analysis
- Olszewski et al. (2023): Measured reproducibility directly vs our upstream concentration mechanism
- HPO-B (2021): Created benchmark vs our analysis of benchmark usage patterns

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | pending |
| H-M1 | Mechanism | MUST_WORK | H-E1 | pending |
| H-M2 | Mechanism | SHOULD_WORK | H-M1 | pending |
| H-M3 | Mechanism | SHOULD_WORK | H-M2 | pending |
| H-M4 | Mechanism | SHOULD_WORK | H-M3 | pending |
| H-M5 | Mechanism | SHOULD_WORK | H-M4 | pending |

---

### 2.2 Hypothesis Specifications

#### H-E1: HHI Concentration Measurable from PWC Data

**Type:** EXISTENCE
**Statement:** Under standard API access to Papers With Code, if we query NeurIPS/ICML/ICLR papers (2018-2024), then we can compute valid HHI concentration scores per venue-year, because PWC provides dataset tags with 80%+ coverage.

**Rationale:** This existence hypothesis validates that our measurement infrastructure works. Without measurable concentration, the entire causal chain cannot be tested. PWC coverage is established fact but computation pipeline needs verification.

**Variables:**
- IV: PWC API queries for venue-year combinations
- DV: HHI scores (0-1 range, non-null for all venue-years)
- CV: Venue list (NeurIPS, ICML, ICLR), Year range (2018-2024)

**Verification Protocol:**
1. Query PWC API for all papers in target venues (2018-2024)
2. Extract dataset tags per paper, compute dataset share per venue-year
3. Calculate HHI = Σ(share²) for each of 21 venue-year combinations
4. Verify all 21 HHI scores are valid (non-null, range 0-1)

**Success Criteria:**
- Primary: 21/21 venue-years have valid HHI scores
- Secondary: HHI variance > 0 (not all identical)

**Failure Response:** IF fails: PIVOT to alternative data source (Semantic Scholar, OpenAlex)

**Dependencies:** None (foundation hypothesis)
**Source:** Phase 2A SH1

---

#### H-M1: High HHI Indicates Community Convergence

**Type:** MECHANISM
**Statement:** Under computed HHI scores, if HHI > venue median for a venue-year, then fewer unique datasets account for majority of evaluations, because HHI mathematically captures market share concentration.

**Rationale:** This validates that HHI interpretation is correct for ML context. High HHI should mean top-k datasets dominate, not just mathematical artifact.

**Variables:**
- IV: HHI score per venue-year
- DV: Top-5 dataset share (% of papers using top 5 datasets)
- CV: Venue, year

**Verification Protocol:**
1. Split venue-years into high-HHI (>median) and low-HHI groups
2. Compute top-5 dataset concentration for each group
3. Test if high-HHI group has significantly higher top-5 share
4. Validate with Spearman correlation between HHI and top-5 share

**Success Criteria:**
- Primary: High-HHI group top-5 share > low-HHI group (p < 0.05)
- Secondary: Spearman ρ > 0.7 between HHI and top-5 share

**Failure Response:** IF fails: EXPLORE alternative concentration measures (CR4, Gini)

**Dependencies:** H-E1
**Source:** Phase 2A Causal Step 1

---

#### H-M2: Convergence Creates Implicit Evaluation Standards

**Type:** MECHANISM
**Statement:** Under high HHI venue-years, if concentration persists, then paper acceptance correlates with using standard benchmarks, because implicit norms favor established evaluation practices.

**Rationale:** This tests the social mechanism: does concentration reflect/create norms? Harder to test directly, but can proxy via benchmark persistence and new paper behavior.

**Variables:**
- IV: Venue-year HHI (lagged)
- DV: New paper benchmark choice (standard vs novel)
- CV: Paper topic, author experience

**Verification Protocol:**
1. Identify "standard" datasets (top-5 by usage in prior year)
2. Track new papers' dataset choices vs prior-year standards
3. Compute correlation between venue HHI and standard-benchmark adoption
4. Control for topic (CV/NLP/RL) and author publication history

**Success Criteria:**
- Primary: Higher HHI predicts higher standard-benchmark adoption (β > 0, p < 0.05)
- Secondary: Effect persists after topic controls

**Failure Response:** IF fails: EXPLORE direct norm measurement (surveys, reviewer guidelines)

**Dependencies:** H-M1
**Source:** Phase 2A Causal Step 2

---

#### H-M3: Papers Follow Standards for Comparability

**Type:** MECHANISM
**Statement:** Under implicit evaluation standards, if authors cite prior work, then they use same benchmarks as cited papers, because comparability requires shared evaluation.

**Rationale:** Tests whether citation network drives benchmark homogeneity. If papers cite work X, they should evaluate on same datasets as X.

**Variables:**
- IV: Citation overlap between papers
- DV: Dataset overlap between papers
- CV: Venue, year, topic

**Verification Protocol:**
1. Build citation network within venue-year
2. Compute Jaccard similarity of datasets between citing/cited pairs
3. Compare to random baseline (non-cited pairs)
4. Test if citation predicts dataset overlap beyond topic similarity

**Success Criteria:**
- Primary: Citing pairs have higher dataset overlap than random (p < 0.01)
- Secondary: Effect size (Cohen's d) > 0.3

**Failure Response:** IF fails: EXPLORE alternative comparability mechanisms

**Dependencies:** H-M2
**Source:** Phase 2A Causal Step 3

---

#### H-M4: Reduced Diversity Hides Benchmark-Specific Overfitting

**Type:** MECHANISM
**Statement:** Under low evaluation diversity, if papers only evaluate on standard benchmarks, then benchmark-specific overfitting goes undetected, because no out-of-distribution tests exist.

**Rationale:** This is the harm mechanism—why concentration matters. Requires proxy since we can't directly observe "hidden" overfitting.

**Variables:**
- IV: Evaluation diversity (entropy) per venue-year
- DV: Cross-benchmark performance variance (proxy for overfitting)
- CV: Model architecture, training data

**Verification Protocol:**
1. Identify papers with multi-benchmark evaluation (rare but exist)
2. Compute performance variance across benchmarks
3. Test if low-diversity venue-years have higher cross-benchmark variance
4. Use meta-analysis of existing multi-benchmark papers

**Success Criteria:**
- Primary: Negative correlation between entropy and cross-benchmark variance
- Secondary: Effect detectable in at least 2 of 3 venues

**Failure Response:** IF fails: PIVOT to qualitative evidence review

**Dependencies:** H-M3
**Source:** Phase 2A Causal Step 4

---

#### H-M5: Concentration-Diversity Cycle Reinforces Itself

**Type:** MECHANISM
**Statement:** Under high concentration, if HHI increases year-over-year, then entropy decreases in subsequent year, because the positive feedback loop amplifies lock-in.

**Rationale:** This is the core causal test—temporal precedence of concentration over diversity decline. Panel regression with lagged IV.

**Variables:**
- IV: ΔHHI_t (year-over-year HHI change)
- DV: ΔEntropy_{t+1} (subsequent year entropy change)
- CV: Venue FE, year FE, paper count

**Verification Protocol:**
1. Construct panel dataset: 21 venue-years with HHI and entropy
2. Run lagged panel regression: Entropy_t ~ HHI_{t-1} + venue FE + year FE
3. Run Granger causality test with 1-2 year lags
4. Check robustness with alternative lag structures

**Success Criteria:**
- Primary: β(HHI_{t-1}) < 0 with p < 0.05
- Secondary: HHI Granger-causes entropy (but not reverse)

**Failure Response:** IF fails: ABANDON causal claim, report as correlation only

**Dependencies:** H-M4
**Source:** Phase 2A Causal Step 5, Primary Prediction P1

<!--
Each hypothesis follows this format:

#### {H-ID}: {Title}

**Type:** {EXISTENCE|MECHANISM|CONDITION|COMPARISON}
**Statement:** {Full Under-If-Then-Because statement}

**Variables:**
- IV: {independent variable}
- DV: {dependent variable}
- CV: {controlled variables}

**Success Criteria:**
- {quantitative threshold 1}
- {quantitative threshold 2}

**Gate:**
- Type: {MUST_WORK|SHOULD_WORK|DETERMINES_SUCCESS}
- If Fail: {consequence}

**Prerequisites:** {list or "None"}

**Verification Protocol:** (100-150 words)
{step-by-step protocol}

---
-->

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-M5
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | 21/21 venue-years have valid HHI | STOP - reassess data source |
| H-M1 | MUST_WORK | High-HHI group > low-HHI group (p<0.05) | PIVOT to alt metrics |
| H-M2 | SHOULD_WORK | β > 0, p < 0.05 | Document as limitation |
| H-M3 | SHOULD_WORK | Citation-dataset overlap > random | Document as limitation |
| H-M4 | SHOULD_WORK | Negative correlation | Document as limitation |
| H-M5 | SHOULD_WORK | β(HHI_{t-1}) < 0, p < 0.05 | Report correlation only |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 1 week |
| Phase 2: Mechanism | H-M1 to H-M5 | 3 weeks |
| Phase 3: Analysis | Integration | 1 week |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Risk Identification

**Risk R1: PWC Data Quality**
- Source: A1 (PWC tags reflect evaluation practices)
- Description: PWC dataset tags may be incomplete, inconsistent, or systematically biased toward popular benchmarks
- Severity: High
- Likelihood: Medium

**Risk R2: Metric Validity**
- Source: A2 (HHI/entropy are valid proxies)
- Description: HHI may not capture meaningful concentration; entropy may miss diversity nuances
- Severity: Medium
- Likelihood: Low

**Risk R3: Temporal Coverage**
- Source: A3 (2018-2024 captures variation)
- Description: 7 years may be insufficient for robust panel regression; limited degrees of freedom
- Severity: High
- Likelihood: Medium

**Risk R4: Venue Representativeness**
- Source: A4 (Major venues representative)
- Description: NeurIPS/ICML/ICLR may not generalize to domain-specific venues or industry practices
- Severity: Medium
- Likelihood: Medium

**Risk R5: Lag Structure**
- Source: A5 (One-year lag appropriate)
- Description: Concentration effects may operate on different timescales (faster or slower than 1 year)
- Severity: Medium
- Likelihood: Medium

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 | A1 | H-E1, H-M1, H-M2, H-M3 | High |
| R2 | A2 | H-M1, H-M5 | Medium |
| R3 | A3 | H-M5 (panel regression) | High |
| R4 | A4 | All (generalizability) | Medium |
| R5 | A5 | H-M5 (lagged test) | Medium |

### 4.3 Mitigation Strategies

**R1 Mitigation (PWC Data Quality):**
1. Prevention: Validate PWC sample against manual paper review (N=50)
2. Detection: Compute inter-rater agreement on dataset extraction
3. Response:
   - PIVOT: Supplement with Semantic Scholar or manual extraction
   - SCOPE: Focus on high-confidence tags only
   - ABORT: If >30% of papers have no/wrong tags

**R2 Mitigation (Metric Validity):**
1. Prevention: Report multiple concentration metrics (HHI, CR4, Gini)
2. Detection: Check correlation between metrics
3. Response:
   - PIVOT: Use alternative metric if HHI shows floor/ceiling effects
   - SCOPE: Report all metrics, discuss divergence
   - ABORT: N/A (multiple metrics provide robustness)

**R3 Mitigation (Temporal Coverage):**
1. Prevention: Use all available years; consider venue-specific trends
2. Detection: Check statistical power before running main analysis
3. Response:
   - PIVOT: Aggregate to annual level if venue-year too sparse
   - SCOPE: Report confidence intervals; acknowledge power limitation
   - ABORT: If <10 effective observations after controls

**R4 Mitigation (Venue Representativeness):**
1. Prevention: Explicitly scope claims to "major ML venues"
2. Detection: Compare patterns across venues; check heterogeneity
3. Response:
   - PIVOT: Add CVPR/ACL/EMNLP for domain-specific comparison
   - SCOPE: Report as "major venue" finding, not universal
   - ABORT: N/A (scope limitation is acceptable)

**R5 Mitigation (Lag Structure):**
1. Prevention: Test multiple lag structures (0, 1, 2 years)
2. Detection: Compare model fit across lag specifications
3. Response:
   - PIVOT: Report best-fitting lag with sensitivity analysis
   - SCOPE: If no lag works, report as correlation only
   - ABORT: N/A (lag sensitivity is informative)

### 4.4 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | PWC data quality | A1 | High | H-E1, H-M1-3 | Validate sample + alternative sources |
| R2 | Metric validity | A2 | Medium | H-M1, H-M5 | Multiple metrics |
| R3 | Temporal coverage | A3 | High | H-M5 | Power analysis + scope claims |
| R4 | Venue representativeness | A4 | Medium | All | Explicit scope limitation |
| R5 | Lag structure | A5 | Medium | H-M5 | Multi-lag sensitivity |

**Risk Distribution:**
- Critical: 0
- High: 2 (R1, R3)
- Medium: 3 (R2, R4, R5)
- Low: 0

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 6 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    ┌─────────────────────────────────┐
    │  H-E1: HHI Measurable from PWC  │
    │  Gate: MUST_WORK                │
    └─────────────────────────────────┘
                    │
                    ▼
[Level 1 - Mechanism Chain]
    ┌─────────────────────────────────┐
    │  H-M1: HHI = Community Conv.    │
    │  Gate: MUST_WORK                │
    └─────────────────────────────────┘
                    │
                    ▼
    ┌─────────────────────────────────┐
    │  H-M2: Implicit Standards       │
    │  Gate: SHOULD_WORK              │
    └─────────────────────────────────┘
                    │
                    ▼
    ┌─────────────────────────────────┐
    │  H-M3: Papers Follow Standards  │
    │  Gate: SHOULD_WORK              │
    └─────────────────────────────────┘
                    │
                    ▼
    ┌─────────────────────────────────┐
    │  H-M4: Diversity Hides Overfit  │
    │  Gate: SHOULD_WORK              │
    └─────────────────────────────────┘
                    │
                    ▼
    ┌─────────────────────────────────┐
    │  H-M5: Feedback Loop (Core)     │
    │  Gate: SHOULD_WORK              │
    └─────────────────────────────────┘
                    │
                    ▼
               [COMPLETE]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-M5
All hypotheses sequential - no parallelization
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Phase |
|-------|-----------|---------------|-----------|-------|
| 0 | H-E1 | None | MUST_WORK | Foundation |
| 1 | H-M1 | H-E1 | MUST_WORK | Mechanism |
| 2 | H-M2 | H-M1 | SHOULD_WORK | Mechanism |
| 3 | H-M3 | H-M2 | SHOULD_WORK | Mechanism |
| 4 | H-M4 | H-M3 | SHOULD_WORK | Mechanism |
| 5 | H-M5 | H-M4 | SHOULD_WORK | Mechanism |

### 5.3 Gantt Timeline

```
Week      1         2         3         4         5
          |---------|---------|---------|---------|
H-E1      ████████
H-M1               ████████
H-M2                        ████████
H-M3                        ████████
H-M4                                  ████████
H-M5                                  ████████
Analysis                                        ████████

Legend: ████ = Active work
Note: H-M2/M3 and H-M4/M5 can partially overlap as data flows
```

### 5.4 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-M5

**Bottlenecks:**
1. H-E1 (Data extraction): PWC API rate limits may slow extraction
2. H-M5 (Panel regression): Statistical power depends on sample size

**Risk Points:**
- Gate 1 (H-E1): If PWC data unavailable, entire pipeline blocked
- Gate 2 (H-M1): If HHI interpretation invalid, mechanism tests meaningless

**Parallelization:** Limited. Some H-M hypotheses can partially overlap once data flows, but dependencies enforce sequential logic.

### 5.5 Resource Summary

| Resource | Requirement | Hypothesis |
|----------|-------------|------------|
| PWC API access | Required | H-E1 |
| Python (pandas, statsmodels) | Required | All |
| Compute | Minimal (no GPU) | All |
| Storage | ~1GB (paper metadata) | H-E1 |
| Time (researcher) | 5 weeks | All |

### 5.6 Execution Order

1. **Week 1:** H-E1 - Extract PWC data, compute HHI/entropy for all venue-years
2. **Week 2:** H-M1 - Validate HHI interpretation (high vs low HHI groups)
3. **Week 3:** H-M2, H-M3 - Test implicit standards and citation-benchmark correlation
4. **Week 4:** H-M4, H-M5 - Test diversity-overfitting link and core panel regression
5. **Week 5:** Integration - Synthesize results, write analysis, address limitations

---

## 6. Dialectical Analysis

### 6.1 Overview

This section evaluates the hypothesis through Thesis-Antithesis-Synthesis structure, using the null hypothesis (H0) from Phase 2A as the antithesis foundation. The goal is robust verification by explicitly considering opposing viewpoints.

### 6.2 Thesis Statement

**Core Claim:** Under conditions of high benchmark dataset concentration (HHI > venue median) in major ML venues, if HHI increases year-over-year, then evaluation diversity (normalized entropy) decreases in the subsequent year, because researchers collectively optimize for established benchmarks.

**Supporting Evidence:**
1. Causal mechanism: 5-step chain from concentration to lock-in (Phase 2A Section 1.3)
2. Established facts: HHI/entropy are standard metrics; PWC has 80%+ coverage
3. Testable predictions: Lagged panel regression with fixed effects

**Strengths:**
- Builds on established economic concentration metrics (HHI)
- Clear temporal-causal design with lagged IV
- Falsifiable with explicit β < 0, p < 0.05 criterion
- Uses existing data (no new collection needed)

**Expected Outcomes:**
- Primary: β(HHI_{t-1}) < 0 with p < 0.05
- Secondary: HHI Granger-causes entropy (but not reverse)
- Tertiary: Papers using high-HHI datasets evaluate on fewer unique datasets

### 6.3 Antithesis Development

**Null Hypothesis (H0):** There is no significant relationship between year-over-year HHI changes and subsequent year evaluation entropy changes (β = 0, p > 0.05).

**Counter-Arguments:**
1. **Positive concentration interpretation:** High HHI may reflect field maturity and consensus on best practices, not pathological lock-in
2. **Measurement artifacts:** PWC coverage gaps may create spurious concentration patterns
3. **Confounding factors:** Technological shifts (new modalities) may drive both concentration and diversity changes

**Potential Failure Points:**
- R1: PWC data quality issues mask true effects or create artifacts
- R3: Insufficient temporal variation limits statistical power
- R5: Wrong lag structure misses true relationship

**Conditions Under Which H0 Would Be Supported:**
- β(HHI_{t-1}) ≥ 0 or p > 0.05 in panel regression
- Reverse Granger causality (entropy causes HHI)
- High-HHI and low-HHI groups show no difference in diversity

### 6.4 Synthesis

**Balanced Assessment:**

The hypothesis H-BenchmarkConcentration-v1 presents a testable claim about epistemic lock-in in ML research. The thesis argues that concentration (HHI) temporally precedes and predicts diversity decline. However, the antithesis raises valid concerns: concentration may be beneficial (field maturity), measurement may be flawed (PWC gaps), and confounders may explain correlations.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Validates data quality before any causal claims
2. **Sequential mechanism testing (H-M1-M5):** Tests each causal step independently
3. **Multiple metrics:** Uses HHI, CR4, and entropy with sensitivity checks
4. **Lagged design:** Addresses reverse causality concern explicitly

**Conditions for Thesis Support:**
- H-E1 passes (21/21 venue-years have valid HHI)
- H-M1 passes (HHI interpretation valid)
- H-M5 passes (β < 0, p < 0.05 in lagged regression)

**Conditions for Antithesis Support:**
- H-E1 fails (data unavailable/invalid)
- H-M1 fails (HHI doesn't correlate with top-5 share)
- H-M5 fails (β ≥ 0 or p > 0.05)

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Epistemic lock-in confirmed
2. **Partial Support:** H-M4/M5 fail → Correlation exists but causal mechanism unclear
3. **No Support:** H-E1 or H-M1 fail → Data or metric validity problems

### 6.5 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | HHI measurable from PWC | PWC coverage may be biased | H-E1: Validate sample |
| Mechanism | Concentration → lock-in | Could be field maturity | H-M1-M5: Test each step |
| Causality | HHI precedes entropy | Reverse causality possible | Lagged design + Granger |
| Scope | Major ML venues | May not generalize | Explicit scope limitation |

**Overall Robustness Score:** Medium-High

**Confidence in Verification Plan:** 0.75

**Rationale:** The plan systematically addresses key challenges through sequential hypothesis testing. The main residual uncertainty is whether observational data can establish causality (addressed via lagged design but not definitive).

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Benchmark concentration (HHI) predicts evaluation diversity decline
- ID: H-BenchmarkConcentration-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 6 total (H-E: 1, H-M: 5)
- Phases: 2 phases over 5 weeks
- Critical Gates: 2 decision points (H-E1, H-M1)

**Risk Assessment:** Medium
- Primary concerns: PWC data quality (R1), temporal coverage (R3)

**Immediate Action:** Begin Phase 1 with H-E1 (PWC data extraction)

### 7.2 Final Summary

**Key Achievements:**
- 6 hypotheses across 2 phases with clear verification protocols
- H0 addressed: β = 0, p > 0.05 (no relationship)
- Scope reduction: 67% (4 of 6 claims established, 2 need verification)

**Verification Execution Order:**

**Phase 1: Foundation** (1 week)
- H-E1: Validate HHI measurable from PWC data
- Gate 1: MUST PASS (21/21 venue-years valid)

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: HHI indicates community convergence
- H-M2: Convergence creates implicit standards
- H-M3: Papers follow standards for comparability
- H-M4: Reduced diversity hides overfitting
- H-M5: Concentration-diversity feedback loop
- Gate 2: H-M1 must pass

### 7.3 Conclusions

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, pivot to alternative data source
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - CRITICAL FAIL → Reassess HHI interpretation
   - OPTIONAL FAIL (H-M2-5) → Document as limitation

**Open Questions:**
- Optimal lag structure (1 year assumed, could test 2 years)
- Whether to use change scores (ΔHHI) or levels (HHI)
- Paper-level vs venue-year level as primary unit of analysis

**Recommendations:**

1. **Immediate Actions:**
   - Start Phase 1 with H-E1 (PWC API data extraction)
   - Set up HHI/entropy computation pipeline
   - Validate sample against manual review (N=50)

2. **Resource Allocation:**
   - Allocate 5 weeks for critical path
   - Reserve 1 week buffer for data issues

3. **Failure Management:**
   - Document all H-M failures as limitations
   - Execute PIVOT strategies per risk mitigation plan

### 7.4 Appendices

**A. Phase 2A Reference**
- Source: 03_refinement.yaml (ID: H-BenchmarkConcentration-v1)
- Convergence: 18 exchanges, all 6 criteria satisfied

**B. MCP Tool Usage Summary**
- Total MCP calls: 2
- Tools: scientificmethod (hypothesis + experiment stages)

---

## 8. State & Pipeline Integration

### 8.1 Verification State Status

**File Generated:** `verification_state.yaml`

| Field | Value |
|-------|-------|
| Project | Benchmark Concentration and Epistemic Lock-in |
| Main Hypothesis | H-BenchmarkConcentration-v1 |
| Sub-Hypotheses | 6 (H-E1, H-M1-M5) |
| Next Hypothesis | H-E1 (READY) |
| Schema Version | 1.0.0 |

### 8.2 Pipeline Tasks Updated

| Task | Status | ID |
|------|--------|-----|
| Phase 2B - Verification Planning | done | 3272c6ed-b6a6-4ccd-964e-498a32f54596 |
| Phase 2C - Experiment Design | todo | e7ab8ef1-ec0e-47c3-890a-5a5111cea914 |

### 8.3 Hypothesis Tasks Created

| Hypothesis | Type | Task ID |
|------------|------|---------|
| H-E1 | EXISTENCE | 1cceca75-bf40-44bd-8f9b-6f7565fe1712 |
| H-M1 | MECHANISM | bfda532d-56cc-4a79-954a-f2240d935a56 |
| H-M2 | MECHANISM | 673cd1c0-d645-40ce-bf7a-d84999d5206d |
| H-M3 | MECHANISM | d05709f7-77d2-4220-9278-7c4f99e18d3e |
| H-M4 | MECHANISM | 5cc5e1d7-0d12-4d5b-a7df-4a972dc6cd73 |
| H-M5 | MECHANISM | e73cb00b-a3de-458e-b40d-fa4be0f58e96 |

---

*Phase 2B Complete - 2026-08-10*
