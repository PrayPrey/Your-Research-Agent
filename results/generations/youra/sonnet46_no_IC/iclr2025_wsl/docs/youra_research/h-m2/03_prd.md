# Product Requirements Document: H-M2
# Scale vs Permutation Equivariance Ablation in EquiSSL

**Hypothesis ID:** H-M2
**Type:** MECHANISM (PoC)
**Date:** 2026-08-05
**Author:** Anonymous
**Phase:** 3 Implementation Planning

---

## stepsCompleted
- [x] Step 1: Problem Statement
- [x] Step 2: Functional Requirements
- [x] Step 3: Data Specification
- [x] Step 4: Evaluation Protocol
- [x] Step 5: Dependencies
- [x] Step 6: Success Criteria
- [x] Step 7: Non-Functional Requirements

---

## 1. Executive Summary

H-M2 is an incremental ablation experiment extending H-M1. It formally quantifies whether scale+permutation equivariance (ScaleGMN monomial group, EquiSSL) provides statistically significant improvement over permutation-only equivariance (neural-graphs backbone, EquiSSL-perm) on ViT Model Zoo property prediction.

**Pre-observed result from H-M1 seed 0:** ΔR² = −0.0207 (EquiSSL = 0.2098, EquiSSL-perm = 0.2305). Gate is SHOULD_WORK — if ΔR² < 0.05, document as ablation finding and continue pipeline.

Key tasks:
1. Train EquiSSL-perm for seeds 1–4 (seed 0 checkpoint from H-M1)
2. Extract embeddings for both models across 5 seeds
3. Compute paired statistics (ΔR², 95% CI, paired t-test)
4. Visualize latent geometry (t-SNE/UMAP)
5. Compare MMD ratios (secondary metric)

---

## 2. Problem Statement

H-M1 confirmed that both graph encoders outperform SANE on ViT zoo property prediction. The remaining question is whether scale equivariance (ScaleGMN monomial group) provides additional benefit over permutation-only equivariance (neural-graphs) in the SSL cross-architecture setting.

Theoretical context: ViTs use LayerNorm which already normalizes activations, reducing the gauge freedom from scaling symmetries. Per arXiv:2510.08300, scale equivariance inductive bias has less data to exploit in LayerNorm architectures. H-M2 empirically tests this prediction.

Gate condition (SHOULD_WORK): ΔR²_mean ≥ 0.05. If fails: document as ablation finding ("permutation equivariance suffices for ViT transfer"), refine thesis claim, continue pipeline to H-M3.

---

## 3. Functional Requirements

### FR-1: EquiSSL-perm Training (Seeds 1–4)
Train ScaleGMN encoder with `symmetry='permutation'` flag for seeds 1, 2, 3, 4.
- Seed 0 checkpoint already exists: `h-m1/checkpoints/equi_perm_seed0.pt`
- Training dataset: SANE MultiZoo (~30k MLP+CNN models) — same as H-M1
- Optimizer: Adam (lr=1e-3, weight_decay=1e-4)
- Scheduler: CosineAnnealingLR(T_max=100, eta_min=1e-5)
- Batch size: 64 model graphs
- Epochs: 100
- Objective: NT-Xent (τ=0.07) + λ_rec·MSE (λ_rec=0.1)
- Augmentation: perm_augment=True, scale_augment=False (control condition)
- Output: `h-m2/checkpoints/equi_perm_seed{1,2,3,4}.pt`

### FR-2: EquiSSL Embedding Extraction (5 Seeds, Reuse H-E1)
Load frozen EquiSSL (scale+perm, ScaleGMN) checkpoints from H-E1, extract embeddings for all 53 ViT models.
- Checkpoints: `h-e1/checkpoints/equissl_best_seed{0..4}.pt`
- Graph construction: same schema as H-M1 (node_in_dim=4, edge_in_dim=4)
- No retraining required

### FR-3: EquiSSL-perm Embedding Extraction (5 Seeds)
Load EquiSSL-perm checkpoints (seed 0 from H-M1, seeds 1–4 from FR-1), extract embeddings for all 53 ViT models.
- Checkpoint seed 0: `h-m1/checkpoints/equi_perm_seed0.pt`
- Checkpoint seeds 1–4: `h-m2/checkpoints/equi_perm_seed{1..4}.pt`
- Graph construction: identical to FR-2

### FR-4: Linear Probe Evaluation (Both Models, 5 Seeds)
For each model × seed:
- Split 53 ViT models 80/20 (42 train / 11 test) using random_state=seed
- Fit RidgeCV(alphas=[0.1, 1.0, 10.0, 100.0]) on frozen embeddings
- Compute R² on test split
- Use same train/test indices per seed for both models (paired evaluation)
- Report: mean ± std over 5 seeds per model

### FR-5: ΔR² Statistical Analysis
Compute pairwise comparison statistics over 5 seeds:
- `delta_r2 = r2_equissl - r2_equissl_perm` per seed
- Mean ΔR², std, 95% CI: `[mean - 1.96·std/√5, mean + 1.96·std/√5]`
- One-sample t-test: `scipy.stats.ttest_1samp(delta_r2, popmean=0)`
- Directional test: p < 0.10 for ΔR² > 0
- Gate evaluation: ΔR²_mean ≥ 0.05 → PASS; else DOCUMENT

### FR-6: MMD Ratio Comparison (Secondary Metric)
For both encoders' ViT embeddings, compute MMD ratio:
- Split ViT models by accuracy (median threshold)
- MMD(z_high_acc, z_low_acc) for each encoder
- Compare: does scale equivariance improve separation of scale-varied subpopulations?
- Reuse `h-e1/code/evaluation/mmd.py` kernel implementation

### FR-7: Visualization (4 Required Figures)
Save all figures to `h-m2/figures/`:
1. **Gate Metrics Comparison**: Bar chart — EquiSSL R² vs EquiSSL-perm R² with error bars, horizontal line at SANE R² (baseline) and +0.05 gate threshold
2. **ΔR² Distribution Plot**: Per-seed ΔR² scatter + mean ± std; horizontal line at 0.05; annotate PASS/DOCUMENT
3. **t-SNE Latent Geometry (2×2 panel)**: EquiSSL vs EquiSSL-perm embeddings for ViT models, colored by (a) accuracy, (b) L2 norm (model scale)
4. **Ablation Ladder (H-M1+H-M2)**: Stacked bar — SANE → EquiSSL-perm → EquiSSL R² progression

### FR-8: Ablation Variants (All Required)
Both models MUST appear in results:
1. **EquiSSL** — scale+permutation equivariant (ScaleGMN backbone, reused from H-E1)
2. **EquiSSL-perm** — permutation-only (neural-graphs backbone, seed 0 from H-M1, seeds 1–4 new)

Reference baselines (from H-M1, displayed but not re-run):
- SANE R² = 0.0721 (reported constant)
- H-M1 seed 0 values: EquiSSL=0.2098, EquiSSL-perm=0.2305

### FR-9: Results Report
Generate `h-m2/04_validation.md` with:
- R² table: mean ± std for EquiSSL and EquiSSL-perm (5 seeds)
- ΔR² analysis: mean, std, 95% CI, p-value
- Gate evaluation (PASS / DOCUMENT) with interpretation
- Figure references
- Conclusion: scale vs permutation equivariance for ViT zoo transfer

---

## 4. Data Specification

### 4.1 Training Dataset (Reuse H-M1)
| Property | Value |
|----------|-------|
| Name | SANE MultiZoo |
| Source | github.com/HSG-AIML/MultiZoo-SANE |
| Size | ~30,000 MLP+CNN model checkpoints |
| Download | Reuse from H-M1 (already downloaded) |
| Status | REUSE — validated in H-E1/H-M1 |
| Note | Only needed to train EquiSSL-perm seeds 1–4 |

### 4.2 Evaluation Dataset (Reuse H-M1)
| Property | Value |
|----------|-------|
| Name | Real ViT Model Zoo |
| Source | github.com/ModelZoos/ModelZooDownloader |
| Size | 53 ViT-S/16 checkpoints (full real subset) |
| Labels | Accuracy on ImageNet subset (continuous, 0.3–0.8) |
| Download | Reuse from H-M1 (already downloaded) |
| Splits | 80% train / 20% test per seed (42/11 models) |
| Preprocessing | Graph construction: node_in_dim=4, edge_in_dim=4 (same as H-M1) |
| Note | 53 models is the full available real ViT-S/16 subset |

### 4.3 Reused Checkpoints
| Model | Path | Seeds | Status |
|-------|------|-------|--------|
| EquiSSL | `h-e1/checkpoints/equissl_best_seed{i}.pt` | 0–4 | Available |
| EquiSSL-perm | `h-m1/checkpoints/equi_perm_seed0.pt` | 0 | Available |
| EquiSSL-perm | `h-m2/checkpoints/equi_perm_seed{1..4}.pt` | 1–4 | To train (FR-1) |

---

## 5. Evaluation Protocol

### 5.1 Primary Metric
- **ΔR²** = R²(EquiSSL) − R²(EquiSSL-perm) on ViT zoo accuracy prediction
- Mean and std over 5 seeds
- 95% CI using normal approximation

### 5.2 Statistical Tests
- One-sample t-test: `ttest_1samp(delta_r2, popmean=0)` — is ΔR² significantly different from 0?
- Report: t-statistic, p-value
- Directional p < 0.10 (weak evidence threshold for SHOULD_WORK gate)

### 5.3 Gate Evaluation
| Outcome | Condition | Action |
|---------|-----------|--------|
| PASS | ΔR²_mean ≥ 0.05 | Confirm scale equivariance benefit |
| DOCUMENT | ΔR²_mean < 0.05 | Document: "scale equivariance not necessary in SSL setting with ViTs"; continue pipeline |

### 5.4 Secondary Metric
- MMD ratio comparison between EquiSSL and EquiSSL-perm embeddings

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- All random ops seeded (seeds 0–4)
- Paired evaluation: identical train/test splits per seed for both models

### NFR-2: Code Organization (FULL Tier, INCREMENTAL)
- Extends h-m1/code/ directly (no full rewrite)
- New script: `h-m2/run_hm2.py` calling existing utilities
- New training script for EquiSSL-perm seeds 1–4

### NFR-3: Experiment Scale
- Full ViT Model Zoo: 53 real models (NOT subsets of 10-50)
- 5 seeds for statistical validity
- Full 80/20 split (42/11 models)

### NFR-4: Reuse from H-M1
- All evaluation code: reuse `h-m1/code/evaluation/` directly
- Dataset loading: reuse `h-m1/code/data/vitzoo_graph_dataset.py`
- EquiSSL encoder: reuse `h-m1/code/models/equissl_encoder.py` with `symmetry='permutation'`
- Bug fixes from H-E1/H-M1 MUST be applied

### NFR-5: Pre-observed Result Handling
- Seed 0 results already known from H-M1 (EquiSSL=0.2098, EquiSSL-perm=0.2305)
- Reproduce seed 0 results as sanity check; train/evaluate seeds 1–4

---

## 7. Dependencies

### 7.1 Python Packages (Reuse H-M1 Environment)
```
torch>=2.0.1
torch-geometric>=2.3.0
pytorch-scatter
numpy
scikit-learn
scipy
einops
hydra-core
pyyaml
matplotlib
seaborn
tqdm
```

### 7.2 External Repositories (Reference)
| Repo | Purpose | URL |
|------|---------|-----|
| jkalogero/scalegmn | EquiSSL-perm backbone | github.com/jkalogero/scalegmn |
| mkofinas/neural-graphs | EquiSSL-perm alternative backbone | github.com/mkofinas/neural-graphs |

### 7.3 H-M1/H-E1 Artifacts (Required)
- `h-m1/code/` — all reusable modules (data, models, evaluation)
- `h-m1/checkpoints/equi_perm_seed0.pt` — EquiSSL-perm seed 0
- `h-e1/checkpoints/equissl_best_seed{i}.pt` — EquiSSL all 5 seeds

---

## 8. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| Code runs without error | No exceptions | Required |
| EquiSSL-perm seeds 1–4 trained | 4 checkpoint files | Required |
| R² reported for both models (5 seeds) | mean ± std | Required |
| ΔR² statistical test reported | t-stat, p-value | Required |
| 4 figures generated | Save to h-m2/figures/ | Required |
| Gate evaluated | PASS or DOCUMENT | Required (SHOULD_WORK) |
| 03_tasks.yaml within budget | ≤ 30 tasks (FULL) | Required |

---

## 9. Out of Scope

- Hyperparameter tuning for EquiSSL-perm (use H-M1 settings exactly)
- New model architectures beyond EquiSSL / EquiSSL-perm
- ViT-specific fine-tuning
- Extension to H-M3/H-M4 experiments
- Full 250-model ViT zoo (Phase 5 scope)
