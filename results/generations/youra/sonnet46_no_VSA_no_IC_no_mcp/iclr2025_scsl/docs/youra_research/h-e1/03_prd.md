---
title: "PRD: h-e1 — Spurious/Task Probe Accuracy Ratio Across Pretraining Paradigms"
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
tier: LIGHT
date: 2026-08-26
author: yoon303b@gmail.com
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - nfrs
  - success_criteria
  - data_specification
  - dependencies
---

# PRD: h-e1 — Spurious/Task Probe Accuracy Ratio Study

## 1. Executive Summary

This document specifies the implementation requirements for hypothesis h-e1: a proof-of-concept probing experiment to determine whether different pretraining paradigms (ERM, MoCo-v3, DINO, BarlowTwins) encode spurious features to statistically different degrees in frozen ResNet-50 features.

The experiment trains linear probes on frozen ResNet-50 features from 4 pretrained models, measuring probe accuracy for task labels (bird species) and spurious attributes (background) on Waterbirds balanced test split. The ratio spurious_acc / task_acc is computed per paradigm across 5 seeds, then tested for significant differences.

Gate: MUST_WORK — at least one paradigm pair shows Bonferroni-corrected p < 0.05 AND ratio difference ≥ 0.02.

---

## 2. Problem Statement

### 2.1 Research Question
Do different pretraining paradigms (supervised ERM, contrastive SSL MoCo-v3, self-distillation DINO, non-contrastive SSL BarlowTwins) encode spurious features at statistically different levels in frozen ResNet-50 representations?

### 2.2 Hypothesis Statement
At least one paradigm pair shows a statistically significant difference in spurious/task probe accuracy ratio on Waterbirds balanced test split (≥ 2%, p < 0.05, across 5 seeds using frozen ResNet-50 features and linear probes).

### 2.3 Motivation
If pretraining paradigm affects spurious encoding, then SSL models may provide better or worse starting points for downstream fairness-aware learning. This existence check is the prerequisite for mechanism and mitigation hypotheses.

---

## 3. Scope

### 3.1 In Scope
- Feature extraction from 4 frozen ResNet-50 pretrained models
- Linear probe training on group-balanced Waterbirds val split
- Evaluation on full Waterbirds balanced test split (5,794 images)
- Statistical significance testing (ANOVA + 6 pairwise t-tests, Bonferroni corrected)
- Visualization of results (bar chart + supplementary figures)

### 3.2 Out of Scope
- Fine-tuning any backbone
- Custom architectures
- Datasets other than Waterbirds
- Group DRO or fairness interventions

---

## 4. Data Specification

### 4.1 Primary Dataset: Waterbirds (WILDS)

| Field | Value |
|---|---|
| Name | Waterbirds |
| Source | WILDS 2.0 benchmark |
| Loading | `wilds.get_dataset('waterbirds', download=True, root_dir='./data/')` |
| Auto-download | Yes — no manual download task required |
| Train size | 4,795 images (4 groups, 95% spurious correlation) |
| Val size | 1,199 images (balanced groups) |
| Test size | 5,794 images (balanced, 50% spurious per class) |

**Group structure:** 4 groups = {bird_label ∈ {waterbird, landbird}} × {background ∈ {water, land}}

**Labels:**
- Task label: bird species (waterbird=1, landbird=0)
- Spurious label: background (water=1, land=0) — from `metadata_array[:, 0]`

### 4.2 Preprocessing

```python
from torchvision import transforms
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
```

### 4.3 Probe Train Split

- Source: WILDS `val` subset
- Sampling: Group-balanced (equal samples per group = 4 × min_group_count)
- Rationale: Avoids 95% spurious correlation in training set biasing probe

### 4.4 Evaluation Split

- Source: Full WILDS `test` subset (5,794 images)
- No subsampling — use complete balanced test set

### 4.5 No Manual Download Required

Waterbirds is auto-downloaded via WILDS API. No data-preparation task needed.

---

## 5. Functional Requirements

### FR-1: Model Loading (4 Paradigms)

The system MUST load all 4 frozen ResNet-50 models:

| FR | Paradigm | Loading Method | Feature Dim |
|---|---|---|---|
| FR-1.1 | ERM (Supervised) | `torchvision.models.resnet50(pretrained=True); model.fc = nn.Identity()` | 2048 |
| FR-1.2 | MoCo-v3 | `torch.hub.load('facebookresearch/moco-v3:main', 'resnet50')` | 2048 |
| FR-1.3 | DINO | `torch.hub.load('facebookresearch/dino:main', 'dino_resnet50')` | 2048 |
| FR-1.4 | BarlowTwins | `torch.hub.load('facebookresearch/barlowtwins:main', 'resnet50'); model.fc = nn.Identity()` | 2048 |

All models: `.eval()`, no gradient, frozen backbone.

**Tensor shape assertion required:** `assert features.shape[1] == 2048`

### FR-2: Feature Extraction

The system MUST extract frozen features from each model:

```python
def extract_features(model, dataloader, device) -> tuple[Tensor, Tensor, Tensor]:
    """Returns: (features: (N,2048), task_labels: (N,), spurious_labels: (N,))"""
```

- Batch size: 256
- No augmentation (deterministic)
- Task label: `y` (bird species)
- Spurious label: `metadata[:, 0]` (background)

### FR-3: Probe Train Split Construction

The system MUST construct a group-balanced probe train split from the WILDS val set:

- Equal samples per group (4 groups)
- Seed-controlled random sampling (5 seeds: [0, 1, 2, 3, 4])
- Implementation: index groups via `metadata_array`, sample `min_group_count` per group

### FR-4: Linear Probe Training (2 Targets × 4 Paradigms × 5 Seeds = 40 fits)

The system MUST train sklearn LogisticRegression probes:

```python
from sklearn.linear_model import LogisticRegression
clf = LogisticRegression(max_iter=1000, C=1.0, solver='lbfgs', multi_class='auto')
clf.fit(features_train.numpy(), labels_train.numpy())
```

- 2 probes per (paradigm, seed): task-label probe + spurious-label probe
- Total: 4 paradigms × 2 targets × 5 seeds = 40 fits

### FR-5: Ratio Computation

The system MUST compute the spurious/task ratio per (paradigm, seed):

```python
ratio = spurious_probe_acc / task_probe_acc
```

- Higher ratio = spurious feature more strongly encoded relative to task feature
- Must log: `Paradigm={paradigm}, seed={seed}, spurious_acc={:.3f}, task_acc={:.3f}, ratio={:.4f}`

### FR-6: Statistical Analysis

The system MUST compute:

| Test | Specification |
|---|---|
| One-way ANOVA | `scipy.stats.f_oneway(*[ratios[p] for p in PARADIGMS])` |
| 6 pairwise t-tests | `scipy.stats.ttest_ind(ratios[p1], ratios[p2])` for all C(4,2) pairs |
| Bonferroni correction | `p_corrected = p_raw * 6` |
| Cohen's d | Effect size per pair |
| Report | Mean ± std ratio per paradigm, p-values, effect sizes |

### FR-7: Gate Verification

The system MUST evaluate the MUST_WORK gate:

```python
gate_satisfied = any(
    p_bonferroni < 0.05 and abs(mean_ratio_A - mean_ratio_B) >= 0.02
    for each pair (A, B)
)
```

Log gate pass/fail and which pairs satisfy the condition.

### FR-8: Visualization (Mandatory + Autonomous)

**FR-8.1 (Mandatory):** Bar chart — spurious/task ratio per paradigm (mean ± std), horizontal threshold line at ratio_diff = 0.02, p-value annotations for significant pairs.

**FR-8.2 (Autonomous, Phase 4 discretion):**
- 2×4 heatmap: (spurious_acc, task_acc) × 4 paradigms
- Scatter: spurious_acc vs. task_acc per paradigm (5 seeds as points)
- 4×4 pairwise p-value matrix (Bonferroni corrected)
- Violin/box plot of ratio distribution per paradigm

All figures saved to `./docs/youra_research/h-e1/figures/`.

### FR-9: Pre-condition Validation

Before proceeding to statistical analysis:
```python
assert all(probe_acc > 0.5 for probe_acc in [task_acc, spurious_acc])  # above balanced chance
```

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- All 5 seeds fixed: [0, 1, 2, 3, 4]
- `torch.manual_seed(seed)`, `np.random.seed(seed)` before each probe fit
- Feature extraction is deterministic (no augmentation, eval mode)

### NFR-2: Compute
- Target: ≤ 3 hours on single GPU (CUDA)
- Feature extraction: batch_size=256, no_grad context

### NFR-3: Output Artifacts
- `results/h-e1_ratios.csv` — per-paradigm per-seed ratios, accuracies
- `results/h-e1_stats.json` — ANOVA, pairwise tests, gate verdict
- `figures/` — all visualizations
- `logs/h-e1_run.log` — per-seed logging

### NFR-4: Code Quality
- No hard-coded paths (use config)
- Modular: data_utils.py, model_utils.py, probe_utils.py, stats_utils.py, run_experiment.py

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0
torchvision>=0.15
wilds>=2.0
scikit-learn>=1.2
scipy>=1.10
numpy>=1.24
matplotlib>=3.7
pandas>=2.0
```

### 7.2 External Repositories (Reference Only)

| Repository | URL | Purpose |
|---|---|---|
| izmailovpavel/spurious_feature_learning | https://github.com/izmailovpavel/spurious_feature_learning | Protocol reference (NOT a code dependency) |
| facebookresearch/moco-v3 | https://github.com/facebookresearch/moco-v3 | Hub source for MoCo-v3 weights |
| facebookresearch/dino | https://github.com/facebookresearch/dino | Hub source for DINO weights |
| facebookresearch/barlowtwins | https://github.com/facebookresearch/barlowtwins | Hub source for BarlowTwins weights |

### 7.3 Hardware
- Single GPU (CUDA) required for feasible runtime
- Min VRAM: 8GB (ResNet-50 feature extraction, batch=256)
- Disk: ~5GB for Waterbirds dataset + model weights cache (~4 × 100MB)

---

## 8. Success Criteria

### 8.1 MUST_WORK Gate (Phase 4 Exit Criterion)

| Criterion | Specification |
|---|---|
| Gate condition | min(Bonferroni-corrected p) < 0.05 AND max(ratio_diff) ≥ 0.02 across any paradigm pair |
| Pre-condition | All probe accuracies > 0.5 (above balanced chance baseline) |
| Code must run | Full pipeline completes for all 4 paradigms × 5 seeds without error |

### 8.2 Expected Baseline Performance (from research)

| Paradigm | Expected spurious_acc | Expected task_acc | Expected ratio |
|---|---|---|---|
| ERM ResNet-50 | ~90–100% | ~85–90% | ~1.05–1.15 |
| DINO ResNet-50 | TBD by experiment | TBD | Expected lower ratio |
| MoCo-v3 ResNet-50 | TBD | TBD | TBD |
| BarlowTwins ResNet-50 | TBD | TBD | TBD |

Source: Izmailov et al. 2022, DINOv2 background bias analysis.

### 8.3 Gate Failure Routing
If gate fails: route to Phase 0 (per verification_state gate configuration).

---

## 9. Traceability

| Requirement | Source |
|---|---|
| Dataset choice (Waterbirds WILDS) | 02c_experiment_brief.md §Dataset; Izmailov et al. 2022 |
| 4 paradigm models | 02c_experiment_brief.md §Models |
| Logistic regression probe | Izmailov et al. 2022 protocol |
| 5 seeds | 02b_verification_plan.md |
| Bonferroni correction, 6 pairs | 02b_verification_plan.md |
| Success criterion (≥2%, p<0.05) | 02b_verification_plan.md; 02c_experiment_brief.md §Gate Condition |
| Visualization requirements | 02c_experiment_brief.md §Visualization Requirements |
