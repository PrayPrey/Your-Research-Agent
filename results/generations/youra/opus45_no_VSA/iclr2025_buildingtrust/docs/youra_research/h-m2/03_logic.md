# Logic: H-M2 (Instruction-Tuning Effect on BSI & PC1,residual)

**Type**: MECHANISM

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1 referenced)
**Status**: `h-e1/code/` does not exist on disk (glob `h-e1/code/**` returned 0 files) — cannot verify actual API signatures. Re-implementing `residualize`/`fit_pca` from `h-e1/03_architecture.md` spec, per that doc's own External Dependencies note.
**Analyzed Path**: `h-e1/code/` (0 files found)
**Relevant Symbols**: None — no code to import; algorithm reused by spec only.

Applied: Standard OLS-residualization → PCA pattern (statsmodels + sklearn), paired-difference stats (scipy.stats.ttest_rel/wilcoxon). No relevant KB matches found for paired t-test pattern; using standard scipy API.

---

## A-3 (B-3): BSI Evaluator [Complexity: 9, Budget: 2 subtasks]

### API Signatures

```python
# src/bsi_evaluator.py
import pandas as pd
from torch import Tensor

def load_paws(cache_dir: str) -> pd.DataFrame:
    """Concat PAWS-Wiki test + PAWS-QQP dev. Cols: sentence1, sentence2, paraphrase_label"""
    ...

def paraphrase_prompt(pair: str, s1: str, s2: str, few_shot: bool = False) -> str:
    """Builds classification prompt. few_shot=True prepends 3 fixed examples."""
    ...

def classify_pair(model, tokenizer, s1: str, s2: str, few_shot: bool = False) -> int:
    """Greedy decode (temperature=0), parses 0/1 from generated text."""
    ...

def compute_bsi(model, tokenizer, paws_df: pd.DataFrame, few_shot: bool = False) -> float:
    """BSI = mean(pred(s1,s2) == pred(s2,s1)) over all rows."""
    ...

def evaluate_model_bsi(model_id: str, few_shot: bool = False) -> dict:
    """Loads model/tokenizer, returns {model_id, bsi, n_pairs}. Catches OOM/load errors -> returns {model_id, bsi: None, error: str}."""
    ...
```

### Pseudo-code (agreement scoring — non-trivial part)

```
for each row (s1, s2) in paws_df:
    pred_orig = classify_pair(model, tok, s1, s2, few_shot)      # order 1
    pred_swap = classify_pair(model, tok, s2, s1, few_shot)      # order 2 (paraphrase direction)
    agree = 1 if pred_orig == pred_swap else 0
BSI = mean(agree over all rows)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A3-1 | Prompting + classify_pair | `paraphrase_prompt`, `classify_pair` w/ greedy decode + regex/keyword parse of 0/1 |
| L-A3-2 | BSI aggregation + model eval wrapper | `compute_bsi` (paired-order agreement loop), `evaluate_model_bsi` (load/catch/return dict) |

---

## A-4 (B-4): PC1 Scorer [Complexity: 7]

### API Signatures

```python
# src/pc1_scorer.py
import numpy as np
import pandas as pd

BENCHMARKS = ["truthfulqa", "mmlu", "advglue", "bbh", "gsm8k", "winogrande"]
SEED = 42

def load_benchmark_scores(model_ids: list[str]) -> pd.DataFrame:
    """From Open LLM Leaderboard API. Cols: model_id, log_params, release_date, *BENCHMARKS.
    Raises ValueError listing missing models."""
    ...

def residualize(Y: np.ndarray, X: np.ndarray) -> np.ndarray:
    # Y: [N, 6] standardized benchmark scores, X: [N, 2] (log_params, release_date)
    """OLS residuals per benchmark column (statsmodels.OLS). Returns Y_resid [N, 6]."""
    ...

def compute_pc1(df: pd.DataFrame) -> pd.Series:
    """residualize(Y, X) -> sklearn PCA(n_components=1).fit_transform -> pd.Series indexed by model_id."""
    ...
```

Reuses H-E1 `residualize`/`fit_pca` algorithm (spec-level, no import — see Codebase Analysis).

---

## Reference Signatures (no dedicated subtasks — copy directly from architecture)

```python
# src/paired_analysis.py
def paired_deltas(base_vals: np.ndarray, instruct_vals: np.ndarray) -> np.ndarray: ...

def run_paired_ttest(base_vals: np.ndarray, instruct_vals: np.ndarray) -> dict:
    """Returns {t_stat, p_value, mean_delta, cohens_d}. Raises ValueError if N<2."""
    ...

def run_wilcoxon(base_vals: np.ndarray, instruct_vals: np.ndarray) -> dict:
    """Returns {stat, p_value}"""
    ...

def delta_correlation(delta_bsi: np.ndarray, delta_pc1: np.ndarray) -> dict:
    """Returns {pearson_r, p_value}"""
    ...

# src/run_experiment.py
def main() -> dict:
    """Loads model_pairs.yaml, runs BSI+PC1 for 32 models (base few_shot=True per FR-5),
    runs paired_analysis, writes results/*.csv + results/statistical_results.json"""
    ...
```

### Tensor/Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| Y | [N=32, 6] | standardized benchmark scores |
| X | [N=32, 2] | log_params, release_date |
| Y_resid | [N=32, 6] | OLS residuals |
| pc1_scores | [N=32] | pd.Series, index=model_id |
| base_vals / instruct_vals | [16] | paired arrays for ttest/wilcoxon |

---

## External Dependencies (Base Hypothesis)

No importable code exists at `h-e1/code/`. `pc1_scorer.residualize`/`compute_pc1` re-implement the algorithm documented in `h-e1/03_architecture.md` (`analysis.residualize`, `analysis.fit_pca`) directly rather than importing. If `h-e1/code/analysis.py` is added later, replace these two function bodies with imports.
