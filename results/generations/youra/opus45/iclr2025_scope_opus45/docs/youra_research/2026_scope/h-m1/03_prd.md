# Product Requirements Document: H-M1

**Hypothesis:** SSM State Dynamics Governed by Discretized Transition Matrix
**Type:** MECHANISM
**Date:** 2026-03-27
**Author:** Anonymous
**Status:** Draft

---

## 1. Executive Summary

This PRD defines the implementation requirements for validating hypothesis H-M1: empirically demonstrating that SSM state dynamics are governed by the discretized transition matrix Ā = exp(ΔA) where eigenvalues determine information decay rates.

**Key Deliverable:** An empirical validation framework that tests whether the eigenvalue-derived spectral memory horizon (H_spec) predicts actual perplexity degradation on real language modeling tasks (WikiText-103).

**Success Criterion:** Perplexity degradation ratio > 1.1 when context is truncated below H_spec (256 tokens).

**Non-Tautological Design:** This tests the PREDICTIVE POWER of eigenvalue-derived H_spec against EMPIRICAL behavior on natural text - not a mathematical identity.

---

## 2. Problem Statement

### 2.1 Background
H-E1 established that H_spec = 256.18 tokens is a stable, measurable property of Mamba-1.4B (CV ≈ 0). H-M1 validates that this mathematically-derived quantity has actual predictive power for model behavior on real text.

### 2.2 Research Gap
While H_spec can be computed from eigenvalues, no prior work has validated that this theoretical quantity predicts empirical memory behavior. The hypothesis "eigenvalues determine information decay" is falsifiable - attention mechanisms or other factors could dominate.

### 2.3 Gate Condition
**MUST_WORK Gate:** If perplexity is context-independent OR degrades at thresholds unrelated to H_spec, the eigenvalue-based memory theory is invalidated and MHSH/EUH framework collapses.

---

## 3. Functional Requirements

### FR-1: Model Loading
- **Description:** Load pretrained Mamba-1.4B model
- **Source:** state-spaces/mamba-1.4b (HuggingFace)
- **Acceptance:** Model loads without error, forward pass functional

### FR-2: Dataset Loading
- **Description:** Load WikiText-103 validation set for perplexity evaluation
- **Source:** HuggingFace Datasets (wikitext/wikitext-103-raw-v1)
- **Statistics:**
  - Validation set: ~218K tokens
  - Evaluation sequences: 1000 non-overlapping chunks
  - Sequence length: 1024 tokens (max)
- **Acceptance:** 1000 evaluation sequences prepared

### FR-3: Eigenvalue Extraction and H_spec Computation
- **Description:** Extract A_log parameters and compute theoretical H_spec
- **Method:** Reuse H-E1 validated methodology
  - λ_discrete = exp(-exp(A_log))
  - H_spec = -1/log(λ_max)
- **Expected Result:** H_spec ≈ 256.18 tokens (from H-E1)
- **Acceptance:** H_spec computed, consistent with H-E1 results

### FR-4: Context-Length Perplexity Measurement
- **Description:** Measure perplexity at varying context lengths around H_spec
- **Context Lengths to Test:**
  - 0.1 × H_spec ≈ 26 tokens
  - 0.25 × H_spec ≈ 64 tokens
  - 0.5 × H_spec ≈ 128 tokens
  - 1.0 × H_spec ≈ 256 tokens
  - 2.0 × H_spec ≈ 512 tokens
  - 4.0 × H_spec ≈ 1024 tokens
- **Method:** Truncate context and measure cross-entropy loss
- **Acceptance:** Perplexity values recorded for each context length

### FR-5: Perplexity Degradation Ratio Computation
- **Description:** Compute degradation ratio comparing perplexity below vs at/above H_spec
- **Formula:** ratio = mean(PPL when ctx < H_spec) / mean(PPL when ctx >= H_spec)
- **Target:** ratio > 1.1 (10% worse perplexity with truncated context)
- **Acceptance:** Degradation ratio computed and compared to threshold

### FR-6: Baseline Perplexity Validation
- **Description:** Verify full-context perplexity matches published benchmark
- **Expected:** ~16.3 PPL (from original Mamba paper Table 1)
- **Tolerance:** ±20% (13.0 - 19.6 PPL)
- **Acceptance:** Full-context perplexity within expected range

### FR-7: Visualization
- **Description:** Generate required figures
- **Required Figures:**
  1. Perplexity vs Context Length Curve (with vertical line at H_spec)
  2. Gate Metrics Comparison (degradation ratio vs threshold)
- **Optional Figures:**
  3. Perplexity Degradation Heatmap
  4. Per-Layer Eigenvalue Distribution
  5. Decay Rate Profile per Layer
- **Acceptance:** Figures saved to `figures/` subfolder

---

## 4. Data Specification

### 4.1 Input Data

| Dataset | Type | Source | Download |
|---------|------|--------|----------|
| WikiText-103 | standard | HuggingFace | `load_dataset("wikitext", "wikitext-103-raw-v1")` |

**Loading Code:**
```python
from datasets import load_dataset
from transformers import AutoTokenizer

dataset = load_dataset("wikitext", "wikitext-103-raw-v1")
tokenizer = AutoTokenizer.from_pretrained("state-spaces/mamba-1.4b-hf")

# Tokenize and chunk validation set
tokenized = dataset["validation"].map(
    lambda x: tokenizer(x["text"], truncation=False),
    batched=True, remove_columns=["text"]
)
```

### 4.2 Model Checkpoints

| Model | Source | Method |
|-------|--------|--------|
| Mamba-1.4B | state-spaces/mamba-1.4b | HuggingFace auto-download |
| Tokenizer | state-spaces/mamba-1.4b-hf | HuggingFace auto-download |

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Complete evaluation in < 1 hour on single GPU
- Memory usage < 16GB (Mamba-1.4B inference)

### NFR-2: Reproducibility
- Fixed random seed (42) for sequence selection
- Deterministic evaluation (no sampling)

### NFR-3: Statistical Validity
- Minimum 1000 evaluation sequences (not trivially small samples)
- Use full validation set or statistically meaningful subset

### NFR-4: Numerical Precision
- Perplexity computation in float32
- Eigenvalue computation in float32/64

---

## 6. Success Criteria

### Primary Gate (MUST_WORK)
| Metric | Target | Threshold |
|--------|--------|-----------|
| Perplexity Degradation Ratio | > 1.1 | PASS if ratio > 1.1, FAIL otherwise |

### Secondary Metrics (Informational)
| Metric | Expected |
|--------|----------|
| Full-context Perplexity | ~16.3 PPL (±20%) |
| H_spec Prediction | Inflection near 256 tokens |
| Context Independence | Perplexity should NOT be flat |

### Falsification Conditions (Hypothesis FAILS if):
- Perplexity is constant regardless of context length
- Perplexity degrades at threshold far from H_spec (>2× difference)
- Degradation ratio < 1.05 (no meaningful context dependence)

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
mamba-ssm>=1.0.0
transformers>=4.30.0
datasets>=2.0.0
numpy>=1.20.0
matplotlib>=3.5.0
pyyaml>=6.0
```

### 7.2 Previous Hypothesis Results
- **H-E1:** VALIDATED (MUST_WORK PASS)
  - H_spec = 256.18 tokens
  - CV(H_spec) = 2.22e-16
  - MambaProbe class for eigenvalue extraction

### 7.3 External Repositories (Reference)

| Repository | Purpose |
|------------|---------|
| state-spaces/mamba | Official Mamba implementation |
| johnma2006/mamba-minimal | Pure PyTorch reference |

---

## 8. Constraints

### 8.1 Resource Constraints
- Single GPU execution (CUDA_VISIBLE_DEVICES)
- No training required (inference only)

### 8.2 Time Constraints
- Perplexity evaluation: 30-45 minutes for 1000 sequences × 6 context lengths
- Total execution: < 1 hour including setup

### 8.3 Scope Constraints
- MECHANISM hypothesis - validates theoretical prediction
- Pretrained model evaluation only (no fine-tuning)
- Builds on H-E1 validated methodology

---

## 9. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Perplexity context-independent | Low | High (invalidates MHSH) | This is the gate condition - no mitigation |
| Full-context PPL far from benchmark | Medium | Medium | Check model loading, verify tokenizer |
| Memory overflow for long sequences | Low | Low | Batch processing, gradient checkpointing |
| Eigenvalue computation mismatch with H-E1 | Low | Low | Reuse H-E1 validated code |

---

## 10. Implementation Notes

### 10.1 Perplexity Computation
```python
import torch.nn.functional as F

def compute_perplexity(model, input_ids):
    with torch.no_grad():
        outputs = model(input_ids)
        logits = outputs.logits if hasattr(outputs, 'logits') else outputs[0]
        shift_logits = logits[:, :-1, :].contiguous()
        shift_labels = input_ids[:, 1:].contiguous()
        loss = F.cross_entropy(
            shift_logits.view(-1, shift_logits.size(-1)),
            shift_labels.view(-1),
            reduction='mean'
        )
        return torch.exp(loss).item()
```

### 10.2 Context Truncation Evaluation
```python
def evaluate_at_context_length(model, full_sequences, context_length):
    truncated = full_sequences[:, -context_length:]
    return compute_perplexity(model, truncated)
```

### 10.3 Degradation Ratio Computation
```python
def compute_degradation_ratio(ppl_curve, h_spec):
    below = [ppl for ctx, ppl in ppl_curve.items() if ctx < h_spec]
    above = [ppl for ctx, ppl in ppl_curve.items() if ctx >= h_spec]
    if below and above:
        return (sum(below) / len(below)) / (sum(above) / len(above))
    return 1.0
```

### 10.4 H_spec Reuse from H-E1
```python
# Reuse validated H_spec from H-E1
H_SPEC_MAMBA_1_4B = 256.18  # tokens (validated CV ≈ 0)

# Or recompute for verification
def compute_h_spec(model):
    global_max_lambda = 0.0
    for name, param in model.named_parameters():
        if 'A_log' in name:
            lambda_discrete = torch.exp(-torch.exp(param.float()))
            max_lambda = lambda_discrete.max().item()
            global_max_lambda = max(global_max_lambda, max_lambda)
    return -1.0 / math.log(global_max_lambda)
```

---

## Appendix: Phase 2C Reference

**Source Document:** `02c_experiment_brief.md`
**Hypothesis Statement:** SSM state dynamics are governed by discretized transition matrix Ā = exp(ΔA) where eigenvalues determine information decay rates.

**Non-Tautological Validation:**
- H_spec is computed from static weights (eigenvalues)
- Perplexity is measured from model behavior on real text
- The hypothesis predicts a relationship that can empirically fail

---

*Generated by Phase 3 Implementation Planning*
*PRD Version: 1.0*
