# Adversarial Review Report — Round 2
**Paper:** "When the Signal is Real but the Training is Not: Variance-Guided RLEF Data Selection and the Cold-Start Problem"
**Revision:** R1
**Review Date:** 2026-08-21
**Round Focus:** Numerical Verification, Mathematical Validity, Baseline Fairness, Persuasiveness Re-check

---

## 1. Numerical Verification Table

| Check | Claim in Paper R1 | Calculation | Verdict |
|---|---|---|---|
| C1: 50,000+ total attempts | "50,000+ generation attempts (50–200 steps)" | h-m2: 50×50×4=10,000; h-m3: 200×50×4=40,000; combined=50,000 | **PASS** |
| C2a: 69.25% Nie vs 91.7% empirical framing | "more severe than 69.25% theoretical" | Nie: 69.25% = zero-gradient groups (all-fail+all-pass). Paper: 91.7% = per-problem all-fail rate. Different units. | **FLAG** |
| C2b: "truncation amplifies gradient starvation" | Credited to max_new_tokens=128 | Hypothesis, not controlled experiment. | **FLAG** |
| C3: Variance at k=4, p=0.25 | v_i=0.1875 in Table 1 | 0.25×0.75=0.1875 ✓ | **PASS** |
| C3: max_variance_i=0.2500 vs Table 1 zero at p=0.50 | No contradiction | 0.2500 is theoretical max, not observed | **PASS** |
| C4: Ratio 4.24× | 0.1113/0.0262=4.24× | 0.1113/0.0262=4.248≈4.24 ✓ | **PASS** |
| C4: MWU U=1807 plausibility | n=50 vs n=50 | Max U=2500; U=1807=72.3% pairs; consistent with 29 vs ~7 high-variance problems | **PASS** |
| C5: mean_p_top50=0.225 (ground truth) | Paper says "21 zero-variance filler problems" | 29×0.25/50=0.145; not 0.225. Ground truth spec inconsistency — paper does not cite this value, no paper error | **FLAG (GT spec, not paper)** |
| C6: Baseline fairness | random-50 as null hypothesis | Appropriate — training-stage comparison impossible under cold-start | **PASS** |
| C7: 29 gate vs threshold 15 | "29 problems exceed gate of 15" | 29>15 ✓ | **PASS** |
| Table 1 row sums | 343+29+0+2=374 | 374 ✓ | **PASS** |

---

## 2. Mathematical Validity Analysis

### C2: Apples-to-Oranges Comparison (MAJOR)

Section 5.1 states: "The 91.7% all-fail rate is substantially more severe than the 69.25% theoretical estimate [Nie et al., 2026] — confirming that max_new_tokens=128 truncation dramatically amplifies gradient starvation beyond the theoretical baseline."

**Problem:** Unit mismatch.
- Nie et al. 2026: 69.25% = zero-gradient *training groups* (54.75% all-fail + 14.50% all-pass across training steps)
- Paper: 91.7% = per-*problem* all-fail rate in profiling (static, not per training group)

These are related but distinct metrics. The paper's zero-gradient total at profiling = 91.7% + 0.5% = 92.2% of *problems* with zero variance — not of training groups. Additionally, attributing the difference to "max_new_tokens=128 truncation" is a hypothesis without a controlled comparison (vs. same model at max_new_tokens=512).

**Fix:** Change one sentence in Section 5.1 to acknowledge the different units and soften "confirming" to "suggesting."

---

## 3. Remaining Issues

| ID | Severity | Description |
|---|---|---|
| **R2-MAJOR-1** | MAJOR | Section 5.1: "confirming that truncation amplifies" — unit mismatch + causal overclaim |
| R2-MINOR-1 | MINOR | mean_p_top50=0.225 in ground truth inconsistent with Table 1 (paper doesn't cite this value, no action needed) |
| R2-MINOR-2 | MINOR | "To our knowledge" hedge present but no new GRPO-on-MBPP comparison citations |

---

## 4. R1 MAJOR Issues — Resolution Status

| R1 Issue | Status |
|---|---|
| AC-2: "~13 unique rollouts" unverified | **FIXED** — removed from paper |
| AC-3: Root cause framed as confirmed | **FIXED** — Section 6.2 now has 4 ranked candidates with evidence |
| OC-1: "First characterization" overclaim | **FIXED** — "to our knowledge" added throughout |
| BR-1: ICML framing weak | **FIXED** — "Why this negative result is worth reporting" paragraph added |
| ML-2: Resolution protocol unexecuted | **FIXED** — explicitly acknowledged as "proposed but not yet empirically validated" |

---

## 5. Persuasiveness Re-check

| Dimension | R1 Score | R2 Score |
|---|---|---|
| abstract_compelling | true | true |
| problem_clear_in_1_minute | true | true |
| novelty_clear_in_2_minutes | false | **marginal→true** |
| would_continue_reading | marginal | **true** |
| attention_lost_at | Section 4 | Section 5.3 (later) |

The "Why this negative result is worth reporting" paragraph in Section 1 substantially improves novelty clarity. Paper now reads as a coherent negative result contribution.

**Persuasiveness: PASSED** (improved from R1)

---

## 6. Summary

| Gate | Status |
|---|---|
| FATAL issues | 0 ✓ |
| New MAJOR issues | 1 (R2-MAJOR-1) |
| Persuasiveness | PASSED ✓ |

**Convergence: NOT YET — one targeted sentence-level MAJOR fix needed in Section 5.1.**

### Required Fix for R2-MAJOR-1

Replace in Section 5.1:
> "The 91.7% all-fail rate is substantially more severe than the 69.25% theoretical estimate [Nie et al., 2026] — confirming that max_new_tokens=128 truncation dramatically amplifies gradient starvation beyond the theoretical baseline."

With:
> "The 91.7% per-problem all-fail rate under profiling (k=4, max_new_tokens=128) substantially exceeds Nie et al.'s 54.75% all-fail component (note: Nie et al. measure per-training-group zero-gradient rate = all-fail + all-pass groups, a different but related unit), suggesting that constrained generation parameters may amplify practical gradient starvation beyond theoretical estimates for this model."
