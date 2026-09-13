# Configuration: H-M1 — PC1,residual vs BSI Correlation

**Hypothesis:** PC1,residual correlates positively with BSI
**Type:** MECHANISM (single fixed config; no hyperparameter search)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (h-m1 has no code/ directory; archived h-m1 config.py under `_archive/` is for an unrelated clustering hypothesis and not reused)
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-1: Experiment Configuration

**Applied**: Standard PyTorch/HF inference defaults

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field


@dataclass
class DatasetConfig:
    paws_name: str = "google-research-datasets/paws"
    paws_config: str = "labeled_final"
    paws_split: str = "test"
    qqp_name: str = "nyu-mll/glue"
    qqp_config: str = "qqp"
    qqp_split: str = "validation"


@dataclass
class ExperimentConfig:
    # Paths
    pc1_scores_path: str = "../h-e1/results/pc1_scores.csv"
    output_dir: str = "./results/"
    figures_dir: str = "./figures/"

    # Datasets
    dataset: DatasetConfig = field(default_factory=DatasetConfig)

    # Inference
    batch_size: int = 32
    max_seq_length: int = 256
    seed: int = 42

    # Statistics
    alpha: float = 0.05
    min_samples: int = 30

    # Output
    results_formats: tuple = ("csv", "json")
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Load PC1 scores | Read `pc1_scores.csv`, validate `min_samples` rows |
| C-1-2 | Load PAWS/QQP | HF `datasets.load_dataset` with configs above, deterministic order (seed) |
| C-1-3 | Write outputs | Save `bsi_scores.csv`, `correlation_results.json`, scatter PNG to configured dirs |

---

## YAML Config Schema

```yaml
# h-m1/config.yaml
data:
  pc1_scores_path: "../h-e1/results/pc1_scores.csv"
  output_dir: "./results/"
  figures_dir: "./figures/"

datasets:
  paws:
    name: "google-research-datasets/paws"
    config: "labeled_final"
    split: "test"
  qqp:
    name: "nyu-mll/glue"
    config: "qqp"
    split: "validation"

inference:
  batch_size: 32
  max_seq_length: 256
  seed: 42

statistics:
  alpha: 0.05
  min_samples: 30

output:
  results_formats: ["csv", "json"]
```

---

## Environment Variables

None required. Optional overrides (only if running on shared cluster):

| Variable | Default | Purpose |
|----------|---------|---------|
| `HF_HOME` | HF default cache | Override HuggingFace dataset cache location |
| `CUDA_VISIBLE_DEVICES` | unset (all GPUs) | Restrict GPU visibility for batch inference |

---

## Default Values

| Field | Default | Rationale |
|-------|---------|-----------|
| `batch_size` | 32 | PRD-specified |
| `max_seq_length` | 256 | PRD-specified (tokenizer truncation) |
| `seed` | 42 | PRD-specified determinism requirement |
| `alpha` | 0.05 | PRD success criterion |
| `min_samples` | 30 | PRD success criterion (min model count) |
| `results_formats` | csv, json | Matches PRD output deliverables |

---

## Validation Rules

- `pc1_scores_path` must exist and contain ≥ `min_samples` rows with non-null `pc1_score`.
- `model_name` values in `pc1_scores.csv` must be the join key against BSI results — no model dropped silently (log any mismatch).
- `batch_size > 0`, `max_seq_length > 0`.
- `alpha` in `(0, 1)`.
- Correlation computation must run only after both PAWS and QQP accuracy are computed per model (no partial BSI).
- Output dirs (`output_dir`, `figures_dir`) created if missing before write.
