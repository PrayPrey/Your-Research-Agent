# Architecture: h-e1 (EXISTENCE PoC)

**Applied**: Metric-computation pipeline pattern (windowed-aggregation + normalization), sourced from evaleval/benchmark-saturation structure referenced in 02c brief. (Archon MCP unavailable in this session — pattern taken from experiment brief research.)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze (Serena MCP unavailable in this session; not required — no base hypothesis, no existing repo code)
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## File Structure

```
h-e1/code/
  data.py        # PWC clone + JSON parse + benchmark filtering
  metrics.py      # DNSIComputer + baseline metrics (H, IR, TSLS)
  config.py       # fixed constants (window, thresholds, target benchmarks)
  train.py        # entrypoint: load -> compute -> validate -> figures
  evaluate.py     # success-rate gate check + validation
```

## Modules

### config.py

**Dependencies**: none

```python
WINDOW_MONTHS: int = 6
MIN_SOTA_ENTRIES: int = 50
MIN_HISTORY_YEARS: int = 3
SEED: int = 1
TARGET_BENCHMARKS: dict[str, int | None]  # name -> difficulty_proxy (class count / vocab size / None)
DNSI_VALID_RANGE: tuple[float, float] = (0.0, 2.0)
SUCCESS_RATE_THRESHOLD: float = 0.5
DATA_DIR: str = "data/pwc"
FIGURES_DIR: str = "figures"
```

### data.py (`code/data.py`)

**Dependencies**: config

```python
def clone_pwc_data(target_dir: str) -> None: ...
def load_evaluation_tables(json_path: str) -> list[dict]: ...
def filter_dense_benchmarks(eval_tables: list[dict], min_entries: int, min_years: int) -> list[dict]: ...
def extract_sota_history(benchmark: dict) -> list[tuple[str, float]]:  # (date_iso, accuracy), sorted
    ...
def match_target_benchmarks(dense: list[dict], targets: dict) -> dict[str, dict]:
    """Returns {benchmark_name: {history, difficulty_proxy}} for matched TARGET_BENCHMARKS"""
    ...
```

### metrics.py (`code/metrics.py`)

**Dependencies**: config, numpy, scipy.stats

```python
class DNSIComputer:
    def __init__(self, window_months: int = 6): ...
    def compute_dnsi(self, sota_history: list[tuple], difficulty_proxy: int | None) -> float | None: ...
    def _compute_windowed_improvements(self, sota_history: list[tuple]) -> "np.ndarray": ...

def compute_raw_entropy(sota_history: list[tuple]) -> float | None: ...
def compute_improvement_rate(sota_history: list[tuple]) -> float | None: ...
def compute_time_since_last_sota(sota_history: list[tuple], reference_date: str) -> int | None: ...
def validate_dnsi(dnsi_value: float | None) -> bool: ...
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: metrics, config

```python
def compute_success_rate(results: dict[str, float | None]) -> float: ...
def check_gate(results: dict[str, float | None], threshold: float) -> bool: ...
def summarize(results: dict) -> dict:  # per-benchmark status + aggregate stats
    ...
```

### train.py (`code/train.py`)

**Dependencies**: data, metrics, evaluate, config, matplotlib

```python
def run_pipeline() -> dict:
    """clone -> load -> filter -> match targets -> compute DNSI + baselines
       -> validate -> generate figures -> print gate result"""
    ...
def generate_figures(results: dict, out_dir: str) -> None:
    """Bar: success rate vs threshold; Histogram: DNSI distribution;
       Scatter: DNSI vs Raw Entropy; Bar: SOTA entry counts"""
    ...

if __name__ == "__main__":
    run_pipeline()
```

---

## Codebase Analysis (Serena) Note
Repeated per template requirement above (single canonical section is the one at top).

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data acquisition | Clone paperswithcode-data, parse evaluation-tables.json | 8 | 2+2+2+2 |
| A-2 | Benchmark filtering & matching | Filter dense benchmarks, match to 8 targets, extract sota_history + difficulty_proxy | 9 | 3+2+2+2 |
| A-3 | DNSIComputer implementation | Windowed improvement aggregation + entropy normalization + edge-case handling | 10 | 3+2+3+2 |
| A-4 | Baseline metrics | Raw entropy, improvement rate, time-since-last-SOTA | 6 | 2+1+2+1 |
| A-5 | Validation & gate check | validate_dnsi, success-rate computation, MUST_WORK gate | 5 | 1+2+1+1 |
| A-6 | Visualization | 4 required/optional figures (bar, histogram, scatter, coverage) saved to figures/ | 7 | 2+1+2+2 |
| A-7 | Pipeline integration (train.py) | Wire data -> metrics -> evaluate -> figures, activation/success/failure logging | 6 | 1+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3], Low(4-8): [A-1, A-4, A-5, A-6, A-7]
