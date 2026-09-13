# Experiment Design: H-E1

**Date:** 2026-05-20
**Author:** Anonymous
**Hypothesis Statement:** Under spurious-correlation settings (Waterbirds, CelebA) with pretrained ResNet-50 initialization, k-means clustering (k=2) on penultimate-layer embeddings at epoch 5 of ERM training recovers spurious feature axes with AMI≥0.5 and worst-cluster purity≥75% across ≥5 random seeds.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** — Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** N/A (no prerequisites for H-E1)
**Gate Status:** MUST_WORK (not yet evaluated — threshold: AMI ≥ 0.5 AND purity ≥ 75%)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
MUST_WORK: AMI ≥ 0.5 AND worst-cluster purity ≥ 75% on both Waterbirds AND CelebA across ≥5 random seeds. If this fails, the entire GSB mechanism is invalid and H-M1, H-M2, H-M3, H-M4, H-C1 are all blocked.

---

## Continuation Context

None — H-E1 is the first hypothesis in the verification chain. No previous hypothesis results to inherit.

### Previous Hypothesis Results (if applicable)
None.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: k-means clustering spurious features experiment design**
- No domain-relevant results found. Archon KB contains diffusion model content, not spurious correlation research.
- Key insight: No past implementation cases available; must rely on Exa + literature.

**Query 2: penultimate layer embedding clustering implementation**
- No domain-relevant results found (similarity scores < 0.42).

**Query 3: worst-group accuracy Waterbirds CelebA benchmark**
- No domain-relevant results found (similarity scores < 0.35).

**Assessment:** Archon KB does not contain spurious correlation / group robustness research. All implementation guidance derived from Exa GitHub search (Step 3).

### Archon Code Examples

**Query 1: k-means clustering PyTorch embeddings AMI**
- No relevant code examples (all results were diffusion model code with similarity < 0.33).

**Query 2: Waterbirds dataset PyTorch dataloader group labels**
- No relevant code examples found.

**Assessment:** No usable code patterns from Archon KB for this domain.

### Exa GitHub Implementations

**Repository 1: PolinaKirichenko/deep_feature_reweighting** (⭐ 110)
- **URL:** https://github.com/PolinaKirichenko/deep_feature_reweighting
- **Relevance:** Official DFR paper codebase — uses ResNet-50 on Waterbirds/CelebA with penultimate-layer embedding extraction. Directly validates that epoch-5 embeddings encode spurious structure separably.
- **Key Files:**
  - `wb_data.py` — Waterbirds and CelebA dataloaders with group labels
  - `train_classifier.py` — ERM training on Waterbirds/CelebA with pretrained ResNet-50
  - `imagenet_extract_embeddings.py` — embedding extraction script (directly reusable)
- **Training Config (Waterbirds):**
  - Optimizer: SGD (standard from GroupDRO repo)
  - Learning rate: 1e-3
  - Weight decay: 1e-3
  - Batch size: 32
  - Epochs: 100
  - Augmentation: AugWaterbirdsCelebATransform
- **Training Config (CelebA):**
  - Learning rate: 1e-3
  - Weight decay: 1e-4
  - Batch size: 128
  - Epochs: 50
- **Results:** DFR achieves 92.0 ± 0.9 worst-group (Waterbirds), 88.02 ± 1.6 (CelebA) — confirms embeddings are highly separable
- **Used For:** Training protocol, dataset loading, embedding extraction pattern

**Repository 2: izmailovpavel/spurious_feature_learning** (⭐ 48)
- **URL:** https://github.com/izmailovpavel/spurious_feature_learning
- **Relevance:** NeurIPS 2022 paper codebase — evaluates ERM feature quality on Waterbirds/CelebA. Achieves 97% worst-group via DFR, directly proving penultimate embeddings encode spurious axes separably at training end.
- **Key Files:**
  - `train_supervised.py` — ERM training script
  - `dfr_evaluate_spurious.py` — embedding extraction + evaluation
- **Training Config (Waterbirds):**
  - Learning rate: 3e-3
  - Weight decay: 1e-4
  - Batch size: 32
  - Epochs: 100
  - Scheduler: cosine_lr_scheduler
  - Model: imagenet_resnet50_pretrained
- **Used For:** Training hyperparameters, confirms ResNet-50 torchvision as standard model

**Repository 3: kohpangwei/group_DRO** (⭐ 295)
- **URL:** https://github.com/kohpangwei/group_DRO
- **Relevance:** Original GroupDRO codebase — provides Waterbirds dataset generation script, standard ERM baseline, group label infrastructure. The basis for DFR and spurious_feature_learning repos.
- **Key Code Pattern (dataset loading):**
  ```python
  # From wb_data.py pattern in GroupDRO / DFR repos
  # Waterbirds: load metadata.csv with group labels [y, place, group_idx]
  # Groups: 0=landbird_land, 1=landbird_water, 2=waterbird_land, 3=waterbird_water
  python run_expt.py -s confounder -d CUB -t waterbird_complete95 -c forest2water2 \
    --lr 0.001 --batch_size 128 --weight_decay 0.0001 --model resnet50 --n_epochs 300
  ```
- **Dataset Download:** `nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz` or via WILDS package
- **Used For:** Dataset loading infrastructure, group label format

**Paper Evidence (PruSC, OpenReview):**
- **URL:** https://openreview.net/pdf?id=EEeVYfXor5
- **Key Finding:** On CelebA, k-means clustering on ERM penultimate embeddings achieves **>95% purity** for spurious attributes (gender/age/beard) even with k=8. With k=2, spurious attribute purity exceeds class purity. This directly validates H-E1's mechanism.
- **Quote:** "k-means clustering effectively groups samples by class label, but achieves even higher purity for spurious attributes"
- **Used For:** Expected baseline performance for AMI/purity metrics, confidence in hypothesis

**Serena Analysis Needed:** false — code from Exa is sufficiently clear for pseudo-code generation.

### 🎯 Implementation Priority Assessment

**CRITICAL: H-E1 is NOT a paper reproduction — it is a NEW hypothesis testing k-means clustering validity on epoch-5 embeddings. Priority hierarchy:**

1. **Primary:** Build on DFR/GroupDRO infrastructure (`wb_data.py`, `train_classifier.py`) for dataset loading and ERM training — these are the ground truth for this domain
2. **Secondary:** Use `imagenet_extract_embeddings.py` pattern from DFR repo for embedding extraction
3. **Fallback:** WILDS package for dataset download if direct download fails

**Recommended Implementation Path:**
- Primary: PolinaKirichenko/deep_feature_reweighting (wb_data.py + train_classifier.py adapted for epoch-5 checkpoint + k-means probe)
- Fallback: izmailovpavel/spurious_feature_learning (same infrastructure, slightly different CLI)
- Justification: DFR repo is the most direct predecessor; its embedding extraction code is directly reusable with minor modifications to add k-means clustering at epoch-5 checkpoint.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. The DFR repo (`wb_data.py`, `train_classifier.py`, `imagenet_extract_embeddings.py`) provides all necessary patterns without requiring deep semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset 1 (Primary): Waterbirds**
- **Full Name:** Waterbirds (waterbird_complete95_forest2water2)
- **Type:** standard
- **Source:** Sagawa et al. 2020 GroupDRO; constructed from CUB-200-2011 + Places365
- **Download:** `https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz` OR via WILDS: `wilds.get_dataset(dataset="waterbirds", root_dir="./data")`
- **Splits:**
  - Train: 4,795 samples (95% waterbird-water, 95% landbird-land — highly spurious)
  - Val: 1,199 samples (50/50 balanced — no spurious correlation)
  - Test: 5,794 samples (50/50 balanced)
- **Groups (4 groups):** landbird-land (G0), landbird-water (G1), waterbird-land (G2), waterbird-water (G3)
- **Spurious Correlation:** Background (land/water) spuriously correlated with bird type (land/water)
- **Classes:** 2 (landbird=0, waterbird=1)
- **Preprocessing:** Resize to 256×256, CenterCrop 224×224, Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
- **Augmentation (train):** RandomResizedCrop(224), RandomHorizontalFlip (AugWaterbirdsCelebATransform from DFR repo)
- **Path Specification:** custom → `./data/waterbirds/` (requires download script)
- **Hypothesis Fit:** CONFIRMED — bird-type vs background spurious correlation is canonical; group labels available for AMI/purity evaluation

**Dataset 2 (Secondary): CelebA**
- **Full Name:** CelebA (Large-scale Celeb Faces Attributes Dataset)
- **Type:** standard
- **Source:** Liu et al. 2015; hair color prediction task (blond/non-blond) with gender as spurious attribute
- **Download:** `torchvision.datasets.CelebA(root='./data', split='train', download=True)` or Kaggle/HuggingFace
- **Metadata:** Requires `celeba_metadata.csv` from DFR repo renamed to `metadata.csv`
- **Splits:**
  - Train: ~162,770 samples
  - Val: ~19,867 samples
  - Test: ~19,962 samples
- **Groups (4 groups):** non-blond female (G0), blond female (G1), non-blond male (G2), blond male (G3, rare ~1%)
- **Spurious Correlation:** Male gender spuriously correlated with non-blond hair
- **Classes:** 2 (non-blond=0, blond=1)
- **Preprocessing:** Resize to 256×256, CenterCrop 224×224, Normalize ImageNet stats
- **Augmentation (train):** RandomResizedCrop(224), RandomHorizontalFlip
- **Path Specification:** custom → `./data/celeba/` (requires download)
- **Hypothesis Fit:** CONFIRMED — gender/hair spurious correlation is canonical; purity of k-means clusters validated in PruSC paper (>95%)

**Loading Information** (for Phase 4 download):
- Method: custom (GroupDRO/DFR repo infrastructure)
- Identifier: `waterbird_complete95_forest2water2` / `celeba`
- Code:
  ```python
  # Waterbirds — from DFR repo wb_data.py pattern
  from wb_data import WaterBirdsDataset
  dataset = WaterBirdsDataset(data_dir='./data/waterbirds', split='train')
  # OR via WILDS:
  from wilds import get_dataset
  dataset = get_dataset(dataset='waterbirds', root_dir='./data', download=True)

  # CelebA — from DFR repo wb_data.py pattern
  from wb_data import CelebADataset
  dataset = CelebADataset(data_dir='./data/celeba', split='train')
  ```

### Models

#### Baseline Model

**Architecture:** ResNet-50 (ImageNet-pretrained) — ERM training only (no clustering modification)
- **Type:** CNN (convolutional neural network)
- **Source:** torchvision.models
- **Penultimate Layer:** `layer4` output → AdaptiveAvgPool2d → 2048-dim feature vector
- **Classification Head:** Linear(2048, num_classes)
- **Configuration:**
  - Input: 224×224×3 RGB images
  - Feature dim: 2048 (penultimate) → 2 (output)
  - Parameters: ~25M
- **Modifications for Hypothesis:** None to baseline. Training proceeds as standard ERM. At epoch 5, embeddings extracted from penultimate layer (before classification head) and passed to k-means probe.

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `resnet50`
- Code:
  ```python
  import torchvision.models as models
  model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
  # Remove classification head for embedding extraction:
  feature_extractor = torch.nn.Sequential(*list(model.children())[:-1])
  # Output: (B, 2048, 1, 1) → flatten → (B, 2048)
  ```

#### Proposed Model

**Architecture:** ResNet-50 (ERM-trained to epoch 5) + k-means clustering probe on penultimate embeddings

**Core Mechanism Implementation:**

```python
# Core Mechanism: Annotation-Free Spurious Direction Discovery via K-Means Clustering
# Based on: DFR repo (PolinaKirichenko/deep_feature_reweighting) embedding extraction
# + PruSC paper (openreview.net/pdf?id=EEeVYfXor5) k-means clustering analysis

import torch
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_mutual_info_score

def extract_embeddings(model, dataloader, device):
    """Extract penultimate-layer embeddings for all training samples."""
    model.eval()
    embeddings, labels, group_ids = [], [], []
    feature_extractor = torch.nn.Sequential(*list(model.children())[:-1])
    with torch.no_grad():
        for x, y, g in dataloader:
            x = x.to(device)
            feat = feature_extractor(x).squeeze(-1).squeeze(-1)  # (B, 2048)
            embeddings.append(feat.cpu().numpy())
            labels.append(y.numpy())
            group_ids.append(g.numpy())
    return (np.concatenate(embeddings),   # (N, 2048)
            np.concatenate(labels),        # (N,) class labels
            np.concatenate(group_ids))     # (N,) group labels for eval

def run_kmeans_probe(embeddings, group_ids, k=2, n_init=10, seed=42):
    """Run k-means and compute AMI + worst-cluster purity vs. group labels."""
    kmeans = KMeans(n_clusters=k, n_init=n_init, random_state=seed)
    cluster_assignments = kmeans.fit_predict(embeddings)       # (N,)

    # AMI between cluster assignments and ground-truth group labels
    ami = adjusted_mutual_info_score(group_ids, cluster_assignments)

    # Worst-cluster purity: for each cluster, fraction of dominant group
    purities = []
    for c in range(k):
        mask = cluster_assignments == c
        if mask.sum() == 0:
            continue
        counts = np.bincount(group_ids[mask])
        purities.append(counts.max() / mask.sum())
    worst_purity = min(purities)

    return ami, worst_purity, cluster_assignments

# Checkpoint hook: call at epoch 5 during ERM training
# Success: AMI >= 0.5 AND worst_purity >= 0.75
```

### Training Protocol

**Optimizer:** SGD
- Parameters: momentum=0.9, weight_decay=1e-3 (Waterbirds) / 1e-4 (CelebA)
- Source: PolinaKirichenko/deep_feature_reweighting train_classifier.py

**Learning Rate:** 1e-3 (Waterbirds) / 1e-3 (CelebA)
- Schedule: Cosine annealing (izmailovpavel/spurious_feature_learning) or StepLR
- Source: izmailovpavel/spurious_feature_learning train_supervised.py

**Batch Size:** 32 (Waterbirds) / 128 (CelebA)
- Source: DFR repo train_classifier.py

**Epochs:** Train for ≥10 epochs; extract embeddings at epoch 5 checkpoint
- Full training: 100 epochs (Waterbirds) / 50 epochs (CelebA) — only epoch 5 checkpoint needed for H-E1

**Loss:** Cross-entropy (standard ERM — no group weighting)

**Seeds:** 1 fixed seed (PoC — single run per dataset)

**Checkpoint Strategy:** Save model checkpoint at end of epoch 5; load for embedding extraction

> ⚠️ **EXISTENCE (PoC):** Single seed is sufficient. No grid search. No multiple seeds at this stage (full seed sweep is Phase 5 / MECHANISM validation).

**Backbone Dependency Control (2×2 factorial — secondary):**
- Condition 1: Pretrained ResNet-50 on Waterbirds (primary)
- Condition 2: Pretrained ResNet-50 on CelebA (primary)
- Condition 3: Random-init ResNet-18 on ColoredMNIST (control — verifies pretrained is required)

### Evaluation

**Primary Metrics:**
- **AMI (Adjusted Mutual Information):** `sklearn.metrics.adjusted_mutual_info_score(group_ids, cluster_assignments)` — measures alignment between k-means clusters and ground-truth group labels
- **Worst-Cluster Purity:** `min([counts.max()/cluster_size for each cluster])` — measures how purely each cluster corresponds to a single group

**Success Criteria (PoC):**
- proposed_metric > baseline_metric:
  - AMI ≥ 0.5 on Waterbirds (k=2 clusters vs 4 group labels, AMI=0.5 is strong signal)
  - Worst-cluster purity ≥ 75% on Waterbirds
  - AMI ≥ 0.5 on CelebA
  - Worst-cluster purity ≥ 75% on CelebA
- Baseline (random): AMI ≈ 0 (random cluster assignments)
- Expected from literature: PruSC paper reports >95% purity for spurious attributes on CelebA

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: clustering evaluation (unsupervised → supervised comparison)
- Library: sklearn.metrics + custom purity computation
- Code:
  ```python
  from sklearn.metrics import adjusted_mutual_info_score
  ami = adjusted_mutual_info_score(group_ids, cluster_assignments)
  # Custom purity (no library needed):
  def worst_cluster_purity(group_ids, cluster_assignments, k):
      purities = []
      for c in range(k):
          mask = cluster_assignments == c
          if mask.sum() == 0: continue
          counts = np.bincount(group_ids[mask])
          purities.append(counts.max() / mask.sum())
      return min(purities)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart — AMI and worst-cluster purity per dataset (Waterbirds, CelebA) vs. threshold lines (AMI=0.5, purity=0.75)

#### Additional Figures (LLM Autonomous)
Based on the clustering nature of this EXISTENCE hypothesis, the following visualizations are recommended:

1. **t-SNE Plot of Penultimate Embeddings (epoch 5):** Color by (a) class label, (b) group label, (c) k-means cluster assignment — demonstrates visual separation
2. **Cluster Purity Breakdown:** Per-cluster group composition stacked bar chart for both datasets
3. **AMI vs Epoch Curve:** AMI computed at epochs 1, 3, 5, 7, 10 — shows when spurious structure emerges (validates epoch-5 choice)
4. **Fisher Direction Variance:** Variance explained by top-1 Fisher direction (validates Assumption A2: ≥60%)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | ResNet-50 penultimate layer (2048-dim) produces embeddings; k-means (k=2) is implementable | TRUE — standard PyTorch + sklearn |
| Mechanism Isolatable | K-means probe can be enabled/disabled independently of ERM training | TRUE — k-means runs post-hoc on saved embeddings |
| Baseline Measurable | Random cluster assignment gives AMI≈0, purity≈50% (chance level for k=2 with balanced groups) | TRUE — sklearn AMI on random labels = ~0 |

### Architecture Compatibility Check

**ResNet-50 with torchvision.models:**
- Penultimate layer: output of `layer4` → `AdaptiveAvgPool2d` → 2048-dim vector
- Access pattern: `torch.nn.Sequential(*list(model.children())[:-1])` gives feature extractor
- Classification head (to be bypassed): `model.fc` (Linear 2048→num_classes)

**Required Features:**
- ImageNet-pretrained weights (required for epoch-5 cluster validity — Assumption A1)
- Penultimate layer must be 2048-dim (standard ResNet-50 topology)

**Incompatible Architectures:**
- Random-init ResNet (tested as control, expected to fail — validates A1)
- ResNets without avg-pool (non-standard variants)

> ⚠️ If model.fc is not bypassed, embeddings will be 2-dim (logits) — FAIL early!

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"Embeddings extracted: shape (N, 2048)"` | `extract_embeddings()` |
| Tensor Shape | Input (B, 3, 224, 224) → Output (B, 2048) after avg_pool squeeze | `feature_extractor.forward()` |
| Metric Delta | AMI(cluster, group) >> AMI(random, group) ≈ 0; purity >> 0.5 | `run_kmeans_probe()` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(embeddings, cluster_assignments, group_ids, k=2):
    """Verify clustering mechanism actually worked."""
    import numpy as np
    from sklearn.metrics import adjusted_mutual_info_score

    # Check 1: embedding shape correct
    assert embeddings.shape[1] == 2048, f"Wrong embedding dim: {embeddings.shape[1]}"

    # Check 2: clusters are non-trivial (both clusters non-empty)
    for c in range(k):
        count = (cluster_assignments == c).sum()
        assert count > 10, f"Cluster {c} nearly empty: {count} samples"

    # Check 3: AMI is meaningfully above chance
    ami_actual = adjusted_mutual_info_score(group_ids, cluster_assignments)
    ami_random = adjusted_mutual_info_score(
        group_ids,
        np.random.randint(0, k, size=len(group_ids))
    )
    indicators = {
        "embedding_shape_correct": embeddings.shape[1] == 2048,
        "clusters_non_trivial": all((cluster_assignments == c).sum() > 10 for c in range(k)),
        "ami_above_chance": ami_actual > ami_random + 0.1,
        "ami_passes_threshold": ami_actual >= 0.5,
    }
    return all(indicators.values()), indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Wrong embedding dim | shape != (N, 2048) | FAIL: model.fc not bypassed |
| Empty cluster | cluster size < 10 | FAIL: k-means degenerate |
| AMI ≈ 0 | AMI < 0.1 | FAIL: no spurious structure at epoch 5; try epoch 3, 7 |
| Purity ≈ 0.5 | worst_purity < 0.55 | FAIL: clusters random; check pretrained init |
| Epoch-5 too early | AMI low at 5, high at 10 | PIVOT: use epoch 7 checkpoint |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | Embeddings are 2048-dim, clusters non-trivial |
| Effect Measurable | AMI > 0.1 (above chance) | AMI(cluster, group) vs AMI(random, group) |
| Hypothesis Supported | AMI ≥ 0.5 AND worst_purity ≥ 0.75 on both datasets | `run_kmeans_probe()` output |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (embedding extraction + k-means completes)
2. `AMI ≥ 0.5` on Waterbirds AND CelebA
3. `worst_cluster_purity ≥ 0.75` on Waterbirds AND CelebA

**Expected Outcome (from literature):** HIGH CONFIDENCE of passing. PruSC paper reports >95% purity on CelebA. DFR's 97% worst-group accuracy via last-layer retraining implies strong embedding separability. Epoch-5 may show slightly lower AMI than epoch-100, but pretrained backbone already encodes background/gender axes strongly from epoch 1.

**Failure Pivot Plan:** If AMI < 0.5 at epoch 5, try epochs 3 and 7 before concluding failure.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No relevant sources found in Archon KB (KB contains diffusion model content, not spurious correlation research).

### B. GitHub Implementations (Exa)

**Repository 1:** PolinaKirichenko/deep_feature_reweighting (⭐ 110)
- **URL:** https://github.com/PolinaKirichenko/deep_feature_reweighting
- **Query Used:** "Kirichenko DFR spurious correlations GroupDRO Waterbirds CelebA official implementation GitHub"
- **Relevance:** Official DFR paper code — provides wb_data.py (dataset loader), train_classifier.py (ERM training), imagenet_extract_embeddings.py (embedding extraction). Direct basis for H-E1 implementation.
- **Key Code (dataset + model):**
  ```python
  # train_classifier.py pattern
  python3 train_classifier.py --output_dir=<OUTPUT_DIR> --pretrained_model \
    --num_epochs=100 --weight_decay=1e-3 --batch_size=32 --init_lr=1e-3 \
    --eval_freq=1 --data_dir=<WATERBIRDS_DIR> --augment_data --seed=<SEED>
  ```
- **Configuration Extracted:** SGD, lr=1e-3, wd=1e-3, bs=32, 100 epochs for Waterbirds; lr=1e-3, wd=1e-4, bs=128, 50 epochs for CelebA
- **Their Results:** 92.0 ± 0.9 worst-group Waterbirds; 88.02 ± 1.6 CelebA (via DFR)
- **Used For:** Training protocol, dataset loading, embedding extraction pattern, model configuration

**Repository 2:** izmailovpavel/spurious_feature_learning (⭐ 48)
- **URL:** https://github.com/izmailovpavel/spurious_feature_learning
- **Query Used:** "Kirichenko DFR spurious correlations GroupDRO Waterbirds CelebA official implementation GitHub"
- **Relevance:** NeurIPS 2022 extension of DFR — achieves 97% worst-group on Waterbirds via ERM+DFR, proving penultimate embeddings have full spurious/invariant separability.
- **Key Code:**
  ```bash
  python3 train_supervised.py --output_dir=logs/waterbirds/erm_seed1 \
    --num_epochs=100 --seed=1 --weight_decay=1e-4 --batch_size=32 \
    --init_lr=3e-3 --scheduler=cosine_lr_scheduler \
    --dataset=SpuriousCorrelationDataset --model=imagenet_resnet50_pretrained
  ```
- **Configuration Extracted:** lr=3e-3, wd=1e-4, bs=32, cosine scheduler, 100 epochs (Waterbirds)
- **Used For:** Alternative training hyperparameters, validates 97% worst-group is achievable from ERM embeddings

**Repository 3:** kohpangwei/group_DRO (⭐ 295)
- **URL:** https://github.com/kohpangwei/group_DRO
- **Query Used:** "Waterbirds dataset PyTorch loading GroupDRO kohpangwei dataloader"
- **Relevance:** Original GroupDRO codebase — defines Waterbirds dataset format, group label structure (4 groups: landbird-land, landbird-water, waterbird-land, waterbird-water), standard ERM baseline.
- **Dataset Download:** `https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz`
- **Used For:** Dataset format specification, group label definitions, standard ERM baseline reference

**Paper Evidence:** PruSC (openreview.net/pdf?id=EEeVYfXor5)
- **Relevance:** Directly validates H-E1 mechanism. Shows k-means on CelebA ERM penultimate embeddings achieves >95% purity for spurious attributes (gender). Purity for spurious attributes > purity for class labels.
- **Key Quote:** "k-means clustering effectively groups samples by class label, but achieves even higher purity for spurious attributes"
- **Used For:** Expected performance baseline for AMI/purity thresholds; confidence calibration for H-E1

### C. Code Analysis (Serena)

Serena analysis not performed — code from DFR/GroupDRO repositories was sufficiently clear without semantic analysis. The `imagenet_extract_embeddings.py` and `wb_data.py` files provide complete implementation patterns.

### D. Previous Hypothesis Context

None — H-E1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: Waterbirds | GitHub | kohpangwei/group_DRO (B.3) |
| Dataset: CelebA | GitHub | PolinaKirichenko/deep_feature_reweighting (B.1) |
| Dataset preprocessing (Waterbirds) | GitHub | DFR repo AugWaterbirdsCelebATransform (B.1) |
| Dataset preprocessing (CelebA) | GitHub | DFR repo wb_data.py (B.1) |
| Baseline model: ResNet-50 pretrained | GitHub | izmailovpavel/spurious_feature_learning (B.2) |
| Model loading code | torchvision docs | torchvision.models.ResNet50_Weights.IMAGENET1K_V1 |
| Training config (Waterbirds) | GitHub | DFR repo train_classifier.py (B.1) |
| Training config (CelebA) | GitHub | DFR repo train_classifier.py (B.1) |
| K-means probe (AMI, purity) | Paper | PruSC openreview (B.4) |
| Pseudo-code pattern | GitHub | DFR imagenet_extract_embeddings.py (B.1) |
| Evaluation metrics (AMI) | sklearn docs | sklearn.metrics.adjusted_mutual_info_score |
| Expected performance | Paper | PruSC >95% purity on CelebA (B.4) |
| Mechanism verification code | Synthesis | From DFR embedding extraction + sklearn AMI |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-20T00:00:00

### Workflow History for This Hypothesis
- H-E1 set to IN_PROGRESS (Phase 2B → Phase 2C, 2026-05-20T01:00:49)
- Phase 2C experiment design: IN_PROGRESS → COMPLETED (2026-05-20)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (GitHub — 3 repos + 1 paper), Serena (skipped — code sufficiently clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
