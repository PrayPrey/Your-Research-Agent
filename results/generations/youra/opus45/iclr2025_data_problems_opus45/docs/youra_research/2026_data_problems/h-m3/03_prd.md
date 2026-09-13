# Product Requirements Document: H-M3

**Date:** 2026-03-26
**Author:** Anonymous
**Hypothesis ID:** H-M3
**Hypothesis Type:** MECHANISM (INCREMENTAL)
**Gate:** SHOULD_WORK
**Prerequisites:** H-M2 (VALIDATED)
**Phase 2C Source:** 02c_experiment_brief.md

---

## Executive Summary

This PRD defines the implementation requirements for validating hypothesis H-M3: demonstrating that methods with different design paradigms (random projection vs HVP iteration vs gradient similarity) show persistent relative advantages on different metrics across compute levels, with top-k Jaccard < 0.70 (>30% disagreement on influential examples). This hypothesis tests the mechanistic claim that trade-offs are tied to method design philosophy, not just measurement noise.

**Objective:** Implement a method comparison experiment that computes pairwise top-k Jaccard similarity between attribution methods, demonstrating that different design paradigms identify fundamentally different sets of influential examples.

**Success Criteria:**
- Code runs without error for all 4 methods × 5 compute budgets × 3 seeds
- min(top-k Jaccard) < 0.70 (>30% disagreement between at least one method pair)
- Persistent relative advantages observed across compute budgets
- Design paradigm correlates with metric strength

---

## Problem Statement

### Context
H-M2 established that metric decoupling in deep networks is structural (R²_deep = 0.034 < 0.80), proving that the single-error-axis model breaks down in non-convex settings. H-M3 takes this further by asking: do different attribution methods actually identify *different* training examples as influential, or do they merely score the same examples differently?

### Hypothesis
Methods with different design paradigms (random projection vs HVP iteration vs gradient similarity) show persistent relative advantages on different metrics across compute levels, with top-k Jaccard < 0.70 (>30% disagreement on influential examples).

**Mechanistic Reasoning:**
1. TRAK uses random projection (dimension reduction)
2. TracIn uses direct dot-product with checkpoint scaling
3. IF uses eigenvalue-weighted gradients (Hessian approximation)
4. FastIF uses gradient similarity with structured noise
5. These fundamentally different approaches should identify different influential examples
6. Low Jaccard similarity proves methods don't just score differently—they disagree on *which* examples matter

### Gap Being Addressed
H-M2 showed metrics decouple structurally; H-M3 demonstrates this decoupling manifests as concrete disagreement on influential example identification. This proves the Pareto trade-offs have practical implications: choosing different methods yields different data attribution insights.

---

## Functional Requirements

### FR-1: Data Pipeline (Reuse from H-E1)

**FR-1.1: CIFAR-10 Dataset**
- Source: torchvision.datasets.CIFAR10
- Training subset: 5,000 samples (matching H-E1/H-M1/H-M2)
- Test subset: 100 samples (for influence computation)
- Preprocessing: Normalize with mean=[0.4914, 0.4822, 0.4465], std=[0.2023, 0.1994, 0.2010]

```python
import torchvision
from torchvision import transforms

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.4914, 0.4822, 0.4465],
        std=[0.2023, 0.1994, 0.2010]
    )
])

train_dataset = torchvision.datasets.CIFAR10(
    root='./data', train=True, download=True, transform=transform
)
```

**FR-1.2: LOO Ground Truth (Optional - for Metric Computation)**
- Load cached LOO ground truth: `../h-e1/code/results/loo_cache.npy`
- Shape: (5000, 100) - influence of each training sample on each test sample
- Note: Primary analysis uses top-k sets, not correlation with LOO

### FR-2: Deep Network Model (Reuse from H-E1)

**FR-2.1: Pre-trained ResNet-18**
- Load from H-E1: `../h-e1/code/checkpoints/model_seed0_final.pt`
- Architecture: ResNet-18 modified for CIFAR-10 (conv1 kernel=3, no maxpool)
- Output: 10 classes (CIFAR-10)

```python
import torch
import torchvision.models as models
import torch.nn as nn

# Load ResNet-18 checkpoint from H-E1
model = models.resnet18(num_classes=10)
model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
model.maxpool = nn.Identity()
model.load_state_dict(torch.load('../h-e1/code/checkpoints/model_seed0_final.pt'))
model.eval()
```

### FR-3: Attribution Methods (Reuse from H-E1)

**FR-3.1: Methods Configuration**
| Method | Design Paradigm | Key Parameter |
|--------|-----------------|---------------|
| TRAK | Random projection | proj_dim varies with budget |
| TracIn | Gradient dot-product | Checkpoint aggregation |
| IF | HVP iteration | CG iterations, damping |
| FastIF | Gradient similarity | Last-layer only, structured noise |

**FR-3.2: Compute Budget Mapping**
| Budget | Gradient-Equivalents | Method Configuration |
|--------|---------------------|---------------------|
| 10 | 10 | Low approximation |
| 25 | 25 | Medium-low |
| 50 | 50 | Medium |
| 75 | 75 | Medium-high |
| 100 | 100 | Full approximation |

**FR-3.3: Attribution Score Output**
- Each method produces: (n_test, n_train) = (100, 5000) attribution scores
- Higher score = more influential training example

### FR-4: Top-k Jaccard Analysis (PRIMARY - GATE METRIC)

**FR-4.1: Top-k Set Extraction**
```python
import numpy as np

def get_topk_indices(scores, k=50):
    """
    Get indices of top-k most influential training examples per test sample.

    Args:
        scores: (n_test, n_train) attribution scores
        k: Number of top examples to consider

    Returns:
        list of sets, one per test sample
    """
    n_test = scores.shape[0]
    topk_sets = []
    for i in range(n_test):
        # Highest scores = most influential
        topk_indices = np.argsort(-scores[i])[:k]
        topk_sets.append(set(topk_indices))
    return topk_sets
```

**FR-4.2: Pairwise Jaccard Similarity (GATE METRIC)**
```python
def compute_pairwise_jaccard(attribution_scores_dict, k=50):
    """
    Compute pairwise Jaccard similarity between top-k influential sets.

    Args:
        attribution_scores_dict: {method_name: (n_test, n_train) scores}
        k: Number of top influential examples to consider

    Returns:
        jaccard_matrix: (n_methods, n_methods) pairwise Jaccard
        min_jaccard: Minimum pairwise Jaccard across all pairs

    Gate Condition: min_jaccard < 0.70 → PASS (>30% disagreement)
    """
    methods = list(attribution_scores_dict.keys())
    n_methods = len(methods)
    n_test = attribution_scores_dict[methods[0]].shape[0]

    # Get top-k indices for each method and test example
    topk_sets = {}
    for method in methods:
        scores = attribution_scores_dict[method]  # (n_test, n_train)
        topk_sets[method] = get_topk_indices(scores, k)

    # Compute pairwise Jaccard
    jaccard_matrix = np.zeros((n_methods, n_methods))
    for i, m1 in enumerate(methods):
        for j, m2 in enumerate(methods):
            jaccards = []
            for t in range(n_test):
                set1, set2 = topk_sets[m1][t], topk_sets[m2][t]
                intersection = len(set1 & set2)
                union = len(set1 | set2)
                jaccards.append(intersection / union if union > 0 else 1.0)
            jaccard_matrix[i, j] = np.mean(jaccards)

    # Min Jaccard (excluding diagonal)
    mask = ~np.eye(n_methods, dtype=bool)
    min_jaccard = jaccard_matrix[mask].min()

    return jaccard_matrix, min_jaccard
```

**FR-4.3: Jaccard by Budget Level**
```python
def compute_jaccard_by_budget(results_dict, budgets, k=50):
    """
    Compute Jaccard matrices for each budget level.

    Args:
        results_dict: {budget: {method: scores}}
        budgets: List of compute budgets
        k: Number of top examples

    Returns:
        dict: {budget: (jaccard_matrix, min_jaccard)}
    """
    jaccard_by_budget = {}
    for budget in budgets:
        scores = results_dict[budget]
        jaccard_matrix, min_jaccard = compute_pairwise_jaccard(scores, k)
        jaccard_by_budget[budget] = {
            'matrix': jaccard_matrix,
            'min': min_jaccard
        }
    return jaccard_by_budget
```

### FR-5: Metric Persistence Analysis

**FR-5.1: Relative Advantage Tracking**
```python
def compute_relative_advantages(metrics_by_method):
    """
    Track which method has the highest rho_r and rho_m at each budget.

    Args:
        metrics_by_method: {budget: {method: {'rho_r': float, 'rho_m': float}}}

    Returns:
        dict: {budget: {'best_rho_r': method, 'best_rho_m': method}}
    """
    advantages = {}
    for budget, methods in metrics_by_method.items():
        best_r = max(methods.keys(), key=lambda m: methods[m]['rho_r'])
        best_m = max(methods.keys(), key=lambda m: methods[m]['rho_m'])
        advantages[budget] = {
            'best_rho_r': best_r,
            'best_rho_m': best_m
        }
    return advantages
```

**FR-5.2: Persistence Check**
- Verify if same methods maintain advantages across 3+ budget levels
- Report "persistent" if method holds top position for >60% of budgets

### FR-6: Visualization Requirements

**FR-6.1: Jaccard Heatmap (MANDATORY - Gate Figure)**
- Heatmap showing pairwise Jaccard similarity between methods
- X/Y-axis: Method names (TRAK, TracIn, IF, FastIF)
- Cell values: Average Jaccard similarity (0-1)
- Colormap: viridis or coolwarm (low=blue, high=red)
- Title: "Top-50 Influential Example Agreement (Jaccard)"
- Horizontal/vertical line at 0.70 threshold for reference

**FR-6.2: Additional Figures (LLM Autonomous)**

1. **Jaccard by Budget Level**
   - Line plot showing min/mean Jaccard across budgets
   - X: Budget [10, 25, 50, 75, 100]
   - Y: Jaccard similarity
   - Horizontal line at 0.70 threshold

2. **Top-k Overlap Visualization**
   - Venn-style diagram or upset plot showing set overlaps
   - For 2-3 representative test samples
   - Shows which methods agree/disagree

3. **Method Ranking Persistence**
   - Stacked bar or table showing which method leads on each metric per budget
   - Demonstrates if advantages are persistent

4. **Design Paradigm Clustering**
   - Dendrogram or MDS plot based on Jaccard distance
   - Shows if methods cluster by design paradigm

### FR-7: Experiment Orchestration

**FR-7.1: Configuration**
```yaml
# h-m3/config.yaml
experiment:
  name: h-m3-method-disagreement
  hypothesis_type: MECHANISM
  gate: SHOULD_WORK
  base_hypothesis: h-m2

data:
  dataset: cifar10
  train_subset: 5000
  test_subset: 100
  loo_cache: ../h-e1/code/results/loo_cache.npy  # optional

model:
  name: resnet18
  checkpoint: ../h-e1/code/checkpoints/model_seed0_final.pt
  type: non-convex

evaluation:
  methods: [trak, tracin, if, fastif]
  budgets: [10, 25, 50, 75, 100]
  seeds: 3
  top_k: 50

success_criteria:
  jaccard_threshold: 0.70  # Must be BELOW this
  disagreement_percent: 30  # >30% disagreement required
```

**FR-7.2: Output Files**
- `h-m3/results/attribution_scores.npz`: All scores per method/budget/seed
- `h-m3/results/jaccard_analysis.csv`: Pairwise Jaccard results
- `h-m3/results/metric_advantages.csv`: Relative advantage tracking
- `h-m3/figures/jaccard_heatmap.png`: Gate figure
- `h-m3/figures/jaccard_by_budget.png`: Budget analysis
- `h-m3/figures/method_clustering.png`: Paradigm clustering

---

## Non-Functional Requirements

### NFR-1: Performance
- Single GPU execution
- Total runtime: <2 hours (attribution computation + analysis)
- Memory: <16GB GPU RAM
- Reuse cached H-E1 attribution scores if available

### NFR-2: Reproducibility
- Fixed random seeds matching H-E1, H-M1, H-M2
- Reuse H-E1 data indices for exact consistency
- Version-pinned dependencies

### NFR-3: Reusability
- Jaccard computation utilities reusable for future experiments
- Top-k analysis framework generalizable
- Visualization templates shareable

---

## Success Criteria

### Gate: SHOULD_WORK

| Criterion | Description | Threshold |
|-----------|-------------|-----------|
| **SC-1** | Code executes without error | 100% completion |
| **SC-2** | Method disagreement | min(Jaccard) < 0.70 |
| **SC-3** | Persistent advantages | Same method leads >60% of budgets |
| **SC-4** | Design paradigm correlation | Similar paradigms cluster together |

### Mechanism Verification Checklist
- [ ] All 4 methods × 5 budgets × 3 seeds computed
- [ ] Top-k sets extracted (k=50)
- [ ] Pairwise Jaccard computed
- [ ] Gate condition (Jaccard < 0.70) verified
- [ ] Relative advantages tracked across budgets
- [ ] Persistence analysis completed
- [ ] Visualization figures generated

### Failure Response
IF min(Jaccard) >= 0.70 for all method pairs → PARTIAL: Methods may score differently but identify similar examples; trade-offs less practically meaningful

---

## Dependencies

### External Dependencies
- PyTorch >= 2.0
- torchvision (CIFAR-10, ResNet-18)
- numpy, pandas (data manipulation)
- scipy (sparse operations if needed)
- matplotlib, seaborn (visualization)

### Internal Dependencies (from Previous Hypotheses)
- **H-E1:**
  - Pre-trained ResNet-18: `h-e1/code/checkpoints/model_seed0_final.pt`
  - Attribution implementations: `h-e1/code/attribution.py`
  - Data loading: `h-e1/code/data.py`
  - Cached attribution scores (if available): `h-e1/code/results/`

- **H-M2:**
  - Metrics computation: `h-m2/code/metrics_analysis.py`
  - Visualization utilities: `h-m2/code/visualize.py`

### Reference Implementations
- Primary: MadryLab/trak - TRAK implementation
- Secondary: Captum - TracIn implementation
- Tertiary: quanda toolkit - TopKCardinalityMetric concept

---

## Data Specifications

### Input Data (from H-E1)
| Component | Shape | Source |
|-----------|-------|--------|
| Model checkpoint | - | h-e1/code/checkpoints/model_seed0_final.pt |
| CIFAR-10 train | (5000, 3, 32, 32) | torchvision |
| CIFAR-10 test | (100, 3, 32, 32) | torchvision |
| LOO ground truth (optional) | (5000, 100) | h-e1/code/results/loo_cache.npy |

### Experiment Parameters (from Phase 2C)
| Parameter | Value |
|-----------|-------|
| Model | ResNet-18 (non-convex) |
| Methods | TRAK, TracIn, IF, FastIF |
| Compute budgets | 10, 25, 50, 75, 100 |
| Seeds | 3 |
| Top-k | 50 |
| Primary metric | Pairwise Jaccard similarity |
| Gate threshold | min(Jaccard) < 0.70 |

### Output Data
| File | Description |
|------|-------------|
| attribution_scores.npz | Method, budget, seed scores |
| jaccard_analysis.csv | Pairwise Jaccard per budget |
| metric_advantages.csv | Relative advantage tracking |
| figures/*.png | All visualization outputs |

---

## Acceptance Criteria

### Phase 4 Deliverables
1. Data loading pipeline (reusing H-E1 utilities)
2. Attribution score computation for all methods/budgets
3. Top-k set extraction (k=50)
4. Pairwise Jaccard computation
5. Jaccard by budget analysis
6. Relative advantage tracking
7. Persistence analysis
8. Results CSV with all Jaccard metrics
9. Visualization figures (4+ total)
10. 04_validation.md report with gate assessment

### Quality Gates
- Attribution scores computed correctly for all methods
- Jaccard computation numerically correct
- Visualization figures clear and informative
- Gate condition properly evaluated

---

## Appendix: Traceability

| Requirement | Source |
|-------------|--------|
| ResNet-18 model | Phase 2C - H-E1 checkpoint reuse |
| Attribution methods | Phase 2C - H-E1 implementation reuse |
| Gate threshold (0.70) | Phase 2B - verification plan |
| Top-k (50) | Phase 2C - experiment specification |
| Methods | H-E1 - controlled comparison |
| Compute budgets | H-E1 - matched for comparison |
| Jaccard metric | Phase 2C - quanda toolkit reference |

---

*Generated by Phase 3 Implementation Planning*
*Source: Phase 2C Experiment Brief (02c_experiment_brief.md)*
*Next: Architecture Design (03_architecture.md)*
