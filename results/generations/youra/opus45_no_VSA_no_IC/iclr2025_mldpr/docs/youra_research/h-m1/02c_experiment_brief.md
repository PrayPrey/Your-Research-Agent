# Experiment Design: H-M1

**Date:** 2026-08-24
**Author:** Anonymous
**Hypothesis Statement:** Benchmark Fingerprint Score (classifier confidence for true benchmark) correlates positively with cross-dataset performance gap (r>0.3, p<0.05)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Template** - Tests causal relationship between fingerprint strength and generalization gap.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 VALIDATED (99.51% accuracy, Cohen's d = 698.08)
**Gate Status:** SHOULD_WORK (correlation threshold: r > 0.3, p < 0.05)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition
SHOULD_WORK: Correlation r > 0.3 with p < 0.05 between Benchmark Fingerprint Score and cross-dataset performance gap.

---

## Continuation Context

### Previous Hypothesis Results (H-E1)

Building on validated H-E1:
- Linear probe achieved **99.51% accuracy** classifying benchmark origin
- Cohen's d = 698.08 (massive effect size)
- Shuffled baseline at 50.43% confirms methodology
- **Reuse:** Same 6 fine-tuned models (3 per benchmark), same feature extraction pipeline

**What H-M1 Adds:**
1. Extract classifier confidence scores (softmax probabilities) as Benchmark Fingerprint Score (BFS)
2. Measure cross-dataset generalization gap for each model
3. Compute Pearson correlation between BFS and Gap

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Correlation Analysis / Fingerprint Confidence**
- Limited direct results for this specific analysis pattern
- Found relevant probing methodology in nn-observability research
- Partial correlation techniques documented for controlling confounds

**Query 2: Cross-dataset Generalization**
- Transfer learning literature shows ID-OOD accuracy correlations
- Pearson correlation standard for measuring linear relationships
- Partial correlations control for confounding variables

### Archon Code Examples

- scipy.stats.pearsonr documented for correlation with p-value
- Linear probe training patterns well-established
- Confidence extraction via softmax on logits

### Exa GitHub Implementations

**Repository 1**: tmcarmichael/nn-observability
- **Relevance**: Probing for prediction confidence using linear classifiers
- **Key Pattern**: Partial Spearman correlation controlling for confidence
- **Insight**: Confidence controls absorb 60.3% of raw probe signal - important baseline

**Repository 2**: mmiao2/Verbal_Confidence_Mech_Interp
- **URL**: https://github.com/mmiao2/Verbal_Confidence_Mech_Interp
- **Relevance**: Probe training with R² evaluation, isotonic calibration
- **Code Pattern**:
```python
from sklearn.linear_model import Ridge
from sklearn.isotonic import IsotonicRegression
# Train probe, compute R² on validation
```

**Repository 3**: SciPy pearsonr
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html
- **Relevance**: Official scipy.stats.pearsonr implementation
- **Code**:
```python
from scipy.stats import pearsonr
r, p_value = pearsonr(fingerprint_scores, generalization_gaps)
```

**Repository 4**: arxiv 2107.04649 - Accuracy on the Line
- **Relevance**: ID-OOD correlation analysis methodology
- **Key Finding**: ID and OOD accuracies often linearly correlated
- **Insight**: Use partial correlations to control for in-domain performance

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a correlation analysis, not paper reproduction**

**Recommended Implementation Path:**
- Primary: scipy.stats.pearsonr for correlation with p-value
- Fallback: numpy.corrcoef + manual t-test
- Justification: Standard statistical method, no custom implementation needed

### Code Analysis (Serena MCP)

*Skipped - no complex codebase to analyze. Standard scipy/sklearn patterns.*

---

## Experiment Specification

### Dataset

**Primary Dataset (In-Domain):** Same as H-E1
- Flowers102 (102 classes, 8,189 images)
- CIFAR-100 (100 classes, 60,000 images)

**Cross-Dataset Evaluation:**
- NABirds (555 classes, 48,562 images) - fine-grained bird classification

**Type:** standard (torchvision + custom NABirds loader)

**Loading Information** (for Phase 4 download):
- Method: torchvision + HuggingFace
- Identifier: `torchvision.datasets.Flowers102`, `torchvision.datasets.CIFAR100`
- Code:
```python
from torchvision.datasets import Flowers102, CIFAR100
from datasets import load_dataset

# In-domain datasets
flowers = Flowers102(root='./data', split='test', download=True)
cifar100 = CIFAR100(root='./data', train=False, download=True)

# Cross-dataset (NABirds)
nabirds = load_dataset("nabirds", split="test")
```

### Models

#### Baseline Model

**Architecture:** ResNet-50 (pretrained ImageNet-1K)
**Configuration:** From H-E1 - 6 fine-tuned models (3 seeds × 2 benchmarks)

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)`
- Code:
```python
import torchvision.models as models
model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
```

**Reuse from H-E1:**
- 6 fine-tuned checkpoints: `h-e1/code/models/finetuned/*.pt`
- Same feature extraction pipeline (2048-d avgpool)

#### Proposed Model

**Architecture:** Linear Fingerprint Classifier (from H-E1) + Gap Computation

**Core Mechanism Implementation:**

```python
# Core Mechanism: BFS-Gap Correlation Analysis
# Based on: scipy.stats.pearsonr, H-E1 fingerprint classifier

import torch
import numpy as np
from scipy.stats import pearsonr
from sklearn.linear_model import LogisticRegression

class BFSGapCorrelation:
    """
    Compute correlation between Benchmark Fingerprint Score (BFS)
    and cross-dataset generalization gap.
    """
    
    def __init__(self, fingerprint_classifier: LogisticRegression):
        self.classifier = fingerprint_classifier
    
    def compute_bfs(self, features: np.ndarray, true_benchmark: int) -> float:
        """
        BFS = classifier confidence (softmax probability) for true benchmark.
        
        Args:
            features: (N, 2048) - pooled features from model
            true_benchmark: int - index of true fine-tuning benchmark
        Returns:
            float - mean confidence score for true benchmark
        """
        probs = self.classifier.predict_proba(features)  # (N, num_benchmarks)
        bfs = probs[:, true_benchmark].mean()  # confidence for true class
        return bfs
    
    def compute_gap(self, in_domain_acc: float, cross_dataset_acc: float) -> float:
        """
        Gap = in-domain accuracy - cross-dataset accuracy
        
        Args:
            in_domain_acc: accuracy on fine-tuning benchmark test set
            cross_dataset_acc: accuracy on NABirds
        Returns:
            float - generalization gap (positive = worse OOD)
        """
        return in_domain_acc - cross_dataset_acc
    
    def compute_correlation(self, 
                            bfs_scores: np.ndarray, 
                            gaps: np.ndarray) -> tuple:
        """
        Pearson correlation between BFS and Gap.
        
        Args:
            bfs_scores: (n_models,) - BFS for each model
            gaps: (n_models,) - gap for each model
        Returns:
            (r, p_value) - Pearson r and two-sided p-value
        """
        r, p = pearsonr(bfs_scores, gaps)
        return r, p

# Usage in experiment:
# for each of 6 models:
#   bfs = compute_bfs(model_features, model_benchmark_idx)
#   gap = compute_gap(indomain_acc, nabirds_acc)
# r, p = compute_correlation(all_bfs, all_gaps)
```

### Training Protocol

**No training required** - H-M1 is a correlation analysis using:
1. Pre-trained fingerprint classifier from H-E1
2. Pre-trained fine-tuned models from H-E1

**Evaluation-only protocol:**
- Load 6 fine-tuned models from H-E1
- Load fingerprint classifier from H-E1
- For each model: compute BFS and cross-dataset gap
- Compute Pearson correlation

**Seeds:** Inherited from H-E1 (3 seeds × 2 benchmarks = 6 models)

### Evaluation

**Primary Metrics:**
1. **Pearson r:** Correlation coefficient between BFS and Gap
2. **p-value:** Two-sided significance test

**Secondary Metrics:**
1. **Per-model BFS:** Classifier confidence for true benchmark
2. **Per-model Gap:** In-domain accuracy - NABirds accuracy
3. **Scatter plot:** BFS vs Gap with regression line

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: correlation analysis
- Library: scipy.stats
- Code:
```python
from scipy.stats import pearsonr
r, p_value = pearsonr(bfs_scores, gaps)
```

**Success Criteria:**
- r > 0.3 (moderate positive correlation)
- p < 0.05 (statistically significant)

**Falsification Criteria:**
- r ≤ 0 (no positive correlation)
- OR p > 0.1 (not significant)

### Visualization Requirements

#### Required Figure (Mandatory)
- **BFS vs Gap Scatter Plot**: X-axis = BFS, Y-axis = Gap, with regression line and r/p annotation

#### Additional Figures (LLM Autonomous)
- Per-benchmark breakdown of BFS and Gap
- Confidence interval visualization for correlation

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: TRUE - BFS (classifier confidence) computable from H-E1 classifier
- `mechanism_isolatable`: TRUE - Gap = in-domain acc - cross-dataset acc
- `baseline_measurable`: TRUE - Shuffled/random BFS as null baseline

### Architecture Compatibility
- H-E1 fingerprint classifier outputs probabilities for each benchmark
- Fine-tuned models have standard classification head for both in-domain and cross-dataset evaluation
- NABirds evaluation requires replacing classification head (555 classes)

### Activation Indicators
- `mechanism_log_message`: "BFS computed for model {model_id}: {bfs_value:.4f}"
- `tensor_shape_change`: Features (N, 2048) → Probabilities (N, 2) → BFS (scalar)
- `metric_delta_expected`: Positive correlation r > 0.3

### Mechanism Verification Code
```python
def verify_mechanism(bfs_scores, gaps):
    """Verify BFS-Gap correlation mechanism is active."""
    # Check 1: BFS values in valid range [0, 1]
    assert np.all(bfs_scores >= 0) and np.all(bfs_scores <= 1), "BFS out of range"
    
    # Check 2: Gaps are reasonable (not NaN, within [-1, 1])
    assert not np.any(np.isnan(gaps)), "NaN in gaps"
    assert np.all(np.abs(gaps) <= 1), "Gap out of range"
    
    # Check 3: Sufficient sample size for correlation
    n = len(bfs_scores)
    assert n >= 6, f"Need at least 6 models, got {n}"
    
    # Check 4: Variance exists (correlation meaningless with constant values)
    assert np.std(bfs_scores) > 0.01, "BFS has no variance"
    assert np.std(gaps) > 0.01, "Gap has no variance"
    
    print(f"✅ Mechanism verification passed: n={n}, BFS std={np.std(bfs_scores):.4f}, Gap std={np.std(gaps):.4f}")
    return True
```

### Hypothesis Support Criteria
- `hypothesis_support_metric`: Pearson r
- `hypothesis_support_threshold`: r > 0.3 AND p < 0.05

---

## 🔬 PoC Success Check

**MECHANISM Pass Condition:**
1. Code runs without error
2. n ≥ 6 models evaluated
3. r > 0.3 (positive correlation)
4. p < 0.05 (significant)

---

## Appendix: Reference Implementations

### Primary References

1. **scipy.stats.pearsonr**
   - URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html
   - Usage: `r, p = pearsonr(x, y)`

2. **Accuracy on the Line (Miller et al., 2021)**
   - URL: https://arxiv.org/abs/2107.04649
   - Key insight: ID-OOD correlations, partial correlation methodology

3. **H-E1 Validated Results**
   - 99.51% fingerprint classification accuracy
   - Shuffled baseline 50.43%
   - 6 fine-tuned models available

### Code Snippets

**Fingerprint Score Extraction:**
```python
# Load H-E1 classifier
classifier = joblib.load("h-e1/code/models/fingerprint_classifier.pkl")

# Extract BFS for a model
features = extract_features(model, dataset)  # (N, 2048)
probs = classifier.predict_proba(features)   # (N, 2)
bfs = probs[:, true_benchmark].mean()        # scalar
```

**Cross-Dataset Evaluation:**
```python
# Evaluate on NABirds
# Replace classification head for 555 classes
model.fc = nn.Linear(2048, 555)
model.fc.load_state_dict(...)  # Or train linear probe
nabirds_acc = evaluate(model, nabirds_loader)
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24

### Workflow History for This Hypothesis
- Phase 2C experiment design: IN_PROGRESS → COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
