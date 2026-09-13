# Config: H-M2

**Applied**: Standard PyTorch-style config.py module pattern (single source-of-truth constants, no matching KB example for data-analysis config)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass (module-level constants for thresholds, dataclasses for structured settings)

This is data analysis, not ML training — config covers thresholds, API/rate-limit settings, and output paths only.

---

## A-1: config.py [Complexity: 4, Budget: 4]

**Applied**: Flat module-level constants for simple thresholds; dataclasses for grouped settings (API, paths)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

# --- Classification threshold (hardcoded per NFR-3, not tunable post-hoc) ---
POST_2020_THRESHOLD: float = 0.80
GPT3_RELEASE_DATE: str = "2020-06-01"
GPT3_RELEASE_YEAR: int = 2020

# --- Dataset source ---
PWC_DATASET_ID: str = "pwc-archive/datasets"
PWC_SPLIT: str = "train"

# --- Classification rules ---
EMERGENT_KEYWORDS: list[str] = [
    "reasoning", "emergent", "capability", "understanding",
    "commonsense", "multi-task", "chain-of-thought", "few-shot",
]
EMERGENT_BENCHMARK_NAMES: set[str] = {
    "mmlu", "big-bench", "bigbench", "humaneval", "truthfulqa", "gsm8k",
}
EMERGENT_TASK_TYPES: set[str] = {
    "question-answering", "code-generation", "math-word-problems",
}
MIN_EMERGENT_BENCHMARKS: int = 50  # acceptance criterion floor


@dataclass
class SemanticScholarConfig:
    base_url: str = "https://api.semanticscholar.org/graph/v1"
    rate_limit_per_min: int = 100          # NFR-1
    timeout_sec: int = 10
    max_retries: int = 3
    retry_backoff_sec: float = 2.0


@dataclass
class RunConfig:
    max_runtime_min: int = 20              # NFR-1 gate
    seed: int = 42
    results_path: str = "results/results.json"
    figures_dir: str = "figures/"


@dataclass
class VizConfig:
    # Applied: Standard matplotlib color/label pattern (no KB match)
    emergent_color: str = "#d62728"    # red
    traditional_color: str = "#1f77b4"  # blue
    threshold_line_color: str = "#2ca02c"  # green
    gpt3_marker_color: str = "#7f7f7f"  # gray dashed vline
    figsize: tuple[int, int] = (10, 6)
    dpi: int = 150
    font_size: int = 11
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Create code/ dir + `__init__.py` | Project scaffold |
| C-1-2 | Write config.py constants | Threshold, dataset ID, keyword/name sets above |
| C-1-3 | Write SemanticScholarConfig + RunConfig | Rate limit, timeout, paths |
| C-1-4 | Write VizConfig | Colors, figsize, dpi for figures |

---

## Notes on Non-Standard Values

- `POST_2020_THRESHOLD = 0.80`: fixed by PRD success criterion (FR-4.2), not tunable.
- `rate_limit_per_min = 100`: fixed by NFR-1 (Semantic Scholar rate limit).
- `max_runtime_min = 20`: fixed by NFR-1 pipeline runtime budget.
- `MIN_EMERGENT_BENCHMARKS = 50`: fixed by PRD Acceptance Criteria #2.

All other values (retries, timeout, seed, viz colors) are standard defaults — no special justification needed.
