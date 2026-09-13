# Product Requirements Document: H-M2 Experiment

**Hypothesis:** If agents identify error clusters (H-M1), then they will prioritize fixes targeting root causes (high fix-impact-ratio per modification) rather than addressing errors arbitrarily, because strategic prioritization maximizes test pass rate improvement per iteration.

**Date:** 2026-08-28
**Author:** Phase 3 Implementation Planning
**Experiment ID:** h-m2

---

## Executive Summary

H-M2 tests whether agents strategically prioritize debugging fixes by targeting root causes. Building on H-M1's validated clustering ability (coefficient 1.909), this experiment measures whether agents show higher proportion of high-impact fixes (Δpassing_tests ≥ 2) compared to random/sequential baselines.

**Success Criteria:** Proportion of high-impact fixes (Proposed) > Proportion (Baseline)

**Gate:** MUST_WORK - Failure stops workflow (PIVOT)

---

## Functional Requirements

### FR1: Dataset Reuse
**Priority:** P0
**Description:** Reuse 50 Codeforces problems from H-M1 (rating 1200-1800, solve_count >1000) for controlled comparison.
**Acceptance Criteria:**
- Problems cached from H-M1 or fetched via Codeforces API
- 15-50 test cases per problem
- 986 test failures across 4 error types (validated in H-M1)

### FR2: Baseline Agent Implementation
**Priority:** P0
**Description:** Sequential debugging baseline - address test failures one-by-one without clustering.
**Acceptance Criteria:**
- GPT-4 Turbo (gpt-4-turbo-2024-04-09) with temperature 0.7
- Iterate through failed tests in original order
- Max 10 fix iterations per problem
- Track Δpassing_tests per modification

### FR3: Proposed Agent Implementation
**Priority:** P0
**Description:** Root cause prioritization - use H-M1 clustering to prioritize fixes by cluster size.
**Acceptance Criteria:**
- GPT-4 Turbo + RootCausePrioritizer mechanism
- Cluster errors using H-M1 approach
- Sort clusters by size (descending)
- Address largest cluster first
- Track Δpassing_tests per modification

### FR4: Fix-Impact-Ratio Measurement
**Priority:** P0
**Description:** Measure fix impact as Δpassing_tests = sum(after) - sum(before).
**Acceptance Criteria:**
- Record test results before and after each modification
- Calculate Δpassing_tests
- Classify as high-impact if Δ ≥ 2
- Store fix impacts for all modifications

### FR5: Proportion Metric Calculation
**Priority:** P0
**Description:** Calculate proportion of high-impact fixes for both baseline and proposed.
**Acceptance Criteria:**
- `high_impact_count = sum(1 for d in fix_impacts if d >= 2)`
- `proportion_high_impact = high_impact_count / len(fix_impacts)`
- Calculate for baseline and proposed separately
- Compare: proposed > baseline (directional test for PoC)

### FR6: Visualization Generation
**Priority:** P0
**Description:** Generate required and additional figures.
**Acceptance Criteria:**
- **Required:** Bar chart comparing proportion of high-impact fixes (Baseline vs Proposed)
- **Additional:** Histogram of Δpassing_tests distribution
- **Additional:** Cumulative tests passed over iteration count
- **Additional:** Scatter plot of cluster size vs fix impact
- Save all figures to `h-m2/figures/`

---

## Non-Functional Requirements

### NFR1: Reproducibility
- Fixed random seed (1) for deterministic results
- Temperature 0.7 for sampling diversity (same as H-M1)
- Max 10 iterations (consistent with H-M1 setup)

### NFR2: Data Continuity
- Reuse H-M1 dataset (50 problems) for controlled comparison
- Preserve error distribution (4 types, 986 failures)

### NFR3: Evaluation Protocol
- PoC success: `proposed_metric > baseline_metric` (directional)
- No statistical test required for PoC
- Track all fix sequences for post-hoc analysis

---

## Technical Constraints

### TC1: API Dependencies
- OpenAI API access required (GPT-4 Turbo)
- Codeforces API for dataset loading (if not cached from H-M1)

### TC2: Compute Requirements
- 50 problems × 2 agents × 10 iterations × ~30s per fix = ~5 hours runtime
- Minimal GPU requirements (inference only)

### TC3: Storage
- Dataset cache: ~10 MB (50 problems + test cases)
- Experiment results: ~50 MB (fix sequences, test results)
- Figures: ~5 MB (4 plots)

---

## Success Criteria

**PoC Pass Condition:**
1. Code runs without error
2. `proportion_high_impact_proposed > proportion_high_impact_baseline`

**Expected Performance:**
- Baseline: ~0.15-0.25 (random/sequential distribution)
- Proposed: >0.35 (strategic prioritization)

---

## Dependencies

**Prerequisites:**
- H-M1 VALIDATED (clustering coefficient 1.909, p=0.001)
- H-M1 dataset (50 Codeforces problems)
- H-M1 clustering mechanism

**External:**
- OpenAI API (GPT-4 Turbo)
- Codeforces API (dataset loading)

---

## Out of Scope

- Statistical significance testing (PoC only)
- Fine-tuning GPT-4 model
- Multi-agent collaboration
- Alternative clustering algorithms
- Hyperparameter tuning beyond temperature 0.7

---

## Appendix: Reference Implementations

**Archon KB Sources:**
- Fix-impact-ratio measurement pattern
- Prioritization by cluster size

**GitHub Repos:**
- openai/human-eval-infilling: Fix-impact evaluation harness
- microsoft/repobench: Clustering integration
- codeforces-api/codeforces-problems: Dataset loading

---

*This PRD defines the scope for Phase 4 implementation.*
*Next: Architecture, Logic, and Configuration documents.*
