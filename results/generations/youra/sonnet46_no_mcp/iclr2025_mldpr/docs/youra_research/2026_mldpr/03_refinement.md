# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-04T00:00:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0 (Inline, UNATTENDED)
- **Gap ID**: gap-3
- **Gap Title**: Lack of Large-Scale Empirical Evidence Linking FAIR Compliance to ML Research Outcomes
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15
- **Convergence**: All 6 criteria met at Exchange 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria satisfied (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS) after 15-exchange Tikitaka discussion.

### Key Insights

1. **Run counts over download counts**: OpenML run counts (deliberate experimental engagement requiring algorithm specification + result upload) are a cleaner DV than download counts — immune to scraping, course projects, and automated pipelines.
2. **Survival analysis framing**: Modeling time-to-50-runs via Kaplan-Meier transforms a static FAIR-reuse correlation into a longitudinal measurement of *dataset research longevity* — more actionable for repository administrators.
3. **Sub-criteria disaggregation**: Using F-UJI's 17 individual sub-criteria as regression features (not aggregate score) identifies which FAIR dimensions drive ML outcomes — directly actionable prioritization guidance.
4. **Post-2018 cohort restriction**: Addresses left censoring from retroactive FAIR tagging (high-reuse datasets may be FAIRified after achieving reuse, reversing the causal arrow).
5. **Multi-repository design**: Cross-repository comparison (OpenML tabular + HuggingFace vision/NLP) tests whether FAIR effects are universal or repository-culture-specific — could reveal "social infrastructure" as HuggingFace alternative.

### Breakthrough Moments

- **Exchange 6** (Prof. Rex): Run counts as DV — eliminates noise from course projects and scraping
- **Exchange 7** (Dr. Nova): Survival analysis on run timestamps — transforms study into longitudinal longevity measurement using 12 years of existing OpenML data
- **Exchange 8** (Prof. Vera): Left censoring threat identified — motivates post-2018 cohort restriction
- **Exchange 11** (Prof. Rex): F-UJI 0.5 threshold pre-committed — avoids circular median-based thresholding
- **Exchange 12** (Dr. Nova): Multi-repository design — HuggingFace card completeness proxy enables cross-repository comparison without F-UJI

---

## Final Hypothesis

### Title
**FAIR Compliance Predicts ML Dataset Research Longevity: A Multi-Repository Survival Analysis**

**Hypothesis ID**: H-FAIROutcomes-v1

### Core Claim

Under the conditions of public ML dataset repositories (OpenML post-2018 tabular cohort; HuggingFace vision/NLP datasets with card metadata), if a dataset has higher automated FAIR compliance scores (F-UJI sub-criteria ≥ 0.5 for OpenML; documentation completeness proportion of filled card YAML fields for HuggingFace), then it will show significantly higher longitudinal research engagement (run accumulation trajectories; Kaplan-Meier log-rank p < 0.05) and downstream model adoption (download counts; Spearman r > 0.15), because FAIR compliance reduces friction in dataset discovery, access, and integration — making deliberate research engagement more likely and sustained across the dataset's lifetime.

### Mechanism

1. **FAIR → reduced discovery friction** (Findable: persistent IDs, rich metadata → dataset found via search)
2. **Reduced friction → higher first-use rate** (Accessible: open license, standard format → lower barrier to initial use)
3. **High Reusable scores → sustained engagement** (clear provenance, usage terms → researchers confidently build on dataset)
4. **Sustained engagement → higher run counts + more downstream model adoptions** (cumulative effect across dataset lifetime)

*The Reusable dimension is predicted to dominate: ML researchers are primarily deterred by unclear provenance and license ambiguity, not discoverability.*

### Null Hypothesis

There is no significant difference in run accumulation trajectories between high-FAIR and low-FAIR matched OpenML dataset pairs in the post-2018 cohort, and no significant Spearman correlation between documentation completeness and download counts or downstream model adoption on HuggingFace, after controlling for dataset age, task type, and size.

---

## Predictions

| ID | Type | Statement | Success Criterion | Falsification |
|----|------|-----------|-------------------|---------------|
| P1 | Primary | High-FAIR datasets (F-UJI ≥ 0.5) show faster run accumulation in matched post-2018 OpenML cohort | Kaplan-Meier log-rank p < 0.05 | p ≥ 0.05 or high-FAIR median time-to-50-runs ≥ low-FAIR |
| P2 | Secondary | "Reusable" F-UJI sub-criteria have largest regression coefficient predicting total OpenML run count | Reusable β > 0.15 and dominates other dimensions | Reusable β ≤ 0.15 or another dimension dominates |
| P3 | Secondary | HuggingFace card completeness correlates with downloads and model adoption | Spearman r > 0.15 for downloads, r > 0.10 for model adoption | r ≤ 0.15 for downloads or r ≤ 0.10 for model adoption |

---

## Novelty

**What's new**: First large-scale empirical study linking automated FAIR compliance scores to ML research outcomes across two major repositories (OpenML + HuggingFace), using survival analysis to model dataset research longevity.

**Key differentiations from prior work**:
- Wilkinson et al. (2016): theoretical FAIR framework — no ML outcome empirical validation
- Vanschoren et al. (2019): OpenML infrastructure description — no FAIR-outcome analysis
- Gebru et al. (2021): documentation dimensions defined — no large-scale outcome correlation
- Pineau et al. (2020): reproducibility checklist for papers — not dataset-level FAIR compliance

**Potential paradigm shift**: If HuggingFace social signals (likes, follows, model adoptions) outperform FAIR metadata as reuse predictors, establishes "social infrastructure" as an alternative to FAIR for ML data quality — a new 3-5 year research agenda.

---

## Experimental Design

| Component | Specification |
|-----------|---------------|
| **Primary data source** | OpenML post-2018 cohort (~3,000-5,000 datasets, upload_date ≥ 2018-01-01) |
| **Secondary data source** | HuggingFace dataset hub (all datasets with card YAML metadata) |
| **IV (OpenML)** | F-UJI sub-criteria scores (17 features, 0–1 per dimension); binary at 0.5 threshold |
| **IV (HuggingFace)** | Proportion of filled card YAML fields (continuous 0–1) |
| **Primary DV (OpenML)** | Time-to-50-runs (Kaplan-Meier survival); total run count |
| **Primary DV (HuggingFace)** | Download count; downstream model adoption count |
| **Controls** | Creation year quartile, task type, dataset size decile, data modality |
| **Matching** | Propensity-score matching on controls within each repository |
| **Statistical tests** | Kaplan-Meier + log-rank (OpenML); Spearman correlation + linear regression (HuggingFace) |
| **Validation** | F-UJI scores cross-validated against OpenML qualities metrics; FAIR×date diagnostic for retroactive tagging |

---

## Limitations

1. **Scope**: OpenML overrepresents tabular/structured data — findings may not generalize to vision/NLP without HuggingFace component
2. **HuggingFace model adoption sparsity**: `datasets` field inconsistently filled for pre-2020 model cards — mitigated by downloads as primary DV
3. **F-UJI Interoperability validity**: May produce artifactually low scores for ML datasets due to schema mismatch with Dublin Core/DataCite standards — mitigated by OpenML qualities cross-validation diagnostic
4. **Statistical power**: Depends on post-2018 matched pairs size — pre-registered power analysis with cohort expansion fallback to post-2016 if needed
5. **Observational design**: Causal claims are quasi-experimental; unmeasured confounders (institution prestige, dataset marketing) may persist after matching

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at Exchange 15 |
| **Clarity Verified** | Yes |
| **Feasibility Confirmed** | Yes — all data sources public, programmatic, no new collection |
| **Remaining Objections** | 3 (all mitigated with existing data) |
| **Phase 2B Readiness** | READY |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Gap: gap-3 | Hypothesis: H-FAIROutcomes-v1 | Exchanges: 15 | Mode: UNATTENDED*
