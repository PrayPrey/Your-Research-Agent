# Product Requirements Document: H-M3

**Hypothesis:** Under sequential generation, if hedging markers appear before confidence verbalization, then the confidence estimate has access to these signals, because autoregressive generation keeps prior tokens in context.

**Date:** 2026-08-19
**Version:** 1.0
**Status:** DRAFT

---

## 1. Executive Summary

H-M3 validates Step 3 of the causal chain: verifying that autoregressive LLM generation ensures hedging markers precede confidence statements in token sequence. This is a text analysis hypothesis operating on cached H-M2 outputs rather than requiring new API calls.

**Key Deliverable:** Positional analysis pipeline that measures marker-before-confidence ordering rates.

---

## 2. Problem Statement

### 2.1 Background
H-M2 established that 82% of CoT+confidence outputs contain hedging markers. H-M3 must verify these markers appear BEFORE the confidence statement in token sequence, validating the autoregressive access assumption.

### 2.2 Hypothesis
- **Type:** MECHANISM
- **Gate:** SHOULD_WORK
- **Condition 1:** >99% of outputs have correct CoT-then-confidence ordering
- **Condition 2:** Hedging markers precede confidence in >95% of cases where markers exist

### 2.3 Prerequisites
- H-M2 (VALIDATED): Hedging presence rate 82.0%, mean 2.84 markers/output

---

## 3. Functional Requirements

### FR-1: H-M2 Output Cache Loading
Load cached CoT+confidence outputs from H-M2 experiment results.
- Source: `../h-m2/code/results/` or cached API responses
- Format: JSON with output text per sample
- Fallback: Re-generate subset if cache unavailable

### FR-2: Confidence Position Extraction
Extract position of "Confidence: X%" statement in each output.
- Pattern: `Confidence:\s*(\d+)%` (case-insensitive)
- Output: Character position, confidence value

### FR-3: Hedging Marker Position Extraction
Find all hedging markers and their positions in output text.
- Markers: might, possibly, could, perhaps, may, likely, unlikely, however, uncertain, although, but, alternatively
- Output: List of (marker, position) tuples sorted by position

### FR-4: Positional Analysis
Calculate marker-confidence position relationships.
- markers_before_confidence: Count of markers appearing before confidence statement
- markers_after_confidence: Count appearing at/after
- cot_then_confidence_order: Boolean (confidence appears after 30% of output length)

### FR-5: Gate Metrics Computation
Compute H-M3 gate validation metrics.
- Gate 1: cot_order_rate = % outputs with CoT-then-confidence ordering (threshold >99%)
- Gate 2: markers_precede_rate = % outputs where all markers precede confidence (threshold >95%)

### FR-6: Visualization Generation
Generate required figures:
- **Mandatory:** Gate metrics bar chart (rates vs thresholds)
- **Optional:** Position distribution histogram, marker position timeline scatter

---

## 4. Data Specification

### 4.1 Input Data

| Dataset | Source | Size | Notes |
|---------|--------|------|-------|
| TruthfulQA (Generation) | H-M2 cached outputs | 817 items | Full generation split |

**Loading:** Reuse H-M2 experiment cache (no new API calls needed)

```python
import json
with open('../h-m2/code/results/h-m2_results.json', 'r') as f:
    cached_outputs = json.load(f)
```

### 4.2 Output Data

| Output | Format | Location |
|--------|--------|----------|
| Analysis results | JSON | results/h-m3_results.json |
| Gate metrics | YAML | results/gate_metrics.yaml |
| Figures | PNG | figures/ |

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Processing time: <5 seconds for 817 items (CPU only)
- No GPU required

### NFR-2: Reproducibility
- Deterministic text parsing
- All outputs reproducible from same input

### NFR-3: Compatibility
- Python 3.8+
- No external ML dependencies (only re, dataclasses)

---

## 6. Success Criteria

| Metric | Threshold | Priority |
|--------|-----------|----------|
| cot_order_rate | >99% | MUST |
| markers_precede_rate | >95% | MUST |
| Code runs without error | True | MUST |

**Expected Outcome:** PASS - Prompt format enforces reasoning-before-confidence structure.

---

## 7. Dependencies

### 7.1 Python Packages
```
pyyaml>=6.0
matplotlib>=3.5
```

### 7.2 Internal Dependencies
- H-M2 cached results (prerequisite)
- Shared utilities from h-m2/code/ if available

---

## 8. Assumptions and Constraints

### 8.1 Assumptions
- H-M2 outputs follow expected format (CoT → Answer → Confidence)
- Confidence statement uses "Confidence: X%" pattern

### 8.2 Constraints
- No new API calls required
- Analysis only, no training

---

## 9. Glossary

| Term | Definition |
|------|------------|
| CoT | Chain-of-Thought prompting |
| Hedging marker | Uncertainty indicator word (may, could, etc.) |
| Positional analysis | Comparing character positions of text elements |
| Autoregressive | Left-to-right token generation |

---

*Generated for Phase 3 Implementation Planning*
