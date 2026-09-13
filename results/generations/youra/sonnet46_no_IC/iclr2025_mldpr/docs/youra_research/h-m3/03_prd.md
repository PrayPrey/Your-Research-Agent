# PRD: H-M3 — Categorical Tag Count Dose-Response → Task Run Count (NB-2 Monotonic Gate)

**Hypothesis ID:** H-M3
**Type:** MECHANISM (Dose-Response Categorical)
**Gate:** SHOULD_WORK
**Date:** 2026-08-05
**Phase 2C Source:** h-m3/02c_experiment_brief.md
**Tier:** FULL (≤30 tasks)
**Base Hypothesis:** H-E1 (MUST_WORK PASS — IRR=1.2263, p=1.87e-16), H-M1 (MUST_WORK PASS — mechanism confirmed), H-M2 (SHOULD_WORK PASS — IRR_P2=1.5332, p=1.28e-82)

---

## 1. Executive Summary

H-M3 tests whether the categorical tag count dose-response structure is monotonic across four bins (0, 1-2, 3-5, 6+) on the full OpenML corpus (N=5,217). Using the H-E1 preprocessed parquet (reuse), we fit a Negative Binomial Regression Type 2 (NB-2) with `C(tag_count_cat)` categorical dummy variable (reference = "0"), controlling for dataset size, age (quadratic), and decade-of-upload fixed effects. Success requires: (1) monotonic IRR ordering — IRR(1-2) < IRR(3-5) < IRR(6+) — all vs reference category "0"; AND (2) ≥2/3 adjacent contrasts significant at Bonferroni-corrected α=0.0167.

**Gate type is SHOULD_WORK** — an informative negative (non-monotonic ordering or <2/3 contrasts) is scientifically valid and would constrain the Discovery→Task Creation mechanism to binary threshold only.

This is the 4th and final sub-hypothesis in the H-E1→H-M1→H-M2→H-M3 mechanism chain. All prerequisites passed with strong effects (H-M2: IRR_P2=1.5332). Expected IRR estimates: IRR(1-2)~1.4-1.7, IRR(3-5)~1.8-2.5, IRR(6+)~2.5-4.0.

---

## 2. Problem Statement

**Research Question:** Among all OpenML datasets with N_tasks ≥ 1 (N=5,217), does grouping by categorical tag count (0, 1-2, 3-5, 6+) reveal a monotonic dose-response relationship with registered ML tasks (N_tasks), after controlling for dataset size, age, and decade?

**Mechanism Chain:** More keyword tags → More search pathways in OpenML tag index → Higher category → Monotonically higher N_tasks (dose-response structure)

**Null (H₀):** No monotonic ordering — IRRs across categories are not strictly increasing

**Alternative (H₁):** Monotonic IRR ordering (0 < 1-2 < 3-5 < 6+ vs reference) AND ≥2/3 adjacent contrasts p < 0.0167

**Gate Condition (SHOULD_WORK):**
- **Full PASS:** Monotonic ordering AND ≥2/3 adjacent contrasts p < 0.0167
- **Partial PASS (document):** Monotonic with exactly 2/3 contrasts significant
- **Informative negative:** Non-monotonic OR <2/3 contrasts — binary/continuous dose-response is the full FAIR F1 signal

**Prerequisites Confirmed:**
- H-E1: IRR=1.2263 (CI=[1.1681,1.2873]), p=1.87e-16 — MUST_WORK PASS
- H-M1: has_tags survives C(decade) FE, attenuation_ratio=1.122 — mechanism STRONG
- H-M2: IRR_P2=1.5332 (CI=[1.4680,1.6014]), p=1.28e-82 — dose-gradient confirmed

---

## 3. Functional Requirements

### FR-01: Load Full Corpus from H-E1 Parquet

- **What:** Load preprocessed H-E1 parquet (full corpus, N=5,217)
- **Primary path:** `docs/youra_research/h-e1/results/preprocessed.parquet`
- **Fallback:** Load raw CSV `h-e1/code/data/h_e1/openml_dataset_corpus.csv` and re-run preprocessing
- **Filter:** All N=5,217 rows (N_tasks ≥ 1 already applied in cache)
- **Required columns:** N_tasks, tags (or tag_count), n_instances, n_features, upload_date (or pre-derived: log_n_instances, log_n_features, age_years, age_sq, decade)

```python
import pandas as pd
import numpy as np

# Primary path — H-E1 preprocessed parquet
df = pd.read_parquet('docs/youra_research/h-e1/results/preprocessed.parquet')
print(f"Full corpus N={len(df)}")  # expect 5,217
assert len(df) >= 5000, f"Unexpected corpus size: {len(df)}"
```

### FR-02: Derive tag_count and Categorical Bins

- **tag_count derivation:** From parquet (already computed) OR `df['tags'].str.count(',') + 1` for non-null rows; 0 for null/empty
- **Categorical bins:** `pd.cut` with breaks at [-1, 0, 2, 5, inf], labels ["0", "1-2", "3-5", "6+"]
- **Validate:** All 4 bins populated (>0 datasets each); verify reference bin "0" = ~2,592 datasets

```python
# Derive tag_count if not in parquet
if 'tag_count' not in df.columns:
    df['tag_count'] = df['tags'].apply(
        lambda x: int(str(x).count(',') + 1) if pd.notna(x) and str(x).strip() not in ['', 'nan', '[]'] else 0
    )

# Derive categorical bins
df['tag_count_cat'] = pd.cut(
    df['tag_count'],
    bins=[-1, 0, 2, 5, float('inf')],
    labels=["0", "1-2", "3-5", "6+"]
).astype(str)

# Report bin counts
bin_counts = df['tag_count_cat'].value_counts().sort_index()
print("Tag count category distribution:")
print(bin_counts)
assert (bin_counts > 0).all(), "Some bins are empty"
```

### FR-03: Controls Verification

- **Required controls:** log_n_instances, log_n_features, age_years, age_sq, decade
- If not in parquet, derive them (same as H-E1 FR-02)
- Verify no NaN in any control variable (critical for BFGS convergence)

```python
controls_needed = ['log_n_instances', 'log_n_features', 'age_years', 'age_sq', 'decade']
for col in controls_needed:
    if col not in df.columns:
        raise ValueError(f"Missing control: {col}. Re-run H-E1 preprocessing.")
    nan_count = df[col].isna().sum()
    if nan_count > 0:
        print(f"Warning: {nan_count} NaN in {col} — dropping affected rows")
        df = df.dropna(subset=controls_needed)
print(f"N after controls check: {len(df)}")
```

### FR-04: Overdispersion Check (CT LR Test)

- Reconfirm NB-2 appropriateness with categorical model
- Fit Poisson baseline (controls-only) and NB-2 baseline (controls-only)
- LR stat = 2*(llf_NB2 − llf_Poisson) ~ chi²(1) — expected >> 3.84

```python
import statsmodels.formula.api as smf
from scipy.stats import chi2

controls_formula = 'log_n_instances + log_n_features + age_years + age_sq + C(decade)'
baseline_formula = f'N_tasks ~ {controls_formula}'

poisson_res = smf.poisson(baseline_formula, data=df).fit(method='bfgs', disp=False)
nb2_baseline = smf.negativebinomial(baseline_formula, data=df, loglike_method='nb2').fit(
    method='bfgs', maxiter=200, disp=False)

lr_stat = 2 * (nb2_baseline.llf - poisson_res.llf)
p_ct = 1 - chi2.cdf(lr_stat, df=1)
print(f"CT LR={lr_stat:.2f}, p={p_ct:.2e} (NB-2 appropriate if LR >> 3.84)")
```

### FR-05: Baseline Model (Controls-Only NB-2)

```python
baseline = smf.negativebinomial(
    baseline_formula, data=df, loglike_method='nb2'
).fit(method='bfgs', maxiter=200, disp=False)
print(f"Baseline LLF={baseline.llf:.2f}, AIC={baseline.aic:.2f}")
```

### FR-06: Primary NB-2 Regression — Categorical IV (Proposed Model)

```python
cat_formula = ('N_tasks ~ C(tag_count_cat) '
               '+ log_n_instances + log_n_features '
               '+ age_years + age_sq + C(decade)')

result_cat = smf.negativebinomial(
    cat_formula, data=df, loglike_method='nb2'
).fit(method='bfgs', maxiter=200, disp=False)

# Extract IRR for each category vs reference "0"
params = result_cat.params
conf = result_cat.conf_int()

cat_keys = [k for k in params.index if 'tag_count_cat' in k]
irr = {k: np.exp(params[k]) for k in cat_keys}
ci_lower = {k: np.exp(conf.loc[k, 0]) for k in cat_keys}
ci_upper = {k: np.exp(conf.loc[k, 1]) for k in cat_keys}
pvals = {k: result_cat.pvalues[k] for k in cat_keys}

# Report
for k in sorted(cat_keys):
    cat_label = k.replace('C(tag_count_cat)[T.', '').rstrip(']')
    print(f"  IRR({cat_label}): {irr[k]:.4f} (CI=[{ci_lower[k]:.4f},{ci_upper[k]:.4f}]), p={pvals[k]:.3e}")
```

### FR-07: Monotonicity Check

```python
def check_monotonicity(irr_dict):
    """Verify IRR("1-2") < IRR("3-5") < IRR("6+") — each vs reference "0" → all should be >1 and ordered."""
    key_12 = [k for k in irr_dict if '1-2' in k]
    key_35 = [k for k in irr_dict if '3-5' in k]
    key_6p = [k for k in irr_dict if '6+' in k]

    if not (key_12 and key_35 and key_6p):
        return False, "Missing category keys"

    v12 = irr_dict[key_12[0]]
    v35 = irr_dict[key_35[0]]
    v6p = irr_dict[key_6p[0]]

    monotonic = (v12 < v35) and (v35 < v6p) and (v12 > 1.0)
    return monotonic, (v12, v35, v6p)

is_monotonic, irr_values = check_monotonicity(irr)
print(f"Monotonic IRR ordering: {is_monotonic}")
print(f"IRR(1-2)={irr_values[0]:.4f}, IRR(3-5)={irr_values[1]:.4f}, IRR(6+)={irr_values[2]:.4f}")
```

### FR-08: Adjacent Contrast Testing (Bonferroni)

```python
# 3 adjacent contrasts: 0 vs 1-2, 1-2 vs 3-5, 3-5 vs 6+
# Use t_test_pairwise with Bonferroni correction (α/3 = 0.0167)
pw = result_cat.t_test_pairwise('C(tag_count_cat)', method='bonferroni')
pw_df = pw.result_frame

# Count significant adjacent contrasts (Bonferroni-corrected)
# Focus on adjacent pairs only (not all-vs-all)
print("Adjacent contrast results (Bonferroni-corrected):")
print(pw_df[['coef', 'std err', 't', 'P>|t|', 'pvalue-bonferroni', 'reject-bonferroni']])

# Extract the 3 adjacent contrast p-values
adj_contrasts = {
    '1-2 vs 0': None,
    '3-5 vs 1-2': None,
    '6+ vs 3-5': None
}

bonf_alpha = 0.0167  # Bonferroni-corrected threshold

# Count passing adjacent contrasts
n_passing = sum(1 for row in ['1-2 vs 0', '3-5 vs 1-2', '6+ vs 3-5']
                if adj_contrasts.get(row) is not None and adj_contrasts[row] < bonf_alpha)

gate_pass = is_monotonic and (n_passing >= 2)
```

### FR-09: Robustness Checks (RC-6 and RC-7)

#### RC-6: Decade × Category Interaction Check
```python
formula_interact = ('N_tasks ~ C(tag_count_cat)*C(decade) '
                    '+ log_n_instances + log_n_features + age_years + age_sq')
result_rc6 = smf.negativebinomial(
    formula_interact, data=df, loglike_method='nb2'
).fit(method='bfgs', maxiter=200, disp=False)
print(f"RC-6 (decade interaction): AIC={result_rc6.aic:.2f}")
```

#### RC-7: No Decade FE (Attenuation Measurement)
```python
formula_no_fe = ('N_tasks ~ C(tag_count_cat) '
                 '+ log_n_instances + log_n_features + age_years + age_sq')
result_rc7 = smf.negativebinomial(
    formula_no_fe, data=df, loglike_method='nb2'
).fit(method='bfgs', maxiter=200, disp=False)

# Compare IRRs: with vs without decade FE
irr_no_fe = {k: np.exp(result_rc7.params[k]) for k in result_rc7.params.index if 'tag_count_cat' in k}
print("RC-7 (no decade FE) IRRs:", {k: round(v, 4) for k, v in irr_no_fe.items()})
```

### FR-10: Gate Evaluation and Results Export

```python
gate_result = {
    'gate': 'SHOULD_WORK',
    'hypothesis': 'H-M3',
    'is_monotonic': is_monotonic,
    'n_adjacent_contrasts_passing': n_passing,
    'bonferroni_alpha': bonf_alpha,
    'passed': gate_pass,
    'result': 'PASS' if gate_pass else 'INFORMATIVE_NEGATIVE',
    'irr_by_category': {k.replace('C(tag_count_cat)[T.', '').rstrip(']'): round(v, 4) for k, v in irr.items()},
    'ci_lower': {k.replace('C(tag_count_cat)[T.', '').rstrip(']'): round(v, 4) for k, v in ci_lower.items()},
    'ci_upper': {k.replace('C(tag_count_cat)[T.', '').rstrip(']'): round(v, 4) for k, v in ci_upper.items()},
    'pvalues': {k.replace('C(tag_count_cat)[T.', '').rstrip(']'): float(v) for k, v in pvals.items()},
    'n_corpus': int(len(df)),
    'bin_counts': bin_counts.to_dict()
}

import json, os
os.makedirs('docs/youra_research/h-m3/results', exist_ok=True)
with open('docs/youra_research/h-m3/results/primary_results.json', 'w') as f:
    json.dump(gate_result, f, indent=2)
```

### FR-11: Figure Generation

- **Fig 1 (MANDATORY):** Gate metrics bar chart — IRR per category (0, 1-2, 3-5, 6+) with 95% CI error bars; horizontal reference lines at IRR=1.0 and IRR=1.1 (H-E1 threshold)
- **Fig 2:** Dose-Response Plot — IRR by category colored by adjacent contrast significance (green=sig, orange=marginal, red=not sig)
- **Fig 3:** Category Distribution — bar chart of N per tag_count_cat bin
- **Fig 4:** Adjacent Contrast Forest Plot — 3 adjacent contrasts with Bonferroni-corrected CIs
- **Fig 5:** Attenuation Comparison — IRR with vs without C(decade) FE (RC-7)
- **Save location:** `docs/youra_research/h-m3/figures/`
- **Format:** PNG, 300 DPI

---

## 4. Data Specification

### Primary Dataset
| Field | Value |
|-------|-------|
| Name | OpenML Dataset Corpus — Full Corpus with Categorical Tag Bins |
| Source | H-E1 Phase 4 preprocessed parquet |
| Path | `docs/youra_research/h-e1/results/preprocessed.parquet` |
| N | 5,217 datasets (N_tasks ≥ 1 filter from H-E1) |
| Unit | One row per OpenML dataset |
| DV | N_tasks (count of registered ML tasks, integer ≥ 1) |
| IV | tag_count_cat: categorical bins ("0", "1-2", "3-5", "6+"), reference = "0" |
| Controls | log_n_instances, log_n_features, age_years, age_sq, C(decade) |

**Expected bin distribution (from H-M2 context):**
- Bin "0" (has_tags=0): ~2,592 datasets (49.7%)
- Bin "1-2": subset of ~2,625 tagged with tag_count 1 or 2
- Bin "3-5": tagged datasets with tag_count 3-5
- Bin "6+": tagged datasets with tag_count ≥ 6

**No manual download required** — full corpus reused from H-E1 Phase 4.

### Data Quality Requirements
- Verify N=5,217 total (all bins combined)
- Verify bin "0" has both has_tags=0 datasets AND zero-count edge cases
- Check no NaN in controls (log_n_instances, age_years, etc.)
- Report actual bin distribution (N per category)

---

## 5. Baseline Models

| Model | Formula | Dataset | Purpose |
|-------|---------|---------|---------|
| Poisson (controls-only) | N_tasks ~ controls | Full (N=5,217) | CT overdispersion pre-test |
| NB-2 (controls-only) | N_tasks ~ controls | Full (N=5,217) | Baseline LLF |
| NB-2 (binary H-E1 ref) | N_tasks ~ has_tags + controls | Full (N=5,217) | Reference binary effect |
| NB-2 (proposed, categorical) | N_tasks ~ C(tag_count_cat) + controls | Full (N=5,217) | Primary gate model |
| NB-2 (RC-6, decade interaction) | N_tasks ~ C(tag_count_cat)*C(decade) + controls | Full | Decade specificity check |
| NB-2 (RC-7, no decade FE) | N_tasks ~ C(tag_count_cat) + log controls | Full | Attenuation check |

**Controls in all models:** log_n_instances, log_n_features, age_years, age_sq

---

## 6. Evaluation Metrics

### Primary Gate Metrics (SHOULD_WORK)
| Metric | Threshold | Role |
|--------|-----------|------|
| Monotonic IRR ordering | IRR(1-2) < IRR(3-5) < IRR(6+), all > 1 | Gate condition 1 |
| Adjacent contrasts significant | ≥2/3 p < 0.0167 (Bonferroni) | Gate condition 2 |
| Overall Wald test for C(tag_count_cat) | p < 0.05 | Quality check |

### Secondary Metrics
| Metric | Purpose |
|--------|---------|
| IRR for each category (vs reference "0") | Effect size by bin |
| 95% CI per category | Precision of dose-response estimates |
| All 3 adjacent contrast p-values (raw + Bonferroni) | Dose-response resolution |
| Attenuation ratio (no FE / with FE) per category | RC-7 decade FE impact |
| CT LR stat | Confirms NB-2 appropriateness |
| N per bin | Sample size distribution |

### Gate Logic
```python
gate_pass_full = is_monotonic and (n_adj_passing == 3)
gate_pass_partial = is_monotonic and (n_adj_passing == 2)
gate_fail = (not is_monotonic) or (n_adj_passing < 2)
```

---

## 7. Non-Functional Requirements

### NFR-01: Correctness
- Use `statsmodels.formula.api.negativebinomial` with `loglike_method='nb2'`
- BFGS optimizer (`method='bfgs'`, `maxiter=200`) — confirmed convergent in H-E1, H-M1, H-M2
- Reference category: "0" (patsy default with `C(tag_count_cat)`)
- Adjacent contrast testing via `result.t_test_pairwise('C(tag_count_cat)', method='bonferroni')`
- IRR CIs from `result.conf_int()` (Wald intervals)

### NFR-02: Reproducibility
- Load from H-E1 parquet — deterministic preprocessing
- MLE-based NB-2 is deterministic (no random seeds)
- Save all results to `h-m3/results/primary_results.json`
- Categorical bins defined by fixed `pd.cut` boundaries (reproducible)

### NFR-03: Performance
- Parquet load: < 1 second
- Each NB-2 fit: < 5 minutes (N=5,217 with categorical dummies + decade FE)
- Total runtime: < 20 minutes (5 models including RC-6, RC-7)

### NFR-04: Code Organization
```
h-m3/
├── code/
│   ├── 01_preprocess.py          # FR-01, FR-02, FR-03 (load, bins, controls)
│   ├── 02_fit_models.py          # FR-04, FR-05, FR-06, FR-07, FR-08, FR-09 (all models + contrasts)
│   ├── 03_generate_figures.py    # FR-11 (5 figures)
│   └── 04_evaluate_gate.py       # FR-10 (gate eval + results export)
├── figures/                      (created by FR-11)
└── results/
    └── primary_results.json      (created by FR-10)
```

### NFR-05: Dependency on H-E1, H-M1, H-M2
- MUST verify H-E1 and H-M1 gate PASS before proceeding
- MUST load from `h-e1/results/preprocessed.parquet` as primary data source
- H-M2 context informs expected IRR range (IRR_P2=1.5332 → expect similar categorical IRRs)
- No refitting of prior models — only categorical IV derivation and new contrasts

---

## 8. Success Criteria

### Phase 3 Success (Implementation Planning)
- ✅ PRD, Architecture, Logic, Config documents complete
- ✅ 03_tasks.yaml generated within FULL tier budget (≤30 tasks)

### Phase 4 Success (Code + Gate)
- ✅ Full corpus loaded (N=5,217 verified)
- ✅ tag_count_cat bins derived (all 4 bins non-empty)
- ✅ NB-2 categorical model converges with BFGS
- ✅ Gate evaluated: monotonic ordering AND ≥2/3 adjacent contrasts p < 0.0167
- ✅ 5 figures generated (Fig 1 mandatory)
- ✅ Results saved to primary_results.json

### Failure Conditions
- NB-2 fails to converge → try Nelder-Mead; flag issue
- All datasets in bins "3-5" or "6+" have identical N_tasks → degenerate model
- Less than 10 datasets in any bin → report and consider merging bins

---

## 9. Dependencies

### Python Packages
```
statsmodels>=0.14
numpy>=1.24
pandas>=2.0
scipy>=1.10
matplotlib>=3.7
patsy>=0.5
pyarrow>=11.0   # for parquet loading
```

### H-E1 Dependencies (CRITICAL)
```
docs/youra_research/h-e1/results/preprocessed.parquet  # primary data source
docs/youra_research/h-e1/code/data/h_e1/openml_dataset_corpus.csv  # CSV fallback
docs/youra_research/h-e1/04_validation.md              # H-E1 gate confirmation
```

### H-M1, H-M2 Dependencies (Context)
```
docs/youra_research/h-m1/results/primary_results.json  # mechanism confirmation
docs/youra_research/h-m2/results/primary_results.json  # dose-response baseline (IRR_P2=1.5332)
```

### No DL Frameworks Required
Pure statistical regression study — no PyTorch, TensorFlow, or GPU needed.

---

## 10. Scope Exclusions

- No causal inference (observational census study)
- No new data collection (H-E1 parquet reused)
- No prediction task (hypothesis testing only)
- No composite metadata score
- No new hyperparameter search (BFGS confirmed in H-E1 through H-M2)
- No binary or continuous IV analysis (H-E1 and H-M2 covered those)
- No OpenML API calls unless parquet is missing

---

*stepsCompleted: [Executive Summary, Problem Statement, Functional Requirements, Data Specification, Baselines, Metrics, NFRs, Success Criteria, Dependencies, Scope Exclusions]*
