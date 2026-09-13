---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Model-Based Judges for Code Evaluation"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-24
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Benchmarking and evaluation for code using model-based judges

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

**Source:** ICLR 2025 DL4C Workshop - "Emergent Possibilities and Challenges in Deep Learning for Code"

**Workshop Themes:**
1. Agentic Methods for Programming Tasks
2. Post-training and Alignment for Code
3. Developer Productivity and HCI for Code
4. Open Science and Responsible AI for Code
5. Benchmarking and Evaluation for Code

**Selected Focus Area:** Benchmarking and Evaluation for Code - specifically model-based judges for code quality assessment

**Feasibility Constraints Applied:**
- Must use existing benchmarks (HumanEval, MBPP, CodeContests)
- No new benchmark creation
- No human evaluation required
- No synthetic data generation
- Immediate testability with existing datasets

---

## Lessons from Previous Attempts

### What Was Tried Before

Previous attempts focused on **GRPO-based reinforcement learning from execution feedback** for code generation alignment. The approach used:
- DeepSeek-Coder-7B-Instruct as base model
- Binary execution reward (pass/fail on test cases)
- MBPP training problems with HumanEval+ evaluation
- Variance-based curriculum selection for training problems

### Why It Failed

**Cold-Start Problem:** The base model (DeepSeek-Coder-7B-Instruct-v1.5) produces pass@k ≈ 0.0 for MBPP problems during GRPO training. With zero rewards across all completions:
- `frac_reward_zero_std = 1.0` (no gradient signal)
- No differentiation between training conditions
- Both SFT and GRPO checkpoints generate syntactically broken code
- MUST_WORK gate failed: 0/20 HumanEval+ problems solved

**Technical Issues Encountered:**
- vLLM 0.11.0 incompatible with TRL 1.10 (use_vllm=False required)
- 5-step smoke run insufficient (< 2% of epoch)
- Cold-start persists even with LR=1e-6 and 200 steps

### How THIS Direction Avoids Those Pitfalls

**Key Pivot:** Instead of training with execution feedback (which requires non-zero rewards), this direction evaluates **model-based judges** which:
1. **No cold-start dependency** - Judges evaluate existing model outputs, no RL training required
2. **No reward sparsity** - Judge outputs are always available (scores, rankings, critiques)
3. **Existing benchmarks** - Uses HumanEval/MBPP as evaluation targets
4. **Immediate testability** - Can compare judge accuracy against execution ground truth

---

## Session Plan

Auto-fill mode: Extract research question from workshop themes that meets feasibility constraints AND avoids previous failure modes.

**Selected Theme:** Benchmarking and Evaluation for Code → Model-based Judges

**Rationale:**
- Model-based judges are evaluation tools, not training objectives
- No dependency on reward signal quality during training
- Can be validated against execution-based ground truth
- Directly addresses DL4C workshop interest in "model-based judges"

---

## Technique Sessions

**Technique Applied:** Failure-Informed Constraint Extraction

1. **Failure Analysis:** Previous RL-from-execution approach blocked by cold-start (zero rewards)
2. **Constraint Addition:** New direction must NOT require successful code generation during training
3. **Workshop Theme Match:** "model-based judges" explicitly listed in Benchmarking track
4. **Feasibility Filter:** Judge evaluation uses existing benchmark outputs (no new data needed)

---

## Research Question Development

### Initial Question

How effective are model-based judges at evaluating code generation quality compared to execution-based evaluation?

### Refined Question

How do model-based code judges (LLM-as-judge) compare to execution-based evaluation on code correctness, and what factors (prompt design, judge model scale, code complexity) most influence judge-execution agreement?

### Detailed Sub-Questions

1. What is the correlation between model-based judge scores and execution-based pass@1 on HumanEval and MBPP benchmarks?

2. How does judge model scale (7B vs 70B vs proprietary) affect agreement with execution ground truth?

3. Do different judging prompts (pairwise comparison, absolute scoring, critique-then-score) yield different accuracy levels against execution results?

4. For which code properties (correctness, efficiency, readability) do model-based judges most/least align with execution outcomes?

5. Can model-based judges identify subtle bugs (off-by-one, edge cases) that require test execution to detect?

---

## Reference Papers

1. **Judging LLM-as-a-Judge (Zheng et al., 2023)** - MT-Bench and Chatbot Arena for evaluating LLM judges
   - Relevance: Foundational framework for LLM judge evaluation methodology

2. **CodeBERTScore (Zhou et al., 2023)** - Evaluating Code Generation with Pre-trained Models of Code
   - Relevance: Model-based code evaluation metrics

3. **ICE-Score (Zhuo, 2024)** - Instructing Large Language Models to Score Code
   - Relevance: Prompting strategies for code evaluation

4. **CodeScore (Dong et al., 2023)** - Evaluating Code Generation by Learning Code Execution
   - Relevance: Learning execution-aware evaluation

5. **EvalPlus (Liu et al., 2023)** - Rigorous Evaluation of LLM-Synthesized Code
   - Relevance: Execution-based ground truth for comparison

---

## Validation Results

### So What Test

**Impact Statement:** Understanding when model-based judges can substitute for expensive execution-based evaluation enables faster iteration on code generation research. This has direct practical value for researchers evaluating code models at scale.

**Novelty:** While LLM-as-judge is established for NLP tasks, systematic analysis of judge accuracy vs execution ground truth for code is underexplored.

**Timeliness:** Directly addresses DL4C workshop explicit interest in "model-based judges" for code evaluation.

### Feasibility Check

| Criterion | Status | Notes |
|-----------|--------|-------|
| Existing Benchmarks | PASS | HumanEval, MBPP, CodeContests available |
| No New Benchmarks | PASS | Using established evaluation sets |
| No Human Eval | PASS | Comparing judges to execution, not humans |
| No Synthetic Data | PASS | Using existing benchmark problems and model outputs |
| Immediate Testability | PASS | Can collect judge outputs immediately |
| No Cold-Start Dependency | PASS | No RL training required |

**Overall Feasibility:** PASS - All pipeline constraints satisfied, previous failure mode avoided

---

## Phase 1 Input Package

<phase1-input>

### research_question
How do model-based code judges (LLM-as-judge) compare to execution-based evaluation on code correctness, and what factors (prompt design, judge model scale, code complexity) most influence judge-execution agreement?

### detailed_question
1. What is the correlation between model-based judge scores and execution-based pass@1 on HumanEval and MBPP benchmarks?
2. How does judge model scale (7B vs 70B vs proprietary) affect agreement with execution ground truth?
3. Do different judging prompts (pairwise comparison, absolute scoring, critique-then-score) yield different accuracy levels against execution results?
4. For which code properties (correctness, efficiency, readability) do model-based judges most/least align with execution outcomes?
5. Can model-based judges identify subtle bugs (off-by-one, edge cases) that require test execution to detect?

### reference_papers
1. Judging LLM-as-a-Judge (Zheng et al., 2023) - MT-Bench and Chatbot Arena - LLM judge evaluation methodology
2. CodeBERTScore (Zhou et al., 2023) - Evaluating Code Generation with Pre-trained Models - Model-based code metrics
3. ICE-Score (Zhuo, 2024) - Instructing LLMs to Score Code - Prompting strategies for code evaluation
4. CodeScore (Dong et al., 2023) - Evaluating Code Generation by Learning Code Execution - Execution-aware evaluation
5. EvalPlus (Liu et al., 2023) - Rigorous Evaluation of LLM-Synthesized Code - Execution ground truth

</phase1-input>

---

## Session Insights

### Key Discoveries

- Previous failure was cold-start specific to RL training; evaluation tasks avoid this
- Model-based judges are explicit DL4C workshop topic
- Can use execution results as ground truth without requiring successful RL training
- Pivoting from "training with feedback" to "evaluating with judges" sidesteps reward sparsity

### Techniques Used

- Failure-informed constraint extraction
- Workshop theme matching with failure avoidance
- Feasibility filtering against pipeline requirements + previous failure modes

### Areas for Further Exploration

- Judge calibration across different code domains
- Multi-judge ensembles for robust evaluation
- Judge-guided code ranking for downstream selection

---

## Next Steps

1. **Phase 1:** Targeted literature research on model-based code evaluation
2. **Phase 2A:** Generate hypotheses about judge-execution agreement factors
3. **Phase 2B:** Design experimental protocol comparing judges to execution on HumanEval/MBPP

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
