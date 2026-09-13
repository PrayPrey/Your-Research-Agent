# Phase 2B: Verification Plan
# H-Diversity-v1: Benchmark Submitter Diversity Predicts Plurality Displacement Hazard

Generated: 2026-08-03T00:00:00Z
Main Hypothesis ID: H-Diversity-v1
Gap: gap-3 — Theoretical Direction of Diversity-Displacement Relationship (HR<1 vs HR>1)

---

## Main Hypothesis

Under the h-e2 panel (87 tasks, 345 plurality-benchmark displacement events, 2015-2023, Papers With
Code), log_unique_paper_count_at_intro_z (log-transformed, z-standardized count of distinct paper_url
values per benchmark through plurality-introduction year from pwc-archive/evaluation-tables) significantly
predicts plurality benchmark displacement hazard in CoxPHFitter(penalizer=0.1) with |HR−1| ≥ 0.10 and
LRT p < 0.05, conditional on passing a 5-gate FAIL FAST pre-validation protocol (G0-G4).

**Effect direction is empirically determined:**
- HR < 1 → lock-in mechanism (diversity → stakeholder entrenchment → resistance to displacement)
- HR > 1 → saturation mechanism (diversity → overuse signal → accelerated community replacement)
- LRT p > 0.05 (gates pass) → meaningful null (rules out community-breadth predictor class)

---

## Sub-Hypothesis Inventory

### H-E1 — Data Pipeline & FAIL FAST Gate Validation (MUST_WORK)

**Statement:** pwc-archive/evaluation-tables paper_url column joined to h-e2 panel achieves ≥80%
coverage (G0), both diversity predictors are time-independent (G1-G2 partial_r²>0.01), the diversity
ratio has sufficient variance (G3 std>0.10), and all covariates have VIF<10 (G4).

**Prerequisites:** None (READY immediately)
**Gate:** MUST_WORK — all 5 gates must pass; failure routes to Attempt 12

**Gates (ordered, stop on first failure):**
- G0: ≥80% h-e2 benchmarks with non-null paper_url after task_path fuzzy join
- G1: partial_r²(log_unique_paper_count_at_intro_z vs [task_age, intro_year]) > 0.01
- G2: partial_r²(paper_diversity_ratio_at_intro_z vs [task_age, intro_year]) > 0.01
- G3: std(paper_diversity_ratio_at_intro) > 0.10 across joined h-e2 benchmarks
- G4: VIF < 10 for all covariates in Cox model (warn if 5-10, exclude if >10)

**Collinearity failsafe:** if Pearson r(log_count_z, diversity_ratio_z) > 0.95, use primary predictor only.

**Implementation notes:**
- Load evaluation-tables via `load_dataset('pwc-archive/evaluation-tables', split='train')`
- Join via task_path fuzzy matching (same slug space as h-e1, 95.5% prior coverage)
- Filter rows to ≤ plurality introduction year per benchmark before computing counts
- `unique_paper_count = df.groupby('task_path')['paper_url'].nunique()`
- `diversity_ratio = unique_count / total_rows_per_benchmark_at_intro`
- partial_r² computed via OLS residualization: regress predictor on temporal controls, take r² of residuals

---

### H-M1 — Primary Cox Regression (MUST_WORK)

**Statement:** log_unique_paper_count_at_intro_z significantly predicts plurality benchmark
displacement hazard in CoxPHFitter(penalizer=0.1) on h-e2 panel: LRT p < 0.05 AND |HR-1| ≥ 0.10.

**Prerequisites:** H-E1 (all 5 FAIL FAST gates passed)
**Gate:** MUST_WORK — failure (LRT p≥0.05 or |HR-1|<0.10) = meaningful null, still routes to Phase 6 (null is publishable)

**Procedure:**
1. Fit M0: CoxPHFitter(penalizer=0.1).fit(panel_df, duration_col='duration', event_col='event') with covariates [task_age, log_publication_volume, benchmark_introduction_year]
2. Fit M1: M0 + log_unique_paper_count_at_intro_z
3. LRT stat = -2*(M0.log_likelihood_ - M1.log_likelihood_), df=1; p from scipy.stats.chi2(df=1).sf(stat)
4. HR = exp(M1.params_['log_unique_paper_count_at_intro_z']); extract 95% CI from M1.confidence_intervals_

**Success criteria:**
- LRT p < 0.05 AND |HR-1| ≥ 0.10

**Direction-interpretation protocol (pre-specified, prevents HARKing):**
- HR < 1.0 AND p < 0.05 → H1 lock-in: breadth → stakeholder network → resistance (Ott 2022)
- HR > 1.0 AND p < 0.05 → H2 saturation: diversity → overuse signal → replacement (Koch 2021, ICLR 2025)
- p > 0.05 (gates pass) → H0 null: community-breadth class does not predict displacement timing

---

### H-M2 — Secondary Predictions & KM Confirmation (SHOULD_WORK)

**Statement:** (P2) The 95% CI of HR for log_unique_paper_count_at_intro_z does not contain 1.0.
(P3) Kaplan-Meier Q1 vs Q4 diversity quartiles show log-rank p < 0.05.

**Prerequisites:** H-M1 (primary Cox significant)
**Gate:** SHOULD_WORK — failure does not block Phase 5

**Procedure P2:** Extract CI_lower, CI_upper from M1.confidence_intervals_. Check CI_lower > 1.0 (H2) or CI_upper < 1.0 (H1).

**Procedure P3:**
1. Stratify h-e2 benchmarks into quartiles by log_unique_paper_count_at_intro
2. Plot KM curves for Q1 vs Q4 using lifelines.KaplanMeierFitter
3. Compute log-rank test: lifelines.statistics.logrank_test(Q1_durations, Q4_durations, Q1_events, Q4_events)

**Success criteria:**
- P2: CI excludes 1.0 (CI_lower > 1.0 or CI_upper < 1.0)
- P3: log-rank p < 0.05

---

### H-R1 — Robustness Checks (SHOULD_WORK)

**Statement:** Primary Cox result holds under 3 robustness variants; at least 2/3 consistent with primary.

**Prerequisites:** H-M1 (primary Cox significant)
**Gate:** SHOULD_WORK — failure does not block Phase 5; weakens robustness claim only

**Checks:**
- R1: Replace primary predictor with paper_diversity_ratio_at_intro_z; check LRT p < 0.05
- R2: Add interaction term log_unique_paper_count_z × task_age; check primary HR still p < 0.05
- R3: Restrict to Koch 133 core tasks only (subset of 87); check LRT p < 0.05 (marginal p<0.10 acceptable)

**Success criteria:** ≥2/3 robustness checks consistent with primary result

---

## Dependency Graph (DAG)

```
H-E1 (MUST_WORK, READY)
  └─► H-M1 (MUST_WORK, prereq: H-E1)
        ├─► H-M2 (SHOULD_WORK, prereq: H-M1)
        └─► H-R1 (SHOULD_WORK, prereq: H-M1)
```

H-M2 and H-R1 execute in parallel after H-M1 completes.

---

## Execution Order

1. **H-E1** — data join + 5 FAIL FAST gates (G0→G4 in order, stop on first failure)
2. **H-M1** — Cox M0 vs M1, LRT, HR extraction, direction interpretation
3. **H-M2 + H-R1** — parallel execution after H-M1 passes

Total: 4 sub-hypotheses, 2 MUST_WORK, 2 SHOULD_WORK

---

## Phase 5 Configuration

Per `pipeline_options.skip_baseline_comparison=true`, Phase 5 (baseline comparison H-C1) is deferred.
Null model (M0 controls only) serves as the internal baseline. h-m1 Run 2 (HR=0.871, p=0.565) is the
prior-attempt directional baseline for contextual comparison.

---

## Key References

- Ott et al. 2022 (Nature Comms): breadth → longevity (H1 lock-in)
- Koch et al. 2021: concentration methodology complement (H2 saturation)
- ICLR 2025 workshop: overuse framing (H2 saturation)
- h-m1 Run 2 empirical baseline: HR=0.871 calibrates |HR-1|≥0.10 threshold
- pwc-archive/evaluation-tables: CC-BY-SA-4.0, 326k rows, paper_url column confirmed
- h-e2 panel: 87 tasks, 345 events, EPV=115, validated 14/14 tests
