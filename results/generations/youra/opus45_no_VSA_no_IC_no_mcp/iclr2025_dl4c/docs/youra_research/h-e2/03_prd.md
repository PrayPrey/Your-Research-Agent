# Product Requirements Document: h-e2

**Date:** 2026-08-28
**Hypothesis:** AI-critic feedback yields measurably higher pass@1 than random baseline after k=3 refinement iterations
**Type:** EXISTENCE (PoC)
**Gate:** MUST_WORK

---

## Executive Summary

Validate that LLM-generated critique provides meaningful signal for code refinement. Compare AI-critic feedback loop against random feedback baseline on standard code generation benchmarks.

---

## Problem Statement

Code generation models produce imperfect outputs. Iterative refinement with feedback can improve results, but it's unclear whether AI-generated critique provides better signal than random noise. This experiment establishes the existence of meaningful improvement from AI feedback.

---

## Functional Requirements

### FR-1: Data Pipeline
- Load HumanEval dataset (164 problems) via HuggingFace
- Load MBPP test split (500 problems) via HuggingFace
- Parse problem prompts and test cases

### FR-2: Baseline Model (Zero-Shot)
- Load CodeLlama-7B-Instruct from HuggingFace
- Generate initial code solutions (temperature=0.7, max_tokens=512)
- Execute against test cases, compute pass@1

### FR-3: AI Critic Feedback Loop
- Generate initial code from problem prompt
- For k=3 iterations:
  - Generate critique using same model (CodeLlama-7B-Instruct)
  - Refine code based on critique
- Execute final code against test cases

### FR-4: Random Baseline Feedback Loop
- Same structure as FR-3
- Replace AI critique with random/nonsense feedback
- Serves as control to isolate critique signal

### FR-5: Evaluation
- Compute pass@1 for each condition:
  - Zero-shot baseline
  - AI-critic (k=3)
  - Random-baseline (k=3)
- Statistical comparison: AI-critic vs random-baseline

### FR-6: Visualization
- Bar chart: pass@1 comparison across conditions
- Per-iteration improvement curve (k=0,1,2,3)

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed
- Deterministic execution order

### NFR-2: Compute Budget
- Single GPU (A100 or equivalent)
- ~2-4 hours total runtime

---

## Success Criteria

**PoC Pass Condition:**
1. Code executes without error
2. `AI_critic_pass@1 > random_baseline_pass@1`

**Expected Performance:**
- Zero-shot: ~30-35% pass@1
- AI-critic: +5-10% improvement over zero-shot

---

## Data Specifications

| Dataset | Source | Size | Format |
|---------|--------|------|--------|
| HumanEval | openai_humaneval | 164 | HuggingFace |
| MBPP | mbpp (test split) | 500 | HuggingFace |

---

## Dependencies

- transformers (HuggingFace)
- datasets (HuggingFace)
- torch
- evalplus (optional, for rigorous evaluation)

---

## Out of Scope

- Training/fine-tuning (inference only)
- Multiple model comparisons
- Ablation studies (deferred to future hypotheses)
