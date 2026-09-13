# Phase 2B Context: H-M1

**Generated:** 2026-08-19
**Hypothesis ID:** h-m1
**Type:** MECHANISM
**Status:** IN_PROGRESS

---

## Hypothesis Statement

Popular benchmarks attract intensive architecture and hyperparameter search investment.

## Full Statement

If datasets have high popularity (Q4 run-rate), then they receive disproportionately more architecture and hyperparameter search investment, because high leaderboard visibility attracts optimization effort.

## Rationale

This tests the first step of the causal chain - whether popular benchmarks actually receive more intensive optimization than low-use alternatives.

## Variables

- **Independent:** Dataset popularity (run-rate quartile)
- **Dependent:** Architecture search intensity (proxy: published paper count, NAS studies)
- **Controlled:** Dataset age, domain type

## Verification Protocol

1. Query OpenML API for top-10 high-use and bottom-10 low-use image classification datasets.
2. Search academic databases for papers explicitly optimizing on each dataset.
3. Count NAS and hyperparameter tuning studies per dataset.
4. Compare search intensity between popularity quartiles.

## Success Criteria

- **Primary:** High-use datasets have significantly more optimization papers (ratio > 3:1)
- **Secondary:** Trend holds across multiple domains

## Gate Condition

- **Type:** MUST_WORK
- **Pass Condition:** High-use datasets have 3:1 more optimization papers
- **Fail Action:** PIVOT: Alternative intensity metrics

## Prerequisites

- h-e1: VALIDATED (PASS)

## Previous Hypothesis Results (h-e1)

- **Status:** COMPLETED, PASS
- **CIFAR-10 gap:** 18.86%
- **SVHN gap:** -2.35%
- **Gap difference:** 21.21%
- **Direction check:** true

## Experimental Setup (from Phase 2B)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Multiple dataset pairs (standard) | Requires paired high-use/low-use datasets |
| **Model** | N/A for this hypothesis | Focus is on paper counting, not model training |

## Implementation Notes

This hypothesis is a **bibliometric study**, not a model training experiment:
- Query OpenML for run counts
- Query Semantic Scholar/Google Scholar for paper counts
- Compute ratio of optimization papers

No GPU training required for this hypothesis.
