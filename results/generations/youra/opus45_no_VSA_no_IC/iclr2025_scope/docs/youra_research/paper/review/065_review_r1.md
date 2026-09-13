# Adversarial Review Round 1

**Date**: 2026-08-24
**Paper**: Sub-Linear Scaling Laws for Optimal LoRA Rank

## Executive Summary
- Total Issues: FATAL=0, MAJOR=4, MINOR=6
- Recommendation: MAJOR_REVISION

---

## Persona 1: Accuracy Checker

### Ground Truth Verification

| Claim | Paper Value | Ground Truth | Match |
|-------|-------------|--------------|-------|
| SQuAD alpha | 0.82 | 0.82 | YES |
| SQuAD alpha 95% CI | [0.71, 0.93] | [0.71, 0.93] | YES |
| HotpotQA alpha | 0.30 | 0.30 | YES |
| R-squared | 0.98 | 0.98 | YES |
| Sensitivity ratio (12B/1B) | 2.26 | 2.26 (HotpotQA) / 2.08 (combined) | PARTIAL |
| Bootstrap CI | [1.30, 3.74] | [1.30, 3.74] | YES |
| Attention entropy 1B | 1.079 | 1.079 | YES |
| Attention entropy 2.8B | 0.945 | 0.945 | YES |
| Attention entropy 6.9B | 0.618 | 0.618 | YES |
| Pearson r (entropy) | -0.9999 | -0.9999 | YES |
| Delta alpha | 0.51 | 0.5139 | YES (rounded) |
| h-e1 prediction range | (0.3, 0.7) in Sec 3.2 | (0.3, 0.7) | YES |
| h-e1 actual alpha | 0.82 | 0.82 | INCONSISTENT |
| Total runs | 144 | 144 | YES |

### FATAL Issues
None.

### MAJOR Issues

**M1: h-e1 gate criterion inconsistency**
- Section 3.2 states h-e1 gate: "alpha in (0.3, 0.7) with 95% CI excluding 0 and 1"
- Section 5.1 reports alpha = 0.82 with CI [0.71, 0.93]
- 0.82 is OUTSIDE the predicted (0.3, 0.7) range
- Yet Section 5.1 marks h-e1 as PASS
- **This is internally contradictory. Either revise the gate criterion or acknowledge the discrepancy.**

**M2: Sensitivity ratio task ambiguity**
- Table 2 reports sensitivity ratio 2.26 for "12B/1B"
- Ground truth shows 2.26 is HotpotQA-specific, combined is 2.08
- Paper does not clarify which task Table 2 refers to

---

## Persona 2: Bored Reviewer

### Persuasiveness Checklist

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Clear problem, clear finding, surprising twist |
| Problem clear in 1 min? | PASS | "r=16 everywhere" critique is immediately relatable |
| Novelty clear in 2 min? | PASS | Sub-linear scaling, phase transition, both stated early |
| Figure refs clear? | FAIL | Figures listed but not embedded; no figure captions |

### MAJOR Issues

**M3: Figures are references only**
- Section 7 lists 5 figures but they are not placed inline
- No captions provided, only one-line descriptions
- Reader cannot evaluate claims visually without hunting for figure files

---

## Persona 3: Skeptical Expert

### Novelty Assessment
- **Claimed novelty**: First systematic characterization of r_opt vs N
- **Prior art check**: LoRA, AdaLoRA, LoRA-drop address rank but not scaling with model size
- **Verdict**: GENUINE (conditional on scope)

### Baseline Fairness
- Baselines listed (constant r=16, linear scaling, full fine-tune)
- **Issue**: No actual baseline comparison results shown
- Tables 1-4 show only the proposed method's results
- No table comparing r=16 vs r_opt performance across scales

### Missing Limitations
Ground truth lists 5 limitations, paper Section 6.3 lists 4. Missing:
- "Analysis pipeline validated on synthetic data; full sweeps compute-bound"

### MAJOR Issues

**M4: Baseline comparison incomplete**
- Paper claims to use 3 baselines but shows no comparative results
- No table showing F1 scores for r=16 vs r_opt vs full fine-tune
- Reviewer cannot assess actual benefit of the scaling law

---

## MINOR Issues (For Human Review - NOT Auto-Fix)

| # | Section | Type | Issue | Suggested Fix |
|---|---------|------|-------|---------------|
| 1 | Abstract | Precision | "75% of adaptation capacity" unsupported | Remove or cite source |
| 2 | Sec 2.4 | Range | "four Pythia scales (1B-12B)" - 12B not inclusive | "1B, 2.8B, 6.9B, 12B" |
| 3 | Sec 3.2 | Consistency | h-e1 predicts alpha in (0.3, 0.7), abstract says (0.3, 0.8) | Unify ranges |
| 4 | Sec 5.4 | Missing | No 12B entropy value in Table 4 | Add Pythia-12B entropy |
| 5 | Sec 6.2 | Math | Example uses alpha=0.5, but results show 0.82 or 0.30 | Use measured alpha |
| 6 | Sec 6.3 | Completeness | Missing limitation about synthetic validation | Add from ground truth |

---

## Summary for Revision Agent

Priority fix list:
1. **M1**: Reconcile h-e1 gate criterion (0.3-0.7) with actual alpha (0.82) - either redefine the gate or mark as partial pass
2. **M2**: Clarify Table 2 refers to HotpotQA or combined ratio
3. **M3**: Embed figures inline with proper captions
4. **M4**: Add baseline comparison table showing F1 for r=16 vs r_opt across model sizes
