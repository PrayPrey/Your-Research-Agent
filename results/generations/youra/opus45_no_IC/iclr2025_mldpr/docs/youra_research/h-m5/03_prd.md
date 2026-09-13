# Product Requirements Document: H-M5

**Date:** 2026-08-10
**Hypothesis:** Concentration-diversity cycle reinforces itself via positive feedback loop
**Type:** MECHANISM
**Tier:** FULL

---

## Executive Summary

H-M5 tests whether benchmark concentration (HHI) temporally precedes and predicts diversity decline (entropy), establishing a causal feedback mechanism. This validates the final link in the benchmark lock-in chain: concentration → reduced diversity → further concentration.

**Key Deliverable:** Lagged panel regression with Granger causality analysis demonstrating temporal precedence of HHI on entropy.

---

## Problem Statement

H-M4 established strong negative correlation (ρ=-0.958) between concentration and diversity. However, correlation does not establish causation or temporal ordering. H-M5 must demonstrate:
1. HHI at time t-1 predicts entropy at time t (not reverse)
2. Granger causality runs from HHI to entropy (not bidirectional)

---

## Functional Requirements

### FR-1: Data Loading and Preparation
- **FR-1.1:** Load H-E1 panel dataset (21 venue-years: 3 venues × 7 years)
- **FR-1.2:** Create lagged variables (HHI_{t-1}, entropy_{t-1})
- **FR-1.3:** Set MultiIndex (venue, year) for panel structure
- **FR-1.4:** Drop first year per venue (no lag available) → 18 observations

### FR-2: Baseline Model (Pooled OLS)
- **FR-2.1:** Implement Pooled OLS: Entropy_t ~ HHI_{t-1} + PaperCount_t
- **FR-2.2:** Report coefficient, p-value, R² without fixed effects
- **FR-2.3:** Purpose: Naive correlation baseline

### FR-3: Primary Model (Panel OLS with Fixed Effects)
- **FR-3.1:** Implement Two-Way Fixed Effects Panel Regression
- **FR-3.2:** Specification: Entropy_{it} = α_i + γ_t + β₁·HHI_{i,t-1} + β₂·PaperCount_{it} + ε_{it}
- **FR-3.3:** Use linearmodels.PanelOLS with entity_effects=True, time_effects=True
- **FR-3.4:** Use clustered standard errors (cluster_entity=True)
- **FR-3.5:** Extract and report: β(HHI_{t-1}), p-value, 95% CI, R²

### FR-4: Granger Causality Tests
- **FR-4.1:** Test HHI → entropy direction per venue (maxlag=2)
- **FR-4.2:** Test reverse direction: entropy → HHI per venue
- **FR-4.3:** Use statsmodels.grangercausalitytests with ssr_ftest
- **FR-4.4:** Aggregate results across venues (count significant at p<0.05)

### FR-5: Robustness Checks
- **FR-5.1:** Alternative lag structure (2-year lag: HHI_{t-2})
- **FR-5.2:** Model without time fixed effects (entity only)
- **FR-5.3:** Delta specification: ΔEntropy ~ ΔHHI_{t-1}

### FR-6: Visualization
- **FR-6.1:** Gate metrics figure: β coefficient with 95% CI, significance line
- **FR-6.2:** Scatter plot: HHI_{t-1} vs Entropy_t, colored by venue
- **FR-6.3:** Time series: HHI and entropy trends per venue (dual y-axis)
- **FR-6.4:** Granger causality heatmap: p-values both directions
- **FR-6.5:** Residual diagnostics: QQ plot, residuals vs fitted

### FR-7: Results Export
- **FR-7.1:** Save regression results to JSON
- **FR-7.2:** Save figures to h-m5/figures/
- **FR-7.3:** Generate summary statistics table

---

## Non-Functional Requirements

### NFR-1: Statistical Validity
- Use established econometrics libraries (linearmodels, statsmodels)
- Report confidence intervals given small N (18-21 observations)
- Acknowledge statistical power limitations in documentation

### NFR-2: Reproducibility
- Set random seeds where applicable
- Log all parameters and library versions
- Save intermediate data transformations

### NFR-3: Performance
- Analysis should complete in <30 seconds on standard hardware
- No GPU requirements (statistical analysis only)

---

## Dependencies

### Data Dependencies
- H-E1 validated data: `docs/youra_research/h-e1/data/venue_year_metrics.csv`
- Required columns: venue, year, hhi, entropy, paper_count

### Library Dependencies
```
linearmodels>=7.0
statsmodels>=0.14
pandas>=2.0
numpy>=1.24
matplotlib>=3.7
seaborn>=0.12
```

### Prerequisite Hypotheses
- H-M4: COMPLETED (gate satisfied: ρ=-0.958, p<0.001)

---

## Success Criteria

### Gate Condition (SHOULD_WORK)
| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| β(HHI_{t-1}) | < 0 | Primary |
| p-value | < 0.05 | Primary |
| Granger HHI→entropy | p < 0.05 (at least 1 lag) | Secondary |
| Granger entropy→HHI | p > 0.05 (no reverse causality) | Secondary |

### Pass Interpretation
- **PASS:** Concentration temporally precedes diversity decline, supporting causal mechanism
- **FAIL:** Report as correlation only, abandon causal claim

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Small sample size (N=18-21) | High | Medium | Report wide CIs, acknowledge power limitations |
| Granger test requires stationarity | Medium | Medium | Include unit root test, difference if needed |
| Multicollinearity in FE model | Low | Low | Check VIF, entity effects absorb most variation |

---

## Appendix: Phase 2C Completeness Check

| Item | Status | Location |
|------|--------|----------|
| Dataset spec | ✓ | FR-1 |
| Baseline model | ✓ | FR-2 |
| Proposed model | ✓ | FR-3 |
| Granger causality | ✓ | FR-4 |
| Robustness checks | ✓ | FR-5 |
| Visualizations | ✓ | FR-6 |
| Gate condition | ✓ | Success Criteria |
