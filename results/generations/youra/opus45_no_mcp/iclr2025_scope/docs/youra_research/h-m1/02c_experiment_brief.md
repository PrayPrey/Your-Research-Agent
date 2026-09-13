# Experiment Design: H-M1

**Date:** 2026-08-19
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** Under SSM-attention duality conversion, if Transformer weights are mapped to Mamba structure, then loss landscape geometry measurably changes (sharpness, curvature) because structural transformation alters optimization surface topology.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests causal mechanism: conversion transforms landscape geometry.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 PASSED)
**Gate Status:** MUST_WORK - |delta sharpness| > 10%, KL divergence > 0.1

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED - task-dependent pattern exists)

### Gate Condition
- **Primary:** Measurable change in sharpness (|delta| > 10%)
- **Secondary:** Eigenvalue distribution shift detectable (KL divergence > 0.1)

---

## Continuation Context

H-E1 validated task-dependent adaptation transformation exists:
- GSM8K (sequential): delta = -2% (within threshold)
- NQ (retrieval): delta = -18% (below threshold)
- Spearman ρ = 0.80 correlation between retrieval density and delta

H-M1 investigates the causal mechanism: does architecture conversion itself transform loss landscape geometry?

### Previous Hypothesis Results (H-E1)
| Benchmark | Transformer+LoRA | Mamba+LoRA | Delta |
|-----------|------------------|------------|-------|
| GSM8K | 0.47 | 0.45 | -0.02 |
| NQ | 0.28 | 0.10 | -0.18 |

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable - using web search research*

Key findings from literature:
1. SAM (Sharpness-Aware Minimization) established method for measuring landscape sharpness
2. Loss-Equated SAM (LE-SAM, 2026) improves sharpness-aware optimization
3. Perturbation radius epsilon=0.05 standard for SAM measurement

### Archon Code Examples

*MCP unavailable - using web search research*

Reference implementations:
- davda54/sam (GitHub): Standard SAM PyTorch implementation
- Two forward-backward passes for sharpness-aware gradient

### Exa GitHub Implementations

Key repositories identified:
1. **state-spaces/mamba** - Official Mamba implementation
2. **amirgholami/PyHessian** - Hessian eigenvalue computation
3. **noahgolmant/pytorch-hessian-eigenthings** - Efficient Hessian eigendecomposition
4. **davda54/sam** - SAM optimizer implementation

### 🎯 Implementation Priority Assessment

**CRITICAL: Use established libraries for landscape analysis**

**Recommended Implementation Path:**
- Primary: PyHessian for eigenvalue analysis + custom SAM perturbation measurement
- Fallback: pytorch-hessian-eigenthings for lighter computation
- Justification: PyHessian widely used, supports distributed computation, well-documented

### Code Analysis (Serena MCP)

*Serena MCP unavailable - using static analysis*

From H-E1 codebase:
- MambaWithLoRA module exists with A_log, D parameters
- SSM state evolution verified functional
- Can reuse model loading infrastructure

---

## Experiment Specification

### Dataset

**Name:** GSM8K + Natural Questions (subset for landscape analysis)
**Type:** standard
**Source:** HuggingFace datasets

| Split | GSM8K | Natural Questions |
|-------|-------|-------------------|
| Landscape Eval | 500 samples | 500 samples |

**Preprocessing:**
- Tokenize with Llama-2 tokenizer
- Truncate/pad to max_length=512
- Batch size 16 for Hessian computation

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: gsm8k (main split), google-research-datasets/natural_questions
- Code:
```python
from datasets import load_dataset
gsm8k = load_dataset("gsm8k", "main", split="test[:500]")
nq = load_dataset("natural_questions", split="validation[:500]")
```

### Models

#### Baseline Model

**Architecture:** Llama-2-7B (Transformer)
**Source:** meta-llama/Llama-2-7b-hf
**Purpose:** Pre-conversion landscape baseline

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: meta-llama/Llama-2-7b-hf
- Code:
```python
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
```

#### Proposed Model

**Architecture:** Mamba-converted from Llama-2-7B

**Core Mechanism Implementation:**

```python
# Landscape Sharpness Measurement via SAM Perturbation
def measure_sharpness_sam(model, dataloader, epsilon=0.05):
    """
    Compute SAM-based sharpness: max_||e||<=eps L(w+e) - L(w)
    Uses gradient direction for worst-case perturbation
    """
    model.eval()
    original_params = {n: p.clone() for n, p in model.named_parameters()}
    
    # Compute base loss
    base_loss = compute_loss(model, dataloader)
    
    # Compute gradient for perturbation direction
    model.zero_grad()
    loss = compute_loss(model, dataloader)
    loss.backward()
    
    # Apply perturbation: w + epsilon * grad/||grad||
    grad_norm = compute_grad_norm(model)
    for name, param in model.named_parameters():
        if param.grad is not None:
            param.data.add_(epsilon * param.grad / grad_norm)
    
    # Compute perturbed loss
    perturbed_loss = compute_loss(model, dataloader)
    sharpness = perturbed_loss - base_loss
    
    # Restore original parameters
    for name, param in model.named_parameters():
        param.data.copy_(original_params[name])
    
    return sharpness.item()

# Hessian Eigenvalue Analysis via PyHessian
def compute_hessian_eigenvalues(model, dataloader, top_k=50):
    """
    Compute top-k eigenvalues of loss Hessian
    Uses power iteration from PyHessian
    """
    from pyhessian import hessian
    
    criterion = nn.CrossEntropyLoss()
    hessian_comp = hessian(model, criterion, dataloader=dataloader, cuda=True)
    
    top_eigenvalues, _ = hessian_comp.eigenvalues(top_n=top_k)
    trace = hessian_comp.trace()
    
    return {
        'eigenvalues': top_eigenvalues,
        'trace': trace,
        'spectral_norm': max(top_eigenvalues)
    }

# KL Divergence for Distribution Comparison
def compute_kl_divergence(eig_pre, eig_post, num_bins=50):
    """
    KL divergence between pre/post conversion eigenvalue distributions
    """
    import numpy as np
    from scipy.stats import entropy
    
    # Normalize and bin eigenvalues
    all_eig = np.concatenate([eig_pre, eig_post])
    bins = np.linspace(min(all_eig), max(all_eig), num_bins+1)
    
    hist_pre, _ = np.histogram(eig_pre, bins=bins, density=True)
    hist_post, _ = np.histogram(eig_post, bins=bins, density=True)
    
    # Add small epsilon for numerical stability
    eps = 1e-10
    hist_pre = hist_pre + eps
    hist_post = hist_post + eps
    
    return entropy(hist_pre, hist_post)
```

### Training Protocol

**Note:** H-M1 is a measurement hypothesis, not a training hypothesis. Protocol focuses on landscape measurement at specific checkpoints.

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Measurement Points | Pre-conversion, Post-conversion | Compare same logical position |
| SAM epsilon | 0.05 | Standard from SAM literature |
| Hessian top-k | 50 | Captures dominant curvature |
| Batch size (Hessian) | 16 | Memory constraint for Hessian-vector products |
| Gradient accumulation | 4 | Effective batch 64 for stability |
| Seed | 42 | Reproducibility |

### Evaluation

**Primary Metrics:**
1. **Sharpness Delta:** |(sharpness_mamba - sharpness_transformer) / sharpness_transformer|
2. **KL Divergence:** D_KL(P_transformer || P_mamba) for eigenvalue distributions
3. **Spectral Norm Ratio:** max_eig_mamba / max_eig_transformer

**Success Criteria (PoC: Direction-based):**
- Primary: |sharpness_delta| > 10%
- Secondary: KL_divergence > 0.1

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: landscape_analysis
- Library: PyHessian, scipy, numpy
- Code:
```python
from pyhessian import hessian
from scipy.stats import entropy, spearmanr
import numpy as np
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Eigenvalue Distribution Comparison**: Histogram overlay of Transformer vs Mamba eigenvalues

#### Additional Figures (LLM Autonomous)
- **Sharpness Bar Chart**: Pre vs post conversion sharpness by task
- **Eigenvalue Spectrum**: Log-scale plot of top-50 eigenvalues
- **Curvature Heatmap**: Top eigenvector directions visualization

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. |sharpness_delta| > 10% (measurable landscape change)
3. KL_divergence > 0.1 (detectable distribution shift)

**Gate Logic:**
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

## Appendix: Reference Implementations

### SAM Implementation
- **Repository:** [davda54/sam](https://github.com/davda54/sam)
- **Key Files:** sam.py (SAM optimizer wrapper)
- **Usage:** Wrap base optimizer, two forward-backward passes

### PyHessian
- **Repository:** [amirgholami/PyHessian](https://github.com/amirgholami/PyHessian)
- **Key Files:** pyhessian/hessian.py
- **Methods:** eigenvalues(), trace(), density()

### Mamba Official
- **Repository:** [state-spaces/mamba](https://github.com/state-spaces/mamba)
- **Key Files:** mamba_ssm/models/mixer_seq_simple.py

### Related Literature
- [Flat-LoRA: Low-Rank Adaptation over a Flat Loss Landscape](https://arxiv.org/pdf/2409.14396)
- [Bi-LoRA: Efficient Sharpness-Aware Minimization](https://arxiv.org/html/2508.19564v2)
- [Fix the Loss, Not the Radius: LE-SAM](https://arxiv.org/html/2605.10183v1)
- [PyHessian: Neural Networks Through the Lens of the Hessian](https://rise.cs.berkeley.edu/projects/pyhessian/)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- H-E1 VALIDATED: Task-dependent pattern confirmed
- H-M1 IN_PROGRESS: Experiment design complete

---

*MCP Tools Used: WebSearch (fallback for Archon/Exa)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
