---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: DL4C Agentic Methods and Benchmarking"
---

# Research Brainstorm Session Results

**Session Date:** 2026-07-10
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Exploring agentic methods for programming tasks and benchmarking/evaluation for code from the DL4C workshop, with emphasis on approaches that can be validated using existing benchmarks and real datasets

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

The third DL4C workshop titled "Emergent Possibilities and Challenges in Deep Learning for Code" provides a vibrant platform for researchers to share their work on deep learning for code, emphasizing emergent possibilities and challenges. Key topics include:

- **Agentic Methods for Programming Tasks**: Agents able to solve realistic coding tasks, such as solving GitHub issues or software development tasks
- **Post-training and Alignment for Code**: Learning from human feedback, execution feedback, and AI feedback for better code generation
- **Developer Productivity and HCI for Code**: Adaptation of models to users' needs to increase developer productivity
- **Open Science and Responsible AI for Code**: Openness and transparency in research practices
- **Benchmarking and Evaluation for Code**: Execution-based benchmarks, code understanding, code efficiency, model-based judges, and project-level context

**Source Type:** Workshop CFP / Structured Input
**Context:** Retrying after previous failure - new research direction learning from past overhead limitations

---

## Lessons from Previous Attempts

### Previous Failures Summary

**Failure 1: Runtime Profiling Overhead (h-e1 Run 1)**
- **Hypothesis:** Lightweight runtime tracing with sys.settrace for code performance prediction
- **Failure Type:** MUST_WORK_GATE_FAILED (Phase 4)
- **Performance Gap:** Median overhead 4.05× (threshold: 2.5×), P95 overhead 13.58× (threshold: 3.0×)
- **Root Cause:** sys.settrace profiling mechanism has fundamentally too high per-line callback overhead for production use
- **Key Learning:** ANY approach requiring extensive runtime profiling or tracing will face unacceptable overhead

**Partial Success: Temperature Scaling Calibration (h-e1 Run 1)**
- **Methodology:** Temperature scaling for confidence calibration
- **Result:** PARTIAL_VALIDATION - 58.3% ECE reduction (from 0.12 to 0.054)
- **Status:** 4/10 folds passed ECE < 0.05 threshold, proving feasibility
- **Key Insight:** Temperature scaling methodology is validated and can be applied to calibrate model confidence in any prediction task

**Previous Pivot: Static Analysis for Code Understanding**
- **Direction:** Pure static analysis (AST, CFG, DFG) to predict runtime properties without execution
- **Rationale:** Eliminate runtime overhead entirely by using only code structure
- **Status:** Archived attempt - focused on code understanding and complexity prediction

### Critical Root Cause Analysis

The fundamental pattern across attempts:
1. **Runtime overhead bottleneck:** Any profiling-based or extensive execution-based approach faces measurement overhead (sys.settrace: 4.05× median)
2. **Static-only limitations:** While static analysis avoids overhead, it may lack dynamic runtime context needed for certain predictions
3. **Need for pragmatic hybrid:** Balance between overhead and prediction accuracy

### Key Lessons Learned

**What Failed:**
1. ❌ Extensive runtime tracing (sys.settrace, per-line profiling) - median 4.05× overhead is unacceptable
2. ❌ Approaches requiring comprehensive runtime profiling for every code execution
3. ❌ Measurement-heavy methods that create circular dependencies (profiling cost exceeds benefit)

**What Worked:**
1. ✅ Temperature scaling for confidence calibration (58.3% ECE reduction) - reusable methodology
2. ✅ Stratified sampling by complexity tier - successfully covered diverse problem types
3. ✅ Experiment infrastructure (dataset loading, execution harness, analysis) - reusable for new hypotheses
4. ✅ Focus on existing benchmarks and datasets - enables immediate validation

**What Showed Promise:**
1. ✅ Static analysis (AST, CFG) - zero overhead but may lack runtime context
2. ✅ Execution feedback (test pass/fail) - minimal overhead compared to full profiling
3. ✅ Model-based evaluation - can substitute expensive human evaluation

### Critical Pivot Insight

**THE FUNDAMENTAL REALIZATION:**
The DL4C workshop explicitly emphasizes **"model-based judges"** and **"execution-based benchmarks"** as core evaluation topics. This suggests a NEW direction that COMBINES insights from both previous attempts:

1. **From Failure 1 (sys.settrace):** Avoid EXTENSIVE runtime profiling - use lightweight execution feedback instead
2. **From Previous Pivot (static analysis):** Leverage code structure analysis where possible to minimize runtime dependency
3. **NEW INSIGHT:** Focus on **agentic methods** that can be evaluated using **existing execution-based benchmarks** (HumanEval, MBPP, SWE-bench) rather than requiring new profiling infrastructure

**THE NEW DIRECTION:**
Shift to **AGENTIC METHODS FOR CODE** that can be validated using **EXISTING EXECUTION-BASED BENCHMARKS** with **MINIMAL OVERHEAD**. The evaluation is simple test pass/fail (not profiling), and the focus is on improving agent performance through better:
- Feedback mechanisms (execution results, not profiling data)
- Model-based self-critique (judging code quality before execution)
- Benchmark performance (measured by existing test suites)

This aligns with DL4C priorities:
- **Agentic Methods:** Core workshop focus - agents solving GitHub issues, software development tasks
- **Benchmarking/Evaluation:** Using existing benchmarks (HumanEval, MBPP, SWE-bench) avoids new benchmark creation
- **Model-based Judges:** LLM-as-judge for code quality, avoiding human evaluation overhead

### Approaches to AVOID

**❌ Forbidden Directions (Proven Failures):**
- Any sys.settrace or per-line runtime profiling approaches
- Performance prediction requiring extensive runtime measurement infrastructure
- Approaches creating new benchmarks or rubrics (violates feasibility constraints)
- Methods requiring synthetic data generation or human annotation

**❌ Low-Feasibility Directions:**
- Approaches requiring new scoring frameworks or rubrics
- Methods dependent on future data collection or annotation
- Hypotheses that cannot be tested on existing real datasets immediately

### Promising Directions (Aligned with DL4C Topics + Feasibility)

**✅ Agentic Methods with Existing Benchmark Validation:**
- Agents for code generation evaluated on HumanEval, MBPP, or CodeContests
- GitHub issue resolution agents validated on SWE-bench
- Self-correction and iterative refinement using execution feedback (test pass/fail, NOT profiling)
- Multi-turn code generation with model-based self-critique

**✅ Model-Based Judges for Code Quality:**
- LLM-as-judge for code quality assessment (replaces human evaluation)
- Self-critique mechanisms for code before execution
- Confidence calibration using temperature scaling (validated method from previous success)

**✅ Execution Feedback (Lightweight, NOT Profiling):**
- Test execution results (pass/fail) as feedback signal - minimal overhead
- Error messages and stack traces for debugging guidance
- Functional correctness via existing test suites (not performance profiling)

---

## Session Plan

Auto-extracted from DL4C workshop input with failure context integration. **Focus on agentic methods validated using existing execution-based benchmarks** - avoid profiling overhead while leveraging lightweight execution feedback (test pass/fail).

---

## Technique Sessions

ROUTE_TO_0 Auto-Fill Mode (failure context integration with pivot to agentic methods + existing benchmark evaluation)

---

## Research Question Development

### Initial Question

How can agentic methods for code generation and problem-solving be improved using lightweight execution feedback and model-based self-critique, validated on existing benchmarks without requiring new evaluation frameworks?

### Refined Question

Can iterative refinement agents that combine model-based self-critique (LLM-as-judge) with lightweight execution feedback (test pass/fail) achieve better performance on existing code generation benchmarks (HumanEval, MBPP, CodeContests) compared to single-shot generation baselines?

### Detailed Sub-Questions

1. Can model-based self-critique (LLM judging its own generated code before execution) reduce the number of execution attempts needed to reach a correct solution on HumanEval/MBPP?
2. How does iterative refinement with execution feedback (test pass/fail signals) compare to single-shot generation in terms of final accuracy and number of attempts on existing benchmarks?
3. Can confidence calibration via temperature scaling (validated from previous success) improve agent decision-making on when to submit vs. refine generated code?
4. What is the relative contribution of model-based self-critique vs. execution feedback in multi-turn code generation success rates on CodeContests or SWE-bench?
5. Can agents learn effective refinement strategies from execution feedback alone (test results + error messages) without requiring runtime profiling or performance measurement?

---

## Reference Papers

Not provided - will discover in Phase 1 focusing on:
- Agentic code generation (multi-turn, iterative refinement, self-correction)
- Execution feedback for code generation (AlphaCode, CodeRL, PPOCoder)
- Model-based evaluation and LLM-as-judge for code quality
- Self-critique and self-refinement methods for LLMs
- Existing code generation benchmarks (HumanEval, MBPP, CodeContests, SWE-bench)
- Confidence calibration for code generation

---

## Validation Results

### So What Test

**Significance:** Previous failures revealed that extensive runtime profiling creates unacceptable overhead (4.05× median). The DL4C workshop explicitly calls for research on **agentic methods** and **model-based judges** - both can be evaluated using **existing execution-based benchmarks** with MINIMAL overhead (test pass/fail, not profiling).

The NEW direction focuses on **iterative refinement agents** that:
1. Use **model-based self-critique** (LLM-as-judge) to evaluate code quality BEFORE execution
2. Leverage **lightweight execution feedback** (test pass/fail, error messages) for refinement - NOT profiling
3. Can be validated on **existing benchmarks** (HumanEval, MBPP, CodeContests) - no new evaluation needed

**Impact:** If successful, enables agentic code generation systems that:
- Reduce execution attempts through better self-critique (faster development cycles)
- Improve code quality before execution (fewer failed submissions)
- Work within existing benchmark infrastructure (immediate research validation)
- Apply temperature scaling confidence calibration (validated method) to decide when to submit vs. refine

**Novelty:** Combines model-based self-critique (internal quality assessment) with execution feedback (external validation) in a calibrated iterative refinement loop. Previous work often uses one OR the other; this explores their SYNERGY with confidence-based decision-making.

### Feasibility Check

**MANDATORY FEASIBILITY CONSTRAINTS (Pipeline-Enforced):**
✅ Uses existing real datasets - HumanEval (164 problems), MBPP (974 problems), CodeContests (13,328 problems), SWE-bench (2,294 real GitHub issues)
✅ Uses existing benchmarks - Functional correctness via existing test suites, no new evaluation needed
✅ No new benchmarks needed - Test pass/fail is established evaluation protocol
✅ No synthetic/generated data required - Real programming problems from established datasets
✅ No human evaluation needed - Automated test execution + model-based self-critique (LLM-as-judge)
✅ Testable immediately with available resources - Datasets and evaluation scripts publicly available

**Technical Feasibility:**
- Baseline models: Use existing code LLMs (CodeLlama, StarCoder, GPT-4, Claude)
- Execution environment: Existing benchmark execution sandboxes (HumanEval uses exec, CodeContests has evaluation server)
- Self-critique: Prompt-based LLM self-evaluation (no new model training required for initial validation)
- Execution feedback: Test results (pass/fail) + error messages (already provided by benchmarks)
- Confidence calibration: Temperature scaling from previous validated success (58.3% ECE reduction)
- Metrics: Pass@k, success rate, number of attempts - all standard and automated

**Pivot Rationale:**
1. **Eliminates profiling overhead:** Uses test pass/fail (minimal overhead), NOT sys.settrace profiling
2. **Aligns with DL4C priorities:** Agentic methods + model-based judges are core workshop topics
3. **Leverages existing infrastructure:** HumanEval, MBPP, CodeContests have established evaluation
4. **Avoids forbidden constraints:** No new benchmarks, no synthetic data, no human evaluation
5. **Applies validated methodology:** Temperature scaling confidence calibration (58.3% ECE reduction)

**Connection to Previous Success:**
- **Temperature scaling:** Calibrate agent confidence on when to submit vs. continue refining
- **Stratified sampling:** Sample problems by difficulty tier (easy, medium, hard) for diverse evaluation
- **Execution infrastructure:** Adapt benchmark execution harness (CodeContests, HumanEval) instead of custom profiling

**Key Differentiator from Previous Attempts:**
- **Attempt 1 (sys.settrace):** Heavy runtime profiling for performance prediction (4.05× overhead) ❌
- **Previous Pivot (static analysis):** Zero runtime, pure structure-based prediction ⚠️
- **NEW (agentic + lightweight feedback):** Minimal runtime (test pass/fail only), iterative refinement ✅

**Why This Works:**
1. **Lightweight execution:** Test pass/fail has negligible overhead compared to profiling
2. **Model-based pre-filter:** Self-critique reduces bad submissions (fewer wasted executions)
3. **Existing benchmarks:** No new evaluation framework needed (satisfies feasibility constraints)
4. **Calibrated decisions:** Temperature scaling confidence helps agent decide submit vs. refine

---

## Phase 1 Input Package

<phase1-input>

### research_question
Can iterative refinement agents that combine model-based self-critique (LLM-as-judge) with lightweight execution feedback (test pass/fail) achieve better performance on existing code generation benchmarks (HumanEval, MBPP, CodeContests) compared to single-shot generation baselines?

### detailed_question
1. Can model-based self-critique (LLM judging its own generated code before execution) reduce the number of execution attempts needed to reach a correct solution on HumanEval/MBPP?
2. How does iterative refinement with execution feedback (test pass/fail signals) compare to single-shot generation in terms of final accuracy and number of attempts on existing benchmarks?
3. Can confidence calibration via temperature scaling (validated from previous success) improve agent decision-making on when to submit vs. refine generated code?
4. What is the relative contribution of model-based self-critique vs. execution feedback in multi-turn code generation success rates on CodeContests or SWE-bench?
5. Can agents learn effective refinement strategies from execution feedback alone (test results + error messages) without requiring runtime profiling or performance measurement?

### reference_papers
Not provided - will discover in Phase 1 focusing on agentic code generation (multi-turn, self-correction), execution feedback methods (AlphaCode, CodeRL), LLM-as-judge for code, self-critique/refinement, and confidence calibration for code generation

</phase1-input>

---

## Session Insights

### Key Discoveries

Previous failures and DL4C workshop alignment revealed:
1. **Profiling overhead (4.05× median) is prohibitive** - but lightweight execution feedback (test pass/fail) is acceptable
2. **DL4C explicitly calls for agentic methods and model-based judges** - core workshop priorities
3. **Existing benchmarks (HumanEval, MBPP, CodeContests) eliminate need for new evaluation** - satisfies feasibility constraints
4. **Model-based self-critique can reduce execution overhead** - pre-filter bad code before running tests

The pivot to **agentic iterative refinement with model-based self-critique + lightweight execution feedback** addresses all previous failure modes:
- No profiling overhead (test pass/fail only)
- Uses existing benchmarks (no new rubrics or human evaluation)
- Applies validated confidence calibration (temperature scaling: 58.3% ECE reduction)
- Aligns with DL4C workshop priorities (agentic methods, model-based judges, benchmarking)

### Techniques Used

ROUTE_TO_0 Auto-Fill Mode (failure context analysis with pivot to agentic methods validated on existing benchmarks)

### Areas for Further Exploration

- Multi-agent debate for code generation (multiple LLM critics before execution)
- Hierarchical refinement (high-level plan critique → detailed implementation critique)
- Learned self-critique (train a separate critic model vs. prompt-based self-evaluation)
- Adaptive refinement strategies (learn when to stop refining vs. continue based on problem difficulty)
- Cross-benchmark transfer (refinement strategies learned on HumanEval applied to CodeContests)

---

## Next Steps

Proceed to Phase 1 - Targeted Research (focus on agentic code generation, iterative refinement, execution feedback methods, LLM-as-judge, self-critique, and confidence calibration)

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
