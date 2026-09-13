---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: ML Benchmark Saturation and Score Convergence"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-21
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Quantifying benchmark saturation dynamics in ML leaderboards — when and how benchmarks reach performance ceiling convergence, using confirmed PwC-internal data and the validated finding that high-reuse benchmarks exhibit significantly LOWER CoV (rho=−0.28, p=0.0025)

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode — 3rd attempt)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

Datasets are a central pillar of machine learning (ML) research—from pretraining to evaluation and benchmarking. A growing body of work highlights serious issues throughout the ML data ecosystem, including the under-valuing of data work, ethical issues in datasets that go undiscovered, a lack of standardized dataset deprecation procedures, the (mis)use of datasets out-of-context, an overemphasis on single metrics rather than holistic model evaluation, and the overuse of the same few benchmark datasets.

Source Type: Workshop CFP / Structured Input (ICLR 2025 Workshop: The Future of Machine Learning Data Practices and Repositories)

**Retrying after three prior failures (H-E1 original join attempt, H-E1 CoV direction failure, H-M2 k-shot domain failure)** — this iteration exploits the CONFIRMED empirical finding from H-E1 as the primary hypothesis rather than treating it as a null result. High-reuse → lower CoV is empirically established (N=111, rho=−0.28, p=0.0025, permutation p=0.0). The new research question asks: *what is the structure, timing, and task-type pattern of benchmark saturation?*

---

## Lessons from Previous Attempts

### What Was Tried Before

**H-E1 v1 (EXISTENCE / FOUNDATION):** Cross-repository join of PwC leaderboards with OpenML datasets to characterize reuse and result consistency. Assumed PwC benchmark names and OpenML dataset names are the same entities.

**H-E1 v2 (H-CoVReuse-v1):** Within PwC data, tested whether high-reuse benchmarks show HIGHER result CoV (variance inflation hypothesis). N=111, Spearman rho=−0.2841 (negative, significant). Hypothesis direction wrong.

**H-M2 (Benchmark Difficulty Calibration):** Sigmoid difficulty calibration on H-E1 top-20 overlap pairs (k-shot benchmarks). 13/20 pairs skipped (n_pre2020 < 5), 7/20 degenerate (R²<0). fraction_pass=0%.

### Why It Failed

**H-E1 v1 ROOT CAUSE:** PwC and OpenML are different entity domains. Fuzzy join yielded only 36/1,096×4,931 matches. Cross-repository join assumption empirically falsified.

**H-E1 v2 ROOT CAUSE:** Causal mechanism inverted. High-reuse benchmarks converge toward performance ceiling (Goodhart saturation) — community pressure to "solve" popular benchmarks compresses score variance, not expands it. Effect is real and confirmed (rho=−0.28, permutation p=0.0) but direction opposite to hypothesis.

**H-M2 ROOT CAUSE:** k-shot variant benchmarks (Mini-ImageNet k-shot, CIFAR-FS k-shot) emerged post-2018 — insufficient pre-2020 model history. Score variance dominated by shot-count parameter, not model capability. Sigmoid calibration model assumptions violated.

### How This New Direction Avoids Those Pitfalls

1. **Exploits confirmed finding as primary signal** — rho=−0.28 (high-reuse → lower CoV) is the dependent variable relationship; new hypotheses characterize its structure, not re-test its direction
2. **No cross-repository join** — all analysis uses PwC-internal data (1,096 benchmarks, 30,928 rows confirmed via `ingest_pwc.py`)
3. **No k-shot benchmarks** — exclude k-shot variant pairs; require ≥20 pre-2020 result rows per benchmark
4. **Reusable code** — `ingest_pwc.py`, `derive.py` (compute_result_cov, compute_reuse_rate, compute_rank_reversal_rate), `report.py`, `run.py` all confirmed correct

---

## Session Plan

ROUTE_TO_0 Auto-extraction — research direction derived from:
1. Current input: ICLR 2025 MLDPR Workshop CFP (benchmark reproducibility, overuse of benchmark datasets, non-traditional benchmarking paradigms)
2. Failure lessons: avoid variance-inflation framing (empirically inverted), avoid cross-repository joins, avoid k-shot benchmarks
3. Confirmed empirical anchor: high-reuse → lower CoV (rho=−0.28, p=0.0025) — exploit this as established fact
4. Reusable assets: full PwC pipeline confirmed correct

---

## Technique Sessions

ROUTE_TO_0 Mode — No interactive sessions.

**Research direction pivot analysis:**

| Prior Frame | Confirmed Finding | New Frame |
|-------------|-------------------|-----------|
| "High reuse → higher variance (inflation)" | REFUTED — direction inverted | "High reuse → saturation (convergence toward ceiling)" |
| Cross-repository data quality join | FAILED — entity mismatch | PwC-internal only |
| k-shot benchmark temporal analysis | FAILED — no pre-2020 data | Traditional benchmarks with ≥20 pre-2020 entries |

**CFP topic feasibility filter (MANDATORY CONSTRAINTS applied):**

| CFP Topic | Status | Rationale |
|-----------|--------|-----------|
| Benchmark reproducibility | ✅ ACCEPTED | Measurable via CoV in existing PwC result rows |
| Overfitting/overuse of benchmark datasets | ✅ ACCEPTED | Saturation quantifiable from confirmed PwC data |
| Non-traditional/alternative benchmarking paradigms | ✅ ACCEPTED | Saturation timing as diagnostic for when to retire benchmarks |
| Holistic and contextualized benchmarking | ✅ ACCEPTED | Cross-task-type saturation comparison using existing PwC data |
| Dataset reproducibility | ✅ ACCEPTED | CoV-over-time from existing leaderboard history |
| New benchmarks, rubrics, scoring frameworks | ❌ REJECTED | Pipeline-enforced constraint |
| Human evaluation or annotation | ❌ REJECTED | Pipeline-enforced constraint |
| Synthetic/generated data | ❌ REJECTED | Pipeline-enforced constraint |

---

## Research Question Development

### Initial Question

Given the confirmed finding that high-reuse benchmarks exhibit significantly lower result CoV (rho=−0.28, p=0.0025, N=111), can we characterize the temporal and structural dynamics of benchmark saturation — specifically, at what reuse level saturation onset occurs, whether saturation speed differs by task type, and whether score ceiling proximity predicts saturation better than raw paper count?

### Refined Question

Using existing Papers With Code leaderboard data (1,096 benchmarks, 30,928 result rows, confirmed via `pwc-archive/evaluation-tables`), can we characterize benchmark saturation dynamics by: (1) detecting saturation onset as the paper_count threshold at which result CoV drops below a stable floor, (2) comparing saturation trajectories across task types (image classification vs. NLP vs. object detection), and (3) testing whether score ceiling proximity (max_score / theoretical_maximum) predicts residual CoV better than paper_count alone — all using existing published results with no new experiments, benchmarks, or human evaluation?

### Detailed Sub-Questions

1. Using confirmed PwC data (N=111 benchmarks with computed CoV), does result CoV exhibit a detectable breakpoint as a function of paper_count — i.e., is there a saturation onset threshold (paper_count*) below which CoV is stable and above which CoV monotonically decreases, detectable via piecewise regression or change-point analysis on existing data?

2. Among the 111 benchmarks with computed CoV and paper_count, does the slope of CoV-vs-paper_count differ significantly across task type groups (image classification, reading comprehension, object detection) — indicating that some domains saturate faster than others?

3. For benchmarks with ≥20 pre-2020 result rows (required temporal depth), does the year-of-first-saturation (first year CoV drops below median) correlate with task type or benchmark age at that year — using only existing PwC temporal result data?

4. Can score ceiling proximity (defined as: mean of top-10 scores relative to the maximum possible score for the metric, computable from existing result rows) predict residual CoV variation not explained by paper_count — i.e., does adding ceiling proximity improve CoV prediction beyond paper_count alone (via partial regression on existing data)?

5. Among benchmarks where confirmed saturation has occurred (CoV in bottom quartile), what is the distribution of rank_reversal_rate (from confirmed-working `compute_rank_reversal_rate()`) — and is rank_reversal_rate lower in saturated benchmarks than in non-saturated ones, suggesting that saturation also reduces benchmark discriminative power?

---

## Reference Papers

Not provided - will discover in Phase 1

Focus areas for Phase 1 literature search:
- Benchmark saturation and ceiling effects in ML leaderboards (Goodhart's Law applied to ML benchmarks)
- Change-point detection / piecewise regression methods for time-series benchmarking data
- Score convergence and benchmark retirement criteria in ML evaluation
- Cross-task-type evaluation diversity (image classification vs. NLP vs. detection leaderboard comparison)
- Papers With Code leaderboard analysis — prior empirical studies using PwC data
- Rank stability and discriminative power of saturated benchmarks

---

## Validation Results

### So What Test

Input from established research venue (ICLR 2025 Workshop) — significance pre-validated. The workshop explicitly targets "overuse of the same few benchmark datasets" and "non-traditional/alternative benchmarking paradigms." This research directly quantifies *when* and *how* benchmarks become overused (saturation onset), providing empirical criteria for benchmark retirement decisions — a concrete contribution to ML data practices. The confirmed H-E1 finding (rho=−0.28) means Phase 4 can report an empirically anchored result; sub-questions characterize the structure of a known real effect rather than test a speculative hypothesis. Failure-to-find risk is substantially reduced compared to H-E1 v2.

### Feasibility Check

All sub-questions testable on confirmed-available data:
- PwC data: 1,096 benchmarks, 30,928 result rows (`ingest_pwc.py` confirmed correct)
- CoV and reuse_rate: already computed for N=111 in H-E1 (`derive.py` confirmed)
- Piecewise regression / change-point analysis: standard statsmodels / ruptures libraries, no new data
- Score ceiling proximity: computable from existing result rows (max of top-10 / metric max)
- Task type: available as PwC metadata field (task_type)
- Temporal analysis: filtered to ≥20 pre-2020 entries (enforced to avoid H-M2 pitfall)
- Pipeline-enforced constraints satisfied: no new benchmarks, no rubrics, no human scoring, no synthetic data

---

## Phase 1 Input Package

<phase1-input>

### research_question
Using existing Papers With Code leaderboard data (1,096 benchmarks, 30,928 result rows), can we characterize benchmark saturation dynamics — specifically the paper_count threshold at which result CoV stabilizes (saturation onset), whether saturation speed differs by task type, and whether score ceiling proximity predicts residual CoV better than paper_count alone — using only existing published results with no new experiments or benchmarks?

### detailed_question
1. Does result CoV exhibit a detectable breakpoint as a function of paper_count in PwC data (N=111 benchmarks with computed CoV) — i.e., is there a saturation onset threshold detectable via piecewise regression or change-point analysis on the confirmed rho=−0.28 relationship?

2. Does the slope of CoV-vs-paper_count differ significantly across task type groups (image classification, reading comprehension, object detection) in existing PwC benchmark data — indicating domain-specific saturation rates?

3. For benchmarks with ≥20 pre-2020 result rows, does year-of-first-saturation (first year CoV drops below median) correlate with task type or benchmark age at saturation — using only existing PwC temporal data?

4. Does score ceiling proximity (top-10 mean score / metric maximum, computable from existing result rows) explain residual CoV variation beyond paper_count alone, as tested via partial regression on confirmed PwC data?

5. Is rank_reversal_rate (from confirmed-working `compute_rank_reversal_rate()`) lower in saturated benchmarks (CoV bottom quartile) than non-saturated ones — suggesting saturation also reduces benchmark discriminative power?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

- H-E1 v2 confirmed real empirical finding: high-reuse → lower CoV (rho=−0.28, permutation p=0.0, N=111) — this is the empirical anchor for the new hypothesis family
- Saturation framing converts a FAILED hypothesis into a productive research program: instead of "does reuse inflate variance?" ask "what is the structure of saturation?"
- Score ceiling proximity is computable from existing result rows (no new data needed) — extends the confirmed finding with a mechanistic predictor
- Piecewise regression / change-point detection applies directly to the confirmed CoV-vs-paper_count monotonic relationship
- All confirmed reusable code from H-E1 (`ingest_pwc.py`, `derive.py`, `report.py`, `run.py`) eliminates re-implementation risk

### Techniques Used

ROUTE_TO_0 Auto-Fill Mode — structured input extraction from ICLR 2025 Workshop CFP combined with three-failure context integration from Serena Memory (H-E1 v1 join failure, H-E1 v2 CoV direction failure, H-M2 k-shot domain failure), pivoting to exploit the confirmed empirical finding as the primary research anchor.

### Areas for Further Exploration

- OpenML tabular dataset saturation (separate domain from PwC — could be valid standalone study)
- Licensing and deprecation policy implications of saturation onset detection (CFP topic, requires legal expertise)
- Foundation model benchmark saturation (different scale — MMLU, HumanEval; might have different saturation dynamics)
- FAIR compliance scoring for benchmark repositories (requires new rubric — deprioritized per constraints)

---

## Next Steps

Proceed to Phase 1 - Targeted Research (`/phase1-targeted`)

Phase 1 literature search priorities:
1. Benchmark saturation and Goodhart's Law in ML — empirical prior work on score convergence
2. Change-point analysis methods applied to ML evaluation data
3. Score ceiling / benchmark retirement criteria — existing proposals and empirical evidence
4. Cross-task-type evaluation diversity — domain-specific saturation rates in prior work
5. Papers With Code as empirical instrument — prior studies using PwC leaderboard data for meta-analysis

**Reusable assets to pass to Phase 2A:**
- `ingest_pwc.py`, `derive.py`, `report.py`, `run.py` (all confirmed correct from H-E1)
- Confirmed finding: rho=−0.28 (high-reuse → lower CoV), N=111, p=0.0025, permutation p=0.0
- Gate requirement: ≥20 pre-2020 result rows per benchmark (enforced to avoid H-M2 pitfall)
- Exclude: k-shot variant benchmarks, cross-repository joins
- New analytical tools needed: piecewise regression (ruptures or statsmodels), partial regression

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm (ROUTE_TO_0 - Failure Recovery, 3rd attempt)*
*Ready for: Phase 1 - Targeted Research*
