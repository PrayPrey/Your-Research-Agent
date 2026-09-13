# Adversarial Review — Round 2: Numerical Verification and Credibility
**Paper:** Gradient Alignment as Spurious-Minority Detector (R1 version)  
**Round:** R2 — Numerical Verification, Baseline Fairness, Mathematical Validity  
**Personas:** Accuracy Checker · Skeptical Expert  
**Date:** 2026-08-31  
**Note:** Serena MCP unavailable (ablation mode). Numerical verification performed against 04_validation.md and 065_ground_truth.yaml directly.

---

## Ground Truth Verification Table (R2)

| Claim | Paper (R1) | Ground Truth | Serena Verified | Match |
|-------|-----------|--------------|-----------------|-------|
| WB alignment ROC-AUC epoch 1 | 0.150 | 0.1495 | manual: exact | ✓ |
| WB alignment ROC-AUC epoch 5 | 0.301 | 0.3006 | manual: exact | ✓ |
| WB alignment ROC-AUC epoch 10 | 0.340 | 0.3401 | manual: exact | ✓ |
| WB alignment ROC-AUC epoch 25 | 0.340 | 0.3404 | manual: exact | ✓ |
| WB alignment ROC-AUC epoch 50 | 0.349 | 0.3485 | manual: exact | ✓ |
| WB loss ROC-AUC epoch 1 | 0.930 | 0.9297 | manual: exact | ✓ |
| WB loss ROC-AUC epoch 5 | 0.854 | 0.8541 | manual: exact | ✓ |
| WB loss ROC-AUC epoch 10 | 0.821 | 0.8208 | manual: exact | ✓ |
| WB loss ROC-AUC epoch 25 | 0.801 | 0.8007 | manual: exact | ✓ |
| WB loss ROC-AUC epoch 50 | 0.775 | 0.7747 | manual: exact | ✓ |
| CelebA alignment ROC-AUC epoch 1 | 0.246 | 0.2462 | manual: exact | ✓ |
| CelebA alignment ROC-AUC epoch 10 | 0.523 | 0.5227 | manual: exact | ✓ |
| CelebA alignment ROC-AUC epoch 50 | 0.632 | 0.6321 | manual: exact | ✓ |
| CelebA loss ROC-AUC epoch 1 | 0.975 | 0.9745 | manual: exact | ✓ |
| CelebA loss ROC-AUC epoch 50 | 0.905 | 0.9053 | manual: exact | ✓ |
| WB gap epoch 1 | −0.780 | 0.9297−0.1495=0.7802 | computed: exact | ✓ |
| CelebA gap epoch 1 | −0.729 | 0.9745−0.2462=0.7283 | computed: exact | ✓ |
| WB gap epoch 50 | −0.426 | 0.7747−0.3485=0.4262 | computed: exact | ✓ |
| CelebA gap epoch 50 | −0.273 | 0.9053−0.6321=0.2732 | computed: exact | ✓ |

**Numerical Verdict: ALL numbers verified. Zero discrepancies.**

---

## Serena MCP Verification Log

*Serena MCP unavailable in this session (ablation mode). Verification performed against:*
- `h-e1/04_validation.md` (Tables 2.1, 2.2)
- `docs/youra_research/paper/065_ground_truth.yaml`
- `docs/youra_research/045_validated_hypothesis.md`

*All patterns searched manually: WGA, accuracy, sensitivity, FPR, epochs, top-k, upweight, baseline comparisons.*

---

## Mathematical Validity Analysis

### Check 1: Gap Range Claims

**Paper claims:** "gap 0.43–0.78 throughout training" (Waterbirds), "gap up to 0.73 on CelebA"

**Verification:**
- WB minimum gap: epoch 50 = 0.7747 − 0.3485 = 0.4262 → rounds to 0.43 ✓
- WB maximum gap: epoch 1 = 0.9297 − 0.1495 = 0.7802 → rounds to 0.78 ✓
- CelebA maximum gap: epoch 1 = 0.9745 − 0.2462 = 0.7283 → rounds to 0.73 ✓
- Paper says "0.43–0.78" range for WB — this is correct but uses *signed* gaps in Table 1 as negatives (−0.426 to −0.780). The magnitude is correctly 0.43–0.78. ✓

**Verdict:** PASS

### Check 2: CelebA Gap at Epoch 50

**Paper (R1) Conclusion:** "within-batch gradient alignment ROC-AUC ≤ 0.35 (Waterbirds) and ≤ 0.63 (CelebA)"

**Verification:**
- WB max alignment: 0.3485 → ≤ 0.35 ✓
- CelebA max alignment: 0.6321 → ≤ 0.63 ✓ (exactly 0.63 by rounding)

**Verdict:** PASS

### Check 3: Abstract loss range "0.77–0.97"

**Paper (R1) Abstract:** "far below per-sample loss (0.77–0.97, across datasets and epochs)"

**Verification:**
- WB loss range: 0.7747 (min, epoch 50) to 0.9297 (max, epoch 1)
- CelebA loss range: 0.9053 (min, epoch 50) to 0.9745 (max, epoch 1)
- Combined range: 0.7747 to 0.9745 → rounds to 0.77–0.97 ✓

**Verdict:** PASS

### Check 4: Batch Contamination Formal Estimate

**Paper (R1) Section 6:** "if minority gradients have magnitude $k > 1$ times majority gradient magnitude, the minority contribution to the batch mean is $\propto k \cdot n_\text{min} / B$. With $k$ potentially large at epoch 1 (due to high minority loss) and $n_\text{min} = 1$..."

**Check:** R1 revision removed the specific claim "$k \approx 10$" from the original. Now says "potentially large." This is appropriate since k is not measured. ✓

**Verdict:** PASS — R1 already fixed this.

### Check 5: "0.26 minority samples expected per batch" (CelebA)

**Paper Section 5 (R1):** "at 0.8% minority prevalence and B=32, expected minority samples per batch is 0.26"

**Verification:** 0.008 × 32 = 0.256 ≈ 0.26 ✓

**Verdict:** PASS

### Check 6: "5% minority, 1–2 minority per batch" (Waterbirds)

**Paper Section 5 (R1):** "With batch size $B = 32$ and ~5% minority prevalence, 1–2 minority samples per batch"

**Verification:** 
- 05% × 32 = 1.6 → "1–2" ✓
- Ground truth: "~18% (combined spurious groups); ~5% for most underrepresented"
- Paper uses ~5% for the most underrepresented group. Consistent. ✓

**Verdict:** PASS

### Check 7: "82% majority" Waterbirds

**Paper Section 4:** "Train: 4,795 samples, ~82% majority"

**Verification:** 
- Ground truth: minority_group_ids: [1, 2], approximate_minority_prevalence: "~18% (combined spurious groups)"
- 1 − 18% = 82% majority ✓

**Verdict:** PASS

---

## Baseline Fairness Assessment

### JTT 86.7% WGA on Waterbirds

**Paper claims:** JTT achieves 86.7% WGA (cited from Liu et al. 2021)
**Assessment:** 
- This number is from the JTT paper under their experimental setup
- Paper (R1) now correctly clarifies: "We do not reproduce JTT or GroupDRO baselines in our experimental setup"
- The JTT number is used as motivational context only, not as a direct comparison
- **Verdict: FAIR** (with R1 clarification)

### ERM 72% WGA on Waterbirds

**Paper claims:** ERM achieves 72% worst-group accuracy (Sagawa et al. 2020)
**Assessment:** Standard benchmark number, widely cited. Consistent with ground truth `dataset_facts.waterbirds.erm_worst_group_accuracy: "72.6%"` (paper rounds to 72%). ✓

### Per-Sample Loss vs. Gradient Alignment

This is the core comparison. Both computed under identical conditions: same model, same data, same epochs. The comparison is maximally fair. **Verdict: FAIR**

---

## Executive Summary R2

| Severity | Count |
|----------|-------|
| FATAL | 0 |
| MAJOR | 0 |
| MINOR | 2 |

**All numerical claims verified.** All mathematical validity checks pass. Baseline comparisons are fair. No new FATAL or MAJOR issues found in R2.

### R2 MINOR Issues (Human Review)

| ID | Category | Location | Issue |
|----|----------|---------|-------|
| R2-MINOR-001 | Clarity | Sec 6 Discussion | "k potentially large at epoch 1 (due to high minority loss)" — consider adding an informal estimate or cross-reference to 04_validation.md loss values to give the reader a sense of magnitude, without claiming it as a measurement |
| R2-MINOR-002 | Formatting | Table 1 signed gaps | The signed gaps (−0.780) and the unsigned gap range in text (0.43–0.78) use different sign conventions; consider a brief note "(negative = alignment below loss)" in Table 1 footnote for clarity |

---

## Convergence Status

- FATAL remaining: 0
- MAJOR remaining: 0
- Persuasiveness: PASSED (all checks pass post-R1)
- Rounds completed: R1 + R2 ≥ 2 (min_rounds met)

**CONVERGE → Proceed to Step 07 Finalize.**
