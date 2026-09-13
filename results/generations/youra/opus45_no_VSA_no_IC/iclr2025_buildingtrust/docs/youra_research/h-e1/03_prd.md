# Product Requirements Document: H-E1

**Date:** 2026-08-24
**Author:** Anonymous
**Hypothesis:** Moderate inter-benchmark correlations (r > baseline AND r < 0.7) exist between TruthfulQA, HaluEval, and FactScore across N≥30 diverse LLMs
**Type:** EXISTENCE (PoC)

---

## Executive Summary

This experiment validates whether truthfulness-related LLM benchmarks (TruthfulQA, HaluEval, FactScore) exhibit moderate inter-correlations, supporting multi-dimensional trustworthiness measurement. Success confirms benchmarks measure related but distinct constructs.

---

## Problem Statement

Current LLM evaluation lacks understanding of whether truthfulness benchmarks measure the same or different underlying capabilities. This meta-analysis determines correlation structure across benchmarks to inform composite evaluation strategies.

---

## Functional Requirements

### FR-1: Data Collection Pipeline
- **FR-1.1:** Fetch benchmark scores from Open LLM Leaderboard API for N≥30 models
- **FR-1.2:** Ensure model diversity: multiple architectures (Llama, Mistral, Falcon, Phi, Qwen), scales (7B-70B), training variants (base, instruct, RLHF, DPO)
- **FR-1.3:** Collect scores for: TruthfulQA (MC2), HaluEval (recognition accuracy), FactScore (precision), MMLU-Physics (baseline)

### FR-2: Correlation Analysis
- **FR-2.1:** Compute Spearman correlation matrix for all benchmark pairs
- **FR-2.2:** Compute baseline reference: r(MMLU-Physics, HaluEval)
- **FR-2.3:** Test hypothesis condition: baseline_r < r(cross-benchmark) < 0.7

### FR-3: Statistical Validation
- **FR-3.1:** Compute p-values for all correlations
- **FR-3.2:** Apply multiple comparison correction (Bonferroni)
- **FR-3.3:** Report 95% confidence intervals

### FR-4: Visualization
- **FR-4.1:** Generate correlation heatmap
- **FR-4.2:** Generate pairwise scatter plots with regression lines
- **FR-4.3:** Generate gate metrics bar chart (cross-benchmark r vs baseline)
- **FR-4.4:** Generate model diversity histogram

---

## Non-Functional Requirements

### NFR-1: Performance
- Complete analysis in <1 hour (excluding data collection)
- No GPU required

### NFR-2: Reproducibility
- Seed all random operations (N/A for deterministic correlation)
- Log all model selections and data sources

### NFR-3: Data Quality
- Require complete scores on all 4 benchmarks per model
- Handle missing values via listwise deletion

---

## Success Criteria

### Primary (Gate Condition)
- **PASS:** All cross-benchmark correlations satisfy: baseline_r < r < 0.7
- **FAIL:** Any r ≤ baseline_r OR any r ≥ 0.7

### Secondary
- Code executes without error
- Visualizations generated successfully
- Statistical significance: p < 0.05 for primary correlations

---

## Data Specifications

| Dataset | Source | Size | Metric |
|---------|--------|------|--------|
| TruthfulQA | lm-evaluation-harness | 817 questions | MC2 accuracy |
| HaluEval | RUCAIBox/HaluEval | 35K samples | Recognition accuracy |
| FactScore | shmsw25/FActScore | 500 entities | Factual precision |
| MMLU-Physics | lm-evaluation-harness | subset | Accuracy (baseline) |

---

## Dependencies

- Python 3.10+
- pandas, numpy, scipy, matplotlib, seaborn
- huggingface_hub (API access)

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Insufficient models with all scores | Extend search to additional leaderboards |
| Missing FactScore data | Use alternative factual benchmark if needed |
| High correlation found (r > 0.7) | Document as negative result, hypothesis fails |

---

*Generated for Phase 3 Implementation Planning*
