# Logic Design: H-M1 Conditional Margin Inflation Analysis

**Hypothesis:** H-M1 (MECHANISM)
**Date:** 2026-03-24
**Phase:** 3 Logic Design

Applied: Standard scipy permutation test pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified via direct file reads (Serena project selection unavailable; Read tool used as fallback)
**Analyzed Path**: `docs/youra_research/20260323_buildingtrust/h-e1/code/`
**Relevant Symbols**:
- `compute_conditional_margins(margins, correctness) -> dict[str, float]` — returns `{mean_correct, mean_incorrect}`
- `compute_auroc_with_ci(margins, correctness, n_bootstrap, seed) -> dict[str, float]`
- `CACHE_DIR = HYPOTHESIS_DIR / "cache"` — resolved relative to `h-e1/code/config.py`
- Cache layout: `h-e1/cache/{family}/{family}_{variant}_margins.npy` (inferred from architecture doc)

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual H-E1 Code)

```python
# From: h-e1/code/metrics.py (ACTUAL CODE)
def compute_conditional_margins(
    margins: np.ndarray,      # (N,) float
    correctness: np.ndarray,  # (N,) int {0,1}
) -> dict[str, float]:
    """Returns {mean_correct, mean_incorrect}."""
    ...

def compute_auroc_with_ci(
    margins: np.ndarray,
    correctness: np.ndarray,
    n_bootstrap: int = BOOTSTRAP_N,  # 1000
    seed: int = SEED,                # 42
) -> dict[str, float]:
    """Returns {auroc, ci_lower, ci_upper}."""
    ...

# From: h-e1/code/config.py (ACTUAL CODE)
CACHE_DIR: Path = HYPOTHESIS_DIR / "cache"   # h-e1/cache/
# Array naming convention (from architecture doc, confirmed consistent):
# h-e1/cache/{family}/{family}_base_margins.npy
# h-e1/cache/{family}/{family}_base_correctness.npy
# h-e1/cache/{family}/{family}_instruct_margins.npy
# h-e1/cache/{family}/{family}_instruct_correctness.npy
```

**Verified from**: `h-e1/code/metrics.py`, `h-e1/code/config.py` (actual implementation)

**Note**: H-M1 reimplements conditional stats locally (isolation); does NOT import H-E1 metrics directly.

---

## A-1: Project Setup [Complexity: 5, Budget: 1/4]

**Applied**: Standard PyTorch-free Python module setup

### API Signatures

```python
# config.py
SEED: int = 42
PERMUTATION_N: int = 9999
BOOTSTRAP_N: int = 1000
FAMILIES: list[str] = ["qwen", "mistral"]

H_E1_CODE_DIR: Path  # = Path(__file__).parent.parent.parent / "h-e1" / "code"
H_E1_CACHE_DIR: Path  # = H_E1_CODE_DIR.parent / "cache"
H_E1_RESULTS_JSON: Path  # = H_E1_CODE_DIR.parent / "experiment_results.json"

CODE_DIR: Path  # = Path(__file__).parent
HYPOTHESIS_DIR: Path  # = CODE_DIR.parent
FIGURES_DIR: Path  # = HYPOTHESIS_DIR / "figures"

def ensure_directories() -> None: ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | config.py | Constants, path resolution, ensure_directories |

---

## A-2: Data Loader [Complexity: 8, Budget: 1/4]

**Applied**: Standard NumPy file loading pattern

### API Signatures

```python
# data_loader.py
def load_family_arrays(
    family: str,
    cache_dir: Path,
) -> dict[str, np.ndarray]:
    """Load base/instruct margins and correctness for one family.
    Returns: {base_margins, base_correctness, inst_margins, inst_correctness} each (N,)"""
    ...

def validate_arrays(arrays: dict[str, np.ndarray]) -> None:
    """Raise ValueError if shape mismatch or invalid values."""
    ...

def load_h_e1_results_json(json_path: Path) -> dict:
    """Load H-E1 experiment_results.json."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| base_margins | (N,) float | N ~ 14k per family |
| base_correctness | (N,) int | binary {0,1} |
| inst_margins | (N,) float | same N |
| inst_correctness | (N,) int | same N |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | data_loader.py | load_family_arrays, validate_arrays, load_h_e1_results_json |

---

## A-3 + A-4 + A-5 + A-6: Analysis Pipeline [Complexity: 34, Budget: 1/4]

**Applied**: scipy.stats.permutation_test with independent permutation type

### API Signatures

```python
# analysis.py
def compute_conditional_stats(
    margins: np.ndarray,       # (N,)
    correctness: np.ndarray,   # (N,) binary
) -> dict[str, float]:
    """Returns: mean_correct, mean_incorrect, se_correct, se_incorrect, n_correct, n_incorrect."""
    ...

def run_permutation_test(
    base_margins: np.ndarray,       # (N_base,)
    base_correctness: np.ndarray,   # (N_base,)
    inst_margins: np.ndarray,       # (N_inst,)
    inst_correctness: np.ndarray,   # (N_inst,)
    n_resamples: int = PERMUTATION_N,
    seed: int = SEED,
) -> dict[str, float]:
    """One-tailed permutation test on E[margin|incorrect].
    Returns: p_value, statistic (mean_inst_incorrect - mean_base_incorrect)."""
    ...

def compute_effect_size(
    base_margins_incorrect: np.ndarray,   # (M_base,) subset where correctness==0
    inst_margins_incorrect: np.ndarray,   # (M_inst,) subset where correctness==0
) -> dict[str, float]:
    """Returns: raw_diff, inflation_ratio, cohens_d."""
    ...

def compute_bootstrap_ci(
    base_margins_incorrect: np.ndarray,
    inst_margins_incorrect: np.ndarray,
    n_bootstrap: int = BOOTSTRAP_N,
    seed: int = SEED,
) -> dict[str, float]:
    """95% bootstrap CI on mean difference.
    Returns: ci_lower, ci_upper."""
    ...

def compute_kl_divergence(
    base_margins: np.ndarray,
    inst_margins: np.ndarray,
    n_bins: int = 100,
) -> float: ...

def analyze_family(
    family: str,
    arrays: dict[str, np.ndarray],
) -> dict:
    """Full per-family pipeline: stats -> permutation -> effect size -> CI -> gate.
    Returns structured results dict matching experiment_results.yaml schema."""
    ...
```

### Pseudo-code for run_permutation_test

```
1. base_inc = base_margins[base_correctness == 0]  # (M_base,)
2. inst_inc = inst_margins[inst_correctness == 0]   # (M_inst,)
3. statistic_fn = lambda x, y: np.mean(x) - np.mean(y)
4. result = scipy.stats.permutation_test(
       (inst_inc, base_inc),
       statistic=statistic_fn,
       permutation_type='independent',
       alternative='greater',
       n_resamples=n_resamples,
       random_state=seed,
   )
5. return {p_value: result.pvalue, statistic: result.statistic}
```

### Pseudo-code for analyze_family

```
1. base_stats = compute_conditional_stats(arrays["base_margins"], arrays["base_correctness"])
2. inst_stats = compute_conditional_stats(arrays["inst_margins"], arrays["inst_correctness"])
3. perm = run_permutation_test(arrays["base_margins"], arrays["base_correctness"],
                               arrays["inst_margins"], arrays["inst_correctness"])
4. base_inc = arrays["base_margins"][arrays["base_correctness"] == 0]
5. inst_inc = arrays["inst_margins"][arrays["inst_correctness"] == 0]
6. effect = compute_effect_size(base_inc, inst_inc)
7. ci = compute_bootstrap_ci(base_inc, inst_inc)
8. gate_pass = (inst_stats["mean_incorrect"] > base_stats["mean_incorrect"]) and (perm["p_value"] < 0.05)
9. return structured results dict
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | analysis.py | All analysis functions: conditional stats, permutation test, effect size, bootstrap CI, KL, analyze_family |

---

## A-7 + A-8 + A-9 + A-10 + A-11: Visualization, Reporting, Orchestration [Complexity: 41, Budget: 1/4]

**Applied**: Standard matplotlib/seaborn figure pattern

### API Signatures

```python
# visualize.py
def plot_gate_metrics(
    family_results: dict[str, dict],
    figures_dir: Path,
) -> str:
    """Bar chart E[margin|incorrect] base vs instruct with CI error bars. Returns path."""
    ...

def plot_kde_distributions(
    family_results: dict[str, dict],
    arrays_by_family: dict[str, dict],
    figures_dir: Path,
) -> str:
    """4-panel KDE: base-correct, base-incorrect, inst-correct, inst-incorrect. Returns path."""
    ...

def plot_box_plots(arrays_by_family: dict[str, dict], figures_dir: Path) -> str: ...

def plot_inflation_ratios(family_results: dict[str, dict], figures_dir: Path) -> str:
    """Bar chart: correct_ratio vs incorrect_ratio per family. Returns path."""
    ...

def plot_forest(family_results: dict[str, dict], figures_dir: Path) -> str:
    """Effect sizes with 95% CIs + pooled estimate. Returns path."""
    ...

def save_all_figures(
    family_results: dict[str, dict],
    arrays_by_family: dict[str, dict],
    figures_dir: Path,
) -> list[str]: ...

# report.py
def evaluate_gate(family_results: dict[str, dict]) -> str:
    """Returns 'PASS' if all families gate_pass=True, else 'FAIL'."""
    ...

def save_experiment_results_yaml(
    family_results: dict[str, dict],
    gate_result: str,    # "PASS" | "FAIL"
    output_path: Path,
) -> None: ...

def generate_validation_report(
    family_results: dict[str, dict],
    gate_result: str,
    output_path: Path,
) -> None: ...

# run_experiment.py
def set_seed(seed: int = SEED) -> None: ...

def main(families: list[str] = None) -> None:
    """Orchestrates: load -> validate -> analyze -> visualize -> report."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | visualize.py + report.py + run_experiment.py | All figures, YAML/MD report, main orchestrator, argparse |

---

## Budget Summary

| Budget Slot | Tasks Covered | Subtask ID |
|-------------|--------------|------------|
| 1/4 | A-1 (config) | L-1-1 |
| 2/4 | A-2 (data loader) | L-2-1 |
| 3/4 | A-3/4/5/6 (analysis) | L-3-1 |
| 4/4 | A-7/8/9/10/11 (viz+report+orchestrate) | L-4-1 |

**Total subtasks**: 4/4 used

---

## Gate Logic

```python
# Per family: gate_pass = True iff BOTH:
gate_pass = (
    inst_stats["mean_incorrect"] > base_stats["mean_incorrect"]
    and perm["p_value"] < 0.05  # one-tailed
)
# Overall: PASS iff all families pass
gate_result = "PASS" if all(r["gate_pass"] for r in family_results.values()) else "FAIL"
```
