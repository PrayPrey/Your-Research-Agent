# Architecture: H-E1 — Conditional Demographic Association Density Pipeline

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Generated:** 2026-03-14

Applied: Standard corpus analysis pipeline pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch. No base hypothesis code exists.

---

## File Structure

```
h-e1/
  code/
    config.py
    corpus_filter.py
    entropy_measure.py
    statistical_tests.py
    visualize.py
    run_experiment.py
  figures/
  data/
    corpora/       # C0–C6 JSONL subsets
    scores/        # fastText scores cache
  results.json
  04_validation.md
```

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies:** None

```python
SEED = 42
N_DOCS = 10_000_000
WINDOW_SIZE = 10
N_BOOTSTRAP = 10_000
GATE_THRESHOLD_PCT = 5.0

FASTTEXT_MODEL_ID = "mlfoundations/fasttext-oh-eli5"
DATASET_ID = "mlfoundations/dclm-baseline-1.0"

CONFIGURATIONS: dict = {
    "C0": {"type": "unfiltered", "percentile": 0},
    "C1": {"type": "fasttext",   "percentile": 10},
    "C2": {"type": "fasttext",   "percentile": 30},
    "C3": {"type": "fasttext",   "percentile": 50},
    "C4": {"type": "fasttext",   "percentile": 70},
    "C5": {"type": "fasttext",   "percentile": 90},
    "C6": {"type": "doremi",     "percentile": None},
}

OCCUPATION_LEXICON: list[str] = [...]   # 60 WinoBias occupations
DEMOGRAPHIC_LEXICON: list[str] = [...]  # gendered pronouns + demographic NEs

DATA_DIR: str = "h-e1/data"
FIGURES_DIR: str = "h-e1/figures"
RESULTS_PATH: str = "h-e1/results.json"
VALIDATION_PATH: str = "h-e1/04_validation.md"
```

---

### CorpusFilter (`code/corpus_filter.py`)

**Dependencies:** config

```python
class CorpusFilter:
    def __init__(self, fasttext_model_path: str, seed: int = 42): ...

    def load_and_sample(self, dataset_id: str, n_docs: int) -> list[dict]: ...

    def score_documents(self, docs: list[dict]) -> list[float]: ...

    def apply_fasttext_filter(
        self,
        docs: list[dict],
        scores: list[float],
        percentile: int
    ) -> list[dict]: ...

    def apply_doremi_reweight(
        self,
        docs: list[dict],
        domain_key: str = "source"
    ) -> list[dict]: ...

    def save_corpus(self, docs: list[dict], config_id: str, data_dir: str) -> str: ...

    def load_corpus(self, config_id: str, data_dir: str) -> list[dict]: ...

    def build_all_corpora(self, data_dir: str) -> dict[str, str]: ...
```

---

### EntropyMeasure (`code/entropy_measure.py`)

**Dependencies:** config

```python
class EntropyMeasure:
    def __init__(
        self,
        occ_lexicon: list[str],
        demo_lexicon: list[str],
        window_size: int = 10
    ): ...

    def compute_joint_counts(
        self,
        docs: list[dict]
    ) -> dict[str, dict[str, int]]: ...

    def joint_counts_to_arrays(
        self,
        joint_counts: dict[str, dict[str, int]]
    ) -> tuple[list[str], list[str]]: ...

    def compute_conditional_entropy(
        self,
        docs: list[dict]
    ) -> float: ...

    def compute_all_entropies(
        self,
        corpora: dict[str, list[dict]]
    ) -> dict[str, float]: ...
```

---

### StatisticalTests (`code/statistical_tests.py`)

**Dependencies:** config

```python
class StatisticalTests:
    def __init__(self, n_bootstrap: int = 10_000): ...

    def relative_entropy_change(
        self,
        h_c1: float,
        h_c5: float
    ) -> float: ...

    def bootstrap_ci(
        self,
        entropy_samples_a: list[float],
        entropy_samples_b: list[float],
        confidence: float = 0.95
    ) -> tuple[float, float]: ...

    def spearman_correlation(
        self,
        percentiles: list[int],
        entropy_values: list[float]
    ) -> tuple[float, float]: ...

    def ols_regression(
        self,
        fasttext_scores: list[float],
        demo_densities: list[float]
    ) -> dict: ...

    def run_all_tests(
        self,
        entropies: dict[str, float],
        joint_counts_per_config: dict[str, dict]
    ) -> dict: ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies:** config

```python
class Visualizer:
    def __init__(self, figures_dir: str): ...

    def bar_chart_gate_metric(
        self,
        entropies: dict[str, float],
        ci_bounds: dict[str, tuple[float, float]]
    ) -> str: ...

    def monotonic_trend_plot(
        self,
        entropies: dict[str, float]
    ) -> str: ...

    def demographic_heatmap(
        self,
        joint_counts_c1: dict[str, dict[str, int]],
        joint_counts_c5: dict[str, dict[str, int]]
    ) -> str: ...

    def relative_change_chart(
        self,
        relative_changes: dict[str, float],
        gate_threshold: float = 5.0
    ) -> str: ...

    def generate_all(
        self,
        entropies: dict[str, float],
        joint_counts: dict[str, dict],
        stats_results: dict
    ) -> list[str]: ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies:** config, CorpusFilter, EntropyMeasure, StatisticalTests, Visualize

```python
def setup_directories() -> None: ...

def verify_mechanism_activated(
    config_entropies: dict[str, float],
    results: dict
) -> tuple[bool, dict]: ...

def write_results_json(results: dict, path: str) -> None: ...

def write_validation_md(results: dict, mechanism_check: dict, path: str) -> None: ...

def main() -> None: ...
```

---

## Data Flow

- `run_experiment.py` orchestrates all modules sequentially
- `corpus_filter.py` produces JSONL corpora saved to `data/corpora/`
- `entropy_measure.py` reads corpora, produces `{config_id: H_value}` + joint count matrices
- `statistical_tests.py` consumes entropies and joint counts, produces stats dict
- `visualize.py` consumes entropies + stats, writes PNG files to `figures/`
- `run_experiment.py` writes `results.json` and `04_validation.md`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment Setup | Install deps, verify HF access, download fastText model, create directory structure | 5 | 1+1+1+2 |
| A-2 | Corpus Filter Module | Implement `corpus_filter.py`: sample 10M docs, fastText scoring, percentile filters C0–C5, DoReMi reweighting C6, JSONL save/load | 16 | 4+3+5+4 |
| A-3 | Entropy Measurement Module | Implement `entropy_measure.py`: co-occurrence window scan, joint count accumulation, pyitlib entropy computation for all 7 configurations | 14 | 4+2+4+4 |
| A-4 | Statistical Tests Module | Implement `statistical_tests.py`: relative entropy change, BCa bootstrap CI (n=10,000), Spearman ρ, OLS regression | 13 | 3+2+5+3 |
| A-5 | Visualization Module | Implement `visualize.py`: 4 figures (bar chart, trend plot, heatmap, relative change chart) saved to figures/ | 10 | 3+2+3+2 |
| A-6 | Experiment Orchestration and Reporting | Implement `run_experiment.py`: full pipeline orchestration, mechanism verification, results.json + 04_validation.md output | 11 | 3+3+3+2 |

**Distribution:** VeryHigh(18-20): [] | High(14-17): [A-2, A-3] | Medium(9-13): [A-4, A-5, A-6] | Low(4-8): [A-1]

---

## External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| datasets | >=2.14.0 | DCLM-POOL streaming load |
| fasttext | >=0.9.2 | fasttext-oh-eli5 document scoring |
| pyitlib | >=0.2.2 | H(occupation|demographic) via entropy_conditional() |
| scipy | >=1.11.0 | Bootstrap BCa CI, Spearman ρ |
| statsmodels | >=0.14.0 | OLS regression |
| numpy | >=1.24.0 | Array operations |
| matplotlib | >=3.7.0 | Figure generation |
| seaborn | >=0.12.0 | Heatmap |
| tqdm | >=4.65.0 | Progress bars |
| jsonlines | >=3.1.0 | JSONL I/O |

**Fallback:** If DCLM-Pool gated access unavailable — use `mlfoundations/dclm-baseline-1.0` as C5 proxy and `DCLM-RefinedWeb` as C0 proxy; run 2-endpoint existence check only.

---

## Gate Condition Reference

- **PASS:** `relative_entropy_change >= 5.0` AND bootstrap 95% CI excludes 0
- **FAIL:** Either condition unmet — blocks H-M1, H-M2, H-M3
