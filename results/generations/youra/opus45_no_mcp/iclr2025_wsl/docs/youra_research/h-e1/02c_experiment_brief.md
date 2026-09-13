# Experiment Design: H-E1

**Date:** 2026-08-19
**Author:** PrayPrey
**Hypothesis Statement:** Under standard Model Zoo evaluation, if we analyze the accuracy distribution, then σ(accuracy) > 10% and labels are consistent, because diverse training configurations produce meaningful accuracy variance.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (none required)
**Gate Status:** MUST_WORK - not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition

- **Type:** MUST_WORK
- **Pass Condition:** σ(accuracy) > 10%
- **Fail Action:** STOP entire verification chain, benchmark invalid

---

## Continuation Context

This is the **first hypothesis** in the verification chain. No previous results to build upon.

### Previous Hypothesis Results (if applicable)

N/A - H-E1 is the root hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP Archon unavailable - research conducted via web sources*

**Model Zoos Dataset (Schurholt et al. 2022, NeurIPS Datasets & Benchmarks):**
- 50,360 unique neural network models
- 27 distinct model zoos with varying hyperparameter combinations
- 8 base image datasets (CIFAR-10, MNIST, Fashion-MNIST, SVHN, etc.)
- 3,844,360 total collected model states including sparsified variants
- Dataset enables: model analysis, learning dynamics discovery, population representations

**Key Insight:** Dataset designed for studying "populations of NN models" - diverse training configurations are intentional, suggesting accuracy variance is built-in.

### Archon Code Examples

*MCP Archon unavailable*

**Expected loading pattern (from literature):**
```python
# Model Zoos typically loaded via HuggingFace or direct download
from datasets import load_dataset
# OR direct torch loading from .pt files
zoo_data = torch.load("model_zoo_cifar10.pt")
accuracies = zoo_data["test_accuracy"]  # Ground truth labels
```

### Exa GitHub Implementations

*MCP Exa unavailable - research conducted via arxiv/web*

**Source 1:** Model Zoos Paper (arxiv:2209.14764)
- **URL:** https://arxiv.org/abs/2209.14764
- **Relevance:** Primary dataset source
- **Key Details:**
  - Dataset hosted at modelzoos.cc
  - Models trained with systematic hyperparameter variations
  - Each model has associated accuracy from standardized evaluation
  - NeurIPS 2022 peer-reviewed

**Source 2:** Permutation Equivariant Neural Functionals (arxiv:2302.14040)
- **URL:** https://arxiv.org/abs/2302.14040
- **Relevance:** Uses model zoos for "predicting classifier generalization"
- **Key Details:**
  - Validates that model zoos have meaningful accuracy labels
  - Demonstrates accuracy prediction as downstream task

### Implementation Priority Assessment

**CRITICAL: For dataset validation experiments, use official dataset source**

- **Primary:** modelzoos.cc official download
- **Fallback:** HuggingFace mirror if available
- **Justification:** Official source guarantees label consistency and standardized evaluation protocol

**Recommended Implementation Path:**
- Primary: Load from modelzoos.cc or HuggingFace datasets
- Fallback: Direct .pt file download from paper authors
- Justification: Ensures reproducibility with original paper's evaluation protocol

### Code Analysis (Serena MCP)

*Skipped* - This is an observational/statistical analysis experiment, not a mechanism implementation. No complex code requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** Model Zoos CIFAR-10 Zoo
**Type:** standard
**Source:** Schurholt et al. 2022 (NeurIPS Datasets & Benchmarks)

**Statistics:**
- Models: ~5,000-10,000 per zoo (CIFAR-10 subset)
- Architecture: CNN variants
- Training: Varied hyperparameters (lr, batch_size, optimizer, epochs)
- Labels: Test accuracy from standardized CIFAR-10 evaluation

**Preprocessing:**
- Extract accuracy labels only (weights not needed for H-E1)
- Filter out corrupted or incomplete entries
- Normalize to [0, 100] percentage scale

**Splits:**
- Full zoo used (no train/test split needed for observational study)
- Minimum 500+ models required for statistical validity

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets OR direct download
- Identifier: "model-zoos/cifar10" (tentative) or modelzoos.cc
- Code:
```python
# Option 1: HuggingFace (if available)
from datasets import load_dataset
zoo = load_dataset("Konstantin-Scheffold/model-zoos", "cifar10")
accuracies = zoo["train"]["test_accuracy"]

# Option 2: Direct download
import requests
import torch
# Download from modelzoos.cc
zoo_data = torch.load("cifar10_zoo.pt")
accuracies = zoo_data["properties"]["test_accuracy"]
```

### Models

#### Baseline Model

**Architecture:** N/A (observational study)

This hypothesis validates dataset properties, not a model. No baseline model required.

**Loading Information** (for Phase 4 download):
- Method: N/A
- Identifier: N/A
- Code: N/A

#### Proposed Model

**Architecture:** N/A (statistical analysis only)

**Core Mechanism Implementation:**

```python
# H-E1: Model Zoo Dataset Validity Check
# Purpose: Verify accuracy distribution has σ > 10%

import numpy as np
from scipy import stats

def validate_model_zoo_variance(accuracies: np.ndarray) -> dict:
    """
    Validate Model Zoo dataset has sufficient accuracy variance.
    
    Args:
        accuracies: (N,) array of test accuracies [0-100]
    
    Returns:
        dict with statistics and PASS/FAIL status
    """
    # Step 1: Compute basic statistics
    mean_acc = np.mean(accuracies)
    std_acc = np.std(accuracies)
    min_acc = np.min(accuracies)
    max_acc = np.max(accuracies)
    
    # Step 2: Compute quartiles
    q1, q2, q3 = np.percentile(accuracies, [25, 50, 75])
    
    # Step 3: Check for outliers (IQR method)
    iqr = q3 - q1
    outliers = np.sum((accuracies < q1 - 1.5*iqr) | 
                      (accuracies > q3 + 1.5*iqr))
    
    # Step 4: Gate check
    gate_passed = std_acc > 10.0  # σ > 10%
    
    return {
        "mean": mean_acc,
        "std": std_acc,
        "min": min_acc,
        "max": max_acc,
        "q1": q1, "q2": q2, "q3": q3,
        "n_outliers": outliers,
        "n_samples": len(accuracies),
        "gate_passed": gate_passed,
        "gate_value": std_acc,
        "gate_threshold": 10.0
    }
```

### Training Protocol

**N/A** - This is an observational study analyzing existing data, not training a model.

**Analysis Protocol:**
1. Load Model Zoo accuracy labels
2. Run `validate_model_zoo_variance()` function
3. Generate distribution visualization
4. Report statistics and gate status

**Seeds:** 1 (deterministic analysis)

### Evaluation

**Primary Metrics:**
- σ(accuracy): Standard deviation of accuracy distribution
- Range: max(accuracy) - min(accuracy)

**Success Criteria:**
- σ(accuracy) > 10% (MUST_WORK gate)
- No systematic label errors (visual inspection)

**Expected Performance (from literature):**
- Model Zoos designed with diverse hyperparameters
- Expected σ range: 15-30% based on hyperparameter variation
- Source: Schurholt et al. 2022 methodology

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical analysis
- Library: numpy, scipy.stats
- Code:
```python
import numpy as np
from scipy import stats

# Primary metric
std_accuracy = np.std(accuracies)

# Secondary checks
shapiro_stat, shapiro_p = stats.shapiro(accuracies[:5000])  # Normality
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing σ(accuracy) vs 10% threshold

#### Additional Figures (LLM Autonomous)

1. **Accuracy Distribution Histogram**: Show full distribution with mean, std annotations
2. **Box Plot**: Visualize quartiles and outliers
3. **Per-Zoo Comparison** (if multiple zoos): Compare variance across different model populations

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. σ(accuracy) > 10% threshold met

**Mechanism Verification:**
- Pre-condition: Dataset loads with valid accuracy labels
- Activation Indicator: `gate_passed == True` in results
- Failure Detection: `std_acc <= 10.0` or loading errors

---

## Appendix: Reference Implementations

### A. Primary Sources

**Source 1:** Model Zoos Paper
- **Type:** Dataset paper (NeurIPS 2022)
- **URL:** https://arxiv.org/abs/2209.14764
- **Used For:** Dataset specifications, expected properties
- **Key Insight:** 50,360 models across 27 zoos with systematic hyperparameter variation

**Source 2:** Permutation Equivariant Neural Functionals
- **Type:** Method paper using model zoos
- **URL:** https://arxiv.org/abs/2302.14040
- **Used For:** Validation that accuracy prediction is viable downstream task
- **Key Insight:** Confirms model zoos have meaningful accuracy labels

### B. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset scale (50K models) | Paper | arxiv:2209.14764 |
| σ > 10% threshold | Phase 2B | 02b_verification_plan.md |
| Analysis methodology | Standard | numpy/scipy statistical analysis |
| Success criteria | Phase 2B | Gate condition |

### C. Previous Hypothesis Context

N/A - H-E1 is the root hypothesis.

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis

- Phase 2B: Hypothesis defined with MUST_WORK gate
- Phase 2C: Experiment design completed (this document)

---

*Research conducted via WebFetch (Archon/Exa MCP unavailable)*
*All specifications grounded in published research*
*Next Phase: Phase 3 - Implementation Planning*
