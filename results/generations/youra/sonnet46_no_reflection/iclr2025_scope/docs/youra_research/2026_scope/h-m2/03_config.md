# Config: H-M2 — JointLoRA-KV Joint Training

**Hypothesis:** Joint end-to-end training of LoRA adapter + Locret retaining head in single backward pass
**Type:** MECHANISM (FULL tier)
**Date:** 2026-05-20

---

## Applied Patterns

Applied: HuggingFace PEFT LoRA parameter isolation (name filter via "lora_" in param name)
Applied: Dual-parameter-group AdamW optimizer (diffusers SDXL dual-LoRA pattern)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-1 (Config submodule): ExperimentConfig Dataclass [Complexity: 9, Budget: 2 subtasks]

**Applied**: Standard PyTorch/HuggingFace PEFT dataclass defaults

### Configuration (Python Dataclass) — `h-m2/code/config.py`

```python
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import yaml


@dataclass
class ModelConfig:
    base_model: str = "meta-llama/Meta-Llama-3.1-8B"
    torch_dtype: str = "bfloat16"
    attn_implementation: str = "eager"


@dataclass
class LoRAConfig:
    r: int = 16
    lora_alpha: int = 32
    target_modules: List[str] = field(default_factory=lambda: ["q_proj", "k_proj", "v_proj"])
    lora_dropout: float = 0.05
    bias: str = "none"


@dataclass
class LocretConfig:
    hidden_dim: int = 1024
    n_heads: int = 8  # KV heads for GQA (LLaMA-3.1-8B has 8 KV heads)
    warm_init_checkpoint: Optional[str] = "hyx21/Locret-llama-3.1-8B-instruct"
    kv_budget_ratio: float = 0.5


@dataclass
class TrainingConfig:
    lora_lr: float = 1e-4
    locret_lr: float = 5e-4  # Non-standard: higher lr for retaining heads to catch up from warm init
    weight_decay: float = 0.01
    betas: Tuple[float, float] = (0.9, 0.999)
    eps: float = 1e-8
    warmup_ratio: float = 0.10
    lr_schedule: str = "cosine"
    batch_size: int = 8
    gradient_accumulation_steps: int = 4
    max_epochs: int = 3
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456])
    grad_clip_norm: float = 1.0


@dataclass
class DatasetConfig:
    glue_tasks: List[str] = field(default_factory=lambda: ["mnli", "sst2", "qnli"])
    longbench_tasks: List[str] = field(default_factory=lambda: ["narrativeqa", "qasper", "multifieldqa_en"])
    max_seq_len_glue: int = 512


@dataclass
class StabilityConfig:
    divergence_window: int = 100
    divergence_threshold: float = 2.0
    log_interval: int = 50


@dataclass
class PathConfig:
    output_dir: str = "h-m2/"
    checkpoint_dir: str = "h-m2/checkpoints/"
    figures_dir: str = "h-m2/figures/"
    results_dir: str = "h-m2/results/"


@dataclass
class ExperimentConfig:
    model: ModelConfig = field(default_factory=ModelConfig)
    lora: LoRAConfig = field(default_factory=LoRAConfig)
    locret: LocretConfig = field(default_factory=LocretConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    stability: StabilityConfig = field(default_factory=StabilityConfig)
    paths: PathConfig = field(default_factory=PathConfig)


# ── Validation ──────────────────────────────────────────────────────────────

def validate_config(cfg: ExperimentConfig) -> None:
    assert 0.0 < cfg.locret.kv_budget_ratio < 1.0, \
        f"kv_budget_ratio must be in (0,1), got {cfg.locret.kv_budget_ratio}"
    assert len(cfg.training.seeds) > 0, "seeds must be non-empty"
    assert cfg.training.batch_size > 0, "batch_size must be > 0"
    assert cfg.training.max_epochs > 0, "max_epochs must be > 0"
    assert cfg.training.grad_clip_norm > 0.0, "grad_clip_norm must be > 0"
    assert cfg.training.warmup_ratio >= 0.0 and cfg.training.warmup_ratio < 1.0, \
        f"warmup_ratio must be in [0,1), got {cfg.training.warmup_ratio}"
    assert cfg.lora.r > 0, "LoRA rank r must be > 0"
    assert cfg.stability.divergence_threshold > 1.0, \
        f"divergence_threshold must be > 1.0, got {cfg.stability.divergence_threshold}"
    assert len(cfg.dataset.glue_tasks) > 0, "glue_tasks must be non-empty"
    assert len(cfg.dataset.longbench_tasks) > 0, "longbench_tasks must be non-empty"


# ── Loaders ──────────────────────────────────────────────────────────────────

def _dict_to_config(d: dict) -> ExperimentConfig:
    cfg = ExperimentConfig()
    if "model" in d:
        cfg.model = ModelConfig(**d["model"])
    if "lora" in d:
        cfg.lora = LoRAConfig(**d["lora"])
    if "locret" in d:
        cfg.locret = LocretConfig(**d["locret"])
    if "training" in d:
        t = d["training"].copy()
        if "betas" in t:
            t["betas"] = tuple(t["betas"])
        if "seeds" in t:
            t["seeds"] = list(t["seeds"])
        cfg.training = TrainingConfig(**t)
    if "dataset" in d:
        cfg.dataset = DatasetConfig(**d["dataset"])
    if "stability" in d:
        cfg.stability = StabilityConfig(**d["stability"])
    if "paths" in d:
        cfg.paths = PathConfig(**d["paths"])
    return cfg


def load_config(path: str) -> ExperimentConfig:
    with open(path, "r") as f:
        d = yaml.safe_load(f)
    cfg = _dict_to_config(d)
    validate_config(cfg)
    return cfg


def save_config(cfg: ExperimentConfig, path: str) -> None:
    import dataclasses
    d = dataclasses.asdict(cfg)
    with open(path, "w") as f:
        yaml.dump(d, f, default_flow_style=False, sort_keys=False)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | ExperimentConfig dataclass | All config group dataclasses + validate_config |
| C-1-2 | YAML load/save utility | load_config, save_config, _dict_to_config |

---

## A-9 (YAML schema): Complete experiment.yaml [Complexity: 12, Budget: 2 subtasks]

**Applied**: Standard YAML flat-section schema, no anchors required

### Configuration (YAML) — `h-m2/experiment.yaml`

```yaml
model:
  base_model: "meta-llama/Meta-Llama-3.1-8B"
  torch_dtype: "bfloat16"
  attn_implementation: "eager"

lora:
  r: 16
  lora_alpha: 32
  target_modules:
    - "q_proj"
    - "k_proj"
    - "v_proj"
  lora_dropout: 0.05
  bias: "none"

locret:
  hidden_dim: 1024
  n_heads: 8
  warm_init_checkpoint: "hyx21/Locret-llama-3.1-8B-instruct"
  kv_budget_ratio: 0.5

training:
  lora_lr: 0.0001
  locret_lr: 0.0005
  weight_decay: 0.01
  betas:
    - 0.9
    - 0.999
  eps: 1.0e-8
  warmup_ratio: 0.10
  lr_schedule: "cosine"
  batch_size: 8
  gradient_accumulation_steps: 4
  max_epochs: 3
  seeds:
    - 42
    - 123
    - 456
  grad_clip_norm: 1.0

dataset:
  glue_tasks:
    - "mnli"
    - "sst2"
    - "qnli"
  longbench_tasks:
    - "narrativeqa"
    - "qasper"
    - "multifieldqa_en"
  max_seq_len_glue: 512

stability:
  divergence_window: 100
  divergence_threshold: 2.0
  log_interval: 50

paths:
  output_dir: "h-m2/"
  checkpoint_dir: "h-m2/checkpoints/"
  figures_dir: "h-m2/figures/"
  results_dir: "h-m2/results/"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | YAML schema file | Complete experiment.yaml with all hyperparameters |
| C-9-2 | Gate-critical defaults verification | Confirm budget_ratio=0.5, seeds=[42,123,456], divergence_threshold=2.0 match Phase 2B controlled variables |

---

## Self-Validation

- [x] ONE format only — dataclass (no dict alternative)
- [x] No ASCII diagrams
- [x] No KB search logs — only "Applied: X" lines
- [x] Rationale only for non-standard values (locret_lr comment)
- [x] Subtask count within budget (2 per task)
- [x] Total length < 400 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] Green-field — Serena skip acceptable
