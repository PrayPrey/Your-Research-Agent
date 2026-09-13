# Verification Plan: Incremental SMT Verification for LLM Code Repair

**Date:** 2026-08-28
**Hypothesis ID:** H-IncrementalSMT-v1
**Confidence:** 0.80
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under iterative LLM code repair workflows in statically-typed languages, if incremental SMT verification is used (re-verifying only modified functions + dependencies), then verification time reduces by 2-5x compared to batch re-verification, because unchanged code portions skip redundant constraint checking.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in verification time between incremental and batch SMT approaches for LLM code repair (speedup < 1.5x).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval + Pydantic Type Extensions (to be created) | Provides code generation benchmark with existing test suites; type extension enables static analysis |
| **Model** | GPT-4 or Claude Sonnet 3.5 | State-of-the-art code LLMs capable of generating typed Python with repair iterations |

**Dataset Details:**
- Source: OpenAI HumanEval benchmark extended with Pydantic type annotations
- Path: N/A - to be created

**Model Details:**
- Type: Code generation LLM
- Source: OpenAI API / Anthropic API

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Batch SMT Verification (Z3 on full program) | Verification time scales O(n²) with codebase size - infeasible for large LLM outputs | General SMT-LIB benchmarks | No incremental solving → re-verifies unchanged code on every iteration |
| Test-Suite-Only Validation | Fast but incomplete - misses edge cases not covered by tests | HumanEval test suites | No formal guarantees - LLM can pass tests while having subtle bugs |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | LLM-generated code in typed languages has extractable static analysis constraints | Type annotations provide structured contracts for Prusti/Pyre | Cannot extract SMT constraints → entire approach fails |
| A2 | LLM repair modifications are typically localized (1-3 functions) | Neural repair literature shows 80%+ repairs touch 1-3 lines | Broad modifications → large invalidation cone → minimal speedup |
| A3 | Dependency analysis accurately identifies invalidated constraints | Conservative over-approximation maintains soundness | Missed dependencies → false negatives → unsound verification |
| A4 | Static analyzer overhead (constraint extraction) is small relative to SMT solving time | SMT solving is computationally expensive relative to AST parsing | Extraction time dominates → incremental approach provides no speedup |
| A5 | LLM code doesn't use heavy dynamic features that block static analysis | Scoped to typed subsets, ban eval/exec/metaprogramming | Static analysis fails → cannot extract constraints → approach inapplicable |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First application of incremental SMT verification to neural code generation repair workflows

**Key Innovation:** Combining established techniques (incremental SMT + typed LLM code) in new configuration to solve LLM verification scalability bottleneck

**Differentiation:**
- vs Angelix, Prophet (SMT-guided repair for human code): Applied to small patches on human code; we scale to LLM-generated full programs with typed constraints
- vs AlphaCode, CodeT5 (neural code generation): No formal verification; we add SMT-based correctness guarantees
- vs Prusti, Pyre (static analyzers for typed languages): Used for human code verification; we integrate with LLM repair loop + incremental SMT

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | Mechanism | MUST_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Extractable SMT Constraints Exist in Typed LLM Code

**Type:** EXISTENCE

**Statement:** Under LLM code generation in statically-typed languages (Rust, typed Python), if type annotations are present, then static analyzers can extract SMT constraints from the generated code because type annotations provide structured contracts that map directly to formal verification predicates.

**Rationale:**
This existence hypothesis validates the foundational assumption that LLM-generated code in typed languages can serve as input to formal verification toolchains. Without extractable constraints, the entire incremental SMT approach fails. Phase 2A identified this as BUILD_ON (established capability for human code via Prusti/Pyre), but needs verification for LLM-generated code specifically.

**Variables** (from Phase 2A):
- Independent: Code generation method (LLM vs human-written)
- Dependent: Constraint extraction success rate (%)
- Controlled: Language (typed Python with Pydantic), static analyzer (Pyre), code complexity (10-50 LOC)

**Verification Protocol:**
1. Generate 100 typed Python programs using GPT-4/Claude Sonnet 3.5 from HumanEval prompts with Pydantic type extensions
2. Extract SMT constraints from each program using Pyre static analyzer
3. Measure extraction success rate (% of programs with usable constraints extracted)
4. Verify extracted constraints are semantically meaningful (not trivial/empty)
5. Compare extraction success between LLM code and equivalent human-written code

**Success Criteria** (PoC: Direction-based):
- Primary: Extraction success ≥ 90% (threshold from Phase 2A assumption A1)
- Secondary: No significant difference vs human code (statistical equivalence test)

**Gate:**
- Type: MUST_WORK
- If Fail: PIVOT to neural constraint extraction (H2 future work from Phase 2A)

**Prerequisites:** None (foundation)

**Source:** Phase 2A Section 5 (SH1 - sh1_existence), Assumption A1

---

#### H-M1: Static Analyzer Extracts SMT Constraints from Type Annotations

**Type:** MECHANISM

**Statement:** Under typed Python code with Pydantic annotations, if static analyzer (Pyre) processes the AST, then SMT constraints are extracted representing type contracts and function preconditions/postconditions because type annotations map to first-order logic predicates.

**Rationale:**
This mechanism validates the first link in the causal chain - that the static analysis infrastructure can transform type-annotated LLM code into formal constraints suitable for SMT solving.

**Variables:**
- Independent: Presence and quality of type annotations
- Dependent: Number and quality of extracted constraints
- Controlled: Static analyzer (Pyre), language subset (typed Python, no eval/exec)

**Verification Protocol:**
1. Take validated typed programs from H-E1
2. Run Pyre constraint extraction on each program
3. Measure constraint count per program and categorize by type (precondition, postcondition, invariant)
4. Verify constraints are well-formed Z3-compatible predicates
5. Measure extraction time overhead vs total SMT solving time (validates assumption A4)

**Success Criteria:**
- Primary: Constraint extraction completes for all H-E1-validated programs
- Secondary: Extraction time < 10% of SMT solving time (validates A4)

**Gate:**
- Type: MUST_WORK
- If Fail: EXPLORE optimized AST parsing or caching

**Prerequisites:** H-E1 (needs validated typed programs as input)

**Source:** Phase 2A Section 1.3 Causal Mechanism Step 1

---

#### H-M2: Dependency Analysis Identifies Invalidated Constraints After Modification

**Type:** MECHANISM

**Statement:** Under iterative code repair where LLM modifies 1-3 functions, if dependency analysis computes the transitive closure of modified functions, then only constraints in the dependency cone are marked for re-verification because unchanged code portions have cached verification results that remain valid.

**Rationale:**
This mechanism validates the second link - that incremental SMT can accurately determine which constraints need re-checking after localized modifications, avoiding redundant work while maintaining soundness.

**Variables:**
- Independent: Modification scope (number of functions changed)
- Dependent: Invalidation cone size (% of constraints marked for re-verification)
- Controlled: Dependency analysis strategy (conservative over-approximation from Phase 2A assumption A3)

**Verification Protocol:**
1. Generate initial code + constraints from H-M1
2. Induce 1-2 errors per program, LLM generates repair modifying 1-3 functions
3. Run dependency analysis to compute invalidation cone
4. Measure invalidation cone size (% of total constraints)
5. Verify soundness: seed errors in dependency-connected code, check if incremental approach catches all (validates P3)

**Success Criteria:**
- Primary: Invalidation cone < 30% for localized repairs (validates repair locality assumption A2)
- Secondary: Zero false negatives in error detection (100% soundness from P3)

**Gate:**
- Type: SHOULD_WORK
- If Fail: PIVOT to broader modifications or analyze dependency spread issue

**Prerequisites:** H-M1 (needs initial constraints as input)

**Source:** Phase 2A Section 1.3 Causal Mechanism Step 2

---

#### H-M3: Re-verifying Only Invalidated Constraints Achieves 2-5x Speedup

**Type:** MECHANISM

**Statement:** Under incremental SMT where only invalidated constraints are re-verified using Z3 push/pop contexts, if invalidation cone is small (< 30%), then wall-clock verification time is 2-5x faster than batch re-verification because unchanged portions skip redundant constraint checking.

**Rationale:**
This mechanism validates the final link and primary claim (P1) - that the incremental approach delivers measurable speedup over batch verification in realistic repair scenarios.

**Variables:**
- Independent: Verification strategy (batch vs incremental)
- Dependent: Wall-clock verification time (seconds), speedup factor (batch/incremental)
- Controlled: Same programs and repairs tested with both strategies

**Verification Protocol:**
1. Take validated repair scenarios from H-M2
2. Measure batch verification time (re-verify entire program on each iteration)
3. Measure incremental verification time (Z3 push/pop, re-verify invalidation cone only)
4. Compute speedup factor for each program, aggregate statistics (median, 75th percentile)
5. Test P2: stratify by program size (10-50 LOC, 50-100 LOC) to measure speedup correlation

**Success Criteria** (Primary Prediction P1):
- Primary: Median speedup ≥ 2x across 100 programs
- Secondary: 75th percentile speedup ≥ 3x

**Gate:**
- Type: MUST_WORK
- If Fail: ABANDON (H0 supported - no practical benefit)

**Prerequisites:** H-M2 (needs invalidation cone measurements)

**Source:** Phase 2A Section 1.3 Causal Mechanism Step 3, Prediction P1

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Extraction success ≥ 90% | ABORT → pivot to neural extraction |
| H-M1 | MUST_WORK | Extraction completes for all programs | ABORT → extraction infrastructure broken |
| H-M2 | SHOULD_WORK | Invalidation cone < 30%, zero false negatives | MODIFY → fallback to conservative analysis |
| H-M3 | MUST_WORK | Median speedup ≥ 2x, 75th percentile ≥ 3x | ABANDON → H0 supported |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1 | 2 weeks |
| Phase 2: Mechanisms | H-M2 | 1 week |
| Phase 2: Mechanisms | H-M3 | 1 week |

**Total Duration:** 6 weeks

---

## 4. Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1: Extractable SMT Constraints Exist
    Gate: MUST_WORK
         │
         ▼
[Level 1 - Mechanism Step 1]
    H-M1: Static Analyzer Extracts Constraints
    Gate: MUST_WORK
    Prerequisites: H-E1
         │
         ▼
[Level 2 - Mechanism Step 2]
    H-M2: Dependency Analysis Identifies Invalidation Cone
    Gate: SHOULD_WORK
    Prerequisites: H-M1
         │
         ▼
[Level 3 - Mechanism Step 3]
    H-M3: Incremental Re-verification Achieves 2-5x Speedup
    Gate: MUST_WORK (primary prediction P1)
    Prerequisites: H-M2

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 (4 steps)
Parallelization: None (sequential dependency chain)
═══════════════════════════════════════════════════════════
```

### 4.1 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2 │ W3-4 │ W5 │ W6 │
─────────────────┼──────┼──────┼────┼────┤
PHASE 1: Foundation
  H-E1           │ ████ │      │    │    │
  [Gate 1]       │      │ ◆    │    │    │
─────────────────┼──────┼──────┼────┼────┤
PHASE 2: Mechanisms
  H-M1           │      │ ████ │    │    │
  H-M2           │      │      │ ██ │    │
  H-M3           │      │      │    │ ██ │
  [Gate 2]       │      │      │    │  ◆ │
─────────────────┼──────┼──────┼────┼────┤
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 4.2 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3

**Total Duration:** 6 weeks
- Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) = 6 weeks

**Slack Available:** 0 weeks (all sequential dependencies)

**Key Milestones:**
- Week 2: Gate 1 decision (H-E1 validation)
- Week 4: H-M1 complete (extraction infrastructure validated)
- Week 5: H-M2 complete (dependency analysis validated)
- Week 6: Gate 2 decision (H-M3 speedup measurement, primary prediction P1)

### 4.3 Resource Summary

**Total Hypotheses:** 4
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1 to H-M3)

**Verification Phases:** 2
1. Foundation (H-E1) - Week 1-2
2. Mechanisms (H-M1 to H-M3) - Week 3-6

**Total Duration:** 6 weeks
**Critical Path Length:** 6 weeks
**Execution Mode:** Sequential chain (no parallelization)

**Dataset Requirements:**
- HumanEval + Pydantic extensions (100 programs, 10-50 LOC)
- Seeded error scenarios (1-2 errors per program)

**Tooling Requirements:**
- LLM API (GPT-4 or Claude Sonnet 3.5)
- Static analyzer (Pyre for Python)
- SMT solver (Z3 with incremental mode)
- Test suite (HumanEval existing tests)

### 4.4 Execution Order

**Step 1:** Execute H-E1 (Foundation) - Week 1-2
→ Generate 100 typed Python programs using LLM
→ Extract SMT constraints using Pyre
→ Measure extraction success rate

**Step 2:** Evaluate Gate 1 - Week 2
→ If extraction success ≥ 90%: PASS → proceed to H-M1
→ If extraction success < 90%: FAIL → pivot to neural extraction (H2 future work)

**Step 3:** Execute H-M1 (Constraint Extraction) - Week 3-4
→ Run Pyre on validated programs from H-E1
→ Measure constraint count and quality
→ Measure extraction time overhead

**Step 4:** Execute H-M2 (Dependency Analysis) - Week 5
→ Induce errors, LLM repairs
→ Compute invalidation cone size
→ Test soundness with seeded errors (P3)

**Step 5:** Execute H-M3 (Speedup Measurement) - Week 6
→ Measure batch vs incremental verification time
→ Compute speedup factor distribution
→ Test P2 (speedup vs codebase size correlation)

**Step 6:** Evaluate Gate 2 - Week 6
→ If median speedup ≥ 2x and 75th percentile ≥ 3x: PASS → hypothesis validated (proceed to Phase 5 baseline comparison)
→ If speedup < 1.5x: FAIL → H0 supported, ABANDON hypothesis

**Final:** Verification complete (if all gates pass)

---

## 5. Risk Analysis

### 5.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 | A1 | H-E1, H-M1 | Critical |
| R2 | A2 | H-M2, H-M3 | High |
| R3 | A3 | H-M1, H-M2, H-M3 | Critical |
| R4 | A4 | H-M1, H-M3 | Medium |
| R5 | A5 | All hypotheses | High |

### 5.2 Mitigation Strategies

**Risk R1: Static Analysis Extraction Failure**
- **Source:** A1 (LLM code has extractable constraints)
- **Description:** Static analyzer fails to extract usable SMT constraints from LLM-generated typed code (< 90% success)
- **Affected Hypotheses:** H-E1, H-M1
- **Severity:** Critical (entire approach fails)
- **Mitigation Strategy:**
  1. Prevention: Strict type annotation requirements in LLM prompt, validate annotation completeness before extraction
  2. Detection: Monitor extraction success rate in H-E1, flag programs with missing/incomplete constraints
  3. Response: If < 90% → PIVOT to neural constraint extraction (H2 future work), or SCOPE to subset of programs with successful extraction
- **Early Warning:** Extraction success < 95% in first 20 programs

**Risk R2: Repair Non-Locality**
- **Source:** A2 (LLM repairs are localized to 1-3 functions)
- **Description:** LLM modifications touch > 50% of codebase, invalidation cone too large for speedup
- **Affected Hypotheses:** H-M2, H-M3
- **Severity:** High (minimal speedup = H0 supported)
- **Mitigation Strategy:**
  1. Prevention: Constrain LLM repair scope via prompt ("modify only the failing function"), track modification spread in early trials
  2. Detection: Measure invalidation cone size in H-M2, alert if > 50% consistently
  3. Response: If cone > 70% → EXPLORE repair prompt engineering to reduce scope, or PIVOT to different error types that require localized fixes
- **Early Warning:** Invalidation cone > 40% in > 30% of repair cases

**Risk R3: Dependency Analysis Unsoundness**
- **Source:** A3 (Dependency analysis accurately identifies invalidated constraints)
- **Description:** Missed indirect dependencies → false negatives → bugs slip through
- **Affected Hypotheses:** H-M1, H-M2, H-M3
- **Severity:** Critical (unsound verification defeats purpose)
- **Mitigation Strategy:**
  1. Prevention: Use conservative dependency analysis (over-approximation), err on side of re-verifying more
  2. Detection: Seed known errors in dependency-connected code (P3 soundness test), check 100% detection
  3. Response: If any false negatives → ABORT incremental approach for affected programs, switch to batch verification as fallback
- **Early Warning:** Any false negative in soundness testing

**Risk R4: Extraction Overhead Dominance**
- **Source:** A4 (Static analyzer overhead small vs SMT solving)
- **Description:** Constraint extraction time dominates, negating speedup benefits
- **Affected Hypotheses:** H-M1, H-M3
- **Severity:** Medium (approach still sound, just slower)
- **Mitigation Strategy:**
  1. Prevention: Measure extraction time separately in H-M1, optimize AST traversal if needed
  2. Detection: Track extraction time as % of total verification time
  3. Response: If extraction > 30% of total → EXPLORE caching extracted constraints across iterations, or SCOPE to programs where SMT dominates
- **Early Warning:** Extraction time > 20% of total in > 50% of cases

**Risk R5: Dynamic Feature Blocker**
- **Source:** A5 (LLM code doesn't use dynamic features that block static analysis)
- **Description:** LLM generates eval/exec/metaprogramming that breaks static analysis
- **Affected Hypotheses:** All hypotheses
- **Severity:** High (programs become unanalyzable)
- **Mitigation Strategy:**
  1. Prevention: Explicit prompt constraints ("do not use eval, exec, or metaprogramming"), pre-filter generated code for banned patterns
  2. Detection: Static analysis failure mode detection (AST parse errors, constraint extraction crashes)
  3. Response: If detected → REJECT program and regenerate with stricter prompt, or SCOPE to verified-safe subset
- **Early Warning:** Any eval/exec/reflection usage in generated code

### 5.3 Risk Summary Table

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Extraction failure | A1 | Critical | H-E1, H-M1 | Strict annotations, pivot to neural extraction if < 90% |
| R2 | Repair non-locality | A2 | High | H-M2, H-M3 | Constrain repair scope, measure cone early |
| R3 | Dependency unsoundness | A3 | Critical | H-M1-3 | Conservative analysis, 100% soundness testing |
| R4 | Extraction overhead | A4 | Medium | H-M1, H-M3 | Measure separately, cache constraints |
| R5 | Dynamic features | A5 | High | All | Ban in prompts, pre-filter code |

**Critical Risks:** 2 (R1, R3)
**High Risks:** 2 (R2, R5)
**Medium Risks:** 1 (R4)
**Low Risks:** 0

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Under iterative LLM code repair workflows in statically-typed languages, if incremental SMT verification is used (re-verifying only modified functions + dependencies), then verification time reduces by 2-5x compared to batch re-verification, because unchanged code portions skip redundant constraint checking.

**Supporting Evidence:**
1. Causal mechanism: Typed code → static analyzer extracts constraints → dependency analysis identifies invalidation cone → only modified portions re-verified
2. Established capabilities: Z3 incremental solving (push/pop), Prusti/Pyre constraint extraction from typed languages, repair locality (80%+ touch 1-3 lines)
3. Testable predictions: P1 (2-5x speedup), P2 (speedup scales with size), P3 (soundness maintained)

**Strengths:**
- Builds on established SMT and static analysis capabilities (Phase 2A Section 0 - BUILD_ON claims)
- Clear causal mechanism with falsifiable steps
- Quantitative success criteria (median speedup ≥ 2x)
- Conservative dependency analysis maintains soundness (A3)

**Expected Outcomes:**
- Primary: Median speedup ≥ 2x, 75th percentile ≥ 3x across 100 programs
- Secondary: Speedup increases with codebase size (100 LOC = 2x, 500 LOC ≥ 5x)
- Tertiary: Zero false negatives (100% error detection soundness)

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference in verification time between incremental and batch SMT approaches for LLM code repair (speedup < 1.5x).

**Counter-Arguments:**
1. LLM repair patterns may differ from human code - repair locality assumption (A2) may not hold for neural code generation
2. Dependency graphs in LLM code may be more tangled than human code - invalidation cones could be large (> 70%), negating speedup benefits
3. Static analysis extraction overhead (A4) may be higher for LLM code due to inconsistent annotation quality

**Potential Failure Points:**
- R1 (Critical): Static analysis fails to extract constraints from LLM code (< 90% success) → entire approach fails
- R2 (High): LLM repairs are non-local (> 50% invalidation cone) → minimal speedup
- R3 (Critical): Dependency analysis misses indirect dependencies → false negatives → unsound verification
- R4 (Medium): Constraint extraction overhead dominates → no net speedup
- R5 (High): LLM generates dynamic features (eval/exec) → static analysis blocked

**Conditions Under Which H0 Would Be Supported:**
- If median speedup < 1.5x (P1 falsification criterion)
- If H-E1 fails: extraction success < 90% (A1 violated)
- If H-M2 fails: invalidation cone > 70% consistently (A2 violated)
- If H-M3 fails: extraction overhead > 30% of total time (A4 violated)

### 6.3 Synthesis

**Balanced Assessment:**

The hypothesis H-IncrementalSMT-v1 presents a testable claim that incremental SMT verification can achieve 2-5x speedup for LLM code repair by exploiting repair locality and incremental solving. However, the null hypothesis raises valid concerns regarding whether LLM-generated code exhibits the same locality properties as human code, and whether dependency analysis can accurately track invalidation without either missing dependencies (unsoundness) or over-approximating (losing speedup).

**Resolution Path:**

The verification plan addresses this dialectic through a sequential validation approach:

1. **Foundation verification (H-E1):** Establishes that LLM code is even amenable to static analysis before investing in mechanism testing. If extraction success < 90%, pivot to neural approaches (H2 future work) rather than proceeding with broken foundation.

2. **Sequential mechanism testing (H-M1 → H-M2 → H-M3):** Tests each causal chain link independently:
   - H-M1 validates extraction infrastructure works for LLM code
   - H-M2 measures actual invalidation cone sizes and tests soundness
   - H-M3 measures end-to-end speedup only after mechanism validated

3. **Gate conditions:** Allow early detection of H0 support:
   - Gate 1 (H-E1): MUST_WORK - stops entire approach if static analysis fails
   - Gate 2a (H-M1): MUST_WORK - stops if extraction infrastructure broken
   - Gate 2b (H-M2): SHOULD_WORK - can fallback to conservative analysis
   - Gate 2c (H-M3): MUST_WORK - speedup < 1.5x = H0 supported

**Conditions for Thesis Support:**
- All MUST_WORK gates pass (H-E1, H-M1, H-M3)
- Median speedup ≥ 2x, 75th percentile ≥ 3x (P1 confirmed)
- Zero false negatives in soundness testing (P3 confirmed)
- Invalidation cone < 30% for localized repairs (validates A2)

**Conditions for Antithesis Support:**
- H-E1 fails: extraction success < 90% (LLM code not analyzable)
- H-M1 fails: extraction infrastructure broken
- H-M3 fails: median speedup < 1.5x (no practical benefit, H0 supported)

**Nuanced Outcome Possibilities:**
1. **Full Support:** All gates pass, speedup ≥ 2x → Thesis validated, incremental SMT works for LLM code repair
2. **Partial Support:** H-M2 shows large cones (40-60%) but speedup still ≥ 2x → Refined thesis: works for subset of repair types
3. **No Support:** H-E1 or H-M1 fail → Antithesis supported, LLM code fundamentally different from human code assumptions
4. **H0 Support:** H-M3 speedup < 1.5x → Antithesis supported, incremental approach provides no practical benefit despite working mechanism

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | LLM typed code has extractable constraints | LLM code quality varies, annotations incomplete | H-E1: Measure 90% threshold, pivot to neural if fails |
| Mechanism | Incremental SMT skips unchanged code | Invalidation cones may be large for LLM repairs | H-M2: Measure actual cone sizes, test locality assumption |
| Soundness | Conservative analysis maintains correctness | Over-approximation may negate speedup | P3: 100% error detection test, balance speed vs soundness |
| Performance | 2-5x speedup vs batch | Extraction overhead may dominate | H-M1/M3: Measure extraction time separately, cache if needed |
| Scope | Applies to typed LLM code repair | Limited to non-dynamic code, specific repair types | Document boundaries explicitly, Phase 5 tests real-world fit |

**Overall Robustness Score:** Medium-High

**Reasoning:**
- Strong foundation: Builds on established SMT/static analysis capabilities (BUILD_ON claims)
- Clear falsification: Quantitative thresholds make success/failure unambiguous
- Conservative approach: Sequential gates prevent investing in broken mechanisms
- Honest uncertainty: Acknowledges unknown (LLM repair locality) and tests it directly
- Risk mitigation: Critical risks (R1, R3) have detection + pivot strategies

**Weaknesses:**
- Assumes repair locality transfers from human to LLM code (empirical question)
- Limited to typed language subset (excludes large portion of LLM code generation)
- Cold start problem not addressed in PoC (Phase 4 focuses on iteration 2+)

**Confidence in Verification Plan:** 0.80 (from Phase 2A)

**Justification:** High confidence that plan can definitively validate or falsify hypothesis through quantitative measurements. Lower confidence in actual thesis outcome due to unknown LLM repair patterns.

---

## 7. Executive Summary

**Main Hypothesis:** Incremental SMT verification reduces verification time for LLM-generated code repairs in typed languages by 2-5x compared to batch re-verification by re-verifying only modified functions + dependencies.
- ID: H-IncrementalSMT-v1, Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (builds on Phase 2A Dialogue)
- Sub-Hypotheses: 4 total
  - H-E: 1 (Existence), H-M: 3 (Mechanism steps)
- Phases: 2 phases over 6 weeks
- Critical Gates: 4 decision points (Gate 1, Gate 2a-c)

**Scope Reduction:** 25% (3 BUILD_ON claims skipped, 1 PROVE_NEW claim targeted)

**Risk Assessment:** Medium-High
- Primary concerns: Extraction failure (R1 - Critical), Repair non-locality (R2 - High), Dependency unsoundness (R3 - Critical)
- Mitigation: Sequential gates allow early abort, pivot strategies for critical failures

**Immediate Action:** Begin Phase 1 with H-E1 (extract SMT constraints from 100 typed LLM programs, verify ≥90% success)

### 7.1 Key Achievements

- 4 hypotheses across 2 phases with sequential dependency chain
- H0 addressed: "No significant difference in verification time between incremental and batch SMT approaches (speedup < 1.5x)"
- All risks mapped to hypotheses with mitigation strategies
- Clear falsification criteria for each hypothesis
- Baseline comparison deferred to Phase 5 (skip_baseline_comparison config)

### 7.2 Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: Typed LLM code with extractable constraints exists (static analyzers work on type annotations)
- Gate 1: MUST PASS (≥90% extraction success) → FAIL = pivot to neural extraction

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: Static analyzer extracts constraints from type annotations (Week 3-4)
- H-M2: Dependency analysis identifies invalidation cone < 30% (Week 5)
- H-M3: Incremental re-verification achieves 2-5x speedup (Week 6)
- Gate 2a (H-M1): MUST PASS → FAIL = extraction infrastructure broken
- Gate 2b (H-M2): SHOULD PASS → FAIL = fallback to conservative analysis
- Gate 2c (H-M3): MUST PASS → FAIL = H0 supported, abandon hypothesis

### 7.3 Critical Decision Points

1. **Gate 1 (Foundation - Week 2):** H-E1 extraction success
   - FAIL (< 90%) → ABORT entire hypothesis, pivot to neural constraint extraction (H2 future work)
   - PASS (≥ 90%) → Proceed to H-M1

2. **Gate 2a (H-M1 - Week 4):** Constraint extraction infrastructure
   - CRITICAL FAIL → ABORT (extraction doesn't work for LLM code)
   - PASS → Proceed to H-M2

3. **Gate 2b (H-M2 - Week 5):** Dependency analysis accuracy
   - FAIL (soundness issues) → MODIFY to conservative over-approximation, continue to H-M3
   - PARTIAL (large cones 40-70%) → Document limitation, continue to H-M3
   - PASS → Proceed to H-M3

4. **Gate 2c (H-M3 - Week 6):** Primary prediction P1 validation
   - FAIL (median speedup < 1.5x) → H0 supported, ABANDON hypothesis
   - PARTIAL (1.5x-2x) → Document as marginal improvement, Phase 5 decision
   - PASS (≥ 2x median, ≥ 3x 75th percentile) → Hypothesis validated, proceed to Phase 5

### 7.4 Open Questions

- What is actual iteration count distribution for LLM repair in practice? (affects cold start impact - not measured in PoC)
- Can cross-program constraint caching (P4) further improve first-iteration speedup?
- Does embedding-based retrieval cache (H2 future work) provide additional speedup beyond incremental SMT?
- How does incremental approach perform on full-scale codebases (> 500 LOC) vs HumanEval subset?

### 7.5 Recommendations

**Immediate Actions:**
- Start Phase 1 with H-E1: Generate 100 typed Python programs (HumanEval + Pydantic extensions)
- Set up measurement infrastructure: Pyre static analyzer, Z3 SMT solver, timing harness
- Validate LLM prompts constrain to typed subset (no eval/exec/metaprogramming)

**Resource Allocation:**
- Allocate 6 weeks for critical path execution
- Reserve 2-week buffer for H-M failures requiring modification attempts
- Dataset creation: 2-3 days (extend HumanEval with Pydantic annotations)

**Failure Management:**
- Document all gate failures in Serena memory for Phase 0 routing context
- Execute PIVOT strategies defined in Risk Analysis
- If H-E1 or H-M1 fails → Route to Phase 2A-Dialogue to redesign hypothesis
- If H-M3 fails (H0 supported) → Route to Phase 0 for new research direction

**Phase 5 Preparation:**
- Baseline repository search: Angelix, Prophet (SMT-guided repair for human code)
- Comparison target: Batch SMT verification time as primary baseline
- Deferred per module config: skip_baseline_comparison=true

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-IncrementalSMT-v1)
- **Causal Chain:** 3 steps (static analysis → dependency analysis → incremental re-verification)
- **Established Facts:** 3 BUILD_ON, 1 PROVE_NEW (25% scope reduction)

### B. MCP Tool Usage Summary
- **Mode:** Incremental (Phase 2A pre-mapped structure)
- **Total MCP calls:** 2 (batch mode simulation)
- **Tools:** scientificmethod (H-E1 verification, H-M integrated mechanism)

### C. Hypothesis ID Mapping
- H-E1 → SH1 from Phase 2A Section 5
- H-M1 → Causal Mechanism Step 1
- H-M2 → Causal Mechanism Step 2
- H-M3 → Causal Mechanism Step 3 + Prediction P1

---

**Document Status:** Complete
**Created:** 2026-08-28
**Phase:** 2B - Verification Planning
**Next Phase:** 2C - Experiment Design (start with h-e1)
