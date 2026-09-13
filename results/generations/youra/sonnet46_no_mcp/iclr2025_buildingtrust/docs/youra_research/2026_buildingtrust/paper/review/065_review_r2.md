# Adversarial Review Report — Round 2
**Paper:** Epistemic Reliability as a Latent Dimension in LLM Trustworthiness
**Review Round:** R2 — Verification and Credibility
**Personas:** Accuracy Checker, Skeptical Expert
**Input Paper:** 06_paper_r1.md (post-R1 revision)
**Generated:** 2026-04-30T16:50:00Z
**Mode:** UNATTENDED (inline execution)
**Note:** Serena MCP unavailable (no-mcp mode) — verification performed directly from loaded Phase 4/5 source files

---

## Numerical Verification Log

All numerical claims in 06_paper_r1.md verified against:
- h-e1/04_validation.md (loaded)
- h-m1/04_validation.md (loaded)
- h-m2/04_validation.md (loaded)
- 065_ground_truth.yaml (loaded)
- verification_state.yaml (loaded)

---

## Ground Truth Verification Table

| Claim | Paper R1 Value | Ground Truth Source | Match |
|-------|---------------|---------------------|-------|
| ρ(ECE, TruthfulQA%) | −0.758 | h-e1: −0.758; h-m1: −0.758 | ✅ |
| CI(ECE, TruthfulQA%) | [−0.894, −0.504] | h-e1: [−0.894, −0.504] | ✅ |
| ρ(ECE, AdvGLUE drop) | −0.719 | h-e1: −0.718; h-m2: −0.7185 | ✅ rounding |
| CI(ECE, AdvGLUE) Section 5.1 | [−0.882, −0.386] | h-m2: [−0.8822, −0.3862] | ✅ rounding |
| ρ(ECE, ANLI drop) | −0.667 | h-e1: −0.667; h-m2: −0.6667 | ✅ rounding |
| CI(ECE, ANLI) | [−0.821, −0.407] | h-e1: [−0.821, −0.407] | ✅ |
| ρ(ECE, Brier) | +0.723 | h-e1: +0.723 | ✅ |
| CI(ECE, Brier) | [+0.325, +0.899] | h-e1: [+0.325, +0.899] | ✅ |
| ρ(Brier, TruthfulQA%) | −0.738 | h-e1: −0.738 | ✅ |
| CI(Brier, TruthfulQA%) | [−0.894, −0.460] | h-e1: [−0.894, −0.460] | ✅ |
| Factor 1 variance explained | 72.1% | h-e1: 72.1% | ✅ |
| KMO adequacy | 0.879 | h-e1: 0.879 | ✅ |
| Tucker's congruence | 1.000 | h-e1: 1.000 | ✅ |
| Survival fraction | 0.943 | h-m1: 0.943 | ✅ |
| Construct validity ρ(ECE,Brier) | 0.775 | h-m1: 0.775 | ✅ |
| Discriminant validity (abs) | 0.082 | h-m1: abs(−0.082)=0.082 | ✅ |
| LOO-AUC composite | 0.739 | h-m2: 0.7386 | ✅ rounding |
| LOO-AUC MMLU-only | 0.688 | h-m2: 0.6875 | ✅ rounding |
| ΔAUC | 0.051 | h-m2: 0.0511 | ✅ rounding |
| ΔAUC CI | [−0.194, 0.449] | h-m2: [−0.1944, 0.4492] | ✅ rounding |
| ΔAUC CI width (0.643) | 0.643 | Calculated: 0.6436 | ✅ |
| Survival fraction "5.7%" (R1 fix) | 5.7% | 1−0.943=0.057=5.7% | ✅ R1 fix correct |
| N models | 30 | verification_state: 30 | ✅ |
| Families | 8 | verification_state: 8 | ✅ |
| Parameter range | 7B–70B | verification_state: 7B–70B | ✅ |
| H-E1 gate | PASS | verification_state: PASS | ✅ |
| H-M1 gate | PASS | verification_state: PASS | ✅ |
| H-M2 gate | PARTIAL | verification_state: PARTIAL | ✅ |
| H-M3 status | NOT EXECUTED | verification_state: NOT_STARTED | ✅ |
| Overall verdict | PARTIALLY_SUPPORTED | verification_state: PARTIALLY_SUPPORTED | ✅ |

---

## Mathematical Validity Analysis

**Check 1: ΔAUC CI width**
- CI [−0.194, 0.449]: width = 0.643 ✅ (paper states 0.643 in Section 5.3)

**Check 2: Survival fraction → 5.7% (R1 fix)**
- 1 − 0.943 = 0.057 = 5.7% ✅ (corrected by R1 revision)

**Check 3: LOO-AUC rounding consistency**
- 0.7386 rounds to 0.739 ✅; 0.6875 rounds to 0.688 ✅; 0.0511 rounds to 0.051 ✅

**Check 4: Tucker's congruence greedy-only caveat**
- L4 present in Section 6.2 ✅
- **MISSING inline qualifier at point of claim in Section 5.1** → MAJOR-R2-001

**Check 5: Figure count consistency**
- Paper claims 7 figures; ground_truth.yaml lists 7 figures; all paths match ✅

**Check 6: H-M3 description consistency**
- Described as "pre-registered; not executed" in Sections 3.1, 5.4, 6.2(L3), 6.3(FW2) ✅

---

## Executive Summary

| Severity | Count |
|----------|-------|
| FATAL | 0 |
| MAJOR | 1 |
| MINOR (→ human_review_notes) | 0 (no new ones) |

**All R1 numerical fixes verified correct.**
**One new MAJOR issue found: Tucker's congruence inline caveat missing at point of claim.**

---

## FATAL Issues

*None found.*

---

## MAJOR Issues

### MAJOR-R2-001: Tucker's Congruence Greedy-Only Caveat Missing at Point of Claim

**Persona:** Accuracy Checker + Skeptical Expert
**Location:** Section 5.1, factor analysis result paragraph

**Issue:**
Section 5.1 states: "Tucker's congruence φ = 1.000 confirms factor stability."

The ground_truth.yaml adversary_check for this claim specifically requires: "Confirm caveat about greedy-only assessment is present in paper (L4)." L4 is present in Section 6.2, but **not at the point of claim in Section 5.1**. A reviewer reading Results will see φ = 1.000 as a strong stability claim without the critical qualifier that this was assessed within the greedy decoding regime only — the T=0.7 comparison (which gives the cross-condition stability meaning of Tucker's congruence) was never executed.

Tucker's congruence is defined as stability *across* decoding conditions. A value of 1.000 with only one decoding condition is mathematically trivial — it's comparing the factor to itself. The claim that "factor stability = 1.000" is misleading without this context.

**Required Fix:**
In Section 5.1, change: "Tucker's congruence φ = 1.000 confirms factor stability." to "Tucker's congruence φ = 1.000 within the greedy decoding regime (T=0.7 replication pre-registered as FW1; cross-condition stability unconfirmed — see L4)."

Also update the contributions table in Section 5.4 summary: the Tucker's congruence cell should carry a footnote or asterisk noting greedy-only.

**Evidence:** ground_truth.yaml: `tuckers_congruence.caveat: "Assessed within greedy regime only — T=0.7 data unavailable (L4)"`; h-e1/04_validation.md: "Tucker's congruence (greedy vs T=0.7): 1.000" — the source itself labels it as a greedy vs T=0.7 check that was presumably run on synthetic data with T=0.7 also synthetic, but the real-data T=0.7 check is pre-registered.

---

## Baseline Fairness Assessment

- Only comparison: composite epistemic predictor vs. MMLU-only LOO logistic classifier
- Both use same LOO CV framework, same StandardScaler normalization ✅
- Both use same N=30 synthetic data ✅
- Comparison is fair and appropriate for the paper's claims ✅
- No literature-reported baseline numbers needed (methodology paper, not benchmark comparison) ✅

---

## R1 Fix Verification

| R1 Fix | Verified Correct |
|--------|-----------------|
| MAJOR-001: "5.7%" survival fraction language | ✅ All 4 locations corrected |
| MAJOR-002: Section 6.1 conditional framing | ✅ "If this pattern replicates..." present |
| MAJOR-003: L7 within-family non-independence | ✅ L7 added to Section 6.2 |

---

## Summary for Revision Agent

**Fix MAJOR-R2-001:**
In Section 5.1, add inline greedy-only qualifier to Tucker's congruence claim.
Specifically change: "Tucker's congruence φ = 1.000 confirms factor stability."
To: "Tucker's congruence φ = 1.000 within the greedy decoding regime (T=0.7 cross-condition replication pre-registered as FW1; see L4)."

**Issue Counts:**
- fatal: 0
- major: 1 (MAJOR-R2-001)
- human_review_notes: 0 new
