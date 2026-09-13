# Phase 6.5 Adversarial Review — Round 2
**Date:** 2026-03-15
**Paper:** When Partial Credit Counts: Prescreening-Gated Ratio Rewards for GRPO on Code Generation
**Paper File:** `docs/youra_research/20260315_dl4c/paper/06_paper_r1.md`
**Venue:** ICML 2025
**Round:** R2 (post-R1 revision)
**Focus:** Numerical verification, mathematical validity, baseline fairness

---

## Executive Summary

| Category | FATAL | MAJOR | HRN |
|----------|-------|-------|-----|
| Mathematical Validity | 1 | 0 | 1 |
| Numerical Verification | 0 | 0 | 0 |
| Baseline Fairness | 0 | 1 | 1 |
| Metadata/Residual | 0 | 0 | 3 |
| **Total** | **1** | **1** | **5** |

**Overall Recommendation: MAJOR_REVISION** (narrowed from R1; one critical math formula inconsistency found)

---

## PART 1: Serena Verification Log

### Metric Verification Table

| Metric | Ground Truth | Paper (r1) | Status |
|--------|-------------|-----------|--------|
| prescreening_pass_rate | 0.0 | 0% | MATCH |
| problems_in_tractability_window | 0 / 300 | 0/300 | MATCH |
| total_solution_attempts | 2,400 (300 × 8) | 2,400 | MATCH |
| k_rollouts | 8 | 8 | MATCH |
| tasks_completed | 15/15 | 15/15 | MATCH |
| integration_tests_passed | 67/67 | 67/67 | MATCH |
| overall_gate_decision | FAIL | FAIL (fixed in R1) | MATCH |
| Afterburner attribution | Du et al., 2025 | Du et al., 2025 | MATCH |
| Var(r_ratio) formula | q(1-q)/T | q(1-q) — MISSING /T | MISMATCH |
| Variance ratio formula | q(1-q)/[T×q^T(1-q^T)] | q(1-q)/[q^T(1-q^T)] — MISSING T | MISMATCH |
| ρ(0.5, 5) correct value | ~1.65× (with /T) | 8.25× (without /T) | MISMATCH |

### R1 Fixes Confirmed
- AC-1 (Liao→Du in section files): CONFIRMED FIXED
- AC-2 (PARTIAL→FAIL in Table 2): CONFIRMED FIXED
- AC-3 (section numbering): CONFIRMED FIXED
- BR-1 (replicates→corroborates in Abstract, Introduction, Conclusion): CONFIRMED FIXED
- BR-2 (Table 5.5 framing sentence): CONFIRMED FIXED
- SE-2 (Binomial derivation positioning): CONFIRMED FIXED
- BR-1 PARTIAL: Section 2.2 body still says "independently discover" — NOT FIXED (see R2-MAJOR-1)

---

## PART 2: Mathematical Validity Check

### [R2-FATAL-1] — FATAL: Variance Formula Drops /T Factor — ρ Inflated

**Location:** Section 3.1 (line ~91), Section 3.1 (line ~103), Introduction (line ~39), Conclusion (~line 320)

**The mathematical issue:**

The paper defines R_ratio = tests_passed / T. For tests_passed ~ Binomial(T, q):
- Correct: Var(R_ratio) = Var(tests_passed/T) = T×q(1-q)/T² = **q(1-q)/T**

However, the paper states (Section 3.1):
```
E[Var(r_ratio)] = q(1-q)    ← MISSING /T
```

And the variance ratio formula (line ~103):
```
Paper:   ρ(q,T) = q(1-q) / [q^T(1-q^T)]
Correct: ρ(q,T) = q(1-q) / [T × q^T(1-q^T)]
```

**Numerical impact:**

| q | T | Paper ρ (incorrect) | Correct ρ |
|---|---|---------------------|-----------|
| 0.5 | 5 | 8.25× | 1.65× |
| 0.5 | 10 | 341× | 34.1× |
| 0.45 | 5 | ~13.6× | ~2.7× |

The claimed "5–20× advantage" in Abstract and Introduction is based on the incorrect formula without /T. Ground truth (065_ground_truth.yaml line 154) states: `ρ(q,T) = q(1-q)/[T×q^T(1-q^T)]` with `peak_advantage: ρ ≥ 5× for q∈[0.3,0.55], T=5`.

**Note on ground truth peak claim:** The ground truth claims ρ ≥ 5× for T=5, which with the correct formula gives ~1.65-2.7× — inconsistent with the claimed ≥5×. The ground truth `peak_advantage` field itself may reflect the paper's formula rather than the corrected calculation. **Author must rederive from first principles** using the correct formula.

**Fix required:**
1. Correct Sec 3.1 formula: `E[Var(r_ratio)] = q(1-q)/T`
2. Correct variance ratio: `ρ(q,T) = q(1-q) / [T × q^T(1-q^T)]`
3. Recalculate ρ(0.5,5) = 1.65 (not 8.25), ρ(0.5,10) = 34.1 (not 341)
4. Reassess "5–20×" range — may need to revise to smaller values or justify different T assumption
5. Update Abstract, Introduction, and Conclusion accordingly

**Alternative resolution:** If the author intended R_ratio = tests_passed (unnormalized, range [0,T]) rather than tests_passed/T, then Var = q(1-q)×T (not /T), and ρ = q(1-q)×T/[q^T(1-q^T)] which equals T × paper's formula. At T=5, ρ(0.5,5) = 5×8.25/8.25 = 5×... no, that gives ρ=5×(paper)/8.25 = different. Author clarification required.

---

### [R2-HRN-1] — HRN: Introduction q(1-q) Claim Depends on R2-FATAL-1 Resolution

Line ~39: "the expected within-group variance of R_ratio is q(1-q)"
Fix depends on author's choice above; must be updated after FATAL-1 resolution.

---

## PART 3: Baseline Fairness Check

### [R2-MAJOR-1] — MAJOR: "Independently Discover" in Sec 2.2 Not Updated from R1 Fix

**Location:** Section 2.2, line ~59.

"Our work is complementary to Afterburner: **we independently discover the same SFT prerequisite** through our 0% base model pass rate finding..."

R1 fix [BR-1] updated the Abstract and Conclusion but missed this instance in Related Work. A null result from format incompatibility is not a "discovery" — it is an observation consistent with prior work. This is the same overclaiming-tone issue flagged as MAJOR in R1.

**Fix:** "we independently discover the same SFT prerequisite" → "we independently observe the same SFT prerequisite pattern" or "our 0% result is consistent with and independently corroborates the SFT prerequisite"

### Baseline Fairness — No Additional Issues

R_binary baseline is fairly set up: identical GRPO framework, same problem set, same group size. The blocked Stage 2 comparison is correctly labeled PROJECTED. No unfair baseline manipulation.

---

## PART 4: Human Review Notes (Additional MINOR Issues)

| # | Issue ID | Category | Description |
|---|----------|----------|-------------|
| 1 | R2-HRN-1 | clarity | q(1-q) in Introduction needs update after FATAL-1 resolution |
| 2 | R2-HRN-2 | formatting | Stale metadata note in Paper Statistics block (lines ~408-410) references "Liao et al." warning — now obsolete after R1 fix |
| 3 | R2-HRN-3 | formatting | "~72% pass@1 on HumanEval" claim (line ~253) has no citation source |
| 4 | R2-HRN-4 | clarity | SE-1 from R1 (alternative harness baseline) partially addressed by HumanEval mention but citation missing |
| 5 | R2-HRN-5 | clarity | ground_truth_file peak_advantage claim (ρ ≥ 5× for T=5) may itself be based on incorrect formula — after author resolves FATAL-1, update 065_ground_truth.yaml accordingly |

---

## Summary for Revision Agent

### Priority-Ordered Fix List for R2

**FATAL (fix before resubmission):**

1. **[R2-FATAL-1] Correct Var(r_ratio) formula and all derived claims:**
   - Section 3.1: `E[Var(r_ratio)] = q(1-q)` → `E[Var(r_ratio)] = q(1-q)/T`
   - Section 3.1: `ρ(q,T) = q(1-q)/[q^T(1-q^T)]` → `ρ(q,T) = q(1-q)/[T × q^T(1-q^T)]`
   - Introduction and Abstract: update "5–20× higher" claim after recalculating correct range
   - Conclusion: update formula and magnitude claims
   - Recalculate ρ(0.5,5) ≈ 1.65 (was 8.25), ρ(0.5,10) ≈ 34.1 (was 341)
   - IMPORTANT: Author must decide whether the "5–20×" range can be defended for some (q,T) combination or whether the range needs revision

**MAJOR:**

2. **[R2-MAJOR-1] Fix "independently discover" in Section 2.2:**
   "we independently discover the same SFT prerequisite" → "our results independently corroborate the SFT prerequisite"

**Human Review Notes:** 5 items (see Part 4 above)

---

## Return Summary

```
FATAL_COUNT: 1
MAJOR_COUNT: 1
HUMAN_REVIEW_NOTES_COUNT: 5
PERSUASIVENESS_PASSED: true
RECOMMENDATION: MAJOR_REVISION (narrowed — purely mathematical fix needed)
ABSTRACT_COMPELLING: true (pending math fix)
WOULD_CONTINUE_READING: true
ATTENTION_LOST_AT: never

R1_FIXES_ALL_CONFIRMED: mostly yes (BR-1 partial miss in Sec 2.2)
NEW_FATAL: R2-FATAL-1 — variance formula inconsistency
```
