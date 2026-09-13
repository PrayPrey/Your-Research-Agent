# Experiment Design: H-M1

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under Small CNN Zoo scope, if we extract features from weight matrices, then these features will correlate with class-wise accuracy profiles
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 COMPLETED (residual_ratio=0.6758 > 0.05)
**Gate Status:** MUST_WORK - failure stops workflow

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (PASSED)

### Gate Condition
MUST_WORK gate: If weight features cannot predict class-wise accuracy better than stratified baseline, the core mechanism hypothesis fails and workflow stops.

---

## Continuation Context

Building on H-E1 success (residual_ratio = 0.6758), H-M1 tests whether weight matrices encode the observed behavioral variance. This is the first causal step: proving weights contain extractable behavioral information.

### Previous Hypothesis Results (if applicable)
- H-E1 validated behavioral variance exists in class-wise accuracy profiles
- Residual variance ratio: 67.58% (far exceeds 5% threshold)
- Different models show different per-class error patterns

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP unavailable - using Exa search results*

### Exa GitHub Implementations

**Primary Source: Unterthiner et al. 2020 - "Predicting Neural Network Accuracy from Weights"**
- Paper: https://arxiv.org/abs/2002.11448
- Code: https://github.com/google-research/google-research/tree/master/dnn_predict_accuracy
- Result: R² > 0.98 using simple weight statistics on Small CNN Zoo
- Method: Per-layer statistics (mean, std, min, max, norms) → GBM predictor

**Secondary Source: ModelZoos.cc (Schürholt et al. 2022)**
- Paper: NeurIPS 2022 Datasets & Benchmarks
- Data: https://doi.org/10.5281/zenodo.6620868 (CIFAR10 zoo)
- Benchmark: Layer-wise weight quintiles predict accuracy with high R² using linear models
- Format: Preprocessed .pt files with vectorized weights

**ProbeGen (ICLR 2025)**
- Deep Linear Probe Generators achieve Kendall's τ = 0.933 on CIFAR10-Wild-Park
- Shows probing approaches work well for weight-space learning

### Implementation Priority Assessment

**For H-M1 (Weight → Class-wise Accuracy), use Unterthiner et al. approach:**
- Their Small CNN Zoo already has per-model predictions stored
- Weight statistics method proven to work (R² > 0.98 for overall accuracy)
- Extend to CLASS-WISE accuracy (10 outputs instead of 1)

**Recommended Implementation Path:**
- Primary: Extract per-layer weight statistics, train Ridge regression to predict 10-class accuracy vector
- Fallback: Use raw flattened weights of last dense layer (shown effective in Unterthiner et al.)
- Justification: Simplest method that tests H-M1 core claim; matches literature baseline

### Code Analysis (Serena MCP)

*Serena analysis skipped - sufficient implementation details from Exa research*

---

## Experiment Specification

### Dataset

**Name:** Small CNN Zoo (CIFAR-10 subset)
**Type:** standard (model zoo)
**Source:** https://storage.cloud.google.com/gresearch/smallcnnzoo-dataset/cifar10.tar.xz
**Alternative:** https://doi.org/10.5281/zenodo.6620868 (ModelZoos.cc)

**Statistics:**
- ~30,000 unique CNN models trained on CIFAR-10
- 270,000 checkpoints (9 epochs × 30k models)
- Each model: 4,970 parameters (3 conv + 1 dense)
- Stored: flattened weights + metrics.csv with test_accuracy

**For H-M1:** Use final checkpoint (epoch 86) weights only
- Sample size: ~30,000 models (statistically meaningful)
- Split: 80% train / 20% test

**Loading Information** (for Phase 4 download):
- Method: Direct download + numpy
- Identifier: `gresearch/smallcnnzoo-dataset/cifar10.tar.xz`
- Code:
```python
import numpy as np
import pandas as pd

# Load weight matrix and metrics
weights = np.load("cifar10_weights.npy")  # (N, 4970)
metrics = pd.read_csv("metrics.csv.gz")

# Filter to final epoch only
final_epoch = metrics[metrics["step"] == 86]
weights_final = weights[final_epoch.index]
```

### Models

#### Baseline Model

**Stratified Baseline:** Predict class-wise accuracy from overall accuracy + per-class difficulty

**Architecture:** Linear regression with 2 features per class
- Feature 1: Overall test accuracy (same for all classes)
- Feature 2: Per-class baseline difficulty (mean class accuracy across all models)

**Rationale:** Tests H0 that class-wise accuracy is fully explained by overall accuracy + class difficulty

**Loading Information** (for Phase 4 download):
- Method: sklearn
- Identifier: `sklearn.linear_model.Ridge`
- Code:
```python
from sklearn.linear_model import Ridge

# Stratified baseline: predict class_acc[c] from (overall_acc, class_difficulty[c])
baseline = Ridge(alpha=1.0)
```

#### Proposed Model

**Architecture:** Linear probe on weight statistics → class-wise accuracy

**Core Mechanism Implementation:**

```python
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

def extract_weight_statistics(weights, layout):
    """
    Extract per-layer statistics from flattened weight vector.
    
    Args:
        weights: (N, 4970) - flattened weights for N models
        layout: dict mapping layer names to weight indices
    
    Returns:
        features: (N, num_features) - per-layer statistics
    """
    features = []
    for layer_name, (start, end) in layout.items():
        layer_weights = weights[:, start:end]
        # Per-layer statistics (Unterthiner et al. 2020)
        stats = [
            np.mean(layer_weights, axis=1),
            np.std(layer_weights, axis=1),
            np.min(layer_weights, axis=1),
            np.max(layer_weights, axis=1),
            np.linalg.norm(layer_weights, axis=1),
        ]
        features.extend(stats)
    return np.column_stack(features)

# Train linear probe for class-wise accuracy
class WeightToClassAccuracyProbe:
    def __init__(self, alpha=1.0):
        self.scaler = StandardScaler()
        self.probe = Ridge(alpha=alpha)
    
    def fit(self, weight_features, class_accuracies):
        # weight_features: (N, D), class_accuracies: (N, 10)
        X = self.scaler.fit_transform(weight_features)
        self.probe.fit(X, class_accuracies)
    
    def predict(self, weight_features):
        X = self.scaler.transform(weight_features)
        return self.probe.predict(X)
```

### Training Protocol

**Optimizer:** Closed-form (Ridge regression)
**Regularization:** alpha=1.0 (cross-validate if needed)
**Seeds:** 1 (fixed split)
**Cross-validation:** 5-fold for hyperparameter selection

**Data Split:**
- Train: 80% of models (~24,000)
- Test: 20% of models (~6,000)

### Evaluation

**Primary Metric:** R² (coefficient of determination) for class-wise accuracy prediction

**Success Criteria (PoC):**
- `proposed_R2 > baseline_R2` (weight features beat stratified baseline)

**Expected Baseline Performance:**
- Stratified baseline R²: ~0.7-0.8 (overall accuracy explains most variance)
- Proposed R²: >0.85 (per Unterthiner et al. overall accuracy R² > 0.98)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: regression (multi-output)
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import r2_score

# Per-class R² and mean R²
r2_per_class = [r2_score(y_true[:, c], y_pred[:, c]) for c in range(10)]
r2_mean = np.mean(r2_per_class)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Proposed R² vs Stratified Baseline R² bar chart (per-class + mean)

#### Additional Figures (LLM Autonomous)
- Scatter plot: predicted vs actual class-wise accuracy (sample of classes)
- Feature importance: which weight statistics contribute most
- Per-class R² comparison bar chart

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_R2 > baseline_R2` (weight features predict class-wise accuracy better than stratified baseline)

**Gate:** MUST_WORK - If this fails, weights do not encode behavioral information and NF-Layer hypothesis is undermined.

---

## Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: Weight statistics extraction function implemented
- `mechanism_isolatable`: Proposed model differs from baseline only in feature source
- `baseline_measurable`: Stratified baseline R² can be computed

### Architecture Compatibility
- Input: Flattened weight vectors (4970 dims)
- Output: 10-class accuracy predictions
- Compatible with any sklearn regressor

### Activation Indicators
- `mechanism_log_message`: "Extracted {N} features from {L} layers for {M} models"
- `tensor_shape_change`: weights (N, 4970) → features (N, ~20) → predictions (N, 10)
- `metric_delta_expected`: proposed_R2 - baseline_R2 > 0

### Verification Code
```python
# Verify mechanism is working
assert weight_features.shape[1] > 0, "No features extracted"
assert not np.isnan(weight_features).any(), "NaN in features"
assert proposed_r2 > baseline_r2, f"Gate FAILED: {proposed_r2:.4f} <= {baseline_r2:.4f}"
print(f"Gate PASSED: proposed_R2={proposed_r2:.4f} > baseline_R2={baseline_r2:.4f}")
```

### Success Threshold
- `hypothesis_support_metric`: mean R² across 10 classes
- `hypothesis_support_threshold`: proposed_R2 > baseline_R2

---

## Appendix: Reference Implementations

### Primary References

1. **Unterthiner et al. 2020** - "Predicting Neural Network Accuracy from Weights"
   - Paper: https://arxiv.org/abs/2002.11448
   - Code: https://github.com/google-research/google-research/tree/master/dnn_predict_accuracy
   - Key finding: R² > 0.98 using per-layer weight statistics

2. **Schürholt et al. 2022** - "Model Zoo Dataset"
   - Paper: NeurIPS 2022 Datasets and Benchmarks
   - Data: https://doi.org/10.5281/zenodo.6620868
   - Benchmark: Linear models on weight quintiles achieve high R²

3. **ProbeGen (ICLR 2025)** - "Deep Linear Probe Generators"
   - Paper: https://arxiv.org/abs/2410.10811
   - Method: Probing-based weight space learning
   - Result: Kendall's τ = 0.933 on CIFAR10-Wild-Park

### Code Snippets from Research

**Weight Statistics (Unterthiner et al.):**
- Per-layer: mean, std, min, max, range, norm
- Last dense layer weights most informative
- GBM achieves best results, but linear models work well

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19T01:55:23: H-M1 set to IN_PROGRESS (Phase 2C start)
- 2026-08-19: Experiment design completed with Level 1.5 specification

---

*MCP Tools Used: Exa (GitHub/Web search)*
*All specifications grounded in Unterthiner et al. 2020 and ModelZoos.cc research*
*Next Phase: Phase 3 - Implementation Planning*
