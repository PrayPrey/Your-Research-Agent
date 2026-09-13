---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning", "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]
status: complete
completedAt: "2026-08-31T00:00:00Z"
generatedAt: "2026-08-31T00:00:00Z"
hypothesisId: "H-MetaMisuse-v1"
researchMode: "incremental"
---

# Verification Plan: Metadata-Observable Dataset Misuse Predicts ML Reproducibility Failure

**Date:** 2026-08-31
**Hypothesis ID:** H-MetaMisuse-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 0. Established Facts & Scope Reduction

**Scope Reduction: 57% (3 of 6 claims are BUILD_ON — not re-verified)**

| Claim | Status | Evidence |
|-------|--------|----------|
| Raff 2019 provides binary reproducibility labels for 255 ML papers, 50.8% reproducible | BUILD_ON | Raff (2019) arXiv:1909.06674 |
| HuggingFace dataset cards follow Datasheets for Datasets schema (Gebru et al. 2021), accessible via public API | BUILD_ON | Gebru et al. 2021; HF Hub API docs |
| OpenML exposes per-dataset run counts and task creation timestamps via openml-python API | BUILD_ON | Vanschoren et al. 2014 |
| Documentation completeness score (HF card field-presence) predicts dataset misuse likelihood | PROVE_NEW | Phase 1 gap confirmation |
| Dataset concentration (HHI) independently predicts reproducibility failure above documentation completeness | PROVE_NEW | Novel claim; D'Amour et al. mechanism, Raff linkage untested |
| intended_use and out_of_scope_use fields dominate field-level importance | PROVE_NEW | Proposed; not yet empirically validated |

**Phase 2B Focus:** Only the 3 PROVE_NEW claims require hypothesis verification (H-E1, H-M1–3).

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the condition of published ML papers from top venues (NeurIPS, ICML, ICLR, JMLR) that use standard benchmark datasets, if a paper relies on a dataset with lower documentation completeness (measured by HuggingFace dataset card field-presence score using the Datasheets for Datasets schema) and/or higher usage concentration (measured by Herfindahl-Hirschman Index over OpenML run counts filtered to pre-publication period), then that paper is more likely to fail independent reproducibility verification (as labeled by Raff 2019), because high concentration signals accumulated dataset-specific artifacts that models overfit to (underspecification; D'Amour et al. 2021), while low documentation completeness increases out-of-context application risk by failing to specify scope boundaries.

### 1.2 Alternative Hypothesis (H0)

There is no significant association between dataset-level metadata-observable misuse signals (documentation completeness score, HHI concentration) and binary reproducibility outcomes in Raff's 255-paper corpus, after controlling for paper-level quality features (equation count, pseudocode presence, hyperparameter reporting).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Raff 2019 Reproducibility Corpus + HF Hub API + OpenML API (standard) | Raff's corpus provides binary reproducibility ground truth (DV). HF Hub API provides documentation completeness scores (IV1). OpenML API provides run counts for HHI (IV2). No new data collection required. |
| **Model** | Logistic Regression (primary) + Random Forest (robustness) | Binary outcome (reproducible/not) with continuous predictors; logistic regression is standard. Random Forest provides non-linearity robustness check. |

**Dataset Details:**
- Source: Raff (2019) published dataset; HuggingFace Hub public API; OpenML Python API
- Path: arXiv:1909.06674 supplementary data; huggingface_hub.list_datasets(); openml.datasets.list_datasets()

**Model Details:**
- Type: statistical classification
- Source: scipy.stats, sklearn.linear_model.LogisticRegression, sklearn.ensemble.RandomForestClassifier

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Paper-quality-only logistic regression (Raff's original features: equations, pseudocode, hyperparameters, reference implementation) | AUC ~0.65–0.70 (estimated) | Raff's 255-paper corpus |
| Intercept-only null model (majority class = reproducible) | Accuracy = 50.8%, AUC = 0.5 | Raff's 255-paper corpus |

**Target:** AUC improvement ≥0.05 from adding dataset-level signals, OR significant LRT p<0.05 for concentration's unique contribution.

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | HF dataset cards for Raff's corpus datasets (2013-2018) are sufficiently populated for field-presence scoring in ≥50% of ~30-60 unique datasets | HF Hub lists cards for major benchmarks retroactively created by community | <50% coverage → missing data dominates; mitigation: OpenML quality measures as fallback |
| A2 | OpenML run counts with pre-publication temporal filtering provide valid proxy for concentration at time of paper writing | OpenML stores task creation timestamps; rank order of concentration stable over time | Temporal confound attenuates HHI effect; mitigation: dataset age proxy + sensitivity analysis |
| A3 | Raff's binary reproducibility label (single annotator) provides generalizable ground truth | Consistent methodology + inter-rater reliability subset; ML Reproducibility Challenge independent validation available | Single-annotator bias; mitigation: replicate on ML Reproducibility Challenge data |
| A4 | Paper-level averaging across datasets is adequate approximation of dataset-level exposure | Most papers use 1-3 datasets; averaging is reasonable | Measurement error attenuates effects; robustness: weight by proportion of experiments per dataset |
| A5 | Relationship between misuse signals and failure is approximately linear on log-odds scale | No strong prior reason for non-linearity; N=255 too small for non-parametric with adequate power | Non-linear effects missed; robustness: Random Forest classification |

### 1.6 Research Gap & Novelty

**First empirical linkage** between metadata-observable dataset misuse signals (documentation completeness, usage concentration) and labeled reproducibility failure outcomes. First use of Raff's corpus to test dataset-level (vs. paper-level) predictors of reproducibility. Bridges two previously-separate literatures: dataset documentation (Gebru et al.) and ML reproducibility auditing (Raff), via programmatic metadata extraction from public APIs. Produces actionable field-level importance results for platform administrators.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Data Infrastructure Feasibility**

**Statement:** Under the condition of top-venue ML papers in Raff's 2019 corpus (N=255), if the data acquisition pipeline is executed (HF Hub API queried for each unique dataset, OpenML API queried for run counts with temporal filtering, Raff 2019 supplementary labels parsed), then the resulting dataset will have ≥50% HF card coverage and functional OpenML timestamp filtering, because these are publicly documented APIs for foundational benchmarks that the research community has retroactively maintained.

**Rationale:**
This hypothesis validates that the empirical foundation is achievable before any statistical modeling. Without sufficient HF card coverage and reliable OpenML temporal data, the primary independent variables cannot be operationalized. Failure here terminates the study.

**Variables:**
- Independent: HF Hub API availability; OpenML task timestamp completeness
- Dependent: HF card coverage rate (% of unique datasets with parseable cards); OpenML pre-publication filter success rate
- Controlled: Raff corpus dataset list (fixed); time window (pre-publication year)

**Verification Protocol:**
1. Extract unique dataset names from Raff 2019 supplementary data; map to HF Hub slugs and OpenML IDs.
2. Query HF Hub API for each dataset card; record field presence for {intended_use, out_of_scope_use, limitations, license, task_categories, dataset_info, provenance}.
3. Query OpenML API for run counts per dataset; apply task_creation_timestamp < paper_publication_year filter; verify filter produces non-trivial counts.
4. Compute coverage statistics: % datasets with HF cards, % with ≥1 completed field, % with valid OpenML temporal filter.
5. Pass criterion: ≥50% HF card coverage AND OpenML timestamp filter functional for ≥70% of datasets.

**Success Criteria (PoC):**
- Primary: HF card coverage ≥50% of Raff's unique datasets
- Secondary: OpenML temporal filtering returns non-empty run counts for ≥70% of datasets; Raff labels parseable as structured CSV/JSON

**Failure Response:**
- IF <50% HF coverage: PIVOT to OpenML quality measures as completeness proxy; reduce scope to datasets present on both platforms
- IF OpenML timestamps unreliable: SCOPE to dataset-age proxy (years since publication); document as limitation

**Dependencies:** None (root hypothesis)

**Source:** Phase 2A Section 2 (Experimental Setup) + A1 + A2 + sh1_existence

---

**H-M1: Documentation Completeness Predicts Reproducibility Failure (P1)**

**Statement:** Under the condition of Raff's 255-paper corpus with matched HF card completeness scores, if documentation completeness score (HF card field-presence, 0–7 normalized to [0,1]) is included as predictor in a logistic regression controlling for paper-quality features (equations, pseudocode, hyperparameters, reference implementation) and dataset age, then the coefficient for completeness will be significantly negative (β < 0, p_BH < 0.05), because low documentation completeness removes the only scalable misuse boundary signal (Gebru et al. 2021), enabling out-of-context dataset application that produces non-reproducible results.

**Rationale:**
This tests the primary prediction (P1) and the core causal step 2: documentation incompleteness → out-of-context application → reproducibility failure. It is the first novel empirical claim and the minimum result required for the paper to contribute to the reproducibility literature.

**Variables:**
- Independent: Documentation completeness score (0–7 normalized; HF card field-presence sum)
- Dependent: Binary reproducibility outcome (Raff 2019: 1=reproducible, 0=not)
- Controlled: Equation count, pseudocode presence, hyperparameter reporting, reference implementation (all from Raff's coding); dataset age (years from dataset publication to paper publication); number of datasets per paper

**Verification Protocol:**
1. Merge dataset-level completeness scores into Raff's paper-level dataset (average across datasets per paper).
2. Fit Model 1: logit(reproducible) ~ completeness + equations + pseudocode + hyperparameters + ref_impl + dataset_age + n_datasets.
3. Extract β_completeness with standard error; apply Benjamini-Hochberg correction across all coefficients.
4. Check sign (must be negative) and corrected p-value (must be < 0.05).
5. Report OR = exp(β_completeness) with 95% CI; must be < 1.0.

**Success Criteria (PoC):**
- Primary: β_completeness < 0 AND p_BH < 0.05 AND OR < 1.0
- Secondary: AUC of Model 1 > AUC of paper-quality-only model (≥ +0.03 improvement acceptable for PoC)

**Failure Response:**
- IF β_completeness ≥ 0: EXPLORE imputation strategy (completeness=0 for missing cards may reverse signal; try mean-imputation sensitivity); document as P1 falsified if robust
- IF p_BH ≥ 0.05: SCOPE to direction-only claim; check if effect exists in ML Reproducibility Challenge data (secondary validation)

**Dependencies:** H-E1

**Source:** Phase 2A Section 1.3 Causal Step 2 + Section 1.6 Prediction P1 + sh2_mechanism

---

**H-M2: Dataset Concentration (HHI) Adds Independent Predictive Power (P2)**

**Statement:** Under the condition of Raff's 255-paper corpus with matched HHI scores and documentation completeness, if dataset concentration (HHI normalized, OpenML pre-publication run counts) is added to the completeness-controlled logistic regression (Model 1 → Model 2), then the likelihood ratio test between models will be significant (χ² p < 0.05) with β_HHI > 0, because high concentration signals artifact overfitting (D'Amour et al. 2021 underspecification mechanism), which is a distinct pathway to failure not captured by documentation quality alone.

**Rationale:**
This tests prediction P2 and causal step 1: benchmark concentration → artifact accumulation → reproducibility failure. It is the highest-impact novel claim — showing structural benchmark monoculture is an independent reproducibility risk justifies dataset diversity requirements at venues and repositories.

**Variables:**
- Independent: Dataset concentration HHI (normalized to [0,1]; OpenML run counts filtered to pre-publication)
- Dependent: Binary reproducibility outcome (Raff 2019)
- Controlled: Same as H-M1 + documentation completeness score (Model 1 baseline)

**Verification Protocol:**
1. Compute HHI per dataset: HHI = Σ(run_count_i / total_runs)² over papers sharing dataset j, filtered to pre-publication.
2. Merge HHI into Raff paper-level dataset (average/max across datasets per paper).
3. Fit Model 2: Model 1 predictors + HHI.
4. Likelihood ratio test: LRT(Model 2 vs. Model 1) — χ² statistic, df=1, p-value.
5. Check β_HHI sign (must be positive: higher concentration = higher failure probability) and LRT p < 0.05.

**Success Criteria (PoC):**
- Primary: LRT p < 0.05 AND β_HHI > 0
- Secondary: AUC(Model 2) > AUC(Model 1) (direction; exact threshold not required for PoC)

**Failure Response:**
- IF LRT p ≥ 0.05: EXPLORE alternative HHI operationalization (max instead of average across paper's datasets; unfiltered run counts); document as P2 falsified if both operationalizations fail
- IF β_HHI negative: investigate temporal confound (high-HHI datasets may be old with better documentation — multicollinearity with completeness); document interaction

**Dependencies:** H-M1

**Source:** Phase 2A Section 1.3 Causal Step 1 + Section 1.6 Prediction P2

---

**H-M3: Field-Level Importance — intended_use and out_of_scope_use Dominate (P3)**

**Statement:** Under the condition of Raff's 255-paper corpus with seven binary field-level indicators replacing the composite completeness score, if a logistic regression with individual field indicators (intended_use_present, out_of_scope_use_present, limitations_present, license_present, task_categories_present, dataset_info_present, provenance_present) is fitted controlling for paper-quality features, then |β_intended_use| > |β_license| AND |β_out_of_scope_use| > |β_provenance| with non-overlapping bootstrapped 95% CIs, because these fields encode the only explicit scope boundaries in the Datasheets schema (Gebru et al. 2021) and their absence directly enables the out-of-context application mechanism.

**Rationale:**
This tests prediction P3 and provides the most actionable result of the study: it identifies which specific datasheet fields platform administrators should prioritize for enforcement. Failure (license or provenance dominating) would challenge the specificity of the Gebru et al. mechanism claim.

**Variables:**
- Independent: Seven binary field indicators (each ∈ {0,1})
- Dependent: Binary reproducibility outcome (Raff 2019)
- Controlled: Paper-quality features (same as H-M1/M2)

**Verification Protocol:**
1. Create seven binary columns for each field in the 7-field completeness set from HF card metadata.
2. Fit Model 3: logit(reproducible) ~ intended_use_present + out_of_scope_use_present + limitations_present + license_present + task_categories_present + dataset_info_present + provenance_present + paper_quality_controls.
3. Bootstrap Model 3 (1000 iterations, stratified by reproducibility outcome) to obtain 95% CIs for each β.
4. Compare: |β_intended_use| vs. |β_license|; |β_out_of_scope_use| vs. |β_provenance|.
5. Check for non-overlapping 95% CIs (both comparisons must pass).

**Success Criteria (PoC):**
- Primary: |β_intended_use| > |β_license| AND |β_out_of_scope_use| > |β_provenance| with non-overlapping 95% CIs
- Secondary: Both intended_use and out_of_scope_use individually significant (p < 0.10, uncorrected) for directional support

**Failure Response:**
- IF CIs overlap: SCOPE claim to "directional evidence" rather than confirmed field dominance; report as exploratory finding
- IF license or provenance dominate: EXPLORE whether temporal confound (license presence correlates with newer/better-maintained datasets) explains the pattern; document as partial P3 falsification

**Dependencies:** H-M2

**Source:** Phase 2A Section 1.6 Prediction P3 + Section 1.3 Causal Step 2 (mechanism specificity)

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | ≥50% HF card coverage + OpenML temporal filter functional | STOP — redesign data sources before proceeding |
| H-M1 | MUST_WORK | β_completeness < 0, p_BH < 0.05 | PIVOT imputation; if robust → P1 falsified, document as negative result |
| H-M2 | SHOULD_WORK | LRT p < 0.05, β_HHI > 0 | Document P2 as unsupported; proceed to H-M3 with scope note |
| H-M3 | SHOULD_WORK | Non-overlapping CIs: intended_use > license AND out_of_scope > provenance | SCOPE to directional/exploratory finding |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3 | 4 weeks (1+1+2) |
| **Total** | 4 hypotheses | **6 weeks** |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Risk–Assumption Mapping

**Risk R1 (from A1): Insufficient HF Card Coverage**

**Source Assumption:** A1 — HF cards for Raff's pre-2020 datasets are sufficiently populated (≥50% coverage threshold)

**Description:** If fewer than 50% of Raff's ~30–60 unique datasets have parseable HF cards, the completeness score distribution will be dominated by zero-imputed values, potentially masking any real signal or introducing systematic bias (all missing = 0 conflates "no documentation" with "card missing").

**Affected Hypotheses:** H-E1 (blocking), H-M1, H-M3

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Before committing to HF Hub as primary source, run a coverage check script against Raff's dataset list as the first task of Phase 4.
2. **Detection:** Coverage rate < 50% triggers immediate pivot assessment; report coverage as data quality metric.
3. **Response:**
   - PIVOT: Supplement with OpenML quality measures (dataset_quality field) as a second completeness proxy; create composite score.
   - SCOPE: Restrict analysis to datasets with HF cards (complete-case analysis) + sensitivity analysis with imputed zeros.

**Early Warning Indicators:** Coverage rate < 60% on first 20 datasets checked; >30% of datasets map to no HF slug.

---

**Risk R2 (from A2): OpenML Temporal Filter Unreliable**

**Source Assumption:** A2 — OpenML task creation timestamps enable valid pre-publication filtering for HHI computation

**Description:** If OpenML task timestamps are sparse, backdated, or unreliable, the HHI values computed will not accurately reflect concentration at time of paper writing. This would attenuate the HHI effect toward zero even if the true relationship exists.

**Affected Hypotheses:** H-M2

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Query OpenML API for a sample of 5 well-known datasets (MNIST, CIFAR-10, GLUE) and verify timestamp coverage and plausibility before full data collection.
2. **Detection:** If >30% of task entries lack valid timestamps, switch to fallback proxy.
3. **Response:**
   - PIVOT: Use dataset age (years between dataset publication and paper publication year) as HHI proxy — captures maturation-based concentration without requiring run timestamps.
   - SCOPE: Run sensitivity analysis comparing timestamp-filtered HHI vs. age-proxy; report both operationalizations.

**Early Warning Indicators:** >30% missing task timestamps; MNIST/CIFAR-10 HHI values implausibly low given known overuse.

---

**Risk R3 (from A3): Single-Annotator Bias in Raff's Labels**

**Source Assumption:** A3 — Raff's binary labels are generalizable ground truth beyond one annotator's methodology

**Description:** If Raff's reproducibility assessments reflect idiosyncratic methodology rather than a consistent standard, the DV may have high noise, reducing statistical power and making any signal difficult to detect even if the true relationship is real.

**Affected Hypotheses:** H-M1, H-M2, H-M3

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Pre-check Raff's inter-rater reliability statistics (reported in the paper) before analysis; document measurement reliability as a study limitation.
2. **Detection:** If effect sizes are unexpectedly small (OR < 1.2), consider whether label noise is attenuating effects.
3. **Response:**
   - SCOPE: Treat Raff's labels as noisy proxy; focus on direction and significance rather than magnitude for PoC claims.
   - PIVOT: Use ML Reproducibility Challenge 2021 as secondary validation to check replication in an independent labeling scheme.

**Early Warning Indicators:** High null-model deviance in logistic regression suggesting high outcome variability; no variables significant even with expected effect sizes.

---

**Risk R4 (from A4): Averaging Across Datasets Introduces Measurement Error**

**Source Assumption:** A4 — Paper-level aggregation (averaging dataset scores across papers using multiple datasets) is an adequate operationalization

**Description:** For papers using 2–3 datasets with very different completeness/HHI profiles, simple averaging may wash out the effect of the most influential dataset, attenuating regression coefficients.

**Affected Hypotheses:** H-M1, H-M2

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Code number of datasets per paper as a control variable (already planned); weight by experiment proportion if that information is available in Raff's coding.
2. **Detection:** If R4 attenuates effects, maximum-dataset operationalization (use scores for the dataset with the most experiments) will show larger effects.
3. **Response:**
   - SCOPE: Run robustness check: max-dataset operationalization vs. average; report if results differ substantially.
   - PIVOT: If multi-dataset papers drive attenuation, analyze single-dataset papers as a cleaner subgroup.

**Early Warning Indicators:** Significant interaction between n_datasets and completeness/HHI in regression.

---

**Risk R5 (from A5): Non-Linear Relationship Missed by Logistic Regression**

**Source Assumption:** A5 — Relationship between misuse signals and failure is approximately linear on log-odds scale

**Description:** If the true relationship is threshold-based (e.g., completeness below 3/7 fields suddenly increases failure risk), logistic regression will underestimate the effect and may fail to reach significance even if the pattern is real and strong.

**Affected Hypotheses:** H-M1, H-M2, H-M3

**Severity:** Low

**Mitigation Strategy:**
1. **Prevention:** Already planned: Random Forest as robustness check for non-linearity detection.
2. **Detection:** If RF feature importances show completeness/HHI as top predictors but LR coefficients are non-significant, non-linearity is likely.
3. **Response:**
   - SCOPE: Report RF results alongside LR; frame as exploratory evidence if LR fails but RF confirms importance.

**Early Warning Indicators:** RF AUC substantially higher than LR AUC (> 0.05 gap); partial dependence plots show step-function patterns.

---

### 4.2 Risk Summary Table

| ID | Risk | Source | Severity | Affected Hypotheses | Mitigation |
|----|------|--------|----------|---------------------|------------|
| R1 | Insufficient HF card coverage (<50%) | A1 | High | H-E1(blocking), H-M1, H-M3 | Coverage check first; OpenML quality fallback |
| R2 | OpenML temporal timestamps unreliable | A2 | High | H-M2 | Pre-check sample; dataset-age proxy fallback |
| R3 | Single-annotator label bias (Raff) | A3 | Medium | H-M1, H-M2, H-M3 | Document limitation; ML RepChallenge secondary validation |
| R4 | Averaging attenuation across multi-dataset papers | A4 | Medium | H-M1, H-M2 | Max-dataset robustness check; single-dataset subgroup |
| R5 | Non-linear relationship missed by LR | A5 | Low | H-M1, H-M2, H-M3 | Random Forest robustness check; partial dependence plots |

**Critical Risks:** 0
**High Risks:** 2 (R1, R2)
**Medium Risks:** 2 (R3, R4)
**Low Risks:** 1 (R5)

---

## 5. Dependency Graph (DAG) & Timeline

### 5.1 Dependency Graph

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 — Root: Foundation]
    H-E1: Data Infrastructure Feasibility
    (no prerequisites)
         │
         ▼ [Gate 1: MUST_WORK]
[Level 1 — Core Mechanism: Documentation]
    H-M1: Documentation Completeness Predicts Failure (P1)
    (prerequisite: H-E1)
         │
         ▼ [Gate 2: MUST_WORK]
[Level 2 — Core Mechanism: Concentration]
    H-M2: HHI Adds Independent Predictive Power (P2)
    (prerequisite: H-M1)
         │
         ▼ [Gate 3: SHOULD_WORK]
[Level 3 — Field-Level Specificity]
    H-M3: intended_use/out_of_scope_use Dominate (P3)
    (prerequisite: H-M2)
         │
         ▼ [Gate 4: SHOULD_WORK]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Depth: 4 levels
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis   │ W1-2   │ W3     │ W4     │ W5-6   │
───────────────────┼────────┼────────┼────────┼────────┤
PHASE 1: Foundation
  H-E1             │ ██████ │        │        │        │
  [Gate 1]         │      ◆ │        │        │        │
───────────────────┼────────┼────────┼────────┼────────┤
PHASE 2: Mechanisms
  H-M1             │        │ ██████ │        │        │
  [Gate 2]         │        │      ◆ │        │        │
  H-M2             │        │        │ ██████ │        │
  [Gate 3]         │        │        │      ◆ │        │
  H-M3             │        │        │        │ ██████ │
  [Gate 4]         │        │        │        │      ◆ │
═══════════════════════════════════════════════════════════════════
Legend: ██ = Active work  │  ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3

Total Duration: 6 weeks
  Formula: 2 (H-E1) + 1 (H-M1) + 1 (H-M2) + 2 (H-M3)
  Note: H-M3 allocated 2 weeks due to bootstrapping requirement

Slack Available: 0 weeks (fully sequential chain)
Parallelization: None possible (each step requires prior output)
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
- Condition: 0

Verification Phases: 2
1. Foundation (H-E1): 2 weeks
2. Mechanisms (H-M1–3): 4 weeks

Total Duration: 6 weeks
Critical Path Length: 6 weeks
Execution Mode: Sequential chain
Tools Required: huggingface_hub, openml-python, scipy, sklearn
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

**Step 1:** Execute H-E1 (Data Infrastructure) — Week 1–2
**Step 2:** Evaluate Gate 1 → If ≥50% HF coverage + OpenML functional: proceed; else STOP and redesign
**Step 3:** Execute H-M1 (Documentation Completeness → P1) — Week 3
**Step 4:** Evaluate Gate 2 → If β_completeness < 0, p_BH < 0.05: proceed; else explore pivot options
**Step 5:** Execute H-M2 (HHI Concentration → P2) — Week 4
**Step 6:** Evaluate Gate 3 → If LRT p < 0.05, β_HHI > 0: proceed; else document as P2 unsupported
**Step 7:** Execute H-M3 (Field-Level Specificity → P3) — Week 5–6
**Step 8:** Evaluate Gate 4 → Determine scope of P3 claim (confirmed / directional / exploratory)
**Final:** PoC Verification complete → Phase 4.5 Synthesis

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Metadata-observable dataset misuse signals (documentation completeness + HHI concentration) causally contribute to ML reproducibility failure through two independent mechanisms: artifact overfitting (high concentration) and out-of-context application (low documentation), both grounded in established theory (D'Amour et al. 2021; Gebru et al. 2021).

**Supporting Evidence:**
1. D'Amour et al. (2021) provide the underspecification mechanism for Step 1 (concentration → artifact overfitting); high OpenML run counts are a metadata-observable proxy.
2. Gebru et al. (2021) explicitly designed the Datasheets schema to prevent out-of-context use via intended_use and out_of_scope_use fields — absence of these fields removes the only scalable scope boundary signal.
3. Raff (2019) establishes that 49.2% of top-venue papers fail reproduction and provides structured paper-quality controls (equations, pseudocode, hyperparameters) as confound covariates, enabling causal attribution.

**Strengths:**
- No new data collection required; all sources are existing public APIs and published datasets
- Paper-quality confound addressed by including Raff's own coding as controls (validated by Prof. Rex)
- Three independently falsifiable predictions (P1/P2/P3) with BH correction for multiple comparisons
- All 5 expert perspectives rated STRONG or MODERATE in Phase 2A round table

**Expected Outcomes:**
- Primary (P1): β_completeness < 0, p_BH < 0.05, OR < 1.0
- Secondary (P2): LRT p < 0.05, β_HHI > 0
- Tertiary (P3): |β_intended_use| > |β_license| with non-overlapping 95% CIs

### 6.2 Antithesis

**Null Hypothesis (H0):** After controlling for paper-level quality features, dataset-level metadata signals show no significant association with reproducibility outcomes in Raff's 255-paper corpus.

**Counter-Arguments:**
1. **Selection confound:** Well-written papers may both choose better-documented datasets AND reproduce better — even with paper-quality controls, residual confounding from researcher quality/thoroughness could fully explain any observed correlation.
2. **Coverage bias:** If HF card completeness is skewed toward newer/popular datasets, the completeness scores may not reflect the actual documentation state at time of paper writing (2013–2018 papers predate HF's 2020 launch by 2–7 years).
3. **Sample size limitation:** N=255 with binary outcome, ~30–60 unique datasets, and multiple predictors leaves limited degrees of freedom; any detected effects may not survive cross-validation.

**Potential Failure Points:**
- R1: <50% HF card coverage collapses completeness signal into noise (zero-imputation dominates)
- R2: OpenML timestamp unreliability washes out temporal HHI signal
- R3: Single-annotator label noise reduces statistical power below detectable thresholds

**Conditions Under Which H0 Would Be Supported:**
- β_completeness ≥ 0 OR p_BH ≥ 0.05 (P1 falsified)
- LRT p ≥ 0.05 for Model 1 vs. Model 2 (P2 falsified)
- Paper-quality controls fully account for outcome variance with near-zero residual from dataset-level signals

### 6.3 Synthesis

**Balanced Assessment:**

The thesis presents a well-grounded, mechanistically motivated hypothesis with existing infrastructure for empirical testing. The antithesis identifies legitimate threats primarily centered on data quality (HF card coverage) and confounding (researcher quality proxy). The dialectical tension is resolvable because Phase 2A explicitly designed H-E1 to test feasibility before committing to mechanism testing, and the paper-quality confound is addressed by design (Raff's own codings as controls).

**Resolution Path:** The verification plan addresses this dialectic sequentially:
1. H-E1 tests whether the empirical foundation is achievable at all (antithesis concern about coverage addressed first)
2. H-M1 tests P1 in a controlled design that includes the most plausible confound as a covariate
3. H-M2 uses LRT (incremental model design) to test whether dataset signals add beyond the confound
4. H-M3 provides field-level specificity that would be extremely unlikely to arise from general confounding

**Nuanced Outcome Possibilities:**
1. **Full Support (thesis wins):** H-E1 passes, H-M1 significant (p_BH < 0.05), H-M2 LRT significant, H-M3 CIs non-overlapping → all three PROVE_NEW claims confirmed
2. **Partial Support (thesis refined):** H-E1 passes, H-M1 significant, H-M2 marginal (p = 0.06–0.15), H-M3 directional → paper reports P1 as primary finding, P2/P3 as suggestive
3. **Antithesis supported:** H-E1 fails (<50% coverage) OR H-M1 non-significant → dataset-level signals not detectable in Raff's corpus with current operationalization; negative result with clear boundary conditions

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Data Feasibility | Public APIs sufficient for full operationalization | Pre-2020 datasets may have sparse HF cards | H-E1 empirical coverage check before any modeling |
| Documentation Effect | Completeness predicts failure (P1, mechanism grounded in Gebru et al.) | General researcher quality confound | Paper-quality controls from Raff's own coding; incremental R² design |
| Concentration Effect | HHI adds above completeness (P2, mechanism in D'Amour et al.) | Temporal validity of OpenML timestamps | Pre-check + dataset-age proxy as fallback |
| Field Specificity | intended_use/out_of_scope_use dominate (P3) | License/provenance could dominate if temporal confound present | Bootstrap CIs; interaction analysis if needed |
| Sample Power | N=255 adequate for OR>1.5 (>80% power per Prof. Pax) | Multiple predictors reduce effective df | Conservative BH correction; pre-registration to prevent HARKing |

**Overall Robustness Score:** Medium-High (strong mechanism + adequate power; primary vulnerability is data coverage)

**Confidence in Verification Plan:** 0.75

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Metadata-observable dataset misuse signals (doc completeness + HHI concentration) predict ML reproducibility failure above paper-quality controls.
- ID: H-MetaMisuse-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A Dialogue available; 57% scope reduction applied)
- Sub-Hypotheses: 4 total (H-E1: existence, H-M1–3: mechanism chain)
- Phases: 2 phases over 6 weeks
- Critical Gates: 4 decision points (Gate 1: MUST_WORK; Gates 2–4: SHOULD_WORK after Gate 2 MUST_WORK)

**Risk Assessment:** Medium
- Primary concerns: HF card coverage for pre-2020 datasets (R1, High); OpenML timestamp reliability (R2, High)

**Immediate Action:** Begin Phase 2C for H-E1 experiment design; implement HF Hub coverage check as first executable task.

### 7.2 Conclusions

**Key Achievements:**
- 4 sub-hypotheses spanning 2 verification phases (Foundation + Mechanisms)
- H0 explicitly addressed: controlled design with Raff's paper-quality covariates
- All 3 PROVE_NEW claims mapped to falsifiable predictions with pre-specified thresholds and BH correction

**Verification Execution Order:**

**Phase 1: Foundation (2 weeks)**
- H-E1: HF Hub ≥50% coverage + OpenML temporal filter functional
- Gate 1: MUST PASS — blocking

**Phase 2: Core Mechanisms (4 weeks)**
- H-M1: Documentation completeness → β_completeness < 0, p_BH < 0.05 — MUST PASS (Gate 2)
- H-M2: HHI concentration → LRT p < 0.05, β_HHI > 0 — SHOULD PASS (Gate 3)
- H-M3: Field specificity → non-overlapping CIs for intended_use/out_of_scope — SHOULD PASS (Gate 4)

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL (<50% HF coverage) → STOP, pivot to OpenML quality fallback, re-assess operationalization
   - PASS → Proceed to Phase 2

2. **Gate 2 (Primary Mechanism):** H-M1 must pass
   - FAIL (β_completeness ≥ 0 or p_BH ≥ 0.05) → Explore robustness; if robust, document P1 as falsified; evaluate whether study still publishable as negative result
   - PASS → Proceed to H-M2

3. **Gates 3–4 (Secondary/Tertiary):** Failures narrow but do not invalidate
   - FAIL → Document as unsupported secondary claims; paper reports P1 + negative P2/P3

**Open Questions:**
- How many of Raff's ~30–60 unique datasets have HF cards? (Empirical check required before Phase 4 commit)
- Is Raff's supplementary data available as structured CSV/JSON or requires PDF extraction?
- Are OpenML task creation timestamps reliable for pre-publication filtering (random sample check needed)?

**Recommendations:**

1. **Immediate Actions:**
   - Begin Phase 2C with H-E1 experiment design (data acquisition protocol)
   - Pre-register analysis plan on OSF/AsPredicted before any data pull (mandatory per Prof. Rex's objection)

2. **Resource Allocation:**
   - Allocate 6 weeks for critical path; HF card coverage check in Week 1 determines viability
   - Reserve contingency: if R1 materializes, 1–2 additional weeks for OpenML quality fallback integration

3. **Failure Management:**
   - Document all failures with root cause analysis per gate
   - If H-M1 fails: treat as publishable negative result (absence of evidence is evidence of absence given adequate power)

### 7.3 Appendices

**Appendix A: Phase 2A Reference**
- Source: `docs/youra_research/03_refinement.yaml` (ID: H-MetaMisuse-v1)
- Convergence: All 6 criteria met after 8 exchanges; 6 expert agents participated

**Appendix B: MCP Tool Usage Summary**
- Total simulated MCP calls: 2 (ClearThought scientificmethod: H-E1 verification + H-M integrated chain)
- ABLATION NOTE: ClearThought and Archon MCP not available in this session; reasoning executed inline per ablation mode instructions

---
