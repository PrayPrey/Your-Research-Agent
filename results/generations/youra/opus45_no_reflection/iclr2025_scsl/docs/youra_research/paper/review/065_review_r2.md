# Adversarial Review - Round 2 (Numerical Verification)

**Paper:** Emergence Uniformity Cannot Distinguish Spurious Features on Frozen Pretrained Representations
**Reviewed:** 2026-08-19T03:25:00+00:00
**Reviewer:** Adversary Agent (Numerical Focus)
**MCP Used:** Ground truth file (Serena not needed - paper has no baseline comparison claims)

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Numerical Accuracy | 0 | 0 | OK |
| Mathematical Validity | 0 | 0 | OK |
| Baseline Fairness | 0 | 0 | N/A |
| **TOTAL** | **0** | **0** | **CLEAN** |

**Recommendation:** CONDITIONAL_ACCEPT

---

## Ground Truth Verification Log

### Performance Claims

| Metric | Paper Value | Ground Truth | Serena/Source | Match? |
|--------|-------------|--------------|---------------|--------|
| AUC | 0.0 | 0.0 | 04_validation.md | ✓ |
| CV(background) | 0.0393 | 0.0393 | 04_validation.md | ✓ |
| CV(bird_type) | 0.0360 | 0.0360 | 04_validation.md | ✓ |
| AUC threshold | ≥0.75 | 0.75 | ground_truth.yaml | ✓ |

### Experimental Configuration

| Parameter | Paper Value | Ground Truth | Match? |
|-----------|-------------|--------------|--------|
| Feature extractor | CLIP ViT-B/16 | CLIP ViT-B/16 | ✓ |
| Embedding dim | 512 | 512 | ✓ |
| C-sweep | [0.001, 0.01, 0.1, 1, 10, 100] | [0.001, 0.01, 0.1, 1, 10, 100] | ✓ |
| n_subsets | 5 | 5 | ✓ |
| subset_fraction | 20% | 0.2 | ✓ |
| seed | 42 | 42 | ✓ |
| Dataset | Waterbirds | Waterbirds | ✓ |
| Train split | 4,795 | 4795 | ✓ |

---

## Mathematical Validity Analysis

### Check 1: CV Difference Interpretation

**Paper claims:** CV difference = 0.0033 (0.0393 - 0.0360)

**Verification:** 
- CV(spurious) = 0.0393
- CV(core) = 0.0360  
- Difference = 0.0393 - 0.0360 = 0.0033 ✓

**Status:** Mathematically correct

### Check 2: AUC = 0.0 with 2 samples

**Context:** With only 2 feature types (background, bird_type), AUC is binary:
- If CV(spurious) < CV(core) → AUC = 1.0
- If CV(spurious) > CV(core) → AUC = 0.0

**Paper observation:** CV(spurious) = 0.0393 > CV(core) = 0.0360

**Computed AUC:** With the spurious feature ranked ABOVE core by CV (opposite of expected), AUC = 0.0 ✓

**Status:** Mathematically consistent with the "direction reversal" discussed in paper

### Check 3: Trajectory Flatness Claim

**Paper claims:** "Probes converge immediately at all regularization strengths, producing flat trajectories"

**Evidence from ground truth:**
- Both features show ~100% probe accuracy across all C values
- No variation to measure → CV captures only sampling noise

**Status:** Claim is consistent with methodology

---

## Baseline Fairness Assessment

**Not applicable.** This paper presents a negative result about hypothesis validation. No baseline method comparisons are claimed.

The paper explicitly states this is a hypothesis validation paper (H-E1), not a method comparison paper. No claims like "our method beats GroupDRO/JTT/DFR" appear.

---

## Hypothesis Status Verification

| Hypothesis | Paper Status | Ground Truth Status | Match? |
|------------|--------------|---------------------|--------|
| H-E1 (Existence) | FAIL | FAIL (AUC=0.0 < 0.75) | ✓ |
| H-M1 (Mechanism) | NOT_TESTED | NOT_STARTED (blocked by H-E1) | ✓ |
| H-M2 (Threshold) | NOT_TESTED | NOT_STARTED (blocked by H-M1) | ✓ |
| H-M3 (Intervention) | NOT_TESTED | NOT_STARTED (blocked by H-M2) | ✓ |

**Status:** Paper correctly represents hypothesis cascade.

---

## FATAL Issues - Numerical

None identified.

---

## MAJOR Issues - Numerical

None identified.

---

## Minor Notes for Human Review

| Location | Note | Type |
|----------|------|------|
| Section 5.2 | Table formatting could be cleaner | formatting |
| Section 5.5 | "Gate Evaluation" table duplicates info from 5.1 | redundancy |

---

## Summary

### Numerical Verification Result

All numerical claims in the paper match ground truth exactly:
- AUC = 0.0 ✓
- CV values ✓
- Experimental configuration ✓
- Mathematical derivations ✓

### Serena MCP Note

Full Serena MCP search was not required because:
1. This is a hypothesis validation paper (not method comparison)
2. No baseline performance claims to verify against literature
3. Ground truth file already extracts all values from 04_validation.md
4. No Phase 5 baseline comparison exists (blocked by H-E1 failure)

### Convergence Recommendation

**CONVERGED.** Paper passes R2 with:
- FATAL issues: 0
- MAJOR issues: 0
- Numerical accuracy: Verified
- Persuasiveness: Passed in R1

Proceed to Step 07 (Finalize).
