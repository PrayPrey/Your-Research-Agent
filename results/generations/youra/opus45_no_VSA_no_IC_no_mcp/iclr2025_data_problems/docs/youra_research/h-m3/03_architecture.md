# Architecture: H-M3 — Optimal Balance Point via Dose-Response Analysis

**Applied**: Polynomial dose-response fitting + AIC/BIC model selection + derivative peak-finding + bootstrap CI (scipy/statsmodels pattern)

Analysis-only hypothesis. No training infrastructure — reuses H-E1/H-M2 sweep outputs (or fresh lm-eval runs) as input.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2, INCONCLUSIVE — reused for sweep data format)
**Status**: Patterns found from base code — read directly (Serena MCP unavailable in this session)
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Findings**: H-M2's `analyze.py::aggregate_results` expects `results[level][seed]["scores"][task]`, but actual files at `h-m2/code/results/{level}/{seed}_eval.json` store flat `{task: score}` dicts with no `scores` wrapper and no `final_loss` key. **H-M3's SweepLoader must read the flat format directly, not reuse `analyze.py` as-is.**

---

## Data Flow

```
sweep_results (JSON, per-threshold per-seed benchmark scores)
  → SweepLoader.load()            → SweepData (thresholds, scores_matrix)
  → PolynomialAnalyzer.fit()      → dict[model_name -> OLS fit + AIC/BIC]
  → PolynomialAnalyzer.find_peak()→ (optimal_threshold, optimal_score, is_internal)
  → PolynomialAnalyzer.bootstrap_ci() → (lower, upper)
  → DoseResponseResult (assembled)
  → verify_optimal_balance_point() → pass/fail
  → figures.py                    → dose_response_curve.png + 3 optional figures
```

---

## File Layout

```
h-m3/src/
  dose_response.py      # DoseResponseResult, PolynomialAnalyzer
  sweep_loader.py        # SweepLoader
  lm_eval_runner.py       # optional: fresh benchmark runs if sweep data missing
  figures.py              # visualization
  run_analysis.py         # main entrypoint
  tests/
    test_dose_response.py
```

No `model.py` / `train.py` / `config.py` — this hypothesis performs no training.

---

## Modules

### SweepLoader (`sweep_loader.py`)

**Dependencies**: none (stdlib json, pathlib)

```python
class SweepLoader:
    def __init__(self, results_root: str, thresholds: list[int] = None): ...
    def load(self) -> dict[int, dict[str, list[float]]]:
        """Returns {threshold: {task: [score_seed0, score_seed1, ...]}}.
        Reads flat {results_root}/{threshold}/seed{N}_eval.json files
        (matches actual H-M2 output format, not analyze.py's nested spec)."""
    def to_ensemble_matrix(self, sweep: dict) -> tuple:
        """Returns (thresholds: np.ndarray, scores_matrix: np.ndarray[n_thresholds, n_seeds])
        via per-seed mean across tasks."""
```

### PolynomialAnalyzer (`dose_response.py`)

**Dependencies**: numpy, statsmodels, scipy

```python
@dataclass
class DoseResponseResult:
    optimal_threshold: float
    optimal_score: float
    confidence_interval: tuple[float, float]
    best_model: str  # 'linear' | 'quadratic' | 'cubic'
    aic_values: dict[str, float]
    is_peak_internal: bool

class PolynomialAnalyzer:
    def fit_models(self, thresholds: np.ndarray, scores: np.ndarray) -> dict: ...
    def select_best(self, models: dict, criterion: str = "bic") -> str: ...
    def find_peak(self, thresholds: np.ndarray, scores: np.ndarray,
                  coeffs: np.ndarray, degree: int) -> tuple[float, float, bool]: ...
    def bootstrap_ci(self, thresholds: np.ndarray, scores_matrix: np.ndarray,
                     n_bootstrap: int = 1000) -> tuple[float, float]: ...
    def analyze(self, sweep_results: dict) -> DoseResponseResult:
        """Full pipeline: fit_models -> select_best -> find_peak -> bootstrap_ci."""

def verify_optimal_balance_point(result: DoseResponseResult) -> bool: ...
```

### LmEvalRunner (`lm_eval_runner.py`) — optional fallback

**Dependencies**: lm_eval (only if sweep data missing per PRD Risk Mitigation)

```python
class LmEvalRunner:
    def __init__(self, tasks: list[str] = ["hellaswag","arc_easy","piqa","winogrande"]): ...
    def evaluate(self, checkpoint_path: str) -> dict[str, float]:
        """Calls lm_eval.simple_evaluate(model='hf', model_args=f'pretrained={checkpoint_path}',
        tasks=self.tasks, batch_size=16); returns {task: acc}."""
```

### Figures (`figures.py`)

**Dependencies**: matplotlib, PolynomialAnalyzer outputs

```python
def plot_dose_response_curve(thresholds, scores, fitted_curve, result: DoseResponseResult, out_path: str): ...
def plot_model_comparison(aic_values: dict, out_path: str): ...
def plot_per_benchmark_curves(sweep_results: dict, out_path: str): ...
def plot_bootstrap_distribution(bootstrap_samples: list[float], out_path: str): ...
def plot_residuals(thresholds, scores, model, out_path: str): ...
```

### run_analysis.py (entrypoint)

```python
def main(results_root: str = "../h-e1/results", output_dir: str = "./figures"): ...
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| DEDUP_LEVELS (threshold ordering reference) | not reused — H-M3 uses its own perplexity threshold list `[0,10,...,90]` | `h-m2/code/config.py` |

**Verified from**: `docs/youra_research/h-m2/code/results/*/seed*_eval.json` (actual flat-dict format). H-M2's `analyze.py` is NOT reused directly due to format mismatch noted above; H-M3's `SweepLoader` reimplements loading against the real file layout.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | SweepLoader | Load flat JSON sweep results into threshold/seed matrix | 6 | 2+1+2+1 |
| A-2 | PolynomialAnalyzer.fit_models | OLS linear/quadratic/cubic fits with AIC/BIC via statsmodels | 8 | 2+2+3+1 |
| A-3 | PolynomialAnalyzer.find_peak | Derivative-based critical point search + boundary fallback | 9 | 2+2+4+1 |
| A-4 | PolynomialAnalyzer.bootstrap_ci | Seed-resampling bootstrap for threshold CI | 6 | 2+1+2+1 |
| A-5 | DoseResponseResult assembly + verify_optimal_balance_point | Wire pipeline, implement pass/fail gate checks | 5 | 1+1+2+1 |
| A-6 | Primary figure: dose-response curve | Fitted curve + optimal point + CI band | 5 | 1+1+2+1 |
| A-7 | Secondary figures | AIC/BIC comparison, per-benchmark curves, bootstrap histogram, residuals | 6 | 2+1+2+1 |
| A-8 | LmEvalRunner fallback | lm_eval.simple_evaluate wrapper for missing sweep points | 5 | 1+2+1+1 |
| A-9 | run_analysis.py + tests | End-to-end script, unit tests on synthetic dose-response data | 6 | 2+1+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3], Low(4-8): [A-1, A-2, A-4, A-5, A-6, A-7, A-8, A-9]
