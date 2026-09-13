# Logic Design: H-M1

**Hypothesis**: PC1,residual correlates positively with BSI (ρ > 0, p < 0.05)
**Type**: MECHANISM (not PoC/EXISTENCE) — full pipeline required.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: API signatures verified from actual H-E1 code (NOT `03_prd.md`/brief specs, which reference a nonexistent `pc1_scores.csv`)
**Analyzed Path**: `docs/youra_research/h-e1/code/analysis.py`, `docs/youra_research/h-e1/outputs/`
**Relevant Symbols**: `fit_pca`, `residualize` (h-e1/code/analysis.py); outputs `residualized_matrix.csv`, `h_e1_results.json`

**⚠️ Deviation from spec**: PRD/brief assume `h-e1/results/pc1_scores.csv` with column `pc1_score` exists. It does **not**. H-E1 only persisted:
- `residualized_matrix.csv`: rows=model_name (index), cols=benchmark residuals `[IFEval, BBH, MATH Lvl 5, GPQA, MUSR, MMLU-PRO]`
- `h_e1_results.json` → `pca.loadings_pc1`: dict `{benchmark: loading}` (PC1 eigenvector, unit norm, sklearn `PCA.components_[0]`)

**H-M1 must derive per-model PC1 scores**: `pc1_scores = Y_resid @ loadings_pc1_vector`. This is standard PCA projection (sklearn `PCA.transform` semantics) and introduces no data leakage (loadings are fixed/frozen from H-E1, not refit).

---

## A-1: Load H-E1 Artifacts and Derive PC1 Scores [Complexity: 2, Budget: 2]

**Applied**: Standard PCA projection (sklearn convention)

### API Signatures

```python
import pandas as pd
import numpy as np
import json

def load_pc1_scores(
    resid_csv: str = "../h-e1/outputs/residualized_matrix.csv",
    results_json: str = "../h-e1/outputs/h_e1_results.json",
) -> pd.DataFrame:
    """Derive PC1 scores via projection. Returns df[model_name, pc1_score]."""
    ...
```

### Pseudo-code

```
1. Y_resid_df = pd.read_csv(resid_csv, index_col=0)   # [M, 6], index=model_name
2. results = json.load(results_json)
3. loadings = np.array([results["pca"]["loadings_pc1"][b] for b in Y_resid_df.columns])  # [6]
4. pc1_scores = Y_resid_df.values @ loadings          # [M]  (projection, matches PCA.transform)
5. sign-check: if loadings sum negative-dominant, flip sign so higher PC1 = better (loadings are
   all positive per H-E1, 0.35-0.44, so no flip needed — assert this)
6. return DataFrame({model_name: Y_resid_df.index, pc1_score: pc1_scores})
```

### Edge Cases
- Missing `residualized_matrix.csv` or json key → raise `FileNotFoundError`/`KeyError` with explicit path, do not silently skip.
- `assert all(loadings > 0)`, else log warning (sign flip would invert correlation direction).

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | load_pc1_scores | Read H-E1 outputs, project residuals onto PC1 loadings |
| L-1-2 | schema validation | Assert no NaN, loadings positive, M ≥ 30 |

---

## A-2: Paraphrase Inference (PAWS + QQP) [Complexity: 4, Budget: 5]

**Applied**: HF `datasets` + zero-shot prompt classification (no training)

### API Signatures

```python
from datasets import load_dataset
from typing import Literal

def load_paraphrase_datasets() -> tuple["Dataset", "Dataset"]:
    """Returns (paws_test, qqp_val). paws: sentence1/sentence2/label. qqp: question1/question2/label."""
    ...

def build_prompt(s1: str, s2: str) -> str:
    """"[s1] [SEP] [s2] -> paraphrase:" """
    ...

def run_inference(
    model_name: str,
    pairs: list[tuple[str, str]],
    batch_size: int = 32,
    max_length: int = 256,
    seed: int = 42,
) -> np.ndarray:
    """Binary predictions. Returns preds: [N] int array, values in {0,1}."""
    ...

def compute_accuracy(preds: np.ndarray, labels: np.ndarray) -> float:
    """preds, labels: [N] -> scalar acc in [0,1]."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| paws pairs | [8000] tuples | (sentence1, sentence2) |
| qqp pairs | [40430] tuples | (question1, question2) |
| preds | [N] | int {0,1}, N=8000 or 40430 |
| labels | [N] | ground truth, same dtype |

### Pseudo-code (inference loop, non-trivial due to parsing yes/no from LLM output)

```
1. for batch in batches(pairs, batch_size):
2.     prompts = [build_prompt(s1, s2) for s1, s2 in batch]
3.     raw_outputs = model.generate(prompts, max_new_tokens=5, do_sample=False, seed=seed)
4.     preds_batch = [parse_yes_no(o) for o in raw_outputs]
5.     append to preds
6. return np.array(preds)

parse_yes_no(text: str) -> int:
    text = text.strip().lower()
    if text.startswith("yes"): return 1
    if text.startswith("no"): return 0
    return 0  # fallback: unparseable = treat as "no" (conservative), log warning count
```

### Edge Cases
- Empty/malformed model output → fallback to 0, increment `unparseable_count`; if `unparseable_count / N > 0.1`, flag model as unreliable (exclude from BSI, log to `h-m1/results/excluded_models.txt`).
- Truncation at `max_length=256` tokens — sentences exceeding limit are truncated, not dropped (deterministic tokenizer truncation).
- If a model errors entirely on a dataset (OOM, API failure) → mark BSI as NaN for that model, exclude from correlation (do not impute).

### Subtasks [3/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | load_paraphrase_datasets | HF datasets loader for PAWS labeled_final test + QQP validation |
| L-2-2 | run_inference | Batched generation + yes/no parsing, seed=42 |
| L-2-3 | compute_accuracy | Vectorized accuracy per dataset |

---

## A-3: BSI Computation and Correlation Analysis [Complexity: 3, Budget: 3]

**Applied**: Standard PoC pattern — Pearson r + Fisher z CI

### API Signatures

```python
def compute_bsi(paws_acc: float, qqp_acc: float) -> float:
    """Geometric mean. Both in [0,1] -> bsi in [0,1]."""
    return float(np.sqrt(max(paws_acc, 0.0) * max(qqp_acc, 0.0)))

def fisher_z_ci(rho: float, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """95% CI for Pearson rho via Fisher z-transform."""
    ...

def run_correlation_analysis(
    pc1_scores: np.ndarray, bsi_scores: np.ndarray
) -> dict:
    """pc1_scores, bsi_scores: [M] aligned by model_name (inner join, drop NaN).
    Returns {rho, p_value, ci_lower, ci_upper, n}."""
    ...
```

### Pseudo-code

```
compute_bsi:
1. assert 0 <= paws_acc <= 1 and 0 <= qqp_acc <= 1
2. return sqrt(paws_acc * qqp_acc)

fisher_z_ci:
1. z = arctanh(rho)                    # undefined at rho=+-1, clip rho to [-0.9999, 0.9999]
2. se = 1 / sqrt(n - 3)                # requires n > 3
3. lo, hi = tanh(z - 1.96*se), tanh(z + 1.96*se)
4. return lo, hi

run_correlation_analysis:
1. df = inner_join(pc1_df, bsi_df, on="model_name")   # [M', 2], drop rows with NaN either side
2. assert len(df) >= 30, "Sample size < 30 models required by PRD"
3. rho, p_value = scipy.stats.pearsonr(df.pc1_score, df.bsi_score)
4. ci_lower, ci_upper = fisher_z_ci(rho, len(df))
5. return {rho, p_value, ci_lower, ci_upper, n: len(df)}
```

### Verification Checks (mechanism gate, run before reporting result)

```python
def verify_bsi_mechanism(pc1_scores: np.ndarray, bsi_scores: np.ndarray, min_samples: int = 30) -> tuple[bool, str]:
    """Pre-flight checks. Returns (passed, reason)."""
    if len(pc1_scores) < min_samples:
        return False, f"Insufficient samples: {len(pc1_scores)} < {min_samples}"
    if np.std(pc1_scores) < 1e-6:
        return False, "No variance in PC1 scores"
    if np.std(bsi_scores) < 1e-6:
        return False, "No variance in BSI scores"
    if np.any(~np.isfinite(pc1_scores)) or np.any(~np.isfinite(bsi_scores)):
        return False, "NaN or Inf detected"
    return True, "OK"
```

Gate verdict logic (mirrors H-E1 `main()` pattern):
```
success_criteria = {
    "rho_positive": rho > 0,
    "p_lt_0.05": p_value < 0.05,
    "ci_excludes_zero": ci_lower > 0,
    "n_gte_30": n >= 30,
}
gate_verdict = "PASS" if all(success_criteria.values()) else "FAIL"
```

### Edge Cases
- `n <= 3` → `fisher_z_ci` divide-by-zero; guard with explicit check, raise `ValueError`.
- `rho` exactly ±1 (degenerate, unlikely with real data) → clip before `arctanh`.
- Model present in H-E1 but missing from paraphrase inference results (failed inference) → excluded via inner join, logged to `excluded_models.txt` with reason.

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | compute_bsi + fisher_z_ci | Pure functions, unit-testable |
| L-3-2 | run_correlation_analysis | Join, pearsonr, CI, sample-size assert |
| L-3-3 | verify_bsi_mechanism + gate_verdict | Pre-flight + PRD success criteria to JSON |

---

## A-4: Output Artifacts and Visualization [Complexity: 2, Budget: 2]

**Applied**: Standard matplotlib scatter + regression (no KB pattern needed)

### API Signatures

```python
def save_results(
    bsi_df: pd.DataFrame,          # model_name, paws_acc, qqp_acc, bsi_score
    corr_result: dict,             # rho, p_value, ci_lower, ci_upper, n
    output_dir: str = "h-m1/results",
) -> None: ...

def plot_pc1_vs_bsi(
    pc1_scores: np.ndarray, bsi_scores: np.ndarray, corr_result: dict,
    out_path: str = "h-m1/figures/pc1_vs_bsi_scatter.png",
) -> None:
    """Scatter + OLS regression line + rho/p annotation."""
    ...
```

### Pseudo-code

```
save_results:
1. bsi_df.to_csv(f"{output_dir}/bsi_scores.csv", index=False)
2. json.dump(corr_result, open(f"{output_dir}/correlation_results.json", "w"), indent=2)

plot_pc1_vs_bsi:
1. scatter(pc1_scores, bsi_scores)
2. slope, intercept = np.polyfit(pc1_scores, bsi_scores, 1)
3. plot regression line over x-range
4. annotate: f"rho={rho:.3f}, p={p_value:.4f}, n={n}"
5. savefig(out_path, dpi=150)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | save_results | Write CSV + correlation JSON |
| L-4-2 | plot_pc1_vs_bsi | Scatter + regression + annotation figure |

---

## External Dependencies (Base Hypothesis: H-E1)

```python
# From: docs/youra_research/h-e1/code/analysis.py (ACTUAL CODE)
def fit_pca(Y_resid: np.ndarray) -> dict:
    """Returns dict with keys: eigenvalues, variance_ratio, loadings_pc1 (list[float], len=6),
    lambda_1, variance_explained_pc1."""
    ...
```

**Verified from**: `docs/youra_research/h-e1/code/analysis.py` and `docs/youra_research/h-e1/outputs/` (actual run artifacts, not `03_prd.md`/brief which reference a nonexistent `pc1_scores.csv`).

**Consumption pattern for H-M1**: Do not call `fit_pca` again (would refit PCA — leakage risk / non-determinism). Instead read frozen `loadings_pc1` from `h_e1_results.json` and project `residualized_matrix.csv` (see A-1).
