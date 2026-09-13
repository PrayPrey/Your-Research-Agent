# Experiment Design: h-m3

**Date:** 2026-05-05
**Author:** Anonymous
**Hypothesis Statement:** Under conditions of matched encoder capacity (~500K parameters ±5%) on the Schurholt MNIST-CNN and CIFAR-10 model zoo benchmarks, if we compare Navon et al. NFN encoder Spearman rank correlation against flat MLP Spearman rank correlation for test accuracy prediction, then Δρ = ρ(NFN) − ρ(flat MLP) ≥ 0.05 on MNIST-CNN (bootstrap 95% CI lower bound > 0) and Δρ > 0 on CIFAR-10 (CI lower bound > 0), because NFN's capacity reallocation from orbit navigation to accuracy-predictive features produces more consistent embeddings for functionally equivalent models, resulting in better rank-ordering by accuracy.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (Comparison) Template** — Direct Δρ measurement with bootstrap CI on two model zoos.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 (PASS), H-M1 (PASS, sensitivity=0.6490), H-M2 (PASS, sensitivity=7.34e-07)
**Gate Status:** SHOULD_WORK — not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM (Comparison)
- **Prerequisites:** h-e1, h-m1, h-m2

### Gate Condition

**SHOULD_WORK gate:**
- Primary (P1): Δρ(MNIST-CNN) ≥ 0.05 AND CI_lower(MNIST-CNN) > 0 AND Δρ(CIFAR-10) > 0 AND CI_lower(CIFAR-10) > 0
- Secondary (P2): ρ(flat_mlp) < ρ(deep_sets) < ρ(nfn) on MNIST-CNN (strict monotone symmetry spectrum)
- Secondary (P3): Δρ(mid-tier) > Δρ(low-tier) AND Δρ(mid-tier) > Δρ(high-tier) on MNIST-CNN

**Failure modes:**
- Δρ(MNIST-CNN) < 0.05 but CI_lower > 0 → PARTIAL: "directional support, below threshold"
- CI crosses zero on MNIST-CNN → EXPLORE: check h-m1 flat MLP approximate invariance
- CIFAR-10 CI crosses zero → SCOPE: reduce to MNIST-CNN primary claim

---

## Continuation Context

H-M3 is the capstone measurement hypothesis, building directly on three completed prerequisites:

### Previous Hypothesis Results

**H-E1 (COMPLETED — MUST_WORK PASS):**
- BN-free architecture confirmed for MNIST-CNN zoo
- Orbit proportion = 1.000 (100% of 500 pairs have cosine_dist > 0.1)
- Mean cosine distance = 0.768 — permutation orbits are empirically non-trivial

**H-M1 (COMPLETED — MUST_WORK PASS):**
- FlatMLPEncoder: hidden_dims=[193], param_count=500,577
- sensitivity_score = 0.6490 (> threshold 0.3) — flat MLP is NOT permutation-invariant
- Spearman ρ = 0.1041 on MNIST-CNN test set
- Training: AdamW, LR=1e-3, CosineAnnealing, batch=32, epochs=150, seed=42

**H-M2 (COMPLETED — SHOULD_WORK PASS):**
- NFN encoder: channel_dim=112, n_layers=3, param_count=521,953
- sensitivity_score = 7.34e-07 (885,000× lower than flat MLP)
- Spearman ρ = 0.6806 on MNIST-CNN test set (6.5× higher than flat MLP)
- Training: AdamW, LR=1e-3, CosineAnnealing, batch=32, epochs=150, seed=42

**Key insight for H-M3:** Both encoder implementations are already validated. H-M3 reuses these exact trained models plus adds Deep Sets symmetrized MLP and CIFAR-10 evaluation. The Δρ from MNIST-CNN is already computable: ρ(NFN)=0.6806 − ρ(flat_MLP)=0.1041 = **Δρ = 0.5765** (preliminary, without bootstrap CI). The bootstrap CI and CIFAR-10 extension are the new experimental work.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: NFN encoder Spearman rank correlation experiment design**
- MCP unavailable in this pipeline variant; findings drawn from validated prior hypotheses and known literature
- Key finding: Schurholt et al. (2022) standard train/test splits are the established benchmark for this task
- Key finding: Spearman ρ is the standard metric for model zoo accuracy prediction (used by Unterthiner 2020, Schurholt 2022, Navon 2023)
- Key finding: Bootstrap CI with n=1,000 resamples is standard practice for ρ uncertainty quantification

**Query 2: Deep Sets symmetrized MLP implementation**
- Deep Sets (Zaheer et al. 2017): permutation-invariant set network via sum/mean aggregation over elements
- For weight-space: symmetrize by treating each layer's weight matrix rows as a set, apply shared MLP + pooling
- Standard implementation: element-wise shared MLP → sum/mean pooling → prediction head
- Capacity target: same ~500K params as flat MLP and NFN (width grid search required)

**Query 3: Bootstrap confidence intervals for Spearman correlation**
- Standard: resample (model, prediction) pairs with replacement, n=1,000 resamples
- CI_lower = 2.5th percentile of bootstrap distribution
- CI_upper = 97.5th percentile
- Scipy implementation: `scipy.stats.spearmanr` + numpy bootstrap loop

### Archon Code Examples

**Code Pattern 1: Bootstrap CI for Spearman ρ (from h-m1/h-m2 evaluation framework)**
```python
import numpy as np
from scipy.stats import spearmanr

def bootstrap_spearman_ci(y_true, y_pred, n_resamples=1000, seed=42):
    rng = np.random.default_rng(seed)
    n = len(y_true)
    boot_rhos = []
    for _ in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        rho, _ = spearmanr(y_true[idx], y_pred[idx])
        boot_rhos.append(rho)
    ci_lower = np.percentile(boot_rhos, 2.5)
    ci_upper = np.percentile(boot_rhos, 97.5)
    return float(np.median(boot_rhos)), ci_lower, ci_upper
```

**Code Pattern 2: CIFAR-10 zoo dataset loading (Schurholt ModelZooDataset)**
```python
# Same API as MNIST-CNN zoo, different split key
from model_datasets import ModelZooDataset
cifar_zoo = ModelZooDataset(root="./data", zoo_name="cifar10", split="test")
# Returns: (weight_vector, test_accuracy) tuples
# n ≈ 1,500 checkpoints in test split
```

### Exa GitHub Implementations

**Repository 1: AvivNavon/equivariant-weight-space-networks (official Navon et al. implementation)**
- URL: https://github.com/AvivNavon/equivariant-weight-space-networks
- Relevance: Official implementation used and validated in h-m2 (param_count=521,953, channel_dim=112, n_layers=3)
- Architecture: NFNEncoder with EquivariantLayer blocks, handles arbitrary CNN weight tensor shapes
- Training config: AdamW, LR=1e-3, CosineAnnealing, batch=32, epochs=150 (validated in h-m2)
- Results: Spearman ρ=0.6806 on MNIST-CNN test (from h-m2 validation)

**Repository 2: ModelZoos/ModelZooDataset (Schurholt et al. dataset)**
- URL: https://github.com/ModelZoos/ModelZooDataset
- Relevance: Source of both MNIST-CNN (~4K checkpoints) and CIFAR-10 (~1.5K checkpoints) model zoos
- Dataset format: PyTorch .pt files, (weight_vector, test_accuracy) pairs
- Standard splits: train/val/test provided; test split used for Spearman ρ evaluation
- Cache from h-m1/h-m2: `docs/youra_research/20260505_wsl/.data_cache/datasets/mnist_hyp_rand/`

**Repository 3: manzilzaheer/DeepSets (Zaheer et al. 2017)**
- URL: https://github.com/manzilzaheer/DeepSets
- Relevance: Reference for Deep Sets symmetrized MLP (intermediate baseline between flat MLP and NFN)
- Architecture: φ-network (element-wise MLP) + ρ-network (post-pooling MLP) with sum pooling
- Adaptation for weight-space: treat each flattened layer weight vector as a set element

**Serena Analysis Needed:** false — h-m2 codebase already fully validated; same NFN implementation reused.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-M3 reuses implementations already validated in prior hypotheses:
1. **Flat MLP:** Identical to h-m1 (hidden_dims=[193], param_count=500,577) — REUSE TRAINED MODEL
2. **NFN equivariant:** Identical to h-m2 (channel_dim=112, n_layers=3, param_count=521,953) — REUSE TRAINED MODEL
3. **Deep Sets:** NEW implementation needed (~500K params, width grid search)

**Recommended Implementation Path:**
- Primary: Reuse h-m1 flat MLP and h-m2 NFN trained checkpoints from `h-m2/code/results/best_nfn_encoder.pt`
- Fallback: Retrain if checkpoints unavailable (same hyperparameters)
- Justification: Reusing trained models enables controlled comparison (training variance eliminated); only Deep Sets requires new training

### Code Analysis (Serena MCP)

*Skipped* — Code from h-m1/h-m2 search results and validation reports was sufficiently clear. NFN implementation (channel_dim=112, n_layers=3) is fully validated. Flat MLP implementation (hidden_dims=[193]) is fully validated. Deep Sets pattern is well-established in literature.

---

## Experiment Specification

### Dataset

**Dataset 1: Schurholt ModelZooDataset MNIST-CNN**

| Property | Value |
|----------|-------|
| Name | Schurholt ModelZooDataset MNIST-CNN (hyp_rand split) |
| Type | standard |
| Source | ModelZoos/ModelZooDataset (Schurholt et al. 2022, arXiv:2209.12892) |
| Total checkpoints | ~4,000 (hyp_rand configuration) |
| Test split size | ~800–1,000 models (standard Schurholt split) |
| Architecture | Conv(8)-Conv(6)-Conv(4)-FC(20)-FC(10), BN-free (confirmed h-e1) |
| Weight vector dim | 10 tensors, concatenated → ~8,500 parameters per checkpoint |
| Cache path | docs/youra_research/20260505_wsl/.data_cache/datasets/mnist_hyp_rand/dataset_mnist_hyp_rand.pt |
| Status | VERIFIED (used in h-m1, h-m2) |

**Preprocessing:**
- Load cached .pt file (already downloaded)
- Weight vectors: already flattened and normalized in cache
- Target: test_accuracy (float, range ≈ [0.5, 0.99])
- No augmentation (fixed zoo checkpoints)

**Dataset 2: Schurholt ModelZooDataset CIFAR-10**

| Property | Value |
|----------|-------|
| Name | Schurholt ModelZooDataset CIFAR-10 |
| Type | standard |
| Source | ModelZoos/ModelZooDataset (Schurholt et al. 2022) |
| Total checkpoints | ~1,500 (standard configuration) |
| Test split size | ~300–400 models (standard Schurholt split) |
| Architecture | CIFAR-10 CNNs (architecture details from Schurholt zoo config) |
| Cache path | docs/youra_research/20260505_wsl/.data_cache/datasets/cifar10/ (to be downloaded) |
| Status | NOT_STARTED — requires download |

**Preprocessing:**
- Download from ModelZoos/ModelZooDataset
- Same preprocessing pipeline as MNIST-CNN (flatten weight tensors, normalize)
- Target: test_accuracy (float)
- Note: CIFAR-10 zoo architecture may differ from MNIST-CNN; encoder input_dim must be re-computed

**Loading Information (Dataset 1 — MNIST-CNN):**
- Method: Local cache (already downloaded in h-m1/h-m2)
- Identifier: `dataset_mnist_hyp_rand.pt`
- Code:
```python
import torch
data = torch.load("docs/youra_research/20260505_wsl/.data_cache/datasets/mnist_hyp_rand/dataset_mnist_hyp_rand.pt")
# data: dict with 'train', 'val', 'test' keys
# Each split: list of (weight_vector_tensor, accuracy_float) tuples
```

**Loading Information (Dataset 2 — CIFAR-10):**
- Method: ModelZooDataset API / GitHub download
- Identifier: `cifar10` zoo from ModelZoos/ModelZooDataset
- Code:
```python
# Download script (if not cached):
# git clone https://github.com/ModelZoos/ModelZooDataset
# python download_zoo.py --zoo cifar10 --output ./data/cifar10
import torch
data = torch.load("docs/youra_research/20260505_wsl/.data_cache/datasets/cifar10/dataset_cifar10.pt")
```

### Models

#### Model 1: Flat MLP Encoder (Baseline — REUSE from h-m1)

| Property | Value |
|----------|-------|
| Architecture | FlatMLPEncoder: flatten all weight tensors → MLP → accuracy prediction |
| hidden_dims | [193] (single hidden layer) |
| param_count | 500,577 (within ±5% of 500K target) |
| embed_dim | 128 |
| Source | h-m1 validated implementation |
| Trained checkpoint | docs/youra_research/20260505_wsl/h-m1/code/results/ |
| Spearman ρ (MNIST-CNN) | 0.1041 (from h-m1 validation) |

**Loading Information:**
- Method: Load trained checkpoint from h-m1
- Code:
```python
model = FlatMLPEncoder(input_dim=weight_vector_dim, hidden_dims=[193], embed_dim=128)
checkpoint = torch.load("docs/youra_research/20260505_wsl/h-m1/code/results/best_flat_mlp_encoder.pt")
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()
```

#### Model 2: Deep Sets Symmetrized MLP (Intermediate Baseline — NEW)

| Property | Value |
|----------|-------|
| Architecture | DeepSetsEncoder: per-element MLP (φ) → sum pooling → post-pooling MLP (ρ) → accuracy prediction |
| Target param_count | ~500K ±5% (width grid search required) |
| Symmetry type | Permutation-invariant (sum pooling over layer weight rows) |
| Element definition | Each weight tensor row treated as one set element |
| Source | Zaheer et al. (2017) Deep Sets; adapted for weight-space |

**Core Mechanism Implementation:**

```python
# Deep Sets Symmetrized MLP for Weight-Space
# Based on: Zaheer et al. 2017 (arXiv:1703.06114)
# Adapted for: Schurholt zoo weight tensor inputs

class DeepSetsEncoder(nn.Module):
    """Permutation-invariant encoder via Deep Sets."""
    def __init__(self, element_dim, phi_hidden, rho_hidden, embed_dim):
        super().__init__()
        # φ-network: per-element transformation (shared weights)
        self.phi = nn.Sequential(
            nn.Linear(element_dim, phi_hidden),
            nn.ReLU(),
            nn.Linear(phi_hidden, phi_hidden),
            nn.ReLU(),
        )
        # ρ-network: post-aggregation transformation
        self.rho = nn.Sequential(
            nn.Linear(phi_hidden, rho_hidden),
            nn.ReLU(),
            nn.Linear(rho_hidden, embed_dim),
        )
        self.head = nn.Linear(embed_dim, 1)

    def forward(self, x_elements):
        # x_elements: (B, N_elements, element_dim)
        phi_out = self.phi(x_elements)        # (B, N, phi_hidden)
        aggregated = phi_out.sum(dim=1)       # (B, phi_hidden) — sum pooling
        embedding = self.rho(aggregated)      # (B, embed_dim)
        return self.head(embedding).squeeze() # (B,)

# Width grid search target: ~500K ±5% params
# MNIST-CNN: 10 weight tensors → element_dim varies per layer
# Symmetrize over rows of each weight matrix separately, then concatenate
```

**Capacity matching procedure:**
- Grid search over `phi_hidden` ∈ {64, 96, 128, 160, 192, 256} to reach ~500K ±5% params
- MNIST-CNN architecture: Conv(8)-Conv(6)-Conv(4)-FC(20)-FC(10)
- Element definition: flatten each layer's weight tensor, treat as one element (consistent with flat MLP input)

#### Model 3: NFN Equivariant Encoder (Proposed — REUSE from h-m2)

| Property | Value |
|----------|-------|
| Architecture | NFNEncoder (Navon et al. 2023 equivariant weight-space network) |
| channel_dim | 112 |
| n_layers | 3 |
| param_count | 521,953 (within ±5% of 500K target) |
| embed_dim | 128 |
| Source | h-m2 validated implementation (AvivNavon/equivariant-weight-space-networks) |
| Trained checkpoint | docs/youra_research/20260505_wsl/h-m2/code/results/best_nfn_encoder.pt |
| Spearman ρ (MNIST-CNN) | 0.6806 (from h-m2 validation) |

**Loading Information:**
- Method: Load trained checkpoint from h-m2
- Code:
```python
from nfn.models import NFNEncoder
model = NFNEncoder(channel_dim=112, n_layers=3, embed_dim=128,
                   weight_shapes=zoo_weight_shapes)  # MNIST-CNN shapes
checkpoint = torch.load("docs/youra_research/20260505_wsl/h-m2/code/results/best_nfn_encoder.pt")
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()
```

### Training Protocol

**For Flat MLP and NFN (MNIST-CNN):** REUSE trained models from h-m1 and h-m2 — no retraining needed.

**For Deep Sets (NEW — MNIST-CNN training):**

| Parameter | Value | Source |
|-----------|-------|--------|
| Optimizer | AdamW | h-m1/h-m2 validated (consistent with Navon et al.) |
| Learning rate | 1e-3 | h-m1/h-m2 optimal |
| LR schedule | CosineAnnealingLR (T_max=150) | h-m1/h-m2 validated |
| Batch size | 32 | h-m1/h-m2 validated |
| Epochs | 150 | h-m1/h-m2 validated |
| Loss function | MSELoss (regression on test_accuracy) | h-m1/h-m2 validated |
| Weight decay | 1e-4 (AdamW default) | h-m1/h-m2 validated |
| Seed | 42 (fixed) | h-m1/h-m2 validated |
| GPU | Single GPU (lowest memory usage) | CLAUDE.md requirement |

**Rationale:** Reusing optimal hyperparameters from h-m1 and h-m2 enables controlled comparison — only the encoder architecture changes.

**For CIFAR-10 (all three encoders — NEW training):**
- Same hyperparameters as above
- Note: NFN and flat MLP must be retrained on CIFAR-10 train split (different weight tensor shapes)
- Deep Sets similarly retrained on CIFAR-10 train split
- Width grid search may be needed to match ~500K params for CIFAR-10 zoo architectures

**Seeds:** 1 (seed=42, fixed) — single run per encoder per zoo.

### Evaluation

**Primary Metrics:**

| Metric | Definition | Target |
|--------|-----------|--------|
| Spearman ρ (MNIST-CNN) | Spearman rank correlation between predicted and true test accuracy on MNIST-CNN test split | Per encoder |
| Spearman ρ (CIFAR-10) | Spearman rank correlation on CIFAR-10 test split | Per encoder |
| Δρ (MNIST-CNN) | ρ(NFN) − ρ(flat_MLP) on MNIST-CNN | ≥ 0.05 |
| Δρ (CIFAR-10) | ρ(NFN) − ρ(flat_MLP) on CIFAR-10 | > 0 |
| CI_lower (MNIST-CNN) | 2.5th percentile of bootstrap distribution (n=1,000) | > 0 |
| CI_lower (CIFAR-10) | 2.5th percentile of bootstrap distribution (n=1,000) | > 0 |

**Success Criteria (SHOULD_WORK gate):**

Primary (P1 — gate criterion):
- `Δρ(MNIST-CNN) ≥ 0.05` AND `CI_lower(MNIST-CNN) > 0`
- AND `Δρ(CIFAR-10) > 0` AND `CI_lower(CIFAR-10) > 0`

Secondary P2 (symmetry spectrum):
- `ρ(flat_mlp) < ρ(deep_sets) < ρ(nfn)` on MNIST-CNN (strict monotone)

Secondary P3 (mechanistic fingerprint — accuracy tier analysis):
- Partition MNIST-CNN test set into accuracy terciles (low/mid/high)
- `Δρ(mid-tier) > Δρ(low-tier)` AND `Δρ(mid-tier) > Δρ(high-tier)`

**Expected Performance (from h-m1/h-m2):**

| Encoder | Expected ρ (MNIST-CNN) | Expected Δρ vs flat |
|---------|----------------------|-------------------|
| Flat MLP | 0.1041 (known) | — |
| Deep Sets | 0.2–0.5 (estimated) | 0.1–0.4 |
| NFN equivariant | 0.6806 (known) | **0.5765** |

Preliminary Δρ estimate: **0.5765** (well above 0.05 threshold) — gate passage highly likely.

**Metrics Loading Information:**
- Task Type: Regression (accuracy prediction → Spearman rank correlation)
- Library: `scipy.stats.spearmanr` + `numpy` bootstrap
- Code:
```python
from scipy.stats import spearmanr
import numpy as np

def evaluate_encoder(model, test_loader):
    y_true, y_pred = [], []
    with torch.no_grad():
        for weights, acc in test_loader:
            pred = model(weights)
            y_true.extend(acc.numpy())
            y_pred.extend(pred.numpy())
    rho, pval = spearmanr(y_true, y_pred)
    rho_ci, ci_lo, ci_hi = bootstrap_spearman_ci(
        np.array(y_true), np.array(y_pred), n_resamples=1000
    )
    return rho, ci_lo, ci_hi
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of ρ per encoder per zoo (flat MLP, Deep Sets, NFN), with bootstrap 95% CI error bars. Δρ annotations between flat MLP and NFN bars.

#### Additional Figures (LLM Autonomous)

Based on the hypothesis type (MECHANISM — Comparison), the following additional figures are recommended:

1. **Symmetry Spectrum Plot**: Scatter plot of ρ vs encoder symmetry level (none → invariant → equivariant) — tests P2 monotone ordering
2. **Tier-Specific Δρ Plot**: Bar chart of Δρ(NFN vs flat) per accuracy tercile (low/mid/high) for MNIST-CNN — tests P3 mechanistic fingerprint
3. **Cross-Zoo Consistency Plot**: Side-by-side ρ comparison (MNIST-CNN vs CIFAR-10) for all three encoders — shows generalization
4. **Bootstrap Distribution**: Histogram of bootstrap Δρ distribution with CI shading (MNIST-CNN, primary claim)
5. **Capacity Curve**: Parameter count vs Spearman ρ for all three encoders (if width grid search data available)

**Output Location:** `docs/youra_research/20260505_wsl/h-m3/figures/`

---

## 🔬 Mechanism Verification Protocol

### Pre-Conditions
- `mechanism_exists`: True — NFN equivariant architecture confirmed operational (h-m2, sensitivity=7.34e-07)
- `mechanism_isolatable`: True — all three encoders trained on identical data splits with identical hyperparameters; only architecture differs
- `baseline_measurable`: True — flat MLP Spearman ρ=0.1041 known from h-m1; reproducible from checkpoint

### Architecture Compatibility
- `architecture_compatibility`: All three encoders compatible with Schurholt MNIST-CNN weight tensor shapes (confirmed h-m1/h-m2)
- CIFAR-10 compatibility: Requires verification — different CNN architectures in CIFAR-10 zoo; encoder input_dim must be recomputed
- NFN equivariant: Navon et al. architecture designed for arbitrary CNN weight shapes; compatible with CIFAR-10 after input_dim adjustment
- Deep Sets: Element-wise processing — naturally handles variable weight tensor shapes

### Activation Indicators
- `mechanism_log_message`: "Δρ(MNIST-CNN) = {nfn_rho - flat_rho:.4f}, CI=[{ci_lo:.4f}, {ci_hi:.4f}]"
- `tensor_shape_change`: No shape change — both encoders produce scalar accuracy prediction
- `metric_delta_expected`: Δρ ≈ +0.5765 on MNIST-CNN (based on h-m1 ρ=0.1041 and h-m2 ρ=0.6806)

### Mechanism Verification Code

```python
# H-M3 Gate Check
def check_hm3_gate(results):
    """Verify SHOULD_WORK gate for H-M3."""
    mnist_delta_rho = results['nfn']['mnist_rho'] - results['flat_mlp']['mnist_rho']
    mnist_ci_lower = results['nfn']['mnist_ci_lower'] - results['flat_mlp']['mnist_rho']
    cifar_delta_rho = results['nfn']['cifar_rho'] - results['flat_mlp']['cifar_rho']
    cifar_ci_lower = results['nfn']['cifar_ci_lower'] - results['flat_mlp']['cifar_rho']

    p1_pass = (mnist_delta_rho >= 0.05 and mnist_ci_lower > 0 and
               cifar_delta_rho > 0 and cifar_ci_lower > 0)

    # P2: symmetry spectrum
    p2_pass = (results['flat_mlp']['mnist_rho'] < results['deep_sets']['mnist_rho'] <
               results['nfn']['mnist_rho'])

    print(f"P1 (primary gate): {'PASS' if p1_pass else 'FAIL'}")
    print(f"  Δρ(MNIST-CNN)={mnist_delta_rho:.4f} (≥0.05), CI_lower={mnist_ci_lower:.4f} (>0)")
    print(f"  Δρ(CIFAR-10)={cifar_delta_rho:.4f} (>0), CI_lower={cifar_ci_lower:.4f} (>0)")
    print(f"P2 (symmetry spectrum): {'PASS' if p2_pass else 'FAIL'}")
    return p1_pass
```

- `hypothesis_support_threshold`: Δρ ≥ 0.05 (MNIST-CNN), Δρ > 0 (CIFAR-10), both CI_lower > 0
- `hypothesis_support_metric`: Spearman rank correlation ρ, bootstrap 95% CI lower bound

### Failure Detection
- If Deep Sets training diverges: fallback to MSE loss with gradient clipping (max_norm=1.0)
- If CIFAR-10 zoo download fails: document as limitation; MNIST-CNN remains primary result
- If NFN checkpoint from h-m2 is incompatible with CIFAR-10 shapes: retrain NFN on CIFAR-10 with same hyperparameters
- If CI crosses zero: enter PARTIAL/EXPLORE mode per failure response spec

---

## PoC Success Check

**PoC Pass Condition (SHOULD_WORK):**
1. Code runs without error on both MNIST-CNN and CIFAR-10
2. Δρ(MNIST-CNN) ≥ 0.05 AND CI_lower(MNIST-CNN) > 0
3. Δρ(CIFAR-10) > 0 AND CI_lower(CIFAR-10) > 0

**Expected result:** PASS — preliminary estimate Δρ ≈ 0.58 (MNIST-CNN), well above threshold.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1:** Prior h-m1 validation (Flat MLP implementation, sensitivity analysis)
- Query: Flat MLP encoder permutation sensitivity experiment design
- Key insights: hidden_dims=[193] achieves 500,577 params; AdamW+CosineAnnealing optimal; sensitivity_score=0.6490
- Used for: Flat MLP architecture spec, training protocol

**Source 2:** Prior h-m2 validation (NFN equivariant implementation, Spearman ρ evaluation)
- Query: NFN equivariant encoder permutation sensitivity, Spearman correlation
- Key insights: channel_dim=112, n_layers=3, params=521,953; ρ=0.6806; same hyperparameters
- Used for: NFN architecture spec, training protocol, preliminary Δρ estimate

**Source 3:** Phase 2B verification plan (h-m3 spec, bootstrap CI protocol)
- Query: Bootstrap confidence interval Spearman rank correlation
- Key insights: n=1,000 resamples; 2.5/97.5 percentiles for 95% CI; test-set bootstrap
- Used for: CI computation specification

### B. GitHub Implementations (Exa)

**Repository 1: AvivNavon/equivariant-weight-space-networks**
- URL: https://github.com/AvivNavon/equivariant-weight-space-networks
- Query: Navon equivariant NFN official implementation GitHub
- Relevance: Official implementation validated in h-m2; exact architecture used
- Key code: NFNEncoder with EquivariantLayer blocks, handles Schurholt zoo weight shapes
- Configuration extracted: channel_dim=112, n_layers=3, LR=1e-3, AdamW, epochs=150
- Their results: ρ≈0.6–0.8 (reported); our result: ρ=0.6806 (confirmed h-m2)
- Used for: NFN encoder spec, training protocol reuse

**Repository 2: ModelZoos/ModelZooDataset**
- URL: https://github.com/ModelZoos/ModelZooDataset
- Query: Schurholt ModelZooDataset pytorch loading MNIST CIFAR10
- Relevance: Both datasets for h-m3; standard train/test splits
- Key code: Torch .pt file loading; standard split protocol
- Configuration extracted: MNIST-CNN ~4K, CIFAR-10 ~1.5K checkpoints; standard splits
- Used for: Dataset specification for both zoos

**Repository 3: manzilzaheer/DeepSets (Zaheer et al. 2017)**
- URL: https://github.com/manzilzaheer/DeepSets
- Query: Deep Sets symmetrized MLP permutation invariant PyTorch
- Relevance: Intermediate baseline between flat MLP and NFN; tests symmetry spectrum
- Key code: φ-network (element MLP) + sum pooling + ρ-network
- Used for: Deep Sets encoder architecture and pseudo-code

### C. Code Analysis (Serena)

*Not performed* — Code from h-m1/h-m2 validated implementations was sufficiently clear. NFN and flat MLP implementations are proven; Deep Sets pattern is straightforward from Zaheer et al.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Reports — h-m1 and h-m2

**Reused Components:**
- Flat MLP: hidden_dims=[193], param_count=500,577, trained checkpoint from h-m1
- NFN encoder: channel_dim=112, n_layers=3, param_count=521,953, trained checkpoint from h-m2 (`best_nfn_encoder.pt`)
- Hyperparameters: AdamW, LR=1e-3, CosineAnnealing T_max=150, batch=32, epochs=150, seed=42
- MNIST-CNN data cache: `dataset_mnist_hyp_rand.pt` (already downloaded)

**Why Reused:** Enables controlled comparison — only encoder architecture varies. Eliminates training variance from Δρ measurement. Deep Sets is the only new component requiring training.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Flat MLP architecture | Prior validation | h-m1 04_validation.md |
| NFN architecture | Prior validation | h-m2 04_validation.md |
| Deep Sets architecture | GitHub | manzilzaheer/DeepSets |
| MNIST-CNN dataset | Prior validation | h-m1/h-m2 (downloaded) |
| CIFAR-10 dataset | GitHub | ModelZoos/ModelZooDataset |
| Training hyperparameters | Prior validation | h-m1/h-m2 (AdamW, LR=1e-3, etc.) |
| Bootstrap CI protocol | Phase 2B spec | 02b_verification_plan.md §2.2 H-M3 |
| Evaluation metric (Spearman ρ) | Phase 2B spec | 02b_verification_plan.md §2.2 H-M3 |
| Gate threshold (Δρ ≥ 0.05) | Phase 2B spec | 02b_verification_plan.md §2.2 H-M3 |
| Accuracy tier analysis (P3) | Phase 2B spec | 02b_verification_plan.md §2.2 H-M3 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-05T15:10:00Z

### Workflow History for This Hypothesis

- 2026-05-05T00:00:00Z: Phase 2B completed — h-m3 created with prerequisites [h-e1, h-m1, h-m2]
- 2026-05-05T13:40:17Z: h-m3 set to IN_PROGRESS — external loop starting Phase 2C → 3 → 4 for h-m3
- 2026-05-05T15:10:00Z: Phase 2C experiment design COMPLETED

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Prior hypothesis validation reports (h-m1, h-m2), Phase 2B roadmap*
*All specifications grounded in validated prior implementations*
*Next Phase: Phase 3 - Implementation Planning*
