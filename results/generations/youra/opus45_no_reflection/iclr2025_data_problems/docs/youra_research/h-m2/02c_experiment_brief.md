# Experiment Design: H-M2

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** Different attention structures create different Hessian curvature patterns (block-diagonal vs dense)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing causal mechanism in hypothesis chain.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1: PASS, H-M1: PASS)
**Gate Status:** SHOULD_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (PASSED)

### Gate Condition
Measurable difference in Hessian spectrum between BERT and GPT-2 architectures. GPT-2 should show better Kronecker factorization fit due to causal attention structure creating more block-diagonal Jacobian patterns.

---

## Continuation Context

This hypothesis builds on H-M1 which proved that attention patterns fundamentally differ:
- BERT: bidirectional full attention (upper_sparsity = 0.0118)
- GPT-2: causal masked attention (upper_sparsity = 1.0)

Now we test whether these structural differences propagate to Hessian curvature.

### Previous Hypothesis Results
- H-M1 PASSED: 98.82% sparsity difference confirms distinct attention structures
- 872 samples tested on SST-2 validation set
- Per-layer analysis shows consistent pattern across all 12 layers

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct Hessian curvature results in KB. Primary relevant finding:
- LoRA and PEFT methods implicitly leverage low-rank curvature structure
- Transformer attention patterns affect gradient flow and curvature

### Archon Code Examples

No direct Hessian eigenvalue code in Archon KB. Proceeding with Exa findings.

### Exa GitHub Implementations

**Primary Libraries Found:**

1. **PyHessian** (github.com/amirgholami/PyHessian) - 789 stars
   - Computes top Hessian eigenvalues, trace, and full ESD
   - Paper: arxiv.org/abs/1912.07145
   - MIT license, active development

2. **pytorch-hessian-eigenthings** (github.com/noahgolmant/pytorch-hessian-eigenthings) - 471 stars
   - Efficient Hessian eigendecomposition via Lanczos/power iteration
   - Supports GGN, empirical Fisher, HuggingFace transformers
   - `HessianOperator`, `GGNOperator`, `EmpiricalFisherOperator`
   - Parameter filtering: `param_filter=match_names("blocks.*.attn.*")`

3. **hessian-spectrum** (github.com/zyushun/hessian-spectrum) - 65 stars
   - "Why Transformers Need Adam: A Hessian Perspective" (arxiv.org/abs/2402.16788)
   - **Directly relevant**: Compares Hessian spectrum across transformer architectures
   - Blockwise and full Hessian spectrum estimation via Stochastic Lanczos Quadrature

**Key Papers:**
- Grosse et al. 2023: EK-FAC for influence functions on LLMs up to 52B params
- "Why Transformers Need Adam" (arxiv.org/abs/2402.16788): Hessian spectrum analysis of transformers

### 🎯 Implementation Priority Assessment

**CRITICAL: For Hessian spectrum computation, use established libraries**

| Source | Priority | Reason |
|--------|----------|--------|
| pytorch-hessian-eigenthings | **PRIMARY** | HuggingFace transformer support, GGN/Hessian options |
| PyHessian | Fallback | Simpler API, good for validation |
| Manual HVP + Lanczos | If needed | torch.autograd.functional.hvp + scipy.sparse.linalg.eigsh |

**Recommended Implementation Path:**
- Primary: `hessian-eigenthings` with HessianOperator and GGNOperator
- Fallback: PyHessian for cross-validation
- Justification: Direct HuggingFace support, Lanczos for top-k eigenvalues, proven on transformers

### Code Analysis (Serena MCP)

N/A - No existing codebase to analyze. Using external libraries.

---

## Experiment Specification

### Dataset

| Field | Value |
|-------|-------|
| Name | SST-2 (Stanford Sentiment Treebank) |
| Version | GLUE benchmark |
| Source | HuggingFace datasets |
| Train Split | 67,349 samples (for Hessian computation) |
| Validation Split | 872 samples (for consistency with H-M1) |
| Preprocessing | Standard tokenization via model tokenizer |
| Augmentation | None |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `glue/sst2`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("glue", "sst2")
train_data = dataset["train"]
val_data = dataset["validation"]
```

### Models

#### Baseline Model

| Field | Value |
|-------|-------|
| Name | BERT-base-uncased |
| Parameters | ~110M |
| Layers | 12 |
| Attention | Bidirectional (full n×n) |
| Source | HuggingFace Transformers |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `bert-base-uncased`
- Code:
```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
```

#### Comparison Model

| Field | Value |
|-------|-------|
| Name | GPT-2 |
| Parameters | ~124M |
| Layers | 12 |
| Attention | Causal (lower triangular) |
| Source | HuggingFace Transformers |

**Loading Information**:
```python
from transformers import GPT2ForSequenceClassification, GPT2Tokenizer
model = GPT2ForSequenceClassification.from_pretrained("gpt2", num_labels=2)
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token
model.config.pad_token_id = tokenizer.pad_token_id
```

#### Proposed Analysis

**Architecture:** Compare Hessian spectrum between BERT and GPT-2

**Core Mechanism Implementation:**

```python
# Pseudo-code: Hessian Spectrum Comparison (10-30 lines)
import torch
from hessian_eigenthings import HessianOperator, GGNOperator, lanczos, trace

def compute_hessian_metrics(model, dataloader, loss_fn, device, k=20):
    """Compute Hessian spectrum metrics for a model."""
    # Create Hessian operator
    H = HessianOperator(model, dataloader, loss_fn)
    
    # Top-k eigenvalues via Lanczos
    eig_result = lanczos(H, k=k, seed=42)
    top_eigenvalues = eig_result.eigenvalues
    
    # Trace estimate (sum of all eigenvalues)
    trace_estimate = trace(H, num_matvecs=100, seed=42)
    
    # Compute metrics
    metrics = {
        "top_eigenvalue": float(top_eigenvalues[-1]),
        "eigenvalue_ratio": float(top_eigenvalues[-1] / top_eigenvalues[0]),
        "trace": float(trace_estimate),
        "top_k_eigenvalues": top_eigenvalues.tolist(),
        "spectral_norm": float(top_eigenvalues[-1]),
    }
    return metrics

def compute_kronecker_fit(model, dataloader, layer_name="attention"):
    """Estimate how well Kronecker factorization fits the curvature."""
    # For each attention layer, compute:
    # 1. Full layer Hessian block (or GGN approximation)
    # 2. Kronecker-factored approximation
    # 3. Frobenius norm of difference
    
    # Using GGN (block-diagonal by construction)
    G = GGNOperator(model, dataloader, loss_fn)
    
    # Compute per-layer metrics
    # Kronecker fit quality = || G_layer - A ⊗ S ||_F / || G_layer ||_F
    # Lower = better Kronecker factorization fit
    pass  # Implementation in Phase 4

def main():
    # Load models
    bert_model = load_bert()
    gpt2_model = load_gpt2()
    
    # Compute Hessian metrics for both
    bert_metrics = compute_hessian_metrics(bert_model, dataloader, loss_fn, device)
    gpt2_metrics = compute_hessian_metrics(gpt2_model, dataloader, loss_fn, device)
    
    # Compare
    results = {
        "bert": bert_metrics,
        "gpt2": gpt2_metrics,
        "eigenvalue_ratio_diff": gpt2_metrics["eigenvalue_ratio"] - bert_metrics["eigenvalue_ratio"],
        "trace_diff": gpt2_metrics["trace"] - bert_metrics["trace"],
    }
    return results
```

### Training Protocol

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Fine-tuning | Pre-trained → SST-2 fine-tuned | Match H-M1 setup |
| Epochs | 3 | Standard for GLUE tasks |
| Batch Size | 32 | Memory-efficient for Hessian computation |
| Optimizer | AdamW | Standard for transformers |
| Learning Rate | 2e-5 | Standard for BERT/GPT-2 fine-tuning |
| Hessian Batch | 256-512 samples | Sufficient for Lanczos convergence |
| Lanczos Steps | 40-60 | Balance accuracy vs compute |
| Top-k Eigenvalues | 20 | Capture dominant curvature |

### Evaluation

| Metric | Description | Success Criterion |
|--------|-------------|-------------------|
| Top Eigenvalue | Largest Hessian eigenvalue | Measurable difference |
| Eigenvalue Ratio | λ_max / λ_min (condition number proxy) | GPT-2 lower ratio expected |
| Trace | Sum of eigenvalues (total curvature) | Measurable difference |
| Spectral Density | Distribution of eigenvalues | Different shapes |
| Kronecker Fit Error | ||G - A⊗S||_F / ||G||_F | GPT-2 lower error expected |

**Success Criteria (PoC: Direction-based):**
- Primary: Measurable difference (>10%) in at least one spectral metric
- Secondary: GPT-2 shows lower Kronecker fit error than BERT

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Curvature analysis (not classification)
- Library: hessian-eigenthings, numpy, scipy
- Code:
```python
# pip install hessian-eigenthings
from hessian_eigenthings import HessianOperator, lanczos, trace, spectral_density
import numpy as np
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing BERT vs GPT-2 spectral metrics

#### Additional Figures (LLM Autonomous)

1. **Eigenvalue Spectrum Plot**: Top-20 eigenvalues for both models (log scale)
2. **Spectral Density Comparison**: Overlaid ESD curves for BERT vs GPT-2
3. **Condition Number by Layer**: Per-layer eigenvalue ratio comparison
4. **Kronecker Fit Quality**: Per-layer fit error (if computed)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## Ablation Studies

| Variant | Purpose | Expected Outcome |
|---------|---------|------------------|
| Different seeds | Verify stability | Consistent pattern |
| Different batch sizes | Check Hessian estimate quality | Convergence at ~256 |
| Attention-only params | Isolate attention contribution | Stronger effect |
| Full model vs MLP-only | Localize curvature source | Attention drives difference |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Measurable Hessian spectrum difference between architectures (any direction)
3. At least one metric shows >10% relative difference

**Gate Pass (SHOULD_WORK):**
- If any spectral metric shows measurable architecture-dependent difference
- If GPT-2 shows better Kronecker fit (lower error)
- Document finding even if unexpected direction

---

## Appendix: Reference Implementations

### Primary: pytorch-hessian-eigenthings

```python
# Installation
pip install hessian-eigenthings

# Usage with HuggingFace models
from hessian_eigenthings import HessianOperator, lanczos, spectral_density
from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")
data = [(batch_x, batch_y) for batch_x, batch_y in dataloader]

H = HessianOperator(model, data, supervised_loss(nn.CrossEntropyLoss()))
eig = lanczos(H, k=20, seed=0)
density = spectral_density(H, num_runs=8, lanczos_steps=40, seed=0)
```

### Fallback: PyHessian

```python
# Installation
pip install pyhessian

# Usage
from pyhessian import hessian
hessian_comp = hessian(model, criterion, data=(inputs, targets), cuda=True)
top_eigenvalues, top_eigenvectors = hessian_comp.eigenvalues(top_n=20)
trace = hessian_comp.trace()
density_eigen, density_weight = hessian_comp.density()
```

### Manual HVP (if libraries fail)

```python
# Using torch.autograd.functional.hvp
from scipy.sparse.linalg import LinearOperator, eigsh

def hessian_vector_product(model, loss_fn, data, vector):
    model.zero_grad()
    loss = loss_fn(model(data[0]), data[1])
    grads = torch.autograd.grad(loss, model.parameters(), create_graph=True)
    flat_grad = torch.cat([g.view(-1) for g in grads])
    hvp = torch.autograd.grad(flat_grad @ vector, model.parameters())
    return torch.cat([h.view(-1) for h in hvp])

# Wrap as LinearOperator for scipy.eigsh
linear_op = LinearOperator((n_params, n_params), matvec=lambda v: hvp(v))
eigenvalues, eigenvectors = eigsh(linear_op, k=20, which='LM')
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18

### Workflow History for This Hypothesis
- H-M2 set to IN_PROGRESS for Phase 2C experiment design
- Prerequisites satisfied: H-E1 PASS, H-M1 PASS
- Building on H-M1 result: 98.82% sparsity difference in attention patterns

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Code Context)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
