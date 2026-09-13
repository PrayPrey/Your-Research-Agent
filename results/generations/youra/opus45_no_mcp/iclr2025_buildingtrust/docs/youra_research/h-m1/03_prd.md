# Product Requirements Document: H-M1

**Date:** 2026-08-19
**Hypothesis:** H-M1 (CoT Reasoning Chain Detection)
**Type:** MECHANISM
**Phase:** 3 - Implementation Planning

---

## Executive Summary

This PRD defines requirements for validating that Chain-of-Thought (CoT) prompting elicits multi-step reasoning chains from LLMs. The experiment compares baseline (direct answer) vs CoT-prompted outputs to verify that "Let's think step by step" activates sequential reasoning patterns.

**Success Criteria:** >90% of CoT outputs contain multi-step reasoning with mean step count >2.

---

## Problem Statement

**Research Question:** Does CoT prompting reliably produce multi-step reasoning outputs?

**Context:** H-E1 validated that confidence values are extractable. H-M1 tests the first mechanism: that CoT prompts force explicit reasoning articulation.

**Prerequisites:** H-E1 VALIDATED (confidence extraction infrastructure confirmed)

---

## Functional Requirements

### FR-1: Dataset Loading
- Load TruthfulQA MC2 split (817 questions) from HuggingFace
- Format as multiple-choice with option letters [A/B/C/D/E]
- Use full test set (no subsampling for statistical power)

### FR-2: Baseline Condition
- Prompt: Direct answer format (no CoT)
- Template: "Answer directly with the letter of the correct option."
- Extract: answer, confidence (if present)

### FR-3: CoT Condition  
- Prompt: Include "Let's think step by step"
- Template: Full CoT prompt with reasoning request
- Extract: raw_output, reasoning_text, step_count, answer, confidence

### FR-4: Reasoning Chain Detection
- Detect numbered steps: `1.`, `2)`, `Step 1:`, etc.
- Detect ordinal markers: First, Second, Third, Finally
- Detect logical connectors: therefore, thus, hence, because
- Return: has_reasoning (bool), step_count (int)

### FR-5: Metrics Computation
- Primary: reasoning_presence_rate (target >0.90)
- Secondary: mean_step_count (target >2.0)
- Comparison: CoT - Baseline difference (target >0.50)

### FR-6: Model Interface
- Primary: OpenAI API (gpt-3.5-turbo)
- Fallback: Together AI (Llama-2-70B-chat)
- Temperature: 0 (deterministic)
- Max tokens: 1024

### FR-7: Output Persistence
- Save raw outputs to JSON per condition
- Save metrics summary to YAML
- Generate comparison visualizations

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
- Estimated runtime: ~30 min for 1634 calls
- Cache responses for re-analysis

---

## Success Criteria

| Metric | Target | Gate |
|--------|--------|------|
| CoT reasoning_presence_rate | >0.90 | MUST_WORK |
| CoT mean_step_count | >2.0 | MUST_WORK |
| CoT - Baseline reasoning_rate | >0.50 | MUST_WORK |

---

## Dependencies

- **H-E1:** Validated (provides extraction infrastructure)
- **Datasets:** HuggingFace `truthful_qa`
- **APIs:** OpenAI or Together AI
- **Libraries:** openai, datasets, regex

---

## Visualization Requirements

1. **Gate Metrics Comparison:** Bar chart (Baseline vs CoT reasoning rates)
2. **Step Count Distribution:** Histogram of CoT step counts
3. **Example Outputs:** Side-by-side comparison (3 examples)
4. **Pattern Breakdown:** Pie chart of reasoning pattern types

---

## Timeline

| Phase | Duration |
|-------|----------|
| Phase 4 Implementation | 1-2 days |
| Data collection | ~30 min |
| Analysis & Visualization | 1-2 hours |

---

*Generated from Phase 2C experiment brief for H-M1*
