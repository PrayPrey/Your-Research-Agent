# Logic: H-M3 — Categorical Tag Count Dose-Response (NB-2)

**Date:** 2026-08-05
**Gate:** SHOULD_WORK
**Budget:** 5 subtasks

Applied: H-E1 flat-4-script pattern (NumpyEncoder, fit_nb2, serialize_results verified from actual code)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**:
- `NumpyEncoder` — handles np.integer, np.floating, np.ndarray, bool
- `fit_nb2(formula, df, label, target_col="N_tasks") -> dict` — returns dict with params/bse/pvalues/conf_int/llf/aic/converged
- `serialize_results(results, out_path) -> None` — json.dump with NumpyEncoder
- `ct_lr_test(df) -> dict` — returns lr_stat, p_value, nb2_appropriate
- `evaluate_gate(irr, ci_lower, ci_upper, pval) -> str` — H-E1 signature (DIFFERENT from H-M3 gate logic)

---

## External Dependencies API

### Verified from `docs/youra_research/h-e1/code/02_fit_models.py` (ACTUAL CODE)

```python
# H-E1 actual signatures — do NOT deviate from these param names

def fit_nb2(formula: str, df: pd.DataFrame, label: str, target_col: str = "N_tasks") -> dict[str, Any]:
    """Fit NB-2; returns dict with keys: label, converged, llf, aic, bic, n_obs,
       params {str->float}, bse, pvalues, conf_int {str->[lo,hi]}."""
    # result.conf_int() -> DataFrame; iterated as conf_int_df.iterrows()
    # conf_int stored as {str(name): [float(row[0]), float(row[1])]}
    # Falls back to Nelder-Mead if BFGS unconverged

def serialize_results(results: dict[str, Any], out_path: str) -> None:
    """json.dump with NumpyEncoder, makedirs."""

class NumpyEncoder(json.JSONEncoder):
    # handles: np.integer -> int, np.floating -> float, np.ndarray -> list, bool -> bool
```

**Key detail**: `fit_nb2` returns serializable dict, NOT a RegressionResultsWrapper.
H-M3 must call `smf.negativebinomial(...).fit(...)` directly to access `.t_test_pairwise()`.

---

## A-9: Implement 5 Figures [Complexity: 9, Budget: 2 subtasks]

### L-9-1: Figure 1 — IRR Bar Chart

```python
def fig1_irr_bar_chart(results: dict, save_dir: str) -> None:
    """IRR per category with 95% CI error bars and reference lines."""
    # results keys used: results['cat_model']['irr_by_cat']
    # irr_by_cat: {"0": 1.0, "1-2": float, "3-5": float, "6+": float}
    # ci_lower_by_cat, ci_upper_by_cat: same structure
```

**Pseudo-code:**
```
categories = ["0", "1-2", "3-5", "6+"]
irr_vals   = [results['cat_model']['irr_by_cat'][c] for c in categories]
ci_lo      = [results['cat_model']['ci_lower_by_cat'][c] for c in categories]
ci_hi      = [results['cat_model']['ci_upper_by_cat'][c] for c in categories]
yerr_lo    = [irr - lo for irr, lo in zip(irr_vals, ci_lo)]
yerr_hi    = [hi - irr for irr, hi in zip(irr_vals, ci_hi)]

fig, ax = plt.subplots(figsize=(7, 5))
ax.bar(categories, irr_vals, yerr=[yerr_lo, yerr_hi], capsize=5, color='steelblue', alpha=0.8)
ax.axhline(1.0, color='black', linestyle='--', linewidth=1, label='IRR=1.0 (null)')
ax.axhline(1.1, color='red',   linestyle='--', linewidth=1, label='IRR=1.1 (H-E1 threshold)')
ax.set_xlabel("Tag Count Category")
ax.set_ylabel("Incidence Rate Ratio (vs. ref '0')")
ax.set_title("H-M3: IRR by Tag Count Category (NB-2)")
ax.legend()
save_fig(fig, "fig1_irr_bar_chart", save_dir)
```

**Note**: Category "0" bar uses IRR=1.0 (reference), no CI bars (or symmetric 0 error).

### L-9-2: Figure 4 — Contrast Forest Plot

```python
def fig4_contrast_forest(results: dict, save_dir: str) -> None:
    """Horizontal CI intervals for 3 adjacent contrasts with Bonferroni threshold."""
    # results keys: results['adjacent_contrasts']['contrasts']
    # contrasts: list of {label: str, coef: float, ci_lo: float, ci_hi: float, pval_bonf: float}
    # 3 rows: "1-2 vs 0", "3-5 vs 1-2", "6+ vs 3-5"
```

**Pseudo-code:**
```
contrasts = results['adjacent_contrasts']['contrasts']
# contrasts stored as exp(coef) — plot on log scale OR plot raw coef
# Use IRR scale (exp): coef_irr, ci_lo_irr, ci_hi_irr

fig, ax = plt.subplots(figsize=(7, 4))
y_pos = range(len(contrasts))  # [0, 1, 2]
for i, c in enumerate(contrasts):
    color = 'green' if c['pval_bonf'] < BONF_ALPHA else 'red'
    ax.plot([c['ci_lo_irr'], c['ci_hi_irr']], [i, i], color=color, linewidth=2)
    ax.plot(c['coef_irr'], i, 'o', color=color, markersize=8)

ax.axvline(1.0, color='black', linestyle='--', linewidth=1)
ax.set_yticks(list(y_pos))
ax.set_yticklabels([c['label'] for c in contrasts])
ax.set_xlabel("IRR of Adjacent Contrast")
ax.set_title(f"H-M3: Adjacent Contrasts (Bonferroni α={BONF_ALPHA})")
# Annotate significance
for i, c in enumerate(contrasts):
    sig = "p<0.0167*" if c['pval_bonf'] < BONF_ALPHA else "n.s."
    ax.text(c['ci_hi_irr'] + 0.02, i, sig, va='center', fontsize=9)
save_fig(fig, "fig4_contrast_forest", save_dir)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | fig1_irr_bar_chart | Bar chart with CI error bars, reference lines at 1.0 and 1.1 |
| L-9-2 | fig4_contrast_forest | Horizontal forest plot of 3 adjacent contrasts, significance coloring |

---

## A-4: Categorical NB-2 Primary Model [Complexity: 9, Budget: 1 subtask]

### L-4-1: extract_cat_irr()

```python
def extract_cat_irr(result: Any) -> dict[str, Any]:
    """Extract IRR, CI, pvalue for each C(tag_count_cat) level from live result wrapper.

    Statsmodels patsy key format: 'C(tag_count_cat)[T.1-2]', 'C(tag_count_cat)[T.3-5]',
    'C(tag_count_cat)[T.6+]'. Reference category '0' is omitted (IRR=1.0 by definition).
    """
    # result is RegressionResultsWrapper (NOT the dict from fit_nb2)
    params   = result.params         # pd.Series, index = param names
    conf     = result.conf_int()     # pd.DataFrame, columns [0, 1]
    pvalues  = result.pvalues        # pd.Series

    cat_keys = [k for k in params.index if 'tag_count_cat' in k]
    # Expected: ['C(tag_count_cat)[T.1-2]', 'C(tag_count_cat)[T.3-5]', 'C(tag_count_cat)[T.6+]']

    irr_by_cat      = {"0": 1.0}
    ci_lower_by_cat = {"0": 1.0}
    ci_upper_by_cat = {"0": 1.0}
    pval_by_cat     = {"0": None}

    for k in cat_keys:
        label = k.replace("C(tag_count_cat)[T.", "").rstrip("]")  # -> "1-2", "3-5", "6+"
        irr_by_cat[label]      = float(np.exp(params[k]))
        ci_lower_by_cat[label] = float(np.exp(conf.loc[k, 0]))
        ci_upper_by_cat[label] = float(np.exp(conf.loc[k, 1]))
        pval_by_cat[label]     = float(pvalues[k])

    return {
        'irr_by_cat':      irr_by_cat,       # {"0":1.0, "1-2":float, "3-5":float, "6+":float}
        'ci_lower_by_cat': ci_lower_by_cat,
        'ci_upper_by_cat': ci_upper_by_cat,
        'pval_by_cat':     pval_by_cat,
        'cat_keys_raw':    cat_keys,          # for debugging patsy key format
    }
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | extract_cat_irr | Key lookup via 'tag_count_cat' filter, np.exp mapping, conf_int extraction |

---

## A-6: Adjacent Contrast Testing [Complexity: 9, Budget: 2 subtasks]

### L-6-1: test_adjacent_contrasts()

```python
def test_adjacent_contrasts(
    result: Any,              # RegressionResultsWrapper (live, NOT dict)
    bonf_alpha: float = 0.0167
) -> tuple[pd.DataFrame, int, dict]:
    """Run pairwise contrasts, extract 3 adjacent pairs, count passing.

    Returns: (full_pw_df, n_passing, contrasts_list_for_serialization)
    """
```

**Pseudo-code:**
```
pw = result.t_test_pairwise('C(tag_count_cat)', method='bonferroni')
pw_df = pw.result_frame  # pd.DataFrame; index = contrast labels e.g. "1-2-0", "3-5-0", ...

# Adjacent pairs only — NOT all-vs-all
# Patsy contrast index format: "level_b-level_a" where b > a in sort order
# For categories ["0","1-2","3-5","6+"] the 3 adjacent contrasts are:
ADJACENT_PAIRS = [
    ("0", "1-2"),    # contrast label pattern: "1-2-0"
    ("1-2", "3-5"),  # contrast label pattern: "3-5-1-2"
    ("3-5", "6+"),   # contrast label pattern: "6+-3-5"
]

# Robustly find rows: scan pw_df.index for strings containing both level names
contrasts_out = []
n_passing = 0
for (lo, hi) in ADJACENT_PAIRS:
    # Find matching row — index may be "hi-lo" format
    matched = [idx for idx in pw_df.index if (lo in idx and hi in idx)]
    if not matched:
        contrasts_out.append({'label': f"{hi} vs {lo}", 'found': False})
        continue
    row = pw_df.loc[matched[0]]
    coef_irr   = float(np.exp(row['coef']))
    ci_lo_irr  = float(np.exp(row['coef'] - 1.96 * row['std err']))
    ci_hi_irr  = float(np.exp(row['coef'] + 1.96 * row['std err']))
    # Use Bonferroni-corrected p from statsmodels column
    pval_bonf  = float(row.get('pvalue-bonferroni', row.get('P>|t|', 1.0)))
    passing    = pval_bonf < bonf_alpha
    if passing:
        n_passing += 1
    contrasts_out.append({
        'label':      f"{hi} vs {lo}",
        'coef_irr':   coef_irr,
        'ci_lo_irr':  ci_lo_irr,
        'ci_hi_irr':  ci_hi_irr,
        'pval_bonf':  pval_bonf,
        'significant': passing,
    })

return pw_df, n_passing, contrasts_out
```

**Note**: `t_test_pairwise` column names vary by statsmodels version. Check for `'pvalue-bonferroni'` first, fallback to `'P>|t|'`.

### L-6-2: check_monotonicity()

```python
def check_monotonicity(irr_dict: dict) -> tuple[bool, dict]:
    """Verify strict IRR ordering: 1-2 < 3-5 < 6+, all > 1.0.

    irr_dict keys: {"0":1.0, "1-2":float, "3-5":float, "6+":float}
    Returns: (is_monotonic, detail_dict)
    """
```

**Pseudo-code:**
```
# Key lookup — use exact string keys from extract_cat_irr output
v12 = irr_dict.get("1-2")
v35 = irr_dict.get("3-5")
v6p = irr_dict.get("6+")

if any(v is None for v in [v12, v35, v6p]):
    return False, {'error': 'Missing category keys', 'found_keys': list(irr_dict.keys())}

cond_12_gt1  = v12 > 1.0
cond_order   = (v12 < v35) and (v35 < v6p)
is_monotonic = cond_12_gt1 and cond_order

return is_monotonic, {
    'irr_1_2':    v12,
    'irr_3_5':    v35,
    'irr_6plus':  v6p,
    'cond_12_gt1': cond_12_gt1,
    'cond_order':  cond_order,
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | test_adjacent_contrasts | t_test_pairwise call, adjacent pair extraction, Bonferroni p lookup |
| L-6-2 | check_monotonicity | Key lookup for "1-2"/"3-5"/"6+", strict ordering check, all > 1.0 |

---

## Supporting API Signatures (All 4 Scripts)

### 01_preprocess.py

```python
BASE_DIR: str = "docs/youra_research/h-m3"
H_E1_PARQUET: str = "docs/youra_research/h-e1/results/preprocessed.parquet"
H_E1_CSV_FALLBACK: str = "docs/youra_research/h-e1/code/data/h_e1/openml_dataset_corpus.csv"
PREPROCESSED_OUT: str = f"{BASE_DIR}/results/preprocessed.parquet"
EXPECTED_N: int = 5217
BIN_BREAKS: list = [-1, 0, 2, 5, float('inf')]
BIN_LABELS: list = ["0", "1-2", "3-5", "6+"]

def load_corpus() -> pd.DataFrame: ...
def derive_tag_count(df: pd.DataFrame) -> pd.DataFrame: ...
def verify_controls(df: pd.DataFrame) -> pd.DataFrame: ...
def validate(df: pd.DataFrame) -> None: ...
def main() -> None: ...
```

### 02_fit_models.py

```python
BASE_DIR: str = "docs/youra_research/h-m3"
PREPROCESSED: str = f"{BASE_DIR}/results/preprocessed.parquet"
MODEL_RESULTS: str = f"{BASE_DIR}/results/model_results.json"
_CONTROLS: str = "log_n_instances + log_n_features + age_years + age_sq + C(decade)"
FORMULA_BASELINE: str = f"N_tasks ~ {_CONTROLS}"
FORMULA_BINARY: str = f"N_tasks ~ has_tags + {_CONTROLS}"
FORMULA_CAT: str = f"N_tasks ~ C(tag_count_cat) + {_CONTROLS}"
FORMULA_RC6: str = f"N_tasks ~ C(tag_count_cat)*C(decade) + log_n_instances + log_n_features + age_years + age_sq"
FORMULA_RC7: str = f"N_tasks ~ C(tag_count_cat) + log_n_instances + log_n_features + age_years + age_sq"
NB2_METHOD: str = "bfgs"
NB2_MAXITER: int = 200
NB2_DISP: bool = False
BONF_ALPHA: float = 0.0167

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any: ...  # identical to H-E1

def ct_lr_test(df: pd.DataFrame) -> dict[str, Any]: ...
    # Uses FORMULA_BASELINE (controls-only); returns lr_stat, p_value, nb2_appropriate

def fit_nb2(formula: str, df: pd.DataFrame, label: str) -> dict[str, Any]: ...
    # Mirror H-E1 fit_nb2 exactly (BFGS + Nelder-Mead fallback)
    # Returns serializable dict (NOT RegressionResultsWrapper)

def fit_cat_model(df: pd.DataFrame) -> tuple[Any, dict]:
    """Fit primary categorical NB-2; return (live_result, serializable_dict).
    live_result needed for t_test_pairwise and extract_cat_irr.
    """

def extract_cat_irr(result: Any) -> dict[str, Any]: ...
    # result: RegressionResultsWrapper (live)
    # Returns irr_by_cat, ci_lower_by_cat, ci_upper_by_cat, pval_by_cat

def check_monotonicity(irr_dict: dict) -> tuple[bool, dict]: ...
    # irr_dict: {"0":1.0, "1-2":float, "3-5":float, "6+":float}

def test_adjacent_contrasts(
    result: Any, bonf_alpha: float = 0.0167
) -> tuple[pd.DataFrame, int, dict]: ...
    # result: RegressionResultsWrapper (live)
    # Returns (pw_df, n_passing, contrasts_list)

def serialize_results(results: dict[str, Any], out_path: str) -> None: ...
    # Identical to H-E1

def main() -> None: ...
```

### 03_generate_figures.py

```python
BASE_DIR: str = "docs/youra_research/h-m3"
MODEL_RESULTS: str = f"{BASE_DIR}/results/model_results.json"
FIGURES_DIR: str = f"{BASE_DIR}/figures"
FIGURE_DPI: int = 300
FIGURE_FORMAT: str = "png"
BONF_ALPHA: float = 0.0167

def save_fig(fig: Any, name: str, save_dir: str) -> None: ...
    # fig.savefig(f"{save_dir}/{name}.{FIGURE_FORMAT}", dpi=FIGURE_DPI, bbox_inches='tight')

def fig1_irr_bar_chart(results: dict, save_dir: str) -> None: ...
def fig2_dose_response(results: dict, save_dir: str) -> None: ...
def fig3_bin_distribution(results: dict, save_dir: str) -> None: ...
def fig4_contrast_forest(results: dict, save_dir: str) -> None: ...
def fig5_attenuation(results: dict, save_dir: str) -> None: ...
def main() -> None: ...
```

### 04_evaluate_gate.py

```python
BASE_DIR: str = "docs/youra_research/h-m3"
MODEL_RESULTS: str = f"{BASE_DIR}/results/model_results.json"
PRIMARY_RESULTS: str = f"{BASE_DIR}/results/primary_results.json"
BONF_ALPHA: float = 0.0167
MIN_CONTRASTS_PASS: int = 2

def evaluate_gate(model_data: dict) -> dict:
    """Extract is_monotonic, n_adj_passing; compute gate verdict.

    Returns dict with: gate_type, hypothesis_id, is_monotonic, n_adj_passing,
    gate_pass (bool), result ('PASS'|'PARTIAL_PASS'|'INFORMATIVE_NEGATIVE').
    """
    # gate_pass_full    = is_monotonic and n_adj_passing == 3 -> 'PASS'
    # gate_pass_partial = is_monotonic and n_adj_passing == 2 -> 'PARTIAL_PASS'
    # else -> 'INFORMATIVE_NEGATIVE'

def main() -> None: ...
    # load MODEL_RESULTS, call evaluate_gate, save PRIMARY_RESULTS
    # sys.exit(1) only on INFORMATIVE_NEGATIVE (mirrors H-E1 pattern)
```

---

## results/model_results.json Schema

```json
{
  "ct_lr_test": {"lr_stat": float, "p_value": float, "nb2_appropriate": bool},
  "baseline":   {<fit_nb2 dict>},
  "binary":     {<fit_nb2 dict>},
  "cat_model": {
    "<fit_nb2 fields>",
    "irr_by_cat":      {"0": 1.0, "1-2": float, "3-5": float, "6+": float},
    "ci_lower_by_cat": {"0": 1.0, "1-2": float, "3-5": float, "6+": float},
    "ci_upper_by_cat": {"0": 1.0, "1-2": float, "3-5": float, "6+": float},
    "pval_by_cat":     {"0": null, "1-2": float, "3-5": float, "6+": float},
    "monotonicity":    {"is_monotonic": bool, "irr_1_2": float, ...},
    "adjacent_contrasts": {
      "n_passing": int,
      "bonf_alpha": 0.0167,
      "contrasts": [{"label": str, "coef_irr": float, "ci_lo_irr": float,
                     "ci_hi_irr": float, "pval_bonf": float, "significant": bool}]
    }
  },
  "rc6_interact": {<fit_nb2 dict>},
  "rc7_no_fe":    {<fit_nb2 dict>, "irr_by_cat": {...}},
  "bin_counts":   {"0": int, "1-2": int, "3-5": int, "6+": int}
}
```
