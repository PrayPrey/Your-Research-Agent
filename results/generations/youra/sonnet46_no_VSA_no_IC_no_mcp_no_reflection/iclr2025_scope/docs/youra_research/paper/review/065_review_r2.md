# Adversarial Review - Round 2

**Paper:** API Compatibility Is Not Gradient Compatibility: Projection-Only LoRA Fails on Mamba-130m for Classification Tasks (R1 revised)
**Reviewed:** 2026-08-31
**Reviewer:** Adversary Agent - Round 2 Numerical Verification

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Arithmetic | 0 | 0 | All calculations verified correct |
| Cross-section consistency | 0 | 0 | Numbers consistent throughout |
| Mathematical validity | 0 | 1 | SE calculation borderline; minor framing issue |
| New R1 additions | 0 | 1 | "Partial barrier" paragraph adds tension with §3.4 claim |
| **TOTAL** | **0** | **2** | |

**Recommendation:** MINOR_REVISION — numerical foundation is solid. Two MAJOR items require prose fixes, not data corrections. All R1 additions are internally consistent.

---

## Ground Truth Verification Table

| Claim | Paper Value | Ground Truth | Match? |
|-------|-------------|--------------|--------|
| SST-2 zero-shot | 0.4908 | 0.4908 | YES |
| SST-2 epochs 1-3 | 0.5092 / 0.5092 / 0.5092 | 0.5092 / 0.5092 / 0.5092 | YES |
| SST-2 net gain | +1.84pp | 1.84pp | YES |
| SST-2 gap to gate | −0.1908 (19.1pp) | 0.70 − 0.5092 = 0.1908 | YES |
| MNLI zero-shot | 0.3463 | 0.3463 | YES |
| MNLI epoch 1 | 0.3326 | 0.3326 | YES |
| MNLI epoch 1 delta | −1.4pp (from "−0.0137") | −1.37pp → rounded −1.4pp | YES (correct rounding) |
| MNLI epoch 2 | 0.3234 | 0.3234 | YES |
| MNLI epoch 2 delta | −2.3pp (from "−0.0229") | −2.29pp → rounded −2.3pp | YES (correct rounding) |
| LoRA rank | 8 | 8 | YES |
| LoRA alpha | 16 | 16 | YES |
| LoRA dropout | 0.05 | 0.05 | YES |
| Trainable params | 1,484,288 / 1.14% | 1,484,288 / 1.14% | YES |
| Gradient steps/epoch | 125 (4000/32) | 125 | YES |
| Total gradient steps | 375 (3 × 125) | 375 | YES |
| Loss range | 0.65–0.73 | 0.65–0.73 | YES |
| ln(2) reference | 0.693 | 0.693 | YES |
| SST-2 validation N | 872 | 872 | YES |
| MNLI validation N | 9,815 | 9,815 | YES |
| Binomial SE | ~0.017 (1.7pp) | sqrt(0.5092×0.4908/872) = 0.01694 | YES (≈1.7pp) |
| 1.84pp ≈ 1 SE | stated as "approximately 1 SE" | 1.84/1.694 = 1.086 SE | YES |
| SST-2 % form | 50.9% | 0.5092 × 100 = 50.92% | YES (50.9% correct rounding) |
| Zero-shot % form | 49.1% | 0.4908 × 100 = 49.08% | YES (49.1% correct rounding) |
| MNLI % forms | 34.6%, 33.3%, 32.3% | 34.63%, 33.26%, 32.34% | YES (all correct rounding) |
| QNLI zero-shot | 0.5056 | 0.5056 | YES |
| QQP zero-shot | 0.0000 | 0.0000 | YES |
| ~40pp gap to MambaPEFT | "approximately 40 percentage points" | 90%−50.9% = 39.1pp | YES |
| Mamba layers | 24 | 24 | YES |
| d_model | 768 | 768 | YES |
| d_inner | 1536 | 1536 | YES |
| dt_rank | 48 | 48 | YES |
| LoRA 1.14% of 130M check | 1,484,288 / 130M = 1.141% | 1.14% | YES |

---

## Mathematical Validity Analysis

### A. Arithmetic checks

**1.84pp gain:** 0.5092 − 0.4908 = 0.0184 = 1.84pp. CONFIRMED.

**MNLI ep1 delta:** 0.3463 − 0.3326 = 0.0137 = 1.37pp → paper says 1.4pp. CONFIRMED (correct rounding to 1 decimal).

**MNLI ep2 delta:** 0.3463 − 0.3234 = 0.0229 = 2.29pp → paper says 2.3pp. CONFIRMED (correct rounding).

**Gradient steps:** 4000 / 32 = 125 per epoch. 125 × 3 = 375 total. Paper states both. CONFIRMED.

**LoRA parameter fraction:** 1,484,288 / 130,000,000 = 0.01141 = 1.141% → stated as 1.14%. CONFIRMED.

**ln(2) = 0.693:** Standard constant. Loss range 0.65–0.73: center = (0.65+0.73)/2 = 0.69, which is 0.003 below ln(2)=0.693. Claim that range is "centered near ln(2)" is approximately correct — the midpoint is 0.69 vs 0.693, a 0.3% difference. CONFIRMED (accurate to the spirit of the claim).

**Binomial SE:** sqrt(0.5092 × 0.4908 / 872) = sqrt(0.24991... / 872) = sqrt(0.000286714) = 0.016933 ≈ 0.0169 ≈ 1.7pp. Paper states "≈ 0.017 (1.7pp)". CONFIRMED.

**1 SE claim:** 1.84pp gain / 1.69pp SE = 1.09 SE. Paper says "approximately 1 SE above the zero-shot baseline." CONFIRMED — 1.09 SE rounds to ~1 SE; the characterization is accurate.

### B. Percentage/decimal consistency across sections

| Location | Form | Value | Consistent? |
|----------|------|-------|-------------|
| Abstract | decimal | 0.5092, 0.4908 | YES |
| Intro §1.1 | percent | 50.9%, 49.1% | YES |
| Intro §1.2 | percent | 50.9% vs 49.1%, 34.6%, 32.3% | YES |
| §1.4 Contributions | decimal | 0.5092, 0.4908, 0.3463, 0.3234 | YES |
| Table 2 | decimal | 0.5092, 0.4908 | YES |
| Table 3 | decimal | 0.3463, 0.3326, 0.3234 | YES |
| Table 3 deltas | pp | −1.4pp, −2.3pp | YES |
| §5.5 | steps | 125/epoch, 375 total | YES |
| §6.1 | decimal | 0.5092, 0.65–0.73 | YES |
| Conclusion §7 | decimal/percent mixed | 0.5092, 49.1%, 0.3463, 0.3234 | YES |

All forms are mutually consistent. No discrepancy found.

### C. "Three identical values = zero learning" — mathematical soundness

The argument: on n=872 with p near 0.5, any stochastic prediction change would produce measurable accuracy variation. Three identical values at 0.5092 eliminate slow-convergence explanations. This argument is mathematically sound for the stated reason: a minimum accuracy shift of 1/872 ≈ 0.0011 (0.11pp) is observable, and the values are reported to 4 decimal places. Three identical readings at 0.5092 on an 872-sample validation set is statistically distinguishable from any prediction distribution change affecting even one example. CONFIRMED.

### D. Loss oscillation centered at ln(2)

Claim: 0.65–0.73 oscillation "centered near ln(2) = 0.693." Midpoint is 0.69, which is 0.003 below ln(2). This is an approximate claim and is accurate — the range spans from 0.043 below ln(2) to 0.037 above it, keeping ln(2) near-center. The description is valid. CONFIRMED.

---

## Part 1: Accuracy Check - Round 2

### FATAL Issues

*None.* All arithmetic and numerical claims verify exactly against ground truth. Cross-section consistency is maintained throughout all sections. R1 additions introduce no numerical errors.

### MAJOR Issues

*None numerical.* All numbers are correct.

---

## Part 2: Credibility Check - Round 2

### FATAL Issues

*None.*

### MAJOR Issues

**MAJOR-CRED-R2-1: "Partial barrier" framing (§6.1 R1 addition) creates tension with §3.4 zero-learning claim**

Location: §6.1, "Clarifying the gradient barrier: partial, not total" paragraph (R1 addition).

The new paragraph argues the barrier is partial, not total, because MNLI degrades (meaning gradient reaches the classification head). This is internally consistent. However, §3.4 states: "Three consecutive identical accuracy values across epochs eliminate all alternative explanations" and specifically "Evaluation bug (same checkpoint evaluated repeatedly) was ruled out by confirming... the LoRA weight values differ between epochs confirming distinct model states were evaluated."

The tension: the new §6.1 text says LoRA matrices DO receive gradient (noise gradient), but §3.4's zero-learning claim says the LoRA matrices are "not changing the model's classification decisions." These are compatible — weights update but predictions don't change — but the paper doesn't explicitly reconcile them. A reviewer will ask: "If LoRA weights are updated by non-discriminative gradient, why is SST-2 accuracy identically 0.5092 to 4 decimal places across all three epochs?" The answer is that non-discriminative updates cancel out at the prediction level (symmetric around the decision boundary), but this is not stated.

Fix: Add one sentence in §6.1 after the partial-barrier paragraph: "The SST-2 flat accuracy despite LoRA weight updates is consistent with this framing: non-discriminative updates that are symmetric with respect to the binary decision boundary produce no net shift in predictions, yielding identical accuracy values even as individual weight values change."

This is a prose fix, not a data fix. Severity: MAJOR (creates an apparent internal contradiction that reviewers will flag).

**MAJOR-CRED-R2-2: SE calculation framing — "approximately 1 SE" understates the noise boundary**

Location: §5.2 — "The observed gain of 1.84pp is approximately 1 SE above the zero-shot baseline — well within one standard error."

The phrase "well within one standard error" is contradicted by the number. 1.84pp at SE=1.7pp is 1.09 SE, which is *just above* 1 SE, not "well within." The correct characterization is "approximately 1 SE above the zero-shot baseline" (which appears first and is accurate) — the follow-up phrase "well within one standard error" mischaracterizes the 1 SE finding. "Well within" typically implies < 0.5 SE; 1.09 SE is not "well within" by any convention.

This is a prose precision error, not an arithmetic error. The conclusion (gain is within noise) is correct — 1 SE is not statistically significant — but "well within" is inaccurate and a careful reviewer will catch it.

Fix: Replace "well within one standard error" with "within one standard error" or "not statistically distinguishable from zero at conventional thresholds."

---

## Part 4: Human Review Notes

| Location | Note | Type |
|----------|------|------|
| §5.2, "well within one standard error" | Phrase is imprecise: 1.84pp / 1.7pp SE = 1.09 SE, which is above 1 SE, not "well within." Change to "within one standard error." | Precision (see MAJOR-CRED-R2-2) |
| §6.1 new paragraph | "partial, not total" framing is good addition from R1 but needs one bridging sentence to explain why SST-2 accuracy is nevertheless identical across epochs if LoRA weights are being updated | Consistency (see MAJOR-CRED-R2-1) |
| §5.5, gradient steps phrasing | Paper §5.5 says "125 gradient steps per epoch (4,000 samples / batch size 32; 375 steps total across 3 epochs)" — this is correct and clear. No change needed. | Verified |
| Table 3 delta notation | "−0.0137 (−1.4pp)" and "−0.0229 (−2.3pp)" — both are correct: 0.0137 = 1.37pp → 1.4pp; 0.0229 = 2.29pp → 2.3pp. No error. | Verified |
| §5.6, ranked MambaPEFT hypotheses | R1 addition: "checkpoint type (base vs. instruction-tuned) is our top candidate" followed by "classification head design" second. This is a reasonable priority ranking given the magnitude (40pp) and consistent with what instruction-tuning does to gradient pathways. The ranking is scientifically defensible. | Verified as reasonable |
| Figure placeholders (Fig 1, Fig 2) | Figure 1: "classification head → SSM scan (dashed, labeled 'non-discriminative gradient') → LoRA matrices" is internally consistent with the partial barrier framing. Figure 2: "SST-2 flat line at 0.5092 across epochs 1-3; zero-shot reference line at 0.4908" matches Table 2 exactly. Both descriptions are accurate to the data. | Verified |
| Abstract confidence hedge | Abstract now reads: "we interpret as acting as a gradient barrier between the classification head and the projection-layer adapters; gradient magnitudes were not directly logged, so this remains a medium-confidence mechanistic interpretation." This correctly hedges MEDIUM confidence from R1 revision per MAJOR-CRED-2 from Round 1. | Fixed from R1 |
| §6.1 "Clarifying" paragraph | Paragraph explicitly labels barrier as "partial," resolves tension with MNLI degradation evidence, and marks it "medium-confidence." This directly addresses MAJOR-CRED-1 from Round 1. | Fixed from R1 |
| §3.4 evaluation bug alternative | Paper now includes: "Evaluation bug...was ruled out by confirming that evaluation was run as a callback at the end of each training epoch, not from a saved checkpoint; the LoRA weight values differ between epochs confirming distinct model states were evaluated." Addresses Round 1 human review note. | Fixed from R1 |
| MNLI halt transparency | §5.3 now explicitly states: "This halting decision was made adaptively based on the observed trajectory — it was not pre-specified as part of the protocol — and is noted explicitly to ensure transparency." Addresses Round 1 human review note. | Fixed from R1 |
| Total gradient steps consistency | §5.5 states "125 gradient steps per epoch × 3 epochs = 375 steps total." Abstract does not state this number. No conflict — 375 is not claimed in abstract. | Verified, no issue |

---

## Summary for Revision Agent

### Priority Fix List

1. **MAJOR-CRED-R2-2 (prose precision, §5.2):** Change "well within one standard error" to "within one standard error" or "not statistically significant at conventional thresholds." The 1.09 SE finding is not "well within" 1 SE. Single word change.

2. **MAJOR-CRED-R2-1 (internal consistency, §6.1):** Add one bridging sentence after the "partial, not total" paragraph explaining why SST-2 accuracy is identically 0.5092 across all three epochs despite LoRA weights being updated. Suggested text: "The SST-2 flat accuracy despite LoRA weight updates is consistent with this framing: non-discriminative updates symmetric with respect to the binary decision boundary produce no net shift in class predictions, yielding identical accuracy values even as individual weight values change."

### What's Working (Confirmed in R2)

- **All arithmetic is exact:** Every calculation in the paper matches ground truth to the stated precision. Net gains, deltas, gradient step counts, SE calculation, LoRA percentage — all verified.
- **Cross-section numerical consistency:** Decimal and percentage forms are consistent across all sections. Table values match text values throughout.
- **R1 additions are numerically clean:** The "partial barrier" paragraph, figure placeholders, and ranked MambaPEFT hypotheses introduce no new numerical claims that could be false.
- **MNLI rounding is correct:** 1.37pp → 1.4pp and 2.29pp → 2.3pp are both standard rounding.
- **SE calculation is valid:** sqrt(0.5092 × 0.4908 / 872) = 0.01694 ≈ 1.7pp; 1.84pp ÷ 1.7pp = 1.09 SE. The conclusion (within noise) is correct; only the word "well" in "well within" is imprecise.
- **ln(2) oscillation center claim:** Midpoint of 0.65–0.73 is 0.69, vs ln(2) = 0.693. 0.3% difference. The "centered near ln(2)" claim is accurate.
- **Round 1 major issues addressed:** Abstract now hedges gradient barrier as medium-confidence (MAJOR-CRED-2 fixed). §6.1 now has "partial, not total" paragraph with MNLI degradation reconciliation (MAJOR-CRED-1 addressed). §5.6 now has ranked hypothesis ordering (MAJOR-CRED-4 addressed). §3.4 now addresses the evaluation-bug alternative explanation.

### Final Verdict

The paper's numerical foundation is correct and internally consistent. The two remaining MAJOR issues are prose precision problems, not data problems. Neither requires re-running experiments or modifying tables. One word change and one sentence addition resolves both. The paper is ready for final submission after these two targeted fixes.
