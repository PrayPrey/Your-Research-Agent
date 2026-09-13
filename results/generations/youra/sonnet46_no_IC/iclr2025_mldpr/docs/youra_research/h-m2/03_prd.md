# PRD: H-M2 — Tag Count Dose-Response → Task Run Count (NB-2 Mechanism PoC)

**Hypothesis ID:** H-M2
**Type:** MECHANISM (PoC)
**Gate:** SHOULD_WORK
**Date:** 2026-08-05
**Phase 2C Source:** h-m2/02c_experiment_brief.md
**Tier:** FULL (≤30 tasks)
**Base Hypothesis:** H-E1 (MUST_WORK PASS — IRR=1.2263, p=1.87e-16), H-M1 (MUST_WORK PASS — mechanism confirmed)

---

## 1. Executive Summary

H-M2 tests whether the number of keyword tags attached to an OpenML dataset has a continuous dose-response relationship with the number of registered ML tasks (N_tasks). Within the tagged subset (has_tags=1, N≈2,625), we fit a Negative Binomial Regression Type 2 (NB-2) with `log(tag_count+1)` as the independent variable, controlling for dataset size, age (quadratic), and decade-of-upload fixed effects. Success requires IRR_P2 (for log_tag_count_p1) with 95% CI lower ≥ 1.05 AND p < 0.05.

**Gate type is SHOULD_WORK** — an informative negative (CI_lower < 1.05) is scientifically valid: it would confirm that binary tag presence (not count) is the full FAIR F1 signal, consistent with OpenML's 0/1 search indexing architecture.

This is a continuation experiment building on H-E1 infrastructure. New work: filter to has_tags=1 subset, derive log(tag_count+1) IV, refit NB-2, produce dose-response diagnostics.

---

## 2. Problem Statement

**Research Question:** Among tagged OpenML datasets (has_tags=1, N≈2,625), does having more keyword tags (higher log(tag_count+1)) predict significantly more registered ML tasks (N_tasks), after controlling for dataset size, age, and decade?

**Mechanism Chain:** More keyword tags → More search pathways in OpenML tag index → Higher discovery probability → More registered ML tasks (N_tasks)

**Null (H₀):** β_log_tag_count_p1 = 0 (tag count has no dose-response effect above binary threshold)

**Alternative (H₁):** IRR_P2 = exp(β_log_tag_count_p1) with 95% CI lower ≥ 1.05 AND p < 0.05

**Gate Condition (SHOULD_WORK):** Informative negative is acceptable — binary threshold may be the full FAIR F1 signal.

**Prerequisites Confirmed:**
- H-E1: IRR=1.2263 (95% CI: [1.1681, 1.2873]), p=1.87e-16 — MUST_WORK PASS
- H-M1: has_tags survives C(decade) FE (p=1.87e-16), attenuation_ratio=1.122 — mechanism STRONG

**Subset Rationale:** Restricting to has_tags=1 removes zero-tag datasets, eliminating collinearity between log(tag_count+1) and has_tags binary. Tests whether dose-response exists above the binary threshold.

---

## 3. Functional Requirements

### FR-01: Load and Filter to Tagged Subset

- **What:** Load preprocessed H-E1 parquet, filter to has_tags=1 subset
- **Primary path:** `docs/youra_research/h-e1/results/preprocessed.parquet`
- **Fallback:** Load raw CSV `h-e1/code/data/h_e1/openml_dataset_corpus.csv` and re-run preprocessing
- **Filter:** `df_tagged = df[df['has_tags'] == 1].copy()`
- **Verify:** N≈2,625 (expected 50.3% of 5,217)
- **Required columns:** N_tasks, tags, n_instances, n_features, upload_date (or pre-derived controls)

```python
import pandas as pd
import numpy as np

# Primary path
df = pd.read_parquet('docs/youra_research/h-e1/results/preprocessed.parquet')
df_tagged = df[df['has_tags'] == 1].copy()

print(f"Tagged subset N={len(df_tagged)}")  # expect ~2,625
assert len(df_tagged) > 500, f"Subset too small: {len(df_tagged)}"
```

### FR-02: Derive Continuous IV — log(tag_count+1)

- **tag_count derivation:** Count commas in tags string + 1 (handles single-tag case)
- **IV:** `log_tag_count_p1 = log(tag_count + 1)` (natural log, +1 for zero safety — not needed in has_tags=1 subset but applied for consistency)
- **Validate:** tag_count ≥ 1 for all rows in tagged subset (by definition of has_tags=1)

```python
# Derive tag_count from tags field
df_tagged['tag_count'] = df_tagged['tags'].str.count(',') + 1

# Derive log IV
df_tagged['log_tag_count_p1'] = np.log(df_tagged['tag_count'] + 1)

# Report distribution
print(f"tag_count: min={df_tagged['tag_count'].min()}, max={df_tagged['tag_count'].max()}, "
      f"mean={df_tagged['tag_count'].mean():.2f}, median={df_tagged['tag_count'].median():.0f}")
print(f"log_tag_count_p1: min={df_tagged['log_tag_count_p1'].min():.3f}, "
      f"max={df_tagged['log_tag_count_p1'].max():.3f}, mean={df_tagged['log_tag_count_p1'].mean():.3f}")
```

### FR-03: Collinearity Pre-Check (RC-3 Analog)

- Check Spearman correlation between `log_tag_count_p1` and `decade` (numeric)
- Check mean tag_count by decade (to diagnose potential temporal confounding)
- Log result; proceed regardless (informational diagnostic)

```python
from scipy.stats import spearmanr

decade_numeric = df_tagged['decade'].astype(int)
rho, p_rho = spearmanr(df_tagged['log_tag_count_p1'], decade_numeric)
print(f"Spearman rho(log_tag_count_p1, decade)={rho:.3f}, p={p_rho:.3e}")
print(df_tagged.groupby('decade')['tag_count'].agg(['mean', 'median', 'count']))
```

### FR-04: Overdispersion Check on Tagged Subset (CT LR Test)

- Fit Poisson controls-only on df_tagged
- Fit NB-2 controls-only on df_tagged
- Compute LR stat = 2*(llf_NB2 − llf_Poisson) ~ chi²(1)
- Expected: LR >> 3.84 (overdispersion confirmed in full corpus; expected to hold in subset)

```python
import statsmodels.formula.api as smf

controls = 'log_n_instances + log_n_features + age_years + age_sq + C(decade)'
formula_baseline = f'N_tasks ~ {controls}'

poisson_baseline = smf.poisson(formula_baseline, data=df_tagged).fit(method='bfgs', disp=False)
nb2_baseline = smf.negativebinomial(formula_baseline, data=df_tagged, loglike_method='nb2').fit(
    method='bfgs', disp=False)

lr_stat = 2 * (nb2_baseline.llf - poisson_baseline.llf)
print(f"CT LR={lr_stat:.2f} (threshold 3.84 → NB-2 appropriate if LR >> 3.84)")
```

### FR-05: Baseline Model (Controls-Only NB-2 on Tagged Subset)

```python
baseline_model = smf.negativebinomial(
    formula_baseline, data=df_tagged, loglike_method='nb2'
).fit(method='bfgs', disp=False)
print(f"Baseline LLF={baseline_model.llf:.2f}, AIC={baseline_model.aic:.2f}")
```

Purpose: Establishes counterfactual for tagged datasets without tag-count dose-response.

### FR-06: Primary NB-2 Regression — log(tag_count+1) IV (Proposed Model)

```python
formula_proposed = ('N_tasks ~ log_tag_count_p1 '
                    '+ log_n_instances + log_n_features '
                    '+ age_years + age_sq + C(decade)')

result_p2 = smf.negativebinomial(
    formula_proposed, data=df_tagged, loglike_method='nb2'
).fit(method='bfgs', maxiter=100, disp=False)

# Extract IRR and CI for primary IV
irr_p2 = np.exp(result_p2.params['log_tag_count_p1'])
ci_p2 = result_p2.conf_int()
ci_lower_p2 = np.exp(ci_p2.loc['log_tag_count_p1', 0])
ci_upper_p2 = np.exp(ci_p2.loc['log_tag_count_p1', 1])
pval_p2 = result_p2.pvalues['log_tag_count_p1']
```

**Gate check (SHOULD_WORK):**
- PASS: `ci_lower_p2 >= 1.05 AND pval_p2 < 0.05`
- INFORMATIVE NEGATIVE: `ci_lower_p2 < 1.05` → binary threshold is full FAIR F1 signal

### FR-07: Attenuation Analysis (Decade FE vs No FE)

```python
formula_no_fe = ('N_tasks ~ log_tag_count_p1 '
                 '+ log_n_instances + log_n_features + age_years + age_sq')

result_no_fe = smf.negativebinomial(
    formula_no_fe, data=df_tagged, loglike_method='nb2'
).fit(method='bfgs', maxiter=100, disp=False)

irr_no_fe = np.exp(result_no_fe.params['log_tag_count_p1'])
attenuation_ratio = irr_no_fe / irr_p2  # > 1 if decade FE attenuates
print(f"Attenuation ratio: {attenuation_ratio:.4f}")
```

### FR-08: Gate Evaluation and Results Export

```python
def evaluate_gate(irr_p2, ci_lower_p2, pval_p2, gate_irr_lower=1.05, gate_p=0.05):
    passed = (ci_lower_p2 >= gate_irr_lower) and (pval_p2 < gate_p)
    return {
        'gate': 'SHOULD_WORK',
        'passed': passed,
        'IRR_P2': round(irr_p2, 4),
        'CI_lower_P2': round(ci_lower_p2, 4),
        'CI_upper_P2': round(ci_upper_p2, 4),
        'p_value_P2': float(pval_p2),
        'result': 'PASS' if passed else 'INFORMATIVE_NEGATIVE',
        'n_tagged_subset': len(df_tagged),
        'attenuation_ratio': round(attenuation_ratio, 4)
    }
```

Save to: `docs/youra_research/h-m2/results/primary_results.json`

### FR-09: Figure Generation

- **Fig 1 (MANDATORY):** Gate metrics bar chart — IRR_P2 with 95% CI error bars vs threshold line at 1.05; annotate pass/fail status
- **Fig 2:** Tag count distribution — histogram of tag_count in tagged subset; log scale x-axis if skewed
- **Fig 3:** Partial regression plot (added variable plot) — log_tag_count_p1 vs log(N_tasks) controlling for confounders
- **Fig 4:** IRR comparison forest plot — log_tag_count_p1 IRR with/without decade FE (attenuation check)
- **Save location:** `docs/youra_research/h-m2/figures/`
- **Format:** PNG, 300 DPI

---

## 4. Data Specification

### Primary Dataset
| Field | Value |
|-------|-------|
| Name | OpenML Dataset Corpus — Tagged Subset (has_tags=1) |
| Source | H-E1 Phase 4 preprocessed parquet |
| Path | `docs/youra_research/h-e1/results/preprocessed.parquet` |
| N | ≈2,625 datasets (has_tags=1 filter from N=5,217) |
| Unit | One row per OpenML dataset |
| DV | N_tasks (count of registered ML tasks, integer ≥ 1) |
| IV | log_tag_count_p1 = log(tag_count + 1) (continuous) |
| Controls | log_n_instances, log_n_features, age_years, age_sq, C(decade) |

**No manual download required** — data reused from H-E1 Phase 4. CSV fallback available.

### Key Statistics (from H-E1)
- Full corpus N = 5,217 (N_tasks ≥ 1 filter)
- Tagged subset (has_tags=1): N≈2,625 (50.3% of full corpus)
- tag_count: min=1 (by has_tags=1 definition); max and distribution to be reported at runtime
- Decades: predominantly 2010s (2010s had high tagging rates per H-M1)

### Data Quality Requirements
- Verify N≈2,625 in tagged subset
- Verify tag_count ≥ 1 for all rows (by definition of has_tags=1 filter)
- Check for NaN in derived controls (log_n_instances, age_years)
- Report tag_count distribution summary statistics

---

## 5. Baseline Models

| Model | Formula | Dataset | Purpose |
|-------|---------|---------|---------|
| NB-2 (controls-only, baseline) | N_tasks ~ controls | df_tagged | Overdispersion check + baseline LLF |
| NB-2 (proposed + decade FE) | N_tasks ~ log_tag_count_p1 + controls + C(decade) | df_tagged | Primary gate model |
| NB-2 (proposed, no decade FE) | N_tasks ~ log_tag_count_p1 + controls | df_tagged | Attenuation analysis |

**Controls in all models:** log_n_instances, log_n_features, age_years, age_sq

---

## 6. Evaluation Metrics

### Primary Gate Metrics (SHOULD_WORK)
| Metric | Threshold | Role |
|--------|-----------|------|
| IRR_P2 = exp(β_log_tag_count_p1) | — (reported) | Effect size |
| CI_lower_P2 | ≥ 1.05 | Gate condition |
| Wald p-value | < 0.05 | Significance gate |

### Secondary Metrics
| Metric | Purpose |
|--------|---------|
| CI_upper_P2 | Precision of dose-response estimate |
| Attenuation ratio (no FE / with FE) | Decade FE impact on tag-count coefficient |
| Spearman rho (log_tag_count_p1 × decade) | RC-3 analog diagnostic |
| CT LR stat (on tagged subset) | Confirms NB-2 over Poisson in subset |
| Delta LLF (proposed vs baseline) | Marginal dose-response contribution |
| N (tagged subset) | Sample size confirmation |

### Gate Logic
```python
gate_passed = (ci_lower_p2 >= 1.05) and (pval_p2 < 0.05)
result_label = 'PASS' if gate_passed else 'INFORMATIVE_NEGATIVE'
# INFORMATIVE_NEGATIVE: binary threshold is full FAIR F1 signal — document and proceed to H-M3
```

---

## 7. Non-Functional Requirements

### NFR-01: Correctness
- Use `statsmodels.formula.api.negativebinomial` with `loglike_method='nb2'`
- BFGS optimizer (`method='bfgs'`, `maxiter=100`) — confirmed convergent in H-E1
- Derive log_tag_count_p1 as `np.log(tag_count + 1)` — natural log
- IRR CIs from `result.conf_int()` (Wald intervals)

### NFR-02: Reproducibility
- Load from H-E1 parquet — deterministic preprocessing
- MLE-based NB-2 is deterministic (no random seeds needed)
- Save all results to `h-m2/results/primary_results.json`

### NFR-03: Performance
- Parquet load + filter: < 1 second
- Each NB-2 fit: < 3 minutes (N≈2,625, smaller than full corpus)
- Total runtime: < 15 minutes

### NFR-04: Code Organization
```
h-m2/
├── code/
│   ├── 01_preprocess.py          # FR-01, FR-02, FR-03 (load, filter, derive IV, collinearity check)
│   ├── 02_fit_models.py          # FR-04, FR-05, FR-06, FR-07 (models, attenuation)
│   ├── 03_generate_figures.py    # FR-09 (4 figures)
│   └── 04_evaluate_gate.py       # FR-08 (gate eval + results export)
├── figures/                      (created by FR-09)
└── results/
    └── primary_results.json      (created by FR-08)
```

### NFR-05: Dependency on H-E1 and H-M1
- MUST verify H-E1 gate PASS before proceeding
- MUST load from `h-e1/results/preprocessed.parquet` as primary data source
- H-M1 gate PASS confirms mechanism context (attenuation documented, non-fatal)
- No refitting of H-E1 models — only subset restriction and new IV derivation

---

## 8. Success Criteria

### Phase 3 Success (Implementation Planning)
- ✅ PRD, Architecture, Logic, Config documents complete
- ✅ 03_tasks.yaml generated within FULL tier budget (≤30 tasks)

### Phase 4 Success (Code + Gate)
- ✅ Tagged subset loaded (N≈2,625 confirmed)
- ✅ log_tag_count_p1 derived correctly (tag_count ≥ 1 for all rows)
- ✅ NB-2 proposed model converges with BFGS
- ✅ Gate evaluated: CI_lower_P2 ≥ 1.05 AND p < 0.05 → PASS; else INFORMATIVE_NEGATIVE
- ✅ Attenuation ratio computed (with vs without decade FE)
- ✅ 4 figures generated (Fig 1 mandatory)
- ✅ Results saved to primary_results.json

### Failure Conditions
- NB-2 fails to converge → try Nelder-Mead; flag issue
- N (tagged subset) < 500 → report unexpected sample size issue
- All tag_counts = 1 → degenerate IV; report and treat as INFORMATIVE_NEGATIVE

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
docs/youra_research/h-e1/results/preprocessed.parquet  # primary data (has_tags, controls)
docs/youra_research/h-e1/code/data/h_e1/openml_dataset_corpus.csv  # CSV fallback
docs/youra_research/h-e1/04_validation.md              # H-E1 gate confirmation
```

### H-M1 Dependencies (Context)
```
docs/youra_research/h-m1/results/primary_results.json  # attenuation context
```

### No DL Frameworks Required
Pure statistical continuation study — no PyTorch, TensorFlow, or GPU.

---

## 10. Scope Exclusions

- No causal inference (observational census study)
- No new data collection (H-E1 parquet reused)
- No H-M3 analysis (separate categorical dose-response — out of scope for H-M2)
- No composite metadata score
- No new hyperparameter search (BFGS confirmed optimal in H-E1)
- No reanalysis of full corpus (H-M2 explicitly restricts to has_tags=1 subset)

---

*stepsCompleted: [Executive Summary, Problem Statement, Functional Requirements, Data Specification, Baselines, Metrics, NFRs, Success Criteria, Dependencies, Scope Exclusions]*
