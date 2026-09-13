---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Execution Feedback RL for Code Generation Post-Training"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-31
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Post-training and alignment for code generation using execution feedback — specifically, how different reward signal formulations in reinforcement learning affect code LLM performance on existing benchmarks.

**Session Approach:** Auto-Fill Mode (Structured Input Detected)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

The DL4C workshop (ICLR 2025) invites submissions on deep learning for code, with specific emphasis on agentic methods, post-training/alignment for code, developer productivity, open science, and benchmarking/evaluation. The call explicitly welcomes work on reinforcement learning for code, execution-based feedback for alignment, and code generation beyond standard tasks.

Source Type: Workshop CFP / Structured Input

Feasibility constraints (pipeline-enforced): Only existing real datasets and benchmarks are permitted. No new benchmarks, rubrics, human evaluation, or synthetic data.

---

## Lessons from Previous Attempts

N/A - First attempt

---

## Session Plan

Auto-extracted from structured input

---

## Technique Sessions

Auto-Fill Mode - No interactive sessions

---

## Research Question Development

### Initial Question

How does the formulation of execution-based reward signals in reinforcement learning from execution feedback (RLEF) affect code LLM post-training performance across functional correctness, code efficiency, and generalization on existing benchmarks?

### Refined Question

Does the granularity of execution feedback reward signals (binary pass/fail vs. partial credit based on test case coverage ratio vs. output similarity) differentially affect the post-training effectiveness of code LLMs, as measured on existing execution-based benchmarks (HumanEval, MBPP, LiveCodeBench, SWE-bench-lite)?

### Detailed Sub-Questions

1. **Reward Signal Granularity:** Does moving from binary pass/fail reward to test-coverage-ratio reward (# passing tests / total tests) yield measurably higher performance gains in RLEF post-training on HumanEval and MBPP?

2. **Generalization vs. Overfitting:** Do models trained with partial-credit execution rewards generalize better to held-out problems (LiveCodeBench) compared to models trained with binary rewards, or do they overfit to training test suite structures?

3. **Efficiency vs. Correctness Trade-off:** When execution feedback includes runtime efficiency signals (e.g., time/memory from existing benchmark test cases), does joint reward optimization improve or degrade functional correctness scores on existing benchmarks?

4. **Model Scale Interaction:** Does the impact of reward signal granularity vary with model scale (e.g., 1B vs. 7B vs. 13B parameter code LLMs available on HuggingFace), using existing open-weight code models (DeepSeek-Coder, CodeLlama, StarCoder2)?

5. **Cross-Benchmark Transfer:** Do RLEF post-training gains on HumanEval/MBPP transfer to repository-level tasks on SWE-bench-lite, and does reward formulation affect this transfer?

---

## Reference Papers

Not provided - will discover in Phase 1

---

## Validation Results

### So What Test

Input from established research venue (ICLR DL4C workshop) - significance pre-validated. The question of how execution feedback reward formulation affects RLEF is practically significant: practitioners fine-tuning code LLMs must choose reward signal design without clear guidance. Current literature compares RLEF vs. SFT but rarely ablates reward granularity systematically. A result showing partial-credit rewards outperform binary rewards would directly change how practitioners design post-training pipelines for code LLMs.

### Feasibility Check

All required components are available without new data collection:
- **Existing models:** DeepSeek-Coder, CodeLlama, StarCoder2 (open-weight, downloadable)
- **Existing benchmarks:** HumanEval (164 problems), MBPP (374 problems), LiveCodeBench (existing), SWE-bench-lite (300 issues)
- **Execution infrastructure:** Standard Python test harness; no new rubrics needed
- **Reward signal variants:** Binary (0/1), ratio (k/n passing tests), and similarity — all computable from existing test cases
- **No human evaluation:** All metrics are automated execution-based
- **No new data:** Training uses existing code datasets (APPS, CodeContests available publicly)

Structured input indicates clear, immediately testable research direction. All feasibility constraints satisfied.

---

## Phase 1 Input Package

<phase1-input>

### research_question
Does the granularity of execution-based reward signals (binary pass/fail vs. test-coverage-ratio vs. output similarity) differentially affect post-training effectiveness of code LLMs under reinforcement learning from execution feedback (RLEF), as measured on existing execution-based benchmarks (HumanEval, MBPP, LiveCodeBench, SWE-bench-lite)?

### detailed_question
1. Does test-coverage-ratio reward (# passing tests / total tests) yield significantly higher RLEF post-training gains than binary pass/fail reward on HumanEval and MBPP?
2. Do models trained with partial-credit execution rewards generalize better to LiveCodeBench compared to binary-reward-trained models, or do they overfit to training test suite structures?
3. When execution feedback includes efficiency signals (runtime/memory from existing benchmark test cases), does joint reward optimization improve or degrade functional correctness on existing benchmarks?
4. Does the impact of reward signal granularity interact with model scale across existing open-weight code LLMs (DeepSeek-Coder, CodeLlama, StarCoder2 at 1B–13B)?
5. Do RLEF post-training gains transfer from HumanEval/MBPP to SWE-bench-lite, and does reward formulation affect this cross-benchmark transfer?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

- DL4C CFP explicitly targets execution feedback and RL for code as priority areas
- Reward signal granularity is an underexplored axis in RLEF literature (most work compares RLEF vs. SFT, not reward variants)
- All required benchmarks and models exist and are publicly accessible — zero new data needed
- The hypothesis is directly testable via ablation study on existing infrastructure
- Feasibility constraints eliminate: new benchmark creation, synthetic data generation, human annotation

### Techniques Used

Auto-Fill Mode (structured input extraction from workshop CFP)

### Areas for Further Exploration

- Agentic code repair (multi-turn execution feedback loops) — DL4C priority but requires agentic infrastructure
- Developer productivity measurement — HCI angle, excluded due to human evaluation requirement
- Code translation quality evaluation — interesting but requires cross-language benchmark alignment work
- Formal verification integration into RLEF — theoretically interesting but requires formal spec datasets
- Post-training data selection strategies for code (curriculum learning angle)

---

## Next Steps

Proceed to Phase 1 - Targeted Research. Use the `<phase1-input>` section above as direct input for Phase 1 initialization.

Key papers to find in Phase 1:
- RLEF / RLHF for code generation (execution feedback alignment)
- Reward shaping and partial credit in RL for code
- HumanEval, MBPP, LiveCodeBench benchmark papers
- DeepSeek-Coder, CodeLlama, StarCoder2 model papers
- SWE-bench paper for repository-level evaluation

Run: `/phase1-targeted`

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
