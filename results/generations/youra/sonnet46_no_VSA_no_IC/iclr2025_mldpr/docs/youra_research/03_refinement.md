# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-21T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- **Gap ID**: gap_1
- **Gap Title**: No Empirical Saturation Onset Threshold (paper_count*) Detected in PwC Leaderboard Data
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 10

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 10

**Convergence Reason**: All 6 criteria met at Exchange 10 (Dr. Ally synthesis)

### Key Insights
1. Goodhart saturation creates a genuine **regime shift** (discrete phase transition), not a smooth trend — this reframing makes change-point detection appropriate and novel.
2. **Residual CoV** (after OLS linear detrending by paper_count) is the correct PELT input — removes the known rho=−0.28 trend before structural break detection.
3. **Two-level analysis** (global paper_count* + task-type-stratified) simultaneously addresses Gap 1 (Q1) and Gap 2 (Q2), amplifying the research contribution.

### Breakthrough Moments
- **Exchange 4 (Prof. Pax)**: Identified that pooling raw CoV values as a series conflates cross-sectional heterogeneity with saturation dynamics. Fix: residual detrending before PELT.
- **Exchange 6 (Prof. Rex)**: Required permutation test for significance and flagged stratum N concern, leading to pre-specified PELT vs. F-test selection rule.
- **Exchange 7 (Dr. Nova)**: Reframed task-type heterogeneity in paper_count* as a positive finding (bridges Gap 1 and Gap 2) rather than a methodological flaw.

---

## Final Hypothesis

### Title
**H-SatOnset-v1**: Benchmark Saturation Onset Threshold Detection in PwC Leaderboard Data

### Core Claim
Under PwC leaderboard benchmark data (N=111 benchmarks with confirmed CoV and paper_count),
**if we apply PELT change-point detection to linearly detrended residual CoV values sorted by paper_count,
then a statistically significant structural break (paper_count*) will be detected**,
because Goodhart saturation dynamics create a genuine regime shift from high-variance CoV (performance exploration)
to low-variance CoV (ceiling compression) as paper counts cross the threshold.

**H₀**: No statistically significant change-point in the CoV-vs-paper_count relationship (permutation p ≥ 0.05 and/or Brown-Forsythe p ≥ 0.05). The rho=−0.28 relationship is a smooth monotonic trend without a regime shift.

### Mechanism (3-Step Goodhart Saturation)
1. **Early phase** (paper_count < paper_count*): Benchmark newly introduced; model families explore diverse approaches. High CoV = genuine performance exploration.
2. **Transition** (paper_count ≈ paper_count*): Community identifies dominant approach. Publication incentives shift from exploration to incremental improvement. CoV begins compressing.
3. **Post-saturation** (paper_count > paper_count*): Goodhart's Law active — community optimizes toward known ceiling. CoV variance collapses. Benchmark loses discriminative power.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| **P1** (primary) | Global paper_count* detectable in PwC N=111 via PELT on residual CoV | Permutation test p < 0.05; paper_count* ∈ [10, 120] | Permutation p ≥ 0.05: no significant change-point |
| **P2** | Post-breakpoint residual CoV has lower variance (Goodhart compression) | Brown-Forsythe p < 0.05; variance ratio (post/pre) < 1.0 | Brown-Forsythe p ≥ 0.05: no variance compression |
| **P3** | Task-type-stratified paper_count* differs across image_classification and NLP | At least one pair with non-overlapping 95% bootstrap CIs | All stratum CIs overlap: no domain-specific thresholds |

---

## Novelty
- **First** application of PELT change-point detection to PwC-internal CoV-vs-paper_count series
- **First** empirically grounded benchmark retirement threshold (paper_count*) for individual benchmarks
- Differentiates from Liao et al. 2022 (aggregate trends, no individual threshold), S_index (composite metric, no change-point), nandomp/AI_Research_Dynamics (performance jumps ≠ CoV saturation, N=25)

---

## Experimental Design

**Data**: PwC N=111 benchmarks, derive.py output (confirmed from H-E1 v2). No new data needed.

**Analysis pipeline**:
1. OLS detrending: `CoV ~ paper_count` → extract residuals
2. PELT: `rpt.Pelt(model='l2', min_size=3).fit(residual_cov_sorted).predict(pen=bic_tuned)`
3. Permutation test: shuffle ×1000, compare null distribution to observed paper_count*
4. Brown-Forsythe: `scipy.stats.levene(pre, post, center='median')` — variance homogeneity
5. Bootstrap: resample 111 ×1000, 95% CI for paper_count* stability (target: CI width ≤ 20 papers)
6. Task-type stratification: repeat 1-5 within strata (N≥20 → PELT; N<20 → F-test only)

**Baselines**: OLS linear (no change-point = H₀), S_index (cross-validation), Liao 2022 temporal saturation (consistency check)

**Tools**: ruptures, statsmodels, scipy — all existing; no new dependencies

---

## Limitations
1. N=111 is a subset of 1,096 total PwC benchmarks (only those with computable CoV)
2. Object_detection stratum N~15-20 may be too small for reliable PELT — pre-specified F-test fallback
3. Cross-sectional pooling (not longitudinal) — assumes benchmarks are IID
4. Single change-point assumption — PELT may detect 2+ (still interpretable)
5. Results may not generalize to non-PwC leaderboard data (HELM, OpenLLM)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-SatOnset-v1 |
| **Discussion Convergence** | All 6 criteria met at Exchange 10 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | 2 (both mitigated — see final_opinions.yaml) |
| **Phase 2B Ready** | YES |

---

*Phase: 2A - Dialogue*
*Architecture: Self-Contained Tikitaka Loop (Independent-Controller Ablation — Claude plays all personas)*
*Generated: 2026-08-21*
