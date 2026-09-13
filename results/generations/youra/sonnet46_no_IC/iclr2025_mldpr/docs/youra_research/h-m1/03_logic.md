# Logic: H-M1 — Tag-Indexed Search Pathway Mechanism Verification

Applied: continuation-experiment minimal-reuse pattern

---

## Codebase Analysis (Serena)

**Analyzed**: `docs/youra_research/h-e1/code/02_fit_models.py`
**Key findings**:
- `fit_nb2(formula, df, label, target_col="N_tasks") -> dict` at line 78 — full signature verified
- `extract_has_tags_stats(fit_result) -> dict` at line 115 — extracts IRR/CI/pval
- `NumpyEncoder` at line 44 — handles np.integer, np.floating, np.ndarray, bool
- H-E1 `model_results.json` keys: `ct_lr_test`, `baseline`, `proposed`, `rc4_winsorized`, `rc5_tagged_only`, `rc7_age_vs_decade`
- `proposed` key contains nested `has_tags` dict with `irr`, `ci_lower`, `ci_upper`, `pval`
- `rc7_age_vs_decade` key contains `irr_with_decade`, `irr_without_decade`, `attenuation_ratio`

All H-M1 code copies `fit_nb2` and `NumpyEncoder` inline — H-E1 scripts are not a package.

---

## External Dependencies API

### From H-E1 `02_fit_models.py` (verified from actual code)

```python
def fit_nb2(
    formula: str,
    df: pd.DataFrame,
    label: str,
    target_col: str = "N_tasks"
) -> dict[str, Any]:
    """
    Fit NB-2 model. BFGS with Nelder-Mead fallback.
    Returns dict with keys:
      label: str
      converged: bool
      llf: float
      aic: float
      bic: float
      n_obs: int
      params: dict[str, float]      # key = coef name (e.g. 'has_tags', 'Intercept')
      bse: dict[str, float]
      pvalues: dict[str, float]
      conf_int: dict[str, [float, float]]  # key = coef name, value = [lower, upper]
    Raises RuntimeError on fit failure.
    """

def extract_has_tags_stats(fit_result: dict[str, Any]) -> dict[str, float]:
    """
    Extract IRR metrics from fit_nb2 output.
    Returns: {'irr': float, 'ci_lower': float, 'ci_upper': float, 'pval': float}
    Note: irr = exp(params['has_tags']), ci_lower = exp(conf_int['has_tags'][0])
    """

class NumpyEncoder(json.JSONEncoder):
    """Handles np.integer, np.floating, np.ndarray → Python native types."""
```

### H-E1 `model_results.json` Schema (for `load_or_fit_models`)

```python
# Keys available in h-e1/results/model_results.json
{
    "proposed": {
        "has_tags": {"irr": 1.2263, "ci_lower": 1.1681, "ci_upper": 1.2873, "pval": 1.87e-16},
        "params": {"has_tags": 0.2039, ...},
        "pvalues": {"has_tags": 1.87e-16, ...},
        "conf_int": {"has_tags": [0.1554, 0.2524], ...}
    },
    "rc7_age_vs_decade": {
        "irr_with_decade": 1.2263,
        "irr_without_decade": 1.3758,
        "attenuation_ratio": 1.122
    }
}
```

---

## Subtask L-3-1: `fit_nb2` Copy and `load_or_fit_models` Logic

**Parent Epic**: A-3 (Model Fitter, complexity 10)

### Full `load_or_fit_models` Implementation

```python
def load_or_fit_models(
    df: pd.DataFrame,
    h_e1_results: dict | None
) -> dict[str, Any]:
    """
    Load pre-computed H-E1 models or refit from scratch.

    Strategy:
    1. If h_e1_results has 'proposed' AND 'rc7_age_vs_decade':
       → extract IRRs directly (no refitting needed)
    2. Else:
       → fit FORMULA_WITH_FE and FORMULA_NO_FE via fit_nb2

    Returns:
    {
        'with_fe': {
            'irr': float, 'ci_lower': float, 'ci_upper': float, 'pval': float,
            'params': dict, 'pvalues': dict, 'conf_int': dict,
            'converged': bool, 'llf': float
        },
        'no_fe': {
            'irr': float, 'ci_lower': float, 'ci_upper': float, 'pval': float,
            'converged': bool
        },
        'source': 'h_e1_cache' | 'refitted'
    }
    """
    if h_e1_results and 'proposed' in h_e1_results and 'rc7_age_vs_decade' in h_e1_results:
        # Path 1: extract from cache
        proposed = h_e1_results['proposed']
        rc7 = h_e1_results['rc7_age_vs_decade']

        # Extract with-FE stats
        if 'has_tags' in proposed:
            # nested format: proposed.has_tags.irr
            ht = proposed['has_tags']
        else:
            # flat format: use extract_has_tags_stats
            ht = extract_has_tags_stats(proposed)

        with_fe = {
            'irr': ht['irr'],
            'ci_lower': ht['ci_lower'],
            'ci_upper': ht['ci_upper'],
            'pval': ht['pval'],
            'params': proposed.get('params', {}),
            'pvalues': proposed.get('pvalues', {}),
            'conf_int': proposed.get('conf_int', {}),
            'converged': proposed.get('converged', True),
            'llf': proposed.get('llf', None),
        }
        no_fe = {
            'irr': rc7['irr_without_decade'],
            'ci_lower': None,   # not stored in rc7 entry
            'ci_upper': None,
            'pval': None,       # not stored in rc7 entry
            'converged': True,
        }
        return {'with_fe': with_fe, 'no_fe': no_fe, 'source': 'h_e1_cache'}
    else:
        # Path 2: refit both models
        fit_with = fit_nb2(FORMULA_WITH_FE, df, "h_m1_with_fe")
        fit_no   = fit_nb2(FORMULA_NO_FE,   df, "h_m1_no_fe")
        ht_with  = extract_has_tags_stats(fit_with)
        ht_no    = extract_has_tags_stats(fit_no)
        with_fe = {**ht_with, **{k: fit_with[k] for k in ('params','pvalues','conf_int','converged','llf')}}
        no_fe   = {**ht_no,   'converged': fit_no['converged']}
        return {'with_fe': with_fe, 'no_fe': no_fe, 'source': 'refitted'}
```

### Pseudo-code: `02_fit_models.py` main flow

```
1. load_preprocessed() → df (N=5217)
2. load_h_e1_results() → h_e1_results (dict or None)
3. models = load_or_fit_models(df, h_e1_results)
4. cramers_v, p_chi2 = compute_cramers_v(df)
   - pd.crosstab(df['decade'], df['has_tags'])
   - chi2_contingency → chi2, p, dof
   - cramers_v = sqrt(chi2 / (N * (min_dim - 1)))
5. attenuation = compute_attenuation_ratio(models['no_fe']['irr'], models['with_fe']['irr'])
   - attenuation_ratio = irr_no_fe / irr_with_fe
6. Serialize to MODEL_RESULTS:
   {
     'with_fe': models['with_fe'],
     'no_fe': models['no_fe'],
     'cramers_v': cramers_v,
     'p_chi2': p_chi2,
     'attenuation_ratio': attenuation,
     'source': models['source'],
     'has_tags_by_decade': df.groupby('decade')['has_tags'].mean().to_dict()
   }
```

---

## Subtask L-8-1: Integration Verification Logic

**Parent Epic**: A-8 (End-to-end Integration, complexity 9)

### Expected Values Check

```python
TOLERANCES = {
    'irr_with_fe':       (1.2263, 0.05),   # (expected, tolerance)
    'irr_no_fe':         (1.3758, 0.05),
    'attenuation_ratio': (1.122,  0.02),
    'cramers_v':         (0.823,  0.05),
}

def verify_results(primary_results: dict) -> list[str]:
    """
    Returns list of failed checks (empty = all pass).
    """
    failures = []
    for key, (expected, tol) in TOLERANCES.items():
        actual = primary_results.get(key)
        if actual is None:
            failures.append(f"MISSING: {key}")
        elif abs(actual - expected) > tol:
            failures.append(
                f"OUT_OF_RANGE: {key}={actual:.4f}, "
                f"expected {expected}±{tol}"
            )
    return failures
```

### Pipeline Execution Sequence

```python
# Run from project root:
scripts = [
    "docs/youra_research/h-m1/code/01_load_data.py",
    "docs/youra_research/h-m1/code/02_fit_models.py",
    "docs/youra_research/h-m1/code/03_generate_figures.py",
    "docs/youra_research/h-m1/code/04_evaluate_gate.py",
]
for script in scripts:
    returncode = subprocess.run(["python", script]).returncode
    assert returncode == 0, f"Script failed: {script}"

# Verify outputs
assert Path("docs/youra_research/h-m1/results/primary_results.json").exists()
assert Path("docs/youra_research/h-m1/figures/fig1_irr_comparison.png").exists()
```

---

## API Reference Summary

| Module | Function | Inputs | Returns |
|--------|----------|--------|---------|
| `02_fit_models` | `fit_nb2` | formula, df, label | dict (params/pvalues/conf_int/llf/aic/bic) |
| `02_fit_models` | `extract_has_tags_stats` | fit_result dict | {irr, ci_lower, ci_upper, pval} |
| `02_fit_models` | `compute_cramers_v` | df | (cramers_v: float, p_chi2: float) |
| `02_fit_models` | `compute_attenuation_ratio` | irr_no_fe, irr_with_fe | float |
| `02_fit_models` | `load_or_fit_models` | df, h_e1_results | {with_fe, no_fe, source} |
| `04_evaluate_gate` | `evaluate_gate` | h_e1_gate, irr_with_fe, p_with_fe | "PASS"\|"FAIL" |
| `04_evaluate_gate` | `build_results` | model_results dict | primary_results dict |
