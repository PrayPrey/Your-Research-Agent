---
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - non_functional_requirements
  - data_specification
  - evaluation_criteria
  - dependencies
  - success_criteria
hypothesis_id: h-m1
hypothesis_type: MECHANISM
tier: FULL
generated_at: "2026-08-21T12:30:00+00:00"
---

# PRD: H-M1 — Permutation Equivariance Mechanism Verification

## 1. Executive Summary

This experiment verifies the structural permutation-equivariance mechanism of DWSNets and GNN-NFN encoders against a flat-MLP negative control. The verification tests whether identical weight tensors under neuron-order permutation produce identical output representations from equivariant encoders (max absolute difference < 1e-5). This is a Proof-of-Concept (PoC) verification experiment — no training is involved; encoders are loaded from H-E1 checkpoints or random initialization. Success confirms the mechanistic basis for the R² advantage observed in H-E1.

**Prerequisite:** H-E1 VALIDATED — GNN-NFN vs flat-MLP R² advantage confirmed on CIFAR-10 zoo at ≤500 training samples.

---

## 2. Problem Statement

H-E1 demonstrated that equivariant encoders (GNN-NFN) outperform flat-MLP encoders in accuracy prediction at small training set sizes. **H-M1 asks why**: is the advantage due to structural permutation equivariance encoded in the architecture?

The mechanism claim: DWSNets (via DWS-layer block structure, Theorem 5.1) and GNN-NFN (via graph node permutation symmetry) are mathematically constrained to produce identical output regardless of neuron-ordering permutation within hidden layers. Flat-MLP has no such constraint and should produce different outputs under permutation.

**If verified:** The R² advantage in H-E1 is attributable to equivariant inductive bias — the encoder inherently ignores irrelevant permutation symmetry, reducing effective sample complexity.

---

## 3. Functional Requirements

### FR-1: DWSNets Encoder Loading
- Load DWSNets from official repository `AvivNavon/DWSNets`
- Install: `git clone https://github.com/AvivNavon/DWSNets && pip install -e .`
- Configure `network_spec` matching CIFAR-10 zoo CNN architecture
- If H-E1 checkpoint exists: load it; else use random initialization (equivariance is structural, not learned)

### FR-2: GNN-NFN Encoder Loading
- Load GNN-NFN from H-E1 checkpoint: `h-e1/checkpoints/gnn_nfn_best.pt`
- Source: `mkofinas/neural-graphs` (already in environment from H-E1)
- Configuration: `hidden_dim=128, num_layers=4`

### FR-3: Flat-MLP Encoder Loading (Negative Control)
- Load flat-MLP from H-E1 checkpoint: `h-e1/checkpoints/flat_mlp_best.pt`
- Architecture: `FlatMLP(input_dim=weight_dim, hidden=512, output_dim=128)`
- Purpose: Confirm test detects non-equivariance (max_diff > 1e-3 expected)

### FR-4: Weight Sample Loading
- Load N=200 random models from CIFAR-10 zoo: `data/model_zoos/cifar10/`
- Each model: OrderedDict of weight tensors `{layer.weight, layer.bias, ...}`
- Fixed seed: `torch.manual_seed(42)` for reproducibility

### FR-5: Permutation Function
- Implement `permute_weights(weight_dict, layer_idx, perm)`:
  - `W_in` (layer_idx): permute rows by `perm` (P^T @ W_in)
  - `W_out` (layer_idx+1): permute cols by `perm` (W_out @ P)
  - Bias of permuted layer: reorder by `perm`
- Apply to all hidden layers (not input/output layers)

### FR-6: Equivariance Verification Loop
- For each of 200 weight samples:
  - Compute encoder output on original weights: `out_orig = encoder(weights)`
  - For each of K=50 random permutations:
    - Generate `perm = torch.randperm(hidden_dim)`
    - Apply `permute_weights()` to get `weights_perm`
    - Compute `out_perm = encoder(weights_perm)`
    - Compute `diff = (out_orig - out_perm).abs().max().item()`
    - Append to `max_diffs`
- Total: 200 × 50 = 10,000 checks per encoder
- Run for ALL THREE encoders: DWSNets, GNN-NFN, Flat-MLP

### FR-7: Result Assertions
- `assert dwsnet_max_diff < 1e-5` — DWSNets equivariant
- `assert gnn_max_diff < 1e-5` — GNN-NFN equivariant
- `assert flat_max_diff > 1e-3` — Flat-MLP NOT equivariant (negative control)

### FR-8: Mechanism Activation Check
- Implement `verify_mechanism_activated(results)`:
  - `dwsnet_equivariant`: max_diff < 1e-5
  - `gnn_equivariant`: max_diff < 1e-5
  - `flat_not_equivariant`: max_diff > 1e-3
  - `gap_exists`: flat_diff / (dwsnet_diff + 1e-10) > 100

### FR-9: Visualization (Mandatory)
- **Bar chart**: max_abs_diff per encoder with 1e-5 threshold line
- **CDF plot**: Cumulative distribution of per-permutation max abs diffs (log x-axis), one line per encoder
- **Histogram**: Distribution of 10,000 max abs diffs per encoder (3-panel figure)
- Save all figures to `docs/youra_research/h-m1/figures/`

### FR-10: Results Report
- Print summary table: encoder name, max_diff, mean_diff, median_diff, p95_diff, PASS/FAIL
- Save full results to `docs/youra_research/h-m1/results/`
- Save JSON results for Phase 4.5 synthesis

---

## 4. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed `torch.manual_seed(42)` applied before all random operations
- All permutations generated deterministically from seed

### NFR-2: Compute
- Device: CPU sufficient (weight tensors are small); GPU optional
- Runtime: < 5 minutes total for all 10,000 checks per encoder
- Memory: < 4GB RAM

### NFR-3: Numerical Precision
- All computations in float32 (default PyTorch)
- Theoretical equivariance threshold: < 1e-5 (above float32 noise floor ~1e-7)
- Non-equivariance threshold: > 1e-3 (well above numerical noise)

### NFR-4: Code Quality
- Inference-only (`torch.no_grad()` context throughout)
- All encoders in `eval()` mode
- Single-script implementation for reproducibility

---

## 5. Data Specification

### 5.1 Primary Dataset

**Name:** ModelZooDataset — CIFAR-10 Model Zoo  
**Type:** Reuse from H-E1 (no download required)  
**Location:** `data/model_zoos/cifar10/` (from H-E1 experiment)  
**Format:** PyTorch checkpoint files (`.pt`), each containing `state_dict`  

**Loading code:**
```python
zoo_dir = Path("data/model_zoos/cifar10/")
ckpt = torch.load(zoo_dir / "model_{i:04d}.pt", map_location="cpu")
weights = ckpt["state_dict"]  # OrderedDict
```

**Sample selection:** N=200 random models, seed=42

### 5.2 Encoder Checkpoints (from H-E1)

| Encoder | File | Source |
|---------|------|--------|
| GNN-NFN | `h-e1/checkpoints/gnn_nfn_best.pt` | H-E1 validation |
| Flat-MLP | `h-e1/checkpoints/flat_mlp_best.pt` | H-E1 validation |
| DWSNets | random init or `h-e1/checkpoints/dwsnet_best.pt` if exists | FR-1 |

**Note:** DWSNets was not run in H-E1. Install from official repo; random init is valid since equivariance is structural.

---

## 6. Evaluation Criteria

### 6.1 Primary Gate Metric

| Encoder | Metric | Threshold | Gate |
|---------|--------|-----------|------|
| DWSNets | max_abs_diff over 10,000 checks | < 1e-5 | MUST_WORK |
| GNN-NFN | max_abs_diff over 10,000 checks | < 1e-5 | MUST_WORK |
| Flat-MLP | max_abs_diff over 10,000 checks | > 1e-3 | Negative control |

### 6.2 Reported Statistics (per encoder, per 10,000 checks)

- max_abs_diff
- mean_abs_diff
- median_abs_diff
- 95th percentile abs_diff
- Fraction of checks passing threshold

### 6.3 Gate Condition

PASS if:
1. DWSNets max_abs_diff < 1e-5 AND
2. GNN-NFN max_abs_diff < 1e-5 AND
3. Flat-MLP max_abs_diff > 1e-3 (negative control valid)

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.1
torchvision
numpy
matplotlib
seaborn
scipy
pathlib
json
yaml
```

### 7.2 External Repositories

| Repository | Purpose | Install |
|------------|---------|---------|
| `AvivNavon/DWSNets` | DWSNets encoder | `git clone https://github.com/AvivNavon/DWSNets && pip install -e .` |
| `mkofinas/neural-graphs` | GNN-NFN encoder | Already installed from H-E1 |
| `ModelZoos/ModelZooDataset` | Dataset | Already downloaded from H-E1 |

### 7.3 H-E1 Artifacts Required

- `data/model_zoos/cifar10/` — CIFAR-10 zoo checkpoints
- `h-e1/checkpoints/gnn_nfn_best.pt` — GNN-NFN trained checkpoint
- `h-e1/checkpoints/flat_mlp_best.pt` — Flat-MLP trained checkpoint

---

## 8. Success Criteria

### 8.1 PoC Pass Conditions

1. Script executes without error end-to-end
2. DWSNets: max_abs_diff < 1e-5 over all 10,000 permutation checks
3. GNN-NFN: max_abs_diff < 1e-5 over all 10,000 permutation checks
4. Flat-MLP: max_abs_diff > 1e-3 (negative control passes)
5. `verify_mechanism_activated()` returns `True`

### 8.2 Visualization Deliverables

- `figures/gate_metrics_bar.png` — bar chart with threshold line
- `figures/cdf_comparison.png` — CDF plot (log x-axis)
- `figures/diff_histograms.png` — 3-panel histogram

### 8.3 Phase 4 Validation Output

- `results/equivariance_results.json` — full numeric results
- `04_validation.md` — summary report with pass/fail verdict
