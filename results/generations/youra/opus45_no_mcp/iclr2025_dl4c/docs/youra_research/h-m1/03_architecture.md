# Architecture: h-m1 (Gradient Concentration Analysis) — MECHANISM

**Applied:** RLTF fine-grained reward + PyTorch autograd for gradient tracking.

## Codebase Analysis (Serena)

**Project Type:** incremental (extends H-E1)
**Base Hypothesis:** H-E1 (VALIDATED)
**Status:** Reuses H-E1 infrastructure, adds gradient analysis module
**Reused Files:** h-e1/code/reward.py, data.py, model.py, config.py

---

## File Structure (Extends H-E1)

```
h-m1/code/
  gradient_analysis.py   # NEW: Core gradient concentration analysis
  sample_collector.py    # NEW: Generate failing samples with tracebacks  
  visualization.py       # NEW: 4 required figures
  run_analysis.py        # NEW: Main entry point
h-m1/figures/
h-m1/results/

# Reused from H-E1 (symlink or import):
h-e1/code/
  reward.py              # classify_error, parse_traceback_line, compute_gated_reward
  data.py                # load_apps, tokenize_batch
  model.py               # PolicyModel (CodeT5-large wrapper)
  config.py              # Hyperparameters
```

---

## Module Interfaces

### gradient_analysis.py (NEW)

**Dependencies**: h-e1/code/reward.py, h-e1/code/model.py

```python
def tokenize_with_lines(code: str, tokenizer) -> tuple[list[str], list[int]]: ...
    # Returns (tokens, line_numbers) mapping each token to its source line

def analyze_gradient_concentration(
    model: "PolicyModel",
    code_tokens: list[str],
    token_lines: list[int],
    traceback: str,
    reward_fn: Callable,
) -> dict[str, float]: ...
    # Returns {error_line, error_line_gradient, other_line_gradient, 
    #          concentration_ratio, within_2_lines_pct, success}

def run_gradient_analysis(
    model: "PolicyModel",
    samples: list[tuple[str, str]],  # (code, traceback) pairs
    reward_fn: Callable,
) -> dict[str, float]: ...
    # Aggregates across samples, returns {n_samples, mean_concentration_ratio,
    #                                     mean_within_2_lines_pct, success_rate,
    #                                     primary_criterion_met, secondary_criterion_met}
```

### sample_collector.py (NEW)

**Dependencies**: h-e1/code/data.py, h-e1/code/model.py, h-e1/code/reward.py

```python
def generate_failing_samples(
    model: "PolicyModel",
    dataset: list[dict],
    n_samples: int = 500,
    error_type_filter: str | None = None,  # 'U_line', 'U_ignore', or None for mixed
) -> list[tuple[str, str, str]]: ...
    # Returns [(code, traceback, error_type), ...]
```

### visualization.py (NEW)

**Dependencies**: results from gradient_analysis.py

```python
def plot_gradient_comparison(error_grad: float, other_grad: float, path: str): ...
    # Required figure: bar chart error-line vs other

def plot_concentration_histogram(ratios: list[float], path: str): ...

def plot_line_gradient_heatmap(line_gradients: dict[int, float], error_line: int, path: str): ...

def plot_error_type_comparison(u_line_ratio: float, u_ignore_ratio: float, random_ratio: float, path: str): ...
```

### run_analysis.py (NEW)

**Dependencies**: all above modules

```python
def main() -> dict: ...
    # 1. Load model and dataset
    # 2. Generate 500 failing samples
    # 3. Run gradient analysis (full, U_line, U_ignore, random)
    # 4. Generate figures
    # 5. Return verdict
```

---

## Data Flow

```
APPS dataset (h-e1/data.py)
  -> PolicyModel.generate (h-e1/model.py) -> candidate code
  -> execute_code_safely (h-e1/reward.py) -> traceback
  -> sample_collector filters for failing samples
  -> gradient_analysis.analyze_gradient_concentration:
       -> tokenize_with_lines -> (tokens, line_numbers)
       -> apply fine-grained reward (h-e1/reward.py)
       -> model.forward with gradients enabled
       -> loss.backward()
       -> aggregate grad.abs() per line
       -> compute concentration_ratio, within_2_pct
  -> run_gradient_analysis aggregates across 500 samples
  -> visualization.py generates 4 figures
  -> PASS/FAIL verdict based on criteria
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Token-line mapping | tokenize_with_lines: map CodeT5 tokens to source lines | 8 | 2+2+3+1 |
| A-2 | Gradient extraction | Per-parameter gradient extraction and aggregation | 12 | 3+3+4+2 |
| A-3 | Concentration metrics | concentration_ratio, within_2_lines_pct calculation | 8 | 2+2+3+1 |
| A-4 | Sample collection | generate_failing_samples with error type filtering | 10 | 3+2+3+2 |
| A-5 | Error type stratification | Separate analysis for U_line, U_ignore, random | 6 | 2+2+1+1 |
| A-6 | Statistical tests | One-sample t-test, confidence intervals | 5 | 2+1+1+1 |
| A-7 | Visualization | 4 required figures (bar, histogram, heatmap, comparison) | 7 | 2+2+2+1 |
| A-8 | Main runner | run_analysis.py orchestration + verdict logic | 6 | 2+1+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-4], Low(4-8): [A-1, A-3, A-5, A-6, A-7, A-8]

**Total tasks: 8 (within FULL tier max 30, 6-12 epics range)**

---

## Self-Validation

- No ASCII diagrams (text arrows only) - OK
- Interface-only module code - OK
- 8 epic tasks with complexity - OK
- Incremental: H-E1 reuse documented - OK
- MECHANISM tier complexity appropriate - OK
