---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Reward Signal Design for GRPO on Tractable Code Generation"
---

# Research Brainstorm Session Results

**Session Date:** 2026-03-15
**Facilitator:** Research Question Architect
**Participant:** Anonymous
---

## Executive Summary

**Initial Interest:** Reward signal design for GRPO-based RLHF on code generation tasks in the partial-tractability regime (S_term ∈ [0.3, 0.6]) using APPS introductory problems and Qwen2.5-Coder-7B-Instruct

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

Deep Learning for Code (dl4c) research on reward-shaping for GRPO-based reinforcement learning from execution feedback (RLEF). Previous work investigated whether ratio-based reward (R_ratio = k_pass / k_total) outperforms binary reward (R_binary ∈ {0,1}) for reducing zero-reward fraction (ZRF) and improving gradient SNR during GRPO training on APPS coding problems with Qwen2.5-Coder-7B-Instruct. Source Type: ROUTE_TO_0 — Failure Recovery from 5 prior Phase 4 FAIL runs.

---

## Lessons from Previous Attempts

### What Was Tried Before

Five Phase 4 runs (h-e1, Runs 1–5) tested the hypothesis that R_ratio reduces ZRF ≥20% and increases gradient SNR ≥1.5x vs R_binary on APPS competition/interview problems (S_term > 0.85) under GRPO with Qwen2.5-Coder-7B-Instruct.

### Why It Failed

1. **S_term > 0.85 selects completely intractable problems**: At competition/interview APPS difficulty, Qwen2.5-Coder-7B achieves k_pass = 0 for ALL rollouts across ALL runs, seeds, and steps. R_ratio ≡ R_binary ≡ 0 in this regime — the reward distinction is mathematically vacuous.
2. **max_completion_length = 512 too short**: Competition-level problems require 100–400+ lines of Python. All completions were truncated (clipped_ratio ≈ 1.0), producing syntactically invalid code.
3. **EXISTENCE hypothesis measured via GRPO training gates**: The prescreening check (does k_pass > 0 exist?) was conflated with GRPO training evaluation (ZRF/SNR). These require separate experimental protocols.
4. **S_term estimated from category labels** (competition=0.95, interview=0.75) rather than empirical inference pass rates — fundamentally unvalidated prior.
5. **Cascade failure**: h-m1, h-m2, h-m3, h-c1 all CASCADE_FAILED due to h-e1 prerequisite failure.

### How THIS Direction Avoids Those Pitfalls

- **Target S_term ∈ [0.3, 0.55]** (APPS introductory problems), empirically calibrated via inference prescreening — not category-label estimates
- **Decouple prescreening from GRPO training**: Run direct pass@k inference (k=8, temperature=0.8) first to confirm ≥10% rollouts have k_pass > 0 before any GRPO experiment
- **Use max_new_tokens ≥ 1024** (or 2048) for code generation
- **Existing infrastructure reusable**: TRL v0.29.0 GRPOTrainer, APPS HuggingFace cache, s_term_labels.json, SFT checkpoint (h-e1/code/sft_checkpoint/)
- **Lower success threshold**: fraction(k_pass ≥ 1) ≥ 10% as prescreening gate (not 20%)

---

## Session Plan

Auto-extracted from structured ROUTE_TO_0 failure recovery context and recommendations from 5 failure records.

---

## Technique Sessions

Auto-Fill Mode - No interactive sessions (ROUTE_TO_0 failure recovery)

---

## Research Question Development

### Initial Question

Does ratio reward (R_ratio = k_pass/k_total) provide meaningfully different gradient signal than binary reward (R_binary) in GRPO-based code generation training when the model operates in a *partial-tractability regime* (S_term ∈ [0.3, 0.55], APPS introductory problems), as verified by empirical prescreening of the k_pass distribution before training?

### Refined Question

In GRPO-based RLEF for code generation with Qwen2.5-Coder-7B-Instruct on APPS introductory problems (difficulty=0, empirically filtered to S_term ∈ [0.3, 0.55] via pass@8 prescreening), does ratio reward (R_ratio = k_pass/k_total) reduce the zero-reward fraction (ZRF) by ≥20% and improve gradient SNR by ≥1.5× compared to binary reward (R_binary), in the first 25% of training steps?

### Detailed Sub-Questions

1. **EXISTENCE (Prescreening)**: On APPS introductory problems with Qwen2.5-Coder-7B-Instruct (max_new_tokens=1024, temperature=0.8, k=8), what fraction of problems in S_term ∈ [0.3, 0.55] have at least one rollout with k_pass > 0? Is this fraction ≥10%?
2. **ZRF Reduction**: After filtering to the confirmed partial-tractability subset, does GRPO with R_ratio yield ZRF < 0.80 while R_binary yields ZRF ≥ 0.80 in early training?
3. **Gradient SNR**: Does R_ratio produce gradient SNR ≥ 1.5× higher than R_binary when operating on the prescreened tractable subset?
4. **Training Stability**: Does R_ratio lead to more stable policy updates (lower variance in advantage estimates) compared to R_binary in the tractable regime?
5. **Feasibility Constraints**: Can the prescreening + GRPO pipeline be executed on a single H100 NVL with the existing SFT checkpoint and APPS dataset without synthetic data or human evaluation?

---

## Reference Papers

Not provided — will discover in Phase 1

---

## Validation Results

### So What Test

If confirmed, ratio reward provides a simple reward-engineering intervention that unlocks GRPO training effectiveness on problems where the model has partial capability. This has direct implications for curriculum design in RLEF: researchers should pre-screen problem difficulty to the partial-tractability regime before applying GRPO, and adopt R_ratio over R_binary in that regime. The result is immediately testable on existing datasets (APPS) with existing model checkpoints — no new benchmarks, no human evaluation, no synthetic data required.

### Feasibility Check

- **Dataset**: APPS (codeparrot/apps) — existing, HuggingFace cached, real benchmark
- **Model**: Qwen2.5-Coder-7B-Instruct + SFT checkpoint (h-e1/code/sft_checkpoint/) — available
- **Evaluation**: pass@k on APPS introductory problems — automated, no human rating
- **Infrastructure**: TRL v0.29.0 GRPOTrainer, H100 NVL, proven working from previous runs
- **Gate Metrics**: ZRF, gradient SNR — computed programmatically from training logs
- **No new benchmarks required**: Uses existing APPS + existing pass@k evaluation
- **FEASIBILITY: PASS** — Immediately executable with existing resources

---

## Phase 1 Input Package

<phase1-input>

### research_question
In GRPO-based RLEF for code generation with Qwen2.5-Coder-7B-Instruct on APPS introductory problems (difficulty=0, empirically filtered to S_term ∈ [0.3, 0.55] via pass@8 prescreening), does ratio reward (R_ratio = k_pass/k_total) reduce the zero-reward fraction (ZRF) by ≥20% and improve gradient SNR by ≥1.5× compared to binary reward (R_binary), in the first 25% of training steps?

### detailed_question
1. EXISTENCE (Prescreening): On APPS introductory problems with Qwen2.5-Coder-7B-Instruct (max_new_tokens=1024, temperature=0.8, k=8), what fraction of problems in S_term ∈ [0.3, 0.55] have at least one rollout with k_pass > 0? Is this fraction ≥10%?
2. ZRF Reduction: After filtering to the confirmed partial-tractability subset, does GRPO with R_ratio yield ZRF < 0.80 while R_binary yields ZRF ≥ 0.80 in early training?
3. Gradient SNR: Does R_ratio produce gradient SNR ≥ 1.5× higher than R_binary when operating on the prescreened tractable subset?
4. Training Stability: Does R_ratio lead to more stable policy updates (lower variance in advantage estimates) compared to R_binary in the tractable regime?
5. Feasibility: Can the prescreening + GRPO pipeline be executed on a single H100 NVL with existing SFT checkpoint and APPS dataset?

### reference_papers
Not provided — will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

- Input was `dummy` (no structured research idea) — direction generated entirely from ROUTE_TO_0 failure recovery context
- 5 previous runs (h-e1 Runs 1–5) confirm S_term > 0.85 is completely intractable for Qwen2.5-Coder-7B; must target introductory problems
- Prescreening must be decoupled from GRPO training: verify k_pass distribution first, then train
- Existing infrastructure (TRL v0.29.0, APPS cache, SFT checkpoint) is validated and reusable

### Techniques Used

Auto-Fill Mode (ROUTE_TO_0 failure recovery — extracted from 8 Serena memory files)

### Areas for Further Exploration

- Alternative reward functions beyond R_ratio: process-reward models, step-level feedback
- Curriculum learning: gradually increasing S_term during GRPO training
- Other code datasets: HumanEval+, MBPP — potentially more tractable for 7B models
- Larger models: Qwen2.5-Coder-14B may have partial tractability on interview-level problems
- Reward normalization strategies under sparse reward signal

---

## Next Steps

Proceed to Phase 1 - Targeted Research: gather papers on GRPO reward shaping, ratio vs binary rewards, partial-credit scoring in RL for code generation, and curriculum difficulty in RLEF.

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
