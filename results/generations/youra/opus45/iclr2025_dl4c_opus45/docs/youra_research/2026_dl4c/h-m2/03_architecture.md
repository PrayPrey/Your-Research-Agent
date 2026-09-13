# Architecture: H-M2 Execution Depth Analysis

**Applied**: analysis-hypothesis flat-module pattern (no training, reuse prior results)
**Applied**: trace-based execution measurement pattern (Python stdlib trace module)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-m1)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/20260323_dl4c/h-m1/code/`
**Findings**: H-M1 uses flat 5-file structure (config.py, data_loader.py, analyze.py, visualize.py, run_experiment.py). All modules import via flat namespace (`from config import CONFIG`). H-E1 results stored in separate `rl_execution_results.json` / `dpo_execution_results.json` files with `status` and `error_trace` fields. H-M2 will mirror this flat structure exactly.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| HM1Config pattern | Reference only - not imported | `h-m1/code/config.py` |
| load_h_e1_results pattern | Reference only - not imported | `h-m1/code/data_loader.py` |
| classify_error | Inlined (copied from h-m1) | `h-m1/code/data_loader.py` |
| H-E1 RL results | `../../h-e1/code/outputs/rl_execution_results.json` | h-e1/code/outputs/ |
| H-E1 DPO results | `../../h-e1/code/outputs/dpo_execution_results.json` | h-e1/code/outputs/ |

**Verified from**: `docs/youra_research/20260323_dl4c/h-m1/code/` (actual implementation)
**Pattern**: H-M1 inlines helper functions rather than importing across hypothesis folders.

---

## File Organization

```
h-m2/code/
  config.py          - HM2Config dataclass with paths and thresholds
  data_loader.py     - Load H-E1 results, extract failure cases + generated code
  depth_tracer.py    - Execution depth measurement via Python trace module
  analyze.py         - t-test statistical analysis, Cohen's d
  visualize.py       - All figure generation
  run_experiment.py  - Entry point, orchestrates pipeline
  outputs/           - metrics.json, experiment_results.json, depth_data.csv
  figures/           - gate_metrics.png, depth_distribution.png, ...
```

---

## Module Definitions

### Config (`config.py`)

**Dependencies**: stdlib only

```python
from dataclasses import dataclass
import os

@dataclass
class HM2Config:
    # H-E1 data paths (relative to h-m2/code/)
    rl_results_path: str
    dpo_results_path: str
    h_e1_experiment_results_path: str
    h_e1_metrics_path: str
    # Output paths
    output_dir: str
    figures_dir: str
    # Statistical thresholds
    t_test_p_threshold: float = 0.05
    alternative: str = "greater"
    execution_timeout: float = 5.0
    random_seed: int = 42
    # Expected counts
    expected_rl_failures: int = 236
    expected_dpo_failures: int = 530
    def __post_init__(self): ...  # normalize to absolute paths

CONFIG = HM2Config(...)
```

---

### DataLoader (`data_loader.py`)

**Dependencies**: config.py

```python
from typing import Dict, List, Tuple
from config import HM2Config

def load_h_e1_results(config: HM2Config) -> Tuple[List[dict], List[dict]]:
    """Load rl_execution_results.json and dpo_execution_results.json.
    Returns (rl_results, dpo_results) - all samples including passes."""
    ...

def extract_failures(results: List[dict]) -> List[dict]:
    """Filter to status == 'fail' records only."""
    ...

def validate_data_integrity(
    rl_failures: List[dict],
    dpo_failures: List[dict],
    config: HM2Config,
) -> Dict: ...

def classify_error(error_trace: str) -> str:
    """Inline ICSE 2025 taxonomy: syntax/runtime/assertion/other/pass."""
    ...
```

---

### DepthTracer (`depth_tracer.py`)

**Dependencies**: stdlib (trace, ast, signal), config.py

```python
from dataclasses import dataclass
from typing import Optional
from config import HM2Config

@dataclass
class DepthResult:
    sample_id: str
    model: str          # "rl" or "dpo"
    problem_id: str
    total_lines: int
    executed_lines: int
    execution_depth: float   # executed_lines / max(total_lines, 1)
    error_type: str          # syntax/runtime/assertion/other
    trace_success: bool

def count_executable_lines(code_string: str) -> int:
    """Count non-blank, non-comment lines using ast.parse."""
    ...

def measure_execution_depth(
    code_string: str,
    sample_id: str,
    problem_id: str,
    model: str,
    timeout: float = 5.0,
) -> DepthResult:
    """Use trace.Trace(count=True, trace=False) to measure lines executed before failure.
    SyntaxError -> depth=0. Timeout -> depth=partial. Exception -> depth from trace results."""
    ...

def measure_all_failures(
    failures: List[dict],
    model: str,
    config: HM2Config,
) -> List[DepthResult]:
    """Batch measure with progress reporting. Catches per-sample failures."""
    ...
```

---

### Analyzer (`analyze.py`)

**Dependencies**: depth_tracer.py, config.py, numpy, scipy

```python
from typing import Dict, List, Tuple
import numpy as np
from scipy import stats
from depth_tracer import DepthResult
from config import HM2Config

def run_ttest(
    rl_depths: List[float],
    dpo_depths: List[float],
    alternative: str = "greater",
) -> Tuple[float, float]:
    """scipy.stats.ttest_ind, one-sided. Returns (t_statistic, p_value_one_sided)."""
    ...

def compute_cohens_d(rl_depths: List[float], dpo_depths: List[float]) -> float:
    """Pooled-std Cohen's d effect size."""
    ...

def compute_descriptive_stats(depths: List[float]) -> Dict:
    """mean, std, median, min, max, n, 95% CI."""
    ...

def run_analysis(
    rl_results: List[DepthResult],
    dpo_results: List[DepthResult],
    config: HM2Config,
) -> Dict:
    """Full analysis pipeline: t-test + Cohen's d + descriptive stats.
    Saves metrics.json, experiment_results.json, depth_data.csv.
    Returns metrics dict."""
    ...
```

---

### Visualizer (`visualize.py`)

**Dependencies**: analyze.py, depth_tracer.py, matplotlib, seaborn

```python
from typing import Dict, List
from depth_tracer import DepthResult

def plot_gate_metrics(metrics: Dict, figures_dir: str) -> None:
    """Bar chart: target p=0.05 vs actual p-value, RL vs DPO mean depth. -> gate_metrics.png"""
    ...

def plot_depth_distribution(
    rl_results: List[DepthResult],
    dpo_results: List[DepthResult],
    figures_dir: str,
) -> None:
    """Violin/box plot of execution depth distributions. -> depth_distribution.png"""
    ...

def plot_depth_by_error_type(
    rl_results: List[DepthResult],
    dpo_results: List[DepthResult],
    figures_dir: str,
) -> None:
    """Grouped bar chart: mean depth by error type (syntax/runtime/assertion). -> depth_by_error_type.png"""
    ...

def plot_depth_cdf(
    rl_results: List[DepthResult],
    dpo_results: List[DepthResult],
    figures_dir: str,
) -> None:
    """CDF of execution depth for RL vs DPO. -> depth_cdf.png"""
    ...

def plot_depth_scatter(
    rl_results: List[DepthResult],
    dpo_results: List[DepthResult],
    figures_dir: str,
) -> None:
    """Scatter: execution depth vs total_lines, colored by model. -> depth_scatter.png"""
    ...

def generate_all_figures(
    rl_results: List[DepthResult],
    dpo_results: List[DepthResult],
    metrics: Dict,
    figures_dir: str,
) -> None: ...
```

---

### RunExperiment (`run_experiment.py`)

**Dependencies**: config.py, data_loader.py, depth_tracer.py, analyze.py, visualize.py

```python
from config import CONFIG, HM2Config

def main(config: HM2Config = None) -> int:
    """H-M2 execution depth analysis pipeline.
    1. Load H-E1 RL/DPO execution results
    2. Validate data integrity
    3. Measure execution depth for all failures
    4. Run t-test analysis
    5. Generate figures
    Returns 0 if gate passes (p < 0.05 and RL > DPO), 1 otherwise."""
    ...

if __name__ == "__main__":
    sys.exit(main())
```

---

## Data Flow

- `run_experiment.py` -> `data_loader.load_h_e1_results` -> List[dict] (raw H-E1 records)
- `data_loader.extract_failures` -> failure subsets (rl_failures, dpo_failures)
- `depth_tracer.measure_all_failures` -> List[DepthResult] per model
- `analyze.run_analysis` -> metrics dict + saved files
- `visualize.generate_all_figures` -> saved PNG files

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment Setup | Create h-m2/code/ structure, config.py with HM2Config, verify H-E1 data paths accessible | 6 | 1+1+2+2 |
| A-2 | Data Loading | Implement data_loader.py: load H-E1 results, extract failures, inline classify_error, validate counts | 9 | 2+2+3+2 |
| A-3 | Executable Line Counter | Implement count_executable_lines using ast.parse, handle edge cases (empty, comments, SyntaxError) | 10 | 3+1+4+2 |
| A-4 | Trace Execution Engine | Implement measure_execution_depth with trace.Trace, timeout handling (signal.alarm), SyntaxError path | 15 | 4+2+5+4 |
| A-5 | Batch Depth Measurement | Implement measure_all_failures with progress reporting, per-sample error catching, batch logging | 10 | 2+3+3+2 |
| A-6 | Statistical Analysis | Implement t-test (one-sided), Cohen's d, descriptive stats, gate pass logic in analyze.run_analysis | 12 | 3+2+4+3 |
| A-7 | Output Serialization | Save metrics.json, experiment_results.json, depth_data.csv inside run_analysis | 8 | 2+2+2+2 |
| A-8 | Visualization | Implement all 5 figure generators (gate_metrics, distribution, error_type, cdf, scatter) | 14 | 3+2+4+5 |
| A-9 | Pipeline Integration | Implement run_experiment.py main(), end-to-end test, logging setup, exit code | 9 | 2+2+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4, A-8], Medium(9-13): [A-3, A-5, A-6, A-9], Low(4-8): [A-1, A-2, A-7]

---

## Key Interface Notes for Phase 4

- H-E1 record format (from actual h-m1 code): `{"status": "fail"|"pass", "error_trace": str|None, "generated_code": str, "problem_id": str}`
- H-M1 verified H-E1 paths: `../../h-e1/code/outputs/rl_execution_results.json` and `dpo_execution_results.json`
- All modules use flat imports (no subdirectory packages), matching h-m1 pattern
- classify_error must be inlined (not imported from h-m1) per h-m1 lesson learned
- trace.Trace is sensitive to multiprocessing; use signal-based timeout not threading
- depth_data.csv columns: `sample_id, model, problem_id, total_lines, executed_lines, depth, error_type`

---

*Generated by Phase 3 Architecture Workflow | Anonymous Research Pipeline*
*Hypothesis: H-M2 | Type: MECHANISM | Gate: SHOULD_WORK*
*Base Code Analyzed: h-m1/code/ (actual implementation)*
