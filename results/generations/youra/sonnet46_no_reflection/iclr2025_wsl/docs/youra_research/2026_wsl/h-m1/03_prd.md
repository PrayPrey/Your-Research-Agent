# Product Requirements Document: H-M1
# Orbit-PE Mechanism Verification — Unified Codebase & Overhead Constraint

**Hypothesis**: H-M1 (MECHANISM — INCREMENTAL on H-E1)
**Date**: 2026-05-21
**Author**: Anonymous Pipeline (Phase 3 — UNATTENDED)
**Source**: Phase 2C Experiment Brief (`02c_experiment_brief.md`)
**Tier**: FULL (MECHANISM hypothesis, max 30 tasks)

---

## 1. Executive Summary

H-M1 verifies that the orbit-PE mechanism (introduced conceptually in H-E1) is:
1. **Computable** for all linear operator types (Linear, Conv2d, MultiheadAttention) using a **unified codebase** with no architecture-conditional branches
2. **Efficient** — computation overhead ≤1.2× vanilla SANE sequential-PE

This is a **computability + timing benchmark** experiment. No model training is performed. The experiment runs on 100 CNN checkpoints + 100 Transformer checkpoints from the Small CNN Zoo and Small Transformer Zoo datasets.

Gate: **MUST_WORK** — all three criteria (computability_rate=1.0, unified_codebase=True, overhead_ratio≤1.2) must be satisfied.

---

## 2. Problem Statement

SANE's sequential positional encoding [n, l, k] is architecture-specific. Orbit-PE replaces it with orbit membership vectors derived from the (input-channel perm × output-channel perm) group action. For orbit-PE to be the universal replacement claimed in the main hypothesis (H-OrbitPE-v1), it must:

- Work identically for all linear operator types without if/else layer-type branches
- Not impose prohibitive computational overhead vs the simple sequential-PE baseline

H-E1 proved orbit computation is accuracy-preserving. H-M1 now tests whether the implementation is practically viable as a unified drop-in replacement for SANE's tokenizer.

---

## 3. Goals and Non-Goals

### Goals
- Implement `OrbitPEComputer` module that handles Linear, Conv2d, and MultiheadAttention uniformly
- Measure wall-clock overhead ratio (orbit-PE / sequential-PE) over 200 checkpoints
- Verify all orbit membership vectors have consistent dimensionality
- Verify no architecture-conditional branches in the core computation path

### Non-Goals
- Model training (no gradient computation)
- Accuracy benchmarking (H-E1 covered this)
- Cross-architecture transfer learning (H-M3 covers this)
- Hyperparameter tuning

---

## 4. Data Specification

### 4.1 Primary Dataset: Small CNN Zoo

| Property | Value |
|----------|-------|
| Source | AllanYangZhou/nfn repository (`experiments/` folder) |
| Content | CIFAR-10 and SVHN CNN classifiers (varying hyperparameters) |
| Total Size | ~50,000 CNN models |
| **Sample for H-M1** | **100 checkpoints** (stratified by architecture type) |
| Format | `.pt` PyTorch checkpoint files |
| Layer Types | Conv2d, Linear (fully-connected layers) |
| Download Method | `git clone https://github.com/AllanYangZhou/nfn` + download script |

**Loading Code**:
```python
import torch
from pathlib import Path
checkpoints = list(Path("data/cnn_zoo/").glob("**/*.pt"))[:100]
models = [torch.load(ckpt, map_location='cpu') for ckpt in checkpoints]
```

**Task**: Requires manual clone and data download → generates `data-preparation` task.

### 4.2 Secondary Dataset: Small Transformer Zoo

| Property | Value |
|----------|-------|
| Source | MathematicalAI-NUS/Transformer-NFN repository (`data/` folder) |
| Content | 125K+ Transformer checkpoints on MNIST + AGNews |
| Total Size | 125,000+ checkpoints |
| **Sample for H-M1** | **100 checkpoints** (stratified by architecture type) |
| Format | `.pt` PyTorch checkpoint files |
| Layer Types | MultiheadAttention (W_Q, W_K, W_V, W_O), Linear (FFN) |
| Download Method | `git clone https://github.com/MathematicalAI-NUS/Transformer-NFN` + data download |

**Task**: Requires manual clone and data download → generates `data-preparation` task.

### 4.3 Data Preprocessing

```python
# Per-checkpoint preprocessing
from nfn.common import state_dict_to_tensors, network_spec_from_wsfeat

# Load and convert checkpoint to WeightSpaceFeatures
state_dict = torch.load(ckpt_path, map_location='cpu')
wsfeat = state_dict_to_tensors(state_dict, network_spec)
network_spec = network_spec_from_wsfeat(wsfeat)
# No gradient computation — inference/analysis only
```

---

## 5. Functional Requirements

### FR-1: OrbitPEComputer Module Implementation

| Requirement | Description |
|-------------|-------------|
| FR-1.1 | Implement `OrbitPEComputer(nn.Module)` with `compute_orbit_id(weight, layer_type)` and `forward(weight, layer_type)` methods |
| FR-1.2 | Support all three layer types: `"Linear"`, `"Conv2d"`, `"MultiheadAttention"` |
| FR-1.3 | Use **unified code path** — no `if layer_type == "MHA": ...` branches in the core orbit computation |
| FR-1.4 | Output shape: `(cout, token_dim)` matching SANE sequential-PE output shape exactly |
| FR-1.5 | Orbit IDs computed as rank of row norms (permutation-invariant canonical form) |
| FR-1.6 | MHA weight matrices (W_Q, W_K, W_V, W_O) must be head-flattened before orbit computation |

### FR-2: Vanilla SANE Sequential-PE Baseline

| Requirement | Description |
|-------------|-------------|
| FR-2.1 | Implement `SequentialPEBaseline` that replicates SANE's 3D position encoding [n, l, k] |
| FR-2.2 | Baseline and proposed must run on identical checkpoint samples for fair timing comparison |
| FR-2.3 | Timing measurement: `time.perf_counter()` before and after tokenization for each checkpoint |

### FR-3: Timing Benchmark

| Requirement | Description |
|-------------|-------------|
| FR-3.1 | Measure `overhead_ratio = t_orbit / t_vanilla` per checkpoint |
| FR-3.2 | Report `mean_overhead_ratio ± std` across all 200 checkpoints |
| FR-3.3 | Report per-layer-type overhead breakdown (Linear, Conv2d, MHA) |
| FR-3.4 | Single GPU execution (`CUDA_VISIBLE_DEVICES` set; GPU available but computation is CPU-heavy) |

### FR-4: Mechanism Activation Verification

| Requirement | Description |
|-------------|-------------|
| FR-4.1 | Log `"OrbitPE computed for layer {name} (type={layer_type}): dim={orbit_dim}"` for each layer |
| FR-4.2 | Verify `orbit_pe.shape[-1] == expected_dim` for all layers |
| FR-4.3 | Verify `has_arch_branches == False` (code inspection flag) |
| FR-4.4 | Run `verify_orbit_pe_activated()` function from experiment brief |

### FR-5: Visualization

| Requirement | Description |
|-------------|-------------|
| FR-5.1 | Bar chart: `overhead_ratio` per layer type vs 1.2× threshold line (MANDATORY gate figure) |
| FR-5.2 | Box plots: overhead_ratio distribution across 200 checkpoints, grouped by CNN vs Transformer |
| FR-5.3 | Save all figures to `docs/youra_research/20260521_wsl/h-m1/figures/` |

### FR-6: Result Reporting

| Requirement | Description |
|-------------|-------------|
| FR-6.1 | Save metrics JSON: `{computability_rate, unified_codebase, overhead_ratio_mean, overhead_ratio_std, dim_consistent}` |
| FR-6.2 | Generate Phase 4 validation report `04_validation.md` with gate pass/fail determination |

---

## 6. Non-Functional Requirements

| NFR | Description |
|-----|-------------|
| NFR-1 | Runtime ≤ 60 minutes total (100 CNN + 100 Transformer checkpoints) |
| NFR-2 | Single GPU (lowest-memory GPU via `nvidia-smi`) |
| NFR-3 | No Internet access during experiment (all data pre-downloaded) |
| NFR-4 | Reproducible with fixed seed (seed=42 for checkpoint sampling) |
| NFR-5 | Memory usage < 8GB GPU VRAM (CPU-dominant computation) |

---

## 7. Success Criteria (Gate: MUST_WORK)

| Criterion | Threshold | Gate |
|-----------|-----------|------|
| `computability_rate` | == 1.0 (all 200 checkpoints succeed) | PRIMARY |
| `unified_codebase` | == True (no arch-conditional branches) | PRIMARY |
| `overhead_ratio` (mean) | ≤ 1.2 | PRIMARY |
| `dim_consistent` | == True | SECONDARY |

**PASS**: All 3 PRIMARY criteria met → proceed to H-M2
**FAIL**: Any PRIMARY criterion not met → document failure, explore parameterized orbit-PE adapter

---

## 8. Dependencies

### 8.1 Python Packages

```
torch>=1.12.0
numpy>=1.21.0
matplotlib>=3.5.0
scipy>=1.7.0
pyyaml>=6.0
tqdm>=4.62.0
```

### 8.2 External Repositories (Manual Clone Required)

| Repository | Purpose | URL |
|------------|---------|-----|
| AllanYangZhou/nfn | Orbit computation primitives (`WeightSpaceFeatures`, `NPLinear`, `state_dict_to_tensors`) | https://github.com/AllanYangZhou/nfn |
| MathematicalAI-NUS/Transformer-NFN | Transformer Zoo dataset + MHA group structure reference | https://github.com/MathematicalAI-NUS/Transformer-NFN |
| HSG-AIML/SANE | Sequential-PE baseline timing reference | https://github.com/HSG-AIML/SANE |

### 8.3 Base Hypothesis Dependencies (H-E1)

H-M1 is INCREMENTAL on H-E1. The following verified results from H-E1 inform H-M1:
- H-E1 confirmed orbit-PE is accuracy-preserving for CNN + Transformer layers
- H-E1 confirmed nfn library handles all 3 layer types functionally
- H-M1 code may reuse orbit computation utilities validated in H-E1 if they exist

**H-E1 code location**: `docs/youra_research/20260521_wsl/h-e1/code/`

---

## 9. Constraints

| Constraint | Value |
|-----------|-------|
| Sample size | 100 CNN + 100 Transformer checkpoints (mechanism test, not statistical) |
| Timing baseline | Wall-clock only (no GPU profiling needed) |
| No training | Pure inference / computability check |
| Seed | Fixed seed=42 for checkpoint sampling; overhead_ratio does not depend on seed |

---

## 10. Risks

| Risk | Mitigation |
|------|------------|
| MHA weight shape varies by model | Head-flatten before orbit computation; document shape handling |
| nfn library doesn't support Transformer Zoo format | Fallback: manual `state_dict_to_tensors` wrapper |
| Overhead > 1.2× | Optimize orbit computation (vectorize row norm, cache network_spec) |
| Architecture branches required for MHA | Explore parameterized adapter; document as limitation |

---

*Generated by Phase 3 PRD Generation (UNATTENDED — inline execution) from Phase 2C experiment brief*
*Source: docs/youra_research/20260521_wsl/h-m1/02c_experiment_brief.md*
