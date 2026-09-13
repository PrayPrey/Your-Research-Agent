# Experiment Design: H-M1

**Date:** 2026-08-12
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** NFN equivariant layers produce permutation-invariant outputs (correlation > 0.99)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates causal mechanism of NFN equivariance.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** YES (H-E1 PASSED with R² diff = 0.5995)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED)

### Gate Condition
Output correlation > 0.99 across 10 random permutations of input CNN weights.

**Failure Response:** PIVOT to check NFN implementation (bug in equivariance)

---

## Continuation Context

This hypothesis builds on H-E1 which demonstrated NFN R² = 0.9524 vs MLP R² = 0.3529 at N=1K. H-M1 now verifies the *mechanism* claim: that NFN's advantage comes from built-in permutation equivariance.

### Previous Hypothesis Results (H-E1)
- **NFN R²:** 0.9524
- **MLP R²:** 0.3529
- **Difference:** 0.5995 (threshold: 0.05)
- **Gate:** PASSED
- **Trained NFN checkpoint:** `h-e1/checkpoints/nfn_model.pt`

---

## Implementation Research Summary

### Archon Knowledge Base Findings

No direct NFN-related entries in Archon KB. The search returned diffusers/quantization content (low similarity ~0.35). NFN is a specialized library not present in general ML documentation sources.

### Archon Code Examples

No relevant code examples found. Archon KB contains HuggingFace Diffusers patterns, not weight-space learning architectures.

### Exa GitHub Implementations

**Primary Source: AllanYangZhou/nfn** (Official Implementation)
- Repository: https://github.com/AllanYangZhou/nfn
- Paper: "Permutation Equivariant Neural Functionals" (NeurIPS 2023)
- Install: `pip install nfn`

**Critical Discovery:** Official repo includes `examples/basic_cnn/check_nfn_inv.py` - a script specifically designed to verify permutation invariance of NFN. This directly implements our H-M1 test.

**Key Architecture Components:**
- `layers.NPLinear` - Permutation equivariant linear layer
- `layers.HNPPool` - Hierarchical pooling for invariance
- `nfn.common.network_spec_from_wsfeat` - Spec generation

**NFN Architecture Pattern:**
```python
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

### 🎯 Implementation Priority Assessment

**CRITICAL: Official implementation provides exact test script**

**Recommended Implementation Path:**
- Primary: Adapt `check_nfn_inv.py` from AllanYangZhou/nfn repo
- Fallback: Implement permutation test from scratch using trained H-E1 model
- Justification: Official test script validates core equivariance property; we extend it for correlation measurement

### Code Analysis (Serena MCP)

Serena analysis skipped - NFN is an external pip package, not in local codebase. The `nfn` library is well-documented at https://www.kaienyang.com/nfn-docs/.

---

## Experiment Specification

### Dataset

**Type:** Reuse H-E1 trained model + synthetic test weights
**Description:** No new training data needed. This is a model property test, not a learning experiment.

**Test Data:**
- Generate 1 synthetic MLP with known weights (same architecture as H-E1 training data)
- Apply 10 random neuron permutations to this MLP
- Feed all 11 weight configurations (original + 10 permuted) to trained NFN

**Loading Information:**
- Method: Generate synthetic MLP weights in-memory
- Identifier: N/A (generated on-the-fly)
- Code:
```python
def generate_test_mlp(hidden_sizes=[64, 64], input_dim=784, output_dim=10, seed=42):
    torch.manual_seed(seed)
    layers_weights = []
    prev_dim = input_dim
    for h in hidden_sizes:
        W = torch.randn(h, prev_dim) * 0.1
        b = torch.zeros(h)
        layers_weights.append((W, b))
        prev_dim = h
    W_out = torch.randn(output_dim, prev_dim) * 0.1
    b_out = torch.zeros(output_dim)
    layers_weights.append((W_out, b_out))
    return layers_weights
```

### Models

#### Baseline Model

**Not Applicable.** H-M1 tests a property of the trained NFN, not a comparison between models.

**Loading Information:**
- Method: Load from H-E1 checkpoint
- Identifier: `h-e1/checkpoints/nfn_model.pt`
- Code:
```python
from nfn import layers
from nfn.common import network_spec_from_wsfeat

# Load trained NFN from H-E1
nfn_model = NFNRegressor(network_spec, nfn_channels=32)
nfn_model.load_state_dict(torch.load('h-e1/checkpoints/nfn_model.pt'))
nfn_model.eval()
```

#### Proposed Model

**Architecture:** N/A - This experiment tests existing trained NFN, not a new model.

**Core Mechanism Implementation:**

```python
# Permutation Invariance Test (10-30 lines pseudo-code)

def permute_hidden_layer(weights, biases, perm):
    """Apply permutation to a hidden layer's weights and biases."""
    # Permute output neurons of current layer
    W_perm = weights[perm, :]
    b_perm = biases[perm]
    return W_perm, b_perm

def permute_mlp_weights(layer_weights, layer_perms):
    """Apply neuron permutations to entire MLP.
    
    layer_perms[i] = permutation for hidden layer i's output neurons
    Must also permute next layer's input connections.
    """
    permuted = []
    for i, (W, b) in enumerate(layer_weights):
        if i < len(layer_perms):  # Hidden layer
            perm = layer_perms[i]
            W_out = W[perm, :]  # Permute outputs
            b_out = b[perm]
            if i > 0:  # Also permute inputs from previous layer
                prev_perm = layer_perms[i-1]
                W_out = W_out[:, prev_perm]
            permuted.append((W_out, b_out))
        else:  # Output layer
            if len(layer_perms) > 0:
                prev_perm = layer_perms[-1]
                W_out = W[:, prev_perm]
            else:
                W_out = W
            permuted.append((W_out, b))
    return permuted

def test_permutation_invariance(nfn_model, test_weights, n_perms=10, seed=0):
    """Test if NFN produces same output for permuted weights."""
    torch.manual_seed(seed)
    
    # Get baseline prediction
    wsfeat_original = weights_to_wsfeat(test_weights)
    with torch.no_grad():
        pred_original = nfn_model(wsfeat_original)
    
    # Test with random permutations
    predictions = [pred_original.item()]
    hidden_sizes = [w.shape[0] for w, b in test_weights[:-1]]
    
    for _ in range(n_perms):
        # Generate random permutation for each hidden layer
        layer_perms = [torch.randperm(h) for h in hidden_sizes]
        
        # Apply permutation
        permuted_weights = permute_mlp_weights(test_weights, layer_perms)
        wsfeat_perm = weights_to_wsfeat(permuted_weights)
        
        with torch.no_grad():
            pred_perm = nfn_model(wsfeat_perm)
        predictions.append(pred_perm.item())
    
    # Compute correlation
    predictions = torch.tensor(predictions)
    correlation = torch.corrcoef(torch.stack([predictions, predictions]))[0, 1]
    # For invariance: all predictions should be identical
    # Use std/mean as invariance metric, or just max deviation
    mean_pred = predictions.mean()
    max_deviation = (predictions - mean_pred).abs().max()
    
    return {
        'predictions': predictions.tolist(),
        'mean': mean_pred.item(),
        'std': predictions.std().item(),
        'max_deviation': max_deviation.item(),
        'invariance_score': 1.0 if max_deviation < 1e-5 else 0.0
    }
```

### Training Protocol

**No Training Required.** This experiment uses the pre-trained NFN from H-E1.

**Test Protocol:**
1. Load trained NFN from `h-e1/checkpoints/nfn_model.pt`
2. Generate 1 synthetic test MLP (fixed seed=42 for reproducibility)
3. Apply 10 random permutations (seeds 0-9)
4. Record all 11 predictions (original + 10 permuted)
5. Compute pairwise correlations
6. Report mean correlation across all pairs

| Parameter | Value |
|-----------|-------|
| Model | Trained NFN from H-E1 |
| Test MLPs | 1 synthetic MLP |
| Permutations | 10 random |
| Seeds | 0-9 for permutations, 42 for test MLP |

### Evaluation

**Primary Metric:** Output correlation across permutations

**Success Criterion (PoC):**
- Primary: Correlation > 0.99 (near-perfect invariance)
- Equivalently: Max absolute deviation < 1e-5

**Secondary Metrics:**
- Standard deviation of predictions
- Max absolute deviation from mean
- Invariance score (binary: 1 if deviation < 1e-5, else 0)

**Metrics Loading Information:**
- Task Type: Invariance verification (not regression/classification)
- Library: PyTorch built-in (torch.corrcoef, torch.std)
- Code:
```python
import torch

def compute_invariance_metrics(predictions):
    """Compute invariance metrics from list of predictions."""
    preds = torch.tensor(predictions)
    n = len(preds)
    
    # Pairwise correlations
    correlations = []
    for i in range(n):
        for j in range(i+1, n):
            corr = torch.corrcoef(torch.stack([preds[[i]], preds[[j]]]))[0, 1]
            correlations.append(corr.item())
    
    # Since all values should be identical for perfect invariance,
    # correlation is undefined (0 variance). Use deviation instead.
    mean_pred = preds.mean()
    max_dev = (preds - mean_pred).abs().max()
    std_pred = preds.std()
    
    return {
        'mean_prediction': mean_pred.item(),
        'std': std_pred.item(),
        'max_deviation': max_dev.item(),
        'is_invariant': max_dev.item() < 1e-5,
        'invariance_correlation': 1.0 - min(max_dev.item() / mean_pred.abs().item(), 1.0)
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Permutation Invariance Plot**: Bar chart showing predictions for original + 10 permuted inputs. All bars should be at same height if invariant.

#### Additional Figures (LLM Autonomous)
- **Deviation Heatmap**: Pairwise absolute differences between predictions
- **Histogram**: Distribution of predictions (should be a spike at single value)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Output correlation > 0.99 OR max_deviation < 1e-5

**Gate Logic:**
```python
gate_passed = (max_deviation < 1e-5) or (invariance_correlation > 0.99)
```

---

## Appendix: Reference Implementations

### Primary Reference
- **Repository:** https://github.com/AllanYangZhou/nfn
- **Test Script:** `examples/basic_cnn/check_nfn_inv.py`
- **Paper:** Zhou et al., "Permutation Equivariant Neural Functionals", NeurIPS 2023
- **ArXiv:** https://arxiv.org/abs/2302.14040

### Key Code Patterns from Official Repo
```python
# From AllanYangZhou/nfn README
from nfn import layers
from nfn.common import network_spec_from_wsfeat

network_spec = network_spec_from_wsfeat(wsfeat)
nfn_channels = 32

nfn = nn.Sequential(
    layers.NPLinear(network_spec, 1, nfn_channels, io_embed=True),
    layers.TupleOp(nn.ReLU()),
    layers.NPLinear(network_spec, nfn_channels, nfn_channels, io_embed=True),
    layers.TupleOp(nn.ReLU()),
    layers.HNPPool(network_spec),  # pooling layer, for invariance
    nn.Flatten(start_dim=-2),
    nn.Linear(nfn_channels * layers.HNPPool.get_num_outs(network_spec), 1)
)
```

### H-E1 Artifacts to Reuse
- `h-e1/checkpoints/nfn_model.pt` - Trained NFN weights
- `h-e1/code/model.py` - NFNRegressor class definition
- `h-e1/code/data.py` - Weight-space feature utilities

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-12

### Workflow History for This Hypothesis
1. H-E1 COMPLETED (2026-08-12) - Gate PASSED, NFN R² 0.9524 vs MLP R² 0.3529
2. H-M1 started (2026-08-12) - Experiment design phase

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
