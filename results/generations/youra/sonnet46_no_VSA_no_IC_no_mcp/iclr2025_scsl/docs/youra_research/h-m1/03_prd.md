# Product Requirements Document: H-M1
# SimCLR Background-Replacement Augmentation — Mechanism Hypothesis

---
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - non_functional_requirements
  - data_specification
  - evaluation_metrics
  - dependencies
  - success_criteria
hypothesis_id: h-m1
hypothesis_type: MECHANISM
tier: FULL
generated_at: "2026-08-26T10:30:00Z"
---

---

## 1. Executive Summary

This PRD specifies the implementation of an ablation study testing whether **augmentation invariance** is the causal mechanism linking contrastive self-supervised learning (SimCLR) to spurious feature encoding. The experiment trains two SimCLR models on the Waterbirds dataset — one with standard augmentations (SimCLR-Original) and one with background-replacement augmentation (SimCLR-NoBackground) — and measures the ratio of spurious-to-task probe accuracy to determine whether suppressing background invariance causally reduces spurious feature encoding.

**Research Question:** Does making background features non-invariant across contrastive views (via background replacement) causally reduce spurious feature encoding in SimCLR representations?

**Expected Outcome:** SimCLR-NoBackground shows ≥5% lower spurious/task ratio than SimCLR-Original (p < 0.05, 5 seeds), with task probe accuracy drop ≤5%.

---

## 2. Problem Statement

### 2.1 Research Gap

SimCLR and similar contrastive SSL methods have been observed to encode spurious features (e.g., background type in Waterbirds), causing poor worst-group generalization. The **mechanism** is hypothesized to be augmentation invariance: features that remain stable across augmented views are encoded. Standard SimCLR augmentations (crop, jitter, grayscale, blur, flip) do NOT randomize background texture, making background a stable, instance-discriminative signal that gets encoded.

### 2.2 Causal Intervention Design

The experiment implements a **causal intervention**: hold all training variables fixed (architecture, optimizer, loss, data), and modify only the augmentation pipeline by replacing background pixels (identified via CUB-200-2011 segmentation masks) with randomly sampled Places365 images. If the mechanism hypothesis is correct, this intervention should reduce background invariance across views → reduce background encoding → reduce spurious probe accuracy → reduce the spurious/task ratio.

### 2.3 Hypothesis Statement

> SimCLR trained with background-replacement augmentation (SimCLR-NoBackground) shows a spurious/task probe accuracy ratio at least 5% lower than SimCLR trained with standard augmentations (SimCLR-Original) on Waterbirds (p < 0.05, 5 seeds), with task probe accuracy remaining within 5% — confirming augmentation invariance as the causal mechanism for spurious feature encoding in contrastive SSL.

---

## 3. Functional Requirements

### FR-1: Data Pipeline

**FR-1.1 Waterbirds Dataset Loading**
- Load Waterbirds via WILDS: `wilds.get_dataset(dataset='waterbirds', root_dir='./data', download=True)`
- Use train split (4,795 images, 95% spuriously correlated), val split (1,199 balanced), test split (5,794 balanced, 25% per group)
- Provide group labels: 4 groups = bird_type × background_type
- Preprocessing: Resize(256) → CenterCrop(224) → Normalize(ImageNet mean/std)
- Dependency: WILDS library, auto-downloads dataset

**FR-1.2 CUB-200-2011 Segmentation Masks**
- Download CUB-200-2011 dataset from Caltech (manual download required — see Section 7.2)
- Load per-image binary segmentation masks from `CUB_200_2011/segmentations/` (one PNG per image)
- Mask format: binary PNG, 1=bird (foreground), 0=background
- Must align masks to Waterbirds image indices (Waterbirds uses CUB image IDs)
- Dependency: CUB-200-2011 manual download; mask loading utility

**FR-1.3 Places365 Background Pool**
- Load Places365-Standard (small=True, 256×256 images) as background replacement pool
- Use torchvision: `torchvision.datasets.Places365(root='./data/places365', split='train-standard', small=True, download=True)`
- Pre-load N=10,000 images into memory as PIL Images for fast random sampling (or lazy-load from disk)
- Dependency: torchvision, disk space ~10GB for small split

**FR-1.4 SimCLR-Original Augmentation Pipeline**
- Standard SimCLR augmentations applied twice per image to generate two views:
  - `RandomResizedCrop(224, scale=(0.2, 1.0))`
  - `RandomApply([ColorJitter(0.8, 0.8, 0.8, 0.2)], p=0.8)`
  - `RandomGrayscale(p=0.2)`
  - `GaussianBlur(kernel_size=23, sigma=(0.1, 2.0))`
  - `RandomHorizontalFlip()`
  - `ToTensor()`, `Normalize(mean, std)`

**FR-1.5 SimCLR-NoBackground Augmentation Pipeline**
- For each image: apply background replacement FIRST, then standard SimCLR augmentations
- `BackgroundReplacementTransform`: load CUB seg mask → sample random Places365 image → replace background pixels (mask=False regions) with Places365 pixels → apply FR-1.4 augmentations
- Each of the two views independently samples a DIFFERENT Places365 background
- Mechanism verification: call `verify_mechanism_activated()` on first batch of training
- Dependency: CUB masks (FR-1.2), Places365 pool (FR-1.3)

### FR-2: Model Architecture

**FR-2.1 SimCLR Backbone**
- ResNet-50 trained from scratch (no pretrained weights): `torchvision.models.resnet50(pretrained=False)`
- Remove final FC layer: `backbone.fc = nn.Identity()` → 2048-dim output from global average pool
- Both SimCLR-Original and SimCLR-NoBackground use IDENTICAL backbone architecture

**FR-2.2 Projection Head**
- 2-layer MLP: Linear(2048, 2048) → ReLU → Linear(2048, 128)
- L2-normalize output: `F.normalize(z, dim=1)`
- Projection head is discarded after pretraining; only backbone used for probe evaluation
- Both conditions use IDENTICAL projection head architecture

### FR-3: SimCLR Training

**FR-3.1 NT-Xent Loss**
- Temperature τ = 0.5
- Formula: InfoNCE loss between positive pairs (augmented views of same image)
- Implementation: gather all views in batch, compute pairwise cosine similarity, mask diagonal, compute cross-entropy with positive pair labels
- Both conditions use IDENTICAL loss function and temperature

**FR-3.2 Training Configuration (Both Conditions)**
- Optimizer: SGD(lr=0.03, momentum=0.9, weight_decay=1e-4)
- LR Schedule: CosineAnnealingLR(T_max=50, eta_min=0)
- Batch size: 256
- Epochs: 50
- Image size: 224×224
- Seeds: 5 seeds [0, 1, 2, 3, 4] — same seeds used for both conditions (paired design)

**FR-3.3 Two-Condition Training Loop**
- For each seed in [0, 1, 2, 3, 4]:
  - Train SimCLR-Original (FR-1.4 augmentation) for 50 epochs → save checkpoint
  - Train SimCLR-NoBackground (FR-1.5 augmentation) for 50 epochs → save checkpoint
- Save checkpoints: `checkpoints/h-m1/{condition}_seed{seed}_epoch50.pt`

**FR-3.4 Mechanism Activation Verification**
- Before SimCLR-NoBackground training: call `verify_mechanism_activated()` on first batch
- Assert `pixel_diff > 0.05` in background regions
- Log message: `"BackgroundReplacementTransform applied — N images with background replaced"` per epoch
- Halt with descriptive error if mechanism not activated

### FR-4: Linear Probe Evaluation

**FR-4.1 Feature Extraction**
- After training: freeze backbone, extract 2048-dim features for all train, val, test images
- Forward pass: disable gradients, pass images through backbone only (no projection head)
- Store: feature arrays `(N, 2048)` with labels

**FR-4.2 Spurious Probe (Background Label)**
- Train `LogisticRegression(C=1.0, max_iter=1000, solver='lbfgs')` on training features
- Labels: background type (land=0, water=1)
- Evaluate on balanced test split (25% per group)
- Record: `spurious_probe_acc` per condition per seed

**FR-4.3 Task Probe (Bird Species)**
- Train `LogisticRegression(C=1.0, max_iter=1000, solver='lbfgs')` on training features
- Labels: bird species (landbird=0, waterbird=1)
- Evaluate on balanced test split
- Record: `task_probe_acc` per condition per seed

**FR-4.4 Ratio Computation**
- `ratio = spurious_probe_acc / task_probe_acc` per condition per seed
- Record all 5 ratios per condition: `ratios_original[5]`, `ratios_no_background[5]`

### FR-5: Statistical Analysis

**FR-5.1 Paired t-Test**
- One-sided paired t-test: `ratios_no_background < ratios_original` across 5 seeds
- `scipy.stats.ttest_rel(ratios_no_background, ratios_original, alternative='less')`
- Report: t-statistic, p-value, Cohen's d effect size

**FR-5.2 Confound Check**
- Compute `task_acc_diff = |task_probe_acc_NoBackground_mean − task_probe_acc_Original_mean|`
- If `task_acc_diff > 0.05`: flag result as INCONCLUSIVE (representation quality confounded)
- If `task_acc_diff ≤ 0.05` AND `ratio_diff ≥ 0.05` AND `p < 0.05`: mechanism CONFIRMED

**FR-5.3 Results Summary**
- Save JSON results: `results/h-m1/probe_results.json` with all per-seed metrics and statistical test output
- Print summary table to stdout

### FR-6: Visualization

**FR-6.1 Required Figure — Gate Metrics Comparison (MANDATORY)**
- Bar chart: mean ratio (Original vs NoBackground) ± std across 5 seeds
- Side-by-side bars for spurious_probe_acc and task_probe_acc
- Save to: `docs/youra_research/h-m1/figures/gate_metrics_comparison.png`

**FR-6.2 Spurious vs Task Scatter Plot**
- Scatter: x=task_probe_acc, y=spurious_probe_acc, one point per condition per seed (10 points total)
- Color by condition (Original vs NoBackground)
- Save to: `docs/youra_research/h-m1/figures/spurious_task_scatter.png`

**FR-6.3 Paired Ratio Plot**
- Lines connecting Original → NoBackground ratio for each seed (5 lines)
- Visualizes consistency of effect across seeds
- Save to: `docs/youra_research/h-m1/figures/paired_ratio_plot.png`

**FR-6.4 Background Replacement Visualization**
- Show 4–6 example images: original image vs background-replaced versions
- Qualitative illustration of augmentation effect
- Save to: `docs/youra_research/h-m1/figures/background_replacement_examples.png`

---

## 4. Non-Functional Requirements

**NFR-1: Reproducibility**
- All randomness controlled via `torch.manual_seed(seed)`, `np.random.seed(seed)`, `random.seed(seed)` at the start of each seed's training run
- Checkpoint saved after final epoch for replication

**NFR-2: Experiment Isolation**
- Two completely separate training runs per seed (not shared parameters)
- Only augmentation pipeline differs between conditions; all other variables held fixed

**NFR-3: Computation Constraints**
- Target hardware: Single GPU (16GB VRAM sufficient for batch=256, ResNet-50)
- Estimated time: ~2–4 hours per seed per condition (50 epochs × ~19 steps/epoch on Waterbirds)
- Total: ~20–40 hours for all 10 runs (2 conditions × 5 seeds)

**NFR-4: Failure Modes Handled**
- Missing CUB masks → raise FileNotFoundError with download instructions
- Places365 load failure → raise with fallback instruction (use pre-downloaded subset)
- SimCLR collapse (task_probe_acc < 0.53) → log WARNING, mark seed as FAILED, continue
- Mechanism not activated (pixel_diff < 0.05) → HALT with descriptive error

**NFR-5: Code Organization**
- Modular: separate files for data loading, augmentation, model, training, evaluation, visualization
- Single entrypoint: `run_experiment.py --seed N --condition {original|no_background}`
- Results aggregation: `aggregate_results.py` reads all per-seed JSONs and runs statistical analysis

---

## 5. Data Specification

### 5.1 Primary Dataset: Waterbirds

| Field | Value |
|-------|-------|
| Source | WILDS (`wilds.get_dataset('waterbirds')`) — auto-download |
| Train size | 4,795 images (95% spurious correlation) |
| Val size | 1,199 images (balanced) |
| Test size | 5,794 images (balanced, 25% per group) |
| Groups | 4: {landbird-land, landbird-water, waterbird-land, waterbird-water} |
| Labels | bird_type (0=landbird, 1=waterbird), background_type (0=land, 1=water) |
| Preprocessing | Resize(256) → CenterCrop(224) → Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]) |

### 5.2 CUB-200-2011 Segmentation Masks

| Field | Value |
|-------|-------|
| Source | Manual download from Caltech CUB-200-2011 website (see FR-1.2) |
| Format | Binary PNG per image; 1=bird foreground, 0=background |
| Path | `./data/CUB_200_2011/segmentations/{species_folder}/{image_name}.png` |
| Coverage | One mask per CUB image (all Waterbirds images derived from CUB) |
| Download | Required before running SimCLR-NoBackground condition |

### 5.3 Places365 Background Pool

| Field | Value |
|-------|-------|
| Source | `torchvision.datasets.Places365(split='train-standard', small=True, download=True)` — auto-download |
| Size | ~1.8M images (small=True, 256×256); use any subset ≥ 10K for background diversity |
| Usage | Random sampling for background replacement augmentation |
| Memory | Pre-load 10K images as PIL Images (~2GB RAM); or lazy-load from disk |

---

## 6. Evaluation Metrics

### 6.1 Primary Metrics (per condition, per seed)

| Metric | Formula | Purpose |
|--------|---------|---------|
| `spurious_probe_acc` | Linear probe accuracy on background label | Measures spurious feature encoding |
| `task_probe_acc` | Linear probe accuracy on bird species | Measures task-relevant feature quality |
| `ratio` | `spurious_probe_acc / task_probe_acc` | Primary hypothesis metric |

### 6.2 Statistical Metrics (across 5 seeds)

| Metric | Computation | Threshold |
|--------|-------------|-----------|
| `ratio_diff_mean` | `mean(ratios_original) - mean(ratios_no_background)` | ≥ 0.05 |
| `p_value` | One-sided paired t-test | < 0.05 |
| `cohen_d` | Effect size | Reported only |
| `task_acc_diff` | `|mean(task_original) - mean(task_no_background)|` | ≤ 0.05 (confound check) |

### 6.3 Gate Condition

- PASS: `ratio_diff_mean ≥ 0.05` AND `p_value < 0.05` AND `task_acc_diff ≤ 0.05`
- INCONCLUSIVE: `task_acc_diff > 0.05` (representation quality confounded)
- FAIL: `ratio_diff_mean < 0.05` OR `p_value ≥ 0.05`

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
torchvision>=0.15.0
wilds>=2.0.0
numpy>=1.24.0
scikit-learn>=1.2.0
scipy>=1.10.0
Pillow>=9.0.0
matplotlib>=3.7.0
tqdm>=4.65.0
pyyaml>=6.0
```

### 7.2 External Repositories / Manual Downloads

| Resource | Source | Action Required |
|----------|--------|-----------------|
| CUB-200-2011 dataset | http://www.vision.caltech.edu/datasets/cub_200_2011/ | Manual download, extract to `./data/CUB_200_2011/` |
| CUB segmentation masks | Included in CUB-200-2011 archive | Already included in `./data/CUB_200_2011/segmentations/` |
| HobbitLong/SupContrast | https://github.com/HobbitLong/SupContrast | Reference only (do not install; implement from scratch) |

### 7.3 Hardware Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| GPU VRAM | 12GB | 16GB |
| CPU RAM | 16GB | 32GB |
| Disk | 50GB | 100GB |
| GPUs | 1 | 1 |

---

## 8. Success Criteria

| Criterion | Measurement | Pass Threshold |
|-----------|-------------|----------------|
| Code runs without error | Both SimCLR conditions complete for all 5 seeds | No exceptions |
| Mechanism activated | `verify_mechanism_activated()` passes | `pixel_diff > 0.05` |
| Effect direction correct | `ratio_NoBackground_mean < ratio_Original_mean` | Directional |
| Effect size sufficient | `ratio_diff_mean` | ≥ 0.05 |
| Statistical significance | Paired t-test p-value | < 0.05 |
| Confound not triggered | `task_acc_diff` | ≤ 0.05 |
| Results saved | `results/h-m1/probe_results.json` | File exists, valid JSON |
| Figures generated | 4 figures in `figures/` folder | All 4 present |

---

## 9. Out of Scope

- SupCon, BYOL, MoCo, or other SSL methods (H-M1 tests SimCLR specifically)
- ImageNet-pretrained backbone (must train from scratch)
- Group-balanced training (Waterbirds standard training set used as-is)
- DRO or reweighting during SSL pretraining
- Fine-tuning (linear probe only)
- Multi-GPU training

---

## 10. Implementation Notes

### Priority of Causal Isolation
The experiment's validity depends entirely on **isolating the augmentation as the only variable**. All other aspects (architecture, optimizer, loss, data order per seed, batch construction) must be identical between conditions. Use `torch.manual_seed(seed)` BEFORE both condition training runs for each seed.

### CUB Mask Alignment
Waterbirds uses CUB-200-2011 images but reindexes them. The mask loading module must correctly map Waterbirds indices to CUB image filenames. Use the Waterbirds metadata file (`metadata.csv`) which contains the original CUB image IDs.

### Places365 Background Diversity
Pre-loading a fixed set of 10K Places365 images provides sufficient diversity. Shuffle and cache at experiment start. Do not re-download per epoch.
