# Config: H-E1 (EXISTENCE / PoC)

**Applied**: None — Archon KB has no time-series/change-point config patterns (indexes ML model repos only). Confirmed via `rag_search_knowledge_base("DL config patterns", "experiment configuration")` — top hits (latent-diffusion, pytorch inductor config, jax) irrelevant to statistical PELT analysis. Using standard Python dataclasses.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project — no existing code to analyze
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## EXISTENCE PoC Rule Applied

Single fixed config, no hyperparameter grid, no ablation configs, 1 run (PELT deterministic, no seed needed). FR-5 ablation variants (model="l1"/"l2", penalty ±20%) are **out of scope** for this EXISTENCE config — belongs to a future ROBUSTNESS hypothesis, not PoC.

---

## Configuration (Python Dataclasses)

```python
from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-e1"
    output_dir: str = "results/"
    figures_dir: str = "figures/"
    results_file: str = "results.json"


@dataclass
class DataConfig:
    dataset_name: str = "pwc-archive/evaluation-tables"
    date_start: str = "2018-01-01"
    date_end: str = "2024-12-31"
    aggregation: str = "monthly"  # groupby freq for benchmark usage counts


@dataclass
class PELTConfig:
    model: str = "rbf"  # ruptures kernel; primary variant per FR-3.1
    min_size: int = 3   # minimum segment length (months), per FR-3.3
    # penalty computed at runtime: pen = log(n) * variance(signal), per FR-3.2
    # (not a fixed default — depends on series length/variance; see model.py)
    penalty: float = None


@dataclass
class EvaluationConfig:
    alpha: float = 0.05
    target_window: Tuple[int, int] = (2019, 2022)  # inclusive years, gate check FR-4.1
```

---

## Task: A-1 Setup Config [Complexity: 4, Budget: 4]

**Applied**: Standard Python dataclass defaults, no KB pattern needed (green-field PoC).

### Configuration
See dataclasses above — combine into single `config.py` module, exported as module-level instances:

```python
EXPERIMENT = ExperimentConfig()
DATA = DataConfig()
PELT = PELTConfig()
EVAL = EvaluationConfig()
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Define dataclasses | ExperimentConfig, DataConfig, PELTConfig, EvaluationConfig in config.py |
| C-1-2 | Module-level instances | EXPERIMENT/DATA/PELT/EVAL singletons for import by other modules |
| C-1-3 | Folder setup | Create `results/` and `figures/` dirs if missing (os.makedirs) |
| C-1-4 | Verify importability | `python -c "import config"` smoke check |

---

## Self-Validation

- [x] ONE format only (dataclass, not dict)
- [x] No ASCII diagrams
- [x] Archon KB search logged as "Applied: None" (1 line, justified)
- [x] Rationale only for non-standard values (PELT penalty formula, ablation exclusion)
- [x] Subtask count within budget (4/4, matches architecture A-1 budget)
- [x] Total length < 400 lines
- [x] Codebase Analysis (Serena) section included (green-field, skip acceptable)
