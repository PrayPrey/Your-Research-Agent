# Phase 2B Context: H-M1

**Generated:** 2026-07-13T08:42:00+00:00
**Source:** 02b_verification_plan.md (Section 2.2)
**Hypothesis ID:** H-M1
**Type:** MECHANISM

---

## Hypothesis Information

### Statement
Dataset characteristics (sample size, dimensionality, signal properties) determine which method families have structural advantages.

### Rationale
Tests causal step 1 of 4. Zhou: small datasets benefit from augmentation (+17pp), Champneys: structured problems favor polynomial bases.

### Type
MECHANISM

---

## Variables

**Independent Variables:**
- Dataset features (sample size, dimensionality, class imbalance, signal statistics)

**Dependent Variables:**
- Method family structural advantage indicators (correlation with rankings)

**Controlled Variables:**
- Tier 1+2 feature computation (<1 min)
- Domain diversity

---

## Experimental Setup

**Dataset:**
- Name: Aggregated Benchmark Collection
- Type: custom (reuse from H-E1)
- Source: Multi-source literature mining (OGB, FedML, LEAF, pFL-Bench, Papers with Code, Manual)
- Path: ./data/collected_benchmarks/ (from H-E1)
- Hypothesis Fit: Contains diverse dataset characteristics needed for correlation analysis

**Model:**
- Name: Random Forest Meta-Classifier
- Type: Ensemble tree-based classifier
- Source: scikit-learn RandomForestClassifier(n_estimators=100, max_depth=10)
- Hypothesis Fit: Interpretable (feature importance), handles nonlinear relationships, robust to small samples

---

## Verification Protocol

1. Compute Tier 1+2 features for all collected benchmarks
2. Measure correlation between features and method rankings (Spearman ρ)
3. Test: features show significant correlation (p < 0.05) with method performance

---

## Success Criteria (SHOULD_WORK Gate)

**Primary:**
- Feature-ranking correlation ρ > 0.3, p < 0.05

**Secondary:**
- No features show inverse correlation

---

## Failure Response

- IF ρ < 0.3 OR p > 0.05: EXPLORE Tier 3 features or PIVOT to simpler model

---

## Dependencies

**Prerequisites:** H-E1 (MUST_WORK gate)

**Falsifier:** If features show zero correlation (ρ ≈ 0, p > 0.1)

---

## Baseline Comparison Targets

**Baseline:** Random feature-method pairing (ρ ≈ 0, p > 0.1)

**Expected:** Significant positive correlations for sample size, dimensionality features based on Zhou 2025 and Champneys 2024 observations

---

## Source Reference

Phase 2A Causal Step 1
Phase 2B Section 2.2: H-M1 specification
