# Product Requirements Document: h-m3

**Hypothesis:** Targeted edits have higher probability of fixing bugs than global rewrites
**Type:** MECHANISM
**Date:** 2026-08-28
**Gate:** MUST_WORK

---

## Executive Summary

This experiment validates the mechanism hypothesis that targeted code edits (small, localized changes) achieve higher bug fix rates than global rewrites (large-scale code regeneration). Building on h-m2's finding that detailed execution feedback enables targeted edits, h-m3 tests whether this edit scope causally determines fix success.

---

## Problem Statement

When LLMs refine buggy code based on execution feedback, they produce edits of varying scope. Some edits are targeted (few AST changes at bug location), while others are global rewrites (extensive changes across the code). Understanding which edit type has higher fix probability is essential for optimizing iterative code refinement systems.

---

## Functional Requirements

### FR-1: Dataset Loading
- Load HumanEval dataset (164 problems) from HuggingFace
- Load MBPP dataset (500+ problems) from HuggingFace
- Use full test sets for statistically meaningful results

### FR-2: Model Integration
- Integrate CodeLlama-7B-Instruct as primary model
- Integrate StarCoder-7B as secondary model for generalization
- Configure deterministic inference (temperature=0.0)

### FR-3: Code Generation Pipeline
- Generate initial code solutions for each problem
- Execute code against test cases
- Capture detailed execution feedback (error traces, line numbers)

### FR-4: Code Refinement Pipeline
- Feed execution feedback to model for code refinement
- Generate refined code within single iteration
- Store both original and refined code versions

### FR-5: AST Edit Distance Computation
- Parse code before/after using tree-sitter
- Compute AST node differences
- Classify edits: targeted (≤5 AST operations) vs global (>5)

### FR-6: Fix Rate Analysis
- Execute refined code against test cases
- Record fix outcomes per edit scope category
- Compute targeted_fix_rate and global_fix_rate

### FR-7: Statistical Analysis
- Compare fix rates between edit scope categories
- Compute effect size (targeted - global)
- Validate MUST_WORK gate condition

### FR-8: Visualization
- Bar chart: targeted vs global fix rates
- Histogram: AST edit distance distribution
- Scatter plot: fix probability vs AST distance

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed for all operations
- Deterministic model inference
- Version-locked dependencies

### NFR-2: Performance
- Process full HumanEval (164) + MBPP (500+) problems
- Complete within reasonable compute budget (~2-4 GPU hours)

### NFR-3: Modularity
- Reuse h-m2 execution feedback components
- Clean separation of AST analysis from fix evaluation

---

## Success Criteria

### Primary Gate (MUST_WORK)
- `targeted_fix_rate > global_fix_rate`

### Expected Performance
- Based on h-m2: detailed feedback yields 40% higher pass rate
- Hypothesis: majority of successful fixes come from targeted edits

---

## Dependencies

### From h-m2
- Dataset pipeline (HumanEval, MBPP loading)
- Model configuration (CodeLlama-7B-Instruct)
- Execution feedback generation (detailed traces)

### External
- tree-sitter-python for AST parsing
- bigcode-evaluation-harness for execution

---

## Baselines

### Baseline 1: Global Edits
- Edits with AST distance > 5
- Expected lower fix rate

### Proposed: Targeted Edits
- Edits with AST distance ≤ 5
- Expected higher fix rate

---

## Out of Scope

- Training or fine-tuning models
- Multiple refinement iterations (single iteration per h-m2)
- Cross-language generalization
