# Configuration: H-M2 (TC-SSM)

**Applied**: Standard PyTorch dataclass config pattern

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: Config classes verified from base code — H-M1 has no separate config.py; `TaskEmbeddingEncoder` uses constructor args only (`hidden_dim`, `embedding_dim`), no dataclass to inherit. No field-name collisions.
**Config Files Found**: None in h-m1 or h-m2 (green-field for h-m2 config schema)
**Pattern Used**: Dataclass (new)

---

## 1. Configuration Schema (YAML)

```yaml
# config.yaml
model:
  d_model: 1024
  d_state: 16
  d_conv: 4
  expand: 2
  task_emb_dim: 128
  rank: 32
  modulation_target: all_matrices  # delta_only | all_matrices

experiment:
  tasks: [boolq, rte, wic]
  samples_per_task: 100
  warmup_iters: 10
  measure_iters: 100
  seed: 42

measurement:
  device: cuda
  significance_level: 0.05
  overhead_threshold: 2.0

ablation:
  ranks: [16, 32, 64]
  modulation_targets: [delta_only, all_matrices]
```

---

## 2. Python Dataclasses

```python
from dataclasses import dataclass, field
from typing import Literal

@dataclass
class TCSSMConfig:
    d_model: int = 1024
    d_state: int = 16
    d_conv: int = 4
    expand: int = 2
    task_emb_dim: int = 128
    rank: int = 32
    modulation_target: Literal["delta_only", "all_matrices"] = "all_matrices"


@dataclass
class ExperimentConfig:
    tasks: list[str] = field(default_factory=lambda: ["boolq", "rte", "wic"])
    samples_per_task: int = 100
    warmup_iters: int = 10
    measure_iters: int = 100
    seed: int = 42
    checkpoint_path: str = "docs/youra_research/h-m1/code/checkpoints/task_embedding.pt"


@dataclass
class MeasurementConfig:
    device: str = "cuda"
    significance_level: float = 0.05
    overhead_threshold: float = 2.0


@dataclass
class AblationConfig:
    ranks: list[int] = field(default_factory=lambda: [16, 32, 64])
    modulation_targets: list[str] = field(
        default_factory=lambda: ["delta_only", "all_matrices"]
    )
```

---

## 3. Hyperparameter Ranges (Ablation)

| Parameter | Values | Notes |
|-----------|--------|-------|
| rank | 16, 32, 64 | Per brief; 32 = default |
| modulation_target | delta_only, all_matrices | delta_only = cheapest; all_matrices = full conditioning |
| d_model | 1024 | Fixed (mamba-370m dim) |
| d_state | 16 | Fixed (Mamba default) |

Ablation grid = 3 ranks × 2 targets = 6 runs, each measured for overhead + state variance.

---

## 4. Experiment Configuration Templates

```python
# Default run (rank=32, all_matrices)
DEFAULT = TCSSMConfig()

# Rank ablation configs
RANK_ABLATION_CONFIGS = [
    TCSSMConfig(rank=r) for r in AblationConfig().ranks
]

# Modulation-target ablation configs
TARGET_ABLATION_CONFIGS = [
    TCSSMConfig(modulation_target=t) for t in AblationConfig().modulation_targets
]
```

---

## 5. Environment Variables

None required — device selection handled via `MeasurementConfig.device`, no external API keys or secrets needed.

---

## Per-Task Configs

## A-2: LowRankProjection [Complexity: 4, Budget: 4]

**Applied**: LoRA near-zero init pattern

```python
@dataclass
class LowRankProjectionConfig:
    task_emb_dim: int = 128
    target_dim: int = 1024  # set per usage: d_model or d_state
    rank: int = 32
    down_init_std: float = 0.01  # Non-standard: near-zero init for training stability
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Init config | Wire config fields into `nn.Linear` down/up layers |

---

## A-4: TaskConditionedMamba [Complexity: 14, Budget: 14]

**Applied**: Standard PyTorch defaults + TCSSMConfig above

Uses `TCSSMConfig` directly (see Section 2). No additional fields needed.

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Base projections | delta/B/C linear layers from `d_model`, `d_state` |
| C-4-2 | Low-rank mod wiring | Instantiate 1 or 3 `LowRankProjection`s per `modulation_target` |
| C-4-3 | Forward + broadcast | Additive modulation across sequence dim |
| C-4-4 | get_state | Expose internal state for variance analysis |

---

## A-6: FLOPs/overhead measurement [Complexity: 10, Budget: 10]

**Applied**: `torch.profiler` + wall-clock timing ratio

Uses `ExperimentConfig` (warmup_iters, measure_iters) + `MeasurementConfig` (device, overhead_threshold).

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | count_flops | Profile single forward pass |
| C-6-2 | measure_overhead | Warmup + timed loop ratio (vanilla vs TC-SSM) |
| C-6-3 | per_matrix_breakdown | Isolate Δ/B/C contribution to overhead |

---

## A-7: State variance analysis [Complexity: 8, Budget: 8]

**Applied**: scipy `f_oneway` ANOVA

Uses `MeasurementConfig.significance_level` (0.05).

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Collect states | Run `get_state` per task embedding |
| C-7-2 | ANOVA | `f_oneway` across states, compare p-value to threshold |

---

## A-8: Rank ablation framework [Complexity: 9, Budget: 9]

**Applied**: Grid sweep over `AblationConfig`

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | run_rank_ablation | Sweep `ranks`, fixed `modulation_target=all_matrices` |
| C-8-2 | run_matrix_ablation | Sweep `modulation_targets`, fixed `rank=32` |

---

## Self-Validation

- [x] ONE format only (dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values (init std)
- [x] Subtask counts within budget
- [x] Total length < 400 lines
- [x] Codebase Analysis (Serena) section included
