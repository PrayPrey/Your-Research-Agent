# Verification Plan: Static-Execution Feedback Orthogonality

**Date:** 2026-08-19
**Hypothesis ID:** H-StaticExecOrthogonality-v1
**Confidence:** 0.75
**Total Hypotheses:** 5

---

## 0. Established Facts & Scope Reduction

### 0.1 Claims Registry

| Claim | Status | Evidence |
|-------|--------|----------|
| Static analysis feedback improves LLM code generation | BUILD_ON | Static Analysis as Feedback Loop (2508.14419): 40%→13% security issues |
| Execution feedback improves LLM code generation | BUILD_ON | CodeRL, RLPF, StepCoder demonstrate effectiveness |
| Iterative refinement paradigm works for code generation | BUILD_ON | Self-Refine (2303.17651): ~20% improvement |
| Static and execution feedback are orthogonal | **PROVE_NEW** | No prior controlled comparison exists |

### 0.2 Scope Reduction

**Reduction: 25%** (3 of 4 claims established)

Phase 2B-4 focuses only on PROVE_NEW claim: orthogonality of static vs execution feedback.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under iterative code refinement using Self-Refine on HumanEval+/MBPP+, if we provide combined static+execution feedback versus single-source feedback, then the combined condition achieves pass@k improvement that exceeds the maximum of individual improvements (Δ_combined > max(Δ_static, Δ_exec)), because static analysis captures structural errors (pylint/mypy detectable) while execution captures behavioral errors (test failures) - orthogonal signal classes.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference between combined feedback improvement and the maximum of individual feedback improvements (Δ_combined = max(Δ_static, Δ_exec)), indicating feedback sources are redundant with one subsuming the other.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval+ and MBPP+ (standard) | Standard code generation benchmarks with 80x/35x more tests than originals, ideal for testing feedback impact |
| **Model** | GPT-4 or CodeLlama-70B | Widely used code generation models capable of following feedback instructions |

**Dataset Details:**
- Source: evalplus (neuralmagic/evalplus)
- Path: https://github.com/neuralmagic/evalplus
- Size: HumanEval+ (164 problems), MBPP+ (399 problems) - **full test sets**

**Model Details:**
- Type: Large Language Model
- Source: OpenAI API or HuggingFace

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Static Analysis as Feedback Loop | 40%→13% security issues | Custom security benchmarks | No execution comparison, different benchmark |
| Self-Refine | ~20% improvement | Multiple benchmarks | Single feedback source, no factorial design |
| Helping LLMs Improve Code Generation | Combined static+execution improvement | Code benchmarks | Doesn't isolate individual contributions |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Static analysis and execution feedback capture different error classes | pylint/mypy detect type/syntax issues; tests detect runtime/logic issues | Combined feedback would show redundant improvement |
| A2 | LLMs can effectively incorporate feedback from either source | Self-Refine demonstrates feedback-driven refinement works | No improvement in any condition |
| A3 | HumanEval+/MBPP+ contain both structural and behavioral error opportunities | These benchmarks test diverse programming problems | Results may not generalize |
| A4 | Combining feedback does not confuse the LLM (no interference) | Prompt design can separate feedback types clearly | Combined < max, indicating negative interaction |
| A5 | The chosen LLM is representative of modern code generation models | GPT-4/CodeLlama-70B are widely used and studied | Results may not generalize to other models |

### 1.6 Research Gap & Novelty

**Gap:** No prior controlled comparison of static-only vs execution-only feedback exists.

**Novelty:**
- First systematic decomposition of feedback signal contributions on standard benchmarks
- Quantitative orthogonality test (additive vs max improvement model)
- 2×2 factorial design on HumanEval+/MBPP+

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | Mechanism | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | Mechanism | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Existence of Orthogonal Error Classes

**Type:** EXISTENCE
**Statement:** Under LLM code generation on HumanEval+/MBPP+, if we analyze error types from pylint/mypy vs test failures, then errors detected by static analysis are categorically different from errors detected by execution, because static tools operate on code structure while tests operate on runtime behavior.

**Rationale:** Before testing orthogonality of feedback effectiveness, we must establish that the error classes themselves are distinct. If static and execution feedback detect the same errors, orthogonality is impossible.

**Variables:**
- Independent: Error detection source (static analysis vs execution)
- Dependent: Error category distribution (structural vs behavioral)
- Controlled: Same code samples, same LLM, same problems

**Verification Protocol:**
1. Generate initial code for 563 problems (164 HumanEval+ + 399 MBPP+) using base LLM
2. Run pylint+mypy on all generated code, categorize errors (type errors, undefined vars, unreachable code, etc.)
3. Run evalplus test suite, categorize failures (wrong output, runtime exceptions, edge cases)
4. Compute Jaccard similarity between error sets per problem
5. Statistical test: errors should be <30% overlapping

**Success Criteria (PoC: Direction-based):**
- Primary: Jaccard similarity < 0.3 between static and execution error sets
- Secondary: At least 70% of problems show non-overlapping error types

**Failure Response:**
- IF fails: PIVOT to analyzing why overlap exists, may indicate feedback types are redundant

**Dependencies:** None

**Source:** Phase 2A SH1

---

#### H-M1: Static Analysis Detects Structural Errors

**Type:** MECHANISM
**Statement:** Under LLM code generation, if pylint+mypy are run on generated code, then they detect structural errors (type mismatches, undefined variables, unreachable code) that would not be caught by execution alone, because static analysis examines code structure without execution.

**Rationale:** This establishes the first half of the causal mechanism: static analysis provides a unique signal not available from execution feedback.

**Variables:**
- Independent: Code generation with structural errors
- Dependent: pylint/mypy error detection rate
- Controlled: Same LLM, temperature=0, same problems

**Verification Protocol:**
1. Generate code for full HumanEval+/MBPP+ test set (563 problems)
2. Run pylint+mypy, record all E/W codes
3. Categorize errors as structural (E0001, E1101, etc.) vs other
4. Verify structural errors are present in >50% of initially failing code

**Success Criteria:**
- Primary: pylint/mypy detect errors in >60% of problems with test failures
- Secondary: Structural error categories (type, undefined, unreachable) are present

**Failure Response:**
- IF fails: EXPLORE alternative static analysis tools (ruff, pyright)

**Dependencies:** H-E1

**Source:** Phase 2A Causal Step 2

---

#### H-M2: Execution Detects Behavioral Errors

**Type:** MECHANISM
**Statement:** Under LLM code generation, if test suites are run on generated code, then they detect behavioral errors (wrong output, runtime exceptions, edge case failures) that would not be caught by static analysis alone, because tests execute code paths with specific inputs.

**Rationale:** This establishes the second half of the causal mechanism: execution feedback provides a unique signal not available from static analysis.

**Variables:**
- Independent: Code generation with behavioral errors
- Dependent: Test failure detection rate
- Controlled: Same LLM, temperature=0, same problems

**Verification Protocol:**
1. Generate code for full HumanEval+/MBPP+ test set
2. Run evalplus test suite, record all failures
3. Categorize failures as behavioral (wrong output, exception, edge case)
4. Verify behavioral errors are present where static analysis found no issues

**Success Criteria:**
- Primary: Test failures occur in >40% of problems with zero pylint/mypy errors
- Secondary: Behavioral categories (wrong output, exception) are dominant failure modes

**Failure Response:**
- IF fails: EXPLORE whether static analysis is catching behavioral issues via type inference

**Dependencies:** H-M1

**Source:** Phase 2A Causal Step 3

---

#### H-M3: Combined Feedback Enables Dual Error Fixing

**Type:** MECHANISM
**Statement:** Under Self-Refine with combined feedback, if both static analysis and test results are provided to the LLM, then the LLM can fix both structural and behavioral errors in a single refinement cycle, because the combined signal provides complete error information.

**Rationale:** This tests whether the LLM can effectively use orthogonal feedback sources together without interference.

**Variables:**
- Independent: Feedback type (static-only, exec-only, combined)
- Dependent: Error fix rate per iteration
- Controlled: Same LLM, temperature=0, max 5 iterations, same prompt structure

**Verification Protocol:**
1. For each of 563 problems, run Self-Refine with 3 conditions
2. Record errors fixed per iteration for each condition
3. Compute error fix rate: (initial_errors - final_errors) / initial_errors
4. Compare combined vs single-source fix rates

**Success Criteria:**
- Primary: Combined condition fixes errors from both categories
- Secondary: Combined fix rate ≥ sum of individual category fix rates

**Failure Response:**
- IF fails: PIVOT to sequential feedback (static first, then exec) instead of concatenated

**Dependencies:** H-M2

**Source:** Phase 2A Causal Step 4

---

#### H-M4: Combined Improvement Exceeds Maximum of Individuals

**Type:** MECHANISM
**Statement:** Under Self-Refine on HumanEval+/MBPP+, if combined feedback is provided, then pass@1 improvement exceeds the maximum of static-only and exec-only improvements (Δ_combined > max(Δ_static, Δ_exec)), because orthogonal feedback enables additive improvements.

**Rationale:** This is the primary test of the orthogonality hypothesis - super-additive improvement proves feedback sources are not redundant.

**Variables:**
- Independent: Feedback type (none, static-only, exec-only, combined)
- Dependent: pass@1 on HumanEval+/MBPP+ (full test sets: 164+399 problems)
- Controlled: Base LLM, temperature=0, max 5 iterations, identical prompts

**Verification Protocol:**
1. Run 4-condition experiment: none, static-only, exec-only, combined
2. For each condition, run Self-Refine on full 563 problems
3. Compute pass@1 for each condition
4. One-tailed t-test: Δ_combined > max(Δ_static, Δ_exec) with p < 0.05

**Success Criteria:**
- Primary: Δ_combined > max(Δ_static, Δ_exec) with p < 0.05
- Secondary: Effect size d > 0.3

**Failure Response:**
- IF fails: Document as disproof of orthogonality (valid negative result)

**Dependencies:** H-M3

**Source:** Phase 2A Prediction P1

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Jaccard < 0.3 | STOP, feedback types likely redundant |
| H-M1 | MUST_WORK | Static errors in >60% of failing code | EXPLORE alt tools |
| H-M2 | SHOULD_WORK | Test failures where static found nothing | Document limitation |
| H-M3 | SHOULD_WORK | Combined fixes both error types | PIVOT to sequential |
| H-M4 | SHOULD_WORK | Δ_combined > max with p<0.05 | Document as negative result |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks |

**Total Duration:** 7 weeks

---

## 4. Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════
DEPENDENCY GRAPH - 5 Hypotheses (Sequential Chain)
═══════════════════════════════════════════════════════════════════

[Level 0 - Foundation]
         ┌─────┐
         │H-E1 │ (Existence: Error classes are orthogonal)
         └──┬──┘
            │ MUST_WORK
            ▼
[Level 1 - Mechanism Start]
         ┌─────┐
         │H-M1 │ (Static detects structural errors)
         └──┬──┘
            │ MUST_WORK
            ▼
[Level 2]
         ┌─────┐
         │H-M2 │ (Execution detects behavioral errors)
         └──┬──┘
            │ SHOULD_WORK
            ▼
[Level 3]
         ┌─────┐
         │H-M3 │ (Combined enables dual error fixing)
         └──┬──┘
            │ SHOULD_WORK
            ▼
[Level 4 - Final]
         ┌─────┐
         │H-M4 │ (Combined > max improvement)
         └─────┘
            │ SHOULD_WORK
            ▼
        COMPLETE

═══════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════════════
```

---

## 5. Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses over 7 Weeks
═══════════════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3-4    │ W5      │ W6      │ W7
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
PHASE 1: Foundation
  H-E1           │ ████████│         │         │         │
  [Gate 1]       │        ◆│         │         │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
PHASE 2: Mechanisms
  H-M1           │         │ ████████│         │         │
  H-M2           │         │         │ ████    │         │
  H-M3           │         │         │         │ ████    │
  H-M4           │         │         │         │         │ ████
  [Gate 2]       │         │         │         │         │    ◆
═══════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════════════
```

### 5.1 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4

**Total Duration:** 7 weeks
- Phase 1 (H-E1): 2 weeks
- Phase 2 (H-M1-M4): 5 weeks (2 + 1 + 1 + 1)

**Slack Available:** 0 weeks (all sequential)

### 5.2 Resource Summary

- Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Verification Phases: 2
- Execution Mode: Sequential chain

---

## 6. Risk Analysis

### 6.1 Risk-Assumption Mapping

| Risk | Source | Description | Severity | Affected |
|------|--------|-------------|----------|----------|
| R1 | A1 | Error classes overlap significantly | Critical | H-E1, H-M1, H-M2 |
| R2 | A2 | LLM cannot incorporate feedback effectively | High | H-M3, H-M4 |
| R3 | A3 | Benchmarks lack error diversity | Medium | All |
| R4 | A4 | Combined feedback causes LLM confusion | High | H-M3, H-M4 |
| R5 | A5 | Results don't generalize to other models | Medium | All |

### 6.2 Mitigation Strategies

**R1: Error Class Overlap (Critical)**
- Prevention: Use strict categorization (E-codes vs test failures)
- Detection: Compute Jaccard similarity early in H-E1
- Response: If overlap >30%, document as evidence against orthogonality

**R2: LLM Feedback Incorporation (High)**
- Prevention: Use established Self-Refine prompt structure
- Detection: Monitor error fix rate per iteration
- Response: PIVOT to CoT prompting or few-shot examples

**R3: Benchmark Error Diversity (Medium)**
- Prevention: Use both HumanEval+ and MBPP+ (563 total problems)
- Detection: Report results separately per benchmark
- Response: Document as limitation, suggest future multi-benchmark study

**R4: Combined Feedback Confusion (High)**
- Prevention: Clear prompt structure separating feedback types
- Detection: If combined < max, interference detected
- Response: PIVOT to sequential feedback (static first, then exec)

**R5: Model Generalization (Medium)**
- Prevention: Report as scope limitation upfront
- Detection: N/A (single model study)
- Response: Document for future work

---

## 7. Dialectical Analysis

### 7.1 Thesis

**Core Claim:** Combined static+execution feedback improves LLM code generation more than either alone because they capture orthogonal error classes.

**Supporting Evidence:**
1. Static analysis tools (pylint/mypy) operate on code structure
2. Tests execute code with specific inputs to check behavior
3. These two approaches cannot detect each other's error types by design

**Strengths:**
- Clear causal mechanism based on tool design
- Testable predictions with existing benchmarks
- All outcomes (orthogonal, redundant, interference) are publishable

### 7.2 Antithesis

**Null Hypothesis (H0):** Δ_combined = max(Δ_static, Δ_exec) - feedback types are redundant.

**Counter-Arguments:**
1. Static analysis may catch behavioral issues via type inference
2. Execution failures may correlate with static analysis findings
3. LLM may already encode static analysis knowledge internally

**Potential Failure Points:**
- Error overlap exceeds 30% (R1)
- Combined feedback confuses LLM (R4)
- One feedback type dominates, making the other redundant

### 7.3 Synthesis

The verification plan addresses this dialectic through sequential hypothesis testing:

1. **H-E1 (Foundation):** First establishes whether error classes are distinct
2. **H-M1-M2 (Mechanisms):** Validates each feedback type provides unique signal
3. **H-M3-M4 (Integration):** Tests whether orthogonality translates to improvement

**Conditions for Thesis Support:**
- Jaccard similarity < 0.3 (H-E1)
- Both feedback types detect unique errors (H-M1, H-M2)
- Combined > max with p < 0.05 (H-M4)

**Conditions for Antithesis Support:**
- Jaccard similarity ≥ 0.3 (H-E1 fails)
- Combined ≤ max (H-M4 fails)

**Nuanced Outcomes:**
1. Full Support: All pass → orthogonality confirmed
2. Partial Support: H-M4 fails but H-E1/H-M1-3 pass → orthogonal errors exist but don't translate to improvement
3. No Support: H-E1 fails → error classes are not orthogonal

### 7.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Error classes distinct | May overlap | H-E1 Jaccard test |
| Mechanism | Unique signals | May correlate | H-M1, H-M2 |
| Integration | Additive benefit | May interfere | H-M3 |
| Performance | Combined > max | Redundant | H-M4 statistical test |

**Overall Robustness:** HIGH - clear tests for each position

---

## 8. Executive Summary

**Main Hypothesis:** Combined static+execution feedback exceeds max of individuals
- ID: H-StaticExecOrthogonality-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4)
- Phases: 2 phases over 7 weeks
- Critical Gates: 2 decision points (Gate 1: H-E1, Gate 2: H-M1)

**Risk Assessment:** Medium
- Primary concerns: R1 (error overlap), R4 (LLM confusion)

**Sample Sizes:** Full standard test sets
- HumanEval+: 164 problems (full)
- MBPP+: 399 problems (full)
- Total: 563 problems per condition

**Immediate Action:** Begin Phase 1 with H-E1 (error class analysis)

---

## Appendices

### A. Phase 2A Reference
- Source: 03_refinement.yaml
- ID: H-StaticExecOrthogonality-v1
- Schema Version: 10.0.0

### B. Variables Reference

**Independent Variable:** Feedback type
- Levels: none, static-only, exec-only, combined

**Dependent Variables:**
- Primary: pass@1 (0-1)
- Secondary: Error reduction rate, Refinement efficiency

**Controlled Variables:**
- Base LLM (GPT-4 or CodeLlama-70B)
- Temperature (0.0)
- Max iterations (5)
- Prompt template (identical structure)

### C. Testable Predictions

| ID | Statement | Test | Success Criterion |
|----|-----------|------|-------------------|
| P1 | Combined > max of individuals | One-tailed t-test | p < 0.05, d > 0.3 |
| P2 | Static reduces more pylint errors | Error count | Static > Exec reduction |
| P3 | Exec reduces more test failures | Failure count | Exec > Static reduction |

---

*Generated by Phase 2B Planning Workflow*
*Date: 2026-08-19*
*Mode: UNATTENDED*
