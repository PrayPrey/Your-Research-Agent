# Logic: H-M2
## DPO vs SFT Logit Delta Variance in Low-Margin Regions

**Hypothesis ID:** H-M2
**Type:** MECHANISM (INCREMENTAL — extends H-M1)
**Date:** 2026-03-17
**Budget:** 10 subtasks

Applied: Standard scipy/numpy patterns (Archon KB domain mismatch — diffusion content only)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-m1/code/ implementation
**Analyzed Path**: `docs/youra_research/20260317_buildingtrust/h-m1/code/`
**Relevant Symbols**:
- `compute_logit_delta(base_logprobs, aligned_logprobs)` → `np.ndarray [N, 4]`
- `run_isotropic_sanity_check(n_items, seed)` → `dict`
- `verify_mechanism_activated(pair_id, base_logprobs, aligned_logprobs, results)` → `tuple`
- `evaluate_gate(all_pair_results, gate_thresholds)` → `dict`
- `MODEL_PAIRS`, `DATASETS`, `GATE_THRESHOLDS` in `config.py`

---

## External Dependencies API (Base Hypothesis)

Signatures verified from actual `h-m1/code/analysis_anisotropy.py` (NOT spec):

```python
# From: h-m1/code/analysis_anisotropy.py (ACTUAL CODE)

def compute_logit_delta(
    base_logprobs: np.ndarray,    # [N, 4]
    aligned_logprobs: np.ndarray, # [N, 4]
) -> np.ndarray:                  # [N, 4]
    """Compute delta = aligned - base. No centering."""
    ...

def run_isotropic_sanity_check(
    n_items: int = 1000,
    seed: int = 1,
) -> dict:
    """Returns {"anisotropy_ratio": float, "expected_approx_1": bool}."""
    ...
```

**Import path** (matches H-M1 actual pattern from `config.py`):
```python
import sys, os
HM1_CODE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "h-m1", "code"))
sys.path.insert(0, HM1_CODE_DIR)
from analysis_anisotropy import compute_logit_delta
```

**Verified from**: `h-m1/code/analysis_anisotropy.py` and `h-m1/code/config.py` (actual code)

---

## A-5: Statistical Testing [Complexity: 14, Budget: 4 subtasks]

Applied: Welch's t one-tailed + bootstrap CI (standard scipy pattern)

### API Signatures

```python
# analysis_variance.py

def test_method_quintile_interaction(
    dpo_q1_residuals: np.ndarray,  # (n_dpo_q1,) KL-residualized delta_var for DPO Q1
    sft_q1_residuals: np.ndarray,  # (n_sft_q1,) KL-residualized delta_var for SFT Q1
    n_bootstrap: int = 5000,
    seed: int = 1,
) -> dict:
    """Welch's t (one-tailed), Cohen's d, variance ratio, bootstrap CI.

    Returns keys: t_stat, p_one_tailed, cohens_d, q1_variance_ratio, bootstrap_ci.
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| dpo_q1_residuals | (n_dpo_q1,) | ~2808 for MMLU, ~163 for TQA |
| sft_q1_residuals | (n_sft_q1,) | same expected sizes |
| bootstrap_ci | (2,) | [lower, upper] 95% CI on variance ratio |

### Pseudo-code (non-trivial algorithm)

```
1. t_stat, p_two = scipy.stats.ttest_ind(dpo_q1_residuals, sft_q1_residuals, equal_var=False)
2. p_one_tailed = p_two / 2  # directional: DPO > SFT
3. pooled_std = sqrt((var(dpo_q1_residuals) + var(sft_q1_residuals)) / 2)
4. cohens_d = (mean(dpo) - mean(sft)) / pooled_std
5. q1_variance_ratio = var(dpo_q1_residuals) / var(sft_q1_residuals)
6. np.random.seed(seed)
7. bootstrap_ratios = []
   for _ in range(n_bootstrap):
       dpo_boot = np.random.choice(dpo_q1_residuals, size=len(dpo_q1_residuals), replace=True)
       sft_boot = np.random.choice(sft_q1_residuals, size=len(sft_q1_residuals), replace=True)
       bootstrap_ratios.append(var(dpo_boot) / var(sft_boot))
8. bootstrap_ci = (np.percentile(bootstrap_ratios, 2.5), np.percentile(bootstrap_ratios, 97.5))
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Welch's t one-tailed | ttest_ind + p_two/2 directional |
| L-5-2 | Cohen's d + variance ratio | pooled_std, q1_variance_ratio |
| L-5-3 | Bootstrap CI (5000 reps) | resample residuals, var ratio distribution |
| L-5-4 | Cross-benchmark gate | p < 0.05 on >= 2/3 datasets |

---

## A-4: KL-Residualized Variance [Complexity: 13, Budget: 2 subtasks]

Applied: OLS residualization via np.polyfit (standard numpy pattern)

### API Signatures

```python
def compute_variance_by_quintile(
    base_logprobs: np.ndarray,    # (N, 4)
    aligned_logprobs: np.ndarray, # (N, 4)
    margin: np.ndarray,           # (N,) z-scored confidence margin from cache
    kl_div: np.ndarray,           # (N,)
    n_quintiles: int = 5,
    kl_control: bool = True,
) -> dict:
    """Compute KL-residualized delta variance per quintile.

    Returns: quintile_variances (5,), quintile_counts (5,), q1_residuals (n_q1,),
             kl_residualization_applied (bool), boundaries (6,).
    """
    ...
```

### Pseudo-code

```
1. delta = compute_logit_delta(base_logprobs, aligned_logprobs)  # (N, 4)
2. delta_var = np.var(delta, axis=1)                              # (N,)
3. boundaries = np.percentile(margin, [0, 20, 40, 60, 80, 100])  # (6,)
4. quintile_labels = np.digitize(margin, boundaries[1:-1])        # (N,) in [0..4]
5. for q in range(n_quintiles):
     mask = (quintile_labels == q)
     delta_var_q = delta_var[mask]    # (n_q,)
     kl_q = kl_div[mask]             # (n_q,)
     if kl_control and len(delta_var_q) >= 10:
         slope, intercept = np.polyfit(kl_q, delta_var_q, 1)
         residuals = delta_var_q - (slope * kl_q + intercept)
         quintile_variances[q] = np.var(residuals)
     else:
         residuals = delta_var_q
         quintile_variances[q] = np.var(delta_var_q)
     if q == 0:
         q1_residuals = residuals
6. return {"quintile_variances": (5,), "q1_residuals": q1_residuals, ...}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | delta_var computation | delta (N,4) → delta_var (N,) via np.var axis=1 |
| L-4-2 | OLS residualization loop | per-quintile polyfit + residuals + var |

---

## A-6: Ablation Variants [Complexity: 10, Budget: 1 subtask]

### API Signatures

```python
def run_ablation_no_kl(
    base_logprobs: np.ndarray,    # (N, 4)
    aligned_logprobs: np.ndarray, # (N, 4)
    margin: np.ndarray,           # (N,)
    kl_div: np.ndarray,           # (N,) passed but not used
) -> dict:
    """Raw variance without KL residualization — ablation FR-5.2.

    Calls compute_variance_by_quintile with kl_control=False.
    Returns same structure as compute_variance_by_quintile.
    """
    ...

def run_isotropic_sanity_check(n: int = 1000, seed: int = 1) -> dict:
    """Gaussian delta control — expects flat quintile trend.

    Returns: {"quintile_variances": np.ndarray (5,), "is_flat": bool}
    """
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | No-KL ablation + isotropic sanity | kl_control=False call + synthetic Gaussian check |

---

## A-3: Quintile Stratification [Complexity: 9, Budget: 1 subtask]

### API Signatures

```python
def compute_quintile_labels(
    margin: np.ndarray,   # (N,) z-scored confidence margin from cache
    n_quintiles: int = 5,
) -> tuple[np.ndarray, np.ndarray]:
    """Stratify items by margin percentile.

    Returns: (quintile_labels (N,) in [0..n_quintiles-1], boundaries (n_quintiles+1,))
    """
    ...
```

Note: `margin` is already z-scored in H-E1 cache. No additional z-scoring needed — FR-2.1 is
satisfied by cache contents directly. Verify with `scipy.stats.zscore` only if cache margin is raw.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | np.digitize stratification + min-N check | boundaries + labels + count validation |

---

## A-12: Integration & Validation [Complexity: 12, Budget: 2 subtasks]

### API Signatures

```python
# run_analysis.py

def load_all_caches(
    model_pairs: list[dict],   # [{"pair_id": "pair2", "method": "DPO"}, ...]
    datasets: list[dict],      # [{"name": "mmlu", "n": 14042}, ...]
    cache_dir: str,            # path to h-e1/cache/
) -> dict:
    """Load all 6 pickle files.

    Returns: {pair_id: {dataset_name: cache_dict}} where cache_dict has
             base_logprobs (N,4), aligned_logprobs (N,4), margin (N,), kl_div (N,).
    """
    ...

def run_per_dataset_analysis(
    caches: dict,              # from load_all_caches
    n_quintiles: int = 5,
    n_bootstrap: int = 5000,
    seed: int = 1,
) -> dict:
    """Run compute_variance_by_quintile + test_method_quintile_interaction for all datasets.

    Returns: {dataset: {"dpo": variance_result, "sft": variance_result, "test": test_result}}
    """
    ...

def evaluate_gate(results: dict) -> dict:
    """Apply 2/3 benchmark criterion.

    Returns: {"gate_pass": bool, "n_significant": int, "per_dataset": dict}
    """
    ...

def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    """Check 4 indicators: stratification_ok, variance_computed, kl_controlled, test_executed.

    Returns: (all_pass: bool, indicators: dict)
    """
    ...

def main() -> None:
    """Entry: load caches → run analysis → visualize → evaluate gate → save results."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-12-1 | load_all_caches + validate | pickle load × 6 files + validate_cache calls |
| L-12-2 | run_per_dataset_analysis + gate eval | full pipeline + experiment_results.json write |

---

## Summary: Subtask Allocation

| Task | Subtasks | IDs |
|------|----------|-----|
| A-5 Statistical Testing | 4 | L-5-1, L-5-2, L-5-3, L-5-4 |
| A-4 KL-Residualized Variance | 2 | L-4-1, L-4-2 |
| A-6 Ablation Variants | 1 | L-6-1 |
| A-3 Quintile Stratification | 1 | L-3-1 |
| A-12 Integration | 2 | L-12-1, L-12-2 |
| **Total** | **10** | within budget |

---

*Generated by Phase 3 Logic Agent — H-M2 MECHANISM INCREMENTAL*
*Base hypothesis API verified from h-m1/code/analysis_anisotropy.py (actual implementation)*
*Key verified parameter names: compute_logit_delta(base_logprobs, aligned_logprobs), run_isotropic_sanity_check(n_items, seed)*
