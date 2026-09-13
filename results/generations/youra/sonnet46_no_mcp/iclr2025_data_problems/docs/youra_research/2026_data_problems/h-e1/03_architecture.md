# Architecture Document: H-E1
# Cross-Sub-Task Contamination Variance in The Pile v1

**Hypothesis**: H-E1 | **Type**: EXISTENCE (PoC) | **Date**: 2026-05-04

Applied: EXISTENCE-minimal-pipeline (single config, flat file structure, no ablation modules)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. Standard Python pipeline using wimbd + scipy.stats + datasketch.

---

## File Structure

- `code/config.py` — single fixed config
- `code/data_loader.py` — benchmark dataset loading
- `code/ngram_extractor.py` — 13-gram extraction + text formatting
- `code/pile_query.py` — wimbd primary + MinHash LSH fallback
- `code/stats_analyzer.py` — Kruskal-Wallis, Spearman, rate aggregation
- `code/visualizer.py` — all figure generation
- `code/run_experiment.py` — orchestration entry point
- `results/` — contamination_rates.csv, statistical_tests.json
- `figures/` — all generated plots

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass

@dataclass
class Config:
    ngram_n: int = 13
    seed: int = 1
    pile_index: str = "pile"
    wimbd_es_host: str = ""          # from WIMBD_ES_HOST env var
    text_format: str = "question_choices"  # or "question_only"
    retry_attempts: int = 3
    min_token_length: int = 13
    results_dir: str = "results"
    figures_dir: str = "figures"
    mmlu_tasks: list = None          # all 57 sub-tasks
    gate_p_threshold: float = 0.05
    max_pair_diff_threshold: float = 0.05

def load_config() -> Config: ...
```

---

### DataLoader (`code/data_loader.py`)

**Dependencies**: Config

```python
from datasets import Dataset

class DataLoader:
    def __init__(self, config: Config): ...
    def load_mmlu(self) -> dict[str, list[str]]:
        """Returns {subtask_name: [formatted_text, ...]} for 57 sub-tasks."""
        ...
    def load_hellaswag(self) -> dict[str, list[str]]:
        """Returns {"hellaswag": [formatted_text, ...]}."""
        ...
    def load_bbh(self) -> dict[str, list[str]]:
        """Returns {"bbh": [formatted_text, ...]}."""
        ...
    def load_all(self) -> dict[str, list[str]]:
        """Returns merged dict of all 59 sub-tasks."""
        ...
    def format_text(self, item: dict, dataset: str) -> str:
        """Applies question+choices or question-only format per config."""
        ...
```

---

### NgramExtractor (`code/ngram_extractor.py`)

**Dependencies**: Config

```python
class NgramExtractor:
    def __init__(self, config: Config): ...
    def extract(self, text: str) -> list[str]:
        """Sliding-window 13-gram extraction. Returns [] if < min_token_length."""
        ...
    def extract_batch(self, texts: list[str]) -> list[list[str]]:
        """Batch extraction; logs skipped items (< 13 tokens)."""
        ...
```

---

### PileQuery (`code/pile_query.py`)

**Dependencies**: Config, NgramExtractor

```python
class PileQuery:
    def __init__(self, config: Config, extractor: NgramExtractor): ...
    def _use_wimbd(self) -> bool:
        """Checks WIMBD_ES_HOST availability."""
        ...
    def is_contaminated(self, text: str) -> int:
        """Returns 1 if any 13-gram matches Pile index, 0 otherwise. Retries 3x."""
        ...
    def query_subtask(self, name: str, texts: list[str]) -> list[int]:
        """Returns per-item contamination labels (0/1) for a sub-task with logging."""
        ...
    def query_all(self, subtask_texts: dict[str, list[str]]) -> dict[str, list[int]]:
        """Returns {subtask_name: [0/1, ...]} for all 59 sub-tasks."""
        ...
    @property
    def mode(self) -> str:
        """Returns 'wimbd' or 'fallback_minhash'."""
        ...
```

---

### StatsAnalyzer (`code/stats_analyzer.py`)

**Dependencies**: Config

```python
import pandas as pd
from scipy.stats import kruskal, spearmanr

class StatsAnalyzer:
    def __init__(self, config: Config): ...
    def compute_rates(self, labels: dict[str, list[int]]) -> pd.DataFrame:
        """Returns DataFrame with columns: subtask, n_items, n_contaminated, rate."""
        ...
    def kruskal_wallis(self, labels: dict[str, list[int]]) -> dict:
        """Returns {kruskal_stat, p_value, gate_pass, max_pair_diff}."""
        ...
    def spearman_correlation(
        self, rates_a: pd.Series, rates_b: pd.Series
    ) -> tuple[float, float]:
        """Returns (rho, p_value) for sensitivity analysis."""
        ...
    def sanity_check(self, rates_df: pd.DataFrame, reference: dict) -> pd.DataFrame:
        """Compares our rates vs WIMBD Table 2 values. Returns diff table."""
        ...
    def assert_gate(self, p_value: float) -> None:
        """assert p_value < 0.05, f'Gate FAILED: p={p_value:.4f} >= 0.05'"""
        ...
```

---

### Visualizer (`code/visualizer.py`)

**Dependencies**: Config

```python
import pandas as pd
import matplotlib.pyplot as plt

class Visualizer:
    def __init__(self, config: Config): ...
    def plot_contamination_rates_bar(
        self, rates_df: pd.DataFrame, p_value: float
    ) -> None:
        """59-bar sorted barplot with p-value annotation. Saves contamination_rates_barplot.png."""
        ...
    def plot_heatmap(self, rates_df: pd.DataFrame) -> None:
        """Sub-task x rate heatmap sorted by academic domain. Saves heatmap.png."""
        ...
    def plot_distribution(self, rates_df: pd.DataFrame) -> None:
        """Histogram/KDE of contamination rates. Saves distribution.png."""
        ...
    def plot_domain_boxplot(self, rates_df: pd.DataFrame) -> None:
        """Box plot: MMLU academic vs commonsense. Saves domain_boxplot.png."""
        ...
    def plot_top_bottom(self, rates_df: pd.DataFrame) -> None:
        """Top-10/bottom-10 horizontal bar chart. Saves top_bottom.png."""
        ...
    def plot_sensitivity_scatter(
        self, rates_primary: pd.Series, rates_sensitivity: pd.Series, rho: float
    ) -> None:
        """Scatter: question-only vs question+choices. Saves sensitivity_scatter.png."""
        ...
    def save_all(self, rates_df: pd.DataFrame, stats: dict) -> None:
        """Calls all plot methods in sequence."""
        ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: Config, DataLoader, NgramExtractor, PileQuery, StatsAnalyzer, Visualizer

```python
def run_primary(config: Config) -> dict:
    """Full pipeline: load -> extract -> query -> stats -> visualize -> assert gate."""
    ...

def run_sensitivity(config: Config, primary_rates: pd.DataFrame) -> dict:
    """Repeat with question-only format; compute Spearman vs primary."""
    ...

def save_results(rates_df: pd.DataFrame, stats: dict, config: Config) -> None:
    """Writes contamination_rates.csv and statistical_tests.json."""
    ...

def main() -> None:
    """Entry point: load_config -> run_primary -> run_sensitivity -> save_results -> assert_gate."""
    ...

if __name__ == "__main__":
    main()
```

---

## Module Dependencies

```
run_experiment.py
  ├── config.py
  ├── data_loader.py    -> config
  ├── ngram_extractor.py -> config
  ├── pile_query.py     -> config, ngram_extractor
  ├── stats_analyzer.py -> config
  └── visualizer.py     -> config
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | config.py, requirements.txt, directory structure, env vars | 5 | 1+1+1+2 |
| A-2 | Benchmark Data Loading | data_loader.py: all 59 sub-tasks (MMLU x57 + HellaSwag + BBH), text formatting | 10 | 3+2+2+3 |
| A-3 | N-gram Extraction | ngram_extractor.py: 13-gram sliding window, min-token guard, batch logging | 6 | 2+1+2+1 |
| A-4 | Pile Index Query | pile_query.py: wimbd primary path + MinHash LSH fallback, retry logic, per-item labels | 14 | 3+3+4+4 |
| A-5 | Statistical Analysis | stats_analyzer.py: Kruskal-Wallis, Spearman, rate aggregation, sanity check, gate assert | 12 | 3+2+4+3 |
| A-6 | Visualization + Output | visualizer.py: 6 figures + save_results (CSV + JSON) | 10 | 3+2+2+3 |
| A-7 | Orchestration + Sensitivity | run_experiment.py: primary + sensitivity runs, gate assertion, end-to-end integration | 11 | 2+3+3+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-2, A-5, A-6, A-7], Low(4-8): [A-1, A-3]

---

## Output File Paths

| File | Purpose |
|------|---------|
| `code/config.py` | Single fixed config dataclass |
| `code/data_loader.py` | HuggingFace benchmark loading |
| `code/ngram_extractor.py` | 13-gram sliding window |
| `code/pile_query.py` | wimbd + MinHash LSH fallback |
| `code/stats_analyzer.py` | Kruskal-Wallis + Spearman + gate |
| `code/visualizer.py` | All 6 figure generators |
| `code/run_experiment.py` | Entry point orchestration |
| `results/contamination_rates.csv` | Per-sub-task rates output |
| `results/statistical_tests.json` | Gate result + stats |
| `figures/*.png` | 6 generated plots |
