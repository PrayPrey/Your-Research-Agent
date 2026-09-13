# Experiment Design: H-M2

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under Model Zoo benchmark, if we add Git Re-Basin alignment preprocessing to Layer-wise encoding, then Pearson correlation improves by Δr > 0.05, because alignment removes permutation-induced variance revealing functional equivalence.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing alignment preprocessing benefit.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 PASS (Δr=0.1262, p=0.0002)
**Gate Status:** SHOULD_WORK (allows failure with documentation)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (Layer-wise Structure Advantage)

### Gate Condition
SHOULD_WORK: Δr > 0.05 with p < 0.05. Failure documented as limitation, verification continues.

---

## Continuation Context

Building on H-M1 validated Layer-wise encoding (mean r=0.547). H-M2 tests whether Git Re-Basin alignment preprocessing further improves correlation by removing permutation-induced variance.

### Previous Hypothesis Results
- **H-M1 Result:** PASS
- **Layer-wise Mean r:** 0.547
- **Flatten+MLP Mean r:** 0.421
- **Improvement:** Δr = 0.1262
- **Key Learning:** Per-layer statistics (mean, std, min, max) capture functional patterns

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable (no-mcp mode). Using verification plan context.*

Git Re-Basin (Ainsworth et al., 2022):
- Aligns neural network weights via permutation matching
- Demonstrated on ResNets, enables model merging
- Key algorithm: weight matching to minimize activation distance
- Reference model selection matters (random or first model typical)

### Archon Code Examples

*MCP unavailable. Using established implementations.*

```python
# Git Re-Basin core concept
from git_rebasin import PermutationSpec, weight_matching

# Define permutation specification for architecture
perm_spec = PermutationSpec.from_axes(model)
# Find optimal permutation to align model_b to model_a
perm = weight_matching(perm_spec, model_a.state_dict(), model_b.state_dict())
# Apply permutation
aligned_sd = perm.apply(model_b.state_dict())
```

### Exa GitHub Implementations

*MCP unavailable. Primary references from literature:*

1. **Official Git Re-Basin:** github.com/samuela/git-re-basin
   - PyTorch implementation of weight matching
   - PermutationSpec for various architectures
   
2. **Model Zoos codebase:** github.com/HSG-AIML/model-zoos
   - Contains CIFAR-10 Model Zoo dataset
   - Standardized model checkpoints

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

Given no MCP access, use established codebases:
1. Git Re-Basin official repo for alignment
2. H-M1 validated codebase for Layer-wise encoding

**Recommended Implementation Path:**
- Primary: Integrate git-re-basin library into H-M1 codebase
- Fallback: Implement simplified weight matching if library issues
- Justification: Official implementation ensures correctness; H-M1 code already validated

### Code Analysis (Serena MCP)

*MCP unavailable. Architecture analysis from H-M1:*

Model Zoo architecture: Simple CNN (Conv-Conv-FC pattern)
- Conv1: [in_channels, 32, 3, 3]
- Conv2: [32, 64, 3, 3]  
- FC layers vary by model

Permutation points: After each conv layer (channel permutation)

---

## Experiment Specification

### Dataset

**Name:** CIFAR-10 Model Zoo (Small)
**Source:** HSG-AIML/model-zoos (Schurholt et al., 2022)
**Total Models:** 61,335
**Split:**
- Train: 42,650 (70%)
- Validation: 9,340 (15%)
- Test: 9,345 (15%)

**Type:** standard (real benchmark, not synthetic)

**Preprocessing:**
1. Load model checkpoints (.pt files)
2. Extract state_dict
3. Apply Git Re-Basin alignment to reference model
4. Apply Layer-wise statistics extraction (mean, std, min, max per layer)

**Loading Information** (for Phase 4 download):
- Method: Custom loader (same as H-M1)
- Identifier: CIFAR-10 Model Zoo from H-M1 validated codebase
- Code:
```python
from data import load_model_zoo
models, labels = load_model_zoo(split='train')  # Reuse H-M1 data loading
```

### Models

#### Baseline Model

**Architecture:** Layer-wise Encoder + MLP Regressor (from H-M1)

**Components:**
1. Layer-wise Statistics: Per-layer (mean, std, min, max)
2. Aggregation: Concatenate all layer stats
3. Regressor: MLP [input_dim → 256 → 128 → 1]

**Expected Performance:** r ≈ 0.547 (from H-M1)

**Loading Information** (for Phase 4 download):
- Method: Reuse H-M1 codebase
- Identifier: h-m1/code/models.py
- Code:
```python
from models import LayerwiseEncoder, MLPRegressor
encoder = LayerwiseEncoder(layer_dims)
regressor = MLPRegressor(encoder.output_dim)
```

#### Proposed Model

**Architecture:** Git Re-Basin Alignment + Layer-wise Encoder + MLP Regressor

**Core Mechanism Implementation:**

```python
# Git Re-Basin Alignment Preprocessing
# ponytail: simplified weight matching, full GRB if convergence issues

import torch
from typing import Dict, List

def align_to_reference(
    model_sd: Dict[str, torch.Tensor],
    reference_sd: Dict[str, torch.Tensor],
    perm_layers: List[str]
) -> Dict[str, torch.Tensor]:
    """
    Align model weights to reference using weight matching.
    
    Args:
        model_sd: State dict of model to align
        reference_sd: State dict of reference model
        perm_layers: Layer names where permutation applies
    
    Returns:
        Aligned state dict
    """
    aligned_sd = model_sd.copy()
    
    for layer_name in perm_layers:
        # Get weight matrices
        w_ref = reference_sd[layer_name]  # [out, in, ...]
        w_model = model_sd[layer_name]
        
        # Compute optimal permutation via correlation matrix
        # Shape: [out_ref, out_model]
        w_ref_flat = w_ref.view(w_ref.size(0), -1)
        w_model_flat = w_model.view(w_model.size(0), -1)
        
        # Correlation-based matching
        corr = torch.mm(w_ref_flat, w_model_flat.t())  # [out, out]
        
        # Hungarian algorithm for optimal assignment
        # Using greedy approximation for speed
        perm = torch.argmax(corr, dim=1)  # [out]
        
        # Apply permutation to output dimension
        aligned_sd[layer_name] = w_model[perm]
        
        # Propagate to next layer's input dimension
        next_layer = get_next_layer(layer_name, model_sd)
        if next_layer is not None:
            w_next = aligned_sd[next_layer]
            # Reorder input channels
            aligned_sd[next_layer] = reorder_input_dim(w_next, perm)
    
    return aligned_sd


def compute_alignment_batch(
    model_zoo: List[Dict],
    reference_idx: int = 0
) -> List[Dict]:
    """
    Align all models in zoo to reference model.
    
    Args:
        model_zoo: List of state dicts
        reference_idx: Index of reference model (default: first)
    
    Returns:
        List of aligned state dicts
    """
    reference_sd = model_zoo[reference_idx]
    perm_layers = detect_permutable_layers(reference_sd)
    
    aligned_zoo = []
    convergence_count = 0
    
    for i, model_sd in enumerate(model_zoo):
        if i == reference_idx:
            aligned_zoo.append(model_sd)
            convergence_count += 1
            continue
            
        aligned_sd = align_to_reference(model_sd, reference_sd, perm_layers)
        
        # Verify alignment improved correlation
        if verify_alignment(aligned_sd, reference_sd) > verify_alignment(model_sd, reference_sd):
            convergence_count += 1
            
        aligned_zoo.append(aligned_sd)
    
    convergence_rate = convergence_count / len(model_zoo)
    print(f"Alignment convergence: {convergence_rate:.2%}")
    
    return aligned_zoo
```

### Training Protocol

**Optimizer:** AdamW
**Learning Rate:** 1e-3 (same as H-M1)
**LR Schedule:** ReduceLROnPlateau (factor=0.5, patience=5)
**Batch Size:** 256
**Epochs:** 50 max
**Early Stopping:** Patience 10, monitor val_loss
**Loss:** MSE (for regression)
**Regularization:** Weight decay 1e-4

**Two-phase training:**
1. **Alignment Phase:** Run GRB on all train models (offline, once)
2. **Training Phase:** Train Layer-wise encoder + regressor on aligned weights

### Evaluation

**Primary Metric:** Pearson correlation (r) with ground-truth accuracy
**Success Criteria:** 
- Δr > 0.05 (Layer-wise+GRB vs Layer-wise)
- p < 0.05 (paired t-test across 5 seeds)

**Secondary Metrics:**
- GRB convergence rate (target: >95%)
- Training stability (no NaN/divergence)

**Statistical Test:** Paired t-test, 5 random seeds

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Regression
- Library: scipy.stats (pearsonr, ttest_rel)
- Code:
```python
from scipy.stats import pearsonr, ttest_rel
r, p = pearsonr(predictions, ground_truth)
t_stat, p_val = ttest_rel(grb_correlations, baseline_correlations)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing Layer-wise r vs Layer-wise+GRB r

#### Additional Figures (LLM Autonomous)

1. **Scatter Plot:** Predicted vs actual accuracy (both methods)
2. **Per-Seed Comparison:** Line plot showing Δr across 5 seeds
3. **Alignment Diagnostic:** Histogram of pre/post alignment distances
4. **Convergence Rate:** Pie chart of GRB convergence statistics

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## Ablation Studies

### Ablation 1: Reference Model Selection
- **Variants:** Random reference, median-accuracy reference, highest-accuracy reference
- **Measures:** Impact on final correlation

### Ablation 2: Alignment Algorithm
- **Variants:** Greedy matching vs Hungarian algorithm
- **Measures:** Convergence rate, final correlation

### Ablation 3: Partial Alignment
- **Variants:** Align only conv layers, align all layers
- **Measures:** Correlation improvement, compute cost

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `grb_r > baseline_r + 0.05` (mean across seeds)
3. `p_value < 0.05` (paired t-test)
4. GRB convergence rate > 95%

**Secondary Check:**
- Consistent improvement across all 5 seeds

---

## Appendix: Reference Implementations

1. **Git Re-Basin Official**
   - URL: github.com/samuela/git-re-basin
   - Key files: weight_matching.py, permutation_spec.py
   - License: MIT

2. **H-M1 Validated Codebase**
   - Location: h-m1/code/
   - Key files: models.py, data.py, train.py
   - Reuse: Data loading, Layer-wise encoder, training loop

3. **Model Zoos Dataset**
   - URL: github.com/HSG-AIML/model-zoos
   - Paper: Schurholt et al. (2022)
   - Contains: CIFAR-10 trained models with accuracy labels

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- H-M2 set to IN_PROGRESS: 2026-08-19T06:32:11
- Prerequisites: H-M1 PASS (Δr=0.1262, p=0.0002)
- Current Phase: Phase 2C - Experiment Design

---

*MCP Tools Used: None (no-mcp mode)*
*All specifications grounded in H-M1 validated codebase and literature*
*Next Phase: Phase 3 - Implementation Planning*
