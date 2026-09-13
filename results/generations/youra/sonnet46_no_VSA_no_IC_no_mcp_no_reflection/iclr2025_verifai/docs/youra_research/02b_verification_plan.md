---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation"]
status: in_progress
hypothesisId: H-FormalFeedbackComparison-v1
totalHypotheses: 5
researchMode: incremental
---

# Verification Plan: Formal Feedback Category Efficiency and Bug-Type Coverage in LLM Code Generation

**Date:** 2026-08-31
**Hypothesis ID:** H-FormalFeedbackComparison-v1
**Confidence:** 0.72
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under LLM code generation on HumanEval and MBPP benchmarks with a fixed backbone (GPT-4o-mini) and fixed repair budget (3 iterations), if the post-generation verifier type is varied across four formal feedback categories (execution monitoring, static analysis, type checking, SMT solving), then correctness-per-overhead efficiency and bug-type coverage profiles will differ systematically across categories, because feedback signal specificity trades off with computational overhead and matches the dominant error types in these benchmarks.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in pass@1 improvement per unit wall-clock overhead between formal feedback categories when applied to the same LLM backbone (GPT-4o-mini) on HumanEval/MBPP.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval + MBPP (standard) | Standard LLM code generation benchmarks with ground-truth test suites; used by all prior formal feedback papers enabling comparison |
| **Model** | GPT-4o-mini | Cost-effective capable model; ~75-80% baseline pass@1 on HumanEval leaves room for improvement; widely accessible for reproducibility |

**Dataset Details:**
- Source: openai/human-eval (GitHub); google-research/mbpp (GitHub)
- Path: Download from public GitHub repos

**Model Details:**
- Type: API-based LLM (OpenAI)
- Source: OpenAI API

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| No feedback (vanilla generation) | GPT-4o-mini baseline ~75-80% pass@1 | HumanEval + MBPP |
| Self-Repair / Execution monitoring (Olausson et al., 2023) | ~5-10% pass@1 improvement (GPT-4) | HumanEval, MBPP |
| Reflexion (Shinn et al., 2023) | HumanEval ~80% → ~91% with GPT-4 + verbal reflection | HumanEval |
| CodeT (Bei Chen et al., 2022) | Improvement via test-based selection | HumanEval |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Auto-extracted Z3 constraints from HumanEval docstrings are sound enough to produce useful counterexamples (~40% problem coverage) | HumanEval docstrings contain type annotations and example I/O; LLM-generated Z3 feasible per training knowledge | SMT category cannot be fairly evaluated; comparison reduces to 3 categories |
| A2 | Bug-type classification from error traces (type/runtime/logic error) is reliable enough for stratified analysis | Pyright errors are typed; runtime errors have exception types; logic errors defined as passes-static-but-fails-tests | P2 (bug-type routing) cannot be tested; only P1 and P3 remain |
| A3 | GPT-4o-mini is representative enough of current capable LLMs that findings generalize to GPT-4-class models | GPT-4o-mini achieves ~75-80% pass@1 on HumanEval; similar architecture to GPT-4o | Results are GPT-4o-mini specific; generalization claim must be weakened |
| A4 | 3 repair iterations are sufficient to observe differential effects across categories | Self-Repair (Olausson 2023): diminishing returns after 2-3 iterations; most gains in first 1-2 | SMT may need more iterations; 3-iteration budget may favor execution monitoring artificially |
| A5 | HumanEval + MBPP problem distribution is representative enough to generalize broadly | Both benchmarks are standard evaluation suites used by majority of LLM code generation papers | Findings are benchmark-specific; SWE-bench or CodeContests may show different ordering |

### 1.6 Research Gap & Novelty

**Gap:** No controlled cross-category comparison of formal feedback methods on the same LLM backbone and benchmarks exists. All prior work (Self-Repair, Reflexion, CodeT, Grammar-Constrained Decoding) studies exactly one formal feedback category in isolation, on different LLMs, different benchmarks, without overhead normalization.

**Novelty:** First controlled cross-category formal feedback comparison with overhead normalization (correctness-per-overhead efficiency ratio) and bug-type coverage profiling enabling a diagnostic routing recommendation: match formal feedback method to dominant error type in task distribution.

**Scope Reduction:** 67% — 4 out of 6 claims are BUILD_ON (pre-validated infrastructure). Only 2 PROVE_NEW claims require experimental verification: (1) the cross-category comparison itself, (2) differential bug-type coverage profiles.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Differential Feedback Signal Existence**

**Statement**: Under application of four formal feedback categories (execution monitoring, static analysis, type checking, SMT solving) to GPT-4o-mini-generated code on HumanEval+MBPP (538 problems), if each verifier is independently applied to the same initial code solutions, then each category will produce a measurably distinct feedback signal on a non-trivial fraction of problems (≥10% activation rate per category) because the categories target different error types and use different formalism levels.

**Rationale**: Before testing efficiency ratios, we must confirm that all four feedback categories actually fire on the benchmark problems and produce non-degenerate signals. If any category has near-zero activation, the comparison is moot. This is the existence prerequisite for all mechanism testing.

**Variables** (from Phase 2A):
- Independent: Formal Feedback Category (4 levels)
- Dependent: Activation rate per category (fraction of 538 problems where verifier produces non-trivial output)
- Controlled: GPT-4o-mini backbone, standardized prompt template, same 538 problems

**Verification Protocol** (3 steps):
1. Generate initial solutions for all 538 problems with GPT-4o-mini (temperature 0.2).
2. Apply each of the 4 feedback categories independently to all initial solutions; record activation rate (non-trivial feedback produced).
3. For SMT: run 20-problem pilot first to validate Z3 auto-extraction soundness before full run.

**Success Criteria** (PoC: Direction-based):
- Primary: All 4 categories activate on ≥10% of 538 problems
- Secondary: SMT pilot shows ≥30% sound constraint extraction rate (validates A1)

**Failure Response**:
- IF any category activates on <5% of problems: PIVOT — exclude that category, reduce to 3-category comparison
- IF SMT pilot fails soundness: SCOPE — document SMT as infeasible, 3-category comparison

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 5 (sh1_existence), Section 0 PROVE_NEW claims

---

---
**H-M1: Error Type Distribution in Initial LLM Generations**

**Statement**: Under GPT-4o-mini generating initial solutions for 538 HumanEval+MBPP problems (before any repair loop), if failures are classified by bug type (type error / runtime error / logic error) using automated heuristics from error traces, then a mixed distribution of bug types will be observed (no single type exceeding 80% of failures) because LLM code generation errors span syntactic, type, and algorithmic domains.

**Rationale**: Causal chain step 1 — the mechanism requires that initial generations contain a realistic mix of bug types, otherwise the bug-type coverage profiling (P2) has no discriminatory power. This validates the precondition for the differential coverage hypothesis.

**Variables** (from Phase 2A):
- Independent: Problem set (HumanEval 164 + MBPP 374 = 538 total)
- Dependent: Bug-type distribution (fraction type/runtime/logic errors among failures)
- Controlled: GPT-4o-mini temperature 0.2, no repair, same problem set

**Verification Protocol** (4 steps):
1. Generate single-shot solutions for all 538 problems with GPT-4o-mini (temperature 0.2).
2. Run evaluation: classify failures by automated heuristic (Pyright error = type error; exception without Pyright error = runtime error; no exception but test failure = logic error).
3. Check inter-rater reliability: compare automated classifier against Pyright error categories as secondary ground truth for type errors.
4. Report distribution: fraction of failing problems in each bug-type stratum.

**Success Criteria** (PoC: Direction-based):
- Primary: No single bug type exceeds 80% of failures (mixed distribution confirmed)
- Secondary: Bug-type classifier achieves ≥70% agreement with secondary ground truth for type errors (validates A2)

**Failure Response**:
- IF distribution is >80% single type: SCOPE — P2 has reduced power; document as limitation
- IF classifier reliability <60%: PIVOT — use coarser 2-class scheme (type vs. non-type)

**Dependencies**: H-E1

**Source**: Phase 2A Section 1.3 Causal Step 1, Section 1.4 A2

---

---
**H-M2: Verifier Feedback Specificity Gradient**

**Statement**: Under the same set of failing LLM-generated solutions, if four feedback categories (execution monitoring, static analysis, type checking, SMT solving) are applied independently, then the feedback signals will exhibit a measurable specificity gradient (SMT > static analysis/type checking > execution monitoring) as operationalized by the information content of the feedback string (character count and error-field count of structured output) because higher formalism levels produce more detailed diagnostic information.

**Rationale**: Causal chain step 2 — the efficiency mechanism requires that feedback specificity actually varies across categories in a measurable way. If all signals are equally informative (or equally uninformative) to the LLM, the proposed efficiency trade-off mechanism is broken.

**Variables** (from Phase 2A):
- Independent: Formal Feedback Category (4 levels)
- Dependent: Feedback specificity proxy (mean character count of feedback string, mean number of structured error fields per problem)
- Controlled: Same failing solutions, standardized output format

**Verification Protocol** (3 steps):
1. Apply all 4 verifiers to the same set of failing solutions from H-M1.
2. Measure feedback specificity: character count of feedback string; number of distinct error fields in structured output (e.g., JSON keys for Pyright; counterexample variable bindings for Z3).
3. Rank categories by mean specificity; verify ordering matches prediction (SMT ≥ static/type > execution).

**Success Criteria** (PoC: Direction-based):
- Primary: Specificity ordering SMT ≥ {static analysis, type checking} > execution monitoring confirmed (Kruskal-Wallis p<0.05)
- Secondary: Pairwise differences between adjacent categories are non-trivial (>20% difference in mean character count)

**Failure Response**:
- IF specificity ordering does not hold: EXPLORE — examine whether LLM parsing of structured vs. natural language feedback explains anomaly
- IF SMT produces fewer characters than execution (due to timeouts): SCOPE — document as overhead-budget confound

**Dependencies**: H-M1

**Source**: Phase 2A Section 1.3 Causal Step 2, Geng et al. 2023, Pyright/Z3 overhead characteristics

---

---
**H-M3: Repair Quality Correlation with Feedback Specificity**

**Statement**: Under 3-iteration repair loops applied to failing solutions from H-M1 using GPT-4o-mini, if the four feedback categories (ordered by specificity from H-M2) are used to generate repair prompts, then per-iteration repair success rate will positively correlate with feedback specificity (higher specificity = higher single-iteration repair rate) because more precise error signals enable more targeted code edits, reducing tokens wasted on incorrect repair attempts.

**Rationale**: Causal chain step 3 — this tests the core LLM behavior assumption (A3, A4): that the LLM actually uses the specificity of feedback to produce better repairs. Without this link, the efficiency ratios could differ purely due to overhead, not LLM behavior.

**Variables** (from Phase 2A):
- Independent: Formal Feedback Category (operationalized by specificity level from H-M2)
- Dependent: Per-iteration repair success rate (fraction of failing solutions repaired on first iteration)
- Controlled: Same initial solutions, same 3-iteration budget, same prompt template, GPT-4o-mini temperature 0.0 for repair

**Verification Protocol** (3 steps):
1. Run repair loops for all 4 categories on all 538 problems (up to 3 iterations); record pass/fail per iteration.
2. Compute per-iteration-1 repair success rate for each category (fraction of initially failing problems passing after iteration 1 of repair).
3. Spearman rank correlation between specificity order (from H-M2) and per-iteration-1 success rate.

**Success Criteria** (PoC: Direction-based):
- Primary: Spearman correlation between specificity rank and per-iteration-1 success rate > 0 (positive direction)
- Secondary: Categories with higher specificity require fewer mean iterations to achieve first pass (mean iterations negatively correlated with specificity rank)

**Failure Response**:
- IF correlation is ≤0 (higher specificity = worse repair): EXPLORE — examine whether feedback format (JSON vs. trace) confounds LLM parsing
- IF all categories have similar per-iteration rates: SCOPE — efficiency differences will be entirely overhead-driven; P1 still testable

**Dependencies**: H-M2

**Source**: Phase 2A Section 1.3 Causal Step 3, Self-Repair (Olausson 2023)

---

---
**H-M4: Overhead-Determined Efficiency Ratios**

**Statement**: Under measurement of wall-clock overhead for all 4 feedback categories on 538 problems with GPT-4o-mini, if overhead per problem is measured as mean seconds from problem submission to final answer across all repair iterations, then overhead will follow the ordering execution monitoring < static analysis ≈ type checking < SMT solving (O(ms) vs O(100ms) vs O(1-10s)), and this overhead differential will create distinct correctness-per-overhead efficiency ratios (Δpass@1 / mean wall-clock seconds) across categories, with execution monitoring predicted to achieve the highest ratio.

**Rationale**: Causal chain step 4 — this is the empirically open question identified as the key tension in Phase 2A: whether SMT's higher specificity (fewer iterations needed) offsets its higher per-iteration overhead. The efficiency ratio is the primary metric (P1) and requires both the pass@1 outcome and the overhead measurement.

**Variables** (from Phase 2A):
- Independent: Formal Feedback Category (4 levels)
- Dependent: Correctness-per-overhead efficiency ratio (Δpass@1 / mean wall-clock seconds per problem); also mean wall-clock overhead alone
- Controlled: Identical infrastructure, same time window, same API call parameters

**Verification Protocol** (4 steps):
1. Record wall-clock time for each problem × category combination across all repair iterations (infrastructure: time.time() around API + verifier calls).
2. Compute Δpass@1 for each category (pass@1 after repair loop minus vanilla generation pass@1).
3. Compute efficiency ratio = Δpass@1 / mean wall-clock seconds per problem for each category.
4. Bootstrap confidence intervals (10,000 samples) for pairwise differences; test P1: execution monitoring ratio ≥ 1.5× next-best category (p<0.05).

**Success Criteria** (PoC: Direction-based):
- Primary (P1): Execution monitoring achieves highest efficiency ratio; ≥ 1.5× next-best category by bootstrap CI (p<0.05)
- Secondary: Overhead ordering confirmed (execution < static ≈ type < SMT)

**Failure Response**:
- IF SMT achieves highest efficiency ratio (fast convergence offsets overhead): PIVOT — reframe as "SMT is efficient for logic-error-rich distributions"; update routing recommendation
- IF all ratios within 1.5×: SCOPE — report efficiency rankings without strong ordering claim; focus on bug-type coverage profiling (P2) as primary contribution

**Dependencies**: H-M3

**Source**: Phase 2A Section 1.3 Causal Step 4, Section 1.6 P1, key tension

---

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          HYPOTHESIS INVENTORY (5 hypotheses)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID    | Type      | Statement (Brief)                              | Prerequisites | Source         |
|-------|-----------|------------------------------------------------|---------------|----------------|
| H-E1  | Existence | All 4 categories activate on ≥10% of problems  | None          | SH1, PROVE_NEW |
| H-M1  | Mechanism | Mixed bug-type distribution in initial LLM code | H-E1          | Causal Step 1  |
| H-M2  | Mechanism | Verifier specificity gradient exists            | H-M1          | Causal Step 2  |
| H-M3  | Mechanism | Repair quality correlates with specificity      | H-M2          | Causal Step 3  |
| H-M4  | Mechanism | Overhead creates differential efficiency ratios | H-M3          | Causal Step 4  |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | All 4 categories activate ≥10%; SMT pilot ≥30% sound | STOP, reassess entire approach |
| H-M1 | MUST_WORK | Mixed bug-type distribution (no single type >80%); classifier ≥70% agreement | SCOPE: reduced P2 power |
| H-M2 | SHOULD_WORK | Specificity ordering confirmed (Kruskal-Wallis p<0.05) | EXPLORE format confound |
| H-M3 | SHOULD_WORK | Positive Spearman correlation specificity vs. repair rate | SCOPE: overhead-only efficiency |
| H-M4 | SHOULD_WORK | P1 confirmed: execution monitoring ≥1.5× next-best (bootstrap p<0.05) | PIVOT: update routing recommendation |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 (incl. SMT pilot) | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3, H-M4 | 4 weeks |
| **Total** | **5 hypotheses** | **6 weeks** |

**Total Duration:** 6 weeks (2 + 4: formula 2 + causal_chain_count)

---

## 4. Risk Analysis

### 4.1 Assumptions and Risks

**Risk R1: SMT Auto-Extraction Failure**

**Source Assumption:** A1 — Z3 constraints auto-extracted from HumanEval docstrings are sound (~40% coverage).

**Description:** LLM-generated Z3 encodings may be logically unsound (encoding bugs, unsatisfiable constraints, or trivially true constraints that never produce counterexamples), making the SMT category unable to provide meaningful feedback.

**Affected Hypotheses:** H-E1, H-M2, H-M4

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Run 20-problem SMT pilot before full experiment. Manually validate Z3 encoding soundness for pilot problems.
2. **Detection:** Pilot success criterion: ≥30% of pilot problems produce non-trivial counterexamples (i.e., Z3 returns SAT with counterexample, not UNSAT or timeout).
3. **Response:**
   - PIVOT: If pilot fails (<30% sound), reduce to 3-category comparison (execution, static analysis, type checking); document as scope limitation.
   - SCOPE: If partial (~30-50% sound), proceed with matched-subset analysis for SMT.
   - ABORT: Do not abort — 3-category comparison still produces valid contribution.

**Early Warning Indicators:**
- >50% of pilot SMT calls return UNSAT immediately (trivially unsatisfiable encoding)
- >50% of pilot SMT calls timeout within 10s budget

---

**Risk R2: Bug-Type Classification Unreliable**

**Source Assumption:** A2 — automated bug-type classification from error traces is reliable.

**Description:** Automated heuristic classifier (Pyright error → type; exception → runtime; test-fail-only → logic) may misclassify, making the stratified analysis for P2 invalid.

**Affected Hypotheses:** H-M1, H-M3 (indirectly)

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Design classifier with explicit precedence rules (Pyright error fires first, then exception type, then residual).
2. **Detection:** Inter-rater check: compare automated classifier against Pyright error category as secondary ground truth for type errors on a 50-problem sample.
3. **Response:**
   - PIVOT: If agreement <60%, switch to 2-class scheme (type error = Pyright fires; non-type = all else).
   - SCOPE: Report P2 with caveat on classifier reliability; include confusion matrix in appendix.

**Early Warning Indicators:**
- >30% of Pyright-flagged problems also raise runtime exceptions (ambiguous classification)
- >20% disagreement on 50-problem inter-rater sample

---

**Risk R3: GPT-4o-mini Non-Representative**

**Source Assumption:** A3 — GPT-4o-mini representative of GPT-4-class models.

**Description:** Efficiency ordering or bug-type coverage profiles may be specific to GPT-4o-mini's particular response patterns, not generalizing to other LLMs.

**Affected Hypotheses:** H-M3, H-M4 (generalizability claims)

**Severity:** Low (within-study validity unaffected; generalization weakened)

**Mitigation Strategy:**
1. **Prevention:** Keep claims scoped to "GPT-4o-mini on HumanEval+MBPP" as primary claim.
2. **Detection:** Monitor if repair patterns seem anomalous (e.g., model consistently ignoring Z3 counterexamples).
3. **Response:**
   - SCOPE: Explicitly limit generalization claim; note as future work with other LLMs.

**Early Warning Indicators:**
- GPT-4o-mini repair completions that repeat the original code verbatim despite explicit error feedback (signal the model is not using feedback)

---

**Risk R4: 3-Iteration Budget Insufficient**

**Source Assumption:** A4 — 3 repair iterations sufficient to observe differential effects.

**Description:** SMT's higher specificity may require more than 3 iterations to manifest advantage (SMT counterexamples may need iterative refinement to be acted on correctly), artificially penalizing SMT in efficiency ratio.

**Affected Hypotheses:** H-M3, H-M4

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Record per-iteration outcomes for all categories; compute efficiency ratios at iteration counts 1, 2, 3 separately.
2. **Detection:** If SMT shows near-zero Δpass@1 at iteration 1 but sharp improvement at iteration 2-3, 3-iteration budget may be the critical constraint.
3. **Response:**
   - EXPLORE: Report per-iteration efficiency curves; note if ordering changes across iterations.
   - PIVOT: If SMT shows monotonically improving efficiency past iteration 3 (extrapolated trend), note as limitation and recommend future experiment with 5-7 iterations.

**Early Warning Indicators:**
- SMT Δpass@1 near-zero at iteration 1 but non-zero at iterations 2-3 (delayed benefit pattern)
- Execution monitoring's ratio advantage shrinks substantially from iteration 1 to iteration 3

---

**Risk R5: Benchmark Distribution Unrepresentative**

**Source Assumption:** A5 — HumanEval + MBPP representative of LLM code generation broadly.

**Description:** Both benchmarks are function-level competitive-programming-style tasks, potentially over-representing runtime and type errors relative to repository-level or real-world code.

**Affected Hypotheses:** H-M1 (distribution), H-M4 (efficiency claim generalizability)

**Severity:** Low (within-benchmark validity unaffected)

**Mitigation Strategy:**
1. **Prevention:** Scope all claims explicitly to "function-level code generation on HumanEval+MBPP."
2. **Detection:** N/A — benchmark limitation is known a priori.
3. **Response:**
   - SCOPE: Note SWE-bench as natural extension; function-level focus is the stated scope.

**Early Warning Indicators:**
- N/A (known limitation, not a failure risk)

---

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: SMT Auto-Extraction Failure | A1 | H-E1, H-M2, H-M4 | High |
| R2: Bug-Type Classification Unreliable | A2 | H-M1, H-M3 | Medium |
| R3: GPT-4o-mini Non-Representative | A3 | H-M3, H-M4 | Low |
| R4: 3-Iteration Budget Insufficient | A4 | H-M3, H-M4 | Medium |
| R5: Benchmark Distribution Unrepresentative | A5 | H-M1, H-M4 | Low |

### 4.3 Risk Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    RISK SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID | Risk                        | Source | Severity | Affected      | Mitigation          |
|----|----------------------------|--------|----------|---------------|---------------------|
| R1 | SMT Auto-Extraction Failure | A1     | High     | H-E1,M2,M4    | 20-problem pilot    |
| R2 | Bug-Type Classifier Unreliable | A2  | Medium   | H-M1, H-M3    | Inter-rater check   |
| R3 | GPT-4o-mini Non-Representative | A3  | Low      | H-M3, H-M4    | Scope claims        |
| R4 | 3-Iteration Budget Insufficient | A4  | Medium   | H-M3, H-M4    | Per-iteration curves |
| R5 | Benchmark Unrepresentative  | A5     | Low      | H-M1, H-M4    | Scope claims        |

Critical Risks: 0
High Risks: 1 (R1)
Medium Risks: 2 (R2, R4)
Low Risks: 2 (R3, R5)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 5. Dependency Graph and Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1  (Existence — no dependencies)
    [MUST_WORK: all 4 categories activate]
         │
         ▼
[Level 1 - Mechanism Foundation]
    H-M1 ← H-E1
    [MUST_WORK: mixed bug-type distribution confirmed]
         │
         ▼
[Level 2 - Specificity Evidence]
    H-M2 ← H-M1
    [SHOULD_WORK: specificity gradient measurable]
         │
         ▼
[Level 3 - Repair Behavior]
    H-M3 ← H-M2
    [SHOULD_WORK: repair quality correlates with specificity]
         │
         ▼
[Level 4 - Efficiency Measurement]
    H-M4 ← H-M3
    [SHOULD_WORK: overhead-determined efficiency ratios, P1]
         │
         ▼
    [COMPLETE]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 DEPENDENCY HIERARCHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Level | Hypothesis | Prerequisites | Gate Type   |
|-------|-----------|---------------|-------------|
| 0     | H-E1      | None          | MUST_WORK   |
| 1     | H-M1      | H-E1          | MUST_WORK   |
| 2     | H-M2      | H-M1          | SHOULD_WORK |
| 3     | H-M3      | H-M2          | SHOULD_WORK |
| 4     | H-M4      | H-M3          | SHOULD_WORK |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis     │ W1-2     │ W3-4     │ W5       │ W6       │
─────────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 1: Foundation  │          │          │          │          │
  H-E1 (incl. pilot) │ ████████ │          │          │          │
  [Gate 1]           │        ◆ │          │          │          │
─────────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 2: Mechanisms  │          │          │          │          │
  H-M1               │          │ ████████ │          │          │
  H-M2               │          │        ██│ ██       │          │
  H-M3               │          │          │   █████  │          │
  H-M4               │          │          │        ██│ ██       │
  [Gate 2]           │          │          │          │        ◆ │
─────────────────────┼──────────┼──────────┼──────────┼──────────┤
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

**Note:** H-M1 through H-M4 can overlap in practice since data collection (initial generation + verifier application) is largely parallel — H-M1 and H-M2 use the same experimental run. Timeline shown as conservative sequential planning.

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

Total Duration: 6 weeks
  Formula: 2 (H-E1) + 4 (H-M1 through H-M4, 1 week each after W3)

Slack Available: 0 weeks (all sequential, single critical path)

Practical Note: H-M1 through H-M4 share the same experimental
run data — the primary parallelization opportunity is in analysis,
not data collection. Wall-clock can be compressed to ~3-4 weeks
with concurrent analysis.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 5
  Existence: 1 (H-E1)
  Mechanism: 4 (H-M1 to H-M4)
  Condition: 0 (not applicable)

Verification Phases: 2
  1. Foundation (H-E1) — includes SMT pilot
  2. Mechanisms (H-M1 through H-M4)

Total Duration: 6 weeks (conservative sequential)
Critical Path Length: 6 weeks
Execution Mode: Sequential chain (data collection parallelizable)

Compute Resources:
  API calls: 538 problems × 4 conditions × 3 iterations = 6,456 GPT-4o-mini calls
  Estimated cost: ~$50-100 (per Phase 2A feasibility assessment)
  Infrastructure: Pyright CLI, mypy CLI, Z3 Python API, subprocess, openai/human-eval harness

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

```
Step 1: Execute H-E1 (Foundation + SMT pilot) — Week 1-2
Step 2: Evaluate Gate 1 — MUST_WORK: proceed only if all 4 categories activate
Step 3: Execute H-M1 (bug-type distribution) — Week 3-4 (uses same initial generation data)
Step 4: Execute H-M2 (specificity gradient) — overlaps with H-M1 data collection
Step 5: Execute H-M3 (repair quality correlation) — Week 5 (requires repair loop data)
Step 6: Execute H-M4 (efficiency ratios) — Week 5-6 (requires complete timing data)
Step 7: Evaluate Gate 2 — SHOULD_WORK: document any failures as limitations
Step 8: Verification complete → Proceed to Phase 4.5 Synthesis
```

---

## 6. Dialectical Analysis

### 6.1 Thesis Statement

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: Formal feedback categories differ systematically in
correctness-per-overhead efficiency (execution monitoring highest)
and bug-type coverage profiles (static analysis best for type
errors, execution for runtime, SMT for logic), enabling a
diagnostic routing recommendation for practitioners.

Supporting Evidence:
1. Causal mechanism: 4-step chain from error generation through
   verifier specificity → repair quality → efficiency ratio
   (Olausson 2023; Pyright/Z3 known overhead profiles)
2. Key assumptions grounded: All 4 categories implementable
   with existing tools; GPT-4o-mini representative;
   HumanEval+MBPP provide ground-truth test suites
3. Testable predictions: P1 (≥1.5× ratio), P2 (chi-squared
   interaction), P3 (difficulty stratification) — all quantitative

Strengths:
- First controlled cross-category comparison (no prior work)
- Overhead normalization reframes the resource-allocation question
- Bug-type routing is actionable for practitioners
- All tools available, feasibility confirmed ($50-100 budget)

Expected Outcomes:
- P1: Execution monitoring ≥1.5× next-best efficiency ratio
- P2: Static analysis best for type errors; SMT best for logic
- P3: Hard problems gain more; efficiency ordering preserved

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis Development (H0-Based)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): No significant difference in pass@1
improvement per unit wall-clock overhead between formal feedback
categories on GPT-4o-mini over HumanEval+MBPP.

Counter-Arguments:
1. All categories may produce similar Δpass@1 (LLM repairs
   well regardless of signal quality — repair quality
   ceiling reached at 3 iterations for all methods)
2. SMT unsoundness (A1) may disqualify the SMT category,
   reducing to 3-category comparison with less power to
   demonstrate ordering
3. Bug-type classification noise (A2) may mask the
   cross-category interaction P2 depends on

Potential Failure Points:
- R1: SMT auto-extraction fails pilot → 3-category comparison
- R2: Bug-type classifier unreliable → P2 untestable
- R4: 3-iteration budget too short for SMT to show advantage

Conditions Under Which H0 Would Be Supported:
- If all 4 categories achieve Δpass@1 within 1.5× of each other
  on similar overhead budgets (efficiency ratios collapse)
- If LLM ignores counterexample detail in SMT feedback
  (treats it same as pass/fail trace)
- If HumanEval/MBPP errors are dominated by runtime errors
  that all categories address equally

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:

The hypothesis H-FormalFeedbackComparison-v1 presents a
testable claim grounded in a 4-step causal chain with
existing empirical support for each link. However, the null
hypothesis raises valid concerns: LLM repair behavior may
be insensitive to feedback specificity at the level GPT-4o-mini
operates, and the SMT coverage limitation (40% of problems)
reduces statistical power for the strongest-specificity comparison.

Resolution Path:

The verification plan addresses this dialectic through:
1. Foundation verification (H-E1): Confirms all categories
   fire before testing efficiency — avoids null comparison
2. Sequential mechanism testing (H-M1→H-M4): Tests each
   causal link independently, isolating where H0 holds
3. Gate conditions: MUST_WORK on H-E1 and H-M1 allows
   early detection of H0 support at fundamental level
4. Fallback path: Even if P1 ordering fails, P2 bug-type
   coverage profiling remains a novel contribution

Conditions for Thesis Support:
- H-E1 and H-M1 pass MUST_WORK gates
- P1: Execution monitoring ≥1.5× next-best (bootstrap p<0.05)
- P2: Chi-squared significant for bug-type × category interaction

Conditions for Antithesis Support:
- H-E1 fails (some categories don't fire on benchmark)
- H-M1 fails (single bug-type dominates, P2 has no power)
- H-M4 shows ratios within 1.5× across all categories

Nuanced Outcome Possibilities:
1. Full Support: H-E1→H-M4 all pass → Thesis validated, P1+P2+P3
2. Partial Support: P1 fails but P2 holds → Bug-type taxonomy
   is the primary contribution; efficiency ordering not confirmed
3. No Support: H-E1 or H-M1 fail → H0 supported; back to
   hypothesis design

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Aspect      | Thesis Position               | Antithesis Challenge           | Resolution       |
|-------------|-------------------------------|--------------------------------|------------------|
| Existence   | All 4 categories produce signal | SMT may not fire (40% limit)  | H-E1 + pilot     |
| Mechanism   | 4-step causal chain valid      | LLM ignores specificity detail | H-M2, H-M3 tests |
| Bug-typing  | Differential coverage by type  | Classifier too noisy           | Inter-rater check |
| Efficiency  | Execution monitoring wins      | SMT fast-convergence offsets   | H-M4 bootstrap   |
| Performance | Outperforms no-feedback baseline | Marginal Δpass@1              | Phase 5 (skipped) |

Overall Robustness Score: Medium-High
  - Strong causal grounding and prior evidence
  - One high-risk assumption (A1/R1) with clear mitigation
  - Fallback contributions robust even under partial failure

Confidence in Verification Plan: 0.72

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Formal feedback categories (execution monitoring / static analysis / type checking / SMT solving) produce systematically different correctness-per-overhead efficiency ratios and bug-type coverage profiles when applied in GPT-4o-mini repair loops on HumanEval+MBPP.
- ID: H-FormalFeedbackComparison-v1, Confidence: 0.72

**Verification Structure:**
- Mode: Incremental (67% scope reduction — 4/6 claims are pre-validated BUILD_ON)
- Sub-Hypotheses: 5 total (H-E1 + H-M1 through H-M4)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points (Gate 1: MUST_WORK; Gate 2: SHOULD_WORK)

**Risk Assessment:** Medium
- Primary concerns: R1 (SMT auto-extraction soundness — mitigated by 20-problem pilot); R2 (bug-type classifier reliability — mitigated by inter-rater check)

**Immediate Action:** Begin Phase 1 with H-E1 including SMT 20-problem pilot

### 7.2 Conclusions

**Key Achievements:**
- 5 hypotheses across 2 phases (66 week execution plan)
- H0 addressed: No significant cross-category efficiency difference — tested by H-M4 with bootstrap CI
- 67% scope reduction achieved by leveraging Phase 2A Established Facts (BUILD_ON claims as infrastructure)

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Confirm all 4 categories activate on ≥10% of 538 problems; SMT pilot
- Gate 1: MUST PASS — all categories must produce non-degenerate signals

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: Mixed bug-type distribution in initial LLM generations
- H-M2: Verifier specificity gradient measurable across categories
- H-M3: Repair quality positively correlated with feedback specificity
- H-M4: Overhead-determined efficiency ratios; P1 test (execution monitoring ≥1.5×)
- Gate 2: H-M1 MUST_WORK; H-M2/M3/M4 SHOULD_WORK

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 MUST_WORK
   - FAIL → STOP: reassess entire approach (specific categories infeasible)
   - SMT pilot fail → SCOPE: 3-category comparison

2. **Gate 2 (Mechanisms):** H-M1 MUST_WORK
   - H-M1 FAIL → SCOPE: P2 reduced power; focus on P1 only
   - H-M2/M3/M4 FAIL → EXPLORE/PIVOT: document mechanism limitations; bug-type taxonomy remains

**Open Questions:**
- What fraction of HumanEval/MBPP problems have auto-extractable Z3 properties? (Answered by SMT pilot in H-E1)
- Does bug-type classification accuracy meet reliability threshold for P2 test? (Answered by inter-rater check in H-M1)
- Does GPT-4o-mini respond differently to Pyright JSON vs. Z3 counterexample format? (Partially answered by H-M2/M3 analysis)

**Recommendations:**

1. **Immediate Actions:**
   - Begin H-E1 with SMT 20-problem pilot before allocating full compute budget
   - Set up standardized infrastructure: timing harness, prompt template, evaluation harness

2. **Resource Allocation:**
   - Allocate 6 weeks for critical path (conservative); 3-4 weeks if analysis parallelized
   - API budget: ~$50-100 for 538 × 4 × 3 = 6,456 GPT-4o-mini calls

3. **Failure Management:**
   - Document all partial results — bug-type taxonomy is a novel contribution independent of P1 confirmation
   - Execute PIVOT strategies per risk mitigation plans (R1→3-category; R2→2-class scheme)

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: `docs/youra_research/03_refinement.yaml` (ID: H-FormalFeedbackComparison-v1)
- Gap: gap-2 "No Overhead-Normalized Cross-Category Comparison of Formal Feedback Methods"
- Convergence: 8 exchanges, 6 personas, all criteria met

**B. MCP Tool Usage Summary**
- Total MCP calls: 0 (ClearThought, Archon, Exa unavailable — batch/ablation mode)
- Hypotheses generated from Phase 2A causal chain structure (4 steps → 4 H-M hypotheses)
- Note: In production mode, MCP scientificmethod would validate hypothesis framing
