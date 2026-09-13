# Experiment Design: H-M3

**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Hypothesis Statement:** Under the weight-space property prediction setting, if Flat-MLP + permutation augmentation (PermAug) is trained at the same training sizes, then its R² will be strictly between Flat-MLP (no augmentation) and equivariant encoders at training sizes ≤250 models with non-overlapping bootstrap 95% CIs, because permutation augmentation makes the training data distribution approximately symmetric but does not structurally eliminate non-symmetric functions from the hypothesis space, providing partial but not full benefit.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M2 VALIDATED (gate: 6.804× efficiency ratio on CIFAR-10)
**Gate Status:** SHOULD_WORK — strict ordering Flat-MLP < PermAug < GNN-NFN at N ≤ 250 with non-overlapping bootstrap 95% CIs

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (VALIDATED), H-M1 (VALIDATED), H-E1 (VALIDATED)

### Gate Condition

**Type:** SHOULD_WORK

**Pass condition:** Strict ordering Flat-MLP R² < Flat-MLP+PermAug R² < GNN-NFN R² with non-overlapping bootstrap 95% CIs at BOTH N=100 AND N=250 on at least one zoo (CIFAR-10 available; MNIST requires download).

**Secondary criterion:** PermAug closes 50–80% of Flat-MLP-to-equivariant gap (P2 criterion from Phase 2A).

**Failure modes:**
- IF PermAug ≈ equivariant → mechanism is data-distributional, not structural; publishable null result
- IF PermAug ≈ Flat-MLP → augmentation provides no benefit; negative result on A3

---

## Continuation Context

This is a **continuation experiment** building directly on H-E1 and H-M2 results.

**Critical finding from H-M2 (must address):** In H-E1, `flat_mlp_perm_aug` results were **identical** to `flat_mlp` (same seeds used — H-E1 bug). H-M3 CANNOT simply load H-E1 results for PermAug; it must **re-run PermAug training with correct augmentation** (verified by checking that augmentation actually permutes weight tensors during training).

**Proven components reused from H-M2:**
- GNN-NFN as primary equivariant encoder (DWSNets excluded — CNN zoo incompatible)
- CIFAR-10 zoo as primary dataset (MNIST not available locally)
- `analysis.py`: `bootstrap_ci()`, `check_gate()`, `verify_mechanism_activated_batch()`
- `results_loader.py`: H-E1 result loading pattern
- Hyperparameters: Adam lr=1e-3, weight_decay=1e-4, batch_size=64, epochs=100

### Previous Hypothesis Results (H-M2)

| Encoder | N=100 | N=250 | N=500 | N=1000 |
|---------|-------|-------|-------|--------|
| flat_mlp | -0.141 | 0.449 | 0.687 | 0.740 |
| flat_mlp_perm_aug | -0.141 | 0.449 | 0.687 | 0.740 | ← INVALID (same as flat_mlp, must re-run)
| gnn_nfn | -0.016 | 0.767 | 0.847 | 0.864 |

H-M3 primary task: produce valid `flat_mlp_perm_aug` results at N=100, 250 on CIFAR-10.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Permutation augmentation data augmentation symmetry**
- Archon KB does not contain domain-specific weight-space encoder papers (KB is diffusion/image-gen focused). No relevant hits.

**Query 2: Equivariance vs. augmentation structural inductive bias**
- No relevant hits. Archon KB lacks weight-space learning content.

**Conclusion:** Archon KB not applicable to this domain. Research grounded in Exa GitHub and published papers directly.

### Archon Code Examples

- No relevant code examples found in Archon KB for this domain.

### Exa GitHub Implementations

**Query 1: Flat-MLP PermAug implementation — ModelZooDataset**

**Primary Source (HIGHEST PRIORITY):** NFN paper (Zhou et al., NeurIPS 2023) — official implementation
- **URL:** https://github.com/AllanYangZhou/nfn
- **Relevance:** Official NFN code compares MLP vs MLPAug vs NFN (NFNHNP, NFNNP) on property prediction tasks
- **Key finding:** NFN paper Table 3 directly shows the ordering we need to verify:
  - MLP (no aug): MNIST-10=14.5%, FashionMNIST=12.5%, CIFAR-10=16.9%
  - MLPAug (PermAug): MNIST-10=21.0%, FashionMNIST=15.9%, CIFAR-10=18.9%
  - NFN-NP: MNIST-10=92.9%, FashionMNIST=75.6%, CIFAR-10=46.6%
  - **Pattern confirmed:** MLPAug > MLP but << NFN (INR classification task)
- **PermAug implementation:** Zhou et al. describe augmenting with permutations using Eq. 1 (randomly permute neuron orderings in weight tensors). Implementation in `nfn` repo augmentation utilities.
- **Training config (INR classification):** AdamW, lr=5e-3 (DWSNet) / lr=1e-3 (GNN), 250 epochs on ModelNet40; 300/100 epochs on FMNIST

**Query 2: Data augmentations for weight spaces (Shamsian et al., ICML 2024)**
- **URL:** https://proceedings.mlr.press/v235/shamsian24a.html / https://ar5iv.labs.arxiv.org/html/2402.04081
- **Relevance:** Directly analyzes augmentation strategies including random permutation (analogous to PermAug)
- **Key finding:** "Randomized weight space MixUp" = applying random permutations to second weight vector during MixUp. Permutation augmentation alone (without MixUp) is simpler and reduces overfitting but less effective than alignment-based MixUp.
- **Results on ModelNet40:** MixUp + random perm DWS achieves ~73.89% vs MixUp DWS ~74.36% (similar). Random perm alone has smaller benefit than full alignment.
- **Implication for H-M3:** PermAug provides partial benefit over no augmentation, consistent with "intermediate" hypothesis.

**Query 3: ModelZooDataset**
- **URL:** https://github.com/modelzoos/modelzoodataset
- **Key code:** `checkpoints_to_datasets/dataset_base.py` — PyTorch dataset class for loading zoo checkpoints. Pre-computed train/val/test splits available.
- **Critical:** ModelZooDataset CIFAR-10 zoo uses CNN architecture. GNN-NFN (neural-graphs repo) handles CNNs; DWSNets excluded (MLP-only).

**Serena Analysis Needed:** false — PermAug mechanism is straightforward; NFN repo code snippets are clear.

### 🎯 Implementation Priority Assessment

**CRITICAL: Implementation Priority for PermAug**

For the PermAug condition specifically, there is no single authoritative reference implementation on ModelZooDataset. The NFN paper (Zhou 2023) used PermAug on INR datasets, not ModelZooDataset CIFAR-10 zoo. We implement PermAug ourselves following Eq. 1 from Zhou 2023.

**Recommended Implementation Path:**
- Primary: NFN paper (AllanYangZhou/nfn) augmentation pattern (Eq. 1 — random neuron permutation within hidden layers)
- Fallback: Shamsian et al. 2024 "randomized weight space MixUp" (simpler than alignment MixUp)
- Justification: NFN MLPAug is the exact baseline used in the seminal paper; most directly comparable

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. PermAug is ~10 lines: for each batch, randomly sample a permutation of hidden-layer neuron indices and apply it to weight tensor rows/columns. No complex architecture analysis needed.

---

## Experiment Specification

### Dataset

**Name:** ModelZooDataset CIFAR-10 CNN Zoo
**Type:** standard (pre-existing, real)
**Source:** Schürholt et al. 2022 [arXiv:2209.14764], https://github.com/ModelZoos/ModelZooDataset
**Path:** auto (download from modelzoos.cc / Zenodo; code/data/ directory)

**Statistics:**
- ~9,000 CNN models trained on CIFAR-10 with systematic HP variation
- Each model: weights + test accuracy label
- Pre-computed train/val/test splits (same as H-E1, H-M2 — fixed seed)

**Preprocessing:**
- Load via `checkpoints_to_datasets/dataset_base.py` (ModelZooDataset utility)
- Vectorize weights: flatten all weight matrices into a 1D vector per model
- Normalize: per-feature z-score using training set statistics
- No data augmentation at load time (augmentation applied in training loop)

**Subsampling for training sizes:** {100, 250} (primary gate); {500, 1000} for effect size analysis
- Fixed random seed for subsampling (same seed as H-E1/H-M2 for controlled comparison)
- Test set: full held-out test split (same across all training sizes — fixed)

**Loading Information** (for Phase 4 download):
- Method: custom (ModelZooDataset utility)
- Identifier: CIFAR-10 CNN zoo from modelzoos.cc / Zenodo
- Code: `from checkpoints_to_datasets.dataset_base import WeightDataset; ds = WeightDataset(zoo_path, split='train')`

### Models

#### Baseline Model 1: Flat-MLP (no augmentation)

**Architecture:** 3-layer MLP on vectorized weights
**Configuration:** input_dim=vectorized_weight_dim, hidden=256, hidden=128, output=1 (R² regression)
**Parameter count:** ~medium tier, matched to GNN-NFN
**Source:** H-E1 implementation (reuse exactly)

**Loading Information** (for Phase 4):
- Method: custom PyTorch (implemented in H-E1 code)
- Code: `FlatMLP(input_dim, hidden_dims=[256, 128], output_dim=1)`
- Reuse from: `docs/youra_research/h-e1/code/`

#### Baseline Model 2: Flat-MLP + PermAug

**Architecture:** Same Flat-MLP as above
**Key difference:** During training, each batch is augmented with random neuron permutations applied to the vectorized weight tensor before feeding to MLP
**Augmentation count:** 10 random permutations per original sample (following NFN paper convention; maximizes augmentation effectiveness per H-M3 verification protocol)
**Source:** New implementation for H-M3 (H-E1 PermAug was broken — same seeds used)

**Loading Information** (for Phase 4):
- Method: custom PyTorch — same FlatMLP with PermAug wrapper in DataLoader
- Code: `PermAugDataset(base_dataset, num_permutations=10)` wrapping base dataset

#### Proposed Model: GNN-NFN (equivariant encoder)

**Architecture:** Graph Neural Network Neural Functional Network — equivariant to neuron permutations
**Source:** mkofinas/neural-graphs (GNN-NFN), https://github.com/mkofinas/neural-graphs
**Configuration (from H-M2):** hidden_dim=64, num_layers=4
**Note:** Reuse H-M1/H-E1/H-M2 trained checkpoints at N=100, 250 — no re-training required if H-E1 results stored

**Loading Information** (for Phase 4):
- Method: H-E1 results loader (`results_loader.py` from H-M2)
- Code: `load_he1_results(zoo='cifar10', encoder='gnn_nfn', sizes=[100, 250, 500, 1000])`

**Core Mechanism Implementation (PermAug — the mechanism under test):**

```python
# PermAug: Permutation Augmentation for Flat-MLP
# Based on: Zhou et al. 2023 (NFN paper), Eq. 1
# Applied per-batch during training; NOT applied at test time

import torch
import numpy as np

def apply_random_permutation(weight_vector, layer_sizes):
    """
    Apply random neuron permutation to vectorized weights.
    Permutes hidden layer neurons (not input/output layers).
    
    Args:
        weight_vector: (D,) flattened weight+bias tensor
        layer_sizes: list of layer dims, e.g. [input, h1, h2, output]
    Returns:
        permuted_vector: (D,) same shape, neurons reordered
    """
    # Reconstruct weight matrices from flat vector
    # Apply random permutation P to hidden layer l:
    #   W_l -> P @ W_l  (permute rows)
    #   W_{l+1} -> W_{l+1} @ P^T  (permute cols to maintain equiv function)
    # Flatten back to vector
    
    # Build offset index for each layer
    offset = 0
    matrices = []
    for i in range(len(layer_sizes) - 1):
        in_dim, out_dim = layer_sizes[i], layer_sizes[i+1]
        W = weight_vector[offset:offset + out_dim * in_dim].reshape(out_dim, in_dim)
        b = weight_vector[offset + out_dim * in_dim:offset + out_dim * in_dim + out_dim]
        matrices.append((W, b))
        offset += out_dim * in_dim + out_dim
    
    # Permute hidden layers only (indices 0 to L-2)
    for l in range(len(matrices) - 1):
        perm = torch.randperm(layer_sizes[l+1])  # permute neurons of layer l+1
        W_l, b_l = matrices[l]
        W_next, b_next = matrices[l+1]
        matrices[l] = (W_l[perm, :], b_l[perm])          # permute output neurons
        matrices[l+1] = (W_next[:, perm], b_next)         # compensate input neurons
    
    # Flatten back
    return torch.cat([t for W, b in matrices for t in [W.flatten(), b]])


class PermAugDataset(torch.utils.data.Dataset):
    """Wraps base dataset; returns num_permutations+1 views per sample."""
    def __init__(self, base_dataset, layer_sizes, num_permutations=10):
        self.base = base_dataset
        self.layer_sizes = layer_sizes
        self.n_aug = num_permutations
    
    def __len__(self):
        return len(self.base) * (self.n_aug + 1)
    
    def __getitem__(self, idx):
        base_idx = idx // (self.n_aug + 1)
        aug_idx = idx % (self.n_aug + 1)
        x, y = self.base[base_idx]
        if aug_idx == 0:
            return x, y  # original
        return apply_random_permutation(x, self.layer_sizes), y
```

### Training Protocol

**Reusing from H-M2 / H-E1 (controlled comparison — only PermAug condition changes):**

**Optimizer:** Adam
- lr = 1e-3
- weight_decay = 1e-4
- **Source:** H-E1 optimal hyperparameters (confirmed working in H-M2)

**Batch Size:** 64
**Epochs:** 100
**Loss Function:** MSE (R² computed on test set after training)
**Seeds:** 1 fixed seed (PoC mode — single run per condition)
**Schedule:** None (fixed LR, consistent with H-E1/H-M2)

**Conditions to run:**
1. `flat_mlp` at N ∈ {100, 250} — **reuse H-E1 stored results** (valid, not affected by PermAug bug)
2. `flat_mlp_perm_aug` at N ∈ {100, 250} — **must re-train** (H-E1 version was broken)
3. `gnn_nfn` at N ∈ {100, 250} — **reuse H-E1/H-M2 stored results**

**Compute budget:** Only PermAug re-training at N=100 and N=250 on CIFAR-10. Each run: ~few minutes on GPU. Total: ~4 training runs.

### Evaluation

**Primary Metrics:**
- R² (coefficient of determination) on fixed held-out test set
- Bootstrap 95% CI: 1000-resample percentile method (reuse `bootstrap_ci()` from H-M2)

**Success Criteria:**
- **Primary (gate):** Strict ordering `flat_mlp R² < flat_mlp_perm_aug R² < gnn_nfn R²` with non-overlapping bootstrap 95% CIs at BOTH N=100 AND N=250
- **Secondary:** PermAug closes 50–80% of Flat-MLP-to-equivariant gap

**Gap metrics:**
- `gap_total = R²(gnn_nfn) - R²(flat_mlp)`
- `gap_perm_aug = R²(flat_mlp_perm_aug) - R²(flat_mlp)`
- `perm_aug_fraction = gap_perm_aug / gap_total`  (target: 0.50–0.80)

**Expected baseline performance (from H-M2 at N=250):**
- flat_mlp: R² = 0.449 (confirmed)
- gnn_nfn: R² = 0.767 (confirmed)
- flat_mlp_perm_aug: unknown (invalid in H-E1) — expected between 0.449 and 0.767

**Metrics Loading Information** (for Phase 4):
- Task Type: regression (R² on scalar accuracy prediction)
- Library: sklearn.metrics (`r2_score`) + custom bootstrap CI
- Code: `from sklearn.metrics import r2_score; r2 = r2_score(y_true, y_pred)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of R² values for flat_mlp, flat_mlp_perm_aug, gnn_nfn at N=100 and N=250, with bootstrap 95% CI error bars. Must show whether ordering is strict (non-overlapping CIs).

#### Additional Figures (LLM Autonomous)

1. **Ordering Plot:** R² vs. training size (N=100, 250, 500, 1000) for all 3 conditions, with CI bands. Shows where PermAug is intermediate and where ordering may collapse.

2. **Gap Fraction Plot:** Bar chart of `perm_aug_fraction` at N=100 and N=250. Horizontal bands at 50% and 80% for P2 criterion visualization.

3. **PermAug Verification Plot:** Loss curves for flat_mlp vs flat_mlp_perm_aug (training loss only) to confirm PermAug training differs from plain MLP — this is the mechanism activation check.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | PermAug wrapper applies real permutation to weight vectors before MLP forward pass | TRUE — implemented in `PermAugDataset` |
| Mechanism Isolatable | flat_mlp_perm_aug vs flat_mlp differ ONLY in augmentation; same architecture, same hyperparameters | TRUE |
| Baseline Measurable | flat_mlp (no aug) and gnn_nfn results loadable from H-E1/H-M2 stored results | TRUE |

### Architecture Compatibility Check

**H-M3 mechanism:** Permutation augmentation applied to vectorized weight inputs of a plain MLP.

**Required features:**
- Weight vectors representable as flat 1D tensors (CIFAR-10 CNN zoo models: yes, via ModelZooDataset vectorization)
- Layer structure known (needed to correctly permute row/col pairs): available from `index_dict.json` in ModelZooDataset

**Incompatible architectures:**
- DWSNets: excluded (CNN zoo incompatibility, confirmed in H-M2)
- Any encoder that requires non-vectorized weight representation for PermAug computation

**CRITICAL PRE-CHECK (Phase 4 must implement):**
```python
# Verify PermAug is actually different from plain MLP
def verify_perm_aug_activated(x_batch, layer_sizes):
    x_aug = apply_random_permutation(x_batch[0], layer_sizes)
    diff = (x_aug - x_batch[0]).abs().max().item()
    assert diff > 1e-6, "PermAug produced no change — check layer_sizes!"
    print(f"[H-M3 MECHANISM CHECK] PermAug diff = {diff:.4e} > 1e-6 ✓")
    return diff
```

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `[H-M3 MECHANISM CHECK] PermAug diff = X > 1e-6 ✓` | Training loop init |
| Tensor Difference | `(x_aug - x_orig).abs().max() > 1e-6` for every augmented sample | `PermAugDataset.__getitem__` |
| Training Curve Difference | `flat_mlp_perm_aug` training loss should differ from `flat_mlp` at epoch > 1 | `run_experiment.py` |
| R² Difference | `R²(perm_aug)` at N=250 ≠ 0.449 (H-E1 broken value) | `evaluate.py` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_perm_aug_mechanism(train_loader_perm, train_loader_plain, layer_sizes):
    """Verify PermAug actually changes weight tensors."""
    indicators = {}
    
    # Check 1: Augmented batch differs from plain batch
    x_plain, y_plain = next(iter(train_loader_plain))
    x_perm, y_perm = next(iter(train_loader_perm))
    # (same underlying data, different augmentation)
    aug_diff = (x_perm - x_plain).abs().max().item()
    indicators["perm_differs_from_plain"] = aug_diff > 1e-6
    
    # Check 2: Dataset sizes differ (perm aug has 11x samples)
    indicators["dataset_size_correct"] = len(train_loader_perm.dataset) == \
        len(train_loader_plain.dataset) * 11  # 10 perms + 1 original
    
    # Check 3: Both conditions reach different R² at N=250
    # (filled after training — assert perm_aug R² != flat_mlp R²)
    
    print(f"[H-M3] Mechanism checks: {indicators}")
    all_pass = all(indicators.values())
    if not all_pass:
        raise RuntimeError(f"H-M3 mechanism verification FAILED: {indicators}")
    return all_pass, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| PermAug identical to plain MLP | `aug_diff < 1e-6` | FAIL: Bug in `apply_random_permutation` — check layer_sizes |
| Dataset size not 11× | `len(perm_dataset) != 11 * len(plain_dataset)` | FAIL: PermAugDataset __len__ bug |
| R²(perm_aug) = R²(flat_mlp) at N=250 | Identical to H-E1 broken result (0.449) | FAIL: Seeds not differentiated — check augmentation actually applied |
| PermAug R² > GNN-NFN R² | Ordering violated on high side | Document: PermAug unexpectedly strong; implies data symmetry sufficient |
| PermAug R² < Flat-MLP R² | Ordering violated on low side | Document: Augmentation hurts; check for label noise or overfitting |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | `aug_diff > 1e-6` AND dataset 11× larger | Pre-training verification |
| Effect Measurable | R²(perm_aug) ≠ R²(flat_mlp) at N=250 | Post-training comparison |
| Hypothesis Supported | Strict ordering: flat_mlp < perm_aug < gnn_nfn, non-overlapping 95% CIs at N=100 AND N=250 | Bootstrap CI comparison |
| Effect Size | perm_aug_fraction ∈ [0.50, 0.80] | Gap analysis |

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `R²(flat_mlp_perm_aug) > R²(flat_mlp)` AND `R²(flat_mlp_perm_aug) < R²(gnn_nfn)` at N ≤ 250 with non-overlapping 95% CIs on CIFAR-10

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Finding:** Archon KB does not contain relevant weight-space encoder literature. All research grounded in Exa/GitHub sources.

### B. GitHub Implementations (Exa)

**Repository 1:** AllanYangZhou/nfn (⭐ NFN official implementation)
- **URL:** https://github.com/AllanYangZhou/nfn
- **Query Used:** "NFN neural functional networks permutation augmentation MLP baseline"
- **Relevance:** Official implementation of MLPAug baseline directly comparable to our PermAug condition; the NFN paper is the primary source for augmentation protocol
- **Key Code (from paper Eq. 1 and MLPAug description):**
  ```python
  # MLPAug: augment training with random permutations
  # For weight tensor W with hidden layer of size h:
  perm = torch.randperm(h)
  W_l_permuted = W_l[perm, :]        # permute output neurons of layer l
  W_lp1_permuted = W_lp1[:, perm]   # compensate input neurons of layer l+1
  ```
- **Results used:** Table 3 — MLP=16.9%, MLPAug=18.9%, NFN-NP=46.6% on CIFAR-10 INR (confirms intermediate ordering)
- **Used For:** PermAug implementation design; confirms intermediate-position hypothesis has prior empirical support

**Repository 2:** ModelZoos/ModelZooDataset
- **URL:** https://github.com/modelzoos/modelzoodataset
- **Query Used:** "flat MLP permutation augmentation weight space property prediction ModelZooDataset"
- **Relevance:** Primary dataset source; provides `dataset_base.py` PyTorch loader
- **Key Code:**
  ```python
  from checkpoints_to_datasets.dataset_base import WeightDataset
  train_ds = WeightDataset(zoo_path, split='train')
  # Returns (weight_vector, label) pairs
  ```
- **Used For:** Dataset loading specification

**Repository 3:** Shamsian et al. 2024 (ar5iv/arXiv:2402.04081)
- **URL:** https://ar5iv.labs.arxiv.org/html/2402.04081
- **Query Used:** "DWSNets GNN-NFN equivariant weight space encoder sample efficiency learning curve"
- **Relevance:** Directly studies data augmentations for weight spaces including random permutation augmentation
- **Key Insight:** "Randomized weight space MixUp" = random permutation applied to second weight in interpolation. Simple permutation augmentation (our PermAug) is a degenerate case. Paper shows MixUp+perm ≈ MixUp (similar); both >> no augmentation.
- **Table result (ModelNet40):** MixUp DWS=74.36%, MixUp+random perm DWS=73.89% (perm adds ~nothing to MixUp); plain perm would be strictly less than MixUp variants
- **Used For:** Confirms PermAug intermediate position is plausible but not guaranteed to be large effect

**Repository 4:** NFN paper NeurIPS 2023 (proceedings)
- **URL:** https://proceedings.neurips.cc/paper_files/paper/2023/file/4e9d8aeeab6120c3c83ccf95d4c211d3-Paper-Conference.pdf
- **Relevance:** Primary citation for MLPAug baseline on INR classification tasks (not ModelZooDataset property prediction — our setting differs)
- **Key finding:** Even with PermAug (MLPAug), equivariant architectures consistently outperform (CIFAR-10 INR: 18.9% vs 46.6%). This directly motivates H-M3's expected ordering.
- **Used For:** Prior evidence that strict ordering (MLP < MLPAug < equivariant) exists in related tasks

### C. Code Analysis (Serena)

Serena analysis not performed — code from search results (NFN repo, ModelZooDataset) was sufficiently clear for this mechanism.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-M2 (`docs/youra_research/h-m2/04_validation.md`)
- **Reused components:**
  - GNN-NFN results at N=100, 250, 500, 1000 on CIFAR-10 (valid — no re-training)
  - flat_mlp results at N=100, 250, 500, 1000 on CIFAR-10 (valid — load from H-E1 results)
  - `analysis.py` (`bootstrap_ci`, `check_gate`), `results_loader.py`, `visualize.py`
  - Hyperparameters: Adam lr=1e-3, wd=1e-4, batch=64, epochs=100
- **NOT reused:** flat_mlp_perm_aug results from H-E1 (broken — identical to flat_mlp)
- **Why:** Enables controlled experiment where ONLY the PermAug condition changes

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (CIFAR-10 CNN zoo) | Previous (H-M2) | H-M2 validation report; H-E1 data available locally |
| PermAug implementation design | GitHub | NFN paper (AllanYangZhou/nfn), Eq. 1 |
| num_permutations=10 | Research | H-M3 verification protocol; maximizes augmentation per H-M3 risk R3 mitigation |
| GNN-NFN results | Previous (H-M2) | results/learning_curve_results.json |
| flat_mlp results | Previous (H-E1) | H-E1 results.json (via results_loader.py) |
| Optimizer / LR / epochs | Previous (H-M2) | Optimal hyperparameters from H-M2 handoff |
| Bootstrap CI | Previous (H-M2) | `analysis.py:bootstrap_ci()` |
| Prior evidence for intermediate ordering | GitHub / Paper | NFN Table 3 (Zhou 2023 NeurIPS); Shamsian 2024 augmentation results |
| Strict ordering success criterion | Phase 2B | `02b_verification_plan.md` H-M3 verification protocol step 3 |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restate block at end of document)
**Date:** 2026-08-21

### Workflow History for This Hypothesis

- 2026-08-21: Phase 2C experiment design IN_PROGRESS → COMPLETED
- Prerequisites: H-M2 VALIDATED (6.804× efficiency ratio on CIFAR-10)
- Critical finding: H-E1 PermAug results invalid; H-M3 must re-run with corrected augmentation

---

*MCP Tools Used: Exa (GitHub/papers), Archon (no relevant results — domain mismatch)*
*All specifications grounded in NFN paper (Zhou 2023), Shamsian 2024, and H-M2 validation report*
*Next Phase: Phase 3 - Implementation Planning*
