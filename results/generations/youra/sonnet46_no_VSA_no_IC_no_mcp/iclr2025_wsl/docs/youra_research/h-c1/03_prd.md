# PRD: H-C1 — Sign-Flip Canonicalization Uniqueness Audit

**Hypothesis:** H-C1  
**Type:** CONDITION (scope boundary verification)  
**Date:** 2026-08-27  
**Author:** yoon303b@gmail.com  
**Phase 2C Source:** 02c_experiment_brief.md  

---

## 1. Executive Summary

H-C1 validates that the sign-flip canonicalization algorithm — majority-sign simultaneous flip for the single consecutive layer pair in M=2 MLPs — produces a unique deterministic canonical form for ≥99% of Schürholt MNIST zoo models sampled (N=500). This is a low-cost algorithmic audit (~60 seconds CPU), not a training experiment. The output characterizes the scope boundary of sign-flip canonicalization for the M=2 setting and confirms whether Assumption A4 from the H-M3 chain holds.

**Key deliverables:**
- `fraction_unique` and `fraction_idempotent` measured over 500 zoo models
- Characterization of degenerate cases (if any)
- Gate verdict: PASS (≥99% unique) or SCOPE BOUNDARY (<95% unique)

---

## 2. Problem Statement

H-M3 showed that sign-flip canonicalization ran without crash on N=500 zoo models (informal observation), but did not systematically measure the fraction of models for which the canonical form is unique and deterministic. Exact sign ties (equal counts of positive and negative weights in a neuron's incoming weight column) cause ambiguity in the canonical form. For d_in=784 this is theoretically negligible, but must be confirmed empirically on the actual zoo weight distribution.

**Core question:** For Schürholt MNIST zoo M=2 MLPs, does majority-sign simultaneous flip produce a unique canonical form for ≥99% of models?

---

## 3. Scope

### In Scope
- Sign-flip canonicalization (majority-sign simultaneous flip)
- M=2 MLPs only (784→64→10), single consecutive layer pair
- Schürholt MNIST zoo (HuggingFace), 500 uniformly sampled models
- Uniqueness check: `is_degenerate` (any neuron with exact sign tie)
- Idempotency check: `canon(canon(W)) == canon(W)` for all models
- Degeneracy characterization: tied neuron count, weight statistics

### Out of Scope
- Training new models
- Permutation canonicalization
- M>2 MLPs
- Performance/accuracy prediction (separate from H-M3)

---

## 4. Data Specification

### Primary Dataset

| Field | Value |
|-------|-------|
| Name | Schürholt MNIST Model Zoo |
| Source | HuggingFace: `MarcBrun/model-zoos` |
| Architecture | M=2 MLP (784→64→10), no BN, no WN |
| Zoo size | ~50,000 trained models |
| Sample size | N=500 (uniformly random) |
| Sampling seed | 1 (same as H-M3 for reproducibility) |
| Data split | None (all 500 are "subjects", not train/val/test) |
| Download | Auto-download via HuggingFace `datasets` library |
| Local path | `./data/` (auto-managed) |

**Loading code:**
```python
from datasets import load_dataset
zoo = load_dataset("MarcBrun/model-zoos", split="train")
```

**Weight extraction:**
```python
# Each zoo model record contains weight matrices
# W1: (64, 784), W2: (10, 64)
# Confirmed format from H-E1 and H-M3
```

**Manual download required:** No — HuggingFace auto-download.

---

## 5. Functional Requirements

### FR-1: Dataset Loading
Load Schürholt MNIST zoo via HuggingFace `datasets`, extract W1 (64,784) and W2 (10,64) for each of 500 sampled models. Verify shapes.

**Acceptance:** 500 models loaded; all W1.shape==(64,784), W2.shape==(10,64).

### FR-2: Sign-Flip Canonicalization (Reused from H-M3)
Implement `exact_majority_sign(weights)` and `canonicalize_sign_flip_m2(W1, W2)` as specified in 02c_experiment_brief.md. Tie-breaking: default to +1.

**Acceptance:** Function runs without error on all 500 models; returns W1_canon, W2_canon, is_degenerate.

### FR-3: Uniqueness Audit
For each of 500 models, record `is_degenerate` flag. Compute `fraction_unique = sum(not degen) / 500`.

**Acceptance:** `fraction_unique` computed; gate check against 0.99 threshold.

### FR-4: Idempotency Check
For each model, verify `canon(canon(W)) == canon(W)`. Compute `fraction_idempotent`.

**Acceptance:** `fraction_idempotent == 1.00` (must be exact for all 500 models).

### FR-5: Degeneracy Characterization (Conditional)
If any degenerate models found: compute `mean_tied_neurons_per_degenerate_model`, `weight_norm_of_tied_neurons`, and cluster analysis by accuracy bin.

**Acceptance:** Characterization report generated if degenerate count > 0; "No degenerate cases found" report otherwise.

### FR-6: Visualization
- **Mandatory:** Bar chart — `fraction_unique` vs 0.99 threshold (gate pass/fail)
- **Conditional:** Histogram of tied neuron counts per degenerate model (if any found)
- **Conditional:** Scatter — weight L1-norm of tied neurons vs fraction tied
- All figures saved to `docs/youra_research/h-c1/figures/`

**Acceptance:** At least the mandatory bar chart is generated and saved.

### FR-7: Result Summary and Gate Verdict
Print structured summary: `fraction_unique`, `fraction_idempotent`, gate verdict (PASS/FAIL/SCOPE), degenerate count.

**Acceptance:** Summary printed; gate verdict rendered against thresholds from 02c_experiment_brief.md.

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Runtime | < 60 seconds on CPU |
| Compute | CPU-only sufficient |
| Reproducibility | Fixed seed (1); same as H-M3 |
| Code reuse | Reuse H-M3 canonicalization code directly |
| Self-check | Assert-based idempotency check on first model before full audit |

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=1.12.0
numpy>=1.21.0
datasets>=2.0.0       # HuggingFace datasets (auto-download zoo)
matplotlib>=3.5.0
```

### 7.2 Codebase Dependencies
- H-M3 canonicalization code (`h-m3/code/canonicalize.py` or equivalent)
- If H-M3 code unavailable: implement from scratch per 02c_experiment_brief.md spec

### 7.3 External References
- Godfrey et al. 2022 "Symmetries of Neural Networks" — theoretical basis
- Schürholt et al. 2022 "Model Zoos" — dataset source

---

## 8. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| P1 (Gate): `fraction_unique` | ≥ 0.99 | SHOULD_WORK |
| P2 (Gate): `fraction_idempotent` | == 1.00 | MUST |
| Degeneracy characterization | Present if degen > 0 | Required |
| Runtime | < 60s CPU | NFR |
| Mandatory figure generated | Yes | Required |

**Failure handling:**
- `fraction_unique` ∈ [0.95, 0.99): propose tie-breaking rule, document as limitation, gate = DOCUMENT
- `fraction_unique < 0.95`: SCOPE BOUNDARY — recommend falling back to scaling-only (Condition B)

---

## 9. Evaluation Protocol

1. Load 500 zoo models (seed=1)
2. Self-check: assert idempotency on first model
3. For each model: `canonicalize_sign_flip_m2(W1, W2)` → record is_degenerate, is_idempotent
4. Compute fraction_unique, fraction_idempotent
5. If degenerate > 0: run characterization
6. Generate visualizations
7. Print gate verdict

---

## 10. Traceability

| Item | Source |
|------|--------|
| Gate thresholds (99%, 100%) | 02b_verification_plan.md, 02c_experiment_brief.md |
| Algorithm spec | 02c_experiment_brief.md §Core Mechanism |
| Dataset spec | 02c_experiment_brief.md §Dataset |
| Tie-breaking | Domain knowledge + H-M3 prior |
| Implementation reuse | H-M3 prior hypothesis |
