# Config: H-M5 (Modality Divergence — Phase Transition Effect)

**Applied**: Standard PyTorch/pandas domain-standard config (no relevant KB entries for statistical-analysis config found; using dataclass pattern).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field - no existing codebase to analyze
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-1 to A-11: Full Pipeline Config [Complexity: 65 total, Budget: shared config module]

**Applied**: Single frozen dataclass, statistical-analysis config (not ML hyperparameters).

### Configuration (Python Dataclass)

```python
# config.py
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExperimentConfig:
    # Data source
    dataset_name: str = "pwc-archive/datasets"
    dataset_split: str = "train"

    # Date range (FR-1.3)
    date_start: str = "2018-01"
    date_end: str = "2024-12"

    # Period cutoffs (FR-3.1)
    pre_cutoff: str = "2020-01"   # pre-2020: all months < this
    post_cutoff: str = "2021-01"  # post-2021: all months >= this

    # Modality keywords (FR-1.2)
    modality_keywords: dict = field(default_factory=lambda: {
        "CV": ["image", "vision", "object detection", "segmentation"],
        "NLP": ["text", "language", "nlp", "translation", "summarization"],
        "Audio": ["audio", "speech", "sound"],
        "Tabular": ["tabular", "structured"],
    })
    default_modality: str = "Other"

    # Rolling correlation (FR-3.2)
    rolling_window: int = 6  # months

    # Gate thresholds (FR-5.1)
    gate_r_pre_min: float = 0.6
    gate_r_post_max: float = 0.4
    gate_p_value_max: float = 0.05

    # Baseline null model (FR-4.1)
    baseline_r_min: float = 0.5

    # Minimum sample sizes (Success Metrics)
    min_n_pre: int = 24
    min_n_post: int = 36
    min_time_points: int = 72  # FR-2.2

    # Reproducibility
    seed: int = 42

    # Output paths
    output_dir: str = "figures"
    gate_metrics_path: str = "figures/gate_metrics.png"
    rolling_correlation_path: str = "figures/rolling_correlation.png"
    gini_trajectories_path: str = "figures/gini_trajectories.png"
    correlation_heatmap_path: str = "figures/correlation_heatmap.png"
    validation_report_path: str = "04_validation.md"


CONFIG = ExperimentConfig()
```

### Subtasks [0/0 — no subtask decomposition needed]

Single shared config module used by all A-1..A-11 tasks per architecture (`config.py` at hypothesis root, imported by each `code/*.py` module). No per-task config variants required — this is a MECHANISM/statistical hypothesis with fixed thresholds from the PRD, not a hyperparameter search.
