# Config: H-E1

**Hypothesis:** H-E1 (EXISTENCE)
**Date:** 2026-08-03

Applied: No domain-relevant KB patterns found (similarity < 0.50); using standard PyTorch dataclass defaults

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Config Files Found**: None — new config design
**Pattern Used**: dataclass

---

## A-5: Analysis & Visualization [Complexity: 9, Budget: 1 subtask]

### Configuration (Python Dataclasses)

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class MOHAWKConfig:
    stage_tokens: dict = field(default_factory=lambda: {
        "stage1": 26_000_000,
        "stage2": 52_000_000,
        "stage3": 920_000_000,
    })
    lr: dict = field(default_factory=lambda: {
        "stage1": 1e-3,
        "stage2": 5e-4,
        "stage3": 1e-4,
    })
    batch_size: dict = field(default_factory=lambda: {
        "stage1": 8,
        "stage2": 8,
        "stage3": 32,
    })
    seq_len: int = 2048
    seed: int = 42
    config_dir: str = "configs/Llama/8B/"


@dataclass
class LAWCATConfig:
    seq_len: int = 1024
    phase1_tokens: int = 50_000_000
    phase1_lr: float = 1e-2
    phase1_mse_weight: float = 1000.0
    lora_r: int = 16
    lora_alpha: int = 32
    lora_lr: float = 1e-4
    seed: int = 0


@dataclass
class Hybrid4Config:
    kept_layers: List[int] = field(default_factory=lambda: list(range(14, 18)))
    stage3_tokens: int = 200_000_000


@dataclass
class EvalConfig:
    categories: List[str] = field(default_factory=lambda: [
        "single_doc_qa",
        "multi_doc_qa",
        "long_in_context_learning",
        "long_dialogue",
        "code_repo",
        "long_structured_data",
    ])
    retrieval_heavy: List[str] = field(default_factory=lambda: [
        "multi_doc_qa",
        "long_structured_data",
    ])
    generation_heavy: List[str] = field(default_factory=lambda: [
        "long_in_context_learning",
    ])
    judge_threshold: float = 0.0  # exact letter match; no soft threshold


@dataclass
class AnalysisConfig:
    # Bootstrap
    n_resamples: int = 10_000
    bootstrap_seed: int = 42
    ci_alpha: float = 0.05
    # Mixed-effects model
    # Non-standard: formula string passed directly to statsmodels/pymer4
    mixed_effects_formula: str = "delta_norm ~ C(task_type) * C(strategy) + (1|task_id)"
    # Holm correction
    holm_correction: bool = True
    interaction_p_threshold: float = 0.01
    # Interaction ratio threshold (PoC gate)
    interaction_ratio_threshold: float = 2.0
    # Gate thresholds (mechanism verification)
    frobenius_max: float = 0.15
    l2_max: float = 0.15
    ppl_relative_gap_max: float = 0.05


@dataclass
class ExperimentConfig:
    teacher_model_id: str = "meta-llama/Llama-3-8B"
    c4_dataset: tuple = ("allenai/c4", "en")
    longbench_dataset: tuple = ("THUDM/LongBench", "v2")
    mohawk_repo: str = "repos/mohawk"
    lawcat_repo: str = "repos/LAWCAT"
    longbench_repo: str = "repos/LongBench"
    checkpoint_dir: str = "checkpoints"
    results_dir: str = "results"
    figures_dir: str = "figures"
    abort_on_gate_fail: bool = True
    mohawk: MOHAWKConfig = field(default_factory=MOHAWKConfig)
    lawcat: LAWCATConfig = field(default_factory=LAWCATConfig)
    hybrid4: Hybrid4Config = field(default_factory=Hybrid4Config)
    eval: EvalConfig = field(default_factory=EvalConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
```

### YAML Config Schema (`config.yaml`)

```yaml
teacher_model_id: "meta-llama/Llama-3-8B"
c4_dataset: ["allenai/c4", "en"]
longbench_dataset: ["THUDM/LongBench", "v2"]
mohawk_repo: "repos/mohawk"
lawcat_repo: "repos/LAWCAT"
longbench_repo: "repos/LongBench"
checkpoint_dir: "checkpoints"
results_dir: "results"
figures_dir: "figures"
abort_on_gate_fail: true

mohawk:
  config_dir: "configs/Llama/8B/"
  seq_len: 2048
  seed: 42
  stage_tokens:
    stage1: 26000000
    stage2: 52000000
    stage3: 920000000
  lr:
    stage1: 0.001
    stage2: 0.0005
    stage3: 0.0001
  batch_size:
    stage1: 8
    stage2: 8
    stage3: 32

lawcat:
  seq_len: 1024
  phase1_tokens: 50000000
  phase1_lr: 0.01
  phase1_mse_weight: 1000.0
  lora_r: 16
  lora_alpha: 32
  lora_lr: 0.0001
  seed: 0

hybrid4:
  kept_layers: [14, 15, 16, 17]
  stage3_tokens: 200000000

eval:
  categories:
    - single_doc_qa
    - multi_doc_qa
    - long_in_context_learning
    - long_dialogue
    - code_repo
    - long_structured_data
  retrieval_heavy:
    - multi_doc_qa
    - long_structured_data
  generation_heavy:
    - long_in_context_learning
  judge_threshold: 0.0

analysis:
  n_resamples: 10000
  bootstrap_seed: 42
  ci_alpha: 0.05
  mixed_effects_formula: "delta_norm ~ C(task_type) * C(strategy) + (1|task_id)"
  holm_correction: true
  interaction_p_threshold: 0.01
  interaction_ratio_threshold: 2.0
  frobenius_max: 0.15
  l2_max: 0.15
  ppl_relative_gap_max: 0.05
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Statistical Analysis Config | AnalysisConfig + ExperimentConfig dataclasses; full config.yaml schema |
