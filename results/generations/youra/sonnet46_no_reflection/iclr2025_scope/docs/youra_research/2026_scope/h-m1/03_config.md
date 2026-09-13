# Config: H-M1 JointLoRA-KV

Applied: PEFT LoRA separate param groups pattern (HuggingFace PEFT)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 extends H-E1)
**Status**: config classes verified from base code (`h-e1/code/config.py`)
**Config Files Found**: `h-e1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis H-E1)

Fields verified from actual `h-e1/code/config.py`:

```python
# From: h-e1/code/config.py (ACTUAL CODE — verified field names)
@dataclass
class ExperimentConfig:
    # Inherited unchanged in H-M1:
    attn_impl: str = "eager"
    dtype: str = "float16"
    num_query_heads: int = 32
    num_kv_heads: int = 8
    num_layers: int = 32
    kv_repeat: int = 4           # num_query_heads // num_kv_heads
    max_seq_len: int = 512
    hypothesis_folder: str = "."
    results_dir: str = "results"
    figures_dir: str = "figures"
    locret_checkpoint: str = "hyx21/Locret-llama-3.1-8B-instruct"

    # H-E1 only (NOT inherited — replaced in H-M1):
    # lora_base_model -> renamed to base_model in H-M1
    # lora_checkpoint -> removed (H-M1 trains LoRA from scratch)
    # dataset_id, dataset_config, primary_n, extended_n -> replaced by GLUE multi-task setup
    # seed: int = 42 -> replaced by seeds: List[int] = [42, 123, 456]
    # aggregation_method, spearman_alternative -> removed (different eval)
    # device_map: str = "auto" -> removed
```

**New in H-M1** (not in H-E1): `lora_r`, `lora_alpha`, `lora_target_modules`, `lora_dropout`, `head_dim`, `lora_lr`, `locret_lr`, `weight_decay`, `adam_betas`, `adam_eps`, `warmup_ratio`, `max_grad_norm`, `per_device_batch_size`, `grad_accum_steps`, `epochs_mnli`, `epochs_sst2`, `epochs_qnli`, `seeds`, `budget_ratio`, `budget_ratios_sweep`, `glue_tasks`, `longbench_tasks`, `longbench_max_len`.

---

## A-1: ExperimentConfig [Complexity: 2, Budget: 2]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List
import os

@dataclass
class ExperimentConfig:
    # Model settings (locret_checkpoint inherited from H-E1)
    base_model: str = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    locret_checkpoint: str = "hyx21/Locret-llama-3.1-8B-instruct"
    attn_impl: str = "eager"          # inherited from H-E1
    dtype: str = "float16"            # inherited from H-E1

    # LoRA settings
    lora_r: int = 16
    lora_alpha: int = 32              # standard 2x rank
    lora_target_modules: List[str] = field(default_factory=lambda: ["q_proj", "k_proj", "v_proj"])
    lora_dropout: float = 0.1

    # GQA architecture constants (inherited from H-E1, + head_dim new)
    num_query_heads: int = 32         # inherited from H-E1
    num_kv_heads: int = 8             # inherited from H-E1
    num_layers: int = 32              # inherited from H-E1
    head_dim: int = 128
    kv_repeat: int = 4                # inherited from H-E1 (32//8)

    # Training hyperparameters
    lora_lr: float = 1e-4
    locret_lr: float = 5e-4           # non-standard: Locret heads converge faster than LoRA
    weight_decay: float = 0.01
    adam_betas: tuple = (0.9, 0.999)
    adam_eps: float = 1e-8
    warmup_ratio: float = 0.06
    max_grad_norm: float = 1.0
    per_device_batch_size: int = 8
    grad_accum_steps: int = 4         # effective batch = 32
    epochs_mnli: int = 3
    epochs_sst2: int = 5
    epochs_qnli: int = 5
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456])

    # KV budget
    budget_ratio: float = 0.5         # fixed controlled variable per Phase 2B
    budget_ratios_sweep: List[float] = field(default_factory=lambda: [0.3, 0.5, 0.7])

    # GLUE settings
    glue_tasks: List[str] = field(default_factory=lambda: ["mnli", "sst2", "qnli"])
    max_seq_len: int = 512            # inherited from H-E1

    # LongBench settings
    longbench_tasks: List[str] = field(default_factory=lambda: ["narrativeqa", "qasper", "multifieldqa_en"])
    longbench_max_len: int = 15360

    # Output paths (inherited from H-E1)
    hypothesis_folder: str = "."
    results_dir: str = "results"
    figures_dir: str = "figures"

    def get_epochs(self, task: str) -> int:
        """Return epoch count for given GLUE task."""
        return {"mnli": self.epochs_mnli, "sst2": self.epochs_sst2, "qnli": self.epochs_qnli}[task]

    def get_results_path(self, tag: str) -> str:
        """Return path for results JSON file."""
        return os.path.join(self.hypothesis_folder, self.results_dir, f"{tag}.json")

    def get_figures_dir(self) -> str:
        """Return absolute figures directory path."""
        return os.path.join(self.hypothesis_folder, self.figures_dir)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | ExperimentConfig dataclass | Full dataclass with all fields and helper methods |
| C-1-2 | Config validation | Assert invariants at runtime |

---

## A-2: YAML Configuration [Complexity: 1, Budget: 1]

### experiment.yaml

```yaml
# H-M1 Experiment Configuration

model:
  base_model: "meta-llama/Meta-Llama-3.1-8B-Instruct"
  locret_checkpoint: "hyx21/Locret-llama-3.1-8B-instruct"
  attn_implementation: "eager"
  dtype: "float16"

lora:
  r: 16
  alpha: 32
  target_modules: ["q_proj", "k_proj", "v_proj"]
  dropout: 0.1
  task_type: "CAUSAL_LM"

locret:
  num_layers: 32
  num_kv_heads: 8
  num_query_heads: 32
  head_dim: 128
  kv_repeat: 4
  retaining_head_hidden_dim: 1024

training:
  lora_lr: 1.0e-4
  locret_lr: 5.0e-4
  weight_decay: 0.01
  adam_betas: [0.9, 0.999]
  adam_eps: 1.0e-8
  warmup_ratio: 0.06
  max_grad_norm: 1.0
  per_device_batch_size: 8
  grad_accum_steps: 4
  effective_batch_size: 32
  epochs:
    mnli: 3
    sst2: 5
    qnli: 5
  seeds: [42, 123, 456]

kv_budget:
  budget_ratio: 0.5
  budget_ratios_sweep: [0.3, 0.5, 0.7]

glue:
  tasks: ["mnli", "sst2", "qnli"]
  max_seq_len: 512
  validation_splits:
    mnli: "validation_matched"
    sst2: "validation"
    qnli: "validation"
  num_labels:
    mnli: 3
    sst2: 2
    qnli: 2

longbench:
  tasks: ["narrativeqa", "qasper", "multifieldqa_en"]
  max_len: 15360
  split: "test"

output:
  hypothesis_folder: ".."
  results_dir: "results"
  figures_dir: "figures"

hardware:
  cuda_visible_devices: "0"
  precision: "float16"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | experiment.yaml | YAML mirror of ExperimentConfig defaults |

---

## A-3: Hyperparameter Justification [Complexity: 1, Budget: 1]

| Hyperparameter | Value | Source | Justification |
|----------------|-------|--------|---------------|
| lora_r | 16 | H-E1 proven | Enables controlled comparison with H-E1 |
| lora_alpha | 32 | H-E1 proven | Standard 2x rank |
| lora_lr | 1e-4 | PEFT GLUE | Standard LoRA GLUE fine-tuning LR |
| locret_lr | 5e-4 | Locret paper | Faster convergence for MLP retaining heads |
| budget_ratio | 0.5 | Phase 2B | Fixed controlled variable |
| per_device_batch_size | 8 | PEFT GLUE | Fits H100 80GB in float16 |
| grad_accum_steps | 4 | PEFT GLUE | Effective batch = 32 |
| warmup_ratio | 0.06 | PEFT GLUE | Standard 6% warmup |
| seeds | [42,123,456] | Phase 2B | 3-seed robustness check |
| budget_ratios_sweep | [0.3,0.5,0.7] | Phase 2B | Sensitivity analysis range |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Hyperparameter table | Justified values for all non-obvious settings |

---

## A-4: Config Validation [Complexity: 1, Budget: 1]

```python
def validate_config(cfg: ExperimentConfig) -> None:
    """Assert config invariants. Call at experiment start."""
    assert cfg.kv_repeat == cfg.num_query_heads // cfg.num_kv_heads, \
        f"kv_repeat must equal num_query_heads // num_kv_heads"
    assert 0.0 < cfg.budget_ratio < 1.0, "budget_ratio must be in (0, 1)"
    assert len(set(cfg.seeds)) == len(cfg.seeds), "seeds must be unique"
    assert cfg.lora_lr < cfg.locret_lr, \
        "locret_lr must exceed lora_lr (Locret heads learn faster)"
    assert all(0.0 < r < 1.0 for r in cfg.budget_ratios_sweep), \
        "all budget_ratios_sweep values must be in (0, 1)"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | validate_config function | Runtime invariant checks |

---

## A-5: Environment Setup [Complexity: 1, Budget: 1]

```bash
# Minimum package versions (from PRD Section 7.1)
torch>=2.0.0
transformers>=4.40.0
peft>=0.10.0
datasets>=2.18.0
evaluate>=0.4.0
accelerate>=0.28.0
numpy>=1.24.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
pyyaml>=6.0
tqdm>=4.65.0
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | requirements.txt | Minimum pinned package versions |

---

## Subtask Summary

Total budget: 8 subtasks used: 6/8

| ID | Task | Subtasks |
|----|------|----------|
| C-1-1 | ExperimentConfig dataclass | 1 |
| C-1-2 | Config validation function | 1 |
| C-2-1 | experiment.yaml | 1 |
| C-3-1 | Hyperparameter justification table | 1 |
| C-4-1 | validate_config function | 1 |
| C-5-1 | requirements.txt | 1 |
