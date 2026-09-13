# Architecture: H-M3 (Researcher Attention Shift)

**Type:** MECHANISM | **Gate:** SHOULD_WORK

Applied: statistical-hypothesis-testing pattern (chi-square contingency analysis) — no directly relevant KB implementation found; general pattern used from PRD/brief spec.

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch; no base hypothesis code to reuse.

---

## File Structure

```
h-m3/code/
├── config.py
├── data_collection.py
├── classifier.py
├── analysis.py
├── visualization.py
├── run_experiment.py
```

---

## Modules

### config.py

**Dependencies**: none

```python
EMERGENT_BENCHMARKS: list[str]  # MMLU, BIG-Bench, HumanEval, GSM8K, MATH, ARC, HellaSwag, WinoGrande, TruthfulQA, LAMBADA
TRADITIONAL_BENCHMARKS: list[str]  # ImageNet, CIFAR-10, CIFAR-100, MNIST, SQuAD, GLUE, CoNLL, Penn Treebank
TIME_RANGE = ("2018-01", "2024-12")
SPLIT_DATE = "2021-01"
PRE_POST_SPLITS = ["2020-01", "2021-01", "2022-01"]  # ablation
```

### data_collection.py (`data_collection.py`)

**Dependencies**: config.py

```python
@dataclass
class PaperCountRecord:
    benchmark: str
    category: Literal["emergent", "traditional"]
    year_month: str
    paper_count: int

def fetch_from_pwc_api(benchmarks: list[str]) -> list[PaperCountRecord]: ...
def fetch_from_huggingface_fallback(benchmarks: list[str]) -> list[PaperCountRecord]: ...
def collect_paper_counts(retries: int = 3) -> pd.DataFrame: ...  # tries PWC API, falls back to HF, retries w/ backoff
```

### classifier.py (`classifier.py`)

**Dependencies**: config.py

```python
def classify_benchmark(name: str) -> Literal["emergent", "traditional", "unknown"]: ...
def label_dataframe(df: pd.DataFrame) -> pd.DataFrame: ...  # adds 'category' column
```

### analysis.py (`analysis.py`)

**Dependencies**: config.py, classifier.py

```python
def assign_period(year_month: str, split_date: str = "2021-01") -> str: ...  # pre_2021 / post_2021
def compute_shares(df: pd.DataFrame, split_date: str) -> pd.DataFrame: ...  # period x category totals + emergent_share
def chi_square_test(period_totals: pd.DataFrame) -> dict: ...  # chi2, p_value, dof, expected
def compare_2024_absolute(df: pd.DataFrame) -> dict: ...  # emergent_2024_count, traditional_2024_count
def analyze_attention_shift(df: pd.DataFrame, split_date: str = "2021-01") -> dict: ...  # full pipeline, returns all metrics
def run_ablation_time_windows(df: pd.DataFrame) -> dict[str, dict]: ...  # runs analyze_attention_shift per split in PRE_POST_SPLITS
```

### visualization.py (`visualization.py`)

**Dependencies**: analysis.py

```python
def plot_gate_metrics(result: dict, out_path: str) -> None: ...  # required: bar chart pre vs post share
def plot_share_timeline(df: pd.DataFrame, out_path: str) -> None: ...
def plot_absolute_counts(df: pd.DataFrame, out_path: str) -> None: ...  # stacked area
def plot_benchmark_heatmap(df: pd.DataFrame, out_path: str) -> None: ...  # top 20 by year
def plot_chi_square_residuals(result: dict, out_path: str) -> None: ...
```

### run_experiment.py (`run_experiment.py`)

**Dependencies**: all modules

```python
def main() -> None: ...
    # 1. collect_paper_counts()
    # 2. label_dataframe()
    # 3. analyze_attention_shift() -> primary result
    # 4. run_ablation_time_windows() -> sensitivity
    # 5. generate all figures to figures/
    # 6. write results.json with gate PASS/FAIL determination
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config setup | Benchmark category lists, time constants | 4 | 1+1+1+1 |
| A-2 | PWC API client | Fetch leaderboard paper counts via paperswithcode-client | 12 | 3+3+3+3 |
| A-3 | HuggingFace fallback | Load pwc-archive/datasets, retry/backoff logic | 10 | 2+3+3+2 |
| A-4 | Benchmark classifier | Map benchmark name to emergent/traditional | 5 | 1+1+2+1 |
| A-5 | Share & period aggregation | Monthly aggregation, pre/post split, share calc | 8 | 2+2+2+2 |
| A-6 | Chi-square analysis | Contingency table + chi2_contingency + gate metrics | 7 | 2+2+2+1 |
| A-7 | Ablation: time window sensitivity | Run analysis across 3 split dates | 6 | 2+2+1+1 |
| A-8 | Visualization pipeline | 5 figures (gate, timeline, area, heatmap, residuals) | 10 | 3+2+2+3 |
| A-9 | Results aggregation & gate decision | Combine metrics, write results.json, PASS/FAIL | 6 | 2+1+1+2 |
| A-10 | End-to-end experiment runner | Wire pipeline, error handling, logging | 8 | 2+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-8], Low(4-8): [A-1, A-4, A-5, A-6, A-7, A-9, A-10]

---

## External Dependencies

Green-field project — no base hypothesis code reused. No External Dependencies section required.

## Package Dependencies

```
paperswithcode-client>=0.3.0
datasets>=2.14.0
scipy>=1.10.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
pyyaml>=6.0
```
