# Phase 2B Context: H-M1

**Generated:** 2026-08-25
**Hypothesis ID:** H-M1
**Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under retrospective validation using the corpus from H-E1, if we measure correlation between 10-sample overhead (O_10) and full-dataset overhead (O_full), then correlation r will exceed 0.7, because overhead operations (like KL divergence in h-e1) scale predictably across sample sizes.

### Type
MECHANISM

### Rationale
Core mechanism assumption (A1). If O_10 doesn't correlate with O_full, extrapolation from Gate 1 micro-pilot to full-scale prediction is invalid.

### Variables
- **Independent:** Sample size (10 vs full dataset)
- **Dependent:** Measured overhead (O_10, O_full)
- **Controlled:** Hypothesis type, benchmark dataset, hardware

---

## Experimental Setup

### Dataset
**Name:** Retrospective ML Projects Corpus (from H-E1)
**Type:** custom
**Source:** H-E1 validation output (04_validation.md)
**Details:** 
- Corpus of 30+ hypotheses with both 10-sample and full-scale overhead measurements
- Extracted from Papers with Code + ML conference papers (NeurIPS, ICML, ICLR)
- Stratified by overhead level (low <20%, mid 20-80%, high >80%)

### Model
**Type:** Statistical correlation analysis
**Architecture:** Pearson correlation + linear regression
**Implementation:** scipy.stats for correlation, sklearn.linear_model for regression

---

## Verification Protocol

1. Extract O_10 and O_full from each hypothesis in the corpus (from H-E1 results)
2. Compute Pearson correlation r between O_10 and O_full across all hypotheses
3. Fit linear regression O_full = k × O_10 to derive scaling factor k
4. Compute per-hypothesis-type k values (attention, gradient, etc)
5. Test if r >0.7 and k variance is low within types

---

## Success Criteria (PoC)

**Primary:** Correlation r >0.7 between O_10 and O_full
**Secondary:** Scaling factor k consistent within hypothesis types (CV <30%)

---

## Failure Response

- **IF r <0.5:** ABANDON (extrapolation fundamentally invalid)
- **IF 0.5 ≤ r <0.7:** EXPLORE non-linear models or per-type calibration

---

## Gate Conditions

**Gate Type:** MUST_WORK
**If Fail:** Predictive scaling invalid → framework collapses

---

## Dependencies

**Prerequisites:** H-E1 (requires corpus)
**Dependent Hypotheses:** H-M2, H-M3

---

## Previous Hypothesis Results

### H-E1 Validation Results
(To be loaded from h-e1/04_validation.md)

**Expected Outputs:**
- Validated corpus with ≥30 hypotheses
- Overhead measurements: O_10 and O_full for each hypothesis
- Stratification breakdown (low/mid/high overhead categories)

---

*Context generated for Phase 2C experiment design*
*Source: Phase 2A Section 1.3 Causal Step 1, Assumption A1*
