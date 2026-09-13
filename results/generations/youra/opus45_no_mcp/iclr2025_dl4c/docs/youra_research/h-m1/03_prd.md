# Product Requirements Document: h-m1

**Hypothesis:** Fine-Grained Feedback Targets Error Line Tokens
**Date:** 2026-08-19
**Type:** MECHANISM
**Phase:** Implementation Planning
**Prerequisite:** H-E1 (VALIDATED)

---

## Executive Summary

Validate that RLTF's fine-grained reward mechanism concentrates gradient signal at error-line tokens via traceback parsing. This is the first causal step in the mechanism chain: demonstrating that per-token penalties localize credit to the actual error location.

**Success Criterion:** 
- Gradient concentration ratio (error_line / other_lines) > 1.0 for >80% of samples
- >80% of penalty gradient within ±2 lines of traceback location for >80% of samples

---

## Problem Statement

H-E1 established that error-type gating improves sample efficiency. H-M1 tests the underlying mechanism: does fine-grained feedback actually localize gradient signal to error-line tokens? If the gradient spreads uniformly despite per-token penalties, the theoretical basis for RLTF's fine-grained approach would be undermined.

---

## Functional Requirements

### FR-1: Reuse H-E1 Infrastructure
- Reuse `h-e1/code/reward.py` for error classification and traceback parsing
- Reuse `h-e1/code/data.py` for APPS dataset loading
- Reuse `h-e1/code/model.py` for CodeT5-large wrapper

### FR-2: Gradient Tracking Module
- Track per-token gradients during backward pass
- Map token indices to source code line numbers
- Aggregate gradient magnitudes by line

### FR-3: Sample Collection
- Generate 500 failing code samples from APPS using CodeT5
- Execute each sample and collect tracebacks
- Filter to samples with parseable traceback line numbers

### FR-4: Concentration Analysis
- For each sample:
  - Apply fine-grained reward (error-line penalty)
  - Compute single backward pass
  - Measure gradient magnitude at error line vs other lines
- Aggregate: concentration ratio, within-±2-lines percentage

### FR-5: Error Type Stratification
- Stratify analysis by error type (U_line vs U_ignore)
- Report concentration metrics separately per category
- Include random baseline (random line penalties)

### FR-6: Visualization
- Required: Bar chart of mean gradient at error-line vs other lines
- Histogram of concentration ratios across 500 samples
- Heatmap of gradient by line position (error line centered)
- U_line vs U_ignore concentration comparison

---

## Non-Functional Requirements

### NFR-1: No Training Required
- This is analysis-only experiment
- Single backward pass per sample, no weight updates
- Reuse pre-trained CodeT5-large weights

### NFR-2: Statistical Validity
- 500 samples provides sufficient statistical power
- Report confidence intervals on concentration metrics
- One-sample t-test for mean ratio > 1.0

### NFR-3: Compute Budget
- Single GPU, ~2-3 hours for full analysis
- No multi-seed required (mechanism test, not performance)

---

## Success Criteria

| Metric | Condition | Threshold |
|--------|-----------|-----------|
| Primary | mean(concentration_ratio) | > 1.0 |
| Secondary | mean(within_2_lines_pct) | > 0.80 |
| Statistical | Primary criterion | p < 0.05 (t-test) |
| Stratification | U_line ratio > U_ignore ratio | Expected |

---

## Dependencies

| Dependency | Source | Notes |
|------------|--------|-------|
| H-E1 codebase | ../h-e1/code/ | Reuse reward.py, data.py, model.py |
| CodeT5-large | HuggingFace | Salesforce/codet5-large |
| APPS Dataset | HuggingFace | codeparrot/apps |
| PyTorch | pip | >=2.0 (autograd) |

---

## Data Specifications

### Input
- 500 failing code samples with tracebacks
- Mix of U_line (~50%) and U_ignore (~50%) error types

### Output
- Per-sample gradient metrics (concentration ratio, within_2_pct)
- Aggregate statistics with confidence intervals
- 4 visualization figures
- PASS/FAIL verdict based on success criteria

---

## Ablation Variants

| Variant | Purpose | Sample Count |
|---------|---------|--------------|
| Full sample | Primary result | 500 |
| U_line only | Error-type effect | 250 |
| U_ignore only | Error-type effect | 250 |
| Random baseline | Sanity check | 500 |

---

## Out of Scope

- Training loop (covered by H-E1)
- Multi-seed validation
- Performance optimization
- Other reward schemes

---

## References

1. Liu et al., "RLTF: Reinforcement Learning from Unit Test Feedback" (NeurIPS 2023) - Equations 4-5
2. H-E1 validated implementation - reward.py, data.py, model.py
3. PyTorch autograd documentation
