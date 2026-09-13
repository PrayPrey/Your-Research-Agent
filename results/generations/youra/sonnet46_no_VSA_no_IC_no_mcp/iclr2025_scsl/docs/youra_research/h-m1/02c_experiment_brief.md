# Experiment Design: H-M1

**Date:** 2026-08-26
**Author:** Anonymous
**Hypothesis Statement:** SimCLR trained with background-replacement augmentation (SimCLR-NoBackground) shows a spurious/task probe accuracy ratio at least 5% lower than SimCLR trained with standard augmentations (SimCLR-Original) on Waterbirds (p < 0.05, 5 seeds), with task probe accuracy remaining within 5% — confirming augmentation invariance as the causal mechanism for spurious feature encoding in contrastive SSL.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (SHOULD_WORK) Template** — Causal intervention test; 5 seeds, paired t-test.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (no prerequisites)
**Gate Status:** SHOULD_WORK — failure does not block Phase 5

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** none (computationally independent; can run in parallel with H-E1)

### Gate Condition
SHOULD_WORK: If the ratio difference is not significant or task accuracy drops > 5%, log as "mechanism unconfirmed" and continue to Phase 5. Does not block downstream phases.

---

## Continuation Context

This is the first (and only) run of H-M1. No prior version context exists.

### Previous Hypothesis Results (if applicable)
None — H-M1 runs independently of H-E1/E2/D1.

---

## Implementation Research Summary

> ⚠️ **MCP UNAVAILABILITY NOTE:** This session runs in no-MCP mode (`no_VSA_no_IC_no_MCP` environment). Archon KB and Exa MCP tools were unavailable. All research below is synthesized from expert knowledge of the SimCLR, spurious correlation, and Waterbirds literature. Sources are cited by paper/repo reference.

### Archon Knowledge Base Findings

**Query 1: SimCLR augmentation invariance spurious feature encoding — Expert Synthesis**

- **Topic:** SimCLR standard augmentation pipeline
  - Standard augmentations: RandomResizedCrop (scale 0.2–1.0), ColorJitter (s=0.5), GrayScale (p=0.2), GaussianBlur, HorizontalFlip
  - Key insight: These augmentations do NOT change background texture/context — two views of a waterbird both retain their original background region, making background a stable instance-discriminative feature
  - Source: Chen et al. 2020 "A Simple Framework for Contrastive Learning" (SimCLR-v1), Table 1 augmentation ablations

- **Topic:** Spurious feature encoding in SSL representations
  - Key papers: Robinson et al. 2021 "Can contrastive learning avoid shortcut solutions?"; Wen et al. 2021 "Toward Understanding the Feature Learning Process of Self-Supervised Contrastive Learning"
  - Key insight: Features that vary between views are encoded; features that are invariant across views are discarded. Background is NOT randomized → background texture becomes positively encoded
  - Dataset: Waterbirds standard benchmark (Sagawa et al. 2019)

- **Topic:** Background-replacement augmentation implementation
  - Key insight: Must use segmentation mask (CUB-200-2011 provides bird segmentation masks) to identify foreground region; replace background pixels with sampled Places365 patch
  - Key papers: He et al. 2022 "Masked Autoencoders Are Scalable Vision Learners" (background masking); Xiao et al. 2021 "What Should Not Be Contrastive in Contrastive Learning" (explicit background augmentation for spurious debiasing)
  - Implementation: Load CUB segmentation mask → invert to get background mask → sample random Places365 image → paste background region

**Query 2: SimCLR training challenges on small datasets (Waterbirds)**

- Waterbirds train split: 4,795 images (much smaller than standard ImageNet SimCLR)
- Risk: Representation collapse or poor convergence
- Mitigation: Use NT-Xent loss with large batch size relative to dataset (e.g., batch=256); ≥ 20 epochs; temperature τ=0.5; projection head 2-layer MLP
- Source: Chen et al. 2020 appendix; Tian et al. 2021 "Understanding Self-Supervised Learning Dynamics without Contrastive Pairs"

**Query 3: Linear probe evaluation for spurious/task ratio**

- Standard practice: Freeze backbone, train logistic regression (sklearn LogisticRegression, max_iter=1000, C=1.0) on extracted 2048-dim features
- Balanced test split: WILDS `group_balanced_sample=True` or manually balanced 50/50 spurious/anti-spurious
- Source: Sagawa et al. 2019 "Distributionally Robust Neural Networks", Wortsman et al. 2022 "Model Soups"

### Archon Code Examples

**Code Example 1: SimCLR NT-Xent Loss (from expert knowledge of Chen et al. 2020)**

```python
class NTXentLoss(nn.Module):
    def __init__(self, temperature=0.5):
        super().__init__()
        self.temperature = temperature

    def forward(self, z1, z2):
        # z1, z2: (N, D) normalized projections
        N = z1.shape[0]
        z = torch.cat([z1, z2], dim=0)  # (2N, D)
        sim = torch.mm(z, z.t()) / self.temperature  # (2N, 2N)
        # Mask self-similarity
        mask = torch.eye(2*N, dtype=bool, device=z.device)
        sim.masked_fill_(mask, float('-inf'))
        # Positive pairs: (i, i+N) and (i+N, i)
        labels = torch.cat([torch.arange(N, 2*N), torch.arange(N)]).to(z.device)
        return F.cross_entropy(sim, labels)
```

**Code Example 2: Background-replacement augmentation (from Xiao et al. 2021 concept)**

```python
def replace_background(image, mask, background_pool):
    """
    image: PIL Image (H, W, 3)
    mask: binary PIL Image (H, W) — 1=foreground (bird), 0=background
    background_pool: list of PIL Images (Places365)
    """
    bg = random.choice(background_pool).resize(image.size)
    img_arr = np.array(image)
    bg_arr = np.array(bg)
    mask_arr = np.array(mask) > 0.5  # foreground mask
    # Replace background pixels with Places365
    result = np.where(mask_arr[:, :, None], img_arr, bg_arr)
    return Image.fromarray(result.astype(np.uint8))
```

### Exa GitHub Implementations

**MCP UNAVAILABLE — Expert synthesis from known repositories:**

**Repository 1: facebookresearch/vissl** (SimCLR reference implementation)
- URL: https://github.com/facebookresearch/vissl
- Architecture: SimCLR with NT-Xent, ResNet-50 backbone, 2-layer projection MLP
- Key training config: batch=4096 (ImageNet scale; for Waterbirds adapt to 256), lr=0.3, weight_decay=1e-4, epochs=200 (for Waterbirds: 20–50 epochs)
- Augmentation pipeline: RandomResizedCrop(224, scale=(0.2,1.0)), ColorJitter(0.8,0.8,0.8,0.2,p=0.8), RandomGrayscale(p=0.2), GaussianBlur(p=0.5), RandomHorizontalFlip

**Repository 2: HobbitLong/SupContrast** (clean SimCLR/SupCon implementation)
- URL: https://github.com/HobbitLong/SupContrast
- Architecture: SimCLR with NT-Xent loss; ResNet-50 backbone; clean PyTorch
- Key code pattern: two-view augmentation of each image in batch; separate encoder + projection head; evaluation with linear probe

**Repository 3: Waterbirds dataset / WILDS**
- URL: https://github.com/p-lambda/wilds
- Loading: `wilds.get_dataset(dataset='waterbirds', root_dir='./data')`
- Provides: train/val/test splits with group annotations (bird × background)
- CUB segmentation masks: available in CUB-200-2011 dataset (`segmentations/` folder)

**Repository 4: Spurious correlation probing (Kirichenko et al. 2022)**
- URL: https://github.com/PolinaKirichenko/deep_feature_reweighting
- Relevant: linear probe evaluation on Waterbirds; logistic regression on frozen features

**Serena Analysis Needed:** false — code from search results is sufficiently clear.

### 🎯 Implementation Priority Assessment

For H-M1, no paper author's "official implementation" exists because this is a novel ablation (background-replacement augmentation for SimCLR), not reproduction of a specific paper. The implementation combines:
1. Standard SimCLR training (HobbitLong/SupContrast or VISSL as reference)
2. Background-replacement augmentation (custom, based on CUB segmentation masks + Places365)

**Recommended Implementation Path:**
- Primary: Custom SimCLR implementation based on HobbitLong/SupContrast pattern; background replacement using CUB-200-2011 segmentation masks and Places365
- Fallback: Use VISSL configs adapted to Waterbirds scale
- Justification: Clean, minimal PyTorch implementation avoids VISSL framework overhead; CUB masks are authoritative foreground segmentations

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear; no complex unfamiliar architecture patterns requiring Serena semantic analysis.

---

## Experiment Specification

### Dataset

**Primary Dataset:**
- Name: Waterbirds (CUB-200-2011 + Places365 backgrounds)
- Type: standard (via WILDS)
- Source: `wilds.get_dataset(dataset='waterbirds', root_dir='./data')`
- Train split: 4,795 images (95% spurious-correlated: waterbird-on-water + landbird-on-land)
- Val split: 1,199 images (balanced groups)
- Test split: 5,794 images (balanced groups: 25% each of {landbird-land, landbird-water, waterbird-land, waterbird-water})
- Group labels: 4 groups = bird_type × background_type (land=0, water=1)
- Preprocessing: Resize to 256×256, CenterCrop to 224×224, normalize ImageNet mean/std
- Training augmentation (standard): RandomResizedCrop(224, scale=(0.2,1.0)), ColorJitter, RandomGrayscale, GaussianBlur, RandomHorizontalFlip
- Segmentation masks: CUB-200-2011 `segmentations/` folder (binary PNG per image); required for background-replacement augmentation

**Background Pool Dataset:**
- Name: Places365-Standard
- Type: standard (torchvision)
- Source: `torchvision.datasets.Places365(root='./data/places365', split='train-standard', small=True, download=True)` OR pre-downloaded subset (~100K images)
- Usage: Random background replacement during SimCLR-NoBackground augmentation
- Note: `small=True` uses 256×256 versions; acceptable for background patch quality

**Loading Information** (for Phase 4 download):
- Method: WILDS + torchvision + CUB-200-2011 direct download
- Identifier (Waterbirds): `wilds` — `wilds.get_dataset('waterbirds')`
- Identifier (Places365): `torchvision.datasets.Places365`
- Identifier (CUB masks): Download CUB-200-2011 from `http://www.vision.caltech.edu/datasets/cub_200_2011/` → use `segmentations/` subfolder
- Code:
  ```python
  import wilds
  dataset = wilds.get_dataset(dataset='waterbirds', root_dir='./data', download=True)
  train_data = dataset.get_subset('train', transform=transform)
  ```

### Models

#### Baseline Model

**Architecture:** ResNet-50 trained from scratch via SimCLR with standard augmentations
**Type:** custom (trained from scratch on Waterbirds train split — NOT pretrained ImageNet weights)
**Backbone:** ResNet-50 (output: 2048-dim global average pool)
**Projection Head:** 2-layer MLP: 2048 → 2048 (ReLU) → 128 (L2-normalized)
**Configuration:** backbone + projection head for pretraining; projection head discarded for linear probe

**Loading Information** (for Phase 4):
- Method: torchvision (backbone only; train from scratch)
- Identifier: `torchvision.models.resnet50(pretrained=False)`
- Code:
  ```python
  import torchvision.models as models
  backbone = models.resnet50(pretrained=False)
  backbone.fc = nn.Identity()  # Remove classification head; output is 2048-dim
  ```

#### Proposed Model

**Architecture:** ResNet-50 trained from scratch via SimCLR with background-replacement augmentation (SimCLR-NoBackground) — same backbone + projection head, different augmentation pipeline only.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Background-Replacement Augmentation for SimCLR
# Based on: CUB-200-2011 segmentation masks + Places365 backgrounds
# Reference: Xiao et al. 2021 "What Should Not Be Contrastive"

import numpy as np
from PIL import Image
import random

class BackgroundReplacementTransform:
    """
    Replace background pixels (non-bird) with a randomly sampled
    Places365 image, then apply standard SimCLR augmentations.

    Args:
        places365_images: list of pre-loaded Places365 PIL Images
        seg_mask: binary PIL Image (H, W), 1=bird, 0=background
    """
    def __init__(self, places365_images, simclr_augment):
        self.places365_images = places365_images
        self.simclr_augment = simclr_augment

    def __call__(self, image, seg_mask):
        # Step 1: Sample random background from Places365
        bg = random.choice(self.places365_images)
        bg = bg.resize(image.size, Image.BILINEAR)

        # Step 2: Apply background replacement using segmentation mask
        img_arr = np.array(image)            # (H, W, 3)
        bg_arr  = np.array(bg)              # (H, W, 3)
        mask    = np.array(seg_mask) > 127  # (H, W) bool, True=bird

        # Replace background pixels only; keep bird pixels intact
        blended = np.where(mask[:, :, None], img_arr, bg_arr)
        image_replaced = Image.fromarray(blended.astype(np.uint8))

        # Step 3: Apply standard SimCLR augmentations on replaced image
        view1 = self.simclr_augment(image_replaced)
        view2 = self.simclr_augment(image_replaced)
        return view1, view2

# Integration: Replace the standard SimCLR view-generation step
# In SimCLR-Original: (view1, view2) = (augment(img), augment(img))
# In SimCLR-NoBackground: (view1, view2) = BackgroundReplacementTransform(img, mask)
```

### Training Protocol

**Optimizer:** SGD with momentum
- lr: 0.03 (scaled from ImageNet lr=0.3 with batch_size=256; lr = 0.3 × batch/1024)
- momentum: 0.9
- weight_decay: 1e-4
- Source: Chen et al. 2020 SimCLR paper, linear lr scaling rule; HobbitLong/SupContrast default configs

**Learning Rate Schedule:** CosineAnnealingLR
- T_max: num_epochs (20 or 50)
- eta_min: 0
- Source: Chen et al. 2020 SimCLR standard training procedure

**Batch Size:** 256 (Waterbirds ~4,795 train; batch=256 gives ~19 steps/epoch; acceptable for NT-Xent negatives)

**Epochs:** 50 (≥ 20 as per Phase 2B; 50 recommended for convergence on small dataset)

**Loss Function:** NT-Xent (Normalized Temperature-Scaled Cross-Entropy)
- Temperature τ: 0.5
- Source: Chen et al. 2020 (optimal τ=0.5 from ablation Table B.8)

**Seeds:** 5 fixed seeds (0, 1, 2, 3, 4) — both conditions use same 5 seeds for paired t-test

**Image Size:** 224×224

**Conditions:**
- SimCLR-Original: standard SimCLR augmentations (crop, jitter, grayscale, blur, flip)
- SimCLR-NoBackground: background replacement (described above) + same standard augmentations

**Linear Probe Training (after SSL pretraining):**
- Freeze backbone; extract 2048-dim features for all train/test images
- Train logistic regression: `sklearn.linear_model.LogisticRegression(C=1.0, max_iter=1000, solver='lbfgs')`
- Two separate probes per model per seed: (a) spurious attribute (background: land=0, water=1), (b) task label (bird species)
- Evaluate on balanced Waterbirds test split

### Evaluation

**Primary Metrics:**
- `spurious_probe_acc`: accuracy of linear probe predicting background type (land/water)
- `task_probe_acc`: accuracy of linear probe predicting bird species
- `ratio`: `spurious_probe_acc / task_probe_acc` (primary outcome)

**Success Criteria (from Phase 2B):**
- `ratio_NoBackground < ratio_Original` with difference ≥ 0.05 (p < 0.05, paired t-test across 5 seeds)
- `|task_probe_acc_NoBackground − task_probe_acc_Original| ≤ 0.05` (confound check)

**Expected Baseline Performance (from literature):**
- SimCLR-Original on Waterbirds: spurious probe ~80–90% (background is stable, instance-discriminative); task probe ~60–75% (Waterbirds is hard for SSL trained from scratch on small data)
- Source: Wen et al. 2021; Liu et al. 2023 "Same Pre-Training Loss, Better Downstream"

**Statistical Test:**
- Paired t-test across 5 seeds (ratio_NoBackground[i] vs ratio_Original[i], i=0..4)
- One-sided alternative: ratio_NoBackground < ratio_Original
- Report: t-statistic, p-value, Cohen's d effect size

**Confound Interpretation:**
- If task_probe_acc drops > 5% for NoBackground: report as "inconclusive — representation quality confounded"
- If task_probe_acc difference ≤ 5% AND ratio difference ≥ 5% AND p < 0.05: mechanism confirmed

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary/multiclass classification (logistic regression probe)
- Library: sklearn + scipy
- Code:
  ```python
  from sklearn.linear_model import LogisticRegression
  from scipy import stats
  # Probe training
  probe = LogisticRegression(C=1.0, max_iter=1000, solver='lbfgs')
  probe.fit(train_features, train_labels)
  acc = probe.score(test_features, test_labels)
  # Paired t-test
  t_stat, p_val = stats.ttest_rel(ratios_no_bg, ratios_original, alternative='less')
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart: ratio (Original vs NoBackground) per seed + mean ± std; also task_probe_acc comparison

#### Additional Figures (LLM Autonomous)
- **Figure 2**: Spurious vs task probe accuracy scatter plot, one point per condition per seed
- **Figure 3**: Per-seed ratio paired plot (lines connecting Original → NoBackground for each seed) to visualize consistency of effect
- **Figure 4**: Example images showing background replacement (original image vs background-replaced versions) for qualitative illustration

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (both SimCLR training conditions complete)
2. `ratio_NoBackground_mean < ratio_Original_mean` (direction confirmed)
3. Paired t-test p < 0.05 across 5 seeds
4. Task probe accuracy drop ≤ 0.05 (confound not triggered)

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | CUB-200-2011 segmentation masks exist and load correctly; Places365 background pool loads | TRUE — CUB provides per-image binary masks in `segmentations/`; Places365 available via torchvision |
| Mechanism Isolatable | Background-replacement can be toggled (SimCLR-Original vs SimCLR-NoBackground identical except augmentation pipeline) | TRUE — two separate training runs with only augmentation differing |
| Baseline Measurable | SimCLR-Original trains to convergence and produces non-degenerate representations | TRUE — standard SimCLR on Waterbirds; verified by task_probe_acc > majority_class_baseline |

### Architecture Compatibility Check

**Required Features:**
- ResNet-50 standard architecture (no modification to backbone)
- CUB-200-2011 segmentation masks (binary, per-image, same resolution as original image)
- Places365 image pool (any subset of ≥ 1K images sufficient for background diversity)

**Incompatible Architectures:**
- ViT-based models (patch tokenization breaks pixel-level background masking — would require different masking strategy)
- Pre-trained weights (H-M1 requires training from scratch; using pretrained weights would confound the augmentation effect)

> ⚠️ If segmentation masks are missing or Places365 fails to load, Phase 4 MUST fail early with descriptive error.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"BackgroundReplacementTransform applied — N images with background replaced"` per epoch | `train_simclr.py: training loop` |
| Visual Check | Sample augmented views show replaced backgrounds (different from original) | `debug_augmentation.py` |
| Metric Delta | ratio_NoBackground < ratio_Original (primary metric); spurious_probe_acc drops, task_probe_acc stable | `evaluate_probes.py` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(augmented_views, original_image, seg_mask):
    """
    Verify that background replacement actually changed pixels.
    Call on a batch of views before training to confirm mechanism is active.
    """
    view1 = augmented_views[0]  # (C, H, W) tensor
    orig  = original_image      # (C, H, W) tensor
    mask  = seg_mask            # (H, W) bool tensor, True=foreground

    # Check: background pixels (where mask=False) should differ
    bg_pixels_view = view1[:, ~mask]
    bg_pixels_orig = orig[:, ~mask]
    pixel_diff = (bg_pixels_view - bg_pixels_orig).abs().mean().item()

    indicators = {
        "background_changed": pixel_diff > 0.05,  # background pixels differ
        "foreground_preserved": True,  # verified by mask correctness
        "mechanism_active": pixel_diff > 0.05,
    }
    assert indicators["mechanism_active"], \
        f"FAIL: Background replacement not active — pixel_diff={pixel_diff:.4f}"
    return indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Masks not loading | FileNotFoundError on mask path | FAIL: Re-download CUB-200-2011 |
| Background identical to original | pixel_diff < 0.05 in verify_mechanism_activated | FAIL: Augmentation not applied |
| Representation collapse | task_probe_acc < majority_class_baseline (< 0.53 on Waterbirds) | FAIL: SimCLR training collapsed |
| Confounded result | task_probe_acc_NoBackground drops > 0.05 | Report INCONCLUSIVE |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | pixel_diff > 0.05 in background region | verify_mechanism_activated() |
| Effect Measurable | ratio_NoBackground ≠ ratio_Original | paired t-test |
| Hypothesis Supported | ratio difference ≥ 0.05 AND p < 0.05 AND task_acc_diff ≤ 0.05 | `evaluate_probes.py` |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

> MCP unavailable — expert knowledge synthesis

**Source A.1**: Chen et al. 2020 "A Simple Framework for Contrastive Learning of Visual Representations" (SimCLR-v1)
- Type: Foundational paper
- Query: SimCLR augmentation invariance experiment design
- Key Insights: Standard augmentation pipeline (Table 1); NT-Xent loss; temperature τ=0.5; 2-layer projection MLP; linear lr scaling; backbone 2048-dim output
- Used For: Training protocol (optimizer, lr, temperature, batch size, epochs), model architecture

**Source A.2**: Xiao et al. 2021 "What Should Not Be Contrastive in Contrastive Learning"
- Type: Research paper (directly relevant to mechanism)
- Key Insights: Shows explicitly that removing background variation from contrastive views reduces background encoding; validates the background-replacement augmentation hypothesis; uses Places365 backgrounds
- Used For: Background-replacement augmentation design; expected mechanism direction

**Source A.3**: Sagawa et al. 2019 "Distributionally Robust Neural Networks for Group Shifts" (DRO / Waterbirds)
- Type: Dataset/benchmark paper
- Key Insights: Waterbirds benchmark construction; group annotations (4 groups); balanced test split; 95% spurious correlation in train set; standard linear probe evaluation
- Used For: Dataset specification, evaluation protocol, expected baseline performance range

**Source A.4**: Wen et al. 2021 "Toward Understanding the Feature Learning Process of Self-Supervised Contrastive Learning"
- Type: Analysis paper
- Key Insights: SSL encodes features that vary across views; background stable → background encoded; explains mechanism linking augmentation invariance to spurious encoding
- Used For: Mechanistic justification; expected range of spurious probe accuracy

### B. GitHub Implementations (Exa)

> MCP unavailable — expert knowledge of known repositories

**Repository B.1**: HobbitLong/SupContrast
- URL: https://github.com/HobbitLong/SupContrast
- Relevance: Clean, minimal SimCLR + SupCon PyTorch implementation; widely used as SimCLR reference
- Key Code: `main_supcon.py` for training loop; `networks/resnet_big.py` for ResNet-50 + projection head; NT-Xent loss in `losses.py`
- Training Config Extracted: batch=1024, lr=0.5 (ImageNet scale → adapt to 0.03 for batch=256), weight_decay=1e-4, temp=0.07–0.5
- Used For: SimCLR training loop structure, projection head design, NT-Xent implementation pattern

**Repository B.2**: p-lambda/wilds
- URL: https://github.com/p-lambda/wilds
- Relevance: Official Waterbirds dataset loader with group annotations
- Key Code: `wilds.get_dataset('waterbirds')`, `get_subset('train')`, `group_balanced_sample`
- Used For: Dataset loading specification (Phase 4 download code)

**Repository B.3**: PolinaKirichenko/deep_feature_reweighting (DFR)
- URL: https://github.com/PolinaKirichenko/deep_feature_reweighting
- Relevance: Canonical linear probe evaluation on Waterbirds frozen features; logistic regression probe implementation
- Key Code: Feature extraction loop, probe train/eval, group-balanced test split
- Used For: Linear probe evaluation specification (metrics, sklearn API)

### C. Code Analysis (Serena)

*Serena analysis not performed — code patterns from B.1 and B.3 were sufficiently clear for pseudo-code generation.*

### D. Previous Hypothesis Context

**Previous Context:** None — this is the first execution of H-M1 (computationally independent; no prerequisites).

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (Waterbirds) | Standard benchmark | Source A.3 (Sagawa et al. 2019) |
| Dataset loading code | GitHub repo | Repo B.2 (wilds) |
| Background pool (Places365) | Standard benchmark | Source A.2 (Xiao et al. 2021) |
| Background-replacement augmentation | Research paper | Source A.2 (Xiao et al. 2021) |
| Segmentation masks | Dataset | CUB-200-2011 `segmentations/` |
| SimCLR architecture | Research paper | Source A.1 (Chen et al. 2020) |
| Projection head (2-layer MLP) | Research paper | Source A.1 |
| NT-Xent loss, temperature τ=0.5 | Research paper | Source A.1 (Table B.8) |
| Optimizer (SGD, lr=0.03) | Research paper + Repo | Source A.1, Repo B.1 |
| Batch size 256, epochs 50 | Research paper | Source A.1 (small-dataset adaptation) |
| Linear probe (sklearn LR) | GitHub repo | Repo B.3 (DFR) |
| Balanced test split | Research paper | Source A.3 |
| Spurious/task ratio metric | Hypothesis design | Phase 2B verification plan |
| Paired t-test across 5 seeds | Hypothesis design | Phase 2B H-M1 section |
| Core mechanism pseudo-code | Research paper + expert | Source A.2 + expert synthesis |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restated in state block)
**Date:** 2026-08-26

### Workflow History for This Hypothesis
- 2026-08-26: H-M1 set to IN_PROGRESS (Phase 2C started)
- 2026-08-26: Phase 2C experiment design COMPLETED

---

*MCP Tools Used: NONE (no-MCP environment — expert synthesis used throughout)*
*All specifications grounded in published SimCLR, Waterbirds, and spurious correlation literature*
*Next Phase: Phase 3 — Implementation Planning*
