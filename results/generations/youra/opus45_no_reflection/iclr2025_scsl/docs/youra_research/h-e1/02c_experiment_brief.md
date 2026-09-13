# Experiment Design: H-E1

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** CV of probe accuracy trajectories distinguishes spurious from core features with AUC >= 0.75
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK - AUC >= 0.75 required

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
Feature classification AUC >= 0.75 when using CV of probe accuracy trajectories to distinguish spurious (background) from core (bird type) features on Waterbirds dataset.

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous results to build upon.

### Previous Hypothesis Results (if applicable)
N/A - Foundation hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches for spurious correlation detection. Archon KB primarily contains diffusion/generative model documentation. Key insight: CLIP feature extraction is well-documented across multiple sources.

### Archon Code Examples

CLIP feature extraction patterns found:
- `CLIPModel.from_pretrained()` for loading
- `model.encode_image()` for feature extraction
- Normalization patterns for downstream tasks

### Exa GitHub Implementations

**Primary Sources Found:**

1. **kohpangwei/group_DRO** (Official Waterbirds benchmark)
   - Dataset download: `https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz`
   - 95% spurious correlation between bird type and background
   - Train: 4795, Val: 1199, Test: 5794 samples
   - Baseline ERM: ~70% WGA, Group DRO: ~91% WGA

2. **openai/CLIP** (Official CLIP repo)
   - Linear probe pattern using sklearn LogisticRegression
   - `clip.load('ViT-B/16')` or `'ViT-B/32'`
   - Feature extraction: `model.encode_image(images.to(device))`
   - L2-normalize before classification

3. **izmailovpavel/spurious_feature_learning**
   - DFR (Deep Feature Reweighting) achieves 91%+ WGA on Waterbirds
   - ERM features are sufficient for SOTA when last layer is retrained
   - Confirms pretrained features capture both spurious and core features

4. **JTT Paper (Liu et al. 2021)**
   - Two-stage approach: identify hard examples, then upweight
   - JTT closes 73% gap between ERM and Group DRO
   - Confirms simplicity bias: ERM fits easy groups first

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Source | Relevance |
|----------|--------|-----------|
| 1 | kohpangwei/group_DRO | Official Waterbirds dataset generation |
| 2 | openai/CLIP | Official CLIP linear probe pattern |
| 3 | izmailovpavel/spurious_feature_learning | DFR baseline comparison |

**Recommended Implementation Path:**
- Primary: Use official Waterbirds dataset + OpenAI CLIP ViT-B/16
- Fallback: WILDS package for dataset loading if download fails
- Justification: Official sources ensure reproducibility; CLIP ViT-B/16 is standard for vision probing

### Code Analysis (Serena MCP)

No existing codebase to analyze - this is a new experiment implementation.

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | Waterbirds |
| **Version** | waterbird_complete95_forest2water2 |
| **Source** | kohpangwei/group_DRO |
| **Type** | standard |
| **Train samples** | 4795 |
| **Val samples** | 1199 |
| **Test samples** | 5794 |
| **Spurious correlation** | 95% (background correlates with bird type) |
| **Groups** | 4 (landbird-land, landbird-water, waterbird-land, waterbird-water) |

**Preprocessing:**
- Resize to 224x224
- CLIP preprocessing (center crop, normalize with CLIP mean/std)
- No augmentation for feature extraction (deterministic)

**Loading Information** (for Phase 4 download):
- Method: direct_download
- Identifier: `https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz`
- Code:
```python
import os
import tarfile
import urllib.request

def download_waterbirds(data_dir):
    url = "https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz"
    tar_path = os.path.join(data_dir, "waterbirds.tar.gz")
    
    if not os.path.exists(os.path.join(data_dir, "waterbird_complete95_forest2water2")):
        urllib.request.urlretrieve(url, tar_path)
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(data_dir)
        os.remove(tar_path)
    
    return os.path.join(data_dir, "waterbird_complete95_forest2water2")
```

### Models

#### Baseline Model

| Attribute | Value |
|-----------|-------|
| **Architecture** | CLIP ViT-B/16 (frozen) |
| **Source** | openai/clip |
| **Purpose** | Feature extraction only |
| **Output dim** | 512 |

**Loading Information** (for Phase 4 download):
- Method: pip_package
- Identifier: `clip` (openai/CLIP repo)
- Code:
```python
import clip
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/16", device=device)
model.eval()

def extract_features(images):
    with torch.no_grad():
        features = model.encode_image(images.to(device))
        features = features / features.norm(dim=-1, keepdim=True)  # L2 normalize
    return features.cpu().numpy()
```

#### Proposed Model

**Architecture:** CLIP ViT-B/16 (frozen) + Linear Probes for multiple visual concepts

**Core Mechanism Implementation:**

```python
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

def compute_cv_for_feature(features, labels, n_subsets=5, subset_frac=0.2, n_epochs=10):
    """
    Compute CV of probe accuracy trajectories across random subsets.
    
    Args:
        features: (N, D) CLIP features for all training samples
        labels: (N,) binary labels for the visual concept being probed
        n_subsets: number of random subsets to evaluate
        subset_frac: fraction of data in each subset
        n_epochs: number of training checkpoints to simulate
    
    Returns:
        cv: coefficient of variation of accuracy improvement rates
    """
    n_samples = len(features)
    subset_size = int(n_samples * subset_frac)
    
    # Store accuracy trajectories for each subset
    trajectories = []
    
    for subset_idx in range(n_subsets):
        # Random subset selection
        indices = np.random.choice(n_samples, subset_size, replace=False)
        subset_features = features[indices]
        subset_labels = labels[indices]
        
        # Simulate training trajectory by varying regularization (proxy for epochs)
        # Higher C = less regularization = later in training
        C_values = np.logspace(-3, 2, n_epochs)  # 0.001 to 100
        accuracies = []
        
        for C in C_values:
            clf = LogisticRegression(C=C, max_iter=1000, random_state=42)
            clf.fit(subset_features, subset_labels)
            acc = clf.score(subset_features, subset_labels)
            accuracies.append(acc)
        
        trajectories.append(accuracies)
    
    # Compute improvement rates (slope of accuracy trajectory)
    improvement_rates = []
    for traj in trajectories:
        # Rate = final_acc - initial_acc
        rate = traj[-1] - traj[0]
        improvement_rates.append(rate)
    
    # CV = std / mean
    mean_rate = np.mean(improvement_rates)
    std_rate = np.std(improvement_rates)
    cv = std_rate / (mean_rate + 1e-8)  # avoid division by zero
    
    return cv

def classify_features_by_cv(feature_cvs, threshold=0.15):
    """
    Classify features as spurious (CV < threshold) or core (CV >= threshold).
    """
    predictions = []
    for cv in feature_cvs:
        if cv < threshold:
            predictions.append(1)  # spurious
        else:
            predictions.append(0)  # core
    return np.array(predictions)

def evaluate_cv_classifier(feature_cvs, ground_truth_spurious, thresholds=[0.1, 0.15, 0.2]):
    """
    Evaluate CV-based classifier using AUC.
    
    Args:
        feature_cvs: CV values for each feature
        ground_truth_spurious: 1 if feature is spurious, 0 if core
        thresholds: CV thresholds to evaluate
    
    Returns:
        auc: area under ROC curve
        best_threshold: threshold with best F1
    """
    # Lower CV = higher spurious probability, so negate for AUC
    spurious_scores = -np.array(feature_cvs)
    auc = roc_auc_score(ground_truth_spurious, spurious_scores)
    
    return auc
```

### Training Protocol

| Parameter | Value | Justification |
|-----------|-------|---------------|
| **Feature Extractor** | CLIP ViT-B/16 | Standard for vision probing |
| **Probe Type** | Linear (LogisticRegression) | Matches H-E1 protocol |
| **Regularization C** | Sweep [0.001, 0.01, 0.1, 1, 10, 100] | Simulate training trajectory |
| **Subsets** | 5 random 20% subsets | Per H-E1 verification protocol |
| **Features to Probe** | background (spurious), bird_type (core) | Ground truth labels available |
| **Optimizer** | L-BFGS (sklearn default) | Convex optimization, no hyperparameters |

**Training Steps:**
1. Extract CLIP features for all Waterbirds training images (once, cached)
2. For each visual concept (background, bird_type):
   - For each of 5 random 20% subsets:
     - Train linear probes at 10 regularization checkpoints
     - Record accuracy trajectory
   - Compute CV of improvement rates across subsets
3. Classify features using CV threshold
4. Compute AUC against ground truth

### Evaluation

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Primary: AUC** | >= 0.75 | ROC-AUC for CV-based spurious/core classification |
| **Secondary: CV Separation** | Visible | KL divergence between spurious vs core CV distributions |
| **Diagnostic: CV Distribution** | Non-overlapping | Histogram of CVs by feature type |

**Success Criteria (PoC):**
- AUC >= 0.75 for distinguishing spurious from core features
- Spurious features (background) show CV < 0.15
- Core features (bird_type) show CV > 0.2

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary_classification
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import roc_auc_score, precision_recall_curve, f1_score

def compute_metrics(cv_values, ground_truth_spurious):
    # Lower CV = more likely spurious, so negate for scoring
    scores = -np.array(cv_values)
    
    # AUC
    auc = roc_auc_score(ground_truth_spurious, scores)
    
    # Best threshold by F1
    precisions, recalls, thresholds = precision_recall_curve(ground_truth_spurious, scores)
    f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-8)
    best_idx = np.argmax(f1_scores)
    best_f1 = f1_scores[best_idx]
    
    return {"auc": auc, "best_f1": best_f1}
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing AUC vs 0.75 threshold

#### Additional Figures (LLM Autonomous)

1. **CV Distribution Histogram**: Overlay of CV distributions for spurious vs core features
2. **Probe Accuracy Trajectories**: Line plots showing accuracy vs regularization for each subset, colored by feature type
3. **ROC Curve**: ROC curve with AUC annotation

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. AUC >= 0.75 (CV distinguishes spurious from core)

**Gate Decision:**
- PASS (AUC >= 0.75): Proceed to H-M1
- FAIL (AUC < 0.75): STOP - Reassess CV metric or detection approach

---

## Appendix: Reference Implementations

### A. Waterbirds Dataset Loading (kohpangwei/group_DRO)

```python
# From: https://github.com/kohpangwei/group_DRO
# Dataset structure after extraction:
# waterbird_complete95_forest2water2/
#   metadata.csv  (img_id, img_filename, y, place, split)
#   [images organized by CUB structure]

import pandas as pd
from PIL import Image
import os

def load_waterbirds(data_dir):
    metadata = pd.read_csv(os.path.join(data_dir, "metadata.csv"))
    
    # y=0: landbird, y=1: waterbird
    # place=0: land background, place=1: water background
    # split: 0=train, 1=val, 2=test
    
    # Ground truth: place is spurious, y is core
    # Group 0: landbird on land (y=0, place=0) - majority
    # Group 1: landbird on water (y=0, place=1) - minority
    # Group 2: waterbird on land (y=1, place=0) - minority  
    # Group 3: waterbird on water (y=1, place=1) - majority
    
    return metadata
```

### B. CLIP Feature Extraction (openai/CLIP)

```python
# From: https://github.com/openai/CLIP
import clip
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

def get_clip_features(dataset, model, preprocess, device, batch_size=100):
    all_features = []
    all_labels = []
    
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    
    with torch.no_grad():
        for images, labels in tqdm(loader):
            features = model.encode_image(images.to(device))
            features = features / features.norm(dim=-1, keepdim=True)
            all_features.append(features.cpu())
            all_labels.append(labels)
    
    return torch.cat(all_features).numpy(), torch.cat(all_labels).numpy()
```

### C. Linear Probe Training (openai/CLIP)

```python
# From: https://github.com/openai/CLIP README
from sklearn.linear_model import LogisticRegression

classifier = LogisticRegression(
    random_state=0, 
    C=0.316,  # hyperparameter sweep recommended
    max_iter=1000,
    solver='lbfgs'
)
classifier.fit(train_features, train_labels)
accuracy = classifier.score(test_features, test_labels)
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19: Hypothesis h-e1 set to IN_PROGRESS (External loop starting Phase 2C)
- 2026-08-19: Phase 2C experiment design completed

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
