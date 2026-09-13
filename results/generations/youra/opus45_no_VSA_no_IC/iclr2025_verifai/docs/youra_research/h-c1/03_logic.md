# Logic: H-C1 (Cross-Model SA-Correctness Generalization)

**Type**: CONDITION

**Applied**: Standard pandas groupby + reuse-h-m1-per-model (KB search "cross-model correlation statistical API" returned no relevant matches, similarity <0.39, only diffusion-model/modelscope results — no applicable pattern, using pandas groupby + h-m1 partial_corr_loc directly)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1) — VALIDATED, fully implemented
**Status**: Serena `find_symbol` returned "No active project" (TEST_verifai not in registered project list) — verified via direct file read instead, per h-m1/architecture.md precedent.
**Analyzed Path**: `docs/youra_research/h-m1/code/metrics.py`, `completions.py`, `correlate.py`
**Relevant Symbols**:
- `metrics.build_dataframe(problems, completions, passed: dict) -> pd.DataFrame` — cols: `task_id, passed, pylint_score, mypy_errors, radon_cc, loc`. **No `model_id` column** — must add after call.
- `completions.load_completions_jsonl(path: str) -> list[Completion]` — one path per call, one model per call.
- `correlate.partial_corr_loc(df, metric) -> tuple[float, float]` — operates on whole df; call per model by filtering `df[df.model_id == m]` first.

---

## External Dependencies (Base Hypothesis)

### API Signatures (Verified from Actual Code)

```python
# From: h-m1/code/dataset.py
def load_all_problems() -> list[Problem]: ...  # Problem has .task_id, .canonical_solution

# From: h-m1/code/completions.py
@dataclass
class Completion:
    task_id: str
    completion: str

def load_completions_jsonl(path: str) -> list[Completion]: ...

# From: h-m1/code/eval_pass1.py (referenced by h-m1 run.py; signature per h-m1 usage)
def evaluate_all(problems: list, completions: list[Completion]) -> dict[str, bool]: ...  # task_id -> passed

# From: h-m1/code/metrics.py (VERIFIED — no model_id col, must add post-hoc)
def build_dataframe(problems: list, completions: list[Completion], passed: dict[str, bool]) -> pd.DataFrame:
    """Cols: task_id, passed(int), pylint_score, mypy_errors, radon_cc, loc."""
    ...

# From: h-m1/code/correlate.py
def partial_corr_loc(df: pd.DataFrame, metric: str) -> tuple[float, float]:
    """Partial r of metric vs passed, controlling loc. Returns (r_partial, p_partial)."""
    ...
```

**Verified from**: `docs/youra_research/h-m1/code/` (direct file read, flat scripts — H-C1 must copy/symlink these files into `h-c1/code/` or prepend `h-m1/code/` to `sys.path`).

---

## C-2/C-3: multi_model_data.py [Complexity: 15, Budget: 15]

**Applied**: pandas concat pattern for per-group dataframe tagging

### API Signatures

```python
# code/multi_model_data.py
import pandas as pd
from dataset import Problem, load_all_problems
from completions import load_completions_jsonl
from eval_pass1 import evaluate_all
from metrics import build_dataframe

def load_model_dataframe(model_id: str, problems: list[Problem], completions_path: str) -> pd.DataFrame:
    """Load one model's completions, eval pass@1, build SA df, tag model_id. Returns df w/ model_id col."""
    ...

def build_multi_model_dataframe(models: list[str], problems: list[Problem], completions_dir: str) -> pd.DataFrame:
    """Concat per-model dfs. Skips model if {completions_dir}/{model}.jsonl missing."""
    ...
```

### Pseudo-code

```
1. load_model_dataframe(model_id, problems, completions_path):
     completions = load_completions_jsonl(completions_path)
     passed = evaluate_all(problems, completions)
     df = build_dataframe(problems, completions, passed)
     df["model_id"] = model_id
     return df

2. build_multi_model_dataframe(models, problems, completions_dir):
     dfs = []
     for m in models:
         path = f"{completions_dir}/{m}.jsonl"
         if not exists(path): continue  # skip, log warning
         dfs.append(load_model_dataframe(m, problems, path))
     assert len(dfs) >= MIN_MODELS
     return pd.concat(dfs, ignore_index=True)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-C-2-1 | load_model_dataframe | Wire completions->eval->build_dataframe, add model_id col |
| L-C-2-2 | build_multi_model_dataframe | Loop models, skip missing files, concat, assert MIN_MODELS |
| L-C-3-1 | data schema check | Assert combined df has task_id, model_id, passed, pylint_score, radon_cc, mypy_errors, loc |

---

## C-4/C-5: cross_correlate.py [Complexity: 13, Budget: 13]

**Applied**: groupby-filter-apply pattern for per-group statistical reuse

### API Signatures

```python
# code/cross_correlate.py
import pandas as pd
from correlate import partial_corr_loc

def compute_per_model_correlations(
    df: pd.DataFrame, metric: str = "pylint_score", models: list[str] = None
) -> dict[str, tuple[float, float]]:
    """Filter df per model, run h-m1 partial_corr_loc. Returns {model_id: (r_partial, p_partial)}."""
    ...

def cross_model_variance(correlations: dict[str, tuple[float, float]]) -> tuple[float, float, float]:
    """Returns (mean_r, std_r, min_r) over r_partial values."""
    ...

def determine_gate_pass(
    mean_r: float, std_r: float, min_r: float, variance_threshold: float = 0.15,
) -> bool:
    """PASS iff std_r < variance_threshold AND mean_r > 0.35 AND min_r > 0.20."""
    ...
```

### Pseudo-code

```
1. compute_per_model_correlations(df, metric, models):
     result = {}
     for m in models:
         sub = df[df.model_id == m]
         r, p = partial_corr_loc(sub, metric)
         result[m] = (r, p)
     return result

2. cross_model_variance(correlations):
     rs = [r for r, p in correlations.values()]
     return mean(rs), std(rs), min(rs)

3. determine_gate_pass(mean_r, std_r, min_r, threshold):
     return std_r < threshold and mean_r > 0.35 and min_r > 0.20
```

### Tensor/Data Shapes

| Variable | Type | Note |
|----------|------|------|
| correlations | dict[str, tuple[float,float]] | model_id -> (r_partial, p_partial) |
| cross_model_variance return | (float, float, float) | (mean_r, std_r, min_r) |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-C-4-1 | compute_per_model_correlations | Filter df by model_id, call h-m1 partial_corr_loc per subset |
| L-C-4-2 | secondary metric pass | Same for radon_cc metric (secondary per architecture) |
| L-C-5-1 | cross_model_variance | mean/std/min of r_partial across models |
| L-C-5-2 | determine_gate_pass | Threshold check: std<0.15, mean>0.35, min>0.20 |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] Applied-pattern lines only (no KB logs)
- [x] Docstrings <=2 lines
- [x] 7 subtasks total (within budget, C-2/C-3 combined 3, C-4/C-5 combined 4)
- [x] Codebase Analysis (Serena) section included — Serena unavailable, direct read documented
- [x] External Dependencies API section with verified h-m1 signatures
- [x] Total length < 250 lines
