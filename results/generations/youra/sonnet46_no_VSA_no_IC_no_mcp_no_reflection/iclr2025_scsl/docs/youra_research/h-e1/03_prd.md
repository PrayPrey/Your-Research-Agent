---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
hypothesis_id: h-e1
phase: 3
document_type: PRD
generated: 2026-08-31
---

# Product Requirements Document: H-E1
## Gradient Alignment Signal Existence Verification

**Hypothesis:** Under standard ERM training on Waterbirds and CelebA with random mini-batch sampling, per-sample last-layer gradient alignment ROC-AUC for predicting spurious-minority group membership exceeds per-sample loss ROC-AUC at ≥1 epoch on BOTH datasets.

**Type:** EXISTENCE (PoC) | **Gate:** MUST_WORK | **Tier:** LIGHT (≤15 tasks)

---

## 1. Executive Summary

H-E1 establishes whether gradient alignment cosine similarity is a stronger predictor of spurious-minority group membership than per-sample loss during standard ERM training. This is a measurement/diagnostic hypothesis: no new model architecture is proposed. The experiment runs standard ERM on ResNet-50 for Waterbirds and CelebA, injects per-sample gradient probes at checkpoint epochs using `torch.func.vmap`, and compares ROC-AUC of gradient alignment vs loss as binary predictors of spurious-minority membership (defined by group annotations).

**Pass condition:** alignment_roc_auc > loss_roc_auc at ≥1 checkpoint epoch on BOTH datasets.

---

## 2. Problem Statement

### 2.1 Research Gap
JTT (Liu et al. 2021) and LfF (Nam et al. 2020) use per-sample loss as proxy for identifying spurious-minority samples. No prior work directly compares gradient alignment (directional cosine similarity with batch mean gradient) against loss ROC-AUC as predictors of spurious-minority membership.

### 2.2 H-E1 Claim
The batch-mean gradient during ERM encodes the dominant spurious correlation direction. Spurious-minority samples — whose correct classification requires ignoring the spurious feature — will have lower cosine similarity to the batch mean than spurious-majority samples. This alignment signal should surpass loss ROC-AUC, especially in early training when spurious correlations are most actively learned.

### 2.3 Theoretical Support
- "Bias Leaves a Gradient Trail" (arxiv 2605.28780): gradient direction probes encode bias signal.
- Gradient-Weight Alignment (arxiv 2510.25480): per-sample cosine similarity with batch gradient quantifies alignment.
- JTT baseline: loss ROC-AUC ~0.6–0.75 for spurious-minority identification.

---

## 3. Functional Requirements

### FR-1: Dataset Loading (Waterbirds)
- Load Waterbirds dataset from `./data/waterbirds/` using kohpangwei/group_DRO `ConfounderDataset` class.
- Standard splits: Train=4,795, Val=1,199, Test=5,794.
- Group labels loaded from metadata CSV (for evaluation only; not used in training).
- Preprocessing: Resize(256) → CenterCrop(224) → ToTensor → ImageNet Normalize.
- Training augmentation: RandomHorizontalFlip.
- DataLoader: batch_size=32, shuffle=True (train), shuffle=False (eval).

### FR-2: Dataset Loading (CelebA)
- Load CelebA dataset from `./data/celeba/` using kohpangwei/group_DRO `CelebADataset`.
- Standard splits: Train=162,770, Val=19,867, Test=19,962.
- Task: Blond hair prediction. Spurious feature: gender.
- Group labels loaded from CelebA attribute metadata.
- Preprocessing: same as Waterbirds (Resize(256), CenterCrop(224), ImageNet normalize).
- Training augmentation: RandomHorizontalFlip.
- DataLoader: batch_size=32, shuffle=True (train), shuffle=False (eval).

### FR-3: ERM Training (Waterbirds)
- Model: ResNet-50 (torchvision, ImageNet pretrained).
- Last layer: Linear(2048, 2) (initialized by ResNet-50 default).
- Optimizer: SGD, lr=0.001, momentum=0.9, weight_decay=1e-4.
- Epochs: 300 (standard ERM per group_DRO).
- Loss: CrossEntropyLoss, no class reweighting, no group reweighting.
- Seed: 42.
- Checkpoint epochs for probe: {1, 5, 10, 25, 50}.

### FR-4: ERM Training (CelebA)
- Model: ResNet-50 (same as FR-3).
- Optimizer: SGD, lr=0.0001, momentum=0.9, weight_decay=1e-4.
- Epochs: 50 (standard ERM per group_DRO).
- Loss: CrossEntropyLoss, no reweighting.
- Seed: 42.
- Checkpoint epochs for probe: {1, 5, 10, 25, 50}.

### FR-5: Per-Sample Gradient Alignment Computation
- At each checkpoint epoch, compute per-sample last-layer gradients over the FULL training set.
- Method: `torch.func.vmap(grad(loss_fn))` where `loss_fn` computes cross-entropy on single sample.
- Scope: Last layer only (`model.fc` — Linear(2048, 2) weight + bias = 4,098 params per sample).
- Output: per-sample gradient vectors shape (N, 4098).
- Batch-mean gradient: mean over all per-sample gradients (1, 4098).
- Alignment score: cosine similarity of each per-sample gradient with batch mean.
- Predictor for ROC-AUC: **negative** cosine similarity (low alignment → likely spurious-minority → high predictor score).

### FR-6: Per-Sample Loss Computation
- At each checkpoint epoch, compute per-sample cross-entropy loss over FULL training set.
- Method: `F.cross_entropy(logits, labels, reduction='none')`.
- Predictor for ROC-AUC: raw loss value (high loss → likely spurious-minority per JTT hypothesis).

### FR-7: ROC-AUC Evaluation
- Binary label: spurious-minority membership (1 if group_id in {waterbird_on_land, landbird_on_water} for Waterbirds; blond_male for CelebA; else 0).
- Metric: `sklearn.metrics.roc_auc_score(spurious_minority_labels, predictor_scores)`.
- Compute alignment_roc_auc and loss_roc_auc at each checkpoint epoch.
- Store results in structured dict for logging and plotting.

### FR-8: Results Logging
- Save results to `h-e1/results/results.json` with schema:
  ```json
  {
    "dataset": "waterbirds",
    "epoch": 5,
    "alignment_roc_auc": 0.74,
    "loss_roc_auc": 0.68,
    "alignment_wins": true
  }
  ```
- One entry per (dataset, checkpoint_epoch) combination.

### FR-9: Visualization — ROC-AUC vs Epoch (MANDATORY)
- Line plot: alignment_roc_auc and loss_roc_auc vs checkpoint epoch {1,5,10,25,50}.
- 2×1 subplot (Waterbirds top, CelebA bottom).
- Save to `h-e1/figures/roc_auc_vs_epoch.png`.

### FR-10: Visualization — Score Distribution (Additional)
- Violin/box plot at epoch 5: alignment scores for spurious-minority vs spurious-majority groups.
- 2×1 subplot (Waterbirds, CelebA).
- Save to `h-e1/figures/score_distribution_epoch5.png`.

### FR-11: Visualization — ROC Curves (Additional)
- ROC curves (FPR vs TPR) at epoch where alignment_roc_auc is maximized, for both datasets.
- Save to `h-e1/figures/roc_curves_best_epoch.png`.

---

## 4. Data Specification

### 4.1 Waterbirds
| Property | Value |
|---|---|
| Source | kohpangwei/group_DRO generate_waterbirds.py |
| Download Type | Manual (script required) |
| Local Path | `./data/waterbirds/` |
| Train size | 4,795 |
| Val size | 1,199 |
| Test size | 5,794 |
| Groups | 4: (bird_type × background) |
| Spurious-minority | waterbird_on_land (56), landbird_on_water (184) |
| Group label source | metadata CSV |

### 4.2 CelebA
| Property | Value |
|---|---|
| Source | kohpangwei/group_DRO CelebA integration |
| Download Type | Manual (CelebA official + group_DRO integration) |
| Local Path | `./data/celeba/` |
| Train size | 162,770 |
| Val size | 19,867 |
| Test size | 19,962 |
| Groups | 4: (blond × gender) |
| Spurious-minority | blond_male (~1,387 train samples) |
| Group label source | CelebA attribute metadata |

---

## 5. Non-Functional Requirements

### NFR-1: Compute Efficiency
- Per-sample gradient computation is batch-wise (not sample-by-sample loop) using vmap.
- Memory: 32 samples × 4,098 floats × 4 bytes ≈ 512 KB — fits in 8GB GPU.
- CelebA full-train gradient pass: 162,770 samples / 32 batch = ~5,087 forward+grad passes per probe epoch.

### NFR-2: Reproducibility
- Fixed seed: `torch.manual_seed(42)`, `random.seed(42)`, `numpy.random.seed(42)`.
- Single run (PoC — no multiple seeds required).
- Results JSON saved for reproducibility.

### NFR-3: Code Organization
- Single experiment script: `h-e1/experiment.py`.
- Dataset loaders adapted from group_DRO (imported or copied minimally).
- Results in `h-e1/results/`, figures in `h-e1/figures/`.

---

## 6. Success Criteria

### Primary (Gate)
- alignment_roc_auc > loss_roc_auc at ≥1 checkpoint epoch on BOTH Waterbirds AND CelebA.
- Code runs without runtime error on both datasets.

### Secondary (Informational)
- max(alignment_roc_auc) > 0.6 on both datasets.
- Alignment advantage visible in early training epochs (consistent with spurious learning hypothesis).

### Failure Conditions
- alignment_roc_auc ≤ loss_roc_auc at ALL checkpoint epochs on ANY dataset → FAIL gate.
- RuntimeError or OOM during gradient computation → implementation bug, not hypothesis failure.

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0.0          # torch.func.vmap, grad (requires PyTorch 2.0+)
torchvision>=0.15.0   # ResNet-50 pretrained weights
scikit-learn>=1.0.0   # roc_auc_score
numpy>=1.21.0         # array operations
pandas>=1.3.0         # metadata CSV loading
Pillow>=8.0.0         # image loading
matplotlib>=3.5.0     # visualization
tqdm>=4.0.0           # progress bars
```

### 7.2 External Repositories
- kohpangwei/group_DRO: dataset loading classes (ConfounderDataset, CelebADataset).
  - Needed files: `data/confounder_utils.py`, `data/celebA_dataset.py`, `data/cub_dataset.py`.
  - Clone to: `./group_dro/` or copy relevant files to `h-e1/data/`.

### 7.3 Data Downloads (Manual)
1. **Waterbirds**: Run `python group_dro/dataset_scripts/generate_waterbirds.py` (requires CUB-200-2011 + Places365 downloads).
2. **CelebA**: Download from official source + integrate with group_DRO metadata CSVs.

---

## 8. Out of Scope

- No group reweighting (DRO, LfF, JTT) — pure ERM only.
- No hyperparameter search — fixed settings from group_DRO README.
- No multiple random seeds — single PoC run.
- No worst-group accuracy reporting — not the hypothesis metric.
- No architectural modification to ResNet-50.
