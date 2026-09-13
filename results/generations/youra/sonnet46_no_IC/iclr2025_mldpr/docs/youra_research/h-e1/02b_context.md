# Phase 2B Context: H-E1

**Generated:** 2026-08-05 (JIT from 02b_verification_plan.md)
**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Gate:** MUST_WORK

---

## Hypothesis Statement

Under the OpenML platform context (N=5,217 datasets with N_tasks ≥ 1, cross-sectional corpus), if a dataset has keyword tags attached (has_tags=1 vs. has_tags=0), then it will have significantly more registered ML tasks (N_tasks), because keyword tags make datasets discoverable through OpenML's tag-indexed search (FAIR F1 mechanism), and discoverability drives researcher engagement and task creation.

Formally: In NB-2 regression of N_tasks on has_tags controlling for log(n_instances), log(n_features), age_years, age², C(decade), the IRR for has_tags will be ≥ 1.1 with 95% CI lower bound ≥ 1.1.

---

## Experimental Setup (from Phase 2A via Phase 2B)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | OpenML Dataset Corpus (h-e1 reuse) | N=5,217 active OpenML datasets with N_tasks≥1; contains tags field (parseable to has_tags + tag_count); same corpus as h-e1 ensuring methodological continuity |
| **Model** | Negative Binomial Type 2 (NB-2) | DV (N_tasks) is overdispersed count (CT LR=2222.68 from h-e1); NB-2 handles variance=μ+αμ² structure; BFGS optimizer achieves convergence |

**Dataset Details:**
- Source: OpenML API via openml-python (`list_datasets(output_format='dataframe')`)
- Path: `h-e1/code/data/h_e1/openml_dataset_corpus.csv`
- N: 5,217 datasets (filtered N_tasks ≥ 1)
- Key columns: dataset_id, N_tasks, tags, n_instances, n_features, upload_date

**Model Details:**
- Type: count regression (statsmodels)
- Source: `statsmodels.formula.api.negativebinomial(loglike_method='nb2')`
- Optimizer: BFGS (method='bfgs', confirmed convergent in h-e1)
- Formula: `N_tasks ~ has_tags + log_n_instances + log_n_features + age_years + age_sq + C(decade)`

---

## Variables

- **Independent Variable (IV):** `has_tags` (binary 0/1 — derived from tags field: non-null, non-empty = 1)
- **Dependent Variable (DV):** `N_tasks` (count of distinct ML tasks registered)
- **Controls:** `log_n_instances`, `log_n_features`, `age_years`, `age_sq`, `C(decade)`

---

## Success Criteria

- **Primary (MUST_WORK gate):** IRR ≥ 1.1 AND 95% CI lower bound ≥ 1.1 AND p < 0.05
- **Secondary (partial pass):** CI_lower ∈ [1.05, 1.1) — scientifically informative

---

## Verification Protocol

1. Load corpus CSV (N=5,217); derive `has_tags` from tags field (non-null, non-empty = 1)
2. Verify overdispersion: re-run Cameron-Trivedi LR test with has_tags model; expect LR stat >> 3.84
3. Pre-check has_tags-decade correlation: `df.groupby('decade')['has_tags'].mean()`
4. Fit NB-2: `smf.negativebinomial('N_tasks ~ has_tags + log_n_instances + log_n_features + age_years + age_sq + C(decade)', data=df).fit(method='bfgs')`
5. Compute IRR = exp(coef['has_tags']); CI_lower = exp(coef - 1.96*se); check: IRR ≥ 1.1 AND CI_lower ≥ 1.1 AND p < 0.05
6. Report RC suite: RC-4 (top-1% winsorization), RC-5 (tag_count≥1 restriction), RC-7 (continuous age-only vs decade FE)

---

## Gate Conditions

- **Gate Type:** MUST_WORK
- **Prerequisites:** None (foundation hypothesis)
- **Failure Response:** PIVOT — check has_tags-decade correlation; if fundamental failure (IRR not significant) → route to Phase 0

---

## Critical Risk

**R3 (Critical): Decade FE may absorb has_tags signal** — same failure mode as h-e1 composite score (IRR=1.014, p=0.19 under decade FE). Pre-check has_tags-decade correlation before full model fit.

---

## Source

Phase 2B Verification Plan: `02b_verification_plan.md` — Section 2.2 H-E1
