# PRD: H-E1 — Sharpness Anisotropy in SSL Loss Landscapes

**Hypothesis:** H-E1 (EXISTENCE)
**Phase:** 3 — Implementation Planning
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Tier:** LIGHT (≤15 tasks)
**Gate:** MUST_WORK

---

## 1. Executive Summary

This PoC experiment tests whether SSL-pretrained ResNet-50 models (SimCLR, MoCo-v2, DINO) trained with SGD on spurious correlation benchmarks exhibit statistically significant sharpness anisotropy in their loss landscape: specifically, that SAM perturbation loss increases more along spurious feature directions (identified via linear probe loss variance proxy) than along random directions (ratio > 1.2), and that this anisotropy ratio correlates negatively with worst-group accuracy across training checkpoints (Pearson r < -0.5, p < 0.05).

---

## 2. Problem Statement

Standard SSL pre-training uses SGD without any awareness of spurious correlations. The hypothesis is that the resulting loss landscape has directional sharpness bias — sharper along spurious feature directions — which can be detected using the SAM perturbation mechanism post-hoc. This existence check (H-E1) is the prerequisite for the entire hypothesis chain (H-E1 → H-M1 → H-M2 → H-M3 → H-M4).

**Novel contribution:** No prior work combines SAM perturbation analysis with SSL spurious correlation benchmarks for loss landscape characterization.

---

## 3. Scope

- **In scope:** SSL pre-training with SGD; post-hoc anisotropy measurement; linear probe proxy; WGA evaluation
- **Out of scope:** SAM as a training optimizer for SSL (that is H-M1+); group-label-based training; non-ResNet backbones
- **PoC scale:** 9 model-dataset combinations (3 SSL × 3 datasets), single seed

---

## 4. Data Specification

### 4.1 Primary Dataset: Waterbirds

- **Source:** Caltech-UCSD Birds-200-2011 (CUB) + Places365 backgrounds
- **Download:** MANUAL — `https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz`
- **Identifier:** `waterbird_complete95_forest2water2`
- **Target path:** `./data/waterbirds/`
- **Spurious correlation:** Bird type × Background, strength=0.95
- **Groups (4):** waterbird-water (3498), waterbird-land (184), landbird-water (56), landbird-land (1057)
- **Splits:** Standard train/val/test from kohpangwei/group_DRO (balanced val/test)
- **Preprocessing:**
  - Train: `RandomResizedCrop(224, scale=(0.2,1.0))`, `RandomHorizontalFlip`, `ColorJitter(0.4,0.4,0.4,0.1)`, `RandomGrayscale(p=0.2)`, `GaussianBlur`, ImageNet normalization
  - Eval: `Resize(256)`, `CenterCrop(224)`, ImageNet normalization
  - Normalization: `mean=[0.485,0.456,0.406]`, `std=[0.229,0.224,0.225]`
- **Loading:** `wilds.get_dataset(dataset='waterbirds', root_dir='./data')` OR kohpangwei/group_DRO loader

### 4.2 Secondary Dataset: CelebA

- **Source:** Liu et al. 2015 — celebrity faces
- **Download:** WILDS (auto-download) or Kaggle `jessicali9530/celeba-dataset`
- **Target path:** `./data/celeba/`
- **Spurious correlation:** Hair color (blond) × Gender (male/female)
- **Groups (4):** blond-female (22880), blond-male (1387), non-blond-female (71629), non-blond-male (66874)
- **Preprocessing:** Same as Waterbirds
- **Loading:** `wilds.get_dataset(dataset='celebA', root_dir='./data')`

### 4.3 Secondary Dataset: CMNIST

- **Source:** Arjovsky et al. 2019 — MNIST digits + programmatic color augmentation
- **Download:** AUTO via `torchvision.datasets.MNIST` (no manual download needed)
- **Spurious correlation:** Digit color ↔ binary label, correlation_strength=0.99
- **Groups (4):** label0-color0, label0-color1, label1-color0, label1-color1
- **Loading:** `torchvision.datasets.MNIST` + color augmentation wrapper

---

## 5. Functional Requirements

### FR-1: SSL Pre-training Pipeline

**SimCLR pre-training on all 3 datasets (ResNet-50 backbone):**
- Loss: NT-Xent (temperature τ=0.5), projection head 2048→128
- Optimizer: SGD, lr=0.03, momentum=0.9, weight_decay=1e-4, cosine annealing
- Batch size: 256, epochs: 200
- Augmentation: RandomResizedCrop(224, scale=(0.2,1.0)), RandomHorizontalFlip, ColorJitter, RandomGrayscale, GaussianBlur
- Checkpoints at epochs: 50, 100, 150, 200
- Source: izmailovpavel/spurious_feature_learning

**MoCo-v2 pre-training on all 3 datasets:**
- Loss: InfoNCE (temperature τ=0.2, queue size K=65536, momentum m=0.999)
- Optimizer: SGD, lr=0.03, cosine annealing, same augmentation
- Batch size: 256, epochs: 200, checkpoints at 50/100/150/200
- Source: facebookresearch/moco

**DINO pre-training on all 3 datasets:**
- Loss: DINO self-distillation (teacher momentum 0.996→1.0, temperature schedule)
- Optimizer: AdamW with DINO schedule, epochs: 200, checkpoints at 50/100/150/200
- Source: facebookresearch/dino

### FR-2: Linear Probe Training

For each (SSL model, dataset, checkpoint) combination:
- Freeze backbone weights
- Train linear classifier: SGD, lr=0.01, momentum=0.9, weight_decay=0, epochs=100
- No group labels used in training
- Source: izmailovpavel/spurious_feature_learning protocol

### FR-3: Sharpness Anisotropy Measurement (Core Mechanism)

For each (SSL model, dataset, checkpoint):
1. Compute per-sample linear probe losses on training set
2. Identify spurious direction proxy: top-25% high-loss samples (Ghaznavi 2023 LFR)
3. Apply SAM perturbation (rho=0.05) along spurious direction → compute loss increase
4. Apply SAM perturbation along 100 random directions (same sample count) → compute mean loss increase
5. Compute anisotropy ratio: `spurious_increase / mean(random_increases)`
6. Source: davda54/sam `first_step()` mechanism

### FR-4: Worst-Group Accuracy Evaluation

For each (SSL model, dataset, checkpoint):
- Evaluate linear probe on test set with group labels
- Compute WGA: `min(avg_accuracy_per_group)`
- Source: kohpangwei/group_DRO `analysis_utils.py`

### FR-5: Statistical Analysis

- Pearson r between anisotropy ratios and WGA across 4 checkpoints per (SSL, dataset) combination
- p-value threshold: 0.05
- Library: `scipy.stats.pearsonr`

### FR-6: Visualization

- **Required:** Bar chart — anisotropy ratio per model-dataset combination with threshold line at 1.2
- **Required:** Scatter plot — anisotropy ratio vs. WGA per checkpoint with Pearson r annotation
- **Additional:** Line plot — anisotropy ratio trajectory over epochs (50/100/150/200)
- **Additional:** 3×3 heatmap — SSL methods × datasets, anisotropy ratio values, color-coded pass/fail
- **Output path:** `docs/youra_research/h-e1/figures/`

### FR-7: Ablation Variants

- **Checkpoint ablation:** 4 checkpoints (50/100/150/200) per model — 36 total measurements
- **Random direction baseline:** n=100 per measurement (statistical robustness)
- **Proxy threshold ablation:** top-25% (primary), top-10% / top-50% (secondary, if budget allows)

---

## 6. Non-Functional Requirements

- **Reproducibility:** Single seed (seed=1) for PoC; results logged to YAML
- **Runtime budget:** ≤48 hours on single GPU (A100/V100) for all 9 SSL training runs
- **Memory:** ResNet-50 + SSL heads fit in 16GB GPU RAM; MoCo-v2 queue requires ~1GB
- **Platform:** Python 3.9+, PyTorch ≥1.12, CUDA 11.x
- **Checkpoint storage:** ~4 checkpoints × 9 models × ~100MB = ~3.6GB

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=1.12.0
torchvision>=0.13.0
wilds>=2.0.0
scipy>=1.9.0
numpy>=1.23.0
matplotlib>=3.6.0
seaborn>=0.12.0
scikit-learn>=1.1.0
pyyaml>=6.0
tqdm>=4.64.0
Pillow>=9.0.0
```

### 7.2 External Repositories (Reference Only)

- `davda54/sam` — SAM/ASAM optimizer (60-line drop-in)
- `kohpangwei/group_DRO` — Dataset loaders, WGA evaluation (analysis_utils.py)
- `izmailovpavel/spurious_feature_learning` — SSL pretraining pipeline
- `facebookresearch/moco` — MoCo-v2 implementation
- `facebookresearch/dino` — DINO implementation

---

## 8. Success Criteria

**Gate Condition (MUST_WORK):**
- Anisotropy ratio > 1.2 in ≥7/9 model-dataset combinations
- |Pearson r| > 0.5 (p < 0.05) in ≥5/9 (SSL, dataset) combinations
- Code runs without error for all 9 SSL training runs + 9 anisotropy measurements

**PoC Pass = Existence Confirmed:**
- PASS → proceed to H-M1 (mechanism hypothesis)
- FAIL → route to Phase 0 (new hypothesis direction)

**Expected Baselines:**
- SimCLR WGA: Waterbirds 43.8%, CelebA 76.7%, CMNIST 81.7% (NeurIPS 2025 spectral reg)
- SGD ERM ResNet-50 WGA on Waterbirds: 72.6% (izmailovpavel/spurious_feature_learning)

---

## 9. Out of Scope

- Multi-seed runs (PoC uses single seed)
- Non-ResNet backbones
- SAM as SSL training optimizer (H-M1+)
- Group-label-based training interventions
- Methods beyond SimCLR, MoCo-v2, DINO

---

## Appendix: Phase 2C Completeness Verification

| Phase 2C Item | Status in PRD |
|---------------|---------------|
| Baseline models (SimCLR, MoCo-v2, DINO) | ✓ FR-1 |
| Static datasets (Waterbirds, CelebA, CMNIST) | ✓ Section 4 |
| Ablation variants (4 checkpoints, n=100 random) | ✓ FR-7 |
| Custom metrics (anisotropy ratio, Pearson r, WGA) | ✓ Section 8 + FR-5 |
| SAM perturbation mechanism | ✓ FR-3 |
| Linear probe proxy | ✓ FR-2 + FR-3 |
| Visualization requirements | ✓ FR-6 |
| Manual download datasets | ✓ Section 4.1 (Waterbirds) |
