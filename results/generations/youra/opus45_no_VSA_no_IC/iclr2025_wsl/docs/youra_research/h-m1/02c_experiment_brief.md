# Experiment Design: H-M1

**Date:** 2026-08-24
**Author:** Anonymous
**Hypothesis Statement:** NFN equivariant layers extract permutation-invariant features architecturally without data augmentation
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates core mechanism works as theorized.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 validated with R² = 0.9995)
**Gate Status:** MUST_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition
NFN equivariant layers must extract permutation-invariant features without data augmentation (validated via feature extraction and prediction task).

---

## Continuation Context

**Building on H-E1 results:**
- Statistics baseline achieves R² = 0.9995 on 500 test models
- Feature extraction pipeline: 63 dimensions (7 stats × 9 layers)
- Model Zoo ResNet-20/CIFAR-10 weights confirmed as valid data source
- RidgeCV consistently selected α=0.1

### Previous Hypothesis Results (if applicable)
H-E1 established baseline performance ceiling. H-M1 validates NFN can match/exceed this with architectural equivariance.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

No direct NFN/equivariant network results in Archon KB. General PyTorch patterns available:
- Model weight loading/quantization patterns (HuggingFace)
- Layer output inspection for debugging
- Distributed tensor operations

NFN is specialized NeurIPS 2023 research - primary reference is official implementation.

### Archon Code Examples

General PyTorch patterns found (not NFN-specific):
- `load_state_dict()` for weight loading
- `nn.Module` container patterns
- Attention mechanisms (scaled dot-product)

### Exa GitHub Implementations

**Repository 1**: AllanYangZhou/nfn (⭐ 93) - **OFFICIAL IMPLEMENTATION**
- **URL**: https://github.com/AllanYangZhou/nfn
- **Paper**: "Permutation Equivariant Neural Functionals" (NeurIPS 2023)
- **License**: MIT
- **Install**: `pip install nfn`
- **Key Classes**:
  - `WeightSpaceFeatures`: Input container for neural network weights
  - `state_dict_to_tensors()`: Convert PyTorch state_dict to NFN input format
  - NF-Layers: Permutation equivariant layers
- **Supports**: MLPs and 2D CNNs (including ResNet with global pooling)
- **Example Usage**:
  ```python
  from nfn.common import state_dict_to_tensors
  from nfn import WeightSpaceFeatures
  
  state_dicts = [m.state_dict() for m in models]
  wts_and_bs = [state_dict_to_tensors(sd) for sd in state_dicts]
  wsfeat = WeightSpaceFeatures(*default_collate(wts_and_bs))
  out = nfn(wsfeat)
  ```

**Repository 2**: Fsoft-AIC/Transformer-NFN (⭐ 3, ICLR 2025)
- Extends NFN to Transformer architectures
- Not needed for ResNet/CNN experiments

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

1. ⭐⭐⭐ **AllanYangZhou/nfn** - Official NeurIPS 2023 implementation (SELECTED)
2. ⭐⭐ Library implementations - N/A (NFN is the library)
3. ⭐ Community reimplementations - Not needed

**Recommended Implementation Path:**
- Primary: Official `nfn` PyPI package (`pip install nfn`)
- Fallback: Clone from GitHub and install editable (`pip install -e .`)
- Justification: Official implementation by paper authors, MIT licensed, pip-installable, actively maintained, supports CNN weight spaces including ResNet

### Code Analysis (Serena MCP)

**Not required** - Official NFN library is well-documented with clear API:
- `WeightSpaceFeatures` for input
- `state_dict_to_tensors()` for conversion
- NF-Layers are drop-in PyTorch modules
- Example code provided in `examples/basic_cnn/`

---

## Experiment Specification

### Dataset

**Name**: Model Zoo ResNet-20/CIFAR-10
**Type**: standard (published benchmark)
**Source**: Zenodo Record 6620869 - "Model Zoo: A Dataset of Diverse Populations of Neural Network Models"
**Authors**: AIML Lab, University of St.Gallen; Samsung AI Lab Montreal; Universitat Politècnica de Catalunya

**Statistics**:
- Total models: 5500 trained ResNet-20 checkpoints
- Training set: 5000 models (variable N subsets)
- Test set: 500 models (fixed, held-out)
- Each model: ResNet-20 trained on CIFAR-10 with varying hyperparameters
- Accuracy range: ~70-95% (diverse population)

**Features per Model** (from H-E1):
- Layer statistics: mean, std, min, max, median, skew, kurtosis per layer
- 9 layers × 7 statistics = 63 dimensions
- Target: test accuracy (continuous, 0-100%)

**Loading Information** (for Phase 4 download):
- Method: Zenodo API + torch.load
- Identifier: `zenodo:6620869`
- Code:
  ```python
  # Download from Zenodo
  import requests
  import zipfile
  
  ZENODO_RECORD = "6620869"
  url = f"https://zenodo.org/api/records/{ZENODO_RECORD}/files"
  # Download and extract model checkpoints
  
  # Load individual model
  state_dict = torch.load(f"model_zoo/model_{idx}.pt")
  ```

### Models

#### Baseline Model

**Name**: Statistics Baseline (from H-E1)
**Type**: Ridge Regression on layer statistics
**Architecture**: 63-dim features → RidgeCV → 1-dim accuracy prediction
**Performance**: R² = 0.9995 (established in H-E1)

This is the comparison target. NFN must demonstrate architectural equivariance while maintaining comparable prediction performance.

**Loading Information** (for Phase 4 download):
- Method: sklearn (no download needed)
- Identifier: `sklearn.linear_model.RidgeCV`
- Code:
  ```python
  from sklearn.linear_model import RidgeCV
  baseline = RidgeCV(alphas=[0.01, 0.1, 1.0, 10.0])
  baseline.fit(X_train_stats, y_train)
  ```

#### Proposed Model

**Architecture:** NFN (Neural Functional Network) with equivariant layers

**Core Mechanism Implementation:**

```python
# Core Mechanism: NFN Equivariant Feature Extraction
# Based on: AllanYangZhou/nfn (NeurIPS 2023)

import torch
import torch.nn as nn
from nfn import NFNBuilder, WeightSpaceFeatures
from nfn.common import state_dict_to_tensors

class NFNAccuracyPredictor(nn.Module):
    """
    NFN-based accuracy predictor for neural network weights.
    Extracts permutation-invariant features via equivariant layers.
    """
    def __init__(self, network_spec, hidden_dim=128, num_layers=3):
        super().__init__()
        # Build NFN using official library
        self.nfn = NFNBuilder(
            network_spec=network_spec,  # ResNet-20 architecture spec
            hidden_channels=hidden_dim,
            num_layers=num_layers,
            invariant_output=True  # Pool to invariant representation
        ).build()
        self.head = nn.Linear(hidden_dim, 1)  # Accuracy prediction
    
    def forward(self, weight_features: WeightSpaceFeatures):
        """
        Args:
            weight_features: WeightSpaceFeatures from model state_dicts
        Returns:
            (B, 1) - predicted accuracy for each model
        """
        # NFN extracts permutation-invariant features
        invariant_repr = self.nfn(weight_features)  # (B, hidden_dim)
        return self.head(invariant_repr)  # (B, 1)

# Equivariance verification (key mechanism test)
def verify_equivariance(nfn, weights, permutation):
    """Verify NFN output invariant to neuron permutation."""
    original_out = nfn(weights)
    permuted_weights = apply_permutation(weights, permutation)
    permuted_out = nfn(permuted_weights)
    return torch.allclose(original_out, permuted_out, atol=1e-5)
```

### Training Protocol

**Optimizer**: Adam
- Learning rate: 1e-3
- Weight decay: 1e-4
- Source: Standard for small regression tasks; NFN paper uses similar

**Schedule**: ReduceLROnPlateau
- Factor: 0.5
- Patience: 10 epochs
- Source: Adaptive for regression convergence

**Batch Size**: 32 models per batch
- Source: Memory-constrained by model weight tensor sizes

**Epochs**: 100 (early stopping patience: 20)
- Source: Sufficient for convergence on 5000 training models

**Loss Function**: MSE Loss
- Target: Accuracy (0-100 scale)
- Source: Standard for regression tasks

**Seeds**: 3 (for mechanism validation)
- Source: Verify consistent equivariance behavior

### Evaluation

**Primary Metrics**:
1. **R² Score**: Coefficient of determination for accuracy prediction
   - Baseline (Statistics): R² = 0.9995 (from H-E1)
   - NFN target: R² ≥ 0.90 (comparable performance)
2. **Equivariance Error**: Max difference under neuron permutation
   - Target: < 1e-5 (numerically invariant)
3. **MAE**: Mean Absolute Error on accuracy prediction
   - For interpretability (accuracy points)

**Mechanism-Specific Metrics** (H-M1 focus):
- **Equivariance Test Pass Rate**: % of test models where `verify_equivariance()` returns True
  - Target: 100% (architectural guarantee, not learned)
- **Feature Dimension**: NFN hidden_dim vs Statistics 63-dim
  - Documents representation capacity

**Success Criteria**:
1. Equivariance test passes on ALL test models (100%)
2. NFN R² ≥ 0.85 on held-out 500 test models
3. Training converges without NaN/explosion

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Regression (accuracy prediction)
- Library: sklearn.metrics + custom equivariance test
- Code:
  ```python
  from sklearn.metrics import r2_score, mean_absolute_error
  
  # Prediction quality
  r2 = r2_score(y_true, y_pred)
  mae = mean_absolute_error(y_true, y_pred)
  
  # Equivariance verification
  equivariance_pass = verify_equivariance(nfn, test_weights, random_perm)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: NFN R² vs Statistics Baseline R² bar chart

#### Additional Figures (LLM Autonomous)

1. **Prediction Scatter Plot**: True accuracy vs NFN predicted accuracy (with R² annotation)
2. **Equivariance Verification**: Before/after permutation output comparison (should overlap perfectly)
3. **Training Curve**: Loss and R² over epochs
4. **Residual Distribution**: Histogram of prediction errors

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. NFN extracts permutation-invariant features (verified via equivariance test)
3. NFN achieves comparable R² to Statistics baseline on accuracy prediction

---

## Appendix: Reference Implementations

### Primary References

1. **NFN Official Implementation**
   - Repository: https://github.com/AllanYangZhou/nfn
   - Paper: "Permutation Equivariant Neural Functionals" (NeurIPS 2023)
   - Authors: Allan Zhou, Kaien Yang, Kaylee Burns, et al. (Stanford, CMU)
   - Install: `pip install nfn`
   - Key files: `nfn/layers.py`, `nfn/common.py`, `examples/basic_cnn/`

2. **Model Zoo Dataset**
   - Source: Zenodo Record 6620869
   - Title: "Model Zoo: A Dataset of Diverse Populations of Neural Network Models - CIFAR10"
   - Authors: AIML Lab (University of St.Gallen), Samsung AI Lab Montreal
   - Contains: 5500+ ResNet-20 checkpoints trained on CIFAR-10

3. **NFN Paper (arXiv)**
   - URL: https://arxiv.org/abs/2302.14040
   - Key sections: Section 3 (NF-Layers), Section 4 (Experiments)
   - Relevant experiments: Predicting classifier generalization (Table 1)

### Secondary References

4. **Neural Functional Transformers**
   - Paper: https://arxiv.org/abs/2305.13546
   - Extends NFN to transformer architectures (future work reference)

5. **Transformer-NFN (ICLR 2025)**
   - Repository: https://github.com/Fsoft-AIC/Transformer-NFN
   - Not used in this experiment (CNN-focused)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24T09:45:00Z

### Workflow History for This Hypothesis
- Phase 2C initiated for H-M1
- Building on H-E1 validation (R² = 0.9995)
- Archon KB searched (no direct NFN results)
- Exa GitHub: Found official NFN repo (AllanYangZhou/nfn)
- Dataset confirmed: Model Zoo Zenodo (standard, not synthetic)
- Experiment specification synthesized

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
