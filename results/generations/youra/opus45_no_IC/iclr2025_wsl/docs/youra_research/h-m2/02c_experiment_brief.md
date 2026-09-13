# Experiment Design: H-M2

**Date:** 2026-08-12
**Author:** PrayPrey
**Hypothesis Statement:** NFN predictions identical under weight permutation (diff < 1e-5)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests architectural property prediction invariance.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 passed: correlation 0.99999986, max_deviation 1.19e-07)
**Gate Status:** Pending validation

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (equivariant layers verified)

### Gate Condition
- **Gate Type:** SHOULD_WORK
- **Success Criterion:** |pred_original - pred_permuted| < 1e-5 for all 10+ permutations
- **Failure Response:** DEBUG NFN architecture (broken implementation)

---

## Continuation Context

H-M2 directly extends H-M1's invariance verification from intermediate layer outputs to final scalar predictions. The same NFN checkpoint, test MLP, and permutation infrastructure will be reused.

### Previous Hypothesis Results (H-M1)

| Metric | Value |
|--------|-------|
| Max Deviation | 1.19e-07 |
| Invariance Correlation | 0.99999986 |
| Invariance Score | 1.0 |
| Gate Status | PASSED |

**Key Finding:** NFN layer outputs are already permutation-invariant at floating-point precision. H-M2 verifies this property propagates to final predictions.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct NFN content in Archon KB. Results focused on diffuser quantization (NF4), not Neural Functional Networks. No relevant experiment design patterns found.

### Archon Code Examples

No NFN-specific code examples found. Results returned BitsAndBytesConfig for NF4 quantization (different "NF").

### Exa GitHub Implementations

**Primary Source Found:** [AllanYangZhou/nfn](https://github.com/AllanYangZhou/nfn)

| Component | Details |
|-----------|---------|
| Repository | github.com/AllanYangZhou/nfn |
| Paper | "Permutation Equivariant Neural Functionals" (NeurIPS 2023) |
| Invariance Test | `examples/basic_cnn/check_nfn_inv.py` |
| Key Layers | NPLinear, HNPPool (invariance via pooling) |
| Installation | `pip install nfn` |

**Architecture Pattern:**
```python
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

### 🎯 Implementation Priority Assessment

**CRITICAL: H-M2 reuses H-M1 infrastructure completely.**

**Recommended Implementation Path:**
- Primary: Reuse `h-m1/code/` modules (test_data.py, permute.py, metrics.py)
- Fallback: N/A - H-M1 code already validated
- Justification: Same NFN checkpoint, same permutation logic, same MLP architecture. Only gate criterion differs.

### Code Analysis (Serena MCP)

*Skipped* - H-M1 codebase already analyzed and validated. No additional semantic analysis needed.

---

## Experiment Specification

### Dataset

| Property | Value |
|----------|-------|
| Name | Synthetic Test MLP |
| Type | Programmatic (generated at runtime) |
| Source | `h-m1/code/test_data.py::generate_test_mlp()` |
| Architecture | 32-32-32-10 (matches H-E1 checkpoint) |
| Test Scale | 1 MLP × 10 permutations = 11 predictions |

**Loading Information** (for Phase 4 download):
- Method: Code generation
- Identifier: `generate_test_mlp(hidden_dims=(32,32), input_dim=32, output_dim=10, seed=42)`
- Code:
```python
from h_m1.code.test_data import generate_test_mlp
base_sd = generate_test_mlp(hidden_dims=(32, 32), input_dim=32, output_dim=10, seed=42)
```

### Models

#### Baseline Model

| Property | Value |
|----------|-------|
| Name | NFN Regressor (from H-E1) |
| Architecture | NPLinear → ReLU → NPLinear → ReLU → HNPPool → Linear |
| Channels | 32 |
| Checkpoint | `h-e1/checkpoints/nfn_model.pt` |

**Loading Information** (for Phase 4 download):
- Method: PyTorch checkpoint
- Identifier: `h-e1/checkpoints/nfn_model.pt`
- Code:
```python
from h_m1.code.model import NFNRegressor
model = NFNRegressor(network_spec, nfn_channels=32)
model.load_state_dict(torch.load(checkpoint_path, map_location="cpu"))
model.eval()
```

#### Proposed Model

**Architecture:** Same NFN (testing property, not comparing models)

**Core Mechanism Implementation:**

```python
def test_prediction_invariance(nfn_model, base_state_dict, hidden_dims, network_spec, n_perms=10):
    """
    H-M2: Test that NFN predictions are identical under weight permutation.
    
    Returns:
        max_deviation: Maximum absolute difference between any two predictions
        all_predictions: List of predictions [original, perm_0, ..., perm_9]
    """
    predictions = []
    
    # Original prediction
    wsfeat = state_dict_to_wsfeat(base_state_dict, network_spec)
    with torch.no_grad():
        pred_original = nfn_model(wsfeat).item()
    predictions.append(pred_original)
    
    # Permuted predictions
    for seed in range(n_perms):
        perms = generate_permutations(hidden_dims, base_seed=seed)
        perm_sd = permute_state_dict(base_state_dict, len(hidden_dims), perms)
        wsfeat_perm = state_dict_to_wsfeat(perm_sd, network_spec)
        with torch.no_grad():
            pred = nfn_model(wsfeat_perm).item()
        predictions.append(pred)
    
    # Compute max deviation
    preds_tensor = torch.tensor(predictions)
    max_deviation = (preds_tensor - preds_tensor[0]).abs().max().item()
    
    return max_deviation, predictions
```

### Training Protocol

**Not Applicable** - H-M2 is a pure evaluation experiment. Uses pre-trained NFN from H-E1.

| Parameter | Value |
|-----------|-------|
| Training Required | No |
| Checkpoint Source | H-E1 |
| Evaluation Mode | model.eval() |

### Evaluation

| Metric | Description | Library |
|--------|-------------|---------|
| max_deviation | max(|pred_i - pred_j|) for all pairs | torch |
| gate_passed | max_deviation < 1e-5 | custom |
| mean_prediction | mean(predictions) | torch |
| std_prediction | std(predictions) | torch |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Property verification
- Library: PyTorch (torch.tensor operations)
- Code:
```python
preds = torch.tensor(predictions)
max_deviation = (preds.max() - preds.min()).item()
gate_passed = max_deviation < 1e-5
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing all 11 predictions (original + 10 permuted)
  - X-axis: Configuration (original, perm_0, ..., perm_9)
  - Y-axis: NFN Prediction value
  - Expected: All bars identical height (within floating-point precision)

#### Additional Figures (LLM Autonomous)

1. **Deviation Heatmap**: Pairwise absolute differences between predictions
   - Expected: Near-zero matrix (all < 1e-5)
   
2. **Prediction Distribution**: Histogram of predictions
   - Expected: Single spike (no variance)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `max_deviation < 1e-5` (all predictions identical within floating-point tolerance)

**Expected Outcome:** Based on H-M1 results (max_deviation = 1.19e-07), H-M2 should trivially pass. H-M1 already demonstrated NFN layer outputs are invariant; predictions are just a linear projection of those outputs.

---

## Appendix: Reference Implementations

### Primary Reference: H-M1 Code (Already Validated)

| File | Purpose | Reuse Status |
|------|---------|--------------|
| `h-m1/code/test_data.py` | Generate test MLP | Direct reuse |
| `h-m1/code/permute.py` | Generate and apply permutations | Direct reuse |
| `h-m1/code/metrics.py` | Compute invariance metrics | Direct reuse (modify gate) |
| `h-m1/code/model.py` | NFNRegressor wrapper | Direct reuse |
| `h-m1/code/test_invariance.py` | Main orchestration | Adapt for H-M2 |

### External References

1. **NFN Official Repo**: https://github.com/AllanYangZhou/nfn
   - `examples/basic_cnn/check_nfn_inv.py` - Official invariance check pattern

2. **Paper**: "Permutation Equivariant Neural Functionals" (NeurIPS 2023)
   - arXiv: 2302.14040
   - Authors: Zhou, Yang, Burns, Cardace, Jiang, Sokota, Kolter, Finn

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-12

### Workflow History for This Hypothesis

| Event | Timestamp | Phase |
|-------|-----------|-------|
| H-M2 set to IN_PROGRESS | 2026-08-12T20:29:30Z | Hypothesis Loop |
| Phase 2C experiment design started | 2026-08-12 | Phase 2C |

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in H-M1 validated implementation + NFN official repo*
*Next Phase: Phase 3 - Implementation Planning*
