# Experiment Design: H-E1

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under CNN model zoo scope, if we analyze class-wise accuracy profiles across models, then variance beyond overall accuracy will be observed
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK - Foundation Gate

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK gate - If this fails, entire research direction stops. Behavioral prediction is meaningless without behavioral variance.

---

## Continuation Context

This is the foundation hypothesis. No previous results to build on.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP unavailable - used Exa search instead*

**Key Prior Work Identified:**
1. **Model Zoo Dataset (Schürholt et al., NeurIPS 2022)**: Standardized dataset of ~50,360 CNN models trained on CIFAR-10 with stored predictions and metrics
2. **SANE (ICML 2024)**: Sequential Autoencoder for Neural Embeddings - weight space learning achieving R² > 0.9 for accuracy prediction
3. **Predicting Neural Network Accuracy from Weights (Unterthiner et al., 2020)**: Baseline achieving R² ~0.97 on small CNN zoo

### Archon Code Examples

*Archon MCP unavailable - used Exa code search instead*

**Relevant Code Patterns:**
- ModelZoos/ModelZooDataset: PyTorch dataset class for loading model checkpoints with metrics
- HSG-AIML/SANE: Weight embedding pipeline with downstream task evaluation
- google-research/dnn_predict_accuracy: Metrics CSV format with test_accuracy per model

### Exa GitHub Implementations

**Primary Sources:**
1. **github.com/ModelZoos/ModelZooDataset** - Official model zoo dataset loader
   - Contains preprocessed .pt files with train/test/val splits
   - Includes metrics per model per epoch (accuracy, loss)
   - Custom PyTorch dataset class in `code/checkpoints_to_datasets/dataset_base.py`

2. **Zenodo DOI: 10.5281/zenodo.6620868** - CIFAR-10 CNN model zoos
   - `cifar_small_hyp_rand.zip` (2.0 GB): ~3000 small CNN models with hyperparameter variation
   - `dataset_cifar_small_hyp_rand.pt` (1.8 GB): Preprocessed PyTorch dataset
   - Contains per-model predictions enabling confusion matrix computation

3. **github.com/HSG-AIML/SANE** - SANE implementation
   - Sequential weight processing for scalable embeddings
   - Benchmark code in `code/benchmark_results.ipynb`

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Source | Reason |
|----------|--------|--------|
| 1 | ModelZoos/ModelZooDataset | Official dataset loader, verified metrics |
| 2 | Zenodo preprocessed .pt files | Direct PyTorch loading, fastest setup |
| 3 | Raw checkpoint files | Full flexibility, requires more processing |

**Recommended Implementation Path:**
- Primary: Download `dataset_cifar_small_hyp_rand.pt` from Zenodo (DOI: 10.5281/zenodo.6620868)
- Fallback: Clone ModelZoos/ModelZooDataset and use custom dataset class
- Justification: Preprocessed .pt contains vectorized weights + metrics, minimizes setup time

### Code Analysis (Serena MCP)

*Serena analysis not applicable - this is a data analysis task, not codebase modification*

---

## Experiment Specification

### Dataset

**Name:** Small CNN Zoo - CIFAR-10 (Hyperparameter Random)
**Type:** standard (real, established dataset)
**Source:** Zenodo DOI: 10.5281/zenodo.6620868
**Size:** ~3000 models with stored predictions across 9 training epochs

| Attribute | Value |
|-----------|-------|
| Models | ~3000 small CNNs |
| Architecture | 3 conv layers (16 units each) + GAP + dense (4970 params) |
| Training Dataset | CIFAR-10 (10 classes) |
| Variation | Random hyperparameters + random seeds |
| Stored Data | Model weights, per-epoch metrics, predictions |

**Splits:**
- Train: Not applicable (analysis task, not training)
- Validation: Not applicable
- Test: All ~3000 models (full analysis)

**Preprocessing:**
1. Load preprocessed dataset from `dataset_cifar_small_hyp_rand.pt`
2. Extract final epoch checkpoints (epoch 86)
3. For each model: compute class-wise accuracy from stored predictions

**Loading Information** (for Phase 4 download):
- Method: zenodo_download
- Identifier: 10.5281/zenodo.6620868
- Code:
```python
import torch
from pathlib import Path

# Download from Zenodo (manual or wget)
# wget https://zenodo.org/records/6620869/files/dataset_cifar_small_hyp_rand.pt

dataset = torch.load("dataset_cifar_small_hyp_rand.pt")
# dataset contains: weights, metrics (accuracy, loss per epoch)
```

### Models

#### Baseline Model

**Name:** Stratified Baseline (Overall Accuracy + Per-Class Difficulty)
**Description:** Predicts class-wise accuracy as: `class_acc[i] = overall_acc * class_difficulty[i]`

Where `class_difficulty[i]` = mean accuracy on class i across all models (captures inherent class hardness).

This baseline tests H0: "Class-wise profiles are fully explained by overall accuracy + fixed per-class difficulty"

**Loading Information** (for Phase 4 download):
- Method: computed (no external model needed)
- Identifier: N/A
- Code:
```python
# Compute stratified baseline
class_difficulty = class_wise_acc.mean(axis=0)  # shape: (10,)
baseline_pred = overall_acc[:, None] * class_difficulty[None, :]
```

#### Proposed Model

**Architecture:** Statistical variance analysis (no trained model)

**Core Mechanism Implementation:**

```python
# Core analysis: Does class-wise variance exist beyond overall accuracy?
# Input: predictions for ~3000 models on CIFAR-10 test set

import numpy as np
from sklearn.metrics import r2_score

def analyze_behavioral_variance(model_predictions, ground_truth):
    """
    Compute class-wise accuracy profiles and analyze variance.
    
    Args:
        model_predictions: dict[model_id] -> np.array shape (10000,) predictions
        ground_truth: np.array shape (10000,) CIFAR-10 test labels
    
    Returns:
        dict with variance analysis results
    """
    n_models = len(model_predictions)
    n_classes = 10
    
    # Step 1: Compute class-wise accuracy for each model
    class_wise_acc = np.zeros((n_models, n_classes))
    overall_acc = np.zeros(n_models)
    
    for i, (model_id, preds) in enumerate(model_predictions.items()):
        overall_acc[i] = (preds == ground_truth).mean()
        for c in range(n_classes):
            mask = (ground_truth == c)
            class_wise_acc[i, c] = (preds[mask] == c).mean()
    
    # Step 2: Compute stratified baseline prediction
    class_difficulty = class_wise_acc.mean(axis=0)  # per-class mean
    baseline_pred = overall_acc[:, None] * (class_difficulty / class_difficulty.mean())
    
    # Step 3: Compute variance explained
    total_variance = np.var(class_wise_acc)
    baseline_residual = class_wise_acc - baseline_pred
    residual_variance = np.var(baseline_residual)
    
    variance_explained_by_baseline = 1 - (residual_variance / total_variance)
    residual_ratio = residual_variance / total_variance
    
    # Step 4: R² of baseline
    r2_baseline = r2_score(class_wise_acc.flatten(), baseline_pred.flatten())
    
    return {
        "total_variance": total_variance,
        "residual_variance": residual_variance,
        "residual_ratio": residual_ratio,  # SUCCESS if > 0.05
        "r2_baseline": r2_baseline,
        "class_difficulty": class_difficulty,
        "n_models": n_models
    }
```

### Training Protocol

**Not Applicable** - This is a statistical analysis task, not a model training task.

**Analysis Protocol:**
1. Load all ~3000 model predictions from Small CNN Zoo
2. Compute class-wise accuracy profiles (10 values per model)
3. Fit stratified baseline (overall_acc × class_difficulty)
4. Compute residual variance after removing baseline
5. Test: residual_ratio > 0.05 (5% variance unexplained)

### Evaluation

**Primary Metric:** Residual Variance Ratio
- Formula: `residual_variance / total_variance`
- Success Threshold: > 0.05 (5%)
- Interpretation: Fraction of class-wise variance NOT explained by overall accuracy + class difficulty

**Secondary Metrics:**
1. R² of stratified baseline (lower = more unexplained variance = good for H-E1)
2. Per-class variance (σ² of accuracy across models for each class)
3. Inter-model correlation (do models cluster by behavioral pattern?)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical_analysis
- Library: numpy, sklearn.metrics
- Code:
```python
from sklearn.metrics import r2_score
import numpy as np

# Primary metric
residual_ratio = residual_variance / total_variance
success = residual_ratio > 0.05

# Secondary metric
r2_baseline = r2_score(class_wise_acc.flatten(), baseline_pred.flatten())
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing residual_ratio vs 0.05 threshold

#### Additional Figures (LLM Autonomous)

1. **Class-wise Accuracy Heatmap**: Models × Classes heatmap showing accuracy patterns
2. **Variance Decomposition Pie Chart**: Baseline-explained vs residual variance
3. **Per-Class Variance Bar Plot**: σ² of accuracy for each of 10 classes
4. **Model Clustering Scatter**: PCA of class-wise profiles colored by overall accuracy

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `residual_ratio > 0.05` (residual variance > 5% of total)

**Gate Decision:**
- PASS: Proceed to H-M1 (weights encode behavioral info)
- FAIL: STOP entire research direction (no behavioral variance exists)

---

## Appendix: Reference Implementations

### A. Model Zoo Dataset Loader
**Source:** github.com/ModelZoos/ModelZooDataset
**File:** `code/checkpoints_to_datasets/dataset_base.py`
**License:** MIT

### B. Zenodo Dataset Structure
```
dataset_cifar_small_hyp_rand.pt
├── weights: Tensor[N_models, 4970]  # Flattened model parameters
├── metrics: DataFrame
│   ├── model_id
│   ├── epoch
│   ├── test_accuracy
│   ├── test_loss
│   └── train_accuracy
└── config: dict  # Hyperparameter configurations
```

### C. CIFAR-10 Ground Truth
```python
from torchvision.datasets import CIFAR10
test_dataset = CIFAR10(root='./data', train=False, download=True)
ground_truth = np.array(test_dataset.targets)  # shape: (10000,)
```

### D. Class-wise Accuracy Computation Reference
```python
# From google-research/dnn_predict_accuracy pattern
def compute_class_accuracy(predictions, labels, n_classes=10):
    class_acc = np.zeros(n_classes)
    for c in range(n_classes):
        mask = (labels == c)
        class_acc[c] = (predictions[mask] == c).mean()
    return class_acc
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19: Hypothesis h-e1 set to IN_PROGRESS (Phase 2C start)
- 2026-08-19: Phase 2C experiment design completed

---

## Quality Validation

### Checklist

- [x] Dataset specified with real data source (Zenodo Small CNN Zoo)
- [x] Sample size statistically meaningful (~3000 models, full test set)
- [x] No synthetic data used
- [x] Baseline model defined (stratified accuracy baseline)
- [x] Core mechanism pseudo-code provided (10-30 lines)
- [x] Evaluation metrics with success thresholds
- [x] Visualization requirements specified
- [x] Reference implementations cited with sources

### MCP Sources Cited

1. Exa GitHub: ModelZoos/ModelZooDataset
2. Exa GitHub: HSG-AIML/SANE
3. Exa Zenodo: 10.5281/zenodo.6620868
4. Exa GitHub: google-research/dnn_predict_accuracy

---

*MCP Tools Used: Exa (GitHub + Web Search)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
