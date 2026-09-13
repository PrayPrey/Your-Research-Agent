# Hypothesis Context: H-M1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-05-19
**Main Hypothesis:** BCBHS — Benchmark-Calibrated Health Score for Cross-Domain Discriminative Collapse Prediction
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under ML benchmarks with ≥20 submissions and ≥2 years history, if submission count accumulates beyond a critical threshold (empirically estimated per benchmark), then score variance in top-k models will fall below 1.5σ_measurement for ≥2 consecutive quarters, because models increasingly overfit test-set statistical properties rather than generalizing, compressing the discriminative score distribution.

### Type
MECHANISM

### Rationale
Tests the first link in the causal chain: that high submission volume causes measurable score compression. This is the mechanism connecting benchmark popularity to degradation. Required before establishing that domain-specific signals emerge from this compression.

---

## Verification Protocol

### Conceptual Test
1. Extract per-benchmark submission time series from Papers With Code API (HuggingFace archive post-July 2025)
2. Compute score variance of top-10 models per benchmark per quarter (2018-2025)
3. Estimate σ_measurement per benchmark from repeated submission scores
4. Apply compression threshold: variance < 1.5σ_measurement for ≥2 consecutive quarters
5. Granger causality test: submission count → score compression (lag analysis)

### Success Criteria
- Primary: Score compression events co-occur with high submission counts (Spearman ρ >0.4, p<0.05)
- Secondary: Granger causality p<0.05 for submission count → compression (2-quarter lag)

### Variables (if applicable)
- **Independent Variable:** Cumulative submission count trajectory per benchmark
- **Dependent Variable:** Score variance in top-k models per quarter; compression indicator (variance < 1.5σ threshold)
- **Controlled Variables:** Benchmark age, model scale growth trend

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Papers With Code Leaderboard Panel
- **Type:** programmatic-api (real data via HuggingFace archive)
- **Source:** pwc-archive/evaluation-tables (HuggingFace) — PWC REST API shut down July 2025
- **Path:** External API — `load_dataset("pwc-archive/evaluation-tables", split="train")`
- **Hypothesis Fit:** PWC leaderboard panel contains per-benchmark time-series of all submissions (model, date, score, task), enabling reconstruction of quarterly score variance and submission count trajectories across 3000+ benchmarks spanning 2018-2025.

### Selected Model
- **Name:** Granger causality analysis + score variance computation (statistical analysis)
- **Type:** Non-parametric statistical tests (no neural network)
- **Source:** statsmodels (Python) for Granger causality; scipy.stats for Spearman ρ
- **Hypothesis Fit:** Granger causality directly tests whether submission count time series causes score variance compression (temporal precedence + explanatory power). Spearman ρ tests monotonic co-occurrence relationship.

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| Score variance + improvement slope (naive) | Unknown — key baseline to beat | Papers With Code (proposed) | No causal direction; no submission count linkage; no temporal analysis |
| Roelofs 2019 overfitting measurement | ~11% accuracy drop on CIFAR-10 retest | CIFAR-10, ImageNet (CV only) | CV-only; no submission count causal mechanism |

### Baseline Performance
- H-E1 established (PASSED): Domain-specific H_d signals discriminate saturated vs. healthy benchmarks (p<0.0001, |d|>5 in all 3 domains, AUC>0.70)
- H-E1 validation results available: CV p<0.0001 |d|=5.267, NLP p<0.0001 |d|=6.910, tabular p<0.0001 |d|=6.515
- These confirm that benchmark health signals are discriminative — H-M1 tests the causal mechanism (submission→compression)

### Gap Analysis
- H-E1 proves EXISTENCE of discriminative signals but does NOT prove causation
- H-M1 fills the causal gap: does submission volume → score compression happen?
- Expected: Spearman ρ >0.4 between submission count and score compression events; Granger causality p<0.05 at 2-quarter lag

---

## Dependencies and Gate Conditions

### Prerequisites
- H-E1: COMPLETED (PASSED) — Domain signals discriminate saturated vs. healthy benchmarks

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow (blocks H-M2, H-M3, H-M4)

**Consequence if Fails:** EXPLORE alternative compression thresholds; check if domain-specific variation explains null result. If Spearman ρ <0.2 in all domains → submission→compression link is absent; reassess BCBHS causal chain.

**Phase Assignment:** Phase 2 (Mechanisms) — Week 3-4

**Estimated Duration:** 2 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
- **Depends on:** H-E1 (EXISTENCE must be confirmed first — H-E1 PASSED)
- **Blocks:** H-M2 (Score Compression → Domain-Specific Degradation Signals)
- **Is part of:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4 causal chain
- **Previous hypothesis results available:** H-E1 validation data and code in h-e1/ folder can inform data pipeline reuse

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS (set by hypothesis loop)
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation (H-E1 PASSED — H-M1 can proceed)
3. Dependency information — reuse H-E1 data pipeline (PWC archive) for efficiency
4. Success criteria: Spearman ρ >0.4 + Granger causality p<0.05 at 2-quarter lag
5. Dataset: Papers With Code Leaderboard Panel (same as H-E1 but focus on CV+NLP submission time series)

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for Granger causality and score compression implementations (Archon, Exa MCP)
3. Reuse H-E1 data pipeline where possible (controlled comparison)
4. Design concrete experiment specification (Level 1.5)
5. Output: h-m1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-M* (Mechanism)**: Baseline is simple correlation (Spearman ρ) vs. causal Granger test

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
