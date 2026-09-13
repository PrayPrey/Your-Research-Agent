# Product Requirements Document: H-M1
# Graph Representation as Cross-Architecture Generalization Mechanism

**Hypothesis ID:** H-M1
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

H-M1 tests whether directed computational graph encoding (node=neuron, edge=weight) enables cross-architecture generalization in weight-space SSL, by comparing three encoders on out-of-distribution ViT Model Zoo property prediction:

- **SANE** (flat tokenizer, reused from H-E1)
- **EquiSSL** (graph + scale+permutation equivariance, reused from H-E1)
- **EquiSSL-perm** (graph + permutation-only equivariance, new training)

Gate condition: BOTH graph encoders (EquiSSL-perm AND EquiSSL) must achieve R² > SANE on ViT zoo, p < 0.05.

---

## 2. Problem Statement

SANE uses flat weight tokenization (fixed-size chunks), which is architecture-specific — it cannot generalize to novel architecture families (e.g., ViTs) unseen during training. The hypothesis asserts that computational graph encoding provides architecture-agnostic structure (node=neuron, edge=weight matrix) that eliminates this representational mismatch, enabling frozen encoders trained on MLP+CNN zoos to generalize to real ViT Model Zoos.

H-E1 confirmed that EquiSSL's latent space better separates architecture families (MMD ratio = 2.575 ± 0.070, p < 0.05). H-M1 now tests whether this translates to downstream property prediction R² on a real ViT zoo with 250 models.

---

## 3. Functional Requirements

### FR-1: EquiSSL-perm Training (New)
Train ScaleGMN encoder with `symmetry=permutation` flag (permutation-only equivariance, no scale component) using NT-Xent + λ·MSE objective on SANE MultiZoo.
- 5 seeds, 100 epochs each
- λ=0.1 (best from H-E1 EquiSSL validation)
- Adam lr=1e-3, CosineAnnealingLR T_max=100
- Batch size: 64 model graphs
- Augmentation: permutation-only (no scale augmentation)
- Output: 5 checkpoint files `equi_perm_seed{i}.pt`

### FR-2: ViT Model Zoo Loading
Download and load 250 real ViT model checkpoints from ModelZoos/ViTModelZoo with accuracy labels.
- Source: `github.com/ModelZoos/ModelZooDownloader`
- Size: 250 unique ViT models
- Labels: accuracy for property prediction
- Zero overlap with training data (strict held-out evaluation)

### FR-3: ViT Computational Graph Construction
Convert each ViT checkpoint to computational graph representation compatible with EquiSSL and EquiSSL-perm encoders.
- Multi-head attention layers → parameter subgraph per GMN paper (ICLR 2024)
- Q/K/V projections → linear layer subgraph with head membership node feature
- Feedforward layers → standard MLP subgraph (node=neuron, edge=weight)
- LayerNorm → node features (scale/bias per neuron)
- Same graph schema as training (node=neuron+bias, edge=weight_matrix)

### FR-4: SANE ViT Embedding Extraction (Reuse H-E1)
Load frozen SANE checkpoints from H-E1, extract embeddings for all 250 ViT models using flat chunk tokenization.
- Reuse: `docs/youra_research/h-e1/checkpoints/sane_seed{i}.pt` (5 seeds)
- Preprocessing: same chunk size=512 as training

### FR-5: EquiSSL ViT Embedding Extraction (Reuse H-E1)
Load frozen EquiSSL (ScaleGMN λ=0.1) checkpoints from H-E1, extract embeddings for all 250 ViT models via graph representation.
- Reuse: `docs/youra_research/h-e1/checkpoints/equi_seed{i}.pt` (5 seeds)
- Graph construction: FR-3 pipeline

### FR-6: EquiSSL-perm ViT Embedding Extraction
Load trained EquiSSL-perm checkpoints (FR-1), extract embeddings for all 250 ViT models via graph representation.
- Input: `docs/youra_research/h-m1/checkpoints/equi_perm_seed{i}.pt`
- Graph construction: FR-3 pipeline (same as EquiSSL)

### FR-7: Linear Probe Property Prediction (All 3 Models)
For each model × seed combination:
- Split 250 ViT models 80/20 (200 train / 50 test) using random_state=seed
- Fit RidgeCV(alphas=[0.1, 1.0, 10.0, 100.0]) on frozen embeddings
- Compute R² on test split
- Report: mean ± std over 5 seeds per model

### FR-8: Statistical Significance Testing
For each graph encoder vs SANE:
- Paired t-test over 5 seeds: `scipy.stats.ttest_rel(r2_graph_seeds, r2_sane_seeds)`
- Report: t-statistic, p-value for EquiSSL-perm vs SANE and EquiSSL vs SANE
- Gate: p < 0.05 for both comparisons (MUST_WORK)

### FR-9: Ablation Variants (All Required)
Three-way ablation comparing:
1. **SANE** — flat tokenizer (baseline, reused)
2. **EquiSSL-perm** — graph + permutation-only equivariance (ablation: no scale)
3. **EquiSSL** — graph + scale+permutation equivariance (full model, reused)

All three MUST appear in results table.

### FR-10: Figure Generation
Mandatory figures (saved to `docs/youra_research/h-m1/figures/`):
1. **Bar chart**: R²(SANE) vs R²(EquiSSL-perm) vs R²(EquiSSL) with error bars; threshold line at SANE R²; p-value annotations
2. **Ablation ladder**: grouped bar chart, three methods × ViT accuracy prediction R²
3. **t-SNE comparison**: 4-panel — SANE / EquiSSL-perm / EquiSSL latent spaces, colored by architecture family
4. **Paired seed scatter**: per-seed R² scatter (dots above diagonal = improvement)
5. **ViT accuracy distribution**: histogram of 250 ViT model accuracies

### FR-11: Results Report
Generate `docs/youra_research/h-m1/04_validation.md` with:
- R² table: mean ± std for all 3 models
- Statistical test results (t-stat, p-value)
- Gate evaluation (PASS / PARTIAL / FAIL)
- Figure references
- Conclusion on graph representation hypothesis

---

## 4. Data Specification

### 4.1 Training Dataset (Reuse H-E1)
| Property | Value |
|----------|-------|
| Name | SANE MultiZoo |
| Source | github.com/HSG-AIML/MultiZoo-SANE |
| Version | ICLR 2025 Workshop (arXiv 2504.10141) |
| Size | ~30,000 MLP+CNN model checkpoints |
| Download | Manual clone required (not auto-download) |
| Cache | `docs/youra_research/h-e1/code/` (H-E1 data pipeline) |
| Status | REUSE — fully validated in H-E1 |
| Preprocessing | Graph construction (node=neuron, edge=weight) for EquiSSL/perm; weight chunks for SANE |

### 4.2 Evaluation Dataset (New)
| Property | Value |
|----------|-------|
| Name | ViT Model Zoo |
| Source | github.com/ModelZoos/ModelZooDownloader |
| Version | arXiv 2504.10231 (ICLR 2025 Workshop) |
| Size | 250 unique ViT model checkpoints |
| Labels | Accuracy labels for property prediction |
| Download | Manual: `git clone && python download.py --zoo vit` |
| Splits | 80% train / 20% test per seed (5 seeds) |
| Zero overlap | STRICT — no ViT models in training data |

### 4.3 Reused Checkpoints (H-E1)
| Model | Path | Seeds |
|-------|------|-------|
| SANE | `docs/youra_research/h-e1/checkpoints/sane_seed{i}.pt` | 0-4 |
| EquiSSL | `docs/youra_research/h-e1/checkpoints/equi_seed{i}.pt` | 0-4 |

---

## 5. Evaluation Protocol

### 5.1 Primary Metric
- **Property Prediction R²** (coefficient of determination)
- Task: ridge regression linear probe on frozen encoder embeddings
- Test set: 50 ViT models (20% of 250), 5 seeds
- Report: mean ± std over 5 seeds

### 5.2 Statistical Test
- Paired t-test (scipy.stats.ttest_rel) over 5 seed R² values
- Null hypothesis: R²_graph = R²_SANE
- Alpha level: 0.05
- Report: t-statistic, p-value (one for each graph encoder vs SANE)

### 5.3 Gate Evaluation
| Outcome | Condition | Action |
|---------|-----------|--------|
| PASS | BOTH graph encoders p < 0.05 vs SANE | Continue pipeline |
| PARTIAL | Only one graph encoder p < 0.05 | Document, continue |
| FAIL | Neither graph encoder p < 0.05 | STOP pipeline |

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- All random operations seeded (seeds 0-4)
- Checkpoint paths documented in 04_validation.md
- Hyperparameters logged per seed

### NFR-2: Code Organization (FULL Tier)
- YAML + dataclass configuration
- Structured logging (WandB optional, CSV fallback)
- Unit tests for critical components (graph construction, linear probe)

### NFR-3: Experiment Scale
- Full ViT Model Zoo: 250 models (NOT subsets of 10-50)
- 5 seeds for statistical validity
- Full 80/20 train/test split (200/50 models)

### NFR-4: Reuse from H-E1
- SANE and EquiSSL checkpoints: load frozen, no retraining
- MultiZoo data pipeline: reuse validated code from H-E1
- Bug fixes from H-E1 MUST be applied (sklearn TSNE `max_iter`, MMD NaN bandwidth clamp)

### NFR-5: Compute Efficiency
- EquiSSL-perm: 5 × 100 epochs on MultiZoo (~30k models)
- Embedding extraction: 250 ViT models × 3 encoders × 5 seeds
- Linear probe: fast (sklearn RidgeCV)

---

## 7. Dependencies

### 7.1 Python Packages
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
wandb  # optional
matplotlib
seaborn
tqdm
```

### 7.2 External Repositories (Reference, Not Auto-Install)
| Repo | Purpose | URL |
|------|---------|-----|
| jkalogero/scalegmn | EquiSSL + EquiSSL-perm backbone | github.com/jkalogero/scalegmn |
| HSG-AIML/MultiZoo-SANE | Training data + SANE baseline | github.com/HSG-AIML/MultiZoo-SANE |
| HSG-AIML/SANE | SANE baseline model | github.com/HSG-AIML/SANE |
| ModelZoos/ModelZooDownloader | ViT Model Zoo download | github.com/ModelZoos/ModelZooDownloader |
| mkofinas/neural-graphs | EquiSSL-perm fallback backbone | github.com/mkofinas/neural-graphs |

### 7.3 H-E1 Artifacts (Required)
- `docs/youra_research/h-e1/checkpoints/` — SANE + EquiSSL trained models
- `docs/youra_research/h-e1/code/` — MultiZoo data pipeline

---

## 8. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| Code runs without error (all 3 models) | No exceptions | Required |
| R²(EquiSSL-perm, ViT zoo) > R²(SANE, ViT zoo) | p < 0.05 | Gate (MUST_WORK) |
| R²(EquiSSL, ViT zoo) > R²(SANE, ViT zoo) | p < 0.05 | Gate (MUST_WORK) |
| Effect size ≥ 0.05 R² units | At least one encoder | Secondary |
| All 5 figures generated | Save to figures/ | Required |
| 03_tasks.yaml within budget | ≤ 30 tasks (FULL) | Required |

---

## 9. Out of Scope

- Hyperparameter search for EquiSSL-perm (use λ=0.1 from H-E1)
- ViT-specific training of any encoder
- Architecture search or NAS
- Deployment or productionization
- Comparison beyond SANE, EquiSSL-perm, EquiSSL
