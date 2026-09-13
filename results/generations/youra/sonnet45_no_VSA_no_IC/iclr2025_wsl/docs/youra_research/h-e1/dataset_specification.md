# Dataset Specification: H-E1 Coverage Audit

**Hypothesis:** h-e1  
**Dataset Type:** standard  
**Date:** 2026-08-20

---

## Primary Datasets

### 1. ModelZooDataset (NeurIPS 2022)

**Purpose:** Comprehensive model zoo with systematically trained populations across multiple vision tasks.

**Access:**
- **Repository:** https://github.com/ModelZoos/ModelZooDataset
- **Hosting:** Zenodo (DOI per dataset)
- **Format:** PyTorch `.pt` files with custom dataset class

**Coverage:**
- **Total models:** 50,360 unique models
- **Architectures:** CNN (small), ResNet-18
- **Tasks:** MNIST, FMNIST, SVHN, USPS, CIFAR10, CIFAR100, TinyImageNet, EuroSAT
- **Splits:** Train/val/test [70%, 15%, 15%]

**Metadata Fields:**
- `architecture`: Model type (CNN, ResNet)
- `dataset`: Training task (CIFAR10, etc.)
- `hyperparams`: Dict with optimizer, lr, augmentation, etc.
- `accuracy`: Per-epoch performance metrics
- `epoch`: Checkpoint epoch number

**Download Commands:**
```bash
# MNIST CNNs
wget https://doi.org/10.5281/zenodo.6631086 -O mnist_cnn.zip
unzip mnist_cnn.zip -d data/modelzoo/mnist

# CIFAR10 CNNs
wget https://doi.org/10.5281/zenodo.6631087 -O cifar10_cnn.zip
unzip cifar10_cnn.zip -d data/modelzoo/cifar10

# CIFAR100 CNNs
wget https://doi.org/10.5281/zenodo.6631105 -O cifar100_cnn.zip
unzip cifar100_cnn.zip -d data/modelzoo/cifar100

# Fashion-MNIST CNNs
wget https://doi.org/10.5281/zenodo.6631104 -O fmnist_cnn.zip
unzip fmnist_cnn.zip -d data/modelzoo/fmnist
```

**Loading Pattern:**
```python
import torch
from pathlib import Path

zoo_path = Path("data/modelzoo/cifar10/cifar10_cnn.pt")
zoo = torch.load(zoo_path)

# Extract metadata
metadata = []
for idx, props in enumerate(zoo['properties']):
    metadata.append({
        'model_id': f"modelzoo_cifar10_{idx}",
        'architecture': 'CNN',
        'task': 'CIFAR10',
        'optimizer': props['hyperparams']['optimizer'],
        'lr': props['hyperparams']['lr'],
        'accuracy': props['accuracy'][-1]  # Final epoch
    })
```

---

### 2. SANE Model Zoos (ICML 2024)

**Purpose:** Sequential auto-encoder training datasets with preprocessed model populations.

**Access:**
- **Repository:** https://github.com/HSG-AIML/SANE
- **Hosting:** modelzoos.cc
- **Format:** FFCV-compiled `.pt` files

**Coverage:**
- **CNN zoos:** ~4,000 models (MNIST, SVHN, USPS, FMNIST)
- **ResNet-18 zoos:** ~3,000-5,000 models (CIFAR10, CIFAR100, TinyImageNet, SVHN, EuroSAT)
- **Architectures:** CNN (token size 289), ResNet-18 (token size 288)
- **Epochs used:** 21-25 (mature training stage)

**Metadata Fields:**
- `architecture`: CNN or ResNet
- `dataset`: Training task
- `token_size`: Architecture-specific tokenization
- `sequence_length`: ~50 (CNN), ~50k (ResNet)

**Download Commands:**
```bash
cd data/sane
bash download_sane_zoos.sh

# Preprocess for metadata extraction
python3 preprocess_dataset_cnn_cifar10_sample.py
python3 preprocess_dataset_resnet_cifar100.py
```

**Loading Pattern:**
```python
from src.data import load_preprocessed_zoo

# Load SANE zoo
zoo = load_preprocessed_zoo("cifar100_resnet18")

# Metadata extraction (from config)
import json
config = json.load(open("data/sane/cifar100_resnet18/config.json"))
metadata = {
    'architecture': 'ResNet',
    'task': config['dataset'],
    'model_count': len(zoo)
}
```

---

### 3. ViTModelZoo (Fallback: Hugging Face)

**Purpose:** Transformer architecture coverage (ViT models).

**Primary Source (if available):**
- **Repository:** https://github.com/ModelZoos/ViTModelZoo
- **Status:** Uncertain availability

**Fallback Source:**
- **Repository:** Hugging Face Model Hub
- **Filter:** `task=image-classification, library=transformers, search=vit`
- **Estimated coverage:** 500-1000 ViT checkpoints

**Fallback Download:**
```python
from huggingface_hub import list_models, snapshot_download

# Search for ViT models
vit_models = list(list_models(
    filter={"task": "image-classification", "library": "transformers"},
    search="vit"
))

# Download subset for coverage audit
for model in vit_models[:100]:  # Sample 100 models
    snapshot_download(
        repo_id=model.modelId,
        local_dir=f"data/vit_zoo/{model.modelId.replace('/', '_')}"
    )
```

**Metadata Extraction:**
```python
from transformers import AutoConfig

config = AutoConfig.from_pretrained(model_id)
metadata = {
    'architecture': 'ViT',
    'task': infer_task_from_config(config),
    'num_parameters': config.num_parameters
}
```

---

## Dataset Integration

### Unified Metadata Schema

```python
import pandas as pd

# Schema for coverage audit
metadata_schema = {
    'model_id': str,           # Unique identifier
    'architecture': str,       # CNN, ResNet, ViT, MLP, RNN
    'task': str,              # MNIST, CIFAR10, ImageNet, etc.
    'source': str,            # ModelZooDataset, SANE, HuggingFace
    'hyperparams': dict,      # Training configuration
    'epoch': int,             # Checkpoint epoch
    'accuracy': float         # Final validation accuracy
}

# Aggregate all sources
all_metadata = pd.concat([
    extract_modelzoo_metadata(),
    extract_sane_metadata(),
    extract_vit_metadata()
], ignore_index=True)

# Save unified database
all_metadata.to_parquet("data/zoo_metadata.parquet")
```

### Coverage Matrix Generation

```python
# Create architecture × task contingency table
coverage_matrix = all_metadata.groupby(['architecture', 'task']).size().unstack(fill_value=0)

# Flag sufficient cells (≥30 models)
sufficient_mask = coverage_matrix >= 30
coverage_pct = sufficient_mask.sum().sum() / coverage_matrix.size * 100

print(f"Coverage: {coverage_pct:.1f}% of cells have ≥30 models")

# Export
coverage_matrix.to_csv("h-e1/coverage_matrix.csv")
```

---

## Expected Storage Requirements

| Dataset | Size | Models | Format |
|---------|------|--------|--------|
| ModelZooDataset (raw) | ~200 GB | 50,360 | .pt (PyTorch) |
| SANE (preprocessed) | ~50 GB | 7,000 | FFCV-compiled |
| ViTModelZoo / HF | ~50-100 GB | 500-1000 | Safetensors |
| **Total** | **~300-350 GB** | **~58,000** | Mixed |

---

## Dataset Quality Checks

### 1. Metadata Completeness
```python
# Check for missing fields
missing_counts = all_metadata.isnull().sum()
assert missing_counts['architecture'] == 0, "Architecture field required"
assert missing_counts['task'] == 0, "Task field required"
```

### 2. Label Consistency
```python
# Validate architecture-task compatibility
# ResNet should not appear on MNIST (28×28 too small)
invalid = all_metadata[
    (all_metadata['architecture'] == 'ResNet') & 
    (all_metadata['task'].isin(['MNIST', 'FMNIST', 'USPS']))
]
if len(invalid) > 0:
    print(f"WARNING: {len(invalid)} invalid arch-task pairs")
```

### 3. Hyperparameter Diversity
```python
# Verify training diversity within cells
for (arch, task), group in all_metadata.groupby(['architecture', 'task']):
    unique_hp = group['hyperparams'].apply(str).nunique()
    if unique_hp < 3:
        print(f"WARNING: {arch}-{task} has low hyperparameter diversity")
```

---

## Data Access Protocol

### Step 1: Initial Download
```bash
# Create directory structure
mkdir -p data/{modelzoo,sane,vit_zoo}

# Download ModelZooDataset (8 datasets)
cd data/modelzoo && bash download_modelzoo.sh

# Download SANE
cd ../sane && bash download_sane_zoos.sh

# Download ViT (if available, else use HF fallback)
cd ../vit_zoo && python download_vit_zoo.py
```

### Step 2: Metadata Extraction
```bash
# Run extraction pipeline
python scripts/extract_modelzoo_metadata.py
python scripts/extract_sane_metadata.py
python scripts/extract_vit_metadata.py

# Merge into unified database
python scripts/merge_metadata.py
```

### Step 3: Coverage Analysis
```bash
# Generate coverage matrix and heatmap
python scripts/coverage_audit.py --output h-e1/

# Expected outputs:
# - h-e1/coverage_matrix.csv
# - h-e1/coverage_heatmap.png
# - h-e1/sparse_cells.csv
```

---

## Verification Checklist

- [ ] ModelZooDataset downloaded (8 datasets)
- [ ] SANE zoos downloaded (7-9 zoos)
- [ ] ViTModelZoo checked (fallback to HF if unavailable)
- [ ] Metadata extracted to `zoo_metadata.parquet`
- [ ] Coverage matrix generated
- [ ] Sparse cells identified and documented
- [ ] Critical cells validated (≥30 models)
- [ ] Gate decision documented

---

**Dataset Type Confirmation:** `standard` (real, established datasets)  
**No synthetic/simulated data used.**
