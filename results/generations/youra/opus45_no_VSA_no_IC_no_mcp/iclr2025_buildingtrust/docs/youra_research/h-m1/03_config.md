# Configuration Document: H-M1

**Hypothesis:** Calibration moderates truthfulness-robustness correlation
**Date:** 2026-08-28

---

## 1. Configuration Schema

```python
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ECEConfig:
    n_bins: int = 15
    min_bin_samples: int = 1
    
@dataclass
class CorrelationConfig:
    ece_r_threshold: float = -0.2
    ece_p_threshold: float = 0.10
    fisher_p_threshold: float = 0.05
    
@dataclass
class ExperimentConfig:
    seed: int = 42
    n_bootstrap: int = 1000
    confidence_level: float = 0.95
    
@dataclass
class H_M1_Config:
    ece: ECEConfig
    correlation: CorrelationConfig
    experiment: ExperimentConfig
    models: List[str]
    h_e1_results_path: str
    output_path: str
```

## 2. YAML Configuration

```yaml
# h-m1/code/config.yaml

experiment:
  seed: 42
  n_bootstrap: 1000
  confidence_level: 0.95

ece:
  n_bins: 15
  min_bin_samples: 1

thresholds:
  ece_correlation_r: -0.2
  ece_correlation_p: 0.10
  fisher_p: 0.05

paths:
  h_e1_results: "../h-e1/code/results"
  output: "./results"
  figures: "../figures"

models:
  # Inherited from h-e1
  pythia:
    - "EleutherAI/pythia-70m"
    - "EleutherAI/pythia-160m"
    - "EleutherAI/pythia-410m"
    - "EleutherAI/pythia-1b"
    - "EleutherAI/pythia-1.4b"
    - "EleutherAI/pythia-2.8b"
  llama2:
    - "meta-llama/Llama-2-7b-hf"
    - "meta-llama/Llama-2-13b-hf"
  mistral:
    - "mistralai/Mistral-7B-v0.1"
  falcon:
    - "tiiuae/falcon-7b"
    - "tiiuae/falcon-40b"
```

## 3. Python Config Module

```python
# h-m1/code/config.py

import yaml
from pathlib import Path

SEED = 42
N_BINS = 15
N_BOOTSTRAP = 1000

# Gate thresholds
THRESHOLDS = {
    "ece_correlation_r": -0.2,
    "ece_correlation_p": 0.10,
    "fisher_p": 0.05
}

# Paths
H_E1_RESULTS = Path("../h-e1/code/results")
OUTPUT_PATH = Path("./results")
FIGURES_PATH = Path("../figures")

# Models (same as h-e1)
MODELS = [
    "EleutherAI/pythia-70m",
    "EleutherAI/pythia-160m",
    "EleutherAI/pythia-410m",
    "EleutherAI/pythia-1b",
    "EleutherAI/pythia-1.4b",
    "EleutherAI/pythia-2.8b",
    "meta-llama/Llama-2-7b-hf",
    "meta-llama/Llama-2-13b-hf",
    "mistralai/Mistral-7B-v0.1",
    "tiiuae/falcon-7b",
    "tiiuae/falcon-40b",
    # Additional models if available
]

def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)
```

## 4. Environment Variables

```bash
# Optional overrides
export H_M1_SEED=42
export H_M1_N_BINS=15
export H_M1_H_E1_PATH="../h-e1/code/results"
```

## 5. Visualization Config

```python
VIZ_CONFIG = {
    "figure_dpi": 300,
    "figure_format": "png",
    "color_palette": {
        "low_ece": "#2ecc71",   # Green
        "high_ece": "#e74c3c",  # Red
        "neutral": "#3498db"    # Blue
    },
    "font_size": {
        "title": 14,
        "label": 12,
        "tick": 10
    }
}
```

## 6. Validation Rules

| Parameter | Valid Range | Default |
|-----------|-------------|---------|
| n_bins | 5-50 | 15 |
| seed | any int | 42 |
| ece_r_threshold | [-1, 0] | -0.2 |
| ece_p_threshold | (0, 1] | 0.10 |
| fisher_p_threshold | (0, 1] | 0.05 |

---

*Configuration for H-M1 calibration moderation experiment*
