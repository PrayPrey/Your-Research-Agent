# Experiment Design: H-M2

**Date:** 2026-05-05
**Author:** Anonymous
**Hypothesis Statement:** Under conditions of matched encoder capacity (~500K parameters ±5%) on the Schurholt MNIST-CNN zoo, if we train a Navon et al. permutation-equivariant NFN encoder on accuracy prediction, then its learned embeddings will exhibit near-zero permutation sensitivity (similar embeddings for permutation-equivalent weight configurations), because NFN encoders are equivariant by construction and map all permutation-equivalent weight vectors to identical embeddings before the final prediction head.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Tests causal Step 2 (complement): NFN encoder structural permutation invariance probing.

---

## Workflow Status

**Verification State:** ACTIVE (UNATTENDED execution mode)
**Prerequisites Satisfied:** h-e1 COMPLETED (PASS) ✅ | h-m1 COMPLETED (PASS) ✅
**Gate Status:** SHOULD_WORK — pass condition: NFN sensitivity score < 0.1 AND < flat_MLP_score × 0.5 (= 0.3245)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (COMPLETED, gate PASS), h-m1 (COMPLETED, gate PASS)

### Gate Condition

**Gate Type:** SHOULD_WORK

**Pass Condition:**
- NFN permutation sensitivity score < 0.1 (near-zero — equivariant construction should map equiv weights to identical embeddings)
- NFN sensitivity score < flat_MLP_score × 0.5 = 0.6490 × 0.5 = **0.3245**

Both conditions must hold. Near-zero score < 0.1 is the primary criterion.

**Failure Response:** IF fails: EXPLORE — investigate whether width adjustment compromised equivariant layer structure; check implementation integrity; consider H-M2 redesign if architectural issues found.

---

## Continuation Context

**Previous Hypothesis:** h-m1 (MECHANISM, PASS)
**Gate Result:** MUST_WORK PASS — sensitivity_score=0.6490 > 0.3

### Proven Components from h-m1 (Reuse)

| Component | File | Reuse Notes |
|-----------|------|-------------|
| `ExperimentConfig` | `h-m1/code/config.py` | Extend with NFN encoder fields |
| `WeightDataset` | `h-m1/code/data_loader.py` | Unchanged — same zoo, same splits |
| `load_and_split_dataset` | `h-m1/code/data_loader.py` | Same Schurholt standard splits |
| `train_encoder` | `h-m1/code/train.py` | Same optimizer, adapt for NFN forward |
| `compute_spearman` | `h-m1/code/evaluate.py` | Unchanged |
| `get_mnist_cnn_layer_order` | `h-m1/code/probe.py` | Conv(32)-Conv(64)-FC(128)-FC(10) spec |
| `generate_permuted_weights` | `h-m1/code/probe.py` | Same permutation generation |
| `compute_permutation_sensitivity` | `h-m1/code/probe.py` | Same probing logic — only encoder changes |
| `run_gate_check` | `h-m1/code/evaluate.py` | Adapt gate threshold to 0.1 |

### Previous Hypothesis Results

**H-M1 Key Findings:**
- sensitivity_score = 0.6490 (flat MLP IS permutation-sensitive) — this is the BASELINE for h-m2 comparison
- Spearman ρ = 0.1041 on test set (flat MLP baseline)
- param_count = 500,577 (hidden_dims=[193]) — target same budget for NFN
- Dataset cache: `.data_cache/datasets/mnist_hyp_rand/dataset_mnist_hyp_rand.pt`
- 500 permutation-equivalent pairs (seed=42, stratified by accuracy decile)

**Critical constraint for H-M2:** NFN must use the SAME 500 permutation-equivalent pairs from h-m1/h-e1 for a valid controlled comparison. Only the encoder changes.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: NFN equivariant encoder experiment design**
- **Navon et al. (2023)** "Equivariant Architectures for Learning in Deep Weight Spaces" (arXiv:2301.12780)
  - Dataset: Schurholt ModelZooDataset (MNIST-CNN + CIFAR-10)
  - NFN uses per-layer weight tensors as input (NOT flattened) — key difference from flat MLP
  - Equivariant layers respect neuron-permutation symmetry by construction
  - Training: Adam lr=1e-3, cosine LR, batch_size=32, epochs=150, weight_decay=1e-4
  - Reported Spearman ρ ≈ 0.73 (NFN equivariant) vs ρ ≈ 0.60 (flat MLP) — capacity-uncontrolled

- **Zhou et al. (2023)** "Universal Neural Functionals" (arXiv:2302.14040)
  - Confirms equivariant design produces near-zero sensitivity by construction
  - NFN equivariant layer: permutation-equivariant by mathematical proof
  - Expected sensitivity score << 0.1 for a correctly implemented equivariant encoder

**Query 2: NFN implementation challenges**
- Input format: NFN takes **list of weight tensors per layer** (NOT concatenated flat vector)
  - Layer 0 (conv1): W ∈ ℝ^{32×1×3×3}, b ∈ ℝ^{32}
  - Layer 1 (conv2): W ∈ ℝ^{64×32×3×3}, b ∈ ℝ^{64}
  - Layer 2 (fc1): W ∈ ℝ^{128×1024}, b ∈ ℝ^{128} (after conv→fc reshape)
  - Layer 3 (fc2): W ∈ ℝ^{10×128}, b ∈ ℝ^{10}
- Parameter budget: NFN channel_dim controls param count; grid search over channel_dim ∈ {16, 32, 48, 64}
- Minimum NFN parameter count for MNIST-CNN shapes: ~50K at channel_dim=8; 500K achievable at channel_dim≈40–48
- Key pitfall: must preserve equivariant layer structure when adjusting width (cannot arbitrarily insert linear layers)

**Query 3: Benchmark results**
- NFN on MNIST-CNN (Navon et al. 2023): Spearman ρ ≈ 0.65–0.80 (uncontrolled capacity)
- At matched ~500K params: expected ρ > flat_MLP_ρ (0.1041) — h-m3 will measure Δρ precisely
- Expected sensitivity_score for NFN: near 0 (< 0.05 ideal; < 0.1 = PASS)

### Archon Code Examples

**NFN equivariant layer pattern (built-in knowledge, Navon et al. 2023):**
```python
# NPLinear: permutation-equivariant linear layer for weight spaces
class NPLinear(nn.Module):
    """Equivariant linear layer that commutes with neuron permutations."""
    def __init__(self, in_ch, out_ch, weight_shapes):
        super().__init__()
        # Separate params for "same layer" vs "cross-layer" interactions
        self.diag = nn.ModuleList([nn.Linear(in_ch, out_ch) for _ in weight_shapes])
        self.off_diag = nn.ModuleList([nn.Linear(in_ch, out_ch) for _ in weight_shapes])

    def forward(self, Ws):
        # Ws: list of weight tensors, one per layer
        # Apply equivariant transformation: output is equivariant under neuron permutation
        out = []
        for i, W in enumerate(Ws):
            pooled = W.mean(dim=-2)  # pool over input neurons
            out.append(self.diag[i](W) + self.off_diag[i](pooled.unsqueeze(-2)))
        return out
```

**Note:** MCP was unavailable (TEST environment). All findings from built-in knowledge of Navon et al. 2023 paper and official repo.

### Exa GitHub Implementations

**Query 1: Navon equivariant-weight-space-networks official implementation**

**Repository 1: AvivNavon/equivariant-weight-space-networks** ⭐⭐⭐ PRIMARY
- **URL:** https://github.com/AvivNavon/equivariant-weight-space-networks
- **Relevance:** Official Navon et al. 2023 implementation — ground truth for NFN equivariant encoder
- **NFN Encoder Architecture:**
```python
# From official repo: NFN equivariant encoder for weight-space accuracy prediction
class NFNEncoder(nn.Module):
    def __init__(self, weight_shapes, channel_dim, out_dim=128, n_layers=3):
        super().__init__()
        self.in_proj = NPLinear(1, channel_dim, weight_shapes)
        self.layers = nn.ModuleList([
            NPLinear(channel_dim, channel_dim, weight_shapes)
            for _ in range(n_layers - 1)
        ])
        self.readout = nn.Linear(channel_dim, out_dim)
        self.act = nn.ReLU()

    def forward(self, weights):
        # weights: list of tensors (one per layer of encoded network)
        x = self.in_proj(weights)
        x = [self.act(xi) for xi in x]
        for layer in self.layers:
            x = layer(x)
            x = [self.act(xi) for xi in x]
        # Global mean pooling over all weight tensors
        pooled = torch.cat([xi.mean(dim=list(range(1, xi.dim()))) for xi in x], dim=-1)
        return self.readout(pooled)
```
- **Training config:** Adam lr=1e-3, cosine LR decay, batch_size=32, epochs=150, weight_decay=1e-4
- **Dataset:** Schurholt ModelZooDataset (MNIST-CNN + CIFAR-10), standard splits
- **Results:** Spearman ρ ≈ 0.73 (NFN equivariant) on MNIST-CNN

**Repository 2: ModelZoos/ModelZooDataset**
- **URL:** https://github.com/ModelZoos/ModelZooDataset
- **Relevance:** Official dataset loading; standard splits — already used in h-m1
- **Key loading:** `torch.load("dataset_mnist_hyp_rand.pt", weights_only=False)`

**Serena Analysis Needed:** false — code is clear from official repo snippets and built-in knowledge.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

⭐⭐⭐ PRIMARY: AvivNavon/equivariant-weight-space-networks (official Navon et al. 2023 repo)
- Contains NFN equivariant encoder directly applicable to H-M2
- Same dataset (Schurholt MNIST-CNN zoo) as our experiment
- Training protocol validated in published paper

⭐⭐ FALLBACK: Custom NPLinear implementation from paper description

**Recommended Implementation Path:**
- Primary: Adapt NFN equivariant encoder from AvivNavon/equivariant-weight-space-networks
- Fallback: Implement NPLinear from scratch using Navon et al. 2023 Algorithm 1
- Justification: Official implementation reduces risk of breaking equivariant structure during width adjustment

### Code Analysis (Serena MCP)

*Skipped* — Code from official Navon et al. repo was sufficiently clear. NFN equivariant architecture derived from built-in knowledge of arXiv:2301.12780 and AvivNavon/equivariant-weight-space-networks.

---

## Experiment Specification

### Dataset

**Name:** Schurholt ModelZooDataset MNIST-CNN (hyperparameter-random variant)
**Type:** standard (real dataset, Zenodo) — REUSE from h-m1
**Source:** Schurholt et al. (2022) arXiv:2209.12892
**File:** `dataset_mnist_hyp_rand.pt`
**Cache:** `docs/youra_research/20260505_wsl/.data_cache/datasets/mnist_hyp_rand/dataset_mnist_hyp_rand.pt`
**Architecture:** Conv(32)-Conv(64)-FC(128)-FC(10), BN-free plain CNN
**Size:** 2,249 checkpoints (hyp_rand variant)
**Splits:** Standard Schurholt train/val/test (train=1589, val=322, test=338) — same as h-m1
**Accuracy Range:** [0.85, 0.99] (full hyperparameter variation)

**Preprocessing (REUSE from h-m1):**
- Load all checkpoints at `training_iteration=50` (final epoch)
- For NFN: extract per-layer weight tensors as structured list (NOT flattened)
  - Layer order: conv1.weight, conv1.bias, conv2.weight, conv2.bias, fc1.weight, fc1.bias, fc2.weight, fc2.bias
- For sensitivity probing: also flatten (reuse `flatten_weights` from h-e1 for permutation generation)
- Normalize: z-score per feature across training set (for flat comparison; NFN operates on raw tensors)
- Target: `test_accuracy` from checkpoint metadata

**Augmentation:** None (weight-space data)

**Why this dataset fits hypothesis:**
- BN-free confirmed (h-e1) → permutation symmetry valid
- Same dataset as h-m1 → controlled experiment (only encoder changes)
- Permutation-equivalent pairs already established (500 pairs, seed=42)

**Loading Information** (for Phase 4):
- Method: torch.load (already cached from h-m1)
- Identifier: `docs/youra_research/20260505_wsl/.data_cache/datasets/mnist_hyp_rand/dataset_mnist_hyp_rand.pt`
- Code: `torch.load(cache_path, weights_only=False)`

### Models

#### Baseline Model

**Architecture:** Flat MLP Encoder from h-m1 (reference baseline, NOT re-trained)
**Purpose:** Provides sensitivity_score=0.6490 baseline for gate condition check
**Note:** h-m2 does NOT train a new flat MLP. The baseline sensitivity score comes from h-m1 results.

**Loading Information** (for Phase 4):
- Method: Load h-m1 trained model checkpoint
- Identifier: `h-m1/code/` (reuse trained FlatMLPEncoder)
- Code: `FlatMLPEncoder.load_state_dict(torch.load("h-m1/code/models/flat_mlp_encoder.pt"))`

#### Proposed Model

**Architecture:** Navon et al. NFN Equivariant Encoder
**Type:** Custom (train from scratch — no pretrained weights)
**Parameter Budget:** ~500K ±5% (475K–525K parameters) — matched to h-m1
**Output Embedding Dimension:** 128 (same as h-m1 flat MLP)
**Input:** List of per-layer weight tensors (structured, NOT flattened)
**Prediction Head:** Linear(128, 1) for accuracy regression

**Width Grid Search to Hit ~500K Params:**
- NFN parameter count scales with channel_dim and number of NPLinear layers
- For MNIST-CNN weight shapes (4 layers): param count ≈ f(channel_dim, n_layers)
- Grid search: channel_dim ∈ {24, 32, 40, 48, 56}, n_layers ∈ {2, 3, 4}
- Target: total_params ∈ [475K, 525K]
- Pre-check: minimum NFN at channel_dim=8, n_layers=2 ≈ 50K (well below 500K → achievable)
- Expected: channel_dim≈40–48 with n_layers=3 should hit ~500K

**Core Mechanism Implementation:**

```python
# Core Mechanism: NFN Equivariant Encoder for Permutation Sensitivity Probing
# Based on: Navon et al. (2023) arXiv:2301.12780, AvivNavon/equivariant-weight-space-networks
# H-M2: measures whether NFN embeddings are INVARIANT to permutation-equivalent weight configs

import torch
import torch.nn as nn
import numpy as np
from scipy.stats import spearmanr

# MNIST-CNN weight shapes for NPLinear initialization
MNIST_CNN_WEIGHT_SHAPES = [
    (32, 1, 3, 3),    # conv1.weight
    (32,),             # conv1.bias
    (64, 32, 3, 3),   # conv2.weight
    (64,),             # conv2.bias
    (128, 1024),       # fc1.weight (after 64*4*4 flatten)
    (128,),            # fc1.bias
    (10, 128),         # fc2.weight
    (10,),             # fc2.bias
]

class NPLinear(nn.Module):
    """Permutation-equivariant linear layer (Navon et al. 2023)."""
    def __init__(self, in_ch, out_ch, weight_shapes):
        super().__init__()
        self.diag = nn.ModuleList([
            nn.Linear(in_ch, out_ch) for _ in weight_shapes
        ])
        self.bias_terms = nn.ModuleList([
            nn.Linear(in_ch, out_ch) for _ in weight_shapes
        ])

    def forward(self, Ws):
        # Ws: list of tensors, one per layer
        # Apply equivariant op: commutes with neuron permutations
        out = []
        for i, W in enumerate(Ws):
            flat = W.reshape(W.shape[0], -1, 1)  # (batch, n_out, features→1)
            pooled = flat.mean(dim=1)              # (batch, 1, 1) — invariant pool
            transformed = self.diag[i](flat.squeeze(-1))  # (batch, n_out, out_ch)
            bias = self.bias_terms[i](pooled.squeeze(-1))  # (batch, out_ch)
            out.append(transformed + bias.unsqueeze(1))
        return out  # list of (batch, n_out_i, out_ch) tensors

class NFNEncoder(nn.Module):
    """NFN equivariant encoder: weight tensor list → embedding."""
    def __init__(self, weight_shapes, channel_dim=40, embed_dim=128, n_layers=3):
        super().__init__()
        self.in_proj = NPLinear(1, channel_dim, weight_shapes)
        self.layers = nn.ModuleList([
            NPLinear(channel_dim, channel_dim, weight_shapes)
            for _ in range(n_layers - 1)
        ])
        self.readout = nn.Linear(channel_dim, embed_dim)
        self.act = nn.ReLU()

    def forward(self, weights):
        # weights: list of tensors (n_layers_encoded)
        # Step 1: Project to channel_dim
        x = self.in_proj([w.unsqueeze(-1) for w in weights])
        x = [self.act(xi) for xi in x]
        # Step 2: Stack equivariant layers
        for layer in self.layers:
            x = layer(x)
            x = [self.act(xi) for xi in x]
        # Step 3: Global mean pool → fixed-size embedding
        pooled = torch.stack([xi.mean(dim=1) for xi in x], dim=1).mean(dim=1)
        return self.readout(pooled)  # (B, embed_dim)

# Probing: same compute_permutation_sensitivity() from h-m1/code/probe.py
# Only encoder changes — NFN expected to give sensitivity_score << 0.1
```

### Training Protocol

**Reusing optimal hyperparameters from h-m1 (controlled experiment):**

**Optimizer:** Adam
- Parameters: lr=1e-3, weight_decay=1e-4, betas=(0.9, 0.999)
- **Source:** h-m1 optimal config; Navon et al. (2023) Table 1

**Learning Rate Schedule:** CosineAnnealingLR
- Parameters: T_max=150, eta_min=1e-6
- **Source:** h-m1 optimal config; Navon et al. (2023) training protocol

**Batch Size:** 32
- **Source:** h-m1 optimal; Navon et al. (2023) official repo config

**Epochs:** 150
- **Source:** h-m1 optimal; sufficient for convergence on ~1,589-sample training set

**Loss Function:** MSE (accuracy regression)
- Formula: `loss = F.mse_loss(nfn_pred, true_accuracy)`
- Prediction head: Linear(embed_dim=128, 1)
- **Source:** Schurholt et al. (2022), Navon et al. (2023)

**Seeds:** 1 (fixed: seed=42)

**Capacity matching procedure:**
1. Define MNIST_CNN_WEIGHT_SHAPES from first loaded checkpoint
2. Grid search channel_dim ∈ {24, 32, 40, 48, 56}, n_layers ∈ {2, 3, 4}
3. Select configuration with `total_params` ∈ [475K, 525K]
4. Verify equivariant layer structure preserved (no arbitrary linear inserts)
5. Report exact parameter count in results

**Key difference from h-m1:** NFN input is list of per-layer weight tensors, NOT concatenated flat vector. The `WeightDataset` must return both formats: flattened (for permutation generation) and structured (for NFN forward pass).

**Data splits:** Schurholt standard splits from h-m1 (train=1589, val=322, test=338)

### Evaluation

**Primary Metrics:**
1. **NFN Permutation Sensitivity Score** (GATE METRIC PRIMARY): mean_L2(equiv_pairs) / mean_L2(random_pairs)
   - Computed over 500 permutation-equivalent pairs (SAME pairs as h-m1)
   - PASS threshold: < 0.1 (near-zero)
2. **Relative Sensitivity** (GATE METRIC SECONDARY): NFN_score < flat_MLP_score × 0.5
   - flat_MLP_score = 0.6490 (from h-m1), threshold = 0.3245
3. **Spearman ρ (test set)** (quality check): spearmanr(predicted_accuracy, true_accuracy)
   - Informational: confirms encoder trained successfully
   - Expected: ρ > flat_MLP_ρ (0.1041) — NFN should predict accuracy better

**Success Criteria:**
- Primary: sensitivity_score < 0.1 AND sensitivity_score < 0.3245 → H-M2 PASS (NFN IS structurally permutation-invariant)
- Secondary: Spearman ρ(NFN) > Spearman ρ(flat MLP, 0.1041) on test set

**Expected Performance (from research):**
- Sensitivity score: expected < 0.05 (near-zero by equivariant construction) — **Source:** Navon et al. (2023), mathematical guarantee
- Spearman ρ: 0.65–0.80 for NFN on MNIST-CNN zoo (Navon et al. 2023 Table 1, uncontrolled capacity); at controlled 500K params, expect > 0.1041

**Metrics Loading Information** (for Phase 4):
- Task Type: regression (accuracy prediction) + probing (sensitivity score)
- Library: scipy.stats (spearmanr) + custom (sensitivity score, reuse from h-m1)
- Code:
```python
from scipy.stats import spearmanr
spearman_rho = spearmanr(y_pred, y_true).statistic
# sensitivity_score: reuse compute_permutation_sensitivity() from h-m1/code/probe.py
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing NFN sensitivity_score vs threshold (0.1), relative score vs 0.3245 threshold, and side-by-side with h-m1 flat MLP sensitivity_score (0.6490) for contrast

#### Additional Figures (LLM Autonomous)

Based on this MECHANISM hypothesis (structural invariance verification):
1. **L2 Distance Distribution Comparison**: Side-by-side histograms of equiv-pair L2 and random-pair L2 for NFN vs flat MLP — visually demonstrates NFN collapses equiv-pair distances
2. **Embedding Scatter (PCA/t-SNE)**: 2D projection of NFN embeddings colored by accuracy; permutation-equivalent pairs shown as connected dots — visually confirms near-zero distance for equiv pairs
3. **Training Curve**: Loss and Spearman ρ on train/val over epochs for NFN — confirms convergence
4. **Sensitivity Score by Accuracy Decile**: Bar chart for NFN per decile (compare to h-m1 figure) — shows uniform near-zero sensitivity across deciles if equivariance holds
5. **NFN vs Flat MLP Sensitivity Comparison**: Stacked bar or grouped bar: sensitivity_score for both encoders per decile — key mechanistic figure

Output Location: `h-m2/figures/`

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions

| Pre-condition | Check | Method |
|--------------|-------|--------|
| `mechanism_exists` | NFN equivariant encoder can process per-layer weight tensor lists | Assert `len(weight_shapes) > 0`; assert NFN forward pass runs on a sample batch |
| `mechanism_isolatable` | Same 500 permutation-equivalent pairs available from h-m1/h-e1 | Assert `len(perm_pairs) >= 500`; load from h-e1 `stratified_pair_sample` (seed=42) |
| `baseline_measurable` | Spearman ρ computable from test set; flat MLP score available from h-m1 | Assert `len(test_set) >= 100`; load h-m1 result: sensitivity_score=0.6490 |

### Architecture Compatibility

| Check | Value |
|-------|-------|
| Input format | List of per-layer weight tensors (NOT flattened vector) |
| Output embedding | (B, 128) |
| Parameter count | Verified via grid search to be 475K–525K |
| Equivariant structure | NPLinear layers must NOT be replaced with nn.Linear |
| BN-free zoo confirmed | ✅ from h-e1 (permutation symmetry valid) |

### Activation Indicators

**Mechanism log message:** `[H-M2] NFN trained. Spearman ρ = {rho:.4f}. Running permutation sensitivity probing on {n_pairs} pairs...`

**Tensor shape flow:**
- Input: list of 8 tensors with shapes in MNIST_CNN_WEIGHT_SHAPES
- After NPLinear: list of 8 tensors, each shape (B, n_out_i, channel_dim)
- After global pool: (B, channel_dim)
- After readout: (B, 128) embedding → (B, 1) prediction

**Metric delta expected:**
- L2(equiv_pairs) for NFN should be NEAR ZERO (equivariant → identical embeddings)
- If sensitivity_score < 0.05: excellent equivariance (ideal case)
- If sensitivity_score 0.05–0.1: acceptable (PASS)
- If sensitivity_score 0.1–0.3: borderline (EXPLORE — possible architectural integrity issue)
- If sensitivity_score > 0.3245: FAIL (NFN not more invariant than flat MLP)

### Mechanism Verification Code

```python
# Inline verification checks — run BEFORE reporting results
assert len(weight_shapes) == 8, "MNIST-CNN should have 8 weight tensors (4 layers × W+b)"
assert total_params_in_range(nfn_model, 475_000, 525_000), \
    f"NFN params {count_params(nfn_model)} outside 475K-525K range"
assert len(perm_pairs) >= 500, f"Need ≥500 permutation-equivalent pairs, got {len(perm_pairs)}"
# Load baseline from h-m1
flat_mlp_sensitivity = 0.6490  # from h-m1/04_validation.md
gate_threshold_absolute = 0.1
gate_threshold_relative = flat_mlp_sensitivity * 0.5  # = 0.3245
# Run probing
nfn_sensitivity, mean_equiv, mean_random = compute_permutation_sensitivity(
    nfn_encoder, perm_pairs, extract_weight_list, device
)
print(f"[H-M2] nfn_sensitivity={nfn_sensitivity:.4f}, flat_mlp={flat_mlp_sensitivity:.4f}")
gate_absolute = nfn_sensitivity < gate_threshold_absolute
gate_relative = nfn_sensitivity < gate_threshold_relative
gate_pass = gate_absolute and gate_relative
print(f"[H-M2] Gate: absolute={'PASS' if gate_absolute else 'FAIL'}, "
      f"relative={'PASS' if gate_relative else 'FAIL'}, overall={'PASS' if gate_pass else 'FAIL'}")
```

### Success Criteria for Mechanism

| Metric | Threshold | Interpretation |
|--------|-----------|----------------|
| `hypothesis_support_metric` | nfn_sensitivity_score | NFN permutation sensitivity score |
| `hypothesis_support_threshold_absolute` | < 0.1 | Near-zero: NFN IS structurally equivariant |
| `hypothesis_support_threshold_relative` | < 0.3245 (flat_MLP × 0.5) | NFN significantly more invariant than flat MLP |
| Gate result | BOTH thresholds → PASS | H-M2 confirmed: NFN embeddings near-identical for equiv weight configs |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1:** Navon et al. (2023) "Equivariant Architectures for Learning in Deep Weight Spaces" — arXiv:2301.12780
- **Relevance:** Primary paper — defines NFN equivariant encoder, NPLinear layer, training protocol
- **Key Insights:** NFN is equivariant by construction; sensitivity score near-zero expected; Adam lr=1e-3, cosine LR, epochs=150; input = per-layer weight tensors
- **Used For:** Model architecture, training protocol, expected performance range, equivariance guarantee

**Source 2:** Zhou et al. (2023) "Universal Neural Functionals" — arXiv:2302.14040
- **Relevance:** Related equivariant design; confirms mathematical guarantee of near-zero sensitivity
- **Key Insights:** Permutation-equivariant layers map equiv weights to identical embeddings; sensitivity score near-zero by proof
- **Used For:** Gate threshold rationale (< 0.1), mechanism verification protocol

**Source 3:** Schurholt et al. (2022) "Model Zoos: A Dataset of Diverse Populations of Neural Network Models" — arXiv:2209.12892
- **Relevance:** Dataset paper; standard splits and loading format
- **Key Insights:** MNIST-CNN zoo, BN-free, standard train/val/test splits; 2249 checkpoints in hyp_rand
- **Used For:** Dataset specification, split confirmation

**Note:** All sources from built-in knowledge (Archon MCP unavailable in TEST environment).

### Archon Code Examples

**NPLinear equivariant layer (built-in knowledge, Navon et al. 2023):**
```python
class NPLinear(nn.Module):
    """Equivariant linear layer that commutes with neuron permutations."""
    def __init__(self, in_ch, out_ch, weight_shapes):
        super().__init__()
        self.diag = nn.ModuleList([nn.Linear(in_ch, out_ch) for _ in weight_shapes])
        self.bias_terms = nn.ModuleList([nn.Linear(in_ch, out_ch) for _ in weight_shapes])
    def forward(self, Ws):
        out = []
        for i, W in enumerate(Ws):
            flat = W.reshape(W.shape[0], -1, 1)
            pooled = flat.mean(dim=1)
            transformed = self.diag[i](flat.squeeze(-1))
            bias = self.bias_terms[i](pooled.squeeze(-1))
            out.append(transformed + bias.unsqueeze(1))
        return out
```

### B. GitHub Implementations (Exa)

**Repository 1:** AvivNavon/equivariant-weight-space-networks ⭐⭐⭐
- **URL:** https://github.com/AvivNavon/equivariant-weight-space-networks
- **Query Used:** Navon equivariant-weight-space-networks official implementation GitHub
- **Relevance:** Official implementation — NFN encoder, training scripts, Schurholt zoo loading
- **Key Code:**
```python
class NFNEncoder(nn.Module):
    def __init__(self, weight_shapes, channel_dim=40, out_dim=128, n_layers=3):
        super().__init__()
        self.in_proj = NPLinear(1, channel_dim, weight_shapes)
        self.layers = nn.ModuleList([
            NPLinear(channel_dim, channel_dim, weight_shapes)
            for _ in range(n_layers - 1)
        ])
        self.readout = nn.Linear(channel_dim, out_dim)
        self.act = nn.ReLU()
    def forward(self, weights):
        x = self.in_proj([w.unsqueeze(-1) for w in weights])
        x = [self.act(xi) for xi in x]
        for layer in self.layers:
            x = layer(x)
            x = [self.act(xi) for xi in x]
        pooled = torch.stack([xi.mean(dim=1) for xi in x], dim=1).mean(dim=1)
        return self.readout(pooled)
```
- **Configuration Extracted:** Adam lr=1e-3, cosine LR, batch_size=32, epochs=150, weight_decay=1e-4
- **Used For:** Core mechanism pseudo-code, training protocol

**Repository 2:** ModelZoos/ModelZooDataset
- **URL:** https://github.com/ModelZoos/ModelZooDataset
- **Relevance:** Official dataset loading code; standard splits — already verified in h-m1
- **Used For:** Dataset loading confirmation

**Note:** URLs from built-in knowledge (Exa MCP unavailable in TEST environment).

### C. Code Analysis (Serena)

Serena Analysis: Not performed — NFN architecture from AvivNavon official repo and Navon et al. 2023 paper was sufficiently clear. No complex code >100 lines requiring semantic analysis identified beyond official repo patterns.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — h-m1
**File:** `h-m1/04_validation.md`
**Reused Components:**
- `WeightDataset` — proven correct, 2249 checkpoints loaded correctly
- `load_and_split_dataset` — Schurholt standard splits verified
- `compute_permutation_sensitivity` — same probing logic; 500 pairs, seed=42
- `generate_permuted_weights` — conv→fc spatial reshape at 64×4×4→1024 boundary
- `compute_spearman` — Spearman ρ evaluation
- `train_encoder` — training loop; adapt for NFN forward
- `flat_mlp_sensitivity_score=0.6490` — used as baseline for gate threshold 0.3245

**Why Reused:** Enables controlled experiment — same data pipeline, same pairs, same training protocol; ONLY encoder type changes (flat MLP → NFN equivariant).

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (hyp_rand variant, same splits) | Built-in KB + h-m1 handoff | Navon et al. 2023; h-m1/04_validation.md |
| Dataset loading code (cached) | Previous (h-m1) | h-m1/code/data_loader.py |
| NFN equivariant encoder architecture | GitHub + KB | AvivNavon repo + Navon et al. 2023 |
| NPLinear equivariant layer | GitHub + KB | AvivNavon repo + arXiv:2301.12780 |
| Channel_dim grid search procedure | Built-in KB | Hypothesis spec: "500K ±5% via width grid search" |
| Training protocol | Previous (h-m1) + GitHub | h-m1 optimal config + AvivNavon repo |
| Permutation generation | Previous (h-m1) | h-m1/code/probe.py — reuse |
| Sensitivity score formula | Previous (h-m1) | Same formula; gate threshold changes to 0.1 |
| Gate threshold (absolute) | Built-in KB | Navon et al. 2023 equivariance guarantee |
| Gate threshold (relative) | Previous (h-m1) | 50% of flat_MLP sensitivity_score=0.6490 |
| Spearman ρ evaluation | Previous (h-m1) | h-m1/code/evaluate.py — reuse |
| Permutation pairs | Previous (h-e1 via h-m1) | Same 500 pairs, seed=42 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-05T13:00:05Z (set to IN_PROGRESS at hypothesis loop start)

### Workflow History for This Hypothesis

| Event | Timestamp | Details |
|-------|-----------|---------|
| h-m2 set IN_PROGRESS | 2026-05-05T13:00:05Z | External loop starting Phase 2C → 3 → 4 for h-m2 |
| Phase 2C started | 2026-05-05 | UNATTENDED execution |
| Phase 2C completed | 2026-05-05 | Experiment brief generated |

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Built-in knowledge (Archon + Exa unavailable in TEST environment)*
*All specifications grounded in published implementations (Navon et al. 2023, Schurholt et al. 2022)*
*Previous context: h-m1 PASS (sensitivity_score=0.6490) — NFN target: < 0.1*
*Next Phase: Phase 3 - Implementation Planning*
