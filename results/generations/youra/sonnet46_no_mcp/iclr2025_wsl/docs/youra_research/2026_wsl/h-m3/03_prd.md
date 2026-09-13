# Product Requirements Document: h-m3
# NFN vs Flat MLP Δρ Controlled Benchmark (MNIST-CNN + CIFAR-10)

---
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - nfr
  - success_criteria
hypothesis_id: h-m3
type: MECHANISM
tier: FULL
generated_at: "2026-05-05T15:15:00Z"
---

## 1. Executive Summary

This experiment measures the Spearman rank correlation advantage (Δρ) of a permutation-equivariant NFN encoder over a flat MLP encoder for test accuracy prediction on two model zoo benchmarks (Schurholt MNIST-CNN and CIFAR-10). H-M3 is the capstone comparison hypothesis of the NFN Delta-Rho pipeline, building directly on validated H-E1, H-M1, and H-M2 results.

**Key deliverable:** Measure Δρ = ρ(NFN) − ρ(flat MLP) with bootstrap 95% CI on both zoos, plus add Deep Sets as an intermediate symmetry-level baseline, confirming a monotone symmetry-performance spectrum.

**Expected result:** Δρ(MNIST-CNN) ≈ 0.5765 (well above ≥0.05 threshold), CI_lower > 0 on both zoos. PASS probability is very high given h-m1 (ρ=0.1041) and h-m2 (ρ=0.6806) are known.

---

## 2. Problem Statement

### 2.1 Research Question

Does replacing a flat MLP encoder with a permutation-equivariant NFN encoder (matched capacity ~500K params) improve Spearman rank correlation for test accuracy prediction on the Schurholt model zoo benchmarks, and by how much (Δρ)?

### 2.2 Hypothesis

Under conditions of matched encoder capacity (~500K parameters ±5%) on the Schurholt MNIST-CNN and CIFAR-10 model zoo benchmarks, if we compare Navon et al. NFN encoder Spearman rank correlation against flat MLP Spearman rank correlation, then:
- Δρ(MNIST-CNN) ≥ 0.05, CI_lower(MNIST-CNN) > 0
- Δρ(CIFAR-10) > 0, CI_lower(CIFAR-10) > 0

Because NFN's capacity reallocation from orbit navigation to accuracy-predictive features produces more consistent embeddings for functionally equivalent models.

### 2.3 Gate Type

**SHOULD_WORK** — directional improvement expected with high confidence from h-m1/h-m2 validated results.

### 2.4 Context from Prior Hypotheses

| Hypothesis | Result | Key Metric |
|-----------|--------|-----------|
| H-E1 | COMPLETED (MUST_WORK PASS) | Orbit proportion=1.000, mean cosine dist=0.768 |
| H-M1 | COMPLETED (MUST_WORK PASS) | Flat MLP sensitivity=0.6490, ρ=0.1041 |
| H-M2 | COMPLETED (SHOULD_WORK PASS) | NFN sensitivity=7.34e-07, ρ=0.6806 |

---

## 3. Functional Requirements

### FR-1: Dataset Loading — MNIST-CNN Zoo

| Property | Value |
|----------|-------|
| Dataset | Schurholt ModelZooDataset MNIST-CNN (hyp_rand) |
| Cache | `docs/youra_research/20260505_wsl/.data_cache/datasets/mnist_hyp_rand/dataset_mnist_hyp_rand.pt` |
| Test split size | ~800–1,000 models |
| Weight vector dim | ~8,500 (10 tensors concatenated) |
| Status | VERIFIED — cached from h-m1/h-m2 |

Loading:
```python
data = torch.load(".data_cache/datasets/mnist_hyp_rand/dataset_mnist_hyp_rand.pt")
# Keys: 'train', 'val', 'test' → list of (weight_tensor, accuracy_float)
```

### FR-2: Dataset Loading — CIFAR-10 Zoo

| Property | Value |
|----------|-------|
| Dataset | Schurholt ModelZooDataset CIFAR-10 |
| Source | ModelZoos/ModelZooDataset (Schurholt et al. 2022) |
| Test split size | ~300–400 models |
| Cache path | `docs/youra_research/20260505_wsl/.data_cache/datasets/cifar10/` |
| Status | NOT_STARTED — requires download |

Download procedure:
```bash
# Clone and download CIFAR-10 zoo
git clone https://github.com/ModelZoos/ModelZooDataset
python download_zoo.py --zoo cifar10 --output .data_cache/datasets/cifar10/
```

### FR-3: Flat MLP Encoder (Baseline — REUSE from H-M1)

| Property | Value |
|----------|-------|
| Architecture | FlatMLPEncoder: flatten weights → MLP → accuracy |
| hidden_dims | [193] |
| param_count | 500,577 |
| embed_dim | 128 |
| Checkpoint | `h-m1/code/results/best_flat_mlp_encoder.pt` |
| MNIST-CNN ρ (known) | 0.1041 |

**Action:** Load trained checkpoint from h-m1. Re-evaluate on MNIST-CNN test split for reproducibility. Train fresh on CIFAR-10 (different weight shapes).

### FR-4: Deep Sets Symmetrized MLP Encoder (Intermediate Baseline — NEW)

| Property | Value |
|----------|-------|
| Architecture | DeepSetsEncoder: φ-MLP (element-wise) → sum pooling → ρ-MLP → accuracy |
| Target params | ~500K ±5% (grid search over phi_hidden) |
| Symmetry | Permutation-invariant (sum pooling) |
| Source | Zaheer et al. 2017 (Deep Sets) |
| Status | New implementation required |

Width grid search:
- `phi_hidden` ∈ {64, 96, 128, 160, 192, 256}
- Target: 475K–525K parameters
- Train on MNIST-CNN train split, then CIFAR-10 train split

### FR-5: NFN Equivariant Encoder (Proposed — REUSE from H-M2)

| Property | Value |
|----------|-------|
| Architecture | NFNEncoder (Navon et al. 2023) |
| channel_dim | 112 |
| n_layers | 3 |
| param_count | 521,953 |
| embed_dim | 128 |
| Checkpoint | `h-m2/code/results/best_nfn_encoder.pt` |
| MNIST-CNN ρ (known) | 0.6806 |

**Action:** Load trained checkpoint from h-m2 for MNIST-CNN. Retrain on CIFAR-10 train split (different weight tensor shapes).

### FR-6: Training Protocol (Deep Sets — MNIST-CNN)

| Hyperparameter | Value |
|---------------|-------|
| Optimizer | AdamW |
| Learning rate | 1e-3 |
| LR schedule | CosineAnnealingLR (T_max=150) |
| Batch size | 32 |
| Epochs | 150 |
| Loss | MSELoss (accuracy regression) |
| Weight decay | 1e-4 |
| Seed | 42 |
| GPU | Single GPU (CUDA_VISIBLE_DEVICES=<empty>) |

### FR-7: CIFAR-10 Training (All Three Encoders)

Same hyperparameters as FR-6. All three encoders trained fresh on CIFAR-10 train split. Width grid search may be needed for Deep Sets on CIFAR-10 (different input_dim).

### FR-8: Primary Evaluation — Spearman ρ with Bootstrap CI

For each encoder × zoo:
```python
from scipy.stats import spearmanr
import numpy as np

def bootstrap_spearman_ci(y_true, y_pred, n_resamples=1000, seed=42):
    rng = np.random.default_rng(seed)
    n = len(y_true)
    boot_rhos = [spearmanr(y_true[rng.integers(0,n,n)], y_pred[rng.integers(0,n,n)])[0]
                 for _ in range(n_resamples)]
    return float(np.median(boot_rhos)), np.percentile(boot_rhos, 2.5), np.percentile(boot_rhos, 97.5)
```

**Metrics table:**

| Metric | Formula | Gate threshold |
|--------|---------|---------------|
| ρ(flat_MLP, MNIST) | Spearman correlation | informational |
| ρ(deep_sets, MNIST) | Spearman correlation | informational |
| ρ(NFN, MNIST) | Spearman correlation | informational |
| Δρ(MNIST) | ρ(NFN) − ρ(flat) | ≥ 0.05 |
| CI_lower(MNIST) | 2.5th bootstrap pct of Δρ | > 0 |
| Δρ(CIFAR-10) | ρ(NFN) − ρ(flat) | > 0 |
| CI_lower(CIFAR-10) | 2.5th bootstrap pct of Δρ | > 0 |

### FR-9: Secondary Evaluation — Symmetry Spectrum (P2)

Test monotone ordering: ρ(flat_MLP) < ρ(deep_sets) < ρ(NFN) on MNIST-CNN test split.

### FR-10: Secondary Evaluation — Accuracy Tier Δρ (P3)

Partition MNIST-CNN test set into accuracy terciles (low/mid/high).  
Compute Δρ(NFN vs flat) per tercile.  
Check: Δρ(mid) > Δρ(low) AND Δρ(mid) > Δρ(high).

### FR-11: Visualization

**Required:**
- Bar chart: ρ per encoder per zoo, with bootstrap 95% CI error bars, Δρ annotations

**Additional (LLM autonomous):**
1. Symmetry spectrum scatter: ρ vs symmetry level (none/invariant/equivariant)
2. Tier-specific Δρ bar chart (P3 mechanistic fingerprint)
3. Cross-zoo consistency: side-by-side MNIST-CNN vs CIFAR-10 ρ
4. Bootstrap Δρ distribution histogram with CI shading
5. Capacity curve (param count vs ρ) if grid search data available

**Output:** `docs/youra_research/20260505_wsl/h-m3/figures/`

### FR-12: Gate Check Function

```python
def check_hm3_gate(results):
    mnist_delta = results['nfn']['mnist_rho'] - results['flat_mlp']['mnist_rho']
    mnist_ci_lo = results['nfn']['mnist_ci_lower'] - results['flat_mlp']['mnist_rho']
    cifar_delta = results['nfn']['cifar_rho'] - results['flat_mlp']['cifar_rho']
    cifar_ci_lo = results['nfn']['cifar_ci_lower'] - results['flat_mlp']['cifar_rho']
    p1 = mnist_delta >= 0.05 and mnist_ci_lo > 0 and cifar_delta > 0 and cifar_ci_lo > 0
    p2 = results['flat_mlp']['mnist_rho'] < results['deep_sets']['mnist_rho'] < results['nfn']['mnist_rho']
    return p1, p2
```

---

## 4. Data Specification

### 4.1 MNIST-CNN Zoo

| Field | Value |
|-------|-------|
| Source | Schurholt et al. 2022 (arXiv:2209.12892) |
| Total checkpoints | ~4,000 (hyp_rand split) |
| Train split | ~2,400 |
| Val split | ~800 |
| Test split | ~800–1,000 |
| Format | PyTorch .pt, dict with 'train'/'val'/'test' |
| Download | **Already cached** — no action needed |
| Cache path | `.data_cache/datasets/mnist_hyp_rand/dataset_mnist_hyp_rand.pt` |

### 4.2 CIFAR-10 Zoo

| Field | Value |
|-------|-------|
| Source | Schurholt et al. 2022 (ModelZoos/ModelZooDataset) |
| Total checkpoints | ~1,500 |
| Test split | ~300–400 |
| Format | PyTorch .pt |
| Download | **Manual download required** — `git clone ModelZooDataset && python download_zoo.py --zoo cifar10` |
| Cache path | `.data_cache/datasets/cifar10/dataset_cifar10.pt` |

---

## 5. Non-Functional Requirements

| NFR | Requirement |
|-----|------------|
| Reproducibility | Fixed seed=42 for all training and bootstrap |
| GPU | Single GPU only (CUDA_VISIBLE_DEVICES=<empty>) |
| Capacity matching | All encoders: 475K–525K parameters (±5% of 500K) |
| Checkpoint reuse | h-m1 flat MLP and h-m2 NFN checkpoints used directly for MNIST-CNN |
| Data consistency | Same MNIST-CNN train/val/test split as h-m1 and h-m2 |
| Output format | Results dict JSON + figures PNG in h-m3/ folder |

---

## 6. Success Criteria (Gate Evaluation)

### Primary Gate (P1 — SHOULD_WORK)
- `Δρ(MNIST-CNN) ≥ 0.05` AND `CI_lower(MNIST-CNN) > 0`
- AND `Δρ(CIFAR-10) > 0` AND `CI_lower(CIFAR-10) > 0`

### Secondary Checks (Informational)
- P2: ρ(flat) < ρ(deep_sets) < ρ(NFN) on MNIST-CNN (monotone symmetry spectrum)
- P3: Δρ(mid-tier) > Δρ(low-tier) AND Δρ(mid-tier) > Δρ(high-tier) on MNIST-CNN

### Expected Values (from h-m1/h-m2)

| Encoder | Expected ρ (MNIST-CNN) |
|---------|----------------------|
| Flat MLP | 0.1041 (known, h-m1) |
| Deep Sets | 0.2–0.5 (estimated) |
| NFN | 0.6806 (known, h-m2) |
| **Δρ(NFN−flat)** | **~0.5765** (well above 0.05) |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=1.12.0
scipy>=1.9.0
numpy>=1.23.0
matplotlib>=3.5.0
seaborn>=0.12.0
pyyaml>=6.0
tqdm>=4.64.0
```

### 7.2 External Repositories (Reference)

| Repository | Purpose | Local Path |
|-----------|---------|-----------|
| AvivNavon/equivariant-weight-space-networks | NFN equivariant encoder (Navon et al. 2023) | Reused from h-m2/code/ |
| ModelZoos/ModelZooDataset | CIFAR-10 zoo download | Download fresh |
| manzilzaheer/DeepSets | Deep Sets reference implementation | Implement inline |

### 7.3 Checkpoint Dependencies

| Checkpoint | Source | Usage |
|-----------|--------|-------|
| `h-m1/code/results/best_flat_mlp_encoder.pt` | H-M1 Phase 4 | MNIST-CNN evaluation |
| `h-m2/code/results/best_nfn_encoder.pt` | H-M2 Phase 4 | MNIST-CNN evaluation |

---

## 8. Out of Scope

- Training flat MLP or NFN from scratch on MNIST-CNN (reuse checkpoints)
- Hyperparameter search (fixed: AdamW, LR=1e-3, epochs=150)
- Additional model zoos beyond MNIST-CNN and CIFAR-10
- Permutation sensitivity analysis (covered in H-M1, H-M2)
