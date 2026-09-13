# Logic: h-e1-v3
# Global Percentile Threshold Language Retention Disparity Analysis

Applied: custom design — KB returned irrelevant vision/GPU/diffusion content (similarity 0.37–0.44, all unrelated)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — Serena skipped (no existing code to analyze)
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation; h-e1 archive explicitly excluded per 02c_experiment_brief.md

---

## A-2: Statistical Analysis [Complexity: 11, Budget: 2 subtasks]

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | analysis.py full API | compute_disparity, apply_holm, verify_mechanism_activated |
| L-2-2 | data_loader.py full API | load, _validate, _download_and_cache |

---

## L-2-1: analysis.py

### API Signatures

```python
# code/analysis.py
import pandas as pd
import numpy as np
from scipy.stats.contingency import association
from scipy.stats import chi2_contingency
from statsmodels.stats.multitest import multipletests
from typing import Tuple

K_VALUES: list[int] = [10, 20, 30, 40, 50]
LANGUAGES: list[str] = ["de", "en", "es", "fr", "it"]


def compute_disparity(
    df: pd.DataFrame,           # (N, 2) cols: ['language', 'ccnet_perplexity']
    k_values: list[int] = K_VALUES,
) -> dict[int, dict]:
    """Compute global threshold disparity for each k. No Holm correction applied here."""
    ...


def apply_holm(
    results: dict[int, dict],   # output of compute_disparity
    k_values: list[int] = K_VALUES,
) -> dict[int, dict]:
    """Add 'p_holm' key to each results[k]. Mutates and returns results."""
    ...


def verify_mechanism_activated(
    df: pd.DataFrame,
    results: dict[int, dict],   # must have 'cramers_v' per k (after apply_holm)
    k_values: list[int] = K_VALUES,
) -> Tuple[bool, dict[str, bool]]:
    """Return (activated, indicators) — 5 boolean checks."""
    ...
```

### Return Types

`compute_disparity` returns:
```python
{
    10: {
        "threshold": float,
        "cramers_v": float,
        "chi2": float,
        "p_value": float,
        "retention_rates": {"de": float, "en": float, "es": float, "fr": float, "it": float},
        "max_min_gap": float,
    },
    # ... same for 20, 30, 40, 50
}
```

`verify_mechanism_activated` returns:
```python
(
    bool,  # True iff all 5 indicators are True
    {
        "data_loaded": bool,        # len(df) >= 190_000
        "five_languages": bool,     # df['language'].nunique() == 5
        "no_nan_perplexity": bool,  # df['ccnet_perplexity'].isna().mean() < 0.01
        "disparity_nonzero": bool,  # all(results[k]['cramers_v'] > 0.10 for k in k_values)
        "disparity_in_range": bool, # all(0.29 <= results[k]['cramers_v'] <= 0.45 for k in k_values)
    }
)
```

### Pseudo-code

```
compute_disparity(df, k_values):
    results = {}
    for k in k_values:
        threshold = df['ccnet_perplexity'].quantile(k / 100)
        retained  = (df['ccnet_perplexity'] < threshold).astype(int)  # [N]
        contingency = pd.crosstab(df['language'], retained)            # (5, 2)
        v    = association(contingency.values, method='cramer')        # float
        chi2, p, _, _ = chi2_contingency(contingency.values)
        rates = df.assign(retained=retained).groupby('language')['retained'].mean()
        results[k] = {
            "threshold": threshold,
            "cramers_v": round(v, 4),
            "chi2": round(chi2, 2),
            "p_value": p,
            "retention_rates": rates.reindex(LANGUAGES).to_dict(),
            "max_min_gap": float(rates.max() - rates.min()),
        }
    return results

apply_holm(results, k_values):
    p_values = [results[k]['p_value'] for k in k_values]
    _, p_holm, _, _ = multipletests(p_values, method='holm')
    for i, k in enumerate(k_values):
        results[k]['p_holm'] = float(p_holm[i])
    return results

verify_mechanism_activated(df, results, k_values):
    indicators = {
        "data_loaded":        len(df) >= 190_000,
        "five_languages":     df['language'].nunique() == 5,
        "no_nan_perplexity":  df['ccnet_perplexity'].isna().mean() < 0.01,
        "disparity_nonzero":  all(results[k]['cramers_v'] > 0.10 for k in k_values),
        "disparity_in_range": all(0.29 <= results[k]['cramers_v'] <= 0.45 for k in k_values),
    }
    return all(indicators.values()), indicators
```

---

## L-2-2: data_loader.py

### API Signatures

```python
# code/data_loader.py
import json
import os
import pandas as pd
from pathlib import Path

CACHE_PATH: str = "docs/youra_research/redpajama_sample.parquet"
REQUIRED_COLS: list[str] = ["language", "ccnet_perplexity"]
MIN_ROWS: int = 190_000


def load(cache_path: str = CACHE_PATH) -> pd.DataFrame:
    """Return df with columns ['language', 'ccnet_perplexity'].
    Uses Parquet cache if valid; falls back to HuggingFace download.
    Raises AssertionError on validation failure."""
    ...


def _validate(df: pd.DataFrame) -> None:
    """Assert row count, language count, NaN rate. Raises AssertionError."""
    ...


def _download_and_cache(cache_path: str) -> pd.DataFrame:
    """Download RedPajama-V2 sample, extract fields, save Parquet, return df."""
    ...
```

### Pseudo-code

```
load(cache_path):
    p = Path(cache_path)
    if p.exists():
        df = pd.read_parquet(p)
        if len(df) >= MIN_ROWS and all(c in df.columns for c in REQUIRED_COLS):
            _validate(df)
            print(f"Cache hit: {len(df)} rows, {df['language'].nunique()} languages")
            return df[REQUIRED_COLS]
        else:
            print("Cache invalid (row count or columns missing) — re-downloading")
    return _download_and_cache(cache_path)

_validate(df):
    assert len(df) >= MIN_ROWS, f"Expected >= {MIN_ROWS} rows, got {len(df)}"
    assert df['language'].nunique() == 5, \
        f"Expected 5 languages, got {df['language'].nunique()}: {df['language'].unique()}"
    nan_rate = df['ccnet_perplexity'].isna().mean()
    assert nan_rate < 0.01, f"NaN rate {nan_rate:.3%} >= 1%"

_download_and_cache(cache_path):
    from datasets import load_dataset
    ds = load_dataset("togethercomputer/RedPajama-Data-V2", name="sample")
    split = ds["train"]  # sample split loads as 'train'

    records = []
    for sample in split:
        try:
            signals  = json.loads(sample["quality_signals"])
            perp     = signals["ccnet_perplexity"][0][2]   # (start, end, score)[2]
            lang     = json.loads(sample["meta"])["language"]
            if perp is not None:
                records.append({"language": lang, "ccnet_perplexity": float(perp)})
        except (KeyError, IndexError, json.JSONDecodeError):
            continue  # skip malformed rows

    df = pd.DataFrame(records)
    Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache_path, index=False)
    print(f"Downloaded and cached: {len(df)} rows → {cache_path}")
    _validate(df)
    return df
```

---

## reporter.py

### API Signatures

```python
# code/reporter.py
import json
from pathlib import Path
from typing import Tuple

RESULTS_DIR: str = "docs/youra_research/h-e1-v3"
V_LO: float = 0.29
V_HI: float = 0.41
P_THRESH: float = 0.001


def check_gate(
    results: dict[int, dict],   # must contain 'cramers_v' and 'p_holm' per k
    k_values: list[int],
) -> Tuple[bool, str]:
    """Evaluate gate. Returns (passed, message) where message describes which condition failed."""
    ...


def write_results(
    results: dict[int, dict],
    k_values: list[int],
    gate_passed: bool,
    out_dir: str = RESULTS_DIR,
) -> None:
    """Write results.json (FR-4.1) and experiment_results.json (FR-4.2)."""
    ...
```

### Pseudo-code

```
check_gate(results, k_values):
    cond_a = all(V_LO <= results[k]['cramers_v'] <= V_HI for k in k_values)
    cond_b = all(results[k]['p_holm'] < P_THRESH for k in k_values)
    passed = cond_a and cond_b
    if passed:
        msg = "GATE: PASS — all V ∈ [0.29, 0.41] and all Holm-p < 0.001"
    else:
        parts = []
        if not cond_a:
            parts.append(f"Condition A FAIL: V = {[results[k]['cramers_v'] for k in k_values]}")
        if not cond_b:
            parts.append(f"Condition B FAIL: p_holm = {[results[k]['p_holm'] for k in k_values]}")
        msg = "GATE: FAIL — " + "; ".join(parts)
    return passed, msg

write_results(results, k_values, gate_passed, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # FR-4.1: results.json
    payload = {
        "hypothesis_id": "h-e1-v3",
        "gate_result": "PASS" if gate_passed else "FAIL",
        "k_values": k_values,
        "results": {
            str(k): {
                **results[k],
                "retention_rates": results[k]["retention_rates"],  # already dict
            }
            for k in k_values
        }
    }
    (out / "results.json").write_text(json.dumps(payload, indent=2))

    # FR-4.2: experiment_results.json
    exp = {
        "hypothesis_id": "h-e1-v3",
        "status": "COMPLETED",
        "gate_passed": gate_passed,
        "primary_metric": "cramers_v",
        "results_by_k": {str(k): results[k] for k in k_values},
    }
    (out / "experiment_results.json").write_text(json.dumps(exp, indent=2))
```

---

## run_h_e1_v3.py

### API Signature

```python
# code/run_h_e1_v3.py
import sys
import matplotlib
matplotlib.use("Agg")  # CPU-only, no display

import data_loader
import analysis
import visualization
import reporter

K_VALUES = [10, 20, 30, 40, 50]


def main() -> None:
    """Full pipeline: load → analyze → visualize → report → gate."""
    ...


if __name__ == "__main__":
    main()
```

### Pseudo-code

```
main():
    # 1. Load data
    df = data_loader.load()
    print(f"Loaded {len(df)} rows, {df['language'].nunique()} languages")

    # 2. Statistical analysis
    results = analysis.compute_disparity(df, K_VALUES)
    results = analysis.apply_holm(results, K_VALUES)

    # 3. Mechanism verification (log only, does not block)
    activated, indicators = analysis.verify_mechanism_activated(df, results, K_VALUES)
    print(f"Mechanism activated: {activated}")
    for name, val in indicators.items():
        print(f"  {name}: {val}")

    # 4. Visualization
    figures_dir = "docs/youra_research/h-e1-v3/figures"
    visualization.plot_gate_metrics(results, K_VALUES, figures_dir)
    visualization.plot_retention_heatmap(df, results, K_VALUES, figures_dir)
    visualization.plot_perplexity_kde(df, figures_dir)
    visualization.plot_gap_vs_k(results, K_VALUES, figures_dir)

    # 5. Gate check
    gate_passed, gate_msg = reporter.check_gate(results, K_VALUES)
    print(gate_msg)

    # 6. Write outputs
    reporter.write_results(results, K_VALUES, gate_passed)

    # 7. Exit code signals gate outcome to harness
    sys.exit(0 if gate_passed else 1)
```

---

*h-e1-v3 | Phase 3 Logic | 2026-07-30*
