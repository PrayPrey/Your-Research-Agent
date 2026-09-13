# Phase 4 Validation Report: H-M3
# SymCanon-WSL — NFT with Weight Symmetry Canonicalization

**Hypothesis ID:** h-m3  
**Gate type:** SHOULD_WORK  
**Gate result:** FAIL (DOCUMENT — non-blocking)  
**Generated:** 2026-08-27  

---

## Hypothesis Statement

Applying both scaling and sign-flip canonicalization (Condition D) before NFT encoding on Schürholt MNIST zoo achieves Spearman ρ at least 0.05 higher than raw weight NFT (Condition A) on test accuracy, and ρ_D > ρ_E (random normalization control) on ≥2/3 tasks, confirming the improvement is symmetry-specific.

---

## Experiment Setup

- **Dataset:** Schürholt MNIST MLP zoo (N=500 total; train=400, val=50, test=50)
- **Conditions:** A (raw), B (scale only), C (sign-flip only), D (both), E (random norm control), F (linear baseline)
- **Seeds:** [42, 123, 456]; results aggregated (mean ± 95% CI)
- **NFT architecture:** 3.4M params; embed_dim=256, n_layers=4, nhead=8
- **Training:** Adam lr=1e-3, wd=1e-4, max_epochs=50, early stopping patience=10 on val Spearman ρ
- **Evaluation:** Spearman ρ with 1000-sample bootstrap CI on test set (n=50)

---

## Canonicalization Verification

All conditions verified via `verify_canonicalization_activated`:

| Condition | Indicator | Pass |
|-----------|-----------|------|
| A | no_change | ✓ |
| B | norms_unit | ✓ |
| C | majority_positive | ✓ |
| D | norms_unit + majority_positive | ✓ |
| E | differs_from_B | ✓ |

---

## Results: Aggregated Spearman ρ (mean ± 95% CI, 3 seeds)

| Condition | test_accuracy | gen_gap | learning_rate |
|-----------|---------------|---------|---------------|
| A (raw) | -0.054 [-0.345, +0.241] | -0.031 [-0.285, +0.250] | -0.017 [-0.299, +0.244] |
| B (scale) | -0.004 [-0.280, +0.278] | -0.112 [-0.398, +0.184] | -0.031 [-0.309, +0.266] |
| C (sign) | -0.010 [-0.292, +0.272] | +0.016 [-0.272, +0.308] | -0.021 [-0.297, +0.247] |
| **D (both)** | **+0.004** [-0.287, +0.287] | **+0.022** [-0.260, +0.318] | **+0.059** [-0.253, +0.343] |
| E (rand ctrl) | +0.068 [-0.205, +0.343] | +0.034 [-0.256, +0.314] | +0.154 [-0.133, +0.409] |
| F (linear) | -0.208 [-0.468, +0.068] | -0.133 [-0.392, +0.178] | +0.064 [-0.226, +0.315] |

---

## Gate Check P1: Δρ_D-A ≥ 0.05 AND CI excludes 0

| Label | Δρ_D-A | Δρ ≥ 0.05 | CI excl 0 | Pass |
|-------|--------|-----------|-----------|------|
| test_accuracy | +0.058 | ✓ | ✗ | **FAIL** |
| generalization_gap | +0.053 | ✓ | ✗ | **FAIL** |
| learning_rate | +0.077 | ✓ | ✗ | **FAIL** |

Δρ meets or approaches the 0.05 threshold on all labels, but CIs are extremely wide (±0.3–0.5) due to n=50 test set.

## Gate Check P2: ρ_D > ρ_E on ≥2/3 tasks

| Label | ρ_D | ρ_E | D > E |
|-------|-----|-----|-------|
| test_accuracy | +0.004 | +0.068 | ✗ |
| generalization_gap | +0.022 | +0.034 | ✗ |
| learning_rate | +0.059 | +0.154 | ✗ |

**n_pass = 0/3 (required 2/3). P2 FAIL.**

ρ_E consistently exceeds ρ_D — the random normalization control outperforms the canonicalized NFT on all tasks. This contradicts the symmetry-specificity claim.

---

## Key Findings

1. **Δρ_D-A in right direction but statistically underpowered.** All three labels show Δρ > 0.05 (P1 threshold met), but n=50 test set produces CIs of width ~0.6, making all comparisons statistically non-significant.

2. **P2 failed: ρ_E > ρ_D on all 3 tasks.** The random normalization control (Condition E) outperforms full canonicalization (Condition D). This is unexpected and suggests the NFT improvement (if any) is not symmetry-specific.

3. **All ρ values near 0.** NFT property prediction on this 500-model zoo with 50-sample test set yields near-random performance across all conditions, consistent with H-M2's finding that N=500 is too small for reliable property regression.

4. **E > D pattern is consistent.** The E-beats-D pattern holds across all 3 seeds and all 3 labels, suggesting a systematic effect: random normalization may provide better-conditioned inputs than canonical normalization for NFT training.

5. **Frozen encoder experiment:** Skipped (insufficient A-checkpoint quality given near-zero val ρ).

---

## Root Cause Analysis

The E > D pattern warrants analysis:

- Condition E applies random unit-direction × B-norm. This preserves the magnitude structure of B but randomizes directions.
- Condition D applies canonical normalization: both norms AND sign flips.
- Hypothesis: The sign-flip canonicalization in D may destroy within-batch variance that the NFT relies on to discriminate models. Random direction (E) preserves some diversity that D removes.
- Alternative: The test set (n=50) is too small for reliable Spearman ρ estimation; E beats D by chance in this sample.

---

## Limitations

- **n=500 zoo, n=50 test:** CI width ≈ 0.6; Δρ=0.05 requires CI width < 0.05 to be detectable. This dataset is too small for the stated gate.
- **No pre-trained NFT checkpoint:** Training from scratch on 400 samples is severely underpowered for a 3.4M parameter model.
- **Consistent with H-M2:** The PCA-based predecessor also found no detectable improvement from canonicalization at N=500.

---

## Gate Verdict

**Gate: SHOULD_WORK → FAIL (DOCUMENT)**

The hypothesis is not confirmed. Gate failure is non-blocking per SHOULD_WORK protocol.

**Causal claim revision:** Canonicalization concentrates geometric structure (confirmed by H-M2 PCA EVR analysis) but does not improve NFT-based property prediction at N=500. The effect size may exist at larger N (>5k models) but is undetectable in this zoo.

---

## Proceed to H-C1

Per hypothesis graph, H-M3 DOCUMENT-path routes to H-C1 (or pipeline continuation). The MECHANISM chain is complete:
- H-M1: VALIDATED (NFT property prediction feasible)
- H-M2: DOCUMENT (PCA canonicalization EVR improves, R² does not)
- H-M3: DOCUMENT (NFT Δρ > 0.05 in point estimate, but not significant; E > D)
