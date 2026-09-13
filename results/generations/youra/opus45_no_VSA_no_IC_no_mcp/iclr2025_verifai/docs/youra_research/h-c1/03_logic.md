# Logic: h-c1 Format × Model Scale Interaction

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1, VALIDATED)
**Status**: API signatures verified from actual h-e1 code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**: `repair_problem` (repair_loop.py), `parse_compiler_output`/`StructuredError` (errors.py), `generate_code`/`load_hf_model` (models.py)

New h-c1 modules (`orchestrate.py`, `stats_analysis.py`, `effect_sizes.py`, `contrasts.py`) are green-field — designed below.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/repair_loop.py (ACTUAL CODE)
def repair_problem(
    model_ref,
    tokenizer,
    problem: Dict,
    use_structured: bool,
    max_attempts: int = None,      # defaults to CONFIG["max_repair_attempts"]
    is_openai: bool = False
) -> Dict:
    """Returns: {"passed": bool, "attempts_used": int, "error_types_seen": List[str]}"""
    ...

# From: h-e1/code/models.py (ACTUAL CODE)
def load_hf_model(model_id: str) -> Tuple[Any, Any]:
    """Returns (model, tokenizer), cached in _model_cache."""
    ...

def generate_code(
    model_ref, tokenizer, prompt: str, is_openai: bool = False,
    max_new_tokens: int = None, temperature: float = None
) -> str: ...

# From: h-e1/code/errors.py (ACTUAL CODE)
@dataclass
class StructuredError:
    line_number: int
    error_type: str
    error_message: str
    code_context: List[str]

def parse_compiler_output(raw_output: str, source_code: str) -> StructuredError: ...
```

**Verified from**: `h-e1/code/` actual implementation. `repair_problem` already dispatches format via `use_structured: bool` and handles both HF (`is_openai=False`) and OpenAI (`is_openai=True`) — no changes needed to reuse for GPT-4 cell.

---

## A-1: Multi-Model Experiment Orchestration [Complexity: 4, Budget: 4]

**Applied**: Standard PyTorch / sequential batch orchestration (no new KB pattern needed — reuses h-e1 repair loop)

### API Signatures

```python
# orchestrate.py
from dataclasses import dataclass, asdict
from typing import Dict, List

MODEL_REGISTRY = {
    "7B":   {"model_id": "codellama/CodeLlama-7b-hf",  "is_openai": False},
    "34B":  {"model_id": "codellama/CodeLlama-34b-hf", "is_openai": False},
    "gpt4": {"model_id": "gpt-4",                       "is_openai": True},
}

@dataclass
class CellResult:
    model: str            # "7B" | "34B" | "gpt4"
    format: str            # "raw" | "structured"
    problem_id: str
    passed: bool
    attempts_used: int

def run_cell(model_key: str, use_structured: bool, problems: List[Dict]) -> List[CellResult]:
    """Runs repair_problem for every problem under one (model, format) cell."""
    ...

def run_all_cells(problems: List[Dict]) -> List[CellResult]:
    """2x3 factorial sweep: for model in MODEL_REGISTRY, for format in [raw, structured]."""
    ...

def save_results(results: List[CellResult], path: str) -> None: ...
def load_results(path: str) -> List[CellResult]: ...
```

### Pseudo-code

```
1. load EvalPlus problems (HumanEval+ + MBPP+, pooled) -> problems
2. for model_key, spec in MODEL_REGISTRY:
     model_ref, tok = load_hf_model(spec.model_id) if not is_openai else (None, None)
     filter problems to those model FAILS on initial generation (per US-1)
     for use_structured in [False, True]:
         for problem in failing_problems:
             res = repair_problem(model_ref, tok, problem, use_structured,
                                   max_attempts=3, is_openai=spec.is_openai)
             append CellResult(model_key, "structured" if use_structured else "raw",
                                problem["task_id"], res["passed"], res["attempts_used"])
3. save_results(all_results, "results/h-c1_raw_results.json")
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | MODEL_REGISTRY + run_cell | Single (model, format) cell runner |
| L-1-2 | run_all_cells | 2x3 sweep driver, reuses `repair_problem` |
| L-1-3 | Failure filtering | Pre-filter to problems each model fails initially (per-model, not shared) |
| L-1-4 | Result persistence | save/load JSON for caching (risk mitigation: API cost) |

---

## A-2: Two-Way ANOVA with Interaction [Complexity: 4, Budget: 4]

**Applied**: statsmodels OLS + `anova_lm` Type III SS (Applied: statsmodels ANOVA pattern)

### API Signatures

```python
# stats_analysis.py
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

def results_to_dataframe(results: List[CellResult]) -> pd.DataFrame:
    """CellResult list -> DataFrame[model, format, passed(0/1)] one row per problem attempt."""
    ...

def two_way_anova(df: pd.DataFrame) -> pd.DataFrame:
    """
    passed ~ C(format) * C(model), Type III SS.
    Requires sum-coded contrasts (sm default is dummy; set sum coding explicitly).
    Returns anova table: rows [C(format), C(model), C(format):C(model), Residual]
                          cols [sum_sq, df, F, PR(>F)]
    """
    ...

def bh_fdr_correct(pvals: List[float]) -> List[float]:
    """Benjamini-Hochberg FDR correction (statsmodels.stats.multitest.multipletests)."""
    ...
```

### Pseudo-code

```
1. df = results_to_dataframe(results)   # columns: model, format, passed
2. set sum-to-zero contrasts (required for Type III SS validity):
     df["format"] = C(df["format"], Sum)
     df["model"]  = C(df["model"], Sum)
3. model = smf.ols("passed ~ C(format, Sum) * C(model, Sum)", data=df).fit()
4. anova_table = anova_lm(model, typ=3)
5. extract F_interaction, p_interaction from row "C(format, Sum):C(model, Sum)"
6. pvals = [p_format, p_model, p_interaction]
7. pvals_adj = bh_fdr_correct(pvals)
8. return anova_table, pvals_adj
```

### Tensor Shapes / Data Shapes

| Variable | Shape | Note |
|----------|-------|------|
| df | [N, 3] | N = total repair attempts across all 6 cells |
| anova_table | [4, 4] | rows: format, model, format:model, Residual |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | results_to_dataframe | Long-format DataFrame builder |
| L-2-2 | two_way_anova | Type III SS via statsmodels sum-coded OLS |
| L-2-3 | bh_fdr_correct | BH-FDR wrapper over 3 primary p-values |
| L-2-4 | Unequal-cell handling | Verify Type III SS valid under unbalanced n (GPT-4 low-failure risk) |

---

## A-3: Simple Effects, Effect Sizes & Planned Contrasts [Complexity: 5, Budget: 5]

**Applied**: scipy.stats (proportion CI, Cohen's d), manual eta-squared, orthogonal polynomial contrast

### API Signatures

```python
# effect_sizes.py / contrasts.py
from scipy import stats
from statsmodels.stats.proportion import proportion_confint
import numpy as np

def simple_effect(df: pd.DataFrame, model_key: str) -> Dict:
    """
    Structured-pass-rate minus Raw-pass-rate for one model.
    Returns: {effect: float, ci_low: float, ci_high: float, d: float}
    """
    ...

def cohens_d_proportions(p1: float, n1: int, p2: float, n2: int) -> float:
    """
    Cohen's d for two proportions via arcsine-transformed effect size,
    or pooled-SD formula: d = (p1 - p2) / sqrt((p1*(1-p1) + p2*(1-p2)) / 2)
    """
    ...

def wilson_ci_diff(p1: float, n1: int, p2: float, n2: int, alpha: float = 0.05) -> Tuple[float, float]:
    """95% CI for difference of two proportions (Newcombe's method)."""
    ...

def eta_squared(anova_table: pd.DataFrame, effect_row: str) -> float:
    """eta^2 = SS_effect / SS_total"""
    ...

def partial_eta_squared(anova_table: pd.DataFrame, effect_row: str) -> float:
    """partial eta^2 = SS_effect / (SS_effect + SS_residual)"""
    ...

def linear_trend_contrast(effects: Dict[str, float]) -> Dict:
    """
    Ordered-hypothesis test: Effect_7B > Effect_34B > Effect_GPT4.
    Contrast weights on model factor: [-1, 0, 1] (linear trend, coded so
    positive coefficient = decreasing effect size with increasing scale).
    Returns: {contrast_estimate: float, t: float, p: float, one_sided_p: float}
    """
    ...
```

### Statistical Formulas

- **η² (interaction)**: `SS_interaction / SS_total`
- **Partial η²**: `SS_interaction / (SS_interaction + SS_residual)`
- **Cohen's d (two proportions, pooled SD)**:
  `d = (p_structured - p_raw) / sqrt((p_structured*(1-p_structured) + p_raw*(1-p_raw)) / 2)`
- **Simple effect CI**: Newcombe/Wilson score interval for difference of proportions (robust for small n, cell-size imbalance per PRD risk R2)
- **Linear trend contrast weights** (3 ordered levels: 7B, 34B, GPT-4): `c = [-1, 0, 1]`
  `L = sum(c_i * Effect_i)`; test via `t = L / SE(L)`, `SE(L) = sqrt(sum(c_i^2 * Var(Effect_i)))`
  one-sided p-value (directional hypothesis: effect decreases with scale)

### Pseudo-code (Planned Contrast)

```
1. compute simple_effect() for each model -> {7B: e1, 34B: e2, gpt4: e3}, with variances
2. weights = [-1, 0, 1]  # linear trend across ordered scale
3. L = -1*e1 + 0*e2 + 1*e3
4. SE_L = sqrt(1*Var(e1) + 0*Var(e2) + 1*Var(e3))
5. t = L / SE_L; df = N - k (k = 6 cells)
6. p_one_sided = stats.t.sf(abs(t), df) if sign matches hypothesis (L < 0 expected) else 1 - p
7. pattern_confirmed = (e1 > e2 > e3)
8. return contrast result + pattern_confirmed flag
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | simple_effect | Per-model Structured-vs-Raw diff + CI + d |
| L-3-2 | cohens_d_proportions + wilson_ci_diff | Effect size + CI primitives |
| L-3-3 | eta_squared / partial_eta_squared | From ANOVA SS table |
| L-3-4 | linear_trend_contrast | Ordered-hypothesis planned contrast |
| L-3-5 | Pattern confirmation check | `e1 > e2 > e3` boolean + report assembly |

---

## Summary API (Entry Point)

```python
# analysis_main.py
def run_h_c1_analysis(results_path: str) -> Dict:
    """
    Full pipeline: load results -> ANOVA -> simple effects -> contrasts -> report dict.
    Returns dict matching PRD success criteria fields:
      {interaction_p, interaction_p_adj, interaction_eta2,
       simple_effects: {7B, 34B, gpt4}, contrast, pattern_confirmed, pass: bool}
    """
    df = results_to_dataframe(load_results(results_path))
    anova_table, pvals_adj = two_way_anova(df)
    effects = {m: simple_effect(df, m) for m in ["7B", "34B", "gpt4"]}
    contrast = linear_trend_contrast({k: v["effect"] for k, v in effects.items()})
    eta2 = eta_squared(anova_table, "C(format, Sum):C(model, Sum)")
    pass_criteria = (pvals_adj[2] < 0.05) and (eta2 > 0.01) and contrast["pattern_confirmed"]
    return {...}
```
