# Logic: H-M1 — Calibration-Hallucination Mechanistic Link

**Type**: MECHANISM (INCREMENTAL, builds on H-E1)
**Date**: 2026-04-30

Applied: BCa-bootstrap-partial-correlation pattern
Applied: incremental-hypothesis-statistical-pipeline pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual H-E1 code (Read tool used; Serena MCP unavailable)
**Analyzed Path**: `docs/youra_research/20260430_buildingtrust/h-e1/code/analysis.py`
**Relevant Symbols**:
- `bca_bootstrap_ci(df, x, y, covar, n_boot, alpha)` — BCa CI for partial Spearman via `pg.partial_corr`
- `compute_partial_corr_matrix(df, indicators, covar)` — pairwise partial Spearman with BCa CI
- `evaluate_gates(corr_df, gate_pairs, threshold)` — pass/fail gate from corr DataFrame

**Note**: H-M1 reads H-E1 CSV outputs only. No Python imports from `h-e1/code/`. BCa logic is adapted inline.

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-e1/code/analysis.py (ACTUAL CODE)
def bca_bootstrap_ci(
    df: pd.DataFrame,
    x: str,
    y: str,
    covar: str,
    n_boot: int = N_BOOTSTRAP,  # default from config
    alpha: float = 0.05,
) -> tuple[float, float]:
    """BCa CI for partial Spearman rho via pg.partial_corr. Returns (ci_lo, ci_hi)."""
    # Key internals verified:
    # - rng = np.random.default_rng(42)  ← seed hardcoded inside
    # - Uses pg.partial_corr(data=df, x=x, y=y, covar=covar, method="spearman")
    # - Jackknife acceleration 'a' via leave-one-out residuals
    ...

def evaluate_gates(
    corr_df: pd.DataFrame,
    gate_pairs: list[tuple],
    threshold: float,
) -> dict:
    """Returns {"PASS": bool, "results": list[dict]}. Gate: |rho| >= threshold AND CI excludes zero."""
    ...
```

**Verified from**: `h-e1/code/analysis.py` (actual implementation).
**Critical**: `bca_bootstrap_ci` hardcodes `seed=42` inside via `np.random.default_rng(42)`.
H-M1 adapts this pattern but exposes `seed` as parameter for testability.

---

## A-1: Project Setup [Complexity: 5, Budget: 1]

Applied: Standard Python project layout

### API Signatures

```python
# h-m1/code/config.py
from pathlib import Path

BASE_DIR: Path = Path(__file__).parent.parent
SCORE_MATRIX_PATH: Path = BASE_DIR.parent / "h-e1" / "results" / "score_matrix.csv"
SCORE_MATRIX_T07_PATH: Path = BASE_DIR.parent / "h-e1" / "results" / "score_matrix_t07.csv"
RESULTS_DIR: Path = BASE_DIR / "results"
FIGURES_DIR: Path = BASE_DIR / "figures"

N_BOOTSTRAP: int = 10_000
BOOTSTRAP_SEED: int = 42
PRIMARY_X: str = "ECE"
PRIMARY_Y: str = "TruthfulQA_pct"
DISCRIMINANT_Y: str = "HumanEval_pass1"
COVARIATE: str = "MMLU_acc"
INTERNAL_X: str = "ECE"
INTERNAL_Y: str = "Brier"

PRIMARY_THRESHOLD: float = 0.40
INTERNAL_THRESHOLD: float = 0.30
DISCRIMINANT_THRESHOLD: float = 0.20
DECODING_INVARIANCE_THRESHOLD: float = 0.30

FIGURE_DPI: int = 150
FIGURE_FORMAT: str = "png"
MIN_MODELS: int = 25

REQUIRED_COLS: list[str] = [
    "model_id", "ECE", "Brier", "TruthfulQA_pct",
    "AdvGLUE_drop", "ANLI_drop", "MMLU_acc", "HumanEval_pass1",
]
GATE_COLS: list[str] = ["ECE", "TruthfulQA_pct", "MMLU_acc", "HumanEval_pass1", "Brier"]
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | config.py | Write all constants and path resolution |

---

## A-2: Data Loader [Complexity: 7, Budget: 1]

Applied: Standard PyTorch

### API Signatures

```python
# h-m1/code/data_loader.py
import pandas as pd
from pathlib import Path
from config import REQUIRED_COLS, GATE_COLS, MIN_MODELS

def load_score_matrix(path: Path) -> pd.DataFrame:
    """Load and validate greedy score matrix. Raises ValueError on schema/row issues."""
    ...

def load_score_matrix_t07(path: Path) -> pd.DataFrame:
    """Load T=0.7 score matrix. Returns empty DataFrame if file missing (invariance optional)."""
    ...

def validate_schema(df: pd.DataFrame, required_cols: list[str], gate_cols: list[str]) -> bool:
    """Check all required_cols present and no NaN in gate_cols. Returns True if valid."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | data_loader.py | Implement all three functions with validation logic |

---

## A-3: BCa Bootstrap Core [Complexity: 10, Budget: 2]

Applied: BCa-bootstrap-partial-correlation pattern (adapted from H-E1 `analysis.py::bca_bootstrap_ci`)

### API Signatures

```python
# h-m1/code/analyzers.py (internal helpers)
import numpy as np
import pandas as pd
import pingouin as pg
from scipy.stats import spearmanr, norm

def _bca_bootstrap_spearman(
    df: pd.DataFrame,
    x: str,
    y: str,
    n_boot: int,
    seed: int,
) -> tuple[float, float]:
    """BCa CI for unconditional spearmanr. Returns (ci_lo, ci_hi)."""
    ...

def _bca_bootstrap_partial(
    df: pd.DataFrame,
    x: str,
    y: str,
    covar: str,
    n_boot: int,
    seed: int,
) -> tuple[float, float]:
    """BCa CI for pg.partial_corr Spearman. Returns (ci_lo, ci_hi)."""
    ...
```

### Pseudo-code (BCa algorithm — shared logic)

```
Function _bca_bootstrap_core(stat_fn, df, n_boot, seed, alpha=0.05):
    rho_obs = stat_fn(df)                       # observed statistic

    rng = np.random.default_rng(seed)
    boot_rhos = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(df), size=len(df))
        df_r = df.iloc[idx].reset_index(drop=True)
        try:
            boot_rhos.append(stat_fn(df_r))
        except Exception:
            boot_rhos.append(nan)
    boot_rhos = array(boot_rhos); remove nans

    # Bias correction z0
    z0 = norm.ppf(clip(mean(boot_rhos < rho_obs), 1e-10, 1-1e-10))

    # Acceleration a via jackknife
    jack_rhos = [stat_fn(df.drop(i)) for i in range(len(df))]
    jack_mean = nanmean(jack_rhos)
    diff = jack_mean - jack_rhos
    a = nansum(diff**3) / (6 * nansum(diff**2)**1.5)  # 0.0 if denom=0

    # Adjusted percentiles
    z_lo, z_hi = norm.ppf(alpha/2), norm.ppf(1-alpha/2)
    p_lo = norm.cdf(z0 + (z0 + z_lo) / (1 - a*(z0 + z_lo)))
    p_hi = norm.cdf(z0 + (z0 + z_hi) / (1 - a*(z0 + z_hi)))

    ci_lo = percentile(boot_rhos, 100 * clip(p_lo, 0, 1))
    ci_hi = percentile(boot_rhos, 100 * clip(p_hi, 0, 1))
    return ci_lo, ci_hi

# _bca_bootstrap_spearman: stat_fn = lambda df: spearmanr(df[x], df[y]).statistic
# _bca_bootstrap_partial:  stat_fn = lambda df: pg.partial_corr(df, x, y, covar, "spearman")["r"].values[0]
```

**Key difference from H-E1**: seed is passed as parameter (not hardcoded). H-E1 hardcodes `np.random.default_rng(42)`.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | _bca_bootstrap_spearman | BCa for unconditional spearmanr |
| L-3-2 | _bca_bootstrap_partial | BCa for pg.partial_corr Spearman; adapt H-E1 pattern |

---

## A-4: Internal Consistency Analyzer [Complexity: 7, Budget: 1]

Applied: Standard PyTorch

### API Signatures

```python
def compute_internal_consistency(
    df: pd.DataFrame,
    x: str,
    y: str,
    n_boot: int,
    seed: int,
) -> dict:
    """Spearman rho(ECE, Brier) + BCa CI.
    Returns: {rho, pval, bca_ci_low, bca_ci_high, passes_threshold}
    """
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | compute_internal_consistency | spearmanr + _bca_bootstrap_spearman; threshold check |

---

## A-5: Partial Correlation Analyzer [Complexity: 11, Budget: 2]

Applied: BCa-bootstrap-partial-correlation pattern

### API Signatures

```python
def compute_partial_corr_bca(
    df: pd.DataFrame,
    x: str,
    y: str,
    covar: str,
    n_boot: int,
    seed: int,
) -> dict:
    """Primary gate: partial rho(ECE, TruthfulQA_pct | MMLU_acc) with BCa CI.
    Returns: {rho_partial, pval, bca_ci_low, bca_ci_high, ci_excludes_zero, passes_threshold}
    """
    ...

def compute_confound_magnitude(raw_rho: float, partial_rho: float) -> dict:
    """Confound decomposition.
    Returns: {raw_rho, partial_rho, survival_fraction, confound_fraction, interpretation}
    """
    ...

def evaluate_gate(partial_result: dict, threshold: float) -> bool:
    """Returns True iff abs(rho_partial) >= threshold AND ci_excludes_zero."""
    ...
```

### Pseudo-code

```
compute_partial_corr_bca(df, x, y, covar, n_boot, seed):
    res = pg.partial_corr(data=df, x=x, y=y, covar=covar, method="spearman")
    rho_partial = float(res["r"].values[0])
    pval = float(res.get("p-val", res.get("p_val", ...)).values[0])

    ci_lo, ci_hi = _bca_bootstrap_partial(df, x, y, covar, n_boot, seed)
    ci_excludes_zero = (ci_lo > 0) or (ci_hi < 0)
    passes = abs(rho_partial) >= PRIMARY_THRESHOLD and ci_excludes_zero

    return {rho_partial, pval, bca_ci_low=ci_lo, bca_ci_high=ci_hi,
            ci_excludes_zero, passes_threshold=passes}

compute_confound_magnitude(raw_rho, partial_rho):
    survival = abs(partial_rho) / abs(raw_rho) if raw_rho != 0 else nan
    confound = 1.0 - survival
    interp = "MMLU explains <50% of raw correlation" if survival >= 0.50 else "MMLU explains ≥50%"
    return {raw_rho, partial_rho, survival_fraction=survival,
            confound_fraction=confound, interpretation=interp}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | compute_partial_corr_bca | pg.partial_corr + _bca_bootstrap_partial; primary gate |
| L-5-2 | compute_confound_magnitude + evaluate_gate | survival fraction; gate boolean |

---

## A-6: Discriminant + Invariance Analyzers [Complexity: 9, Budget: 2]

Applied: BCa-bootstrap-partial-correlation pattern

### API Signatures

```python
def compute_discriminant_validity(
    df: pd.DataFrame,
    x: str,
    y: str,
    covar: str,
    n_boot: int,
    seed: int,
) -> dict:
    """partial rho(ECE, HumanEval | MMLU). passes = abs(rho) < DISCRIMINANT_THRESHOLD.
    Returns: {rho_partial, bca_ci_low, bca_ci_high, passes_threshold}
    """
    ...

def compute_decoding_invariance(
    df_greedy: pd.DataFrame,
    df_t07: pd.DataFrame,
    x: str,
    y: str,
    covar: str,
    n_boot: int,
    seed: int,
) -> dict:
    """Repeat primary partial corr on T=0.7. skipped=True if df_t07 empty.
    Returns: {rho_greedy, rho_t07, delta_rho, passes_threshold, skipped}
    """
    ...
```

### Pseudo-code (Invariance)

```
compute_decoding_invariance(df_greedy, df_t07, x, y, covar, n_boot, seed):
    if df_t07 is empty:
        return {rho_greedy=nan, rho_t07=nan, passes_threshold=False, skipped=True}

    res_g = compute_partial_corr_bca(df_greedy, x, y, covar, n_boot, seed)
    res_t = compute_partial_corr_bca(df_t07, x, y, covar, n_boot, seed+1)  # offset seed

    rho_g = res_g["rho_partial"]
    rho_t = res_t["rho_partial"]
    passes = abs(rho_t) >= DECODING_INVARIANCE_THRESHOLD
    return {rho_greedy=rho_g, rho_t07=rho_t, delta_rho=rho_t-rho_g,
            passes_threshold=passes, skipped=False}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | compute_discriminant_validity | partial rho(ECE, HumanEval\|MMLU); passes = abs < 0.20 |
| L-6-2 | compute_decoding_invariance | repeat primary test on T=0.7 df; skipped flag |

---

## A-7: Visualization Figs 1-3 [Complexity: 10, Budget: 1]

Applied: Standard matplotlib/seaborn

### API Signatures

```python
# h-m1/code/visualizer.py
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from config import FIGURES_DIR, FIGURE_DPI, FIGURE_FORMAT

def plot_gate_bar(
    partial_result: dict,
    threshold: float,
    figures_dir: Path,
) -> Path:
    """Fig 1: bar partial rho vs threshold; BCa CI error bar; PASS/FAIL annotation."""
    ...

def plot_raw_vs_partial(
    raw_rho: float,
    partial_rho: float,
    confound_result: dict,
    figures_dir: Path,
) -> Path:
    """Fig 2: side-by-side bar raw rho vs partial rho; survival_fraction text."""
    ...

def plot_ece_brier_scatter(
    df: pd.DataFrame,
    internal_result: dict,
    figures_dir: Path,
) -> Path:
    """Fig 3: scatter ECE vs Brier N=30; model family color; rho annotated."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Figs 1-3 | Implement three plot functions; save to figures_dir |

---

## A-8: Visualization Figs 4-5 [Complexity: 8, Budget: 1]

### API Signatures

```python
def plot_discriminant_validity(
    primary_result: dict,
    discriminant_result: dict,
    figures_dir: Path,
) -> Path:
    """Fig 4: grouped bar partial rho(ECE,TruthfulQA|MMLU) vs partial rho(ECE,HumanEval|MMLU)."""
    ...

def plot_decoding_invariance(
    invariance_result: dict,
    figures_dir: Path,
) -> Path:
    """Fig 5: scatter greedy vs T=0.7 partial rho. No-op if invariance_result['skipped']."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | Figs 4-5 | Implement two plot functions; handle skipped invariance |

---

## A-9: Reporter [Complexity: 8, Budget: 1]

### API Signatures

```python
# h-m1/code/reporter.py
import json
from pathlib import Path

def write_results_json(
    internal_result: dict,
    primary_result: dict,
    confound_result: dict,
    discriminant_result: dict,
    invariance_result: dict,
    gate_pass: bool,
    output_path: Path,
) -> None:
    """Write h-m1/results/hm1_results.json with all results and pass/fail flags."""
    ...

def write_validation_md(
    internal_result: dict,
    primary_result: dict,
    confound_result: dict,
    discriminant_result: dict,
    invariance_result: dict,
    gate_pass: bool,
    output_path: Path,
) -> None:
    """Write h-m1/04_validation.md; criterion table with threshold/observed/pass."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | reporter.py | JSON + MD output; criterion table format |

---

## A-10: Main Pipeline Integration [Complexity: 10, Budget: 2]

Applied: incremental-hypothesis-statistical-pipeline pattern

### API Signatures

```python
# h-m1/code/main.py
import logging
from pathlib import Path

def main() -> dict:
    """Orchestrate full H-M1 pipeline. Returns gate_eval dict with PASS bool and all results."""
    ...
```

### Pseudo-code

```
main():
    setup_logging()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load data
    df_greedy = load_score_matrix(SCORE_MATRIX_PATH)
    df_t07    = load_score_matrix_t07(SCORE_MATRIX_T07_PATH)
    validate_schema(df_greedy, REQUIRED_COLS, GATE_COLS)  # raises on failure

    # 2. Statistical analyses
    internal_result     = compute_internal_consistency(df_greedy, INTERNAL_X, INTERNAL_Y,
                                                        N_BOOTSTRAP, BOOTSTRAP_SEED)
    primary_result      = compute_partial_corr_bca(df_greedy, PRIMARY_X, PRIMARY_Y,
                                                    COVARIATE, N_BOOTSTRAP, BOOTSTRAP_SEED)
    raw_rho             = spearmanr(df_greedy[PRIMARY_X], df_greedy[PRIMARY_Y]).statistic
    confound_result     = compute_confound_magnitude(raw_rho, primary_result["rho_partial"])
    discriminant_result = compute_discriminant_validity(df_greedy, PRIMARY_X, DISCRIMINANT_Y,
                                                         COVARIATE, N_BOOTSTRAP, BOOTSTRAP_SEED)
    invariance_result   = compute_decoding_invariance(df_greedy, df_t07, PRIMARY_X, PRIMARY_Y,
                                                       COVARIATE, N_BOOTSTRAP, BOOTSTRAP_SEED)

    # 3. Gate evaluation
    gate_pass = evaluate_gate(primary_result, PRIMARY_THRESHOLD)
    log.info(f"PRIMARY GATE: {'PASS' if gate_pass else 'FAIL'} | "
             f"partial_rho={primary_result['rho_partial']:.4f} "
             f"CI=[{primary_result['bca_ci_low']:.4f}, {primary_result['bca_ci_high']:.4f}]")

    # 4. Visualization
    plot_gate_bar(primary_result, PRIMARY_THRESHOLD, FIGURES_DIR)
    plot_raw_vs_partial(raw_rho, primary_result["rho_partial"], confound_result, FIGURES_DIR)
    plot_ece_brier_scatter(df_greedy, internal_result, FIGURES_DIR)
    plot_discriminant_validity(primary_result, discriminant_result, FIGURES_DIR)
    plot_decoding_invariance(invariance_result, FIGURES_DIR)

    # 5. Report
    write_results_json(internal_result, primary_result, confound_result,
                       discriminant_result, invariance_result, gate_pass,
                       RESULTS_DIR / "hm1_results.json")
    write_validation_md(internal_result, primary_result, confound_result,
                        discriminant_result, invariance_result, gate_pass,
                        Path(__file__).parent.parent / "04_validation.md")

    return {"PASS": gate_pass, "primary_result": primary_result,
            "internal_result": internal_result, "confound_result": confound_result,
            "discriminant_result": discriminant_result, "invariance_result": invariance_result}

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result["PASS"] else 1)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-10-1 | main() skeleton | Directory setup, data load, analysis calls |
| L-10-2 | Gate logging + exit | Log primary gate; sys.exit(0/1) on PASS/FAIL |

---

## A-11: Validation + Gate Check [Complexity: 9, Budget: 2]

Applied: Standard PyTorch

### API Signatures

```python
# run as: python main.py
# Gate check is embedded in main() — no separate module needed.
# Validation file: h-m1/04_validation.md (written by reporter.py)

# Test suite entry point: h-m1/code/tests/
def test_bca_determinism():
    """BCa CI with same seed returns identical results across two calls."""
    ...

def test_partial_corr_direction():
    """partial rho(ECE, TruthfulQA_pct | MMLU_acc) is negative (high ECE = low accuracy)."""
    ...

def test_gate_evaluate():
    """evaluate_gate returns True iff |rho| >= threshold AND CI excludes zero."""
    ...

def test_discriminant_below_threshold():
    """partial rho(ECE, HumanEval | MMLU_acc) < DISCRIMINANT_THRESHOLD."""
    ...
```

### Pseudo-code (Gate Verification)

```
Gate verification (A-11):
    result = main()

    assert result["PASS"] == True,
        f"PRIMARY GATE FAILED: partial_rho={result['primary_result']['rho_partial']:.4f}"

    assert abs(result["primary_result"]["rho_partial"]) >= PRIMARY_THRESHOLD
    assert result["primary_result"]["ci_excludes_zero"] == True

    # Log all secondary criteria
    log_secondary(result["internal_result"], INTERNAL_THRESHOLD)
    log_secondary(result["discriminant_result"], DISCRIMINANT_THRESHOLD)
    log_secondary(result["invariance_result"], DECODING_INVARIANCE_THRESHOLD)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-11-1 | pytest test suite | 4 test functions covering BCa, partial corr, gate logic |
| L-11-2 | end-to-end gate verify | Run main(); assert PASS; log secondary criteria |

---

## Summary: Subtask Budget

| Module | Allocated | Used |
|--------|-----------|------|
| A-1 | 1 | 1 |
| A-2 | 1 | 1 |
| A-3 | 2 | 2 |
| A-4 | 1 | 1 |
| A-5 | 2 | 2 |
| A-6 | 2 | 2 |
| A-7 | 1 | 1 |
| A-8 | 1 | 1 |
| A-9 | 1 | 1 |
| A-10 | 2 | 2 |
| A-11 | 2 | 2 |
| **Total** | **16** | **16** |

Archon MCP unavailable - synthesized from domain expertise
