# Product Requirements Document (PRD): h-m2

**Date:** 2026-03-18
**Author:** Anonymous
**Hypothesis:** h-m2 (MECHANISM)
**Version:** 1.0

---

## Executive Summary

This PRD defines the implementation requirements for validating hypothesis h-m2: testing whether sequential single-source feedback presentation reduces mean iterations-to-solution compared to simultaneous aggregation feedback for LLM code generation under cascade routing conditions.

**Core Deliverable:** Comparative experiment system that runs the same 20 dual-sensitive tasks from h-e1 through two feedback routing conditions (sequential vs aggregation) and measures iterations-to-solution, success rates, and token efficiency.

**Success Criteria:** Sequential mode demonstrates lower mean iterations-to-solution than aggregation mode (directional effect sufficient for SHOULD_WORK gate).

---

## Problem Statement

### Background

From h-m1 validation results:
- Cascade routing with mypy → pytest conditional gating is established
- 20 dual-sensitive tasks qualified from h-e1
- Mypy detection rate: 99.6% (697/700 iterations)
- CodeLlama-7B baseline configuration validated

### Current Gap

While h-m1 validates that cascade routing catches errors efficiently, the **feedback presentation mode** (single-source sequential vs simultaneous aggregation) remains untested. Prior work (LLMLOOP, Static Analysis Feedback) suggests iterative refinement works, but does not compare within-iteration presentation modes.

### Hypothesis to Validate

**h-m2:** Under dual-sensitive task conditions with cascade routing (N=20 from H-E1), if LLM receives single-source feedback per iteration (mypy-only OR pytest-only) instead of simultaneous aggregation (both concatenated), then mean iterations-to-solution decreases, because sequential presentation enforces attention economy reducing cognitive load on error type disambiguation.

**Gate Type:** SHOULD_WORK (failure → EXPLORE alternative explanation)

---

## Functional Requirements

### FR-1: Feedback Router Implementation

**Priority:** P0 (Critical)

Implement `FeedbackRouter` class with two modes:

1. **Sequential Mode (Proposed)**
   - If mypy has errors → present ONLY mypy feedback this iteration
   - If mypy clean → present ONLY pytest feedback this iteration
   - Never present both sources simultaneously in one iteration

2. **Aggregation Mode (Baseline)**
   - Always run both mypy and pytest
   - Concatenate all available feedback (mypy + pytest) into single string
   - Present combined feedback to LLM

**Acceptance Criteria:**
- Router correctly isolates feedback sources in sequential mode
- Router correctly concatenates feedback in aggregation mode
- Logging captures which source(s) presented per iteration

### FR-2: LLM Generation Loop

**Priority:** P0 (Critical)

Integrate CodeLlama-7B with feedback router:

**Model Configuration (reuse from h-m1):**
- Model: `codellama/CodeLlama-7b-hf`
- Temperature: 0.8
- Top-p: 0.95
- Top-k: 40
- Max tokens: 256
- Device: Auto (GPU if available)

**Loop Structure:**
- Initial generation from task prompt
- Feedback-driven refinement (max 10 iterations)
- Stop conditions: tests pass OR max iterations reached
- Log all feedback presented and LLM responses

**Acceptance Criteria:**
- Generation matches h-m1 baseline quality
- Iteration counting is accurate
- Logs capture full conversation history

### FR-3: Static Analysis Integration (mypy)

**Priority:** P0 (Critical)

**Reuse from h-m1:**
- mypy --strict configuration
- Parse error messages into structured format
- Extract error location, type, and description

**Acceptance Criteria:**
- Mypy errors correctly detected
- Error messages formatted for LLM consumption
- Clean mypy = zero errors reported

### FR-4: Test Execution Integration (pytest)

**Priority:** P0 (Critical)

**Dataset:** HumanEval+ test suites (20 dual-sensitive tasks from h-e1)

**Test Runner:**
- Execute pytest on generated code
- Capture test failures with assertion details
- Return pass/fail status + failure messages

**Acceptance Criteria:**
- All 164 HumanEval+ tasks loadable
- 20 qualified dual-sensitive tasks selected from h-e1 results
- Pytest correctly executes and captures failures

### FR-5: Experiment Runner (Comparative Design)

**Priority:** P0 (Critical)

**Design:** 2×1 between-subjects comparison

**Procedure:**
1. Load 20 dual-sensitive tasks from h-e1 qualified set
2. For each task:
   - **Condition A:** Run with aggregation mode
   - **Condition B:** Run with sequential mode
3. Record per-task metrics:
   - iterations-to-solution
   - success (solved within 10 iterations: yes/no)
   - total tokens consumed
   - feedback presentation count

**Controlled Variables:**
- Same tasks across both conditions
- Same CodeLlama-7B model and config
- Same mypy/pytest settings
- Same max iteration limit (10)
- Same prompt template structure

**Acceptance Criteria:**
- All 20 tasks tested in both conditions
- Deterministic execution (fixed seed)
- Logs saved per (task, condition) pair

### FR-6: Evaluation Metrics

**Priority:** P0 (Critical)

**Primary Metric:**
- **Mean iterations-to-solution:**
  - Aggregation: μ_agg = mean(iterations) across 20 tasks
  - Sequential: μ_seq = mean(iterations) across 20 tasks
  - **Success criterion:** μ_seq < μ_agg (directional)

**Secondary Metrics:**
- **Success rate:** Proportion solved within 10 iterations (per condition)
- **Token efficiency:** Mean tokens per successful solution (per condition)
- **Convergence pattern:** Iteration count distribution (variance comparison)

**Acceptance Criteria:**
- Metrics computed correctly from logs
- Statistical comparison (mean, SD) reported
- Gate validation: μ_seq < μ_agg → PASS

### FR-7: Mechanism Verification

**Priority:** P0 (Critical)

Verify feedback routing mechanism operates as specified:

**Verification Checks:**
1. Sequential mode never presents multiple sources in one iteration
2. Aggregation mode presents all available sources when errors exist
3. Same tasks tested in both conditions (set equality check)

**Acceptance Criteria:**
- Verification code included in experiment runner
- Assertion failures halt execution with clear error
- Verification passes for all (task, condition) pairs

### FR-8: Visualization Generation

**Priority:** P1 (Important)

**Required Figures:**
1. **Gate Metrics Comparison** (Bar chart)
   - μ_seq vs μ_agg with error bars

**Additional Figures (autonomous):**
2. **Iteration Distribution** (Box plots)
   - Aggregation vs sequential
3. **Convergence Curves** (Line plot)
   - Cumulative success rate per iteration
4. **Per-Task Comparison** (Scatter plot)
   - X: aggregation iterations, Y: sequential iterations
5. **Token Efficiency** (Bar chart)
   - Mean tokens per successful solution

**Output Location:** `{hypothesis_folder}/figures/`

**Acceptance Criteria:**
- All figures generated and saved
- Figures referenced in validation report
- Clear visual distinction between conditions

---

## Data Specifications

### Input Data

| Dataset | Source | Size | Purpose |
|---------|--------|------|---------|
| HumanEval+ | evalplus package | 164 tasks | Full benchmark |
| Qualified tasks (h-e1) | h-e1/04_validation.md | 20 tasks | Dual-sensitive subset |

**Loading:**
```python
from evalplus.data import get_human_eval_plus
dataset = get_human_eval_plus()
# Filter to 20 qualified task IDs from h-e1
```

### Output Data

| Artifact | Format | Location | Content |
|----------|--------|----------|---------|
| Experiment logs | JSON | `{hypothesis_folder}/logs/` | Per-iteration feedback, code, results |
| Metrics summary | JSON | `{hypothesis_folder}/metrics.json` | Aggregated statistics |
| Figures | PNG | `{hypothesis_folder}/figures/` | Visualizations |
| Validation report | Markdown | `{hypothesis_folder}/04_validation.md` | Gate result, analysis |

---

## Non-Functional Requirements

### NFR-1: Performance

- **Runtime:** <30 minutes for full experiment (20 tasks × 2 conditions × ~5-10 iterations)
- **GPU Usage:** Single GPU (select empty GPU via `nvidia-smi`)
- **Memory:** <16GB GPU memory (CodeLlama-7B footprint)

### NFR-2: Reproducibility

- **Fixed seed:** All random operations seeded
- **Version pinning:** Record exact package versions
- **Logging:** Complete conversation history saved per task

### NFR-3: Code Quality

- **Modularity:** Separate classes for FeedbackRouter, LLM, Mypy, Pytest
- **Testing:** Unit tests for router logic (sequential vs aggregation)
- **Documentation:** Docstrings for all public methods

### NFR-4: Error Handling

- **MCP failures:** Retry 3 times with 15s delay
- **Model loading errors:** Clear error messages with fallback instructions
- **Dataset loading errors:** Validate task IDs exist before experiment

---

## Dependencies

### External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| transformers | >=4.30.0 | CodeLlama-7B loading |
| torch | >=2.0.0 | Model inference |
| evalplus | latest | HumanEval+ dataset |
| mypy | >=1.0.0 | Static analysis |
| pytest | >=7.0.0 | Test execution |
| matplotlib | >=3.5.0 | Visualizations |
| seaborn | >=0.12.0 | Enhanced plots |
| numpy | >=1.24.0 | Metrics computation |
| pyyaml | >=6.0 | Config loading |

### Internal Dependencies

| Component | Source | Purpose |
|-----------|--------|---------|
| Dual-sensitive tasks | h-e1/04_validation.md | Qualified task IDs |
| Model config | h-m1/04_validation.md | Optimal hyperparameters |
| Cascade routing | h-m1 implementation | Mypy → pytest conditional gating |

---

## Success Criteria

### Gate Validation (SHOULD_WORK)

**Primary Success Criterion:**
- Sequential mode shows **lower** mean iterations-to-solution than aggregation mode
- **Threshold:** Directional effect (μ_seq < μ_agg), no specific magnitude required

**If PASS:**
- Mechanism validated
- Attention economy hypothesis supported
- Proceed to next hypothesis (h-m3 or h-c1)

**If FAIL:**
- EXPLORE alternative explanation: LLMs may internally normalize feedback regardless of presentation
- Document findings in 04_validation.md
- Proceed with limitation noted

### Quality Gates

| Gate | Criterion | Action if Failed |
|------|-----------|------------------|
| Mechanism Active | Verification checks pass | Fix router logic, re-run |
| Data Completeness | All 20 tasks tested in both conditions | Investigate failures, retry |
| Reproducibility | Re-run produces same results (±5% variance) | Check seed, investigate non-determinism |

---

## Timeline & Milestones

**Phase 4 Implementation:**
1. Environment setup (datasets, models) - Task 1-3
2. Core implementation (router, LLM loop, verification tools) - Task 4-8
3. Experiment execution - Task 9-11
4. Metrics computation and visualization - Task 12-14
5. Validation report generation - Task 15-16

**Total Task Budget:** ≤30 tasks (MECHANISM = FULL tier)

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| CodeLlama-7B model download failure | Blocking | Low | Pre-download in environment setup task |
| GPU memory overflow | Blocking | Low | Use single GPU, batch size = 1 |
| Non-deterministic results | Quality | Medium | Fixed seed + temperature control + logging |
| Sequential mode worse than aggregation | Gate FAIL | Medium | Acceptable outcome (SHOULD_WORK gate) → EXPLORE |
| Qualified tasks (h-e1) not accessible | Blocking | Low | Verify h-e1 results exist in prerequisite check |

---

## Appendix

### Reference Implementations

**Patterns Applied:**
- LLMLOOP feedback loop structure
- Static Analysis Feedback fitness-based iteration
- h-m1 cascade routing infrastructure

**Novel Contribution:**
- Single-source vs simultaneous feedback presentation comparison (not from existing paper)

### Traceability

| Requirement | Source |
|-------------|--------|
| 20 dual-sensitive tasks | h-e1/04_validation.md (35 qualified tasks, use first 20) |
| CodeLlama-7B config | h-m1/04_validation.md optimal config |
| Cascade routing | h-m1 implementation (mypy → pytest conditional) |
| Evaluation metrics | h-m2/02c_experiment_brief.md Section "Evaluation" |
| Mechanism pseudo-code | h-m2/02c_experiment_brief.md Section "Proposed Model" |

---

*PRD Generated by Phase 3 Step 2 | Based on 02c_experiment_brief.md*
