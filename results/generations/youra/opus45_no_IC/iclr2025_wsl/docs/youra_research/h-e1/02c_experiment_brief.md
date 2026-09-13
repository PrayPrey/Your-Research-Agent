# Experiment Design: H-E1

**Date:** 2026-08-12
**Author:** Anonymous
**Hypothesis Statement:** At N=1K, NFN R² > MLP-Matched R² + 0.05 (p<0.05)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 has no prerequisites)
**Gate Status:** MUST_WORK - Failure stops entire workflow

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
At N=1K models, NFN must demonstrate R² > MLP-Matched R² + 0.05 with p < 0.05. Failure abandons the main hypothesis that equivariance provides sample efficiency benefits.

---

## Continuation Context

*Not applicable - H-E1 is the first hypothesis in the verification chain.*

### Previous Hypothesis Results (if applicable)
*None - H-E1 is the foundation hypothesis.*

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: NFN neural functional network weight space**
- No direct NFN documentation in Archon KB
- General PyTorch model tracing and training loop patterns found
- Insight: NFN is a specialized architecture not covered in general KB

**Query 2: permutation equivariance model zoo experiment**
- No direct matches for permutation equivariance experiments
- Related: DreamBooth, consistency models (different domain)
- Insight: This is novel research area, rely on Exa for implementations

**Query 3: weight space learning R2 regression**
- General PyTorch training patterns available
- Regression training loop structure documented
- Insight: Standard PyTorch patterns apply to NFN training

### Archon Code Examples

**Query: NFN equivariant PyTorch**
- Generic PyTorch model code found
- Training loop pattern: blend, compute loss, backward, step
- Insight: Standard training applies; NFN-specific code from Exa

### Exa GitHub Implementations

**Query 1: AllanYangZhou NFN Implementation**

**Repository**: AllanYangZhou/nfn (⭐93)
- **URL**: https://github.com/AllanYangZhou/nfn
- **Relevance**: Official NFN implementation by paper authors (Zhou et al., NeurIPS 2023)
- **Architecture**: Permutation equivariant neural functional network layers
- **Key Code**:
  ```python
  from nfn import layers
  from nfn.common import network_spec_from_wsfeat, state_dict_to_tensors
  
  # Build NFN
  nfn = nn.Sequential(
      layers.NPLinear(network_spec, 1, nfn_channels, io_embed=True),
      layers.TupleOp(nn.ReLU()),
      layers.NPLinear(network_spec, nfn_channels, nfn_channels, io_embed=True),
      layers.TupleOp(nn.ReLU()),
      layers.HNPPool(network_spec),  # pooling for invariance
      nn.Flatten(start_dim=-2),
      nn.Linear(nfn_channels * layers.HNPPool.get_num_outs(network_spec), 1)
  )
  ```
- **Training Config**: Not specified in library; user-defined
- **Dataset**: Compatible with MLP and CNN weight spaces
- **Installation**: `pip install nfn`

**Query 2: Model Zoo Dataset**

**Repository**: ModelZoos/ModelZooDataset (⭐60)
- **URL**: https://github.com/ModelZoos/ModelZooDataset
- **Relevance**: NeurIPS 2022 Dataset & Benchmark track - populations of neural network models
- **Content**: Diverse populations of trained neural networks with weights and metadata
- **Available Zoos**: CIFAR-10, SVHN, ResNet-18 populations
- **Zenodo**: https://zenodo.org/records/6974029 (ResNet-18 CIFAR-10 subset)
- **Paper**: arXiv:2209.14764

**Serena Analysis Needed**: false (NFN code is clear and well-documented)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Source | Status |
|----------|--------|--------|
| ⭐⭐⭐ HIGHEST | AllanYangZhou/nfn (official) | ✅ Available |
| ⭐⭐ MEDIUM | Community reimplementations | Not needed |
| ⭐ LOW | From-scratch implementation | Not needed |

**Recommended Implementation Path:**
- Primary: `pip install nfn` (official package by Allan Zhou)
- Fallback: Clone https://github.com/AllanYangZhou/nfn for editable install
- Justification: Official implementation guarantees correct equivariance properties; maintained package with clear API

### Code Analysis (Serena MCP)

*Skipped* - NFN code from Exa search is sufficiently clear. The official implementation has:
- Clear module structure (nfn.layers, nfn.common)
- Well-documented API for WeightSpaceFeatures
- Example code in examples/basic_cnn/
- NPLinear, HNPPool layers with documented behavior

---

## Experiment Specification

### Dataset

**Name:** Model Zoo CIFAR-10 CNN Subset
**Type:** standard
**Source:** github.com/ModelZoos/ModelZooDataset / Zenodo

**Statistics:**
- Total models: ~50K+ across all zoos
- Target subset: N=1K single-architecture CNNs for H-E1
- Features: Model weights + accuracy labels
- Splits: 80% train / 20% test (fixed)

**Preprocessing:**
- Extract single architecture family (e.g., ResNet-18 or simple CNN)
- Filter for strict layer shape homogeneity
- Normalize weights per-layer (zero mean, unit variance recommended)
- Verify accuracy labels span 10%-90% range

**Loading Information** (for Phase 4 download):
- Method: Custom download + extraction
- Identifier: zenodo.org/records/6974029 (ResNet-18) OR ModelZoos/ModelZooDataset
- Code:
  ```python
  # Option 1: Zenodo direct download
  import requests, zipfile
  url = "https://zenodo.org/records/6974029/files/model_zoo_cifar10_resnet18.zip"
  
  # Option 2: GitHub repo scripts
  git clone https://github.com/ModelZoos/ModelZooDataset
  # Follow repo instructions for specific zoo download
  ```

### Models

#### Baseline Model

**Architecture:** MLP-Matched
**Type:** Standard feedforward MLP with matched parameter count to NFN
**Purpose:** Non-equivariant baseline for fair comparison

**Configuration:**
- Input: Flattened CNN weights (all layers concatenated)
- Hidden layers: 2-3 layers with ReLU activation
- Output: Single regression value (predicted accuracy)
- Parameter count: Matched to NFN for fair comparison

**Loading Information** (for Phase 4 download):
- Method: Custom implementation (no pretrained)
- Identifier: Custom MLP architecture
- Code:
  ```python
  class MLPMatched(nn.Module):
      def __init__(self, input_dim, hidden_dim=256, num_layers=3):
          super().__init__()
          layers = [nn.Linear(input_dim, hidden_dim), nn.ReLU()]
          for _ in range(num_layers - 2):
              layers.extend([nn.Linear(hidden_dim, hidden_dim), nn.ReLU()])
          layers.append(nn.Linear(hidden_dim, 1))
          self.net = nn.Sequential(*layers)
      
      def forward(self, x):
          return self.net(x.flatten(start_dim=1))
  ```

#### Proposed Model

**Architecture:** NFN (Neural Functional Network)

**Core Mechanism Implementation:**

```python
# Core Mechanism: NFN for Weight Space Learning
# Based on: AllanYangZhou/nfn (Zhou et al., NeurIPS 2023)

from nfn import layers
from nfn.common import network_spec_from_wsfeat, state_dict_to_tensors, WeightSpaceFeatures
from torch.utils.data.dataloader import default_collate

class NFNRegressor(nn.Module):
    """
    Permutation-equivariant NFN for predicting model accuracy from weights.
    Exploits neuron ordering symmetry via equivariant NF-Layers.
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
        """
        Input: WeightSpaceFeatures from batch of CNN state_dicts
        Output: (B, 1) predicted accuracy
        """
        return self.nfn(wsfeat)

# Data preparation
def prepare_batch(models):
    state_dicts = [m.state_dict() for m in models]
    wts_and_bs = [state_dict_to_tensors(sd) for sd in state_dicts]
    wts_and_bs = default_collate(wts_and_bs)
    return WeightSpaceFeatures(*wts_and_bs)
```

### Training Protocol

**Optimizer:** AdamW
- Parameters: lr=1e-3, weight_decay=1e-4
- **Source:** Common for regression tasks; NFN repo examples

**Learning Rate:** 1e-3
- **Source:** Standard starting point for Adam variants

**Schedule:** Cosine annealing
- Parameters: T_max=epochs, eta_min=1e-6
- **Source:** verification_state.yaml experimental context

**Batch Size:** 32
- **Source:** Standard for weight-space learning (memory permitting)

**Epochs:** 50
- **Source:** verification_state.yaml experimental context

**Loss Function:** MSE (Mean Squared Error)
- **Source:** Standard for regression tasks

**Seeds:** 1 (fixed for PoC)

> ⚠️ **EXISTENCE (PoC)**: Single seed sufficient. Full study uses 10 seeds.

### Evaluation

**Primary Metrics:**
- **R² (Coefficient of Determination):** Measures variance explained in accuracy prediction
  - Formula: 1 - (SS_res / SS_tot)
  - Range: 0 to 1 (higher is better)

**Success Criteria (PoC):**
1. Code runs without error
2. NFN R² > MLP-Matched R² (effect direction)
3. Difference > 0.05 (magnitude threshold from hypothesis)

**Expected Baseline Performance** (from research):
- MLP-Matched: R² ~ 0.3-0.5 (estimated for N=1K)
- NFN: R² ~ 0.5-0.7 (expected from equivariance benefit)
- **Source:** Hypothesis prediction; to be validated

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: regression
- Library: torchmetrics or sklearn.metrics
- Code:
  ```python
  from sklearn.metrics import r2_score
  # OR
  from torchmetrics import R2Score
  r2 = R2Score()
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: NFN R² vs MLP-Matched R² bar chart with 0.05 threshold line

#### Additional Figures (LLM Autonomous)

Based on EXISTENCE hypothesis type:
1. **Scatter Plot**: Predicted vs actual accuracy for both models
2. **Residual Plot**: Prediction errors distribution
3. **Learning Curves**: Training/validation loss over epochs

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** true (NFN equivariant layers are the core mechanism)
- **mechanism_isolatable:** true (Compare NFN vs MLP-Matched directly)
- **baseline_measurable:** true (MLP-Matched provides clear baseline)

### Architecture Compatibility
- NFN supports 2D CNN weight spaces with global pooling
- Model Zoo CNNs must have compatible layer structure
- WeightSpaceFeatures can be constructed from state_dict

### Activation Indicators
- **mechanism_log_message:** "NFN forward pass completed with WeightSpaceFeatures"
- **tensor_shape_change:** HNPPool reduces variable-size weight space to fixed-size invariant features
- **metric_delta_expected:** NFN R² > MLP R² by ≥0.05

### Mechanism Verification Code
```python
def verify_mechanism(nfn_model, mlp_model, test_loader):
    """Verify NFN equivariance provides measurable benefit."""
    nfn_preds, mlp_preds, targets = [], [], []
    
    for wsfeat, y in test_loader:
        nfn_preds.append(nfn_model(wsfeat).detach())
        x_flat = flatten_weights(wsfeat)  # For MLP
        mlp_preds.append(mlp_model(x_flat).detach())
        targets.append(y)
    
    nfn_r2 = r2_score(torch.cat(targets), torch.cat(nfn_preds))
    mlp_r2 = r2_score(torch.cat(targets), torch.cat(mlp_preds))
    
    print(f"NFN R²: {nfn_r2:.4f}, MLP R²: {mlp_r2:.4f}")
    print(f"Difference: {nfn_r2 - mlp_r2:.4f}")
    
    return {
        "nfn_r2": nfn_r2,
        "mlp_r2": mlp_r2,
        "difference": nfn_r2 - mlp_r2,
        "hypothesis_supported": (nfn_r2 - mlp_r2) > 0.05
    }
```

### Success Criteria
- **hypothesis_support_threshold:** 0.05 (R² difference)
- **hypothesis_support_metric:** nfn_r2 - mlp_r2

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `nfn_r2 > mlp_r2` (direction)
3. `nfn_r2 - mlp_r2 > 0.05` (magnitude)

---

## Appendix: Reference Implementations

### Primary References

1. **NFN Official Implementation**
   - Repository: https://github.com/AllanYangZhou/nfn
   - Paper: Zhou et al., "Permutation Equivariant Neural Functionals", NeurIPS 2023
   - ArXiv: https://arxiv.org/abs/2302.14040
   - PyPI: `pip install nfn`

2. **Model Zoo Dataset**
   - Repository: https://github.com/ModelZoos/ModelZooDataset
   - Paper: "Model Zoos: A Dataset of Diverse Populations of Neural Network Models", NeurIPS 2022
   - ArXiv: https://arxiv.org/abs/2209.14764
   - Zenodo (ResNet-18 CIFAR-10): https://zenodo.org/records/6974029

### Code Snippets Used

**NFN Layer Construction** (from AllanYangZhou/nfn):
```python
layers.NPLinear(network_spec, in_channels, out_channels, io_embed=True)
layers.HNPPool(network_spec)  # Invariant pooling
```

**Weight Space Features** (from AllanYangZhou/nfn):
```python
from nfn.common import state_dict_to_tensors, WeightSpaceFeatures
wsfeat = WeightSpaceFeatures(*default_collate([state_dict_to_tensors(sd) for sd in state_dicts]))
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-12

### Workflow History for This Hypothesis
- 2026-08-12: H-E1 set to IN_PROGRESS by hypothesis loop
- 2026-08-12: Phase 2C experiment design completed

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
