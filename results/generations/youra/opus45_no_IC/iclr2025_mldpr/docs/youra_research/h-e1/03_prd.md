# Product Requirements Document: H-E1

**Hypothesis:** HHI concentration measurable from PWC data for NeurIPS/ICML/ICLR (2018-2024)
**Type:** EXISTENCE (Proof-of-Concept)
**Date:** 2026-08-10
**Author:** YouRA Research Pipeline

---

## Executive Summary

Validate that Herfindahl-Hirschman Index (HHI) concentration metrics can be computed from Papers With Code (PWC) dataset-paper linkage data for 21 venue-year combinations (3 venues × 7 years). This is a MUST_WORK gate hypothesis - failure triggers pivot to alternative data sources.

---

## Problem Statement

### Background
ML research evaluation increasingly concentrates on few benchmark datasets. Quantifying this concentration requires computing market-style concentration metrics (HHI) from paper-dataset usage data.

### Objective
Prove PWC data contains sufficient paper-dataset linkages to compute meaningful HHI scores across all target venue-years.

---

## Functional Requirements

### FR-1: Data Acquisition
- **FR-1.1:** Load `pwc-archive/papers-with-abstracts` from HuggingFace Hub
- **FR-1.2:** Load `pwc-archive/evaluation-tables` from HuggingFace Hub
- **FR-1.3:** Fallback: Use `paperswithcode-client` API if HuggingFace unavailable

### FR-2: Data Processing
- **FR-2.1:** Filter papers by venue (NeurIPS, ICML, ICLR)
- **FR-2.2:** Filter papers by year (2018-2024 inclusive)
- **FR-2.3:** Extract dataset tags per paper
- **FR-2.4:** Aggregate dataset usage counts by venue-year

### FR-3: HHI Computation
- **FR-3.1:** Compute HHI per venue-year: `HHI = Σ(share_i²)` where `share_i = count_i / total`
- **FR-3.2:** Return HHI in decimal scale [0, 1]
- **FR-3.3:** Handle edge cases: zero papers, single dataset

### FR-4: Supplementary Metrics
- **FR-4.1:** Compute normalized Shannon entropy per venue-year
- **FR-4.2:** Track paper count per venue-year
- **FR-4.3:** Track unique dataset count per venue-year

### FR-5: Validation
- **FR-5.1:** Verify 21/21 venue-years have valid (non-null) HHI
- **FR-5.2:** Verify all HHI values in range [0, 1]
- **FR-5.3:** Verify HHI variance > 0 (variation exists)

### FR-6: Visualization
- **FR-6.1:** Generate HHI heatmap (venue × year)
- **FR-6.2:** Generate HHI time series (line plot per venue)
- **FR-6.3:** Generate coverage validation bar chart

---

## Non-Functional Requirements

### NFR-1: Performance
- Complete full analysis in < 5 minutes on standard hardware
- Memory usage < 8GB for full dataset processing

### NFR-2: Reproducibility
- Fixed random seed where applicable
- All data sources versioned (snapshot date)
- Output includes data provenance metadata

### NFR-3: Data Quality
- Minimum 100 papers per venue-year for statistical validity
- Document any venue-years below threshold

---

## Success Criteria

| Metric | Threshold | Priority |
|--------|-----------|----------|
| Coverage | 21/21 venue-years with valid HHI | MUST |
| HHI Range | All values in [0, 1] | MUST |
| HHI Variance | > 0 | MUST |
| Paper Count | Mean > 100 per venue-year | SHOULD |

**Gate Logic:**
```python
if valid_count == 21 and variance > 0:
    gate_status = "PASSED"
    proceed_to = "H-M1"
else:
    gate_status = "FAILED"
    action = "PIVOT to Semantic Scholar or OpenAlex"
```

---

## Data Sources

| Source | Type | Identifier |
|--------|------|------------|
| Papers | HuggingFace | `pwc-archive/papers-with-abstracts` |
| Evaluations | HuggingFace | `pwc-archive/evaluation-tables` |
| Fallback API | REST | `paperswithcode-client` PyPI |

---

## Dependencies

- Python 3.8+
- pandas, numpy
- datasets (HuggingFace)
- matplotlib/seaborn (visualization)
- paperswithcode-client (fallback)

---

## Out of Scope

- Model training or ML experiments
- Comparison with alternative concentration metrics
- Causal analysis of concentration trends
- Cross-venue normalization

---

## Appendix: HHI Reference

- HHI < 0.15 (1500 on 10k scale): Competitive
- 0.15 ≤ HHI ≤ 0.25: Moderately concentrated  
- HHI > 0.25 (2500 on 10k scale): Highly concentrated

Source: DOJ/FTC Horizontal Merger Guidelines
