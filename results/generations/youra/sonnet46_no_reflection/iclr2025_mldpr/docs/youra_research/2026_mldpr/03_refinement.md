# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-19T00:00:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap1
- **Gap Title**: No Generalized Cross-Domain Automated Benchmark Saturation Scoring System
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All six convergence criteria met — SPECIFIC (precise Cox model operationalization), MECHANISM (domain-specific signals → shared hazard calibration), PREDICTIONS (C-index ≥ 0.70, ≥2× HR, ≥12mo lead time), NOVELTY (first survival analysis on benchmark panel data), FEASIBILITY (PWC + OpenML + ConStat fully available), OBJECTIONS (circularity, confounds, measurement invariance all addressed by design).

### Key Insights
- S_index (Polo et al. 2026) is LLM-specific and retrospective; cross-domain health requires domain-calibrated features, not a single formula
- "Universal" benchmark health means **shared hazard calibration structure**, not raw score comparability — the key conceptual reframe that unblocked the discussion
- Discriminative power decay (Kendall τ rank stability over time) is a cleaner, objective ground truth than human retirement decisions, avoiding sociological confounds
- Panel survival analysis on (benchmark × quarter) snapshots elegantly resolves the small-N collapse event problem
- Feature/outcome separation is critical: BCBHS features must be causally upstream signals (robustness gap, contamination probability, rank stability), not concurrent symptoms of collapse

### Breakthrough Moments
1. **Prof. Pax** proposed replacing human retirement labels with discriminative power decay as ground truth — eliminated sociological confound cleanly
2. **Prof. Rex** reframed "universal" from raw score equality to shared hazard calibration — resolved the commensurability objection that had blocked earlier exchanges
3. **Dr. Ally** specified the Cox survival model with pre-registered falsification thresholds — converted a vague framework to a testable scientific claim
4. **Prof. Rex's** insistence on time-split validation (≤2022 train / 2023–2025 test) and leave-one-domain-out evaluation crystallized the experimental design

---

## Final Hypothesis

### Title
**BCBHS: Benchmark-Calibrated Health Score for Cross-Domain Discriminative Collapse Prediction**

**Hypothesis ID**: H-BCBHS-v1

### Core Claim
Under heterogeneous ML benchmarks (CV, NLP, tabular — Papers With Code + OpenML corpora), if we compute domain-specific health estimators H_d(B,t) — robustness gap normalized by historical variance (CV), contamination-adjusted S_index via ConStat (NLP), block-bootstrapped Kendall τ rank stability (tabular) — and calibrate these into a shared Cox proportional hazards model controlling for benchmark age, submission volume, and model scale growth trend, then BCBHS(B,t) will predict time-to-discriminative-collapse T(B) with C-index ≥ 0.70 and lowest-quintile benchmarks showing ≥2× hazard ratio for collapse within 24 months, because benchmark health degrades through domain-specific measurable signals whose shared hazard calibration structure enables prospective early warning ≥12 months before community consensus.

**Null Hypothesis (H0)**: BCBHS(B,t) does not significantly predict time-to-discriminative-collapse after controlling for age, submission volume, and model scale growth (Cox hazard ratio = 1.0, p > 0.05; C-index ≤ 0.60).

### Mechanism
Benchmark health degrades via four causal steps:
1. **Over-optimization**: As submissions accumulate, models increasingly overfit test set statistical properties rather than generalizing the underlying task
2. **Domain-specific signal emergence**: Robustness gap widens (CV), contamination probability increases (NLP), rank correlation stabilizes prematurely (tabular) — all measurable before community consensus forms
3. **Shared hazard structure**: Despite domain-specific manifestations, the underlying risk of discriminative collapse shares a common structure detectable via a shared Cox model — tested via CFA/CCA with partial metric invariance required
4. **Early warning window**: BCBHS signal precedes community consensus by ≥12 months, enabling proactive benchmark replacement

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| **P1** (Primary) | BCBHS(B,t) predicts time-to-discriminative-collapse with C-index ≥ 0.70 under time-split validation; lowest-quintile benchmarks show ≥2× hazard ratio | C-index ≥ 0.70; HR ≥ 2.0; p < 0.05; ΔC-index ≥ 0.05 over slope+variance+age baseline | C-index < 0.65; HR < 1.5; or baseline matches BCBHS (ΔC-index < 0.02) |
| **P2** | BCBHS provides ≥12-month median lead time before discriminative collapse in CV and NLP | Median lead time ≥ 12 months; ≥70% collapse events preceded by threshold crossing | Median lead time < 6 months; or <50% events preceded by crossing |
| **P3** | Domain-specific signals share partial metric invariance; shared Cox model improves LODO prediction ΔC-index ≥ 0.03 | CFI ≥ 0.90 for configural+metric invariance; LODO ΔC-index ≥ 0.03 | Metric invariance rejected; LODO shared model underperforms domain-specific baseline |

---

## Novelty

**What's New:**
- First survival analysis framework for ML benchmark lifecycle prediction on panel leaderboard data
- Two-stage architecture: domain-specific signal extraction → shared hazard calibration (resolves commensurability problem)
- "Universal" redefined as shared risk prediction structure, not a single formula

**Differentiation from Prior Work:**
- **S_index (Polo et al. 2026)**: LLM-specific, retrospective, single formula → BCBHS is cross-domain, prospective, domain-calibrated
- **Roelofs 2019**: CV only, post-hoc characterization → BCBHS adds NLP/tabular, prospective survival prediction
- **evaleval/benchmark-saturation**: Implements S_index for LLM leaderboards without cross-domain extension or prospective validation

---

## Experimental Design

**Corpus:**
- Papers With Code leaderboard panel (CV + NLP, 3000+ benchmarks × 6 years, 2018–2025)
- OpenML benchmark panel (tabular, 21,000+ datasets, standardized evaluation protocols)
- ConStat (eth-sri) for contamination probability estimates on NLP benchmarks
- evaleval/benchmark-saturation for S_index cross-validation

**Model:** Domain-stratified Cox Proportional Hazards + Multi-group CFA for invariance testing

**Baselines (nested ablation):**
1. Slope-only Cox model
2. Slope + score variance Cox model
3. Slope + variance + benchmark age Cox model *(primary ablation)*
4. S_index-only Cox model *(NLP domain)*

**Validation:** Time-split (≤2022 train / 2023–2025 test); leave-one-domain-out; rolling-origin evaluation; bootstrap CI (1000 iterations)

---

## Limitations

- Measurement invariance across domains is empirically unverified — partial metric invariance may be the honest finding (tested via CFA as P3)
- Papers With Code submission completeness bias: only competitive results are typically submitted, potentially biasing rank distributions — sensitivity analysis required
- Small-N for true collapse events (~20–40 historical events) constrains latent factor modeling — panel survival analysis partially mitigates this; power analysis to be pre-registered
- Kendall τ > 0.90 collapse threshold requires domain-specific calibration sensitivity analysis
- RL benchmarks excluded from primary analysis (insufficient structured leaderboard data)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | 15 exchanges; converged via iterative hypothesis refinement from UBHS concept to BCBHS survival framework |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Measurement invariance (addressed as P3); submission completeness bias (addressed via sensitivity analysis) |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
