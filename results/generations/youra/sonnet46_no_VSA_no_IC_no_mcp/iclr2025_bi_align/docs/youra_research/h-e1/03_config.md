# Config: H-E1
# RLHF Dual-Signal Co-existence Verification

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr

Applied: Configuration object pattern — centralize all tuneable values in one place

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — new config design
**Config Files Found:** None — new config
**Pattern Used:** dataclass

Note: Archon MCP unavailable (ablation mode). Patterns cited from standard software engineering references.

---

## C-E6-1: ExperimentConfig [Complexity: 8, Budget: 1]

**Applied**: Configuration object pattern — centralize all tuneable values

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from pathlib import Path
import yaml


@dataclass
class ExperimentConfig:
    # Input data
    coste_csv_path: str = "data/coste2023_kl_curves.csv"
    gao_csv_path: str = "data/gao2023_kl_curves.csv"

    # Output directories
    figures_dir: str = "docs/youra_research/h-e1/figures"
    results_dir: str = "docs/youra_research/h-e1/results"
    results_filename: str = "h_e1_results.json"

    # Gate thresholds (from hypothesis spec)
    min_kl_levels: int = 5
    min_variation: float = 0.01  # non-constant signal floor

    # Visualization
    figure_dpi: int = 150

    # Reproducibility
    random_seed: int = 1

    def validate(self) -> None:
        """Raise FileNotFoundError if input CSV paths do not exist."""
        for attr in ("coste_csv_path", "gao_csv_path"):
            p = Path(getattr(self, attr))
            if not p.exists():
                raise FileNotFoundError(f"Required input not found: {p}")


def load_config(path: str = "config.yaml") -> ExperimentConfig:
    """Load ExperimentConfig from YAML, falling back to defaults for missing keys."""
    cfg_path = Path(path)
    if not cfg_path.exists():
        return ExperimentConfig()
    with open(cfg_path) as f:
        data = yaml.safe_load(f) or {}
    return ExperimentConfig(**{k: v for k, v in data.items()
                               if k in ExperimentConfig.__dataclass_fields__})
```

### Equivalent YAML Schema (`config.yaml`)

```yaml
# H-E1 experiment configuration
coste_csv_path: data/coste2023_kl_curves.csv
gao_csv_path: data/gao2023_kl_curves.csv

figures_dir: docs/youra_research/h-e1/figures
results_dir: docs/youra_research/h-e1/results
results_filename: h_e1_results.json

min_kl_levels: 5
min_variation: 0.01

figure_dpi: 150
random_seed: 1
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E6-1 | ExperimentConfig | Dataclass + YAML schema + load_config + validate |
