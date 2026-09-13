# Logic: H-M2 Percentile-Normalized Monotonicity Attenuation

**Version:** 1.0
**Date:** 2026-03-24
**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-m1 code (Serena project activation not available; files read directly)
**Analyzed Path**: `docs/youra_research/20260323_buildingtrust/h-m1/code/`
**Relevant Symbols**:
- `load_family_arrays(family, cache_dir=None) -> dict[str, np.ndarray]` — h-m1/code/data_loader.py:13
- `validate_arrays(arrays: dict[str, np.ndarray]) -> None` — h-m1/code/data_loader.py:82
- `H_E1_CACHE_DIR = H_E1_CODE_DIR.parent / "cache"` (via `HYPOTHESIS_DIR.parent / "h-e1" / "code" / .. / "cache"`) — h-m1/code/config.py:27
- Cache file pattern: glob `*.npy` in `{cache_dir}/{family}/`; stem contains `instruct`/`chat` for instruct, `margin`/`correct` for type

---

## External Dependencies API

### API Signatures (From Actual H-M1 Code)

```python
# From: h-m1/code/data_loader.py (ACTUAL CODE)
def load_family_arrays(
    family: str,
    cache_dir: Path = None,        # ← defaults to H_E1_CACHE_DIR from config
) -> dict[str, np.ndarray]:
    """Load base/instruct arrays for one family.
    Returns: {base_margins, base_correctness, inst_margins, inst_correctness}
    Keys verified from actual implementation."""
    ...

def validate_arrays(
    arrays: dict[str, np.ndarray],  # ← no expected_n param in actual code!
) -> None:
    """Validate shapes, binary correctness, finite margins. Raises ValueError."""
    ...

# From: h-m1/code/config.py (ACTUAL CODE)
H_E1_CACHE_DIR: Path = H_E1_CODE_DIR.parent / "cache"
# H_E1_CODE_DIR = HYPOTHESIS_DIR.parent / "h-e1" / "code"
# So H_E1_CACHE_DIR = HYPOTHESIS_DIR.parent / "h-e1" / "cache"  (same effective path)
```

**CRITICAL NOTE**: `validate_arrays` in actual h-m1 code has NO `expected_n` parameter.
Architecture doc specifies `expected_n=14042` — h-m2 will add this parameter in its own implementation.

**Verified from**: `h-m1/code/data_loader.py` and `h-m1/code/config.py` (actual implementation)

---

## A-1: Project Setup [Complexity: 5, Budget: 1]

Applied: Standard PyTorch (flat module layout mirroring h-m1)

### API Signatures

```python
# config.py
SEED: int = 42
BOOTSTRAP_N: int = 1000
FAMILIES: list[str] = ["qwen", "mistral"]
GATE_TYPE: str = "MUST_WORK"
P_VALUE_THRESHOLD: float = 0.05
LR_C: float = 1e6
LR_MAX_ITER: int = 1000

CODE_DIR: Path = Path(__file__).parent
HYPOTHESIS_DIR: Path = CODE_DIR.parent
H_E1_CACHE_DIR: Path = HYPOTHESIS_DIR.parent / "h-e1" / "cache"
FIGURES_DIR: Path = HYPOTHESIS_DIR / "figures"
RESULTS_YAML: Path = HYPOTHESIS_DIR / "experiment_results.yaml"
VALIDATION_MD: Path = HYPOTHESIS_DIR / "04_validation.md"

def ensure_directories() -> None: ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | config.py | Constants, path resolution, ensure_directories |

---

## A-2: Data Loader [Complexity: 7, Budget: 1]

Applied: Standard PyTorch (mirrors h-m1 data_loader pattern exactly)

### API Signatures

```python
# data_loader.py
def load_family_arrays(
    family: str,
    cache_dir: Path = None,
) -> dict[str, np.ndarray]:
    """Load base/instruct margins and correctness for one family.
    Returns: {base_margins, base_correctness, inst_margins, inst_correctness}
    Each array shape: (N,) where N=14042"""
    ...

def validate_arrays(
    arrays: dict[str, np.ndarray],
    expected_n: int = 14042,        # h-m2 adds expected_n check
) -> None:
    """Raise ValueError if shapes mismatch, wrong N, non-binary correctness, non-finite margins."""
    ...

def load_all_families(
    families: list[str] = None,
    cache_dir: Path = None,
) -> dict[str, dict[str, np.ndarray]]:
    """Returns {family: arrays_dict} for each family in FAMILIES."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | data_loader.py | load_family_arrays (mirror h-m1), validate_arrays + expected_n check, load_all_families |

---

## A-3 + A-4 + A-5 + A-6: Analysis Module [Complexity: 8+9+11+8, Budget: 1]

Applied: bootstrap-CI-logistic-regression (scipy.stats.zscore + sklearn.LogisticRegression + sklearn.utils.resample)

### API Signatures

```python
# analysis.py
def zscore_normalize(margins: np.ndarray) -> np.ndarray:
    """scipy.stats.zscore; return zeros if std=0. margins: (N,) -> (N,)"""
    ...

def compute_beta_percentile(
    margins: np.ndarray,      # (N,) raw margins
    correctness: np.ndarray,  # (N,) binary {0,1}
) -> float:
    """Fit LogisticRegression(solver='lbfgs', C=LR_C, max_iter=LR_MAX_ITER)
    on zscore_normalize(margins). Returns coef_[0][0]."""
    ...

def bootstrap_beta(
    margins: np.ndarray,
    correctness: np.ndarray,
    n_iterations: int = BOOTSTRAP_N,
    seed: int = SEED,
) -> np.ndarray:
    """Bootstrap resampling via sklearn.utils.resample.
    Returns: (n_iterations,) array of beta values."""
    ...

def compute_bootstrap_ci(
    betas: np.ndarray,   # (n_iterations,)
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    """Returns (beta_mean, ci_lower_2.5, ci_upper_97.5) via percentile method."""
    ...

def bootstrap_difference_test(
    base_margins: np.ndarray,       # (N,)
    base_correctness: np.ndarray,   # (N,)
    inst_margins: np.ndarray,       # (N,)
    inst_correctness: np.ndarray,   # (N,)
    n_iterations: int = BOOTSTRAP_N,
    seed: int = SEED,
) -> dict[str, float]:
    """Paired bootstrap: same indices for base and instruct per iteration.
    Returns: {delta_beta_mean, delta_ci_lower, delta_ci_upper, p_value, effect_size}
    p_value = proportion of iterations where delta_beta <= 0
    effect_size = delta_beta_mean / pooled_std(bootstrap_betas)"""
    ...

def run_2x2_analysis(
    arrays_by_family: dict[str, dict[str, np.ndarray]],
) -> dict[str, dict[str, float]]:
    """Compute beta_percentile per (family x model_type).
    Returns: {family: {base: float, instruct: float}}
    Falls back to 1x2 if prompt_format unavailable."""
    ...

def analyze_family(
    family: str,
    arrays: dict[str, np.ndarray],
) -> dict:
    """Full pipeline: zscore->beta->bootstrap->CI->diff_test->gate.
    Returns: {family, base_beta, base_ci: (mean, lo, hi), inst_beta,
              inst_ci: (mean, lo, hi), delta_beta, p_value,
              effect_size, gate_pass, base_betas, inst_betas}
    gate_pass: beta_instruct < beta_base AND p_value < P_VALUE_THRESHOLD"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| margins | (N,) | Raw logit margins, N=14042 |
| correctness | (N,) | Binary {0,1} int |
| betas | (n_iterations,) | Bootstrap beta samples |
| ci tuple | (3,) floats | (mean, lower_2.5, upper_97.5) |

### Pseudo-code: bootstrap_difference_test

```
rng = np.random.RandomState(seed)
delta_betas = []
for i in range(n_iterations):
    idx = resample(np.arange(N), replace=True, random_state=rng)
    b_base = compute_beta_percentile(base_margins[idx], base_correctness[idx])
    b_inst = compute_beta_percentile(inst_margins[idx], inst_correctness[idx])
    delta_betas.append(b_base - b_inst)
delta_betas = np.array(delta_betas)
delta_mean = np.mean(delta_betas)
delta_ci_lo = np.percentile(delta_betas, 2.5)
delta_ci_hi = np.percentile(delta_betas, 97.5)
p_value = np.mean(delta_betas <= 0)
pooled_std = np.std(delta_betas)
effect_size = delta_mean / pooled_std if pooled_std > 0 else 0.0
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | analysis.py | All 7 functions: zscore, beta, bootstrap_beta, CI, diff_test, 2x2, analyze_family |

---

## A-7 + A-8 + A-9 + A-10 + A-11 + A-12: Visualize, Report, Orchestrator, Tests [Budget: 1]

Applied: Standard PyTorch (matplotlib publication style, flat module layout)

### API Signatures

```python
# visualize.py
def plot_gate_metrics(
    family_results: dict[str, dict],
    figures_dir: Path = None,
) -> str:
    """Bar chart: beta_percentile base vs instruct with 95% CI error bars. Returns path."""
    ...

def plot_bootstrap_distributions(
    family_results: dict[str, dict],
    figures_dir: Path = None,
) -> str:
    """Overlaid histograms of bootstrap betas (base_betas, inst_betas) per family."""
    ...

def plot_logistic_curves(
    family_results: dict[str, dict],
    arrays_by_family: dict[str, dict],
    figures_dir: Path = None,
) -> str:
    """Pr(correct) vs z-score(margin) sigmoid curves per condition."""
    ...

def plot_forest(
    family_results: dict[str, dict],
    figures_dir: Path = None,
) -> str:
    """Forest plot: delta_beta with 95% CIs per family. Returns path."""
    ...

def save_all_figures(
    family_results: dict[str, dict],
    arrays_by_family: dict[str, dict],
    figures_dir: Path = None,
) -> list[str]:
    """Run all 4 figure generators. Returns list of saved paths."""
    ...

# report.py
def evaluate_gate(family_results: dict[str, dict]) -> str:
    """Returns 'PASS' if all families gate_pass=True, else 'FAIL'."""
    ...

def save_experiment_results_yaml(
    family_results: dict[str, dict],
    gate_result: str,
    output_path: Path = None,
) -> None:
    """Write experiment_results.yaml with betas, CIs, p-values, effect sizes, gate."""
    ...

def generate_validation_report(
    family_results: dict[str, dict],
    gate_result: str,
    output_path: Path = None,
) -> None:
    """Write 04_validation.md: markdown summary table + gate pass/fail section."""
    ...

# run_experiment.py
def main(families: list[str] = None) -> None:
    """Orchestrator: ensure_dirs -> load -> validate -> analyze -> 2x2 -> figures -> report.
    exit(0) if PASS, exit(1) if FAIL."""
    ...

# tests/test_analysis.py
def test_zscore_constant_margins() -> None: ...
def test_compute_beta_percentile_synthetic() -> None: ...
def test_bootstrap_ci_bounds() -> None: ...
def test_gate_logic() -> None: ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | visualize.py, report.py, run_experiment.py, tests/ | All remaining modules |

---

## Implementation Notes for Phase 4 Coder

- `H_E1_CACHE_DIR` in h-m2: `HYPOTHESIS_DIR.parent / "h-e1" / "cache"` (verified from h-m1/code/config.py line 27)
- Cache file detection: glob `*.npy` in `{cache_dir}/{family}/`; stem `instruct`/`chat` = instruct; `margin`/`correct` = type
- `validate_arrays` in h-m1 has NO `expected_n` param — h-m2 adds it independently
- `zscore_normalize`: guard `np.std(margins) == 0` before dividing; return `np.zeros_like(margins)`
- Bootstrap seed: use `np.random.RandomState(seed)` passed to `resample(random_state=rng)` for reproducibility
- `analyze_family` must store `base_betas` and `inst_betas` arrays in result dict for visualize.py
- Gate: BOTH `beta_instruct < beta_base` AND `p_value < P_VALUE_THRESHOLD` must be True
- All figures: `dpi=300`, `fontsize=12`, save as PNG to `FIGURES_DIR`
- No GPU required; expected runtime <5 min CPU
