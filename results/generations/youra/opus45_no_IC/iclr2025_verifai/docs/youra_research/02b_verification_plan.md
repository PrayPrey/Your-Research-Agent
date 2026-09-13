# Verification Plan: Formal Verification Pipeline for LLM Code Generation

**Date:** 2026-08-12
**Hypothesis ID:** H-VerifPipeline-v1
**Confidence:** 0.80
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under standard code generation benchmarks (HumanEval, MBPP), if formal verification strategies are combined in a pipeline ordered by abstraction level (grammar constraints → static analysis → SMT-guided repair), then the combined pass@k improvement exceeds individual strategy improvements, because each strategy targets largely independent error classes (syntax, semantics, specifications) enabling multiplicative error reduction.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in pass@k between the combined verification pipeline and the arithmetic sum of individual strategy improvements. The synergy coefficient S = 1.0 (±0.2), indicating purely additive effects with no interaction.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval + HumanEval-Verus (standard) | Standard benchmark with test cases (HumanEval) plus formal specs (Verus) enables testing all three verification strategies |
| **Model** | CodeLlama-7B, GPT-4 | Two models spanning capability spectrum test generalization across model sizes |

**Dataset Details:**
- Source: openai/human-eval, secure-foundations/human-eval-verus
- Path: github.com/openai/human-eval, github.com/secure-foundations/human-eval-verus

**Model Details:**
- Type: autoregressive_llm
- Source: meta-llama/CodeLlama-7b-hf, openai/gpt-4

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Baseline (no verification) | Standard LLM generation | HumanEval |
| Grammar-only | >50% compilation error reduction | HumanEval |
| Static-only | Security 40%→13%, reliability 50%→11% | PythonSecurityEval |
| SMT-only | 75-82% pass@1 with SMT pipeline | ContractEval |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Error classes (syntax, semantics, specifications) are largely independent | Different tool categories target different issues by design | Synergy coefficient would be < 0.8 due to redundancy |
| A2 | HumanEval and HumanEval-Verus are representative of code generation tasks | Widely used benchmarks (3333+ stars, 290+ citations) | Results may not generalize to real-world codebases |
| A3 | Existing tools implement their respective strategies correctly | Published implementations with peer review (eth-sri/PLDI, Bandit/OWASP) | Tool bugs would confound strategy effectiveness measurement |
| A4 | Pipeline ordering (syntax → semantics → specs) is optimal | Abstraction level hierarchy; downstream stages benefit from upstream filtering | Different orderings might yield better results |
| A5 | Two LLM models (CodeLlama-7B, GPT-4) provide sufficient generalization | Spans capability spectrum (7B open-source to frontier) | Results might be model-specific |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First unified comparison of all three verification strategies on identical benchmarks

**Key Innovation:** Error-class-independence framework that predicts multiplicative vs. additive improvements

**Differentiation:**
- Mundler et al. 2025: Tests grammar constraints alone; we test in pipeline with other strategies
- Blyth et al. 2025: Tests static analysis alone; we measure interaction with grammar/SMT
- ContractEval 2025: Tests SMT alone; we measure marginal contribution after other stages

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
**H-E1: Error Class Independence Existence**

**Statement**: Under HumanEval benchmark conditions, if grammar constraints, static analysis, and SMT-guided repair are applied independently, then the sets of problems improved by each strategy have Jaccard overlap < 30%, because each strategy targets fundamentally different error categories.

**Rationale:** This hypothesis validates the core assumption that error classes are independent. If overlap exceeds 30%, the multiplicative improvement model fails and strategies are redundant rather than complementary.

**Variables:**
- Independent: verification_strategy (grammar, static, SMT)
- Dependent: error_overlap_rate (Jaccard index)
- Controlled: llm_model, benchmark_dataset, temperature (0.2), sample_count (n=10)

**Verification Protocol:**
1. Generate n=10 samples per HumanEval problem with baseline LLM
2. Apply each verification strategy independently, record improved problem sets
3. Compute pairwise Jaccard indices between strategy-improved sets
4. Aggregate across both LLM models (CodeLlama-7B, GPT-4)
5. Report mean and variance of overlap metrics

**Success Criteria (PoC: Direction-based):**
- Primary: Jaccard(grammar_improved, static_improved) < 0.30
- Secondary: All pairwise overlaps < 0.30

**Failure Response:**
- IF fails: PIVOT to investigating which error classes overlap and why

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A SH1, Prediction P1

---

---
**H-M1: Grammar Constraints Reduce Compilation Errors**

**Statement**: Under HumanEval benchmark, if grammar-constrained decoding (token-level logit masking) is applied during generation, then compilation errors decrease by >50% compared to baseline, because prefix automata enforce syntactic validity at generation time.

**Rationale:** This is the first mechanism step - establishes that syntax-level filtering works. Without syntax errors removed, downstream stages (static analysis, SMT) cannot operate effectively.

**Variables:**
- Independent: grammar_constraint_applied (yes/no)
- Dependent: compilation_error_rate
- Controlled: llm_model, benchmark_dataset, temperature (0.2)

**Verification Protocol:**
1. Generate n=10 samples per HumanEval problem with baseline LLM
2. Record compilation error rate on baseline samples
3. Apply grammar-constrained decoding, generate same problems
4. Record compilation error rate on constrained samples
5. Compute reduction percentage

**Success Criteria (PoC: Direction-based):**
- Primary: Compilation errors decrease (constrained < baseline)
- Secondary: Reduction magnitude measurable

**Failure Response:**
- IF fails: EXPLORE alternative grammar constraint implementations

**Dependencies**: H-E1

**Source**: Phase 2A Causal Step 1, Mundler et al. 2025

---

---
**H-M2: Static Analysis Identifies Semantic Patterns**

**Statement**: Under syntactically-valid code from H-M1, if static analysis feedback (Bandit/Pylint) is applied, then security/reliability issues decrease from baseline levels, because static analyzers detect semantic patterns invisible to syntax-only checks.

**Rationale:** Tests the second mechanism step - semantic filtering operates on different error class than syntax filtering. If static analysis catches same errors as grammar constraints, independence assumption fails.

**Variables:**
- Independent: static_analysis_applied (yes/no)
- Dependent: security_issue_rate, reliability_issue_rate
- Controlled: llm_model, input_code_quality (syntax-valid from H-M1)

**Verification Protocol:**
1. Take syntactically-valid outputs from H-M1
2. Run Bandit (security) and Pylint (reliability) analysis
3. Record issue counts and categories
4. Apply static analysis feedback loop
5. Measure issue reduction

**Success Criteria (PoC: Direction-based):**
- Primary: Security/reliability issues decrease after feedback
- Secondary: Issues detected are different from compilation errors

**Failure Response:**
- IF fails: EXPLORE whether static analysis overlaps with grammar constraints

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 2, Blyth et al. 2025

---

---
**H-M3: SMT-Guided Repair Enforces Specification Satisfaction**

**Statement**: Under semantically-filtered code from H-M2, if SMT-guided repair (Z3) is applied to spec-annotated problems, then pass@1 on formal specifications improves, because SMT solvers can enforce logical constraints that static analysis cannot express.

**Rationale:** Tests the third mechanism step - specification-level verification. Limited to HumanEval-Verus 23-problem subset with formal specs. SMT operates on different abstraction level than static analysis.

**Variables:**
- Independent: smt_repair_applied (yes/no)
- Dependent: spec_satisfaction_rate (pass@1 on Verus specs)
- Controlled: llm_model, input_code_quality (semantically-filtered from H-M2)

**Verification Protocol:**
1. Take semantically-filtered outputs from H-M2
2. Select HumanEval-Verus 23-problem subset
3. Apply SMT-guided repair using Z3
4. Measure spec satisfaction before/after
5. Report pass@1 improvement

**Success Criteria (PoC: Direction-based):**
- Primary: Spec satisfaction improves after SMT repair
- Secondary: Problems fixed by SMT differ from those fixed by static analysis

**Failure Response:**
- IF fails: EXPLORE whether SMT provides marginal value after static analysis

**Dependencies**: H-M2

**Source**: Phase 2A Causal Step 3, ContractEval 2025

---

---
**H-M4: Pipeline Composition Enables Multiplicative Error Reduction**

**Statement**: Under full pipeline (grammar → static → SMT), if each stage filters a distinct error class, then combined pass@k improvement exceeds sum of individual improvements (synergy coefficient S > 1.0), because downstream stages receive cleaner inputs with less noise.

**Rationale:** This is the integration step - tests that the full pipeline achieves more than sum of parts. The synergy coefficient S measures whether combination is multiplicative (S > 1) or merely additive (S ≈ 1).

**Variables:**
- Independent: pipeline_configuration (baseline, grammar, grammar+static, full)
- Dependent: pass@k, synergy_coefficient S
- Controlled: llm_model, benchmark_dataset

**Verification Protocol:**
1. Measure baseline pass@k on HumanEval
2. Measure pass@k with grammar-only
3. Measure pass@k with grammar+static
4. Measure pass@k with full pipeline
5. Compute S = (Combined - Baseline) / (Sum of individual deltas)

**Success Criteria (PoC: Direction-based):**
- Primary: S > 1.0 (or at minimum, 0.8 <= S <= 1.2 confirms independence)
- Secondary: Combined pass@k > max(individual pass@k)

**Failure Response:**
- IF fails (S < 0.8): PIVOT to investigating interference between stages

**Dependencies**: H-M3

**Source**: Phase 2A Causal Step 4, Prediction P3

---

---

## 3. Risk Analysis

### 3.1 Assumption-to-Risk Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 | A1: Error classes not independent | H-E1, H-M4 | Critical |
| R2 | A2: Benchmarks not representative | All | High |
| R3 | A3: Tool implementation bugs | H-M1, H-M2, H-M3 | Medium |
| R4 | A4: Pipeline ordering suboptimal | H-M4 | Medium |
| R5 | A5: Model-specific effects | All | Medium |

### 3.2 Mitigation Strategies

**Risk R1: Error Class Overlap**
- Prevention: H-E1 explicitly tests this assumption first
- Detection: Jaccard index measurement in H-E1
- Response: If Jaccard >= 0.30, document which classes overlap and revise multiplicative model

**Risk R2: Benchmark Representativeness**
- Prevention: Use widely-adopted benchmarks with established validity
- Detection: Compare results across CodeLlama-7B vs GPT-4
- Response: Scope conclusions to "standard benchmarks" with future work on CodeContests/real repos

**Risk R3: Tool Implementation Bugs**
- Prevention: Use peer-reviewed, published implementations
- Detection: Sanity checks on tool outputs
- Response: Report tool versions and known limitations

**Risk R4: Pipeline Ordering**
- Prevention: Follow abstraction-level hierarchy (syntax < semantics < specs)
- Detection: Monitor whether later stages add value
- Response: Test alternative orderings in future work

**Risk R5: Model-Specific Effects**
- Prevention: Test on two models spanning capability spectrum
- Detection: Per-model analysis in all hypotheses
- Response: Report per-model results; generalization claims scoped accordingly

### 3.3 Risk Summary

| ID | Risk | Severity | Mitigation |
|----|------|----------|------------|
| R1 | Error class overlap > 30% | Critical | H-E1 tests first |
| R2 | Benchmarks unrepresentative | High | Two models, scope claims |
| R3 | Tool bugs | Medium | Published implementations |
| R4 | Suboptimal ordering | Medium | Follow abstraction hierarchy |
| R5 | Model-specific | Medium | Two-model design |

Critical Risks: 1
High Risks: 1
Medium Risks: 3

---

## 4. Execution

### 4.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    H-E1 (Existence - Error Class Independence)
         │
         ▼
[Level 1 - Mechanism]
    H-M1 (Grammar Constraints)
         │
         ▼
[Level 2 - Mechanism]
    H-M2 (Static Analysis)
         │
         ▼
[Level 3 - Mechanism]
    H-M3 (SMT-Guided Repair)
         │
         ▼
[Level 4 - Integration]
    H-M4 (Pipeline Composition)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 4.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

### 4.3 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Jaccard < 0.30 | STOP, reassess hypothesis |
| H-M1 | MUST_WORK | Compilation errors decrease | EXPLORE alternatives |
| H-M2 | SHOULD_WORK | Semantic issues decrease | Document limitation |
| H-M3 | SHOULD_WORK | Spec satisfaction improves | Document limitation |
| H-M4 | SHOULD_WORK | S >= 0.8 | Document interference |

### 4.4 Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2 │ W3-4 │ W5   │ W6   │ W7
─────────────────┼──────┼──────┼──────┼──────┼──────
PHASE 1: Foundation
  H-E1           │██████│      │      │      │
  [Gate 1]       │      │ ◆    │      │      │
─────────────────┼──────┼──────┼──────┼──────┼──────
PHASE 2: Mechanisms
  H-M1           │      │██████│      │      │
  H-M2           │      │      │██████│      │
  H-M3           │      │      │      │██████│
  H-M4           │      │      │      │      │██████
  [Gate 2]       │      │      │      │      │    ◆
═══════════════════════════════════════════════════════════════════
Legend: ██████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

### 4.5 Critical Path Analysis

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

Total Duration: 7 weeks
- H-E1: 2 weeks (foundation)
- H-M1: 2 weeks (first mechanism, more setup)
- H-M2: 1 week
- H-M3: 1 week
- H-M4: 1 week (integration)

Slack Available: 0 weeks (all sequential)

### 4.6 Execution Order

1. **Step 1**: Execute H-E1 (Foundation) - Week 1-2
2. **Step 2**: Evaluate Gate 1 → If Jaccard < 0.30, proceed
3. **Step 3**: Execute H-M1 (Grammar Constraints) - Week 3-4
4. **Step 4**: Execute H-M2 (Static Analysis) - Week 5
5. **Step 5**: Execute H-M3 (SMT Repair) - Week 6
6. **Step 6**: Execute H-M4 (Pipeline Composition) - Week 7
7. **Step 7**: Evaluate Gate 2 → Assess synergy coefficient
8. **Final**: Phase 2B verification complete → proceed to Phase 5

---

## 5. Dialectical Analysis

### 5.1 Thesis

**Core Claim:** Formal verification strategies (grammar constraints, static analysis, SMT-guided repair) target largely independent error classes, and when combined in a pipeline ordered by abstraction level, their combined effectiveness exceeds individual strategy improvements through multiplicative error reduction.

**Supporting Evidence:**
1. Grammar constraints reduce compilation errors >50% (Mundler et al. 2025)
2. Static analysis reduces security issues 40%→13% (Blyth et al. 2025)
3. SMT-guided repair achieves 75-82% pass@1 (ContractEval 2025)

**Strengths:**
- Each strategy has demonstrated effectiveness in isolation
- Clear causal mechanism: each stage filters different error class
- Testable predictions with quantitative thresholds

**Expected Outcomes:**
- P1: Error overlap < 30% (Jaccard index)
- P2: Each stage contributes > 5% marginal improvement
- P3: Synergy coefficient S between 0.8-1.2

### 5.2 Antithesis (H0-Based)

**Null Hypothesis (H0):** The synergy coefficient S = 1.0 (±0.2), indicating that combining verification strategies produces purely additive effects with no interaction.

**Counter-Arguments:**
1. Error classes may share common root causes (e.g., type error causing both compilation failure and security vulnerability)
2. Tool implementations may have overlapping coverage
3. Sequential pipeline may introduce interference (upstream fixes create downstream issues)

**Potential Failure Points:**
- R1: Error class overlap > 30% indicates redundancy
- R3: Tool bugs confound measurement
- R4: Different pipeline orderings might yield better results

**Conditions Under Which H0 Would Be Supported:**
- If Jaccard index >= 0.30 for any strategy pair
- If synergy coefficient S < 0.8 (interference) or > 1.2 (unexpected synergy)
- If mechanism steps H-M1, H-M2, H-M3 show redundant improvements

### 5.3 Synthesis

**Balanced Assessment:**

The hypothesis H-VerifPipeline-v1 presents a testable claim that error classes are independent and pipeline composition yields multiplicative benefits. However, the null hypothesis raises valid concerns regarding potential overlap between error classes and interference between pipeline stages.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Explicitly tests independence assumption before proceeding
2. **Sequential mechanism testing (H-M1-M4):** Tests each causal chain step independently
3. **Gate conditions:** Allow early detection of H0 support at each stage

**Conditions for Thesis Support:**
- All MUST_WORK gates pass (H-E1, H-M1)
- Jaccard < 0.30 confirmed
- Synergy coefficient 0.8 <= S <= 1.2

**Conditions for Antithesis Support:**
- H-E1 fails (overlap >= 30%)
- H-M1 fails (grammar constraints don't reduce compilation errors)
- S < 0.8 (significant interference)

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated, multiplicative model confirmed
2. **Partial Support:** Some H-M fail → Refined thesis with documented limitations
3. **No Support:** H-E1 or H-M1 fail → Antithesis supported, strategies are redundant

### 5.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Error classes independent | May share common causes | H-E1 tests overlap |
| Mechanism | Each stage filters distinct errors | Overlapping coverage | H-M1-3 test marginal contribution |
| Scope | Applies to standard benchmarks | Limited generalization | Two-model design + scoped claims |
| Performance | Multiplicative improvement | Merely additive | H-M4 measures synergy coefficient |

**Overall Robustness Score:** High

**Confidence in Verification Plan:** 0.80

---

## 6. Executive Summary

**Main Hypothesis:** Under standard benchmarks, combining formal verification strategies in an ordered pipeline yields multiplicative error reduction due to error class independence.
- ID: H-VerifPipeline-v1, Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 5 total
  - H-E: 1, H-M: 4
- Phases: 2 phases over 7 weeks
- Critical Gates: 2 decision points

**Risk Assessment:** Medium
- Primary concerns: Error class overlap (R1), benchmark representativeness (R2)

**Immediate Action:** Begin Phase 2C with H-E1 experiment design

---

## 7. Conclusions

### 7.1 Key Achievements

- 5 hypotheses across 2 phases (Foundation + Mechanisms)
- H0 addressed: Synergy coefficient S = 1.0 indicates purely additive effects

### 7.2 Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: Error class independence validation
- Gate 1: MUST PASS (Jaccard < 0.30)

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1: Grammar constraints reduce compilation errors
- H-M2: Static analysis identifies semantic patterns
- H-M3: SMT-guided repair enforces specification satisfaction
- H-M4: Pipeline composition enables multiplicative reduction
- Gate 2: H-M1 must pass

### 7.3 Critical Decision Points

1. **Gate 1 (Foundation):** H-E1 must pass (Jaccard < 0.30)
   - FAIL → STOP, reassess multiplicative model
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - CRITICAL FAIL → Execute failure response
   - OPTIONAL FAIL → Document limitation

### 7.4 Open Questions

- Optimal pipeline ordering (tested assumption: syntax→semantics→specs)
- Generalization beyond HumanEval to CodeContests or real codebases
- Model-specific effects on error overlap structure

### 7.5 Recommendations

1. **Immediate Actions:**
   - Start Phase 2C with H-E1 experiment design
   - Set up measurement infrastructure for Jaccard computation

2. **Resource Allocation:**
   - Allocate 7 weeks for critical path
   - Reserve buffer for gate failures

3. **Failure Management:**
   - Document all failures with quantitative evidence
   - Execute PIVOT strategies as defined

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-VerifPipeline-v1)
- **Schema Version:** 10.0.0

### B. MCP Tool Usage Summary
- **Total MCP calls:** 2
- **Tools:** scientificmethod (2x for H-E1 hypothesis + experiment design)

### C. Established Facts (BUILD_ON - Not Re-Verified)
1. Grammar-constrained decoding reduces compilation errors by >50%
2. Static analysis feedback reduces security issues from 40% to 13%
3. SMT-guided repair can enforce specification satisfaction (75-82% pass@1)
4. HumanEval and MBPP exist with test cases
5. HumanEval-Verus provides formal specifications for 23 problems

---

*Generated by Phase 2B Planning Workflow*
*Status: Complete*
*Completed At: 2026-08-12*
