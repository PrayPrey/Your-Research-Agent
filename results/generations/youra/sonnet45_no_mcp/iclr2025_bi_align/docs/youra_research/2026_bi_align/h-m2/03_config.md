# Configuration Design
# Hypothesis: h-m2 - Embedding Space Clustering Analysis

**Version:** 1.0  
**Date:** 2026-04-19  
**Hypothesis ID:** h-m2  
**Hypothesis Type:** MECHANISM (Step 2)  
**Hypothesis Tier:** EXISTENCE (PoC - Does clustering exist?)  
**Budget:** 5 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Config patterns verified from h-m1 base code  
**Config Files Found:** h-m1/code/config.yaml  
**Pattern Used:** Hardcoded YAML configuration

**Note:** h-m1 uses YAML-based configuration. h-m2 extends this with embedding extraction and statistical analysis parameters.

---

## Configuration Philosophy

**Applied:** KB-003-MinimalConfig (EXISTENCE tier - single fixed configuration)

**EXISTENCE Rule:** PoC config contains ONLY fixed defaults from research, no hyperparameter variations, no ablations, no multiple options. Goal: "Does it work?" not "What works best?"

---

## Inherited Configuration (Base Hypothesis)

### Base Config Structure (From h-m1 Actual Code)

```yaml
# From: h-m1/code/config.yaml (ACTUAL CODE - VERIFIED)
experiment:
  name: str
  hypothesis_id: str
  description: str
  seed: 42
  test_sample_size: int
  n_annotators: int

dataset:
  name: "Anthropic/hh-rlhf"
  subset: null
  split: "train"

gates:
  primary_kappa_threshold: float
  alpha: float

statistical_analysis:
  alpha: float

outputs:
  data_dir: str
  figures_dir: str
  results_file: str

logging:
  level: str
```

**Verified from:** h-m1/code/config.yaml (actual implementation)

---

## Extended Configuration (h-m2)

### Main Configuration File (config.yaml)

```yaml
# Experiment Configuration for H-M2
# Embedding Space Clustering Analysis

experiment:
  name: "h-m2-embedding-clustering"
  hypothesis_id: "h-m2"
  description: "Validate geometric structure in RLHF preference data via embedding clustering"
  seed: 42

# Dataset configuration (INHERITED from h-m1)
dataset:
  name: "Anthropic/hh-rlhf"
  subset: null
  split: "train"
  max_samples: null  # Use full dataset (~160K)
  cache_dir: "./data/hf_cache"

# Embedding extraction (NEW for h-m2)
embedding:
  model_name: "roberta-base"
  batch_size: 32
  max_length: 512
  device: "cuda"
  checkpoint_path: "./data/embeddings/"

# PCA dimensionality reduction (NEW)
pca:
  n_components_viz: 2
  n_components_variance: 50

# MANOVA statistical analysis (NEW)
manova:
  baseline_trials: 100
  random_seed: 42

# Gate conditions (MODIFIED for h-m2)
gates:
  primary_threshold: 0.5  # Cohen's d effect size
  secondary_threshold: 0.3  # Random baseline comparison
  alpha: 0.05

# Outputs (EXTENDED from h-m1)
outputs:
  data_dir: "./data"
  figures_dir: "./outputs/figures"
  results_file: "./outputs/results.json"
  report_file: "./outputs/report.md"
  
  # Embedding checkpoints
  chosen_embeddings_file: "chosen_embeddings.npy"
  rejected_embeddings_file: "rejected_embeddings.npy"
  pca_projection_file: "pca_2d_projection.npy"
  
  # Required figures
  gate_metrics_figure: "gate_metrics.png"
  pca_scatter_figure: "pca_scatter.png"
  effect_size_distribution_figure: "effect_size_distribution.png"
  variance_explained_figure: "variance_explained.png"
  distance_heatmap_figure: "distance_heatmap.png"

# Logging (INHERITED)
logging:
  level: "INFO"
  format: "simple"
```

---

## E-1: Data Loading Configuration

**Complexity:** 7/20, **Budget:** Included in epic scope

### Configuration Parameters

```yaml
dataset:
  name: "Anthropic/hh-rlhf"
  split: "train"
  max_samples: null  # Full dataset
  cache_dir: "./data/hf_cache"
```

**Rationale:** Uses full 160K+ dataset (no sampling) for maximum statistical power.

---

## E-2: RoBERTa Embedding Extraction Configuration

**Complexity:** 12/20, **Budget:** Included in epic scope

### Configuration Parameters

```yaml
embedding:
  model_name: "roberta-base"
  batch_size: 32
  max_length: 512
  device: "cuda"
  checkpoint_path: "./data/embeddings/"
```

**Rationale for Values:**
- `batch_size: 32` - Standard batch size for RoBERTa-base on 4GB GPU
- `max_length: 512` - RoBERTa maximum sequence length
- `device: "cuda"` - GPU acceleration for ~2-3 hour runtime vs ~10+ hours CPU

---

## E-3: PCA Dimensionality Reduction Configuration

**Complexity:** 8/20, **Budget:** Included in epic scope

### Configuration Parameters

```yaml
pca:
  n_components_viz: 2
  n_components_variance: 50
```

**Rationale:**
- `n_components_viz: 2` - Standard 2D visualization
- `n_components_variance: 50` - Sufficient for variance analysis (50/768 ≈ 6.5% of dimensions)

---

## E-4: MANOVA Statistical Analysis Configuration

**Complexity:** 10/20, **Budget:** Included in epic scope

### Configuration Parameters

```yaml
manova:
  baseline_trials: 100
  random_seed: 42

gates:
  primary_threshold: 0.5  # Cohen's d
  secondary_threshold: 0.3
  alpha: 0.05
```

**Rationale:**
- `baseline_trials: 100` - Standard for bootstrap baseline estimation
- `primary_threshold: 0.5` - Medium-to-large effect per Cohen (1988)
- `secondary_threshold: 0.3` - Small effect threshold

---

## E-5: Gate Metrics Visualization Configuration

**Complexity:** 6/20, **Budget:** Included in epic scope

### Configuration Parameters

```yaml
outputs:
  gate_metrics_figure: "gate_metrics.png"
```

No additional parameters needed - bar chart uses gate thresholds from main config.

---

## E-6: Additional Visualizations Configuration

**Complexity:** 9/20, **Budget:** Included in epic scope

### Configuration Parameters

```yaml
outputs:
  pca_scatter_figure: "pca_scatter.png"
  effect_size_distribution_figure: "effect_size_distribution.png"
  variance_explained_figure: "variance_explained.png"
  distance_heatmap_figure: "distance_heatmap.png"
```

All figures use default matplotlib/seaborn styling - no customization needed for PoC.

---

## E-7: Experiment Orchestration Configuration

**Complexity:** 10/20, **Budget:** Included in epic scope

### Configuration Parameters

All configuration parameters from sections above are accessed by main orchestrator.

---

## Configuration Loading Pattern

### Config Loader (Reused from h-m1)

```python
import yaml
from typing import Dict, Any
from pathlib import Path

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config.yaml
    
    Returns:
        Dict with all configuration parameters
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def resolve_paths(config: Dict[str, Any]) -> Dict[str, Path]:
    """Resolve output paths from config."""
    outputs = config["outputs"]
    
    paths = {
        "data_dir": Path(outputs["data_dir"]),
        "figures_dir": Path(outputs["figures_dir"]),
        "results_file": Path(outputs["results_file"]),
        "report_file": Path(outputs["report_file"]),
        "chosen_embeddings": Path(outputs["data_dir"]) / outputs["chosen_embeddings_file"],
        "rejected_embeddings": Path(outputs["data_dir"]) / outputs["rejected_embeddings_file"],
        "pca_projection": Path(outputs["data_dir"]) / outputs["pca_projection_file"]
    }
    
    # Create directories
    paths["data_dir"].mkdir(parents=True, exist_ok=True)
    paths["figures_dir"].mkdir(parents=True, exist_ok=True)
    
    return paths
```

---

## Configuration Usage Example

### In Main Experiment Runner

```python
import yaml
import torch
from transformers import RobertaTokenizer, RobertaModel
from typing import Dict, Any

def run_h_m2_experiment(config_path: str = "config.yaml") -> Dict:
    """Main experiment orchestration."""
    config = load_config(config_path)
    paths = resolve_paths(config)
    
    # Set random seed
    seed = config["experiment"]["seed"]
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    # 1. Load dataset
    dataset = load_dataset(
        config["dataset"]["name"],
        split=config["dataset"]["split"],
        cache_dir=config["dataset"]["cache_dir"]
    )
    max_samples = config["dataset"]["max_samples"]
    if max_samples:
        dataset = dataset.select(range(max_samples))
    
    chosen_texts, rejected_texts = extract_response_pairs(dataset)
    
    # 2. Extract embeddings
    device = config["embedding"]["device"]
    model_name = config["embedding"]["model_name"]
    batch_size = config["embedding"]["batch_size"]
    max_length = config["embedding"]["max_length"]
    
    tokenizer = RobertaTokenizer.from_pretrained(model_name)
    model = RobertaModel.from_pretrained(model_name).to(device)
    model.eval()
    
    chosen_embeddings = extract_embeddings(
        chosen_texts, model, tokenizer, batch_size, max_length, device
    )
    rejected_embeddings = extract_embeddings(
        rejected_texts, model, tokenizer, batch_size, max_length, device
    )
    
    # Save checkpoints
    np.save(paths["chosen_embeddings"], chosen_embeddings)
    np.save(paths["rejected_embeddings"], rejected_embeddings)
    
    # 3. Apply PCA
    n_viz = config["pca"]["n_components_viz"]
    chosen_2d, rejected_2d, pca_model = apply_pca_reduction(
        chosen_embeddings, rejected_embeddings, n_components=n_viz
    )
    
    # 4. Compute MANOVA effect size
    cohens_d = compute_manova_effect_size(chosen_embeddings, rejected_embeddings)
    
    # 5. Compute random baseline
    baseline_trials = config["manova"]["baseline_trials"]
    baseline_seed = config["manova"]["random_seed"]
    baseline_d = baseline_random_separation(
        np.vstack([chosen_embeddings, rejected_embeddings]),
        n_trials=baseline_trials,
        seed=baseline_seed
    )
    
    # 6. Gate decision
    primary_threshold = config["gates"]["primary_threshold"]
    secondary_threshold = config["gates"]["secondary_threshold"]
    
    gate_passed = (
        cohens_d >= primary_threshold and
        cohens_d > secondary_threshold
    )
    
    # 7. Generate visualizations
    generate_all_figures(
        cohens_d=cohens_d,
        baseline_d=np.mean(baseline_d),
        threshold=primary_threshold,
        chosen_2d=chosen_2d,
        rejected_2d=rejected_2d,
        pca_model=pca_model,
        figures_dir=paths["figures_dir"],
        config=config
    )
    
    # 8. Save results
    results = {
        "experiment": {
            "hypothesis_id": config["experiment"]["hypothesis_id"],
            "timestamp": datetime.now().isoformat()
        },
        "metrics": {
            "cohens_d": float(cohens_d),
            "baseline_d_mean": float(np.mean(baseline_d)),
            "baseline_d_std": float(np.std(baseline_d))
        },
        "gate": {
            "decision": "PASS" if gate_passed else "FAIL",
            "primary_threshold": primary_threshold,
            "secondary_threshold": secondary_threshold
        }
    }
    
    with open(paths["results_file"], 'w') as f:
        json.dump(results, f, indent=2)
    
    return results
```

---

## Reproducibility Configuration

### Random Seed Management

```yaml
experiment:
  seed: 42

manova:
  random_seed: 42
```

**Usage:**
```python
import torch
import numpy as np
import random

seed = config["experiment"]["seed"]
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(seed)
```

---

## GPU Configuration

### Device Selection

```yaml
embedding:
  device: "cuda"
```

**Before running experiment:**
```bash
# Check available GPUs
nvidia-smi

# Set single GPU (REQUIRED)
export CUDA_VISIBLE_DEVICES=0  # Use empty GPU
```

**In Python:**
```python
import torch

device = config["embedding"]["device"]
if device == "cuda" and not torch.cuda.is_available():
    print("WARNING: CUDA requested but not available, falling back to CPU")
    device = "cpu"
    config["embedding"]["device"] = "cpu"
```

---

## Output Directory Structure

```
h-m2/
├── code/
│   ├── config.yaml                 # THIS FILE
│   ├── src/
│   │   ├── data/loader.py
│   │   ├── embeddings/extractor.py
│   │   ├── analysis/pca.py
│   │   ├── analysis/manova.py
│   │   └── visualization/plots.py
│   └── main.py
├── data/
│   ├── hf_cache/                   # HuggingFace cache
│   ├── chosen_embeddings.npy       # (N, 768)
│   ├── rejected_embeddings.npy     # (N, 768)
│   └── pca_2d_projection.npy       # (2N, 2)
└── outputs/
    ├── figures/
    │   ├── gate_metrics.png
    │   ├── pca_scatter.png
    │   ├── effect_size_distribution.png
    │   ├── variance_explained.png
    │   └── distance_heatmap.png
    ├── results.json
    └── report.md
```

---

## Configuration Differences from h-m1

### New Sections (h-m2 specific)

| Section | Purpose |
|---------|---------|
| `embedding` | RoBERTa model configuration |
| `pca` | Dimensionality reduction parameters |
| `manova` | Statistical analysis configuration |

### Modified Sections

| Parameter | h-m1 | h-m2 | Reason |
|-----------|------|------|--------|
| `gates.primary_threshold` | 0.70 (κ) | 0.5 (Cohen's d) | Different metric |
| `gates.secondary_threshold` | 0.75 (agreement) | 0.3 (d) | Random baseline comparison |
| `dataset.max_samples` | 300 | null (full) | Full dataset for clustering |

### Removed Sections

- `training` - Not applicable (no annotation study)
- `annotation` - Not applicable (no human annotators)
- `sampling` - Using full dataset (no stratified sampling)

---

## Dependencies Summary

### Configuration Dependencies

```python
import yaml              # Config file parsing
from pathlib import Path # Path resolution
from typing import Dict, Any, Tuple
import numpy as np       # For checkpoint loading
import torch             # For device management
```

**No additional config libraries needed** - same minimal approach as h-m1.

---

## Self-Validation Checklist

### Quick Checks
- [x] ONE format only (Hardcoded YAML - consistent with h-m1)
- [x] No ASCII diagrams
- [x] Codebase Analysis (Serena) section included
- [x] Applied: KB-003-MinimalConfig noted
- [x] Rationale only for non-standard values
- [x] EXISTENCE tier: Single fixed configuration (no variations)
- [x] Total length < 400 lines
- [x] Inherited Configuration section with verified field names

### Base Hypothesis Checks
- [x] Read actual config from h-m1/code/config.yaml
- [x] Field names verified from actual implementation (YAML dict keys)
- [x] Extended configuration clearly separated from inherited
- [x] Reused patterns (outputs, logging, seed management)

### EXISTENCE Tier Checks
- [x] No hyperparameter variations
- [x] No ablation configs
- [x] Single seed (42)
- [x] Fixed batch_size, max_length, n_components
- [x] Default values from research (RoBERTa-base, Cohen's d=0.5)

---

**Document Status:** COMPLETE  
**Next Phase:** Phase 4 Implementation  
**Applied Patterns:** KB-003-MinimalConfig, EXISTENCE tier (PoC)  
**Base Hypothesis:** h-m1 (config structure verified and extended)
