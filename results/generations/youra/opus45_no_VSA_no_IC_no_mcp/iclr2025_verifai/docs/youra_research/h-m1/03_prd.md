# Product Requirements Document: H-M1

**Hypothesis:** Information content is preserved across format transformations, verified by reconstruction test where a third-party LLM can extract original error details from structured format with >95% accuracy

**Date:** 2026-08-28
**Type:** MECHANISM
**Prerequisites:** H-E1 (VALIDATED)

---

## Executive Summary

Validate that the structured error format from H-E1 preserves all diagnostic information from raw compiler output. A third-party LLM extracts error fields from the structured format; if extraction accuracy exceeds 95%, the transformation is information-preserving.

---

## Problem Statement

H-E1 showed structured error format improves repair success. H-M1 verifies this improvement is fair by confirming no information loss during transformation. Without this validation, H-E1 results could be questioned.

---

## Functional Requirements

### FR-1: Error Pair Loading
Load (raw_error, structured_error) pairs from H-E1 experiment outputs.
- Source: `../h-e1/data/error_pairs.json`
- Minimum: 500 samples

### FR-2: Ground Truth Extraction
Parse raw compiler output to extract canonical field values:
- error_type
- line_number
- message
- context

### FR-3: LLM Field Extraction
Use third-party LLM (GPT-4 or Claude-3-Sonnet) to extract fields from structured format.
- Temperature: 0 (deterministic)
- Max tokens: 500
- Structured JSON output

### FR-4: Accuracy Computation
Compute field-level accuracy:
- Per-field exact match
- Mean accuracy across all samples
- Sample pass rate (100% field match)

### FR-5: Visualization
Generate figures:
- Gate metrics comparison (accuracy vs 95% threshold)
- Per-field accuracy breakdown
- Accuracy by error type

---

## Non-Functional Requirements

### NFR-1: Determinism
Judge LLM uses temperature=0 for reproducible results.

### NFR-2: API Rate Limits
Handle OpenAI/Anthropic rate limits with exponential backoff.

### NFR-3: Result Persistence
Save per-sample results for analysis.

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Mean Field Accuracy | >95% |
| Sample Pass Rate | >90% |

---

## Dependencies

- H-E1 validated infrastructure (StructuredError parser)
- H-E1 error corpus (error_pairs.json)
- OpenAI or Anthropic API access
