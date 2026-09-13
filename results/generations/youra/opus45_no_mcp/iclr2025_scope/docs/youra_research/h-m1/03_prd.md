# Product Requirements Document: H-M1

**Hypothesis:** H-M1 - Architecture Conversion Transforms Loss Landscape Geometry
**Date:** 2026-08-19
**Type:** MECHANISM
**Gate:** MUST_WORK (|sharpness_delta| > 10%, KL_divergence > 0.1)

---

## 1. Executive Summary

This PRD specifies requirements for validating the mechanism hypothesis that Transformer-to-Mamba architecture conversion measurably transforms loss landscape geometry. The experiment measures sharpness and Hessian eigenvalue distributions before and after conversion to establish the causal mechanism underlying task-dependent adaptation patterns observed in H-E1.

**Success Criteria:**
- |sharpness_delta| > 10% (measurable landscape change)
- KL_divergence > 0.1 (detectable eigenvalue distribution shift)

---

## 2. Problem Statement

H-E1 validated that task-dependent adaptation transformation exists (GSM8K delta=-2%, NQ delta=-18%, ρ=0.80). H-M1 investigates the underlying mechanism: does architecture conversion itself alter the loss landscape geometry?

**Key Question:** Does mapping Transformer weights to Mamba structure measurably change loss landscape properties (sharpness, curvature)?

---

## 3. Functional Requirements

### FR-1: Loss Landscape Sharpness Measurement
**Priority:** P0 (Critical)
**Description:** Implement SAM-based sharpness measurement for both Transformer and Mamba architectures
**Acceptance Criteria:**
- Compute base loss L(w) on evaluation batch
- Compute gradient direction for worst-case perturbation
- Apply perturbation: w + ε·grad/||grad|| with ε=0.05
- Compute perturbed loss L(w+e)
- Return sharpness = L(w+e) - L(w)

### FR-2: Hessian Eigenvalue Analysis
**Priority:** P0 (Critical)
**Description:** Compute top-k eigenvalues of loss Hessian using PyHessian
**Acceptance Criteria:**
- Use PyHessian library for Hessian-vector products
- Compute top-50 eigenvalues via power iteration
- Compute trace estimate
- Return eigenvalue distribution for comparison

### FR-3: KL Divergence Computation
**Priority:** P0 (Critical)
**Description:** Compute KL divergence between pre/post conversion eigenvalue distributions
**Acceptance Criteria:**
- Normalize eigenvalues to probability distributions
- Bin eigenvalues into 50 bins
- Compute D_KL(P_transformer || P_mamba)
- Add epsilon=1e-10 for numerical stability

### FR-4: Transformer Baseline Model
**Priority:** P0 (Critical)
**Description:** Load Llama-2-7B as baseline Transformer architecture
**Acceptance Criteria:**
- Load from HuggingFace meta-llama/Llama-2-7b-hf
- Use default attention mechanism
- Support batch processing for Hessian computation

### FR-5: Mamba Converted Model
**Priority:** P0 (Critical)
**Description:** Apply Transformer-to-Mamba conversion and measure landscape
**Acceptance Criteria:**
- Reuse conversion from H-E1 codebase
- Map attention weights to SSM parameters
- Maintain comparable capacity

### FR-6: Visualization Generation
**Priority:** P1 (Important)
**Description:** Generate required figures for analysis
**Acceptance Criteria:**
- Eigenvalue distribution histogram (Transformer vs Mamba overlay)
- Sharpness bar chart (pre vs post conversion)
- Eigenvalue spectrum (log-scale top-50)

---

## 4. Data Specification

### 4.1 Evaluation Datasets

| Dataset | Source | Split | Samples | Purpose |
|---------|--------|-------|---------|---------|
| GSM8K | gsm8k/main | test[:500] | 500 | Sequential reasoning landscape |
| Natural Questions | natural_questions | validation[:500] | 500 | Retrieval-dependent landscape |

**Note:** Subset of 500 samples per dataset for Hessian computation (memory constraints).

### 4.2 Preprocessing

- Tokenizer: Llama-2 tokenizer
- Max length: 512 tokens
- Batch size: 16 (Hessian computation)
- Gradient accumulation: 4 (effective batch 64)

### 4.3 Data Loading

```python
from datasets import load_dataset
gsm8k = load_dataset("gsm8k", "main", split="test[:500]")
nq = load_dataset("natural_questions", split="validation[:500]")
```

**Auto-download:** Both datasets auto-download via HuggingFace - no manual download task needed.

---

## 5. Model Specification

### 5.1 Baseline Model

- **Architecture:** Llama-2-7B (Transformer)
- **Source:** meta-llama/Llama-2-7b-hf
- **Parameters:** ~7B
- **Loading:** HuggingFace AutoModelForCausalLM

### 5.2 Proposed Model

- **Architecture:** Mamba-converted from Llama-2-7B
- **Conversion:** Reuse H-E1 conversion logic
- **Key Parameters:** A_log, D (SSM state evolution)

---

## 6. Evaluation Metrics

### 6.1 Primary Metrics

| Metric | Formula | Threshold |
|--------|---------|-----------|
| Sharpness Delta | \|(S_mamba - S_transformer)\| / S_transformer | > 10% |
| KL Divergence | D_KL(P_trans \|\| P_mamba) | > 0.1 |

### 6.2 Secondary Metrics

| Metric | Purpose |
|--------|---------|
| Spectral Norm Ratio | max_eig_mamba / max_eig_transformer |
| Trace Ratio | trace_mamba / trace_transformer |
| Top-5 Eigenvalue Change | Per-eigenvalue delta |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.30.0
datasets>=2.14.0
pyhessian>=0.1.0
mamba-ssm>=1.0.0
scipy>=1.10.0
numpy>=1.24.0
matplotlib>=3.7.0
tqdm>=4.65.0
```

### 7.2 External Repositories

- PyHessian: github.com/amirgholami/PyHessian
- Mamba: github.com/state-spaces/mamba
- SAM reference: github.com/davda54/sam

### 7.3 Hardware Requirements

- GPU: A100 80GB (Hessian computation memory intensive)
- CPU RAM: 64GB minimum
- Storage: 50GB for model checkpoints

---

## 8. Non-Functional Requirements

### NFR-1: Reproducibility
- Seed: 42 for all random operations
- Deterministic CUDA operations enabled

### NFR-2: Memory Efficiency
- Gradient checkpointing for Hessian computation
- Batch size 16 with accumulation

### NFR-3: Compute Budget
- Target runtime: < 4 hours for full experiment
- Checkpoint intermediate results

---

## 9. Success Criteria

### Gate Logic (MUST_WORK)

```python
def check_gate(results):
    sharpness_delta = abs(results['mamba_sharpness'] - results['transformer_sharpness'])
    sharpness_delta_pct = sharpness_delta / results['transformer_sharpness']
    kl_div = results['kl_divergence']
    
    primary_pass = sharpness_delta_pct > 0.10
    secondary_pass = kl_div > 0.1
    
    return {
        'primary_pass': primary_pass,
        'secondary_pass': secondary_pass,
        'gate_pass': primary_pass,  # MUST_WORK requires primary
        'sharpness_delta_pct': sharpness_delta_pct,
        'kl_divergence': kl_div
    }
```

---

## 10. Assumptions and Constraints

### Assumptions
- A1: Sharpness measurement via SAM perturbation is valid proxy for landscape geometry
- A2: PyHessian power iteration converges within reasonable iterations
- A3: 500-sample subset representative for landscape estimation

### Constraints
- C1: Memory-bound by Hessian-vector product computation
- C2: Requires H-E1 conversion code as dependency

---

*Generated by Phase 3 Implementation Planning*
*Prerequisite: H-E1 (VALIDATED)*
