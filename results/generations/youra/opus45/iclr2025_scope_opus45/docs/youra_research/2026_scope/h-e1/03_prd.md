# Product Requirements Document: H-E1

**Hypothesis:** Spectral Memory Horizon Stability in Pretrained Mamba Models
**Type:** EXISTENCE (PoC)
**Date:** 2026-03-27
**Author:** Anonymous
**Status:** Draft

---

## 1. Executive Summary

This PRD defines the implementation requirements for validating hypothesis H-E1: measuring whether the spectral memory horizon H_spec = -1/log|λ_max| is a stable, measurable property of pretrained Mamba models with coefficient of variation CV < 0.3 across different input sequences.

**Key Deliverable:** A measurement framework that computes H_spec across 1000 random input sequences and reports CV to validate stability.

**Success Criterion:** CV(H_spec) < 0.3

---

## 2. Problem Statement

### 2.1 Background
The Memory Horizon Separation Hypothesis (MHSH) and Eigenmode Utilization Hypothesis (EUH) depend on H_spec being a stable, intrinsic model property. If H_spec varies significantly with input, the entire theoretical framework collapses.

### 2.2 Research Gap
No prior work has measured and reported H_spec stability across input sequences for Mamba models. This is the foundation for all subsequent mechanism hypotheses (H-M1 through H-M4).

### 2.3 Gate Condition
**MUST_WORK Gate:** If CV(H_spec) >= 0.3, the entire MHSH/EUH framework is invalidated and the pipeline stops.

---

## 3. Functional Requirements

### FR-1: Model Loading
- **Description:** Load pretrained Mamba-1.4B model
- **Source:** state-spaces/mamba (HuggingFace)
- **Acceptance:** Model loads without error, A_log parameters accessible

### FR-2: Random Sequence Generation
- **Description:** Generate 1000 random token sequences for eigenvalue probing
- **Parameters:**
  - Sequence length: 512 tokens
  - Vocabulary size: Mamba tokenizer vocabulary
  - Sample count: 1000
- **Acceptance:** 1000 sequences generated with reproducible seed

### FR-3: Eigenvalue Extraction
- **Description:** Extract A matrix eigenvalues from each Mamba layer
- **Method:** Access A_log parameter, compute exp(A_log) for diagonal eigenvalues
- **Acceptance:** Eigenvalues extracted for all 48 layers

### FR-4: H_spec Computation
- **Description:** Compute spectral memory horizon H_spec = -1/log|λ_max|
- **Method:** Find maximum eigenvalue magnitude across all layers
- **Acceptance:** Single H_spec value computed per sequence

### FR-5: CV Computation
- **Description:** Calculate coefficient of variation across all sequences
- **Formula:** CV = std(H_spec) / mean(H_spec)
- **Acceptance:** CV value computed with mean and std reported

### FR-6: Scale Consistency Check (Secondary)
- **Description:** Cross-validate H_spec on Mamba-370M for scale consistency
- **Expectation:** H_spec scales monotonically with model size
- **Acceptance:** H_spec values for both models reported

### FR-7: Visualization
- **Description:** Generate required figures
- **Figures:**
  1. H_spec Distribution Histogram (mean, std, CV annotated)
  2. Gate Metrics Comparison (target vs actual bar chart)
  3. H_spec per Layer (optional)
  4. Scale Comparison (optional, if FR-6 executed)
- **Acceptance:** Figures saved to `figures/` subfolder

---

## 4. Data Specification

### 4.1 Input Data

| Dataset | Type | Source | Download |
|---------|------|--------|----------|
| Random Token Sequences | programmatic-api | torch.randint() | N/A (generated) |

**No manual download required** - sequences are generated programmatically at runtime.

### 4.2 Model Checkpoints

| Model | Source | Method |
|-------|--------|--------|
| Mamba-1.4B | state-spaces/mamba-1.4b | HuggingFace auto-download |
| Mamba-370M | state-spaces/mamba-370m | HuggingFace auto-download |
| Tokenizer | EleutherAI/gpt-neox-20b | HuggingFace auto-download |

**No manual download required** - models auto-download via HuggingFace.

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Complete measurement in < 2 hours on single GPU
- Memory usage < 16GB (Mamba-1.4B inference)

### NFR-2: Reproducibility
- Fixed random seed for sequence generation
- Deterministic eigenvalue computation (float64 precision)

### NFR-3: Numerical Precision
- Eigenvalue computation in float32/64 (SSMs sensitive to precision)
- Report precision in results

---

## 6. Success Criteria

### Primary Gate (MUST_WORK)
| Metric | Target | Threshold |
|--------|--------|-----------|
| CV(H_spec) | < 0.3 | PASS if CV < 0.3, FAIL otherwise |

### Secondary Metrics (Informational)
| Metric | Expected |
|--------|----------|
| mean(H_spec) | Positive value in tokens |
| std(H_spec) | < 0.3 * mean(H_spec) |
| H_spec(1.4B) vs H_spec(370M) | Monotonic scaling |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
mamba-ssm>=1.0.0
transformers>=4.30.0
numpy>=1.20.0
matplotlib>=3.5.0
pyyaml>=6.0
```

### 7.2 External Repositories (Reference)

| Repository | Purpose |
|------------|---------|
| state-spaces/mamba | Official Mamba implementation |
| johnma2006/mamba-minimal | Pure PyTorch reference (no CUDA fusion) |

---

## 8. Constraints

### 8.1 Resource Constraints
- Single GPU execution (CUDA_VISIBLE_DEVICES)
- No training required (inference only)

### 8.2 Time Constraints
- Measurement phase: 30-60 minutes for 1000 sequences
- Total execution: < 2 hours including setup

### 8.3 Scope Constraints
- EXISTENCE hypothesis only - no fine-tuning
- Pretrained model measurement only

---

## 9. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| H_spec unstable (CV >= 0.3) | Low | High (stops pipeline) | None - this is the gate condition |
| A_log access blocked by CUDA fusion | Medium | Medium | Use mamba-minimal or slow path |
| Memory overflow for 1.4B model | Low | Low | Batch sequence processing |

---

## 10. Implementation Notes

### 10.1 A Matrix Access Pattern
```python
# Mamba stores A as log for numerical stability
for layer in model.backbone.layers:
    A_log = layer.mixer.A_log  # (d_inner, d_state) or (d_state,)
    A = torch.exp(A_log)  # Diagonal eigenvalues
    lambda_max = A.abs().max()
```

### 10.2 H_spec Formula
```python
H_spec = -1.0 / torch.log(global_lambda_max)
```

### 10.3 CV Formula
```python
cv = np.std(h_spec_values) / np.mean(h_spec_values)
```

---

## Appendix: Phase 2C Reference

**Source Document:** `02c_experiment_brief.md`
**Hypothesis Statement:** The spectral memory horizon H_spec = -1/log|λ_max| is a measurable, stable property of pretrained Mamba models, with coefficient of variation CV < 0.3 across different input sequences.

---

*Generated by Phase 3 Implementation Planning*
*PRD Version: 1.0*
