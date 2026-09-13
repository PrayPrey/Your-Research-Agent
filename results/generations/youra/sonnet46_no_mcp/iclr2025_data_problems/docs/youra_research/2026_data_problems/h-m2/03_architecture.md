# Architecture Document: H-M2
# Domain-Stratified Contamination Re-Analysis: Corpus Source Composition Predicts Domain Signatures

**Hypothesis**: H-M2 | **Type**: MECHANISM (FULL) | **Date**: 2026-05-04

Applied: Domain-stratified-statistical-reanalysis (load existing matrix → classify → directional test → visualize)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental over H-M1 implementation)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/20260504_data_problems/h-m1/code/`
**Findings**: H-M1 code uses flat imports (`from config import Config`, `from stats_analyzer import StatsAnalyzer`). All modules run from `code/` directory as working directory. `experiment_results.json` confirmed at `h-m1/experiment_results.json`. H-M2 reuses `Config`, `Visualizer` patterns; adds `DomainClassifier` and extends `StatsAnalyzer` with Mann-Whitney U directional tests.

---

## File Structure

- `code/config.py` — minimal config (paths + thresholds only; no corpus streaming params)
- `code/domain_classifier.py` — sub-task → domain label mapping (academic / commonsense)
- `code/stats_analyzer.py` — Mann-Whitney U directional tests, Kruskal-Wallis interaction, Cohen's d
- `code/visualizer.py` — 4 figures: heatmap, boxplots, top-5 bar charts, test summary
- `code/run_experiment.py` — pipeline orchestration entry point
- `results/domain_stratified_rates.json` — 2×3 mean rate table
- `results/statistical_tests.json` — all test results + gate verdict
- `figures/` — all generated plots

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass

@dataclass
class Config:
    # Data source
    h_m1_results_path: str = "../../h-m1/experiment_results.json"

    # Statistical parameters
    alpha: float = 0.05
    seed: int = 1

    # Gate threshold
    min_corpora_directional_confirmed: int = 2  # ≥2 of 3 corpora

    # Output paths
    results_dir: str = "results"
    figures_dir: str = "figures"

def load_config() -> Config: ...
```

---

### DomainClassifier (`code/domain_classifier.py`)

**Dependencies**: none

```python
class DomainClassifier:
    COMMONSENSE_TASKS: frozenset[str]  # hellaswag + bbh subtasks
    ACADEMIC_TASKS: frozenset[str]     # all 57 MMLU subtasks

    def classify(self, subtask_name: str) -> str:
        """Returns 'academic' or 'commonsense'."""
        ...

    def build_domain_map(self, subtask_names: list[str]) -> dict[str, str]:
        """Returns {subtask_name: 'academic'|'commonsense'} for all 59 subtasks."""
        ...

    def get_groups(
        self, matrix: dict, domain_map: dict[str, str], corpus: str
    ) -> tuple[list[float], list[float]]:
        """Returns (academic_rates, commonsense_rates) for given corpus."""
        ...
```

---

### StatsAnalyzer (`code/stats_analyzer.py`)

**Dependencies**: Config, DomainClassifier

```python
import pandas as pd
from scipy import stats

class StatsAnalyzer:
    def __init__(self, config: Config): ...

    def compute_domain_stratified_rates(
        self, matrix: dict, domain_map: dict[str, str]
    ) -> dict:
        """Returns {corpus: {domain: mean_rate, domain+"_rates": list[float]}} for 2×3 table."""
        ...

    def mann_whitney_directional(
        self, group_a: list[float], group_b: list[float], alternative: str = "greater"
    ) -> dict:
        """Returns {stat, p, effect_size_r, direction_confirmed (p < alpha)}."""
        ...

    def run_directional_tests(self, stratified: dict) -> dict:
        """Runs pile academic>commonsense + c4 commonsense>academic one-tailed tests.
        Returns {test_name: {stat, p, effect_size_r, direction_confirmed}}.
        """
        ...

    def kruskal_interaction(self, stratified: dict) -> dict:
        """Kruskal-Wallis across all 6 (corpus×domain) groups.
        Returns {H, p, significant}.
        """
        ...

    def cohens_d(self, group_a: list[float], group_b: list[float]) -> float:
        """Returns Cohen's d effect size between two groups."""
        ...

    def top_n_per_corpus(
        self, matrix: dict, domain_map: dict[str, str], n: int = 5
    ) -> dict:
        """Returns {corpus: [{subtask, rate, domain}]} sorted desc."""
        ...

    def assert_gate(self, directional_tests: dict) -> bool:
        """Returns True if ≥2 corpora show expected directional pattern."""
        ...
```

---

### Visualizer (`code/visualizer.py`)

**Dependencies**: Config

```python
import pandas as pd

class Visualizer:
    def __init__(self, config: Config): ...

    def plot_domain_corpus_heatmap(self, stratified: dict) -> None:
        """2×3 heatmap (domain × corpus) with mean contamination rates.
        Saves: figures/domain_corpus_heatmap.png
        """
        ...

    def plot_domain_boxplots(self, stratified: dict) -> None:
        """3-panel boxplots (one per corpus): academic vs commonsense rate distributions.
        Saves: figures/domain_boxplots.png
        """
        ...

    def plot_top5_per_corpus(
        self, top5: dict, domain_map: dict[str, str]
    ) -> None:
        """3 bar charts (one per corpus): top-5 contaminated subtasks, color-coded by domain.
        Saves: figures/top5_per_corpus.png
        """
        ...

    def plot_directional_test_summary(self, directional_tests: dict) -> None:
        """Annotated bar chart of p-values and effect sizes per directional test.
        Saves: figures/directional_test_summary.png
        """
        ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: Config, DomainClassifier, StatsAnalyzer, Visualizer

```python
import json

def load_matrix(path: str) -> dict:
    """Loads h-m1/experiment_results.json. Returns {subtask: {corpus: rate}}."""
    ...

def save_results(stratified: dict, tests: dict, config: Config) -> None:
    """Writes results/domain_stratified_rates.json and results/statistical_tests.json."""
    ...

def main() -> None:
    """Entry: load_config -> load_matrix -> classify -> stratify ->
    directional_tests -> kruskal_interaction -> top5 -> visualize ->
    save_results -> assert_gate.
    """
    ...

if __name__ == "__main__":
    main()
```

---

## Module Dependencies

```
run_experiment.py
  ├── config.py
  ├── domain_classifier.py    (no deps)
  ├── stats_analyzer.py       -> config, domain_classifier
  └── visualizer.py           -> config
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| Config | `from config import Config` | `h-m1/code/config.py` |
| StatsAnalyzer | `from stats_analyzer import StatsAnalyzer` | `h-m1/code/stats_analyzer.py` |
| Visualizer | `from visualizer import Visualizer` | `h-m1/code/visualizer.py` |
| experiment_results | `json.load(open(...))` | `h-m1/experiment_results.json` |

**Verified from**: `h-m1/code/` (flat imports — all modules run from `code/` as cwd)

**Note**: H-M2 does NOT import H-M1 modules directly. It reimplements only what is needed (Config, StatsAnalyzer extended with Mann-Whitney, Visualizer with new figures). The sole data dependency is `h-m1/experiment_results.json`.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | config.py, directory structure (results/, figures/), requirements check (scipy, pandas, matplotlib) | 5 | 1+1+1+2 |
| A-2 | Domain Classifier | domain_classifier.py: full 59-subtask mapping, classify(), build_domain_map(), get_groups() | 9 | 2+1+3+3 |
| A-3 | Matrix Loader | load_matrix() in run_experiment.py: load h-m1/experiment_results.json, validate structure, handle fallback | 6 | 1+2+2+1 |
| A-4 | Stratified Rate Computation | StatsAnalyzer.compute_domain_stratified_rates(): 2×3 table, per-group rate lists | 8 | 2+2+2+2 |
| A-5 | Directional Statistical Tests | mann_whitney_directional(), run_directional_tests(), cohens_d(), assert_gate() | 13 | 3+2+5+3 |
| A-6 | Interaction & Top-N Analysis | kruskal_interaction(), top_n_per_corpus() — secondary metrics | 9 | 2+2+3+2 |
| A-7 | Visualization | 4 figures: heatmap, boxplots, top-5 bars, test summary with p-value annotations | 11 | 3+2+3+3 |
| A-8 | Orchestration + Results | run_experiment.py main(), save_results(), gate assertion, logging | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-4 combined=17 split, A-5, A-7], Low(4-8): [A-1, A-3, A-4, A-6, A-8]

**Revised Distribution**: High(14-17): [A-5], Medium(9-13): [A-2, A-6, A-7], Low(4-8): [A-1, A-3, A-4, A-8]

---

## Output File Paths

| File | Purpose |
|------|---------|
| `code/config.py` | Minimal config (paths + thresholds) |
| `code/domain_classifier.py` | 59-subtask → academic/commonsense mapping |
| `code/stats_analyzer.py` | Mann-Whitney U directional tests + Kruskal + Cohen's d |
| `code/visualizer.py` | 4 figure generators |
| `code/run_experiment.py` | Entry point orchestration |
| `results/domain_stratified_rates.json` | 2×3 mean contamination table |
| `results/statistical_tests.json` | All test results + gate verdict |
| `figures/domain_corpus_heatmap.png` | Primary result: 2×3 heatmap |
| `figures/domain_boxplots.png` | Distribution comparison per corpus |
| `figures/top5_per_corpus.png` | Top-5 subtasks with domain color coding |
| `figures/directional_test_summary.png` | p-values + effect sizes per test |
