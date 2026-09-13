# Experiment Design: H-M2

**Date:** 2026-05-21
**Author:** Anonymous
**Hypothesis Statement:** Under weight space analysis on Small CNN Zoo checkpoint trajectories, if weight vectors are projected onto permutation orbit directions and GL orbit directions, then Var_perm / (Var_perm + Var_GL) > 0.60, because NFN's success (τ>0.93) using only permutation equivariance implies that permutation orbits capture the dominant functional variation in model zoo checkpoint geometry. GATE: if ratio < 0.60, pivot to hybrid orbit-PE + GL trace features before H-M3.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Tests whether permutation orbit variance dominates GL orbit variance in CNN Zoo checkpoint geometry.

---

## Workflow Status

**Verification State:** ACTIVE (UNATTENDED mode)
**Prerequisites Satisfied:** H-E1 (PASS), H-M1 (PASS)
**Gate Status:** MUST_WORK — Var_perm / (Var_perm + Var_GL) > 0.60

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED), H-M1 (VALIDATED)

### Gate Condition
**MUST_WORK Gate:**
- Primary success criterion: Var_perm / (Var_perm + Var_GL) > 0.60 across full Small CNN Zoo trajectory set
- Secondary: Ratio stable across CIFAR-10-GS and SVHN-GS model families (not dataset-specific)
- **If PASS (ratio ≥ 0.60):** Proceed to H-M3 with orbit-PE as primary PE strategy
- **If FAIL (ratio < 0.60):** PIVOT — implement hybrid orbit-PE + low-degree GL invariant polynomial traces (tr(W^Q W^{K,T})); re-run H-M3 with hybrid model

---

## Continuation Context

**Continuation from H-M1:** H-M1 validated that orbit-PE computation is architecture-agnostic with overhead 1.167x ± 0.061 (threshold ≤1.2x, unified codebase). This experiment uses the orbit-PE computation module built in H-M1 for the permutation orbit projection component.

### Previous Hypothesis Results (H-M1)
- computability_rate = 1.0 (all 200 checkpoints: 100 CNN + 100 Transformer)
- overhead_ratio_mean = 1.167x ± 0.061 (PASS)
- unified_codebase = True (HAS_ARCH_BRANCHES=False)
- dim_consistent = True (all layer types produce token_dim=64 output)
- Layer coverage: Conv2d (1.168x), Linear (1.168x), MultiheadAttention (1.147x)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Experiment Design (variance decomposition permutation orbit weight space)**
- No domain-relevant matches found — Archon KB contains diffusion model content (similarity ~0.38)
- **Interpretation:** Novel research territory for permutation variance decomposition in weight space — confirmed by H-E1 and H-M1 history

**Query 2: Weight space checkpoint trajectory projection**
- Most relevant: arxiv:2402.19159 (similarity 0.441) — general weight space paper, not specifically about variance decomposition
- No implementation cases for Var_perm / Var_GL decomposition exist in KB

**Query 3: Neural network zoo CNN model property prediction (Kendall tau)**
- No domain-relevant matches
- **Conclusion:** This exact variance decomposition experiment is novel; implementation must be derived from related work (NFN orbit theory + trajectory PCA literature)

### Archon Code Examples

**Query: Permutation orbit projection PyTorch variance**
- No relevant code examples in Archon KB (only diffusion/distributed training code)
- **Fallback:** Relying on Exa GitHub findings (NFN library + loss-landscape trajectory PCA)

### Exa GitHub Implementations

**Repository 1: AllanYangZhou/nfn** (Primary Reference)
- **URL:** https://github.com/AllanYangZhou/nfn
- **Relevance:** Official NFN library — provides permutation orbit structure, WeightSpaceFeatures, NPLinear layers
- **Key Pattern:** `state_dict_to_tensors()` + `WeightSpaceFeatures` for loading CNN Zoo checkpoints; orbit parameter sharing via `orbit index partitioning`
- **Dataset Used:** Small CNN Zoo (CIFAR-10-GS, SVHN-GS) — τ results NFN_HNP: best on both
- **Results:** τ > 0.93 on CNN Zoo using ONLY permutation equivariance (validates Assumption A2)
- **Used For:** Permutation orbit projection basis; CNN Zoo loading pattern

**Repository 2: tomgoldstein/loss-landscape** (trajectory PCA pattern)
- **URL:** https://github.com/tomgoldstein/loss-landscape/blob/master/projection.py
- **Relevance:** `setup_PCA_directions()` and `project_trajectory()` — exact SVD-based trajectory projection pattern needed for variance decomposition
- **Key Code:**
  ```python
  def setup_PCA_directions(args, model_files, w, s):
      # Find PCA directions for optimization path
      # Returns dir_name: h5 file with PCA directions
      ...
  def project_trajectory(dir_file, w, s, dataset, model_name, model_files,
                 dir_type='weights', proj_method='cos'):
      # Project trajectory onto given two directions
      # Cosine projection
  ```
- **Pattern:** Load checkpoints → compute ∆θ(t) = θ(t) − θ(0) → SVD → project → variance fractions
- **Used For:** Core variance decomposition algorithm design

**Repository 3: ModelZoos/ModelZooDataset + wsl-modelzoo** (Dataset Loading)
- **URL:** https://github.com/ModelZoos/ModelZooDataset; https://pypi.org/project/wsl-modelzoo/
- **Key:** `dataset_base.py` PyTorch dataset class; `wsl-modelzoo` CLI for checkpoint download
- **Checkpoint Range:** cnn-small + cifar10: checkpoints 0..50 per model (51 checkpoints per trajectory)
- **Loading Code:**
  ```bash
  modelzoo fetch --zoo core --arch cnn-small --dataset cifar10 --config uniform --seed all --ckpts all
  ```
- **Used For:** Dataset loading specification

**Repository 4: arXiv:2410.04207 (Learning on LoRAs — GL-equivariant processing)**
- **URL:** https://arxiv.org/abs/2410.04207
- **Relevance:** GL orbit structure for weight space (U, V decomposition via SVD); GL orbit projection via orthogonal Procrustes / polar decomposition
- **Key Insight:** GL orbit of W = {gW : g ∈ GL(n)} projected via polar decomposition: W = QS where Q is orthogonal (permutation-like) and S is positive-definite (GL-type). Var_GL estimated via residual after permutation orbit projection.
- **Used For:** GL orbit projection design

**Repository 5: arxiv:2602.23696 / loss-landscape (trajectory PCA analysis)**
- **Relevance:** Uncentered PCA on trajectory drift ∆θ(t) = θ(t) − θ(0); PC1 captures 78-81% of total squared drift. Framework directly applicable to orbit-specific variance decomposition.
- **Used For:** Variance fraction computation method

**Serena Analysis Needed:** false — code patterns sufficiently clear from Exa results.

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a novel analysis module — no official author implementation exists.**

- **Primary:** Custom implementation derived from NFN orbit theory (AllanYangZhou/nfn) + trajectory PCA pattern (tomgoldstein/loss-landscape)
- **Fallback:** scipy.linalg.svd + numpy for projection; pytorch tensor operations for orbit computation
- **Justification:** No prior work computes Var_perm/Var_GL decomposition on CNN Zoo checkpoint trajectories. The experiment DESIGN is novel; implementation borrows projection patterns from loss-landscape and orbit structure from NFN.

**Recommended Implementation Path:**
- Primary: Custom `VarianceDecompositionModule` using H-M1's orbit-PE computation + SVD-based GL orbit projection
- Fallback: Simplified proxy — permutation orbit variance = variance explained by orbit-aligned PCA directions; GL variance = residual
- Justification: H-M1 already built the orbit-PE computation module; this experiment extends it to measure variance fractions on full trajectories.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. NFN orbit structure + trajectory PCA patterns provide unambiguous implementation guidance.

---

## Experiment Specification

### Dataset

**Dataset 1: Small CNN Zoo (CIFAR-10-GS subset) — Primary**
- **Name:** Small CNN Zoo CIFAR-10-GS
- **Type:** standard (real checkpoint dataset from published zoo)
- **Source:** ModelZoos/ModelZooDataset (Schürholt et al., NeurIPS 2022); also via NFN paper [Zhou et al., NeurIPS 2023 Table 2]
- **Download:** `wsl-modelzoo` CLI or modelzoos.cc Zenodo repository
- **Architecture:** cnn-small (Conv2d + Linear + global pooling, ~2.5k params)
- **Checkpoint range:** epochs 0..50 per model (51 checkpoints per trajectory)
- **Models in zoo:** ~1000+ CNN models with varied hyperparameters (learning rate, optimizer, weight decay, dropout, initialization, activation)
- **Splits:** Standard train/val/test split [70, 15, 15] by model; ALL checkpoints (0..50) per model used for trajectory analysis
- **Synthetic data check:** PASSED — standard real-data checkpoint dataset from published research

**Dataset 2: Small CNN Zoo (SVHN-GS subset) — Secondary (cross-dataset stability check)**
- **Name:** Small CNN Zoo SVHN-GS
- **Type:** standard
- **Source:** Same Zenodo repository as CIFAR-10-GS
- **Purpose:** Validate that Var_perm / (Var_perm + Var_GL) ratio is not dataset-specific (secondary success criterion)
- **Architecture:** Same cnn-small architecture
- **Checkpoint range:** epochs 0..50

**Loading Information:**
- Method: wsl-modelzoo CLI (pip install wsl-modelzoo) + ModelZoos dataset_base.py
- Identifier: `core / cnn-small / cifar10 / uniform` and `core / cnn-small / svhn / uniform`
- Code:
  ```bash
  pip install wsl-modelzoo
  modelzoo fetch --zoo core --arch cnn-small --dataset cifar10 --config uniform --seed all --ckpts all --dir ./data/cnn_zoo_cifar10/
  modelzoo fetch --zoo core --arch cnn-small --dataset svhn --config uniform --seed all --ckpts all --dir ./data/cnn_zoo_svhn/
  ```

### Models

#### Baseline Model

**No pretrained model needed for variance decomposition.** This experiment analyzes the geometry of existing CNN Zoo checkpoints — it does not train a new model.

**Variance Decomposition Module (New — Pure Analysis):**
- **Type:** Analysis module (not a trainable model)
- **Components:**
  1. Orbit-PE computation from H-M1 (orbit membership vectors for each weight layer)
  2. Permutation orbit projector: projects weight vectors onto orbit-aligned subspace
  3. GL orbit projector: projects residual onto GL-structured subspace via polar decomposition
  4. Variance ratio calculator: Var_perm / (Var_perm + Var_GL)

**Loading Information:**
- Method: Custom module (builds on H-M1 orbit-PE code)
- Identifier: N/A (new implementation)
- Code: `from orbit_pe import OrbitPEComputer  # from H-M1 implementation`

#### Proposed Model

**Architecture:** Same analysis module — there is no "baseline vs proposed" model distinction here. The experiment measures the variance ratio directly.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Variance Decomposition — Var_perm / (Var_perm + Var_GL)
# Based on: NFN orbit structure (AllanYangZhou/nfn) + trajectory PCA (tomgoldstein/loss-landscape)

class VarianceDecomposer:
    """
    Decomposes CNN Zoo checkpoint trajectory variance into permutation-orbit
    and GL-orbit components. Measures Var_perm / (Var_perm + Var_GL).
    """
    def __init__(self, orbit_pe_computer):
        self.orbit_pe = orbit_pe_computer  # From H-M1

    def flatten_weights(self, state_dict):
        """Flatten all weight tensors to 1D vector. Shape: (P,)"""
        return torch.cat([p.flatten() for p in state_dict.values()])

    def compute_perm_orbit_projection(self, W_flat, orbit_basis):
        """
        Project W onto permutation orbit subspace.
        orbit_basis: (D, P) — top-D orbit-aligned PCA directions from orbit-PE
        Returns: W_perm (projection), Var_perm (scalar)
        """
        coords = orbit_basis @ W_flat          # (D,)
        W_perm = orbit_basis.T @ coords        # (P,) — projection onto orbit subspace
        return W_perm, (coords ** 2).sum()

    def compute_gl_orbit_projection(self, W_layer):
        """
        GL orbit projection via polar decomposition: W = Q * S.
        GL-orbit variation captured by symmetric factor S (scales, not permutations).
        Returns: Var_GL contribution for this layer.
        """
        U, s, Vt = torch.linalg.svd(W_layer, full_matrices=False)
        W_polar_S = (Vt.T * s) @ Vt           # Positive-definite factor S
        W_gl_component = W_polar_S - W_layer   # Residual = GL component
        return (W_gl_component ** 2).sum()

    def compute_trajectory_variance_ratio(self, trajectory):
        """
        trajectory: list of state_dicts (T checkpoints for one model)
        Returns: ratio = Var_perm / (Var_perm + Var_GL)
        """
        # Step 1: Compute orbit-aligned basis from H-M1 orbit-PE vectors
        orbit_basis = self.orbit_pe.get_orbit_basis(trajectory[0])  # (D, P)

        var_perm_total, var_gl_total = 0.0, 0.0
        for state_dict in trajectory:
            W_flat = self.flatten_weights(state_dict)
            _, vp = self.compute_perm_orbit_projection(W_flat, orbit_basis)
            vg = sum(self.compute_gl_orbit_projection(
                p.view(p.shape[0], -1)) for p in state_dict.values() if p.dim() >= 2)
            var_perm_total += vp.item()
            var_gl_total += vg.item()

        ratio = var_perm_total / (var_perm_total + var_gl_total + 1e-8)
        return ratio
```

### Training Protocol

**Note:** This is a pure analysis experiment — no neural network training. The "protocol" is the analysis pipeline.

**Analysis Pipeline:**

**Optimizer:** N/A (no training)

**Checkpoint loading:**
- Load full trajectory per model: epochs 0..50 (51 checkpoints)
- Subsample to ≤50 checkpoints if memory-constrained (following trajectory PCA convention from arXiv:2602.23696)

**Analysis scope:**
- CIFAR-10-GS subset: full available models (all with complete 0..50 trajectories)
- SVHN-GS subset: full available models (secondary stability check)
- Minimum: 200 models per subset to ensure statistical reliability (>500 total trajectory-checkpoint pairs per subset)

**Computation:**
- Per-model: Compute VarianceDecomposer.compute_trajectory_variance_ratio()
- Aggregate: Mean ± std of ratio across all models in zoo

**Seeds:** 1 (deterministic — SVD-based projection is deterministic given checkpoints)

**Expected runtime:** ~10-30 minutes on single GPU (CPU-bound SVD, not GPU-intensive)

**Source:** Trajectory PCA conventions from tomgoldstein/loss-landscape + arXiv:2602.23696

### Evaluation

**Primary Metrics:**

- **Var_perm / (Var_perm + Var_GL) ratio** — primary gate metric
  - Success threshold: ratio > 0.60 (MUST_WORK gate)
  - Failure threshold: ratio < 0.60 → PIVOT to hybrid orbit-PE + GL traces
  - Reported: mean ± std across all model trajectories in CIFAR-10-GS subset

- **Cross-dataset stability** — secondary metric
  - Check: |ratio_CIFAR10 - ratio_SVHN| < 0.10 (stable across datasets)
  - Failure: Large discrepancy suggests dataset-specific effect, not architecture-universal property

**Success Criteria:**
- Var_perm / (Var_perm + Var_GL) > 0.60 (primary, MUST_WORK gate)
- Ratio stable across CIFAR-10 and SVHN subsets (secondary)

**Expected Baseline Performance (from research):**
- NFN achieves τ > 0.93 using ONLY permutation equivariance on CNN Zoo → implies permutation structure captures ≥ 60-70% of predictive variance [Zhou et al., NeurIPS 2023, Table 2]
- Trajectory PCA literature: PC1 captures 78-81% of total squared drift in training trajectories [arXiv:2602.23696] — consistent with permutation dominance hypothesis

**Metrics Loading Information:**
- Task Type: variance_decomposition (statistical analysis, not ML classification)
- Library: `scipy.stats` (no Kendall tau needed here), `torch.linalg.svd`, `numpy`
- Code:
  ```python
  import numpy as np
  ratio_mean = np.mean(ratios)
  ratio_std = np.std(ratios)
  print(f"Var_perm / (Var_perm + Var_GL) = {ratio_mean:.4f} ± {ratio_std:.4f}")
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing Var_perm, Var_GL, and ratio for CIFAR-10-GS and SVHN-GS subsets side by side

#### Additional Figures (LLM Autonomous)
Based on the variance decomposition nature of this experiment:
1. **Trajectory variance ratio histogram** — distribution of per-model ratios across all CNN Zoo models (shows spread around mean)
2. **Ratio vs training epoch** — how Var_perm/Var_GL evolves across the 0..50 checkpoint trajectory (early vs late training)
3. **Per-layer breakdown** — Conv2d vs Linear layer contribution to Var_perm and Var_GL (validates layer-agnostic dominance)
4. **Scatter: ratio vs model accuracy** — check if variance ratio predicts final model accuracy (secondary analysis)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/20260521_wsl/h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Orbit-PE computation module from H-M1 available; SVD-based GL projection implementable | TRUE — H-M1 validated orbit-PE module |
| Mechanism Isolatable | Var_perm and Var_GL computed independently; ratio = Var_perm / (Var_perm + Var_GL) isolates each component | TRUE |
| Baseline Measurable | Baseline = ratio computed on raw (non-projected) variance; comparison: with vs without orbit alignment | TRUE |

### Architecture Compatibility Check

**Required Features:**
- Small CNN Zoo checkpoints with full training trajectories (epochs 0..50)
- cnn-small architecture: Conv2d layers + Linear layers + global pooling (confirmed compatible with NFN orbit structure)
- H-M1 orbit-PE computation module (already validated for Conv2d and Linear layers)

**Incompatible Architectures:**
- Architectures without complete trajectory checkpoints (only final-epoch checkpoints)
- Models with non-standard weight structures not handled by NFN's WeightSpaceFeatures

> ⚠️ If checkpoints are missing trajectory data (only epoch-25 snapshots available), Phase 4 MUST report this and adapt to single-epoch variance estimation.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"Trajectory loaded: N checkpoints for model {model_id}"` | data_loader.py |
| Tensor Shape | orbit_basis shape: (D, P) where D ≤ 64, P = total params | orbit_projector.py:compute_orbit_basis() |
| Metric Delta | ratio > 0.60 indicates permutation dominance confirmed | evaluate.py:compute_variance_ratio() |

**Activation Verification Code (Phase 4 must implement):**
```python
def verify_mechanism_activated(results):
    indicators = {
        "trajectories_loaded": results["n_trajectories"] > 100,
        "orbit_basis_computed": results["orbit_basis_shape"][0] > 0,
        "ratio_computed": 0.0 <= results["var_ratio"] <= 1.0,
        "both_components_nonzero": results["var_perm"] > 0 and results["var_gl"] > 0
    }
    return all(indicators.values()), indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| No trajectory data | All checkpoints at same epoch | FAIL: Load single-epoch zoo; adapt to cross-model variance |
| SVD divergence | NaN in singular values | FAIL: Check for zero-weight layers, add numerical stability |
| Ratio = 0 or 1 | Degenerate projection | FAIL: Orbit basis may be all-zero or spanning all dimensions |
| Memory OOM | >200 models × 51 checkpoints | Subsample to 100 models × 25 checkpoints |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | All verify_mechanism_activated() indicators pass |
| Effect Measurable | ratio ∈ (0, 1), non-degenerate | ratio distribution has std > 0.01 |
| Hypothesis Supported | ratio_mean > 0.60 | np.mean(ratios) > 0.60 across CIFAR-10-GS subset |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (SVD converges, ratios computed for all models)
2. Var_perm / (Var_perm + Var_GL) > 0.60 (mean across CIFAR-10-GS subset)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Result:** No domain-relevant sources found in Archon KB (3 queries executed).
- Queries: "variance decomposition permutation orbit weight space", "weight space checkpoint trajectory projection", "neural network zoo CNN model property prediction Kendall tau"
- All results were diffusion model / unrelated content (similarity < 0.45)
- **Implication:** This experiment is genuinely novel — no prior art in KB.

### B. GitHub Implementations (Exa)

**Repository B.1**: AllanYangZhou/nfn
- **URL:** https://github.com/AllanYangZhou/nfn
- **Query Used:** "AllanYangZhou nfn NFN neural functional network weight space variance decomposition permutation orbit CNN zoo"
- **Relevance:** Official NFN library — permutation orbit structure, WeightSpaceFeatures, CNN Zoo benchmark (τ>0.93)
- **Key Code:**
  ```python
  from nfn.common import state_dict_to_tensors, network_spec_from_wsfeat
  from nfn import layers
  wsfeat = WeightSpaceFeatures(*wts_and_bs)
  network_spec = network_spec_from_wsfeat(wsfeat)
  # orbit parameter sharing: partition θ indices by orbit under group action S
  ```
- **Configuration Extracted:** NFN orbit parameter sharing → basis for permutation orbit projection
- **Their Results:** τ_CIFAR-10-GS > 0.93, τ_SVHN-GS > 0.93 (Table 2, NeurIPS 2023)
- **Used For:** Permutation orbit basis design; CNN Zoo dataset specification

**Repository B.2**: tomgoldstein/loss-landscape (projection.py)
- **URL:** https://github.com/tomgoldstein/loss-landscape/blob/master/projection.py
- **Query Used:** "weight space PCA variance decomposition model zoo checkpoint trajectories PyTorch projection"
- **Key Code:**
  ```python
  def setup_PCA_directions(args, model_files, w, s):
      # SVD on T×P matrix of checkpoint deltas ∆θ(t) = θ(t) − θ(0)
      # Returns PCA directions (explained variance fractions)
  def project_trajectory(dir_file, w, ...):
      # Project each checkpoint onto PCA directions via cosine projection
  ```
- **Configuration Extracted:** Uncentered PCA on drift matrix; cosine projection method
- **Used For:** Core trajectory variance decomposition algorithm

**Repository B.3**: ModelZoos/ModelZooDataset + wsl-modelzoo
- **URL:** https://github.com/ModelZoos/ModelZooDataset; https://pypi.org/project/wsl-modelzoo/
- **Query Used:** "HSG-AIML SANE weight tokenizer Small CNN Zoo checkpoint loading PyTorch"
- **Key Code:**
  ```bash
  modelzoo fetch --zoo core --arch cnn-small --dataset cifar10 --config uniform --seed all --ckpts all
  ```
- **Configuration Extracted:** Checkpoint range 0..50 for cnn-small; dataset_base.py PyTorch class
- **Used For:** Dataset loading specification; checkpoint trajectory structure

**Repository B.4**: arXiv:2410.04207 (Learning on LoRAs)
- **URL:** https://arxiv.org/abs/2410.04207
- **Key Insight:** GL orbit symmetry (invertible matrices) vs permutation symmetry; GL projection via SVD polar decomposition (W = Q * S where Q is orthogonal, S is positive-definite)
- **Used For:** GL orbit projection design (polar decomposition approach)

**Repository B.5**: arXiv:2602.23696 (Trajectory PCA)
- **Relevance:** PC1 captures 78-81% of total squared drift in training trajectories; uncentered SVD on ∆θ(t) matrix
- **Used For:** Variance fraction estimation methodology; subsample to ≤100 checkpoints convention

### C. Code Analysis (Serena)
**Serena Analysis:** Not performed — code from search results was sufficiently clear.

### D. Previous Hypothesis Context
**Source:** Phase 4 Validation Report — H-M1
- **File:** `docs/youra_research/20260521_wsl/h-m1/04_validation.md`
- **Reused Components:**
  - orbit-PE computation module (orbit_pe_computer) — validated for Conv2d, Linear, MultiheadAttention
  - CNN Zoo loading pattern (100 checkpoints per architecture type)
  - nfn library integration (WeightSpaceFeatures, state_dict_to_tensors)
- **Why Reused:** H-M1 built and validated the orbit-PE infrastructure; H-M2 extends it to measure variance fractions on full trajectory data (not just single-checkpoint overhead test)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: Small CNN Zoo CIFAR-10-GS | GitHub + Paper | NFN [Zhou et al. 2023] Table 2; B.3 (wsl-modelzoo) |
| Dataset: Small CNN Zoo SVHN-GS | GitHub + Paper | NFN [Zhou et al. 2023] Table 2; B.3 (wsl-modelzoo) |
| Checkpoint trajectory range (0..50) | GitHub CLI docs | B.3 (wsl-modelzoo checkpoint range table) |
| Permutation orbit projection design | GitHub library | B.1 (AllanYangZhou/nfn orbit parameter sharing) |
| GL orbit projection (polar decomposition) | arXiv | B.4 (arXiv:2410.04207 GL orbit structure) |
| Trajectory variance decomposition algorithm | GitHub code | B.2 (tomgoldstein projection.py, SVD approach) |
| Subsample to ≤100 checkpoints | arXiv | B.5 (arXiv:2602.23696, trajectory PCA convention) |
| Core mechanism pseudo-code | All Exa findings | B.1 orbit structure + B.2 projection pattern |
| Evaluation: ratio > 0.60 threshold | Phase 2B | 02b_verification_plan.md Section 2.2 H-M2 |
| Evaluation: cross-dataset stability | Phase 2B | 02b_verification_plan.md Section 2.2 H-M2 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-21T02:26:37Z

### Workflow History for This Hypothesis
- 2026-05-20T23:35:00Z: Phase 2B completed; H-M2 identified as MUST_WORK gate for full pipeline
- 2026-05-21T02:26:37Z: H-M2 set to IN_PROGRESS; Phase 2C started (external loop)
- 2026-05-21T02:26:37Z: Phase 2C experiment design started (UNATTENDED mode)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (3 KB queries, 1 code query — no domain matches), Exa (5 queries, 5 repos/papers found), Serena (skipped — clear code patterns)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
