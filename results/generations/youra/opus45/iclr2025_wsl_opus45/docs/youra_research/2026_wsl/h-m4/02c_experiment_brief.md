# Experiment Design: h-m4

**Date:** 2026-04-13
**Author:** Anonymous
**Hypothesis Statement:** Under controlled conditions, if we analyze Grassmann distances per layer type, then some layers (attention vs MLP) will show stronger task-similarity clustering than others (at least one layer type with Cohen's d > 0.8), because different layers encode different aspects of task-specific transformations.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM (Exploratory) Template** - Testing layer-wise clustering strength differences.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-m3 VALIDATED)
**Gate Status:** SHOULD_WORK (exploratory - failure informs but doesn't block)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m4
- **Type:** MECHANISM (Exploratory)
- **Prerequisites:** h-m3 (VALIDATED - Spearman ρ = 0.389)

### Gate Condition
- **Primary:** At least one layer type shows Cohen's d > 0.8
- **Secondary:** Systematic attention vs MLP difference identified
- **Consequence if Fails:** EXPLORE (informative null result, no mechanism block)

---

## Continuation Context

This experiment is a **continuation** from H-E1 and H-M3, reusing the same 40 trained LoRA adapters.

### Previous Hypothesis Results

**H-E1 (EXISTENCE - VALIDATED):**
- 40 adapters trained (8 tasks × 5 seeds)
- Aggregate Cohen's d = 0.7652 (within vs between cluster)
- p = 8.63e-28 (highly significant)
- Adapters stored at: `h-e1/results/`

**H-M3 (MECHANISM - VALIDATED):**
- Spearman ρ = 0.389 between Grassmann distances and FLAN taxonomy
- p = 1.29e-29
- 95% CI [0.328, 0.450] excludes zero
- Reused H-E1 distance matrix

**Continuation Rationale:** H-M4 disaggregates the aggregate analysis from H-E1/H-M3 to identify which specific layer types carry the strongest task-similarity signal. Same adapters, layer-wise breakdown.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP unavailable - relying on Exa GitHub implementations*

### Archon Code Examples

*Archon MCP unavailable*

### Exa GitHub Implementations

**Query 1: LoRA Layer-wise Analysis**

**Source 1**: Layer-wise LoRA Analysis Research (arXiv:2603.15990)
- **URL**: https://arxiv.org/pdf/2603.15990
- **Relevance**: W2T framework for LoRA weight space learning with layer-wise encoding
- **Key Insight**: Position-level and layer-level transformers can process LoRA adapters hierarchically
- **Pattern**: Layer embeddings + position embeddings for LoRA analysis

**Source 2**: LISA - Layerwise Importance Sampled AdamW (OpenReview)
- **URL**: https://openreview.net/pdf?id=mwARP6kgIXj
- **Relevance**: Documents layer-wise weight norm skewness in LoRA training
- **Key Insight**: Bottom and top layers show larger weight norms than intermediate layers
- **Pattern**: Layer-wise analysis reveals differential contribution patterns

**Source 3**: PLoP - Precise LoRA Placement (arXiv:2506.20629)
- **URL**: https://arxiv.org/pdf/2506.20629
- **Relevance**: Analyzes attention vs MLP module placement for LoRA
- **Key Insight**: Different layers (attention vs MLP) have different alignment with tasks
- **Pattern**: NFN (Normalized Feature Norm) scores differ by module type

**Query 2: Grassmann Distance Implementation**

**Source 4**: Grassmann Distance PyTorch Implementation
- **URL**: https://jyopari.github.io/posts/grassman
- **Code Pattern**:
```python
import torch
import math

def grassman(A, B):
    # get orthogonal basis
    Q_A, R = torch.linalg.qr(A)
    Q_B, R = torch.linalg.qr(B)
    # get singular values
    _, S, _ = torch.svd(Q_A.T @ Q_B)
    # cosine inverse
    thetas = torch.arccos(S)
    # return norm
    return torch.norm(thetas, p=2)
```

**Source 5**: UQpy Grassmann Distances Documentation
- **URL**: https://uqpyproject.readthedocs.io/en/stable/utilities/distances/grassmann_distances.html
- **Relevance**: Formal definitions of Grassmann distance metrics
- **Key Insight**: Principal angles from SVD of X₀ᵀX₁

**Source 6**: Grassmann Pooling for Fine-Grained Classification (ECCV 2018)
- **URL**: https://www.ecva.net/papers/eccv_2018/papers_ECCV/papers/Xing_Wei_Grassmann_Pooling_for_ECCV_2018_paper.pdf
- **Relevance**: Projection distance definition for Grassmann manifold
- **Formula**: dP(U1, U2) = √(k - ||U1ᵀU2||²F)

### Implementation Priority Assessment

**CRITICAL: Analysis-only experiment reusing H-E1 validated adapters**

**Recommended Implementation Path:**
- Primary: Extend H-E1 analysis infrastructure with layer-type grouping
- Fallback: N/A (adapters already exist)
- Justification: No new training needed; pure analysis of existing layer-wise B matrices

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear for this analysis-only experiment.

---

## Experiment Specification

### Dataset

**Dataset**: H-E1 Validated Adapters
**Type**: custom (real experimental data)

**Statistics**:
- Total adapters: 40 (8 tasks × 5 seeds)
- Tasks: gsm8k, arc, logiqa, strategyqa (Reasoning); mnli, qqp, sst2, mrpc (NLU)
- Layers per adapter: 22 transformer layers
- Layer types: 7 (q_proj, k_proj, v_proj, o_proj, up_proj, down_proj, gate_proj)

**Loading Information** (for Phase 4):
- Method: Local file system
- Identifier: `h-e1/results/`
- Code:
```python
import os
import torch
from pathlib import Path

def load_adapters(results_dir: Path) -> dict:
    """Load all H-E1 adapters organized by task and seed."""
    adapters = {}
    adapter_dir = results_dir / "adapters"
    for task_dir in adapter_dir.iterdir():
        if task_dir.is_dir():
            task_name = task_dir.name
            adapters[task_name] = {}
            for seed_dir in task_dir.iterdir():
                seed = int(seed_dir.name.replace("seed_", ""))
                adapter_path = seed_dir / "adapter_model.safetensors"
                adapters[task_name][seed] = load_adapter_weights(adapter_path)
    return adapters
```

### Models

#### Baseline Model

**Architecture**: TinyLlama-1.1B-Chat-v1.0
**Configuration**: 22 transformer layers, LoRA r=32, alpha=64
**Source**: TinyLlama/TinyLlama-1.1B-Chat-v1.0 (same as H-E1)

**Loading Information** (for Phase 4):
- Method: Not needed (analysis-only, model already used in H-E1)
- Identifier: N/A
- Code: N/A (no model inference needed)

#### Proposed Model

**Architecture**: Layer-wise Grassmann Distance Analysis Pipeline

**Core Mechanism Implementation:**

```python
# Core Mechanism: Layer-wise Grassmann Distance Analysis
# Based on: H-E1 infrastructure + layer grouping extension

import torch
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple

# Layer type definitions for TinyLlama
ATTENTION_LAYERS = ['q_proj', 'k_proj', 'v_proj', 'o_proj']
MLP_LAYERS = ['up_proj', 'down_proj', 'gate_proj']
ALL_LAYER_TYPES = ATTENTION_LAYERS + MLP_LAYERS

def grassmann_distance(A: torch.Tensor, B: torch.Tensor) -> float:
    """Compute Grassmann geodesic distance between column spaces."""
    Q_A, _ = torch.linalg.qr(A)
    Q_B, _ = torch.linalg.qr(B)
    S = torch.linalg.svdvals(Q_A.T @ Q_B)
    S = torch.clamp(S, -1.0, 1.0)  # numerical stability
    thetas = torch.arccos(S)
    return torch.norm(thetas, p=2).item()

def extract_layer_distances(adapters: Dict, layer_type: str) -> np.ndarray:
    """Extract pairwise distances for a specific layer type across all adapters."""
    # Filter B matrices for this layer type across all layers
    # Compute pairwise Grassmann distances
    # Return distance matrix
    pass

def compute_cohens_d(within: np.ndarray, between: np.ndarray) -> Tuple[float, float, float]:
    """Compute Cohen's d with 95% CI for within vs between comparison."""
    n1, n2 = len(within), len(between)
    mean1, mean2 = np.mean(within), np.mean(between)
    var1, var2 = np.var(within, ddof=1), np.var(between, ddof=1)
    
    # Pooled standard deviation
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    d = (mean2 - mean1) / pooled_std  # between > within expected
    
    # Standard error (Hedges & Olkin, 1985)
    se = np.sqrt((n1+n2)/(n1*n2) + d**2/(2*(n1+n2)))
    ci_low = d - 1.96 * se
    ci_high = d + 1.96 * se
    
    return d, ci_low, ci_high

def analyze_layer_types(adapters: Dict, task_categories: Dict) -> Dict:
    """Main analysis: compute Cohen's d per layer type."""
    results = {}
    for layer_type in ALL_LAYER_TYPES:
        distances = extract_layer_distances(adapters, layer_type)
        within, between = split_by_category(distances, task_categories)
        d, ci_low, ci_high = compute_cohens_d(within, between)
        results[layer_type] = {
            'cohens_d': d,
            'ci_low': ci_low,
            'ci_high': ci_high
        }
    return results
```

### Training Protocol

**No Training Required** - This is an analysis-only experiment.

**Analysis Protocol:**
1. Load 40 adapters from H-E1 results
2. For each layer type (7 types):
   - Extract B matrices from all 22 layers matching that type
   - Compute pairwise Grassmann distances (40×40 matrix per layer)
   - Average across layers of same type
3. For each layer type:
   - Split distances into within-cluster and between-cluster
   - Compute Cohen's d with bootstrap 95% CI
4. Rank layer types by Cohen's d
5. Test attention vs MLP group difference

**Computational Requirements:**
- No GPU needed (pure numpy/scipy analysis)
- Estimated runtime: < 5 minutes
- Memory: < 4GB RAM

### Evaluation

**Primary Metrics:**
- Cohen's d per layer type (7 values)
- 95% confidence interval for each Cohen's d

**Success Criteria:**
- **Primary:** At least one layer type shows Cohen's d > 0.8
- **Secondary:** Systematic difference between attention (q/k/v/o) and MLP (up/down/gate) layer groups

**Expected Baseline Performance** (from H-E1 aggregate):
- Aggregate Cohen's d = 0.7652
- We expect some layers to exceed this (d > 0.8) while others may be lower

**Metrics Loading Information**:
- Task Type: Statistical comparison
- Library: `scipy.stats`, `pingouin` (for bootstrap CI)
- Code:
```python
import pingouin as pg
import numpy as np

# Cohen's d with bootstrap CI
def compute_effect_with_ci(within, between):
    d = pg.compute_effsize(within, between, eftype='cohen')
    ci = pg.compute_bootci(within, between, func='cohen', n_boot=2000)
    return d, ci
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing Cohen's d per layer type with 0.8 threshold line and CI error bars

#### Additional Figures (LLM Autonomous)

Based on hypothesis type and analysis:
1. **Layer-type Cohen's d ranking**: Horizontal bar chart ranking all 7 layer types by Cohen's d
2. **Attention vs MLP comparison**: Box/violin plot comparing Cohen's d distribution for attention layers vs MLP layers
3. **Heatmap per layer type**: 8×8 task-level mean distance heatmap for highest-d layer type
4. **Distribution plots**: KDE/histogram of within vs between distances for top 2 and bottom 2 layer types

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m4/figures/`.

---

## Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists**: Yes - Layer-type grouping and per-type distance computation
- **mechanism_isolatable**: Yes - Each layer type analyzed independently
- **baseline_measurable**: Yes - H-E1 aggregate Cohen's d = 0.7652 serves as baseline

### Architecture Compatibility
- TinyLlama has 7 distinct layer types across 22 transformer layers
- Layer naming follows pattern: `model.layers.{i}.{layer_type}.lora_B`
- All layer types present in every transformer layer

### Activation Indicators
- **Log message**: "Analyzing layer type: {layer_type}, distances computed: {n_pairs}"
- **Tensor shape change**: Distance matrix per layer type: (40, 40)
- **Metric delta expected**: Cohen's d should vary across layer types; at least one > 0.8

### Mechanism Verification Code
```python
def verify_mechanism(results: Dict) -> bool:
    """Verify that layer-wise analysis produces valid results."""
    # Check all layer types analyzed
    assert len(results) == 7, f"Expected 7 layer types, got {len(results)}"
    
    # Check Cohen's d computed for each
    for layer_type, metrics in results.items():
        assert 'cohens_d' in metrics, f"Missing Cohen's d for {layer_type}"
        assert 'ci_low' in metrics, f"Missing CI for {layer_type}"
        print(f"Layer {layer_type}: d={metrics['cohens_d']:.3f} [{metrics['ci_low']:.3f}, {metrics['ci_high']:.3f}]")
    
    # Primary success criterion
    max_d = max(m['cohens_d'] for m in results.values())
    best_layer = max(results.keys(), key=lambda k: results[k]['cohens_d'])
    print(f"Best layer type: {best_layer} with Cohen's d = {max_d:.3f}")
    
    return max_d > 0.8
```

### Success Thresholds
- **hypothesis_support_threshold**: Cohen's d > 0.8 for at least one layer type
- **hypothesis_support_metric**: Maximum Cohen's d across layer types

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. At least one layer type shows Cohen's d > 0.8
3. Clear ranking of layer types by effect size

**Secondary Success:**
- Attention layers (q/k/v/o) vs MLP layers (up/down/gate) show systematic difference
- Results inform practical applications (e.g., which layers to prioritize for adapter matching)

---

## Appendix: Reference Implementations

### A. Exa GitHub Sources

**Source 1**: Grassmann Distance Implementation (jyopari)
- **URL**: https://jyopari.github.io/posts/grassman
- **Query Used**: "Grassmann distance layer-wise neural network subspace analysis principal angles PyTorch"
- **Key Code**:
```python
def grassman(A, B):
    Q_A, R = torch.linalg.qr(A)
    Q_B, R = torch.linalg.qr(B)
    _, S, _ = torch.svd(Q_A.T @ Q_B)
    thetas = torch.arccos(S)
    return torch.norm(thetas, p=2)
```
- **Used For**: Grassmann distance computation in layer-wise analysis

**Source 2**: Cohen's d with Bootstrap CI (pingouin)
- **URL**: https://pingouin-stats.org/generated/pingouin.compute_bootci.html
- **Query Used**: "Cohen's d effect size calculation Python scipy statistics bootstrap confidence interval"
- **Key Code**:
```python
import pingouin as pg
d = pg.compute_effsize(within, between, eftype='cohen')
ci = pg.compute_bootci(within, between, func='cohen', n_boot=2000)
```
- **Used For**: Effect size computation with confidence intervals

**Source 3**: Layer-wise LoRA Analysis Research
- **URL**: https://arxiv.org/pdf/2506.20629 (PLoP paper)
- **Query Used**: "LoRA adapter layer-wise analysis attention MLP weight space PyTorch"
- **Key Insight**: Different layer types (attention vs MLP) have different task alignment
- **Used For**: Hypothesis rationale and expected patterns

### B. Previous Hypothesis Context

**Source**: H-E1 and H-M3 Validation Reports
- **Files**: `h-e1/04_validation.md`, `h-m3/04_validation.md`
- **Reused Components**:
  - 40 trained LoRA adapters
  - Task category assignments (FLAN taxonomy)
  - Grassmann distance computation infrastructure
- **Why Reused**: Enables controlled analysis - only aggregation level changes (aggregate → per-layer-type)

### C. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (H-E1 adapters) | Previous Hypothesis | H-E1 validation report |
| Grassmann distance | Exa GitHub | jyopari blog |
| Cohen's d computation | Exa GitHub | pingouin docs |
| Layer-type grouping | Exa Research | PLoP paper, LISA paper |
| Bootstrap CI | Exa GitHub | pingouin docs |
| Success thresholds | Phase 2B | 02b_verification_plan.md |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-13T05:30:00+00:00

### Workflow History for This Hypothesis
- 2026-04-13T05:13:48: Hypothesis h-m4 set to IN_PROGRESS
- 2026-04-13T05:30:00: Phase 2C experiment design completed

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Exa (GitHub/Code Context)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
