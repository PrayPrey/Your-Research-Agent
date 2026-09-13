# Product Requirements Document: H-E1
# OrbitVar Measurement — DeepSets & NFN Encoders on ModelZooDataset CIFAR10-GS

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-03
**Author:** Anonymous
**Source:** 02c_experiment_brief.md

---

## 1. Executive Summary

This experiment validates the core existence claim: architecturally invariant weight encoders (DeepSets sum pooling C2, NFN structured equivariance C3) achieve mean OrbitVar < 1e-6 on the ModelZooDataset CIFAR10-GS benchmark under S_16³ functional permutations. This contrasts with CISE (C1, OrbitVar = 0.010333). The experiment is a pure measurement study — no gradient-based training — computing the variance of encoder outputs over 50 functional permutations per model across 100 CNN models.

---

## 2. Problem Statement

Weight encoders for model zoo datasets must be invariant to functional permutations of network weights — i.e., permutations that leave the network's computed function unchanged. Standard encoders (e.g., CISE) exhibit high within-orbit variance (OrbitVar = 0.010333), polluting representations with symmetry noise. Architecturally invariant encoders (DeepSets, NFN) should achieve OrbitVar ≈ 0 by construction.

**Gate Condition (MUST_WORK):** mean OrbitVar(C2) < 1e-6 AND mean OrbitVar(C3) < 1e-6. Failure halts the pipeline.

---

## 3. Functional Requirements

### FR-1: Dataset Loading
- Load `dataset_cifar_small_hyp_rand.pt` from Zenodo DOI 10.5281/zenodo.6620868
- Support reconstruction of CNN model state dicts using `index_dict.json`
- CNN architecture: 3 conv layers (C=16 channels), 1 dense layer, AdaptiveAvgPool2d
- Expose weight tensors per model for encoder input

### FR-2: Functional Permutation Generator
- Implement S_16³ coupled row-column permutations (DWSNet Eq. 5):
  - Simultaneously permute rows of W^(i) AND columns of W^(i+1) for adjacent conv layers
  - Support K=50 random functional permutations per model
- **Mandatory pre-run audit:** verify ||f_v(x) - f_{π·v}(x)||_∞ ≤ 1e-6 for random x ∈ [0,1]^(3,32,32)

### FR-3: C2 Encoder — DeepSets Sum Pooling
- Implement `DeepSetsChannelEncoder` per conv layer:
  - `phi`: MLP mapping per-channel weight vector → hidden embedding
  - Sum aggregation over C=16 output channels (permutation-invariant by Theorem 2)
  - `rho`: post-aggregation MLP to embed_dim
- Concatenate per-layer embeddings to form full weight representation
- No argmax/argsort over channel dim (would break invariance)

### FR-4: C3 Encoder — NFN NF-Layers
- Install and use official `nfn` library (`pip install nfn`)
- Build encoder using `layers.NPLinear` + `layers.HNPPool` (permutation-invariant pooling)
- Construct `WeightSpaceFeatures` via `state_dict_to_tensors(state_dict)`
- Verify CNN compatibility: `nn.AdaptiveAvgPool2d(1)` present in CIFAR10-GS CNN

### FR-5: OrbitVar Computation
- For each model v in {1..100}:
  - Apply K=50 S_16³ permutations → encode each → collect K embeddings
  - OrbitVar(v) = Var_π[enc(π·W_v)] (scalar mean over embedding dimensions)
- Compute mean_OrbitVar and max_OrbitVar for C2 and C3
- Log per-model orbit variance for debugging

### FR-6: Baseline Reference
- Use pre-established CISE OrbitVar = 0.010333 (BUILD_ON from sh1 PASS)
- Do NOT re-run CISE encoder — reference value only

### FR-7: Visualization
- **Required:** OrbitVar bar chart — C2 vs C3 vs CISE(C1), log-scale y-axis, horizontal threshold line at 1e-6
- **Optional (LLM autonomous):**
  - PCA scatter of encoder outputs for 10 models × 50 permutations
  - Violin plot of per-model OrbitVar distribution for C2 and C3
- Save all figures to `h-e1/figures/`

### FR-8: Results Reporting
- Print mean_OrbitVar and max_OrbitVar for C2 and C3
- Print PASS/FAIL gate result
- Save results to `h-e1/results/orbit_var_results.json`

---

## 4. Data Specification

### Primary Dataset
| Field | Value |
|-------|-------|
| Name | ModelZooDataset CIFAR10-GS |
| Source | Zenodo DOI 10.5281/zenodo.6620868 |
| File | `dataset_cifar_small_hyp_rand.pt` |
| Size | ~100 CNN models with CIFAR-10 test accuracy labels |
| Architecture | 3-conv (C=16), 1-dense, AdaptiveAvgPool2d |
| Label | test accuracy (float, 0–1) |
| Download | Manual — Zenodo requires browser/CLI download |
| Local path | `data/dataset_cifar_small_hyp_rand.pt` |

**Loading code:**
```python
import torch
dataset = torch.load("data/dataset_cifar_small_hyp_rand.pt")
# dataset[i] = (weight_vector, accuracy_label)
```

### Supporting Files
| File | Source | Purpose |
|------|--------|---------|
| `index_dict.json` | Zenodo 6620868 | Map weight vector indices to layer names |

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed = 1 for all permutation sampling
- Deterministic encoder forward passes (no dropout during measurement)

### NFR-2: Numerical Precision
- OrbitVar computed in float64 for precision
- Functional audit tolerance: 1e-6

### NFR-3: Performance
- Total encoder forward passes: 5,000 (100 models × 50 permutations)
- Expected runtime: < 10 minutes on CPU (no GPU required for measurement)

### NFR-4: Code Quality
- Single script execution: `python run_experiment.py`
- No partial results — all 100 models must complete before reporting

---

## 6. Success Criteria

| Criterion | Target | Condition |
|-----------|--------|-----------|
| Functional audit | max_diff ≤ 1e-6 | Pre-condition (HARD BLOCK if fails) |
| mean OrbitVar(C2) | < 1e-6 | MUST_WORK gate |
| mean OrbitVar(C3) | < 1e-6 | MUST_WORK gate |
| max OrbitVar(C2) | < 1e-4 | Secondary |
| max OrbitVar(C3) | < 1e-4 | Secondary |
| Delta vs CISE | ≥ 4 orders magnitude | Directional |

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=1.12.0
numpy>=1.21.0
nfn          # pip install nfn (AllanYangZhou/nfn)
matplotlib>=3.5.0
scipy>=1.7.0
```

### 7.2 External Repositories (Reference Only)
- AllanYangZhou/nfn: official NFN implementation (pip-installable)
- AvivNavon/DWSNets: S_16³ permutation definition (Eq. 5)
- ModelZoos/ModelZooDataset: dataset loader code reference

### 7.3 Pre-established Baselines (BUILD_ON)
- CISE OrbitVar = 0.010333 (sh1 PASS result — not re-run)

---

## 8. Out of Scope

- Training new CNN models
- Supervised learning / regression on weight space
- Comparison beyond C2 and C3 (additional encoders are H-M1+ scope)
- GPU optimization
- Hyperparameter tuning for encoders (phi/rho MLP dimensions are fixed)

---

## 9. Assumptions and Risks

| Assumption | Risk | Mitigation |
|------------|------|------------|
| NFN compatible with 3-conv+AdaptiveAvgPool2d CNN | Medium | Verify via `network_spec_from_wsfeat` before full run |
| Zenodo dataset accessible for download | Low | Document DOI; provide wget command |
| DeepSets sum pooling achieves OrbitVar ≈ 0 | Low | Guaranteed by Theorem 2 (mathematical proof) |
| CISE OrbitVar = 0.010333 valid as baseline | Low | BUILD_ON from validated sh1 result |

---

*stepsCompleted: [executive_summary, problem_statement, functional_requirements, data_specification, nfr, success_criteria, dependencies]*
