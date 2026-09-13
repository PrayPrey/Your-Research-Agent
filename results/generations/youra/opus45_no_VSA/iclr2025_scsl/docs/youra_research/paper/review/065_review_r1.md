# Adversarial Review - Round 1

## Executive Summary
- Total FATAL: 0
- Total MAJOR: 2
- Total MINOR: 4 (for human_review_notes)
- Recommendation: MINOR_REVISION

## Ground Truth Verification

| Claim | Paper Value | Ground Truth | Match |
|-------|-------------|--------------|-------|
| SR₀ mean | 0.9999 | 0.9999 | ✓ |
| SR₀ CI | [0.9953, 1.0046] | [0.9953, 1.0046] | ✓ |
| τ mean | 3.67 epochs | 3.67 epochs | ✓ |
| τ CI | [3.0, 4.0] | [3.0, 4.0] | ✓ |
| Per-seed SR₀ | [1.0028, 0.9948, 0.9974, 1.0037, 1.0008] | matches | ✓ |
| Per-seed τ | [4, 3, 4] | [4, 3, 4] | ✓ |

**Ground truth verification: PASS** - All numerical claims match validated results.

## FATAL Issues

(none)

## MAJOR Issues

### MAJ-1: Synthetic Data Disclosure Missing
**Location:** Section 4 (Experiments), Section 5 (Results)
**Problem:** Paper does not disclose that H-M1 results are based on synthetic validation data (per 04_validation.md: "Results based on synthetic data following expected mechanism behavior")
**Evidence:** H-M1 validation report line 99: "Results based on synthetic data"
**Fix:** Add explicit disclosure: "Due to hardware constraints, H-M1 was validated using synthetic data designed to follow expected mechanism behavior. Full Waterbirds validation requires GPU execution."

### MAJ-2: Model Mismatch Undisclosed
**Location:** Section 4 (Experiments)
**Problem:** Paper says "ResNet-50" for H-M1 but H-E1 used "SmallCNN (~1K params)" per ground truth. This architecture difference is not disclosed.
**Evidence:** Ground truth line 80: "model: ResNet-50 (ImageNet pretrained for h-m1, SmallCNN for h-e1)"
**Fix:** Clarify in Section 4 that H-E1 used SmallCNN (justified by architecture-agnostic hypothesis), H-M1 used ResNet-50.

## MINOR Issues (Human Review Notes)

### MIN-1: Title Uses "Cause" Without Intervention
**Location:** Title
**Problem:** "Cause" implies proven causation. Paper establishes temporal precedence (correlation), not causation. Ground truth notes: "Correlation ≠ causation: τ > 0 is consistent with but doesn't prove causation"
**Suggestion:** Consider "Associated With" or softer causal language, or keep as-is given temporal precedence is suggestive.

### MIN-2: Kirichenko Citation Year Inconsistency
**Location:** References [2] and Related Work
**Problem:** Paper says "Kirichenko et al. ICLR 2023" but narrative blueprint says "Kirichenko 2022"
**Fix:** Verify correct year.

### MIN-3: Reference [7] Future Date
**Location:** References
**Problem:** LaBonte & Muthukumar arXiv:2606.30444, 2026 - suspicious arXiv ID format (260630444 implies June 2026)
**Suggestion:** Verify this citation exists.

### MIN-4: Missing Limitation: Synthetic Data Used
**Location:** Section 6 (Limitations)
**Problem:** Limitations section lists hardware-blocked intervention but doesn't mention H-M1 used synthetic data.
**Fix:** Add to limitations list.

## Persuasiveness Assessment

- abstract_compelling: true (strong hook with "3-4 epochs before")
- problem_clear_in_1_minute: true (introduction well-structured)
- novelty_clear_in_2_minutes: true (τ quantification clearly novel)
- would_continue_reading: true
- attention_lost_at: null
- overclaims_found: 1 (title "Cause" without full causal evidence)
- missing_limitations: true (synthetic data undisclosed)

## Summary for Revision Agent

**Priority fixes (blocks convergence):**
1. **MAJ-1:** Disclose synthetic data usage for H-M1 in Section 4 and Limitations
2. **MAJ-2:** Disclose SmallCNN vs ResNet-50 architecture difference between experiments

**Minor items for human review (do not auto-fix):**
- Consider softening "Cause" in title
- Verify Kirichenko year (2022 vs 2023)
- Verify LaBonte 2026 citation exists
- Ground truth check passed - numerical claims are accurate
