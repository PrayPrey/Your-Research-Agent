# Architecture: h-m1

**Type:** MECHANISM | **Applied:** statistical-correlation-pipeline-pattern (Archon KB: "DL experiment architecture" — small-n correlation analysis with bootstrap CI)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: Serena MCP unavailable in this environment; used direct Read on h-e1/code/*.py instead (equivalent manual analysis).
**Analyzed Path**: `h-e1/code/` (train.py, metrics.py, evaluate.py, config.py)
**Findings**:
- h-e1 exposes `run_pipeline() -> dict` in `train.py` (not a saved JSON file). The dict contains `results["dnsi"]` = `{benchmark_name: float|None}`.
- **Critical deviation from PRD/brief**: PRD/02c assume `h-e1/code/results/dnsi_results.json` exists on disk — it does NOT. No file write occurs in h-e1/train.py. h-m1 MUST import `run_pipeline` from h-e1 and call it in-process, OR read benchmark_data via `h-e1/code/data.py` directly. Chose: import and call `run_pipeline()`.
- h-e1 benchmark keys (from `data.py`/`config.py` `TARGET_BENCHMARKS`) must be mapped to h-m1's benchmark names (ImageNet, CIFAR-10, ObjectNet, HANS) — verify exact key strings via `CONFIG`/`TARGET_BENCHMARKS` at runtime, do not hardcode assumptions.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| run_pipeline | `from train import run_pipeline` (add h-e1/code to sys.path) | `h-e1/code/train.py` |
| CONFIG, TARGET_BENCHMARKS | `from config import CONFIG, TARGET_BENCHMARKS` | `h-e1/code/config.py` |
| validate_dnsi | `from metrics import validate_dnsi` | `h-e1/code/metrics.py` |

**Verified from**: `h-e1/code/` (actual implementation, not `03_architecture.md` spec — no `results/dnsi_results.json` exists).

**Integration note**: h-m1/code/data.py must do:
```python
import sys
sys.path.insert(0, "../../h-e1/code")
from train import run_pipeline
```

---

## File Structure

```
h-m1/code/
  config.py       # gap ground truth + analysis constants
  data.py         # load DNSI from h-e1 (in-process call) + merge with gap data
  metrics.py       # CorrelationAnalyzer (Pearson/Spearman/bootstrap)
  evaluate.py      # gate check (MUST_WORK) + summary
  train.py         # pipeline orchestration + figure generation
  results/         # output json (created at runtime)
  figures/         # output png (created at runtime)
```

---

## Modules

### config.py (`h-m1/code/config.py`)

**Dependencies**: none

```python
CONFIG = {
    "n_bootstrap": 10000,
    "seed": 42,
    "success_r_threshold": -0.4,
    "fail_r_threshold": -0.2,
    "ci_level": 0.95,
    "figures_dir": "figures",
    "results_dir": "results",
}

GAP_DATA = {
    "ImageNet": 0.125,
    "CIFAR-10": 0.040,
    "ObjectNet": 0.425,
    "HANS": 0.400,
}
```

### data.py (`h-m1/code/data.py`)

**Dependencies**: config.py, h-e1/code/train.py (external)

```python
def load_dnsi_from_h_e1() -> dict[str, float | None]: ...
def build_dataset(dnsi: dict, gap: dict) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Returns (benchmark_names, dnsi_array, gap_array) for benchmarks with valid DNSI + gap."""
```

### metrics.py (`h-m1/code/metrics.py`)

**Dependencies**: config.py

```python
class CorrelationAnalyzer:
    def __init__(self, n_bootstrap: int = 10000, seed: int = 42): ...
    def analyze(self, dnsi: np.ndarray, gap: np.ndarray) -> dict:
        """Returns: n, r_pearson, p_pearson, r_spearman, p_spearman,
        ci_95_lower, ci_95_upper, bootstrap_r (np.ndarray), hypothesis_supported: bool"""
    def _bootstrap_correlation(self, x: np.ndarray, y: np.ndarray) -> np.ndarray: ...
```

### evaluate.py (`h-m1/code/evaluate.py`)

**Dependencies**: config.py, metrics.py

```python
def check_gate(analysis: dict) -> bool:
    """MUST_WORK: fails if r_pearson > -0.2 or r_pearson > 0."""
def summarize(analysis: dict, benchmark_names: list[str], dnsi: np.ndarray, gap: np.ndarray) -> dict: ...
```

### train.py (`h-m1/code/train.py`)

**Dependencies**: data.py, metrics.py, evaluate.py

```python
def generate_figures(analysis: dict, names: list, dnsi: np.ndarray, gap: np.ndarray, out_dir: str) -> None:
    """1) scatter+regression+CI shading (mandatory)
       2) bootstrap histogram
       3) benchmark grouped bar (dnsi vs gap)
       4) residual plot"""
def run_pipeline() -> dict: ...

if __name__ == "__main__":
    results = run_pipeline()
```

---

## Codebase Analysis Summary (Serena section already above per template requirement)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Config setup | GAP_DATA + CONFIG constants | 4 | 1+1+1+1 |
| M-2 | h-e1 integration | sys.path bridge, call run_pipeline(), extract dnsi dict, map benchmark keys | 10 | 2+4+2+2 |
| M-3 | Dataset builder | build_dataset merging DNSI+gap, filter valid/None, validate n | 6 | 2+2+1+1 |
| M-4 | CorrelationAnalyzer | Pearson, Spearman, bootstrap CI (seeded) | 9 | 3+1+4+1 |
| M-5 | Gate + summary | check_gate MUST_WORK logic, summarize stats | 5 | 1+2+1+1 |
| M-6 | Scatter+regression figure | mandatory viz with CI shading and R annotation | 7 | 3+1+2+1 |
| M-7 | Additional figures | bootstrap histogram, grouped bar, residual plot | 8 | 4+1+2+1 |
| M-8 | Pipeline orchestration | train.py run_pipeline wiring all steps + logging per brief's print format | 6 | 2+3+1+0 |
| M-9 | Results persistence | save analysis json to results/, verify against success/failure criteria | 4 | 1+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-2, M-4], Low(4-8): [M-1, M-3, M-5, M-6, M-7, M-8, M-9]
