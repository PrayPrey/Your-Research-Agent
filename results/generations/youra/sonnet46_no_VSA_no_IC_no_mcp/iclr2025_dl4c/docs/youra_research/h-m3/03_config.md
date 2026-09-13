# Config Design: h-m3 (RLEF-Fraction vs RLEF-Binary)

Applied: Standard dataclass extension pattern from h-E1; bootstrap config reuse
Applied: verified-field incremental config inheritance pattern

---

## Inherited Configuration (Base Hypothesis)

Verified from `/docs/youra_research/h-e1/code/config.py` (actual code):

```python
# h-E1 actual fields — DO NOT RENAME
@dataclass
class TrainingConfig:
    lr: float = 1e-5        # h-m3 overrides to 1e-6
    batch_size: int = 4
    grad_accum: int = 8     # h-m3 overrides to 4
    epochs: int = 3
    max_length: int = 1024
    max_new_tokens: int = 512
    seed: int = 42
    precision: str = "bfloat16"
    grad_clip: float = 1.0
    warmup_steps: int = 100
    lr_schedule: str = "cosine"

@dataclass
class GRPOConfig:
    num_generations: int = 8   # G rollouts per prompt
    beta: float = 0.04
    temperature_rollout: float = 0.8

@dataclass
class BootstrapConfig:
    n_boot: int = 1000
    seed: int = 42
    ci_level: float = 0.95
    gate_ratio: float = 1.5   # unused in h-m3; gate is p<0.05
```

---

## A-5: Evaluation Config Schema [Complexity: 1, Budget: 1]

**Applied**: Standard PyTorch defaults

### C-A5-1: Evaluation Config

```python
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class BenchmarkPaths:
    bigcode_harness_dir: str = "external/bigcode-evaluation-harness"
    livecodebench_dir: str = "external/LiveCodeBench"
    bigcode_harness_commit: str = "FILL_BEFORE_RUN"

@dataclass
class CheckpointPaths:
    sft_checkpoint: str = "docs/youra_research/h-e1/code/checkpoints/sft"
    fraction_checkpoint: str = "docs/youra_research/h-e1/code/checkpoints/rlef_fraction"
    binary_checkpoint: str = "docs/youra_research/h-m3/code/checkpoints/rlef_binary"

@dataclass
class EvalRunConfig:
    batch_size: int = 8
    n_samples: int = 1
    n_workers: int = 4
    temperature: float = 0.2
    max_new_tokens: int = 512

@dataclass
class OutputPaths:
    results_dir: str = "docs/youra_research/h-m3/results"
    figures_dir: str = "docs/youra_research/h-m3/figures"
    # file pattern: {results_dir}/{model_tag}_{task}.json
    stats_file: str = "docs/youra_research/h-m3/results/stats.yaml"

@dataclass
class EvalConfig:
    benchmarks: BenchmarkPaths = field(default_factory=BenchmarkPaths)
    checkpoints: CheckpointPaths = field(default_factory=CheckpointPaths)
    run: EvalRunConfig = field(default_factory=EvalRunConfig)
    output: OutputPaths = field(default_factory=OutputPaths)
    tasks: Dict[str, str] = field(default_factory=lambda: {
        "humaneval": "humaneval",
        "mbpp": "mbpp",
        "lcb_easy": "livecodebench",
        "lcb_medium": "livecodebench",
        "lcb_hard": "livecodebench",
    })
    lcb_difficulty_flag: Dict[str, str] = field(default_factory=lambda: {
        "lcb_easy": "easy",
        "lcb_medium": "medium",
        "lcb_hard": "hard",
    })
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-A5-1 | Eval Config Schema | Dataclass for benchmark paths, checkpoints, run params, output paths |

---

## A-6: Statistical Test Config [Complexity: 1, Budget: 1]

**Applied**: Bootstrap pattern from h-E1 `BootstrapConfig` (verified fields: `n_boot`, `seed`, `ci_level`)

### C-A6-1: Statistical Test Config

```python
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class StatTestConfig:
    # Bootstrap params — field names match h-E1 BootstrapConfig
    n_boot: int = 1000
    seed: int = 42
    ci_level: float = 0.95
    significance_threshold: float = 0.05   # gate: p < 0.05

    # Difficulty stratification → LCB labels
    difficulty_map: Dict[str, str] = field(default_factory=lambda: {
        "Easy": "lcb_easy",
        "Medium": "lcb_medium",
        "Hard": "lcb_hard",
    })

    # Primary gate benchmark (non-standard: Hard only per PRD)
    gate_benchmark: str = "lcb_hard"

    # Results serialization
    results_schema_version: str = "1.0"
    results_file: str = "docs/youra_research/h-m3/results/stats.yaml"
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-A6-1 | Stat Test Config | Bootstrap params, gate threshold, difficulty map, results path |

---

## Full YAML Example Config

```yaml
# h-m3 experiment config — copy-paste ready
# Save as: docs/youra_research/h-m3/code/config.yaml

training:
  lr: 1.0e-6          # non-standard: 1e-5 in h-E1; lowered for binary reward stability
  batch_size: 4
  grad_accum: 4       # non-standard: 8 in h-E1; effective batch=16 per PRD
  epochs: 3
  max_length: 1024
  max_new_tokens: 512
  seed: 42
  precision: bfloat16
  grad_clip: 1.0
  warmup_steps: 100
  lr_schedule: cosine

grpo:
  num_generations: 8
  beta: 0.04
  temperature_rollout: 0.8

benchmarks:
  bigcode_harness_dir: external/bigcode-evaluation-harness
  livecodebench_dir: external/LiveCodeBench
  bigcode_harness_commit: FILL_BEFORE_RUN

checkpoints:
  sft_checkpoint: docs/youra_research/h-e1/code/checkpoints/sft
  fraction_checkpoint: docs/youra_research/h-e1/code/checkpoints/rlef_fraction
  binary_checkpoint: docs/youra_research/h-m3/code/checkpoints/rlef_binary

eval:
  batch_size: 8
  n_samples: 1
  n_workers: 4
  temperature: 0.2
  max_new_tokens: 512
  tasks:
    humaneval: humaneval
    mbpp: mbpp
    lcb_easy: livecodebench
    lcb_medium: livecodebench
    lcb_hard: livecodebench
  lcb_difficulty_flag:
    lcb_easy: easy
    lcb_medium: medium
    lcb_hard: hard

output:
  results_dir: docs/youra_research/h-m3/results
  figures_dir: docs/youra_research/h-m3/figures
  stats_file: docs/youra_research/h-m3/results/stats.yaml

stats:
  n_boot: 1000
  seed: 42
  ci_level: 0.95
  significance_threshold: 0.05
  gate_benchmark: lcb_hard
  difficulty_map:
    Easy: lcb_easy
    Medium: lcb_medium
    Hard: lcb_hard
  results_schema_version: "1.0"
  results_file: docs/youra_research/h-m3/results/stats.yaml
```

---

## Results Serialization Schema (YAML)

```yaml
# stats.yaml output schema
version: "1.0"
experiment: h-m3
date: "YYYY-MM-DD"
gate_result: PASS | FAIL   # PASS if delta_fraction > delta_binary at lcb_hard, p < 0.05

models:
  sft:
    checkpoint: <path>
    scores: {humaneval: 0.0, mbpp: 0.0, lcb_easy: 0.0, lcb_medium: 0.0, lcb_hard: 0.0}
  fraction:
    checkpoint: <path>
    scores: {humaneval: 0.0, mbpp: 0.0, lcb_easy: 0.0, lcb_medium: 0.0, lcb_hard: 0.0}
  binary:
    checkpoint: <path>
    scores: {humaneval: 0.0, mbpp: 0.0, lcb_easy: 0.0, lcb_medium: 0.0, lcb_hard: 0.0}

deltas:
  fraction_vs_sft: {humaneval: 0.0, mbpp: 0.0, lcb_easy: 0.0, lcb_medium: 0.0, lcb_hard: 0.0}
  binary_vs_sft:   {humaneval: 0.0, mbpp: 0.0, lcb_easy: 0.0, lcb_medium: 0.0, lcb_hard: 0.0}

bootstrap:
  n_boot: 1000
  seed: 42
  lcb_hard_pvalue: 0.0
  lcb_hard_ci_fraction: [0.0, 0.0]
  lcb_hard_ci_binary: [0.0, 0.0]
```
