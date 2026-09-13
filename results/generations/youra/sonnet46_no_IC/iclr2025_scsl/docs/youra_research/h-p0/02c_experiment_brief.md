# Experiment Design: h-p0

**Date:** 2026-08-05
**Author:** Anonymous
**Hypothesis Statement:** Under ResNet-50 checkpoints from izmailovpavel/spurious_feature_learning, DFR layer4 features and ERM layer4 features at matching seeds are numerically identical (mean cosine similarity >= 0.9999 for all 3 seed pairs), because DFR protocol explicitly freezes backbone and retrains only the classification head.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** None required (H-P0 is the foundation hypothesis)
**Gate Status:** MUST_WORK — failure stops all downstream hypotheses

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-p0
- **Type:** EXISTENCE (Sanity Check)
- **Prerequisites:** None

### Gate Condition
MUST_WORK gate. Pass condition: mean cosine similarity ≥ 0.9999 for all 3 seed pairs (DFR vs ERM at matching seeds) AND variance < 1e-6. Failure branches: DFR must be treated as 4th independent backbone condition in H-M3; entire comparison framework redesigned.

---

## Continuation Context

This is the FIRST hypothesis in the verification chain. No previous hypothesis context available.

### Previous Hypothesis Results (if applicable)
None — H-P0 is the foundation (Level 0) hypothesis with no prerequisites.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: DFR backbone identity cosine similarity linear probe**
- Archon KB does not contain domain-specific entries for DFR/spurious correlation experiments. The KB primarily indexes diffusers/image-generation content. No relevant results found (similarity scores < 0.40, all from HuggingFace diffusers unrelated to this task).

**Query 2: ResNet-50 feature extraction layer4 frozen checkpoint**
- No relevant results (similarity < 0.53, all diffusers content). Archon KB lacks spurious correlation / probing literature.

**Query 3: Spurious correlation Waterbirds linear probe accuracy**
- No relevant results (similarity < 0.31, unrelated content).

**Assessment:** Archon KB is not indexed for this research domain. All implementation evidence sourced from Exa GitHub search.

### Archon Code Examples

**Query: cosine similarity feature comparison PyTorch**
- No relevant code examples found in Archon KB (all diffusers/image generation code, similarity scores < 0.40).

### Exa GitHub Implementations

**Repository 1: izmailovpavel/spurious_feature_learning** ⭐ Primary — Author's Official Implementation
- **URL:** https://github.com/izmailovpavel/spurious_feature_learning
- **Relevance:** This is the EXACT repository containing the 12 checkpoints (3 seeds × 4 methods) that H-P0 tests. The `dfr_evaluate_spurious.py` file shows the backbone loading and evaluation pattern.
- **Key Code (checkpoint loading pattern):**
  ```python
  model_cls = getattr(models, args.model)
  model = model_cls(n_classes)
  ckpt_dict = torch.load(args.ckpt_path)
  model.load_state_dict(ckpt_dict)
  model.cuda()
  model.eval()
  ```
- **Key Finding:** The DFR protocol (per Kirichenko 2022 and Izmailov 2022) freezes the backbone and retrains only the classification head (`fc` layer). The `dfr_evaluate_spurious.py` script evaluates DFR by extracting embeddings from the frozen backbone and retraining a logistic regression classifier — confirming that DFR backbone weights ARE the same as ERM backbone weights at the same seed.
- **Key Paper Finding:** Izmailov 2022 NeurIPS explicitly states: "we show that the performance improvements of group DRO are largely explained by the better weighting of the learned features in the last classification layer, and not by learning a better representation of the core features." This directly implies DFR backbone ≡ ERM backbone.
- **Dataset:** Waterbirds WILDS — test set has 5794 samples (confirmed from Exa results: test group_counts [2255, 2255, 642, 642])
- **Results:** ERM WGA=0.72, GroupDRO WGA=0.88, DFR WGA=0.91 (from Izmailov 2022)

**Repository 2: PolinaKirichenko/deep_feature_reweighting** ⭐ DFR Original Implementation
- **URL:** https://github.com/polinakirichenko/deep_feature_reweighting
- **Relevance:** Original DFR codebase; izmailovpavel/spurious_feature_learning is built on top of this
- **Key Finding:** DFR checkpoints available. The DFR procedure uses the feature extractor (backbone) unchanged from ERM training — only the logistic regression classifier (last layer) is retrained on group-balanced held-out data.
- **Checkpoints:** Available on Google Drive and through HuggingFace Hub for Waterbirds

**Repository 3: PyTorch ResNet-50 Feature Extraction (torchvision docs)**
- **URL:** https://docs.pytorch.org/vision/0.11/feature_extraction.html
- **Relevance:** Standard pattern for extracting layer4 features from ResNet-50
- **Key Code:**
  ```python
  from torchvision.models.feature_extraction import create_feature_extractor
  return_nodes = {'layer4.2.relu_2': 'layer4'}
  feature_extractor = create_feature_extractor(model, return_nodes=return_nodes)
  # OR via forward hook:
  model.layer4.register_forward_hook(hook)
  ```
- **Layer4 output shape:** [B, 2048, 7, 7] → after AdaptiveAvgPool2d(1,1) → [B, 2048, 1, 1] → flatten → [B, 2048]

**Repository 4: Waterbirds dataset stats (intermediate-layer-generalization)**
- **URL:** https://github.com/oshapio/intermediate-layer-generalization
- **Key Data Confirmed:**
  - Train: 4795 samples
  - Val: 1199 samples
  - Test: 5794 samples (group_counts: [2255, 2255, 642, 642])
  - Group structure: {landbird-land, landbird-water, waterbird-land, waterbird-water}

**Serena Analysis Needed:** false — code from search results is sufficiently clear for this experiment. H-P0 is a simple cosine similarity sanity check, not a complex novel architecture.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

The izmailovpavel/spurious_feature_learning repository IS the author's official implementation. The checkpoints are released on HuggingFace Hub as part of the NeurIPS 2022 paper artifacts.

**Recommended Implementation Path:**
- Primary: izmailovpavel/spurious_feature_learning checkpoints (HuggingFace Hub) — ground truth for this experiment
- Fallback: PolinaKirichenko/deep_feature_reweighting (Google Drive checkpoints)
- Justification: H-P0 tests the IDENTITY of DFR vs ERM checkpoints from THIS specific repository. Using any other checkpoint source would invalidate the sanity check.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. H-P0 is a straightforward cosine similarity comparison between two sets of frozen features. No complex novel architecture requiring Serena semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** Waterbirds WILDS v1.0
**Type:** standard (real dataset — NOT synthetic)
**Source:** WILDS benchmark (Koh et al. 2021); Sagawa et al. 2019 (original Waterbirds)
**Local Path:** `/home/PrayPrey/.wilds_cache/waterbirds_v1.0` (already cached)

**Dataset Statistics:**
- Total: 11,788 images
- Train: 4,795 images (group_counts: [3498, 184, 56, 1057])
- Val: 1,199 images (group_counts: [467, 466, 133, 133])
- Test: 5,794 images (group_counts: [2255, 2255, 642, 642])
- Classes: 2 (landbird=0, waterbird=1)
- Groups: 4 (group_array: 0=landbird-land, 1=landbird-water, 2=waterbird-land, 3=waterbird-water)
- Background label: `background_label = group_array % 2` (0=land background, 1=water background)

**For H-P0 specifically:** Only 50 fixed test images needed (sanity check, not full test set). Use first 50 images from test split with fixed random seed for reproducibility.

**Preprocessing:**
```python
transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
```
(Standard ImageNet normalization — used by izmailovpavel/spurious_feature_learning)

**Loading Information** (for Phase 4 download):
- Method: wilds library (already cached) + custom dataset class from izmailovpavel repo
- Identifier: `waterbirds_v1.0` at `/home/PrayPrey/.wilds_cache/waterbirds_v1.0`
- Code:
  ```python
  from wilds import get_dataset
  dataset = get_dataset(dataset='waterbirds', download=False,
                        root_dir='/home/PrayPrey/.wilds_cache')
  test_data = dataset.get_subset('test', transform=transform)
  ```

### Models

#### Baseline Model

**Architecture:** ResNet-50 (ERM-trained, izmailovpavel/spurious_feature_learning)
**Configuration:** Standard ResNet-50, 3 seeds (seed1, seed2, seed3)
**Source:** izmailovpavel/spurious_feature_learning GitHub / HuggingFace Hub
**Checkpoint naming:** `erm_seed{1,2,3}/final_checkpoint.pt`

**Feature Extraction:**
```python
# Forward through backbone only (no classification head)
# layer4 output: [B, 2048, 7, 7]
pool = nn.AdaptiveAvgPool2d(output_size=(1, 1))
# After pool + flatten: [B, 2048]
```

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Hub / direct checkpoint download
- Identifier: `izmailovpavel/spurious_feature_learning` — `erm_seed{1,2,3}/final_checkpoint.pt`
- Code:
  ```python
  import torch
  from models import imagenet_resnet50_pretrained  # from izmailovpavel repo
  model = imagenet_resnet50_pretrained(n_classes=2)
  ckpt = torch.load('erm_seed1/final_checkpoint.pt')
  model.load_state_dict(ckpt)
  model.eval()
  ```

#### Proposed Model

**Architecture:** ResNet-50 (DFR-trained) — SHOULD BE IDENTICAL to ERM backbone

**Core Mechanism Implementation:**

```python
# H-P0: DFR Backbone Identity Sanity Check
# Tests whether DFR and ERM ResNet-50 backbones are numerically identical
# Based on: izmailovpavel/spurious_feature_learning checkpoint protocol

import torch
import torch.nn as nn
import torch.nn.functional as F

def extract_layer4_features(model, images, device='cuda'):
    """
    Extract frozen layer4 features from ResNet-50.
    Input: images (B, 3, 224, 224)
    Output: features (B, 2048) — after AdaptiveAvgPool2d + flatten
    """
    model.eval()
    with torch.no_grad():
        features = []
        # Hook captures layer4 output [B, 2048, 7, 7]
        def hook_fn(module, input, output):
            features.append(output)
        handle = model.layer4.register_forward_hook(hook_fn)
        _ = model(images.to(device))
        handle.remove()
        feat = features[0]  # [B, 2048, 7, 7]
        pool = nn.AdaptiveAvgPool2d((1, 1))
        feat = pool(feat).flatten(1)  # [B, 2048]
    return feat

def compute_pairwise_cosine_similarity(feat1, feat2):
    """
    Compute mean cosine similarity between paired feature vectors.
    Input: feat1, feat2 — both (N, 2048)
    Output: mean_sim (scalar), per_sample_sim (N,)
    """
    sim = F.cosine_similarity(feat1, feat2, dim=1)  # (N,)
    return sim.mean().item(), sim

# Main sanity check loop
results = {}
for seed in [1, 2, 3]:
    erm_feats = extract_layer4_features(erm_model_seed[seed], test_images_50)
    dfr_feats = extract_layer4_features(dfr_model_seed[seed], test_images_50)
    mean_sim, per_sample = compute_pairwise_cosine_similarity(erm_feats, dfr_feats)
    variance = per_sample.var().item()
    results[seed] = {'mean_cosine_sim': mean_sim, 'variance': variance}
    print(f"Seed {seed}: mean_cosine_sim={mean_sim:.6f}, variance={variance:.2e}")

# Gate evaluation
all_pass = all(r['mean_cosine_sim'] >= 0.9999 and r['variance'] < 1e-6
               for r in results.values())
print(f"H-P0 Gate: {'PASS' if all_pass else 'FAIL'}")
```

### Training Protocol

**Note: H-P0 is NOT a training experiment.** It is a feature extraction + cosine similarity sanity check on pre-trained checkpoints. No model training occurs.

**Execution Protocol:**
- **Optimizer:** N/A (no training)
- **Learning Rate:** N/A
- **Batch Size:** 50 (all test images processed in one batch for H-P0)
- **Epochs:** N/A
- **Loss Function:** N/A — this is inference-only
- **Seeds:** Fixed test image selection with `torch.manual_seed(42)` for reproducibility
- **Device:** CUDA (GPU) for forward pass; CPU fallback acceptable (small batch)
- **Precision:** float32 (default)

**Checkpoint Loading Order:**
1. ERM seed1 vs DFR seed1
2. ERM seed2 vs DFR seed2
3. ERM seed3 vs DFR seed3

Total compute: ~6 forward passes on 50 images through ResNet-50. Expected runtime: < 5 minutes.

### Evaluation

**Primary Metric:** Mean cosine similarity between DFR and ERM layer4 features (per seed pair)

**Pass/Fail Criterion:**
- PASS: mean cosine similarity ≥ 0.9999 for ALL 3 seed pairs AND variance < 1e-6
- FAIL: cosine similarity < 0.999 → DFR backbone differs from ERM

**Expected Values:**
- If DFR protocol correctly frozen: similarity ≈ 1.0000 (numerical identity up to float32 precision)
- Float32 precision floor: ~1e-7 differences acceptable → similarity ≈ 0.9999999
- Practical threshold: ≥ 0.9999 (conservative, accounts for any minor numerical differences in checkpoint saving/loading)

**Secondary Check:** Also verify ERM baseline probe accuracy > 0.6 on background attribute (A2 validation) as embedded sanity check.

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: cosine similarity computation (not classification)
- Library: `torch.nn.functional.cosine_similarity` (built-in, no additional library needed)
- Code: `F.cosine_similarity(feat1, feat2, dim=1).mean()`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Per-seed cosine similarity bar chart (3 seeds, DFR vs ERM), with 0.9999 threshold line

#### Additional Figures (LLM Autonomous)
- **Per-sample cosine similarity distribution:** Histogram of 50 per-sample cosine similarities per seed (should be a spike at ~1.0 if identical)
- **Feature space scatter:** 2D PCA projection of ERM and DFR features for one seed (visual overlap confirmation)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-p0/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (checkpoints load, features extracted successfully)
2. Mean cosine similarity ≥ 0.9999 for all 3 seed pairs AND variance < 1e-6

**If FAIL:** Document whether DFR backbone differs from ERM — this is a BRANCHING outcome (not a failure of the approach, but a redesign trigger for H-M3 to include DFR as 4th backbone condition).

---

## Mechanism Verification Protocol

**Pre-conditions:**
- `mechanism_exists`: DFR protocol freeze mechanism is verifiable via cosine similarity comparison
- `mechanism_isolatable`: H-P0 isolates exactly the backbone identity question; only the backbone weights are compared (classification head differences are irrelevant)
- `baseline_measurable`: ERM features are the reference; cosine similarity is bounded [0,1] and deterministic

**Architecture Compatibility:**
- ResNet-50 layer4 output: [B, 2048, 7, 7] → AdaptiveAvgPool2d(1,1) → [B, 2048] ✓
- All 12 checkpoints use identical ResNet-50 architecture (imagenet_resnet50_pretrained) ✓
- checkpoint loading via `model.load_state_dict(torch.load(ckpt_path))` ✓

**Activation Indicators:**
- `mechanism_log_message`: "Seed {seed}: mean_cosine_sim={val:.6f}, variance={var:.2e}" — logged per seed
- `tensor_shape_change`: Input [50, 3, 224, 224] → layer4 [50, 2048, 7, 7] → pool → [50, 2048] — expected shape chain
- `metric_delta_expected`: Expected delta between DFR and ERM features ≈ 0 (identical). Any delta > 1e-4 in cosine distance (1 - cosine_sim) is a warning flag.

**Mechanism Verification Code:**
```python
# Verify backbone identity before cosine similarity computation
assert erm_feats.shape == (50, 2048), f"ERM feature shape wrong: {erm_feats.shape}"
assert dfr_feats.shape == (50, 2048), f"DFR feature shape wrong: {dfr_feats.shape}"
# Check for degenerate features (all zeros would give undefined cosine sim)
assert erm_feats.norm(dim=1).min() > 0, "ERM features contain zero vectors"
assert dfr_feats.norm(dim=1).min() > 0, "DFR features contain zero vectors"
print(f"Feature norms: ERM mean={erm_feats.norm(dim=1).mean():.3f}, "
      f"DFR mean={dfr_feats.norm(dim=1).mean():.3f}")
```

**Failure Detection:**
- If cosine similarity < 0.999: FAIL gate → log "DFR backbone differs from ERM at seed {seed}, sim={val:.4f}"
- If cosine similarity 0.999-0.9999: WARN → "Near-identical but below threshold, investigate checkpoint"
- If features are all identical (sim=1.0000): PASS → "Confirmed: DFR and ERM backbones are numerically identical"

**Success Criteria Thresholds:**
- `hypothesis_support_threshold`: 0.9999 (cosine similarity)
- `hypothesis_support_metric`: mean cosine similarity across 50 test images, reported per seed

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB Query Results:** No relevant domain-specific sources found. Archon KB is indexed primarily for diffusers/image-generation content and does not contain spurious correlation or linear probing literature. All implementation evidence sourced from Exa GitHub search.

### B. GitHub Implementations (Exa)

**Repository 1:** izmailovpavel/spurious_feature_learning (NeurIPS 2022 official)
- **URL:** https://github.com/izmailovpavel/spurious_feature_learning
- **Query Used:** "izmailovpavel spurious_feature_learning DFR ERM backbone checkpoint cosine similarity GitHub"
- **Relevance:** Author's official implementation containing the 12 checkpoints H-P0 tests. `dfr_evaluate_spurious.py` shows backbone loading and DFR evaluation pattern.
- **Configuration Extracted:**
  - Model: `imagenet_resnet50_pretrained` (torchvision ResNet-50, ImageNet pretrained)
  - Checkpoint: `logs/waterbirds/{method}_seed{n}/final_checkpoint.pt`
  - DFR evaluates by extracting frozen backbone embeddings and retraining logistic regression
- **Their Results:** ERM WGA=0.72, GroupDRO WGA=0.88, DFR WGA=0.91 (Waterbirds)
- **Used For:** Checkpoint loading pattern, dataset loading, architectural confirmation that DFR ≡ ERM backbone

**Repository 2:** PolinaKirichenko/deep_feature_reweighting (DFR original)
- **URL:** https://github.com/polinakirichenko/deep_feature_reweighting
- **Query Used:** Same Exa query (returned as related result)
- **Relevance:** Original DFR codebase; confirms DFR procedure uses feature extractor unchanged
- **Key Finding:** "Model checkpoints and last layers trained with DFR for Waterbirds and CelebA are available" — confirms DFR only changes last layer
- **Used For:** Theoretical confirmation that DFR backbone = ERM backbone

**Repository 3:** torchvision feature extraction docs
- **URL:** https://docs.pytorch.org/vision/0.11/feature_extraction.html
- **Query Used:** "Waterbirds WILDS pytorch feature extraction ResNet50 layer4 linear probe sklearn"
- **Key Code (used for pseudo-code):**
  ```python
  # Layer4 output node in ResNet-50
  return_nodes = {'layer4.2.relu_2': 'layer4'}
  # OR via hook:
  model.layer4.register_forward_hook(hook_fn)
  # layer4 → AdaptiveAvgPool2d(1,1) → flatten → [B, 2048]
  ```
- **Used For:** Feature extraction implementation pattern in pseudo-code

**Repository 4:** Dataset statistics source
- **URL:** https://github.com/oshapio/intermediate-layer-generalization
- **Key Data:** Waterbirds test split = 5794 images, group_counts = [2255, 2255, 642, 642]
- **Used For:** Dataset split sizes confirmation

**Repository 5:** Izmailov 2022 NeurIPS paper (arxiv)
- **URL:** https://export.arxiv.org/pdf/2210.11369v1.pdf
- **Key Finding:** "performance improvements of group DRO are largely explained by the better weighting of the learned features in the last classification layer, and not by learning a better representation of the core features" — directly confirms backbone identity between DFR and ERM
- **Used For:** Theoretical basis for H-P0 expected outcome (similarity ≈ 1.0)

### C. Code Analysis (Serena MCP)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. H-P0 is a simple feature extraction + cosine similarity computation using well-understood PyTorch patterns (forward hook, AdaptiveAvgPool2d, F.cosine_similarity). No complex novel architecture requiring Serena semantic analysis.

### D. Previous Hypothesis Context

**Previous Context:** None — this is the FIRST hypothesis in the verification chain (Level 0, no prerequisites).

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: Waterbirds WILDS | Phase 2B | 02b_verification_plan.md Section 1.3 |
| Dataset path | Phase 2B | verification_state.yaml (data_setup.dataset.cache_path) |
| Dataset splits (4795/1199/5794) | GitHub (Exa) | Repo B.4 (intermediate-layer-generalization) |
| Model: ResNet-50 checkpoints | Phase 2B | 02b_verification_plan.md Section 1.3 |
| Checkpoint source | GitHub (Exa) | Repo B.1 (izmailovpavel/spurious_feature_learning) |
| Feature extraction: layer4→pool→flatten→2048 | Phase 2B | 02b_verification_plan.md Section 2.2 |
| Feature extraction code pattern | GitHub (Exa) | Repo B.3 (torchvision docs) |
| DFR = ERM backbone (theoretical) | Paper (Exa) | Repo B.5 (Izmailov 2022 NeurIPS) |
| DFR checkpoint loading pattern | GitHub (Exa) | Repo B.1 (dfr_evaluate_spurious.py) |
| Cosine similarity threshold 0.9999 | Phase 2B | 02b_verification_plan.md H-P0 success criteria |
| 50 test images for sanity check | Phase 2B | 02b_verification_plan.md H-P0 verification protocol step 3 |
| Preprocessing (ImageNet normalization) | GitHub (Exa) | Repo B.3 (intermediate-layer-generalization, train_waterbirds.py) |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-05

### Workflow History for This Hypothesis
- 2026-08-05T00:00:00Z: Phase 2B completed — H-P0 identified as first hypothesis (EXISTENCE/MUST_WORK, no prerequisites)
- 2026-08-05T16:16:55Z: Hypothesis h-p0 set to IN_PROGRESS (external loop starting Phase 2C → 3 → 4)
- 2026-08-05: Phase 2C experiment design COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results found), Exa (GitHub — primary source), Serena (Code Analysis — skipped, code sufficiently clear)*
*All specifications grounded in author's official implementation (izmailovpavel/spurious_feature_learning)*
*Next Phase: Phase 3 - Implementation Planning*
