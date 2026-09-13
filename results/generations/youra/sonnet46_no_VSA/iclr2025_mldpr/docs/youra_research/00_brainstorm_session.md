---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: ML Benchmark Submitter Diversity → Displacement Hazard"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-03
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Benchmark dataset lifecycle dynamics in ML — what measurable *submitter diversity* properties of ML benchmarks predict benchmark displacement hazard in PWC task communities, pivoting away from all ten prior failed approaches: Gini concentration, authorship Gini, displacement event counting with strict thresholds, domain-type as moderator, raw publication volume, SOTA score improvement rate, performance saturation/ceiling proximity, FAIR-documentation composite (metrics_count degenerate; papers_linked_count competition-confounded), lagged annual submission flow via CoxTimeVaryingFitter (EPV=8.5, 34 events, HR=0.991, pure null), and cumulative submission count at introduction year via CoxPHFitter (partial_r²=0.0011, C_t variance is time-explained not investment-explained).

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode — Eleventh Attempt)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

Datasets are a central pillar of machine learning (ML) research—from pretraining to evaluation and benchmarking. A growing body of work highlights serious issues throughout the ML data ecosystem: the under-valuing of data work, ethical issues in datasets that go undiscovered, a lack of standardized dataset deprecation procedures, the (mis)use of datasets out-of-context, an overemphasis on single metrics rather than holistic model evaluation, and the overuse of the same few benchmark datasets.

Source Type: Workshop CFP / Structured Input (ICLR 2025 Workshop: The Future of Machine Learning Data Practices and Repositories)

**Feasibility Constraints (Pipeline-Enforced):**
- No new benchmarks, rubrics, or scoring frameworks
- No synthetic/generated data or future follow-up data
- No human evaluation, annotation, or subjective scoring
- Only hypotheses testable immediately using existing real datasets and existing benchmarks

**ROUTE_TO_0 Context:** Eleventh attempt. Ten previous runs documented in Serena Memory and archived brainstorms:
- Attempt 1 (h-m1 cross-sectional): Cross-sectional Gini concentration → cross-task adoption — FAILED (ρ=+0.12, p=0.30, wrong direction, n=71)
- Attempt 2 (h-e1 Run 1): Displacement counting with Gini std gate — FAILED (Gini std=0.065 < 0.10)
- Attempt 3 (h-e1 Run 2): Displacement counting relaxed threshold — FAILED (38/100 events, slug matching too strict)
- Attempt 4 (h-e2): NLP vs CV reign length — FAILED (p=0.9513; NLP displaced FASTER, wrong direction)
- Attempt 5 (h-m1 raw volume): Raw publication volume → Cox — FAILED (HR=0.975, LRT p=0.870, null)
- Attempt 6 (h-m1 Run 2): Δscore (SOTA improvement rate) → Cox — FAILED (HR=0.871, LRT p=0.565; 34.1% coverage, 22 events, underpowered)
- Attempt 7 (superseded): Performance saturation → Cox — superseded (same 34.1% coverage ceiling)
- Attempt 8 (FAIR-doc): FAIR-Documentation composite — FAILED (metrics_count=0 degenerate; papers_linked_count HR=1.092 competition-confounded)
- Attempt 9 (h-m1 Run 1, submission delta): Lagged annual submission flow via CoxTimeVaryingFitter — FAILED (HR=0.991, p=0.977, PURE NULL; EPV=8.5, 34 events, structurally underpowered)
- Attempt 10 (h-m1 Run 1, cumulative count): Cumulative submission count at introduction year via CoxPHFitter — FAILED (partial_r²=0.0011; C_t collinear with temporal controls r=0.447; variance is time-explained not investment-explained)

---

## Lessons from Previous Attempts

### Attempts 1–3 — Gini/Displacement Counting
**Root Cause:** Gini near-zero in diffuse PWC authorship; strict slug matching; event count below threshold.
**Lesson 11:** h-e2 panel (87 tasks, 345 events) validated and directly reusable. No new event counting.

---

### Attempt 4 — NLP vs CV Domain Comparison
**Root Cause:** Domain type does not moderate benchmark persistence (medians equal at 1.0 year; NLP displaced FASTER).
**Lesson 11:** Domain-type as primary analysis permanently exhausted. Use only as interaction term if needed.

---

### Attempt 5 — Raw Publication Volume → Cox
**Root Cause:** Quantity of papers ≠ competitive pressure. Null effect.
**Lesson 11:** Raw paper count at task level is not a valid predictor. Eliminated.

---

### Attempt 6 — Δscore (SOTA Improvement) → Cox
**Root Cause:** evaluation-tables SOTA score coverage = 34.1% (252/740 rows). Only 22 events in covered subset.
**Lesson 11:** ALL score-trajectory predictors face same 34.1% ceiling. Performance-trajectory space is closed.

---

### Attempt 7 — Performance Saturation → Cox
**Status:** Correctly abandoned. Same 34.1% coverage ceiling. Closed.

---

### Attempt 8 — FAIR-Doc Composite
**Root Cause 1:** metrics_count = 0 for all 227 spells — column is degenerate. Permanently excluded.
**Root Cause 2:** papers_linked_count confounded with competition intensity (direction reversal HR=1.092).
**Lesson 11:** Do not use metrics_count (degenerate) or papers_linked_count as primary predictor.

---

### Attempt 9 — Lagged Annual Submission Flow (CoxTimeVaryingFitter)
**Root Cause:** Requires tasks with post-entry temporal flow data → only 34/87 tasks qualify → EPV=8.5. Single-spell structure (all event=1) provides no within-subject variation. HR=0.991, pure null.
**Lesson 11:** Do NOT use CoxTimeVaryingFitter for submission count.

---

### Attempt 10 — Cumulative Submission Count at Introduction Year (CoxPHFitter) — NEW CRITICAL LESSON
**Root Cause:** C_t (cumulative count) collapses into a time proxy. partial_r²=0.0011 (threshold=0.05). Both correlations r(C_t, task_age)=0.447 and r(C_t, intro_year)=0.447 — C_t captures elapsed time, not distinct community investment signal. log_publication_volume uncorrelated with C_t (r=-0.045).
**Lesson 11:** Do NOT use raw cumulative count metrics. They reflect time accumulation, not independent community investment. Alternative proxies needed: **submission diversity** (unique submitters, paper-per-entry ratio), **recency-weighted counts**, or **external citation-based proxies**. The h-m1 Run 1 failure record explicitly recommends submission diversity metrics as next direction.

---

### How THIS Direction (Attempt 11) Avoids All Prior Pitfalls

1. **Submitter diversity instead of submission count.** The fundamental failure of Attempts 9–10: raw counts (delta, cumulative) are time-proxies. Diversity is not: a benchmark with 50 unique papers submitting once each and a benchmark with 50 submissions from 1 paper have identical counts but radically different community footprints. The `paper-to-row ratio` (unique `paper_url` count / total rows per benchmark) at introduction year is a pure normalized diversity measure — independent of elapsed time by construction.

2. **Pure count operation on evaluation-tables.** No score values needed. No author metadata required. `paper_url` is present in evaluation-tables and is already used by h-e1 pipeline. Computing `unique_paper_count` per (benchmark, year ≤ intro_year) is a groupby+nunique on `paper_url` — same data operations as cumulative count but with pandas `nunique()` instead of `len()`.

3. **Reuse h-e2 survival panel directly.** 87 tasks, 345 displacement events, archived. Same panel used by all prior Cox attempts. No new data collection. fuzzy task match (RapidFuzz ≥85) confirmed at 92% coverage by h-e1.

4. **Reuse h-m1 CoxPHFitter infrastructure.** cox_runner.py (14/14 tests pass), gate_evaluator.py, penalizer=0.1, _available() zero-variance guard — all confirmed working. Implementation delta is replacing `cumulative_submission_count` column derivation with `unique_paper_count_at_intro` and `paper_diversity_ratio_at_intro` column derivation.

5. **Mechanistic independence from time.** Submission diversity (paper-to-row ratio) is normalized — a benchmark with 10 entries from 10 unique papers has ratio=1.0 regardless of whether those entries accumulated over 1 year or 5 years. This survives partial correlation with task_age and benchmark_introduction_year by construction. Addresses the exact root cause of Attempt 10 failure.

6. **Two operationalizations for robustness:** (a) `log_unique_paper_count_at_intro_z` — log-transformed absolute count of unique papers, normalized within survival panel; (b) `paper_diversity_ratio_at_intro_z` — unique paper count / total rows (ratio), z-standardized. The ratio is time-independent; the count provides statistical power. Run both; either passing constitutes support.

7. **Schema pre-validation gate (CRITICAL).** Step 0: Load evaluation-tables. Verify `paper_url` column exists. Count unique `paper_url` values per benchmark. Verify ≥80% of h-e2 panel benchmarks have non-zero unique paper counts. FAIL FAST if below 80%. Use `dataset.to_table().to_pandas()` batch load — NOT row-by-row Arrow iteration (46-min penalty confirmed in h-e1).

8. **ICLR 2025 connection: "overuse of benchmark datasets."** Submitter diversity directly operationalizes the BREADTH of overuse — not just how many evaluations but how many distinct research groups have evaluated on this benchmark. A benchmark that many groups use (high diversity) maps directly onto "how central is this benchmark to the community" at introduction time. High diversity at introduction could predict entrenchment (broad stakeholders resist replacement) or saturation (community breadth accelerates awareness of overuse). Both outcomes address the workshop's "overuse" and "non-traditional benchmarking paradigms" themes.

---

## Session Plan

ROUTE_TO_0 Auto-Fill (eleventh attempt) — research direction synthesized from:
1. Current input (ICLR 2025 Workshop CFP on ML Data Practices)
2. All 5 Serena failure/limitation Memory records (failure_h-e1_run1, failure_h-e1_run2, failure_h-m1_run1 [2026-08-03], failure_h-m1_run2, limitation_h-e2_run1)
3. Most recent archived brainstorm (20260803T060132_routing_recovery — Attempt 10)
4. Critical new lesson from Attempt 10: C_t (cumulative count) collapses into time proxy (partial_r²=0.0011). h-m1 Run 1 failure feedback explicitly recommends "submission diversity metrics (unique submitters, submission entropy)" as next direction.

Strategy: Extract `unique_paper_count_at_intro` (count of distinct paper_url values per benchmark in evaluation-tables through plurality introduction year) and `paper_diversity_ratio_at_intro` (unique paper count / total rows) from pwc-archive/evaluation-tables. Use as time-fixed covariates in CoxPHFitter on h-e2 survival panel. Test: does higher submitter diversity at introduction predict slower (entrenchment via broad community investment) or faster (saturation via widespread awareness) displacement?

---

## Technique Sessions

ROUTE_TO_0 Mode — No interactive sessions. Automated synthesis from failure context + structured input.

---

## Research Question Development

### Initial Question

Do ML benchmarks with higher submitter diversity at the time they achieve plurality status — measured as the number of unique papers submitting evaluation results to a benchmark in pwc-archive/evaluation-tables up through the benchmark's introduction year — predict benchmark displacement hazard in Papers With Code task communities, testing whether broad community investment (many distinct teams evaluating) creates entrenchment and slower displacement, or accelerates saturation and faster replacement?

### Refined Question

Using pwc-archive evaluation-tables `unique_paper_count_at_intro` (count of distinct `paper_url` values per benchmark through plurality introduction year, log1p-transformed and z-standardized) and `paper_diversity_ratio_at_intro` (unique paper count / total evaluation-table rows per benchmark at introduction year, z-standardized) as time-fixed proxies for submitter diversity — both extractable as pure count operations on `paper_url`, requiring no score values and achieving 100% coverage for plurality benchmarks by construction — and the h-e2 survival panel (87 tasks, 345 displacement events) directly reused from archive, can we determine whether **benchmark submitter diversity at introduction year** significantly predicts plurality benchmark displacement hazard in a CoxPHFitter model (EPV=115), testing whether high submission diversity creates broad stakeholder lock-in (HR < 1, slower displacement) or signals benchmark ubiquity/overuse pressure (HR > 1, faster displacement), providing empirical evidence on benchmark lifecycle dynamics that directly addresses the ICLR 2025 workshop's concerns about "overfitting and overuse of benchmark datasets," "benchmark reproducibility," and "non-traditional benchmarking paradigms," and crucially avoiding the time-proxy collapse that failed Attempt 10 (partial_r²=0.0011 for cumulative count) by using a normalized diversity ratio that is independent of temporal accumulation by construction?

### Detailed Sub-Questions

1. What is the distribution of `unique_paper_count_at_intro` and `paper_diversity_ratio_at_intro` across the 87-task h-e2 survival panel, and does the diversity ratio have sufficient variance independent of task_age and benchmark_introduction_year? [Pre-condition FAIL FAST gate: ≥80% of panel benchmarks have non-zero unique paper counts; log(unique_paper_count)_z std > 0.5; partial_r² of diversity_ratio with temporal controls > 0.05 (contrast with Attempt 10 which had partial_r²=0.0011)]

2. Does `log_unique_paper_count_at_intro_z` significantly predict plurality benchmark displacement hazard in CoxPHFitter on h-e2 panel (87 tasks, 345 events, EPV=115), with HR significantly different from 1.0 (p < 0.05), and in which direction (HR < 1 = entrenchment, HR > 1 = saturation/ubiquity)?

3. Does `paper_diversity_ratio_at_intro_z` (unique papers / total rows — normalized, time-independent by construction) independently predict displacement hazard, and does it survive partial correlation with temporal controls (task_age, benchmark_introduction_year) with partial_r² > 0.05?

4. Does the submitter diversity → displacement hazard relationship hold after controlling for task-level confounders (task_age, log_publication_volume, benchmark_introduction_year) reused from h-m1 panel_with_covariates.parquet?

5. Robustness: do top-quartile diversity benchmarks show qualitatively different Kaplan-Meier survival curves than bottom-quartile benchmarks (KM quartile stratification), and does the result hold with `submission_count_intro_year_only` as a third covariate (to verify diversity effect is not simply masking count effect)?

---

## Reference Papers

Not provided - will discover in Phase 1

---

## Validation Results

### So What Test

**Why it matters:** The ICLR 2025 workshop explicitly targets "overfitting and overuse of benchmark datasets," "benchmark reproducibility," and "non-traditional benchmarking paradigms." Submitter diversity (unique papers evaluating a benchmark at introduction year) is the first *community-breadth* measure of benchmark adoption in longitudinal benchmark lifecycle analysis — distinct from documentation counts (confounded), score values (34.1% coverage gap), annual flow (structurally underpowered at 34 events), and cumulative count (Attempt 10: time proxy, partial_r²=0.0011).

**Impact if confirmed (high submitter diversity → slower displacement / entrenchment):**
- Quantifies "community lock-in via breadth": benchmarks entered by many distinct research groups at plurality introduction are harder to displace — actionable for repository administrators (OpenML, HuggingFace, PWC) to identify entrenched benchmarks before accumulated overuse becomes irreversible
- Policy implication: actively diversifying benchmark usage (encouraging more distinct teams to evaluate) may inadvertently entrench benchmarks, slowing healthy turnover
- Connects directly to workshop theme of "benchmark usability" and "dataset reproducibility" — highly usable benchmarks attract diverse submitters and become entrenched

**Impact if confirmed (high submitter diversity → faster displacement / saturation):**
- Broad community awareness at introduction signals that the benchmark is thoroughly known — faster collective recognition of saturation → earlier replacement
- "Overuse" is self-terminating: the more groups that evaluate on a benchmark, the faster community consensus on its limits, the sooner replacement emerges
- Actionable for "deprecation procedures": high-diversity benchmarks are candidates for earlier community discussion of replacement

**Impact if null:**
- Rules out submitter diversity (breadth) as a lifecycle predictor, alongside submission count (depth, Attempt 10)
- Together with Attempt 10, establishes that neither volume nor breadth of leaderboard participation at introduction predicts displacement hazard
- Still publishable: comprehensive negative evidence on what does NOT predict benchmark displacement in PWC communities — important empirical null for the ICLR 2025 workshop's evidence base

**Venue significance:** "Overuse of benchmark datasets" is a primary ICLR 2025 workshop concern. Submitter diversity directly operationalizes breadth of community engagement — who uses the benchmark, not just how often. This is a novel empirical contribution.

### Feasibility Check

**Testable immediately with existing data:**

| Sub-Q | Data Required | Source | Accessibility |
|-------|--------------|--------|---------------|
| 1 | nunique(`paper_url`) per (benchmark, year ≤ intro_year) | pwc-archive/evaluation-tables (HuggingFace, cached) | pandas groupby+nunique on paper_url column — same batch load as Attempt 10 |
| 2 | CoxPHFitter with time-fixed log_unique_paper_count_at_intro_z | h-e2 survival panel (87 tasks, 345 events, archived) | Direct reuse of h-m1 CoxPHFitter pipeline (14/14 tests pass) |
| 3 | paper_diversity_ratio_at_intro_z = unique_count / total_rows | Same evaluation-tables batch load | Simple derived column from nunique() / len() |
| 4 | task_age, log_publication_volume, benchmark_introduction_year | h-m1 panel_with_covariates.parquet (archived) | Direct reuse from archive |
| 5 | KM quartile curves | Sub-Q 1+2 + lifelines | KaplanMeierFitter available in lifelines |

**Implementation path:**

- Step 0 (SCHEMA PRE-VALIDATION — CRITICAL): Load pwc-archive/evaluation-tables from Arrow/Parquet cache via `dataset.to_table().to_pandas()` (NOT row-by-row, 46-min penalty confirmed). Inspect schema: verify `paper_url` column exists. Count unique paper_url per benchmark. Verify ≥80% of h-e2 panel benchmarks have non-zero unique paper counts. FAIL FAST if below 80%. Additionally: compute partial_r² of paper_diversity_ratio with task_age and benchmark_introduction_year. FAIL FAST if partial_r² < 0.01 (guards against another time-proxy collapse).

- Step 1: Load h-e2 archived survival panel from `docs/youra_research/_archive/20260803T011304_routing_recovery/` (87 tasks, 345 displacement events). Extract benchmark identifier and introduction year for each benchmark spell.

- Step 2: For each benchmark in survival panel: filter evaluation-tables rows where benchmark=benchmark AND paper_year ≤ intro_year. Compute: `unique_paper_count_at_intro` = nunique(paper_url); `total_rows_at_intro` = len(); `paper_diversity_ratio_at_intro` = unique_paper_count / max(total_rows, 1). Apply log1p to unique_paper_count. Z-standardize both.

- Step 3: Join to h-e2 spell-level data (one row per benchmark spell). Add controls: task_age, log_publication_volume, benchmark_introduction_year from h-m1 panel_with_covariates.parquet (reused directly).

- Step 4: Run CoxPHFitter with `log_unique_paper_count_at_intro_z` + controls (penalizer=0.1, reuse h-m1 cox_runner.py). Primary gate: p < 0.05 AND |HR - 1| ≥ 0.10. Also run with `paper_diversity_ratio_at_intro_z` as alternative predictor. Report HR, p-value, 95% CI, concordance for both.

- Step 5: Robustness: (a) KM quartile curves stratified by diversity ratio quartile; (b) model with both unique_count_z and diversity_ratio_z to assess independent contributions; (c) domain interaction (NLP vs CV) if primary gate passes.

**Why this avoids ALL prior failures:**
- Not Gini/authorship metrics (Attempts 1–3) → paper_url uniqueness count
- Not domain-type as primary (Attempt 4) → domain as interaction only
- Not raw task-level publication count (Attempt 5) → benchmark-level evaluation-table operations
- Not score-trajectory predictor (Attempts 6–7) → pure paper_url count, no score values
- Not metrics_count (Attempt 8 degenerate) → paper_url nunique operation
- Not papers_linked_count (Attempt 8 competition confound) → evaluation-table submission diversity, not citation
- Not CoxTimeVaryingFitter with post-entry flow (Attempt 9, EPV=8.5) → CoxPHFitter time-fixed (EPV=115)
- Not cumulative raw count (Attempt 10, time proxy, partial_r²=0.0011) → normalized diversity RATIO (time-independent by construction); FAIL FAST gate on partial_r² pre-validates independence
- Schema pre-validation gate + batch Parquet load → all prior data infrastructure lessons applied

**Constraints satisfied:**
- ✅ No new benchmarks or scoring frameworks
- ✅ No synthetic or future data (evaluation-tables is historical leaderboard record)
- ✅ No human annotation
- ✅ All data from existing publicly accessible sources (pwc-archive HuggingFace cache, archived panels)
- ✅ Operationalization distinct from all ten prior failed directions

---

## Phase 1 Input Package

<phase1-input>

### research_question
Using pwc-archive evaluation-tables `unique_paper_count_at_intro` (count of distinct `paper_url` values per benchmark through plurality introduction year, log1p-transformed and z-standardized) and `paper_diversity_ratio_at_intro` (unique paper count / total evaluation-table rows per benchmark at introduction year, z-standardized) as time-fixed proxies for submitter diversity — both extractable as pure groupby+nunique operations on `paper_url`, requiring no score values and achieving 100% coverage for plurality benchmarks by construction — and the h-e2 survival panel (87 tasks, 345 displacement events) directly reused from archive, can we determine whether **benchmark submitter diversity at introduction year** significantly predicts plurality benchmark displacement hazard in a CoxPHFitter model (EPV=115), testing whether high submission diversity creates broad stakeholder lock-in (HR < 1, slower displacement) or signals benchmark ubiquity/overuse pressure driving community replacement (HR > 1, faster displacement), providing empirical evidence on benchmark lifecycle dynamics that directly addresses the ICLR 2025 workshop's concerns about "overfitting and overuse of benchmark datasets" and "non-traditional benchmarking paradigms," critically avoiding the time-proxy collapse of Attempt 10 (partial_r²=0.0011 for cumulative count) by using a normalized diversity ratio whose independence from temporal controls is verified via FAIL FAST partial_r² gate before Cox regression?

### detailed_question
1. What is the distribution of `unique_paper_count_at_intro` and `paper_diversity_ratio_at_intro` across the 87-task h-e2 survival panel, and is the diversity ratio independent of temporal controls? [FAIL FAST gate: ≥80% benchmarks have non-zero unique paper counts; log(unique_paper_count)_z std > 0.5; partial_r² of diversity_ratio with (task_age, benchmark_introduction_year) > 0.01 — this guards against the time-proxy collapse that failed Attempt 10]
2. Does `log_unique_paper_count_at_intro_z` significantly predict plurality benchmark displacement hazard in CoxPHFitter on h-e2 panel (87 tasks, 345 events, EPV=115), with p < 0.05 and |HR-1| ≥ 0.10, and what is the direction (HR < 1 = entrenchment, HR > 1 = saturation)?
3. Does `paper_diversity_ratio_at_intro_z` (unique papers / total rows — normalized, time-independent by construction) independently predict displacement hazard after controlling for task_age, log_publication_volume, benchmark_introduction_year (from h-m1 panel_with_covariates.parquet)?
4. Do top-quartile diversity benchmarks show qualitatively different Kaplan-Meier survival curves than bottom-quartile benchmarks (KM quartile stratification on diversity ratio)?
5. Robustness: does the result hold when both `log_unique_paper_count_at_intro_z` and `paper_diversity_ratio_at_intro_z` are included together, and when `submission_count_intro_year_only_z` is added as covariate (to verify diversity effect is not masking a count effect)?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

- Eleven attempts have now systematically eliminated: Gini benchmark concentration, authorship Gini, displacement event counting with strict/relaxed thresholds, domain-type as primary moderator, raw publication volume, SOTA score improvement rate, performance saturation/ceiling proximity, FAIR-documentation composite (metrics_count degenerate, papers_linked_count competition-confounded), lagged annual submission flow via CoxTimeVaryingFitter (Attempt 9: EPV=8.5, 34 events, pure null), and cumulative submission count via CoxPHFitter (Attempt 10: partial_r²=0.0011, time proxy).
- Attempt 10 adds one critical new exclusion and one critical new direction: raw cumulative submission counts (and by extension any pure aggregation of rows over time) collapse into time proxies and fail the partial_r² independence gate. BUT: the h-m1 Run 1 failure record explicitly recommends "unique submitters, submission entropy" as the next direction — which maps directly onto `paper_url` uniqueness in evaluation-tables.
- `paper_diversity_ratio_at_intro` (unique_paper_count / total_rows) is normalized by construction — a ratio is invariant to elapsed time that accumulates both numerator and denominator at the same rate. This is the key structural distinction from all prior count-based Attempts 5, 9, and 10.
- h-e2 panel (87 tasks, 345 events) directly reusable. CoxPHFitter infrastructure (h-m1, 14/14 tests pass) directly reusable. evaluation-tables `paper_url` column present and used by h-e1 pipeline.
- FAIL FAST partial_r² gate is new critical safeguard: verifies predictor independence from temporal controls BEFORE running Cox regression. Had this gate existed in Attempt 10, it would have caught the time-proxy collapse immediately.

### Techniques Used

ROUTE_TO_0 Auto-Fill Mode (eleventh attempt) — failure context synthesis from 5 Serena Memory records (failure_h-e1_run1, failure_h-e1_run2, failure_h-m1_run1 [2026-08-03], failure_h-m1_run2, limitation_h-e2_run1) + most recent archived brainstorm (20260803T060132_routing_recovery — Attempt 10) + h-m1 Run 1 (2026-08-03) failure feedback: "explore submission diversity metrics (unique submitters, submission entropy)"

### Areas for Further Exploration

- **Submitter concentration index:** Herfindahl-Hirschman Index (HHI) of papers per benchmark — complement to diversity ratio measuring concentration at the other extreme
- **New-submitter ratio:** fraction of papers in introduction year that are first-time evaluators on that benchmark — pure novelty measure
- **Temporal diversity trajectory:** does diversity ratio increase or decrease over the benchmark's reign? Increasing diversity = growing community; decreasing = narrowing to specialists
- **Cross-repository presence:** benchmarks tracked on OpenML/HuggingFace AND PWC — does multi-platform diversity moderate displacement?
- **Institutional diversity:** do benchmarks with cross-institutional submitters (inferred from author lists) persist longer? Requires author metadata — higher data risk, leave for later
- **Citation diversity:** papers citing the benchmark paper (not submitting to leaderboard) — requires Semantic Scholar join, external data source
- **Benchmark age × diversity interaction:** older benchmarks accumulate more unique submitters by construction — age interaction term may be needed in robustness checks

---

## Next Steps

Proceed to Phase 1 - Targeted Research

**Research Direction for Phase 1:**
- Search for empirical studies on benchmark overuse, benchmark diversity, and leaderboard participation diversity in ML
- Look for survival analysis approaches applied to dataset/benchmark lifecycle with community breadth measures
- Find papers on "community lock-in" vs "benchmark saturation" dynamics in evaluation ecosystems
- Search for bibliometric studies on unique contributor counts and community adoption/longevity (analogous to submitter diversity)
- Find papers analyzing PWC submission patterns and unique team participation in benchmark leaderboards
- Look for papers on FAIR data principles and community breadth of dataset adoption (diversity of users, not just count)
- Search for prior ICLR/NeurIPS ML data practices workshop papers on benchmark lifecycle, overuse patterns, and community evaluation diversity
- Find information-theoretic approaches to measuring diversity/entropy in community-contributed evaluation datasets

**Implementation Notes for Phase 2A+:**
- CRITICAL Step 0 (Schema Pre-Validation + Independence Gate): Load evaluation-tables from Arrow/Parquet cache via `dataset.to_table().to_pandas()`. Verify `paper_url` column exists. Compute unique_paper_count and diversity_ratio per benchmark. Verify ≥80% coverage. Verify partial_r² of diversity_ratio with temporal controls > 0.01. FAIL FAST on either condition.
- Step 1: Load h-e2 archived survival panel from `docs/youra_research/_archive/20260803T011304_routing_recovery/` (87 tasks, 345 events). Extract benchmark identifier and introduction year per spell.
- Step 2: For each benchmark: filter evaluation-tables rows where paper_year ≤ intro_year. Compute unique_paper_count = paper_url.nunique(); total_rows = len(); paper_diversity_ratio = unique_paper_count / max(total_rows, 1). Apply log1p to unique_paper_count. Z-standardize both.
- Step 3: Join to h-e2 spell-level data. Add controls from h-m1 panel_with_covariates.parquet.
- Step 4: Run CoxPHFitter (penalizer=0.1, reuse h-m1 cox_runner.py) with log_unique_paper_count_at_intro_z + controls. Also run with paper_diversity_ratio_at_intro_z. Primary gate: p < 0.05 AND |HR-1| ≥ 0.10 for either predictor.
- Step 5: Robustness: KM quartile curves; joint model with both predictors; domain interaction.
- DO NOT use CoxTimeVaryingFitter (Attempt 9 lesson).
- DO NOT use raw cumulative row count without normalization (Attempt 10 lesson: time proxy).
- NEW: Add partial_r² pre-validation gate BEFORE Cox regression to catch time-proxy collapse early.
- EPV = 345/3 = 115 — strong statistical power for CoxPHFitter.

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm (ROUTE_TO_0 - Failure Recovery, Eleventh Attempt)*
*Ready for: Phase 1 - Targeted Research*
