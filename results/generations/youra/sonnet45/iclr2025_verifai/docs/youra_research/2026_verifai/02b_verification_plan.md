# Verification Plan: Sequential Single-Source Feedback Routing

**Date:** 2026-03-18
**Hypothesis ID:** H-SeqRouting-v1
**Confidence:** 0.80
**Total Sub-Hypotheses:** 5

---

## Executive Summary

**Main Hypothesis:** Under programming tasks requiring compositional verification, if LLM code generation uses sequential single-source feedback routing (static analysis → execution), then iteration-to-solution count decreases relative to simultaneous multi-source aggregation, because staged verification enforces attention economy and computational efficiency.

**Verification Structure:**
- Mode: Incremental (Phase 2A pre-mapped)
- Sub-Hypotheses: 5 total (H-E1, H-M1-3, H-C1)
- Phases: 3 phases over 6 weeks
- Critical Gates: 2 MUST_WORK, 3 SHOULD_WORK

**Risk Assessment:** Medium
- Primary concerns: Pilot variance exceeds SD=1.0, mypy error detection <20%

**Immediate Action:** Begin Phase 2C with H-E1 experiment design

---

## 1. Main Hypothesis & Context

### 1.1 Core Statement

Under programming tasks requiring compositional verification (type safety + logical correctness validation), if LLM code generation uses sequential single-source feedback routing (static analysis → execution, one source per iteration), then iteration-to-solution count decreases relative to simultaneous multi-source aggregation (both sources concatenated each iteration), because staged verification enforces attention economy (single-source focus) and computational efficiency (skip execution if static analysis fails).

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in mean iterations-to-solution between sequential routing and simultaneous aggregation conditions on dual-sensitive programming tasks.

### 1.3 Experimental Setup

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval with HumanEval+ augmented tests (standard) | 164 tasks, 80+ robustness tests per task, classification-evaluation decoupling |
| **Model** | CodeLlama-7B (Base 7B parameters) | Widely used baseline, <30min inference, tests feedback routing not instruction-following |

**Dataset Details:**
- Source: evalplus Python package (pip install evalplus)
- Path: Built-in task loader

**Model Details:**
- Type: Base code generation model
- Source: HuggingFace: codellama/CodeLlama-7b-hf

### 1.4 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | K=20 classification correlates with HumanEval+ | HumanEval+ 80+ tests per task | >30% failures → scope narrows |
| A2 | Paired variance SD ≤ 1.0 | PerfCodeGen σ ≈ 1.0 reported | Power collapses → underpowered |
| A3 | LLMs normalize feedback differently | Context-window constraints | Null result → routing adds no value |
| A4 | Mypy errors sufficiently informative | Mypy structured JSON output | Cascade struggles → aggregation helps |
| A5 | Token caps don't favor condition | 1000/source/iter equality enforced | Truncation biases results |

### 1.5 Research Gap & Novelty

**Gap:** No prior work demonstrates systematic orchestration of multiple feedback sources for LLM code generation. All 22 directly relevant sources (Phase 1) use single feedback type only.

**Novelty:** First empirical test of feedback routing policy causality via cascade-aggregation ablation. Gating Index provides quantitative mechanism probe. Pre-registered task classification with HumanEval+ decoupling ensures methodological rigor.

**Differentiation:**
- vs LLMDebugger: We test orchestration of static + execution, not just execution depth
- vs PerfCodeGen: They optimize performance; we test correctness with compositional guarantees
- vs LLMLOOP: They use all sources simultaneously (aggregation); we test routing policy
- vs AutoSafeCoder: We isolate routing vs. aggregation with explicit ablation

---

## 2. Sub-Hypotheses Inventory

| ID | Type | Gate | Prerequisites | Statement (Brief) |
|----|------|------|---------------|-------------------|
| H-E1 | EXISTENCE | MUST_WORK | None | N≥20 dual-sensitive tasks exist with SD≤1.0 pilot variance |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | Mypy catches ~30-40% errors instantly (zero execution cost) |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | Sequential presentation reduces iterations via attention economy |
| H-M3 | MECHANISM | SHOULD_WORK | H-M1 | Conditional gating maintains token efficiency (≤15% overhead) |
| H-C1 | CONDITION | SHOULD_WORK | H-M1,H-M2,H-M3 | Cascade advantage scoped to 7B base models |

---

## 3. Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1 - Foundation Mechanism]
    H-M1 ← H-E1
         │
         ▼
[Level 2 - Core Mechanisms]
    H-M2 ← H-M1
    H-M3 ← H-M1
         │
         ▼
[Level 3 - Boundary Conditions]
    H-C1 ← H-M1, H-M2, H-M3

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-C1
Total Depth: 4 levels
═══════════════════════════════════════════════════════════
```

---

## 4. Timeline & Execution Order

```
═══════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 6 Weeks Total
═══════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3-4    │ W5      │ W6      │
─────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1           │ ████████│         │         │         │
  [Gate 1]       │         │ ◆       │         │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms
  H-M1           │         │ ████████│         │         │
  H-M2           │         │         │ ████    │         │
  H-M3           │         │         │ ████    │         │
  [Gate 2]       │         │         │     ◆   │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2.5: Conditions
  H-C1           │         │         │         │ ████    │
═══════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
═══════════════════════════════════════════════════════════
```

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-C1 (all sequential)
**Total Duration:** 6 weeks (2 foundation + 3 mechanisms + 1 condition)
**Slack Available:** 0 weeks (critical path covers all hypotheses)

---

## 5. Risk Analysis

### R1: Insufficient Dual-Sensitive Task Pool
**Source:** Assumption A1
**Affected Hypotheses:** H-E1, all downstream
**Severity:** CRITICAL
**Likelihood:** Low (HumanEval 164 tasks is large pool)
**Mitigation:**
- Prevention: Relax hard_threshold to 0.2 if N<20 with 0.0 threshold
- Detection: K=20 classification shows <20 qualifying tasks
- Response: STOP pipeline if even relaxed threshold yields N<20

### R2: Pilot Variance Exceeds Power Assumptions
**Source:** Assumption A2
**Affected Hypotheses:** H-M2 (primary), all mechanism tests
**Severity:** HIGH
**Likelihood:** Medium (PerfCodeGen reports σ≈1.0, but task-specific variance unknown)
**Mitigation:**
- Prevention: Pilot N=5 tasks with 2 seeds to estimate empirical SD before full N=20
- Detection: Pilot SD>1.0 indicates underpowered design
- Response: Downgrade to "underpowered exploratory," widen CI interpretation, temper claims

### R3: Static Analysis Low Error Detection Rate
**Source:** Assumption A4
**Affected Hypotheses:** H-M1 (blocks all downstream)
**Severity:** HIGH
**Likelihood:** Low (mypy provides compositional guarantees)
**Mitigation:**
- Prevention: Use mypy --strict mode with --json-output for structured errors
- Detection: Mypy catches <20% of errors in H-M1 validation
- Response: PIVOT to execution-first routing or ABANDON cascade hypothesis

### R4: LLMs Internally Normalize Feedback
**Source:** Assumption A3
**Affected Hypotheses:** H-M2 (core attention economy claim)
**Severity:** MEDIUM
**Likelihood:** Medium (untested assumption about LLM internal processing)
**Mitigation:**
- Prevention: None (inherent to hypothesis testing)
- Detection: Null result in H-M2 (CI spans zero, d<0.3)
- Response: Publishable negative finding - routing policies don't matter for this model size

### R5: Token Budget Asymmetry
**Source:** Assumption A5
**Affected Hypotheses:** H-M3 (efficiency claim)
**Severity:** LOW
**Likelihood:** Low (cap enforced equally, 1000 tokens/source generous)
**Mitigation:**
- Prevention: Monitor granular token breakdown (static vs execution vs response)
- Detection: Systematic truncation in one condition, unequal token usage patterns
- Response: Report token breakdown, acknowledge limitation if asymmetry detected

---

## 6. Gate Conditions

### Gate 1: Foundation (Week 2)
**Hypothesis:** H-E1
**Condition:** N≥20 dual-sensitive tasks AND pilot SD≤1.0
**If PASS:** Proceed to Phase 2 (H-M1)
**If FAIL:**
- N<20: Relax thresholds → retry → if still fail, STOP pipeline
- SD>1.0: Downgrade to underpowered exploratory, proceed with tempered claims

### Gate 2: Core Mechanisms (Week 5)
**Hypotheses:** H-M1 (MUST_WORK), H-M2 (SHOULD_WORK), H-M3 (SHOULD_WORK)
**Condition:** H-M1 mypy error detection ≥20%
**If H-M1 FAIL:** STOP or PIVOT (cascade loses primary justification)
**If H-M2/H-M3 FAIL:** Document limitation, proceed to H-C1 boundary documentation

---

## 7. Next Steps

1. **Phase 2C - Experiment Design:** Generate detailed experiment specifications for each hypothesis starting with H-E1
2. **Tooling:** `/phase2c-experiment-design` or `/hypothesis-next` skill
3. **Verification Order:** Execute hypotheses sequentially following dependency graph (H-E1 → H-M1 → H-M2 → H-M3 → H-C1)

---

*Generated by YouRA Phase 2B Planning | 2026-03-18T13:32:57Z*
*verification_state.yaml: 5 sub-hypotheses (1 READY, 4 NOT_STARTED)*
