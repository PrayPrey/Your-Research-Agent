# Phase 2B Context: H-M1

**Hypothesis ID:** H-M1
**Type:** MECHANISM
**Title:** Foundation Model Emergence Timeline

## Hypothesis Statement

Under the condition of examining ML publication records (2019-2021), if foundation models represent a paradigm shift, then GPT-3 (2020), ViT (2020), and BERT successors are identifiable as high-impact papers with citation counts exceeding field medians by >2σ.

## Rationale

This validates that foundation model emergence actually occurred as hypothesized and was significant enough to plausibly drive ecosystem change.

## Variables

- **IV:** Paper publication date (2019-2021)
- **DV:** Citation impact relative to field median
- **CV:** Publication venue, paper type

## Success Criteria (PoC: Direction-based)

- **Primary:** Foundation model papers have citation impact >2σ above field median
- **Secondary:** Timeline aligns with hypothesized 2019-2021 emergence window

## Verification Protocol

1. Identify foundation model papers from Semantic Scholar (GPT-3, ViT, BERT variants)
2. Compute citation counts and field-normalized impact
3. Compare to contemporaneous ML paper distribution
4. Confirm >2σ impact for key papers

## Gate Condition

- **Type:** MUST_WORK
- **Pass Condition:** Foundation papers >2σ impact
- **Fail Action:** STOP, no paradigm shift evidence

## Prerequisites

- H-E1: COMPLETED (PASS) - Change point detected in 2019-04 and 2021-03

## Experimental Setup

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Semantic Scholar API | Citation counts with field-normalized metrics |
| **Model** | Statistical comparison | Z-score computation against field distribution |

## Previous Hypothesis Results

H-E1 validated existence of phase transition signal:
- Change points detected: 2019-04, 2021-03
- BIC improvement: 17.13
- Gate: PASS

## Dependencies

- Requires: H-E1 (COMPLETED)
- Blocks: H-M2, H-M3, H-M4, H-M5
