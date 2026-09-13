# Verification Plan: ML Dataset Documentation Gap - Prevalence and Community Pressure Mechanism

**Date:** 2026-07-12
**Hypothesis ID:** h-doc-prevalence
**Confidence:** 0.75 (estimated from Phase 2A analysis)
**Total Hypotheses:** 2

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Among ML dataset repositories on HuggingFace created 2022–2024 with ≥10 stars, ≤40% achieve a Documentation Completeness Score (DCS_3) ≥ 80% within 90 days of first release, demonstrating a significant framework-to-practice compliance gap despite the existence of standardized documentation frameworks.

**Mechanism:** Repository community engagement drives documentation quality. Repositories with higher activity levels (commits/month, contributors, issue responsiveness) exhibit significantly higher DCS_3 scores (Spearman ρ ≥ 0.30, p < 0.05), suggesting documentation gaps arise from lack of community pressure rather than framework inadequacy.

### 1.2 Alternative Hypothesis (H0)

**Existence H0:** ≥70% of sampled repositories achieve DCS_3 ≥ 2.4 within 90 days
**Existence H1:** ≤40% achieve compliance

**Mechanism H0:** Spearman ρ (activity, DCS_3) ≤ 0.10 or p ≥ 0.05
**Mechanism H1:** ρ ≥ 0.30 and p < 0.05

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HuggingFace Datasets Hub (standard) | N=100 ML dataset repositories, stratified by year (2022-2024), ≥10 stars threshold for visibility. Aligns with sampling frame requirements. |
| **Model** | Documentation Completeness Score (DCS_3) - 3-component rubric | Based on Rondina 2025 validated framework. Components: data collection context, preprocessing transparency, licensing clarity. Reduces multicollinearity vs full 14-component rubric. |

**Dataset Details:**
- Source: HuggingFace Datasets Hub via `datasets` library + GitHub API
- Path: Repos created 2022-01-01 to 2024-12-31, ≥10 stars
- Temporal measurement: T0 + 90 days (3-tier fallback: release tag > dataset commit > repo creation)

**Model Details:**
- Type: Observational measurement (cross-sectional with retrospective temporal validation)
- Source: Rondina et al. 2025 rubric (published, Table 2)
- Inter-rater reliability: κ ≥ 0.70 required (20% dual-coded sample)

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Rondina et al. 2025 | N=100 datasets, current state documentation | HuggingFace (snapshot) | No temporal precedence validation (T0 + 90), used full 14-component rubric |
| Oreamuno et al. 2024 | Ethics weakness identified | HuggingFace | Cross-sectional only, no mechanism test |
| Gim et al. 2025 | 0% Reusable, 5% Findable (FAIR) | OpenML | FAIR ≠ documentation completeness, different framework |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | HuggingFace datasets 2022-2024 represent contemporary ML dataset publishing | Platform dominance in ML community | Generalizability threatened, results platform-specific |
| A2 | 3-component subset adequately captures documentation completeness | Rondina 2025 factor analysis | DCS_3 may miss critical dimensions, validity threatened |
| A3 | GitHub metadata provides sufficient temporal precision for T0 | 3-tier fallback strategy | >5% missing T0 would reduce sample size, power threatened |
| A4 | Cross-sectional correlation is valid proxy for community pressure | Limitation acknowledged (correlation not causation) | Mechanism interpretation weakened, RCT needed |
| A5 | DCS remains stable within 90-day window | Assumption of front-loaded documentation | Temporal pattern prediction fails if DCS changes >5% |

### 1.6 Research Gap & Novelty

**Gap Addressed:**
- **Temporal Precedence Gap:** Prior studies (Rondina 2025, Oreamuno 2024) measured current state, not documentation at release. This study measures at T0 + 90 days, establishing temporal precedence.
- **Implementation Failure Gap:** Prior attempts (h-da2, h-e1 runs 1-2, h-m1, h-m3) failed due to: external API brittleness, semantic proxy failures, multicollinearity, synthetic data. This design avoids all 6 failure modes.
- **Mechanism Gap:** Voluntary adoption inertia tested via observable activity proxies instead of unobservable incentive structures.

**Novelty:**
1. **First temporal precedence validation** (T0 + 90 vs current state)
2. **Feasibility-grounded design** (learns from 6 prior implementation failures)
3. **Community pressure mechanism test** (bridges documentation studies + software engineering metrics)

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | SHOULD_WORK | H-E1 | NOT_STARTED |

**Total: 2 sub-hypotheses**

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Documentation Gap Prevalence

**Type:** EXISTENCE

**Statement:** Among ML dataset repositories on HuggingFace created 2022–2024 with ≥10 stars, ≤40% achieve DCS_3 ≥ 2.4 within 90 days of first release, demonstrating that a significant framework-to-practice compliance gap exists despite standardized documentation frameworks.

**Rationale:** This hypothesis validates the core premise that a measurable documentation gap exists in practice. It provides the empirical foundation required before testing mechanism hypotheses. Prior studies (Rondina 2025, Oreamuno 2024) measured current state; this is the first temporal precedence validation (T0 + 90 days).

**Variables:**
- **Independent Variables:**
  - repository_period (categorical: 2022, 2023, 2024)
  - platform (categorical: HuggingFace)
  - visibility_threshold (numeric: ≥10 stars)
- **Dependent Variable:**
  - DCS_3 (Documentation Completeness Score: 0-3 scale, threshold 2.4)
  - Components: data collection context, preprocessing transparency, licensing clarity
- **Controlled Variables:**
  - measurement_timepoint (T0 + 90 days via 3-tier fallback)
  - stratification (by year to control temporal trends)

**Verification Protocol:**
1. Sample N=100 HuggingFace dataset repositories (2022-2024, ≥10 stars) using stratified sampling by year
2. Determine T0 for each repository via 3-tier fallback (release tag > first dataset commit > repo creation)
3. Clone repository state at T0 + 90 days commit and assess 3 DCS components using Rondina 2025 rubric
4. Conduct inter-rater reliability check on 20% dual-coded sample (κ ≥ 0.70 required)
5. Calculate compliance rate (proportion achieving DCS_3 ≥ 2.4) with 95% confidence interval
6. Run binomial proportion test: H0: π ≥ 0.70 vs H1: π < 0.70

**Success Criteria (MUST_WORK Gate):**
- **Primary:** 95% CI upper bound < 60% (rejects H0, confirms gap exists)
- **Secondary:** Component breakdown analysis shows non-uniform distribution (chi-square test)
- **Gate Criterion:** If CI upper bound ≥ 60%, existence hypothesis fails

**Failure Response:**
- **IF FAIL (CI upper ≥ 60%):** Documentation gap does not exist at hypothesized severity → ROUTE to Phase 0 (fundamental premise violated)
- **IF PARTIAL (60% < CI < 70%):** Gap exists but less severe → MODIFY H-M1 to test smaller effect sizes

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A Section 1.1 (Core Statement), Section 1.6 (Prediction 1: prevalence_quantitative)

**Gate Type:** MUST_WORK (existence must be validated before testing mechanisms)

---

#### H-M1: Community Pressure Mechanism

**Type:** MECHANISM

**Statement:** Repository community engagement (commits/month, contributors, issue responsiveness) positively correlates with documentation quality (DCS_3) with Spearman ρ ≥ 0.30 (p < 0.05), demonstrating that documentation gaps arise from lack of community pressure rather than framework inadequacy.

**Rationale:** This hypothesis tests the mechanism behind the documentation gap. If community activity correlates with documentation quality, it suggests voluntary adoption inertia driven by social pressure, not framework design flaws. This bridges documentation studies with software engineering process metrics.

**Variables:**
- **Independent Variables (Activity Metrics):**
  - commits_per_month (count in first 90 days / 3)
  - unique_contributors (count in first 90 days)
  - median_issue_response_time (days, if ≥5 issues exist)
- **Dependent Variable:**
  - DCS_3 (from H-E1 measurement)
- **Controlled Variables:**
  - repository_age (days since creation, for partial correlation control)

**Verification Protocol:**
1. For same N=100 repositories from H-E1, collect activity metrics via GitHub API (first 90 days)
2. Compute composite activity score or analyze metrics individually
3. Calculate Spearman rank correlation between activity metrics and DCS_3
4. Run partial correlation controlling for repository age to isolate community effect
5. Test significance: ρ ≥ 0.30, p < 0.05 (one-tailed), must persist in partial correlation

**Success Criteria (SHOULD_WORK Gate):**
- **Primary:** Spearman ρ ≥ 0.30, p < 0.05 (one-tailed)
- **Secondary:** Partial correlation (controlling age) remains significant (ρ ≥ 0.25, p < 0.05)
- **Gate Criterion:** If ρ < 0.10 or p ≥ 0.05, mechanism hypothesis fails

**Failure Response:**
- **IF FAIL (ρ < 0.10 or not significant):** Community pressure is not the mechanism → ROUTE to Phase 2A-Dialogue (explore alternative mechanisms: framework design, tool availability, training gaps)
- **IF PARTIAL (0.10 ≤ ρ < 0.30):** Weak correlation detected → MODIFY to test alternative activity metrics or confounders

**Dependencies:** H-E1 (must confirm gap exists before testing mechanism)

**Source:** Phase 2A Section 1.1 (Mechanism Statement), Section 1.6 (Prediction 3: mechanism_correlation)

**Gate Type:** SHOULD_WORK (mechanism test is exploratory, not foundational)

**Limitations Acknowledged:**
- Correlation not causation (RCT deferred to future work per Phase 2A Section 1.4 Assumption A4)
- Cross-sectional design cannot establish temporal precedence of activity → DCS
- Activity metrics may be confounded by project popularity or domain

---

---

## 2.3 Risk Analysis

### Key Assumptions (from Phase 2A)

| ID | Assumption | Evidence | Consequence if Violated | Criticality |
|----|------------|----------|-------------------------|-------------|
| A1 | HuggingFace datasets 2022-2024 represent contemporary ML dataset publishing | Platform dominance in ML community | Generalizability threatened, results platform-specific | High |
| A2 | 3-component subset adequately captures documentation completeness | Rondina 2025 factor analysis | DCS_3 may miss critical dimensions, validity threatened | Medium |
| A3 | GitHub metadata provides sufficient temporal precision for T0 | 3-tier fallback strategy | >5% missing T0 would reduce sample size, power threatened | High |
| A4 | Cross-sectional correlation is valid proxy for community pressure | Limitation acknowledged (correlation not causation) | Mechanism interpretation weakened, RCT needed | Medium |
| A5 | DCS remains stable within 90-day window | Assumption of front-loaded documentation | Temporal pattern prediction fails if DCS changes >5% | Medium |

### Risk-Hypothesis Mapping

| Risk ID | Risk Description | Source | Affected Hypotheses | Severity |
|---------|------------------|--------|---------------------|----------|
| R1 | Platform-specific bias: HuggingFace may not represent broader ML ecosystem | A1 | H-E1, H-M1 | Medium |
| R2 | DCS_3 measurement validity: 3-component rubric may miss important dimensions | A2 | H-E1, H-M1 | Medium |
| R3 | Temporal alignment failure: >5% repos have undetectable T0 | A3 | H-E1 | High |
| R4 | Mechanism misattribution: correlation ≠ causation | A4 | H-M1 | Low |
| R5 | DCS instability: Documentation changes significantly within 90 days | A5 | H-E1 | Low |

### Mitigation Strategies

**Risk R1: Platform-Specific Bias**

**Source Assumption:** A1 - HuggingFace datasets 2022-2024 represent contemporary ML dataset publishing

**Description:** Results may not generalize beyond HuggingFace. Platform-specific tools, culture, or community norms may influence documentation practices differently than Papers with Code, OpenML, or Zenodo.

**Affected Hypotheses:** H-E1, H-M1

**Severity:** Medium (impacts generalizability but not internal validity)

**Mitigation Strategy:**
1. **Prevention:** Explicitly scope claims to "HuggingFace ecosystem" in H-E1/H-M1 statements
2. **Detection:** Compare HuggingFace platform features (e.g., dataset card templates) vs other platforms in discussion
3. **Response:**
   - DOCUMENT: Frame results as HuggingFace-specific baseline for future cross-platform studies
   - SCOPE: Limit conclusions to "HuggingFace datasets 2022-2024" explicitly
   - FUTURE: Pilot study on Papers with Code (N=20) to assess cross-platform validity (Phase 6 Discussion)

**Early Warning Indicators:**
- Preliminary literature review shows major platform differences in documentation tooling
- HuggingFace dataset card templates significantly more comprehensive than other platforms

---

**Risk R2: DCS_3 Measurement Validity**

**Source Assumption:** A2 - 3-component subset adequately captures documentation completeness

**Description:** DCS_3 (data context, preprocessing, licensing) may miss critical documentation dimensions from full 14-component Rondina rubric (e.g., ethics, limitations, intended use). Factor analysis assumed but not validated for 3-component subset.

**Affected Hypotheses:** H-E1, H-M1

**Severity:** Medium (construct validity threat)

**Mitigation Strategy:**
1. **Prevention:** Conduct pilot coding (N=20 repos) with both DCS_3 and full DCS_14 to validate correlation (Pearson r ≥ 0.80 required)
2. **Detection:** Monitor inter-rater reliability (κ ≥ 0.70); low κ suggests unclear construct
3. **Response:**
   - EXPAND: If pilot shows DCS_3 vs DCS_14 correlation <0.70, expand to 5-component subset (add ethics + limitations)
   - REPORT: Acknowledge limitation in Phase 6 Discussion, recommend full 14-component validation
   - ABORT: If κ < 0.50, rubric is unreliable; halt and refine measurement protocol

**Early Warning Indicators:**
- Pilot coding shows DCS_3 and DCS_14 divergence (r < 0.70)
- Inter-rater reliability κ < 0.70 on pilot 20 repos
- Coders report ambiguity in 3-component operationalization

---

**Risk R3: Temporal Alignment Failure**

**Source Assumption:** A3 - GitHub metadata provides sufficient temporal precision for T0

**Description:** >5% of sampled repositories may lack all 3 T0 indicators (release tag, dataset commit pattern, repo creation date), leading to missing T0 and reduced sample size below N=100 threshold for power=0.75.

**Affected Hypotheses:** H-E1

**Severity:** High (threatens statistical power)

**Mitigation Strategy:**
1. **Prevention:** Oversample to N=120 to accommodate up to 15% T0 detection failure while maintaining N≥100 valid cases
2. **Detection:** Track T0 detection rate during sampling; flag if >10% fail all 3 tiers
3. **Response:**
   - TIER-4 FALLBACK: Use "first commit with >100 LOC Python file" as proxy for initial development
   - LOWER THRESHOLD: Reduce star threshold from ≥10 to ≥5 to expand sampling frame (validate in Phase 2C)
   - ABORT: If >20% missing T0, temporal precedence claim is invalid; pivot to current-state measurement (loses novelty)

**Early Warning Indicators:**
- Pilot sample (N=10) shows >10% T0 detection failure
- Manual inspection reveals repositories with atypical commit patterns (e.g., bulk uploads)
- GitHub API rate limits prevent full commit history retrieval

---

**Risk R4: Mechanism Misattribution**

**Source Assumption:** A4 - Cross-sectional correlation is valid proxy for community pressure

**Description:** Spearman correlation between activity and DCS_3 does not establish causation. Confounders (e.g., project maturity, research area, team size) may drive both activity and documentation quality. Reverse causation possible (good documentation → attracts contributors).

**Affected Hypotheses:** H-M1

**Severity:** Low (acknowledged limitation, does not invalidate exploratory mechanism test)

**Mitigation Strategy:**
1. **Prevention:** Use partial correlation to control for repository age; report correlation as "association, not causation"
2. **Detection:** Test for reverse causation using Granger causality if longitudinal data available (future work)
3. **Response:**
   - ACKNOWLEDGE: Explicitly state correlation limitation in H-M1 conclusions (Phase 6 Section 5: Limitations)
   - FUTURE-RCT: Document RCT design in Phase 6 Discussion for causal validation (60-day intervention)
   - NO-ABORT: Even if correlation is spurious, it provides hypothesis for future causal studies

**Early Warning Indicators:**
- Literature review reveals known confounders not controlled (e.g., funding source, academic vs industry)
- Partial correlation (controlling age) drops below significance (ρ < 0.10, p ≥ 0.05)

---

**Risk R5: DCS Instability (Temporal Drift)**

**Source Assumption:** A5 - DCS remains stable within 90-day window

**Description:** Documentation may change significantly between T0+30 and T0+90 (>5% change), violating assumption that documentation is "front-loaded" at release. This would invalidate T0+90 as representative of "initial documentation."

**Affected Hypotheses:** H-E1

**Severity:** Low (temporal pattern prediction, not existence claim)

**Mitigation Strategy:**
1. **Prevention:** Measure DCS_3 at both T0+30 and T0+90 for subset (N=30) to validate stability
2. **Detection:** Calculate change rate: |DCS(T+90) - DCS(T+30)| / DCS(T+30); flag if >5% on average
3. **Response:**
   - REPORT: Document temporal pattern (iterative vs front-loaded) as finding in Phase 6 Section 4.4
   - NO-IMPACT: Existence claim (H-E1) still valid; only Prediction 4 (temporal pattern) affected
   - ADJUST: Use T0+30 as measurement timepoint if T0+90 shows systematic drift

**Early Warning Indicators:**
- Pilot temporal validation (N=10) shows >10% mean DCS change between T+30 and T+90
- Literature suggests iterative documentation improvement is common in ML repos

---

### Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation Status |
|----|------|--------|----------|----------|-------------------|
| R1 | Platform-specific bias | A1 | Medium | H-E1, H-M1 | Explicit scoping + future cross-platform pilot |
| R2 | DCS_3 validity | A2 | Medium | H-E1, H-M1 | Pilot validation (N=20) vs DCS_14 |
| R3 | T0 detection failure | A3 | High | H-E1 | Oversample to N=120 + 4-tier fallback |
| R4 | Correlation ≠ causation | A4 | Low | H-M1 | Partial correlation + acknowledged limitation |
| R5 | DCS temporal drift | A5 | Low | H-E1 | T+30/T+90 stability check (N=30 subset) |

**Risk Distribution:**
- Critical: 0
- High: 1 (R3: T0 detection)
- Medium: 2 (R1: platform bias, R2: DCS_3 validity)
- Low: 2 (R4: causation, R5: temporal drift)

**Critical Path Mitigation:** R3 (High severity) requires immediate action via oversampling to N=120.

---

## 3. Execution

### 3.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 2 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root / Foundation]
    ┌─────────────────────────────────────────┐
    │ H-E1: Documentation Gap Prevalence      │
    │ Type: EXISTENCE                         │
    │ Gate: MUST_WORK                         │
    │ Prerequisites: None                     │
    └─────────────────────────────────────────┘
                     │
                     ▼
[Level 1 - Mechanism]
    ┌─────────────────────────────────────────┐
    │ H-M1: Community Pressure Mechanism      │
    │ Type: MECHANISM                         │
    │ Gate: SHOULD_WORK                       │
    │ Prerequisites: H-E1                     │
    └─────────────────────────────────────────┘
                     │
                     ▼
            [Phase 5: Baseline Comparison]
                (Not sub-hypothesis)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → Phase 5
Total Depth: 2 levels
Parallelization: None (sequential verification)
═══════════════════════════════════════════════════════════
```

**Dependency Hierarchy:**
- **Level 0:** H-E1 (foundation, no dependencies)
- **Level 1:** H-M1 (depends on H-E1)
- **Phase 5:** Baseline comparison (depends on successful H-E1 validation)

**Gate Logic:**
1. **H-E1 Gate (MUST_WORK):** If fails → ROUTE to Phase 0 (fundamental premise violated)
2. **H-M1 Gate (SHOULD_WORK):** If fails → ROUTE to Phase 2A-Dialogue (mechanism wrong, not gap)
3. **Phase 5 Gate (DETERMINES_SUCCESS):** If fails → ROUTE to Phase 0 (approach inferior to baseline)

### 3.2 Verification Phases & Gates

**Phase 2C-4: PoC Verification (Sub-Hypotheses)**

| Phase | Hypothesis | Test | Gate Type | Pass Condition | Fail Action |
|-------|------------|------|-----------|----------------|-------------|
| Phase 2C-4.1 | H-E1 | Prevalence measurement (N=100, DCS_3 at T0+90) | MUST_WORK | 95% CI upper < 60% | ROUTE to Phase 0 |
| Phase 2C-4.2 | H-M1 | Activity-DCS correlation (Spearman ρ) | SHOULD_WORK | ρ ≥ 0.30, p < 0.05 | ROUTE to Phase 2A-Dialogue |

**Phase 5: Baseline Comparison (Main Hypothesis)**

| Phase | Comparison | Gate Type | Pass Condition | Fail Action |
|-------|------------|-----------|----------------|-------------|
| Phase 5 | Ours vs Baseline (Rondina 2025 method) | DETERMINES_SUCCESS | Our method identifies gap more reliably OR with better precision | ROUTE to Phase 0 (if baseline superior) |

**Note:** Phase 5 comparison is against Rondina 2025's current-state measurement approach. Our temporal precedence approach (T0+90) should show clearer gap vs their cross-sectional snapshot.

### 3.3 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | 95% CI upper bound < 60% compliance rate | ROUTE to Phase 0 (gap doesn't exist at severity claimed) |
| H-M1 | SHOULD_WORK | Spearman ρ ≥ 0.30, p < 0.05, persists in partial correlation | ROUTE to Phase 2A-Dialogue (mechanism wrong, explore alternatives) |

**Gate Failure Routing:**
- **MUST_WORK fail:** Fundamental premise violated → Phase 0 (new direction needed)
- **SHOULD_WORK fail:** Mechanism wrong but gap exists → Phase 2A-Dialogue (refine mechanism hypothesis)
- **DETERMINES_SUCCESS PARTIAL (Phase 5):** Baseline outperforms → Phase 0 (approach fundamentally inferior)

### 3.4 Timeline Estimate

| Phase | Activities | Hypotheses | Duration | Dependencies |
|-------|-----------|------------|----------|--------------|
| **Phase 2C** | Experiment design for H-E1, H-M1 | 2 | 2-3 days | Phase 2B complete |
| **Phase 3** | Implementation planning (PRD, Architecture, Tasks) | 2 | 3-4 days | Phase 2C complete |
| **Phase 4** | Coding & PoC validation | 2 | 2-3 weeks | Phase 3 complete |
| **Phase 4.5** | Hypothesis synthesis (evidence-refined claims) | - | 1-2 days | Phase 4 complete |
| **Phase 5** | Baseline repository comparison | - | 1 week | Phase 4.5 complete |
| **Phase 6** | Paper writing | - | 1-2 weeks | Phase 5 complete |

**Total Duration:** 5-7 weeks

**Critical Path:**
```
Phase 2B (2 days) → Phase 2C (3 days) → Phase 3 (4 days) → 
Phase 4 (3 weeks) → Phase 4.5 (2 days) → Phase 5 (1 week) → Phase 6 (2 weeks)
```

**Effort Breakdown:**
- **Phase 4 (Week 1):** Data collection automation (sampling, T0 detection, GitHub API)
- **Phase 4 (Week 2):** Manual DCS_3 coding (8 hours) + IRR validation (2 hours)
- **Phase 4 (Week 3):** Statistical analysis (binomial test, Spearman correlation, visualization)
- **Phase 5 (Week 1):** Baseline method replication + comparison analysis

---

---

## 4. Dialectical Analysis

### 4.1 Thesis

**Core Claim:** Among ML dataset repositories on HuggingFace created 2022–2024 with ≥10 stars, ≤40% achieve DCS_3 ≥ 2.4 within 90 days of first release, demonstrating a significant framework-to-practice compliance gap. Repository community engagement drives documentation quality (Spearman ρ ≥ 0.30), suggesting gaps arise from lack of community pressure rather than framework inadequacy.

**Supporting Evidence:**
1. **Empirical Gap Evidence:** Rondina 2025 found lack of context/preprocessing documentation in N=100 current datasets; Gim 2025 found 0% Reusable, 5% Findable (FAIR compliance crisis)
2. **Framework Existence:** Documentation frameworks exist and are well-cited (Datasheets: 3142 cites, Model Cards: 2899 cites), yet gaps persist
3. **Voluntary Adoption Inertia:** No enforcement mechanisms exist in any governance study, suggesting community pressure is key driver
4. **Implementation Feasibility:** All data sources confirmed (HuggingFace API, GitHub API, Rondina rubric), learns from 6 prior implementation failures

**Strengths:**
- **Temporal Precedence Novelty:** First study to measure documentation at T0+90 days vs current state
- **Feasibility-Grounded:** Explicitly learns from h-da2, h-e1 (runs 1-2), h-m-integrated, h-m1, h-m3 failures
- **Mechanism Test:** Bridges documentation studies with software engineering process metrics
- **Power Analysis:** N=100 provides power=0.75 for detecting 70% vs 40% difference

**Expected Outcomes:**
- **Primary (H-E1):** Compliance rate 35% [CI: 26%-44%], gate: CI upper < 60%
- **Secondary (Component Breakdown):** Non-uniform distribution (data context 25%, preprocessing 40%, licensing 50%)
- **Tertiary (H-M1):** Spearman ρ = 0.35-0.45, p < 0.01, persists in partial correlation controlling age

---

### 4.2 Antithesis

**Null Hypothesis (H0):**
- **Existence H0:** ≥70% of sampled repositories achieve DCS_3 ≥ 2.4 within 90 days (gap is minor or non-existent)
- **Mechanism H0:** Spearman ρ (activity, DCS_3) ≤ 0.10 or p ≥ 0.05 (community pressure is not the mechanism)

**Counter-Arguments:**

1. **Framework Effectiveness Argument:**
   - Frameworks may be working better than thesis claims. Rondina 2025's cross-sectional snapshot may reflect older repos; 2022-2024 repos may show improvement due to increased framework awareness.
   - HuggingFace provides dataset card templates and documentation prompts, which may drive higher compliance than Papers with Code or OpenML.
   - Boyd 2021 showed Datasheets improved user understanding (N=23 controlled study), suggesting frameworks do work when adopted.

2. **Measurement Validity Challenge:**
   - DCS_3 (3-component subset) may be too narrow. Full 14-component Rondina rubric may show higher compliance rates.
   - Inter-rater reliability κ ≥ 0.70 is ambitious for documentation assessment; lower reliability would invalidate prevalence claims.
   - T0 detection via 3-tier fallback may introduce systematic bias (repos with clear release processes may also have better documentation).

3. **Mechanism Misattribution:**
   - Correlation between activity and documentation may be spurious. Confounders include:
     - **Project maturity:** Well-established projects have both more activity and better documentation
     - **Research area:** Some domains (ethics-sensitive) require documentation regardless of community pressure
     - **Funding/Institution:** Academic vs industry teams may differ in documentation culture
   - **Reverse causation:** Good documentation may attract contributors, not the other way around
   - Cross-sectional design cannot establish temporal precedence of activity → documentation

4. **Scope Limitations:**
   - HuggingFace-specific results may not generalize to Papers with Code, OpenML, Zenodo, or GitHub-only datasets
   - ≥10 stars threshold excludes "long tail" of niche datasets (which may have worse documentation)
   - 2022-2024 timeframe may miss historical improvement trends (pre-2022 may have had worse compliance)

5. **Alternative Mechanisms Not Tested:**
   - **Tool availability:** HuggingFace's dataset card generator may drive compliance, not community pressure
   - **Platform defaults:** Auto-generated sections (licensing via GitHub) may inflate DCS_3 scores
   - **Selection bias:** Repositories with ≥10 stars are already more visible, may have documentation incentives independent of community activity

---

### 4.3 Synthesis

**Reconciliation of Thesis and Antithesis:**

The thesis and antithesis represent two plausible interpretations of the ML documentation ecosystem. The synthesis acknowledges both perspectives and defines clear empirical tests to distinguish between them.

**Points of Agreement:**
1. Documentation frameworks exist and are well-known (3000+ citations for Datasheets/Model Cards)
2. Some documentation gap has been empirically observed (Rondina 2025, Oreamuno 2024, Gim 2025)
3. Documentation quality varies across repositories
4. Multiple confounders exist (platform, tools, culture, domain)

**Points of Divergence:**
1. **Gap Severity:** Thesis claims ≤40% compliance; Antithesis suggests ≥70% (or improving trend)
2. **Mechanism:** Thesis attributes gap to lack of community pressure; Antithesis suggests tool availability, framework design, or confounders
3. **Generalizability:** Thesis frames as "ML ecosystem-wide"; Antithesis highlights HuggingFace-specific context

**Empirical Resolution Strategy:**

The verification plan is designed to **falsify the thesis** via multiple checkpoints:

1. **H-E1 Falsification (MUST_WORK Gate):**
   - **IF 95% CI upper ≥ 60%:** Thesis rejected, gap is less severe than claimed → ROUTE to Phase 0
   - **IF 95% CI overlaps 70%:** H0 cannot be rejected, gap may not exist → ROUTE to Phase 0
   - **IF 95% CI upper < 60%:** Thesis survives, proceed to mechanism test

2. **H-M1 Falsification (SHOULD_WORK Gate):**
   - **IF ρ < 0.10 or p ≥ 0.05:** Community pressure mechanism rejected → ROUTE to Phase 2A-Dialogue (explore alternatives)
   - **IF partial correlation (controlling age) loses significance:** Confounders explain correlation, not community pressure → MODIFY H-M1
   - **IF ρ ≥ 0.30, p < 0.05, persists in partial:** Mechanism survives, proceed to Phase 5

3. **Phase 5 Baseline Comparison (DETERMINES_SUCCESS Gate):**
   - **IF Rondina 2025 method performs equal/better:** Our temporal approach adds no value → ROUTE to Phase 0
   - **IF our method shows clearer gap:** Temporal precedence provides empirical advantage → Proceed to Phase 6

**Balanced Conclusion:**

The thesis is **strong on novelty** (temporal precedence, implementation feasibility) but **vulnerable on generalizability** (HuggingFace-specific, 3-component DCS). The antithesis raises valid concerns about **measurement validity** and **mechanism confounders**, but does not invalidate the **empirical test design**.

**The synthesis is a falsifiable verification plan** that:
- Explicitly tests thesis predictions (≤40% compliance, ρ ≥ 0.30)
- Defines clear failure conditions (MUST_WORK, SHOULD_WORK gates)
- Acknowledges limitations (correlation not causation, platform specificity)
- Routes to Phase 0 or Phase 2A-Dialogue on failure (not ad-hoc pivots)

**Robustness Assessment:**

| Concern | Severity | Addressed? | How |
|---------|----------|------------|-----|
| DCS_3 validity | Medium | Partially | Pilot validation (N=20) vs DCS_14, κ ≥ 0.70 required |
| Platform bias | Medium | Acknowledged | Explicit scoping to HuggingFace, future cross-platform pilot |
| Mechanism confounders | Low | Partially | Partial correlation controls age, limitation acknowledged |
| T0 detection failure | High | Yes | Oversample to N=120, 4-tier fallback |
| Sample size adequacy | Low | Yes | Power=0.75 for 70% vs 40% difference |

**Critical Vulnerability:** If DCS_3 inter-rater reliability κ < 0.70, measurement construct is invalid → halt and refine protocol (Risk R2 mitigation). All other concerns are managed via gates, scoping, or acknowledged limitations.

---


## 5. Executive Summary

### 5.1 Verification Plan Overview

**Main Hypothesis:** ML dataset documentation gap exists (≤40% DCS_3 compliance within 90 days) and is driven by lack of community pressure rather than framework inadequacy.

**Sub-Hypotheses:** 2 hypotheses (H-E1: Existence, H-M1: Mechanism)

**Verification Approach:** Sequential validation with MUST_WORK and SHOULD_WORK gates

**Timeline:** 5-7 weeks (Phase 2C through Phase 6)

**Critical Success Factors:**
1. H-E1 MUST pass (95% CI upper < 60%) to proceed
2. Inter-rater reliability κ ≥ 0.70 for DCS_3 measurement
3. T0 detection success rate ≥ 95% (oversample to N=120)
4. Phase 5 baseline comparison shows temporal precedence advantage

### 5.2 Key Innovations

1. **Temporal Precedence Validation:** First study to measure documentation at T0+90 days (vs current state)
2. **Feasibility-Grounded Design:** Explicitly learns from 6 prior implementation failures in this pipeline
3. **Community Pressure Mechanism:** Bridges documentation studies with software engineering process metrics
4. **Falsifiable Gates:** Clear MUST_WORK and SHOULD_WORK criteria with defined failure routing

### 5.3 Risk Mitigation Summary

| Risk | Severity | Mitigation |
|------|----------|------------|
| T0 detection failure | High | Oversample to N=120, 4-tier fallback |
| Platform-specific bias | Medium | Explicit HuggingFace scoping, future cross-platform pilot |
| DCS_3 validity | Medium | Pilot validation (N=20) vs DCS_14, κ ≥ 0.70 |
| Mechanism confounders | Low | Partial correlation controls age, limitation acknowledged |
| DCS temporal drift | Low | T+30/T+90 stability check (N=30) |

### 5.4 Decision Points

**Gate 1 (H-E1 MUST_WORK):**
- **IF PASS:** Proceed to H-M1 mechanism test
- **IF FAIL:** Documentation gap doesn't exist at claimed severity → ROUTE to Phase 0

**Gate 2 (H-M1 SHOULD_WORK):**
- **IF PASS:** Community pressure mechanism survives → Proceed to Phase 5
- **IF FAIL:** Mechanism wrong → ROUTE to Phase 2A-Dialogue (explore alternatives)

**Phase 5 Gate (DETERMINES_SUCCESS):**
- **IF PASS:** Temporal precedence approach superior to baseline → Phase 6 paper writing
- **IF PARTIAL:** Baseline equal/better → ROUTE to Phase 0 (approach not novel enough)

### 5.5 Expected Outcomes

**If All Gates Pass:**
- **Phase 4 Output:** Validated existence hypothesis (gap exists at ≤40% compliance) + mechanism evidence (ρ ≥ 0.30)
- **Phase 5 Output:** Temporal precedence approach shows clearer gap than Rondina 2025 cross-sectional method
- **Phase 6 Output:** Publication-ready paper with empirical evidence + implementation feasibility

**If Gate Failures Occur:**
- **H-E1 FAIL:** Pivot to Phase 0 (explore alternative documentation quality gaps or dataset governance issues)
- **H-M1 FAIL:** Refine mechanism in Phase 2A-Dialogue (explore tool availability, framework design, training gaps)
- **Phase 5 PARTIAL:** Recognize temporal approach adds no empirical value, pivot to Phase 0 for new direction

### 5.6 Execution Order

```
Phase 2B (COMPLETE) → Phase 2C (H-E1, H-M1 experiment design) → 
Phase 3 (Implementation planning) → Phase 4 (PoC validation) → 
Phase 4.5 (Hypothesis synthesis) → Phase 5 (Baseline comparison) → 
Phase 6 (Paper writing)
```

**Critical Path:** H-E1 → H-M1 → Phase 5 (no parallelization, sequential validation)

**Total Duration:** 5-7 weeks

**Phase 4 Effort Breakdown:**
- Week 1: Sampling automation + T0 detection (GitHub API)
- Week 2: Manual DCS_3 coding (8h) + IRR validation (2h)
- Week 3: Statistical analysis (binomial test, Spearman correlation, visualization)

---

## 6. Appendices

### A. Related Work Summary

**Baseline Studies:**
- **Rondina et al. 2025:** N=100 datasets, current state documentation, full 14-component rubric
- **Oreamuno et al. 2024:** HuggingFace documentation weakness in ethics dimensions
- **Gim et al. 2025:** 0% Reusable, 5% Findable (FAIR compliance crisis)

**Our Innovation:** Temporal precedence (T0+90) + 3-component subset + community pressure mechanism test

**Frameworks Referenced:**
- Datasheets for Datasets (Gebru et al. 2018, 3142 citations)
- Model Cards (Mitchell et al. 2018, 2899 citations)
- Boyd 2021: Datasheets effectiveness (N=23 controlled study)

### B. Data Sources Confirmed

1. HuggingFace Datasets Hub metadata (via `datasets` library)
2. GitHub commit history (via GitHub API, authenticated)
3. Rondina 2025 rubric (published, Table 2)

### C. Phase 2B Deliverables

✅ **Completed:**
- Main hypothesis validation (from Phase 2A)
- 2 sub-hypotheses (H-E1, H-M1) with verification protocols
- Risk analysis (5 assumptions → 5 risks, all mitigated)
- Dependency graph (H-E1 → H-M1 → Phase 5)
- Timeline estimate (5-7 weeks)
- Dialectical analysis (Thesis-Antithesis-Synthesis)
- Executive summary

🔄 **Next Phase (2C):**
- Detailed experiment design for H-E1 (sampling, DCS_3 coding, binomial test)
- Detailed experiment design for H-M1 (activity metrics, Spearman correlation)
- Per-hypothesis context files (02b_context_H-E1.md, 02b_context_H-M1.md) - generated JIT by Phase 2C

---

**Verification Plan Status:** ✅ COMPLETE

**Ready for Phase 2C:** ✅ YES

**Total Hypotheses:** 2 (H-E1: MUST_WORK, H-M1: SHOULD_WORK)

**Critical Path:** Sequential validation (H-E1 → H-M1 → Phase 5)

**Timeline:** 5-7 weeks total

