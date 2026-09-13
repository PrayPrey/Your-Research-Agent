# Adversarial Review — Round 2
# Focus: Numerical Verification and Credibility (Accuracy Checker + Skeptical Expert)
# Date: 2026-08-31T06:45:00+00:00
# Input paper: 06_paper_r1.md

---

## Ground Truth Verification Table (R2 — Full Numerical Check)

| Claim | Paper Value | Ground Truth / Calculation | Serena/Direct Verified | Match |
|---|---|---|---|---|
| LOO-CV accuracy | 83.3% (10/12) | 0.833 | h-e1/04_validation.md ✅ | ✅ |
| Permutation p | 0.031 | 0.031 | h-e1/04_validation.md ✅ | ✅ |
| TruthfulQA Fisher | 0.8122 | 0.8122 | h-m1/04_validation.md ✅ | ✅ |
| Dominance ratio | 9.5× | 0.8122/0.0856=9.487≈9.5 | Calculated ✅ | ✅ |
| TruthfulQA per-pair delta | +4.6pp | 0.2759/6=0.04598≈0.046 | Calculated ✅ | ✅ |
| BBQ per-pair delta | +0.5pp | 0.03/6=0.005 | Calculated ✅ | ✅ |
| BBQ group mean delta | +3.8pp | 0.460−0.422=0.038 | Calculated ✅ | ✅ |
| BBQ k | 3/6 | k_positive=3/6 | h-m1/04_validation.md ✅ | ✅ |
| BBQ p | 0.66 | 0.6562 | h-m1/04_validation.md ✅ | ✅ |
| WinoGender k | 4/6 | k_positive=4/6 | h-m1/04_validation.md ✅ | ✅ |
| WinoGender p | 0.34 | 0.3438 | h-m1/04_validation.md ✅ | ✅ |
| Sensitivity k=3 | 75.0% | k3_accuracy=0.750 | h-e1/04_validation.md ✅ | ✅ |
| Sensitivity k=5 | 66.7% | k5_accuracy=0.667 | h-e1/04_validation.md ✅ | ✅ |
| **P4-excluded TruthfulQA mean delta** | **≈+3.8pp** | **(0.1789/5=0.03578≈+3.6pp)** | **Calculated** | **❌ ERROR** |

---

## Executive Summary (R2)

| Severity | Count |
|---|---|
| FATAL | 0 |
| MAJOR | 2 |
| MINOR | 2 |

**R1 carried-over issues:** All 0 (FATAL-001 addressed; all 5 MAJORs addressed)

---

## MAJOR Issues (R2)

### R2-MAJOR-001: Sensitivity analysis value ≈+3.8pp should be ≈+3.6pp

**Location:** Section 6, L4 paragraph (added in R1)

**Issue:** The paper states (after R1 revision): "Sensitivity analysis excluding P4 yields k_TruthfulQA=3/5 pairs with DPO higher and mean delta≈+3.8pp."

Calculation: Excluding P4 (TruthfulQA Δ=+0.0970):
- P1: −0.0096, P2: +0.0223, P3: +0.0967, P5: −0.0097, P6: +0.0792
- Sum = 0.1789
- Mean = 0.1789/5 = 0.03578 ≈ **+3.6pp**, not +3.8pp.

**Fix:** Change "mean delta≈+3.8pp" to "mean delta≈+3.6pp"

---

### R2-MAJOR-002: "establishes" remains in Section 6 and Section 7

**Location:** Section 6 (Discussion, Finding 1) and Section 7 (Conclusion)

**Issue:** The Abstract was fixed in R1 ("demonstrates the feasibility of"), but two additional uses of "establishes" with overclaiming tone remain:

1. Section 6, Finding 1: "The 83.3% LOO-CV accuracy (p=0.031) **establishes** that DPO and SFT training produce detectably different 4D trustworthiness profiles."

2. Section 7, Conclusion: "classification accuracy (permutation p=0.031) **establishes** that the alignment fingerprint is real and statistically reliable."

Both assert definitive proof at n=12. The paper's own L2 acknowledges p=0.031 is "close to α=0.05." These should be softened consistently with the Abstract fix.

**Fix:**
- Section 6: Change "establishes" to "provides evidence that"
- Section 7: Change "establishes that the alignment fingerprint is real and statistically reliable" to "confirms that the alignment fingerprint is present and statistically significant at pilot scale"

---

## MINOR Issues (R2) — Collected for Human Review

### R2-MINOR-001: Figure number vs filename inconsistency (clarification)

**Location:** Section 5.2 Figure 6 reference

**Issue:** Paper refers to "Figure 6 (fig3_fisher_criterion.png)." The filename "fig3" reflects local numbering in h-m1 folder, while paper assigns it Figure 6 globally. Within the paper, Figure 6 is consistently referenced. No numerical error. Human reviewer should verify all 7 figure references are consistent.

### R2-MINOR-002: Section 6 "0.5–4.6pp range" conflates different benchmark deltas

**Location:** Section 6, Finding 1

**Issue:** "despite subtle differences in absolute scores (0.5–4.6pp range)" conflates BBQ per-pair delta (+0.5pp) with TruthfulQA per-pair delta (+4.6pp). These are different benchmarks, not a range of the same metric.

**Suggested revision:** "despite score differences spanning 0.5pp (BBQ) to 4.6pp (TruthfulQA) across benchmarks"

---

## Mathematical Validity Analysis

### Check: TOP-K vs dataset composition (N/A)
This paper has no TOP-K selection or conflict sample logic — not applicable.

### Check: Permutation test p-value plausibility
With 1000 permutations of balanced labels (6 DPO, 6 SFT), the null distribution of LOO-CV accuracy is discrete. Probability of achieving ≥83.3% by random label assignment: p=0.031 means ~31/1000 permutations scored ≥10/12. This is plausible and consistent with published permutation distributions for n=12 balanced datasets. ✅

### Check: Fisher criterion formula
Paper states: Fisher(j) = (μ_DPO,j − μ_SFT,j)² / (σ²_DPO,j + σ²_SFT,j)
This is the standard one-way Fisher criterion for binary classification. Appropriate for this use. ✅

### Check: Paired sign test
Paper: k_j = |{pairs i : score_DPO,i,j > score_SFT,i,j}|, H₀: k_j ~ Binomial(6, 0.5)
k_BBQ=3 → P(X≥3 | Binomial(6, 0.5)) one-tailed with H₁: k>3 → p = P(X>3) = P(X≥4) = (C(6,4)+C(6,5)+C(6,6))/64 = (15+6+1)/64 = 22/64 = 0.344. Wait — the paper states p_BBQ=0.6562. This is P(X≥3) not P(X≥4).

Re-check: if gate is k≥4, then p-value is P(X≥4 | H₀: X~Bin(6,0.5)) = 0.344. But if p-value is reported as P(X≥k_observed), then for k=3: P(X≥3) = P(X=3)+P(X=4)+P(X=5)+P(X=6) = (20+15+6+1)/64 = 42/64 = 0.6563 ≈ 0.6562. ✅ The p-value is reported as P(X≥k_observed), not P(X≥gate_threshold). This is correct and matches ground truth. ✅

### Baseline fairness assessment
The paper's permutation baseline is statistically appropriate for n=12. The binomial sign test is standard for paired comparisons. No unfair baselines identified. ✅

---

## Serena MCP Verification Log

Note: Serena MCP not available in this session (no MCP tools configured). Direct verification performed using Read tool on all Phase 4/5 validation files. All accessible ground truth files were verified directly.

| Search | Path | Result |
|---|---|---|
| h-e1/04_validation.md | Read directly | All classification metrics confirmed |
| h-m1/04_validation.md | Read directly | All mechanism metrics confirmed |
| 065_ground_truth.yaml | Read directly | All claims verified |
| 045_validated_hypothesis.md | Read directly | Consistency confirmed |

---

## Summary for R2 Revision

**MAJOR fixes needed:**
1. R2-MAJOR-001: Change "+3.8pp" to "+3.6pp" in L4 sensitivity analysis (Section 6)
2. R2-MAJOR-002: Fix "establishes" in Section 6 Finding 1 and Section 7

**MINOR — collect for human review:**
3. R2-MINOR-001: Figure number vs filename (human check)
4. R2-MINOR-002: "0.5–4.6pp range" clarification in Section 6
