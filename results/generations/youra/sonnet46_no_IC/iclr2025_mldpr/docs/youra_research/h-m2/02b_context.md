# Phase 2B Context: H-M2

**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Generated:** 2026-08-05 (JIT from 02b_verification_plan.md)

---

## Hypothesis Statement

Under OpenML context (has_tags=1 subset, N varies), if a dataset has more keyword tags (higher log(tag_count+1)), then it will have more registered ML tasks (N_tasks), because more tags create more search pathways leading to higher discovery probability, with NB-2 IRR for log(tag_count+1) having 95% CI lower >= 1.05 and p < 0.05.

## Hypothesis Type & Rationale

**Type:** MECHANISM — Step 2: Search Index Membership → Discovery Magnitude Effect

This tests whether tag count above the binary threshold provides additional predictive signal for adoption. If yes, it supports the discovery-probability gradient mechanism (more search pathways → more encounters). If not, binary threshold is the full signal (FAIR F1 operates as a 0/1 gate, not a dose-response relationship).

## Variables

- **Independent:** log_tag_count_plus1 = log(tag_count + 1)
- **Dependent:** N_tasks (count of distinct ML tasks)
- **Controlled:** log_n_instances, log_n_features, age_years, age_sq, C(decade)
- **Sample Restriction:** has_tags=1 only (avoids collinearity with has_tags binary IV)

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset
- **Name:** OpenML Dataset Corpus — tagged subset (has_tags=1)
- **Type:** standard (programmatic-api reuse)
- **Source:** OpenML API / h-e1 corpus cache
- **Path:** h-e1/code/data/h_e1/openml_dataset_corpus.csv (filter has_tags==1)
- **N (full corpus):** 5,217; **N (has_tags=1):** ~2,625 (50.3%)
- **Hypothesis Fit:** Subset restriction removes zero-tag datasets to isolate continuous tag count signal without collinearity with binary has_tags

### Model
- **Name:** NB-2 restricted to has_tags=1 subset
- **Type:** count regression (statsmodels smf.negativebinomial, loglike_method='nb2')
- **Source:** Statsmodels official implementation
- **Hypothesis Fit:** Same model family as H-E1 (NB-2 confirmed appropriate, CT LR=7356.36); restricting to tagged subset allows log(tag_count+1) as continuous IV without collinearity issues

## Verification Protocol (from Phase 2B)

1. Restrict to df_tagged = df[df.has_tags == 1]; report N (fraction of 5,217 with tags).
2. Derive tag_count = tags.str.count(',') + 1 for tagged rows; log_tag_count_p1 = log(tag_count + 1).
3. Report has_tags / log(tag_count+1) correlation in full sample (collinearity diagnostic).
4. Fit NB-2: `smf.negativebinomial('N_tasks ~ log_tag_count_p1 + log_n_instances + log_n_features + age_years + age_sq + C(decade)', data=df_tagged).fit(method='bfgs')`.
5. Compute IRR_P2 = exp(coef['log_tag_count_p1']); CI_lower_P2; check: IRR_P2 >= 1.05 AND CI_lower_P2 >= 1.05 AND p < 0.05.

## Success Criteria

- **Primary (PASS):** IRR_P2 95% CI lower >= 1.05 AND p < 0.05 → dose gradient exists above binary threshold
- **Null (informative negative):** CI_lower_P2 < 1.05 → binary threshold is the full FAIR F1 signal

## Gate

- **Type:** SHOULD_WORK
- **Pass:** IRR_P2 CI_lower >= 1.05 AND p < 0.05
- **Fail Action:** DOCUMENT as informative negative — binary has_tags captures the full FAIR F1 effect; dose-response does not extend beyond threshold

## Prerequisites

- H-E1: COMPLETED (IRR=1.2263, CI=[1.1681,1.2873], p=1.87e-16) ✅
- H-M1: COMPLETED (has_tags survives C(decade) FE, attenuation_ratio=1.122) ✅

## Key Risks

- **RC-3:** Cramér's V=0.823 between decade and has_tags (confirmed in H-E1). In tagged-only subset, decade-tag_count correlation may also be present — diagnose before model fitting.
- **Sample size reduction:** Restricting to has_tags=1 reduces N from 5,217 to ~2,625. Still statistically adequate for NB-2 with 6 predictors.
- **Informative null:** If CI_lower < 1.05, this is a valid scientific finding (binary threshold is the full FAIR F1 effect), not a failure requiring re-routing.
