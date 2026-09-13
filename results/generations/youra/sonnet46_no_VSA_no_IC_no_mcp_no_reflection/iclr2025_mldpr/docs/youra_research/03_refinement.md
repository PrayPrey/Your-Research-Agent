# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-31T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (IC Ablation — no orchestrate_exchange.py)
- **Gap ID**: gap-2
- **Gap Title**: Absence of Empirical Linkage Between Metadata-Observable Dataset Misuse and Reproducibility Failure Outcomes
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 8

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 8

**Convergence Reason**: All 6 convergence criteria met — SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS addressed

### Key Insights
1. The paper-quality confound (well-written papers both reproduce better AND choose better-documented datasets) is addressable because Raff already coded paper-quality control variables (equations, pseudocode, hyperparameters)
2. Documentation completeness operationalized as field-presence score is more rigorous than task-type drift because it requires no paper-text NLP — fully automatable from HF Hub API
3. Concentration as independent predictor (P2) is the highest-impact novel claim: structural benchmark monoculture is a reproducibility risk independent of documentation quality
4. Field-level importance (P3) is the most actionable result: identifies which specific datasheet fields platform administrators should enforce

### Breakthrough Moments
- Exchange 3 (Dr. Sage): Framing concentration as independent predictor "above and beyond documentation quality" — makes P2 novel vs. replicating Gebru et al.
- Exchange 4 (Prof. Pax): Confirmed paper-level modeling (N=255) provides adequate power — resolved sample size concern
- Exchange 6 (Prof. Rex): Raff's existing quality features serve as paper-quality controls — transforms blocking confound into a design choice

---

## Final Hypothesis

### Title
Metadata-Observable Dataset Misuse Predicts ML Reproducibility Failure (H-MetaMisuse-v1)

### Core Claim
Under the condition of published ML papers from top venues (NeurIPS, ICML, ICLR, JMLR) that use standard benchmark datasets, if a paper relies on a dataset with lower documentation completeness (HuggingFace dataset card field-presence score, 0-7) and/or higher usage concentration (HHI over OpenML pre-publication run counts), then that paper is more likely to fail independent reproducibility verification (Raff 2019 binary label), because high concentration signals accumulated dataset-specific artifacts that models overfit to (underspecification; D'Amour et al. 2021) while low documentation completeness increases out-of-context application risk by failing to specify scope boundaries.

### Mechanism
1. **Concentration → artifact accumulation**: High-HHI datasets are used by many papers; models implicitly overfit dataset-specific artifacts rather than learning generalizable patterns (D'Amour et al. 2021 underspecification mechanism)
2. **Documentation incompleteness → out-of-context application**: Without `intended_use` and `out_of_scope_use` fields, researchers lack scope boundary signals, enabling task-type mismatch without awareness
3. **Artifact overfitting + misuse → reproducibility failure**: Results that depend on dataset artifacts break when independently replicated in slightly different setups

---

## Predictions

| ID | Statement | Test | Success Criterion |
|----|-----------|------|-------------------|
| **P1** (primary) | Documentation completeness negatively predicts failure | Logistic regression, β_completeness with BH correction | β < 0, p_BH < 0.05 |
| **P2** | Concentration adds predictive power above completeness | Likelihood ratio test Model 1 vs. Model 2 | LRT p < 0.05, β_HHI > 0 |
| **P3** | intended_use / out_of_scope_use dominate field-level coefficients | Field-level logistic regression with bootstrapped CIs | |β_intended_use| > |β_license|, non-overlapping CIs |

---

## Novelty

**What's new:** First empirical linkage between metadata-observable dataset misuse signals and labeled ML reproducibility failure outcomes using existing public APIs and Raff's published ground-truth corpus.

**How it differs:**
- vs. Gebru et al. 2021: provides empirical validation that specific fields predict failure (not just proposing the schema)
- vs. Raff 2019: adds dataset-level predictors not in original model (what dataset you choose matters above how well you document methods)
- vs. D'Amour et al. 2021: operationalizes underspecification mechanism with metadata-observable proxies and tests against ground-truth labels

---

## Experimental Design

**Ground truth**: Raff 2019 binary reproducibility labels (N=255 papers, ~30-60 unique datasets; arXiv:1909.06674)

**Independent variables**:
- Documentation completeness: HF Hub API → field-presence score (0-7, normalized)
- Usage concentration: OpenML API → HHI over pre-publication run counts (normalized)
- Field-level indicators: 7 binary features for field-level importance analysis (P3)

**Controls**: Raff's paper-quality features (equations, pseudocode, hyperparameters, reference implementation); dataset age; number of datasets per paper

**Models**:
- Model 0: Intercept only (null baseline)
- Model 1: Paper-quality controls + completeness (Raff's baseline + P1)
- Model 2: Model 1 + HHI concentration (P2 via LRT)
- Model 3: Field-level indicators replacing completeness composite (P3)

**Secondary validation**: ML Reproducibility Challenge 2021 (Papers with Code) — directional replication

**Implementation**: openml-python + huggingface_hub + scipy/sklearn; estimated 2-3 weeks

---

## Limitations

- **Top-venue selection bias**: Raff's corpus restricted to NeurIPS/ICML/ICLR/JMLR; results may not generalize to workshop papers or preprints
- **HF card temporal validity**: Cards for pre-2020 datasets may be retroactively created with inflated completeness; dataset age covariate partially controls this
- **Single annotator (Raff)**: Binary labels from one researcher introduce annotator bias; mitigated by secondary validation on ML Reproducibility Challenge data
- **Temporal HHI**: OpenML run counts today ≠ concentration at time of writing; mitigated by pre-publication timestamp filtering (feasibility pending verification)
- **Missing metadata**: Datasets without HF cards imputed as completeness=0 (conservative; may underestimate true effect)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | 8 exchanges, all 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Open Questions** | HF card coverage for pre-2020 datasets (verify before implementation); Raff quality features in machine-readable form; OpenML timestamp reliability |
| **Recommended Next Step** | Phase 2B — begin with feasibility check: (1) download Raff corpus data, (2) check HF card availability for top-20 datasets in corpus, (3) verify OpenML task timestamps |

---

*Phase 2A Complete — Self-Contained Tikitaka Loop (IC Ablation)*
*Personas: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex*
*Papers read: Raff 2019, D'Amour et al. 2021, Gebru et al. 2021*
