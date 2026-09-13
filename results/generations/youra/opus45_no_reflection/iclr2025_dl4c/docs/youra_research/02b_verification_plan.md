# Verification Plan: Execution-Verified AI Feedback (EVAF)

**Date:** 2026-08-18
**Hypothesis ID:** H-EVAF-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under post-training alignment of code generation models using CodeT5-770M on HumanEval/MBPP benchmarks, if we apply Execution-Verified AI Feedback (EVAF)—where AI-generated code critiques are filtered through unit test execution before being used as training signals—then EVAF will achieve significantly higher pass@1 than pure execution feedback on problems where the baseline model primarily fails due to semantic errors (incorrect logic rather than syntax/runtime errors), because EVAF combines ground-truth verification (filtering out hallucinated AI suggestions) with rich semantic guidance (explaining WHY code is wrong), addressing the orthogonal dimensions of signal fidelity and semantic richness that neither pure approach satisfies alone.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in pass@1 between EVAF and Exec-Fine feedback strategies on semantic-error-prone code generation problems (OR = 1.0, 95% CI includes 1.0).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval (standard) | 164 problems with execution tests; widely used benchmark for code generation |
| **Model** | CodeT5-770M | Same model used by CodeRL and RLTF; enables direct comparison |

**Dataset Details:**
- Source: openai/human-eval
- Path: N/A (downloaded via evaluation harness)
- Secondary: MBPP (500 test), APPS (5000 test)

**Model Details:**
- Type: encoder-decoder
- Source: Salesforce/codet5-large (or RLTF checkpoint)

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| RLTF (Liu et al., 2023) | pass@1: 1.45 on APPS | APPS, MBPP | High fidelity but low semantic richness; doesn't explain why code fails |
| CodeRL (Le et al., 2022) | pass@1: 2.69 on APPS | APPS, MBPP | Episode-level rewards; less granular than RLTF |
| Self-Refine (Madaan et al., 2023) | +8.2% on code optimization | Various | Low fidelity (94% failures from bad feedback); test-time only |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Baseline error type distribution (syntactic vs semantic) is stable across training | Error types determined by problem structure, not model state | Stratification becomes invalid; need dynamic re-stratification |
| A2 | AI feedback errors are detectable via test execution (correctness-affecting) | Focus on functional correctness; style/design suggestions excluded | Verification cannot filter bad semantic suggestions about non-functional aspects |
| A3 | Filtered AI feedback volume is sufficient for learning (accept rate 20-60%) | Empirical; must monitor during training | EVAF degenerates to pure execution feedback if accept rate <10% |
| A4 | HumanEval/MBPP test suites are sufficient to catch regressions | Standard benchmarks; ~7 tests/problem average | False accepts lead to learning from incorrect AI suggestions |
| A5 | CodeT5-770M has sufficient capacity to benefit from richer feedback signals | RLTF shows gains with fine-grained feedback on same model | Smaller models may not have capacity to utilize semantic guidance |

### 1.6 Research Gap & Novelty

EVAF is a novel method that combines execution verification with AI feedback, achieving high fidelity and high semantic richness simultaneously. The key innovation is the **fidelity × richness decomposition**: execution and AI feedback are not competitors but operate along orthogonal dimensions. EVAF uses execution as a gating mechanism for AI feedback rather than as an alternative to it.

**Differentiation:**
- vs CodeRL/RLTF: Pure execution feedback lacks semantic richness
- vs Self-Refine: Pure AI feedback lacks fidelity guarantee (61% wrong fix rate)
- vs CodeT: Uses LLM-generated tests for ranking; doesn't use AI feedback for training

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Statement (Brief) | Gate | Prerequisites | Status |
|----|------|-------------------|------|---------------|--------|
| H-E1 | Existence | EVAF mechanism implementable with 20-60% accept rate | MUST_WORK | None | READY |
| H-M1 | Mechanism | AI feedback generator produces actionable suggestions | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | Execution gating correctly filters incorrect suggestions | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | Mechanism | Filtered feedback improves learning on semantic errors | SHOULD_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: EVAF Mechanism Existence

**Type:** EXISTENCE
**Statement:** Under implementation of the EVAF pipeline, if we apply AI-generated critiques filtered through unit test execution, then the system will achieve a measurable accept rate between 20-60%, because this range indicates selective filtering (neither accepting all nor rejecting all suggestions).

**Rationale:**
Before testing whether EVAF improves learning, we must verify the mechanism exists and operates selectively. An accept rate outside 20-60% would indicate either (a) AI feedback is nearly always wrong (<10%) making EVAF degenerate to pure execution, or (b) AI feedback is nearly always correct (>90%) making gating unnecessary.

**Variables:**
- Independent: EVAF pipeline implementation (AI feedback + execution gating)
- Dependent: Accept rate (fraction of AI suggestions passing execution verification)
- Controlled: AI feedback generator model, test harness, problem set

**Verification Protocol:**
1. Implement AI feedback generator using CodeLlama-Instruct on 164 HumanEval problems
2. For each problem with failing baseline code, generate AI critique
3. Apply AI suggestion tentatively and run unit tests
4. Record accept/reject decisions across all problems
5. Calculate overall accept rate and per-problem distribution

**Success Criteria (PoC: Direction-based):**
- Primary: Accept rate is between 20% and 60%
- Secondary: AI generates actionable suggestions for >80% of failing tests

**Failure Response:**
- IF fails (accept rate <10%): PIVOT to relaxed gating (accept if any test improves)
- IF fails (accept rate >90%): EXPLORE why AI is so accurate (may not need EVAF)

**Dependencies:** None

**Source:** Phase 2A SH1, Prediction P1 precondition

---

#### H-M1: AI Feedback Quality

**Type:** MECHANISM
**Statement:** Under the EVAF pipeline, if the AI feedback generator (CodeLlama-Instruct) processes failing code, then it will produce semantically rich suggestions with a measurable error rate (~40-60% incorrect), because AI models can explain code issues but hallucinate fixes.

**Rationale:**
This validates causal steps 1-2: AI generates rich critique AND some suggestions are incorrect. We need material to filter—if AI were perfect, gating would be unnecessary; if AI produced no actionable suggestions, EVAF would have nothing to work with.

**Variables:**
- Independent: AI feedback generator (CodeLlama-Instruct)
- Dependent: (a) Suggestion coverage (% of problems with actionable feedback), (b) Error rate (% of suggestions that fail tests)
- Controlled: Prompt template, temperature, problem set

**Verification Protocol:**
1. Run AI feedback generator on all failing baseline solutions
2. Parse generated suggestions into actionable code modifications
3. Classify suggestions: actionable vs non-actionable
4. For actionable suggestions, measure how many break tests (error rate)
5. Validate error rate is in expected range (40-60%)

**Success Criteria (PoC: Direction-based):**
- Primary: Error rate measurable and >30% (sufficient material to filter)
- Secondary: Coverage >70% (AI produces suggestions for most failures)

**Failure Response:**
- IF fails (error rate <10%): Document that AI is highly accurate; PIVOT to simpler approach
- IF fails (coverage <50%): EXPLORE different prompt templates or AI models

**Dependencies:** H-E1

**Source:** Phase 2A Causal Steps 1-2

---

#### H-M2: Execution Gating Effectiveness

**Type:** MECHANISM
**Statement:** Under the EVAF pipeline, if execution gating is applied to AI suggestions, then it will correctly filter out incorrect suggestions with false accept rate <20%, because unit tests provide ground-truth verification of code correctness.

**Rationale:**
This validates causal steps 3-4: execution gating applies tests AND correctly accepts/rejects. The gating must be effective—if false accept rate is high, bad suggestions pollute training signal.

**Variables:**
- Independent: Execution gating (unit test verification)
- Dependent: False accept rate (% of accepted suggestions that are actually incorrect)
- Controlled: Test harness, timeout settings, problem set

**Verification Protocol:**
1. Take all AI suggestions that pass execution gating (accepted)
2. Manually verify a sample of accepted suggestions for correctness
3. Calculate false accept rate (accepted but incorrect / total accepted)
4. Analyze failure modes (why did some incorrect suggestions pass?)
5. Validate false accept rate <20%

**Success Criteria (PoC: Direction-based):**
- Primary: False accept rate <20%
- Secondary: True reject rate >80% (gating catches most bad suggestions)

**Failure Response:**
- IF fails (false accept >30%): EXPLORE stronger test suites or multi-test voting
- IF fails (test coverage insufficient): Document limitation, proceed with caveat

**Dependencies:** H-M1

**Source:** Phase 2A Causal Steps 3-4

---

#### H-M3: Learning Signal Improvement

**Type:** MECHANISM
**Statement:** Under EVAF training, if the model learns from filtered AI feedback, then it will achieve higher pass@1 than Exec-Fine on semantic-error-prone problems, because filtered feedback provides both WHAT to fix (from execution) and HOW to fix (from semantic guidance).

**Rationale:**
This validates causal steps 5-6: filtered feedback retains richness with fidelity AND model learns both dimensions. This is the core mechanism claim—EVAF's advantage should manifest specifically on problems where semantic guidance matters.

**Variables:**
- Independent: Training signal source (EVAF vs Exec-Fine)
- Dependent: pass@1 on semantic-error-prone problems (stratified subset)
- Controlled: Base model, training budget, evaluation protocol, problem stratification

**Verification Protocol:**
1. Stratify HumanEval problems by baseline error type (semantic vs syntactic)
2. Train two models: EVAF-trained and Exec-Fine-trained (same budget)
3. Evaluate pass@1 on semantic-error stratum using bigcode-evaluation-harness
4. Compare using mixed-effects logistic regression with problem random effects
5. Report odds ratio and 95% CI

**Success Criteria (PoC: Direction-based):**
- Primary: EVAF pass@1 > Exec-Fine pass@1 on semantic stratum
- Secondary: Odds ratio >1.0 (direction of improvement correct)

**Failure Response:**
- IF fails (EVAF ≤ Exec-Fine): ABANDON main hypothesis; H0 supported
- IF marginal (OR near 1.0): Document as limitation, scale up in Phase 5

**Dependencies:** H-M2

**Source:** Phase 2A Causal Steps 5-6, Prediction P1

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Accept rate 20-60% | STOP, reassess EVAF mechanism |
| H-M1 | MUST_WORK | Error rate >30%, coverage >70% | PIVOT to different AI model |
| H-M2 | SHOULD_WORK | False accept <20% | Document limitation, proceed |
| H-M3 | SHOULD_WORK | EVAF > Exec-Fine on semantic | If fail, H0 supported |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3 | 4 weeks |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 | A1 (error type stability) | H-M3 | Medium |
| R2 | A2 (errors detectable via tests) | H-M2 | Medium |
| R3 | A3 (accept rate 20-60%) | H-E1, H-M1 | High |
| R4 | A4 (test suite coverage) | H-M2 | Medium |
| R5 | A5 (model capacity) | H-M3 | Low |

### 4.2 Mitigation Strategies

**Risk R3: Accept Rate Outside Target Range (HIGH)**
- Source: A3 - Filtered AI feedback volume must be sufficient
- Prevention: Monitor accept rate during early runs; abort if <10% or >90%
- Detection: Real-time accept rate logging per problem
- Response:
  - PIVOT: If <10%, relax gating (accept if any test improves)
  - PIVOT: If >90%, investigate AI accuracy (may not need EVAF)
- Early Warning: Accept rate trending <15% after 50 problems

**Risk R1: Error Type Instability (MEDIUM)**
- Source: A1 - Stratification assumes stable error distribution
- Prevention: Use pre-training baseline for stratification (before any intervention)
- Detection: Compare error type distribution at start vs mid-training
- Response: Dynamic re-stratification if distribution shifts >20%

**Risk R2: Non-Detectable Errors (MEDIUM)**
- Source: A2 - Some AI errors may not be caught by tests
- Prevention: Focus on functional correctness; exclude style suggestions
- Detection: Manual review of accepted suggestions sample
- Response: Document false accept rate; strengthen test suites if needed

**Risk R4: Insufficient Test Coverage (MEDIUM)**
- Source: A4 - Standard benchmarks may have sparse tests
- Prevention: Use benchmarks with known good coverage (HumanEval ~7 tests/problem)
- Detection: Count tests per problem; flag problems with <3 tests
- Response: Exclude low-coverage problems from primary analysis

**Risk R5: Model Capacity Limitation (LOW)**
- Source: A5 - CodeT5-770M may be too small
- Prevention: RLTF showed gains on same model; capacity likely sufficient
- Detection: Compare learning curves EVAF vs Exec-Fine
- Response: If no improvement, test on larger model (CodeT5-3B)

### 4.3 Risk Summary

| ID | Risk | Severity | Mitigation |
|----|------|----------|------------|
| R3 | Accept rate outside 20-60% | High | Real-time monitoring, adaptive gating |
| R1 | Error type distribution shifts | Medium | Pre-intervention stratification |
| R2 | Non-functional errors undetected | Medium | Functional focus, manual sampling |
| R4 | Sparse test coverage | Medium | Problem exclusion criteria |
| R5 | Model too small for benefit | Low | Scale to larger model if needed |

- Critical Risks: 0
- High Risks: 1
- Medium Risks: 3
- Low Risks: 1

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    H-E1 (Existence - EVAF mechanism implementable)
         │
         ▼
[Level 1 - Mechanism: AI Feedback]
    H-M1 (AI generates actionable suggestions with errors)
         │
         ▼
[Level 2 - Mechanism: Gating]
    H-M2 (Execution gating filters incorrect suggestions)
         │
         ▼
[Level 3 - Mechanism: Learning]
    H-M3 (Filtered feedback improves semantic-error learning)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
═══════════════════════════════════════════════════════════
```

### 5.2 Verification Phases

**Phase 1 - Foundation (Weeks 1-2)**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | EVAF pipeline implementation, accept rate measurement | MUST PASS |

→ **Gate 1**: If H-E1 fails (accept rate outside 20-60%) → STOP, reassess entire hypothesis.

**Phase 2 - Core Mechanisms (Weeks 3-6)**
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST PASS |
| H-M2 | H-M1 | SHOULD PASS |
| H-M3 | H-M2 | SHOULD PASS |

→ **Gate 2**: H-M1 must pass. H-M2/H-M3 failures = document limitation, proceed to Phase 5.

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis  │ W1-2     │ W3-4     │ W5       │ W6
──────────────────┼──────────┼──────────┼──────────┼──────────
PHASE 1: Foundation
  H-E1            │ ████████ │          │          │
  [Gate 1]        │          │ ◆        │          │
──────────────────┼──────────┼──────────┼──────────┼──────────
PHASE 2: Mechanisms
  H-M1            │          │ ████████ │          │
  H-M2            │          │          │ ████     │
  H-M3            │          │          │          │ ████
  [Gate 2]        │          │          │          │    ◆
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

- **Critical Path:** H-E1 → H-M1 → H-M2 → H-M3
- **Total Duration:** 6 weeks (2 + 2 + 1 + 1)
- **Slack Available:** 0 weeks (fully sequential)
- **Execution Mode:** Sequential chain (no parallelization)

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** EVAF achieves higher pass@1 than pure execution feedback on semantic-error-prone problems by combining ground-truth verification with rich semantic guidance.

**Supporting Evidence:**
1. Self-Refine demonstrates AI can generate actionable feedback (causal step 1)
2. Execution provides deterministic correctness verification (causal steps 3-4)
3. RLTF shows fine-grained feedback improves over episode-level (supports richness value)

**Strengths:**
- Novel synthesis: First to combine execution verification with AI feedback for training
- Addresses orthogonal dimensions: fidelity (execution) and richness (AI)
- Clear mechanism: verification gating is technically straightforward

**Expected Outcomes:**
- P1: EVAF > Exec-Fine on semantic-error problems (OR ≥ 1.5, p < 0.05)
- P2: EVAF > AI-Only on semantic-error problems (p < 0.05)
- P3: Exec-Fine ≈ EVAF on syntactic-error problems (non-inferiority)

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference in pass@1 between EVAF and Exec-Fine feedback strategies on semantic-error-prone code generation problems (OR = 1.0, 95% CI includes 1.0).

**Counter-Arguments:**
1. Accept rate may be too low (<10%), causing EVAF to degenerate to pure execution feedback
2. AI semantic guidance may not be learnable through RL training signal
3. Benchmark saturation on HumanEval may limit observable effect sizes

**Potential Failure Points:**
- R3: Accept rate outside target range (most critical)
- H-M1 failure: AI feedback not actionable or too accurate
- H-M3 failure: Learning doesn't transfer semantic understanding

**Conditions Under Which H0 Would Be Supported:**
- EVAF pass@1 ≤ Exec-Fine pass@1 on semantic stratum
- Odds ratio 95% CI includes 1.0
- Accept rate <10% (verification too aggressive)

### 6.3 Synthesis

**Balanced Assessment:**

The hypothesis H-EVAF-v1 presents a testable claim that combining execution verification with AI feedback can improve code generation alignment on semantic-error problems. However, the null hypothesis raises valid concerns regarding accept rate viability and whether semantic richness translates to learnable training signal.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes accept rate before investing in mechanism testing
2. **Sequential mechanism testing (H-M1 → H-M2 → H-M3):** Tests causal chain step-by-step
3. **Gate conditions:** Allow early detection of H0 support (MUST_WORK gates)

**Conditions for Thesis Support:**
- H-E1: Accept rate 20-60% (mechanism is selective)
- H-M1: AI feedback actionable with measurable error rate
- H-M3: EVAF > Exec-Fine on semantic stratum

**Conditions for Antithesis Support:**
- H-E1 fails: Accept rate <10% or >90%
- H-M3 fails: EVAF ≤ Exec-Fine (no semantic advantage)

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated, proceed to Phase 5
2. **Partial Support:** H-M2 or H-M3 marginal → Refined thesis with limitations
3. **No Support:** H-E1 or H-M1 fail → Antithesis supported, pivot required

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | EVAF mechanism implementable | Accept rate may be extreme | H-E1 test with monitoring |
| AI Quality | AI produces rich, filterable suggestions | AI may be too accurate/inaccurate | H-M1 measures error rate |
| Gating | Execution filters errors | Some errors may pass tests | H-M2 measures false accept |
| Learning | Filtered feedback improves semantics | Signal may not transfer | H-M3 direct comparison |

**Overall Robustness Score:** Medium-High

**Confidence in Verification Plan:** 0.75

---

## 7. Executive Summary

**Main Hypothesis:** EVAF achieves higher pass@1 on semantic-error-prone code generation problems
- ID: H-EVAF-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 4 total
  - H-E: 1, H-M: 3
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points (Gate 1 at H-E1, Gate 2 at H-M1)

**Risk Assessment:** Medium
- Primary concerns: Accept rate viability (R3), AI feedback quality (R1/R2)

**Immediate Action:** Begin Phase 1 with H-E1 (EVAF implementation and accept rate measurement)

---

## 8. Conclusions

### 8.1 Key Achievements
- 4 hypotheses across 2 phases (Foundation + Mechanisms)
- H0 addressed: No difference between EVAF and Exec-Fine (OR = 1.0)
- Clear falsification criteria established

### 8.2 Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: EVAF mechanism existence with accept rate 20-60%
- Gate 1: MUST PASS

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: AI feedback generates actionable suggestions with errors
- H-M2: Execution gating filters incorrect suggestions
- H-M3: Filtered feedback improves semantic-error learning
- Gate 2: H-M1 must pass

### 8.3 Critical Decision Points

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, reassess hypothesis
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - CRITICAL FAIL → Execute failure response
   - OPTIONAL FAIL → Document limitation

### 8.4 Open Questions
- What is the optimal accept rate for execution gating?
- Does EVAF transfer zero-shot to MBPP as well as pure execution methods?
- What AI feedback model (CodeLlama-Instruct vs GPT-4) is sufficient for EVAF?

### 8.5 Recommendations

1. **Immediate Actions:**
   - Start Phase 1 with H-E1 implementation
   - Set up accept rate monitoring infrastructure

2. **Resource Allocation:**
   - Allocate 6 weeks for critical path
   - Reserve buffer for gate failures

3. **Failure Management:**
   - Document all failures with detailed analysis
   - Execute PIVOT strategies as defined

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-EVAF-v1)
- **Schema Version:** 10.0.0
- **Convergence:** All 6 criteria met after 15 exchanges

### B. MCP Tool Usage Summary
- **Total MCP calls:** 4
- **Tools used:**
  - mcp__clearThought__scientificmethod (2x): H-E1 hypothesis + experiment
  - mcp__clearThought__sequentialthinking (3x): Mechanism decomposition

### C. Established Facts (from Phase 2A)
- BUILD_ON: Execution feedback provides ground-truth signals (CodeRL, RLTF)
- BUILD_ON: AI feedback provides semantically rich but potentially incorrect suggestions (Self-Refine)
- BUILD_ON: RLTF's fine-grained localization improves over episode-level rewards
- PROVE_NEW: EVAF can achieve high fidelity + high semantic richness simultaneously

**Scope Reduction:** 25% (3 BUILD_ON claims not re-verified)

---

*Generated by Phase 2B Planning Workflow*
*Date: 2026-08-18*
