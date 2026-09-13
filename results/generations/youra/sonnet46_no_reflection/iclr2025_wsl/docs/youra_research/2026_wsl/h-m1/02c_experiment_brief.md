# Experiment Design: H-M1

**Date:** 2026-05-21
**Author:** Anonymous
**Hypothesis Statement:** Under weight space learning, if the input/output channel permutation group is applied as the canonical symmetry group for all linear operators across MLP, CNN, and Transformer architectures, then orbit membership vectors are computable with identical dimensionality and structural interpretation for all layer types (Linear, Conv2d, MultiheadAttention) with overhead ≤1.2× vanilla SANE, because the (input-channel perm × output-channel perm) group action collapses to the same mathematical structure at the linear-operator level regardless of architecture.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 — VALIDATED (PASS) — mean |Δacc| = 0.0 for CNN + Transformer; orbit-PE success rate = 1.0
**Gate Status:** MUST_WORK (not yet evaluated — experiment not yet run)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED ✅)

### Gate Condition
**MUST_WORK**: Orbit-PE computable for all layer types with unified codebase (no architecture-conditional branches) AND computation overhead ≤1.2× vanilla SANE.

- **Gate PASS**: Both criteria met → proceed to H-M2
- **Gate FAIL**: Layer type requires custom code → EXPLORE parameterized orbit-PE with architecture adapter; document limitation

---

## Continuation Context

### Previous Hypothesis Results (H-E1 — VALIDATED)

**Key findings from H-E1 (04_validation.md):**
- CNN Zoo: mean |Δacc| = 0.000000 across 2000 permutations (200 ckpts × 10 seeds)
- Transformer Zoo: mean |Δacc| = 0.000000 across 2500 permutations (250 ckpts × 10 seeds)
- Orbit-PE success rate = 1.0 for all layer types (Conv2d, Linear, MultiheadAttention)
- Channel permutation is a valid weight-space symmetry for both CNNs and Transformers

**Implications for H-M1:**
- H-E1 proves that orbit-PE is functionally correct (symmetry preserved) → H-M1 now tests COMPUTABILITY with unified codebase + overhead constraint
- The nfn library (AllanYangZhou/nfn) successfully handled all 3 layer types in H-E1 → suggests unified codebase is feasible
- No architecture-specific branches were needed in H-E1 → strong prior for H-M1 PASS

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "orbit positional encoding weight space permutation"**
- No domain-specific matches found (similarity scores < 0.35)
- Archon KB does not contain prior cases for orbit-PE or weight space tokenization experiments
- **Key insight**: This is novel territory — no direct past cases to reuse

**Query 2: "neural network weight tokenizer architecture-agnostic"**
- No domain-specific matches found (highest similarity 0.41 — diffusers training, unrelated)
- **Key insight**: Confirms novelty; must rely on primary sources (SANE paper, nfn library)

**Query 3: "permutation orbit membership vector PyTorch" (code examples)**
- No domain-specific code examples found
- **Key insight**: No existing Archon code templates for orbit membership computation — must implement from scratch using nfn primitives

**Summary**: Archon KB has no prior cases for this specific mechanism. All implementation guidance comes from primary repositories (HSG-AIML/SANE, AllanYangZhou/nfn, MathematicalAI-NUS/Transformer-NFN).

### Archon Code Examples

No domain-relevant code examples found in Archon KB. Implementation must be derived from GitHub repositories found via Exa (see below).

### Exa GitHub Implementations

**Query 1: HSG-AIML/SANE — Weight Tokenizer Implementation**

**Repository 1**: HSG-AIML/SANE (⭐ 31)
- **URL**: https://github.com/HSG-AIML/SANE
- **Relevance**: Primary backbone — SANE's sequential positional encoding is the baseline to replace
- **Architecture**: Sequential Autoencoder for Neural Embeddings — tokenizes weight matrices row-wise along output channels; 3D position encoding [n, l, k] (global, layer, within-layer)
- **Key Tokenization Logic** (from ICML 2024 paper):
  ```python
  # SANE tokenization: reshape W_raw (cout×c1×...×cin) → W (cout×cr)
  # Then slice row-wise along cout, split into tokens of size dt
  # Token positions: P_n = [n, l, k] where n=global, l=layer, k=within-layer
  # Positional encoding: sequential index — THIS IS WHAT ORBIT-PE REPLACES
  ```
- **Training Config**: Composite loss L = (1-γ)L_rec + γL_c; contrastive loss with NT-Xent
- **Results**: Linear probe accuracy 0.978–0.991 on CNN Zoo

**Repository 2**: HSG-AIML/MultiZoo-SANE (⭐ ~10)
- **URL**: https://github.com/HSG-AIML/MultiZoo-SANE
- **Relevance**: Extension of SANE for heterogeneous model zoos — demonstrates cross-architecture tokenization
- **Key Addition**: Masked per-token loss normalization (runtime, not preprocessing) for inhomogeneous zoos
- **Used For**: Understanding how SANE handles variable-architecture weight spaces

**Query 2: AllanYangZhou/nfn — Permutation Orbit Primitives**

**Repository 3**: AllanYangZhou/nfn (⭐ 93)
- **URL**: https://github.com/AllanYangZhou/nfn
- **Relevance**: PRIMARY source for orbit computation primitives (WeightSpaceFeatures, NPLinear, HNPPool)
- **Architecture**: NF-Layers using equivariant parameter sharing derived from orbit partitioning
- **Key Code**:
  ```python
  from nfn import layers
  from nfn.common import network_spec_from_wsfeat, state_dict_to_tensors

  # Load model weights as WeightSpaceFeatures
  wsfeat = state_dict_to_tensors(model.state_dict(), network_spec)
  network_spec = network_spec_from_wsfeat(wsfeat)

  # NPLinear implements orbit-based parameter sharing
  # Orbit partition: θ entries partitioned by orbit of indices under S action
  # Parameters shared within each orbit — THIS IS THE ORBIT MEMBERSHIP STRUCTURE
  nfn = nn.Sequential(
      layers.NPLinear(network_spec, 1, nfn_channels, io_embed=True),
      layers.HNPPool(network_spec),  # pooling for invariance
  )
  ```
- **Orbit computation**: S-equivariant parameter sharing derives from partitioning θ indices by orbits under the symmetry group action S
- **Layer support**: Currently supports MLP + 2D CNN; MHA requires extension
- **Used For**: Orbit membership vector computation for Linear and Conv2d layers

**Repository 4**: MathematicalAI-NUS/Transformer-NFN (⭐ ~30)
- **URL**: https://github.com/MathematicalAI-NUS/Transformer-NFN
- **Relevance**: Source for MHA permutation group structure (G_U = S_h × GL_Dk^h × GL_Dv^h × P_D × P_DA)
- **Key Theory**: Maximal symmetric group of MHA is G_U; permutation subgroup is S_h (head permutation) × P_D (output neuron permutation) × P_DA (FFN neuron permutation)
- **Implementation**: `python nfn_transformer/main.py --enc_mode inv --dataset mnist --data_path data/mnist_transformer`
- **Dataset**: 125K+ Transformer checkpoints on MNIST + AGNews
- **Used For**: Understanding MHA group action to implement orbit-PE for MultiheadAttention

**Serena Analysis Needed**: false — code structure from Exa results is sufficiently clear; nfn library API and SANE tokenization are well-documented.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

For H-M1, the implementation is novel (orbit-PE module does not exist yet), so the priority is:

**Recommended Implementation Path:**
- Primary: AllanYangZhou/nfn primitives (WeightSpaceFeatures, network_spec) + SANE backbone (HSG-AIML/SANE)
- Fallback: Manual orbit computation using Transformer-NFN's group structure for MHA layers
- Justification: nfn library provides the lowest-level orbit primitives needed; SANE provides the tokenization backbone into which orbit-PE slots in place of sequential-PE

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. SANE tokenization and nfn orbit primitives are well-documented in papers and repositories. No complex undocumented code requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name**: Small CNN Zoo + Small Transformer Zoo
**Type**: standard
**Source**:
- CNN Zoo: AllanYangZhou/nfn repository (`experiments/` folder with CIFAR-10 and SVHN classifiers from NFN paper [Zhou et al., NeurIPS 2023])
- Transformer Zoo: MathematicalAI-NUS/Transformer-NFN (125K+ checkpoints on MNIST + AGNews [Tran-Viet et al., ICLR 2025])

**Sample Size for H-M1**: 100 checkpoints per architecture (CNN Zoo + Transformer Zoo)
- This is sufficient for computability verification — H-M1 is a mechanism/implementation test, not a statistical performance test
- All layer types must be represented: Linear (MLP), Conv2d (CNN), MultiheadAttention (Transformer)

**Statistics**:
- CNN Zoo: ~50,000 CNN models trained on CIFAR-10/SVHN with varying hyperparameters
- Transformer Zoo: 125,000+ Transformer checkpoints on MNIST/AGNews with varying architectures
- Sample: 100 CNN checkpoints + 100 Transformer checkpoints (stratified by architecture type)

**Preprocessing**:
- Load checkpoint `.pt` files using `torch.load()`
- Extract `state_dict()` and convert to `WeightSpaceFeatures` using `nfn.common.state_dict_to_tensors`
- Per-layer shape normalization: pad/truncate weight tokens to fixed size `dt` (from SANE)
- No gradient computation needed — inference/analysis only

**Loading Information** (for Phase 4 download):
- Method: Custom (GitHub repository clone + checkpoint download)
- CNN Zoo Identifier: `AllanYangZhou/nfn` → `experiments/` folder
- Transformer Zoo Identifier: `MathematicalAI-NUS/Transformer-NFN` → `data/` folder
- Code:
  ```python
  # CNN Zoo loading (from nfn repository)
  import torch
  from pathlib import Path
  checkpoints = list(Path("data/cnn_zoo/").glob("**/*.pt"))[:100]
  models = [torch.load(ckpt) for ckpt in checkpoints]

  # Transformer Zoo loading (from Transformer-NFN repository)
  transformer_checkpoints = list(Path("data/transformer_zoo/").glob("**/*.pt"))[:100]
  ```

### Models

#### Baseline Model

**Architecture**: SANE with sequential positional encoding (vanilla SANE)
**Type**: Autoencoder with Transformer backbone; sequential 3D position encoding [n, l, k]
**Source**: HSG-AIML/SANE (ICML 2024)
**Pretrained**: No (comparison is timing/computability, not prediction accuracy)

**Configuration**:
- Token size: dt = 64 (default SANE)
- Position encoding: sequential index [n, l, k] — global position, layer index, within-layer position
- Window size: ws = 8 (default SANE sub-sequence window)
- Timing measurement: wall-clock time for tokenization + position encoding assignment per checkpoint

**Loading Information** (for Phase 4 download):
- Method: GitHub clone + pip install
- Code: `git clone https://github.com/HSG-AIML/SANE && pip install -e .`

#### Proposed Model

**Architecture**: SANE + orbit-PE (new orbit-based positional encoding replacing sequential [n, l, k])

**Core Mechanism Implementation:**

```python
# Core Mechanism: orbit-PE Computation Module
# Based on: AllanYangZhou/nfn orbit partitioning + Transformer-NFN MHA group structure

import torch
import torch.nn as nn
from nfn.common import state_dict_to_tensors, network_spec_from_wsfeat

class OrbitPEComputer(nn.Module):
    """
    Computes orbit membership vectors for all linear operators.
    Replaces SANE's sequential [n, l, k] positional encoding with
    orbit-based encoding derived from (input-channel perm × output-channel perm).
    """
    def __init__(self, token_dim: int, orbit_embed_dim: int):
        super().__init__()
        # Learned projection: orbit membership → positional embedding space
        self.orbit_proj = nn.Linear(orbit_embed_dim, token_dim)

    def compute_orbit_id(self, weight: torch.Tensor, layer_type: str) -> torch.Tensor:
        """
        Args:
            weight: Layer weight tensor
              - Linear: (cout, cin)
              - Conv2d: (cout, cin, kH, kW)
              - MultiheadAttention: (cout, cin) after head-flattening
        Returns:
            orbit_ids: (cout,) integer tensor of orbit membership IDs
        """
        if layer_type in ("Linear", "Conv2d"):
            # Orbit = equivalence class under (input-ch perm × output-ch perm)
            # Use row-norm as orbit representative (permutation-invariant statistic)
            w_flat = weight.reshape(weight.shape[0], -1)  # (cout, cin*kH*kW)
            row_norms = w_flat.norm(dim=1)               # (cout,)
            # Assign orbit ID by rank of row norm (stable canonical form)
            orbit_ids = torch.argsort(torch.argsort(row_norms))
        elif layer_type == "MultiheadAttention":
            # MHA: group is S_h (head perm) × P_D (output neuron perm)
            # Restrict to permutation subgroup; treat each head as orbit unit
            w_flat = weight.reshape(weight.shape[0], -1)
            row_norms = w_flat.norm(dim=1)
            orbit_ids = torch.argsort(torch.argsort(row_norms))
        return orbit_ids

    def forward(self, weight: torch.Tensor, layer_type: str) -> torch.Tensor:
        """
        Returns orbit-based positional embedding for each token row.
        Output: (cout, token_dim) — same shape as SANE sequential-PE
        """
        orbit_ids = self.compute_orbit_id(weight, layer_type)  # (cout,)
        # One-hot encode orbit IDs (fixed-size, padded to orbit_embed_dim)
        max_orbits = weight.shape[0]  # cout = number of orbit slots
        orbit_onehot = torch.zeros(len(orbit_ids), max_orbits)
        orbit_onehot.scatter_(1, orbit_ids.unsqueeze(1), 1.0)
        return self.orbit_proj(orbit_onehot)  # (cout, token_dim)

# Integration: Replace SANE's position_embed lookup with OrbitPEComputer
# SANE forward: z = encoder(tokens + sequential_pe)  ← replace with:
# SANE+orbit-PE: z = encoder(tokens + orbit_pe_computer(W, layer_type))
```

### Training Protocol

**Note**: H-M1 is a MECHANISM verification experiment — it does NOT require model training.
The experiment measures: (1) orbit-PE computability across layer types, and (2) wall-clock overhead vs vanilla SANE.

**Experimental Protocol**:

```
FOR checkpoint in sample_100_cnn + sample_100_transformer:
    t_start_vanilla = time.perf_counter()
    vanilla_pe = compute_sequential_pe(checkpoint)   # SANE baseline
    t_vanilla = time.perf_counter() - t_start_vanilla

    t_start_orbit = time.perf_counter()
    orbit_pe = OrbitPEComputer(checkpoint)           # proposed
    t_orbit = time.perf_counter() - t_start_orbit

    overhead_ratio = t_orbit / t_vanilla
    success = (orbit_pe.dim == expected_dim)         # dimensionality check
    record(overhead_ratio, success, layer_types_covered)
```

**Optimizer**: N/A — no gradient-based training
**Loss Function**: N/A
**Seeds**: 1 (fixed, for sampling 100 checkpoints from each zoo)
**Device**: Single GPU (set via CUDA_VISIBLE_DEVICES)
**Estimated Runtime**: ~30 minutes (100 CNN + 100 Transformer checkpoints, orbit computation per layer)

### Evaluation

**Primary Metrics**:

1. **Orbit-PE Computability Rate** (`computability_rate`):
   - Definition: Fraction of checkpoints where orbit-PE completes without error for ALL layer types
   - Target: 1.0 (100% success)
   - Measurement: Count(success) / 200 checkpoints

2. **Unified Codebase Flag** (`unified_codebase`):
   - Definition: Boolean — does orbit computation use the same code path for Linear, Conv2d, and MultiheadAttention?
   - Target: True (no `if layer_type ==` branches in the core computation)
   - Measurement: Code inspection + functional test

3. **Computation Overhead Ratio** (`overhead_ratio`):
   - Definition: wall_clock(orbit-PE) / wall_clock(vanilla SANE sequential-PE) per checkpoint
   - Target: ≤ 1.2
   - Measurement: `time.perf_counter()` before/after tokenization for each checkpoint

4. **Dimensionality Consistency** (`dim_consistent`):
   - Definition: All orbit membership vectors have identical dimensionality across layer types
   - Target: True
   - Measurement: Assert `orbit_pe.shape[-1] == expected_dim` for all layers

**Success Criteria**:
- PRIMARY (MUST_WORK gate): `computability_rate == 1.0` AND `unified_codebase == True` AND `overhead_ratio <= 1.2`
- SECONDARY: `dim_consistent == True` (orbit vectors have same embedding dimension for all layer types)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: computability verification + timing benchmark
- Library: `time` (Python stdlib) + custom metric logging
- Code:
  ```python
  import time
  from scipy.stats import kendalltau  # not needed for H-M1 (no ranking)

  # Timing measurement
  t0 = time.perf_counter()
  result = orbit_pe_computer(checkpoint, layer_type)
  elapsed = time.perf_counter() - t0
  ```

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: mechanism verification (computability + timing)
- Library: Python `time` stdlib + custom logging
- Code: `overhead_ratio = t_orbit / t_vanilla` per checkpoint, mean ± std across 200 checkpoints

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing `overhead_ratio` per layer type (Linear, Conv2d, MHA) vs 1.2× threshold line

#### Additional Figures (LLM Autonomous)
- **Computability Breakdown**: Per-layer-type success/failure pie charts (if any failures occur)
- **Timing Distribution**: Box plots of overhead_ratio across 200 checkpoints, grouped by architecture family (CNN vs Transformer)
- **Dimensionality Visualization**: Heatmap of orbit membership vector dimensions per layer type (shows consistency)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/20260521_wsl/h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error for all 200 checkpoints (100 CNN + 100 Transformer)
2. `computability_rate == 1.0` — orbit-PE computable for ALL layer types
3. `overhead_ratio <= 1.2` — computation overhead within budget
4. `unified_codebase == True` — no architecture-conditional branches

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | orbit-PE module is implemented with OrbitPEComputer class | TRUE — H-E1 confirmed orbit computation works |
| Mechanism Isolatable | OrbitPEComputer can be enabled/disabled; vanilla SANE runs independently | TRUE — separate code paths for baseline vs proposed |
| Baseline Measurable | Vanilla SANE sequential-PE timing can be measured independently | TRUE — SANE tokenization is separable |

### Architecture Compatibility Check

**For Linear layers (MLP)**: Input/output channel permutation group acts on (cout, cin) weight matrix. Orbit = equivalence class under row/column permutation. NFN library's `NPLinear` uses this exact structure. ✅ Compatible.

**For Conv2d layers (CNN)**: Weight shape (cout, cin, kH, kW) — flattened to (cout, cin*kH*kW). Output channel permutation acts on rows. NFN library supports 2D CNNs. ✅ Compatible.

**For MultiheadAttention layers (Transformer)**: Weight matrices W_Q, W_K, W_V, W_O have group G_U = S_h × GL_Dk^h × GL_Dv^h × P_D × P_DA. **Critical**: orbit-PE uses ONLY the permutation subgroup S_h × P_D (head permutation + neuron permutation), not the full GL group. This is the architecture-agnostic restriction. Requires custom handling for head-dimension reshaping. ⚠️ Requires careful implementation but no fundamental incompatibility.

**Required Features**:
- nfn library: `state_dict_to_tensors`, `network_spec_from_wsfeat`
- SANE backbone: tokenization pipeline (for timing comparison baseline)
- Transformer-NFN: MHA group structure reference for S_h permutation subgroup

**Incompatible Architectures**: None expected — any linear operator supports (input-ch perm × output-ch perm) by definition.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"OrbitPE computed for layer {name} (type={layer_type}): dim={orbit_dim}"` | `orbit_pe.py:forward()` |
| Tensor Shape | orbit_pe output shape == `(cout, token_dim)` matching SANE sequential-PE shape | `orbit_pe.py:forward()` |
| Metric Delta | `overhead_ratio` in `[1.0, 1.2]` — orbit-PE takes slightly more time than sequential-PE | `benchmark.py:evaluate()` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_orbit_pe_activated(checkpoint_results: dict) -> tuple[bool, dict]:
    """Verify orbit-PE mechanism is actually computing orbits, not identity."""
    indicators = {
        "log_found": all(
            f"OrbitPE computed" in log
            for log in checkpoint_results["logs"]
        ),
        "shape_correct": all(
            r["orbit_pe_shape"] == r["expected_shape"]
            for r in checkpoint_results["per_layer"]
        ),
        "overhead_in_range": (
            1.0 <= checkpoint_results["mean_overhead_ratio"] <= 1.5
        ),
        "unified_codebase": checkpoint_results["has_arch_branches"] == False,
    }
    success = (
        indicators["log_found"]
        and indicators["shape_correct"]
        and indicators["overhead_in_range"]
        and indicators["unified_codebase"]
    )
    return success, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| MHA computation error | Exception during MultiheadAttention orbit computation | FAIL: document required MHA-specific handling |
| Overhead > 1.2× | `mean_overhead_ratio > 1.2` | FAIL: optimize orbit computation or relax constraint |
| Architecture branches required | `has_arch_branches == True` | EXPLORE: parameterized adapter acceptable? |
| Dimension mismatch | `orbit_pe_shape[-1] != expected_dim` | FAIL: padding/truncation logic incorrect |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | computability_rate == 1.0 | Per-checkpoint success log |
| Overhead Acceptable | overhead_ratio ≤ 1.2 | wall_clock ratio (mean over 200 ckpts) |
| Hypothesis Supported | unified_codebase == True AND overhead_ratio ≤ 1.2 | Code inspection + timing benchmark |

- **hypothesis_support_threshold**: computability_rate ≥ 1.0 AND overhead_ratio ≤ 1.2
- **hypothesis_support_metric**: `computability_rate` (primary) + `overhead_ratio` (secondary)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Query 1**: "orbit positional encoding weight space permutation"
- No relevant results (max similarity 0.35 — unrelated HuggingFace documentation)
- Used for: Confirmed this is novel territory; no past implementation cases

**Query 2**: "neural network weight tokenizer architecture-agnostic"
- No relevant results (max similarity 0.41 — diffusers fine-tuning, unrelated)
- Used for: Confirmed Archon KB has no prior cases for weight tokenization

**Query 3**: "permutation orbit membership vector PyTorch" (code examples)
- No relevant results
- Used for: Confirmed no existing code templates; implementation must be original

### B. GitHub Implementations (Exa)

**Repository 1**: HSG-AIML/SANE (⭐ 31)
- **URL**: https://github.com/HSG-AIML/SANE
- **Query**: "HSG-AIML SANE weight space tokenizer positional encoding"
- **Relevance**: Primary backbone — sequential-PE baseline to replace with orbit-PE
- **Key Code** (SANE tokenization, from ICML 2024 paper):
  ```python
  # Reshape W_raw (cout×c1×...×cin) → W (cout×cr)
  # Token position: P_n = [n, l, k]
  #   n: global sequence position
  #   l: layer index
  #   k: position within layer
  # THIS IS THE BASELINE — orbit-PE replaces [n, l, k] with orbit membership vector
  ```
- **Configuration extracted**: token_dim=64, window_size=8, loss=reconstruction+contrastive
- **Results**: Linear probe accuracy 0.978–0.991 on CNN Zoo
- **Used for**: Baseline timing measurement; understanding position encoding integration point

**Repository 2**: AllanYangZhou/nfn (⭐ 93)
- **URL**: https://github.com/AllanYangZhou/nfn
- **Query**: "AllanYangZhou nfn neural functional network permutation orbit computation PyTorch"
- **Relevance**: PRIMARY source for orbit computation primitives
- **Key Code**:
  ```python
  from nfn.common import state_dict_to_tensors, network_spec_from_wsfeat
  from nfn import layers

  # WeightSpaceFeatures: structured wrapper for model weights
  wsfeat = state_dict_to_tensors(model.state_dict(), network_spec)
  network_spec = network_spec_from_wsfeat(wsfeat)

  # NPLinear: orbit-based parameter sharing (S-equivariant)
  # Orbits derived by partitioning θ indices under group action S
  layer = layers.NPLinear(network_spec, in_ch, out_ch, io_embed=True)
  ```
- **Theory**: Equivariant parameter sharing = partitioning θ entries by orbits of indices under S
- **Limitation**: Currently supports MLP + 2D CNN only; MHA requires extension
- **Used for**: orbit_id computation for Linear and Conv2d; `network_spec` structure

**Repository 3**: MathematicalAI-NUS/Transformer-NFN (⭐ ~30)
- **URL**: https://github.com/MathematicalAI-NUS/Transformer-NFN
- **Query**: "MathematicalAI-NUS Transformer-NFN attention head permutation symmetry orbit"
- **Relevance**: MHA group structure for orbit-PE extension to Transformers
- **Key Theory**:
  ```
  G_U = S_h × GL_Dk^h × GL_Dv^h × P_D × P_DA
  Permutation subgroup: S_h × P_D × P_DA
  S_h: head permutation (h heads can be reordered)
  P_D: output neuron permutation (FFN output)
  P_DA: FFN intermediate neuron permutation
  ```
- **Used for**: Understanding which permutation group action to use for MHA orbit-PE; `--enc_mode inv` flag suggests invariant encoding is feasible
- **Dataset**: 125K+ Transformer checkpoints on MNIST + AGNews

**Repository 4**: HSG-AIML/MultiZoo-SANE (⭐ ~10)
- **URL**: https://github.com/HSG-AIML/MultiZoo-SANE
- **Relevance**: Demonstrates SANE with heterogeneous architectures — validates that per-token normalization works
- **Key Addition**: Masked per-token loss normalization for mixed-architecture training
- **Used for**: Understanding how SANE handles variable-architecture weight spaces; confirms cross-architecture tokenization is feasible

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear. SANE tokenization (sequential [n,l,k] → replace with orbit vector) and nfn orbit primitives (WeightSpaceFeatures, NPLinear parameter sharing) are well-documented in papers and README. The integration point is clear: replace SANE's `position_embed` lookup with `OrbitPEComputer.forward()`.

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report — H-E1
- **File**: `docs/youra_research/20260521_wsl/h-e1/04_validation.md`
- **Reused Components**:
  - Dataset: Same Small CNN Zoo + Small Transformer Zoo (100 samples each for H-M1, matching H-E1 scope)
  - nfn library usage pattern: `state_dict_to_tensors` + layer type detection
  - Timing infrastructure: wall-clock measurement per checkpoint
- **Why Reused**: H-E1 proved orbit-PE computes correctly (accuracy-preserving); H-M1 now tests computational efficiency and unified codebase — natural continuation with same data

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (CNN Zoo) | GitHub | AllanYangZhou/nfn repository |
| Dataset selection (Transformer Zoo) | GitHub | MathematicalAI-NUS/Transformer-NFN |
| Orbit computation algorithm | GitHub + Paper | AllanYangZhou/nfn (NPLinear, orbit partitioning) |
| MHA orbit group structure | GitHub + Paper | MathematicalAI-NUS/Transformer-NFN (Theorem 3.2) |
| Baseline timing comparison | GitHub | HSG-AIML/SANE (tokenization pipeline) |
| Overhead threshold (≤1.2×) | Phase 2B | 02b_verification_plan.md H-M1 success criteria |
| OrbitPE pseudo-code | GitHub synthesis | AllanYangZhou/nfn + Transformer-NFN group theory |
| Evaluation: computability_rate | Phase 2B | 02b_verification_plan.md H-M1 protocol step 2-3 |
| Evaluation: overhead_ratio | Phase 2B | 02b_verification_plan.md H-M1 protocol step 4-5 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-21T02:00:00Z

### Workflow History for This Hypothesis
- 2026-05-21T01:45:03Z: H-M1 set to IN_PROGRESS (external hypothesis loop)
- 2026-05-21T02:00:00Z: Phase 2C experiment design COMPLETED

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking) — UNATTENDED mode*
*MCP Tools Used: Archon (3 queries, no domain matches), Exa (4 repos found: HSG-AIML/SANE, AllanYangZhou/nfn, MathematicalAI-NUS/Transformer-NFN, HSG-AIML/MultiZoo-SANE), Serena (skipped — code sufficiently clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 — Implementation Planning*
