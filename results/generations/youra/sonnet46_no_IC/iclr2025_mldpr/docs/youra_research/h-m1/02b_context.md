# Phase 2B Context: H-M1

**Generated:** 2026-08-05 (JIT from 02b_verification_plan.md)
**Hypothesis ID:** h-m1
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## Hypothesis Statement

Under OpenML platform context, if a dataset has keyword tags (has_tags=1), then it will appear in tag-indexed search results (platform search graph membership), because OpenML's search engine indexes keyword tags as primary discovery keys (Vanschoren et al. 2014), operationally verified by H-E1's significant IRR supporting the search pathway activation mechanism.

The mechanism is verified when H-E1 IRR passes MUST_WORK gate AND the has_tags effect survives C(decade) fixed effects (p < 0.05 in decade-controlled model).

---

## Experimental Setup (from Phase 2A via Phase 2B)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | OpenML Dataset Corpus (h-e1 reuse) | N=5,217 active OpenML datasets with N_tasks≥1; same corpus as H-E1; no new data collection required |
| **Model** | Negative Binomial Type 2 (NB-2) — same as H-E1 | Reuse confirmed-appropriate model; CT LR=7356.36 confirms NB-2; BFGS optimizer convergent |

**Dataset Details:**
- Source: OpenML API / preprocessed parquet from H-E1 Phase 4
- Path: `h-e1/code/data/h_e1/openml_dataset_corpus.csv` (raw) OR `h-e1/results/preprocessed.parquet` (preferred)
- N: 5,217 datasets (filtered N_tasks ≥ 1)
- Key columns: dataset_id, N_tasks, has_tags, log_n_instances, log_n_features, age_years, age_sq, decade

**Model Details:**
- Type: count regression (statsmodels)
- Source: `statsmodels.formula.api.negativebinomial(loglike_method='nb2')`
- Optimizer: BFGS (method='bfgs', confirmed convergent)
- Formula: `N_tasks ~ has_tags + log_n_instances + log_n_features + age_years + age_sq + C(decade)`

---

## Variables

- **Independent Variable (IV):** `has_tags` (binary 0/1) — same as H-E1
- **Dependent Variable (DV):** `N_tasks` (count of distinct ML tasks, downstream proxy of search-driven adoption)
- **Controls:** `log_n_instances`, `log_n_features`, `age_years`, `age_sq`, `C(decade)`

---

## Success Criteria

- **Primary (MUST_WORK gate):** H-E1 IRR passes MUST_WORK gate AND has_tags effect survives decade FE (p < 0.05 regardless of IRR magnitude)
- **Secondary:** has_tags coefficient p < 0.05 in all model variants (with and without decade FE)

---

## Verification Protocol

1. Confirm H-E1 MUST_WORK gate PASSED (IRR=1.2263, CI_lower=1.1681, p=1.87e-16) — CONFIRMED from h-e1/04_validation.md
2. Load preprocessed parquet from H-E1: `h-e1/results/preprocessed.parquet`
3. Derive has_tags-decade correlation: `df.groupby('decade')['has_tags'].mean()` — already done (Cramér's V=0.823)
4. Extract H-E1 proposed model with decade FE: IRR=1.2263, p=1.87e-16 (already in results)
5. Fit model WITHOUT C(decade): `N_tasks ~ has_tags + log_n_instances + log_n_features + age_years + age_sq`
6. Compare IRR with vs. without decade FE — attenuation ratio already known: 1.1219
7. Verify has_tags p < 0.05 even with decade FE — CONFIRMED (p=1.87e-16)
8. Document mechanism support level and RC-3 attenuation interpretation

---

## Gate Conditions

- **Gate Type:** MUST_WORK
- **Prerequisites:** H-E1 (MUST_WORK gate must pass) — SATISFIED (h-e1 validated 2026-08-05)
- **Failure Response:** If decade FE fully absorbs has_tags (p ≥ 0.05): EXPLORE decade correlation; document as mechanism limitation

---

## Critical Risk

**R3 (Critical): Decade FE partially absorbs has_tags signal** — already confirmed from H-E1: Cramér's V=0.823, attenuation_ratio=1.122. The has_tags effect survives (p=1.87e-16) but is 12% smaller with decade FE. Documented as conservative lower bound.

---

## Source

Phase 2B Verification Plan: `02b_verification_plan.md` — Section 2.2 H-M1
