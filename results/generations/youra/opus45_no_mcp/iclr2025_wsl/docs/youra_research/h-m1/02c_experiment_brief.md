# Experiment Design: H-M1

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under Model Zoo benchmark, if we compare Layer-wise encoding vs Flatten+MLP, then Pearson correlation improves by Δr > 0.1, because per-layer statistics capture layer-specific functional patterns.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing causal chain step 1.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 PASS)
**Gate Status:** MUST_WORK - Δr > 0.1

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED, PASS)

### Gate Condition
Layer-wise Pearson r > Flatten+MLP Pearson r + 0.1 with p < 0.05 across 5 random seeds.

---

## Continuation Context

This is the first mechanism hypothesis in the causal chain. H-E1 validated the Model Zoo dataset with σ(accuracy) = 15.62%, confirming meaningful accuracy variance exists for prediction tasks.

### Previous Hypothesis Results (H-E1)
- **Gate:** PASS
- **σ(accuracy):** 15.62% > 10% threshold
- **N samples:** 61,335 models
- **Proven:** Data loading from Zenodo, dataset format, train/val/test splits

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable - using established literature:*

1. **Hyper-Representations (Schurholt et al. 2022)**
   - Layer-wise processing preserves per-layer weight statistics
   - Mean/std aggregation across layer dimensions
   - Demonstrated on Model Zoo for property prediction

2. **StatNN Baseline**
   - Flatten all weights → single vector → MLP
   - Simple but loses structural information
   - Common baseline in weight analysis literature

### Archon Code Examples

*MCP unavailable - using reference implementations:*

```python
# From Hyper-Representations codebase
# Layer-wise encoding pattern
def encode_layer_wise(weights_dict):
    layer_features = []
    for name, param in weights_dict.items():
        stats = compute_layer_stats(param)  # mean, std, etc.
        layer_features.append(stats)
    return aggregate(layer_features)  # mean pooling
```

### Exa GitHub Implementations

*MCP unavailable - using known repositories:*

1. **HSG-AIML/model-zoos** (github.com/HSG-AIML/model-zoos)
   - Official Model Zoo dataset repository
   - Data loading utilities

2. **HSG-AIML/hyper-representations** (github.com/HSG-AIML/hyper-representations)
   - Reference VAE encoder for weight embeddings
   - Layer-wise processing patterns

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

Since H-M1 tests a simpler baseline comparison (Flatten+MLP vs Layer-wise), custom implementation is appropriate. The comparison methods are straightforward.

**Recommended Implementation Path:**
- Primary: Custom implementation following Hyper-Representations patterns
- Fallback: Adapt from HSG-AIML/hyper-representations encoder
- Justification: Methods are simple enough for clean implementation; ensures fair comparison

### Code Analysis (Serena MCP)

*MCP unavailable - structural analysis based on H-E1 code:*

From H-E1 validation:
- Data format: PyTorch state_dict with 'weights' and 'accuracy' keys
- Architecture: Small CNNs with varying hyperparameters
- Layers: conv1, conv2, fc1, fc2 typical structure

---

## Experiment Specification

### Dataset

**Name:** CIFAR-10 Model Zoo (Small)
**Type:** standard
**Source:** Schurholt et al. 2022 (NeurIPS)
**DOI:** 10.5281/zenodo.6620869

| Split | Count |
|-------|-------|
| Train | 42,650 |
| Val | 9,340 |
| Test | 9,345 |
| **Total** | **61,335** |

**Task:** Predict model accuracy from weight embeddings
**Labels:** Ground-truth test accuracy (continuous, 7.33% - 56.83%)

**Loading Information** (for Phase 4 download):
- Method: Zenodo download with caching
- Identifier: 10.5281/zenodo.6620869
- Code:
```python
from zenodo_get import zenodo_get
zenodo_get(["-d", "10.5281/zenodo.6620869", "-o", "data/"])
# Load: torch.load("data/dataset_cifar_small_hyp_fix.pt")
```

### Models

#### Baseline Model

**Name:** Flatten+MLP
**Architecture:** Flatten all weights → Linear → ReLU → Linear → Output

**Description:**
1. Extract all parameters from model state_dict
2. Flatten each parameter tensor
3. Concatenate into single vector
4. Pass through 2-layer MLP regressor

**Loading Information** (for Phase 4 download):
- Method: Custom implementation (no pretrained weights)
- Identifier: N/A
- Code:
```python
class FlattenMLPEncoder(nn.Module):
    def __init__(self, input_dim, hidden_dim=256, embed_dim=128):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, embed_dim)
    
    def forward(self, weights_flat):
        x = F.relu(self.fc1(weights_flat))
        return self.fc2(x)
```

#### Proposed Model

**Name:** Layer-wise Encoder
**Architecture:** Per-layer statistics → Concatenate → MLP → Output

**Core Mechanism Implementation:**

```python
class LayerWiseEncoder(nn.Module):
    """
    Layer-wise encoding: compute statistics per layer, then aggregate.
    Preserves structural information that flatten destroys.
    """
    def __init__(self, num_layers, stats_per_layer=4, hidden_dim=256, embed_dim=128):
        super().__init__()
        # stats_per_layer: mean, std, min, max per layer
        input_dim = num_layers * stats_per_layer
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, embed_dim)
    
    def compute_layer_stats(self, param):
        """Compute statistics for a single layer's parameters."""
        flat = param.flatten().float()
        return torch.stack([
            flat.mean(),
            flat.std(),
            flat.min(),
            flat.max()
        ])
    
    def forward(self, weights_dict):
        """
        Args:
            weights_dict: dict of layer_name -> parameter tensor
        Returns:
            embedding: [batch, embed_dim]
        """
        layer_stats = []
        for name in sorted(weights_dict.keys()):  # consistent ordering
            stats = self.compute_layer_stats(weights_dict[name])
            layer_stats.append(stats)
        
        # Concatenate all layer statistics
        x = torch.cat(layer_stats, dim=-1)
        
        # MLP projection
        x = F.relu(self.fc1(x))
        return self.fc2(x)


class AccuracyPredictor(nn.Module):
    """Regressor head for accuracy prediction."""
    def __init__(self, embed_dim=128, hidden_dim=64):
        super().__init__()
        self.fc1 = nn.Linear(embed_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, 1)
    
    def forward(self, embedding):
        x = F.relu(self.fc1(embedding))
        return self.fc2(x).squeeze(-1)
```

### Training Protocol

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Optimizer | AdamW | Standard for regression tasks |
| Learning Rate | 1e-3 | Conservative starting point |
| LR Schedule | ReduceLROnPlateau (factor=0.5, patience=5) | Adaptive to convergence |
| Batch Size | 256 | Balance memory/speed |
| Epochs | 50 | Early stopping based on val loss |
| Loss | MSE | Standard for regression |
| Regularization | Weight decay 1e-4 | Prevent overfitting |
| Random Seeds | 5 (0, 1, 2, 3, 4) | Statistical significance |
| Early Stopping | Patience 10 on val loss | Prevent overfitting |

**Training Procedure:**
1. For each seed (0-4):
   - Initialize encoder + regressor with seed
   - Train on train split (42,650 models)
   - Validate on val split (9,340 models)
   - Select best checkpoint by val MSE
   - Evaluate on test split (9,345 models)
   - Record Pearson r on test set

2. Compare:
   - Flatten+MLP: 5 × test Pearson r
   - Layer-wise: 5 × test Pearson r

3. Statistical test:
   - Paired t-test on 5 seed results
   - Report mean Δr and p-value

### Evaluation

**Primary Metric:** Pearson correlation coefficient (r)
**Task:** Regression (predict continuous accuracy)

| Metric | Formula | Target |
|--------|---------|--------|
| Pearson r | correlation(predicted, actual) | Higher is better |
| Δr | Layer-wise r - Flatten+MLP r | > 0.1 |
| p-value | Paired t-test across seeds | < 0.05 |

**Success Criteria:**
- Primary: Δr > 0.1 with p < 0.05
- Secondary: Consistent improvement across all 5 seeds

**Failure Response:**
- IF fails: PIVOT to alternative layer aggregation strategies (attention, learned pooling)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Regression
- Library: scipy.stats.pearsonr, scipy.stats.ttest_rel
- Code:
```python
from scipy.stats import pearsonr, ttest_rel

def evaluate(predictions, targets):
    r, p = pearsonr(predictions, targets)
    return {'pearson_r': r, 'p_value': p}

def compare_methods(flatten_results, layerwise_results):
    t_stat, p_val = ttest_rel(layerwise_results, flatten_results)
    delta_r = np.mean(layerwise_results) - np.mean(flatten_results)
    return {'delta_r': delta_r, 't_stat': t_stat, 'p_value': p_val}
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing Flatten+MLP r vs Layer-wise r with error bars (std across seeds)

#### Additional Figures (LLM Autonomous)

1. **Correlation Scatter**: Predicted vs actual accuracy for both methods
2. **Per-Seed Results**: Line plot showing r values across 5 seeds for both methods
3. **Loss Curves**: Training/validation loss over epochs

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Both methods produce valid Pearson r values
3. Δr = Layer-wise r - Flatten+MLP r > 0.1
4. p-value < 0.05 (paired t-test across seeds)

---

## Appendix: Reference Implementations

### A. Data Loading (from H-E1)

```python
# Reuse from h-e1/code/data.py
import torch
from pathlib import Path

def load_model_zoo(data_path="data/dataset_cifar_small_hyp_fix.pt"):
    """Load Model Zoo dataset."""
    data = torch.load(data_path)
    return data['train'], data['val'], data['test']

def extract_weights_and_accuracy(sample):
    """Extract weights dict and accuracy from sample."""
    weights = sample['weights']  # dict of layer_name -> tensor
    accuracy = sample['accuracy']  # float
    return weights, accuracy
```

### B. Flatten Encoding

```python
def flatten_weights(weights_dict):
    """Flatten all weights into single vector."""
    flat_parts = []
    for name in sorted(weights_dict.keys()):
        flat_parts.append(weights_dict[name].flatten())
    return torch.cat(flat_parts)
```

### C. Layer-wise Encoding

```python
def layer_wise_stats(weights_dict, stats=['mean', 'std', 'min', 'max']):
    """Compute per-layer statistics."""
    all_stats = []
    for name in sorted(weights_dict.keys()):
        param = weights_dict[name].flatten().float()
        layer_stats = []
        if 'mean' in stats: layer_stats.append(param.mean())
        if 'std' in stats: layer_stats.append(param.std())
        if 'min' in stats: layer_stats.append(param.min())
        if 'max' in stats: layer_stats.append(param.max())
        all_stats.extend(layer_stats)
    return torch.tensor(all_stats)
```

### D. External References

1. **Model Zoos Paper:** Schurholt et al. "Model Zoos: A Dataset of Diverse Populations of Neural Network Weights" NeurIPS 2022
2. **Hyper-Representations:** Schurholt et al. "Hyper-Representations as Generative Models" ICML 2022
3. **Zenodo DOI:** 10.5281/zenodo.6620869

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19: H-M1 set to IN_PROGRESS (Phase 2C start)
- 2026-08-19: H-E1 prerequisite verified PASS (σ=15.62%)
- 2026-08-19: Experiment brief generated

---

*MCP Tools Used: None (no-mcp mode)*
*All specifications grounded in Phase 2B roadmap and H-E1 validation*
*Next Phase: Phase 3 - Implementation Planning*
