# Product Requirements Document: H-E1
# Checkpoint Linear Probe Battery — Existence (PoC) Hypothesis

---
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - non_functional_requirements
  - success_criteria
  - data_specification
  - dependencies
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
tier: LIGHT
generated_at: "2026-05-04"
source: "02c_experiment_brief.md (Phase 2C)"
---

## 1. Executive Summary

**Hypothesis (H-E1):** Under standard ERM training (ResNet-50, ImageNet pretrained) on Waterbirds and CelebA, if checkpoint linear probing is applied every 2 epochs, then `delta(t) = spurious_probe_acc(t) − core_probe_acc(t) > 0` for a statistically significant contiguous window covering ≥10% of training epochs, replicated across ≥3 random seeds and on CelebA, because SGD simplicity bias preferentially encodes lower-complexity (spurious) features before higher-complexity (core) features.

**Scope:** EXISTENCE proof-of-concept. The experiment instruments a standard ERM training loop to save checkpoints every 2 epochs, then applies a checkpoint linear probe battery at each checkpoint to measure spurious and core feature encoding over time. The "proposed model" is the measurement protocol itself — not a new architecture.

**Gate:** MUST_WORK — `delta(t) > 0` for a contiguous window ≥10% of training epochs (≥30 epochs out of 300 for Waterbirds) with paired t-test p < 0.05 across ≥3 seeds. Failure → STOP all downstream hypotheses (H-M1 through H-M4).

**Key References:**
- GroupDRO codebase (Sagawa et al. 2020): Training infrastructure, dataset loaders
- DFR codebase (Kirichenko et al. 2022): Linear probe methodology (L2 logistic regression, C=1.0)
- Simplicity Bias (Shah et al. 2020): Theoretical motivation for delta(t) > 0

---

## 2. Problem Statement

### Background
Spurious correlations in training data cause ERM models to rely on spurious features (e.g., Waterbirds background) rather than core features (bird species). The SGD simplicity bias hypothesis (Shah et al. 2020) predicts that spurious (lower-complexity) features are learned faster than core (higher-complexity) features. If this is measurable as a temporal gap in linear probe accuracy, it explains why post-hoc annotation-free methods (DFR, JTT) succeed when applied after sufficient training.

### Core Question (H-E1)
Can the temporal feature learning gap `delta(t) = spurious_probe_acc(t) − core_probe_acc(t)` be directly measured via checkpoint linear probing, and does it produce a positive contiguous window covering ≥10% of training?

### Why This Matters
If delta(t) > 0 is not observed, the temporal gap hypothesis is falsified and H-M1 through H-M4 cannot proceed. H-E1 is the mandatory empirical foundation for the entire verification chain.

---

## 3. Functional Requirements

### FR-1: ERM Training with Checkpoint Saving

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Train ResNet-50 (ImageNet pretrained) on Waterbirds for 300 epochs using SGD (lr=1e-3, momentum=0.9, weight_decay=1e-4, batch=128) | Must Have |
| FR-1.2 | Train ResNet-50 on CelebA for 50 epochs using SGD (lr=1e-3, momentum=0.9, weight_decay=1e-4, batch=128) | Must Have |
| FR-1.3 | Save model checkpoint (state_dict) every 2 epochs to disk: `checkpoints/seed_{seed}/epoch_{t:03d}.pt` | Must Have |
| FR-1.4 | Apply standard preprocessing: Resize 256×256, CenterCrop 224×224, ImageNet normalization (mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]) | Must Have |
| FR-1.5 | Apply training augmentation: RandomResizedCrop(224), RandomHorizontalFlip | Must Have |
| FR-1.6 | Use CrossEntropyLoss with standard ERM (no group-balancing, no reweighting) | Must Have |
| FR-1.7 | Run with ≥3 independent random seeds (seed=1,2,3 minimum; 5 recommended) | Must Have |
| FR-1.8 | LR schedule: constant (no decay) per GroupDRO standard ERM baseline | Must Have |

### FR-2: Feature Extraction at Each Checkpoint

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | For each checkpoint epoch t, load saved state_dict into ResNet-50 with FC replaced/detached | Must Have |
| FR-2.2 | Extract frozen backbone features from avgpool layer: shape (N_val, 2048) | Must Have |
| FR-2.3 | Use validation set (1,199 Waterbirds / 19,867 CelebA) for probe fitting and evaluation | Must Have |
| FR-2.4 | Set model.eval() and torch.no_grad() during feature extraction to ensure frozen backbone | Must Have |
| FR-2.5 | Feature extraction must NOT store all features simultaneously — load checkpoint, extract, fit probe, discard features | Must Have |

### FR-3: Checkpoint Linear Probe Battery

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | At each checkpoint t, fit two separate L2 logistic regression probes: spurious label probe and core label probe | Must Have |
| FR-3.2 | Probe implementation: `LogisticRegression(C=1.0, max_iter=1000, solver='lbfgs', random_state=42)` (per DFR paper) | Must Have |
| FR-3.3 | Waterbirds spurious label: `place` column (0=land, 1=water); core label: `y` column (0=landbird, 1=waterbird) | Must Have |
| FR-3.4 | CelebA spurious label: `Blond_Hair` attribute; core label: `Male` attribute (per GroupDRO convention) | Must Have |
| FR-3.5 | Compute `spurious_probe_acc(t)` = probe.score(val_feats, val_spurious_labels) | Must Have |
| FR-3.6 | Compute `core_probe_acc(t)` = probe.score(val_feats, val_core_labels) | Must Have |
| FR-3.7 | Compute `delta(t) = spurious_probe_acc(t) − core_probe_acc(t)` | Must Have |
| FR-3.8 | Store results per seed: `delta_curves[seed][t]`, `spurious_curves[seed][t]`, `core_curves[seed][t]` | Must Have |

### FR-4: Statistical Analysis

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Identify contiguous windows where delta(t) > 0 for each seed | Must Have |
| FR-4.2 | Find longest contiguous window per seed and compute as fraction of total training epochs | Must Have |
| FR-4.3 | Run paired t-test (scipy.stats.ttest_rel) across seeds on window duration; report p-value | Must Have |
| FR-4.4 | Compute gap area A = Σ max(delta(t), 0) per seed with 95% CI across seeds | Must Have |
| FR-4.5 | Identify transition epoch t* = first epoch where delta(t) < 0.02 for 3 consecutive checkpoints | Must Have |
| FR-4.6 | Report t* variance (std) across seeds — target std < 10 epochs | Should Have |
| FR-4.7 | Report directional replication on CelebA: delta(t) > 0 window exists | Must Have |

### FR-5: Gate Evaluation and Result Saving

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | Evaluate primary gate: max contiguous window ≥ 10% of epochs AND p < 0.05 across ≥3 seeds | Must Have |
| FR-5.2 | Print gate result: "H-E1 GATE: window={pct:.1f}% >= 10%, p={p:.4f} — PASS/FAIL" | Must Have |
| FR-5.3 | Save full results to `results/h-e1/h-e1_results.json` with all metrics | Must Have |
| FR-5.4 | PoC pass condition: code runs without error AND delta(t) > 0 for ≥10% window on 1 seed | Must Have |

### FR-6: Visualization

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-6.1 | Required figure: line plot of `spurious_probe_acc(t)`, `core_probe_acc(t)`, `delta(t)` vs epoch. Shaded region where delta(t) > 0. Vertical dashed line at t*. | Must Have |
| FR-6.2 | Seed consistency plot: overlay of delta(t) curves for all ≥3 seeds (showing reproducibility) | Should Have |
| FR-6.3 | Gap area bar chart: cumulative gap area A per seed with 95% CI error bars | Should Have |
| FR-6.4 | CelebA replication: side-by-side delta(t) curves for Waterbirds vs CelebA | Should Have |
| FR-6.5 | Save all figures to `h-e1/figures/` directory | Must Have |

---

## 4. Data Specification

### Dataset 1: Waterbirds (Primary)
- **Source:** kohpangwei/group_DRO (generate_waterbirds.py) or CUB-200-2011 + Places365
- **Type:** standard (real benchmark — NOT synthetic)
- **Download required:** Yes — manual via GroupDRO download script
- **Train split:** 4,795 samples (4 groups: landbird-land, landbird-water, waterbird-land, waterbird-water)
- **Val split:** 1,199 samples (used for ALL linear probing)
- **Test split:** 5,794 samples (WGA evaluation only)
- **Spurious label column:** `place` (0=land, 1=water) in metadata CSV
- **Core label column:** `y` (0=landbird, 1=waterbird) in metadata CSV
- **Spurious correlation:** ~95% in training set
- **Checkpoints:** 300/2 = 150 checkpoints per seed; storage ~150 × checkpoint_size

### Dataset 2: CelebA (Replication)
- **Source:** torchvision.datasets.CelebA (auto-download) or GroupDRO
- **Type:** standard (real benchmark — NOT synthetic)
- **Download required:** Yes — torchvision auto-download
- **Train split:** 162,770 samples
- **Val split:** 19,867 samples
- **Test split:** 19,962 samples
- **Spurious label:** `Blond_Hair` attribute index
- **Core label:** `Male` attribute index (non-blond male = worst group)
- **Epochs:** 50 (25 checkpoints per seed)

### Model Weights
- **ResNet-50:** `torchvision.models.resnet50(pretrained=True)` — auto-downloads from torchvision hub (~100MB)

### Loading Code
```python
# Waterbirds — GroupDRO loader
from data.waterbirds_dataset import WaterbirdsDataset
train_data = WaterbirdsDataset(data_dir='./data/waterbirds', split='train')
val_data = WaterbirdsDataset(data_dir='./data/waterbirds', split='val')

# CelebA — torchvision
from torchvision.datasets import CelebA
celeba_val = CelebA(root='./data', split='valid', download=True,
                    target_type='attr', transform=val_transform)

# ResNet-50
import torchvision.models as models
model = models.resnet50(pretrained=True)
model.fc = torch.nn.Linear(2048, 2)
```

---

## 5. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | Single GPU execution (`CUDA_VISIBLE_DEVICES=<single_gpu>`) |
| NFR-2 | Estimated runtime: ~6-8h for 3 seeds × (300-epoch Waterbirds + 50-epoch CelebA) + probe battery |
| NFR-3 | Memory-efficient: Load checkpoint → extract features → fit probe → discard (no bulk feature storage) |
| NFR-4 | Reproducibility: Set random seed for torch, numpy, python random before each training run |
| NFR-5 | All results and figures saved to disk before pipeline continuation |
| NFR-6 | Code must not use group labels during training (labels only used in post-hoc probe evaluation) |
| NFR-7 | Checkpoint disk usage: ~150 × ~100MB (ResNet-50) ≈ 15GB per seed — use tmp/delete after probe evaluation |

---

## 6. Success Criteria

### Primary Gate (MUST_WORK)
- `delta(t) > 0` for a contiguous window covering ≥10% of training epochs (≥30 epochs of 300 for Waterbirds)
- Paired t-test p < 0.05 across ≥3 random seeds
- Direction: `spurious_probe_acc(t) > core_probe_acc(t)` in early training

### PoC Pass Condition (Single-Seed Fast Check)
1. Code runs without error end-to-end
2. `delta(t) > 0` for any contiguous window ≥10% of training epochs on Waterbirds (1 seed sufficient for PoC)

### Secondary Confirmation
- Directional replication on CelebA: delta(t) > 0 window exists (exact threshold relaxed for replication)

### Mechanism Activation Checks (All must pass)
1. Checkpoint files exist at expected epochs (every 2 epochs, 0–300)
2. Feature extraction shape: `(N_val, 2048)` at each checkpoint
3. Both probes converge (LogisticRegression max_iter=1000 is sufficient)
4. `delta_curves` has non-degenerate variance across epochs
5. `t*` is identifiable with std < 10 epochs across ≥3 seeds

### Failure Condition
If `delta(t) > 0` window < 10% of training on Waterbirds: STOP — SGD temporal feature learning gap not observed; re-examine theoretical assumptions before H-M1.

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=1.12.0
torchvision>=0.13.0
numpy>=1.21.0
scipy>=1.7.0
scikit-learn>=1.0.0
matplotlib>=3.5.0
pandas>=1.3.0
pyyaml>=6.0
tqdm>=4.62.0
pillow>=9.0.0
```

### 7.2 External Repositories (Reference — not code dependencies)
- **kohpangwei/group_DRO** — canonical Waterbirds/CelebA dataset loaders and ERM training config
- **izmailovpavel/dfr_spurious_correlations** — linear probe methodology (C=1.0, frozen backbone)
- **p-lambda/wilds** — alternative dataset loading API (optional)

### 7.3 Hardware
- Single GPU with ≥16GB VRAM (ResNet-50 training with batch=128) or ≥8GB with batch=32
- ≥16GB RAM
- ≥50GB disk space (checkpoints per seed; can delete after probe evaluation)

---

## 8. Out of Scope (H-E1)

- Gradient structure analysis (H-M1 scope)
- Feature complexity measurement via FFT/separability (H-M2 scope)
- t* variance analysis across seeds (H-M3 scope)
- DFR correlation with checkpoint epoch (H-M4 scope)
- Group annotation usage during ERM training
- Hyperparameter search / grid sweep
- Architecture variants (ViT, BERT)
- Multi-dataset beyond Waterbirds + CelebA
