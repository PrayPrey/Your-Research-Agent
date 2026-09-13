# Logic Design: h-e1-v3-v4
# Global k-th Percentile Threshold Disparity Analysis (Updated Gate)

**Date:** 2026-07-30
**Phase:** 3 — Logic Design
**Script:** `code/run_experiment.py` (single-file, CPU-only)
**Diff from h-e1:** GATE_V_MIN=0.40, GATE_V_MAX=0.57; output paths → h-e1-v3-v4; add verify_mechanism_activated()

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: API signatures verified from actual base code
**Analyzed Path**: `docs/youra_research/h-e1/code/run_h_e1.py`
**Relevant Symbols**:
- `analyze_thresholds(df, k_values)` — lines 177–216: per-k quantile, crosstab, Cramér's V, chi2, Holm (embedded)
- `check_gate(df, results, k_values)` — lines 221–234: returns `dict` (not tuple), 5 conditions, `bool()` casts
- `plot_figures(df, results, k_values)` — lines 239–299: uses module-level `FIGURES_DIR`, hlines at 0.29/0.41

**Critical findings from actual code:**
- `check_gate` returns `{"gate_passed": bool, "indicators": dict}` — NOT `tuple[bool, dict]` (spec was wrong)
- `plot_figures` takes no `figures_dir` param — uses module-level `FIGURES_DIR` constant
- Holm correction is embedded in `analyze_thresholds` in h-e1; split into `apply_holm_correction` for v3-v4 is optional (coder may inline)
- `association(contingency.values, method='cramer')` — `.values` required, not DataFrame

---

## External Dependencies (Base Hypothesis h-e1)

```python
# From: docs/youra_research/h-e1/code/run_h_e1.py (ACTUAL CODE — verified)

def analyze_thresholds(df: pd.DataFrame, k_values: list[int] = K_VALUES) -> dict:
    # returns {k_int: {threshold, cramers_v, chi2, p_value, retention_rates, p_holm}}

def check_gate(df: pd.DataFrame, results: dict, k_values: list[int] = K_VALUES) -> dict:
    # returns {"gate_passed": bool, "indicators": dict}  ← dict, NOT tuple
    # h-e1 uses 0.29/0.45 V bounds — h-e1-v3-v4 changes to 0.40/0.57

def plot_figures(df: pd.DataFrame, results: dict, k_values: list[int] = K_VALUES) -> None:
    # uses module-level FIGURES_DIR — no figures_dir parameter
    # h-e1 uses 0.29/0.41 hlines — h-e1-v3-v4 uses 0.40/0.57
```

**Verified from**: `docs/youra_research/h-e1/code/run_h_e1.py` (actual implementation, NOT spec)

---

## A-3: Statistical Analysis [Complexity: 10, Budget: 4]

**Applied**: Standard pandas/scipy statistical pipeline (h-e1 proven)

### L-3-1: analyze_thresholds()

#### API Signature

```python
def analyze_thresholds(df: pd.DataFrame, k_values: list[int] = K_VALUES) -> dict:
    """Per-k: global quantile, 5x2 crosstab, Cramér's V, chi2, retention rates."""
    ...
```

#### Pseudo-code

```
languages = sorted(df['language'].unique())   # ['de', 'en', 'es', 'fr', 'it']
results = {}

for k in k_values:
    threshold = df['ccnet_perplexity'].quantile(k / 100)          # scalar float
    retained  = (df['ccnet_perplexity'] < threshold).astype(int)  # 0=excluded, 1=retained
    df_k      = df.assign(retained=retained)

    contingency = pd.crosstab(df_k['language'], df_k['retained'])
    for col in [0, 1]:                    # guard: ensure both columns present
        if col not in contingency.columns:
            contingency[col] = 0
    contingency = contingency[[0, 1]]     # shape: (5, 2)

    v              = association(contingency.values, method='cramer')  # .values required
    chi2, p, _, _  = chi2_contingency(contingency.values)

    retention_rates = (
        df_k.groupby('language')['retained'].mean()
        .reindex(languages)
        .to_dict()
    )

    results[k] = {
        'threshold':       float(threshold),
        'cramers_v':       float(v),
        'chi2':            float(chi2),
        'p_value':         float(p),
        'retention_rates': {lang: float(r) for lang, r in retention_rates.items()},
    }

return results
```

#### DataFrame Shapes

| Variable | Shape | Note |
|----------|-------|------|
| df | (N, 2) | language: str, ccnet_perplexity: float; N ~208k |
| contingency | (5, 2) | rows=languages, cols=[excluded=0, retained=1] |
| retention_rates | dict[str, float] | 5 language keys |

---

### L-3-2: apply_holm_correction()

#### API Signature

```python
def apply_holm_correction(results: dict, k_values: list[int] = K_VALUES) -> dict:
    """Attach p_holm (float) to each k entry. Mutates results in-place, returns it."""
    ...
```

#### Pseudo-code

```
p_vals = [results[k]['p_value'] for k in k_values]   # list of 5 raw p-values
_, p_holm, _, _ = multipletests(p_vals, method='holm')
for i, k in enumerate(k_values):
    results[k]['p_holm'] = float(p_holm[i])           # float() to avoid numpy.float64
return results
```

**Note**: In h-e1, Holm correction is embedded inside `analyze_thresholds`. Coder may inline
`apply_holm_correction` logic at the end of `analyze_thresholds` — both are correct. The
`float()` cast is mandatory for JSON serialization.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | analyze_thresholds | Per-k quantile → crosstab(5×2) → Cramér's V + chi2 + retention_rates |
| L-3-2 | apply_holm_correction | multipletests(method='holm') → p_holm written back to results dict |

---

## A-4: Gate & Output [Complexity: 9, Budget: 4]

**Applied**: Standard Python with updated bounds; matplotlib/seaborn identical to h-e1 except bounds

### Constants (h-e1-v3-v4 specific)

```python
GATE_V_MIN = 0.40        # updated from h-e1's 0.29
GATE_V_MAX = 0.57        # updated from h-e1's 0.45 (check_gate) / 0.41 (plot_figures)
BASE_DIR   = Path("docs/youra_research/h-e1-v3-v4")
OUTPUT_DIR  = BASE_DIR
FIGURES_DIR = BASE_DIR / "figures"
```

### L-4-1: check_gate() + verify_mechanism_activated()

#### API Signatures

```python
def check_gate(df: pd.DataFrame, results: dict, k_values: list[int] = K_VALUES) -> dict:
    """5-condition gate with GATE_V_MIN=0.40, GATE_V_MAX=0.57. Returns {gate_passed, indicators}."""
    ...

def verify_mechanism_activated(results: dict, k_values: list[int] = K_VALUES) -> tuple[bool, dict]:
    """Wider mechanism check V in [0.38, 0.60], Holm p < 0.001. Returns (activated, indicators)."""
    ...
```

#### Pseudo-code: check_gate

```
indicators = {
    "data_loaded":        bool(len(df) > 190_000),
    "five_languages":     bool(df['language'].nunique() == 5),
    "no_nan_perplexity":  bool(df['ccnet_perplexity'].isna().mean() < 0.01),
    "cramers_v_in_range": bool(all(
        GATE_V_MIN <= results[k]['cramers_v'] <= GATE_V_MAX   # [0.40, 0.57]
        for k in k_values
    )),
    "holm_p_significant": bool(all(
        results[k]['p_holm'] < 0.001
        for k in k_values
    )),
}
return {"gate_passed": bool(all(indicators.values())), "indicators": indicators}
```

**Note**: Every value gets `bool()` cast — `numpy.bool_` is not JSON-serializable (h-e1 lesson).

#### Pseudo-code: verify_mechanism_activated

```
# main() must populate results with top-level metadata before calling this:
#   results['n_rows'], results['n_languages'], results['nan_rate'], results['per_k'][k]

indicators = {
    "data_loaded":        results.get("n_rows", 0) >= 190_000,
    "five_languages":     results.get("n_languages", 0) == 5,
    "no_nan_perplexity":  results.get("nan_rate", 1.0) < 0.01,
    "cramers_v_in_range": all(
        0.38 <= results["per_k"][k]["cramers_v"] <= 0.60    # wider than check_gate
        for k in k_values
    ),
    "holm_p_significant": all(
        results["per_k"][k]["p_holm"] < 0.001
        for k in k_values
    ),
}
return bool(all(indicators.values())), indicators
```

**Note**: `results["per_k"]` is the per-k results dict (keyed by int k). The PRD spec uses
`results["per_k_results"]` as a list — either structure works; use dict keyed by k for
consistency with `analyze_thresholds` output format.

---

### L-4-2: plot_figures()

#### API Signature

```python
def plot_figures(df: pd.DataFrame, results: dict, k_values: list[int] = K_VALUES) -> None:
    """Write 4 PNGs to module-level FIGURES_DIR. Updated gate bounds [0.40, 0.57]."""
    ...
```

#### Pseudo-code

```
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
languages = sorted(df['language'].unique())

# 1. cramers_v_bar.png — only change from h-e1: bounds 0.40/0.57
vs     = [results[k]['cramers_v'] for k in k_values]
colors = ['green' if GATE_V_MIN <= v <= GATE_V_MAX else 'red' for v in vs]
ax.bar([str(k) for k in k_values], vs, color=colors)
ax.axhline(GATE_V_MIN, color='navy',       linestyle='--', label=f'lower bound ({GATE_V_MIN})')
ax.axhline(GATE_V_MAX, color='darkorange', linestyle='--', label=f'upper bound ({GATE_V_MAX})')
# save FIGURES_DIR / 'cramers_v_bar.png', dpi=150

# 2. retention_heatmap.png — identical to h-e1
heatmap_data = pd.DataFrame({k: results[k]['retention_rates'] for k in k_values}).loc[languages]
sns.heatmap(heatmap_data, annot=True, fmt='.2f', cmap='YlOrRd', ax=ax)
# save FIGURES_DIR / 'retention_heatmap.png', dpi=150

# 3. perplexity_kde.png — identical to h-e1
for lang in languages:
    subset = df[df['language'] == lang]['ccnet_perplexity'].dropna()
    sns.kdeplot(subset[subset < subset.quantile(0.99)], ax=ax, label=lang, log_scale=True)
# save FIGURES_DIR / 'perplexity_kde.png', dpi=150

# 4. retention_gap.png — identical to h-e1
gaps = [max(results[k]['retention_rates'].values()) - min(results[k]['retention_rates'].values())
        for k in k_values]
ax.plot([str(k) for k in k_values], gaps, marker='o')
# save FIGURES_DIR / 'retention_gap.png', dpi=150
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | check_gate + verify_mechanism_activated | Gate [0.40, 0.57]; verify [0.38, 0.60]; bool() casts |
| L-4-2 | plot_figures | 4 PNGs; cramers_v_bar hlines at 0.40/0.57; figures 2-4 identical to h-e1 |

---

## Subtask Summary [4/4 used]

| ID | Function | Description |
|----|----------|-------------|
| L-3-1 | analyze_thresholds | Per-k quantile → crosstab(5×2) → Cramér's V + chi2 + retention_rates |
| L-3-2 | apply_holm_correction | multipletests(method='holm') → p_holm float into results |
| L-4-1 | check_gate + verify_mechanism_activated | Updated V bounds; bool() cast for numpy.bool_ |
| L-4-2 | plot_figures | 4 PNGs; cramers_v_bar hlines at 0.40/0.57 |

---

## Key Imports (for Phase 4)

```python
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency
from scipy.stats.contingency import association
from statsmodels.stats.multitest import multipletests
```

## JSON Serialization Rules

- `numpy.bool_` → `bool()` — every indicator in `check_gate`
- `numpy.float64` → `float()` — threshold, cramers_v, chi2, p_value, p_holm, retention rate values
- `association(contingency.values, method='cramer')` — `.values` required (numpy array, not DataFrame)
