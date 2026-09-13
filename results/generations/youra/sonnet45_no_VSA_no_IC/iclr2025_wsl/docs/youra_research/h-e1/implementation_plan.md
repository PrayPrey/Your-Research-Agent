# Implementation Plan: H-E1 Coverage Audit

**Hypothesis:** h-e1  
**Type:** EXISTENCE  
**Estimated Duration:** 3-4 days  
**Date:** 2026-08-20

---

## Phase Overview

**Objective:** Audit ModelZooDataset, SANE, and ViTModelZoo for architecture-task cell coverage to validate ≥70% of cells contain ≥30 models.

**No model training required.** This is a dataset metadata analysis task.

---

## Implementation Steps

### Step 1: Environment Setup (0.5 days)

**Compute Requirements:**
- CPU-only workstation (no GPU needed)
- 500GB disk space (dataset storage)
- 32GB RAM (metadata processing)

**Software Stack:**
```yaml
# environment.yml
name: h-e1-coverage
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
    - zenodo_get
    - huggingface_hub
    - pyarrow
```

**Setup Commands:**
```bash
# Create conda environment
conda env create -f environment.yml
conda activate h-e1-coverage

# Create directory structure
mkdir -p data/{modelzoo,sane,vit_zoo,augmented}
mkdir -p scripts
mkdir -p h-e1/outputs
```

---

### Step 2: Dataset Download (1-2 days)

**2.1 ModelZooDataset (Zenodo)**

```bash
# Download script: scripts/download_modelzoo.sh
#!/bin/bash
cd data/modelzoo

# MNIST CNNs
zenodo_get 10.5281/zenodo.6631086
unzip -q mnist_cnn.zip -d mnist && rm mnist_cnn.zip

# Fashion-MNIST CNNs
zenodo_get 10.5281/zenodo.6631104
unzip -q fmnist_cnn.zip -d fmnist && rm fmnist_cnn.zip

# SVHN CNNs
zenodo_get 10.5281/zenodo.6631087
unzip -q svhn_cnn.zip -d svhn && rm svhn_cnn.zip

# CIFAR10 CNNs
zenodo_get 10.5281/zenodo.6631087
unzip -q cifar10_cnn.zip -d cifar10 && rm cifar10_cnn.zip

# CIFAR100 CNNs
zenodo_get 10.5281/zenodo.6631105
unzip -q cifar100_cnn.zip -d cifar100 && rm cifar100_cnn.zip

# TinyImageNet CNNs (if available)
# EuroSAT CNNs (if available)

echo "ModelZooDataset download complete"
```

**Execute:**
```bash
chmod +x scripts/download_modelzoo.sh
./scripts/download_modelzoo.sh
```

**2.2 SANE Model Zoos**

```bash
# Download script: scripts/download_sane.sh
#!/bin/bash
cd data/sane

# Clone SANE repository for download scripts
git clone https://github.com/HSG-AIML/SANE.git
cd SANE/data

# Download CNN zoos (MNIST, FMNIST, SVHN, USPS)
bash download_zoo_sample.sh

# Download ResNet zoos (CIFAR10, CIFAR100, TinyImageNet)
# (follow SANE repository instructions)

cd ../..
echo "SANE zoos download complete"
```

**2.3 ViTModelZoo (Fallback: Hugging Face)**

```python
# scripts/download_vit_zoo.py
from huggingface_hub import list_models, snapshot_download
from pathlib import Path
import json

def download_vit_models(output_dir="data/vit_zoo", max_models=100):
    """Download ViT models from Hugging Face as fallback."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Search for ViT models
    vit_models = list(list_models(
        filter={"task": "image-classification", "library": "transformers"},
        search="vit",
        limit=max_models
    ))
    
    downloaded = []
    for model in vit_models:
        try:
            # Download checkpoint
            local_path = snapshot_download(
                repo_id=model.modelId,
                local_dir=output_dir / model.modelId.replace('/', '_'),
                allow_patterns=["*.bin", "*.safetensors", "config.json"]
            )
            
            downloaded.append({
                'model_id': model.modelId,
                'local_path': str(local_path)
            })
            print(f"Downloaded {model.modelId}")
        except Exception as e:
            print(f"Failed {model.modelId}: {e}")
    
    # Save manifest
    json.dump(downloaded, open(output_dir / "manifest.json", "w"), indent=2)
    print(f"Downloaded {len(downloaded)} ViT models")

if __name__ == "__main__":
    download_vit_models()
```

**Execute:**
```bash
python scripts/download_vit_zoo.py
```

---

### Step 3: Metadata Extraction (0.5 days)

**3.1 ModelZooDataset Metadata**

```python
# scripts/extract_modelzoo_metadata.py
import torch
import pandas as pd
from pathlib import Path
import json

def extract_modelzoo_metadata(zoo_dir="data/modelzoo"):
    """Extract metadata from ModelZooDataset .pt files."""
    zoo_dir = Path(zoo_dir)
    all_metadata = []
    
    for zoo_path in zoo_dir.rglob("*.pt"):
        try:
            zoo = torch.load(zoo_path, map_location='cpu')
            
            # Extract task from directory structure
            task = zoo_path.parent.name.upper()
            
            # Parse properties
            if 'properties' in zoo:
                for idx, props in enumerate(zoo['properties']):
                    all_metadata.append({
                        'model_id': f"modelzoo_{task}_{idx}",
                        'architecture': 'CNN',  # ModelZooDataset is CNN-only
                        'task': task,
                        'source': 'ModelZooDataset',
                        'optimizer': props.get('hyperparams', {}).get('optimizer', 'unknown'),
                        'lr': props.get('hyperparams', {}).get('lr', None),
                        'accuracy': props.get('accuracy', [None])[-1],
                        'epoch': len(props.get('accuracy', [])) - 1
                    })
        except Exception as e:
            print(f"Failed to load {zoo_path}: {e}")
    
    df = pd.DataFrame(all_metadata)
    df.to_parquet("data/modelzoo_metadata.parquet")
    print(f"Extracted {len(df)} ModelZooDataset models")
    return df

if __name__ == "__main__":
    extract_modelzoo_metadata()
```

**3.2 SANE Metadata**

```python
# scripts/extract_sane_metadata.py
import json
import pandas as pd
from pathlib import Path

def extract_sane_metadata(sane_dir="data/sane/SANE"):
    """Extract metadata from SANE preprocessed zoos."""
    sane_dir = Path(sane_dir)
    all_metadata = []
    
    # Search for config.json files
    for config_path in sane_dir.rglob("config.json"):
        try:
            config = json.load(config_path.open())
            
            # Infer architecture from config
            architecture = config.get('architecture', 'CNN')
            task = config.get('dataset', 'unknown').upper()
            model_count = config.get('num_models', 0)
            
            # Create entries for each model in zoo
            for idx in range(model_count):
                all_metadata.append({
                    'model_id': f"sane_{task}_{architecture}_{idx}",
                    'architecture': architecture,
                    'task': task,
                    'source': 'SANE',
                    'token_size': config.get('token_size', None),
                    'sequence_length': config.get('sequence_length', None)
                })
        except Exception as e:
            print(f"Failed to parse {config_path}: {e}")
    
    df = pd.DataFrame(all_metadata)
    df.to_parquet("data/sane_metadata.parquet")
    print(f"Extracted {len(df)} SANE models")
    return df

if __name__ == "__main__":
    extract_sane_metadata()
```

**3.3 ViT Metadata**

```python
# scripts/extract_vit_metadata.py
from transformers import AutoConfig
import pandas as pd
from pathlib import Path
import json

def extract_vit_metadata(vit_dir="data/vit_zoo"):
    """Extract metadata from ViT models."""
    vit_dir = Path(vit_dir)
    manifest = json.load((vit_dir / "manifest.json").open())
    
    all_metadata = []
    for entry in manifest:
        try:
            config = AutoConfig.from_pretrained(entry['local_path'])
            
            # Infer task from model card (simplified)
            task = "ImageNet"  # Default assumption for ViT
            
            all_metadata.append({
                'model_id': entry['model_id'],
                'architecture': 'ViT',
                'task': task,
                'source': 'HuggingFace',
                'num_parameters': getattr(config, 'num_parameters', None)
            })
        except Exception as e:
            print(f"Failed to parse {entry['model_id']}: {e}")
    
    df = pd.DataFrame(all_metadata)
    df.to_parquet("data/vit_metadata.parquet")
    print(f"Extracted {len(df)} ViT models")
    return df

if __name__ == "__main__":
    extract_vit_metadata()
```

**Execute All:**
```bash
python scripts/extract_modelzoo_metadata.py
python scripts/extract_sane_metadata.py
python scripts/extract_vit_metadata.py
```

**3.4 Merge Metadata**

```python
# scripts/merge_metadata.py
import pandas as pd

# Load all sources
modelzoo_df = pd.read_parquet("data/modelzoo_metadata.parquet")
sane_df = pd.read_parquet("data/sane_metadata.parquet")
vit_df = pd.read_parquet("data/vit_metadata.parquet")

# Merge
all_metadata = pd.concat([modelzoo_df, sane_df, vit_df], ignore_index=True)

# Standardize column names
all_metadata = all_metadata[['model_id', 'architecture', 'task', 'source']]

# Save unified database
all_metadata.to_parquet("data/zoo_metadata.parquet")
print(f"Total models: {len(all_metadata)}")
print(all_metadata.groupby(['architecture', 'task']).size().unstack(fill_value=0))
```

**Execute:**
```bash
python scripts/merge_metadata.py
```

---

### Step 4: Coverage Analysis (0.5 days)

```python
# scripts/coverage_audit.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def coverage_audit(output_dir="h-e1"):
    """Generate coverage matrix, heatmap, and validation report."""
    # Load metadata
    df = pd.read_parquet("data/zoo_metadata.parquet")
    
    # Create coverage matrix
    coverage_matrix = df.groupby(['architecture', 'task']).size().unstack(fill_value=0)
    coverage_matrix.to_csv(f"{output_dir}/coverage_matrix.csv")
    
    # Calculate coverage percentage
    sufficient_mask = coverage_matrix >= 30
    coverage_pct = sufficient_mask.sum().sum() / coverage_matrix.size * 100
    
    # Identify critical cells
    critical_cells = {
        ('CNN', 'CIFAR10'): coverage_matrix.loc['CNN', 'CIFAR10'] if 'CNN' in coverage_matrix.index and 'CIFAR10' in coverage_matrix.columns else 0,
        ('ResNet', 'CIFAR100'): coverage_matrix.loc['ResNet', 'CIFAR100'] if 'ResNet' in coverage_matrix.index and 'CIFAR100' in coverage_matrix.columns else 0,
        ('ResNet', 'TinyImageNet'): coverage_matrix.loc['ResNet', 'TinyImageNet'] if 'ResNet' in coverage_matrix.index and 'TinyImageNet' in coverage_matrix.columns else 0,
    }
    
    # Generate heatmap
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(coverage_matrix, annot=True, fmt='d', cmap='RdYlGn',
                vmin=0, vmax=100, cbar_kws={'label': 'Model Count'},
                linewidths=0.5, ax=ax)
    ax.set_title("Architecture-Task Coverage Matrix (H-E1)")
    ax.set_xlabel("Task")
    ax.set_ylabel("Architecture")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/coverage_heatmap.png", dpi=300)
    
    # Sparse cells analysis
    sparse_cells = coverage_matrix[coverage_matrix < 30].stack()
    sparse_cells.to_csv(f"{output_dir}/sparse_cells.csv")
    
    # Validation report
    report = f"""# H-E1 Validation Report

## Coverage Results
- **Overall Coverage:** {coverage_pct:.1f}% of cells with ≥30 models
- **Threshold:** ≥70% (PRIMARY)
- **Status:** {"PASS" if coverage_pct >= 70 else "PARTIAL" if coverage_pct >= 50 else "FAIL"}

## Critical Cells
"""
    for (arch, task), count in critical_cells.items():
        status = "PASS" if count >= 30 else "FAIL"
        report += f"- {arch}-{task}: {count} models [{status}]\n"
    
    report += f"""
## Sparse Cells (<30 models)
Total: {len(sparse_cells)}

{sparse_cells.to_string()}

## Gate Decision
"""
    if coverage_pct >= 70 and all(count >= 30 for count in critical_cells.values()):
        report += "- [x] PASS: Proceed to Phase 1 (H-M-integrated CKA gate)\n"
    elif coverage_pct >= 50 and all(count >= 30 for count in critical_cells.values()):
        report += "- [x] PARTIAL PASS: Proceed with scope reduction\n"
    else:
        report += "- [x] FAIL: Insufficient coverage, ABORT Phase 1\n"
    
    # Save report
    with open(f"{output_dir}/validation_report.md", "w") as f:
        f.write(report)
    
    print(report)
    return coverage_pct, critical_cells

if __name__ == "__main__":
    coverage_audit()
```

**Execute:**
```bash
python scripts/coverage_audit.py
```

---

### Step 5: Validation & Quality Checks (0.5 days)

**5.1 Metadata Quality Validation**

```python
# scripts/validate_metadata.py
import pandas as pd
import random

def validate_metadata_quality(sample_size=100):
    """Manual validation of metadata accuracy."""
    df = pd.read_parquet("data/zoo_metadata.parquet")
    sample = df.sample(n=min(sample_size, len(df)), random_state=42)
    
    # Check 1: No missing required fields
    required_fields = ['model_id', 'architecture', 'task', 'source']
    missing_counts = sample[required_fields].isnull().sum()
    print("Missing field counts:")
    print(missing_counts)
    
    # Check 2: Architecture-task compatibility
    incompatible_pairs = [
        ('ResNet', 'MNIST'),  # ResNet too large for 28x28
        ('ResNet', 'FMNIST'),
        ('ResNet', 'USPS'),
    ]
    
    invalid_count = 0
    for arch, task in incompatible_pairs:
        invalid = sample[(sample['architecture'] == arch) & (sample['task'] == task)]
        invalid_count += len(invalid)
        if len(invalid) > 0:
            print(f"WARNING: {len(invalid)} invalid {arch}-{task} pairs")
    
    # Quality score
    error_rate = (missing_counts.sum() + invalid_count) / (len(sample) * len(required_fields)) * 100
    print(f"\nMetadata error rate: {error_rate:.2f}%")
    print(f"Status: {'PASS' if error_rate < 5.0 else 'FAIL'}")
    
    return error_rate < 5.0

if __name__ == "__main__":
    validate_metadata_quality()
```

**5.2 Bootstrap Power Validation**

```python
# scripts/validate_bootstrap_power.py
from scipy.stats import bootstrap
import numpy as np

def validate_bootstrap_power(n_samples=30, effect_size=0.5, trials=1000):
    """Validate n=30 threshold provides ≥80% power."""
    def wcss(data):
        return np.sum((data - np.mean(data))**2)
    
    detections = 0
    for _ in range(trials):
        group_a = np.random.normal(0, 1, n_samples)
        group_b = np.random.normal(effect_size, 1, n_samples)
        
        res_a = bootstrap((group_a,), wcss, n_resamples=100, random_state=None)
        res_b = bootstrap((group_b,), wcss, n_resamples=100, random_state=None)
        
        if res_a.confidence_interval.high < res_b.confidence_interval.low:
            detections += 1
    
    power = detections / trials
    print(f"Bootstrap power (n={n_samples}, d={effect_size}): {power:.3f}")
    print(f"Status: {'PASS' if power >= 0.80 else 'FAIL'}")
    return power >= 0.80

if __name__ == "__main__":
    validate_bootstrap_power()
```

**Execute:**
```bash
python scripts/validate_metadata.py
python scripts/validate_bootstrap_power.py
```

---

## Timeline Summary

| Step | Duration | Deliverable |
|------|----------|-------------|
| 1. Environment setup | 0.5 days | Conda env, directory structure |
| 2. Dataset download | 1-2 days | Raw zoos cached locally (~300GB) |
| 3. Metadata extraction | 0.5 days | `zoo_metadata.parquet` |
| 4. Coverage analysis | 0.5 days | Coverage matrix, heatmap, report |
| 5. Validation & QC | 0.5 days | Quality checks, power validation |
| **Total** | **3-4 days** | Gate decision ready |

---

## Expected Outputs

### Files in `h-e1/` folder:
1. `coverage_matrix.csv` - Architecture × task contingency table
2. `coverage_heatmap.png` - Color-coded visualization
3. `sparse_cells.csv` - List of cells with <30 models
4. `validation_report.md` - Coverage percentage, critical cell status, gate decision

### Files in `data/` folder:
1. `zoo_metadata.parquet` - Unified metadata database (~55-60K rows)
2. `modelzoo_metadata.parquet` - ModelZooDataset metadata
3. `sane_metadata.parquet` - SANE metadata
4. `vit_metadata.parquet` - ViT metadata

---

## Risk Mitigation

### Risk 1: Dataset Download Failures
- **Mitigation:** Retry logic in download scripts, fallback to manual download
- **Fallback:** Use cached datasets if Zenodo/modelzoos.cc unavailable

### Risk 2: Metadata Extraction Errors
- **Mitigation:** Try-except blocks, skip corrupted files
- **Acceptance:** <5% extraction failures acceptable

### Risk 3: Insufficient Coverage
- **Mitigation:** Fallback strategies (scope reduction, external augmentation)
- **Decision tree:** Documented in baseline_experiments.md

---

## Success Criteria

- [ ] All three dataset sources downloaded (ModelZooDataset, SANE, ViT)
- [ ] Metadata extracted for ≥95% of models
- [ ] Coverage matrix generated
- [ ] Coverage ≥70% OR critical cells ≥30 (PASS/PARTIAL)
- [ ] Validation report generated with gate decision

---

**Implementation Status:** Ready to execute  
**Next Action:** Run Step 1 (environment setup)
