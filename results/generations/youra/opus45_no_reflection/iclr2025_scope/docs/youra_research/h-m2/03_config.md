# Configuration: H-M2 (Token-Level vs Matrix-Level Distillation Drift)

**Type:** MECHANISM — full multi-condition config (not PoC).

Applied: standard PyTorch experiment dataclass pattern (no closely-matching KB hit; used default DL config conventions).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing config code to analyze (H-M1 has no code artifacts)
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-1: AnalysisConfig + ExperimentSettings [Complexity: 8, Budget: 2 subtasks]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class AnalysisConfig:
    # Models
    teacher_name: str = "microsoft/phi-1_5"
    mohawk_name: str = "goombalab/phi-mamba"
    cab_name: str = "wph6/CAB"
    teacher_dim: int = 2048

    # Dataset
    dataset_name: str = "allenai/c4"
    dataset_config: str = "en"
    dataset_split: str = "validation"
    min_doc_chars: int = 8192
    num_samples: int = 500

    # Analysis grid
    target_lengths: List[int] = field(default_factory=lambda: [512, 1024, 1536, 2048])
    middle_layers: List[int] = field(default_factory=lambda: [8, 12, 16])

    # Runtime
    batch_size: int = 8
    seed: int = 42
    device: str = "cuda"
    dtype: str = "float16"  # AutoModel torch_dtype

    # Output
    output_dir: str = "results"
    figures_dir: str = "figures"
    results_filename: str = "drift_results.json"
```

**Non-standard:** `min_doc_chars=8192` ensures docs are long enough to safely truncate to 2048 tokens without padding artifacts.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | AnalysisConfig dataclass | Define fields above in `code/config.py`; single source of truth for all modules |
| C-1-2 | Config validation helper | `validate_config(cfg)` — asserts `target_lengths` sorted, `teacher_dim > 0`, creates `output_dir`/`figures_dir` if missing |

---

## Hyperparameters & Thresholds (embedded in AnalysisConfig — no separate class)

| Name | Value | Used by |
|------|-------|---------|
| `seed` | 42 | data sampling, torch/np seeding |
| `num_samples` | 500 per length | `get_long_documents` |
| Gate: drift bound ratio | `max(cab)/min(cab) < 2.0` | `stats.evaluate_gate` (hardcoded constant, not config — fixed per PRD gate) |
| CI level | 95% | `stats.compute_slope` (scipy default `linregress` + manual CI calc) |

---

## YAML Schema (Experiment Config)

For CLI/reproducibility logging (optional load path mirroring `AnalysisConfig`):

```yaml
teacher_name: microsoft/phi-1_5
mohawk_name: goombalab/phi-mamba
cab_name: wph6/CAB
teacher_dim: 2048

dataset_name: allenai/c4
dataset_config: en
dataset_split: validation
min_doc_chars: 8192
num_samples: 500

target_lengths: [512, 1024, 1536, 2048]
middle_layers: [8, 12, 16]

batch_size: 8
seed: 42
device: cuda
dtype: float16

output_dir: results
figures_dir: figures
results_filename: drift_results.json
```

Load via `AnalysisConfig(**yaml.safe_load(open(path)))`.

---

## OutputConfig (embedded — same dataclass)

No separate `OutputConfig` class; `output_dir`/`figures_dir`/`results_filename` fields on `AnalysisConfig` are sufficient (single-run experiment, no multi-run sweep needed for MECHANISM validation).
