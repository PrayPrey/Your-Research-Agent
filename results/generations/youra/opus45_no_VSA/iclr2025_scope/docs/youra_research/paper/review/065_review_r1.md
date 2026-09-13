# Adversarial Review Round 1: Structural Issues

**Date:** 2026-08-09
**Round:** R1 - Accuracy and Engagement
**Personas:** Accuracy Checker, Bored Reviewer, Skeptical Expert

---

## Executive Summary

| Category | FATAL | MAJOR | MINOR |
|----------|-------|-------|-------|
| Accuracy Checker | 0 | 0 | 1 |
| Bored Reviewer | 0 | 1 | 2 |
| Skeptical Expert | 0 | 0 | 1 |
| **Total** | **0** | **1** | **4** |

**Recommendation:** MINOR_REVISION - No FATAL issues. One MAJOR issue (Figure 1 referenced but not described). Paper is well-structured with honest limitations.

---

## Ground Truth Verification Summary

All quantitative claims verified against 065_ground_truth.yaml:

| Claim ID | Paper Value | Ground Truth | Status |
|----------|-------------|--------------|--------|
| Q1 (Macro-F1) | 0.995 | 0.995 | ✅ MATCH |
| Q2 (Baseline F1) | 0.115 | 0.115 | ✅ MATCH |
| Q3 (Top-1 Acc) | 72.67% | 72.67% | ✅ MATCH |
| Q4 (Top-3 Acc) | 95.78% | 95.78% | ✅ MATCH |
| Q5 (vs Random) | 14.8x | 14.8x | ✅ MATCH |
| Q6 (IPCR/Oracle) | 95.00% | 95.00% | ✅ MATCH |
| Q7 (Oracle) | 91.39% | 91.39% | ✅ MATCH |
| Q8 (IPCR) | 86.82% | 86.82% | ✅ MATCH |
| Q9 (Uniform) | 36.79% | 36.79% | ✅ MATCH |
| Q10 (Random) | 14.97% | 14.97% | ✅ MATCH |
| Q11 (t-stat) | 68.99, p=7.05e-224 | 68.99, 7.05e-224 | ✅ MATCH |
| Q12 (Cosine) | 0.78 | 0.782 | ✅ MATCH (rounded) |
| Q13 (Mask drop) | 44% | 44.4% | ✅ MATCH (rounded) |
| Q14 (Consistency) | 76.1% | 76.1% | ✅ MATCH |

**Ground Truth Discrepancies: 0**

---

## FATAL Issues

None.

---

## MAJOR Issues

### MAJ-001: Figure 1 Referenced but Not Described (Bored Reviewer)

**Location:** Section 5 (Results), line: "Figure 1 shows t-SNE visualization..."

**Problem:** Paper references "Figure 1" as showing t-SNE visualization of embedding space, but:
1. No figure description/caption provided
2. No actual figure content or placeholder
3. Reader cannot evaluate the visual claim

**Impact:** Reviewers will note missing figure. Undermines the "clear clustering" claim.

**Required Fix:** Either:
- Add Figure 1 with proper caption and description
- Remove the reference if figure will be added later in LaTeX
- Change to "Supplementary Figure S1" if relegated to appendix

**Ground Truth Evidence:** H-E0 validation confirms tsne_embeddings.png was generated, but paper text lacks description.

---

## MINOR Issues (Human Review Notes)

### MIN-001: Rounding Inconsistency (Accuracy Checker)

**Type:** formatting

**Location:** Results section

**Issue:** Some values rounded (cosine 0.78 vs ground truth 0.782; drop 44% vs 44.4%), others exact (86.82%, 95.78%).

**Suggestion:** Use consistent rounding convention (e.g., 2 decimal places for all percentages).

### MIN-002: Citation Format (Bored Reviewer)

**Type:** style

**Location:** Related Work

**Issue:** "LORAUTER [Dhasade et al., 2026]" - future date (2026) suggests preprint or prediction.

**Suggestion:** Verify citation year; if preprint, note "(preprint)" or use correct date.

### MIN-003: "cot_" Prefix in Task Names (Bored Reviewer)

**Type:** clarity

**Location:** Section 4 (Experiments)

**Issue:** Task family names include "cot_" prefix (cot_gsm8k, cot_esnli) which may confuse readers unfamiliar with FLAN.

**Suggestion:** Clarify on first use that "cot_" = "chain-of-thought" prefix in FLAN.

### MIN-004: Oracle Approximation Disclosure (Skeptical Expert)

**Type:** clarity

**Location:** Section 6 (Discussion) - Limitation L4

**Issue:** L4 ("Oracle approximation") is mentioned but could be clearer that H-E1 used task names rather than per-sample adapter loss.

**Suggestion:** State explicitly: "We used task-family names as oracle labels rather than computing per-adapter loss for each sample."

---

## Persuasiveness Assessment (Bored Reviewer)

| Check | Result |
|-------|--------|
| Abstract compelling? | ✅ YES - Concrete (95%, F1=0.995), honest limitation |
| Problem clear in 1 min? | ✅ YES - Validation data gap stated in para 2 |
| Novelty clear in 2 min? | ✅ YES - "intrinsic alignment" framing |
| Figure 1 self-explanatory? | ❌ NO - Figure referenced but not present |
| Would continue reading? | ✅ YES - Hook effective |
| Attention lost at? | Never |

**Persuasiveness Passed:** Conditional (pending Figure 1 fix)

---

## Cross-Reference Verification

| Check | Status |
|-------|--------|
| Abstract numbers = Results numbers | ✅ |
| Methodology = Experiments setup | ✅ |
| Thresholds consistent throughout | ✅ |
| Limitation L1-L4 match H-M2 findings | ✅ |
| Statistical significance properly reported | ✅ |

---

## Summary for Revision Agent

### Must Fix (MAJOR)
1. **MAJ-001:** Add Figure 1 description or remove reference

### Collect for Human Review (MINOR)
1. MIN-001: Rounding consistency
2. MIN-002: Citation date (2026)
3. MIN-003: "cot_" prefix explanation
4. MIN-004: Oracle approximation clarity

---

*Review completed by Adversary Agent R1*
*All claims verified against ground truth: 14/14 MATCH*
