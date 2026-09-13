# Architecture: H-M2

**Type**: MECHANISM | **Gate**: SHOULD_WORK | **Tier**: FULL

Applied: rule-based classification + temporal ratio pipeline (no matching KB code example; standard data-analysis pattern used)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base hypothesis code reuse required (H-M1 was a separate analysis, no shared modules specified).

---

## Module Structure

### data_loader.py (`code/data_loader.py`)

**Dependencies**: datasets (HF), requests

```python
def load_pwc_datasets() -> list[dict]: ...
def fetch_semantic_scholar_date(paper_title: str) -> str | None: ...
```

### classifier.py (`code/classifier.py`)

**Dependencies**: none (stdlib)

```python
EMERGENT_KEYWORDS: list[str]
EMERGENT_BENCHMARKS: set[str]

def classify_benchmark(name: str, description: str, tasks: list[str]) -> str: ...
```

### date_extractor.py (`code/date_extractor.py`)

**Dependencies**: data_loader

```python
def extract_benchmark_date(benchmark_metadata: dict) -> int | None: ...
def parse_paper_date(paper: dict) -> int | None: ...
def resolve_missing_dates(benchmarks: list[dict]) -> list[dict]: ...
```

### analysis.py (`code/analysis.py`)

**Dependencies**: classifier, date_extractor

```python
def build_benchmark_records(raw_datasets: list[dict]) -> list[dict]: ...
def compute_post2020_ratio(benchmarks: list[dict]) -> dict: ...
def compute_creation_rate_acceleration(benchmarks: list[dict]) -> dict: ...
def evaluate_hypothesis(results: dict) -> dict: ...
```

### visualize.py (`code/visualize.py`)

**Dependencies**: matplotlib, analysis

```python
def plot_gate_metrics(results: dict, out_path: str) -> None: ...
def plot_creation_timeline(benchmarks: list[dict], out_path: str) -> None: ...
def plot_cumulative_curve(benchmarks: list[dict], out_path: str) -> None: ...
def plot_type_distribution_by_year(benchmarks: list[dict], out_path: str) -> None: ...
```

### run_experiment.py (`code/run_experiment.py`)

**Dependencies**: all above

```python
def main() -> None: ...
```

### config.py (`code/config.py`)

```python
POST_2020_THRESHOLD: float = 0.80
GPT3_RELEASE_DATE: str = "2020-06-01"
PWC_DATASET_ID: str = "pwc-archive/datasets"
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Setup project structure | Create code/, figures/, results/, config.py | 4 | 1+1+1+1 |
| E2 | Implement data_loader | Load PWC dataset via HF datasets lib, Semantic Scholar fallback with rate limiting | 12 | 3+4+3+2 |
| E3 | Implement classifier | Keyword + name + task-based rule classifier | 8 | 2+1+4+1 |
| E4 | Implement date_extractor | Parse PWC paper dates, integrate SS fallback, handle missing dates | 10 | 3+3+3+1 |
| E5 | Implement analysis pipeline | Build records, compute post-2020 ratio, acceleration metrics, gate evaluation | 11 | 3+3+4+1 |
| E6 | Implement visualization suite | 4 required figures (gate bar, timeline histogram, cumulative curve, stacked bar) | 9 | 3+1+3+2 |
| E7 | Implement run_experiment orchestration | Wire pipeline end-to-end, save results.json, error handling | 10 | 2+4+2+2 |
| E8 | Integration test on full PWC dataset | Run full pipeline, verify >=50 emergent benchmarks, verify runtime <20min | 8 | 2+3+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E2,E4,E5,E6,E7], Low(4-8): [E1,E3,E8]

---

## External Dependencies

None — green-field project, no base hypothesis code reuse.

## Data Flow

1. E2 loads PWC datasets + resolves missing dates via Semantic Scholar
2. E3 classifies each benchmark (emergent-capability / traditional)
3. E4 extracts/normalizes creation year per benchmark
4. E5 merges classification + dates, computes ratio and gate PASS/FAIL
5. E6 renders 4 figures from E5 outputs
6. E7 orchestrates E2-E6, persists `results/results.json`
