# Configuration: h-m1 — Cross-Distribution Stability of MLP Activation Sparsity Profiles

**Date:** 2026-05-08
**Hypothesis Type:** MECHANISM (INCREMENTAL — extends h-e1)

Applied: Standard PyTorch dataclass config pattern (h-e1 extension)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-e1)
**Status**: config classes verified from base code
**Config Files Found**: `docs/youra_research/20260508_scope/h-e1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-e1/code/config.py (VERIFIED from actual implementation)
@dataclass
class ExperimentConfig:
    # Model settings
    model_name: str = "meta-llama/Meta-Llama-3-8B"   # overridden in h-m1
    n_layers: int = 32
    torch_dtype: str = "float16"
    device_map: str = "auto"

    # Experiment settings
    n_samples: int = 512
    batch_size: int = 8
    seed: int = 42
    epsilons: List[float] = field(default_factory=lambda: [0.001, 0.01, 0.05, 0.1])
    primary_epsilon: float = 0.01

    # Sequence lengths (h-e1 has both short/long; h-m1 uses single max_length)
    short_length: int = 128
    long_length: int = 512

    # Dataset identifiers
    alpaca_dataset: str = "tatsu-lab/alpaca"
    wikitext_dataset: str = "wikitext"
    wikitext_config: str = "wikitext-103-raw-v1"

    # Output paths
    figures_dir: str = "h-e1/figures"
    results_dir: str = "h-e1/results"

    # Gate thresholds
    cv_threshold: float = 0.3
    tau_threshold: float = 0.6
```

**Verified from**: `h-e1/code/config.py` (actual implementation)

**Key differences in h-m1**:
- `model_name` overridden to `"meta-llama/Llama-3.1-8B"`
- `short_length`/`long_length` replaced by single `max_length: int = 512`
- `results_dir` replaced by `results_path` (single JSON file)
- `cv_threshold` replaced by `icc_threshold` (h-m1 uses ICC, not CV)
- Added: `sst2_dataset`, `sst2_config_name`, `mnli_dataset`, `mnli_config_name`, `mnli_split`, `sep_token`

---

## A-E2: Config Module [Complexity: 7, Budget: 0 subtasks]

**Applied**: Standard PyTorch defaults

### Configuration (Python Dataclass)

```python
# h-m1/code/config.py
from dataclasses import dataclass, field
from typing import List


@dataclass
class ExperimentConfig:
    """Configuration for H-M1 cross-distribution activation sparsity measurement."""

    # Model settings
    model_name: str = "meta-llama/Llama-3.1-8B"  # Non-standard: upgraded from Meta-Llama-3-8B per PRD FR-2.1
    n_layers: int = 32
    torch_dtype: str = "float16"
    device_map: str = "auto"

    # Experiment settings
    n_samples: int = 512
    batch_size: int = 8
    seed: int = 42
    epsilons: List[float] = field(default_factory=lambda: [0.001, 0.01, 0.05, 0.1])
    primary_epsilon: float = 0.01

    # Sequence length (single value; h-e1 used short_length/long_length)
    max_length: int = 512

    # Dataset identifiers — alpaca/wikitext inherited from h-e1
    alpaca_dataset: str = "tatsu-lab/alpaca"
    wikitext_dataset: str = "wikitext"
    wikitext_config: str = "wikitext-103-raw-v1"
    sst2_dataset: str = "nyu-mll/glue"
    sst2_config_name: str = "sst2"
    mnli_dataset: str = "nyu-mll/glue"
    mnli_config_name: str = "mnli"
    mnli_split: str = "validation_matched"  # Non-standard: MNLI uses validation_matched not validation
    sep_token: str = " [SEP] "              # Separator for MNLI premise+hypothesis concatenation

    # Output paths
    figures_dir: str = "h-m1/figures"
    results_path: str = "h-m1/experiment_results.json"

    # Gate thresholds
    icc_threshold: float = 0.75  # Non-standard: ICC(3,k) gate condition from h-m1 PRD
    tau_threshold: float = 0.6   # Inherited from h-e1

    def __post_init__(self):
        assert self.n_samples >= 512, "n_samples must be >= 512"
        assert self.n_samples % self.batch_size == 0, (
            f"n_samples ({self.n_samples}) must be divisible by batch_size ({self.batch_size})"
        )
        assert self.primary_epsilon in self.epsilons, (
            f"primary_epsilon ({self.primary_epsilon}) must be in epsilons list {self.epsilons}"
        )
        assert 0.0 < self.icc_threshold < 1.0, "icc_threshold must be in (0, 1)"
        assert 0.0 < self.tau_threshold <= 1.0, "tau_threshold must be in (0, 1]"
        assert self.torch_dtype in ("float16", "bfloat16", "float32"), (
            f"torch_dtype '{self.torch_dtype}' not supported"
        )
```

---

## YAML Schema

```yaml
# h-m1/code/config.yaml
model:
  name: meta-llama/Llama-3.1-8B
  n_layers: 32
  torch_dtype: float16
  device_map: auto

experiment:
  n_samples: 512
  batch_size: 8
  seed: 42
  primary_epsilon: 0.01
  epsilons: [0.001, 0.01, 0.05, 0.1]
  max_length: 512

datasets:
  alpaca:
    name: tatsu-lab/alpaca
  wikitext:
    name: wikitext
    config: wikitext-103-raw-v1
  sst2:
    name: nyu-mll/glue
    config_name: sst2
    split: validation
  mnli:
    name: nyu-mll/glue
    config_name: mnli
    split: validation_matched
    sep_token: " [SEP] "

gate_thresholds:
  icc_threshold: 0.75
  tau_threshold: 0.6

output:
  figures_dir: h-m1/figures
  results_path: h-m1/experiment_results.json
```

---

## Requirements

```
# h-m1/code/requirements.txt
torch>=2.0
transformers>=4.40
datasets>=2.18
numpy>=1.24
scipy>=1.11
pingouin>=0.5.4
pandas>=2.0
matplotlib>=3.7
seaborn>=0.12
```

---

## Environment Setup Instructions

### Step 1: GPU Selection
```bash
nvidia-smi
# Identify GPU with lowest memory usage
export CUDA_VISIBLE_DEVICES=<empty_gpu_id>   # e.g., export CUDA_VISIBLE_DEVICES=0
```

### Step 2: Install Dependencies
```bash
cd /path/to/h-m1/code
pip install -r requirements.txt
```

### Step 3: Verify HuggingFace Model Access
```bash
# Requires HuggingFace token with access to meta-llama/Llama-3.1-8B
huggingface-cli login
python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('meta-llama/Llama-3.1-8B')"
```

### Step 4: Pre-download Datasets
```bash
python -c "
from datasets import load_dataset
load_dataset('tatsu-lab/alpaca', split='train')
load_dataset('wikitext', 'wikitext-103-raw-v1', split='train')
load_dataset('nyu-mll/glue', 'sst2', split='validation')
load_dataset('nyu-mll/glue', 'mnli', split='validation_matched')
print('All datasets downloaded.')
"
```

---

## Validation Config

Config validation is enforced in `__post_init__`:

| Field | Constraint | Error if violated |
|-------|-----------|-------------------|
| `n_samples` | >= 512 | AssertionError |
| `batch_size` | divides n_samples evenly | AssertionError |
| `primary_epsilon` | must be in `epsilons` list | AssertionError |
| `icc_threshold` | in (0, 1) exclusive | AssertionError |
| `tau_threshold` | in (0, 1] | AssertionError |
| `torch_dtype` | one of float16/bfloat16/float32 | AssertionError |
