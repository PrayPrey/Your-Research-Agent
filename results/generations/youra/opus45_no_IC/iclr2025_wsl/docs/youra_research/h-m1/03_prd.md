# Product Requirements Document: H-M1

**Hypothesis:** NFN equivariant layers produce permutation-invariant outputs (correlation > 0.99)
**Type:** MECHANISM
**Date:** 2026-08-12
**Gate:** MUST_WORK

---

## 1. Executive Summary

This PRD defines requirements for validating H-M1: verifying that NFN's equivariant layers produce permutation-invariant predictions. This is a property test of the trained H-E1 model, not a new training experiment.

**Objective:** Demonstrate that applying random neuron permutations to input MLP weights produces identical NFN outputs (max deviation < 1e-5 or correlation > 0.99).

---

## 2. Problem Statement

H-E1 demonstrated NFN outperforms MLP (R²=0.9524 vs 0.3529). H-M1 validates the *mechanism*: NFN's advantage comes from built-in permutation equivariance, not other factors.

**Success Criterion:** Output correlation > 0.99 across 10 random permutations.

---

## 3. Functional Requirements

### FR-1: Model Loading
- Load trained NFN from `h-e1/checkpoints/nfn_model.pt`
- Verify model architecture matches H-E1 specification
- Set model to evaluation mode

### FR-2: Test Data Generation
- Generate 1 synthetic MLP with known architecture (hidden_sizes=[64,64], input=784, output=10)
- Use fixed seed=42 for reproducibility
- Output: weight tensors in NFN-compatible format

### FR-3: Permutation Generation
- Generate 10 random neuron permutations (seeds 0-9)
- Each permutation affects hidden layer neurons
- Correctly propagate permutation to adjacent layer connections

### FR-4: Permutation Application
- Apply permutation to hidden layer weights/biases
- Propagate to next layer's input weights
- Maintain functional equivalence of permuted MLP

### FR-5: Prediction Collection
- Run NFN inference on original weights
- Run NFN inference on each of 10 permuted weights
- Collect 11 total predictions

### FR-6: Invariance Metrics
- Compute mean prediction
- Compute standard deviation
- Compute max absolute deviation from mean
- Compute invariance score: 1.0 if max_dev < 1e-5, else 0.0

### FR-7: Visualization
- Bar chart: predictions for original + 10 permuted inputs
- All bars should be identical height if invariant
- Save to `h-m1/figures/permutation_invariance.png`

---

## 4. Non-Functional Requirements

### NFR-1: Performance
- Total execution time < 60 seconds (no training)

### NFR-2: Reproducibility
- All random seeds documented
- Deterministic outputs given same seeds

### NFR-3: Compatibility
- PyTorch >= 1.9
- NFN library (pip install nfn)
- NumPy, Matplotlib

---

## 5. Data Specifications

### Input Data
| Item | Specification |
|------|---------------|
| Source | Generated synthetic MLP weights |
| Format | List of (weight, bias) tuples |
| Seed | 42 |

### Model Checkpoint
| Item | Specification |
|------|---------------|
| Path | h-e1/checkpoints/nfn_model.pt |
| Format | PyTorch state_dict |

---

## 6. Success Criteria

### Primary Gate (MUST_WORK)
```python
gate_passed = (max_deviation < 1e-5) or (invariance_correlation > 0.99)
```

### Metrics
| Metric | Target |
|--------|--------|
| Max Deviation | < 1e-5 |
| Invariance Correlation | > 0.99 |
| Std Deviation | ≈ 0 |

---

## 7. Dependencies

### Code Dependencies
- H-E1 trained model checkpoint
- H-E1 model definition code
- NFN library (pip install nfn)

### Prerequisite Hypotheses
- H-E1: COMPLETED (gate passed with R² diff = 0.5995)

---

## 8. Deliverables

| File | Description |
|------|-------------|
| h-m1/code/test_invariance.py | Main test script |
| h-m1/results.json | Invariance metrics |
| h-m1/figures/permutation_invariance.png | Visualization |
| h-m1/04_validation.md | Gate evaluation report |

---

## 9. Risks

| Risk | Mitigation |
|------|------------|
| NFN implementation bug | Verify with official check_nfn_inv.py reference |
| Incorrect permutation logic | Unit test permutation on simple case |
| Checkpoint compatibility | Load and verify model architecture first |

---

*Generated from Phase 2C experiment brief*
*Next Phase: Architecture Design*
