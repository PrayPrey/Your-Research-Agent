# H-M3 Configuration Design

**Date:** 2026-05-08
**Hypothesis:** H-M3 (Sparsity-Rank Sensitivity Correlation)
**Phase:** 3 - Configuration

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m3 incremental from h-m2)
**Status**: config classes verified from base code (h-m2/code/config.py)
**Config Files Found**: `/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-m2/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual h-m2 Code)

```python
# From: h-m2/code/config.py (ACTUAL CODE — verified)
@dataclass
class ExperimentConfig:
    # Model settings
    model_name: str = "meta-llama/Llama-3.1-8B"
    n_layers: int = 32
    torch_dtype: str = "float16"
    device_map: str = "auto"

    # Experiment settings
    n_samples: int = 512
    batch_size: int = 8
    seed: int = 42
    max_length: int = 512

    epsilons: List[float] = field(default_factory=lambda: [0.001, 0.01, 0.05, 0.1])
    primary_epsilon: float = 0.01

    # Dataset identifiers
    alpaca_dataset: str = "tatsu-lab/alpaca"
    wikitext_dataset: str = "wikitext"
    wikitext_config: str = "wikitext-103-raw-v1"

    # Output paths
    figures_dir: str = "...h-m2/figures"
    results_path: str = "...h-m2/experiment_results.json"

    # Gate thresholds (h-m2 specific — NOT reused in h-m3)
    cv_threshold: float = 0.3
    cv_pass_min_count: int = 3
    cross_epsilon_tau_threshold: float = 0.7
    cross_dist_tau_threshold: float = 0.6
```

**Fields inherited by h-m3**: `model_name`, `n_layers`, `torch_dtype`, `max_length`
**Fields replaced**: `torch_dtype` changes from `"float16"` to `"bfloat16"` (H100 NVL optimized)
**Fields dropped**: `epsilons`, `primary_epsilon`, `alpaca_dataset`, `wikitext_dataset`, `wikitext_config`, all cv/tau gate thresholds
**Fields added**: LoRA training params, AdaLoRA params, sensitivity sweep params, new gate thresholds

---

## C-A2-1: LoRA Training Config Schema [Complexity: High, Budget: 1]

Applied: HF PEFT LoRA rank_pattern API

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import yaml


@dataclass
class ExperimentConfig:
    """H-M3: Sparsity-Rank Sensitivity Correlation experiment config."""

    # Model settings (inherited from h-m2, torch_dtype updated for H100)
    model_name: str = "meta-llama/Llama-3.1-8B"
    n_layers: int = 32
    torch_dtype: str = "bfloat16"  # Non-standard: h-m2 used float16; bfloat16 for H100 NVL
    local_files_only: bool = True
    device_map: str = "auto"
    max_length: int = 512

    # LoRA training (uniform reference)
    lora_r: int = 16
    lora_alpha: int = 16
    target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ])
    lora_dropout: float = 0.0

    # Optimizer
    lr: float = 2e-4
    weight_decay: float = 0.01
    adam_beta1: float = 0.9
    adam_beta2: float = 0.999

    # Schedule
    warmup_ratio: float = 0.03

    # Training loop
    batch_size: int = 16
    num_epochs: int = 3
    gradient_accumulation_steps: int = 1
    gradient_checkpointing: bool = False  # Enable if OOM

    # Seeds
    seeds: List[int] = field(default_factory=lambda: [42, 43, 44, 45, 46])

    # Sensitivity sweep
    delta_r: int = 2            # Rank reduction per perturbed layer
    delta_r_fallback: int = 4   # Non-standard: used if <5 layers show >=0.5% drop at delta_r=2
    sensitive_drop_threshold: float = 0.005  # 0.5% accuracy drop = sensitive layer

    # Tasks
    tasks: List[str] = field(default_factory=lambda: ["sst2", "mnli"])

    def __post_init__(self):
        assert self.n_layers == 32, "LLaMA-3.1-8B must have 32 layers"
        assert self.torch_dtype in ("float16", "bfloat16", "float32")
        assert self.delta_r in (2, 4), "delta_r must be 2 or 4"
        assert self.delta_r_fallback in (2, 4), "delta_r_fallback must be 2 or 4"
        assert len(self.seeds) >= 1

    def to_yaml(self, path: str) -> None:
        import dataclasses
        d = dataclasses.asdict(self)
        with open(path, "w") as f:
            yaml.dump(d, f, default_flow_style=False)

    @classmethod
    def from_yaml(cls, path: str) -> "ExperimentConfig":
        with open(path) as f:
            d = yaml.safe_load(f)
        return cls(**d)
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-A2-1 | LoRA Training Config | ExperimentConfig dataclass with YAML serialization |

---

## C-A4-1: AdaLoRA Config Schema [Complexity: Medium, Budget: 1]

Applied: AdaLoRA ICLR 2023 (hf.co/papers/2305.14314)

```python
@dataclass
class AdaLoRAConfig:
    """AdaLoRA hyperparameters for H-M3 reference run (60% budget)."""

    # Budget: target_r = floor(0.60 * lora_r) = floor(0.60 * 16) = 9
    target_r: int = 9
    init_r: int = 16

    # Warmup/cooldown schedule (steps)
    tinit: int = 100    # Steps before rank pruning begins
    tfinal: int = 1500  # Steps at which rank budget is fixed
    deltaT: int = 10    # Rank update frequency (every N steps)

    # EMA smoothing for importance scores
    beta1: float = 0.85
    beta2: float = 0.85

    # Orthogonality regularization weight
    orth_reg_weight: float = 0.5

    # Budget specification
    total_budget_pct: float = 0.60  # 60% of uniform r=16 budget

    def __post_init__(self):
        assert self.target_r == int(self.total_budget_pct * 16), (
            f"target_r={self.target_r} must equal floor(total_budget_pct * 16)"
        )
        assert 0 < self.beta1 < 1 and 0 < self.beta2 < 1
        assert self.tinit < self.tfinal
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-A4-1 | AdaLoRA Config | AdaLoRAConfig dataclass with budget validation |

---

## C-A6-1: Gate Threshold Config [Complexity: Low, Budget: 1]

Applied: Standard PyTorch defaults (thresholds from 02c_experiment_brief.md)

```python
@dataclass
class GateConfig:
    """Gate evaluation thresholds for H-M3 MUST_WORK criteria."""

    # Pearson r: must be <= this value (negative correlation, sparsity vs sensitivity)
    pearson_r_threshold: float = -0.4

    # Kendall tau: must be >= this value (rank correlation, sparsity vs AdaLoRA allocation)
    kendall_tau_threshold: float = 0.4

    # Unique variance explained by sparsity in multiple regression (semipartial r²)
    unique_var_threshold: float = 0.20

    # Significance level for sparsity regression coefficient
    p_value_threshold: float = 0.05

    # Accuracy drop threshold to classify a layer as "sensitive"
    sensitive_drop_threshold: float = 0.005  # 0.5%

    # R6 fallback: if SST-2 has fewer sensitive layers than this, use MNLI-only gate
    r6_min_sensitive_layers: int = 5

    def gate_pass(
        self,
        pearson_r_sst2: float,
        pearson_r_mnli: float,
        kendall_tau_sst2: float,
        kendall_tau_mnli: float,
        unique_var_sparsity: float,
        p_value_sparsity: float,
        n_sensitive_sst2: int,
    ) -> bool:
        r6_fallback = n_sensitive_sst2 < self.r6_min_sensitive_layers
        if r6_fallback:
            gate_pearson = pearson_r_mnli <= self.pearson_r_threshold
            gate_tau = kendall_tau_mnli >= self.kendall_tau_threshold
        else:
            gate_pearson = (pearson_r_sst2 <= self.pearson_r_threshold and
                            pearson_r_mnli <= self.pearson_r_threshold)
            gate_tau = (kendall_tau_sst2 >= self.kendall_tau_threshold and
                        kendall_tau_mnli >= self.kendall_tau_threshold)
        gate_spectral = (unique_var_sparsity >= self.unique_var_threshold and
                         p_value_sparsity < self.p_value_threshold)
        return gate_pearson and gate_tau and gate_spectral
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-A6-1 | Gate Threshold Config | GateConfig with R6 fallback logic |

---

## C-A6-2: Paths and Output Config [Complexity: Low, Budget: 1]

Applied: Standard PyTorch defaults

```python
BASE = "/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope"

@dataclass
class PathConfig:
    """Path management for H-M3."""

    # Input: sparsity profiles from H-M2 (primary epsilon=0.01)
    h_m2_results_path: str = f"{BASE}/h-m2/experiment_results.json"

    # Local model cache (confirmed working in h-m2)
    model_cache_path: str = "~/.cache/huggingface/hub/models--meta-llama--Llama-3.1-8B"

    # Outputs
    figures_dir: str = f"{BASE}/h-m3/figures/"
    results_path: str = f"{BASE}/h-m3/experiment_results.json"
    validation_report_path: str = f"{BASE}/h-m3/04_validation.md"

    # Tasks
    tasks: List[str] = field(default_factory=lambda: ["sst2", "mnli"])
```

### Complete YAML Config (`config.yaml`)

```yaml
# H-M3 Experiment Config — copy to h-m3/code/config.yaml

# Model
model_name: "meta-llama/Llama-3.1-8B"
n_layers: 32
torch_dtype: "bfloat16"
local_files_only: true
device_map: "auto"
max_length: 512

# LoRA
lora_r: 16
lora_alpha: 16
target_modules:
  - q_proj
  - k_proj
  - v_proj
  - o_proj
  - gate_proj
  - up_proj
  - down_proj
lora_dropout: 0.0

# Optimizer
lr: 0.0002
weight_decay: 0.01
adam_beta1: 0.9
adam_beta2: 0.999
warmup_ratio: 0.03

# Training
batch_size: 16
num_epochs: 3
gradient_accumulation_steps: 1
gradient_checkpointing: false

# Seeds
seeds: [42, 43, 44, 45, 46]

# Sensitivity sweep
delta_r: 2
delta_r_fallback: 4
sensitive_drop_threshold: 0.005

# Tasks
tasks:
  - sst2
  - mnli

# AdaLoRA
adalora:
  target_r: 9       # floor(0.60 * 16)
  init_r: 16
  tinit: 100
  tfinal: 1500
  deltaT: 10
  beta1: 0.85
  beta2: 0.85
  orth_reg_weight: 0.5
  total_budget_pct: 0.60

# Gate thresholds
gate:
  pearson_r_threshold: -0.4
  kendall_tau_threshold: 0.4
  unique_var_threshold: 0.20
  p_value_threshold: 0.05
  sensitive_drop_threshold: 0.005
  r6_min_sensitive_layers: 5

# Paths
paths:
  h_m2_results_path: "/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-m2/experiment_results.json"
  model_cache_path: "~/.cache/huggingface/hub/models--meta-llama--Llama-3.1-8B"
  figures_dir: "/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-m3/figures/"
  results_path: "/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-m3/experiment_results.json"
  validation_report_path: "/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-m3/04_validation.md"
```

### Environment Variables

```bash
export CUDA_VISIBLE_DEVICES=0         # Single GPU (lowest memory usage)
export HF_HOME=~/.cache/huggingface   # Model cache root
```

### Validation Constraints

| Field | Constraint | Checked In |
|-------|-----------|------------|
| `delta_r` | must be 2 or 4 | `ExperimentConfig.__post_init__` |
| `n_layers` | must be 32 | `ExperimentConfig.__post_init__` |
| `torch_dtype` | float16, bfloat16, or float32 | `ExperimentConfig.__post_init__` |
| `target_r` | must equal floor(0.60 * 16) = 9 | `AdaLoRAConfig.__post_init__` |
| `tinit < tfinal` | AdaLoRA schedule validity | `AdaLoRAConfig.__post_init__` |

### Example CLI Invocation

```bash
# Run full H-M3 experiment
cd /home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-m3/code/
export CUDA_VISIBLE_DEVICES=0
export HF_HOME=~/.cache/huggingface
python run_experiment.py --config config.yaml

# Override single param (e.g., dry run with fewer seeds)
python run_experiment.py --config config.yaml --seeds "[42]" --num_epochs 1

# Use delta_r fallback manually
python run_experiment.py --config config.yaml --delta_r 4
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-A6-2 | Paths and Output Config | PathConfig dataclass + config.yaml + CLI invocation |

---

## Summary

| Config Class | File | Purpose |
|-------------|------|---------|
| `ExperimentConfig` | config.py | Main experiment config (LoRA, training, seeds, sweep) |
| `AdaLoRAConfig` | config.py | AdaLoRA reference run hyperparameters |
| `GateConfig` | config.py | Gate thresholds + R6 fallback logic |
| `PathConfig` | config.py | Input/output path management |
| `config.yaml` | config.yaml | YAML serialization of all four configs |
