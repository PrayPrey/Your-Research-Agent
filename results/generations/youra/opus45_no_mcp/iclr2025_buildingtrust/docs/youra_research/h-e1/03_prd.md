# Product Requirements Document: H-E1 ECE Measurability Validation

**Date:** 2026-08-19
**Hypothesis:** H-E1 (EXISTENCE)
**Author:** PrayPrey

---

## Executive Summary

Validate that Expected Calibration Error (ECE) can be reliably computed across 5 prompting conditions (baseline, CoT-only, confidence-only, CoT+confidence, token-padding) using GPT-3.5-turbo on TruthfulQA. This is a MUST_WORK gate hypothesis that establishes the measurement infrastructure for subsequent mechanism hypotheses.

---

## Problem Statement

Before investigating CoT+confidence synergy mechanisms (H-M1 through H-M4), we must verify that:
1. Confidence values are extractable from model outputs (>95% success rate)
2. ECE can be computed for all 5 experimental conditions
3. The measurement pipeline produces valid results in [0,1] range

---

## Functional Requirements

### FR-1: Dataset Loading
- Load TruthfulQA mc1 subset from HuggingFace (817 questions)
- Extract question, choices, and correct answer labels
- Format as multiple-choice prompts

### FR-2: Prompting Conditions
Implement 5 prompting strategies:
| Condition | Description |
|-----------|-------------|
| baseline | Direct Q&A with confidence request |
| cot_only | "Let's think step by step" prefix |
| confidence_only | Emphasis on confidence reflection |
| cot_confidence | Combined CoT + confidence |
| token_padding | Filler text matching CoT token count |

### FR-3: API Interface
- OpenAI API integration (gpt-3.5-turbo)
- Temperature=0 for deterministic outputs
- max_tokens=512
- Response caching to avoid duplicate calls

### FR-4: Extraction Pipeline
- Regex extraction: `Confidence:\s*(\d+)%`
- Answer extraction: `Answer:\s*([A-Z])`
- Track extraction failures per condition

### FR-5: ECE Computation
- 15 equal-width bins from 0 to 1
- Standard ECE formula per Guo et al. 2017
- Output ECE value per condition

### FR-6: Results Persistence
- Save raw results as JSON
- Generate reliability diagrams per condition
- Output summary table with extraction rates and ECE values

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Seed control where applicable
- Temperature=0 for API calls
- Response caching

### NFR-2: Efficiency
- 817 questions × 5 conditions = 4,085 API calls
- Batch processing with rate limiting
- Cache responses to enable re-runs

### NFR-3: Error Handling
- Graceful handling of extraction failures
- Log failures for analysis
- Continue processing despite individual failures

---

## Success Criteria

| Metric | Threshold |
|--------|-----------|
| Confidence extraction rate | >95% per condition |
| ECE computability | 100% (all 5 conditions) |
| ECE value range | [0,1] for all conditions |

**Pass Condition:** All thresholds met → proceed to H-M1
**Fail Condition:** Any threshold missed → PIVOT (revise extraction)

---

## Dependencies

- OpenAI API access
- HuggingFace datasets library
- NumPy for ECE computation
- matplotlib for visualizations

---

## Outputs

| File | Description |
|------|-------------|
| results.json | Raw experimental data |
| figures/reliability_*.png | Reliability diagrams |
| figures/ece_comparison.png | ECE bar chart |
| 04_validation.md | Gate evaluation report |

---

## Timeline

| Phase | Duration |
|-------|----------|
| Implementation | 1 day |
| Execution | 2-4 hours (API calls) |
| Analysis | 1 day |

---

*Generated for Phase 3 Implementation Planning*
