# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-09T04:35:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap1
- **Gap Title**: No Predictive Model for Dataset-Level Reproducibility
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met: SPECIFIC core claim, MECHANISM explained, PREDICTIONS defined, NOVELTY articulated, FEASIBILITY established, OBJECTIONS addressed.

### Key Insights
- Reproducibility variance is decomposable: Var_seed + Var_spec + Var_infra
- Component-specific mediation: metadata constrains preprocessing choices, not model hyperparameters
- Early-run analysis addresses reverse causality (popularity driving metadata improvement)
- Absolute effect floor (≥0.01 accuracy) ensures practical significance beyond statistical

### Breakthrough Moments
- Exchange 6: Prof. Vera formalized variance decomposition framework
- Exchange 7: Dr. Ally proposed automated mechanism test via pipeline component extraction
- Exchange 12: Prof. Rex sharpened mediation to component-specific entropy
- Exchange 15: Dr. Nova unified theory as "inverse epistemic entropy"

---

## Final Hypothesis

### Title
Metadata Completeness Predicts Reproducibility Variance via Preprocessing Entropy Reduction

### Core Claim
Under OpenML benchmark datasets with ≥10 matched runs (2019-2024), if metadata completeness score increases (explicit train/test splits, preprocessing specifications, missing value handling, feature semantics, versioning), then reproducibility variance (IQR of performance across matched runs) decreases by ≥20%, because richer documentation constrains preprocessing degrees of freedom, reducing pipeline heterogeneity.

### Mechanism
**Causal Chain: M → E → V_spec**

1. Higher metadata completeness (M) reduces ambiguity about preprocessing choices
2. Reduced ambiguity constrains preprocessing pipeline heterogeneity (E = entropy)
3. Lower pipeline heterogeneity reduces specification-driven variance (V_spec)

**Key Insight**: Documentation constrains preprocessing degrees of freedom, NOT model hyperparameters. This provides a sharp falsifiable pattern for mediation testing.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 | Top-quartile metadata predicts ≥20% IQR reduction AND ≥0.01 absolute accuracy | 95% CI excludes <10% relative | Effect <10% or CI includes 0 |
| P2 | Preprocessing entropy mediates ≥30% of effect | Sobel test p<0.05 | Indirect effect <15% or p>0.10 |
| P2a | High-M shows ≥30% lower preprocessing entropy | Significant difference | No entropy difference |
| P2b | High-M shows NO difference in model hyperparameter entropy | p>0.10 | Significant difference |
| P3 | Effect holds in first-50-runs subsample | Similar magnitude | Effect absent/reversed |
| P4 | Effect persists within RandomForest-only analysis | Similar magnitude | Effect disappears |
| P5 | Pre-2022 model retains ≥75% R² on post-2022 holdout | R² drop <25% | R² drop >50% |
| P6 | Permutation produces <5% of observed effect | Shuffled <5% | Shuffled ≥20% |

---

## Novelty

**Key Innovation**: First study to predict reproducibility from dataset metadata BEFORE experiments run. Reframes reproducibility as a continuous property of datasets (not binary property of papers). Theoretical contribution via "reproducibility as inverse epistemic entropy" framing.

**Differentiation from Prior Work**:
- Kapoor & Narayanan 2022: Identified leakage types post-hoc; we PREDICT pre-experiment
- Reproscreener: Assesses papers; we assess datasets
- rliable: Evaluation tools; we provide predictive guidance
- paper-replay: Verifies after running; we predict before running

---

## Experimental Design

**Dataset**: OpenML Benchmark Suite (200+ datasets, ≥10 matched runs each)

**Model**: Mixed-Effects Regression + Mediation Analysis

**Baselines**:
1. Naive Correlation (no controls)
2. Intrinsic-Stability-Only Model
3. Popularity-Only Model

**Study Phases**:
1. Pilot (50 datasets): Validate pipeline extraction reliability
2. Primary (200+ datasets): Full covariate model
3. Mechanism: Mediation analysis
4. Robustness: Early-run, within-family, temporal, permutation tests

---

## Limitations

- Cannot claim causality without randomized intervention (observational study)
- Generalization to HuggingFace/UCI requires separate validation
- ~30% of OpenML runs have opaque pipeline structure (non-parseable)
- Graph edit distance metric deferred to supplementary analysis
- Seed logging completeness varies across flows

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met across 15 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

---

*Phase 2A Complete. Ready for Phase 2B.*
