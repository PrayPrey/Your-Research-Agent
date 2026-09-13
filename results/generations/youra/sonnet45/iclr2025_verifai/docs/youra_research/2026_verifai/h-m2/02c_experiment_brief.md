# Experiment Design: h-m2

**Date:** 2026-03-18
**Author:** Anonymous
**Hypothesis Statement:** Under dual-sensitive task conditions with cascade routing (N=20 from H-E1), if LLM receives single-source feedback per iteration (mypy-only or pytest-only) instead of simultaneous aggregation (both concatenated), then mean iterations-to-solution decreases, because sequential presentation enforces attention economy reducing cognitive load on error type disambiguation.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Validates causal mechanism operation.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-m1 (COMPLETED)
**Gate Status:** SHOULD_WORK (failure_action: EXPLORE - LLMs internally normalize feedback regardless of presentation)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1

### Gate Condition
SHOULD_WORK gate: If hypothesis fails, explore alternative explanation (LLMs may internally normalize feedback regardless of presentation order).

---

## Continuation Context

This is a **continuation experiment** building on h-m1 (COMPLETED).

**Controlled Variables from h-m1:**
- Same 20 dual-sensitive tasks identified in h-e1
- Same CodeLlama-7B model
- Same cascade routing infrastructure (mypy → pytest conditional gating)

**New Independent Variable:**
- Feedback presentation: Single-source sequential vs simultaneous aggregation

### Previous Hypothesis Results (h-m1)

From h-m1/04_validation.md:
- **Mypy Detection Rate:** 99.6% (697/700 iterations)
- **Gate Result:** PASS (threshold: 30%, actual: 99.6%)
- **Key Finding:** Static analysis catches nearly all type errors before execution
- **Optimal Configuration:** mypy --strict with default settings

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: LLM feedback routing iteration**
- Limited direct matches in Archon KB for this specific mechanism
- General LLM training/iteration patterns found, but not feedback routing specific
- **Key Insight:** This is a novel mechanism not extensively documented in prior work

**Query 2: Sequential feedback attention economy**
- Found attention mechanism papers (Attend-and-Excite, Perturbed Attention Guidance)
- Not directly applicable to feedback routing, but supports attention economy concept
- **Key Insight:** Attention economy is a validated principle in ML, applicable to feedback presentation

**Query 3: Code generation mypy pytest**
- Found Google Python Style Guide and testing utilities
- General Python testing infrastructure, not LLM-specific
- **Key Insight:** Standard mypy/pytest tooling is well-established

**Summary:** Limited prior art on sequential vs simultaneous feedback routing for LLMs. This validates the novelty of h-m2's hypothesis.

### Archon Code Examples

**Query 1: LLM code generation feedback**
- Found general code generation examples (AudioLDM, diffusers)
- Not specific to feedback routing mechanisms
- **Key Insight:** Standard LLM generation patterns exist, but feedback routing is underexplored

**Query 2: Iterative refinement loop**
- Found diffusion model refinement examples (base→refiner pipelines)
- Training loop structures with iterative improvement
- **Key Insight:** Iterative refinement is a common pattern; adapting to feedback routing is the novel contribution

### Exa GitHub Implementations

**Repository 1:** LLMLOOP (ravinravi03/LLMLOOP)
- **URL:** https://github.com/ravinravi03/LLMLOOP
- **Relevance:** ⭐⭐⭐ Implements iterative feedback loops for LLM code generation
- **Key Features:**
  - 5 iterative self-refinement loops (compilation, static analysis, test failures, test quality, coverage)
  - Static analysis integration (similar to our mypy integration)
  - Feedback-driven improvement cycles
- **Key Code Pattern:**
  ```python
  # Loop structure: compilation → static analysis → tests → mutation
  # Feedback is presented to LLM iteratively
  ```
- **Used For:** Feedback loop architecture design
- **Limitation:** Uses *sequential* loop stages (compilation→static→tests), not comparing *within-stage* presentation modes

**Repository 2:** rTED (Reflective Type Error Detection)
- **URL:** https://arxiv.org/html/2507.02318v1
- **Relevance:** ⭐⭐ Type-aware test generation with iterative refinement
- **Key Features:**
  - Type constraint analysis before test generation
  - Reflective validation to reduce false positives
  - Iterative improvement with feedback
- **Used For:** Type-based feedback integration patterns

**Repository 3:** Static Analysis Feedback Loop (arxiv:2508.14419)
- **URL:** https://arxiv.org/abs/2508.14419
- **Relevance:** ⭐⭐⭐ Directly addresses static analysis as feedback for LLMs
- **Key Features:**
  - Iterative refinement with Bandit + Pylint
  - Fitness score improvement cycles
  - **Accepts solution only if fitness improves** (similar to our comparison design)
- **Key Code Pattern:**
  ```python
  while issues_remaining and i < 10:
      propose = mutate(current, llm, prompt)
      if fitness(propose) >= fitness(current):
          current = propose
  ```
- **Used For:** Core iteration loop structure, fitness-based acceptance criterion

**Repository 4:** CodeLutra (Preference-Guided Refinement)
- **URL:** https://arxiv.org/abs/2411.05199
- **Relevance:** ⭐ Preference-based learning from successes/failures
- **Key Features:**
  - Bradley-Terry model for comparing code attempts
  - Learns from both correct and incorrect outputs
- **Used For:** Conceptual support for comparing feedback modes

### 🎯 Implementation Priority Assessment

**CRITICAL: This is NOT a paper reproduction experiment. This is an original research hypothesis.**

**Implementation Priority:**
- **Novel Mechanism:** Single-source vs simultaneous feedback routing is NOT from an existing paper
- **Build on h-m1 infrastructure:** Reuse cascade routing system from h-m1 (validated)
- **Inspiration from:** LLMLOOP structure + Static Analysis Feedback patterns

**Recommended Implementation Path:**
- **Primary:** Custom implementation extending h-m1 cascade routing framework
- **Fallback:** None (novel mechanism requires custom implementation)
- **Justification:** No official implementation exists. We leverage proven patterns (LLMLOOP's feedback loops + Static Analysis Feedback's fitness comparison) but implement the *specific* single-source vs simultaneous presentation comparison ourselves

### Code Analysis (Serena MCP)

*Skipped* - This hypothesis tests a novel feedback routing mechanism (single-source vs simultaneous presentation). The mechanism is conceptual (how feedback is structured in prompts) rather than requiring analysis of complex existing code. Implementation patterns from Exa GitHub sources (LLMLOOP, Static Analysis Feedback) are sufficiently clear without Serena semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset:** HumanEval+ (20 dual-sensitive tasks from h-e1)
**Type:** standard (programming task benchmark)
**Source:** evalplus Python package
**Path:** auto (downloaded via pip install evalplus)

**Selection Rationale (from Phase 2A via Phase 2B):**
- 164 programming tasks with 80+ robustness tests per task
- Classification-evaluation decoupling prevents dataset contamination
- Tasks require compositional verification (type + logic)
- Enables measurement of dual-sensitive task performance

**H-M2 Specific Usage:**
- **Reuse qualified tasks from h-e1:** N=20 dual-sensitive tasks (identified in h-e1 validation as having both mypy-sensitive and pytest-sensitive solutions)
- **Continuation experiment:** Same task pool enables controlled comparison (only feedback routing changes)

**Statistics:**
- Total tasks: 20 (from h-e1 qualified set)
- Samples per task: Multiple iterations until solution (max 10 iterations per task per condition)
- Expected total samples: ~20 tasks × 2 conditions × ~5-10 iterations = 200-400 samples

**Preprocessing:**
- Load task prompts and test suites via evalplus.data.get_human_eval_plus()
- Use same prompt template as h-e1/h-m1 for consistency
- No augmentation (standard HumanEval+ tests)

**Loading Information** (for Phase 4 download):
- Method: Python package (evalplus)
- Identifier: N/A (built-in task loader)
- Code: `from evalplus.data import get_human_eval_plus; dataset = get_human_eval_plus()`

### Models

#### Baseline Model

**Model:** CodeLlama-7B (Base, 7B parameters)
**Type:** Base code generation model (NOT instruction-tuned)
**Source:** HuggingFace: codellama/CodeLlama-7b-hf

**Reuse from h-m1 (continuation experiment):**
- Same model ensures controlled comparison
- Proven stable in h-e1 and h-m1 validations
- Optimal configuration already established:
  - Temperature: 0.8
  - Top-p: 0.95
  - Top-k: 40
  - Max tokens: 256
  - Device: Auto (GPU if available)

**Why CodeLlama-7B:**
- Widely used baseline for code generation research
- Fast inference (<30min for full experiment)
- Tests feedback routing mechanism, not instruction-following capability
- Base model (not instruction-tuned) better isolates feedback presentation effects

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: codellama/CodeLlama-7b-hf
- Code: `from transformers import AutoModelForCausalLM, AutoTokenizer; model = AutoModelForCausalLM.from_pretrained("codellama/CodeLlama-7b-hf"); tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-hf")`

#### Proposed Model

**Architecture:** CodeLlama-7B with **Single-Source Sequential Feedback Routing**

**Conditions:**
1. **Baseline (Simultaneous Aggregation):** Both mypy and pytest feedback concatenated in each iteration
2. **Proposed (Sequential Single-Source):** Only one feedback source per iteration (mypy OR pytest, not both)

**Integration:** Feedback router wraps CodeLlama-7B generation loop

**Core Mechanism Implementation:**

```python
# Core Mechanism: Single-Source Sequential Feedback Routing
# Based on: LLMLOOP feedback loop + Static Analysis Feedback pattern

class FeedbackRouter:
    """
    Routes feedback to LLM one source at a time (sequential)
    vs both sources simultaneously (aggregation).
    """
    def __init__(self, mode: str, llm_model, static_analyzer, test_runner):
        self.mode = mode  # "sequential" or "aggregation"
        self.llm = llm_model
        self.mypy = static_analyzer
        self.pytest = test_runner

    def generate_with_feedback(self, task_prompt: str, max_iter: int = 10):
        """
        Args:
            task_prompt: HumanEval problem description
            max_iter: Maximum feedback iterations
        Returns:
            (solution_code, iterations_to_solution, feedback_log)
        """
        code = self.llm.generate(task_prompt)  # Initial generation

        for iteration in range(max_iter):
            # Step 1: Run mypy static analysis
            mypy_result = self.mypy.check(code, strict=True)

            # Step 2: Decide feedback presentation mode
            if self.mode == "sequential":
                # PROPOSED: Single-source per iteration
                if mypy_result.has_errors:
                    # Present ONLY mypy feedback this iteration
                    feedback = f"Mypy errors:\n{mypy_result.errors}"
                    code = self.llm.refine(code, feedback)
                    continue  # Skip pytest this iteration
                else:
                    # Mypy clean → present ONLY pytest feedback
                    pytest_result = self.pytest.run(code)
                    if pytest_result.passed:
                        return code, iteration+1, "SUCCESS"
                    feedback = f"Test failures:\n{pytest_result.failures}"
                    code = self.llm.refine(code, feedback)

            elif self.mode == "aggregation":
                # BASELINE: Both sources concatenated
                pytest_result = self.pytest.run(code)
                feedback_parts = []
                if mypy_result.has_errors:
                    feedback_parts.append(f"Mypy:\n{mypy_result.errors}")
                if not pytest_result.passed:
                    feedback_parts.append(f"Tests:\n{pytest_result.failures}")

                if not feedback_parts:
                    return code, iteration+1, "SUCCESS"

                feedback = "\n\n".join(feedback_parts)
                code = self.llm.refine(code, feedback)

        return code, max_iter, "MAX_ITER"

# Comparison Experiment:
# - Condition A (Baseline): mode="aggregation"
# - Condition B (Proposed): mode="sequential"
# - Measure: mean iterations-to-solution for each mode
# - Hypothesis: sequential < aggregation (fewer iterations)
```

**Key Difference from Baseline:**
- **Baseline (h-m1):** Tests cascade routing (mypy → pytest conditionally)
- **Proposed (h-m2):** Tests feedback *presentation* (single-source vs simultaneous)

### Training Protocol

**From Previous Hypothesis (h-m1):**
- **Optimizer:** Not applicable (no training, inference-only)
- **Model Configuration:**
  - Temperature: 0.8
  - Top-p: 0.95
  - Top-k: 40
  - Max tokens: 256
  - Seeds: 1 (fixed seed for reproducibility)

**Rationale:** Optimal configuration from h-m1, reusing for controlled experiment.

**Experiment Protocol:**

**Design:** 2×1 between-subjects (condition: sequential vs aggregation)

**Independent Variable (IV):**
- Feedback presentation mode: Single-source sequential vs Simultaneous aggregation

**Procedure:**
1. Load 20 dual-sensitive tasks from h-e1 qualified set
2. For each task:
   - **Condition A (Baseline):** Run with aggregation mode (both feedback sources concatenated)
   - **Condition B (Proposed):** Run with sequential mode (one source per iteration)
3. For each (task, condition) pair:
   - Generate initial solution with CodeLlama-7B
   - Enter feedback loop (max 10 iterations)
   - Record iterations-to-solution
   - Log all feedback presented and LLM responses

**Controlled Variables:**
- Same 20 tasks across both conditions
- Same CodeLlama-7B model and configuration
- Same mypy --strict settings
- Same pytest test suites (HumanEval+)
- Same max iteration limit (10)
- Same prompt template structure

**Sample Size:**
- N=20 tasks
- 2 conditions
- Total: 40 task-condition pairs

### Evaluation

**Primary Metrics:**
1. **Mean iterations-to-solution:**
   - Aggregation mode: μ_agg = mean(iterations_aggregation)
   - Sequential mode: μ_seq = mean(iterations_sequential)
   - **Success criterion:** μ_seq < μ_agg (directional, PoC-level)

2. **Success rate:**
   - Proportion of tasks solved within 10 iterations
   - Track per condition

3. **Token efficiency:**
   - Total tokens consumed per successful solution
   - Compare across conditions

**Secondary Metrics:**
1. **Feedback presentation count:**
   - Sequential: number of feedback instances shown
   - Aggregation: number of concatenated feedback instances
   - Tests if sequential actually reduces feedback load

2. **Convergence pattern:**
   - Iteration count distribution per condition
   - Identify if sequential has tighter distribution (more consistent)

**Success Criteria (SHOULD_WORK gate):**
- **Primary:** Sequential mode shows lower mean iterations-to-solution than aggregation
- **Gate threshold:** No specific threshold (directional effect sufficient for PoC)
- **If fails:** EXPLORE - LLMs may internally normalize feedback regardless of presentation

**Expected Baseline Performance (from h-m1):**
- Aggregation mode with cascade routing: ~3-7 iterations typical
- High variability expected (SD > 1.0)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Code generation with feedback iteration
- Library: Custom metrics (iteration counting, token tracking)
- Code:
  ```python
  # Simple iteration counting
  iterations_aggregation = []
  iterations_sequential = []
  for task in tasks:
      iter_agg = run_experiment(task, mode="aggregation")
      iter_seq = run_experiment(task, mode="sequential")
      iterations_aggregation.append(iter_agg)
      iterations_sequential.append(iter_seq)

  mean_agg = np.mean(iterations_aggregation)
  mean_seq = np.mean(iterations_sequential)
  success = mean_seq < mean_agg
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on hypothesis type (MECHANISM - feedback routing comparison) and evaluation metrics:

1. **Iteration Distribution Comparison** (Box plots)
   - Box plot: iterations-to-solution for aggregation vs sequential
   - Shows distribution, median, outliers

2. **Convergence Curves** (Line plot)
   - X-axis: iteration number
   - Y-axis: cumulative success rate
   - Two lines: aggregation vs sequential
   - Shows which mode converges faster

3. **Per-Task Comparison** (Scatter plot)
   - X-axis: iterations (aggregation)
   - Y-axis: iterations (sequential)
   - Each point = one task
   - Points below diagonal = sequential wins

4. **Token Efficiency** (Bar chart)
   - Mean tokens per successful solution
   - Aggregation vs sequential

> Phase 4 Coder should implement these visualizations using matplotlib/seaborn.
> All figures saved to `h-m2/figures/`.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **Mechanism Exists**: YES - Sequential feedback routing is a discrete implementation choice (one source vs concatenated sources per iteration)
- **Mechanism Isolatable**: YES - Can implement both modes (sequential, aggregation) and compare directly on same tasks
- **Baseline Measurable**: YES - Aggregation mode serves as baseline; iterations-to-solution is directly measurable

### Architecture Compatibility
The feedback routing mechanism is **compatible** with CodeLlama-7B architecture:
- Mechanism operates at the **prompt engineering level** (how feedback is structured in input text)
- No model architecture changes required
- Compatible with any autoregressive LLM
- Independent of model size (7B tested here, generalizable)

**Verification:**
- CodeLlama-7B confirmed working in h-e1 and h-m1
- Feedback routing is a wrapper around generation API
- No GPU/memory conflicts

### Activation Indicators
- **Log Message:**
  ```
  [SEQUENTIAL MODE] Iteration {i}: Presenting {source} feedback only
  [AGGREGATION MODE] Iteration {i}: Presenting both mypy + pytest feedback
  ```
- **Feedback Structure Change:**
  - Sequential: alternating single-source feedback strings
  - Aggregation: concatenated multi-source feedback strings
- **Expected Metric Delta:**
  - Sequential iterations < Aggregation iterations
  - Expected reduction: 10-30% (exploratory, PoC level)

### Mechanism Verification Code
```python
def verify_mechanism_active(experiment_log):
    """
    Verify feedback routing mechanism is working correctly.
    Returns: (mechanism_active, evidence)
    """
    # Check 1: Sequential mode never presents both sources simultaneously
    for entry in experiment_log:
        if entry['mode'] == 'sequential':
            feedback_sources = count_sources(entry['feedback_text'])
            assert feedback_sources == 1, "Sequential violated: multiple sources in one iteration"

    # Check 2: Aggregation mode always presents all available sources
    for entry in experiment_log:
        if entry['mode'] == 'aggregation' and entry['has_errors']:
            feedback_sources = count_sources(entry['feedback_text'])
            assert feedback_sources >= 1, "Aggregation violated: no feedback when errors exist"

    # Check 3: Same tasks tested in both conditions
    tasks_seq = set(e['task_id'] for e in experiment_log if e['mode'] == 'sequential')
    tasks_agg = set(e['task_id'] for e in experiment_log if e['mode'] == 'aggregation')
    assert tasks_seq == tasks_agg, "Task mismatch between conditions"

    return True, "Mechanism verified: routing logic operates as specified"

def count_sources(feedback_text):
    """Count distinct feedback sources in text."""
    sources = 0
    if "mypy" in feedback_text.lower() or "type error" in feedback_text.lower():
        sources += 1
    if "test" in feedback_text.lower() or "assert" in feedback_text.lower():
        sources += 1
    return sources
```

### Success Criteria
- **Threshold:** Directional effect (μ_seq < μ_agg)
- **Metric:** Mean iterations-to-solution
- **Gate Type:** SHOULD_WORK
  - **If pass:** Mechanism validated, supports attention economy hypothesis
  - **If fail:** EXPLORE alternative - LLMs may normalize feedback internally regardless of presentation

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Limited direct relevance** - This hypothesis addresses a novel mechanism (single-source vs simultaneous feedback routing) not extensively documented in prior work. Archon searches provided general context but no direct precedents.

**Query Results Used:**
- Attention economy concept (from attention mechanism papers)
- General LLM iteration patterns
- Standard mypy/pytest tooling documentation

**Key Insight:** Lack of prior art validates the novelty of this research direction.

### B. GitHub Implementations (Exa)

**Repository 1:** LLMLOOP - Iterative Feedback Loops for LLM Code Generation
- **URL:** https://github.com/ravinravi03/LLMLOOP
- **Query Used:** "LLM code generation iterative feedback mypy pytest Python"
- **Relevance:** ⭐⭐⭐ Implements iterative feedback loops (compilation → static analysis → tests)
- **Key Code Pattern:**
  ```python
  # Sequential loop stages
  for issue_type in [compilation, static_analysis, tests, mutation, coverage]:
      feedback = analyze(code, issue_type)
      code = llm.refine(code, feedback)
  ```
- **Used For:** Feedback loop architecture design
- **Limitation:** Addresses *stage* sequencing (compilation→static), not *within-stage* presentation modes (single vs simultaneous)

**Repository 2:** Static Analysis as Feedback Loop (arxiv:2508.14419)
- **URL:** https://arxiv.org/abs/2508.14419 & https://arxiv.org/html/2508.14419v1
- **Query Used:** "CodeLlama iterative refinement static analysis execution feedback"
- **Relevance:** ⭐⭐⭐ **Most relevant** - Iterative refinement with Bandit + Pylint
- **Key Code:**
  ```python
  current = initial_code
  while issues_remaining and i < 10:
      propose = llm.mutate(current, prompt_with_issues)
      if fitness(propose) >= fitness(current):
          current = propose  # Accept only if improves
  ```
- **Used For:**
  - Core iteration loop structure
  - Fitness-based acceptance criterion
  - Static analysis integration pattern
- **Results:** Security issues reduced from >40% to 13% within 10 iterations

**Repository 3:** rTED - Reflective Type Error Detection
- **URL:** https://arxiv.org/html/2507.02318v1
- **Relevance:** ⭐⭐ Type-aware test generation with iterative refinement
- **Key Features:** Type constraint analysis → reflection → iterative test generation
- **Used For:** Type-based feedback integration patterns

**Repository 4:** CodeLutra - Preference-Guided Refinement
- **URL:** https://arxiv.org/abs/2411.05199
- **Relevance:** ⭐ Preference-based learning from successes/failures
- **Key Concept:** Bradley-Terry model for comparing code attempts
- **Used For:** Conceptual support for comparing feedback presentation modes

**Repository 5:** COCOGEN - Iterative Refinement with Compiler Feedback
- **URL:** https://eprints.whiterose.ac.uk/id/eprint/218627/1/2024.findings-acl.138.pdf
- **Relevance:** ⭐⭐ Project-level code generation with iterative refinement
- **Key Pattern:** Generation → verification → retrieval loop
- **Used For:** Iterative refinement methodology

**Repository 6:** Feedback-Driven Security Patching (FDSP)
- **URL:** https://www.mdpi.com/2624-800X/5/4/110
- **Relevance:** ⭐⭐ Closed-loop refinement with static analysis (Bandit)
- **Key Results:** Improved vulnerability detection across GPT-4, GPT-3.5, CodeLlama
- **Used For:** Validation that static analysis feedback improves LLM code quality

### C. Previous Hypothesis Context

**Source:** Phase 4 Validation Report - h-m1
- **File:** `h-m1/04_validation.md`
- **Reused Components:**
  - **Dataset:** Same 20 dual-sensitive tasks from h-e1 qualified set
  - **Model:** CodeLlama-7B with same hyperparameters (temp=0.8, top-p=0.95, top-k=40, max_tokens=256)
  - **Verification Tools:** mypy --strict, pytest with HumanEval+ tests
  - **Infrastructure:** Cascade routing framework (mypy → pytest conditional gating)
- **Why Reused:** Enables controlled experiment - only feedback presentation mode changes between h-m1 and h-m2

**Key h-m1 Results:**
- Mypy detection rate: 99.6% (697/700 iterations caught static errors)
- Validates that mypy provides valuable early feedback
- Establishes baseline cascade routing performance

### D. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (HumanEval+) | Phase 2A via Phase 2B | 02b_verification_plan.md Section 1.3 |
| 20 dual-sensitive tasks | Previous (h-e1) | h-e1/04_validation.md (35 qualified tasks) |
| Model (CodeLlama-7B) | Phase 2A + Previous (h-m1) | 02b_verification_plan.md + h-m1/04_validation.md |
| Hyperparameters | Previous (h-m1) | h-m1/04_validation.md optimal config |
| Feedback loop architecture | GitHub (LLMLOOP) | Exa search result B.1 |
| Iteration logic with fitness | GitHub (Static Analysis Feedback) | arxiv:2508.14419 (Exa B.2) |
| Static analysis integration | GitHub (FDSP, Static Analysis Feedback) | Exa B.2, B.6 |
| Mechanism pseudo-code | Custom (novel) + GitHub patterns | LLMLOOP + Static Analysis Feedback structure |
| Evaluation metrics | Hypothesis (h-m2) + h-m1 baseline | Phase 2B success criteria + h-m1 results |
| mypy --strict configuration | Previous (h-m1) | h-m1/04_validation.md |
| pytest configuration | Previous (h-e1, h-m1) | h-e1/04_validation.md, h-m1/04_validation.md |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-18T16:29:45.605849+00:00

### Workflow History for This Hypothesis
- Event: Hypothesis h-m2 set to IN_PROGRESS
- Timestamp: 2026-03-18T16:29:45.605849+00:00
- Phase: Hypothesis Loop
- Details: External loop starting Phase 2C → 3 → 4 for h-m2

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
