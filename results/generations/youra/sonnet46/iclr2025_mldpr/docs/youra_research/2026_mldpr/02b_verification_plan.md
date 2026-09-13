# Verification Plan: DTS-Weighted Documentation Completeness & Dataset Usage Prediction

**Date:** 2026-03-15
**Hypothesis ID:** H-DocComp-v1
**Confidence:** 0.78
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under ML dataset ecosystems across three major public repositories (HuggingFace Hub,
OpenML, UCI ML Repository), if repository metadata infrastructure provides structured
YAML templates with enforced fields (as HuggingFace post-2021 vs. legacy OpenML/UCI),
then DTS-weighted documentation completeness will be significantly higher for structured
repositories AND completeness score will significantly predict dataset download volume
(standardized β ≥ 0.15) in a pre-registered negative binomial regression, because
structured templates lower documentation friction, improving search filter eligibility
and discoverability, which drives downstream adoption.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in DTS-weighted documentation completeness between
repositories after controlling for dataset age, task domain, and organization type;
AND documentation completeness does not independently predict dataset usage volume
(standardized β < 0.05) after controlling for lagged downloads, dataset age, task
domain fixed effects, and repository fixed effects.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Cross-Repository ML Dataset Metadata Corpus (custom) | Public APIs provide structured metadata (card_data YAML, OpenML fields, UCI ucimlrepo) that directly operationalizes DTS field categories. No annotation required. |
| **Model** | Negative Binomial Regression + ANOVA (statistical) | Download counts are overdispersed count data; NB regression is mechanistically appropriate for overdispersed counts. ANOVA for cross-repo comparison. |

**Dataset Details:**
- Source: HuggingFace Hub API (list_datasets full=True), OpenML REST API, ucimlrepo Python package
- Path: Collected via API — no pre-existing file; ~100K HF datasets, ~4K OpenML datasets, ~600 UCI datasets

**Model Details:**
- Type: statistical
- Source: scipy.stats, statsmodels (NegativeBinomial), sklearn (StandardScaler)

### 1.4 Baseline Methods (for comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Rondina et al. 2025 (DTS schema, 100 datasets) | HF > Kaggle > OpenML > UCI on Presence Average; Uses=0.95, Collection Processes=0.10 asymmetry | 100 popular datasets from HF, Kaggle, OpenML, Papers With Code |
| Oreamuno et al. 2024 (HF-only audit) | 71.52% of HF dataset cards undocumented; Dataset Creation=9%, Considerations=16% | 6,758 HuggingFace model/dataset cards |
| Koch et al. 2021 (dataset reuse via reference counts) | Increasing concentration of reuse around elite-institution datasets 2015-2020 | Papers With Code reference counting |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | API-accessible fields provide valid proxies for documentation completeness when mapped to DTS section categories | Rondina et al. 2025 DTS; Pushkarna et al. 2022 Data Cards map to HF card_data | Automated completeness scores become invalid; entire measurement approach fails. Must validate with 120-dataset blinded human comparison (r ≥ 0.7). |
| A2 | HuggingFace download counts reflect genuine dataset adoption (not gaming/auto-downloads) | HF Hub API returns download_count; Oreamuno et al. 2024 used these statistics | Usage outcome variable invalid; must use Papers With Code reference counts as fallback. |
| A3 | Dataset creation year reliably extractable from repository API metadata | HF card_data last_modified; OpenML date attributes; UCI year field | Age confound uncontrollable; cross-repository comparison invalid without age adjustment. |
| A4 | The 2021 YAML frontmatter adoption on HuggingFace provides sufficient exogenous variation for DiD analysis | HF card_data validation mandated post-2021; co-timed with Pushkarna et al. 2022 | DiD causal interpretation fails; study becomes observational cross-section only. Usage prediction still testable. |
| A5 | Inverse-frequency weights from Rondina et al. 2025 Table 2 generalize to large-scale populations | Rondina et al. sampled popular datasets; section frequencies may be higher than general population | Weights may misrepresent general population; sensitivity analysis with unweighted scores required. |

### 1.6 Research Gap & Novelty

**Scope Reduction: 40%** — Four BUILD_ON claims (gaps widespread, DTS validated, HF ordering confirmed, YAML timing) require no re-verification. Two PROVE_NEW claims drive Phase 2B-4:
1. First population-scale (100K+ datasets) DTS-validated cross-repository completeness measurement
2. First empirical test of documentation completeness → discoverability → reuse pathway (pre-registered β threshold)

**Key Innovation:** Inverse-frequency weighted DTS scoring that captures rare high-effort documentation sections (Collection Processes weight ~10x vs. Uses), turning the Rondina et al. asymmetry from a finding into a measurement design principle.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | MUST_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: DTS Measurement Feasibility — API-Based Completeness Scoring**

**Type:** EXISTENCE
**Statement**: Under the ML dataset ecosystem context (HF Hub, OpenML, UCI), if public APIs are queried for dataset metadata (card_data YAML, OpenML fields, ucimlrepo), then DTS-weighted documentation completeness scores are computable for ≥70% of the target corpus because structured API responses map reliably to the 6 DTS section categories.

**Rationale** (2-3 sentences):
This hypothesis establishes that automated API-based DTS scoring is technically feasible at population scale — a prerequisite for all downstream mechanism and prediction tests. Without this foundation, the entire PROVE_NEW measurement approach fails (A1 violation). Validation against 120-dataset human annotation confirms automated score validity before proceeding.

**Variables** (from Phase 2A):
- Independent: Repository type (HF / OpenML / UCI)
- Dependent: DTS field coverage rate (% of 6 sections scoreable per dataset)
- Controlled: Dataset age (log), task domain

**Verification Protocol**:
1. Sample 500 HF + 200 OpenML + 100 UCI datasets (stratified by task_category and upload year 2016–2024).
2. Apply DTS 6-section binary scoring algorithm using predefined field→section mappings.
3. Compute per-section retrieval rate and overall weighted DTS score for all sampled datasets.
4. Validate automated scores against 120-dataset blinded human annotation (Pearson r ≥ 0.7 threshold).
5. Report coverage rate per repository per section; flag below-threshold sections for remediation strategy.

**Success Criteria** (PoC: Direction-based):
- Primary: Overall API-based DTS coverage rate ≥ 70% across combined corpus
- Secondary: Human-automated correlation r ≥ 0.70 on 120-dataset validation sample

**Failure Response**:
- IF coverage < 70%: PIVOT — supplement with README text parsing or relaxed DTS field mapping
- IF r < 0.70: EXPLORE — refine section-to-field mapping before proceeding to H-M1

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 5 (SH1 existence), Section 1.4 (A1 assumption)

---

**H-M1: Infrastructure → Completeness — Structured Templates Produce Higher DTS Scores**

**Type:** MECHANISM
**Statement**: Under datasets with equivalent age, task domain, and organization type, if repository metadata infrastructure provides structured YAML templates (HuggingFace post-2021) rather than unstructured legacy formats (OpenML, UCI), then DTS-weighted completeness scores will be significantly higher (Cohen's d ≥ 0.3, p < 0.05 Bonferroni) because YAML templates lower documentation friction by pre-defining required fields.

**Rationale** (2-3 sentences):
H-M1 is the first causal step: establishing that infrastructure type predicts completeness differences after controlling for confounds. The within-HF pre/post-2021 DiD provides quasi-experimental leverage to partially disentangle selection effects from template effects (addressing A4 and the key_tension of self-selection bias). Failure here would falsify the infrastructure explanation and reduce the study to observational cross-sectional comparison only.

**Variables** (from Phase 2A):
- Independent: Repository type (structured-template HF post-2021 vs. legacy OpenML/UCI)
- Dependent: DTS-weighted completeness score (inverse-frequency weighted Presence Average)
- Controlled: Dataset age log(years), task domain FE (NLP/CV/tabular/audio/multimodal), organization type (academic/industry)

**Verification Protocol**:
1. Compute DTS completeness scores for full corpus using H-E1 pipeline output.
2. Run one-way ANOVA: completeness ~ repository_type; Tukey post-hoc pairwise tests with Bonferroni correction.
3. Run OLS regression: completeness ~ repo_type + log(age) + task_FE + org_type; extract repo_type coefficient.
4. Run within-HF DiD: completeness ~ post2021_HF + parallel_trends_test (pre-2021 differential trend check).
5. Report Cohen's d effect sizes for HF vs each legacy repository with 95% CI.

**Success Criteria** (PoC: Direction-based):
- Primary: HF mean completeness > OpenML AND HF > UCI (both p < 0.05 after Bonferroni correction)
- Secondary: Cohen's d ≥ 0.3 for HF vs OpenML; DiD interaction term significant (p < 0.05)

**Failure Response**:
- IF H-M1 fails: PIVOT — investigate whether YAML template fields differ from DTS mapping (A4); consider observational re-framing without causal infrastructure claim

**Dependencies**: H-E1

**Source**: Phase 2A Section 1.3 (Causal Step 1), Section 1.6 (P1, P3), Section 1.4 (A4)

---

**H-M2: Completeness → Discoverability — Higher DTS Scores Increase Filter Eligibility**

**Type:** MECHANISM
**Statement**: Under HuggingFace Hub datasets with varying DTS completeness, if a dataset has higher DTS-weighted completeness (particularly task_categories and language field presence), then it has significantly higher search filter eligibility (appearing in filtered API queries) because datasets lacking required YAML fields are mechanistically excluded from all filtered searches.

**Rationale** (2-3 sentences):
H-M2 tests the mechanistic bridge between documentation quality and dataset visibility, providing the causal pathway linking H-M1 (completeness) to H-M3 (downloads). The filter eligibility mechanism is partially directly observable (null card_data → excluded from filtered searches), providing structural rather than purely correlational evidence. Failure of H-M2 does not invalidate H-M3 as a predictive claim, but removes the mechanistic interpretation of the completeness-downloads relationship.

**Variables** (from Phase 2A):
- Independent: DTS-weighted completeness score (continuous, standardized)
- Dependent: Filter eligibility score (binary: dataset appears in task_categories/language filtered HF query = 1)
- Controlled: Dataset age, task domain presence (whether task_categories field exists separately from completeness), organization type

**Verification Protocol**:
1. Select 500 HF datasets and issue 5 filtered API queries (task_categories + language) to assess filter eligibility.
2. Compute DTS section completeness and specifically flag task_categories and language section presence.
3. Run logistic regression: filter_eligibility ~ DTS_completeness + log(age) + org_type.
4. Conduct mediation analysis: completeness → filter_eligibility → downloads (indirect effect via bootstrapped CIs).
5. Report odds ratio for DTS completeness on filter eligibility and standardized indirect path coefficient.

**Success Criteria** (PoC: Direction-based):
- Primary: Logistic β(DTS) > 0 and statistically significant (p < 0.05)
- Secondary: Significant positive indirect mediation path (completeness → eligibility → downloads, p < 0.05)

**Failure Response**:
- IF H-M2 fails: EXPLORE — document as scope limitation; H-M3 still testable as predictive claim without full mediation interpretation

**Dependencies**: H-M1

**Source**: Phase 2A Section 1.3 (Causal Step 2), Jain et al. 2024 (Croissant-RAI discoverability mechanism)

---

**H-M3: Downloads Prediction — DTS Completeness Predicts Dataset Usage (β ≥ 0.15)**

**Type:** MECHANISM
**Statement**: Under ML datasets on HuggingFace Hub (N ≥ 800), if DTS-weighted documentation completeness is higher, then 12-month download counts will be significantly predicted (standardized β ≥ 0.15, p < 0.05) in a pre-registered negative binomial regression controlling for log(age), lagged downloads, task domain FE, and repository FE, because improved discoverability drives downstream dataset adoption.

**Rationale** (2-3 sentences):
H-M3 is the primary testable and publishable prediction — the endpoint of the causal chain and the core novelty claim (first empirical test of completeness → reuse pathway). Pre-registration on OSF prevents p-hacking and confirms confirmatory vs. exploratory status. The explicit disconfirmation threshold (β < 0.05) means failure would constitute a clear null result with scientific value, not an inconclusive test.

**Variables** (from Phase 2A):
- Independent: DTS-weighted completeness score (standardized continuous, inverse-frequency weighted)
- Dependent: Dataset download count (log-transformed 12-month HF downloads, overdispersed count outcome)
- Controlled: log(age), lagged 6-month download count (log-transformed), task domain FE, repository FE, organization type

**Verification Protocol**:
1. Pre-register complete analysis plan on OSF (model specification, β threshold ≥ 0.15, disconfirmation < 0.05) before data collection.
2. Collect 12-month download counts for N ≥ 800 datasets (stratified HF/OpenML/UCI corpus from H-E1).
3. Standardize continuous predictors via StandardScaler; fit pre-registered statsmodels NegativeBinomial model.
4. Extract standardized β₁ (DTS completeness coefficient) with 95% CI; evaluate against ≥ 0.15 threshold.
5. Run sensitivity analysis with unweighted DTS scores and alternate model specifications (OLS on log-downloads).

**Success Criteria** (PoC: Direction-based):
- Primary: Standardized β₁ ≥ 0.15 AND p < 0.05 in pre-registered NB regression
- Secondary: β₁ > 0 in all sensitivity analyses; CI does not include 0

**Failure Response**:
- IF H-M3 fails (β < 0.05): ABANDON usage prediction claim; revise paper to infrastructure-completeness comparison only; H-M1 results sufficient for contribution

**Dependencies**: H-M2

**Source**: Phase 2A Section 1.3 (Causal Step 3), Section 1.6 (P2 — primary prediction), Section 1.1 (core_hypothesis_statement β ≥ 0.15)

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | API coverage ≥ 70%; human validation r ≥ 0.70 | STOP — redesign measurement approach |
| H-M1 | MUST_WORK | HF > OpenML AND HF > UCI (p < 0.05 Bonferroni, Cohen's d ≥ 0.3) | PIVOT — reassess infrastructure-completeness mapping |
| H-M2 | SHOULD_WORK | Logistic β(DTS) > 0, p < 0.05 | EXPLORE — H-M3 still testable; document limitation |
| H-M3 | MUST_WORK | Standardized β₁ ≥ 0.15, p < 0.05 (pre-registered NB regression) | ABANDON — revise to completeness comparison only |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3 (sequential) | 4 weeks |
| **Total** | 4 hypotheses | **6 weeks** |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1: API Field Coverage Insufficient (from A1)**
- Description: HF card_data YAML, OpenML metadata, or UCI ucimlrepo fields do not map adequately to DTS 6 sections
- Severity: **Critical** (invalidates entire measurement approach)
- Likelihood: Medium (HF well-structured; OpenML/UCI less certain)
- Affected Hypotheses: H-E1, H-M1, H-M2, H-M3 (all)
- Mitigation:
  1. Prevention: Pre-survey API field availability before committing to full data collection
  2. Detection: Coverage rate below 70% in H-E1 pilot run
  3. Response: PIVOT to README text parsing; relax DTS section mapping; supplement with manual scoring for UCI

**Risk R2: Download Count Invalidity (from A2)**
- Description: HF download counts include automated/API crawls that inflate counts independent of genuine adoption
- Severity: **High** (invalidates primary DV for H-M3)
- Likelihood: Low (HF tracks unique downloads; prior work used this metric)
- Affected Hypotheses: H-M3
- Mitigation:
  1. Prevention: Use 12-month counts (less inflated than cumulative); check for download count distribution anomalies
  2. Detection: Power-law distribution test; flag datasets with implausibly high counts (>3SD)
  3. Response: Fallback to Papers With Code reference counts as alternative usage proxy for HF datasets

**Risk R3: Age Extraction Failure (from A3)**
- Description: Dataset creation year unreliable or missing across repositories, preventing age confound control
- Severity: **High** (cross-repository comparison invalid without age adjustment)
- Likelihood: Low (HF last_modified, OpenML date_format, UCI year field documented)
- Affected Hypotheses: H-M1, H-M2, H-M3
- Mitigation:
  1. Prevention: Test age field extraction on 50-dataset pilot per repository before full collection
  2. Detection: Missing age rate >20% per repository during H-E1
  3. Response: Estimate age from first appearance date; restrict analysis to datasets with confirmed age

**Risk R4: DiD Validity Failure — YAML Adoption Not Mandatory (from A4)**
- Description: HuggingFace 2021 YAML adoption was optional/gradual, violating DiD parallel trends assumption
- Severity: **Medium** (weakens causal interpretation of H-M1; predictive claims still valid)
- Likelihood: Medium (empirically verifiable during data collection)
- Affected Hypotheses: H-M1 (causal component only)
- Mitigation:
  1. Prevention: Verify YAML adoption policy via HF documentation and GitHub changelog before committing to DiD
  2. Detection: Pre-trends test fails (significant pre-2021 differential trend) or YAML coverage gradual post-2021
  3. Response: Drop DiD; present H-M1 as cross-sectional observational; clearly bound causal language

**Risk R5: Weight Generalization Failure (from A5)**
- Description: Rondina et al. 2025 inverse-frequency weights from 100 popular datasets don't generalize to full population
- Severity: **Medium** (affects weighted DTS score validity; unweighted analysis still feasible)
- Likelihood: Medium (popular dataset sample may over-represent well-documented datasets)
- Affected Hypotheses: H-M1, H-M2, H-M3
- Mitigation:
  1. Prevention: Always run parallel analysis with unweighted DTS as sensitivity check
  2. Detection: Compare weighted vs unweighted score distributions; large divergence signals weight artifact
  3. Response: Report both weighted and unweighted results; derive data-driven weights from own corpus

### 4.2 Risk Summary Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    RISK SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID | Risk                              | Source | Severity | Affected          | Mitigation              |
|----|-----------------------------------|--------|----------|-------------------|-------------------------|
| R1 | API field coverage insufficient   | A1     | Critical | All (H-E1→H-M3)   | README parsing fallback |
| R2 | Download count invalidity         | A2     | High     | H-M3              | PwC reference fallback  |
| R3 | Age extraction failure            | A3     | High     | H-M1, H-M2, H-M3 | Pilot test age fields   |
| R4 | DiD validity — optional YAML      | A4     | Medium   | H-M1 (causal)     | Cross-sectional fallback|
| R5 | Weight generalization failure     | A5     | Medium   | H-M1, H-M2, H-M3 | Unweighted sensitivity  |

Critical Risks: 1 (R1)
High Risks: 2 (R2, R3)
Medium Risks: 2 (R4, R5)
Low Risks: 0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence — no dependencies)
    [GATE 1: MUST_WORK — API coverage ≥70%, r≥0.70]
         │
         ▼
[Level 1 - Core Mechanism Step 1]
    H-M1 ← H-E1
    (Infrastructure → DTS Completeness)
    [GATE 2a: MUST_WORK — HF > OpenML, HF > UCI, d≥0.3]
         │
         ▼
[Level 2 - Core Mechanism Step 2]
    H-M2 ← H-M1
    (Completeness → Filter Eligibility)
    [GATE 2b: SHOULD_WORK — β(DTS) > 0, p<0.05]
         │
         ▼
[Level 3 - Core Mechanism Step 3]
    H-M3 ← H-M2
    (Discoverability → Downloads, β≥0.15)
    [GATE 3: MUST_WORK — pre-registered β≥0.15]
         │
         ▼
[VERIFICATION COMPLETE]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 DEPENDENCY HIERARCHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Level | Hypothesis | Prerequisites | Gate Type  |
|-------|------------|---------------|------------|
| 0     | H-E1       | None          | MUST_WORK  |
| 1     | H-M1       | H-E1          | MUST_WORK  |
| 2     | H-M2       | H-M1          | SHOULD_WORK|
| 3     | H-M3       | H-M2          | MUST_WORK  |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3-4    │ W5      │ W6      │
─────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1           │ ████████│         │         │         │
  [Gate 1]       │         │ ◆       │         │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms
  H-M1           │         │ ████████│         │         │
  H-M2           │         │         │ ████    │         │
  H-M3           │         │         │         │ ████    │
  [Gate 2/3]     │         │         │         │         │ ◆
─────────────────┴─────────┴─────────┴─────────┴─────────┘
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks (2 + 1 + 1 + 1 + 1 gate week)
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3

Total Duration: 6 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3)

Slack Available: 0 weeks (all sequential, full dependency chain)

Duration Breakdown:
- H-E1 (Foundation): 2 weeks (API collection + human validation)
- H-M1 (Mechanisms): 2 weeks (full corpus + ANOVA/DiD analysis)
- H-M2 (Discoverability): 1 week (filter eligibility + mediation)
- H-M3 (Downloads): 1 week (pre-registered NB regression)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 4
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1, H-M2, H-M3)
- Condition: 0 (boundaries documented as constraints)

Verification Phases: 2
1. Foundation (H-E1): API measurement feasibility validation
2. Mechanisms (H-M1 → H-M3): Three-step causal chain testing

Dataset Scale: ~800 datasets minimum (stratified sample for statistical power)
  - HF: 500 (random stratified by task_category × year)
  - OpenML: 200 (stratified by task_type)
  - UCI: ~100 (full population given small size)

Total Duration: 6 weeks
Critical Path Length: 6 weeks
Execution Mode: Sequential chain (fully dependent pipeline)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

```
Step 1: Execute H-E1 (Foundation) — Week 1-2
         API sampling, DTS scoring, human validation
Step 2: Evaluate Gate 1 → If ≥70% coverage AND r≥0.70, proceed
Step 3: Execute H-M1 (Infrastructure→Completeness) — Week 3-4
         Full corpus ANOVA, OLS regression, DiD
Step 4: Evaluate Gate 2a → If HF > OpenML AND HF > UCI, proceed
Step 5: Execute H-M2 (Completeness→Discoverability) — Week 5
         Filter eligibility analysis, mediation
Step 6: Evaluate Gate 2b → Document result; proceed to H-M3 regardless
Step 7: Execute H-M3 (Downloads Prediction) — Week 6
         Pre-registered NB regression (OSF)
Step 8: Evaluate Gate 3 → β≥0.15 determines usage claim validity
Final: Verification complete → Phase 5 (Baseline Comparison) [SKIPPED per config]
       → Phase 6 (Paper Writing)
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: Structured repository infrastructure → DTS completeness → discoverability
            → dataset adoption. Repository infrastructure causally drives documentation
            quality, which mechanistically enables dataset discovery.

Supporting Evidence:
1. Rondina et al. 2025: HF > OpenML > UCI ordering on 100-dataset DTS pilot (BUILD_ON)
2. Pushkarna et al. 2022 Data Cards + HF YAML templates: theoretical-institutional grounding
3. Jain et al. 2024 Croissant-RAI: structured metadata → discoverability mechanistic grounding
4. Koch et al. 2021: Dataset reuse methodology and measurement precedent

Strengths:
- Clear causal mechanism with three independently testable steps
- Pre-registration prevents post-hoc rationalization of results
- Explicit quantitative disconfirmation criteria (β < 0.05 = null result)

Expected Outcomes:
- Primary (P1): HF DTS completeness > OpenML AND > UCI (p < 0.05, d ≥ 0.3)
- Primary (P2): Standardized β₁ (completeness → downloads) ≥ 0.15 (p < 0.05)
- Secondary (P3): DiD interaction term significant within HF pre/post-2021
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): No significant completeness difference between repositories after
controls; completeness does not independently predict downloads (β < 0.05) after
controlling for lagged downloads, age, task FE, repository FE.

Counter-Arguments:
1. Selection confound (key_tension): HF attracts documentation-aware contributors
   regardless of template structure — completeness differences may reflect user base
   characteristics, not infrastructure effects (A4 violation risk)
2. Lagged download dominance: Popular datasets are documented better because they are
   popular, not the reverse — reverse causality makes β ≥ 0.15 uninterpretable as causal
3. Cross-repository incomparability: HF download counts vs. OpenML run counts vs. UCI PwC
   references are different quantities that cannot be directly compared even after normalization

Potential Failure Points:
- R1: API coverage < 70% → H-E1 gate fails → entire chain blocked
- R4: DiD parallel trends fail → H-M1 causal interpretation invalid
- H-M3: Large lagged download coefficient absorbs completeness effect → β < 0.15

Conditions Under Which H0 Would Be Supported:
- If DiD shows no pre/post-2021 change within HF after controlling for selection
- If standardized β₁ < 0.05 with robust controls (completeness does not predict downloads)
- If completeness-downloads correlation disappears after controlling for organization prestige
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:

H-DocComp-v1 presents a pre-registered, falsifiable hypothesis that documentation
infrastructure (template type) drives completeness → discoverability → downloads.
However, H0 raises valid concerns: selection bias (documentation-aware users self-select
to HF), reverse causality (popular datasets receive better documentation), and
cross-repository measurement incomparability.

Resolution Path:
The verification plan addresses this dialectic through:
1. H-E1 (Foundation): Validates measurement tool before any comparison
2. H-M1 DiD design: Partial selection confound mitigation via pre/post-2021 quasi-experiment
3. Pre-registered H-M3: Lagged download control addresses reverse causality
4. Explicit null finding protocol: β < 0.05 threshold defines H0 support clearly

Conditions for Thesis Support:
- H-E1 passes (scoring feasible at scale)
- H-M1 confirms completeness differences (d ≥ 0.3)
- H-M3 confirms β₁ ≥ 0.15 after lagged download control

Conditions for Antithesis Support:
- DiD shows no infrastructure effect on completeness (H-M1 fails after controls)
- Standardized β₁ < 0.05 in pre-registered NB regression (H-M3 null result)
- H-E1 coverage < 70% (measurement approach infeasible)

Nuanced Outcome Possibilities:
1. Full Support: All 4 hypotheses pass → complete causal chain validated → full paper
2. Partial Support (H-M1 pass, H-M3 null): Infrastructure → completeness confirmed, but
   completeness doesn't independently predict downloads → paper revised to measurement contribution
3. No Support: H-E1 or H-M1 fail → H0 supported; pivot to new research direction
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Aspect       | Thesis Position                    | Antithesis Challenge              | Resolution               |
|--------------|------------------------------------|-----------------------------------|--------------------------|
| Measurement  | API-based DTS scoring feasible     | Structural presence ≠ quality     | H-E1 human validation    |
| Infrastructure| Templates drive completeness      | Selection bias (user self-select) | DiD quasi-experiment     |
| Mechanism    | Completeness → filter eligibility  | Other factors dominate visibility | H-M2 logistic regression |
| Downloads    | Completeness predicts reuse (β≥0.15)| Reverse causality / lagged DV   | Pre-registered lagged DV |
| Scale        | Population-level (100K+ datasets)  | Sample bias in pilot findings     | Stratified random sample |

Overall Robustness Score: Medium-High
  (Pre-registration + DiD + explicit null threshold = methodologically sound;
   selection confound partially but not fully addressable)

Confidence in Verification Plan: 0.78
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Structured repository metadata infrastructure → DTS completeness → discoverability → dataset download adoption
- ID: H-DocComp-v1, Confidence: 0.78

**Verification Structure:**
- Mode: Incremental (40% scope reduction from BUILD_ON established facts)
- Sub-Hypotheses: 4 total (H-E: 1, H-M: 3)
- Phases: 2 phases over 6 weeks
- Critical Gates: 3 MUST_WORK + 1 SHOULD_WORK decision points

**Risk Assessment:** Medium (1 Critical, 2 High, 2 Medium)
- Primary concerns: API coverage insufficient (R1), DiD validity for YAML adoption (R4)

**Immediate Action:** Begin Phase 1 with H-E1 (API measurement feasibility)

### 7.2 Conclusions

**Key Achievements:**
- 4 hypotheses across 2 verification phases with clear sequential dependency chain
- H0 formally addressed: β < 0.05 threshold provides explicit disconfirmation criteria
- Pre-registration (OSF) planned for H-M3 to confirm confirmatory analysis status

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: DTS scoring buildable from API with ≥70% coverage + r≥0.70 human validation
- Gate 1: MUST PASS (entire chain blocked if H-E1 fails)

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: Cross-repository completeness ANOVA + DiD (weeks 3-4)
- H-M2: Filter eligibility logistic regression + mediation (week 5)
- H-M3: Pre-registered NB regression β≥0.15 (week 6)
- Gate 2a: H-M1 must pass (MUST_WORK) before H-M2/H-M3 interpretation
- Gate 2b: H-M2 SHOULD pass (failure narrows interpretation, doesn't block H-M3)
- Gate 3: H-M3 must pass (MUST_WORK) for usage prediction claim

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 MUST PASS
   - FAIL → STOP pipeline; redesign measurement approach; consider README parsing
   - PASS → Proceed to Phase 2

2. **Gate 2a (H-M1):** Infrastructure → completeness MUST pass
   - FAIL → PIVOT; drop causal interpretation; consider observational framing only
   - PASS → Proceed to H-M2, H-M3

3. **Gate 3 (H-M3):** Downloads prediction MUST pass
   - FAIL (β < 0.05) → ABANDON usage claim; revise paper scope to measurement contribution

**Open Questions:**
- Was HF YAML frontmatter adoption in 2021 mandatory or optional? (Determines DiD validity)
- Are HF download counts available via API as time series or only cumulative totals?
- Does ucimlrepo provide sufficient metadata for DTS scoring (Motivation, Collection Processes)?

**Recommendations:**

1. **Immediate Actions:**
   - Begin H-E1 with API pilot (50 datasets per repository) to validate coverage before full collection
   - Pre-register H-M3 analysis plan on OSF before any data collection begins

2. **Resource Allocation:**
   - Allocate 6 weeks for critical path (no parallelization possible; fully sequential)
   - Reserve contingency buffer for API rate limiting during H-E1 full corpus collection

3. **Failure Management:**
   - Document all gate decisions in verification_state.yaml
   - Execute PIVOT/EXPLORE/ABANDON strategies per hypothesis failure response

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: 03_refinement.yaml (ID: H-DocComp-v1, Schema: v10.0.0)
- Generated: 2026-03-15T02:56:00Z, 15 discussion exchanges, convergence confirmed

**B. MCP Tool Usage Summary**
- Total MCP calls: 4 (2 × scientificmethod for H-E1 + H-M integrated chain, hypothesis + analysis stages)
- Tools: ClearThought scientificmethod (2 inquiries, 4 stage calls)
- Archon: Pipeline project verified; Phase 2B task set to doing

---

*Generated by YouRA Phase 2B Planning (v6.0) | 2026-03-15*
*stepsCompleted: [step-00-init-environment, step-01-init-parsing, step-02-input-hypothesis, step-03-hypothesis-generation, step-04-hypothesis-inventory, step-05-risk-analysis, step-06-dependency-graph, step-07-timeline-planning, step-08-dialectical-analysis, step-09-summary, step-10-finalize]*
*status: complete*
*completedAt: 2026-03-15T03:10:00Z*
