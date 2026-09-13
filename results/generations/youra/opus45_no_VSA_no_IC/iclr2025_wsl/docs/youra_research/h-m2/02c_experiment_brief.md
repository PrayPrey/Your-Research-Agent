# Experiment Design: H-M2

**Date:** 2026-08-24
**Author:** PrayPrey
**Hypothesis Statement:** At N=500 training models, NFN R² exceeds MLP R² by at least 0.1 (p < 0.05)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing NFN data efficiency advantage over MLP baseline.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 (NFN R²=0.9952, equivariance 100%)
**Gate Status:** MUST_WORK (NFN R² - MLP R² ≥ 0.1 at N=500)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (COMPLETED)

### Gate Condition
NFN R² exceeds MLP R² by at least 0.1 at N=500 training samples with statistical significance (p < 0.05).

---

## Continuation Context

Building on H-M1 validation:
- NFN architecture proven functional (R²=0.9952 on full dataset)
- Equivariance verified (100% pass rate)
- Training protocol established (converged by epoch 25)
- Now testing data efficiency hypothesis: does equivariance help at low N?

### Previous Hypothesis Results (H-M1)
- NFN achieves R²=0.9952 on 500 test models
- Statistics baseline R²=0.9996
- Stable training converged by epoch 25
- Optimal hyperparameters: Adam optimizer, lr=1e-3, batch_size=32

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "NFN MLP comparison data efficiency"**
- No direct matches in knowledge base
- General ML efficiency patterns found but not NFN-specific

**Query 2: "equivariant network sample efficiency"**
- Found consistency models reference (tangential)
- No direct NFN weight space learning content

**Insight:** Archon KB lacks NFN-specific content; relying on Exa GitHub for implementation details.

### Archon Code Examples

No direct NFN code examples found. MLP baseline patterns available from general PyTorch examples.

### Exa GitHub Implementations

**Repository 1**: AllanYangZhou/nfn (⭐ 93)
- **URL**: https://github.com/AllanYangZhou/nfn
- **Relevance**: Official NFN implementation from NeurIPS 2023 paper authors
- **License**: MIT
- **Paper**: "Permutation Equivariant Neural Functionals" (arXiv:2302.14040)
- **Key Code**:
  ```python
  from nfn import layers
  from nfn.common import network_spec_from_wsfeat
  
  network_spec = network_spec_from_wsfeat(wsfeat)
  nfn_channels = 32
  
  nfn = nn.Sequential(
      layers.NPLinear(network_spec, 1, nfn_channels, io_embed=True),
      layers.TupleOp(nn.ReLU()),
      layers.NPLinear(network_spec, nfn_channels, nfn_channels, io_embed=True),
      layers.TupleOp(nn.ReLU()),
      layers.HNPPool(network_spec),  # pooling layer for invariance
      nn.Flatten(start_dim=-2),
      nn.Linear(nfn_channels * layers.HNPPool.get_num_outs(network_spec), 1)
  )
  ```
- **Installation**: `pip install nfn` or editable install from repo
- **PyPI**: https://pypi.org/project/nfn/ (v0.1.2)

**Repository 2**: ModelZoos/ModelZooDataset
- **URL**: https://github.com/ModelZoos/ModelZooDataset
- **Relevance**: Model zoo dataset paper (NeurIPS 2022) with benchmark results
- **Key Finding**: Table 3 shows R² prediction from weights using linear models
- **Baseline**: Per-layer weight statistics s(w) achieve high R² for accuracy prediction

### 🎯 Implementation Priority Assessment

**CRITICAL: Using author's official NFN implementation**

| Priority | Source | Status |
|----------|--------|--------|
| 1. Author's Official | AllanYangZhou/nfn | ✅ Available (pip installable) |
| 2. Library Implementation | N/A | Not needed |
| 3. Community | N/A | Not needed |

**Recommended Implementation Path:**
- Primary: Official `nfn` library from PyPI (`pip install nfn`)
- Fallback: Clone from https://github.com/AllanYangZhou/nfn
- Justification: Authors' implementation guarantees correctness for paper reproduction

### Code Analysis (Serena MCP)

*Skipped* - Official NFN library is pip-installable with clear API documentation. No complex code analysis required.

---

## Experiment Specification

### Dataset

**Name:** Model Zoo ResNet-20/CIFAR-10 Weights
**Type:** programmatic-api (generated from training ResNet-20 models)
**Source:** H-M1 data pipeline (reuse existing model zoo)

**Statistics:**
- Total models: 5500+ (from H-M1)
- Training sizes to test: N ∈ {500} (primary), with comparison at {100, 250, 1000, 2500, 5000}
- Test set: 500 held-out models (fixed across all experiments)
- Features: Flattened ResNet-20 weights (~270K parameters per model)
- Labels: CIFAR-10 test accuracy (continuous, 0-1 range)

**Preprocessing:**
- Flatten all layer weights into single vector per model
- Normalize per-layer (mean=0, std=1)
- Same preprocessing as H-M1 for controlled comparison

**Loading Information** (for Phase 4 download):
- Method: programmatic-api (reuse from H-M1)
- Identifier: `h-m1/data/model_zoo_resnet20_cifar10.pt`
- Code:
  ```python
  # Load pre-generated model zoo from H-M1
  data = torch.load("h-m1/data/model_zoo_resnet20_cifar10.pt")
  weights = data["weights"]  # (N, D) tensor
  accuracies = data["accuracies"]  # (N,) tensor
  ```

### Models

#### Baseline Model

**Architecture:** MLP (Multi-Layer Perceptron)
**Purpose:** Non-equivariant baseline that must learn permutation invariance from data

**Configuration:**
- Input: Flattened ResNet-20 weights (~270K dims)
- Hidden layers: 2 layers, 256 units each
- Activation: ReLU
- Output: 1 (accuracy prediction)
- No weight sharing or equivariance constraints

**Loading Information** (for Phase 4 download):
- Method: custom PyTorch
- Identifier: N/A (built from scratch)
- Code:
  ```python
  class MLPBaseline(nn.Module):
      def __init__(self, input_dim, hidden_dim=256):
          super().__init__()
          self.net = nn.Sequential(
              nn.Linear(input_dim, hidden_dim),
              nn.ReLU(),
              nn.Linear(hidden_dim, hidden_dim),
              nn.ReLU(),
              nn.Linear(hidden_dim, 1)
          )
      
      def forward(self, x):
          return self.net(x)
  ```

#### Proposed Model

**Architecture:** NFN (Neural Functional Network) from H-M1 validation

**Core Mechanism Implementation:**

```python
# Core Mechanism: NFN for Weight Space Learning
# Based on: AllanYangZhou/nfn (NeurIPS 2023)

import torch.nn as nn
from nfn import layers
from nfn.common import network_spec_from_wsfeat

class NFNPredictor(nn.Module):
    """
    Permutation-equivariant neural functional network for
    predicting model accuracy from weights.
    
    Key advantage: Architectural equivariance eliminates need
    to learn permutation invariance from data.
    """
    def __init__(self, network_spec, nfn_channels=32):
        super().__init__()
        self.nfn = nn.Sequential(
            layers.NPLinear(network_spec, 1, nfn_channels, io_embed=True),
            layers.TupleOp(nn.ReLU()),
            layers.NPLinear(network_spec, nfn_channels, nfn_channels, io_embed=True),
            layers.TupleOp(nn.ReLU()),
            layers.HNPPool(network_spec),  # Invariant pooling
            nn.Flatten(start_dim=-2),
            nn.Linear(nfn_channels * layers.HNPPool.get_num_outs(network_spec), 1)
        )
    
    def forward(self, weight_space_features):
        """
        Args:
            weight_space_features: WeightSpaceFeature from nfn library
        Returns:
            (B, 1) accuracy predictions
        """
        return self.nfn(weight_space_features)

# Integration: Same training loop as MLP baseline
# Only model architecture differs
```

### Training Protocol

**Continuation from H-M1:** Using validated hyperparameters.

| Parameter | Value | Source |
|-----------|-------|--------|
| Optimizer | Adam | H-M1 optimal |
| Learning Rate | 1e-3 | H-M1 optimal |
| Batch Size | 32 | H-M1 optimal |
| Epochs | 50 | H-M1 (converged by 25) |
| Loss | MSE | Standard for regression |
| Seeds | 10 | Per 02b_verification_plan |

**Training Sizes for H-M2:**
- Primary: N=500 (hypothesis focus)
- Full sweep: N ∈ {100, 250, 500, 1000, 2500, 5000} for learning curves

**Per-Seed Protocol:**
1. Sample N models from training pool (with seed)
2. Train both NFN and MLP on same N samples
3. Evaluate both on fixed 500-model test set
4. Record R² for each

### Evaluation

**Primary Metrics:**
- R² (coefficient of determination) for accuracy prediction
- Computed on fixed 500-model test set

**Statistical Test (MECHANISM hypothesis):**
- Paired t-test across 10 seeds
- H₀: NFN R² - MLP R² = 0
- H₁: NFN R² - MLP R² > 0.1
- Significance level: α = 0.05

**Success Criteria:**
1. Mean(NFN R²) - Mean(MLP R²) ≥ 0.1 at N=500
2. p-value < 0.05 for paired t-test
3. Effect consistent across seeds (low variance)

**Expected Performance (from research):**
- NFN at N=500: R² ~ 0.85-0.95 (extrapolated from H-M1)
- MLP at N=500: R² ~ 0.70-0.80 (limited data, no equivariance)
- Delta: ~0.1-0.15 expected

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: regression
- Library: sklearn.metrics
- Code:
  ```python
  from sklearn.metrics import r2_score
  from scipy.stats import ttest_rel
  
  r2_nfn = r2_score(y_true, y_pred_nfn)
  r2_mlp = r2_score(y_true, y_pred_mlp)
  delta = r2_nfn - r2_mlp
  
  # Paired t-test across seeds
  t_stat, p_value = ttest_rel(r2_scores_nfn, r2_scores_mlp)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: NFN R² vs MLP R² bar chart with error bars (10 seeds)

#### Additional Figures (LLM Autonomous)
- Learning curve: R² vs N for both methods (N ∈ {100, 250, 500, 1000, 2500, 5000})
- Per-seed scatter: NFN R² vs MLP R² with identity line
- Box plot: R² distribution across seeds for N=500

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: True (NFN layers from official library)
- `mechanism_isolatable`: True (only model architecture differs between NFN and MLP)
- `baseline_measurable`: True (MLP R² serves as baseline)

### Architecture Compatibility
- NFN library supports ResNet-20 weight structure via WeightSpaceFeature
- Same input format as H-M1 (validated)

### Activation Indicators
- `mechanism_log_message`: "NFN forward pass completed with HNPPool invariant output"
- `tensor_shape_change`: Input (B, layers, weights) → Pool output (B, channels)
- `metric_delta_expected`: R² improvement of ≥0.1 at N=500

### Mechanism Verification Code
```python
def verify_mechanism(nfn_model, mlp_model, test_data):
    """Verify NFN mechanism provides data efficiency advantage."""
    # 1. Verify both models produce valid outputs
    assert nfn_model(test_data).shape == mlp_model(test_data).shape
    
    # 2. Verify NFN equivariance (from H-M1)
    # Already validated in H-M1, skip here
    
    # 3. Core check: NFN R² > MLP R² at low N
    r2_nfn = evaluate_r2(nfn_model, test_data)
    r2_mlp = evaluate_r2(mlp_model, test_data)
    
    mechanism_works = (r2_nfn - r2_mlp) >= 0.1
    return mechanism_works, r2_nfn, r2_mlp
```

### Success Threshold
- `hypothesis_support_metric`: R² delta (NFN - MLP)
- `hypothesis_support_threshold`: ≥ 0.1 with p < 0.05

---

## 🔬 PoC Success Check

**This is a MECHANISM hypothesis, not EXISTENCE. Full statistical testing applies.**

**Pass Condition:**
1. Code runs without error
2. NFN R² - MLP R² ≥ 0.1 at N=500
3. p-value < 0.05 (paired t-test across 10 seeds)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No directly relevant sources found. Archon KB lacks NFN/weight-space-learning content.

### B. GitHub Implementations (Exa)

**Repository 1**: AllanYangZhou/nfn (⭐ 93)
- **URL**: https://github.com/AllanYangZhou/nfn
- **Query Used**: "Allan Zhou Neural Functional Network NFN official implementation"
- **Relevance**: Official author implementation, pip installable
- **Used For**: NFN model architecture, core mechanism pseudo-code

**Repository 2**: ModelZoos/ModelZooDataset
- **URL**: https://github.com/ModelZoos/ModelZooDataset
- **Query Used**: "model zoo weight prediction accuracy"
- **Relevance**: Benchmark results for weight-space accuracy prediction
- **Used For**: Expected baseline performance, evaluation methodology

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - official NFN library is pip-installable with clear API.

### D. Previous Hypothesis Context

**Source**: H-M1 Validation Report
- **Reused Components**:
  - Dataset: Model Zoo ResNet-20/CIFAR-10 (proven stable)
  - Hyperparameters: Adam, lr=1e-3, batch=32 (optimal values)
  - NFN configuration: nfn_channels=32
- **Why Reused**: Enables controlled experiment (only training set size varies)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset | H-M1 | Previous hypothesis |
| NFN architecture | GitHub | AllanYangZhou/nfn |
| MLP baseline | Standard | PyTorch nn.Sequential |
| Training protocol | H-M1 | Optimal hyperparameters |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md |
| Statistical test | Phase 2B | Success criteria |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24

### Workflow History for This Hypothesis
- H-M1 completed: 2026-08-24T10:10:00Z (prerequisite satisfied)
- H-M2 experiment design: COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
