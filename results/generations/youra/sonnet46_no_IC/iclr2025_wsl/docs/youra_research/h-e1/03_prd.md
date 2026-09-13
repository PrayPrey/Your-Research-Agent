# Product Requirements Document: H-E1 — EquiSSL Distribution Shift PoC

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Gate:** MUST_WORK — MMD(SANE train→ViT) / MMD(EquiSSL train→ViT) ≥ 2.0
**Phase 2C Source:** `docs/youra_research/h-e1/02c_experiment_brief.md`
**Date:** 2026-08-05
**Tier:** LIGHT (max 15 tasks, 4-8 epics)

---

## 1. Executive Summary

This PoC validates that a scale+permutation equivariant graph encoder (EquiSSL, based on ScaleGMN) trained on SANE MultiZoo (MLP+CNN) produces a latent space with substantially reduced distribution shift when applied to the ViT Model Zoo (250 models, zero ViT training data), compared to the SANE flat-tokenizer baseline. Success is defined as MMD ratio ≥ 2.0, which gates continuation to H-M1.

---

## 2. Problem Statement

SANE (Sequential Autoencoder for Neural Embeddings) uses a flat chunk tokenizer that cannot generalize across architectures — it maps weights to tokens using fixed positional encoding, causing high distribution shift when ViT checkpoints (different weight tensor shapes) are encoded alongside MLP/CNN training data. The hypothesis is that a computational graph representation (node=neuron, edge=weight matrix) is architecture-agnostic, eliminating the representational mismatch and measurably reducing MMD between train and test distributions.

---

## 3. Goals and Non-Goals

**Goals:**
- Train EquiSSL encoder on SANE MultiZoo (MLP+CNN, ~30k models) using contrastive autoencoder objective
- Train SANE baseline on same data
- Compute MMD(train→ViT) for both encoders using RBF kernel (σ = median heuristic)
- Achieve MMD ratio ≥ 2.0

**Non-Goals:**
- Property prediction R² evaluation (H-M1, H-M2)
- ViT fine-tuning or supervision
- Comparison beyond SANE baseline (full ablation in H-M1)
- Hyperparameter search beyond λ sweep {0.01, 0.1, 1.0, 10.0}

---

## 4. Data Specification

### 4.1 Training Dataset: SANE MultiZoo (MLP+CNN)

| Field | Value |
|-------|-------|
| Name | SANE MultiZoo |
| Version | MultiZoo-SANE (arXiv 2504.10141, ICLR 2025 Workshop) |
| Source | `github.com/HSG-AIML/MultiZoo-SANE` |
| Size | ~30,000 MLP+CNN model checkpoints |
| Architecture types | MLP, CNN (no ViT — strict isolation) |
| Download method | `git clone https://github.com/HSG-AIML/MultiZoo-SANE && python data/download.py` |
| Preprocessing | Extract computational graph per checkpoint: node features = bias vectors, edge features = weight matrices; for SANE: use SANE chunk tokenizer |
| Split | 90% SSL pre-training / 10% reconstruction validation (no ViT data anywhere) |

### 4.2 Test Dataset: ViT Model Zoo (held-out, zero training)

| Field | Value |
|-------|-------|
| Name | ViT Model Zoo |
| Version | arXiv 2504.10231 (ICLR 2025 Workshop) |
| Source | `github.com/ModelZoos/ViTModelZoo` via ModelZooDownloader |
| Size | 250 unique ViT models with accuracy labels |
| Download method | `git clone https://github.com/ModelZoos/ModelZooDownloader && python download.py --zoo vit` |
| Usage | Inference-only (no ViT training data used) |
| Labels | Accuracy labels available (used only for secondary property prediction check) |

### 4.3 Preprocessing

**EquiSSL path (graph construction per checkpoint):**
```python
# node_features: bias vectors (shape: [n_neurons, 1])
# edge_features: weight matrices (shape: [n_edges, in_dim, out_dim] → flatten to [n_edges, d])
# Computational graph: directed (layer_i → layer_{i+1})
```

**SANE path:** Use standard SANE chunk tokenizer (512 weights per token, per HSG-AIML/SANE).

---

## 5. Functional Requirements

### FR-1: Data Pipeline
- **FR-1.1:** Download and cache SANE MultiZoo (MLP+CNN) via HSG-AIML/MultiZoo-SANE scripts
- **FR-1.2:** Download and cache ViT Model Zoo (250 models) via ModelZooDownloader
- **FR-1.3:** Implement `MultiZooGraphDataset`: convert MLP/CNN checkpoints to PyG `Data` objects (graph representation)
- **FR-1.4:** Implement `ViTZooGraphDataset`: same graph schema for ViT checkpoints (ensuring cross-architecture compatibility)
- **FR-1.5:** Implement scale+permutation augmentation for positive pairs: `scale_aug(α_i)` and `perm_aug(π)`

### FR-2: EquiSSL Model
- **FR-2.1:** Implement `EquiSSLEncoder` wrapping ScaleGMN (jkalogero/scalegmn, `--scalegmn_args.symmetry=monomial`)
- **FR-2.2:** Implement `GraphDecoder` (inverse of encoder, from odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders pattern)
- **FR-2.3:** Implement `EquiSSLObjective`: NT-Xent loss (τ=0.07) + λ × MSE reconstruction loss
- **FR-2.4:** λ sweep: train 4 models with λ ∈ {0.01, 0.1, 1.0, 10.0}; select best by validation reconstruction loss

### FR-3: SANE Baseline
- **FR-3.1:** Train SANE baseline on same MultiZoo data using HSG-AIML/SANE codebase
- **FR-3.2:** Same Adam optimizer, 100 epochs, 5 seeds
- **FR-3.3:** Extract SANE latent z for all MultiZoo training models and all ViT test models

### FR-4: Training Protocol
- **FR-4.1:** Optimizer: Adam (lr=1e-3, weight_decay=1e-4, betas=(0.9, 0.999))
- **FR-4.2:** Scheduler: CosineAnnealingLR (T_max=100, eta_min=1e-5)
- **FR-4.3:** Batch size: 64 model graphs
- **FR-4.4:** 100 epochs SSL pre-training
- **FR-4.5:** 5 random seeds (same seeds for SANE and EquiSSL)
- **FR-4.6:** Save best checkpoint per seed (lowest validation reconstruction loss)

### FR-5: Evaluation — MMD Ratio (Primary Gate Metric)
- **FR-5.1:** Encode all training models (MLP+CNN) and ViT test models with best EquiSSL checkpoint
- **FR-5.2:** Encode same models with SANE baseline
- **FR-5.3:** Compute `MMD(sane_train_z, vit_z)` using RBF kernel (σ = median heuristic, n_kernels=5)
- **FR-5.4:** Compute `MMD(equi_train_z, vit_z)` with same kernel parameters
- **FR-5.5:** Compute ratio = `MMD_SANE / MMD_EquiSSL`; report per seed and mean±std over 5 seeds
- **FR-5.6:** Gate check: ratio ≥ 2.0 → PASS; ratio < 1.5 → STOP pipeline

### FR-6: Evaluation — Secondary Metrics
- **FR-6.1:** t-SNE (2D) of train_z and vit_z for both encoders; save to `figures/tsne_comparison.png`
- **FR-6.2:** Distribution overlap histogram (L2 distance from ViT test points to nearest training point)
- **FR-6.3:** Training curves: NT-Xent and reconstruction loss per epoch for λ sweep
- **FR-6.4:** Bar chart: MMD(SANE) vs MMD(EquiSSL) with ratio annotation; save to `figures/mmd_comparison.png`

### FR-7: Results Reporting
- **FR-7.1:** Save all figures to `docs/youra_research/h-e1/figures/`
- **FR-7.2:** Save numerical results to `docs/youra_research/h-e1/results.json` (MMD values, ratio per seed, mean±std)
- **FR-7.3:** Save validation report to `docs/youra_research/h-e1/04_validation.md`

---

## 6. Non-Functional Requirements

| Requirement | Specification |
|-------------|---------------|
| GPU memory | ≤ 24 GB VRAM (fits single A100/RTX 3090) |
| Reproducibility | Fixed seeds; deterministic DataLoader; logged hyperparameters |
| Code quality | Modular; separate data/model/training/evaluation modules |
| Checkpoint | Save model weights after each epoch; resume-capable |
| Logging | Console + CSV log per run; WandB optional |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
torch_geometric>=2.3.0
numpy>=1.24.0
scikit-learn>=1.2.0
matplotlib>=3.7.0
seaborn>=0.12.0
pyyaml>=6.0
tqdm>=4.65.0
```

### 7.2 External Repositories (Manual Setup)

| Repository | Purpose | URL |
|------------|---------|-----|
| jkalogero/scalegmn | EquiSSL encoder backbone | https://github.com/jkalogero/scalegmn |
| odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders | Graph decoder pattern | https://github.com/odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders |
| HSG-AIML/MultiZoo-SANE | Training dataset + SANE baseline | https://github.com/HSG-AIML/MultiZoo-SANE |
| HSG-AIML/SANE | SANE model code | https://github.com/HSG-AIML/SANE |
| ModelZoos/ModelZooDownloader | ViT zoo download | https://github.com/ModelZoos/ModelZooDownloader |
| yiftachbeer/mmd_loss_pytorch | MMD computation | https://github.com/yiftachbeer/mmd_loss_pytorch |

---

## 8. Success Criteria

| Criterion | Threshold | Gate Type |
|-----------|-----------|-----------|
| MMD ratio (mean over 5 seeds) | ≥ 2.0 | MUST_WORK |
| Code runs without error | All 5 seeds complete | MUST_WORK |
| MMD ratio minimum | ≥ 1.5 (stop if below) | MUST_WORK |

**PoC Pass Condition:**
1. Code executes without error on all 5 seeds
2. `mean(mmd_ratio) ≥ 2.0` where `mmd_ratio = MMD_SANE / MMD_EquiSSL`

---

## 9. Out of Scope

- Property prediction R² (H-M1)
- EquiSSL-perm ablation (H-M1)
- Full ViT generalization evaluation (H-M4)
- Model interpolation (H-M3)
- Publication-quality figures (Phase 6)
