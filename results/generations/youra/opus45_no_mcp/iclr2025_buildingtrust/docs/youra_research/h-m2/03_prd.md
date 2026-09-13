# Product Requirements Document: H-M2

**Date:** 2026-08-19
**Hypothesis:** H-M2 (Hedging Marker Detection in CoT Outputs)
**Type:** MECHANISM
**Phase:** 3 - Implementation Planning

---

## Executive Summary

This PRD defines requirements for validating that CoT+confidence reasoning chains contain epistemic uncertainty indicators (hedging words, qualifications, alternatives). The experiment analyzes CoT outputs for hedging language to verify that complex reasoning surfaces uncertainty signals.

**Success Criteria:** >30% of CoT outputs contain at least one hedging marker (SHOULD_WORK gate).

---

## Problem Statement

**Research Question:** Do CoT reasoning chains contain detectable uncertainty signals?

**Context:** H-M1 validated that CoT prompting produces multi-step reasoning (100% rate, mean 2.61 steps). H-M2 tests whether these reasoning chains contain epistemic uncertainty markers that could inform confidence calibration.

**Prerequisites:** 
- H-E1 VALIDATED (confidence extraction infrastructure)
- H-M1 VALIDATED (CoT reasoning chain generation)

---

## Functional Requirements

### FR-1: Dataset Loading
- Load TruthfulQA generation split (817 questions) from HuggingFace
- Use full validation set for statistical power (all 817 items)
- No subsampling — meaningful sample size required

### FR-2: CoT+Confidence Generation
- Prompt: Include "Let's think step by step" + confidence request
- Template: Full CoT prompt with reasoning and confidence verbalization
- Extract: raw_output, reasoning_text, confidence_value

### FR-3: Hedging Marker Detection
Primary hedging markers dictionary:
```
might, may, could, possibly, perhaps, uncertain, unsure,
alternatively, however, although, probably, likely, unlikely,
but, not sure, hard to say, difficult to determine
```
- Count occurrences of each marker in reasoning text
- Return: markers_found (dict), total_count (int), has_hedging (bool)

### FR-4: Reasoning Chain Extraction
- Extract reasoning portion before confidence statement
- Split at markers: "confidence:", "my confidence", "i am confident"
- Analyze only reasoning text for hedging (exclude confidence statement)

### FR-5: Metrics Computation
- Primary: hedging_presence_rate (target >0.30)
- Secondary: mean_hedging_count per output
- Tertiary: marker frequency distribution (which markers most common)

### FR-6: Model Interface
- Primary: OpenAI API (gpt-3.5-turbo)
- Temperature: 0 (deterministic)
- Max tokens: 500 (sufficient for CoT reasoning)

### FR-7: Output Persistence
- Save raw outputs with hedging analysis to JSON
- Save metrics summary to YAML
- Generate hedging distribution visualizations

### FR-8: Visualization Requirements
- **Required:** Gate metrics bar chart (hedging rate vs 30% threshold)
- **Additional:** Hedging marker frequency distribution (horizontal bar)
- **Additional:** Hedging count histogram per output

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Deterministic generation (temperature=0)
- Seed random states where applicable
- Log all API call parameters

### NFR-2: Error Handling
- Retry logic: 3 retries with exponential backoff
- Handle rate limits gracefully
- Log extraction failures for manual review

### NFR-3: Performance
- Sequential API calls (respect rate limits)
- Estimated runtime: ~15 min for 817 calls
- Cache responses for re-analysis

---

## Success Criteria

| Metric | Target | Gate |
|--------|--------|------|
| hedging_presence_rate | >0.30 | SHOULD_WORK |
| Gate failure action | EXPLORE (expand dictionary) | Not STOP |

**SHOULD_WORK Gate Logic:**
- Pass: Proceed to H-M3 (sequential generation)
- Fail: EXPLORE alternative hedging dictionaries, do not halt pipeline

---

## Dependencies

- **H-E1:** Validated (extraction infrastructure)
- **H-M1:** Validated (CoT reasoning chain generation confirmed)

### External Libraries
- `datasets` (HuggingFace)
- `openai`
- `matplotlib` (visualization)
- Standard library: `re`, `collections`, `json`, `yaml`

---

## Data Specification

### Input Dataset
| Property | Value |
|----------|-------|
| Name | TruthfulQA |
| Config | generation |
| Split | validation |
| Size | 817 items |
| Source | HuggingFace datasets |

### Loading Code
```python
from datasets import load_dataset
dataset = load_dataset("truthful_qa", "generation")
questions = dataset["validation"]["question"]  # 817 items
```

---

## Appendix: Extended Hedging Dictionary (EXPLORE Fallback)

If primary dictionary yields <30% hedging rate, use extended set:
```
seem, appears, tends, generally, typically, in some cases,
it depends, not always, sometimes, often, rarely, approximately,
roughly, around, i think, i believe, in my opinion, arguably
```
