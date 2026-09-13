# PRD: H-E1 — Binary Keyword Tag Presence → Task Run Count (NB-2 Existence Test)

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Gate:** MUST_WORK
**Date:** 2026-08-05
**Phase 2C Source:** h-e1/02c_experiment_brief.md
**Tier:** LIGHT (≤15 tasks)

---

## 1. Executive Summary

This experiment tests whether binary keyword tag presence (`has_tags` = 1 vs 0) on OpenML datasets is positively associated with more registered ML tasks (N_tasks), with Incidence Rate Ratio ≥ 1.1. Using the existing cached OpenML corpus (N=5,217 datasets with N_tasks ≥ 1), we fit a Negative Binomial Regression Type 2 (NB-2) with `has_tags` binary as the independent variable, controlling for dataset size, age (quadratic), and decade-of-upload fixed effects. This is an observational census study using maximum likelihood estimation (BFGS) — no training/validation split. Success requires IRR ≥ 1.1 AND CI_lower ≥ 1.1 AND p < 0.05.

This is a FAIR F1 operationalization: keyword tag presence as a machine-readable metadata indicator enabling dataset findability/discovery.

---

## 2. Problem Statement

**Research Question:** Among OpenML datasets with at least one registered ML task (N=5,217), does having at least one keyword tag (`has_tags=1`) predict significantly more registered tasks (N_tasks), after controlling for structural factors (dataset size, age, decade)?

**Null Hypothesis (H₀):** β_has_tags = 0 (tag presence has no effect on N_tasks)

**Alternative (H₁):** IRR = exp(β_has_tags) ≥ 1.1 with 95% CI lower ≥ 1.1 and p < 0.05

**Gate Condition (MUST_WORK):** Pipeline terminates and routes to Phase 0 if gate fails.

**Historical Context:**
- Prior h-e1 episode used composite score (0–5), got IRR=1.076 — below 1.1 threshold
- RC-3 (decade FE) absorbed composite: IRR=1.014, p=0.19 — critical RC-3 risk
- Binary has_tags theoretically cleaner: platform search architecture indexes presence/absence
- Binary description presence (RC-2a analog): IRR=1.102 — supports binary IV approach

---

## 3. Functional Requirements

### FR-01: Data Loading from Cache
- **What:** Load existing OpenML corpus from cached CSV
- **How:** `pd.read_csv('h-e1/code/data/h_e1/openml_dataset_corpus.csv')`
- **Filter:** N_tasks ≥ 1 (already filtered in cache; verify N=5,217)
- **Fallback:** If CSV missing, collect via `openml.datasets.list_datasets(output_format='dataframe', status='active')`
- **Key columns required:** dataset_id, N_tasks, tags, n_instances, n_features, upload_date
- **Output:** Pandas DataFrame ready for feature engineering

### FR-02: Feature Engineering
- **IV (primary):**
  - `has_tags` = 1 if tags field is non-null and non-empty, else 0 (binary)
  - `tag_count` = number of tags (for robustness checks)
  - `log_tag_count_p1` = log(tag_count + 1)
- **Controls:**
  - `log_n_instances` = log(n_instances.clip(lower=1))
  - `log_n_features` = log(n_features.clip(lower=1))
  - `upload_year` = pd.to_datetime(upload_date).dt.year
  - `age_years` = 2026 − upload_year
  - `age_sq` = age_years²
  - `decade` = (upload_year // 10) * 10  (e.g., 2010, 2020)
- **Validation:** Verify has_tags has both 0 and 1 values; log distribution of tag counts

### FR-03: Pre-Check — RC-3 Risk Mitigation (Decade Correlation)
- Check `df.groupby('decade')['has_tags'].mean()` — flag if any decade is >90% tagged
- Compute Cramér's V or chi-square between has_tags and decade
- Log result; proceed regardless (RC-7 will directly compare age vs decade model)

### FR-04: Overdispersion Pre-test (Cameron-Trivedi LR Test)
- Fit Poisson with same formula as NB-2
- LR stat = 2*(llf_NB2 − llf_Poisson) ~ chi²(1)
- Expected: LR >> 3.84 (CT LR=2222.68 from prior h-e1 confirms NB-2 appropriate)
- Log result; proceed with NB-2 regardless if prior episode confirmed overdispersion

### FR-05: Baseline Model (Controls-Only NB-2)
```python
formula_baseline = 'N_tasks ~ log_n_instances + log_n_features + age_years + age_sq + C(decade)'
baseline = smf.negativebinomial(formula_baseline, data=df, loglike_method='nb2').fit(method='bfgs')
```
- Extract log-likelihood for comparison with proposed model

### FR-06: Primary NB-2 Regression (Proposed Model)
```python
formula_proposed = ('N_tasks ~ has_tags + log_n_instances + '
                    'log_n_features + age_years + age_sq + C(decade)')
result = smf.negativebinomial(formula_proposed, data=df, loglike_method='nb2').fit(
    method='bfgs', maxiter=100, disp=False)
```
- **Extract for `has_tags`:**
  - `irr = np.exp(result.params['has_tags'])`
  - `ci_lower = np.exp(result.conf_int().loc['has_tags', 0])`
  - `ci_upper = np.exp(result.conf_int().loc['has_tags', 1])`
  - `pval = result.pvalues['has_tags']`
- **Gate check:** `gate_pass = (irr >= 1.1) and (ci_lower >= 1.1) and (pval < 0.05)`

### FR-07: Robustness Check Suite

#### RC-4: Winsorized N_tasks
- Winsorize N_tasks at 99th percentile: `df['N_tasks_w'] = df['N_tasks'].clip(upper=np.percentile(df['N_tasks'], 99))`
- Refit proposed model with N_tasks_w as DV
- Report IRR and CI for has_tags

#### RC-5: Tagged-Only Subset Sensitivity
- Restrict to `tag_count >= 1` (all-tagged subset)
- Refit proposed model on this subset
- Purpose: Check if has_tags effect is driven by tag-count variation

#### RC-7: Age vs Decade FE Comparison
- Fit proposed model with age_years+age_sq only (no decade FE)
- Compare IRR for has_tags with vs without decade FE
- Quantify RC-3 risk: if decade FE reduces IRR_has_tags significantly, flag as limitation

### FR-08: Figure Generation
- **Fig 1 (MANDATORY):** Gate metrics bar chart — IRR of has_tags with 95% CI error bars vs threshold line at 1.1
- **Fig 2:** Forest plot — IRR with CI for all covariates in proposed model
- **Fig 3:** has_tags adoption by decade — bar chart of mean has_tags rate per decade (RC-3 visualization)
- **Fig 4:** RC suite comparison — IRR bar chart across primary, RC-4, RC-5, RC-7 models
- **Fig 5:** Observed vs predicted N_tasks scatter (log scale)
- **Save location:** `docs/youra_research/h-e1/figures/` (create if not exists)
- **Format:** PNG, 300 DPI

### FR-09: Gate Evaluation and Results Export
```python
gate_passed = (irr >= 1.1) and (ci_lower >= 1.1) and (pval < 0.05)
# Partial pass (scientifically informative, continue with qualified claim)
partial_pass = (1.05 <= ci_lower < 1.1) and (pval < 0.05)
```
- Save to `h-e1/results/primary_results.json`
- Log: gate_result (PASS/PARTIAL_PASS/FAIL), irr, ci_lower, ci_upper, pval

---

## 4. Data Specification

### Primary Dataset
| Field | Value |
|-------|-------|
| Name | OpenML Dataset Corpus (h-e1 reuse) |
| Source | Cached CSV from prior h-e1 episode |
| Collection method | Cached: `h-e1/code/data/h_e1/openml_dataset_corpus.csv` |
| N | 5,217 datasets (N_tasks ≥ 1) |
| Unit of analysis | One row per dataset |
| DV | N_tasks (count of registered ML tasks, integer ≥ 1) |
| IV | has_tags (binary: 1=has ≥1 keyword tag, 0=untagged) |

**Loading code:**
```python
df = pd.read_csv('h-e1/code/data/h_e1/openml_dataset_corpus.csv')
df = df[df['N_tasks'] >= 1].copy()  # Verify N=5,217
```

**Note:** Corpus already available. No manual download task required.

### Data Quality Requirements
- Verify N=5,217 after N_tasks ≥ 1 filter
- Check for NaN in n_instances, n_features, upload_date
- Verify has_tags has non-degenerate distribution (both 0s and 1s)

---

## 5. Baseline Models

| Model | Formula | Purpose |
|-------|---------|---------|
| Poisson (controls-only) | N_tasks ~ controls | CT overdispersion pre-test |
| NB-2 (controls-only) | N_tasks ~ controls | Baseline for marginal has_tags contribution |
| NB-2 (proposed) | N_tasks ~ has_tags + controls | Primary model |

**Controls in all models:** log_n_instances, log_n_features, age_years, age_sq, C(decade)

---

## 6. Evaluation Metrics

### Primary Gate Metrics (MUST_WORK)
| Metric | Threshold | Role |
|--------|-----------|------|
| IRR = exp(β_has_tags) | ≥ 1.1 | Required |
| CI_lower | ≥ 1.1 | Required (95% CI lower bound) |
| Wald p-value | < 0.05 | Required |

### Secondary Metrics
| Metric | Purpose |
|--------|---------|
| 95% CI upper bound | Precision of effect estimate |
| Overdispersion alpha | Confirms NB-2 appropriateness |
| LR test stat vs Poisson | Cameron-Trivedi overdispersion test |
| RC-4/5/7 IRR range | Coefficient stability |
| Delta log-likelihood | Marginal contribution of has_tags |
| AIC/BIC (proposed vs baseline) | Model fit comparison |

### Gate Logic
```python
gate_passed = (irr >= 1.1) and (ci_lower >= 1.1) and (pval < 0.05)
partial_pass = (1.05 <= ci_lower < 1.1) and (pval < 0.05)
```

---

## 7. Non-Functional Requirements

### NFR-01: Correctness
- Use `statsmodels.formula.api.negativebinomial` with `loglike_method='nb2'`
- Use BFGS optimizer (`method='bfgs'`, `maxiter=100`) — confirmed convergent from prior h-e1
- All p-values are two-tailed Wald tests (statsmodels default)
- IRR CIs from `result.conf_int()` (profile likelihood)

### NFR-02: Reproducibility
- No random seeds required (deterministic MLE)
- Cache corpus CSV; save intermediate results
- Pin package versions in requirements.txt

### NFR-03: Performance
- CSV load: < 1 second
- NB-2 fit: < 5 minutes (BFGS on N=5,217 with decade FE dummies)
- All 3 RC models: < 15 minutes total

### NFR-04: Code Organization
```
h-e1/
├── code/
│   ├── data/
│   │   └── h_e1/
│   │       └── openml_dataset_corpus.csv  (existing cache)
│   ├── 01_preprocess.py        # FR-01, FR-02, FR-03
│   ├── 02_fit_models.py        # FR-04, FR-05, FR-06, FR-07
│   ├── 03_generate_figures.py  # FR-08
│   └── 04_evaluate_gate.py     # FR-09
├── figures/                    (created by FR-08)
└── results/
    └── primary_results.json    (created by FR-09)
```

---

## 8. Success Criteria

### Phase 3 Success (Implementation Planning)
- ✅ PRD, Architecture, Logic, Config documents complete
- ✅ 03_tasks.yaml generated within LIGHT tier budget (≤15 tasks)

### Phase 4 Success (Code + Gate)
- ✅ Corpus loaded (N=5,217 verified)
- ✅ Feature engineering complete (has_tags, controls derived)
- ✅ NB-2 model converges with BFGS
- ✅ Gate passed: IRR ≥ 1.1 AND CI_lower ≥ 1.1 AND p < 0.05
- ✅ All 5 figures generated
- ✅ Results saved to primary_results.json

### Failure Conditions
- NB-2 fails to converge → try Nelder-Mead fallback; report in paper
- Gate fails (IRR < 1.1 or CI_lower < 1.1) → MUST_WORK failure → route to Phase 0
- Corpus CSV missing → collect via OpenML API (fallback in FR-01)

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
openml>=0.14   # only if CSV cache is missing
tqdm>=4.65
```

### External APIs
- OpenML REST API — only needed if CSV cache is missing (see FR-01 fallback)
- No authentication required for public datasets

### No DL Frameworks Required
Pure statistical regression study — no PyTorch, TensorFlow, or GPU needed.

---

## 10. Scope Exclusions

- No causal inference (observational census study only)
- No ML model comparison (not prediction task)
- No dataset download or content analysis
- H-M1, H-M2, H-M3 sub-hypotheses are out of scope for H-E1
- No composite metadata score (this episode uses binary has_tags IV only)

---

*stepsCompleted: [Executive Summary, Problem Statement, Functional Requirements, Data Specification, Baselines, Metrics, NFRs, Success Criteria, Dependencies, Scope Exclusions]*
