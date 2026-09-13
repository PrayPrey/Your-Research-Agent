# Logic: H-M2 — Reward Entropy & Predictive Correlation

**Applied**: Standard scipy Pearson correlation with Fisher z CI
**Applied**: numpy diff for sequential gains

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from base code
**Analyzed Path**: `h-e1/code/`
**Relevant Symbols**:
- `compute_reward_density(rewards_group: list[float]) -> float` — returns **1.0 or 0.0** (binary, NOT a fraction). std > REWARD_EPSILON check.
- `RewardDensityCallback.on_step_end()` — logs per-step binary density to `reward_density_{condition}.csv` (columns: step, reward_density). CSV has up to 5000 rows (one per step).
- `evaluate_all_checkpoints(condition, checkpoint_dir)` — returns `list[{step: int, "pass@1": float}]`, saved via `save_results()` to `eval_results_{condition}.json` (NOT per-checkpoint CSVs).
- `save_results(condition, results, output_dir)` — writes `eval_results_{condition}.json` with top-level results dict.

**CRITICAL**: Reward density CSV has per-step binary values (up to 5000 rows). Must aggregate into 500-step windows. pass@1 checkpoint CSVs likely absent — fallback must parse `eval_results_{condition}.json` which stores a results dict, not the checkpoint sweep list directly.

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual H-E1 Code)

```python
# From: h-e1/code/training/reward.py (ACTUAL CODE)
def compute_reward_density(rewards_group: list[float]) -> float:
    """Returns 1.0 if std(rewards_group) > 0, else 0.0."""
    # Binary output — NOT a fraction

# From: h-e1/code/training/callbacks.py (ACTUAL CODE)
class RewardDensityCallback(TrainerCallback):
    def __init__(self, condition: str, log_dir: str = LOG_DIR) -> None: ...
    # Writes CSV: columns ["step", "reward_density"], one row per training step
    # density values are 0.0 or 1.0 (binary)

# From: h-e1/code/evaluation/evaluate.py (ACTUAL CODE)
def evaluate_all_checkpoints(condition: str, checkpoint_dir: str) -> list:
    """Returns list[{"step": int, "pass@1": float}]."""

def save_results(condition: str, results: dict, output_dir: str) -> None:
    """Writes eval_results_{condition}.json — top-level dict, not list."""
```

**Verified from**: `h-e1/code/training/reward.py`, `h-e1/code/training/callbacks.py`, `h-e1/code/evaluation/evaluate.py`

**Key implication for H-M2**:
- Density CSV has per-step binary rows. If nrows > 50, aggregate: group by 500-step windows, take mean → fraction in [0,1] suitable for entropy and correlation.
- `eval_results_{condition}.json` stores a dict. The checkpoint sweep list may be under key `"checkpoints"` or similar — must inspect at runtime and adapt.

---

## A-2: DataLoader [Complexity: 11, Budget: 3 subtasks]

### API Signatures

```python
# analysis/load_data.py
import os
import json
import pandas as pd
from typing import Optional

CONDITIONS: list[str] = ["curriculum", "uniform", "easy_only", "hard_only"]


def load_reward_density(log_dir: str, condition: str) -> pd.DataFrame:
    """Load and aggregate reward density CSV. Returns DataFrame(step, reward_density) with ~10 rows."""
    # Returns: pd.DataFrame with columns ["step", "reward_density"], sorted by step
    # Raises: FileNotFoundError if CSV missing; AssertionError if columns absent
    ...


def load_pass1_checkpoints(
    log_dir: str,
    condition: str,
    results_dir: Optional[str] = None,
) -> pd.DataFrame:
    """Load pass@1 checkpoint data. Primary: CSV. Fallback: eval_results JSON.
    Returns DataFrame(step, pass1), sorted by step, >= 5 rows."""
    # Raises: RuntimeError if neither source yields >= 5 rows
    ...


def load_all_conditions(
    log_dir: str,
    results_dir: Optional[str] = None,
) -> dict[str, dict[str, pd.DataFrame]]:
    """Load all 4 conditions. Returns {condition: {"density": df, "pass1": df}}."""
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | load_reward_density | Full signature with aggregation logic |
| L-2-2 | load_pass1_checkpoints | JSON fallback logic |
| L-2-3 | load_all_conditions | Wrapper over both loaders |

### Pseudo-code: load_reward_density

```
1. path = f"{log_dir}/reward_density_{condition}.csv"
2. df = pd.read_csv(path)
3. assert "step" in df.columns and "reward_density" in df.columns
4. df = df.sort_values("step").reset_index(drop=True)
5. if len(df) > 50:  # per-step binary values — aggregate
       df["window"] = (df["step"] - 1) // 500  # window 0=steps 1-500, etc.
       df = df.groupby("window").agg(
           step=("step", "max"),          # use window-end step
           reward_density=("reward_density", "mean")
       ).reset_index(drop=True)
       df = df.sort_values("step").reset_index(drop=True)
6. assert len(df) >= 10, f"Only {len(df)} rows after aggregation for {condition}"
7. return df
```

### Pseudo-code: load_pass1_checkpoints (with JSON fallback)

```
1. primary_path = f"{log_dir}/pass1_checkpoint_{condition}.csv"
2. if os.path.exists(primary_path):
       df = pd.read_csv(primary_path)
       assert "step" in df.columns and "pass1" in df.columns
       df = df.sort_values("step").reset_index(drop=True)
       if len(df) >= 5: return df
       warn(f"Only {len(df)} rows in CSV for {condition}, trying JSON fallback")

3. # JSON fallback
   if results_dir is None: raise RuntimeError(f"No pass1 CSV and no results_dir for {condition}")
   json_path = os.path.join(results_dir, f"eval_results_{condition}.json")
   if not os.path.exists(json_path):
       raise FileNotFoundError(f"No pass1 CSV and no JSON at {json_path}")

   with open(json_path) as f: data = json.load(f)

   # eval_results_{condition}.json is a dict; checkpoint list may be nested
   rows = []
   if isinstance(data, list):
       rows = [{"step": r["step"], "pass1": r["pass@1"]} for r in data if r.get("pass@1") is not None]
   elif isinstance(data, dict):
       # Try common keys: "checkpoints", "results", or top-level step keys
       for key in ("checkpoints", "results", "checkpoint_results"):
           if key in data and isinstance(data[key], list):
               rows = [{"step": r["step"], "pass1": r["pass@1"]} for r in data[key] if r.get("pass@1") is not None]
               break
       if not rows:
           # scan for step-keyed entries: {"500": {"pass@1": 0.1}, ...}
           for k, v in data.items():
               try:
                   step = int(k)
                   p1 = v.get("pass@1") if isinstance(v, dict) else None
                   if p1 is not None: rows.append({"step": step, "pass1": float(p1)})
               except (ValueError, AttributeError):
                   pass

   if len(rows) < 5:
       warn(f"WARNING: Only {len(rows)} checkpoints available for {condition}")
   assert len(rows) >= 5, f"Minimum 5 checkpoints required for {condition}, got {len(rows)}"

   df = pd.DataFrame(rows).sort_values("step").reset_index(drop=True)
   return df
```

---

## A-4: GainsComputer [Complexity: 9, Budget: 1 subtask]

### API Signatures

```python
# analysis/compute_gains.py
import numpy as np
import pandas as pd


def compute_pass1_gains(pass1_df: pd.DataFrame) -> np.ndarray:
    """Compute pass@1 gain per 500-step interval. pass1_df -> shape (n-1,)."""
    # pass1_df columns: ["step", "pass1"]
    # Returns: np.ndarray shape (9,) for 10-checkpoint input
    ...


def build_pooled_observations(
    data: dict[str, dict[str, pd.DataFrame]],
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Build 36 pooled (density, gain) pairs across all 4 conditions.
    Returns: (all_densities [36], all_gains [36], condition_labels [36])"""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | compute_pass1_gains + build_pooled_observations | Gain computation and pooling |

### Pseudo-code: compute_pass1_gains

```
1. df = pass1_df.sort_values("step").reset_index(drop=True)
2. vals = df["pass1"].values  # shape (n,)
3. gains = np.diff(vals)      # shape (n-1,)
4. assert len(gains) >= 5, f"Too few gains: {len(gains)}"
5. return gains
```

### Pseudo-code: build_pooled_observations

```
1. all_densities, all_gains, labels = [], [], []
2. for cond in CONDITIONS:
       density_df = data[cond]["density"].sort_values("step").reset_index(drop=True)
       pass1_df   = data[cond]["pass1"].sort_values("step").reset_index(drop=True)

       n_ckpts = min(len(density_df), len(pass1_df))
       # Use first 9 density rows (T=500..4500), gains = diff of first 10 pass1 rows
       n_intervals = min(n_ckpts - 1, 9)

       densities = density_df["reward_density"].values[:n_intervals]  # T=step[0]..step[n-2]
       gains = np.diff(pass1_df["pass1"].values[:n_intervals + 1])    # shape (n_intervals,)

       all_densities.extend(densities.tolist())
       all_gains.extend(gains.tolist())
       labels.extend([cond] * n_intervals)

3. n = len(all_densities)
4. if n != 36: print(f"WARNING: Expected 36 pooled observations, got {n}")
5. return np.array(all_densities), np.array(all_gains), labels
```

---

## A-5: CorrelationAnalyzer [Complexity: 12, Budget: 2 subtasks]

### API Signatures

```python
# analysis/pearson_correlation.py
import numpy as np
from scipy import stats


def pearson_with_ci(x: np.ndarray, y: np.ndarray) -> dict:
    """Pearson r with 95% CI via Fisher z. Returns full stats dict."""
    # Returns: {"r": float, "p_twotailed": float, "p_onetailed": float,
    #           "ci_low": float, "ci_high": float, "n": int}
    ...


def build_pooled_observations(
    data: dict[str, dict[str, pd.DataFrame]],
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    # See A-4 — imported from compute_gains


def per_condition_correlations(
    data: dict[str, dict[str, pd.DataFrame]],
) -> dict[str, dict]:
    """Pearson r per condition. Returns {cond: {"r": float, "p_onetailed": float, "n": int}}."""
    ...


def wilcoxon_entropy_test(
    entropy_curriculum_early: np.ndarray,
    entropy_uniform_early: np.ndarray,
) -> dict:
    """One-tailed Wilcoxon signed-rank (curriculum > uniform).
    Returns: {"statistic": float, "p_value": float, "direction_correct": bool}"""
    ...


def evaluate_gate(pearson_result: dict) -> bool:
    """Returns True if r > 0.5 AND p_onetailed < 0.05."""
    return pearson_result["r"] > 0.5 and pearson_result["p_onetailed"] < 0.05


def save_results(
    pooled_pearson: dict,
    entropy_comparison: dict,
    per_condition_r: dict,
    wilcoxon_result: dict,
    output_path: str,
) -> None:
    """Write results_summary.json."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | pearson_with_ci | Fisher z CI implementation |
| L-5-2 | build_pooled_observations indexing | Exact density/gain alignment |

### Pseudo-code: pearson_with_ci (Fisher z CI)

```
1. n = len(x)
2. r, p_twotailed = scipy.stats.pearsonr(x, y)
3. p_onetailed = p_twotailed / 2  # one-tailed: r > 0

4. # Fisher z-transformation for 95% CI
5. z = np.arctanh(r)              # Fisher z = 0.5 * ln((1+r)/(1-r))
6. se = 1.0 / np.sqrt(n - 3)     # standard error of z
7. z_crit = 1.96                  # 95% CI
8. ci_low  = np.tanh(z - z_crit * se)
9. ci_high = np.tanh(z + z_crit * se)

10. return {
        "r": float(r),
        "p_twotailed": float(p_twotailed),
        "p_onetailed": float(p_onetailed),
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "n": int(n),
    }
```

---

## A-9: Integration Test & Gate Eval [Complexity: 10, Budget: 1 subtask]

### API Signatures

```python
# in run_analysis.py or analysis/pearson_correlation.py


def verify_mechanism_activated(log_dir: str, results_dir: Optional[str] = None) -> tuple[bool, dict]:
    """End-to-end gate check. Returns (gate_passed, indicators_dict)."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | verify_mechanism_activated | Full pipeline gate check |

### Pseudo-code: verify_mechanism_activated

```
1. conditions = ["curriculum", "uniform", "easy_only", "hard_only"]
2. all_densities, all_gains = [], []

3. for cond in conditions:
       density_df = load_reward_density(log_dir, cond)       # aggregated, >=10 rows
       pass1_df   = load_pass1_checkpoints(log_dir, cond, results_dir)  # >=5 rows

       n_ckpts = min(len(density_df), len(pass1_df))
       n_intervals = min(n_ckpts - 1, 9)

       densities = density_df.sort_values("step")["reward_density"].values[:n_intervals]
       pass1_vals = pass1_df.sort_values("step")["pass1"].values
       gains = np.diff(pass1_vals[:n_intervals + 1])

       all_densities.extend(densities.tolist())
       all_gains.extend(gains.tolist())

4. n = len(all_densities)
5. if n != 36:
       print(f"WARNING: Expected 36 observations, got {n}")

6. r, p_twotailed = scipy.stats.pearsonr(np.array(all_densities), np.array(all_gains))
7. p_onetailed = p_twotailed / 2
8. gate_passed = (r > 0.5) and (p_onetailed < 0.05)

9. indicators = {
       "pearson_r": float(r),
       "p_value_twotailed": float(p_twotailed),
       "p_value_onetailed": float(p_onetailed),
       "n_observations": n,
       "gate_passed": gate_passed,
   }
10. print(f"GATE: {'PASSED' if gate_passed else 'FAILED'} — Pearson r={r:.4f}, p={p_onetailed:.4f}")
11. return gate_passed, indicators
```

---

## Tensor Shapes (non-obvious variables)

| Variable | Shape | Note |
|----------|-------|------|
| density_df | DataFrame (10, 2) | After 500-step window aggregation |
| pass1_df | DataFrame (10, 2) | 10 checkpoints per condition |
| gains per condition | (9,) | np.diff of 10 pass1 values |
| all_densities | (36,) | 9 intervals × 4 conditions |
| all_gains | (36,) | 9 intervals × 4 conditions |
| entropy_curriculum_early | (5,) | Steps 500, 1000, 1500, 2000, 2500 |
| entropy_uniform_early | (5,) | Steps 500, 1000, 1500, 2000, 2500 |
