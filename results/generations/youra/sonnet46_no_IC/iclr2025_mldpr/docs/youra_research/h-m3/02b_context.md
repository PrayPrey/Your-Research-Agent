# Per-Hypothesis Context: H-M3

**Generated:** 2026-08-05
**Source:** 02b_verification_plan.md (JIT extraction by Phase 2C step-01)
**Hypothesis ID:** h-m3

---

## Hypothesis Info

- **ID:** H-M3
- **Type:** MECHANISM
- **Gate:** SHOULD_WORK
- **Statement:** Under OpenML context, if datasets are grouped by tag count categories (0, 1-2, 3-5, 6+), then each higher tag count category will have significantly more N_tasks than the previous category (monotonic dose-response), because the Discovery → Task Creation pathway amplifies with additional search pathways.

**Rationale:** P3 tests the full dose-response structure of the FAIR F1 mechanism: does the adoption effect scale monotonically with tag count? Non-monotonic patterns or insignificant adjacent contrasts would indicate binary threshold is the key mechanism, not continuous dose.

---

## Variables

- **Independent:** tag_count_categorical (0, 1-2, 3-5, 6+) — four-level categorical
- **Dependent:** N_tasks (count of distinct ML tasks)
- **Controlled:** log_n_instances, log_n_features, age_years, age_sq, C(decade)

---

## Experimental Setup

**Dataset:**
- Name: OpenML Dataset Corpus — categorical tag bins (0, 1-2, 3-5, 6+)
- Type: standard (programmatic-api reuse)
- Source: OpenML API via openml-python (full corpus N=5,217)
- Path: h-e1/code/data/h_e1/openml_dataset_corpus.csv (also h-e1/results/preprocessed.parquet)
- Hypothesis Fit: Full corpus N=5,217 (all N_tasks≥1); same as H-E1/H-M1/H-M2 ensuring continuity. Bin derivation: tag_count_cat = pd.cut(tag_count, bins=[-1,0,2,5,inf], labels=["0","1-2","3-5","6+"])

**Model:**
- Name: NB-2 with C(tag_count_cat) dummies (reference category = "0")
- Type: count regression
- Source: statsmodels.formula.api.negativebinomial (loglike_method='nb2')
- Hypothesis Fit: DV (N_tasks) is overdispersed count; NB-2 confirmed appropriate (CT LR=7356 from H-E1); C(tag_count_cat) dummies replace continuous IV to test categorical dose-response

---

## Success Criteria

- **Primary (Full):** Monotonic IRR ordering (IRR(0) < IRR(1-2) < IRR(3-5) < IRR(6+)) AND all 3 adjacent contrasts p < 0.0167 (Bonferroni α/3)
- **Partial:** Monotonic ordering with ≥2/3 adjacent contrasts p < 0.0167

---

## Verification Protocol

1. Derive tag_count_cat bins: 0 → "0", 1-2 → "1-2", 3-5 → "3-5", 6+ → "6+"; report cell sizes.
2. Fit NB-2: `smf.negativebinomial('N_tasks ~ C(tag_count_cat) + log_n_instances + log_n_features + age_years + age_sq + C(decade)', data=df).fit(method='bfgs')`
3. Extract IRR per category: exp(coef for each tag_count_cat level vs. reference "0").
4. Test monotonic ordering: IRR(0) < IRR(1-2) < IRR(3-5) < IRR(6+).
5. Test adjacent contrasts (3 contrasts): 0 vs 1-2, 1-2 vs 3-5, 3-5 vs 6+; apply Bonferroni (α/3=0.0167).

---

## Prerequisites

- H-E1: COMPLETED (MUST_WORK PASS — IRR=1.2263, CI=[1.1681,1.2873], p=1.87e-16)
- H-M1: COMPLETED (MUST_WORK PASS — has_tags survives C(decade) FE, attenuation_ratio=1.122)
- H-M2: COMPLETED (SHOULD_WORK PASS — IRR_P2=1.5332, CI=[1.4680,1.6014], p=1.28e-82)

---

## Key Context from Previous Hypotheses

- H-E1 preprocessed.parquet available at h-e1/results/preprocessed.parquet (N=5,217 rows)
- BFGS optimizer confirmed convergent for NB-2 on this corpus
- CT LR=7356 confirms NB-2 strongly preferred over Poisson
- Cramér's V=0.823 for has_tags-decade correlation (RC-3 documented; attenuation ratio=1.122 for H-E1)
- H-M2 showed log(tag_count+1) IRR_P2=1.5332 on tagged subset → strong dose signal; H-M3 tests categorical structure on full corpus

---

## Gate Condition

**Type:** SHOULD_WORK
**Pass:** Monotonic IRR ordering AND ≥2/3 adjacent contrasts p < 0.0167
**Fail Action:** DOCUMENT — functional form is binary threshold, not dose-response; supports simpler FAIR F1 model

---

## Failure Response

IF fails: DOCUMENT — functional form is binary threshold, not dose-response; supports simpler FAIR F1 model (tag presence = search graph membership, not graded). Continue to Phase 4.5 synthesis.
