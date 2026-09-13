# Verification Plan: FAIR Compliance Predicts ML Dataset Research Longevity

**Date:** 2026-05-04
**Hypothesis ID:** H-FAIROutcomes-v1
**Confidence:** 0.75
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the conditions of public ML dataset repositories (OpenML post-2018 tabular cohort; HuggingFace vision/NLP datasets with card metadata), if a dataset has higher automated FAIR compliance scores (F-UJI sub-criteria ≥ 0.5 threshold for OpenML; documentation completeness proportion of filled card YAML fields for HuggingFace), then it will show significantly higher longitudinal research engagement (run accumulation trajectories on OpenML; Kaplan-Meier log-rank p < 0.05) and downstream model adoption (download counts and model card citations on HuggingFace; Spearman r > 0.15), because FAIR compliance reduces friction in dataset discovery, access, and integration — making deliberate research engagement more likely and sustained across the dataset's lifetime.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in run accumulation trajectories (Kaplan-Meier survival curves) between high-FAIR (F-UJI ≥ 0.5) and low-FAIR (F-UJI < 0.5) matched OpenML dataset pairs in the post-2018 cohort, and no significant Spearman correlation between documentation completeness score and download counts or downstream model adoption on HuggingFace, after controlling for dataset age, task type, and size.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | OpenML post-2018 tabular cohort + HuggingFace dataset hub (standard) | OpenML provides structured run history, upload dates, and machine-computed qualities enabling survival analysis on research engagement trajectories. HuggingFace provides card YAML and download statistics enabling documentation completeness scoring and adoption measurement. Together they span tabular and vision/NLP modalities for cross-repository comparison. |
| **Model** | Statistical analysis pipeline (no ML model training) | Hypothesis concerns observational prediction of research outcomes from FAIR scores — statistical methods are appropriate; no ML model training required or appropriate. |

**Dataset Details:**
- Source: OpenML Python API (openml.org); HuggingFace Hub API (huggingface.co)
- Path: Accessed programmatically via openml-python and huggingface_hub libraries

**Model Details:**
- Type: Observational study: Kaplan-Meier survival analysis + propensity-score matching + Spearman correlation + linear regression
- Source: scipy, lifelines, sklearn (MatchIt equivalent), pandas

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Unadjusted correlation (no propensity matching) | Likely inflated due to confounding (age, prominence) | Full OpenML dataset (all upload dates) |
| F-UJI aggregate score vs. sub-criteria disaggregation | Lower predictive power than sub-criteria disaggregation (expected) | OpenML post-2018 cohort |
| OpenML machine-computed qualities as IV | Serves as F-UJI instrument validity anchor | OpenML post-2018 cohort |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | FAIR metadata in OpenML post-2018 was predominantly set at publication time, not retroactively | Post-2018 datasets uploaded after FAIR became standard practice in ML; retroactive tagging more likely for pre-2016 datasets | Left censoring contaminates causal ordering; FAIR compliance reflects achieved reuse rather than predicts it; mitigation: add FAIR tagging date as covariate |
| A2 | OpenML run counts reflect deliberate research engagement rather than automated pipeline activity | OpenML runs require specifying algorithm, hyperparameters, and uploading results — higher effort than simple downloads | DV is inflated by pipeline runs; mitigation: filter runs by unique user IDs and non-trivial algorithm variety |
| A3 | F-UJI sub-criteria scores are sufficiently reliable for ML datasets on OpenML | F-UJI validated on Zenodo, Pangaea; sub-criteria for Findable (DOI, metadata richness) and Reusable (license, citation) transfer well to OpenML | IV measurement error attenuates effect estimates; mitigation: validate F-UJI scores against OpenML machine-computed qualities metrics |
| A4 | HuggingFace card completeness (proportion of filled YAML fields) is a valid proxy for FAIR compliance | HuggingFace card fields map to FAIR dimensions: license (Reusable), task_categories (Findable), language/size_categories (Accessible), citation (Reusable) | HuggingFace IV is a noisy FAIR proxy; could produce null results due to measurement error; acknowledged as study limitation |
| A5 | Propensity matching on creation year × task type × dataset size adequately controls for the most important confounders | These three variables capture the primary alternative explanations (older datasets have more time to accumulate runs; larger/prominent datasets more likely to be FAIRified and reused) | Residual confounding from unmeasured variables (institution prestige, marketing); addressed by sensitivity analysis with additional covariates |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First large-scale empirical study linking automated FAIR compliance scores to ML research outcomes across two major repositories.

**Key Innovation:** Multi-repository survival analysis design with F-UJI sub-criteria disaggregation reveals which FAIR dimensions drive ML dataset research longevity — actionable guidance for repository administrators without new data collection.

**Differentiation:**
- Wilkinson et al. (2016): Theoretical framework only; no empirical validation for ML datasets; no outcome measurement
- Vanschoren et al. (2014/2019) — OpenML: Describes infrastructure; does not analyze FAIR compliance effects on reuse outcomes
- Gebru et al. (2021) — Datasheets for Datasets: Defines documentation dimensions but does not measure correlation with outcomes at scale
- Pineau et al. (2020): Reproducibility checklist for papers, not dataset-level FAIR compliance; no large-scale observational study

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | MUST_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
#### H-E1: FAIR Compliance Variance Exists at Scale in OpenML Post-2018 Cohort

**Type:** EXISTENCE
**Statement:** Under the post-2018 OpenML tabular cohort (~3,000–5,000 datasets accessible via API), if F-UJI automated scoring is applied to dataset landing pages, then sufficient variance in FAIR compliance scores will be observed (coefficient of variation > 0.15; bimodal or multi-modal distribution above and below the 0.5 threshold), because ML dataset documentation practices are heterogeneous across uploaders, institutions, and time periods — enabling matched-pairs survival analysis.

**Rationale:** This existence hypothesis validates the precondition for all downstream mechanism hypotheses. Without sufficient FAIR score variance and adequate high/low FAIR matched pairs, survival analysis and regression designs are infeasible. This step also validates the F-UJI instrument for ML datasets and detects retroactive FAIR tagging contamination.

**Variables:**
- IV: F-UJI sub-criteria scores applied to OpenML landing page URLs (17 dimensions, 0–1 per dimension)
- DV: Distribution shape of aggregate FAIR scores (CV, IQR, proportion ≥0.5 and <0.5)
- CV: Upload date (for retroactive tagging diagnostic), dataset size decile

**Verification Protocol:**
1. Query OpenML API with `upload_date >= 2018-01-01`; extract dataset IDs and landing page URLs (expected: 3,000–5,000 datasets).
2. Apply F-UJI tool in parallel (asyncio, rate-limited) to all landing page URLs; extract 17 sub-criteria scores per dataset.
3. Compute aggregate FAIR score per dataset; calculate CV, IQR, proportions above/below 0.5 threshold.
4. Validate F-UJI against OpenML machine-computed qualities: compute Spearman r for overlapping dimensions (Findable, Reusable); confirm r > 0.10.
5. Diagnostic: compute Spearman r between aggregate FAIR score and upload_date; confirm r < 0.20 (no retroactive tagging).

**Success Criteria:**
- Primary: CV > 0.15 for aggregate FAIR scores; both high-FAIR (≥0.5) and low-FAIR (<0.5) groups contain ≥ 500 datasets for propensity matching
- Secondary: F-UJI × OpenML qualities Spearman r > 0.10 (instrument validity); FAIR × upload_date r < 0.20 (no retroactive contamination)

**Failure Response:**
- IF CV < 0.10 (uniform scores): PIVOT — switch IV to OpenML machine-computed qualities; exclude F-UJI
- IF matched pairs < 500: EXPLORE — extend cohort to post-2016 (pre-registered fallback)
- IF FAIR × upload_date r > 0.40: SCOPE — restrict analysis to post-2021 cohort

**Dependencies:** None (foundation)
**Source:** Phase 2A Section 5 (sh1_existence), Section 0 (BUILD_ON/PROVE_NEW), Section 1.4 (A1, A3)

---

#### H-M1: F-UJI Findable Sub-Criteria Predicts Discovery Speed (Time-to-First-Run)

**Type:** MECHANISM
**Statement:** Under post-2018 OpenML tabular datasets with sufficient run history (≥ 10 runs, matched on creation year × task type × size), if F-UJI Findable sub-criteria score (persistent ID, metadata richness, indexed in search) is higher, then time-to-first-run will be significantly shorter (log-rank p < 0.05 on matched high/low Findable pairs; Findable Cox HR > 1.2), because persistent identifiers and rich metadata improve repository search ranking and dataset discoverability.

**Rationale:** Causal Step 1 tests whether the Findable FAIR dimension specifically reduces discovery friction. This is a prerequisite for the full causal chain: if datasets cannot be found faster due to FAIR compliance, the mechanism is broken at the first link. Time-to-first-run is a clean discovery proxy that avoids download count noise.

**Variables:**
- IV: F-UJI Findable sub-criteria score (composite of F1_PID, F2_metadata, F3_search_indexed sub-metrics)
- DV: Time-to-first-run (days from upload_date to first recorded experimental run on OpenML)
- CV: Creation year quartile, task type category, dataset size decile (matched)

**Verification Protocol:**
1. From H-E1 cohort, extract run timestamp data for each dataset using OpenML runs API; compute time-to-first-run per dataset.
2. Perform 1:1 propensity-score matching on creation year × task type × size; split into high/low Findable groups at median Findable sub-score.
3. Fit Kaplan-Meier survival curves for time-to-first-run in matched pairs; apply log-rank test.
4. Fit Cox proportional hazards regression with Findable sub-criteria as primary predictor; compute hazard ratio.
5. Sensitivity analysis: repeat with pre-committed F-UJI ≥ 0.5 aggregate threshold instead of Findable median split.

**Success Criteria:**
- Primary: Log-rank p < 0.05; high-Findable median time-to-first-run < low-Findable median
- Secondary: Cox HR > 1.2 for Findable sub-criteria (20% faster discovery per unit increase)

**Failure Response:**
- IF log-rank p ≥ 0.05: EXPLORE — test Accessible sub-criteria as alternative discovery proxy
- IF sample size insufficient: SCOPE — relax matching criteria to 5:1 nearest-neighbor

**Dependencies:** H-E1 (existence confirmed, sufficient matched pairs available)
**Source:** Phase 2A Section 1.3 (causal step 1), Section 1.6 (P1)

---

#### H-M2: F-UJI Accessible Sub-Criteria Predicts Early Adoption Rate

**Type:** MECHANISM
**Statement:** Under post-2018 OpenML tabular datasets matched on creation year × task type × size, if F-UJI Accessible sub-criteria score (open license, standard file format, documented access procedure) is higher, then total run count within the first 12 months post-upload will be significantly higher (Mann-Whitney U p < 0.05; Accessible regression coefficient β > 0.10 standardized), because open licenses and standard formats lower the barrier to initial experimental use.

**Rationale:** Causal Step 2 tests whether the Accessible FAIR dimension converts discovered datasets into actual experimental use. This bridges the gap between findability and engagement — a dataset can be found but still unused due to access friction (unclear license, non-standard format).

**Variables:**
- IV: F-UJI Accessible sub-criteria score (A1_access_protocol, A1.1_standardized_protocol, A1.2_authentication)
- DV: Total run count within first 12 months post-upload_date (from OpenML run timestamps)
- CV: Creation year quartile, task type, dataset size decile (matched), Findable sub-score (covariate)

**Verification Protocol:**
1. From H-E1 cohort, compute 12-month run count per dataset by filtering run timestamps to [upload_date, upload_date + 365 days].
2. Perform 1:1 propensity-score matching; split into high/low Accessible groups at median Accessible sub-score.
3. Apply Mann-Whitney U test on 12-month run count between matched high/low Accessible groups.
4. Fit linear regression of log(12-month run count + 1) on all F-UJI sub-criteria; extract standardized β for Accessible.
5. Compare Accessible β to Findable β from H-M1 regression to test whether each dimension contributes independently.

**Success Criteria:**
- Primary: Mann-Whitney U p < 0.05; high-Accessible mean 12-month run count > low-Accessible
- Secondary: Accessible standardized β > 0.10 in multi-variate sub-criteria regression

**Failure Response:**
- IF p ≥ 0.05: EXPLORE — test with 6-month window (shorter adoption window may reveal faster effect)
- IF β ≤ 0.05: document as non-significant dimension; Accessible may matter less than Findable/Reusable

**Dependencies:** H-M1 (mechanism chain progressing, Findable confirmed or explored)
**Source:** Phase 2A Section 1.3 (causal step 2), Section 1.2 (variables)

---

#### H-M3: F-UJI Reusable Sub-Criteria Dominates Long-Term Engagement (Primary Mechanism)

**Type:** MECHANISM
**Statement:** Among post-2018 OpenML datasets that achieved ≥ 10 runs within the first 12 months, if F-UJI Reusable sub-criteria score (provenance, usage terms, citation guidance, community standards) is higher (≥ median), then sustained engagement rate — measured as run count slope in months 13–36 — will be significantly steeper, and Reusable will show the largest standardized regression coefficient (β_Reusable > 0.15; larger than Findable, Accessible, Interoperable coefficients), because clear provenance and license guidance enable confident long-term reuse across publications.

**Rationale:** Causal Step 3 is the core prediction of the entire hypothesis — the Reusable dimension is predicted to dominate because ML researchers are primarily deterred from long-term reuse by unclear provenance and license ambiguity, not discoverability. This is the main differentiating contribution of the study: disaggregating FAIR dimensions reveals the dominant driver.

**Variables:**
- IV: F-UJI Reusable sub-criteria scores (R1_usage_license, R1.1_license_identifier, R1.2_provenance, R1.3_community_standards)
- DV: Run count slope in months 13–36 (linear regression coefficient of run count on time within that window, per dataset)
- CV: 12-month run count (baseline engagement level), creation year, task type, dataset size

**Verification Protocol:**
1. From H-E1 cohort, filter to datasets with ≥ 10 runs in first 12 months; compute monthly run counts for months 13–36.
2. Fit per-dataset OLS: run_count ~ month (months 13–36); extract slope coefficient as DV.
3. Fit multi-variate regression: run_count_slope ~ all 17 F-UJI sub-criteria + covariates; extract standardized β for each.
4. Dominance test: confirm β_Reusable > β_Findable, β_Accessible, β_Interoperable using 95% confidence interval comparison.
5. Power analysis: if N_qualifying_datasets < 200, extend to post-2016 cohort (pre-registered fallback).

**Success Criteria:**
- Primary: β_Reusable > 0.15 standardized; Reusable β is the largest positive coefficient among all 4 FAIR dimension groups
- Secondary: Reusable-only model R² > Findable-only + Accessible-only + Interoperable-only combined

**Failure Response:**
- IF β_Reusable ≤ 0.15: EXPLORE — test Findable as dominant dimension; document as paradigm-modifying null result
- IF all β < 0.10: document as true null (no FAIR dimension predicts sustained engagement); equally publishable

**Dependencies:** H-M2 (early adoption confirmed, baseline engagement established)
**Source:** Phase 2A Section 1.3 (causal step 3), Section 1.6 (P2), Section 1.4 (A3)

---

#### H-M4: FAIR Documentation Completeness Predicts Cross-Repository Downstream Adoption (HuggingFace)

**Type:** MECHANISM
**Statement:** Under HuggingFace datasets with structured card YAML metadata (any modality), if documentation completeness score (proportion of filled YAML front-matter fields, 0.0–1.0) is higher, then total download count and downstream model adoption count will be significantly positively correlated (Spearman r > 0.15 for downloads; r > 0.10 for model adoption), after controlling for dataset age decile and modality category, because datasets with higher FAIR-proxy documentation are more easily discovered and adopted as training/evaluation sources in downstream model development.

**Rationale:** Causal Step 4 extends the mechanism to cross-repository downstream effects and validates generalizability beyond OpenML. HuggingFace represents a different repository culture (social signals, model cards) and modality range (vision, NLP, audio). Confirming that documentation completeness predicts adoption across this distinct ecosystem strengthens the FAIR universality claim.

**Variables:**
- IV: Documentation completeness score (proportion of filled fields: license, task_categories, language, size_categories, citation, dataset_info, configs, features)
- DV1: Total download count (log-transformed, from HuggingFace Hub API)
- DV2: Downstream model adoption count (number of model cards listing dataset in `datasets` YAML field)
- CV: Dataset creation date decile, data modality (image/text/audio/multimodal/tabular)

**Verification Protocol:**
1. Enumerate HuggingFace datasets via `huggingface_hub.list_datasets()`; filter to datasets with non-empty card YAML; extract all YAML fields.
2. Compute documentation completeness score per dataset: count filled standard fields / total standard fields (8 canonical fields).
3. Extract download counts via Hub API; search model cards for non-empty `datasets` field; count per-dataset model adoptions.
4. Apply partial Spearman rank correlation: completeness vs. log(download_count + 1), controlling for age decile and modality; repeat for model adoption count.
5. Stratify analysis by modality (image/text/audio) to test whether FAIR effects are modality-universal.

**Success Criteria:**
- Primary: Partial Spearman r > 0.15 for completeness vs. downloads (p < 0.05); r > 0.10 for completeness vs. model adoption (p < 0.05)
- Secondary: Positive direction maintained across at least 2 of 3 main modalities (image, text, audio)

**Failure Response:**
- IF r ≤ 0.15 for downloads: document as null result for HuggingFace; scope claim to OpenML-only; still publishable
- IF model adoption DV too sparse (< 20% datasets have any adoption): use downloads as sole DV; acknowledged pre-registered fallback

**Dependencies:** H-M3 (sustained engagement mechanism confirmed on OpenML; cross-repository test is an extension)
**Source:** Phase 2A Section 1.3 (causal step 4), Section 1.6 (P3), Section 1.4 (A4)

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | CV > 0.15; ≥ 500 matched pairs in each FAIR group | STOP — instrument fails; pivot to OpenML qualities as IV |
| H-M1 | MUST_WORK | Log-rank p < 0.05; high-Findable median time-to-first-run shorter | EXPLORE alternative discovery proxy; document limitation |
| H-M2 | SHOULD_WORK | Mann-Whitney U p < 0.05 for 12-month run count | Document as non-significant; proceed to H-M3 |
| H-M3 | MUST_WORK | β_Reusable > 0.15 and dominates other dimensions | EXPLORE Findable as dominant; document paradigm-modifying null |
| H-M4 | SHOULD_WORK | Partial Spearman r > 0.15 (downloads), r > 0.10 (adoption) | Document as null for HuggingFace; scope to OpenML |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | Weeks 1–2 |
| Gate 1 | — | Week 2 |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3 | Weeks 3–5 |
| Gate 2 | — | Week 5 |
| Phase 2 Extension: Cross-Repository | H-M4 | Week 6 |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Retroactive FAIR tagging contamination | A1 | H-E1, H-M1, H-M2, H-M3 | High |
| R2: Automated pipeline contamination in run counts | A2 | H-M1, H-M2, H-M3 | High |
| R3: F-UJI Interoperability invalidity for ML datasets | A3 | H-M2, H-M3 | Medium |
| R4: HuggingFace card completeness noise | A4 | H-M4 | Medium |
| R5: Propensity matching residual confounding | A5 | All (H-E1 through H-M4) | High |

### 4.2 Mitigation Strategies

**Risk R1: Retroactive FAIR Tagging Contamination**
- Source: A1 (FAIR metadata set at publication time assumption)
- Description: High-reuse datasets may receive retroactive FAIR tagging, reversing causal arrow
- Affected: H-E1 (instrument validity), H-M1–3 (causal ordering)
- Severity: High
- Prevention: Restrict cohort to post-2018 where FAIR practice was established; apply FAIR × upload_date diagnostic
- Detection: Spearman r(FAIR score, upload_date) > 0.20 triggers contamination flag
- Response: PIVOT — add FAIR tagging date as covariate; SCOPE — restrict to post-2021 cohort

**Risk R2: Automated Pipeline Contamination in Run Counts**
- Source: A2 (run counts = deliberate engagement assumption)
- Description: Automated ML pipelines, course projects, or scraping inflate run counts as DV
- Affected: H-M1, H-M2, H-M3 (all using run count as DV)
- Severity: High
- Prevention: Filter runs by unique user IDs and algorithm variety (require ≥ 3 distinct algorithms per dataset-user pair)
- Detection: Heavy-tailed run count distribution with very high-count outliers → inspect manually
- Response: SCOPE — apply stricter user deduplication; exclude datasets with > 95th percentile run counts from primary analysis (run sensitivity test with/without)

**Risk R3: F-UJI Interoperability Sub-Criteria Invalidity**
- Source: A3 (F-UJI reliability for ML datasets)
- Description: Interoperability sub-criteria use Dublin Core / DataCite schemas not aligned with ML datasets → artifactually low scores
- Affected: H-M2 (Accessible), H-M3 (Reusable dominance test)
- Severity: Medium
- Prevention: Pre-validate F-UJI Interoperability sub-criteria against OpenML machine-computed qualities (expected: lower correlation than Findable/Reusable)
- Detection: Interoperability CV < 0.10 (no variance) or correlation with qualities r < 0.05
- Response: SCOPE — exclude Interoperability sub-criteria from regression; test 3-dimension model (Findable + Accessible + Reusable only)

**Risk R4: HuggingFace Card Completeness Noise**
- Source: A4 (card completeness = valid FAIR proxy)
- Description: HuggingFace card YAML fields inconsistently filled; completeness may not reflect actual data quality
- Affected: H-M4 (primary HuggingFace analysis)
- Severity: Medium
- Prevention: Use 8 canonical fields (license, task_categories, language, size_categories, citation, dataset_info, configs, features) standardized across datasets
- Detection: Completeness score distribution has > 60% datasets at 0.0 or 1.0 (no variance)
- Response: SCOPE — use weighted completeness (field importance weights from FAIR dimension mapping); EXPLORE alternative proxy (license completeness only)

**Risk R5: Propensity Matching Residual Confounding**
- Source: A5 (matching adequacy)
- Description: Unmeasured confounders (institution prestige, dataset marketing/promotion) inflate FAIR effects
- Affected: All hypotheses
- Severity: High
- Prevention: Match on creation year × task type × dataset size (3 variables); sensitivity analysis with additional covariates
- Detection: Large standardized mean differences (> 0.10) in unmatched baseline characteristics
- Response: SCOPE — add institution type (academic/industry/government) and file format as additional matching variables; report E-value for unmeasured confounding

### 4.3 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Retroactive FAIR tagging | A1 | High | H-E1, H-M1–3 | Post-2018 cohort + r(FAIR, date) diagnostic |
| R2 | Automated pipeline runs | A2 | High | H-M1–3 | User ID + algorithm deduplication |
| R3 | F-UJI Interoperability invalidity | A3 | Medium | H-M2–3 | OpenML qualities cross-validation; 3-dim fallback |
| R4 | HuggingFace card noise | A4 | Medium | H-M4 | Canonical 8-field completeness; weighted proxy |
| R5 | Residual confounding | A5 | High | All | Extended matching; E-value sensitivity analysis |

Critical Risks: 0 | High: 3 (R1, R2, R5) | Medium: 2 (R3, R4) | Low: 0

---

## 5. Dependency Graph & Visualization

### 5.1 DAG

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root / Foundation]
    H-E1: FAIR Variance Exists (EXISTENCE)
    Gate Type: MUST_WORK | Status: READY
         │
         ▼ [Gate 1: CV > 0.15, ≥500 matched pairs]
[Level 1 - Mechanism: Discovery]
    H-M1: Findable → Discovery Speed (MECHANISM)
    Gate Type: MUST_WORK | Status: NOT_STARTED
         │
         ▼
[Level 2 - Mechanism: Early Adoption]
    H-M2: Accessible → Early Adoption Rate (MECHANISM)
    Gate Type: SHOULD_WORK | Status: NOT_STARTED
         │
         ▼
[Level 3 - Mechanism: Sustained Engagement] ← PRIMARY
    H-M3: Reusable → Long-Term Engagement (MECHANISM)
    Gate Type: MUST_WORK | Status: NOT_STARTED
         │
         ▼ [Gate 2: β_Reusable > 0.15, dominates]
[Level 4 - Mechanism: Cross-Repository]
    H-M4: Completeness → HF Downstream Adoption (MECHANISM)
    Gate Type: SHOULD_WORK | Status: NOT_STARTED
         │
         ▼

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Critical Gates: Gate 1 (H-E1), Gate 2 (H-M3)
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | MUST_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses | Total: 6 Weeks
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis   │ W1-2    │ W3-4    │ W5      │ W6      │
───────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1             │ ████████│         │         │         │
  [Gate 1: W2]     │       ◆ │         │         │         │
───────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Core Mechanisms
  H-M1             │         │ ████████│         │         │
  H-M2             │         │         │ ████    │         │
  H-M3             │         │         │     ████│         │
  [Gate 2: W5]     │         │         │        ◆│         │
───────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2 Extension
  H-M4             │         │         │         │ ████████│
───────────────────┼─────────┼─────────┼─────────┼─────────┤
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
Critical Path: H-E1(2w) → H-M1(2w) → H-M2(1w) → H-M3(1w) → H-M4(1w) = 6w
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

Total Duration: 6 weeks
  - H-E1:  2 weeks (API query + F-UJI batch scoring)
  - H-M1:  2 weeks (run timestamps + KM survival analysis)
  - H-M2:  1 week  (12-month run count + Mann-Whitney)
  - H-M3:  1 week  (months 13-36 slope + regression)
  - H-M4:  1 week  (HuggingFace API + Spearman)

Slack Available: 0 weeks (fully sequential chain)
Bottleneck: H-E1 (F-UJI batch processing 3,000-5,000 URLs)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 5
  - Existence: 1 (H-E1)
  - Mechanism: 4 (H-M1 to H-M4)
  - Condition: 0 (none required)

Verification Phases: 3
  1. Foundation (H-E1) — Weeks 1-2
  2. Core Mechanisms (H-M1, H-M2, H-M3) — Weeks 3-5
  3. Cross-Repository Extension (H-M4) — Week 6

Data Sources:
  - OpenML API (3,000-5,000 datasets post-2018)
  - F-UJI tool (parallelized, ~3,000-5,000 URL requests)
  - HuggingFace Hub API (all datasets with card YAML)
  - HuggingFace model cards API (datasets field)

Statistical Tools: scipy, lifelines, sklearn, pandas
GPU Required: No (statistical analysis only)

Total Duration: 6 weeks
Execution Mode: Sequential chain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: FAIR compliance in ML datasets significantly
predicts longitudinal research engagement and downstream
model adoption, independently of confounders, because FAIR
compliance reduces friction across discovery, access, and
integration throughout a dataset's research lifetime.

Supporting Evidence:
1. Causal mechanism: 4-step chain from FAIR scores to
   discovery friction → first-use → sustained engagement
   → downstream adoption (Wilkinson et al. 2016 framework)
2. Assumptions A1-A5 all supported by prior work and
   technical analysis; mitigation strategies pre-defined
3. Three pre-registered predictions with numerical
   thresholds (log-rank p<0.05, β>0.15, r>0.15)

Strengths:
- Multi-repository design tests FAIR universality vs.
  repository-culture specificity (unprecedented scope)
- Survival analysis reveals dynamic longevity, not static
  snapshot correlation
- F-UJI sub-criteria disaggregation identifies actionable
  investment priorities for repository administrators
- Pre-registerable with numerical thresholds; null results
  equally publishable (no publication bias incentive)

Expected Outcomes:
- P1: KM log-rank p < 0.05 for matched OpenML pairs
- P2: β_Reusable > 0.15, dominates all other dimensions
- P3: HF completeness r > 0.15 downloads, r > 0.10 adoption
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): No significant difference in run
accumulation trajectories between matched high/low FAIR
pairs; no significant correlation between documentation
completeness and downloads or model adoption, after
controlling for age, task type, and size.

Counter-Arguments:
1. Baseline limitations: Unadjusted correlation (confounded
   by age/prominence) could explain apparent FAIR effects
   entirely — FAIR compliance may be a proxy for
   "high-quality, well-publicized dataset"
2. Assumption violations: If A1 fails (retroactive tagging),
   the IV post-dates the DV — FAIR scores would reflect
   achieved reuse, not predict it
3. Scope limitations: OpenML over-represents tabular data;
   HuggingFace card YAML quality is highly variable;
   findings may not generalize beyond these two repositories

Potential Failure Points:
- R1: Retroactive FAIR tagging reverses causal direction
- R2: Automated pipeline runs inflate DV, attenuate effect
- R5: Residual confounding from institution prestige dominates

Conditions Under Which H0 Would Be Supported:
- If FAIR × upload_date r > 0.40 (retroactive contamination)
- If H-E1 CV < 0.10 (insufficient FAIR variance for analysis)
- If β_Reusable ≤ 0.10 in multi-variate regression
  (no dimension dominates; all effects near zero)
- If log-rank p ≥ 0.05 for matched OpenML pairs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment: Hypothesis H-FAIROutcomes-v1 presents
a causally grounded, pre-registered claim that FAIR
compliance predicts ML dataset research longevity. The
thesis is grounded in a 4-step causal mechanism with
falsifiable predictions. However, the antithesis raises
valid concerns: retroactive FAIR tagging (R1), automated
run contamination (R2), and residual confounding (R5) could
individually or jointly explain apparent FAIR effects
without any true causal contribution.

Resolution Path: The verification plan addresses this
dialectic through:
1. Foundation verification (H-E1): Validates F-UJI
   instrument reliability AND detects retroactive tagging
   contamination before any causal claims are made
2. Sequential mechanism testing (H-M1-4): Tests causal
   chain step-by-step; each step uses distinct statistical
   method appropriate to its causal claim
3. Gate conditions: Gate 1 (H-E1) blocks progression if
   instrument fails; Gate 2 (H-M3) is the decisive test of
   the Reusable-dominance prediction
4. Pre-registered sensitivity analyses: Automated run
   filtering (R2) and extended matching (R5) run in parallel
   with primary analysis

Outcome Possibilities:
1. Full Support: All 5 hypotheses pass → FAIR compliance
   is a multi-dimensional predictor of ML dataset longevity;
   Reusable dimension dominates → actionable for repository
   administrators
2. Partial Support: H-E1 + H-M3 pass but others fail →
   Refined claim: Reusable FAIR metadata predicts sustained
   engagement but not initial discovery speed; Findable/
   Accessible effects too weak to measure
3. No Support: H-E1 or H-M1 fails → Antithesis supported;
   FAIR compliance does not predict ML dataset research
   engagement; publish as first empirical null result;
   social infrastructure (HuggingFace signals) may explain
   dataset reuse better than FAIR metadata

Robustness: HIGH — sequential gate design with pre-registered
  numerical thresholds, multi-method replication across two
  repositories, and pre-defined null-result publication path
  ensures scientific integrity regardless of direction.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | FAIR variance exists at sufficient scale for matched analysis | F-UJI may produce uniform low scores for ML datasets | H-E1 CV diagnostic + instrument validity pre-check |
| Mechanism Step 1 | Findable sub-criteria shortens discovery time | Confounders explain discovery speed differences | Propensity matching + Cox regression with sub-criteria features |
| Mechanism Step 3 | Reusable sub-criteria dominates long-term engagement | All FAIR dimensions equally weak (null result) | Multi-variate regression with dominance test |
| Cross-Repository | FAIR effects universal across OpenML + HuggingFace | Repository culture (social signals) explains HF adoption, not FAIR | Partial Spearman controlling for age/modality; modality stratification |
| Performance | FAIR outperforms no-FAIR (significant associations) | Confounded by institutional quality | E-value sensitivity analysis for unmeasured confounding |

**Overall Robustness Score:** High
**Confidence in Verification Plan:** 0.75

---

## 7. Executive Summary

**Main Hypothesis:**
- ID: H-FAIROutcomes-v1, Confidence: 0.75
- Claim: FAIR compliance in ML datasets (F-UJI scores on OpenML; card completeness on HuggingFace) predicts longitudinal research engagement and downstream model adoption, independently of confounders

**Verification Structure:**
- Mode: Incremental (Phase 2A pre-seeded)
- Sub-Hypotheses: 5 total (H-E1 × 1, H-M × 4; no H-C)
- Phases: 3 phases over 6 weeks
- Critical Gates: 2 (Gate 1 at H-E1; Gate 2 at H-M3)
- Data: OpenML API (~3,000–5,000 datasets) + HuggingFace Hub API

**Risk Assessment:** High (3 high-severity risks: R1 retroactive tagging, R2 run contamination, R5 residual confounding)
- Primary concerns: R1 (causal ordering threat) and R2 (DV integrity)
- All risks have pre-defined mitigation strategies with specific detection thresholds

**Immediate Action:** Begin Phase 1 (H-E1) — query OpenML API, apply F-UJI batch scoring, validate instrument

---

## 8. Conclusions

**Key Achievements:**
- 5 hypotheses across 3 phases with clear sequential dependency chain
- H0 fully addressed: null result publishable as "first empirical evidence against assumed FAIR value in ML"
- Scope reduced 67%: BUILD_ON claims (FAIR framework, APIs, F-UJI tool) excluded from verification

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Validate FAIR variance exists at scale; validate F-UJI instrument; detect retroactive tagging
- Gate 1: MUST PASS (CV > 0.15, ≥500 matched pairs)

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: Findable sub-criteria → time-to-first-run (survival analysis) — Week 3–4
- H-M2: Accessible sub-criteria → 12-month run count (Mann-Whitney) — Week 5
- H-M3: Reusable sub-criteria dominates long-term engagement (regression) — Week 5
- Gate 2: H-M3 β_Reusable > 0.15 MUST PASS for primary claim to hold

**Phase 2 Extension: Cross-Repository** (1 week)
- H-M4: HuggingFace documentation completeness → downloads + model adoption (Spearman)

**Critical Decision Points:**
1. **Gate 1 (H-E1):** CV > 0.15 + ≥500 matched pairs
   - FAIL → PIVOT to OpenML qualities as IV; if insufficient, STOP and reassess
   - PASS → Proceed to Phase 2

2. **Gate 2 (H-M3):** β_Reusable > 0.15 and dominates
   - CRITICAL FAIL (β ≤ 0.05) → Antithesis supported; publish null result
   - PARTIAL (0.05 < β ≤ 0.15) → Refined claim; Reusable matters but weakly

3. **H-M4 (SHOULD_WORK):** Failure narrows scope to OpenML; does not invalidate primary claim

**Open Questions:**
- What is the actual post-2018 cohort size with sufficient run counts for matching? (API query needed)
- Does F-UJI Interoperability sub-criteria correlate with OpenML qualities? (instrument validity check)
- Is HuggingFace downstream model adoption DV too sparse for statistical power? (API survey needed)
- Does FAIR score correlate with upload_date? (retroactive tagging diagnostic)

**Recommendations:**
1. **Immediate Actions:** Query OpenML API for cohort size first (pilot before full F-UJI batch); confirm N > 500 per FAIR group before committing to full F-UJI scoring run
2. **Resource Allocation:** Allocate 6 weeks for critical path; build in 1-week buffer for F-UJI batch processing delays; ensure rate-limited async implementation
3. **Failure Management:** Document all failures with specific diagnostic values; execute PIVOT strategies (OpenML qualities fallback for R3; cohort expansion for R1); null results recorded and preserved for publication

---

## Appendices

### A. Phase 2A Reference
- **Source:** `03_refinement.yaml` (ID: H-FAIROutcomes-v1)
- **Gap:** gap-3 — "Lack of Large-Scale Empirical Evidence Linking FAIR Compliance to ML Research Outcomes"
- **Pipeline Project:** Anonymous Pipeline: ML Data Practices & Repositories
- **Phase 2A Convergence:** 15-exchange tikitaka discussion, 6 personas, all 6 convergence criteria met

### B. Statistical Methods Summary
- H-E1: Descriptive statistics (CV, IQR), Spearman correlation (instrument validation)
- H-M1: Kaplan-Meier survival curves, log-rank test, Cox proportional hazards regression
- H-M2: Propensity-score matching (1:1), Mann-Whitney U test, OLS regression
- H-M3: OLS regression with standardized coefficients, dominance analysis, confidence interval comparison
- H-M4: Partial Spearman rank correlation (controlling for age decile, modality), stratified analysis

### C. Sample Size Notes
- OpenML post-2018 cohort: expected ~3,000–5,000 datasets (API-queried)
- Minimum for survival analysis: 500+ matched pairs per FAIR group (pre-registered power analysis)
- HuggingFace: all datasets with card YAML (no size restriction)
- Fallback: extend cohort to post-2016 if matched pairs < 500

---

*Generated by YouRA Phase 2B Planning | 2026-05-04*
*Mode: UNATTENDED | Research: ML Data Practices & Repositories*
*Steps completed: 00–09 | Next: Step 10 (Finalize + verification_state.yaml)*
