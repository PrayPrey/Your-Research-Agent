# Configuration Specification: H-E1 Coverage Audit

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC audit)  
**Date:** 2026-08-20

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** Green-field project - designing new config schema  
**Config Files Found:** None - new config  
**Pattern Used:** Hardcoded dict (PoC audit, single run)

---

## Configuration Format

**Applied:** Standard Python dict (no dataclass overhead for single-run audit script)

### config.py

```python
"""H-E1 Coverage Audit Configuration"""

CONFIG = {
    # Dataset paths
    "dataset_paths": {
        "modelzoo_dir": "data/modelzoo",
        "sane_dir": "data/sane/SANE",
        "vit_dir": "data/vit_zoo",
    },
    
    # Zenodo DOIs (ModelZooDataset)
    "zenodo_dois": {
        "mnist_cnn": "10.5281/zenodo.6631086",
        "fmnist_cnn": "10.5281/zenodo.6631104",
        "svhn_cnn": "10.5281/zenodo.6631087",
        "cifar10_cnn": "10.5281/zenodo.6631087",
        "cifar100_cnn": "10.5281/zenodo.6631105",
    },
    
    # Taxonomy definitions
    "architectures": ["CNN", "ResNet", "ViT", "MLP", "RNN"],
    "tasks": ["MNIST", "FMNIST", "SVHN", "USPS", "CIFAR10", 
              "CIFAR100", "TinyImageNet", "EuroSAT", "ImageNet"],
    
    # Coverage thresholds
    "cell_minimum": 30,
    "coverage_threshold": 70.0,  # percent
    "critical_cells": [
        ("CNN", "CIFAR10"),
        ("ResNet", "CIFAR100"),
        ("ResNet", "TinyImageNet"),
    ],
    
    # Output paths
    "output_dir": "h-e1/outputs",
    "metadata_file": "data/zoo_metadata.parquet",
    "coverage_matrix_file": "h-e1/outputs/coverage_matrix.csv",
    "heatmap_file": "h-e1/outputs/coverage_heatmap.png",
    "validation_report_file": "h-e1/outputs/h-e1_validation_report.md",
    "sparse_cells_file": "h-e1/outputs/sparse_cells.csv",
    
    # Visualization settings
    "heatmap_dpi": 300,
    "heatmap_figsize": (12, 6),
    "heatmap_colormap": "RdYlGn",
    "heatmap_vmin": 0,
    "heatmap_vmax": 100,
    
    # Quality validation
    "metadata_error_threshold": 5.0,  # percent
    "validation_sample_size": 100,
    
    # Bootstrap power validation
    "bootstrap_n_samples": 30,
    "bootstrap_effect_size": 0.5,
    "bootstrap_n_resamples": 100,
    "bootstrap_power_threshold": 0.80,
    
    # Hugging Face fallback
    "hf_vit_limit": 100,
}
```

---

## environment.yml

```yaml
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
  - pyarrow
  - pip:
    - zenodo_get
    - huggingface_hub
    - transformers
```

---

## Rationale

**Hardcoded dict vs dataclass:** Single-run audit script, no training loops or hyperparameter sweeps. Dict provides immediate copy-paste usage.

**cell_minimum=30:** Bootstrap power analysis (n=30 provides 80% power for Cohen's d=0.5 at alpha=0.01)

**coverage_threshold=70%:** Allows 30% sparse cells as natural robustness test while ensuring statistical validity

**critical_cells:** CNN-CIFAR10, ResNet-CIFAR100, ResNet-TinyImageNet identified from PRD as most likely well-covered cells

**heatmap_vmax=100:** Caps colormap at 100 models for legibility (cells with >100 all show as dark green)

---

## Usage Example

```python
from config import CONFIG

# Download datasets
for task, doi in CONFIG["zenodo_dois"].items():
    download_zenodo(doi, CONFIG["dataset_paths"]["modelzoo_dir"])

# Extract metadata
metadata = extract_all_metadata(CONFIG["dataset_paths"])

# Audit coverage
coverage_matrix = compute_coverage(
    metadata,
    architectures=CONFIG["architectures"],
    tasks=CONFIG["tasks"]
)

# Evaluate
coverage_pct = evaluate_coverage(
    coverage_matrix,
    cell_min=CONFIG["cell_minimum"],
    threshold=CONFIG["coverage_threshold"],
    critical_cells=CONFIG["critical_cells"]
)
```

---

**END OF CONFIGURATION**
