# Logic: h-e1 (EXISTENCE)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze, designing new APIs
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-2: Evaluation Pipeline [Complexity: 10, Budget: 4 subtasks]

**Applied**: lm-eval-harness subprocess wrapper + JSON result caching

### API Signatures

```python
# config.py
MODELS: list[dict]  # [{"id": str, "family": str, "params": int}, ...]
TASKS: list[str] = ["truthful_qa_mc1", "adversarial_glue"]

# evaluate.py
def run_lm_eval(model_id: str, tasks: list[str], output_path: str) -> None:
    """Runs lm-eval-harness CLI via subprocess, writes JSON to output_path."""
    ...

def result_exists(output_path: str) -> bool:
    """Cache check: True if output_path exists and is valid JSON."""
    ...

def evaluate_all(models: list[dict], tasks: list[str] = TASKS,
                  results_dir: str = RESULTS_DIR) -> None:
    """Iterates models, calls run_lm_eval, skips cached results."""
    ...
```

### Data Flow

`config.MODELS` -> `evaluate_all` -> per-model `run_lm_eval` (subprocess call to `lm_eval` CLI) -> JSON written to `results/{model_id_sanitized}.json` -> cached, skipped on rerun.

### Pseudo-code

```
for model in models:
    out_path = results_dir / sanitize(model["id"]) + ".json"
    if result_exists(out_path):
        continue
    cmd = ["lm_eval", "--model", "hf", "--model_args", f"pretrained={model['id']}",
           "--tasks", ",".join(tasks), "--output_path", out_path]
    subprocess.run(cmd, check=True)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A2-1 | run_lm_eval | Subprocess CLI wrapper, error handling on non-zero exit |
| L-A2-2 | result_exists | Cache check (file exists + valid JSON parse) |
| L-A2-3 | evaluate_all | Loop + skip-cached orchestration |
| L-A2-4 | Model ID sanitization | `model_id.replace("/", "__")` for filesystem-safe paths |

---

## A-5: Partial Correlation + Bootstrap CI [Complexity: 9, Budget: 4 subtasks]

**Applied**: linear residualization (control-variable regression) + percentile bootstrap

### API Signatures

```python
import numpy as np
import pandas as pd
from scipy.stats import pearsonr

def residualize(v: np.ndarray, z: np.ndarray) -> np.ndarray:
    """v: [N], z: [N] -> residuals: [N]. Fits deg=1 polyfit(z, v), returns v - fit(z)."""
    ...

def partial_corr(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> tuple[float, float]:
    """x, y, z: [N]. Returns (r, p) of pearsonr(resid_x, resid_y)."""
    ...

def bootstrap_ci(x: np.ndarray, y: np.ndarray, z: np.ndarray,
                  n_bootstrap: int = 1000, seed: int = 42) -> dict:
    """Returns {r, p, ci_lower, ci_upper, bootstrap_rs: list[float],
    n_models: int, gate_passed: bool}."""
    ...

def run_analysis(df: pd.DataFrame, x_col: str = "truthfulqa_mc1",
                  y_col: str = "advglue_avg", z_col: str = "log_params",
                  n_bootstrap: int = 1000, seed: int = 42) -> dict:
    """Wires df columns -> bootstrap_ci. Returns same dict as bootstrap_ci."""
    ...
```

### Tensor/Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x, y, z | [N] | N = number of models (15-20) |
| resid_x, resid_y | [N] | after removing linear effect of z |
| bootstrap_rs | [n_bootstrap] | resampled partial-r values |

### Pseudo-code

```
# residualize(v, z)
coef = np.polyfit(z, v, deg=1)          # [slope, intercept]
fitted = np.polyval(coef, z)            # [N]
return v - fitted                        # [N]

# partial_corr(x, y, z)
rx = residualize(x, z)
ry = residualize(y, z)
r, p = pearsonr(rx, ry)
return r, p

# bootstrap_ci(x, y, z, n_bootstrap, seed)
rng = np.random.default_rng(seed)
r_obs, p_obs = partial_corr(x, y, z)
bootstrap_rs = []
for i in range(n_bootstrap):
    idx = rng.choice(len(x), size=len(x), replace=True)   # sklearn.utils.resample equiv, fixed seed
    xb, yb, zb = x[idx], y[idx], z[idx]
    if len(np.unique(zb)) < 2:      # guard: polyfit needs variance in z
        continue
    rb, _ = partial_corr(xb, yb, zb)
    bootstrap_rs.append(rb)
ci_lower, ci_upper = np.percentile(bootstrap_rs, [2.5, 97.5])
gate_passed = (r_obs > 0.3) and (p_obs < 0.05) and (ci_lower > 0)
return {"r": r_obs, "p": p_obs, "ci_lower": ci_lower, "ci_upper": ci_upper,
        "bootstrap_rs": bootstrap_rs, "n_models": len(x), "gate_passed": gate_passed}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A5-1 | residualize | polyfit deg=1 + residual computation |
| L-A5-2 | partial_corr | Residualize both vars, pearsonr on residuals |
| L-A5-3 | bootstrap_ci | 1000-resample loop with `np.random.default_rng(seed)`, percentile CI |
| L-A5-4 | run_analysis + gate check | DataFrame column extraction, wires to bootstrap_ci, computes `gate_passed` per PRD 3-criteria |

---

## Notes

- Bootstrap uses `np.random.default_rng(seed)` (NumPy Generator API) rather than `sklearn.utils.resample` for direct seed control — functionally equivalent, simpler dependency footprint. Skipped: sklearn import for this alone.
- `residualize` guards against degenerate resamples (all-identical `z` after bootstrap) by skipping that iteration — ceiling: if guard triggers frequently (>5% of iterations), increase `n_bootstrap` or inspect `z` variance.
