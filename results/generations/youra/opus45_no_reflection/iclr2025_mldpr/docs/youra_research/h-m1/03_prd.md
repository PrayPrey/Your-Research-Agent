# Product Requirements Document: H-M1

**Hypothesis:** Foundation Model Emergence Timeline
**Date:** 2026-08-18
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## Executive Summary

Validate that foundation models (GPT-3, ViT, BERT, RoBERTa, T5) represent statistically significant high-impact papers by measuring citation counts against field distribution. Success requires z-score > 2.0 for majority of target papers.

---

## Problem Statement

H-E1 confirmed phase transition exists (change points 2019-04, 2021-03). H-M1 tests whether foundation model emergence was significant enough to plausibly drive this ecosystem change.

---

## Functional Requirements

### FR-1: Data Collection
- **FR-1.1:** Fetch metadata for 5 foundation model papers via Semantic Scholar API
  - GPT-3 (ARXIV:2005.14165)
  - ViT (ARXIV:2010.11929)
  - BERT (ACL:N19-1423)
  - RoBERTa (ARXIV:1907.11692)
  - T5 (ARXIV:1910.10683)
- **FR-1.2:** Collect comparison set of 1000+ ML papers per year (2019-2021)
  - Venues: NeurIPS, ICML, ACL, CVPR
  - Fields: Computer Science
- **FR-1.3:** Extract citation counts for all papers

### FR-2: Statistical Analysis
- **FR-2.1:** Compute field mean and standard deviation of citation counts
- **FR-2.2:** Calculate z-score for each foundation paper: (citations - mean) / std
- **FR-2.3:** Determine exceeds_2sigma flag for each paper

### FR-3: Visualization
- **FR-3.1:** Generate bar chart of z-scores with 2σ threshold line
- **FR-3.2:** Generate citation distribution histogram with foundation papers marked
- **FR-3.3:** Generate percentile rank table

### FR-4: Validation
- **FR-4.1:** Gate pass condition: ≥3 of 5 foundation papers have z > 2.0
- **FR-4.2:** Report pass/fail with supporting metrics

---

## Non-Functional Requirements

- **NFR-1:** API rate limiting compliance (Semantic Scholar)
- **NFR-2:** Reproducible results (fixed API snapshot or cached data)
- **NFR-3:** Execution time < 10 minutes

---

## Data Requirements

| Dataset | Source | Size | Format |
|---------|--------|------|--------|
| Foundation Papers | Semantic Scholar API | 5 papers | JSON |
| Comparison Set | Semantic Scholar API | 3000+ papers | JSON |

---

## Success Criteria

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| Foundation papers z > 2.0 | ≥3 of 5 | MUST |
| Comparison set size | ≥1000/year | MUST |
| API calls successful | 100% | MUST |

---

## Dependencies

- **Prerequisite:** H-E1 (PASS) - Phase transition confirmed
- **Libraries:** semanticscholar, numpy, scipy, matplotlib

---

## Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| API rate limits | Medium | Caching, batch requests |
| Citation count volatility | Low | Use snapshot date |

---

## Appendix

**Phase 2C Reference:** 02c_experiment_brief.md
**Gate Type:** MUST_WORK - Failure stops hypothesis chain
