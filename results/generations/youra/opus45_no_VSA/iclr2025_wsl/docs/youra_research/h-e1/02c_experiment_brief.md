# Experiment Design: H-E1

**Date:** 2026-08-10
**Author:** Anonymous
**Hypothesis Statement:** CV_PR can be reliably extracted from 100+ timm models using randomized SVD with 20 seeds
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS → COMPLETED
**Prerequisites Satisfied:** None (first hypothesis)
**Gate Status:** MUST_WORK (not yet satisfied)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
Extraction completes for all models with consistent methodology. Must demonstrate feasibility of CV_PR computation across 100+ timm pretrained models.

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous hypothesis results to inherit.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "randomized SVD neural network spectral analysis"**
- Limited direct matches in KB
- Related: PEFT/LoRA (low-rank adaptation) concepts
- Insight: Low-rank approximation is well-studied for model compression

**Query 2: "participation ratio weight matrix analysis"**
- Related: DeepSpeed, HuggingFace PEFT
- Insight: Weight matrix analysis common in pruning/compression literature

**Query 3: "timm pretrained model extraction"**
- huggingface/peft, apple/ml-stable-diffusion, isl-org/MiDaS
- Insight: timm models accessible via `timm.create_model(name, pretrained=True)`

### Archon Code Examples

Limited direct code examples for participation ratio + SVD combination. Primary implementation guidance from Exa search results.

### Exa GitHub Implementations

**Repository 1**: aliutkus/torchrsvd (⭐ 6)
- **URL**: https://github.com/aliutkus/torchrsvd
- **Relevance**: Fast randomized SVD for PyTorch - core algorithm needed
- **Key Code**:
  ```python
  from torchrsvd import rsvd
  U, S, V = rsvd(input, rank=10)  # truncated SVD
  # 60x faster than torch.svd for large matrices
  ```
- **Paper**: Halko et al. "Finding structure with randomness" (arXiv:0909.4061)
- **Used For**: Randomized SVD implementation

**Repository 2**: badooki/dimensionality (⭐ 8)
- **URL**: https://github.com/badooki/dimensionality
- **Relevance**: **EXACT participation ratio implementation with bias correction** (ICLR 2026)
- **Key Formula**:
  ```python
  # Participation Ratio: γ = (Σλ_i)² / Σλ_i²
  # Naive estimator is biased; package provides debiased estimators
  from dimensionality import gamma_naive, gamma_row, gamma_col
  ```
- **Paper**: Chun et al. "Estimating Dimensionality of Neural Representations from Finite Samples" (ICLR 2026)
- **Used For**: Participation ratio computation, bias correction awareness

**Repository 3**: danmlr/svr (⭐ 7)
- **URL**: https://github.com/danmlr/svr
- **Relevance**: Singular Value Representation for neural network analysis
- **Key Code**:
  ```python
  from svr import SVR
  model = torch.hub.load('pytorch/vision:v0.10.0', 'vgg16', pretrained=True)
  weights = [w.detach() for w in model.parameters()]
  svr_model = SVR(weights)
  svr_model.plot()
  ```
- **Used For**: Pattern for extracting and analyzing weight matrices

**Repository 4**: huggingface/pytorch-image-models (⭐ 37058)
- **URL**: https://github.com/huggingface/pytorch-image-models
- **Relevance**: timm library - source of 100+ pretrained models
- **Key Code**:
  ```python
  import timm
  model = timm.create_model('resnet50', pretrained=True)
  # Access layers: model.named_modules(), model.named_parameters()
  ```
- **Model Count**: 1000+ architectures, many with pretrained weights
- **Used For**: Model loading, architecture enumeration

### 🎯 Implementation Priority Assessment

**CRITICAL: For this hypothesis, we implement from first principles using established algorithms**

**Recommended Implementation Path:**
- Primary: Custom implementation using torch.linalg.svd with random projection (Halko algorithm)
- Fallback: torchrsvd library if custom implementation encounters issues
- Justification: Need fine-grained control over seed handling for CV computation

### Code Analysis (Serena MCP)

Serena analysis not required - code patterns from Exa search are sufficiently clear:
1. timm model loading well-documented
2. SVD computation straightforward with torch.linalg
3. Participation ratio formula is simple: (Σλ)² / Σλ²

---

## Experiment Specification

### Dataset

**Dataset**: timm Model Zoo (pretrained ImageNet-1K models)
**Type**: programmatic-api (models loaded via timm API)

**Model Selection Criteria**:
- Pretrained on ImageNet-1K
- Has reported top-1 accuracy in timm metadata
- Architecture families: ResNet, ViT, EfficientNet, ConvNeXt, DenseNet, etc.
- Target: 100+ models minimum

**Loading Information** (for Phase 4 download):
- Method: timm API
- Identifier: `timm.list_models(pretrained=True)`
- Code:
  ```python
  import timm
  model_names = timm.list_models(pretrained=True)
  for name in model_names:
      model = timm.create_model(name, pretrained=True)
  ```

### Models

#### Baseline Model

**Architecture**: N/A (this is an extraction/analysis task, not a training task)
**Purpose**: Extract CV_PR metrics from existing pretrained models
**No baseline comparison** - this is EXISTENCE hypothesis testing feasibility

**Loading Information** (for Phase 4 download):
- Method: timm
- Identifier: `timm.create_model(model_name, pretrained=True)`
- Code:
  ```python
  import timm
  model = timm.create_model(model_name, pretrained=True)
  model.eval()
  ```

#### Proposed Model

**Architecture**: CV_PR Extraction Pipeline (not a neural network model)

**Core Mechanism Implementation:**

```python
# Core Mechanism: CV_PR Extraction via Randomized SVD
# Based on: Halko et al. (2011) + Chun et al. (ICLR 2026)

import torch
import numpy as np
from typing import Dict, List

def randomized_svd(A: torch.Tensor, rank: int, seed: int) -> torch.Tensor:
    """
    Randomized SVD using random projection (Halko algorithm).
    Returns singular values only for efficiency.
    """
    torch.manual_seed(seed)
    m, n = A.shape
    # Random projection
    Omega = torch.randn(n, rank + 10, device=A.device)
    Y = A @ Omega
    Q, _ = torch.linalg.qr(Y)
    B = Q.T @ A
    _, S, _ = torch.linalg.svd(B, full_matrices=False)
    return S[:rank]

def participation_ratio(eigenvalues: torch.Tensor) -> float:
    """PR = (Σλ)² / Σλ²"""
    sum_lambda = eigenvalues.sum()
    sum_lambda_sq = (eigenvalues ** 2).sum()
    return (sum_lambda ** 2 / sum_lambda_sq).item()

def compute_cv_pr(weight: torch.Tensor, n_seeds: int = 20, rank: int = 50) -> Dict:
    """Compute CV of participation ratio across multiple random seeds."""
    pr_values = []
    for seed in range(n_seeds):
        S = randomized_svd(weight.flatten(1) if weight.dim() > 2 else weight, 
                          rank=min(rank, min(weight.shape[-2:])), seed=seed)
        pr = participation_ratio(S ** 2)  # eigenvalues = S²
        pr_values.append(pr)
    
    pr_array = np.array(pr_values)
    return {
        'mean_pr': pr_array.mean(),
        'std_pr': pr_array.std(),
        'cv_pr': pr_array.std() / pr_array.mean() if pr_array.mean() > 0 else 0
    }

# Integration: Apply to each conv2d/linear layer in model
```

### Training Protocol

**⚠️ EXISTENCE (PoC): No training required - this is an extraction/analysis task**

- **Optimizer**: N/A
- **Learning Rate**: N/A
- **Batch Size**: N/A
- **Epochs**: N/A
- **Loss**: N/A

**Extraction Protocol**:
- Models: 100+ timm pretrained models
- Layers: conv2d, linear (weight matrices only)
- Seeds: 20 per layer (fixed across all models)
- Aggregation: Mean CV_PR across layers per model

### Evaluation

**Primary Metrics**:
- Extraction completion rate (% of models successfully processed)
- Mean CV_PR per model
- CV_PR variance across seeds (should be low for reliability)
- Processing time per model

**Success Criteria**:
- All 100+ models processed without error
- CV_PR values are finite and reasonable (0 < CV_PR < 10)
- Standard deviation of CV_PR across seeds is < mean (CV of CV < 100%)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: metric extraction (not classification)
- Library: numpy, scipy.stats
- Code:
  ```python
  import numpy as np
  from scipy.stats import pearsonr
  # For H-E2: pearsonr(cv_pr_values, accuracy_values)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Extraction Success Rate**: Bar chart showing models processed vs total
- **CV_PR Distribution**: Histogram of CV_PR values across all models

#### Additional Figures (LLM Autonomous)
- CV_PR by architecture family (box plot)
- CV_PR vs model size (scatter)
- Processing time distribution

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: True - randomized SVD + participation ratio are well-defined
- `mechanism_isolatable`: True - each component can be tested independently
- `baseline_measurable`: True - can verify against full SVD results

### Architecture Compatibility
- timm models expose `named_parameters()` and `named_modules()`
- Weight tensors accessible via `param.data`
- 2D weight matrices (linear) or 4D (conv2d, reshape to 2D)

### Activation Indicators
- `mechanism_log_message`: "CV_PR computed for layer {layer_name}: {cv_pr:.4f}"
- `tensor_shape_change`: Input (out, in) → SVD S (min(out, in),) → scalar CV_PR
- `metric_delta_expected`: CV_PR values between 0.01 and 5.0 typical

### Verification Code
```python
# Verify mechanism works on single layer
def verify_cv_pr_mechanism():
    test_weight = torch.randn(512, 512)
    result = compute_cv_pr(test_weight, n_seeds=5)
    assert 0 < result['cv_pr'] < 10, f"CV_PR out of range: {result['cv_pr']}"
    assert result['std_pr'] < result['mean_pr'], "High variance in PR estimates"
    print(f"✓ Mechanism verified: CV_PR = {result['cv_pr']:.4f}")
    return True
```

### Success Criteria
- `hypothesis_support_metric`: extraction_completion_rate
- `hypothesis_support_threshold`: >= 0.95 (95% of models processed)

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on 100+ models
2. CV_PR values are extracted for all models
3. Values are consistent (low within-model variance across seeds)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: HuggingFace PEFT Documentation
- **Type**: Knowledge base
- **Query Used**: "timm pretrained model extraction"
- **Key Insight**: Low-rank methods well-established in DL community
- **Used For**: Context on weight matrix analysis approaches

### B. GitHub Implementations (Exa)

**Repository 1**: aliutkus/torchrsvd (⭐ 6)
- **URL**: https://github.com/aliutkus/torchrsvd
- **Query Used**: "randomized SVD pytorch weight matrix"
- **Relevance**: Core algorithm reference
- **Used For**: Randomized SVD implementation pattern

**Repository 2**: badooki/dimensionality (⭐ 8)
- **URL**: https://github.com/badooki/dimensionality
- **Query Used**: "participation ratio eigenvalue spectral"
- **Relevance**: Exact PR implementation with bias correction (ICLR 2026)
- **Used For**: Participation ratio formula, awareness of bias issues

**Repository 3**: danmlr/svr (⭐ 7)
- **URL**: https://github.com/danmlr/svr
- **Query Used**: "randomized SVD pytorch weight matrix"
- **Relevance**: SVR analysis pattern for neural networks
- **Used For**: Pattern for weight extraction and analysis

**Repository 4**: huggingface/pytorch-image-models (⭐ 37058)
- **URL**: https://github.com/huggingface/pytorch-image-models
- **Query Used**: "timm pytorch image models pretrained"
- **Relevance**: Source of pretrained models
- **Used For**: Model loading API reference

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear

### D. Previous Hypothesis Context

**Previous Context**: None - this is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Model loading | GitHub | huggingface/pytorch-image-models |
| Randomized SVD | GitHub | aliutkus/torchrsvd |
| Participation ratio | GitHub + Paper | badooki/dimensionality (ICLR 2026) |
| Weight extraction pattern | GitHub | danmlr/svr |
| CV computation | Standard | NumPy std/mean |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE)
**Date:** 2026-08-10

### Workflow History for This Hypothesis
- Phase 2C Step 01: Initialized
- Phase 2C Step 02: Archon KB search (3 queries)
- Phase 2C Step 03: Exa GitHub search (4 repos found)
- Phase 2C Step 04: Serena skipped (code clear)
- Phase 2C Step 05: Dataset confirmed (timm model zoo)
- Phase 2C Step 06: Specification synthesized
- Phase 2C Step 07: References documented
- Phase 2C Step 08: Validation complete

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
