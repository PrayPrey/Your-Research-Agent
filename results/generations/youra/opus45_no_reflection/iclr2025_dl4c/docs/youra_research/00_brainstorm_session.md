---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Execution vs AI Feedback for Code Alignment"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-18
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Deep learning for code, specifically post-training and alignment methods using different feedback sources (execution feedback vs AI feedback)

**Session Approach:** Auto-Fill (Batch Mode) - Direct extraction from DL4C workshop CFP

**Session Duration:** Auto-generated

---

## Starting Context

The DL4C workshop (ICLR 2025) focuses on "Emergent Possibilities and Challenges in Deep Learning for Code." Key research directions include:
- Agentic methods for programming tasks
- Post-training and alignment for code
- Benchmarking and evaluation for code

The post-training/alignment track specifically welcomes research on "how to learn from human feedback, execution feedback, and AI feedback for better code generation."

---

## Lessons from Previous Attempts

N/A - First attempt

---

## Session Plan

Auto-fill mode: Extract research question directly from workshop topics, ensuring alignment with feasibility constraints (existing benchmarks only, no new data collection, no human evaluation).

---

## Technique Sessions

**Auto-Fill Extraction:**
1. Identified workshop priority: Post-training and Alignment for Code
2. Identified feasibility-compatible angle: Comparing feedback sources (execution vs AI) on existing benchmarks
3. Verified testability: HumanEval, MBPP, SWE-bench exist with execution-based evaluation
4. Formulated comparative hypothesis structure

---

## Research Question Development

### Initial Question

How do different feedback sources (execution feedback vs AI-generated feedback) affect code generation model alignment and downstream benchmark performance?

### Refined Question

Does execution feedback (test pass/fail signals, compiler errors, runtime traces) outperform AI-generated feedback (LLM critique, code review simulation) for post-training alignment of code generation models, as measured by pass@k on existing execution-based benchmarks?

### Detailed Sub-Questions

1. What is the comparative effect of execution feedback vs AI feedback on pass@1 and pass@10 metrics for HumanEval and MBPP?
2. Does the relative advantage of feedback types vary by problem difficulty (easy vs hard coding problems)?
3. What is the sample efficiency of each feedback type during post-training (how many feedback iterations needed to reach performance plateau)?
4. Do hybrid approaches (execution + AI feedback) outperform single-source feedback methods?

---

## Reference Papers

1. **CodeRL** (Le et al., 2022) - RL from execution feedback for code generation
   - Relevance: Establishes execution feedback methodology
   
2. **Self-Refine** (Madaan et al., 2023) - Iterative refinement with LLM feedback
   - Relevance: Demonstrates AI feedback approach
   
3. **RLTF** (Liu et al., 2023) - Reinforcement Learning from Unit Test Feedback
   - Relevance: Direct comparison baseline for execution feedback
   
4. **CodeT** (Chen et al., 2023) - Code generation with dual execution
   - Relevance: Execution-based ranking methodology

---

## Validation Results

### So What Test

**Impact:** Understanding which feedback source is more effective for code alignment directly informs practitioner choices for model training. If execution feedback dominates, investment should prioritize test infrastructure. If AI feedback competes, it enables alignment without execution environments (security benefits, lower infrastructure cost).

**Novelty:** While individual feedback methods exist, systematic comparison on identical base models and benchmarks is underexplored.

### Feasibility Check

- **Existing Benchmarks:** HumanEval, MBPP, APPS - all have execution-based evaluation ✓
- **No New Data Required:** Use existing benchmark test cases as execution feedback source ✓
- **No Human Evaluation:** All metrics are automated (pass@k, execution success) ✓
- **Reproducibility:** Can be run on open-source models (CodeLlama, StarCoder) ✓

**Verdict:** FEASIBLE

---

## Phase 1 Input Package

<phase1-input>

### research_question
Does execution feedback (test pass/fail signals, compiler errors, runtime traces) outperform AI-generated feedback (LLM critique, code review simulation) for post-training alignment of code generation models, as measured by pass@k on existing execution-based benchmarks?

### detailed_question
1. What is the comparative effect of execution feedback vs AI feedback on pass@1 and pass@10 metrics for HumanEval and MBPP?
2. Does the relative advantage of feedback types vary by problem difficulty (easy vs hard coding problems)?
3. What is the sample efficiency of each feedback type during post-training (how many feedback iterations needed to reach performance plateau)?
4. Do hybrid approaches (execution + AI feedback) outperform single-source feedback methods?

### reference_papers
1. CodeRL (Le et al., 2022) - RL from execution feedback for code generation
2. Self-Refine (Madaan et al., 2023) - Iterative refinement with LLM feedback
3. RLTF (Liu et al., 2023) - Reinforcement Learning from Unit Test Feedback
4. CodeT (Chen et al., 2023) - Code generation with dual execution

</phase1-input>

---

## Session Insights

### Key Discoveries

- DL4C explicitly calls for research comparing feedback sources for code alignment
- Execution-based benchmarks (HumanEval, MBPP) provide automated evaluation without human raters
- The comparison angle satisfies all feasibility constraints while being novel

### Techniques Used

- Auto-Fill extraction from workshop CFP
- Feasibility constraint validation
- Research question refinement for testability

### Areas for Further Exploration

- Multi-turn vs single-turn feedback effects
- Transfer across programming languages
- Scaling laws for feedback quantity

---

## Next Steps

1. **Phase 1:** Conduct targeted literature search on execution feedback and AI feedback methods
2. Search for existing comparative studies (may affect novelty claim)
3. Identify specific model architectures and training setups from related work

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
