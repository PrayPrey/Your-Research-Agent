---
hypothesis_id: h-m1
document_type: PRD
phase: 3
generated_at: "2026-08-25"
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - non_functional_requirements
  - data_specification
  - evaluation_metrics
  - dependencies
  - success_criteria
---

# PRD: H-M1 — Temporal Structure Test (Benchmark Overfitting Accumulation)

## 1. Executive Summary

This PRD specifies the implementation of a Spearman-correlation-based temporal signal detection experiment for hypothesis H-M1. The experiment tests whether GLUE and SuperGLUE leaderboard score-over-time trajectories exhibit non-random temporal structure consistent with gradual benchmark overfitting accumulation: monotonically increasing scores with decelerating gains. It reuses cleaned timeseries data from H-E1 and adds statistical analysis, visualization, and result reporting layers.

**Hypothesis gate:** MUST_WORK. Failure blocks H-M2, H-M3, H-M4, H-C1.

---

## 2. Problem Statement

### 2.1 Research Question

Do GLUE and SuperGLUE benchmark leaderboard score trajectories exhibit temporal structure consistent with gradual overfitting accumulation — specifically, monotonically increasing scores with decelerating improvement rates?

### 2.2 Motivation

If models are iteratively tuned with awareness of benchmark test set performance, the resulting community-level score trajectory should show:
1. Monotonic increase: scores consistently rise (benchmark-exploitable signal accumulates)
2. Decelerating gains: improvement rate slows over time (diminishing returns as exploitable signal exhausts)

A random walk or linear improvement would indicate no systematic benchmark exploitation, contradicting H-M1.

### 2.3 Approach

Apply Spearman rank correlation (non-parametric; robust to non-normality and ceiling effects) to:
- ρ(time, score): test monotonicity
- ρ(time, gain_rate): test deceleration of gains

Reuse H-E1 cleaned monthly-aggregated timeseries (GLUE + SuperGLUE). No re-download required.

---

## 3. Functional Requirements

### FR-01: Data Loading (H-E1 Reuse)
**Source:** `03_prd.md` FR-01
Load cleaned timeseries from H-E1 outputs.
- Input: `data/glue_timeseries_clean.csv`, `data/superglue_timeseries_clean.csv`
- Columns required: `months` (int, months-since-release), `monthly_max` (float, [0,1])
- Validate: ≥20 monthly observations, ≥24 month span, score variance >0.001
- Fail loudly if files missing (do not re-download in this hypothesis)

### FR-02: Monotonicity Test
Compute Spearman ρ(time, score) for each benchmark.
- Input: `months` array (N,), `monthly_max` array (N,)
- Tool: `scipy.stats.spearmanr`
- Output: `rho_monotonic` (float in [-1,1])
- Target: >0.8 for PASS

### FR-03: Deceleration Test
Compute Spearman ρ(time, gain_rate) for each benchmark.
- Gain rate: `gains = np.diff(monthly_max)` (shape N-1,), `gain_times = months[1:]`
- Tool: `scipy.stats.spearmanr`
- Output: `rho_decel` (float in [-1,1])
- Target: <-0.3 for PASS

### FR-04: Pre/Post Inflection Gain Rate Ratio
Quantify deceleration magnitude.
- Split series at midpoint index (approximate inflection)
- Compute mean gain pre-inflection and post-inflection
- Output: `pre_post_ratio` = pre_gain_mean / post_gain_mean (expected >1.0)
- Handle edge case: post_gain_mean ≤ 0 → report np.inf

### FR-05: Pass/Fail Determination
Evaluate success criteria per benchmark and overall.
- Per-benchmark PASS: `rho_monotonic > 0.8 AND rho_decel < -0.3`
- Overall PASS: both GLUE and SuperGLUE pass
- PARTIAL: one benchmark passes (proceed with warning, document discrepancy)
- FAIL: neither benchmark passes (gate FAIL, blocks downstream hypotheses)

### FR-06: Sanity Checks
Validate data quality before analysis.
- Time span ≥ 24 months (`assert times.max() - times.min() >= 24`)
- Monthly observations ≥ 20 (`assert len(scores) >= 20`)
- Score variance > 0.001 (`assert scores.std() > 0.001`)
- Raise informative errors with remediation guidance (re-run H-E1)

### FR-07: Results Reporting
Generate structured results dictionary and save to JSON.
- Output file: `results/h_m1_results.json`
- Fields: benchmark, n_months, rho_monotonic, rho_decel, pre_post_ratio, pass, overall_pass
- Print summary table to stdout

### FR-08: Visualization — Gate Metrics Bar Chart (MANDATORY)
Bar chart comparing rho_monotonic and rho_decel for GLUE vs SuperGLUE vs threshold lines.
- X-axis: metric name (rho_monotonic, rho_decel)
- Y-axis: correlation value [-1, 1]
- Horizontal reference lines: 0.8 (monotonicity threshold), -0.3 (deceleration threshold)
- Colors: GLUE=blue, SuperGLUE=orange
- Save: `figures/h_m1_gate_metrics.png`

### FR-09: Visualization — Score Trajectory (Additional)
Line plot of monthly max scores over time for GLUE and SuperGLUE.
- X-axis: months since release
- Y-axis: normalized composite score [0,1]
- Save: `figures/h_m1_score_trajectory.png`

### FR-10: Visualization — Gain Rate (Additional)
Scatter plot of month-over-month gains vs time.
- X-axis: months since release
- Y-axis: gain (score[t] - score[t-1])
- Add LOWESS/moving average trend line
- Save: `figures/h_m1_gain_rate.png`

### FR-11: Visualization — Pre/Post Inflection Box Plot (Additional)
Box plot comparing gain rate distributions pre vs post inflection.
- Two boxes: pre-inflection gains, post-inflection gains
- Save: `figures/h_m1_inflection_comparison.png`

### FR-12: Experiment Runner Script
Single entry-point script orchestrating all steps.
- File: `experiment_h_m1.py`
- Accepts: `--glue-csv`, `--superglue-csv` CLI args (defaults to H-E1 outputs)
- Returns: exit code 0 (PASS/PARTIAL), 1 (FAIL), 2 (data error)

### FR-13: Ablation — Null Model Comparison
Report baseline null correlation (ρ=0) alongside observed for context.
- `baseline_rho_monotonic = 0.0`
- `baseline_rho_decel = 0.0`
- Include in results JSON and summary table

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | Papers With Code Leaderboard Timeseries |
| Benchmarks | GLUE, SuperGLUE |
| Source | H-E1 cleaned outputs (reuse — no download) |
| Files | `data/glue_timeseries_clean.csv`, `data/superglue_timeseries_clean.csv` |
| Coverage | GLUE: ~200+ submissions 2019-2023; SuperGLUE: ~150+ submissions 2019-2023 |
| Resolution | Month-level (confirmed by H-E1) |
| Scale | GLUE: ~48 monthly bins; SuperGLUE: ~48 monthly bins |

**No manual download required.** Data is produced by H-E1 pipeline and assumed present.

### 4.2 Preprocessing (Inherited from H-E1)

1. Standardize to composite score: task average, normalized [0,1]
2. Convert dates → months-since-benchmark-release (integer)
3. Deduplicate: keep best score per model per month
4. Monthly aggregation: `monthly_max = groupby(months).score.max()`
5. Gain rate: `gains = np.diff(monthly_max)`

**No additional preprocessing required for H-M1.**

### 4.3 No Manual Download Tasks

Both datasets auto-inherit from H-E1. No setup task needed for data download.

---

## 5. Evaluation Metrics

| Metric | Type | Target | Threshold | Scope |
|--------|------|--------|-----------|-------|
| rho_monotonic | Spearman ρ(time, score) | >0.8 | PASS gate | Per benchmark |
| rho_decel | Spearman ρ(time, gain_rate) | <-0.3 | PASS gate | Per benchmark |
| pre_post_ratio | Mean gain pre/post inflection | >1.0 | Secondary | Per benchmark |
| Visual S-curve | Manual inspection | Confirmed | Mandatory | Both combined |

---

## 6. Success Criteria

### 6.1 PoC Pass Conditions
1. Code runs without error on both timeseries
2. `rho_monotonic > 0.8` for BOTH GLUE AND SuperGLUE
3. `rho_decel < -0.3` for BOTH GLUE AND SuperGLUE

### 6.2 Graded Outcomes
- **PASS**: All three PoC conditions met → H-M1 gate satisfied → H-M2/M3/M4/C1 unblocked
- **PARTIAL**: Criteria met for one benchmark → document discrepancy, proceed with warning
- **FAIL**: Neither benchmark shows temporal signal → gate FAIL, downstream hypotheses blocked

### 6.3 Expected Performance
- GLUE: rho_monotonic ≈ 0.90-0.95 (extensively optimized 2019-2022)
- SuperGLUE: rho_monotonic ≈ 0.80-0.90 (harder benchmark, more variance)
- Source: Recht et al. (2019); visual inspection of PWC leaderboard curves

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| numpy | ≥1.21 | Array operations, diff, rank |
| pandas | ≥1.3 | CSV loading, groupby aggregation |
| scipy | ≥1.7 | spearmanr correlation |
| matplotlib | ≥3.4 | All 4 figures |
| json | stdlib | Results serialization |
| argparse | stdlib | CLI interface |
| pathlib | stdlib | Path handling |

**No new package installs required** — all are standard scientific Python stack present from H-E1.

### 7.2 External Repositories

| Repo | URL | Usage |
|------|-----|-------|
| modestyachts/imagenet-testbed | https://github.com/modestyachts/imagenet-testbed | Reference for gain rate methodology (no code copied) |
| paperswithcode/sota-extractor | https://github.com/paperswithcode/sota-extractor | Reference for PWC data structure (no code copied) |

### 7.3 H-E1 Artifacts Required

| File | Purpose |
|------|---------|
| `data/glue_timeseries_clean.csv` | GLUE monthly timeseries |
| `data/superglue_timeseries_clean.csv` | SuperGLUE monthly timeseries |

---

## 8. Non-Functional Requirements

- **Reproducibility:** Single seed (deterministic — Spearman has no stochastic component). Results must match across runs.
- **Runtime:** Full experiment must complete in <60 seconds on standard laptop CPU.
- **Output location:** All outputs under `docs/youra_research/h-m1/` subfolder (results/, figures/).
- **Error handling:** Fail loudly with informative message if H-E1 CSVs missing (no silent fallback).
- **Code structure:** Single `experiment_h_m1.py` script + helper module `temporal_analysis.py`.

---

## 9. Out of Scope

- Re-downloading GLUE/SuperGLUE data (H-E1 responsibility)
- Model training or fine-tuning (statistical analysis only)
- p-value interpretation (PoC mode: direction-based, not significance-based)
- Other benchmarks beyond GLUE and SuperGLUE
- Parametric correlation methods (Pearson) — Spearman specified by Phase 2B
