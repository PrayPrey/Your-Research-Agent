# Product Requirements Document: H-M3

**Hypothesis:** Untrained MLP shows no permutation invariance (correlation < 0.3)
**Type:** MECHANISM
**Date:** 2026-08-12
**Author:** Anonymous

---

## Executive Summary

H-M3 establishes the negative control: an untrained (randomly initialized) MLP has NO built-in permutation invariance. When fed permuted weight vectors as input, outputs vary significantly (correlation < 0.3). This contrasts with NFN's perfect invariance (H-M2: max_dev=1.19e-07), confirming equivariance is architectural (NFN) vs learned (MLP).

**Gate Condition:** Output correlation < 0.3 across 10 random permutations OR coefficient of variation > 0.1

---

## Problem Statement

H-M1/H-M2 demonstrated NFN has perfect permutation invariance at both layer and prediction level. H-M3 tests the opposite: an untrained MLP should show HIGH variance when processing permuted inputs, because standard MLP architecture lacks equivariance constraints.

**Success Criterion:** Outputs vary significantly across permutations (no inherent invariance).

---

## Functional Requirements

### FR-1: Test Data Generation
- Reuse H-M1's `generate_test_mlp()` for test CNN weights
- Architecture: 32-32 hidden layers (matches H-M1)
- Seed: 42 for reproducibility

### FR-2: MLP Model Creation
- Create MLPMatched model (NOT NFN)
- Architecture: input_dim → 256 → 128 → 1
- Random initialization (Kaiming uniform default)
- NO TRAINING - test at initialization

### FR-3: Permutation Generation
- Reuse H-M1's `generate_permutations()` function
- Generate 10 permutations using seeds 0-9

### FR-4: Variance Test
- Flatten CNN state_dict to vector (MLP input format)
- Compute prediction on original + 10 permuted vectors
- Calculate coefficient of variation (std/mean)
- Calculate max deviation from mean

### FR-5: Gate Evaluation
- Pass criterion: CV > 0.1 OR max_deviation > 0.01 (high variance = no invariance)
- Store gate result in verification_state.yaml

### FR-6: Visualization
- Prediction distribution histogram (expect wide spread)
- Bar chart: 11 predictions (should show variance)
- NFN vs MLP comparison (tight clustering vs scatter)
- Save to h-m3/figures/

---

## Non-Functional Requirements

### NFR-1: Code Reuse
- MUST reuse H-M1 modules: test_data.py, permute.py
- NEW: mlp_model.py (MLPMatched class)
- NEW: test_variance.py (main script)

### NFR-2: Reproducibility
- Fixed seed (42) for test data
- Fixed seed (1042) for MLP initialization
- Deterministic permutation seeds (0-9)

### NFR-3: Performance
- Single MLP, 11 forward passes
- Expected runtime: < 1 second

---

## Data Specifications

| Item | Source | Format |
|------|--------|--------|
| Test CNN weights | `generate_test_mlp(seed=42)` | state_dict |
| Permutations | `generate_permutations(hidden_dims, seed)` | List[torch.Tensor] |
| MLP Model | MLPMatched(input_dim) | nn.Module |

**Note:** No external datasets needed - procedurally generated test weights.

---

## Success Criteria

| Metric | Threshold | Expected |
|--------|-----------|----------|
| coefficient_of_variation | > 0.1 | > 0.3 (random outputs) |
| max_deviation | > 0.01 | > 0.1 |
| gate_passed | True | True |
| predictions_count | 11 | 11 |

---

## Dependencies

### Code Dependencies (from H-M1)
- `test_data.py` - generate_test_mlp()
- `permute.py` - generate_permutations(), permute_state_dict()

### Hypothesis Dependencies
- **H-M2:** COMPLETED (max_dev=1.19e-07, invariance_corr=0.9999999)

---

## Out of Scope

- NFN testing (covered by H-M1/H-M2)
- MLP training (this tests untrained behavior)
- Large-scale evaluation

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| MLP accidentally invariant | Very Low | High | Random init has no symmetry constraints |
| Numerical issues | Low | Low | Standard float32 sufficient |

---

*Phase 2C Source: h-m3/02c_experiment_brief.md*
*Next Phase: Architecture Design*
