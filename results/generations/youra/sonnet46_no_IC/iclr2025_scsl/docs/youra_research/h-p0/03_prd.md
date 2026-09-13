# Product Requirements Document: H-P0
## DFR Backbone Identity Sanity Check — PoC Existence Experiment

**stepsCompleted:** [1, 2, 3, 4, 5, 6, 7]
**hypothesis_id:** h-p0
**hypothesis_type:** EXISTENCE
**tier:** LIGHT
**generated_at:** 2026-08-05T00:00:00Z
**source:** 02c_experiment_brief.md

---

## 1. Executive Summary

Implement a minimal PoC experiment to verify that DFR-trained and ERM-trained ResNet-50 layer4 features are numerically identical (mean cosine similarity ≥ 0.9999) for all 3 seed pairs from the `izmailovpavel/spurious_feature_learning` checkpoints on 50 fixed Waterbirds WILDS test images.

This sanity check confirms the DFR protocol's backbone freezing claim: DFR retrains only the classification head, so DFR backbone weights must be identical to the ERM backbone weights at the same seed.

**Gate:** MUST_WORK — mean cosine similarity ≥ 0.9999 AND variance < 1e-6 for all 3 seed pairs. Failure requires treating DFR as a 4th independent backbone condition in H-M3.

---

## 2. Problem Statement

The BSER research pipeline assumes that DFR and ERM backbones at matching seeds are numerically identical (DFR only retrains the classification head). If this assumption is violated, the downstream hypothesis chain (H-M1, H-M2, H-M3, H-P2) must be redesigned.

H-P0 verifies this assumption by directly comparing layer4 feature vectors extracted from DFR and ERM checkpoints at each seed using cosine similarity. The expected result is near-perfect identity (cosine sim ≈ 1.0000), as DFR explicitly freezes the backbone per the Kirichenko 2022 / Izmailov 2022 protocol.

---

## 3. Objectives and Success Criteria

### Primary Objective
Confirm that DFR and ERM ResNet-50 layer4 features (D=2048) are numerically identical across all 3 seed pairs on 50 fixed Waterbirds test images.

### Success Criteria (GATE: MUST_WORK)

| Metric | Target | Gate |
|--------|--------|------|
| Mean cosine similarity (seed 1) | ≥ 0.9999 | PASS/FAIL |
| Mean cosine similarity (seed 2) | ≥ 0.9999 | PASS/FAIL |
| Mean cosine similarity (seed 3) | ≥ 0.9999 | PASS/FAIL |
| Variance across 50 samples (all seeds) | < 1e-6 | PASS/FAIL |

**Combined Gate:** ALL seed pairs must satisfy BOTH conditions (mean sim AND variance threshold).

### Secondary Criteria (Non-blocking)
- ERM baseline probe accuracy > 0.6 on background attribute (A2 validation)
- Feature norms non-zero (no degenerate outputs)
- Runtime < 5 minutes on single GPU

### Failure Contingency
If mean cosine similarity < 0.999: DFR backbone differs from ERM → redesign H-M3 to include DFR as 4th backbone condition alongside ERM, SAM, GroupDRO.

---

## 4. Data Specification

### Primary Dataset

**Dataset:** Waterbirds WILDS v1.0
**Source:** WILDS benchmark (Sagawa et al. 2019; Koh et al. 2021)
**Download:** Pre-cached at `/home/PrayPrey/.wilds_cache/waterbirds_v1.0` (do NOT re-download)
**Manual download required:** NO — cache already present
**Loading library:** `wilds` package

```python
from wilds import get_dataset
dataset = get_dataset(dataset='waterbirds', download=False,
                      root_dir='/home/PrayPrey/.wilds_cache')
test_data = dataset.get_subset('test', transform=transform)
# test split: 5,794 images total
# group_array: metadata_array[:, 0] — 0=land-background, 1=water-background
```

**Subset for H-P0:** 50 fixed test images (first 50 from test split with `torch.manual_seed(42)`)
- Note: H-P0 is a sanity check; 50 images is statistically sufficient for cosine similarity verification
- All 50 from test split (indices 0–49 after seeded shuffle)

### Preprocessing
Standard ImageNet normalization (identical to izmailovpavel/spurious_feature_learning):
```python
transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
```

---

## 5. Model Specification

### Checkpoints (6 total for H-P0: 3 ERM + 3 DFR seeds)

**Source:** izmailovpavel/spurious_feature_learning (NeurIPS 2022)
**Access:** HuggingFace Hub `izmailovpavel/spurious_feature_learning`
**Architecture:** ResNet-50, ImageNet pretrained, finetuned on Waterbirds (fully trained, 100 epochs)
**Target layer:** `model.layer4` → AdaptiveAvgPool2d(1,1) → flatten → D=2048

**Checkpoint pairs (seed-matched):**

| Pair | ERM Checkpoint | DFR Checkpoint |
|------|---------------|----------------|
| Seed 1 | `erm_seed1/final_checkpoint.pt` | `dfr_seed1/final_checkpoint.pt` |
| Seed 2 | `erm_seed2/final_checkpoint.pt` | `dfr_seed2/final_checkpoint.pt` |
| Seed 3 | `erm_seed3/final_checkpoint.pt` | `dfr_seed3/final_checkpoint.pt` |

**Loading pattern:**
```python
from models import imagenet_resnet50_pretrained  # from izmailovpavel repo
import torch

def load_checkpoint(ckpt_path, n_classes=2):
    model = imagenet_resnet50_pretrained(n_classes)
    ckpt_dict = torch.load(ckpt_path, map_location='cpu')
    model.load_state_dict(ckpt_dict)
    model.eval()
    return model
```

**No training performed** — inference-only on pre-trained checkpoints.

---

## 6. Functional Requirements

### FR-1: Checkpoint Download/Access
- Download or verify 6 checkpoints from HuggingFace Hub (3 ERM + 3 DFR seeds)
- Load each using `imagenet_resnet50_pretrained(n_classes=2).load_state_dict(ckpt_dict)`
- Verify `model.layer4` exists (ResNet-50 architecture confirmation)

### FR-2: Test Image Selection
- Load Waterbirds WILDS test split (5,794 images)
- Set `torch.manual_seed(42)`, select first 50 indices after shuffle (or indices 0–49 directly)
- Store fixed 50-image batch for consistent comparison across all 6 checkpoints

### FR-3: Layer4 Feature Extraction
- For each checkpoint: forward pass 50 images through backbone to layer4
- Apply AdaptiveAvgPool2d(1,1) → flatten → D=2048 features per image
- Use forward hook on `model.layer4` to capture [B, 2048, 7, 7] output

```python
import torch.nn as nn

def extract_layer4_features(model, images, device='cuda'):
    model.eval()
    features = []
    def hook_fn(module, input, output):
        features.append(output.detach())
    handle = model.layer4.register_forward_hook(hook_fn)
    with torch.no_grad():
        _ = model(images.to(device))
    handle.remove()
    feat = features[0]  # [B, 2048, 7, 7]
    pool = nn.AdaptiveAvgPool2d((1, 1))
    feat = pool(feat).flatten(1)  # [B, 2048]
    return feat
```

### FR-4: Cosine Similarity Computation
- For each seed pair: compute per-sample cosine similarity between ERM and DFR features
- Report mean and variance of the 50 per-sample similarities

```python
import torch.nn.functional as F

def compute_pairwise_cosine_similarity(feat1, feat2):
    sim = F.cosine_similarity(feat1, feat2, dim=1)  # (N,)
    return sim.mean().item(), sim.var().item(), sim
```

### FR-5: Gate Evaluation
- Check: mean_sim ≥ 0.9999 AND variance < 1e-6 for ALL 3 seed pairs
- Report PASS or FAIL per seed pair and overall

```python
gate_passed = all(
    r['mean_cosine_sim'] >= 0.9999 and r['variance'] < 1e-6
    for r in results.values()
)
print(f"H-P0 Gate: {'PASS' if gate_passed else 'FAIL'}")
```

### FR-6: Secondary Validation — ERM Probe Accuracy
- Use ERM seed1 features (50 images) to train sklearn logistic regression on background label
- Report probe accuracy > 0.6 as sanity check that features are informative

### FR-7: Results Logging and Storage
- Log per-seed: `Seed {seed}: mean_cosine_sim={val:.6f}, variance={var:.2e}`
- Save results to `h-p0/results.json`
- Save validation report to `h-p0/04_validation.md`

### FR-8: Visualization
- **Required:** Bar chart of mean cosine similarity per seed pair (3 bars) with 0.9999 threshold line
- **Optional:** Per-sample cosine similarity histogram (50 samples, per seed) — spike at ~1.0 if identical
- **Optional:** 2D PCA projection of ERM and DFR features (one seed) — visual overlap confirmation
- Save figures to `h-p0/figures/`

---

## 7. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed image selection: `torch.manual_seed(42)` before selecting test images
- Deterministic checkpoint loading (map_location='cpu', no random ops)

### NFR-2: Resource Constraints
- GPU memory: minimal (~0.5 GB for 50-image batch × ResNet-50)
- Runtime: < 5 minutes total (6 forward passes × 50 images)
- No training, no backward pass, no optimizer

### NFR-3: PyTorch Version
- PyTorch ≥ 1.8 (standard; no torch.func needed — only F.cosine_similarity)
- wilds package for dataset loading
- sklearn for secondary probe validation

### NFR-4: No Training
- Read-only experiment on pre-trained checkpoints; no weight updates

---

## 8. Dependencies

### 8.1 Python Packages

```
torch>=1.8.0
torchvision
wilds
numpy
matplotlib
scikit-learn
huggingface_hub
```

### 8.2 External Repositories (Reference Only)

| Repository | URL | Purpose |
|------------|-----|---------|
| izmailovpavel/spurious_feature_learning | HuggingFace Hub | Source of 6 checkpoints (ERM+DFR × 3 seeds) |
| PolinaKirichenko/deep_feature_reweighting | GitHub | DFR protocol reference |
| p-lambda/wilds | GitHub | Dataset loading library |

### 8.3 Pre-conditions

- `/home/PrayPrey/.wilds_cache/waterbirds_v1.0` exists and is valid (confirmed in Phase 2B)
- HuggingFace access for `izmailovpavel/spurious_feature_learning` (or local checkpoint cache)
- CUDA GPU available (CPU fallback acceptable for 50-image batch)
- PyTorch ≥ 1.8 installed

---

## 9. Evaluation Criteria

### Primary Metrics (Gate)

| Metric | Definition | Target | GATE |
|--------|-----------|--------|------|
| mean_cos_sim_seed1 | F.cosine_similarity(ERM_s1, DFR_s1).mean() | ≥ 0.9999 | MUST_WORK |
| mean_cos_sim_seed2 | F.cosine_similarity(ERM_s2, DFR_s2).mean() | ≥ 0.9999 | MUST_WORK |
| mean_cos_sim_seed3 | F.cosine_similarity(ERM_s3, DFR_s3).mean() | ≥ 0.9999 | MUST_WORK |
| variance_seed{1,2,3} | per_sample_sim.var() | < 1e-6 | MUST_WORK |

### Secondary Metrics (Non-blocking)

| Metric | Expected |
|--------|---------|
| ERM background probe accuracy | > 0.6 |
| All cosine similarities | ∈ [0.9999, 1.0001] (numerical identity) |
| Feature norms | Non-zero for all 50 images |

---

## 10. Out of Scope

- Model training or fine-tuning (pre-trained checkpoints only)
- SAM or GroupDRO backbone comparison (tested in H-M3, not H-P0)
- Full test set evaluation (50 images sufficient for identity check)
- Statistical hypothesis tests (cosine similarity is deterministic identity check)
- Comparison to baseline methods (Phase 5 scope)
- Any checkpoint sources other than izmailovpavel/spurious_feature_learning

---

## 11. Implementation Notes

- **PoC scope:** Minimal — 6 checkpoints × 50 images × forward pass + cosine similarity
- **No training loop:** Pure inference on frozen checkpoints
- **Memory management:** Load one checkpoint at a time; delete after feature extraction
- **Checkpoint identity:** DFR `final_checkpoint.pt` contains the ERM backbone with DFR-retrained fc head; the backbone layers are numerically identical to the ERM checkpoint at the same seed
- **Threshold rationale:** 0.9999 threshold (conservative) accounts for float32 precision in checkpoint save/load; true identity would yield sim ≈ 1.0000 ± 1e-7

---

*Generated from: h-p0/02c_experiment_brief.md*
*Pipeline position: Phase 3 (Implementation Planning)*
*Gate: MUST_WORK — mean cosine similarity ≥ 0.9999 AND variance < 1e-6 for all 3 seed pairs*
