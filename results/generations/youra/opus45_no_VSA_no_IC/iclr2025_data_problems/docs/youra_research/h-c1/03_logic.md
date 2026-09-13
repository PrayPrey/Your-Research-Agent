# h-c1 Logic: Mode Profile Reliability (Cronbach's Alpha)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (depends on h-m1 outputs)
**Status**: API signatures verified from actual h-m1 code (`evaluate.py`)
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Relevant Symbols**: `compute_mode_sensitivity`, `verify_mechanism_active` (h-m1/code/evaluate.py) — confirms methods=`["trak","tracin","kronfluence"]`, modes=`["mem","transfer","spurious"]`, per-mode scores are 1D `np.ndarray` of shape `(n_probes,)`.

Simplified statistical analysis — no neural networks, no torch.

## A-1: Reliability Analysis [Complexity: 2, Budget: 4]

**Applied**: pingouin `cronbach_alpha` (bootstrap CI supported natively)

### API Signatures

```python
import numpy as np
import pandas as pd
import pingouin as pg

METHODS = ["trak", "tracin", "kronfluence"]
MODES = ["mem", "transfer", "spurious"]

def load_attribution_scores(path: str) -> dict[str, np.ndarray]:
    """Load h-m1 scores.npz. Returns {'method_mode': scores[n_probes]}."""
    ...

def build_mode_matrix(scores: dict[str, np.ndarray], method: str) -> pd.DataFrame:
    """Build (n_probes, 3) DataFrame, columns=MODES, for one method."""
    ...

def compute_reliability(mode_matrix: pd.DataFrame) -> dict:
    """Cronbach's alpha + 95% CI on (n_probes, 3) items-as-columns matrix.
    Returns {'alpha': float, 'ci_lower': float, 'ci_upper': float, 'n_probes': int}.
    """
    ...

def evaluate_gate(results: dict[str, dict]) -> tuple[bool, str]:
    """Check all(alpha > 0.8) across METHODS. Returns (pass, reason)."""
    ...

def run_h_c1(path: str, out_path: str) -> dict:
    """Orchestrates load -> per-method matrix -> reliability -> gate. Writes JSON to out_path."""
    ...
```

### Tensor/Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| scores["trak_mem"] | (1000,) | raw h-m1 attribution scores, one method_mode |
| mode_matrix | (1000, 3) | rows=probes, cols=[mem, transfer, spurious] |
| results["trak"] | dict | {alpha, ci_lower, ci_upper, n_probes} |

### Pseudo-code

```
load_attribution_scores(path):
    data = np.load(path)  # keys: "{method}_{mode}" -> (1000,) arrays
    return {k: data[k] for k in data.files}

build_mode_matrix(scores, method):
    cols = {mode: scores[f"{method}_{mode}"] for mode in MODES}
    return pd.DataFrame(cols)  # (n_probes, 3)

compute_reliability(mode_matrix):
    alpha, ci = pg.cronbach_alpha(data=mode_matrix, ci=0.95)
    return {alpha, ci_lower=ci[0], ci_upper=ci[1], n_probes=len(mode_matrix)}

evaluate_gate(results):
    failing = [m for m in METHODS if results[m]["alpha"] <= 0.8]
    pass_ = len(failing) == 0
    reason = "all methods alpha > 0.8" if pass_ else f"failed: {failing}"
    return pass_, reason

run_h_c1(path, out_path):
    scores = load_attribution_scores(path)
    results = {m: compute_reliability(build_mode_matrix(scores, m)) for m in METHODS}
    passed, reason = evaluate_gate(results)
    json.dump({"results": results, "pass": passed, "reason": reason}, open(out_path, "w"))
    return results
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | load_attribution_scores | Load .npz from h-m1 output dir |
| L-1-2 | build_mode_matrix | Per-method (n_probes, 3) DataFrame |
| L-1-3 | compute_reliability | pg.cronbach_alpha with bootstrap CI |
| L-1-4 | evaluate_gate + run_h_c1 | Threshold check + orchestration + JSON output |

## External Dependencies (Base Hypothesis — h-m1)

```python
# From: docs/youra_research/h-m1/code/evaluate.py (ACTUAL CODE)
def compute_mode_sensitivity(scores: dict) -> dict:
    """Mean influence score per mode. scores: dict[mode -> np.ndarray]"""
    ...
```

h-c1 does not call h-m1 functions directly; it consumes h-m1's saved raw attribution score arrays (keyed `"{method}_{mode}"`, shape `(1000,)`), matching the `MODES`/`METHODS` naming used in `evaluate.py`.

**Verified from**: `docs/youra_research/h-m1/code/evaluate.py`
