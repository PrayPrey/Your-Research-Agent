# Verification Plan: Static Analysis Impact on Functional Correctness

**Date:** 2026-08-29
**Hypothesis ID:** H-StaticFeedback-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under the condition of iterative LLM code repair on HumanEval/MBPP,
if static analyzer feedback (pylint/mypy) is integrated alongside execution feedback,
then pass@k will improve compared to execution-only feedback,
because static analysis provides mechanistic error explanations and catches issues before execution.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in pass@k between static+execution feedback
and execution-only feedback conditions on HumanEval/MBPP benchmarks.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval (standard) | Standard code generation benchmark; pass@k is established metric |
| **Model** | GPT-4 or CodeLlama-34B | State-of-art models for code generation; Self-Debug baseline uses similar |

**Dataset Details:**
- Source: OpenAI (https://github.com/openai/human-eval)
- Path: huggingface: openai_humaneval

**Model Details:**
- Type: Large Language Model (code-capable)
- Source: OpenAI API / HuggingFace

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Self-Debug (execution-only) | ~70% pass@1 | HumanEval |
| Self-Refine | Iterative improvement baseline | Various |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Static analyzers produce meaningful warnings on LLM-generated code | LLM code likely has similar issues to human code | No signal to add; intervention is null |
| A2 | LLMs can interpret static warnings and translate to fixes | LLMs understand natural language error descriptions | Warnings add noise, possibly decreasing pass@k |
| A3 | Static and execution feedback catch non-overlapping error classes | Static catches potential issues; execution catches actual failures | Static is redundant; no improvement expected |
| A4 | HumanEval/MBPP contain problems with static-detectable errors | Common error types include undefined variables, type issues | Improvement limited to subset; effect size reduced |
| A5 | Pylint severity filtering reduces false positives effectively | Error/warning categories are higher precision than conventions | Signal-to-noise ratio too low; intervention ineffective |

### 1.6 Research Gap & Novelty

**Gap:** No prior study has measured static analysis impact on functional correctness (pass@k) in iterative LLM code repair.

**Novelty:**
- First study to measure static analysis impact on pass@k (vs. quality metrics)
- Combining static analysis with execution feedback in iterative repair
- Key differentiation from Blyth et al. (quality metrics only), Self-Debug (execution-only), and Self-Refine (general LLM feedback)

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| h-e1 | EXISTENCE | MUST_WORK | None | READY |
| h-m1 | MECHANISM | MUST_WORK | h-e1 | READY |
| h-m2 | MECHANISM | MUST_WORK | h-m1 | READY |
| h-m3 | MECHANISM | SHOULD_WORK | h-m2 | READY |

---

### 2.2 Hypothesis Specifications

#### H-E1: Static Analyzer Signal Existence

**Type:** EXISTENCE
**Statement:** Under the condition of LLM-generated code on HumanEval, if pylint/mypy is run on the code, then ≥30% of solutions will have at least one warning/error, because LLM-generated code contains patterns detectable by static analysis.

**Variables:**
- IV: Running pylint/mypy on LLM code
- DV: Fraction of solutions with ≥1 warning
- CV: Pylint configuration (severity filter), HumanEval problems, base LLM

**Success Criteria:**
- ≥30% of baseline solutions have static warnings
- Warnings are non-trivial (not just style)

**Gate:**
- Type: MUST_WORK
- If Fail: Entire hypothesis invalid—no signal to add

**Prerequisites:** None

**Verification Protocol:**
1. Generate baseline solutions for all 164 HumanEval problems using GPT-4
2. Run pylint (error+warning severity) on each solution
3. Count solutions with ≥1 warning
4. Calculate fraction and categorize warning types

---

#### H-M1: Warning Interpretability by LLM

**Type:** MECHANISM
**Statement:** Under the condition of receiving static warnings, if LLM is provided pylint output with code, then it can generate fixes that resolve the specific warnings, because LLM understands natural language error descriptions.

**Variables:**
- IV: Providing pylint warnings vs no warnings
- DV: Warning resolution rate (% of warnings fixed)
- CV: Same LLM, same problems, standardized prompt format

**Success Criteria:**
- ≥60% of static warnings resolved after one repair iteration
- Repairs are targeted (don't break existing tests)

**Gate:**
- Type: MUST_WORK
- If Fail: Mechanism step 2 invalid—LLM cannot use static signals

**Prerequisites:** h-e1

**Verification Protocol:**
1. Select 50 solutions with static warnings (from H-E1 pilot)
2. Provide warnings to LLM with repair prompt
3. Run pylint on repaired code
4. Measure warning resolution rate

---

#### H-M2: Non-Redundant Signal

**Type:** MECHANISM
**Statement:** Under the condition of iterative repair, if static warnings exist, then they identify errors that execution feedback alone misses (different error class), because static analysis catches potential issues before runtime.

**Variables:**
- IV: Error detection source (static vs execution)
- DV: Overlap coefficient between error types
- CV: Same problems, same solutions, same repair budget

**Success Criteria:**
- ≤50% overlap between static-detected and execution-detected errors
- Static catches ≥1 unique error type (undefined var, type mismatch)

**Gate:**
- Type: MUST_WORK
- If Fail: Static feedback redundant—no value added

**Prerequisites:** h-m1

**Verification Protocol:**
1. Categorize errors by source (static-only, execution-only, both)
2. Calculate overlap coefficient
3. Identify unique error types caught by each source

---

#### H-M3: Targeted Repair Effectiveness

**Type:** MECHANISM
**Statement:** Under the condition of having non-redundant static signals, if LLM repairs using static+execution feedback, then repairs are more targeted than execution-only, because mechanistic explanations (why) enable better fixes than location-only (where).

**Variables:**
- IV: Feedback type (static+exec vs exec-only)
- DV: Repair efficiency (pass@k per iteration)
- CV: Same LLM, same problems, same iteration budget

**Success Criteria:**
- Fewer iterations needed to reach same pass@k
- Higher delta-pass@k per iteration in static+exec condition

**Gate:**
- Type: SHOULD_WORK
- If Fail: Mechanism complete but effect size small

**Prerequisites:** h-m2

**Verification Protocol:**
1. Run both conditions on 50-problem subset
2. Track pass@k after each iteration (1-5)
3. Compare convergence curves

---

## 3. Execution

### 3.1 Dependency Chain
```
h-e1 → h-m1 → h-m2 → h-m3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| h-e1 | MUST_WORK | ≥30% solutions with warnings | Terminate: no signal |
| h-m1 | MUST_WORK | ≥60% warning resolution | Terminate: mechanism broken |
| h-m2 | MUST_WORK | ≤50% error overlap | Terminate: redundant |
| h-m3 | SHOULD_WORK | Faster convergence | Continue: smaller effect |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1 | h-e1 | 1-2 days |
| Phase 2 | h-m1 | 1-2 days |
| Phase 3 | h-m2 | 1-2 days |
| Phase 4 | h-m3 | 2-3 days |

**Total Duration:** 5-9 days (pilot), full experiment adds 1-2 weeks

---

## 4. Risk Analysis

### 4.1 Identified Risks

| Risk | Probability | Impact | Hypothesis Affected |
|------|-------------|--------|---------------------|
| R1: Few static warnings on LLM code | Medium | Critical | h-e1 |
| R2: LLM cannot interpret warnings | Low | High | h-m1 |
| R3: Static/execution fully overlap | Medium | High | h-m2 |
| R4: Small effect size (<2%) | High | Medium | h-m3 |
| R5: Model-specific effects | Medium | Medium | All |

### 4.2 Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| R1 | Pilot on 50 problems first; adjust severity filter if needed |
| R2 | Use simplified warning format; test on subset |
| R3 | Analyze error categories systematically |
| R4 | Pre-register minimum effect size; consider practical significance |
| R5 | Test on both GPT-4 and open-source model |

---

## 5. Dependency Graph (DAG)

```
┌──────────────────────────────────────────────────────────────┐
│                    VERIFICATION DAG                          │
└──────────────────────────────────────────────────────────────┘

                    ┌─────────┐
                    │  h-e1   │  ← EXISTENCE (Signal exists?)
                    │MUST_WORK│
                    └────┬────┘
                         │
                         ▼
                    ┌─────────┐
                    │  h-m1   │  ← MECHANISM (LLM interprets?)
                    │MUST_WORK│
                    └────┬────┘
                         │
                         ▼
                    ┌─────────┐
                    │  h-m2   │  ← MECHANISM (Non-redundant?)
                    │MUST_WORK│
                    └────┬────┘
                         │
                         ▼
                    ┌─────────┐
                    │  h-m3   │  ← MECHANISM (Effective repairs?)
                    │SHOULD   │
                    └─────────┘

Legend:
  MUST_WORK  = Fail terminates chain
  SHOULD     = Fail reduces confidence but continues
```

### 5.1 Execution Order
1. **h-e1** (no dependencies)
2. **h-m1** (requires h-e1 PASS)
3. **h-m2** (requires h-m1 PASS)
4. **h-m3** (requires h-m2 PASS)

---

## 6. Gantt Timeline

```
Week 1                    Week 2                    Week 3
├─────────────────────────┼─────────────────────────┼──────────────
│ h-e1 ████               │                         │
│      ↓                  │                         │
│      h-m1 ████          │                         │
│           ↓             │                         │
│           h-m2 ████     │                         │
│                ↓        │                         │
│                h-m3 ████████                      │
│                                                   │
│ ─────────── PILOT PHASE ──────────                │
├───────────────────────────────────────────────────┼──────────────
│                         │ FULL EXPERIMENT (Phase 5)│ ANALYSIS
│                         │ ████████████████████████│ █████████
```

### 6.1 Critical Path
h-e1 → h-m1 → h-m2 → h-m3 (all sequential, no parallelism possible)

### 6.2 Resource Summary
- **Compute:** GPT-4 API calls (~164 × 5 iterations × 2 conditions)
- **Human:** ~2-3 hours setup, 1 hour per checkpoint review
- **Risk buffer:** +2 days for R1 mitigation if triggered

---

## 7. Dialectical Analysis

### 7.1 Thesis
Static analysis feedback combined with execution feedback improves pass@k in iterative LLM code repair because:
1. Static analyzers provide mechanistic error explanations (why, not just where)
2. Static analysis catches errors before execution (early signal)
3. Different error classes caught (non-redundant information)

### 7.2 Antithesis (H0 Defense)
The null hypothesis (no improvement) could hold because:
1. **Redundancy:** Most static warnings may overlap with execution errors
2. **Noise:** False positives may confuse LLM more than help
3. **Baseline strength:** Strong LLMs may already infer static-like reasoning
4. **Benchmark bias:** HumanEval may have few static-detectable errors

### 7.3 Synthesis
The dialectical tension can be resolved through:
1. **Empirical pilot:** H-E1 directly tests signal existence (addresses #4)
2. **Overlap analysis:** H-M2 quantifies redundancy (addresses #1)
3. **Severity filtering:** A5 controls noise (addresses #2)
4. **Model comparison:** Testing on both strong/weak models (addresses #3)

### 7.4 Robustness Assessment
- **Strength:** Clear falsifiability at each step; pilot before full commitment
- **Weakness:** Effect size may be small even if mechanism works
- **Recommendation:** Pre-register minimum meaningful effect (2% absolute or 5% relative)

---

## 8. Executive Summary

### Key Findings
- **4 sub-hypotheses** defined (1 existence, 3 mechanism)
- **3 MUST_WORK gates** create clear termination points
- **5-9 day pilot** validates mechanism before full experiment
- **33% scope reduction** from established facts (quality metrics BUILD_ON)

### Decision Points
1. After H-E1: If <30% solutions have warnings → terminate
2. After H-M1: If LLM cannot resolve warnings → terminate
3. After H-M2: If signals fully redundant → terminate
4. After H-M3: If effect small → proceed to Phase 5 with adjusted expectations

### Next Steps
1. Phase 2C: Design detailed experiment for H-E1
2. Execute H-E1 pilot (50-problem subset)
3. Gate check before proceeding to H-M1

---

## Appendix A: Established Facts (BUILD_ON)

| Claim | Status | Evidence |
|-------|--------|----------|
| Static analysis improves code quality metrics | BUILD_ON | Blyth et al. (arXiv:2508.14419) |
| Self-Debug execution-only loops improve pass@k | BUILD_ON | Self-Debug paper |

These claims are accepted baselines—not re-tested in Phase 4.

---

## Appendix B: Phase 5 Comparison Scope

The baseline comparison (H-CP hypotheses) is deferred to Phase 5:
- H-CP1: Static+exec vs execution-only on full HumanEval (164 problems)
- H-CP2: Effect stratification by warning presence

Phase 4 focuses on mechanism validation (does it work?), Phase 5 on magnitude (how much better?).
