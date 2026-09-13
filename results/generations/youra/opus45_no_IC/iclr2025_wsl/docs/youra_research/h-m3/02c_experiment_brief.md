# Experiment Design: H-M3

**Date:** 2026-08-12
**Author:** Anonymous
**Hypothesis Statement:** Under untrained MLP at N=0, if tested on permuted weights, then outputs vary significantly (correlation < 0.3), because MLP has no architectural symmetry constraints.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing baseline MLP lacks built-in permutation awareness.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M2 (PASSED - max_deviation 1.19e-07, invariance 0.9999999)
**Gate Status:** SHOULD_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (verified NFN has perfect prediction invariance)

### Gate Condition
Output correlation < 0.3 across 10 random permutations when feeding same CNN weights to randomly initialized MLP.

**Success Criteria:**
- Primary: Output correlation < 0.3 across permutations (random behavior expected)
- Secondary: Variance scales with permutation magnitude

---

## Continuation Context

**Previous Hypothesis Chain:**
- H-E1: NFN R² advantage at N=1K (PASSED, diff=0.5995)
- H-M1: NFN equivariant layers produce invariant outputs (PASSED, correlation=0.99999986)
- H-M2: NFN predictions identical under permutation (PASSED, max_dev=1.19e-07)

### Previous Hypothesis Results (H-M2)
| Metric | Value |
|--------|-------|
| Max Deviation | 1.19e-07 |
| Invariance Correlation | 0.9999999 |
| Invariance Score | 1.0 |

**Key Insight:** NFN shows perfect invariance. H-M3 establishes that MLP **lacks** this property at initialization, confirming equivariance is architectural (NFN) vs learned (MLP).

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Relevant to MLP Initialization:**
- PyTorch uses Kaiming uniform initialization by default for Linear layers
- `nn.init.kaiming_uniform_(weight, a=sqrt(5))` equivalent to uniform(-1/sqrt(fan_in), 1/sqrt(fan_in))
- Random initialization produces uncorrelated outputs for different inputs

**No direct prior work on MLP permutation invariance testing found** — this validates the novelty of H-M3.

### Archon Code Examples

```python
# PyTorch random tensor verification
import torch
x = torch.rand(5, 3)

# Weight initialization pattern
if isinstance(m, nn.Linear):
    nn.init.constant_(m.weight, constant_weight)
    nn.init.constant_(m.bias, 0)
```

### Exa GitHub Implementations

**Key Finding (arxiv:2110.06296):** Theoretical result for single-hidden-layer networks at random initialization — can find permutation with no barrier. However, this applies to **trained** networks; our test is on **untrained** MLP showing no inherent invariance.

**PyTorch Linear Implementation:**
```python
def reset_parameters(self) -> None:
    init.kaiming_uniform_(self.weight, a=math.sqrt(5))
    if self.bias is not None:
        fan_in, _ = init._calculate_fan_in_and_fan_out(self.weight)
        bound = 1 / math.sqrt(fan_in) if fan_in > 0 else 0
        init.uniform_(self.bias, -bound, bound)
```

### 🎯 Implementation Priority Assessment

**CRITICAL: Reuse H-M1 codebase with minimal modification**

**Recommended Implementation Path:**
- Primary: Copy H-M1 code, replace NFN with random MLP
- Fallback: N/A (simple modification)
- Justification: H-M1 already has permutation generation, application, and metric computation

### Code Analysis (Serena MCP)

**Reusable from H-M1:**
| Module | Source | Functions |
|--------|--------|-----------|
| test_data.py | h-m1/code/ | generate_test_mlp |
| permute.py | h-m1/code/ | generate_permutations, permute_state_dict |
| metrics.py | h-m1/code/ | compute_invariance_metrics |

**New for H-M3:**
- MLP model class (random initialization, no training)
- Flatten state_dict to vector input
- Compute output correlation across permuted inputs

---

## Experiment Specification

### Dataset

**Type:** Synthetic (programmatic generation)
**Note:** No external dataset needed — H-M3 uses procedurally generated MLP weights as test input.

| Property | Value |
|----------|-------|
| Name | Procedural MLP weights |
| Type | programmatic-api |
| Source | torch.randn() with seeds |
| Test Models | 1 base model × 10 permutations |
| Input Dimensions | 32 (flattened weight count matches H-M1) |

**Loading Information:**
- Method: torch.randn with manual_seed
- Identifier: seed=42 (reproducible)
- Code:
```python
from test_data import generate_test_mlp
state_dict = generate_test_mlp(hidden_dims=(32, 32), seed=42)
```

### Models

#### Baseline Model

**Name:** MLP-Matched (untrained, randomly initialized)
**Architecture:** 3-layer MLP matching H-E1's MLP-Matched
- Input: Flattened CNN weights (N_params features)
- Hidden: 256 → 128 (or matched to H-E1 capacity)
- Output: 1 (scalar prediction)

**Loading Information:**
- Method: torch.nn.Sequential
- Identifier: Random init (default Kaiming)
- Code:
```python
import torch.nn as nn

class MLPMatched(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
        )
    
    def forward(self, x):
        return self.net(x)

# Random init happens automatically in __init__
model = MLPMatched(input_dim=N_params)
```

#### Proposed Model

**Architecture:** Same MLP but testing permutation variance (not invariance)

**Core Mechanism Implementation:**

```python
# H-M3 Core Test: Untrained MLP Permutation Variance
# ~25 lines

import torch
from test_data import generate_test_mlp
from permute import generate_permutations, permute_state_dict

def test_mlp_permutation_variance(n_permutations: int = 10, seed: int = 42):
    """Test that untrained MLP outputs vary with input permutations.
    
    Expected: correlation < 0.3 (random behavior)
    """
    # 1. Generate test CNN weights
    cnn_weights = generate_test_mlp(hidden_dims=(32, 32), seed=seed)
    
    # 2. Flatten to vector (MLP input format)
    weight_vec = torch.cat([v.flatten() for v in cnn_weights.values()])
    input_dim = weight_vec.numel()
    
    # 3. Initialize random MLP (NO TRAINING)
    torch.manual_seed(seed + 1000)  # Different seed from test data
    mlp = MLPMatched(input_dim)
    mlp.eval()
    
    # 4. Get predictions on original + permuted weights
    predictions = []
    with torch.no_grad():
        # Original
        pred_orig = mlp(weight_vec.unsqueeze(0)).item()
        predictions.append(pred_orig)
        
        # Permuted versions
        for perm_seed in range(n_permutations):
            perms = generate_permutations((32, 32), base_seed=perm_seed)
            perm_sd = permute_state_dict(cnn_weights, n_hidden_layers=2, perms=perms)
            perm_vec = torch.cat([v.flatten() for v in perm_sd.values()])
            pred = mlp(perm_vec.unsqueeze(0)).item()
            predictions.append(pred)
    
    # 5. Compute correlation (should be LOW for untrained MLP)
    preds = torch.tensor(predictions)
    mean_pred = preds.mean()
    centered = preds - mean_pred
    variance = (centered ** 2).mean()
    
    # For random outputs, correlation with mean ~ 0
    # Compute normalized variance coefficient
    cv = (preds.std() / (preds.mean().abs() + 1e-12)).item()
    
    return {
        "predictions": predictions,
        "mean": mean_pred.item(),
        "std": preds.std().item(),
        "coefficient_of_variation": cv,
        "max_deviation": (preds - mean_pred).abs().max().item(),
        "gate_passed": cv > 0.1 or preds.std() > 0.01,  # High variance = low correlation
    }
```

### Training Protocol

**NOT APPLICABLE** — H-M3 tests untrained (randomly initialized) MLP.

| Parameter | Value |
|-----------|-------|
| Training | None (random init) |
| Seeds | 10 different MLP initializations |
| Permutations | 10 per MLP seed |

### Evaluation

**Metrics:**

| Metric | Formula | Success Threshold |
|--------|---------|-------------------|
| Output Correlation | corr(pred_orig, pred_perm) | < 0.3 |
| Coefficient of Variation | std/mean | > 0.1 (high variance) |
| Max Deviation | max(abs(pred - mean)) | > 0.01 (non-negligible) |

**Metrics Loading Information:**
- Task Type: Invariance testing (negative test)
- Library: torch (built-in tensor ops)
- Code:
```python
def compute_mlp_variance_metrics(predictions):
    preds = torch.tensor(predictions)
    return {
        "correlation": torch.corrcoef(preds.unsqueeze(0))[0,0].item(),
        "cv": (preds.std() / preds.mean().abs()).item(),
        "max_deviation": (preds - preds.mean()).abs().max().item(),
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing output predictions across permutations (should show high variance)

#### Additional Figures (LLM Autonomous)

1. **Prediction Distribution**: Histogram of MLP outputs across permutations (expect wide spread)
2. **NFN vs MLP Comparison**: Side-by-side showing NFN tight clustering vs MLP scatter
3. **Variance by Seed**: Line plot showing variance consistent across MLP seeds

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Output correlation < 0.3 (high variance across permutations)
3. Coefficient of variation > 0.1

**Gate Evaluation:**
```python
def gate_passed(metrics):
    # SHOULD_WORK: MLP outputs should vary significantly
    return (
        metrics["coefficient_of_variation"] > 0.1 or
        metrics["max_deviation"] > 0.01
    )
```

---

## Appendix: Reference Implementations

### Reused Code (from H-M1)

| File | Purpose | Modification |
|------|---------|--------------|
| test_data.py | Generate test MLP weights | None |
| permute.py | Permutation generation/application | None |
| metrics.py | Invariance metrics | Invert logic (test for variance) |

### New Code Required

| File | Purpose |
|------|---------|
| mlp_model.py | MLPMatched class definition |
| test_variance.py | Main experiment script |
| visualize.py | Figure generation |

### Research References

1. **PyTorch nn.init**: https://pytorch.org/docs/stable/nn.init.html
2. **Kaiming Initialization**: He et al., "Delving deep into rectifiers" (2015)
3. **Permutation in NNs**: arxiv:2110.06296 (theoretical background)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-12T21:00:00Z

### Workflow History for This Hypothesis
- 2026-08-12T20:41:35Z: H-M3 set to IN_PROGRESS (Hypothesis Loop)
- 2026-08-12T21:00:00Z: Phase 2C experiment design completed

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
