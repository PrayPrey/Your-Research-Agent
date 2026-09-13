# Configuration: h-p0 — DFR Backbone Identity Sanity Check

**Applied**: Standard flat dataclass config pattern (green-field, EXISTENCE PoC)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-1: ExperimentConfig [Complexity: Low, Budget: 0 subtasks]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ExperimentConfig:
    # --- Reproducibility ---
    seed: int = 42

    # --- Dataset ---
    dataset_root: str = "/home/PrayPrey/.wilds_cache"
    dataset_name: str = "waterbirds"
    dataset_version: str = "waterbirds_v1.0"
    test_split: str = "test"
    n_test_images: int = 50          # sanity check only; full test = 5794

    # --- Preprocessing (ImageNet standard) ---
    resize: int = 256
    crop_size: int = 224
    img_mean: List[float] = field(default_factory=lambda: [0.485, 0.456, 0.406])
    img_std: List[float] = field(default_factory=lambda: [0.229, 0.224, 0.225])

    # --- Model ---
    hf_repo: str = "izmailovpavel/spurious_feature_learning"
    methods: List[str] = field(default_factory=lambda: ["erm", "dfr"])
    seeds: List[int] = field(default_factory=lambda: [1, 2, 3])
    checkpoint_filename: str = "final_checkpoint.pt"
    n_classes: int = 2
    feature_dim: int = 2048          # ResNet-50 layer4 → pool → flatten

    # --- Inference ---
    batch_size: int = 50             # all test images in one batch (small PoC)
    device: str = "cuda"             # CPU fallback acceptable for 50 images

    # --- Gate thresholds ---
    gate_mean_sim: float = 0.9999
    gate_variance: float = 1e-6

    # --- Output paths ---
    output_dir: str = "h-p0/results"
    figures_dir: str = "h-p0/figures"
    results_filename: str = "similarity_results.json"
```

---

## Checkpoint Path Mapping

```python
# method × seed grid → relative checkpoint path (under HF repo root)
CHECKPOINT_MAP: Dict[str, Dict[int, str]] = {
    "erm": {
        1: "erm_seed1/final_checkpoint.pt",
        2: "erm_seed2/final_checkpoint.pt",
        3: "erm_seed3/final_checkpoint.pt",
    },
    "dfr": {
        1: "dfr_seed1/final_checkpoint.pt",
        2: "dfr_seed2/final_checkpoint.pt",
        3: "dfr_seed3/final_checkpoint.pt",
    },
}

# Comparison pairs (erm_seedN vs dfr_seedN, matching seeds only)
SEED_PAIRS = [(1, 1), (2, 2), (3, 3)]
```

---

## YAML Schema

```yaml
# h-p0/config.yaml — copy-paste ready
seed: 42

dataset:
  root: "/home/PrayPrey/.wilds_cache"
  name: "waterbirds"
  version: "waterbirds_v1.0"
  test_split: "test"
  n_test_images: 50
  resize: 256
  crop_size: 224
  img_mean: [0.485, 0.456, 0.406]
  img_std: [0.229, 0.224, 0.225]

model:
  hf_repo: "izmailovpavel/spurious_feature_learning"
  methods: ["erm", "dfr"]
  seeds: [1, 2, 3]
  checkpoint_filename: "final_checkpoint.pt"
  n_classes: 2
  feature_dim: 2048

inference:
  batch_size: 50
  device: "cuda"

gate:
  mean_sim: 0.9999
  variance: 1.0e-6

output:
  output_dir: "h-p0/results"
  figures_dir: "h-p0/figures"
  results_filename: "similarity_results.json"
```

---

## Gate Thresholds and Evaluation Config

```python
# Pass condition: ALL three must hold
GATE_MEAN_SIM: float = 0.9999    # mean cosine similarity per seed pair
GATE_VARIANCE: float = 1e-6      # variance of per-sample cosine similarities

# Warning band (investigate checkpoint, not full fail)
WARN_MEAN_SIM: float = 0.999

# Expected shape at each stage
EXPECTED_SHAPES = {
    "input":   (50, 3, 224, 224),
    "layer4":  (50, 2048, 7, 7),
    "pooled":  (50, 2048, 1, 1),
    "feature": (50, 2048),
}
```

---

## Output Paths Config

```python
import os

OUTPUT_DIR = "h-p0/results"
FIGURES_DIR = "h-p0/figures"

# Created at runtime
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

OUTPUT_FILES = {
    "results_json":       f"{OUTPUT_DIR}/similarity_results.json",
    "gate_bar_chart":     f"{FIGURES_DIR}/gate_cosine_similarity.png",
    "distribution_hist":  f"{FIGURES_DIR}/per_sample_distribution.png",
    "pca_scatter":        f"{FIGURES_DIR}/pca_feature_scatter.png",
}
```
