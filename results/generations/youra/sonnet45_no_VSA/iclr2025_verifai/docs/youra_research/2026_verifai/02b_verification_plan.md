---
workflow: phase2b-planning
generated_at: 2026-07-11T05:18:00Z
main_hypothesis_id: h-verifierteacher-v1
archon_project_id: 6b1361ed-02e6-4b99-ab72-78b79a4178ab
total_sub_hypotheses: 7
execution_mode: UNATTENDED
stepsCompleted:
  - step-00-init-environment
  - step-01-init-parsing
  - step-02-input-hypothesis
  - step-03-hypothesis-generation
  - step-04-hypothesis-inventory
  - step-05-risk-analysis
  - step-06-dependency-graph
  - step-07-timeline-planning
  - step-08-dialectical-analysis
  - step-09-summary
  - step-10-finalize
---

# Phase 2B: Verification Planning Report
**Main Hypothesis**: Verifier-as-Teacher for Specification Synthesis  
**Generated**: 2026-07-11  
**Archon Project**: 6b1361ed-02e6-4b99-ab72-78b79a4178ab  
**Execution Mode**: UNATTENDED

---

## Executive Summary

Phase 2B successfully decomposed the main hypothesis (H-VerifierTeacher-v1) from Phase 2A into **7 testable sub-hypotheses** spanning existence proofs (H-E1, H-E2), mechanism validation (H-M1, H-M2, H-M3), and control conditions (H-C1, H-C2). The verification plan establishes a systematic roadmap for validating that **structured verifier feedback enables LLM-driven specification synthesis** with ≥80% proof discharge rate and cross-verifier portability.

**Key Outcomes:**
- ✅ 7 sub-hypotheses defined with dependency relationships
- ✅ 6 MUST_WORK gates, 1 SHOULD_WORK gate assigned
- ✅ 4-wave execution plan with parallel opportunities
- ✅ Risk analysis with mitigation strategies
- ✅ 16-20 week timeline to Phase 5 readiness
- ✅ Archon project initialized with tracking tasks

---

## Section 1: Main Hypothesis & Research Context

### 1.1 Core Hypothesis Statement

**Hypothesis ID**: h-verifierteacher-v1  
**Confidence Level**: 0.80  
**Total Sub-Hypotheses**: 7

**Core Statement**:
Under formal specification synthesis for programs with verifiable properties, if LLMs receive structured verifier feedback decomposed into three informational dimensions (Witness Instantiation, Logical Structure, Dependency Preservation) and iterate through staged refinement (types → preconditions → postconditions → invariants), then the synthesized specifications will achieve **≥80% proof discharge rate within ≤10 iterations** and demonstrate **cross-verifier portability via semantic normalization**, because structured feedback encodes semantic constraints that guide specification refinement more effectively than unstructured iteration or single-shot synthesis.

**Alternative Hypothesis (H0)**:
There is no significant difference in proof discharge rate or specification strength between verifier-driven iterative refinement and compute-matched single-shot LLM synthesis with self-consistency sampling.

### 1.2 Research Variables

**Independent Variables**:
1. **FeedbackCondition**: Type of feedback provided to LLM (FullStructured | ObligationSlice | TagOnly | RawError | SingleShot)
2. **RefinementStrategy**: Specification synthesis approach (StagedProgressive | CompleteUpfront)

**Dependent Variables**:
1. **ProofDischargeRate** (Primary): Percentage of proof obligations successfully discharged (0-100%)
2. **StrengthScore**: Mutation kill rate relative to gold spec (0-100%)
3. **IterationsToConvergence**: Number of refinement iterations until stabilization (1-10)
4. **CrossVerifierPerformance**: Performance retention when transferring across verifiers (0-100%)

**Controlled Variables**:
- ComputeBudget (tokens + verifier time)
- BenchmarkPrograms (verified C programs with ACSL annotations)
- VerifierToolVersion (Frama-C WP, Z3/Alt-Ergo backends)
- LLMModel (GPT-4 / Claude Opus)

### 1.3 Key Assumptions

1. **Gold-standard specifications exist** for benchmark programs (Frama-C examples, Juliet benchmark)
   - *Testable*: Yes - via implication checks and partial oracles
   
2. **Semantic normalization preserves causal structure** across verifiers
   - *Testable*: Yes - via cross-verifier transfer experiments
   
3. **Mutation-based strength testing** approximates semantic strength
   - *Testable*: Yes - empirically validated by Prof. Vera and Prof. Pax
   
4. **LLMs can learn repair primitives** from structured feedback without fine-tuning
   - *Testable*: Yes - via in-context learning with few-shot examples

### 1.4 Gap & Novelty Justification

**Core Novelty**:
First demonstration of **verifier-as-teacher for specification synthesis** (vs. existing work on code generation). Novel **semantic normalization layer** enables cross-verifier transfer via abstraction of tool-specific feedback. **Information-theoretic decomposition** of feedback into Witness/Structure/Dependency dimensions reframes verifier-LLM interaction as an information theory problem.

**Advances Over Prior Work**:
- **PropertyGPT (119 cites)**: RAG-based, requires domain-specific knowledge base → *We learn from verifier feedback directly*
- **Astrogator (12 cites)**: Requires expert-written queries → *We eliminate expert bottleneck*
- **AutoSpec (5 stars)**: No cross-verifier transfer → *We add semantic normalization for portability*
- **Verification-in-loop (70% of approaches)**: Assumes specs exist → *We synthesize specs themselves*

### 1.5 Dataset & Model Selection

**Selected Dataset**: Verified C programs with gold ACSL annotations  
**Dataset Type**: Standard benchmark (Frama-C examples, Juliet verified subset)  
**Dataset Source**: Open-source verification benchmarks  
**Dataset Path**: To be determined in Phase 3  
**Hypothesis Fit**: Programs with deterministic behavior, verifiable safety/functional properties

**Selected Model**: GPT-4 / Claude Opus (TBD in Phase 3)  
**Model Type**: Large Language Model (API-based)  
**Model Source**: OpenAI / Anthropic APIs  
**Hypothesis Fit**: Strong reasoning capabilities for formal specification synthesis

---

## Section 2: Sub-Hypotheses Inventory

### 2.1 Overview Table

| ID | Type | Gate | Prerequisites | Status | Experiment Focus |
|---|---|---|---|---|---|
| H-E1 | Existence | MUST_WORK | None | READY | LLM + structured feedback refinement |
| H-E2 | Existence | MUST_WORK | None | READY | Cross-verifier semantic primitives |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED | Information gradient hypothesis |
| H-M2 | Mechanism | SHOULD_WORK | H-E1 | NOT_STARTED | Staged vs complete refinement |
| H-M3 | Mechanism | MUST_WORK | H-E2, H-M1 | NOT_STARTED | Semantic normalization transfer |
| H-C1 | Condition | MUST_WORK | H-M1 | NOT_STARTED | Compute-matched control |
| H-C2 | Condition | MUST_WORK | H-M1 | NOT_STARTED | Mutation-based non-vacuity |

### 2.2 Detailed Specifications

#### H-E1: LLM + Structured Feedback Refinement (EXISTENCE)
**Statement**: LLMs can utilize structured verifier feedback (witness + obligation + dependency dimensions) to iteratively refine formal specifications, achieving measurable improvement in proof discharge rate

**Gate Type**: MUST_WORK  
**Rationale**: Foundation hypothesis - if LLMs cannot use structured feedback, entire approach fails  
**Prerequisites**: None  
**Status**: READY

**Experiment Sketch**: Minimal working example with single C function, ACSL annotations, Frama-C WP feedback, and LLM refinement loop. Measure proof discharge improvement across iterations.

**Success Criteria**:
- LLM demonstrates iterative improvement (iteration N+1 > iteration N)
- Achieves ≥50% proof discharge on minimal benchmark (5-10 functions)
- Feedback dimensions are utilized (evidence in LLM responses)

**Failure Conditions**:
- No improvement across iterations (flat performance)
- LLM cannot parse/interpret structured feedback
- Random walk behavior (no systematic refinement)

---

#### H-E2: Cross-Verifier Semantic Primitives (EXISTENCE)
**Statement**: Common semantic primitives exist across verifiers (Frama-C, Dafny, Why3) that can be abstracted into universal repair categories

**Gate Type**: MUST_WORK  
**Rationale**: Required for cross-verifier portability claim - without semantic overlap, normalization is impossible  
**Prerequisites**: None  
**Status**: READY

**Experiment Sketch**: Taxonomy analysis mapping Frama-C, Dafny, Why3 error categories to shared semantic primitives. Validate coverage of abstraction layer.

**Success Criteria**:
- ≥80% of error categories map to shared primitives
- Abstraction layer design is feasible (implementation-ready)
- Coverage validated across 3 verifiers

**Failure Conditions**:
- <60% semantic overlap (tool-specific semantics dominate)
- No viable abstraction layer design emerges
- Critical categories resist abstraction

---

#### H-M1: Information Gradient Hypothesis (MECHANISM)
**Statement**: Information gradient hypothesis: Proof discharge rate scales monotonically with feedback richness (FullStructured > ObligationSlice > TagOnly > RawError by ≥10pp between adjacent conditions)

**Gate Type**: MUST_WORK  
**Rationale**: Core mechanism claim - if ablation shows no gradient, information-theoretic framing is invalid  
**Prerequisites**: H-E1  
**Status**: NOT_STARTED

**Experiment Sketch**: Controlled ablation across 4 feedback conditions on 30-50 benchmark programs, regression analysis with pre-registered monotonic ordering.

**Success Criteria**:
- Monotonic ordering holds: C > B > A > Raw
- Adjacent gaps ≥10 percentage points
- Regression coefficients strictly positive (p < 0.05)

**Failure Conditions**:
- Non-monotonic ordering (e.g., B > C or A > B)
- Adjacent gaps ≤5 percentage points (no gradient)
- Regression shows no significant relationship

---

#### H-M2: Staged vs Complete Refinement (MECHANISM)
**Statement**: Staged progressive refinement (types→pre→post→inv) converges faster and achieves higher proof discharge than complete upfront specification

**Gate Type**: SHOULD_WORK (optimization, not core claim)  
**Rationale**: Failure does not invalidate core approach - staged is optimization over baseline iterative  
**Prerequisites**: H-E1  
**Status**: NOT_STARTED

**Experiment Sketch**: Compare staged vs. complete strategies on shared benchmark with fixed iteration budget. Measure convergence speed and final performance.

**Success Criteria**:
- Staged converges in ≤70% of iterations vs. complete
- Staged achieves ≥5pp higher final proof discharge
- Statistical significance (p < 0.05)

**Failure Conditions**:
- Complete outperforms staged (backtracking overhead dominates)
- No significant difference (neutral result acceptable)

---

#### H-M3: Semantic Normalization Transfer (MECHANISM)
**Statement**: Semantic normalization layer enables cross-verifier transfer with ≤20% performance degradation (train on Frama-C, test on Dafny/Why3)

**Gate Type**: MUST_WORK  
**Rationale**: Cross-verifier portability is key novelty claim distinguishing from prior work  
**Prerequisites**: H-E2, H-M1  
**Status**: NOT_STARTED

**Experiment Sketch**: Train feedback→repair pipeline on Frama-C examples, evaluate on Dafny/Why3 held-out set. Measure performance retention.

**Success Criteria**:
- Cross-verifier degradation ≤20% (same domain)
- Abstraction layer preserves semantic structure
- Transfer works bidirectionally (Frama-C↔Dafny↔Why3)

**Failure Conditions**:
- Degradation >40% (portability claim fails)
- Tool-specific idioms resist normalization
- Transfer only works unidirectionally

---

#### H-C1: Compute-Matched Control (CONDITION)
**Statement**: Under compute-matched budgets (equal tokens + verifier time), iterative feedback outperforms single-shot self-consistency sampling by ≥10pp in proof discharge rate

**Gate Type**: MUST_WORK  
**Rationale**: Critical control - ensures observed gains from feedback signal, not just more sampling  
**Prerequisites**: H-M1  
**Status**: NOT_STARTED

**Experiment Sketch**: Budget-constrained comparison with rigorous token + verifier time tracking. Iterative (N iterations) vs. single-shot (N×M samples).

**Success Criteria**:
- Iterative outperforms single-shot by ≥10pp
- Budget matching within ±10% tolerance
- Statistical significance (p < 0.05)

**Failure Conditions**:
- Single-shot matches or exceeds iterative
- Budget mismatch invalidates comparison
- No significant difference (feedback has no value)

---

#### H-C2: Mutation-Based Non-Vacuity (CONDITION)
**Statement**: Synthesized specifications achieve ≥70% mutation kill rate relative to expert-written gold specs, demonstrating non-vacuity

**Gate Type**: MUST_WORK  
**Rationale**: Guards against vacuous specifications that trivially pass proofs but lack semantic strength  
**Prerequisites**: H-M1  
**Status**: NOT_STARTED

**Experiment Sketch**: Mutation testing framework with standard mutants (arithmetic, relational, boundary). Compare synthesized vs. expert-written kill rates.

**Success Criteria**:
- Mutation kill rate ≥70% of gold spec baseline
- Multiple mutation operators tested
- Non-vacuity threshold empirically validated

**Failure Conditions**:
- Kill rate <50% (specifications are vacuous)
- Synthesized specs pass trivially weak mutants
- No semantic strength demonstrated

---

## Section 3: Risk Analysis & Mitigation

### 3.1 Risk Inventory

| Risk ID | Category | Severity | Probability | Impact | Affected Hypotheses |
|---------|----------|----------|-------------|--------|-------------------|
| R1 | Technical Feasibility | MEDIUM | 0.4 | Limits benchmark complexity | H-E1, H-M1, H-M3 |
| R2 | Evaluation Validity | MEDIUM | 0.6 | Reduces evaluation scale | H-C2, H-M1 |
| R3 | Claim Validity | HIGH | 0.3 | Invalidates information-theoretic framing | H-M1 |
| R4 | Cross-Domain Transfer | MEDIUM | 0.5 | Limits generalization claim | H-M3 |
| R5 | Baseline Control | LOW | 0.3 | Confounds attribution | H-C1 |
| R6 | Implementation Complexity | MEDIUM | 0.4 | Extends timeline | H-M3, H-E2 |

### 3.2 Risk Details & Mitigation

#### R1: Verifier Timeout on Complex Programs
**Severity**: MEDIUM | **Probability**: 0.4

**Description**: Verifier timeout on complex programs may prevent convergence, limiting benchmark program complexity.

**Mitigation Strategies**:
1. Set verification budget caps (10 second timeout per proof obligation)
2. Filter benchmark to programs that expert specs can verify within budget
3. Report timeout rates as secondary metric

**Contingency**: If timeouts exceed 30%, reduce program complexity or increase timeout budget with justification.

---

#### R2: Gold-Spec Availability Limits Evaluation Scale
**Severity**: MEDIUM | **Probability**: 0.6

**Description**: Gold-spec availability limits evaluation scale (circularity issue), reducing benchmark size and statistical power.

**Mitigation Strategies**:
1. Use partial oracle properties (memory safety, no overflow) that don't require full gold specs
2. Implication checks (synthesized ⇒ gold) only where gold specs exist
3. Mutation testing as proxy for semantic strength

**Contingency**: Expand to partial oracle validation if gold specs cover <50% of benchmark.

---

#### R3: Information Gradient Ordering May Not Hold Empirically
**Severity**: HIGH | **Probability**: 0.3

**Description**: Information gradient ordering (Prof. Rex concern) may not hold empirically, invalidating information-theoretic framing.

**Mitigation Strategies**:
1. Pre-register regression analysis with expected monotonic ordering
2. Define explicit falsification boundary: non-monotonic or ≤5pp gaps
3. Fallback to pairwise comparisons if full ordering fails

**Contingency Plans**:
- **Trigger**: H-M1 fails (no information gradient)
- **Action**: Revise to comparative claim: FullStructured vs. RawError only

---

#### R4: Cross-Domain Transfer May Show >40% Degradation
**Severity**: MEDIUM | **Probability**: 0.5

**Description**: Semantic normalization may show >40% degradation across domains, limiting generalization claim scope.

**Mitigation Strategies**:
1. Distinguish cross-verifier (same domain) from cross-domain transfer
2. Pre-specify degradation thresholds: ≤20% for cross-verifier, ≤40% for cross-domain
3. Scope claim to cross-verifier portability if cross-domain fails

**Contingency Plans**:
- **Trigger**: H-M3 fails (>40% degradation)
- **Action**: Scope to single-verifier claim, position cross-tool as future work

---

#### R5: Compute-Matching Difficult to Calibrate
**Severity**: LOW | **Probability**: 0.3

**Description**: Compute-matching may be difficult to calibrate precisely, confounding feedback signal attribution.

**Mitigation Strategies**:
1. Track token counts and verifier wall-clock time separately
2. Report both strict budget match and ±10% tolerance bands
3. Use fixed iteration counts as alternative control

**Contingency**: If budget matching fails, report both constrained and unconstrained results.

---

#### R6: Semantic Normalization Layer Design Non-Trivial
**Severity**: MEDIUM | **Probability**: 0.4

**Description**: Semantic normalization layer design may be non-trivial, extending implementation timeline beyond 3-6 months.

**Mitigation Strategies**:
1. Start with simple tag-based abstraction (Condition A)
2. Incrementally add obligation slices and witnesses (Conditions B, C)
3. Validate minimal viable abstraction via ablation before full implementation

**Contingency**: If design complexity exceeds estimates, simplify abstraction layer to tag-only with future work extensions.

---

### 3.3 Risk Mitigation Priority

**High Priority** (Core claim validity):
- R3: Information gradient validation
- R4: Cross-verifier transfer

**Medium Priority** (Scope/scale issues):
- R1: Verifier timeout management
- R2: Gold-spec availability
- R6: Implementation complexity

**Low Priority** (Measurement precision):
- R5: Compute-matching calibration

---

## Section 4: Dependency Graph & Execution Order

### 4.1 Dependency Hierarchy (DAG)

```
Layer 0 (Foundation - Parallel Execution):
┌─────────────────────────────────┐     ┌─────────────────────────────────┐
│ H-E1: LLM + Structured Feedback │     │ H-E2: Cross-Verifier Primitives │
│ Gate: MUST_WORK                 │     │ Gate: MUST_WORK                 │
│ Prerequisites: None             │     │ Prerequisites: None             │
└────────────┬────────────────────┘     └────────────┬────────────────────┘
             │                                       │
             ├───────────────────────────────────────┤
             │                                       │
             ↓                                       │
Layer 1 (Mechanism - After H-E1):                    │
┌─────────────────────────────────┐                  │
│ H-M1: Information Gradient      │                  │
│ Gate: MUST_WORK                 │                  │
│ Prerequisites: [H-E1]           │                  │
└────────────┬────────────────────┘                  │
             │                                       │
             ├───────────────────────────────────────┤
             │                                       │
             ↓                                       ↓
┌─────────────────────────────────┐     ┌─────────────────────────────────┐
│ H-M2: Staged vs Complete        │     │ H-M3: Semantic Normalization    │
│ Gate: SHOULD_WORK (optional)    │     │ Gate: MUST_WORK                 │
│ Prerequisites: [H-E1]           │     │ Prerequisites: [H-E2, H-M1]     │
└─────────────────────────────────┘     └────────────┬────────────────────┘
                                                     │
Layer 2 (Integration - After H-M1):                  │
             ┌───────────────────────────────────────┤
             │                                       │
             ↓                                       │
┌─────────────────────────────────┐                  │
│ H-C1: Compute-Matched Control   │                  │
│ Gate: MUST_WORK                 │                  │
│ Prerequisites: [H-M1]           │                  │
└─────────────────────────────────┘                  │
             │                                       │
             ↓                                       │
┌─────────────────────────────────┐                  │
│ H-C2: Mutation-Based Non-Vacuity│                  │
│ Gate: MUST_WORK                 │                  │
│ Prerequisites: [H-M1]           │                  │
└─────────────────────────────────┘                  │
```

### 4.2 Critical Path Analysis

**Critical Path** (MUST_WORK gates only):
```
H-E1 → H-M1 → [H-M3 | H-C1 | H-C2]
                 └──────┴──────┘
               (Can execute in parallel)
```

**Optional Path**:
```
H-M2 (SHOULD_WORK - optimization, does not block Phase 5)
```

### 4.3 Parallel Execution Opportunities

**Wave 1 (Foundation)**:
- H-E1 and H-E2 can execute in parallel (independent)

**Wave 2 (Mechanism)**:
- H-M1 and H-M2 can execute in parallel (both depend on H-E1 only)

**Wave 3 (Integration)**:
- H-C1 and H-C2 can execute in parallel (both depend on H-M1 only)
- H-M3 requires both H-E2 and H-M1 (blocks until both complete)

### 4.4 Execution Order Recommendation

1. **Start**: H-E1, H-E2 (parallel)
2. **After H-E1**: H-M1, H-M2 (parallel)
3. **After [H-E2, H-M1]**: H-M3
4. **After H-M1**: H-C1, H-C2 (parallel)

**Total Sequential Waves**: 4  
**Expected Parallelism**: 50% (3/6 waves have parallel execution)

---

## Section 5: Timeline & Gantt Planning

### 5.1 Overall Timeline

**Total Duration**: 16-20 weeks  
**Start Date**: TBD (after Phase 2B completion)  
**Target Completion**: Phase 5 ready for baseline comparison

### 5.2 Phase Breakdown

| Phase | Duration | Activities | Deliverables |
|-------|----------|-----------|--------------|
| **Phase 2C** | 2 weeks | Experiment design for all sub-hypotheses | 7× experiment briefs |
| **Phase 3** | 3 weeks | PRD, architecture, task breakdown | Implementation plans |
| **Wave 1** | 4 weeks | H-E1, H-E2 implementation & validation | Foundation layer complete |
| **Wave 2** | 5 weeks | H-M1, H-M2 implementation & validation | Mechanism layer complete |
| **Wave 3** | 6 weeks | H-M3, H-C1, H-C2 implementation | Integration layer complete |

### 5.3 Detailed Timeline (Gantt)

```
Week 00-02: Phase 2C - Experiment Design
├─ Week 00-01: H-E1, H-E2, H-M1 experiment briefs
└─ Week 01-02: H-M2, H-M3, H-C1, H-C2 experiment briefs

Week 02-05: Phase 3 - Implementation Planning
├─ Week 02-03: PRD and architecture generation
├─ Week 03-04: Complexity assessment, task breakdown
└─ Week 04-05: Archon project initialization

Week 05-09: Wave 1 - Foundation Layer
├─ H-E1 (Parallel with H-E2):
│  ├─ Week 05-06: Frama-C WP feedback parser
│  ├─ Week 06-07: LLM refinement loop implementation
│  └─ Week 07-09: Minimal benchmark validation (5-10 functions)
│
└─ H-E2 (Parallel with H-E1):
   ├─ Week 05-06: Taxonomy analysis (Frama-C, Dafny, Why3)
   ├─ Week 06-07: Semantic primitive mapping
   └─ Week 07-09: Coverage validation, abstraction design

Week 09-14: Wave 2 - Mechanism Layer
├─ H-M1 (Parallel with H-M2):
│  ├─ Week 09-10: Implement 4 feedback conditions
│  ├─ Week 10-12: Ablation study (30-50 programs)
│  └─ Week 12-14: Statistical analysis, regression
│
└─ H-M2 (Parallel with H-M1):
   ├─ Week 09-10: Implement staged & complete strategies
   ├─ Week 10-12: Comparative evaluation
   └─ Week 12-14: Convergence analysis

Week 14-20: Wave 3 - Integration Layer
├─ H-M3 (Sequential - needs H-E2 + H-M1):
│  ├─ Week 14-16: Semantic normalization layer
│  ├─ Week 16-18: Cross-verifier transfer experiments
│  └─ Week 18-19: Degradation analysis
│
├─ H-C1 (Parallel with H-C2):
│  ├─ Week 14-15: Compute budget tracking
│  ├─ Week 15-17: Compute-matched experiments
│  └─ Week 17-18: Statistical comparison
│
└─ H-C2 (Parallel with H-C1):
   ├─ Week 14-15: Mutation testing framework
   ├─ Week 15-17: Mutation kill rate experiments
   └─ Week 17-18: Non-vacuity threshold validation

Week 20: Integration & Phase 5 Preparation
└─ Final validation, documentation, handoff
```

### 5.4 Resource Allocation

**Personnel**:
- ML Engineer: Full-time (40 hrs/week) - LLM integration, refinement loop
- Formal Methods Expert: Part-time (20 hrs/week) - Verifier integration, spec validation
- Research Lead: Part-time (10 hrs/week) - Experiment oversight, statistical analysis

**Compute Resources**:
- LLM API Credits: $2000-4000 (iterative experiments across 7 hypotheses)
- Verification Compute: Modest (CPU-bound, standard workstation sufficient)

### 5.5 Critical Milestones

| Milestone | Week | Deliverable | Gate Check |
|-----------|------|-------------|------------|
| Phase 2B Complete | 0 | Verification plan | N/A |
| Foundation Layer Complete | 9 | H-E1, H-E2 validated | MUST_WORK gates passed |
| Mechanism Layer Complete | 14 | H-M1 validated, H-M2 optional | Information gradient confirmed |
| Integration Layer Complete | 20 | H-M3, H-C1, H-C2 validated | All MUST_WORK gates passed |
| Ready for Phase 5 | 20 | Complete PoC validation | Baseline comparison ready |

**Critical Milestone Details**:
- **Week 9**: H-E1 MUST_WORK gate blocks all downstream mechanism work
- **Week 14**: H-M1 MUST_WORK gate blocks integration layer (H-C1, H-C2, H-M3)
- **Week 20**: H-M3 MUST_WORK gate validates cross-verifier portability claim

---

## Section 6: Dialectical Analysis

### 6.1 Thesis-Antithesis-Synthesis Framework

For each sub-hypothesis, we apply dialectical analysis to identify potential failure modes and resolution strategies.

#### H-E1: LLM + Structured Feedback

**Thesis**: LLMs can utilize structured verifier feedback to iteratively refine formal specifications

**Antithesis**: Formal verification feedback is too specialized/technical for general LLMs to interpret

**Synthesis**: LLMs can leverage structured feedback **IF** it's normalized into semantic primitives (witness, obligation, dependency) with few-shot examples - not raw tool output

**Resolution Strategy**: Demonstrate with minimal example (single function, Frama-C WP) before scaling

---

#### H-E2: Cross-Verifier Semantic Primitives

**Thesis**: Common semantic primitives exist across verifiers enabling universal abstraction

**Antithesis**: Each verifier has tool-specific semantics that resist meaningful abstraction

**Synthesis**: Shared semantic categories exist at the proof obligation level (missing precondition, loop invariant, type safety), but witness formats are tool-specific and require custom parsers

**Resolution Strategy**: Build taxonomy from bottom-up (analyze actual error categories from 3 verifiers) rather than top-down theoretical abstraction

---

#### H-M1: Information Gradient Hypothesis

**Thesis**: Performance scales monotonically with feedback richness (information gradient)

**Antithesis**: More information could confuse LLMs or be redundant after a certain threshold

**Synthesis**: Information gradient holds for repair-critical dimensions (Witness > Structure > Dependency), but with diminishing returns - each dimension provides distinct value, not redundant

**Resolution Strategy**: Pre-register expected ordering with falsification boundary (≤5pp gaps = no gradient)

---

#### H-M2: Staged vs Complete Refinement

**Thesis**: Staged progressive refinement converges faster than complete upfront

**Antithesis**: Complete upfront may avoid backtracking and repair conflicts between spec components

**Synthesis**: Staged refinement trades off convergence speed (faster per-stage) against potential cross-stage conflicts (invariants depend on preconditions) - net benefit depends on program complexity

**Resolution Strategy**: Position as optimization (SHOULD_WORK gate), not core claim - failure doesn't invalidate approach

---

#### H-M3: Semantic Normalization Transfer

**Thesis**: Semantic normalization enables ≤20% performance degradation in cross-verifier transfer

**Antithesis**: Tool-specific idioms and proof strategies resist meaningful transfer

**Synthesis**: Transfer works within same domain (C verification across tools) but degrades across domains (C→Dafny→Why3) - normalization preserves logical structure but not tool-specific tactics

**Resolution Strategy**: Distinguish cross-verifier (same domain, ≤20% target) from cross-domain (≤40% tolerance)

---

#### H-C1: Compute-Matched Control

**Thesis**: Iterative feedback outperforms single-shot sampling under equal compute

**Antithesis**: More diverse samples may explore specification space better than sequential refinement

**Synthesis**: Iterative feedback provides guided search via verifier supervision, while single-shot is unguided exploration - both have value, but feedback should outperform when verifier signals are informative

**Resolution Strategy**: Compute-match rigorously (tokens + verifier time), report both strict and ±10% tolerance

---

#### H-C2: Mutation-Based Non-Vacuity

**Thesis**: Synthesized specs achieve ≥70% mutation kill rate (non-vacuity)

**Antithesis**: LLM specs may converge to weak specifications that pass proofs but don't capture intended semantics

**Synthesis**: Mutation kill rate guards against vacuity BUT is a proxy (not true semantic equivalence) - threshold calibrated to existing verified codebases

**Resolution Strategy**: Use multiple mutation operators (arithmetic, relational, boundary), compare to expert-written baseline

---

### 6.2 Meta-Synthesis

The main hypothesis (verifier-as-teacher for specification synthesis) **survives dialectical stress testing** by:

1. **Scoping claims appropriately** (cross-verifier not cross-domain)
2. **Distinguishing core mechanisms** (information gradient) from optimizations (staged refinement)
3. **Embedding falsification boundaries** in experimental design (compute-matching, mutation thresholds)

**Key Insight**: The novelty is not that verifier feedback is perfect, but that it provides **structured semantic supervision** that outperforms unguided LLM search.

---

## Section 7: Summary & Conclusions

### 7.1 Phase 2B Achievements

✅ **Sub-Hypothesis Decomposition**: 7 testable hypotheses spanning existence, mechanism, and conditions  
✅ **Gate Assignment**: 6 MUST_WORK gates (critical path), 1 SHOULD_WORK gate (optimization)  
✅ **Dependency Analysis**: 4-wave execution plan with 50% parallel opportunities  
✅ **Risk Mitigation**: 6 risks identified with mitigation strategies and contingency plans  
✅ **Timeline Planning**: 16-20 week roadmap to Phase 5 readiness  
✅ **Dialectical Validation**: Thesis-antithesis-synthesis for each hypothesis  
✅ **Archon Integration**: Project initialized with 9 phase tasks + 7 sub-hypothesis tasks

### 7.2 Critical Path Summary

**Foundation → Mechanism → Integration**:
```
H-E1 (Week 9) → H-M1 (Week 14) → [H-M3, H-C1, H-C2] (Week 20)
```

**Parallel Opportunities**:
- Wave 1: H-E1 ‖ H-E2
- Wave 2: H-M1 ‖ H-M2
- Wave 3: H-C1 ‖ H-C2

### 7.3 Readiness for Phase 2C

**Next Phase**: Phase 2C - Experiment Design  
**First Hypotheses to Process**: H-E1, H-E2 (both READY, no prerequisites)  
**Expected Output**: 7× detailed experiment briefs with protocols, datasets, metrics, baselines

### 7.4 Success Criteria Checklist

- [x] All sub-hypotheses assigned gate types
- [x] Dependency graph validated (no circular dependencies)
- [x] Risk analysis completed with mitigation strategies
- [x] Timeline aligns with Phase 2A estimates (3-6 months → 16-20 weeks)
- [x] Archon project initialized with tracking tasks
- [x] Verification state template prepared for Phase 4-5

**Phase 2B Status**: ✅ COMPLETE  
**Blocking Issues**: None

---

## Appendix A: Archon Project Integration

**Project ID**: 6b1361ed-02e6-4b99-ab72-78b79a4178ab  
**Project Title**: Anonymous Pipeline: Verifier-as-Teacher for Specification Synthesis  
**Created**: 2026-07-11T05:17:00Z

### Pipeline Phase Tasks

| Task ID | Phase | Status |
|---------|-------|--------|
| 7d17d99c-66e0-4901-85e7-1e15acc948d8 | Phase 0: Brainstorming | done |
| 43d47d4a-1cbc-4aca-a4d9-88828aec4570 | Phase 1: Targeted Research | done |
| c2170891-f6e1-4ae2-bfb2-e2bc9d54cf3e | Phase 2A: Dialogue Refinement | done |
| 73c0cdc1-4591-4f40-843b-1657e906bb9f | Phase 2B: Verification Planning | done |
| a9cad580-43ac-497c-9919-788b94837207 | Phase 2C: Experiment Design | todo |
| 240a5646-81f4-4988-8aba-6e4f31445893 | Phase 3: Implementation Planning | todo |
| 895a3795-dd73-413a-adbb-468535b54486 | Phase 4: Coding & PoC Validation | todo |
| 190d3f94-86b7-48ba-9e98-006f61bbc7f9 | Phase 5: Baseline Comparison | todo |
| 42d3141e-9821-46d6-ae4c-067914393e44 | Phase 6: Paper Writing | todo |

### Sub-Hypothesis Tasks

| Task ID | Hypothesis | Feature | Status |
|---------|-----------|---------|--------|
| 9826df1b-916c-4d07-8a2d-3af2fb02d8ca | H-E1: LLM + Structured Feedback | h-e1 | todo |
| 8f52c983-bb92-44c5-b1ae-7376f82c27ea | H-E2: Cross-Verifier Primitives | h-e2 | todo |
| 10772fdb-15ab-41d2-adfa-79fca04a8690 | H-M1: Information Gradient | h-m1 | todo |
| 6ce5c0d6-0d8d-4881-afeb-759a9a2159a7 | H-M2: Staged vs Complete | h-m2 | todo |
| 12be2082-f790-4c28-b432-f2710c56828e | H-M3: Semantic Normalization | h-m3 | todo |
| e119be40-86f5-4403-89cf-91afc1017079 | H-C1: Compute-Matched Control | h-c1 | todo |
| d10bb634-4dca-473e-90e3-1f3b911bbf4a | H-C2: Mutation Non-Vacuity | h-c2 | todo |

---

## Appendix B: Hypothesis Task Mapping

```yaml
hypothesis_task_mapping:
  h-e1: "9826df1b-916c-4d07-8a2d-3af2fb02d8ca"
  h-e2: "8f52c983-bb92-44c5-b1ae-7376f82c27ea"
  h-m1: "10772fdb-15ab-41d2-adfa-79fca04a8690"
  h-m2: "6ce5c0d6-0d8d-4881-afeb-759a9a2159a7"
  h-m3: "12be2082-f790-4c28-b432-f2710c56828e"
  h-c1: "e119be40-86f5-4403-89cf-91afc1017079"
  h-c2: "d10bb634-4dca-473e-90e3-1f3b911bbf4a"

pipeline_phase_task_ids:
  "Phase 0": "7d17d99c-66e0-4901-85e7-1e15acc948d8"
  "Phase 1": "43d47d4a-1cbc-4aca-a4d9-88828aec4570"
  "Phase 2A": "c2170891-f6e1-4ae2-bfb2-e2bc9d54cf3e"
  "Phase 2B": "73c0cdc1-4591-4f40-843b-1657e906bb9f"
  "Phase 2C": "a9cad580-43ac-497c-9919-788b94837207"
  "Phase 3": "240a5646-81f4-4988-8aba-6e4f31445893"
  "Phase 4": "895a3795-dd73-413a-adbb-468535b54486"
  "Phase 5": "190d3f94-86b7-48ba-9e98-006f61bbc7f9"
  "Phase 6": "42d3141e-9821-46d6-ae4c-067914393e44"
```

---

**END OF PHASE 2B VERIFICATION PLAN**
