# Architecture: H-E1 — FAIR Score Variance Existence

**Hypothesis Type**: EXISTENCE (PoC)
**Applied**: async-batch-pipeline pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## File Organization

- `config.py` — hardcoded constants, argparse entry
- `src/collect_openml.py` — cohort construction
- `src/score_fuji.py` — async F-UJI batch scoring
- `src/analyze.py` — statistical analysis
- `src/visualize.py` — figure generation
- `src/main.py` — orchestration
- `results/fair_scores.csv` — per-dataset scores (output)
- `results/existence_metrics.json` — CV, n_high, n_low, Spearman (output)
- `results/gate_result.json` — PASS/FAIL gate decision (output)
- `figures/*.png` — distribution plots (output)

---

## Module Interfaces

### Config (`config.py`)

**Dependencies**: none

```python
OPENML_UPLOAD_DATE_MIN: str = "2018-01-01"
OPENML_TASK_TYPES: list = ["supervised_classification", "supervised_regression"]
FUJI_API_BASE: str = "http://localhost:1071"
FUJI_CONCURRENCY: int = 10
FUJI_RETRY_MAX: int = 3
FUJI_RETRY_BASE_S: float = 2.0
FAIR_THRESHOLD: float = 0.5
CV_GATE: float = 0.15
GROUP_SIZE_GATE: int = 500
RESULTS_DIR: str = "results"
FIGURES_DIR: str = "figures"

def parse_args() -> argparse.Namespace: ...
```

---

### OpenML Cohort Builder (`src/collect_openml.py`)

**Dependencies**: config, openml

```python
def list_openml_datasets(
    upload_date_min: str,
    task_types: list[str],
) -> pd.DataFrame:
    """Returns DataFrame: did, name, upload_date, NumberOfInstances,
    NumberOfFeatures, MajorityClassPercentage, landing_page_url"""
    ...

def deduplicate_cohort(df: pd.DataFrame) -> pd.DataFrame:
    """Keep latest version per dataset name."""
    ...

def build_cohort(cfg) -> pd.DataFrame: ...
```

---

### F-UJI Async Batch Scorer (`src/score_fuji.py`)

**Dependencies**: config, aiohttp, asyncio

```python
async def score_one(
    session: aiohttp.ClientSession,
    sem: asyncio.Semaphore,
    did: int,
    landing_url: str,
    retry_max: int,
    retry_base: float,
) -> dict:
    """Returns {did, fair_score, sub_criteria: list[float], status}"""
    ...

async def score_batch(
    cohort: pd.DataFrame,
    fuji_base: str,
    concurrency: int,
    retry_max: int,
    retry_base: float,
    cache_path: str | None = None,
) -> pd.DataFrame:
    """Returns DataFrame: did, fair_score, status"""
    ...

def score_cohort(cohort: pd.DataFrame, cfg) -> pd.DataFrame: ...

def fuji_fallback_proxy(cohort: pd.DataFrame) -> pd.DataFrame:
    """OpenML machine-computed qualities as FAIR proxy when F-UJI unavailable."""
    ...
```

---

### Statistical Analyzer (`src/analyze.py`)

**Dependencies**: config, scipy, pandas

```python
def compute_cv(scores: pd.Series) -> float: ...

def compute_group_sizes(
    scores: pd.Series, threshold: float
) -> tuple[int, int]:
    """Returns (n_high, n_low)."""
    ...

def compute_spearman_correlations(
    df: pd.DataFrame, score_col: str, covariate_cols: list[str]
) -> dict[str, float]: ...

def detect_bimodality(scores: pd.Series) -> dict:
    """Returns {bimodal: bool, dip_stat: float, dip_p: float}"""
    ...

def run_analysis(scored: pd.DataFrame, cfg) -> dict:
    """Returns existence_metrics dict."""
    ...

def evaluate_gate(metrics: dict, cfg) -> dict:
    """Returns {passed: bool, cv: float, n_high: int, n_low: int, reason: str}"""
    ...
```

---

### Visualization Generator (`src/visualize.py`)

**Dependencies**: analyze, matplotlib, seaborn

```python
def plot_fair_distribution(
    scored: pd.DataFrame,
    score_col: str,
    threshold: float,
    out_path: str,
) -> None: ...

def plot_cv_summary(metrics: dict, out_path: str) -> None: ...

def generate_figures(scored: pd.DataFrame, metrics: dict, figures_dir: str, cfg) -> None: ...
```

---

### Results Persister (`src/main.py` inline helpers)

**Dependencies**: config, pandas, json

```python
def save_scores_csv(scored: pd.DataFrame, path: str) -> None: ...
def save_metrics_json(metrics: dict, path: str) -> None: ...
def save_gate_json(gate: dict, path: str) -> None: ...
```

---

### Main Orchestrator (`src/main.py`)

**Dependencies**: all modules, config

```python
def main() -> None:
    """
    1. parse_args / load config
    2. build_cohort -> cohort DataFrame
    3. score_cohort -> scored DataFrame
    4. save_scores_csv
    5. run_analysis -> metrics
    6. evaluate_gate -> gate
    7. save_metrics_json, save_gate_json
    8. generate_figures
    9. print gate result summary
    """
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | config.py, directory structure, requirements.txt, smoke test | 5 | 1+1+1+2 |
| A-2 | OpenML Cohort Builder | list_datasets, filter by date/task-type, deduplicate | 8 | 2+2+2+2 |
| A-3 | F-UJI Async Batch Scorer | aiohttp async, semaphore concurrency, retry, cache, fallback | 15 | 4+3+4+4 |
| A-4 | Statistical Analyzer | CV, group sizes, Spearman correlations, bimodality, gate eval | 10 | 3+2+3+2 |
| A-5 | Visualization Generator | distribution plot, CV summary, figure save | 7 | 2+2+2+1 |
| A-6 | Main Orchestrator + Persistence | orchestrate all modules, CSV/JSON output, print summary | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-4, A-6], Low(4-8): [A-1, A-2, A-5]
