# Adversarial Review — Round 2 (R2)
# Numerical Verification and Credibility Check
# Generated: 2026-05-03T14:35:00Z

**Paper:** Human→AI Annotation Drift (06_paper_r1.md — R1 revised version)
**Round:** R2 — Verification and Credibility
**Personas:** Accuracy Checker · Skeptical Expert
**MCP Status:** Serena MCP unavailable (TEST environment) — direct file reads substituted

---

## Executive Summary

| Severity | Found | Description |
|----------|-------|-------------|
| FATAL    | 0     | — |
| MAJOR    | 1     | H-M1 validation report shows inconsistent β_exposure values across documents |
| MINOR    | 1     | See human_review_notes |

**Recommendation:** MINOR_REVISION — 1 MAJOR issue requires clarification/fix before finalization.

---

## Numerical Verification Log (Serena-equivalent direct file reads)

Files read for numerical verification:
- `h-m2/04_validation.md` — primary coefficient data
- `h-m1/04_validation.md` — AI-typicality projection data
- `h-e1/04_validation.md` — existence experiment data
- `h-m1/04_checkpoint.yaml` — post-fix experiment results (authoritative)
- `verification_state.yaml` — pipeline state (authoritative)
- `paper/065_ground_truth.yaml` — Phase 6 ground truth

---

## Ground Truth Verification Table (R2 — Extended)

| Claim | Paper (r1) | 04_validation.md | Checkpoint/VS | Match | Notes |
|-------|-----------|------------------|---------------|-------|-------|
| β_L early = −0.025 | ✓ | −0.0248 (h-m2) | ✓ | ✓ | |
| β_L late = +0.056 | ✓ | +0.0555 (h-m2) | ✓ | ✓ | |
| Δβ_L = +0.080 | ✓ | 0.0803 (h-m2) | ✓ | ✓ | |
| early_auc = 0.495 | ✓ (added R1) | 0.4952 (h-m2) | ✓ | ✓ | |
| late_auc = 0.511 | ✓ (added R1) | 0.5111 (h-m2) | ✓ | ✓ | |
| n_directional = 1/3 | ✓ | 1 (h-m2) | ✓ | ✓ | |
| β_exposure = 0.041 | ✓ | **0.0000 (h-m1 report)** | **0.0407 (checkpoint)** | ⚠ | MAJOR-005 |
| tercile F = 82.92 | ✓ | **33.226 (h-m1 report)** | **82.92 (VS)** | ⚠ | MAJOR-005 |
| placebo_p = 0.48 | ✓ | 0.4800 (h-m1) | ✓ | ✓ | |
| HH-RLHF rows = 160,800 | ✓ | 160,800 (h-m2) | ✓ | ✓ | |
| WebGPT rows = 19,578 | ✓ | N/A (h-m1) | 19,578 (VS) | ✓ | |
| interaction_p = 1.0 | ✓ | 1.000 (h-e1) | ✓ | ✓ | |
| Bonferroni β_L p=0.000 | ✓ | 0.000 (h-e1) | ✓ | ✓ | |
| VIF < 1.03 | ✓ | 1.029 max (h-e1) | ✓ | ✓ | |
| bootstrap_iters = 2,000 | ✓ | 2000 (h-m2) | ✓ | ✓ | |
| placebo_iters = 200 | ✓ | — | 200 (VS) | ✓ | |
| topic_imbalance_p = 4e-275 | ✓ | 4.0e-275 (h-m2) | ✓ | ✓ | |

---

## MAJOR-005: H-M1 Validation Report vs. Checkpoint Discrepancy

### Finding

The `h-m1/04_validation.md` report table shows:
```
β_exposure: 0.0000
tercile F-stat: 33.226
```

But `h-m1/04_checkpoint.yaml` (line 144) and `verification_state.yaml` (authoritative pipeline state) show:
```
beta_exposure: 0.0407
beta_exposure_p: 2.05e-05
tercile_f_stat: 82.92
```

The paper cites `β_exposure = 0.041, p = 2.05×10⁻⁵; tercile F = 82.92` — matching the checkpoint, not the validation report table.

### Root Cause Analysis

The `04_validation.md` was generated from the **initial mock-data run** before the mock-data violation fix was applied. The report header explicitly states: "Mock Data Fix Summary — RESOLVED (Attempt 1/5)" — meaning the report documents the fix process, but the **results table at the top reflects the pre-fix run** (β_exposure = 0.0000, F = 33.226). The post-fix results are in the checkpoint file (β_exposure = 0.0407, F = 82.92).

The `04_checkpoint.yaml` line 144 reads: `experiment_info: PanelOLS worker FE; β_exposure=0.0407, p=2.05e-05` — this is the authoritative post-fix result.

### Paper Impact

The paper correctly cites the post-fix results (from checkpoint and verification_state). However:
1. The `04_validation.md` serves as the primary documentation artifact for Phase 4
2. A reviewer examining the Phase 4 report would see β_exposure=0 and F=33.226
3. This creates a documentation gap: the paper's numbers cannot be traced back to the validation report without accessing the checkpoint file

### Severity Assessment

**MAJOR** — not because the paper numbers are wrong (they match the authoritative checkpoint), but because:
- The validation report is the canonical Phase 4 documentation
- Numbers in the paper (β_exposure=0.041, F=82.92) cannot be directly verified from the validation report
- A reproducibility reviewer would flag this inconsistency

### Required Fix

**Option A (Preferred):** Add a footnote or appendix note in the paper:
> "H-M1 results are from the post-mock-data-fix experiment run documented in `h-m1/04_checkpoint.yaml`. The `04_validation.md` report table reflects a pre-fix run; authoritative metrics are in the checkpoint file."

**Option B:** Update `h-m1/04_validation.md` to reflect the post-fix results. (Outside paper scope — pipeline artifact fix.)

**For the paper:** Add a data availability/reproducibility note in §4.4 or as a footnote in §5.2 clarifying that H-M1 results come from the validated post-fix run, with checkpoint reference.

---

## Mathematical Validity Checks

### Check 1: β_L Reversal Magnitude

Paper: Δβ_L = +0.080 ≈ "2.6× the early-round CI half-width"

Verification:
- Early CI: [−0.043, −0.006], half-width = (0.043 − 0.006)/2 = 0.0185
- Δβ_L = 0.0803
- Ratio = 0.0803 / 0.0185 = 4.34×, not 2.6×

**MINOR discrepancy:** Paper says "approximately 2.6×" but calculation gives ~4.3×. The CI half-width should be measured as the full CI width / 2 = (0.043 − 0.006) / 2 = 0.0185, giving ratio ≈ 4.3. If measured as distance from point estimate to CI bound: early_β = −0.0248, upper CI = −0.006, distance = 0.0188; ratio = 0.0803/0.0188 = 4.27×. Neither calculation gives 2.6×.

**Correction needed:** Change "approximately 2.6×" to "approximately 4× the early-round CI half-width" or remove the specific multiplier and simply state "substantially exceeds the CI width."

**Severity:** MINOR (does not affect the main finding — CI non-overlap is the criterion, not the multiplier)

### Check 2: Tercile Design Consistency

Paper §5.2: "between-group tercile design on WebGPT; tercile F = 82.92, p ≈ 1.4×10⁻³⁶"
Checkpoint: `tercile_f_stat: 82.92, tercile_p: 1.4e-36` ✓

The tercile design is correctly described as between-group (worker IDs absent → score-magnitude tercile proxy). ✓

### Check 3: Bootstrap Iterations Consistency

H-E1 uses 200 bootstrap iterations; H-M2 uses 2,000. Paper §4.4 states "2,000 stratified bootstrap resamples" — this is correct for H-M2 (primary result). The paper should note H-E1 used 200 iterations (currently mentioned only in §3.5 "200 iterations"). ✓ Adequately distinguished.

### Check 4: Bonferroni Correction Application

Paper §4.3: "family-wise Bonferroni-corrected threshold is α = 0.05/3 ≈ 0.017"
Actual correction in H-E1: α = 0.0167 (= 0.05/3, matching). ✓

### Check 5: Sign Consistency Claim

Paper: "All three stylistic feature deltas are positive (sign_consistent = true)"
H-M2 report: Δβ_L=+0.0803, Δβ_H=+0.0210, Δβ_S=+0.0116 — all positive. ✓

---

## Baseline Fairness Assessment

**No Phase 5 baseline comparison was performed** (`skip_baseline_comparison=true` in module.yaml, `baseline_comparison.status: NOT_STARTED` in verification_state.yaml). The paper does not claim performance against external baselines — the comparison framework uses:
- Random temporal split (internal control)
- Q_early frozen predictor (internal control)
- Placebo AI-typicality vector (internal discriminant validity control)

These are methodological controls, not competitive baselines. **No baseline fairness issues found** — the paper is correct to note this is a first-of-kind measurement with no existing methods to compare against.

---

## Credibility Assessment

### Signal-Performance Coherence

The near-chance AUC (0.495, 0.511) alongside statistically significant coefficient estimates requires coherent explanation. The R1 revision added the AUC note; it is adequate. One additional point: **the tercile F-stat of 82.92 with p≈1.4×10⁻³⁶ alongside β_exposure=0.041 is mathematically coherent** — large F with small β is expected when n is large (19,578 rows, high statistical power detects small effects).

### Claim Scope Appropriateness

The paper claims "first computational evidence" — this is defensible given the review of prior work in §2. The scope (population-level, not causal individual-level) is explicitly stated. ✓

---

## R2 Issue Summary

### MAJOR Issues (1)

| ID | Section | Issue | Fix |
|----|---------|-------|-----|
| MAJOR-005 | §5.2, §4.4 | H-M1 validation report shows β_exposure=0 and F=33.226 while paper cites checkpoint values (β_exposure=0.041, F=82.92). Documentation gap creates reproducibility concern. | Add footnote/note in §5.2 or §4.4 clarifying that H-M1 results are from post-mock-data-fix run (h-m1/04_checkpoint.yaml), not the pre-fix validation report table. |

### MINOR Issues (1 — for human_review_notes)

| ID | Section | Type | Issue |
|----|---------|------|-------|
| MINOR-004 | §5.1 | Clarity | "approximately 2.6× the early-round CI half-width" — calculation gives ~4.3×, not 2.6×. Change to "approximately 4×" or remove specific multiplier. |

---

## Persuasiveness Re-assessment (Post-R1 Fixes)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Concrete numbers, AAI incompleteness now flagged |
| Problem clear in 1 minute? | PASS | §1 paragraph 1 leads with reversal |
| Novelty clear in 2 minutes? | PASS | Gap section explicit |
| Figure 1 self-explanatory? | PASS | Caption added in R1 |
| Would continue reading? | YES | |
| False novelty claims | 0 | |
| Unfair baselines | 0 | No external baselines claimed |
| Overclaims | 0 | AAI incompleteness now properly flagged |
| Missing limitations | 0 | AUC + multiple comparisons added in R1 |

**persuasiveness_passed: true** (all MAJOR-001 through MAJOR-004 resolved in R1)

---

## Summary for Revision Agent

**Priority 1 — MAJOR-005:** Add footnote or note in §5.2 or §4.4 explaining that H-M1 reported metrics (β_exposure=0.041, tercile F=82.92) come from the post-mock-data-fix run captured in `h-m1/04_checkpoint.yaml`. The `04_validation.md` table reflects a pre-fix run.

**Priority 2 — MINOR-004:** Correct "2.6×" to "approximately 4×" in §5.1 (the multiplier for Δβ_L vs. CI half-width). Or simply remove the specific ratio — the non-overlapping CI is itself sufficient evidence.

---

*Review generated by Phase 6.5 Adversarial Review workflow v2.0, Round 2*
*Personas: accuracy_checker, skeptical_expert*
*File verification: h-m2/04_validation.md, h-m1/04_validation.md, h-m1/04_checkpoint.yaml, h-e1/04_validation.md, verification_state.yaml*
