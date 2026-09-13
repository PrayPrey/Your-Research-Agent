# Verification Plan: Actionable Specificity in LLM Code Repair

**Date:** 2026-08-19
**Hypothesis ID:** H-ActionableSpec-v1
**Confidence:** 0.80
**Total Hypotheses:** 5

---

## Executive Summary

**Main Hypothesis:** Under LLM-based iterative code repair on standard benchmarks, if verification signals provide higher Actionable Specificity—decomposed into AS_loc, AS_state, and AS_causal—then single-attempt repair success rates increase.
- ID: H-ActionableSpec-v1, Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points

**Risk Assessment:** Medium
- Primary concerns: AS component independence, LLM context limits

**Immediate Action:** Begin Phase 1 with H-E1

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under LLM-based iterative code repair on standard benchmarks (HumanEval, MBPP), if verification signals provide higher Actionable Specificity—decomposed into Localization (AS_loc), State Exposure (AS_state), and Causal Context (AS_causal)—then single-attempt repair success rates increase, because informationally richer feedback enables the model to localize bugs and infer correct fixes.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in repair success rates between verification signal types when controlling for error category. Repair success is determined solely by error category, and AS components have no predictive power (β_loc = β_state = β_causal = 0).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval + MBPP (standard) | Standard code generation benchmarks with test oracles for automated pass@k evaluation |
| **Model** | GPT-4 / Claude 3.5 Sonnet | State-of-the-art models with demonstrated code repair capability |

**Dataset Details:**
- Source: openai/human-eval, google-research/mbpp
- Path: https://github.com/openai/human-eval, https://github.com/google-research/google-research/tree/master/mbpp
- Total problems: 664 (HumanEval: 164, MBPP: 500)

**Model Details:**
- Type: LLM
- Source: OpenAI API / Anthropic API

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Single-shot generation | Baseline pass@1 | HumanEval |
| Error message only (C4) | Standard error message without trace | Various |
| Static analysis (C5) | mypy/pylint output only | Various |
| Best reported (CodeCoR) | 77.13% Pass@1 multi-agent | HumanEval |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | AS components are independently measurable from signal text | Localization (regex for file:line), state exposure (count variables), causal context (count trace lines) | Cannot operationalize AS; must fall back to categorical signal types |
| A2 | LLMs can effectively use AS information when present | DebugRepair [2026], TyFlow [2025] demonstrate LLM use of structured feedback | Hypothesis false—AS has no effect |
| A3 | Error category confound can be controlled via stratification | Standard statistical practice; mixed-effects models handle nested structure | Cannot isolate AS effect from error difficulty |
| A4 | Single-attempt success is meaningful metric | Debugging Decay [2025] shows 60-80% loss after 2-3 attempts | Need to emphasize multi-attempt survival analysis instead |
| A5 | Results generalize across LLM models | Partial—prior work uses various models with similar patterns | Report model-specific coefficients, acknowledge generalization limits |

### 1.6 Research Gap & Novelty

**Gap:** Prior work measured WHICH signals work (DebugRepair: traces > messages; TyFlow: types help) but did not explain WHY.

**Novelty:** First systematic decomposition of feedback effectiveness into measurable components (AS_loc, AS_state, AS_causal). The Actionable Specificity framework quantifies WHY signals work, enabling prediction of new signal type effectiveness.

**Scope Reduction:** 83% (5 BUILD_ON claims from prior work, 1 PROVE_NEW claim for AS decomposition)

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
**H-E1: AS Components Are Measurable**

**Statement:** Under standard verification signal generation, if we apply AS decomposition rules (file:line extraction, variable counting, trace depth measurement), then AS_loc, AS_state, and AS_causal can be independently computed for each signal type, because these are observable text features.

**Rationale:** The AS framework requires that its components be operationalizable. Without independent measurement, the hypothesis cannot be tested. This validates the framework's foundation before testing predictive power.

**Variables:**
- Independent: Verification signal text (6 conditions: C1-C6)
- Dependent: AS_loc (binary), AS_state (count), AS_causal (count)
- Controlled: Signal generation method (pytest, Python trace module)

**Verification Protocol:**
1. Generate 100 failing test cases across HumanEval/MBPP
2. For each failure, generate all 6 signal variants (C1-C6)
3. Apply AS extraction rules: regex for file:line, count exposed variables, count trace depth
4. Verify inter-rater reliability (automated extraction matches manual annotation)
5. Confirm AS values vary systematically across signal types

**Success Criteria (PoC: Direction-based):**
- Primary: AS components can be extracted from ≥95% of signals
- Secondary: AS values show expected ordering (C1 > C2 > C3 > C4 on all components)

**Failure Response:**
- IF fails: PIVOT to categorical signal comparison only (abandon AS decomposition)

**Dependencies:** None

**Source:** Phase 2A SH1 (Existence)

---

---
**H-M1: Signal Generation Produces Controlled AS Levels**

**Statement:** Under test execution with Python trace module, if we implement 6 signal generation variants (C1-C6), then each variant produces signals with predictable AS levels, because trace truncation/masking systematically reduces available information.

**Rationale:** This validates the experimental manipulation. If signal variants don't produce controlled AS differences, the main experiment cannot isolate AS effects.

**Variables:**
- Independent: Signal variant (C1: full trace, C2: truncated, C3: value-masked, C4: error message, C5: static analysis, C6: syntax error)
- Dependent: Measured AS levels (AS_loc, AS_state, AS_causal)
- Controlled: Same failing code, same test case

**Verification Protocol:**
1. Implement signal generation pipeline for all 6 variants
2. Run on 500+ failing test cases (full MBPP test set)
3. Measure AS components for each generated signal
4. Verify ordering: C1 > C2 > C3 > C4 on AS_state and AS_causal
5. Confirm C5 (static) has AS_loc=1, AS_state=0, AS_causal=0

**Success Criteria (PoC: Direction-based):**
- Primary: Mean AS_state(C1) > AS_state(C2) > AS_state(C3) > AS_state(C4)
- Secondary: Variance within condition < variance between conditions

**Failure Response:**
- IF fails: EXPLORE alternative signal generation methods

**Dependencies:** H-E1

**Source:** Phase 2A Causal Step 1

---

---
**H-M2: LLM Parses AS Information from Signals**

**Statement:** Under LLM processing of verification signals, if signals contain AS information (localization, state, causal context), then the LLM's repair attempt reflects use of that information, because LLMs can process structured error feedback.

**Rationale:** This tests whether AS information is actually used, not just present. Prior work (DebugRepair, TyFlow) established LLMs can use structured feedback; we verify this holds for our signal variants.

**Variables:**
- Independent: Signal AS level (high/low)
- Dependent: Repair attempt quality (targets correct location, uses correct values)
- Controlled: Same original bug, same LLM (GPT-4, temp=0)

**Verification Protocol:**
1. Sample 100 failing cases with known bug locations
2. Generate high-AS (C1) and low-AS (C4) signals for each
3. Prompt LLM with each signal, collect repair attempts
4. Analyze repair attempts: does high-AS lead to correct location targeting?
5. Compare repair precision (correct line targeted) between conditions

**Success Criteria (PoC: Direction-based):**
- Primary: Location precision(C1) > Location precision(C4)
- Secondary: Repairs using variable values appear more in C1 than C4

**Failure Response:**
- IF fails: EXPLORE whether LLM context length limits AS utilization

**Dependencies:** H-M1

**Source:** Phase 2A Causal Step 2

---

---
**H-M3: Higher AS Enables Better Bug Localization**

**Statement:** Under repair attempts with varying AS levels, if AS is higher (more localization, state, causal context), then bug localization accuracy increases, because additional information narrows the search space.

**Rationale:** This is the core mechanism link. AS must improve localization for the full hypothesis chain to hold. If localization doesn't improve, the final repair success link breaks.

**Variables:**
- Independent: AS level (continuous: AS_loc + AS_state + AS_causal composite)
- Dependent: Bug localization accuracy (correct file, correct function, correct line)
- Controlled: Error category, problem difficulty (random effect)

**Verification Protocol:**
1. Use 500+ failing cases with ground-truth bug locations
2. Generate repair attempts under all 6 signal conditions
3. Measure localization accuracy at each AS level
4. Fit logistic regression: P(correct_location) ~ AS_loc + AS_state + AS_causal
5. Test: at least one β coefficient > 0 with p < 0.05

**Success Criteria (PoC: Direction-based):**
- Primary: At least one β > 0 with p < 0.05 (AS predicts localization)
- Secondary: Full model outperforms null model (likelihood ratio test)

**Failure Response:**
- IF fails: PIVOT to error-category-specific analysis (AS may work only for some categories)

**Dependencies:** H-M2

**Source:** Phase 2A Causal Step 3

---

---
**H-M4: Higher AS Leads to Higher Repair Success**

**Statement:** Under single-attempt repair with varying AS levels, if AS is higher, then repair success rate increases, because better localization enables correct fixes.

**Rationale:** This is the ultimate dependent variable. All prior mechanism steps must hold for this prediction to be supported.

**Variables:**
- Independent: AS level (continuous composite or categorical by condition)
- Dependent: Single-attempt repair success (binary: all tests pass)
- Controlled: Error category, problem difficulty, LLM model

**Verification Protocol:**
1. Run full experiment: 664 problems × 6 conditions = 3984 trials (minimum)
2. For each trial: generate signal, prompt LLM, execute repair, run tests
3. Record success/failure for each trial
4. Fit mixed-effects logistic regression with AS predictors
5. Test P1: likelihood ratio test full model vs error-category-only

**Success Criteria (PoC: Direction-based):**
- Primary: Likelihood ratio test p < 0.05 (AS adds predictive power)
- Secondary: C1 outperforms C4 by ≥5pp on assertion errors (P2)

**Failure Response:**
- IF fails: Document which AS components failed, report negative result

**Dependencies:** H-M3

**Source:** Phase 2A Causal Step 4

---

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | AS components extractable from ≥95% signals | STOP: AS framework invalid |
| H-M1 | MUST_WORK | Signal variants produce ordered AS levels | STOP: Manipulation failed |
| H-M2 | SHOULD_WORK | LLM uses high-AS info for localization | Document limitation |
| H-M3 | SHOULD_WORK | AS predicts localization (β > 0, p < 0.05) | Document limitation |
| H-M4 | SHOULD_WORK | AS predicts repair success (LRT p < 0.05) | Document negative result |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4 | 4 weeks |

**Total Duration:** 6 weeks

---

## 4. Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1 - Mechanism]
    H-M1 ← H-E1
         │
         ▼
[Level 2 - Mechanism]
    H-M2 ← H-M1
         │
         ▼
[Level 3 - Mechanism]
    H-M3 ← H-M2
         │
         ▼
[Level 4 - Mechanism]
    H-M4 ← H-M3

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 4.1 Verification Phases with Gates

**Phase 1 - Foundation** (2 weeks)
| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | AS component measurability | MUST PASS |

→ **Gate 1**: If H-E1 fails → STOP, AS framework invalid.

**Phase 2 - Core Mechanisms** (4 weeks)
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST PASS |
| H-M2 | H-M1 | Should pass |
| H-M3 | H-M2 | Should pass |
| H-M4 | H-M3 | Should pass |

→ **Gate 2**: H-M1 must pass. Later H-M failures = document limitation.

### 4.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

---

## 5. Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2 │ W3   │ W4   │ W5   │ W6   │
─────────────────┼──────┼──────┼──────┼──────┼──────┤
PHASE 1: Foundation
  H-E1           │██████│      │      │      │      │
  [Gate 1]       │     ◆│      │      │      │      │
─────────────────┼──────┼──────┼──────┼──────┼──────┤
PHASE 2: Mechanisms
  H-M1           │      │██████│      │      │      │
  H-M2           │      │      │██████│      │      │
  H-M3           │      │      │      │██████│      │
  H-M4           │      │      │      │      │██████│
  [Gate 2]       │      │      │      │      │     ◆│
═══════════════════════════════════════════════════════════════════
Legend: ██████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.1 Critical Path Analysis

- **Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4
- **Total Duration:** 6 weeks (2 + 4)
- **Slack Available:** 0 weeks (fully sequential)

### 5.2 Resource Summary

- **Total Hypotheses:** 5
  - Existence: 1 (H-E1)
  - Mechanism: 4 (H-M1 to H-M4)
- **Verification Phases:** 2
- **Execution Mode:** Sequential chain
- **Estimated API Cost:** $50-100 (4000+ trials)
- **Compute Time:** 2-3 days

---

## 6. Risk Analysis

### 6.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: AS not independently measurable | A1 | H-E1, All | Critical |
| R2: LLM cannot use AS information | A2 | H-M2, H-M3, H-M4 | High |
| R3: Error category confound | A3 | H-M3, H-M4 | Medium |
| R4: Single-attempt metric insufficient | A4 | H-M4 | Medium |
| R5: Results model-specific | A5 | All | Low |

### 6.2 Mitigation Strategies

**R1: AS Not Independently Measurable (Critical)**
- **Prevention:** Use simple, objective extraction rules (regex, counting)
- **Detection:** Check inter-rater reliability in H-E1
- **Response:**
  - PIVOT: Fall back to categorical signal comparison (C1 vs C4 vs C6)
  - SCOPE: Report "signals differ" without mechanistic explanation

**R2: LLM Cannot Use AS Information (High)**
- **Prevention:** Use established prompt patterns from DebugRepair/TyFlow
- **Detection:** Analyze repair attempts for information usage in H-M2
- **Response:**
  - EXPLORE: Try different prompt formats
  - SCOPE: Report which AS components are utilized

**R3: Error Category Confound (Medium)**
- **Prevention:** Stratified analysis by error category
- **Detection:** Check for category×AS interactions
- **Response:**
  - SCOPE: Report category-specific effects
  - PIVOT: Focus on categories where AS has effect

**R4: Single-Attempt Metric Insufficient (Medium)**
- **Prevention:** Also collect multi-attempt data (up to 3)
- **Detection:** Compare single vs multi-attempt patterns
- **Response:**
  - SCOPE: Add survival analysis as secondary metric

**R5: Results Model-Specific (Low)**
- **Prevention:** Test with 2 models (GPT-4, Claude 3.5)
- **Detection:** Compare coefficients across models
- **Response:**
  - SCOPE: Report model-specific coefficients

### 6.3 Risk Summary

| ID | Risk | Severity | Likelihood | Mitigation |
|----|------|----------|------------|------------|
| R1 | AS measurement | Critical | Low | Objective extraction rules |
| R2 | LLM usage | High | Low | Established prompt patterns |
| R3 | Confound | Medium | Medium | Stratified analysis |
| R4 | Metric | Medium | Low | Multi-attempt backup |
| R5 | Generalization | Low | Medium | Multi-model testing |

---

## 7. Dialectical Analysis

### 7.1 Thesis

**Core Claim:** Actionable Specificity (AS) decomposes feedback effectiveness into measurable components (AS_loc, AS_state, AS_causal) that predict single-attempt repair success.

**Supporting Evidence:**
1. DebugRepair [2026] shows traces outperform error messages
2. TyFlow [2025] shows structured type info improves correctness
3. Debugging Decay [2025] shows 60-80% capability loss after 2-3 attempts

**Strengths:**
- Clear causal mechanism with 4 testable steps
- Operationalizable variables (objective extraction rules)
- Falsifiable predictions (β coefficients, p-values)

**Expected Outcomes:**
- P1: AS predicts repair success (LRT p < 0.05)
- P2: C1 > C4 by ≥5pp on assertion errors
- P3: C3 > C6 by ≥5pp (structure helps)
- P4: Optimal trace length exists (β_AS² < 0)

### 7.2 Antithesis

**Null Hypothesis (H0):** Repair success is determined solely by error category. AS components have no predictive power (β_loc = β_state = β_causal = 0).

**Counter-Arguments:**
1. Error category may dominate: syntax errors are easy regardless of signal
2. LLM context limits may prevent full trace utilization
3. Information overload: too much trace may hurt, not help

**Potential Failure Points:**
- H-E1: AS extraction rules may not generalize to all signal types
- H-M2: LLM may ignore additional AS information
- H-M4: Effect size may be too small to detect with available power

**Conditions Under Which H0 Would Be Supported:**
- If likelihood ratio test p > 0.05 (full model no better than category-only)
- If all β coefficients ≈ 0
- If C1 ≈ C4 on assertion errors (no trace advantage)

### 7.3 Synthesis

**Balanced Assessment:**

The hypothesis H-ActionableSpec-v1 presents a testable claim that AS decomposition explains feedback effectiveness. However, H0 raises valid concerns: error category may dominate, and LLM context limits could prevent AS utilization.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes AS measurability before testing effects
2. **Sequential mechanism testing (H-M1-M4):** Tests each causal link independently
3. **Gate conditions:** Allow early detection of H0 support at each step

**Conditions for Thesis Support:**
- All MUST_WORK gates pass (H-E1, H-M1)
- Likelihood ratio test p < 0.05
- At least one β > 0 with p < 0.05

**Conditions for Antithesis Support:**
- H-E1 fails (AS not measurable)
- H-M1 fails (signal variants don't produce controlled AS)
- All β ≈ 0 in final regression

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → AS framework validated
2. **Partial Support:** Some H-M fail → Refined thesis with scope limits
3. **No Support:** H-E1 or H-M1 fail → AS framework invalid

### 7.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | AS is measurable | May be artifact | H-E1 test |
| Mechanism | Causal chain valid | Alternative explanations | H-M1-M4 tests |
| Scope | Applies to all errors | Category-specific | Stratified analysis |
| Performance | AS predicts success | Marginal effect | 4000+ trials for power |

**Overall Robustness Score:** High

**Confidence in Verification Plan:** 0.80

---

## 8. Conclusions

### 8.1 Key Achievements

- 5 hypotheses across 2 phases (6 weeks)
- H0 addressed: β_loc = β_state = β_causal = 0 as null
- Clear falsification criteria at each step

### 8.2 Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: AS component measurability
- Gate 1: MUST PASS

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: Signal generation produces controlled AS levels
- H-M2: LLM parses AS information
- H-M3: Higher AS enables better localization
- H-M4: Higher AS leads to higher repair success
- Gate 2: H-M1 must pass

### 8.3 Critical Decision Points

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, AS framework invalid
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - CRITICAL FAIL → Execute failure response
   - OPTIONAL FAIL → Document limitation

### 8.4 Open Questions

- Exact regression coefficients for AS components (empirical finding)
- Whether optimal trace length exists (P4)
- Generalization across LLM models

### 8.5 Recommendations

1. **Immediate Actions:**
   - Start Phase 1 with H-E1
   - Implement signal generation pipeline for 6 variants
   - Set up evaluation infrastructure (pytest, trace module)

2. **Resource Allocation:**
   - Allocate 6 weeks for critical path
   - Reserve $100 API budget
   - Plan for 4000+ experimental trials

3. **Failure Management:**
   - Document all failures with full context
   - Execute PIVOT strategies at each gate
   - Report negative results if H0 supported

---

## Appendices

### A. Phase 2A Reference

- **Source:** 03_refinement.yaml (ID: H-ActionableSpec-v1)
- **Synthesis:** 02_synthesis.yaml
- **Round Table:** 01_round_table/final_opinions.yaml

### B. MCP Tool Usage Summary

- **Total MCP calls:** 2
- **Tools:** scientificmethod (hypothesis + experiment stages)

### C. Established Facts (BUILD ON)

| Claim | Status | Evidence |
|-------|--------|----------|
| Self-repair improves HumanEval pass rates by 4.9-17.1pp | BUILD_ON | How Many Tries [2026] |
| Assertion errors have lowest repair success (~45%) | BUILD_ON | How Many Tries [2026] |
| Runtime traces outperform error messages | BUILD_ON | DebugRepair [2026] |
| Type constraints improve functional correctness | BUILD_ON | TyFlow [2025] |
| 60-80% capability loss after 2-3 attempts | BUILD_ON | Debugging Decay [2025] |

### D. Variables Quick Reference

| Variable | Type | Operationalization |
|----------|------|-------------------|
| Verification Signal Type | IV (categorical) | 6 conditions: C1-C6 |
| AS_loc | IV (binary) | 1 if file:line provided |
| AS_state | IV (continuous) | Count of exposed variable values |
| AS_causal | IV (continuous) | Trace depth (execution steps) |
| Single-Attempt Repair Success | DV (binary) | 1 if passes all tests |
| Error Category | CV (categorical) | syntax, type, runtime, logic |

---

**Document Status:** Complete
**Generated:** 2026-08-19
**Workflow:** Phase 2B Planning (UNATTENDED mode)
