# Product Requirements Document: H-M1

**Date:** 2026-08-19
**Hypothesis:** Observed coupling persists when controlling for instance difficulty (partial phi ≥ 0.25)
**Type:** MECHANISM
**Prerequisites:** h-e1 (COMPLETED, PASS)

---

## Executive Summary

Validate whether coupling between trustworthiness dimensions (discovered in h-e1) persists when controlling for instance difficulty, or is spurious correlation. Implement dual-validation statistical analysis using partial correlation and stratified quartile methods.

**Core Deliverable:** Difficulty-controlled coupling analyzer showing partial phi ≥ 0.25 for ≥2 dimension pairs.

---

## Problem Statement

h-e1 found 6 dimension pairs with significant coupling (phi ≥ 0.3, p < 0.01). Critical question: Is coupling real (shared vulnerability mechanisms) or artifact (hard instances fail everything)?

Without difficulty control, coupling measurements conflate two effects:
1. True dimensional correlation (target signal)
2. Difficulty-driven correlation (confound)

Separating these validates whether observed patterns reflect genuine model behavior structure.

---

## Functional Requirements

### FR1: Data Loading
Load h-e1 coupling data (500 instances × 3 models × 5 dimensions) from `h-e1_code/data/` directory.

**Acceptance:** DataFrame with columns: instance_id, model, truthfulness, robustness, fairness, safety, privacy

### FR2: Difficulty Score Generation
Generate simulated difficulty scores (Normal dist, mean=0.5, std=0.15, clipped [0,1]) independent of dimension labels.

**Acceptance:** 
- |correlation(difficulty, dimension)| < 0.2 for all dimensions
- Difficulty column added to DataFrame

### FR3: Partial Correlation Analysis
Compute partial correlation controlling for difficulty using pingouin library for all 6 h-e1 significant pairs.

**Acceptance:**
- Output: partial_r, p_value, CI95% per pair
- Method: `pingouin.partial_corr(data, x=dim1, y=dim2, covar='difficulty_score')`

### FR4: Stratified Quartile Analysis
Bin instances into difficulty quartiles (Q1-Q4) and compute phi coefficient within each stratum.

**Acceptance:**
- 4 quartiles with ~125 instances each
- Phi + p-value per quartile per dimension pair

### FR5: Dual Validation Protocol
Compare partial correlation results vs stratified results for consistency.

**Acceptance:**
- Both methods agree on coupling persistence (partial phi ≥ 0.25 AND phi ≥ 0.25 in ≥3 quartiles)

### FR6: Visualization
Generate 4 required figures: partial vs raw phi comparison, quartile stratified phi, difficulty independence check, effect size retention.

**Acceptance:** PNG files saved to `h-m1/figures/` directory

---

## Non-Functional Requirements

### NFR1: Performance
Analysis runtime < 5 seconds (statistical computation, no API calls).

### NFR2: Reproducibility
Fixed random seed (42) for difficulty score generation.

### NFR3: Statistical Rigor
Use scipy.stats.chi2_contingency for phi coefficient, pingouin validated implementation for partial correlation.

---

## Data Specifications

**Input Data:**
- Source: h-e1_code/results/coupling_data.csv
- Format: CSV with binary dimension labels
- Size: 500 rows (instances) × 8 columns

**Output Data:**
- Partial correlation results: DataFrame (6 rows × 4 columns: pair, partial_r, p_value, CI95%)
- Stratified results: DataFrame (24 rows: 6 pairs × 4 quartiles)
- Figures: 4 PNG files

---

## Dependencies

**Python Libraries:**
- pingouin >= 0.5.0 (partial correlation)
- scipy >= 1.7.0 (chi2_contingency)
- pandas >= 1.3.0 (data manipulation)
- numpy >= 1.21.0 (random generation)
- matplotlib >= 3.4.0 (plotting)

**Data Dependencies:**
- h-e1 coupling data (prerequisite must be COMPLETED)

---

## Success Criteria

### Gate Validation (MUST_WORK):
- Partial phi ≥ 0.25 for ≥2 dimension pairs
- Coupling persists in ≥3 quartiles for those pairs
- |correlation(difficulty, dimensions)| < 0.2 (independence verified)

### Technical Validation:
- All 6 h-e1 pairs analyzed
- Partial correlation values ∈ [-1, 1] (valid range)
- No runtime errors, reproducible results (seed=42)

### Outputs Generated:
- Partial correlation table (CSV)
- Stratified analysis table (CSV)
- 4 visualization figures (PNG)
- Validation report (console output)

---

## Out of Scope

- Real difficulty scores from API logprobs (Phase 5 baseline comparison)
- MultiTrust dataset access (gated, using synthetic)
- Additional covariates beyond difficulty
- Alternative partial correlation methods (pingouin only)

---

## Assumptions

1. h-e1 coupling data available and validated
2. Synthetic difficulty scores sufficient proxy for PoC validation
3. Partial correlation equivalent to partial phi for binary data
4. Quartile binning preserves enough samples per stratum (≥100 per quartile)

---

## Risks

**R1: Coupling disappears with difficulty control** (40% likelihood)
- Mitigation: Dual validation (partial + stratified) provides convergent evidence
- Contingency: Route to Phase 2A-Dialogue if partial phi 0.15-0.24

**R2: Difficulty proxy validity** (60% likelihood, synthetic data)
- Mitigation: Compare two independent methods (partial corr vs stratified)
- Contingency: Phase 5 baseline comparison with real API logprobs

**R3: Small quartile sample sizes** (<100 instances)
- Mitigation: Use `duplicates='drop'` in pd.qcut to handle ties
- Contingency: Merge adjacent quartiles if needed

---

## Validation Checklist

- [ ] h-e1 data loaded successfully (500 instances)
- [ ] Difficulty scores generated with |corr| < 0.2
- [ ] Partial correlation computed for 6 pairs
- [ ] Stratified analysis completed for 4 quartiles
- [ ] Dual validation results agree
- [ ] 4 figures generated and saved
- [ ] Gate criteria evaluated (partial phi ≥ 0.25 for ≥2 pairs)
