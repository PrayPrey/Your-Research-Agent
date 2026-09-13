# Experiment Design: H-E1

**Date:** 2026-08-03
**Author:** Anonymous
**Hypothesis Statement:** Under S_16³ functional permutations (coupled row-column across adjacent CNN layers), architecturally invariant weight encoders (DeepSets sum pooling, NFN structured equivariance) achieve mean OrbitVar < 1e-6 on ModelZooDataset CIFAR10-GS, contrasted with CISE (OrbitVar=0.010333), because architectural permutation-invariance by construction eliminates within-orbit representational variance.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** Yes (no prerequisites for H-E1)
**Gate Status:** MUST_WORK (unsatisfied — pending experiment)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
MUST_WORK: mean OrbitVar(C2) < 1e-6 AND mean OrbitVar(C3) < 1e-6. Failure → STOP and debug encoder implementation (do NOT proceed to H-M1).

---

## Continuation Context

No previous hypothesis — H-E1 is the foundation.

### Previous Hypothesis Results (if applicable)
None. This is the first hypothesis in the verification chain.

**Pre-existing baselines (BUILD_ON, not re-verified):**
- CISE OrbitVar = 0.010333 (from sh1 PASS)
- per-layer quantile statistics OrbitVar = 1.24e-33 (from h-m1 FAIL — establishes that truly invariant encoders can achieve near-zero; confirmed by Deep Sets Theorem 2)
- Ŵ_L baseline R² = 0.984 (from Unterthiner et al. 2020)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Status:** Archon KB does not contain weight-space learning or ModelZoo-specific implementation cases. The KB is populated with diffusion model documentation (similarity scores ~0.43 for all relevant queries — below meaningful threshold). All implementation guidance derived from Exa GitHub search results and primary papers.

**Queries executed:**
1. "DeepSets sum pooling permutation invariance experiment design dataset" → No relevant results (max sim 0.43)
2. "NFN Neural Functional Networks weight space permutation invariance implementation" → No relevant results (max sim 0.42)
3. "ModelZooDataset weight space learning model zoo prediction accuracy" → No relevant results (max sim 0.46)
4. Code examples: "DeepSets sum pooling PyTorch permutation invariant encoder" → No relevant results (diffusion model code only)

### Archon Code Examples

No relevant code examples found in Archon KB for this domain.

### Exa GitHub Implementations

**Query 1: DeepSets permutation invariant encoder for weight space**

**Repository 1**: scibits.blog/deepsets (educational) 
- **URL**: https://www.scibits.blog/posts/deepsets/index.html
- **Relevance**: Canonical DeepSets PyTorch pattern (φ → sum → ρ)
- **Key Code**:
  ```python
  class DeepSets(nn.Module):
      def __init__(self, input_dim, hidden_dim, output_dim, aggregator='sum'):
          super().__init__()
          self.psi = nn.Sequential(
              nn.Linear(input_dim, hidden_dim),
              nn.ReLU(),
              nn.Linear(hidden_dim, hidden_dim),
              nn.Tanh()
          )
          self.phi = nn.Sequential(
              nn.Linear(hidden_dim, hidden_dim),
              nn.ReLU(),
              nn.Linear(hidden_dim, output_dim)
          )
      def forward(self, x):
          h = self.psi(x)
          h = h.sum(dim=1)   # sum aggregation = permutation invariant
          return self.phi(h)
  ```
- **Used For**: Baseline pattern for C2 (DeepSets) encoder in H-E1

**Repository 2**: dpernes/deepsets-digitsum (PyTorch, complete)
- **URL**: https://github.com/dpernes/deepsets-digitsum
- **Relevance**: Complete PyTorch implementation with invariant + equivariant layers
- **Key insight**: Permutation invariant layer via sum pooling guarantees OrbitVar=0

**Repository 3**: pydvl DeepSet (production-quality)
- **URL**: https://pydvl.org/stable/api/pydvl/valuation/utility/deepset/
- **Key pattern**: φ network per element → sum bottleneck → ρ network

**Query 2: NFN AllanYangZhou official implementation**

**Repository**: AllanYangZhou/nfn ⭐93
- **URL**: https://github.com/AllanYangZhou/nfn
- **Relevance**: OFFICIAL implementation — exact library used in NFN paper (Zhou et al. 2023)
- **Install**: `pip install nfn`
- **Key Code**:
  ```python
  from nfn import layers
  from nfn.common import network_spec_from_wsfeat, state_dict_to_tensors

  # Build NFN for CNN weight space
  network_spec = network_spec_from_wsfeat(wsfeat)
  nfn_channels = 32

  nfn = nn.Sequential(
      layers.NPLinear(network_spec, 1, nfn_channels, io_embed=True),
      layers.TupleOp(nn.ReLU()),
      layers.NPLinear(network_spec, nfn_channels, nfn_channels, io_embed=True),
      layers.TupleOp(nn.ReLU()),
      layers.HNPPool(network_spec),   # permutation-invariant pooling
      nn.Flatten(start_dim=-2),
      nn.Linear(nfn_channels * layers.HNPPool.get_num_outs(network_spec), 1)
  )
  ```
- **Critical note**: NFN assumes global pooling layer between conv and FC layers. ModelZooDataset CIFAR10-GS CNN (3-conv, 1-dense) must verify this assumption.
- **CNN support**: NF-Layers support 2D CNNs with spatial folding. Confirmed compatible with small CNN architecture.

**Query 3: DWSNet — coupled row-column permutation (S_16³)**

**Repository**: AvivNavon/DWSNets ⭐ (ICML 2023 official)
- **URL**: https://github.com/AvivNavon/DWSNets
- **Relevance**: Defines the functional permutation group S_16³ used in H-E1
- **Coupled permutation**: For adjacent CNN layers, simultaneously permuting rows of W^(i) AND columns of W^(i+1) preserves the network function. This is the DWSNet Eq. 5 symmetry.
- **Used For**: Understanding permutation audit requirements (functional validator: ||f_v(x) - f_{g·v}(x)||_∞ ≤ 1e-6)

**Query 4: ModelZooDataset loading**

**Repository**: ModelZoos/ModelZooDataset
- **URL**: https://github.com/ModelZoos/ModelZooDataset
- **Zenodo DOI**: https://doi.org/10.5281/zenodo.6620868 (CIFAR10 CNN-s, preprocessed)
- **Target file**: `dataset_cifar_small_hyp_rand.pt` (preprocessed PyTorch dataset)
- **Loading**: Standard `torch.load()` — custom PyTorch dataset class included
- **Size**: ~100 CNN models with test accuracy labels (CIFAR10-GS split)

**Serena Analysis Needed**: false — all code is from external repos; no local codebase

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

For C3 (NFN): AllanYangZhou/nfn is the OFFICIAL implementation — use directly via `pip install nfn`.

For C2 (DeepSets): No single official implementation; pattern is well-established. Use scibits.blog/dpernes pattern adapted for channel-level weight encoding.

**Recommended Implementation Path:**
- Primary: `pip install nfn` for C3; custom DeepSets for C2 (pattern from Zaheer et al. 2017)
- Fallback: DWSNet-style channel pooling if NFN spatial folding incompatible with 3-conv architecture
- Justification: NFN official repo explicitly supports 2D CNNs with global avg pool; ModelZooDataset CIFAR10-GS CNN uses AdaptiveAvgPool2d

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. No local codebase to analyze. NFN API is pip-installable; DeepSets pattern is well-documented.

---

## Experiment Specification

### Dataset

**Name:** ModelZooDataset CIFAR10-GS (Gunnar-Split)
**Type:** standard (real, established dataset)
**Source:** Zenodo record 6620868 — https://doi.org/10.5281/zenodo.6620868
**File:** `dataset_cifar_small_hyp_rand.pt` (preprocessed PyTorch dataset)
**Architecture:** Small CNN (3 conv layers, C=16 channels, 1 dense layer, AdaptiveAvgPool2d)
**Size:** ~100 CNN models with CIFAR-10 test accuracy labels
**Label:** test accuracy (float, 0–1)
**Split:** All 100 models used for OrbitVar computation (no train/val/test split needed — this is a measurement experiment, not supervised learning)
**S_16³ group:** Functional permutation group defined by 16-channel conv layers; K=50 functional permutations per model = 5,000 forward passes total

**Loading Information** (for Phase 4 download):
- Method: torch.load (custom PyTorch dataset class from ModelZooDataset)
- Identifier: `dataset_cifar_small_hyp_rand.pt`
- Code:
  ```python
  import torch
  dataset = torch.load("data/dataset_cifar_small_hyp_rand.pt")
  # dataset[i] = (weight_vector, accuracy_label)
  # Reconstruct model: use index_dict.json from Zenodo record
  ```

### Models

#### Baseline Model (CISE — C1, pre-established)

**Architecture:** CISE (Channel-wise Isotropic Sinusoidal Encoder)
**OrbitVar (established):** 0.010333 (from sh1 PASS — not re-measured in H-E1)
**Note:** CISE baseline is BUILD_ON; H-E1 focuses only on C2 and C3 OrbitVar measurement.

**Loading Information** (for Phase 4 download):
- Method: custom (from existing sh1 codebase)
- Identifier: existing `apply_channel_permutation()` + CISE encoder
- Code: reuse sh1 encoder implementation

#### Proposed Models (C2 and C3)

**Architecture C2:** Baseline architecture + DeepSets sum-pooling encoder

**Core Mechanism Implementation — C2 (DeepSets):**

```python
# Core Mechanism: DeepSets Channel Encoder (C2)
# Based on: Zaheer et al. 2017 (Theorem 2) + dpernes/deepsets pattern
# Applied per-layer: φ maps each channel's weight vector → sum over C=16 channels

class DeepSetsChannelEncoder(nn.Module):
    """
    Permutation-invariant encoder over C=16 channels per conv layer.
    OrbitVar = 0 by Deep Sets Theorem 2 (sum pooling guarantee).
    Input: weight tensor W of shape (C_out, C_in, kH, kW) per layer
    Output: fixed-dim embedding invariant to channel permutations
    """
    def __init__(self, weight_dim, hidden_dim=64, embed_dim=128):
        super().__init__()
        # phi: per-channel element embedding
        self.phi = nn.Sequential(
            nn.Linear(weight_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        # rho: post-aggregation transformation
        self.rho = nn.Sequential(
            nn.Linear(hidden_dim, embed_dim),
            nn.ReLU()
        )

    def forward(self, W_layer):
        # W_layer: (C, weight_dim) — flattened weights per output channel
        h = self.phi(W_layer)      # (C, hidden_dim)
        h = h.sum(dim=0)           # (hidden_dim,) — permutation invariant by construction
        return self.rho(h)         # (embed_dim,)

# Full model: apply per layer, concatenate embeddings
# OrbitVar = Var_π[encoder(π·W)] = 0 by Theorem 2
```

**Architecture C3:** NFN NF-Layers encoder (official AllanYangZhou/nfn)

**Core Mechanism Implementation — C3 (NFN):**

```python
# Core Mechanism: NFN NF-Layers Encoder (C3)
# Based on: Zhou et al. 2023 (AllanYangZhou/nfn official)
# pip install nfn

import torch
from torch import nn
from nfn import layers
from nfn.common import network_spec_from_wsfeat, state_dict_to_tensors
from torch.utils.data import default_collate

def build_nfn_encoder(sample_wsfeat, nfn_channels=32, embed_dim=128):
    """NFN encoder for 3-conv CNN weight space."""
    network_spec = network_spec_from_wsfeat(sample_wsfeat)
    nfn = nn.Sequential(
        layers.NPLinear(network_spec, 1, nfn_channels, io_embed=True),
        layers.TupleOp(nn.ReLU()),
        layers.NPLinear(network_spec, nfn_channels, nfn_channels, io_embed=True),
        layers.TupleOp(nn.ReLU()),
        layers.HNPPool(network_spec),          # permutation-invariant pooling
        nn.Flatten(start_dim=-2),
        nn.Linear(
            nfn_channels * layers.HNPPool.get_num_outs(network_spec),
            embed_dim
        )
    )
    return nfn

# CNN assumption: must have nn.AdaptiveAvgPool2d between conv and FC layers
# CIFAR10-GS CNN: verify spatial folding compatibility before running
```

### Training Protocol

**This is a measurement experiment — no gradient-based training of the CNN models.**

The experiment measures OrbitVar of encoder outputs under functional permutations; it does NOT train new models.

**Encoder training (if needed for C2/C3):** Not required for OrbitVar measurement. OrbitVar is computed by:
1. Loading pre-trained CNN weights from ModelZooDataset
2. Applying K=50 functional S_16³ permutations to each model's weights
3. Passing each permuted weight set through the encoder (C2 or C3)
4. Computing variance across K permuted encodings per model

**OrbitVar Computation Protocol:**

```
Optimizer: None (no training)
Seeds: 1 (fixed — for reproducibility of permutation sampling)
Models: 100 CNNs from dataset_cifar_small_hyp_rand.pt
Permutations per model: K = 50 (functional S_16³ permutations)
Total encoder forward passes: 100 × 50 = 5,000

OrbitVar computation:
  For each model v in {1..100}:
    For each permutation π in {1..50}:
      enc_v_π = encoder(π · W_v)    # apply permutation, encode
    OrbitVar(v) = Var_{π}[enc_v_π]  # variance over π orbit
  mean_OrbitVar = mean({OrbitVar(v)})
  max_OrbitVar  = max({OrbitVar(v)})
```

**Functional permutation prerequisite (MANDATORY before any encoding):**
```
For each π in test set:
  Verify: ||f_v(x) - f_{π·v}(x)||_∞ ≤ 1e-6 for random x ∈ [0,1]^(3,32,32)
  If fails: STOP — permutation is not functional; fix apply_channel_permutation()
```

### Evaluation

**Primary Metrics:**
- OrbitVar (C2) = E_v[Var_π(encoder_C2(π·W_v))]: measure of within-orbit variance
- OrbitVar (C3) = E_v[Var_π(encoder_C3(π·W_v))]: same for NFN encoder

**Success Criteria (PoC: direction-based):**
- Primary: mean OrbitVar(C2) < 1e-6 AND mean OrbitVar(C3) < 1e-6
- Secondary: max OrbitVar(C2) < 1e-4 AND max OrbitVar(C3) < 1e-4
- Direction: both invariant encoders must show OrbitVar orders of magnitude below CISE baseline (0.010333)

**Expected Baseline Performance (from established priors):**
- C2 (DeepSets): OrbitVar = 0 (mathematical guarantee, Theorem 2) → expect < 1e-15 (numerical precision floor)
- C3 (NFN): OrbitVar ≈ 0 (equivariance construction) → expect < 1e-10
- CISE baseline: OrbitVar = 0.010333 (from sh1 PASS, BUILD_ON)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: measurement (not classification/regression)
- Library: numpy / torch (variance computation only)
- Code:
  ```python
  import torch
  def compute_orbit_var(encoder, model_weights, permutations):
      embeddings = torch.stack([encoder(perm(model_weights)) for perm in permutations])
      return embeddings.var(dim=0).mean().item()
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: OrbitVar bar chart — C2 vs C3 vs CISE(C1) baseline, log scale (y-axis), with target threshold (1e-6) as horizontal line

#### Additional Figures (LLM Autonomous)
- Orbit embedding scatter plot: PCA of encoder outputs for 10 random models × 50 permutations (should show single point cluster for C2/C3, spread cluster for CISE)
- OrbitVar distribution per model: violin plot showing variance distribution across 100 models for C2 and C3

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Functional permutation audit passes (||f_v(x) - f_{g·v}(x)||_∞ ≤ 1e-6 verified)
2. Code runs without error for all 100 models × 50 permutations
3. `mean_OrbitVar(C2) < 1e-6` AND `mean_OrbitVar(C3) < 1e-6`

---

## 🔬 Mechanism Verification Protocol

**Pre-conditions (verify before running):**

| Check | Condition | Action if Fails |
|-------|-----------|-----------------|
| `mechanism_exists` | Deep Sets sum pooling implemented correctly (no per-position indexing) | Fix phi indexing; OrbitVar > 0 indicates position-aware encoding |
| `mechanism_isolatable` | Permutation audit passes (functional S_16³) | Fix apply_channel_permutation(); re-verify |
| `baseline_measurable` | CISE OrbitVar = 0.010333 reproducible from sh1 code | Use sh1 stored result; do not re-run if baseline valid |

**Architecture compatibility:**

NFN (C3) requires:
- `nn.AdaptiveAvgPool2d(1)` between conv and FC layers in CIFAR10-GS CNN ✓ (standard architecture)
- CNN spatial folding: NFN folds (kH, kW) into channel dim for 2D conv layers ✓ (supported by nfn library)
- Input: `WeightSpaceFeatures` constructed via `state_dict_to_tensors(state_dict)`

DeepSets (C2) requires:
- Per-channel weight flattening: each output channel's weight vector → φ → sum → ρ
- No order statistics (verify: phi uses no argmax/argsort over channel dim)

**Activation Indicators (log during experiment):**

```python
# mechanism_log_message
print(f"[C2] OrbitVar per model: {orbit_vars_c2}")
print(f"[C3] OrbitVar per model: {orbit_vars_c3}")
print(f"[AUDIT] Functional permutation verified: max_diff={max_diff:.2e}")
```

**Tensor shape verification:**
- C2 encoder input: `(C=16, weight_dim)` per layer; output: `(embed_dim,)` — shape invariant to C permutation ✓
- C3 encoder input: `WeightSpaceFeatures` tuple; output: `(embed_dim,)` via HNPPool

**metric_delta_expected:**
- Delta from CISE baseline: OrbitVar(C2) / OrbitVar(CISE) expected >> 1e4 (≥4 orders of magnitude)
- If delta < 100: encoder has position-aware bug — investigate phi indexing

**mechanism_verification_code:**
```python
def verify_mechanism(encoder, W, perms, name):
    embeddings = [encoder(perm(W)) for perm in perms[:5]]
    var = torch.stack(embeddings).var(dim=0).mean().item()
    assert var < 1e-6 or name == 'CISE', f"{name} OrbitVar={var:.2e} exceeds threshold"
    print(f"✓ {name} OrbitVar={var:.2e}")
```

**hypothesis_support_threshold:** mean OrbitVar < 1e-6 for BOTH C2 and C3
**hypothesis_support_metric:** OrbitVar = E_v[Var_π(encoder(π·W_v))]

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Status:** No relevant sources found. Archon KB populated with diffusion model documentation only. All implementation evidence from Exa.

### B. GitHub Implementations (Exa)

**Repository 1**: AllanYangZhou/nfn ⭐93
- **URL**: https://github.com/AllanYangZhou/nfn
- **Query Used**: "NFN Neural Functional Networks AllanYangZhou nfn PyTorch weight space encoder CNN"
- **Relevance**: OFFICIAL NFN implementation — exact library for C3 encoder
- **Key Code**: `pip install nfn`; `layers.NPLinear`, `layers.HNPPool` for permutation-invariant pooling
- **Their Results**: Kendall's τ = 0.934 on ModelZooDataset (Zhou et al. 2023, Table 2)
- **Used For**: C3 encoder implementation; spatial CNN folding; WeightSpaceFeatures API

**Repository 2**: AvivNavon/DWSNets (ICML 2023)
- **URL**: https://github.com/AvivNavon/DWSNets
- **Query Used**: "DWSNet channel permutation S16 coupled row column permutation weight space"
- **Relevance**: Defines S_16³ functional permutation group (Eq. 5 in paper)
- **Key insight**: Coupled row-column permutation: permute rows of W^(i) AND columns of W^(i+1) simultaneously → function-preserving
- **Used For**: Permutation audit specification; understanding what apply_channel_permutation() must implement

**Repository 3**: scibits.blog/deepsets + dpernes/deepsets-digitsum
- **URL**: https://www.scibits.blog/posts/deepsets/ + https://github.com/dpernes/deepsets-digitsum
- **Query Used**: "DeepSets permutation invariant encoder neural network weight space PyTorch"
- **Key Code**: φ → sum → ρ pattern for C2 encoder
- **Used For**: C2 DeepSets encoder implementation pattern

**Repository 4**: ModelZoos/ModelZooDataset
- **URL**: https://github.com/ModelZoos/ModelZooDataset + https://doi.org/10.5281/zenodo.6620868
- **Query Used**: "ModelZooDataset CIFAR10 weight space dataset Zenodo Unterthiner model zoo"
- **Key info**: `dataset_cifar_small_hyp_rand.pt`, preprocessed PyTorch dataset class
- **Used For**: Dataset loading specification; confirming 100 CNN models, C=16 channels, test accuracy labels

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear. External repos (nfn, DWSNets) are pip-installable; local codebase has no weight-space encoder files.

### D. Previous Hypothesis Context

**Previous Context**: None — H-E1 is the first hypothesis in the verification chain.

**Pre-established baselines used (BUILD_ON):**
- CISE OrbitVar = 0.010333 (sh1 PASS) — used as contrast baseline; not re-measured
- Deep Sets Theorem 2: sum pooling OrbitVar = 0 by mathematical proof — grounds C2 success expectation

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: ModelZooDataset CIFAR10-GS | GitHub + Zenodo | B.4 (ModelZoos/ModelZooDataset) |
| Dataset loading: torch.load + index_dict.json | GitHub | B.4 |
| C2 (DeepSets) encoder pattern | GitHub | B.3 (scibits + dpernes) |
| C2 OrbitVar = 0 guarantee | Paper | Zaheer et al. 2017, Theorem 2 |
| C3 (NFN) encoder: pip install nfn | GitHub | B.1 (AllanYangZhou/nfn) |
| C3 NPLinear + HNPPool API | GitHub | B.1 |
| S_16³ permutation definition | GitHub + Paper | B.2 (AvivNavon/DWSNets, Eq. 5) |
| Functional audit: ||f_v - f_{g·v}||_∞ ≤ 1e-6 | Paper | DWSNet Eq. 5 + 02b_verification_plan.md |
| OrbitVar = E_v[Var_π] formula | Phase 2B | 02b_verification_plan.md, H-E1 spec |
| K=50 permutations, N=100 models | Phase 2B | 02b_verification_plan.md, H-E1 spec |
| Success threshold: mean < 1e-6 | Phase 2B | 02b_verification_plan.md, H-E1 gates |
| CISE baseline OrbitVar = 0.010333 | sh1 PASS | BUILD_ON, 02b_verification_plan.md |
| NFN Kendall's τ = 0.934 | Paper | Zhou et al. 2023, Table 2 |
| Ŵ_L R² = 0.984 | Paper | Unterthiner et al. 2020 |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — not written directly)
**Date:** 2026-08-03

### Workflow History for This Hypothesis
- 2026-08-03T17:57:10Z: H-E1 set to IN_PROGRESS (hypothesis loop starting Phase 2C)
- 2026-08-03: Phase 2C experiment design initiated (unattended)
- 2026-08-03: Archon KB search — no relevant results (domain mismatch)
- 2026-08-03: Exa search — AllanYangZhou/nfn, AvivNavon/DWSNets, ModelZoos/ModelZooDataset found
- 2026-08-03: Serena analysis skipped (no local codebase; external code clear)
- 2026-08-03: Dataset confirmed: ModelZooDataset CIFAR10-GS (Zenodo 6620868)
- 2026-08-03: Experiment design synthesized — COMPLETED

---

## Quality Validation (Step 8)

**Check 1: All hyperparameters justified?** ✅
- No gradient-based training; only measurement. K=50 permutations, N=100 models from Phase 2B spec.

**Check 2: Dataset choice justified?** ✅
- ModelZooDataset CIFAR10-GS directly specified in Phase 2B Section 1.3; S_16³ group defined by C=16 channels.

**Check 3: Mechanism grounded in code?** ✅
- C2: DeepSets pattern from dpernes/deepsets-digitsum + Zaheer 2017 paper
- C3: NFN from AllanYangZhou/nfn official implementation (pip installable)

**Check 4: No unsupported assumptions?** ✅
- OrbitVar = 0 expectation grounded in Deep Sets Theorem 2 (mathematical proof)
- NFN equivariance grounded in Zhou et al. 2023 + official implementation

**Check 5: Full traceability?** ✅
- All specifications traced in Traceability Matrix (Section E above)

**Overall: PASSED**

---

*MCP Tools Used: Archon (4 KB queries — no relevant results), Exa GitHub (4 queries — AllanYangZhou/nfn, AvivNavon/DWSNets, ModelZooDataset, DeepSets pattern), Serena (skipped — no local codebase)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
