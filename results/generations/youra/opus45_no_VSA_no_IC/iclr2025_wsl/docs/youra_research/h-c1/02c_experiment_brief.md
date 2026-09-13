# Experiment Design: H-C1

**Date:** 2026-08-24
**Author:** PrayPrey
**Hypothesis Statement:** At N=5000, all three methods (Statistics/MLP/NFN) achieve R² within ±0.03 of each other
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **CONDITION Hypothesis** - Testing convergence behavior at large sample size.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M2 validated: NFN R²=0.9985 vs MLP R²=-1.50 at N=500)
**Gate Status:** SHOULD_WORK (failure does not block pipeline)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-C1
- **Type:** CONDITION
- **Prerequisites:** H-M2 (VALIDATED)

### Gate Condition
All three methods (Statistics, MLP, NFN) must achieve R² values within ±0.03 of each other at N=5000 training samples. This tests whether the data efficiency advantage of NFN diminishes as sample size increases.

---

## Continuation Context

### Previous Hypothesis Results (H-M2)
- NFN R² = 0.9985 at N=500 (highly effective)
- MLP R² = -1.50 at N=500 (complete failure)
- Delta = 2.50 >> threshold 0.1
- 10 seeds, p = 4.58e-06

**Implication for H-C1:** At N=5000, we expect:
- NFN: remains high (~0.99)
- MLP: should improve significantly with more data
- Statistics: stable baseline (~0.85-0.90)
- All three should converge within ±0.03 range

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Model zoo accuracy prediction convergence**
- Limited direct matches for NFN-specific convergence studies
- General ML finding: sample efficiency advantages diminish with large N

**Query 2: NFN equivariant neural network**
- References to LoRA, quantization approaches (tangential)
- No direct NFN convergence benchmarks in KB

### Archon Code Examples

- No NFN-specific code examples found
- General neural network patterns available

### Exa GitHub Implementations

**Repository 1**: AllanYangZhou/nfn (Official NFN Library)
- **URL**: https://github.com/AllanYangZhou/nfn
- **Relevance**: Official NeurIPS 2023 implementation - ground truth for NFN
- **Papers**: "Permutation Equivariant Neural Functionals" (arXiv:2302.14040)
- **Key Code**:
```python
from nfn import layers
from nfn.common import network_spec_from_wsfeat

network_spec = network_spec_from_wsfeat(wsfeat)
nfn = nn.Sequential(
    layers.NPLinear(network_spec, 1, nfn_channels, io_embed=True),
    layers.TupleOp(nn.ReLU()),
    layers.NPLinear(network_spec, nfn_channels, nfn_channels, io_embed=True),
    layers.TupleOp(nn.ReLU()),
    layers.HNPPool(network_spec),
    nn.Flatten(start_dim=-2),
    nn.Linear(nfn_channels * layers.HNPPool.get_num_outs(network_spec), 1)
)
```
- **Install**: `pip install nfn`

**Repository 2**: ModelZoos/ModelZooDataset
- **URL**: https://github.com/ModelZoos/ModelZooDataset
- **DOI**: https://doi.org/10.5281/zenodo.6974028 (CIFAR-10 ResNet-18 zoo)
- **Description**: 1000 ResNet-18 models trained on CIFAR-10 with diverse hyperparameters
- **Statistics**: 47,360+ models across 6 datasets, 70-95% accuracy range
- **Benchmark**: R² prediction benchmark included in paper

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Source | Status |
|----------|--------|--------|
| 1 (Highest) | AllanYangZhou/nfn | ✅ Available, pip installable |
| 2 | ModelZoos dataset | ✅ Available via Zenodo |
| 3 | Community reimplementations | Not needed |

**Recommended Implementation Path:**
- Primary: Official `nfn` library (pip install nfn)
- Fallback: None needed - official implementation is mature
- Justification: NeurIPS 2023 paper, actively maintained, examples included

### Code Analysis (Serena MCP)

*Skipped - Official nfn library is well-documented, <100 lines for core usage*

---

## Experiment Specification

### Dataset

**Dataset**: Model Zoo ResNet-20/CIFAR-10 (from H-E1/H-M2)
**Type**: standard (programmatic generation)

**Source**: Pre-trained ResNet-20 model weights
- Reuse model zoo from H-M2 validation
- Total models: 5500+ (5000 train, 500 test)
- Accuracy range: 70-95%
- Features: flattened weights/biases

**Loading Information** (for Phase 4 download):
- Method: Reuse from H-M2
- Identifier: `h-m2/data/model_zoo/`
- Code: 
```python
# Reuse existing model zoo from H-M2
train_data = torch.load("h-m2/data/model_zoo/train_N5000.pt")
test_data = torch.load("h-m2/data/model_zoo/test_500.pt")
```

**Preprocessing**:
- Weight flattening: layer-wise statistics (mean, std, min, max per layer)
- Normalization: StandardScaler fit on train set

### Models

#### Baseline Model

**Statistics Baseline** (from H-E1):
- Architecture: Linear regression on layer-wise weight statistics
- Features: [mean, std, min, max] × num_layers
- Expected R²: ~0.85-0.90 (stable across all N)

**MLP Baseline**:
- Architecture: 3-layer MLP (hidden: 256, 128)
- Input: Same statistics features
- Expected R² at N=5000: Should approach Statistics level

**Loading Information** (for Phase 4 download):
- Method: Custom implementation (reuse from H-M2)
- Identifier: `h-m2/code/models.py`
- Code:
```python
class StatisticsBaseline(nn.Module):
    def __init__(self, num_features):
        super().__init__()
        self.linear = nn.Linear(num_features, 1)

class MLPBaseline(nn.Module):
    def __init__(self, num_features):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(num_features, 256), nn.ReLU(),
            nn.Linear(256, 128), nn.ReLU(),
            nn.Linear(128, 1)
        )
```

#### Proposed Model

**Architecture:** NFN (Neural Functional Network) - same as H-M2

**Core Mechanism Implementation:**

```python
# Core Mechanism: NFN for weight space processing
# Based on: AllanYangZhou/nfn (NeurIPS 2023)

from nfn import layers
from nfn.common import network_spec_from_wsfeat, state_dict_to_tensors

class NFNAccuracyPredictor(nn.Module):
    """
    Permutation-equivariant accuracy prediction from model weights.
    At N=5000, expected to match Statistics/MLP (convergence).
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
    
    def forward(self, wsfeat):
        return self.nfn(wsfeat)

# Integration: Direct weight space input via WeightSpaceFeatures
```

### Training Protocol

**Reusing from H-M2 (controlled comparison):**

| Parameter | Value | Source |
|-----------|-------|--------|
| Optimizer | Adam | H-M2 validation |
| Learning Rate | 1e-3 | H-M2 optimal |
| Batch Size | 32 | H-M2 optimal |
| Epochs | 100 | H-M2 setting |
| Loss | MSE | Regression task |
| Seeds | 10 | Statistical power |

**Training Sizes**:
- N = 5000 (focus of this hypothesis)
- Test set: 500 models (fixed from H-M2)

### Evaluation

**Primary Metric**: R² (coefficient of determination)

**Success Criteria (CONDITION Gate - SHOULD_WORK)**:
- |R²_NFN - R²_Statistics| ≤ 0.03
- |R²_NFN - R²_MLP| ≤ 0.03
- |R²_Statistics - R²_MLP| ≤ 0.03

**Statistical Test**:
- 10 seeds per method
- Pairwise comparison of mean R²
- Success if ALL pairwise differences ≤ 0.03

**Expected Performance at N=5000**:
| Method | Expected R² | Rationale |
|--------|-------------|-----------|
| Statistics | 0.87 ± 0.02 | Stable baseline |
| MLP | 0.85 ± 0.03 | Improved with more data |
| NFN | 0.88 ± 0.02 | Still high but not dominant |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Regression
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import r2_score
r2 = r2_score(y_true, y_pred)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: R² bar chart for all three methods at N=5000 with error bars (10 seeds)

#### Additional Figures (LLM Autonomous)
- **Convergence Curve**: R² vs N for N ∈ {100, 250, 500, 1000, 2500, 5000} (if time permits)
- **Pairwise R² Difference**: Heatmap showing |R²_i - R²_j| for all method pairs

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-c1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists**: NFN architecture identical to H-M2
- **mechanism_isolatable**: Yes - compare NFN vs Statistics vs MLP directly
- **baseline_measurable**: Yes - Statistics provides stable reference

### Architecture Compatibility
- NFN processes ResNet-20 weight space (same as H-M2)
- WeightSpaceFeatures format unchanged
- All three methods trained on identical data splits

### Activation Indicators
- **mechanism_log_message**: "NFN forward pass completed, output shape: (B, 1)"
- **tensor_shape_change**: Input WeightSpaceFeatures → (B, 1) prediction
- **metric_delta_expected**: At N=5000, NFN R² should be within 0.03 of both baselines

### Failure Detection
- If any method R² < 0.5: Data/model loading issue
- If NFN still dominates by >0.1: Hypothesis not supported (ok for SHOULD_WORK)
- If MLP still fails (R² < 0): Training issue, not convergence

### Success Criteria
- **hypothesis_support_threshold**: 0.03 (max pairwise R² difference)
- **hypothesis_support_metric**: max(|R²_i - R²_j|) for all i,j pairs

---

## 🔬 PoC Success Check

**PoC Pass Condition (CONDITION type):**
1. Code runs without error for all three methods
2. All methods achieve R² > 0.5 (sanity check)
3. Pairwise R² differences measured across 10 seeds

**Gate Pass (SHOULD_WORK):**
- All pairwise |ΔR²| ≤ 0.03

---

## Appendix: Reference Implementations

### NFN (Neural Functional Networks)
- **Paper**: "Permutation Equivariant Neural Functionals" (NeurIPS 2023)
- **arXiv**: https://arxiv.org/abs/2302.14040
- **GitHub**: https://github.com/AllanYangZhou/nfn
- **Install**: `pip install nfn`

### Model Zoo Dataset
- **Paper**: "A Dataset of Diverse Populations of Neural Network Models"
- **Website**: www.modelzoos.cc
- **DOI (CIFAR-10 ResNet-18)**: https://doi.org/10.5281/zenodo.6974028
- **GitHub**: https://github.com/ModelZoos/ModelZooDataset

### Related Work
- MathematicalAI-NUS/Monomial-NFN (NeurIPS 2024)
- Fsoft-AIC/Transformer-NFN (ICLR 2025)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24T11:00:00Z

### Workflow History for This Hypothesis
- 2026-08-24: Phase 2C experiment design initiated
- Prerequisites: H-M2 validated (NFN >> MLP at N=500)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
