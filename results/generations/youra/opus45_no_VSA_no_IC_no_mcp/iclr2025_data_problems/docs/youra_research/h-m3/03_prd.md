# Product Requirements Document: H-M3

**Hypothesis:** Under the quality-diversity tradeoff, an optimal balance point exists where quality and diversity are maximized, with measurable peak in dose-response curve

**Date:** 2026-08-28
**Phase:** 3 - Implementation Planning

---

## 1. Problem Statement

H-M2 established deduplication mechanism but was INCONCLUSIVE due to lm-eval integration failure. H-M3 analyzes perplexity filtering threshold sweep data to identify optimal curation threshold via dose-response curve analysis.

## 2. Objectives

1. Load existing sweep data from H-E1/H-M2 (or generate if unavailable)
2. Fit polynomial models (linear, quadratic, cubic) to benchmark scores
3. Identify optimal threshold via derivative analysis
4. Compute bootstrap confidence intervals
5. Verify peak is internal (p20-p80) with tight CI

## 3. Success Criteria

| Criterion | Target |
|-----------|--------|
| Peak location | Internal (p20-p80, not boundary) |
| Best model | Non-linear (quadratic or cubic) |
| CI width | ≤ 30 percentile points |
| Visualization | Dose-response curve with CI band |

## 4. Scope

### In Scope
- Polynomial regression on sweep data
- Model selection via AIC/BIC
- Bootstrap CI computation
- Dose-response visualization
- lm-eval benchmark evaluation (if new runs needed)

### Out of Scope
- New architecture experiments
- Alternative filtering methods
- Hyperparameter tuning beyond thresholds

## 5. Technical Requirements

### Data
- Source: H-E1/H-M2 sweep results or fresh RedPajama-v2 10B-token runs
- Thresholds: p0, p10, p20, p30, p40, p50, p60, p70, p80, p90
- Seeds: 3 per threshold
- Metrics: HellaSwag, ARC-Easy, PIQA, WinoGrande

### Dependencies
- Python 3.10+
- numpy, scipy, statsmodels
- lm-evaluation-harness v0.4+
- matplotlib/plotly for visualization

## 6. Deliverables

1. `dose_response_analysis.py` - Core analysis module
2. `run_analysis.py` - Main execution script
3. `figures/dose_response_curve.png` - Primary visualization
4. `04_validation.md` - Results report

## 7. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Missing sweep data | Fall back to fresh lm-eval runs on available checkpoints |
| Linear model wins | Document plateau finding, route to EXPLORE |
| Wide CI | Increase bootstrap iterations, add seeds if possible |

## 8. Timeline

- Implementation: 4-6 hours
- Validation: 2 hours (analysis only, no GPU training)
