# Configuration: H-E1
# OrbitVar Measurement — DeepSets & NFN Encoders on ModelZooDataset CIFAR10-GS

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-03

Applied: N/A — Archon KB contains diffusion model docs only; no relevant weight-space config patterns found (max sim ~0.44)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field — no local codebase to analyze
**Config Files Found**: None — new config design
**Pattern Used**: dataclass

---

## ExperimentConfig (Python Dataclass)

```python
from dataclasses import dataclass, field
import os

@dataclass
class ExperimentConfig:
    # --- Fixed from Phase 2B spec — do NOT change ---
    n_models: int = 100
    K_permutations: int = 50
    seed: int = 1
    gate_threshold: float = 1e-6
    cise_baseline_orbitvar: float = 0.010333  # BUILD_ON from sh1 PASS — not re-run

    # --- Dataset ---
    data_path: str = "data/dataset_cifar_small_hyp_rand.pt"
    index_dict_path: str = "data/index_dict.json"

    # --- CNN architecture (fixed — matches CIFAR10-GS zoo) ---
    n_conv_layers: int = 3
    n_channels: int = 16

    # --- C2 DeepSets encoder ---
    c2_hidden_dim: int = 64
    c2_embed_dim: int = 128

    # --- C3 NFN encoder ---
    c3_nfn_channels: int = 32
    c3_embed_dim: int = 128

    # --- Numerical precision (float64 for OrbitVar accuracy) ---
    dtype: str = "float64"

    # --- Output paths ---
    figures_dir: str = "figures"
    results_dir: str = "results"
    results_file: str = "results/orbit_var_results.json"

    # --- Visualization style ---
    fig_dpi: int = 150
    fig_size: tuple = (8, 5)
    color_c2: str = "#2196F3"   # blue
    color_c3: str = "#4CAF50"   # green
    color_cise: str = "#F44336" # red

    def validate(self) -> None:
        assert os.path.exists(self.data_path), f"Dataset not found: {self.data_path}"
        assert os.path.exists(self.index_dict_path), f"Index dict not found: {self.index_dict_path}"
        os.makedirs(self.figures_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
```

---

## YAML Config (Human-editable)

```yaml
# config.yaml — H-E1 OrbitVar Measurement
# Fields marked FIXED must not be changed (Phase 2B spec)

# FIXED
n_models: 100
K_permutations: 50
seed: 1
gate_threshold: 1.0e-6
cise_baseline_orbitvar: 0.010333

# Dataset paths (update if dataset is in a different location)
data_path: "data/dataset_cifar_small_hyp_rand.pt"
index_dict_path: "data/index_dict.json"

# FIXED — CNN architecture matches ModelZoo CIFAR10-GS
n_conv_layers: 3
n_channels: 16

# C2 DeepSets encoder
c2_hidden_dim: 64
c2_embed_dim: 128

# C3 NFN encoder
c3_nfn_channels: 32
c3_embed_dim: 128

# Numerical precision
dtype: "float64"

# Output paths
figures_dir: "figures"
results_dir: "results"
results_file: "results/orbit_var_results.json"

# Visualization
fig_dpi: 150
fig_size: [8, 5]
color_c2: "#2196F3"
color_c3: "#4CAF50"
color_cise: "#F44336"
```

---

## requirements.txt

```
torch>=1.12.0
numpy>=1.21.0
matplotlib>=3.5.0
scipy>=1.7.0
nfn
```

> Install nfn from source if pip install fails:
> `pip install git+https://github.com/AllanYangZhou/nfn.git`

---

## A-1: Environment + Data Setup [Complexity: 9, Budget: 1 subtask]

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Environment Setup & Data Download | Install deps, download dataset, verify files, create directory structure |

### C-1-1: Environment Setup & Data Download Configuration

**Directory structure to create:**
```
h-e1/
  code/
  data/        # gitignored
  figures/
  results/
```

**Setup commands:**
```bash
# Create directories
mkdir -p data figures results

# Install dependencies
pip install torch numpy matplotlib scipy
pip install nfn  # or: pip install git+https://github.com/AllanYangZhou/nfn.git

# Download dataset from Zenodo DOI 10.5281/zenodo.6620868
# Manual browser download: https://zenodo.org/record/6620868
# Or wget (if direct URL available):
wget -O data/dataset_cifar_small_hyp_rand.pt \
  "https://zenodo.org/record/6620868/files/dataset_cifar_small_hyp_rand.pt"
wget -O data/index_dict.json \
  "https://zenodo.org/record/6620868/files/index_dict.json"
```

**Verification script (`code/verify_setup.py`):**
```python
import os, sys, torch

REQUIRED_FILES = [
    "data/dataset_cifar_small_hyp_rand.pt",
    "data/index_dict.json",
]

def verify():
    ok = True
    for f in REQUIRED_FILES:
        if os.path.exists(f):
            print(f"[OK] {f}")
        else:
            print(f"[MISSING] {f}")
            ok = False

    if ok:
        dataset = torch.load(REQUIRED_FILES[0])
        print(f"[OK] Dataset loaded: {len(dataset)} models")
        w, acc = dataset[0]
        print(f"[OK] Weight vector shape: {w.shape}, accuracy: {acc:.4f}")

    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    verify()
```

**Config fields used:** `data_path`, `index_dict_path`

---

## A-6: Visualization + Integration [Complexity: 9, Budget: 1 subtask]

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Visualization Config & Run Script Settings | Figure paths, plot styles, CLI argparse schema, results JSON validation |

### C-6-1: Visualization Configuration & Run Script Settings

**Figure output paths and naming:**
```python
FIGURE_PATHS = {
    "bar":    "figures/orbitvar_comparison.png",   # required
    "pca":    "figures/pca_scatter.png",           # optional
    "violin": "figures/violin_orbitvar.png",       # optional
}
```

**Plot style settings:**
```python
PLOT_STYLE = {
    "colors": {
        "C2":   "#2196F3",   # blue  — DeepSets
        "C3":   "#4CAF50",   # green — NFN
        "CISE": "#F44336",   # red   — baseline
    },
    "figsize":    (8, 5),
    "dpi":        150,
    "yscale":     "log",     # bar chart: log-scale y-axis
    "threshold":  1e-6,      # horizontal line on bar chart
    "n_pca_models": 10,      # PCA scatter uses first 10 models
}
```

**CLI argparse schema (`run_experiment.py`):**
```python
import argparse

def get_args():
    p = argparse.ArgumentParser(description="H-E1 OrbitVar measurement")
    p.add_argument("--config",       default="config.yaml",  help="Path to config YAML")
    p.add_argument("--data-path",    default=None,           help="Override data_path")
    p.add_argument("--skip-pca",     action="store_true",    help="Skip PCA scatter plot")
    p.add_argument("--skip-violin",  action="store_true",    help="Skip violin plot")
    return p.parse_args()
```

**Results JSON schema (orbit_var_results.json):**
```json
{
  "mean_orbitvar_c2": 0.0,
  "max_orbitvar_c2":  0.0,
  "mean_orbitvar_c3": 0.0,
  "max_orbitvar_c3":  0.0,
  "cise_baseline":    0.010333,
  "gate_pass":        true,
  "seed":             1,
  "n_models":         100,
  "K":                50
}
```

**Validation (inline in run_experiment.py):**
```python
import json

def validate_results(path: str) -> bool:
    with open(path) as f:
        r = json.load(f)
    required = ["mean_orbitvar_c2", "max_orbitvar_c2",
                "mean_orbitvar_c3", "max_orbitvar_c3",
                "gate_pass", "seed", "n_models", "K"]
    return all(k in r for k in required)
```

---

## Self-Validation

- [x] ONE format only (dataclass — no dict alternative)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: N/A" line)
- [x] Rationale only for non-standard values
- [x] Subtask count within budget (1 each for A-1, A-6)
- [x] Total length < 400 lines
- [x] Codebase Analysis (Serena) section included
- [x] Green-field — Serena skip acceptable
