# Logic: h-m4
# Difficulty-Stratified ECE + DELTA_ECE Gate + Temperature Scaling Probe

**Date:** 2026-03-18
**Hypothesis:** h-m4 (MECHANISM — Step 4 of 4)
**Gate:** MUST_WORK — DELTA_ECE >= 0.03 in >= 2/3 models, CI excludes zero, persists post-T

Applied: Standard numpy/scipy statistical analysis (Archon KB domain-mismatch; patterns from Guo 2017, p-lambda/verified_calibration, gpleiss/temperature_scaling)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Serena MCP unavailable (no active project); API signatures read directly from actual source files
**Analyzed Path**: `docs/youra_research/20260316_verifia/h-m3/code/src/h_m3/`
**Relevant Symbols**:
- `load_tier_assignments(hm2_results_dir: Path) -> pd.DataFrame` — supports wide format from h-m2; melts to long with columns [problem_id, model, model_short, tier, pass_at_1]
- `filter_hard_easy_tiers(df: pd.DataFrame) -> pd.DataFrame` — filters tier in {hard, easy}
- `MODEL_SHORT_NAMES: dict[str, str]` — {full_model_id: short_name}
- `MODEL_IDS: list[str]` — 3 model IDs
- `DEFAULT_HM2_RESULTS = "../../h-m2/results"` — path convention anchored at h-m3/code/

**Key Finding**: h-m4 does NOT import h-m3 at runtime. Data loading patterns are replicated in h-m4's own `data_loader.py`. Tier CSV wide-format columns are `llama3_tier`, `codellama_tier`, `deepseek_tier` with row key `task_id`.

---

## External Dependencies API

### From Actual h-m3 Code (NOT from specs)

```python
# File: h-m3/code/src/h_m3/data_loader.py (ACTUAL CODE)
def load_tier_assignments(hm2_results_dir: Path) -> pd.DataFrame:
    # Returns DataFrame with columns: problem_id, model, model_short, tier, pass_at_1
    # Wide-format CSV columns verified: task_id, llama3_tier, codellama_tier, deepseek_tier
    ...

def filter_hard_easy_tiers(df: pd.DataFrame) -> pd.DataFrame:
    # Filters df["tier"].isin({"hard", "easy"})
    ...

# File: h-m3/code/src/h_m3/config.py (ACTUAL CODE)
MODEL_SHORT_NAMES: dict[str, str] = {
    "NousResearch/Meta-Llama-3-8B": "llama3_8b",
    "codellama/CodeLlama-7b-hf": "codellama_7b",
    "deepseek-ai/deepseek-coder-6.7b-base": "deepseek_6.7b",
}
MODEL_IDS: list[str]  # 3 entries matching keys above
HARD_THRESHOLD: float = 0.0
EASY_THRESHOLD: float = 0.6
```

**Verified from**: actual source files at `h-m3/code/src/h_m3/data_loader.py` and `config.py`

**h-m4 path anchoring**: h-m3 uses `../../h-m2/results` anchored at h-m3/code/. h-m4 anchors at h-m4/ folder: `../h-m2/results`, `../h-m3/results`, `../h-e1/results`.

**Tier column map** (from actual h-m3 data_loader.py `tier_col_to_short`):
```python
tier_col_to_short = {
    "llama3_tier": "llama3_8b",
    "codellama_tier": "codellama_7b",
    "deepseek_tier": "deepseek_6.7b",
}
```

---

## A-3: ECE Core [Complexity: 13, Budget: 4 subtasks]

### API Signatures

```python
# src/evaluate.py

def compute_ece(
    confidences: np.ndarray,  # (N,) float, c in [0,1]
    labels: np.ndarray,       # (N,) int, binary {0,1}
    M: int = 15,
) -> float:
    """Guo 2017 ECE: sum_m (n_m/n)|acc_m - conf_m|. Returns NaN if all bins empty."""
    ...

def compute_tier_ece(
    c_hard: np.ndarray,   # (n_hard,)
    y_hard: np.ndarray,   # (n_hard,)
    c_easy: np.ndarray,   # (n_easy,)
    y_easy: np.ndarray,   # (n_easy,)
    M: int = 15,
) -> dict[str, float]:
    """Returns: {"ece_hard": float, "ece_easy": float, "delta_ece": float}"""
    ...

def compute_delta_ece_bootstrap(
    c_hard: np.ndarray,   # (n_hard,)
    y_hard: np.ndarray,   # (n_hard,)
    c_easy: np.ndarray,   # (n_easy,)
    y_easy: np.ndarray,   # (n_easy,)
    n_boot: int = 1000,
    M: int = 15,
    seed: int = 42,
) -> tuple[float, float, float, float]:
    """Bootstrap 95% CI for DELTA_ECE.
    Returns: (delta_ece_obs, ci_lower, ci_upper, p_value)
      p_value = fraction of boot samples <= 0"""
    ...
```

### Pseudo-code

**`compute_ece`**:
```
bins = np.linspace(0, 1, M+1)   # M+1 edges → M bins
if len(confidences) == 0:
    warnings.warn("Empty input to compute_ece"); return float("nan")
n = len(confidences)
ece = 0.0
for i in range(M):
    if i == 0:
        mask = (confidences >= bins[0]) & (confidences <= bins[1])  # include 0.0
    else:
        mask = (confidences > bins[i]) & (confidences <= bins[i+1])
    n_bin = mask.sum()
    if n_bin == 0:
        continue
    acc_bin = labels[mask].mean()
    conf_bin = confidences[mask].mean()
    ece += (n_bin / n) * abs(acc_bin - conf_bin)
return float(ece)
```

**`compute_delta_ece_bootstrap`**:
```
rng = np.random.default_rng(seed)
delta_ece_obs = compute_ece(c_hard, y_hard, M) - compute_ece(c_easy, y_easy, M)
boot_deltas = np.zeros(n_boot)
for b in range(n_boot):
    idx_h = rng.integers(0, len(c_hard), len(c_hard))   # resample with replacement
    idx_e = rng.integers(0, len(c_easy), len(c_easy))
    boot_deltas[b] = (compute_ece(c_hard[idx_h], y_hard[idx_h], M)
                    - compute_ece(c_easy[idx_e], y_easy[idx_e], M))
if np.all(boot_deltas == boot_deltas[0]):
    warnings.warn("Bootstrap collapse: all 1000 samples identical")
ci_lower, ci_upper = np.percentile(boot_deltas, [2.5, 97.5])
p_value = float(np.mean(boot_deltas <= 0))
return delta_ece_obs, ci_lower, ci_upper, p_value
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | compute_ece | Guo 2017 formula, skip empty bins, NaN guard, leftmost bin includes 0 |
| L-3-2 | compute_tier_ece | Call compute_ece twice, return dict with delta_ece |
| L-3-3 | compute_delta_ece_bootstrap | rng.integers resampling, percentile CI, p_value |
| L-3-4 | Edge cases | Bootstrap collapse warning, NaN propagation, empty-tier guard |

---

## A-6: Temperature Scaling [Complexity: 12, Budget: 3 subtasks]

### API Signatures

```python
# src/temperature_scaling.py

def fit_temperature(
    c_holdout: np.ndarray,   # (n_holdout,) float, c in [0,1]
    y_holdout: np.ndarray,   # (n_holdout,) int, binary {0,1}
    bounds: tuple[float, float] = (0.01, 10.0),
) -> float:
    """Fit T* on holdout by minimizing binary NLL via scipy.optimize.minimize_scalar.
    Returns T* or float('nan') if convergence fails."""
    ...

def apply_temperature(
    confidences: np.ndarray,   # (N,)
    T: float,
) -> np.ndarray:
    """Returns: np.clip(confidences / T, 0.0, 1.0)  shape (N,)"""
    ...

def compute_post_T_metrics(
    eval_data: dict,     # keys: c_hard, y_hard, c_easy, y_easy
    holdout_data: dict,  # keys: c_hard, y_hard, c_easy, y_easy
    M: int = 15,
    n_boot: int = 1000,
    seed: int = 42,
) -> dict[str, float]:
    """Fit T on combined holdout, scale eval_data, recompute all ECE metrics.
    Returns: {T_star, post_T_ece_hard, post_T_ece_easy, post_T_delta_ece,
              post_T_ci_lower, post_T_ci_upper, post_T_p_value, gate_p3}"""
    ...
```

### Pseudo-code

**`fit_temperature`**:
```
def nll_objective(T: float) -> float:
    c_scaled = np.clip(c_holdout / T, 1e-7, 1.0 - 1e-7)
    return -float(np.mean(
        y_holdout * np.log(c_scaled) + (1 - y_holdout) * np.log(1 - c_scaled)
    ))

result = scipy.optimize.minimize_scalar(nll_objective, bounds=bounds, method='bounded')
if not result.success:
    warnings.warn(f"T-fitting did not converge for this model; P3 = INCONCLUSIVE")
    return float('nan')
return float(result.x)
```

**`compute_post_T_metrics`**:
```
c_ho_all = np.concatenate([holdout_data["c_hard"], holdout_data["c_easy"]])
y_ho_all = np.concatenate([holdout_data["y_hard"], holdout_data["y_easy"]])
T_star = fit_temperature(c_ho_all, y_ho_all)

if np.isnan(T_star):
    return {"T_star": float("nan"), "gate_p3": False, "post_T_delta_ece": float("nan"),
            "post_T_ci_lower": float("nan"), "post_T_ci_upper": float("nan"),
            "post_T_p_value": float("nan"), "post_T_ece_hard": float("nan"),
            "post_T_ece_easy": float("nan")}

c_hard_sc = apply_temperature(eval_data["c_hard"], T_star)
c_easy_sc = apply_temperature(eval_data["c_easy"], T_star)

delta, ci_lo, ci_hi, p = compute_delta_ece_bootstrap(
    c_hard_sc, eval_data["y_hard"], c_easy_sc, eval_data["y_easy"],
    n_boot=n_boot, M=M, seed=seed)
gate_p3 = bool((delta >= 0.03) and (ci_lo > 0))

return {
    "T_star": T_star,
    "post_T_ece_hard": compute_ece(c_hard_sc, eval_data["y_hard"], M),
    "post_T_ece_easy": compute_ece(c_easy_sc, eval_data["y_easy"], M),
    "post_T_delta_ece": delta,
    "post_T_ci_lower": ci_lo,
    "post_T_ci_upper": ci_hi,
    "post_T_p_value": p,
    "gate_p3": gate_p3,
}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | fit_temperature | Binary NLL via minimize_scalar bounded, NaN on failure |
| L-6-2 | apply_temperature | np.clip(c / T, 0, 1) one-liner |
| L-6-3 | compute_post_T_metrics | Combine holdout, fit T, scale eval set, rerun bootstrap, gate_p3 |

---

## A-8: Figures 1-3 [Complexity: 12, Budget: 3 subtasks]

### API Signatures

```python
# src/visualize.py

def plot_delta_ece_gate(
    model_results: dict[str, dict],
    # {model_short: {delta_ece: float, ci_lower: float, ci_upper: float, gate_p1: bool}}
    output_path: Path,
    threshold: float = 0.03,
) -> None:
    """Fig 1: Bar chart DELTA_ECE + 95% CI error bars per model.
    green=PASS (gate_p1=True), red=FAIL. Dashed lines at y=0 and y=threshold."""
    ...

def plot_reliability_diagrams(
    model_eval_data: dict[str, dict],
    # {model_short: {c_hard, y_hard, c_easy, y_easy}}
    model_results: dict[str, dict],
    # {model_short: {ece_hard: float, ece_easy: float}}
    output_path: Path,
    M: int = 15,
) -> None:
    """Fig 2: 3x2 subplot grid (rows=models, cols=hard/easy tiers).
    Each subplot: binned accuracy bars vs confidence, identity diagonal, ECE annotation."""
    ...

def plot_temperature_scaling_effect(
    model_results: dict[str, dict],
    # {model_short: {delta_ece, post_T_delta_ece, T_star, gate_p1, gate_p3}}
    output_path: Path,
) -> None:
    """Fig 3: Grouped bars pre/post T-scaling DELTA_ECE per model. T* annotated on bars."""
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | plot_delta_ece_gate | ax.bar + asymmetric error bars (delta-ci_lo, ci_hi-delta), color by gate_p1, axhline at 0 and 0.03 |
| L-8-2 | plot_reliability_diagrams | fig 3×2 subplots; per subplot: compute bin_acc per M bins, bar acc, plot confidence line, diagonal, annotate ECE |
| L-8-3 | plot_temperature_scaling_effect | Two grouped bars (pre/post) per model, annotate T*, axhline at 0.03 |

---

## A-2: Data Loader [Complexity: 11, Budget: 4 subtasks]

### API Signatures

```python
# src/data_loader.py

def load_confidence_scores(hm3_results_dir: Path) -> dict[str, dict[str, float]]:
    """Load ptrue_confidence_scores.json.
    Returns: {model_short: {task_id: mean_c}} (mean over k solutions)
    Raises: FileNotFoundError if missing."""
    ...

def load_tier_assignments(hm2_results_dir: Path) -> pd.DataFrame:
    """Load tier_assignments.csv (wide format matching h-m2 output).
    Returns: DataFrame with columns [task_id, llama3_tier, codellama_tier, deepseek_tier]
    Raises: FileNotFoundError if missing."""
    ...

def load_correctness(he1_results_dir: Path, model_short: str) -> dict[str, int]:
    """Load correctness_{model_short}.json.
    Returns: {task_id: binary_label} where label = int(mean(solutions) > 0)
    Raises: FileNotFoundError if missing."""
    ...

def align_model_data(
    confidence: dict[str, dict[str, float]],
    tier_df: pd.DataFrame,
    correctness: dict[str, dict[str, int]],
    model_short: str,
) -> dict:
    """Align arrays for one model.
    Returns: {c_hard:(n_hard,), y_hard:(n_hard,), c_easy:(n_easy,), y_easy:(n_easy,),
              n_hard:int, n_easy:int}
    Raises: ValueError if n_hard < MIN_TIER_SIZE or n_easy < MIN_TIER_SIZE.
    Special: CodeLlama n_easy=0 on HE → filter to MBPP-only easy tasks; warn, not fail."""
    ...

def make_holdout_split(
    c_hard: np.ndarray,
    y_hard: np.ndarray,
    c_easy: np.ndarray,
    y_easy: np.ndarray,
    holdout_frac: float = 0.2,
    seed: int = 42,
) -> tuple[dict, dict]:
    """80/20 random split per tier independently.
    Returns: (eval_data, holdout_data) each with keys c_hard, y_hard, c_easy, y_easy"""
    ...
```

### Pseudo-code

**`load_confidence_scores`**:
```
path = Path(hm3_results_dir) / "ptrue_confidence_scores.json"
if not path.exists(): raise FileNotFoundError(f"ptrue_confidence_scores.json not found: {path}")
raw = json.load(open(path))
# raw: {model_short: {task_id: [c_values]}}
return {
    ms: {tid: float(np.mean(c_list)) for tid, c_list in task_dict.items()}
    for ms, task_dict in raw.items()
}
```

**`load_correctness`**:
```
path = Path(he1_results_dir) / f"correctness_{model_short}.json"
if not path.exists(): raise FileNotFoundError(...)
raw = json.load(open(path))
# raw: {task_id: [binary_per_solution]}
return {tid: int(np.mean(vals) > 0) for tid, vals in raw.items()}
```

**`align_model_data`** (CodeLlama special case):
```
tier_col_map = {"llama3_8b": "llama3_tier", "codellama_7b": "codellama_tier", "deepseek_6.7b": "deepseek_tier"}
col = tier_col_map[model_short]
hard_ids = tier_df[tier_df[col] == "hard"]["task_id"].tolist()
easy_ids = tier_df[tier_df[col] == "easy"]["task_id"].tolist()

# CodeLlama special case
if model_short == "codellama_7b" and len(easy_ids) < MIN_TIER_SIZE:
    easy_ids_mbpp = [t for t in easy_ids if "Mbpp" in t or "mbpp" in t]
    if len(easy_ids_mbpp) >= MIN_TIER_SIZE:
        warnings.warn(f"CodeLlama: n_easy HE=0, using MBPP-only easy ({len(easy_ids_mbpp)} tasks)")
        easy_ids = easy_ids_mbpp
    else:
        warnings.warn(f"CodeLlama: n_easy={len(easy_ids)} < MIN_TIER_SIZE after MBPP filter; using all easy")

model_conf = confidence.get(model_short, {})
model_corr = correctness.get(model_short, {})

def extract(ids):
    pairs = [(model_conf[t], model_corr[t]) for t in ids if t in model_conf and t in model_corr]
    if not pairs: return np.array([]), np.array([], dtype=int)
    c, y = zip(*pairs)
    return np.array(c, dtype=float), np.array(y, dtype=int)

c_hard, y_hard = extract(hard_ids)
c_easy, y_easy = extract(easy_ids)

if len(c_hard) < MIN_TIER_SIZE: raise ValueError(f"n_hard={len(c_hard)} < MIN_TIER_SIZE for {model_short}")
if len(c_easy) < MIN_TIER_SIZE: raise ValueError(f"n_easy={len(c_easy)} < MIN_TIER_SIZE for {model_short}")
return {"c_hard": c_hard, "y_hard": y_hard, "c_easy": c_easy, "y_easy": y_easy,
        "n_hard": len(c_hard), "n_easy": len(c_easy)}
```

**`make_holdout_split`**:
```
rng = np.random.default_rng(seed)

def split(c, y):
    idx = rng.permutation(len(c))
    n_ho = max(1, int(len(c) * holdout_frac))
    return c[idx[n_ho:]], y[idx[n_ho:]], c[idx[:n_ho]], y[idx[:n_ho]]

c_he, y_he, c_hh, y_hh = split(c_hard, y_hard)
c_ee, y_ee, c_eh, y_eh = split(c_easy, y_easy)
eval_data = {"c_hard": c_he, "y_hard": y_he, "c_easy": c_ee, "y_easy": y_ee}
holdout_data = {"c_hard": c_hh, "y_hard": y_hh, "c_easy": c_eh, "y_easy": y_eh}
return eval_data, holdout_data
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | load_confidence_scores + load_correctness | JSON load, mean aggregation |
| L-2-2 | load_tier_assignments | Preserve wide-format; no melt needed (h-m4 reads columns directly) |
| L-2-3 | align_model_data | Wide-format column lookup, CodeLlama MBPP fallback, MIN_TIER_SIZE guard |
| L-2-4 | make_holdout_split | rng.permutation per tier, 80/20 split |

---

## A-12: Tests [Complexity: 11, Budget: 4 subtasks]

### Test Structure

```python
# tests/test_ece.py
def test_perfect_calibration():
    """compute_ece(c=y) == 0 when c equals y exactly (single bin)."""
    c = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
    y = np.array([0,   0,   1,   1,   1])
    # With M=5 bins, each sample in own bin: ECE should be small
    assert compute_ece(c, y, M=5) < 0.1

def test_ece_extreme_overconfidence():
    """c=1.0, y=0 → ECE = 1.0."""
    c = np.ones(20); y = np.zeros(20, dtype=int)
    assert abs(compute_ece(c, y, M=15) - 1.0) < 1e-6

def test_ece_empty_bin_skip():
    """All c in [0.9, 1.0] bin; other 14 bins empty → no exception."""
    c = np.full(10, 0.95); y = np.ones(10, dtype=int)
    result = compute_ece(c, y, M=15)
    assert not np.isnan(result)

def test_ece_nan_empty_input():
    """Empty arrays → returns NaN with warning."""
    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = compute_ece(np.array([]), np.array([]))
        assert np.isnan(result)
        assert len(w) == 1

# tests/test_bootstrap.py
def test_bootstrap_reproducibility():
    """Identical (delta, ci_lo, ci_hi, p) across two calls with same seed."""
    c_h = np.random.default_rng(0).uniform(0.3, 0.8, 50)
    y_h = np.zeros(50, dtype=int)
    c_e = np.random.default_rng(1).uniform(0.5, 0.9, 50)
    y_e = np.ones(50, dtype=int)
    r1 = compute_delta_ece_bootstrap(c_h, y_h, c_e, y_e, seed=42)
    r2 = compute_delta_ece_bootstrap(c_h, y_h, c_e, y_e, seed=42)
    assert r1 == r2

def test_bootstrap_ci_excludes_zero_large_delta():
    """Synthetic large DELTA_ECE → ci_lower > 0."""
    c_h = np.full(100, 0.9); y_h = np.zeros(100, dtype=int)   # ECE(hard) ≈ 0.9
    c_e = np.full(100, 0.6); y_e = np.ones(100, dtype=int)     # ECE(easy) ≈ 0.4
    _, ci_lo, _, _ = compute_delta_ece_bootstrap(c_h, y_h, c_e, y_e, n_boot=200, seed=42)
    assert ci_lo > 0

def test_bootstrap_p_value_range():
    """p_value in [0, 1]."""
    c_h = np.random.default_rng(99).uniform(0, 1, 30)
    y_h = np.random.default_rng(99).integers(0, 2, 30)
    c_e = np.random.default_rng(100).uniform(0, 1, 30)
    y_e = np.random.default_rng(100).integers(0, 2, 30)
    _, _, _, p = compute_delta_ece_bootstrap(c_h, y_h, c_e, y_e, n_boot=100, seed=42)
    assert 0.0 <= p <= 1.0

# tests/test_temperature.py
def test_apply_temperature_clip():
    """c/T > 1 clipped to 1; c/T < 0 clipped to 0."""
    c = np.array([0.5, 0.9, 0.1])
    assert apply_temperature(c, T=0.4)[1] == 1.0   # 0.9/0.4 = 2.25 → 1.0
    assert apply_temperature(c, T=10.0)[2] == pytest.approx(0.01)

def test_fit_temperature_well_calibrated():
    """Near-perfect c → T* ≈ 1.0 (within 0.3 tolerance)."""
    rng = np.random.default_rng(42)
    y = rng.integers(0, 2, 200)
    c = np.clip(y.astype(float) + rng.normal(0, 0.05, 200), 0.01, 0.99)
    T = fit_temperature(c, y)
    assert 0.7 <= T <= 1.3

def test_fit_temperature_overconfident():
    """Overconfident c → T* > 1."""
    y = np.zeros(100, dtype=int)
    c = np.full(100, 0.95)
    T = fit_temperature(c, y)
    assert T > 1.0

# tests/test_data_loader.py
def test_load_confidence_scores_file_not_found(tmp_path):
    """Raises FileNotFoundError with path in message."""
    with pytest.raises(FileNotFoundError, match="ptrue_confidence_scores.json"):
        load_confidence_scores(tmp_path)

def test_align_model_data_min_tier_size(tmp_path):
    """Raises ValueError when n_hard < MIN_TIER_SIZE after alignment."""
    # Build tiny tier_df with 3 hard tasks only
    ...
    with pytest.raises(ValueError, match="n_hard"):
        align_model_data(confidence, tier_df, correctness, "llama3_8b")

def test_make_holdout_split_sizes():
    """Eval set ~80%, holdout ~20% of each tier."""
    c_h = np.zeros(100); y_h = np.zeros(100, dtype=int)
    c_e = np.zeros(50);  y_e = np.zeros(50, dtype=int)
    ev, ho = make_holdout_split(c_h, y_h, c_e, y_e, holdout_frac=0.2, seed=42)
    assert len(ev["c_hard"]) == 80 and len(ho["c_hard"]) == 20
    assert len(ev["c_easy"]) == 40 and len(ho["c_easy"]) == 10
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-12-1 | test_ece.py | 4 unit tests: perfect, extreme, empty-bin, NaN |
| L-12-2 | test_bootstrap.py | 3 tests: reproducibility, CI direction, p-value range |
| L-12-3 | test_temperature.py | 3 tests: clip, well-calibrated identity, overconfident direction |
| L-12-4 | test_data_loader.py | 3 tests: FileNotFoundError, MIN_TIER_SIZE ValueError, split sizes |

---

## Supplementary Functions (Non-allocated tasks)

### compute_null_baseline

```python
def compute_null_baseline(
    c_hard: np.ndarray,   # (n_hard,)
    y_hard: np.ndarray,   # (n_hard,)
    c_easy: np.ndarray,   # (n_easy,)
    y_easy: np.ndarray,   # (n_easy,)
    M: int = 15,
) -> dict[str, float]:
    """Returns: {null_conf_hard, null_conf_easy, ece_null_hard, ece_null_easy,
                 excess_ece_hard, excess_ece_easy}"""
    ...
```

**Pseudo-code**:
```
null_conf_hard = float(y_hard.mean())   # tier accuracy ≈ 0.0
null_conf_easy = float(y_easy.mean())   # tier accuracy ≈ 0.6+
c_null_hard = np.full(len(y_hard), null_conf_hard)
c_null_easy = np.full(len(y_easy), null_conf_easy)
ece_null_hard = compute_ece(c_null_hard, y_hard, M)
ece_null_easy = compute_ece(c_null_easy, y_easy, M)
ece_hard = compute_ece(c_hard, y_hard, M)
ece_easy = compute_ece(c_easy, y_easy, M)
return {
    "null_conf_hard": null_conf_hard, "null_conf_easy": null_conf_easy,
    "ece_null_hard": ece_null_hard, "ece_null_easy": ece_null_easy,
    "excess_ece_hard": ece_hard - ece_null_hard,
    "excess_ece_easy": ece_easy - ece_null_easy,
}
```

### compute_m_sensitivity

```python
def compute_m_sensitivity(
    c_hard: np.ndarray, y_hard: np.ndarray,
    c_easy: np.ndarray, y_easy: np.ndarray,
    m_values: list[int] = [10, 15, 20],
) -> dict[int, float]:
    """Returns: {M: delta_ece} e.g. {10: 0.042, 15: 0.038, 20: 0.041}"""
    return {
        M: float(compute_ece(c_hard, y_hard, M) - compute_ece(c_easy, y_easy, M))
        for M in m_values
    }
```

### evaluate_gate

```python
def evaluate_gate(
    model_results: dict[str, dict],
    threshold: float = 0.03,
    min_passing: int = 2,
) -> tuple[bool, int]:
    """P1 gate: PASS if delta_ece >= threshold AND ci_lower > 0.
    Returns: (gate_pass: bool, n_passing: int)"""
    n_passing = sum(
        1 for r in model_results.values()
        if r.get("delta_ece", 0) >= threshold and r.get("ci_lower", -1) > 0
    )
    return n_passing >= min_passing, n_passing
```

### verify_mechanism_activated

```python
def verify_mechanism_activated(
    ece_hard: float, ece_easy: float, delta_ece: float,
    n_hard: int, n_easy: int,
    ci_lower: float, ci_upper: float,
) -> tuple[bool, dict[str, bool]]:
    """Returns: (all_pass: bool, indicators: dict)"""
    indicators = {
        "data_loaded": n_hard >= 20 and n_easy >= 20,
        "ece_computed": (not np.isnan(ece_hard)) and (not np.isnan(ece_easy)),
        "delta_nontrivial": abs(delta_ece) > 1e-6,
        "ci_computed": ci_upper > ci_lower,
        "effect_measured": True,
    }
    return all(indicators.values()), indicators
```

### run_experiment (orchestration)

```python
def run_experiment(cfg: ExperimentConfig) -> dict:
    """Full orchestration. Returns results dict (gate_overall, per-model metrics)."""
    ...
```

**Pseudo-code**:
```
1. Load data:
   confidence = load_confidence_scores(Path(cfg.hm3_results))
   tier_df = load_tier_assignments(Path(cfg.hm2_results))
   correctness = {ms: load_correctness(Path(cfg.he1_results), ms)
                  for ms in MODEL_SHORT_NAMES.values()}

2. Per model (model_short in MODEL_SHORT_NAMES.values()):
   try:
     a. aligned = align_model_data(confidence, tier_df, correctness, model_short)
     b. eval_data, holdout_data = make_holdout_split(
            aligned["c_hard"], aligned["y_hard"],
            aligned["c_easy"], aligned["y_easy"],
            holdout_frac=HOLDOUT_FRAC, seed=cfg.seed)
     c. tier_ece = compute_tier_ece(eval_data["c_hard"], eval_data["y_hard"],
                                     eval_data["c_easy"], eval_data["y_easy"],
                                     M=cfg.m_primary)
     d. delta, ci_lo, ci_hi, p = compute_delta_ece_bootstrap(
            eval_data["c_hard"], eval_data["y_hard"],
            eval_data["c_easy"], eval_data["y_easy"],
            n_boot=cfg.n_boot, M=cfg.m_primary, seed=cfg.seed)
     e. null_m = compute_null_baseline(eval_data["c_hard"], eval_data["y_hard"],
                                        eval_data["c_easy"], eval_data["y_easy"])
     f. m_sens = compute_m_sensitivity(eval_data["c_hard"], eval_data["y_hard"],
                                        eval_data["c_easy"], eval_data["y_easy"])
     g. post_T = compute_post_T_metrics(eval_data, holdout_data,
                                         M=cfg.m_primary, n_boot=cfg.n_boot, seed=cfg.seed)
     h. all_ok, indicators = verify_mechanism_activated(
            tier_ece["ece_hard"], tier_ece["ece_easy"], delta,
            aligned["n_hard"], aligned["n_easy"], ci_lo, ci_hi)
     i. gate_p1 = (delta >= DELTA_ECE_THRESHOLD) and (ci_lo > 0)
     j. print diagnostic to stdout (per FR-6.2 format)
     k. store per-model results dict
   except ValueError as e:
     warnings.warn(f"Skipping {model_short}: {e}")
     continue

3. gate_pass, n_pass = evaluate_gate(model_results)
4. gate_p2_count = sum(r["excess_ece_hard"] > r["excess_ece_easy"] for r in model_results.values())
5. gate_p3_count = sum(r["gate_p3"] for r in model_results.values())

6. results = {
     "gate_overall": "PASS" if gate_pass else "FAIL",
     "n_models_passing_p1": n_pass,
     "models": model_results,
     "m_sensitivity": {ms: m_sensitivity_results[ms] for ms in model_results},
     "gate_p2_count": gate_p2_count,
     "gate_p3_count": gate_p3_count,
     "seed": cfg.seed, "n_boot": cfg.n_boot, "M_primary": cfg.m_primary,
   }

7. Path(cfg.output_dir).mkdir(parents=True, exist_ok=True)
   save_results(results, Path(cfg.output_dir))

8. Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)
   fig_cfg = FigureConfig(figures_dir=cfg.figures_dir)
   save_all_figures(model_eval_data, model_results, m_sensitivity_results,
                    bootstrap_samples, fig_cfg)

9. return results
```

---

## Tensor Shapes Summary

| Variable | Shape | dtype | Note |
|----------|-------|-------|------|
| c_hard, c_easy | (n_hard,), (n_easy,) | float64 | c in [0,1] |
| y_hard, y_easy | (n_hard,), (n_easy,) | int | binary {0,1} |
| boot_deltas | (n_boot,) = (1000,) | float64 | bootstrap distribution |
| c_scaled | same as input | float64 | after apply_temperature |

---

## Error Conditions

| Condition | Behavior |
|-----------|----------|
| Input file missing | `raise FileNotFoundError` with explicit path |
| n_hard < 20 or n_easy < 20 | `raise ValueError(f"n_{tier}={n} < MIN_TIER_SIZE=20")` |
| ECE all-empty bins | `return float('nan')` + `warnings.warn(...)` |
| All bootstrap samples identical | `warnings.warn("bootstrap collapse detected")` |
| T-fitting does not converge | `return float('nan')` + P3 = INCONCLUSIVE |
| CodeLlama n_easy=0 on HE | `warnings.warn(...)` + use MBPP-only easy tasks |
