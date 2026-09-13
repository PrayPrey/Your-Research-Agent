# Architecture: h-m2 (MECHANISM — Temporal Prediction)

**Applied**: Statistical-regression-with-resampling pattern (OLS + bootstrap CI + LOO-CV for small-N), sourced from experiment brief research (Archon MCP unavailable — synthesized from PRD/brief spec).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: Analyzed actual h-e1 code (not spec) — h-e1/03_architecture.md diverges from implementation in several signatures.
**Analyzed Path**: `h-e1/code/` (`metrics.py`, `data.py`, `config.py`)
**Findings**:
- h-e1 uses flat scripts + module-level `CONFIG` dict (not a `config.CONFIG` class), imported as `from config import CONFIG`.
- `DNSIComputer.compute_dnsi(sota_history, difficulty_proxy)` takes pre-parsed `list[tuple[datetime, float]]`, NOT raw JSON — h-m2 must replicate this parsing (via `data.py` helpers) before filtering by cutoff.
- `match_target_benchmarks(dense)` takes only `dense` (reads `TARGET_BENCHMARKS` from config internally) — no `targets` param as PRD pseudocode assumed.
- `load_data()` is the orchestrator entrypoint in h-e1/data.py; h-m2 will call this directly to reuse the full acquisition pipeline, then re-filter by date.

---

## File Structure

```
h-m2/code/
  config.py        # cutoff date, gap ground truth, bootstrap/seed constants
  temporal_dnsi.py # TemporalDNSIComputer (wraps h-e1 DNSIComputer w/ date cutoff)
  analysis.py       # TemporalPredictionAnalyzer (OLS + bootstrap + LOO-CV)
  evaluate.py        # gate check (R² thresholds, slope sign)
  train.py            # entrypoint: load h-e1 data -> filter -> DNSI -> regress -> figures -> gate
```

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| CONFIG, TARGET_BENCHMARKS | `from config import CONFIG, TARGET_BENCHMARKS` (h-e1 path added to sys.path) | `h-e1/code/config.py` |
| load_data | `from data import load_data` | `h-e1/code/data.py` |
| extract_sota_history | `from data import extract_sota_history` | `h-e1/code/data.py` |
| DNSIComputer | `from metrics import DNSIComputer, validate_dnsi` | `h-e1/code/metrics.py` |

**Verified from**: `h-e1/code/` (actual implementation, not `03_architecture.md` spec).

**Note**: `load_data()` returns `{name: {history: list[tuple[datetime,float]], difficulty_proxy, ...}}` already parsed and dated — h-m2 filters `history` by cutoff, no need to re-parse JSON.

---

## Modules

### config.py (`code/config.py`)

**Dependencies**: none

```python
CUTOFF_DATE: str = "2019-01-01"
MIN_HISTORY_YEARS_PRE_CUTOFF: int = 5
MIN_PRE_CUTOFF_ENTRIES: int = 10
N_BOOTSTRAP: int = 10000
SEED: int = 1
R2_PASS_THRESHOLD: float = 0.3
R2_FAIL_THRESHOLD: float = 0.1
LOO_R2_THRESHOLD: float = 0.1
GAP_GROUND_TRUTH: dict[str, dict]  # {benchmark: {gap: float, source: str}}
FIGURES_DIR: str = "figures"
H_E1_CODE_DIR: str = "../../h-e1/code"
```

### temporal_dnsi.py (`code/temporal_dnsi.py`)

**Dependencies**: config, h-e1.metrics (DNSIComputer), numpy

```python
class TemporalDNSIComputer:
    def __init__(self, window_months: int = 6, cutoff_date: str = CUTOFF_DATE): ...
    def compute_dnsi_pre_cutoff(
        self, sota_history: list[tuple], difficulty_proxy: int | None
    ) -> float | None:
        """Filter history < cutoff, require MIN_PRE_CUTOFF_ENTRIES + MIN_HISTORY_YEARS,
        delegate windowed-improvement + entropy calc to h-e1 DNSIComputer."""
        ...
```

### analysis.py (`code/analysis.py`)

**Dependencies**: config, numpy, scipy.stats, sklearn.linear_model, sklearn.metrics

```python
class TemporalPredictionAnalyzer:
    def __init__(self, n_bootstrap: int = 10000, seed: int = 1): ...
    def analyze(self, dnsi_pre: np.ndarray, gap_post: np.ndarray) -> dict:
        """Returns: n, r2, adj_r2, loo_r2, ci_95_lower, ci_95_upper,
        slope, intercept, hypothesis_supported"""
        ...
    def _bootstrap_r2(self, x: np.ndarray, y: np.ndarray) -> np.ndarray: ...
    def _loo_cv(self, x: np.ndarray, y: np.ndarray) -> float: ...
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: config, analysis

```python
def check_gate(results: dict) -> str:
    """Returns 'PASS' | 'FAIL' | 'MARGINAL' based on r2 vs
    R2_PASS_THRESHOLD / R2_FAIL_THRESHOLD"""
    ...
def summarize(results: dict) -> dict:
    """Adds slope-direction check, LOO/CI informational flags"""
    ...
```

### train.py (`code/train.py`)

**Dependencies**: config, temporal_dnsi, analysis, evaluate, matplotlib, sys.path injection for h-e1 code

```python
def run_pipeline() -> dict:
    """sys.path.append(H_E1_CODE_DIR); load_data() from h-e1 ->
       filter history per benchmark < cutoff -> TemporalDNSIComputer.compute_dnsi_pre_cutoff
       -> assemble (dnsi_pre[], gap_post[]) aligned arrays via GAP_GROUND_TRUTH keys
       -> TemporalPredictionAnalyzer.analyze -> check_gate -> generate_figures -> print signals"""
    ...
def generate_figures(dnsi: np.ndarray, gap: np.ndarray, results: dict, out_dir: str) -> None:
    """Scatter w/ regression line + R² annotation (required);
       bootstrap R² histogram; LOO pred-vs-actual scatter"""
    ...

if __name__ == "__main__":
    run_pipeline()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Config + gap ground truth | Cutoff date, thresholds, hardcoded GAP_GROUND_TRUTH dict for 4 benchmarks | 4 | 1+1+1+1 |
| B-2 | h-e1 data reuse bridge | sys.path injection, call `load_data()`, verify history format matches expectation | 6 | 2+3+1+0 |
| B-3 | TemporalDNSIComputer | Cutoff filtering + min-history checks, delegate to h-e1 DNSIComputer | 8 | 2+2+3+1 |
| B-4 | Benchmark-gap alignment | Match matched benchmarks (incl. ObjectNet->ImageNet history reuse) to GAP_GROUND_TRUTH keys, build aligned arrays | 7 | 2+2+2+1 |
| B-5 | TemporalPredictionAnalyzer | OLS regression, adjusted R², bootstrap R² (10k iter), LOO-CV | 12 | 3+2+4+3 |
| B-6 | Gate evaluation | R² pass/fail/marginal gate, slope-sign check, CI/LOO informational flags | 5 | 1+2+1+1 |
| B-7 | Visualization | Scatter+regression (required), bootstrap histogram, LOO pred-vs-actual | 6 | 2+1+1+2 |
| B-8 | Pipeline integration (train.py) | Wire bridge -> DNSI -> alignment -> analysis -> gate -> figures, activation/success/failure logging | 7 | 1+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [B-5], Low(4-8): [B-1, B-2, B-3, B-4, B-6, B-7, B-8]
