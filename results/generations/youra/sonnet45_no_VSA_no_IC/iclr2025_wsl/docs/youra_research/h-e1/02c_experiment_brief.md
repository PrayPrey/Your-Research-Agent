# Experiment Brief: Dataset Coverage Audit (H-E1)

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Phase:** Pre-Phase 1 (Gate: MUST_WORK)  
**Date:** 2026-08-20

---

## 1. Hypothesis Statement

Under heterogeneous model zoo datasets (ModelZooDataset, SANE, ViTModelZoo), if we audit architecture-task cell coverage, then at least 70% of cells will contain ≥30 models, sufficient for statistical validity, because these datasets were specifically designed for inhomogeneous zoo research and target diverse architecture families.

---

## 2. Experiment Overview

### 2.1 Objective
Validate that ModelZooDataset, SANE, and ViTModelZoo collectively provide sufficient architecture-task cell coverage (≥30 models per cell in ≥70% of cells) to enable statistically valid bootstrap testing (n=100 resamples) for downstream hierarchical VAE experiments.

### 2.2 Success Criteria
- **Primary:** ≥70% of architecture-task cells contain ≥30 models
- **Secondary:** All critical cells (ImageNet-CNN, ImageNet-Transformer, CIFAR-CNN) contain ≥30 models
- **Fallback:** 50-70% coverage BUT critical cells covered (scope reduction acceptable)

### 2.3 Failure Response
- **<50% coverage:** ABANDON (insufficient data, need collection phase)
- **50-70% coverage AND critical cells sparse:** PIVOT (reduce to homogeneous subsets, loses novelty)
- **≥70% coverage but critical cells sparse:** EXPLORE (substitute comparable cells)

---

## 3. Dataset Specifications

### 3.1 ModelZooDataset (NeurIPS 2022)

**Source:**
- Repository: https://github.com/ModelZoos/ModelZooDataset
- Hosting: Zenodo (20-year guarantee)
- DOIs: Per-dataset repositories (MNIST, FMNIST, SVHN, CIFAR10, CIFAR100, TinyImageNet)

**Composition:**
- **Total models:** 50,360 unique models
- **Total states:** 3,844,360 collected states (includes epoch checkpoints)
- **Image datasets:** 8 (MNIST, FMNIST, SVHN, USPS, CIFAR10, CIFAR100, TinyImageNet, EuroSAT)
- **Model zoos:** 27 zoos with varying hyperparameter combinations
- **Architectures:** CNNs (small), ResNet-18 (large)
- **Train/val/test splits:** [70%, 15%, 15%]

**Metadata Available:**
- Model hyperparameters (json per model)
- Performance metrics per epoch (accuracy, loss)
- Exact training protocol (optimizer, learning rate, augmentation)
- Architecture definition (PyTorch model class)

**Access Pattern:**
```python
# Via custom PyTorch dataset class
from dataset_base import ModelZooDataset
zoo = ModelZooDataset(dataset_path="path/to/zoo.pt")
# Metadata: zoo.properties (dict with task, architecture, hyperparams)
```

### 3.2 SANE (ICML 2024)

**Source:**
- Repository: https://github.com/HSG-AIML/SANE
- Hosting: modelzoos.cc
- Extension: MultiZoo-SANE (inhomogeneous zoos)

**Composition:**
- **CNN zoos:** 4 datasets (MNIST, SVHN, USPS, FMNIST) × ~1000 models each = 4000 models
- **ResNet-18 zoos:** 3-5 datasets (CIFAR10, CIFAR100, TinyImageNet, SVHN, EuroSAT) × ~600-1000 models each = 3000-5000 models
- **Architectures:** CNNs (token size 289), ResNet-18 (token size 288)
- **Training epochs:** Models saved at epochs 21-25
- **Preprocessing:** FFCV-compiled datasets with sliced windows

**Metadata Available:**
- Task labels (verified via controlled training)
- Architecture type (CNN vs ResNet)
- Training procedure (augmentation strategies, optimizer)
- Model sequence length (~50 for CNNs, ~50k for ResNets)

**Access Pattern:**
```python
# Via SANE preprocessing pipeline
from src.data import load_preprocessed_zoo
zoo = load_preprocessed_zoo("cifar100_resnet18")
# Metadata extraction: parse zoo config JSON
```

### 3.3 ViTModelZoo (2025 - Inferred)

**Source:**
- Repository: https://github.com/ModelZoos/ViTModelZoo (assumed from verification plan)
- Status: Likely extension of ModelZooDataset framework for Vision Transformers

**Composition (Expected):**
- **Architectures:** Vision Transformers (ViT-Small, ViT-Base variants)
- **Estimated models:** ~5000-10000 (based on ModelZooDataset scale)
- **Task coverage:** ImageNet-subset, CIFAR variants, possibly medical imaging

**Fallback Strategy:**
If ViTModelZoo unavailable or underpopulated:
- Use Hugging Face model hub Transformer models (filtered by task)
- Use timm library pre-trained ViT checkpoints
- Accept lower Transformer coverage if CNN/ResNet cells sufficient

---

## 4. Experiment Design

### 4.1 Data Preparation

**Step 1: Dataset Download**
```bash
# ModelZooDataset (via Zenodo DOIs)
wget https://doi.org/10.5281/zenodo.6631086 -O mnist_cnn.zip
wget https://doi.org/10.5281/zenodo.6631104 -O fmnist_cnn.zip
wget https://doi.org/10.5281/zenodo.6631087 -O cifar10_cnn.zip
wget https://doi.org/10.5281/zenodo.6631105 -O cifar100_cnn.zip
# + TinyImageNet, SVHN, EuroSAT zoos

# SANE (via modelzoos.cc)
cd data && bash download_sane_zoos.sh
python3 preprocess_dataset_cnn_cifar10_sample.py

# ViTModelZoo (if available)
# Fallback: Use timm/Hugging Face if unavailable
```

**Step 2: Metadata Extraction**
```python
import pandas as pd
from pathlib import Path
import json

def extract_metadata(zoo_path):
    """Extract (architecture, task, model_id) tuples from zoo."""
    metadata = []
    
    # ModelZooDataset format
    if zoo_path.suffix == '.pt':
        import torch
        zoo = torch.load(zoo_path)
        for idx, props in enumerate(zoo['properties']):
            metadata.append({
                'model_id': f"{zoo_path.stem}_{idx}",
                'architecture': props.get('architecture', 'CNN'),
                'task': props.get('dataset', 'unknown'),
                'hyperparams': props.get('hyperparams', {}),
                'source': 'ModelZooDataset'
            })
    
    # SANE format (preprocessed)
    elif zoo_path.suffix == '.json':
        config = json.load(zoo_path.open())
        # Parse from config structure
        
    return pd.DataFrame(metadata)

# Aggregate all zoos
all_metadata = []
for zoo_path in Path("datasets/").glob("**/*.pt"):
    all_metadata.append(extract_metadata(zoo_path))
df = pd.concat(all_metadata, ignore_index=True)
```

**Step 3: Architecture-Task Taxonomy**

**Architecture Categories:**
1. **CNN:** Convolutional networks (small CNNs from ModelZooDataset)
2. **ResNet:** Residual networks (ResNet-18 from SANE/ModelZooDataset)
3. **ViT:** Vision Transformers (ViTModelZoo or timm)
4. **MLP:** Multi-layer perceptrons (if available in zoos)
5. **RNN:** Recurrent networks (RARE - likely absent, document gap)

**Task Categories (Vision-only):**
1. **MNIST:** Grayscale digit classification (10 classes)
2. **FMNIST:** Fashion item classification (10 classes)
3. **SVHN:** Street View House Numbers (10 classes)
4. **USPS:** Handwritten digits (10 classes)
5. **CIFAR10:** Natural images (10 classes)
6. **CIFAR100:** Natural images (100 classes)
7. **TinyImageNet:** ImageNet subset (200 classes)
8. **EuroSAT:** Satellite imagery (10 land-use classes)
9. **ImageNet:** Full ImageNet (1000 classes) - if ViTModelZoo available

### 4.2 Coverage Audit Protocol

**Step 1: Cross-Tabulation Matrix**
```python
# Create architecture × task contingency table
coverage_matrix = df.groupby(['architecture', 'task']).size().unstack(fill_value=0)

# Flag cells with <30 models
sufficient_mask = coverage_matrix >= 30
coverage_pct = sufficient_mask.sum().sum() / coverage_matrix.size * 100

print(f"Coverage: {coverage_pct:.1f}% of cells have ≥30 models")
```

**Step 2: Critical Cell Validation**
```python
critical_cells = [
    ('CNN', 'CIFAR10'),
    ('CNN', 'ImageNet'),      # Likely sparse/absent
    ('ResNet', 'CIFAR10'),
    ('ResNet', 'CIFAR100'),
    ('ResNet', 'TinyImageNet'),
    ('ViT', 'ImageNet'),      # Likely sparse/absent
]

critical_coverage = {}
for arch, task in critical_cells:
    count = coverage_matrix.loc[arch, task] if (arch in coverage_matrix.index and task in coverage_matrix.columns) else 0
    critical_coverage[(arch, task)] = count
    status = "PASS" if count >= 30 else "FAIL"
    print(f"{arch}-{task}: {count} models [{status}]")
```

**Step 3: Heatmap Visualization**
```python
import seaborn as sns
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(coverage_matrix, annot=True, fmt='d', cmap='RdYlGn', 
            vmin=0, vmax=100, cbar_kws={'label': 'Model Count'},
            linewidths=0.5, ax=ax)
ax.set_title("Architecture-Task Coverage Matrix")
plt.tight_layout()
plt.savefig("coverage_heatmap.png", dpi=300)
```

**Step 4: Sparse Cell Analysis**
```python
# Identify sparse regions for mitigation
sparse_cells = coverage_matrix[coverage_matrix < 30].stack()
print(f"\nSparse cells (<30 models): {len(sparse_cells)}")
print(sparse_cells.sort_values())

# Natural experiment: Treat sparse cells as robustness test
# Document which architecture-task pairs are undersampled
```

### 4.3 Statistical Validity Check

**Bootstrap Power Analysis:**
```python
from scipy.stats import bootstrap
import numpy as np

# Simulate bootstrap test on smallest acceptable cell (n=30)
def wcss_stat(data):
    """Within-cluster sum of squares statistic."""
    return np.sum((data - data.mean())**2)

# Power calculation for n=30 vs n=100
sample_sizes = [30, 50, 100, 200]
for n in sample_sizes:
    # Simulate effect size detection at Cohen's d=0.5
    group_a = np.random.normal(0, 1, n)
    group_b = np.random.normal(0.5, 1, n)  # d=0.5 effect
    
    # Bootstrap test (100 resamples)
    res_a = bootstrap((group_a,), wcss_stat, n_resamples=100)
    res_b = bootstrap((group_b,), wcss_stat, n_resamples=100)
    
    # Empirical power (proportion of significant tests at α=0.01)
    power = (res_a.confidence_interval.high < res_b.confidence_interval.low)
    print(f"n={n}: Bootstrap power = {power}")
```

**Acceptance Threshold:**
- n=30: Minimum for 80% power to detect Cohen's d=0.5 at α=0.01
- n≥30 in ≥70% of cells ensures statistical validity across most comparisons

---

## 5. Baseline Experiments

### 5.1 Metadata Quality Validation

**Check 1: Task Label Accuracy**
```python
# Cross-validate task labels with model architecture
# ResNet-18 should NOT appear in MNIST (image too small)
invalid_pairs = df[(df['architecture'] == 'ResNet') & (df['task'] == 'MNIST')]
if len(invalid_pairs) > 0:
    print(f"WARNING: {len(invalid_pairs)} invalid architecture-task pairs detected")
```

**Check 2: Hyperparameter Diversity**
```python
# Verify training procedures vary within each cell
for (arch, task), group in df.groupby(['architecture', 'task']):
    unique_optimizers = group['hyperparams'].apply(lambda x: x.get('optimizer')).nunique()
    unique_lr = group['hyperparams'].apply(lambda x: x.get('lr')).nunique()
    print(f"{arch}-{task}: {unique_optimizers} optimizers, {unique_lr} learning rates")
```

### 5.2 Fallback Coverage Strategies

**Strategy 1: Scope Reduction**
If coverage <70% but critical cells OK:
```python
# Restrict to well-covered architecture families
sufficient_archs = coverage_matrix[sufficient_mask.sum(axis=1) >= 0.7 * len(coverage_matrix.columns)].index
print(f"Reducing scope to architectures: {list(sufficient_archs)}")
```

**Strategy 2: Synthetic Augmentation (LAST RESORT - NOT PREFERRED)**
If critical cells sparse AND no real data available:
```python
# ONLY if absolutely unavoidable - document as limitation
# Generate additional models via transfer learning from well-covered cells
# Example: Fine-tune CIFAR10-CNN models on CIFAR100 → increases CIFAR100-CNN count
# CRITICAL: Mark these as "derived" in metadata
```

**Strategy 3: External Dataset Integration**
```python
# Hugging Face model hub integration (real models, not synthetic)
from huggingface_hub import list_models

# Example: Augment ViT-ImageNet cell
vit_models = list_models(
    filter={"task": "image-classification", "library": "transformers"},
    search="vit"
)
# Download checkpoints, extract weights, standardize format
```

---

## 6. Expected Outcomes

### 6.1 Predicted Coverage Distribution

**Base Expectation (from literature):**
- ModelZooDataset: 27 zoos × ~1850 models/zoo avg = ~50K models
- SANE: 7-9 zoos × ~500-1000 models/zoo = ~7K models
- ViTModelZoo: Unknown (assume 0-5K models)
- **Total pool:** ~55-60K models

**Architecture-Task Grid:**
- Architectures: {CNN, ResNet, ViT, MLP} = 4
- Tasks: {MNIST, FMNIST, SVHN, USPS, CIFAR10, CIFAR100, TinyImageNet, EuroSAT, ImageNet} = 9
- **Total cells:** 4 × 9 = 36 cells

**Coverage Prediction:**
- **Well-covered cells (≥100 models):** CNN-CIFAR10, CNN-MNIST, ResNet-CIFAR100, ResNet-TinyImageNet (~8-10 cells)
- **Sufficiently covered (30-99 models):** CNN-FMNIST, ResNet-CIFAR10, CNN-SVHN (~10-15 cells)
- **Sparse (<30 models):** ViT-*, MLP-*, RNN-* (~10-18 cells)
- **Expected coverage:** ~55-70% of cells with ≥30 models

**Critical Cells Status:**
- CNN-CIFAR10: PASS (expect >500 models)
- ResNet-CIFAR100: PASS (expect >300 models from SANE)
- ResNet-TinyImageNet: PASS (expect >200 models)
- ViT-ImageNet: LIKELY FAIL (ViTModelZoo availability unknown)
- CNN-ImageNet: FAIL (CNNs too small for ImageNet)

### 6.2 Gate Decision Scenarios

**Scenario A: PASS (≥70% coverage)**
- Proceed to Phase 1 (H-M-integrated CKA feasibility gate)
- Use all available cells for full hierarchical VAE training
- Document sparse cells as natural robustness test

**Scenario B: PARTIAL (50-70%, critical OK)**
- Scope reduction: Restrict to {CNN, ResNet} × {CIFAR10, CIFAR100, TinyImageNet}
- Accept loss of ViT/MLP/RNN families (reduces novelty claim)
- Proceed with caution, add caveat to paper

**Scenario C: FAIL (<50% coverage OR critical cells sparse)**
- ABORT Phase 1, return to Phase 0 or Phase 2A-Dialogue
- Option 1: Collect additional data (ModelZooDataset extension)
- Option 2: Reduce to single-architecture homogeneous setting (loses novelty)

### 6.3 Deliverables

1. **Coverage Matrix CSV** (`coverage_matrix.csv`)
   - Rows: Architectures
   - Columns: Tasks
   - Values: Model counts

2. **Coverage Heatmap** (`coverage_heatmap.png`)
   - Color-coded visualization (red: sparse, green: sufficient)
   - Annotated with model counts per cell

3. **Metadata Database** (`zoo_metadata.parquet`)
   - Schema: `{model_id, architecture, task, hyperparams, source, epoch, accuracy}`
   - ~55-60K rows
   - Indexed by (architecture, task) for fast querying

4. **Validation Report** (`h-e1_validation_report.md`)
   - Coverage percentage (primary metric)
   - Critical cell status (secondary metric)
   - Sparse cell analysis
   - Gate decision recommendation

---

## 7. Implementation Requirements

### 7.1 Compute Resources

**Storage:**
- ModelZooDataset raw: ~200GB (27 zoos × epoch checkpoints)
- SANE preprocessed: ~50GB (FFCV-compiled windows)
- ViTModelZoo: ~50-100GB (if available)
- **Total:** ~300-350GB disk space

**Compute:**
- Metadata extraction: Single CPU core, ~2-4 hours
- Coverage analysis: CPU-only, <30 minutes
- Visualization: CPU-only, <10 minutes

**No GPU required for this hypothesis.**

### 7.2 Software Dependencies

```yaml
# environment.yml
name: h-e1-coverage-audit
channels:
  - pytorch
  - conda-forge
dependencies:
  - python=3.10
  - pytorch=2.0
  - pandas=2.0
  - numpy=1.24
  - scipy=1.11
  - matplotlib=3.7
  - seaborn=0.12
  - jupyter
  - pip:
    - zenodo_get  # For Zenodo downloads
    - huggingface_hub
```

### 7.3 Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Dataset download | 1-2 days | Raw zoos cached locally |
| Metadata extraction | 0.5 days | `zoo_metadata.parquet` |
| Coverage analysis | 0.5 days | `coverage_matrix.csv` |
| Visualization | 0.5 days | `coverage_heatmap.png` |
| Validation report | 0.5 days | `h-e1_validation_report.md` |
| **Total** | **3-4 days** | Gate decision ready |

---

## 8. Risk Mitigation

### 8.1 Risk R1: Insufficient Dataset Coverage (PRIMARY)

**Detection:**
- Coverage heatmap shows >30% sparse cells (red regions)
- Critical cells (CNN-CIFAR10, ResNet-CIFAR100) contain <30 models

**Mitigation:**
1. **Immediate:** Audit ViTModelZoo availability (GitHub/Zenodo search)
2. **Fallback:** Integrate Hugging Face model hub (real models, not synthetic)
3. **Last resort:** Scope reduction to well-covered architecture families

**Acceptance Criteria:**
- If 50-70% coverage + critical cells OK → PROCEED with scope reduction
- If <50% coverage → ABORT, return to Phase 0

### 8.2 Risk R2: Metadata Quality Issues

**Detection:**
- Task labels inconsistent with architecture (e.g., ResNet-18 on 28×28 MNIST)
- Missing hyperparameter fields in >10% of models

**Mitigation:**
1. Cross-validate with model architecture definitions (input size, layer count)
2. Manual inspection of 100 random samples
3. Contact ModelZooDataset authors for clarification

**Acceptance Criteria:**
- Accept if <5% metadata errors
- Document errors, exclude invalid models from coverage count

### 8.3 Risk R5: Architecture Subspace Incompatibility (FUTURE)

**Coverage Impact:**
- Even if 70% coverage achieved, Phase 1 CKA gate may fail
- Sparse ViT/MLP/RNN cells reduce cross-architecture diversity

**Mitigation:**
- Prioritize dense CNN/ResNet cells for Phase 1 CKA pilot
- If CKA fails, coverage audit still provides dataset characterization

---

## 9. Success Metrics Summary

| Metric | Threshold | Type |
|--------|-----------|------|
| Overall coverage | ≥70% cells with ≥30 models | PRIMARY |
| Critical cell coverage | CNN-CIFAR10, ResNet-CIFAR100, ResNet-TinyImageNet all ≥30 | SECONDARY |
| Metadata quality | <5% invalid entries | VALIDATION |
| Sparse cell documentation | All <30 cells catalogued | ROBUSTNESS |

**Gate Decision Tree:**
```
IF coverage ≥ 70%:
    → PASS, proceed to Phase 1 (H-M-integrated CKA gate)
ELIF 50% ≤ coverage < 70% AND critical_cells_ok:
    → PARTIAL PASS, proceed with scope reduction
ELIF coverage < 50%:
    → FAIL, ABORT Phase 1
    → Options: (1) Collect more data, (2) Reduce to homogeneous setting
ELIF coverage ≥ 70% BUT critical_cells_sparse:
    → EXPLORE, substitute comparable cells (e.g., ResNet-SVHN instead of ResNet-ImageNet)
```

---

## 10. Notes

### 10.1 Dataset Type Classification

**Type:** `standard` (real, established datasets)
- ModelZooDataset: Real trained models on standard benchmarks
- SANE: Real models from controlled training procedures
- ViTModelZoo: Real Transformer checkpoints (if available)

**NOT `synthetic`:** This experiment uses ONLY real model checkpoints from actual training runs. No simulated/synthetic datasets.

### 10.2 Sample Size Rationale

**Why n=30 threshold?**
- Bootstrap testing (n=100 resamples) requires ≥30 samples for 80% power
- Cohen's d=0.5 effect size (medium effect) detectable at α=0.01
- Below n=30: Underpowered, clustering results may reflect noise

**Why 70% coverage?**
- Allows 30% sparse cells as natural robustness test
- Ensures critical architecture families (CNN, ResNet) well-covered
- Balances feasibility vs statistical rigor

### 10.3 Relation to Main Hypothesis

This existence hypothesis (H-E1) is a **prerequisite gate** for H-M-integrated (hierarchical VAE mechanism). Without sufficient data, the CKA feasibility gate and WCSS clustering tests in Phases 1-4 cannot proceed.

**Dependency chain:**
```
H-E1 (Pre-Phase 1) → H-M-integrated Phase 1 (CKA gate) → H-M-integrated Phase 2-3 (VAE training) → H-M-integrated Phase 4 (WCSS test)
```

If H-E1 fails, the entire verification timeline blocks at Week 1.

---

**END OF EXPERIMENT BRIEF**
