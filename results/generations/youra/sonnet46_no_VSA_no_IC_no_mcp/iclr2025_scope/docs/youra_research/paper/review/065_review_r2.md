# Adversarial Review — Round 2

**Paper:** The Cache Format Matters: A Reproducible Baseline and Implementation Protocol for KV Cache Eviction in Modern Transformer Libraries
**Reviewed:** 2026-08-27T07:45:00+00:00
**Reviewer:** Adversary Agent v2 (Accuracy Checker + Skeptical Expert)
**Round:** R2 — Verification and Credibility
**Input Paper:** 06_paper_r1.md (post-R1 revision)

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 0 | 0 | OK |
| Credibility | 0 | 0 | OK |
| **TOTAL** | **0** | **0** | CONVERGE |

**Recommendation:** CONDITIONAL_ACCEPT

R1 revisions addressed all four MAJOR issues:
- F1 scale is now consistent (percentage format throughout).
- Citation disclaimer added in Related Work header; "(to be verified before submission)" markers on each reference.
- Pre-Submission Checklist documents condensation plan.
- Figure absence acknowledged in checklist.

R2 deep verification finds no new FATAL or MAJOR issues.

---

## Part 1: Numerical Verification (Accuracy Checker — R2)

### Ground Truth Cross-Check vs. R1 Paper

| Metric | R1 Paper Claims | Ground Truth | Match? |
|--------|----------------|--------------|--------|
| M0 macro-F1 | 8.75% (0.0875) | 0.0875 | ✓ |
| M0 NarrativeQA | 9% (0.09) | 0.09 | ✓ |
| M0 HotpotQA | 9% (0.09) | 0.09 | ✓ |
| M0 2WikiMQA | 11% (0.11) | 0.11 | ✓ |
| M0 MuSiQue | 6% (0.06) | 0.06 | ✓ |
| M1 F1 (all) | 0% (0.00) | 0.00 | ✓ |
| k at 50% retention | 2048 from 4096 | 2048 | ✓ |
| Layers confirmed | 32/32 | 32/32 | ✓ |
| W (observation window) | 16 | 16 | ✓ |
| Hypothesis status | INCONCLUSIVE | INCONCLUSIVE | ✓ |

All numerical claims verified against ground truth. No discrepancies.

### F1 Scale Consistency Check (R1 revision target)

- Abstract: "macro-F1=8.75% (raw 0.0875)" ✓
- §1 Introduction: "macro-F1=8.75% (raw 0.0875)" ✓
- §5.1 Table 1: "M0 F1 % (raw)" column header with "8.75% (0.0875)" ✓
- §5.4 Table 3: "F1=8.75%, coherent text" ✓
- §6.1 Finding 2: "macro-F1=8.75% (raw 0.0875)" ✓
- §7 Conclusion: "M0 (working, F1=8.75%)" ✓

F1 scale is now consistent throughout. MAJOR-ACC-001 resolved.

### Mathematical Validity

- score_M1 formula: mean_{t in [T-W,T]} attn_weight(t,i) — mathematically correct, matches SnapKV reference ✓
- score_M2 formula: sum_{t=0}^{T} attn_weight(t,i) — mathematically correct, matches H2O reference ✓
- k=2048 at 50% retention from 4096: 4096 × 0.50 = 2048 ✓
- Gate criterion corrected: ≥2 percentage points = raw ≥0.02 from M0 baseline 0.0875 ✓

### No FATAL or MAJOR Accuracy Issues in R2

---

## Part 2: Credibility Verification (Skeptical Expert — R2)

### Citation Disclaimer Verification

R1 revision added:
- Section 2 header: "Citation note: All references in this section have not been independently verified..." ✓
- Per-reference markers: "(citation to be verified before submission)" on all 7 references ✓

MAJOR-CRED-001 resolved. The paper now clearly signals citation verification is pending.

### Hypothesis Status Consistency Check

Checking that INCONCLUSIVE (not REFUTED) is consistently stated:
- Abstract: "The underlying metric comparison remains an open empirical question" ✓
- §1 Contributions: "remains empirically untested (not refuted)" ✓
- §5.5 Table: "H-E1 gate evaluable? NO — M2 not executed; M1 degenerate" ✓
- §6.2 L1: "INCONCLUSIVE — not REFUTED" ✓
- §7 Conclusion: "remains open, theoretically motivated, and empirically accessible" ✓

Consistent throughout. No overclaiming of REFUTED status.

### Claim Scope Check

The paper claims:
1. DynamicCache reconstruction fails "to our knowledge" — appropriately hedged ✓
2. "All existing implementations integrate eviction into the attention forward pass" — supported by §2 review of H2O, SnapKV, ScissorHands, PyramidKV ✓
3. Corrected protocol "proposed based on the SnapKV reference implementation design — it was not executed" — explicit disclaimer ✓

No overclaims detected.

### Pre-Submission Checklist Coverage

Checklist added in R1 revision covers:
- Citation verification ✓
- Page count condensation plan ✓
- Figure generation recommendation ✓
- F1 scale consistency ✓ (already achieved in R1)

MAJOR-CRED-002 resolved.

### No FATAL or MAJOR Credibility Issues in R2

---

## Part 3: Persuasiveness Re-Check (R2)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ✓ | Strong counterintuitive hook retained |
| Problem clear? | ✓ | Clear in first paragraph |
| Novelty clear? | ✓ | DynamicCache failure mode distinct from prior work |
| Figure 1 test | N/A | No figure — acknowledged in checklist |
| Would continue reading? | ✓ | Yes |

Persuasiveness criteria: PASSED.

---

## Human Review Notes (R2 — new only)

| Location | Note | Type |
|----------|------|------|
| §4 header | "F1 scale:" note appears before the RQs, slightly awkward placement — consider moving to §4.4 | clarity |
| §5.1 | "below-state-of-the-art F1 is expected and does not indicate a pipeline error" — slightly defensive phrasing; consider "lower than full-context F1 is expected due to 4K truncation" | style |
| §3.4 | Code block uses Python-style comment; no language tag on fenced code block | formatting |
| Pre-Submission Checklist | Section heading is not standard for an ICML submission — should be removed or moved to appendix notes | clarity |

---

## Summary

R2 finds **0 FATAL, 0 MAJOR** issues. Convergence criteria met:
- FATAL remaining = 0 ✓
- MAJOR remaining = 0 ✓
- Persuasiveness passed ✓
- Rounds completed = 2 (≥ min_rounds=2) ✓

**CONVERGE → proceed to finalize.**
