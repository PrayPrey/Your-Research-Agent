# Logic Design: h-e1
# Global k-th Percentile Threshold Disparity Analysis

**Date:** 2026-07-30
**Phase:** 3 — Logic Design
**Script:** `code/run_h_e1.py` (single-file, CPU-only)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: load_or_cache_dataset [Complexity: 2, Budget: 2]

**Applied**: Standard pandas/HuggingFace cache pattern

### API Signatures

```python
def load_or_cache_dataset(cache_path: str) -> pd.DataFrame:
    """Load RedPajama-V2 sample, cache as parquet. Returns (N, 2) DataFrame."""
    ...
```

### Pseudo-code

```
1. if Path(cache_path).exists():
       return pd.read_parquet(cache_path)

2. ds = load_dataset("togethercomputer/RedPajama-Data-V2", name="sample", split="train")

3. rows = []
   for doc in ds:
       signals = json.loads(doc["quality_signals"])
       ppl = signals["ccnet_perplexity"][0][2]   # (start, end, value)[0][2]
       lang = doc["language"]
       rows.append({"language": lang, "ccnet_perplexity": ppl})

4. df = pd.DataFrame(rows)                        # shape: (N, 2)
   df = df.dropna(subset=["ccnet_perplexity"])

5. assert len(df) > 190_000, f"Only {len(df)} rows"
   assert df["language"].nunique() == 5, "Expected 5 languages"

6. df.to_parquet(cache_path, index=False)
   return df
```

### Tensor/DataFrame Shapes

| Variable | Shape | Columns |
|----------|-------|---------|
| df (output) | (N, 2) | language: str, ccnet_perplexity: float |
| N | ~208,263 | after dropna |

---

## A-2: compute_global_threshold_disparity [Complexity: 3, Budget: 3]

**Applied**: Standard pandas/scipy statistical pipeline

### API Signatures

```python
def compute_global_threshold_disparity(
    df: pd.DataFrame,          # (N, 2): language, ccnet_perplexity
    k_values: list[int],       # e.g. [10, 20, 30, 40, 50]
) -> dict:
    """Compute Cramér's V and per-lang retention for each k. Applies Holm-Bonferroni."""
    ...
```

### Pseudo-code

```
1. languages = sorted(df['language'].unique())   # ['de', 'en', 'es', 'fr', 'it']
   results = {}

2. for k in k_values:
       threshold = df['ccnet_perplexity'].quantile(k / 100)   # scalar float

       retained = (df['ccnet_perplexity'] < threshold).astype(int)
       df_k = df.assign(retained=retained)

       # contingency table shape: (5, 2) — rows=languages, cols=[0=excluded, 1=retained]
       contingency = pd.crosstab(df_k['language'], df_k['retained'])

       v = association(contingency.values, method='cramer')   # float in [0,1]
       chi2, p, _, _ = chi2_contingency(contingency.values)

       retention_rates = (
           df_k.groupby('language')['retained'].mean()
           .reindex(languages)
           .to_dict()
       )  # {'de': 0.xx, 'en': 0.xx, ...}

       results[k] = {
           'threshold': threshold,
           'cramers_v': v,
           'chi2': chi2,
           'p_value': p,
           'retention_rates': retention_rates,
       }

3. # Holm-Bonferroni across 5 p-values
   p_vals = [results[k]['p_value'] for k in k_values]
   _, p_holm, _, _ = multipletests(p_vals, method='holm')
   for i, k in enumerate(k_values):
       results[k]['p_holm'] = p_holm[i]

4. return results
```

### Output Structure

```python
results = {
    10: {
        'threshold': float,
        'cramers_v': float,          # target: ~0.29
        'chi2': float,
        'p_value': float,
        'p_holm': float,             # Holm-corrected
        'retention_rates': {         # per-language mean retention
            'de': float, 'en': float, 'es': float, 'fr': float, 'it': float
        }
    },
    # ... keys 20, 30, 40, 50
}
```

---

## A-3: verify_gate [Complexity: 1, Budget: 1]

**Applied**: Standard Python

### API Signatures

```python
def verify_gate(
    df: pd.DataFrame,
    results: dict,
    k_values: list[int],
) -> tuple[bool, dict]:
    """Check 4 gate conditions. Returns (gate_passed, indicators)."""
    ...
```

### Pseudo-code

```
indicators = {
    "row_count_ok":     len(df) > 190_000,
    "language_count_ok": df['language'].nunique() == 5,
    "nan_rate_ok":      df['ccnet_perplexity'].isna().mean() < 0.01,
    "cramers_v_in_range": all(
        0.29 <= results[k]['cramers_v'] <= 0.45 for k in k_values
    ),
}
gate_passed = all(indicators.values())
return gate_passed, indicators
```

---

## A-4: generate_figures [Complexity: 2, Budget: 2]

**Applied**: Standard matplotlib/seaborn

### API Signatures

```python
def generate_figures(
    df: pd.DataFrame,
    results: dict,
    k_values: list[int],
    output_dir: str,            # "docs/youra_research/h-e1/figures"
) -> None:
    """Write 4 PNG figures to output_dir."""
    ...
```

### Figure Logic

```
Path(output_dir).mkdir(parents=True, exist_ok=True)

# 1. cramers_v_bar.png
#    x: k_values, y: cramers_v per k
#    bar color: green if 0.29 <= v <= 0.41 else red
#    hlines at y=0.29 (lower bound) and y=0.41 (upper bound)

# 2. retention_heatmap.png
#    pivot: rows=languages, cols=k_values, values=retention_rates
#    seaborn heatmap with annot=True, fmt=".2f", cmap="YlOrRd"

# 3. perplexity_kde.png
#    for each language: seaborn kdeplot of ccnet_perplexity
#    log-scale x-axis (perplexity spans wide range)
#    legend with language labels

# 4. retention_gap.png
#    x: k_values
#    y: max(retention_rates.values()) - min(retention_rates.values()) per k
#    line + markers; ylabel "Max-Min Retention Gap (pp)"
```

---

## A-5: main [Complexity: 1, Budget: 1]

**Applied**: Standard Python

### API Signatures

```python
def main() -> None:
    """Orchestrate load → analyze → gate → figures → write outputs."""
    ...
```

### Pseudo-code

```
CACHE_PATH  = "docs/youra_research/redpajama_sample.parquet"
OUTPUT_DIR  = "docs/youra_research/h-e1"
FIGURES_DIR = f"{OUTPUT_DIR}/figures"
K_VALUES    = [10, 20, 30, 40, 50]

1. df = load_or_cache_dataset(CACHE_PATH)
   print(f"Loaded {len(df)} rows, {df['language'].nunique()} languages")

2. results = compute_global_threshold_disparity(df, K_VALUES)

3. gate_passed, indicators = verify_gate(df, results, K_VALUES)

4. generate_figures(df, results, K_VALUES, FIGURES_DIR)

5. # Serialize results: convert numpy floats to Python float for JSON
   results_json = {
       str(k): {
           **{key: float(val) if isinstance(val, (np.floating,)) else val
              for key, val in v.items()
              if key != 'retention_rates'},
           'retention_rates': {lang: float(r) for lang, r in v['retention_rates'].items()}
       }
       for k, v in results.items()
   }
   Path(f"{OUTPUT_DIR}/results.json").write_text(json.dumps(results_json, indent=2))
   Path(f"{OUTPUT_DIR}/gate_verdict.json").write_text(
       json.dumps({"gate_passed": gate_passed, "indicators": indicators}, indent=2)
   )

   print(f"Gate passed: {gate_passed}")
   sys.exit(0 if gate_passed else 1)


if __name__ == "__main__":
    main()
```

---

## Subtask Summary [9/9 used]

| ID | Function | Description |
|----|----------|-------------|
| L-1-1 | load_or_cache_dataset | Parquet cache check + HF load |
| L-1-2 | load_or_cache_dataset | quality_signals JSON parse + dropna |
| L-2-1 | compute_global_threshold_disparity | Per-k threshold + contingency table |
| L-2-2 | compute_global_threshold_disparity | Cramér's V + chi2 per k |
| L-2-3 | compute_global_threshold_disparity | Holm-Bonferroni across 5 p-values |
| L-3-1 | verify_gate | 4-condition gate check |
| L-4-1 | generate_figures | cramers_v_bar + retention_heatmap |
| L-4-2 | generate_figures | perplexity_kde + retention_gap |
| L-5-1 | main | Orchestration + JSON output |

---

## Key Imports (for Phase 4)

```python
import json, sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datasets import load_dataset
from scipy.stats import chi2_contingency
from scipy.stats.contingency import association
from statsmodels.stats.multitest import multipletests
```
