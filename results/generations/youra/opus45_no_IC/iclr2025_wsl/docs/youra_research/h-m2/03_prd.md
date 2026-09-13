# Product Requirements Document: H-M2

**Hypothesis:** NFN predictions identical under weight permutation (diff < 1e-5)
**Type:** MECHANISM
**Date:** 2026-08-12
**Author:** PrayPrey

---

## Executive Summary

H-M2 verifies that NFN final scalar predictions are invariant under weight-space permutations. This extends H-M1's layer-level invariance verification to end-to-end prediction invariance. Uses existing H-M1 infrastructure with modified gate criterion.

**Gate Condition:** |pred_original - pred_permuted| < 1e-5 for all 10+ permutations

---

## Problem Statement

H-M1 demonstrated NFN layer outputs are permutation-invariant (max_deviation = 1.19e-07). H-M2 must verify this invariance propagates through the final linear layer to scalar predictions.

**Success Criterion:** All predictions identical within floating-point tolerance (1e-5).

---

## Functional Requirements

### FR-1: Test Data Generation
- Generate synthetic test MLP using H-M1's `generate_test_mlp()` function
- Architecture: 32-32-32-10 (matches H-E1 checkpoint)
- Seed: 42 for reproducibility

### FR-2: NFN Model Loading
- Load pre-trained NFN from H-E1 checkpoint: `h-e1/checkpoints/nfn_model.pt`
- Use H-M1's `NFNRegressor` wrapper
- Set model to eval mode

### FR-3: Permutation Generation
- Generate 10 random permutations using H-M1's `generate_permutations()`
- Apply to test MLP state dict using `permute_state_dict()`

### FR-4: Prediction Invariance Test
- Compute original prediction on base MLP
- Compute predictions on all 10 permuted variants
- Calculate max_deviation = max(|pred_i - pred_j|) for all pairs

### FR-5: Gate Evaluation
- Pass criterion: max_deviation < 1e-5
- Store gate result in verification_state.yaml

### FR-6: Visualization
- Bar chart: 11 predictions (original + 10 permuted)
- Deviation heatmap: pairwise differences
- Save to h-m2/figures/

---

## Non-Functional Requirements

### NFR-1: Code Reuse
- MUST reuse H-M1 modules: test_data.py, permute.py, metrics.py, model.py
- NO new model training required

### NFR-2: Reproducibility
- Fixed seed (42) for test MLP generation
- Deterministic permutation seeds (0-9)

### NFR-3: Performance
- Single MLP, 10 permutations = 11 forward passes
- Expected runtime: < 1 second

---

## Data Specifications

| Item | Source | Format |
|------|--------|--------|
| Test MLP | `generate_test_mlp(seed=42)` | state_dict |
| NFN Checkpoint | h-e1/checkpoints/nfn_model.pt | PyTorch |
| Permutations | `generate_permutations(hidden_dims, seed)` | List[torch.Tensor] |

---

## Success Criteria

| Metric | Threshold | Expected |
|--------|-----------|----------|
| max_deviation | < 1e-5 | ~1e-7 (based on H-M1) |
| gate_passed | True | True |
| predictions_count | 11 | 11 |

---

## Dependencies

- **H-E1:** NFN checkpoint (COMPLETED)
- **H-M1:** Invariance infrastructure code (COMPLETED, gate PASSED)

---

## Out of Scope

- Training new models
- Comparing with baselines (covered by H-E1)
- Large-scale evaluation (covered by H-E1)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Final linear layer breaks invariance | Very Low | High | Architecture uses HNPPool (invariant) before linear |
| Floating-point accumulation | Low | Low | 1e-5 threshold generous vs 1e-7 observed |

---

*Phase 2C Source: h-m2/02c_experiment_brief.md*
*Next Phase: Architecture Design*
