# Product Requirements Document: H-E1

**Date:** 2026-08-19
**Hypothesis:** H-E1 - Existence of Orthogonal Error Classes
**Type:** EXISTENCE (LIGHT tier)
**Gate:** MUST_WORK - Jaccard similarity < 0.3

---

## Executive Summary

Validate that errors detected by static analysis (pylint/mypy) are categorically different from errors detected by execution (test failures) on LLM-generated code. This is the foundation hypothesis for the Static-Execution Feedback Orthogonality research.

---

## Problem Statement

**Research Question:** Are static analysis errors and execution errors orthogonal (non-overlapping) error classes?

**Success Criterion:** Mean Jaccard similarity between static and execution error sets < 0.3 across 563 HumanEval+/MBPP+ problems.

---

## Functional Requirements

### FR-1: Dataset Loading
- Load HumanEval+ (164 problems) via evalplus API
- Load MBPP+ (399 problems) via evalplus API
- Total: 563 problems for analysis

### FR-2: Code Generation
- Generate initial code solutions using CodeLlama-7B-Instruct or GPT-3.5-Turbo
- One solution per problem (pass@1 generation)
- Store generated code for analysis

### FR-3: Static Analysis Pipeline
- Run pylint on each generated solution
- Run mypy on each generated solution
- Collect error codes/messages into a set per problem
- Categorize as "structural errors"

### FR-4: Execution Analysis Pipeline
- Run evalplus test suite for each problem
- Collect test failure types (wrong_answer, runtime_error, timeout)
- Categorize as "behavioral errors"

### FR-5: Jaccard Similarity Computation
- Compute Jaccard similarity: |A ∩ B| / |A ∪ B|
- Calculate per-problem and aggregate mean
- Track overlap categories (static-only, exec-only, both)

### FR-6: Visualization
- Gate metrics bar chart (threshold vs actual)
- Jaccard distribution histogram
- Error category breakdown (stacked bar)
- Per-benchmark comparison (HumanEval+ vs MBPP+)

---

## Non-Functional Requirements

### NFR-1: Scale
- Process all 563 problems (no subsampling)
- Use full test suites from evalplus

### NFR-2: Reproducibility
- Fixed random seed for any LLM sampling
- Version-pinned dependencies (evalplus, pylint, mypy)

### NFR-3: Performance
- Complete analysis within 24 hours on single GPU

---

## Data Specifications

| Dataset | Source | Size | Format |
|---------|--------|------|--------|
| HumanEval+ | evalplus | 164 | Python problems |
| MBPP+ | evalplus | 399 | Python problems |

---

## Evaluation Metrics

| Metric | Description | Threshold |
|--------|-------------|-----------|
| Mean Jaccard | Avg overlap between error sets | < 0.3 (GATE) |
| Non-Overlapping % | Problems with single-source errors | > 70% |
| Static-Only Count | Problems with only static errors | Report |
| Exec-Only Count | Problems with only exec errors | Report |

---

## Success Criteria

1. **GATE PASS:** Mean Jaccard similarity < 0.3
2. **SECONDARY:** Non-overlapping percentage > 70%
3. **OUTPUT:** All 4 figures generated and saved

---

## Dependencies

- evalplus library (HumanEval+/MBPP+ loading)
- pylint (static analysis)
- mypy (type checking)
- transformers (CodeLlama) OR openai (GPT-3.5-Turbo)
- matplotlib/seaborn (visualization)

---

## Out of Scope

- Model training (analysis only)
- Self-refine iterations (tested in H-M3, H-M4)
- Multi-model comparison (future work)
