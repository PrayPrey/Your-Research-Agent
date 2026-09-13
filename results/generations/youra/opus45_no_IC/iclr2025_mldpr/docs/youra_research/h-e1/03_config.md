# Configuration: H-E1 (EXISTENCE)

**Type:** EXISTENCE (PoC) — single fixed config, no tuning/grid.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - designing new config schema (no base hypothesis, no existing codebase)
**Config Files Found**: None - new config
**Pattern Used**: dataclass

**Applied**: No relevant Archon KB config pattern found (searched "experiment configuration dataclass pattern" — only unrelated diffusion/model repos returned). Using standard Python dataclass, PoC-minimal per EXISTENCE rules.

---

## A-1: PWC HHI Analysis Config [Complexity: Low, Budget: LIGHT]

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class HHIAnalysisConfig:
    # Data sources
    hf_papers_dataset: str = "pwc-archive/papers-with-abstracts"
    hf_evaltables_dataset: str = "pwc-archive/evaluation-tables"
    use_api_fallback: bool = True  # paperswithcode-client if HF load fails

    # Venue/year filtering
    venues: List[str] = field(default_factory=lambda: ["NeurIPS", "ICML", "ICLR"])
    year_start: int = 2018
    year_end: int = 2024  # inclusive

    # Output paths
    results_dir: str = "results"
    figures_dir: str = "figures"
    results_csv: str = "results/hhi_metrics.csv"
    validation_json: str = "results/validation.json"

    # Validation thresholds
    expected_venue_years: int = 21  # 3 venues x 7 years
    hhi_min: float = 0.0
    hhi_max: float = 1.0
    min_papers_per_venue_year: int = 100  # SHOULD, not gate-blocking

    # Reproducibility
    seed: int = 42
```

### Subtasks [4/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Data loading | Load HF datasets with API fallback per config |
| C-1-2 | Filter & aggregate | Filter venue/year, explode datasets, count usage |
| C-1-3 | HHI/entropy compute | Compute metrics per venue-year, write results_csv |
| C-1-4 | Validation & figures | Check thresholds, write validation_json, generate 4 figures |
