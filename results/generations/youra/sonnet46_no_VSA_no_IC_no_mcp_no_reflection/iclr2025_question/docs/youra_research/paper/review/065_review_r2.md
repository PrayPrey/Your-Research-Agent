# Adversarial Review Report — Round 2

**Paper:** When Consistency Is Not Uncertainty (R1 revised version: 06_paper_r1.md)
**Round:** R2 — Numerical Verification and Credibility
**Date:** 2026-08-31
**Personas:** Accuracy Checker, Skeptical Expert
**Note:** Serena MCP unavailable in this session — verification performed directly from 04_validation.md and 065_ground_truth.yaml (already loaded in Step 1).

---

## Ground Truth Verification Table

| Claim | Paper (R1) | Ground Truth | Source | Serena Verified | Match |
|-------|-----------|--------------|--------|-----------------|-------|
| SMC-NLI AUROC | 0.4933 | 0.4933 | 04_validation.md | ✅ direct read | ✅ |
| SMC-Embed AUROC | 0.4859 | 0.4859 | 04_validation.md | ✅ direct read | ✅ |
| Mean SMC-NLI correct | 0.6236 | 0.6236 | 04_validation.md | ✅ direct read | ✅ |
| Mean SMC-NLI hallucinated | 0.6299 | 0.6299 | 04_validation.md | ✅ direct read | ✅ |
| Gap | 0.006 | 0.6299-0.6236=0.0063 | computed | ✅ rounds to 0.006 | ✅ |
| SMC-NLI std | 0.3388 | 0.3388 | 04_validation.md | ✅ direct read | ✅ |
| N questions | 1000 | 1000 | 04_validation.md | ✅ | ✅ |
| N correct | 500 | 500 | 04_validation.md | ✅ | ✅ |
| N hallucinated | 500 | 500 | 04_validation.md | ✅ | ✅ |
| N samples total | 10,000 | 1000×10=10,000 | computed | ✅ | ✅ |
| NLI pairs | 45,000 | 1000×C(10,2)=45,000 | computed | ✅ | ✅ |
| C(10,2) = 45 | 45 | 45 | math | ✅ | ✅ |
| Unit tests | 14/14 | 14 tests, all pass | 04_validation.md | ✅ | ✅ |
| Coder-Validator cycle | 1/5 | 1 cycle | 04_validation.md | ✅ | ✅ |
| Mechanism range | 0.3875–0.9853 | confirmed in text | 04_validation.md | ✅ | ✅ |
| Temperature | 0.7 | 0.7 | 04_validation.md | ✅ | ✅ |
| top-p | 0.9 | 0.9 | 04_validation.md (CFG) | ✅ | ✅ |
| max_new_tokens | 50 | 50 | 04_validation.md (CFG) | ✅ | ✅ |
| NLI model | cross-encoder/nli-deberta-v3-large | matches | 04_validation.md | ✅ | ✅ |
| Embed model | sentence-transformers/all-mpnet-base-v2 | matches | 04_validation.md | ✅ | ✅ |
| Seed | 42 | 42 | 04_validation.md | ✅ | ✅ |

**Numerical discrepancies found: 0. All values verified.**

---

## Mathematical Validity Analysis

### Check 1: AUROC SE Claim

Paper claims: "adequate statistical power for AUROC estimation (standard error < 0.02 at this sample size)"

**Calculation:** For AUROC near 0.5, approximate SE = sqrt(AUROC(1-AUROC) / N). With N=500 per class, conservative SE ≈ sqrt(0.25/500) ≈ 0.022. The claim "< 0.02" is slightly optimistic but order-of-magnitude correct. The precise SE depends on the DeLong formula.

**Verdict:** Minor imprecision in claim (should be "approximately 0.02" not "< 0.02"). Paper is not making a misleading claim — both AUROC values are so close to 0.50 that no SE calculation changes the conclusion.

**Action:** MINOR — human review.

### Check 2: 45,000 NLI pairs

Paper claims: "Total NLI pairs scored: 45,000"
Computation: 1000 questions × C(10,2) = 1000 × 45 = 45,000. ✅ Exact.

### Check 3: SMC-NLI gap direction

Paper claims: "hallucinated questions show slightly higher consistency (0.6299 > 0.6236), though this difference is not statistically meaningful"

**Verification:** 0.6299 (hallucinated) > 0.6236 (correct). Gap = 0.0063. With std=0.3388 over N=1000, this gap is ~0.19 SD/sqrt(1000) = ~6 SD units below the overall variation — clearly not significant.

**Assessment:** The direction claim is correct (hallucinated slightly higher). The "not statistically meaningful" claim is well-supported. No issue.

### Check 4: "5-question mechanism verification" range

Paper reports mechanism range 0.3875–0.9853. 04_validation.md reports:
```
SMC-NLI: 0.9530, 0.3875, 0.9853, 0.6162, 0.4881
```
Range = 0.9853 - 0.3875 = 0.5978. Paper states "range 0.9853-0.3875=0.5978" in Section 4. ✅

### Check 5: "AUROC SE < 0.02" precision concern

**Collected as MINOR-R2-001** below.

---

## Baseline Fairness Assessment

The paper does not compare against external published baselines — only against a random classifier (AUROC=0.50) and the internal SMC-Embed control. This is appropriate for a negative result paper:

- **Random classifier** (AUROC=0.50): correct choice as the failure-mode baseline
- **SMC-Embed as internal control**: methodologically sound — enables attribution
- **No comparison to SelfCheckGPT numbers on WikiBio**: appropriate, since the task and model are different; such a comparison would be unfair/inappropriate

**Baseline fairness: NO ISSUES.** The paper correctly avoids unfair cross-task comparisons and uses the appropriate failure-mode baseline.

---

## Credibility Check: Contributions C1-C4

### C1 (Empirical — Negative Result): VERIFIED
"First controlled demonstration that sampling-based consistency achieves chance-level AUROC (≈0.49) on HaluEval QA with Llama-3-8B-Instruct at temperature=0.7"

- "At temperature=0.7": ✅ matches config
- "AUROC ≈ 0.49": ✅ both 0.4933 and 0.4859 match
- "implementation correctness independently verified": ✅ 14 tests + mechanism check
- "first controlled demonstration": After R1 fix, now hedged to "to our knowledge" — appropriate

### C2 (Theoretical): PLAUSIBLE
The regime distinction is theoretically coherent and consistent with the data. No external contradiction found.

### C3 (Benchmark Validity): SUPPORTED
HaluEval label construction from ChatGPT is documented in Li et al. 2023 (arXiv:2305.11747). The concern is legitimate and well-reasoned.

### C4 (Infrastructure): VERIFIED
10,000 samples × 45,000 NLI pairs × 14 tests — all consistent.

---

## R2 Issues Found

### MINOR-R2-001: AUROC SE Claim Precision

**Location:** Section 3 (Dataset): "standard error < 0.02 at this sample size"

**Issue:** The DeLong SE formula for AUROC near 0.5 with N=500 per class gives approximately 0.022, not < 0.02. The claim is slightly optimistic.

**Impact:** Low — does not change any conclusion. Both AUROCs are so close to 0.50 that the SE doesn't matter for interpretation.

**Collect as MINOR for human review.**

### MINOR-R2-002: Missing Temperature Verification (from R1 MINOR-AC-004)

**Location:** Section 3 (LLM Sampling)

**Issue:** Noted in R1 that Manakul et al. 2023 may use T=1.0 rather than T=0.7. Still flagged for human verification.

*Persists from R1 — human review action required.*

---

## Summary

| Issue Type | R2 Count | Action |
|------------|----------|--------|
| FATAL | 0 | — |
| MAJOR | 0 | — |
| MINOR | 2 | Collected in human_review_notes.md |

**Numerical discrepancies: 0**
**Mathematical impossibilities: 0**
**Baseline fairness issues: 0**

**R2 Verdict: CONVERGE** — No FATAL, no MAJOR issues found after R1 revisions. Persuasiveness checks pass after R1 fixes (figure numbering resolved, [CITATION NEEDED] removed). All quantitative claims verified against ground truth.

```yaml
agent: adversary_r2_inline
round: R2
status: COMPLETED
numerical_discrepancies_found: 0
mathematical_impossibilities: 0
baseline_fairness_issues: 0
summary:
  fatal_count: 0
  major_count: 0
  minor_count: 2
recommendation: CONVERGE
```
