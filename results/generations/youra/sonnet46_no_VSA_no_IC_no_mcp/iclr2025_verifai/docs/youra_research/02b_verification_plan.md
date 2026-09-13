---
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
status: complete
completedAt: "2026-08-26T00:00:00Z"
---

# Verification Plan: Static Analysis Feedback in LLM Code Repair Loops

**Date:** 2026-08-26
**Hypothesis ID:** H-StaticRepair-v1
**Confidence:** 0.72
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under Python code generation on HumanEval+ and MBPP+ benchmarks,
if repair loops are augmented with static analysis feedback (mypy type checking)
in addition to execution-based feedback,
then pass@1 after up to k=5 repair rounds increases beyond the execution-only baseline,
because mypy provides error-type-specific correction signal (type mismatch location
and expected type) that narrows the LLM's next-attempt distribution toward
type-correct solutions, whereas execution-only feedback provides only pass/fail
binary signal without type-level diagnostics.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in pass@1 (averaged over k=1..5 repair rounds)
between execution+mypy repair and execution-only repair on HumanEval+ and MBPP+.
(Welch's t-test, p >= 0.05 on both benchmarks)

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | MBPP+ (primary) + HumanEval+ (secondary) (standard) | MBPP+ (378 problems) provides sufficient statistical power to detect 1% absolute improvement. HumanEval+ (164 problems) serves as secondary replication. EvalPlus augmentation reduces false positives. |
| **Model** | GPT-4o-mini | Strong Python understanding; affordable for ~7,400 repair calls ($10-15); deterministic at temperature=0.0 for repair rounds enabling reproducibility. |

**Dataset Details:**
- Source: evalplus/evalplus repository (public)
- Path: https://github.com/evalplus/evalplus

**Model Details:**
- Type: API-based LLM (OpenAI)
- Source: OpenAI API

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| No-repair baseline | ~55-60% pass@1 (estimated) | HumanEval+ |
| Self-Debug (execution-only repair) | ~65-70% pass@1 with k=3 (estimated) | HumanEval/MBPP |
| Reflexion (verbal feedback repair) | ~67% pass@1 with k=3 (estimated) | HumanEval |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Type errors are ~20%+ of HumanEval+/MBPP+ failures under GPT-4o-mini | EvalPlus error analysis (Liu et al. 2023) | If <5% failures, mypy adds negligible signal; pass@1 improvement near zero |
| A2 | GPT-4o-mini can incorporate mypy error messages to improve repair quality | GPT-4o-mini has strong Python understanding; mypy error format is human-readable | LLM cannot parse/use mypy output; Condition B degrades to Condition A |
| A3 | mypy in permissive mode produces actionable errors with low false-positive rate | Permissive flags (--ignore-missing-imports --no-strict-optional) are standard practice | High false-positive rate adds noise, potentially degrading repair quality |
| A4 | k=5 rounds is sufficient to capture asymptotic pass@k benefit | Self-Debug shows most repair benefit within k=3 rounds | Effect requires k>5; timeline extends |
| A5 | LLM-generated Z3 specs are sufficiently correct (validated against EvalPlus test cases) | Pure functions with simple types have reliable formal encodings | Wrong Z3 specs generate misleading counterexamples; Condition C underperforms B |

### 1.6 Research Gap & Novelty

**Gap:** No published controlled comparison of static analysis (mypy) as an explicit
repair-loop feedback signal in LLM code generation on standard benchmarks.

**Novelty:** First controlled comparison treating mypy type-checker output as a distinct,
structured feedback channel — separate from execution feedback — and measuring its
marginal contribution to pass@1 on HumanEval+/MBPP+.

**Scope Reduction (67%):** 4 of 6 claims are established (BUILD_ON):
- Execution-only repair improves pass@k (Chen et al. 2023)
- Grammar-constrained decoding is implementable (Willard & Louf 2023)
- mypy reliably detects Python type errors (mypy docs)
- HumanEval+/MBPP+ are suitable benchmarks (Liu et al. 2023)

Only 2 claims need verification (PROVE_NEW):
1. Static analysis feedback yields higher pass@1 than execution-only
2. LLM-generated Z3 constraints provide additional signal beyond mypy (curated subset)

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | MUST_WORK | H-M2 | NOT_STARTED |
| H-Z1 | EXISTENCE | SHOULD_WORK | H-E1 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Type Error Prevalence in LLM-Generated Python Code**

**Type:** EXISTENCE
**Statement:** Under GPT-4o-mini generation on HumanEval+ and MBPP+
(temperature=0.8, single shot), if we run mypy (permissive mode) on
all initial generated solutions, then a non-trivial fraction (≥10%)
of failing solutions will have mypy-detectable type errors, because
type mismatches are a common failure mode in LLM-generated Python code.

**Rationale:** This is the foundational existence check. If type errors
are rare (<5%), mypy signal is too sparse to improve repair and the
entire main hypothesis becomes moot. Establishing the base rate is a
prerequisite for all mechanism hypotheses.

**Variables:**
- Independent: None (observational)
- Dependent: Fraction of failing solutions with ≥1 mypy error
- Controlled: GPT-4o-mini, temperature=0.8, 3 seeds, full benchmarks

**Verification Protocol:**
1. Generate initial solutions for all HumanEval+ (164) and MBPP+ (378) problems (3 seeds each).
2. Run EvalPlus test suite to identify failing solutions.
3. Run mypy --ignore-missing-imports --no-strict-optional on all failing solutions.
4. Count fraction of failures with ≥1 mypy error per benchmark.
5. Report: mean type-error fraction ± std across 3 seeds.

**Success Criteria (PoC: Direction-based):**
- Primary: ≥10% of failing solutions have ≥1 mypy error on MBPP+
- Secondary: ≥10% on HumanEval+ (expected similar base rate)

**Failure Response:**
- IF fails (type error rate < 5%): PIVOT — reconsider hypothesis scope; mypy signal is too sparse.
- IF borderline (5-10%): EXPLORE — continue with reduced expectation of effect size.

**Dependencies:** None

**Source:** Phase 2A Section 1.3 (causal step 1), A1 assumption, P1 prerequisite

---
**H-M1: Structured mypy Signal Reduces Type Error Count Across Repair Rounds**

**Type:** MECHANISM
**Statement:** Under execution+mypy repair (Condition B, k=1..5 rounds),
if we track mypy error count per repair attempt per problem,
then the mean mypy error count decreases monotonically from round 1
to round 5, because LLM uses structured mypy error messages to generate
subsequent repair attempts with fewer type violations.

**Rationale:** This directly tests causal step 2→3: does the LLM incorporate
mypy's structured feedback? A decreasing error count trajectory is the
minimal mechanistic evidence that the feedback channel is active. This is
a necessary (though not sufficient) condition for pass@1 improvement.

**Variables:**
- Independent: Repair round k (1..5) in Condition B
- Dependent: Mean mypy error count per problem per round
- Controlled: Same as H-E1 setup + execution output provided alongside mypy

**Verification Protocol:**
1. Run full repair-loop experiment (H-M3 experiment) for Condition B (execution+mypy).
2. After each repair round, run mypy on the generated solution for each problem.
3. Record mypy error count per (problem, round) cell.
4. Compute mean ± std across problems for each round 1..5.
5. Test for monotonic decrease: Spearman correlation of mean error count vs round k.

**Success Criteria (PoC: Direction-based):**
- Primary: Spearman ρ < 0 (negative correlation — error count decreases across rounds)
- Secondary: Mean error count at round 5 < mean error count at round 1

**Failure Response:**
- IF fails: EXPLORE — mypy signal may not be interpretable by GPT-4o-mini; test A2 assumption explicitly.

**Dependencies:** H-E1

**Source:** Phase 2A P3 prediction, causal step 2 (mypy signal informativeness), A2 assumption

---
**H-M2: mypy Error Type Distinguishes Repair Targets More Than Execution Output Alone**

**Type:** MECHANISM
**Statement:** Under Condition A (execution-only) vs. Condition B (execution+mypy),
if we categorize initial failure modes (syntax/type/semantic/logic) per problem,
then Condition B achieves higher per-category repair rate specifically for
type-related failures (not semantic/logic), because mypy provides error-type
specificity that execution output lacks.

**Rationale:** Tests causal step 2 (mypy output's informational content): mypy
feedback should improve repairs specifically where type information is actionable.
If improvement is uniform across all error categories, the mechanism is not
type-specific and a confound (e.g., extra context length) may explain the effect.

**Variables:**
- Independent: Feedback condition (A vs. B)
- Dependent: Per-category repair rate (type-error vs. non-type-error problems)
- Controlled: Same model, prompts, temperature, benchmarks

**Verification Protocol:**
1. From H-M3 repair-loop results, extract per-problem failure categories using mypy + manual rule.
2. Label each failing problem: type-related (mypy detects) vs. non-type (mypy clean, fails EvalPlus).
3. Compute repair success rate (pass at k=5) per category per condition.
4. Compare: Condition B vs. A repair rate improvement on type-related problems vs. non-type.
5. Test: Is the Condition B improvement significantly larger for type-related problems?

**Success Criteria (PoC: Direction-based):**
- Primary: Condition B relative improvement on type-error problems > relative improvement on non-type-error problems
- Secondary: Effect size direction consistent across both benchmarks

**Failure Response:**
- IF fails: EXPLORE — mechanism may not be type-specific; consider alternative explanation (extra context).

**Dependencies:** H-M1

**Source:** Phase 2A causal step 2 (mypy signal specificity), A2 assumption, secondary DV

---
**H-M3: execution+mypy Repair Achieves Higher pass@1 Than execution-only Repair**

**Type:** MECHANISM
**Statement:** Under Python code generation on HumanEval+ (secondary) and MBPP+
(primary) with GPT-4o-mini, if we compare Condition B (execution+mypy, k=5) to
Condition A (execution-only, k=5), then Condition B achieves strictly higher pass@1
averaged over k=1..5 rounds, because the structured type-error signal in mypy output
enables more targeted repairs than binary execution pass/fail.

**Rationale:** This is the primary empirical test of the main hypothesis (PROVE_NEW
claim 1). It directly measures the net effect of adding mypy as a feedback channel
across the full benchmark at production repair round counts. Gate: MUST_WORK because
this is the core claim.

**Variables:**
- Independent: Feedback condition (A: execution-only vs. B: execution+mypy)
- Dependent: pass@1 after up to k repair rounds (primary: MBPP+, secondary: HumanEval+)
- Controlled: GPT-4o-mini, temperature=0.8 initial / 0.0 repair, 3 seeds, k=5 max, 2048 token budget

**Verification Protocol:**
1. Run 3-condition repair loop experiment (no-repair, Condition A, Condition B) on full MBPP+ (378) and HumanEval+ (164).
2. Generate initial solutions: temperature=0.8, 3 seeds.
3. For each seed, run k=5 repair rounds per condition per problem.
4. Compute pass@1 at each k per problem per condition.
5. Run Welch's t-test on per-problem improvement delta (Cond B - Cond A) on MBPP+; report p-value and absolute improvement.

**Success Criteria (PoC: Direction-based):**
- Primary: p < 0.05 on MBPP+; absolute pass@1 improvement ≥ 1% on MBPP+
- Secondary: Positive (even if non-significant) pass@1 delta on HumanEval+

**Failure Response:**
- IF H0 supported (p ≥ 0.05 on both): PIVOT — re-examine mechanism; check H-M1 trajectory first.
- IF negative delta (Condition B worse): ABANDON this hypothesis direction; consider confound analysis.

**Dependencies:** H-M2

**Source:** Phase 2A P1 prediction (primary), PROVE_NEW claim 1, main hypothesis statement

---
**H-Z1: LLM-Generated Z3 Constraints Provide Additional Repair Signal Beyond mypy**

**Type:** EXISTENCE
**Statement:** On a curated subset of ~50 arithmetic-heavy HumanEval problems,
if Condition C (execution+mypy+Z3) is compared to Condition B (execution+mypy),
then Condition C achieves higher pass@1 on the curated subset (after Z3 spec
pre-validation against EvalPlus test cases), because formal counterexamples from
Z3 provide a distinct error signal (constraint violation with witness) that
complements mypy's type-error messages.

**Rationale:** Tests PROVE_NEW claim 2. This is a secondary, independent experiment
on a curated subset. Success here demonstrates that formal verification adds a third
distinct feedback channel. Given the confound risk (Z3 spec quality), this is
SHOULD_WORK: a null result is informative but does not invalidate the main hypothesis.

**Variables:**
- Independent: Feedback condition (B: execution+mypy vs. C: execution+mypy+Z3)
- Dependent: pass@1 on curated ~50-problem arithmetic subset
- Controlled: Same model, temperature, k=5; Z3 specs pre-validated against EvalPlus tests

**Verification Protocol:**
1. Select curated subset: ~50 HumanEval problems with pure arithmetic / simple int/str types.
2. For each problem, use GPT-4o-mini to generate Z3 spec; validate spec against EvalPlus tests.
3. Discard problems where Z3 spec fails EvalPlus validation.
4. Run repair loop Conditions B and C on remaining validated subset.
5. Compare pass@1 per condition; report delta and confidence interval (subset may be underpowered).

**Success Criteria (PoC: Direction-based):**
- Primary: Positive pass@1 delta (Condition C > Condition B) on curated subset, even if not statistically significant
- Secondary: At least 30 problems with valid Z3 specs (minimum subset size for meaningful comparison)

**Failure Response:**
- IF fails (C ≤ B): Document as null result for Z3 sub-hypothesis; main hypothesis unaffected.
- IF Z3 spec quality too low (<30 valid): Report constraint as known limitation.

**Dependencies:** H-E1

**Source:** Phase 2A P2 prediction, PROVE_NEW claim 2, A5 assumption

---

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3
H-E1 → H-Z1 (parallel to H-M chain, secondary)
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | ≥10% of failing solutions have ≥1 mypy error on MBPP+ | STOP — reassess entire hypothesis |
| H-M1 | MUST_WORK | Spearman ρ < 0 (error count decreases across rounds) | EXPLORE — check A2 assumption |
| H-M2 | SHOULD_WORK | Condition B improves type-error problems more than non-type | EXPLORE — consider confound |
| H-M3 | MUST_WORK | p < 0.05 on MBPP+; absolute pass@1 ≥ 1% | PIVOT or ABANDON |
| H-Z1 | SHOULD_WORK | Positive delta (C > B) on curated subset | Document null result |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | Week 1-2 |
| Phase 2: Mechanism chain | H-M1, H-M2, H-M3 | Week 3-5 |
| Phase 2.5: Z3 secondary | H-Z1 | Week 6 |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**R1: Type Error Base Rate Too Low (from A1)**
- Description: If GPT-4o-mini's error profile on MBPP+/HumanEval+ is dominated by
  semantic/logic errors rather than type errors, mypy signal is too sparse to produce
  measurable improvement. Type error rate < 5% → H-E1 fails → cascade.
- Severity: **Critical** (blocks all downstream hypotheses)
- Likelihood: **Medium** (EvalPlus analysis suggests type errors are common, but GPT-4o-mini
  may be better at types than older models used in EvalPlus analysis)
- Affected Hypotheses: H-E1, H-M1, H-M3
- Mitigation:
  1. Prevention: Run pilot (50 problems) before full experiment to check base rate.
  2. Detection: H-E1 designed as early check.
  3. Response: If <5%, PIVOT to investigate which error categories dominate; revise hypothesis to target dominant category.

**R2: mypy Output Not Interpretable by LLM (from A2)**
- Description: GPT-4o-mini may not effectively parse/use structured mypy error
  output, making Condition B functionally identical to Condition A (extra tokens wasted).
- Severity: **High** (invalidates mechanism claim)
- Likelihood: **Low** (GPT-4o-mini has strong Python understanding; mypy messages are human-readable)
- Affected Hypotheses: H-M1, H-M3
- Mitigation:
  1. Prevention: Design repair prompt to explicitly reference mypy error field.
  2. Detection: H-M1 monitors mypy error reduction rate as proxy.
  3. Response: If H-M1 shows no reduction, analyze prompt vs. mypy output alignment; revise prompt engineering.

**R3: mypy False-Positive Rate on Benchmark Code Too High (from A3)**
- Description: mypy in permissive mode may still produce noise on dynamically-typed
  EvalPlus code, adding incorrect error messages that confuse the LLM.
- Severity: **High** (can degrade Condition B below Condition A)
- Likelihood: **Low-Medium** (permissive flags are standard; benchmark code is relatively simple Python)
- Affected Hypotheses: H-M1, H-M2, H-M3
- Mitigation:
  1. Prevention: Pilot test mypy on 50 problems; measure false-positive rate (mypy errors on passing solutions).
  2. Detection: Track mypy error rate on initially-correct solutions.
  3. Response: If >20% false-positive rate, add --no-error-summary flag or filter mypy output before feeding to LLM.

**R4: k=5 Insufficient to Observe Asymptotic Benefit (from A4)**
- Description: The mypy-guided repair improvement may require more rounds to accumulate,
  if the LLM needs multi-round conditioning on type feedback.
- Severity: **Medium** (delays or weakens effect observation)
- Likelihood: **Low** (Self-Debug shows k=3 captures most benefit; k=5 is conservative)
- Affected Hypotheses: H-M3
- Mitigation:
  1. Prevention: Log repair trajectories per round; check convergence.
  2. Detection: If improvement curve is still rising at k=5, note limitation.
  3. Response: Extend to k=10 in follow-up if budget allows; report k=5 as lower bound.

**R5: Z3 Spec Quality Too Low on Curated Subset (from A5)**
- Description: LLM-generated Z3 specs may not correctly encode problem semantics,
  generating misleading counterexamples that harm rather than help repair.
- Severity: **Medium** (affects H-Z1 only; main hypothesis unaffected)
- Likelihood: **Medium** (formal spec generation is error-prone even for pure functions)
- Affected Hypotheses: H-Z1
- Mitigation:
  1. Prevention: Pre-validate all Z3 specs against EvalPlus test cases; discard invalid specs.
  2. Detection: Track Z3 spec pass rate during validation step.
  3. Response: If <30 valid specs remain, report insufficient subset size; treat H-Z1 as inconclusive.

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Low type error base rate | A1 | H-E1, H-M1, H-M3 | Critical |
| R2: mypy not interpretable by LLM | A2 | H-M1, H-M3 | High |
| R3: mypy false-positive noise | A3 | H-M1, H-M2, H-M3 | High |
| R4: k=5 insufficient | A4 | H-M3 | Medium |
| R5: Z3 spec quality | A5 | H-Z1 | Medium |

**Risk Summary:** 1 Critical, 2 High, 2 Medium, 0 Low
**Primary Concern:** R1 (type error base rate) — early pilot check is essential.

### 4.3 Baseline Failure Pattern Risks

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| Self-Debug uses execution only — no type info surfaced | May find execution output sufficient; mypy adds marginal info only | Explicitly compare info content; measure H-M2 |
| Reflexion uses LLM-generated verbal feedback | LLM may generate its own type analysis from execution output | Add ablation: execution-only with "explain error type" prompt |
| HumanEval+ is underpowered for 1% effect | Primary result may not reach p<0.05 on HumanEval+ | Use MBPP+ as primary; HumanEval+ as secondary replication |

---

## 5. Dependency Graph (DAG) + Timeline

### 5.1 Dependency Graph

```
═══════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════════

[Level 0 - Root / Foundation]
    H-E1  (EXISTENCE, MUST_WORK — no dependencies)
    │                     │
    │                     │
    ▼                     ▼
[Level 1 - Primary       [Level 1 - Secondary
 Mechanism chain]         Z3 branch]
    H-M1 ← H-E1           H-Z1 ← H-E1
    │
    ▼
    H-M2 ← H-M1
    │
    ▼
    H-M3 ← H-M2

═══════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Secondary Path: H-E1 → H-Z1 (can run in parallel with H-M chain)
═══════════════════════════════════════════════════════════════
```

### 5.2 Verification Phases with Gate Conditions

**Phase 1 — Foundation (Week 1-2)**

| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | mypy base rate pilot + full benchmark | MUST_WORK |

→ Gate 1: If H-E1 fails (type error rate < 5%) → **STOP**, reassess hypothesis. If borderline (5-10%) → continue with reduced effect size expectation.

**Phase 2 — Core Mechanism Chain (Week 3-5)**

| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST_WORK |
| H-M2 | H-M1 | SHOULD_WORK |
| H-M3 | H-M2 | MUST_WORK |

→ Gate 2a: H-M1 must show negative Spearman ρ. Failure → EXPLORE mechanism interpretability.
→ Gate 2b: H-M3 must achieve p < 0.05 on MBPP+. Failure → PIVOT or ABANDON.

Note: H-M2 is SHOULD_WORK — failure narrows causal claim but does not block H-M3.

**Phase 2.5 — Z3 Secondary (Week 6, parallel-opportunistic)**

| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-Z1 | H-E1 | SHOULD_WORK |

→ Gate 2.5: Positive delta (C > B) expected but not required. Null result is valid publishable finding.

### 5.3 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 1 | H-Z1 | H-E1 | SHOULD_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | MUST_WORK |

### 5.4 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase / Hypothesis   │  W1-2  │  W3-4  │  W5    │  W6    │
─────────────────────┼────────┼────────┼────────┼────────┤
PHASE 1: Foundation  │        │        │        │        │
  H-E1               │ ██████ │        │        │        │
  [Gate 1]           │      ◆ │        │        │        │
─────────────────────┼────────┼────────┼────────┼────────┤
PHASE 2: Mechanisms  │        │        │        │        │
  H-M1               │        │ ██████ │        │        │
  H-M2               │        │   ████ │        │        │
  H-M3               │        │        │ ██████ │        │
  [Gate 2]           │        │        │      ◆ │        │
─────────────────────┼────────┼────────┼────────┼────────┤
PHASE 2.5: Z3 Sec.  │        │        │        │        │
  H-Z1               │        │        │        │ ██████ │
  [Gate 2.5]         │        │        │        │      ◆ │
─────────────────────┼────────┼────────┼────────┼────────┤
═══════════════════════════════════════════════════════════════════
Legend: ██ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

Note: H-M1 and H-M2 analyses are derived from the same repair-loop experiment
run for H-M3. W3-4 covers experiment execution + H-M1 analysis. W5 covers H-M3
primary analysis + H-M2 categorization analysis.

### 5.5 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Duration: 5 weeks (critical path)
Secondary Path: H-E1 → H-Z1 (1 additional week)

Slack Available: 1 week on H-Z1 branch

Note: H-M1, H-M2, H-M3 share the same experimental data
(repair-loop experiment). Analyses are sequential but
experiment execution is batched (weeks 3-4).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 5
  Existence:  2 (H-E1, H-Z1)
  Mechanism:  3 (H-M1, H-M2, H-M3)

Phases: 3 (Foundation, Mechanism, Z3 Secondary)
Total Duration: 6 weeks
Critical Path: 5 weeks
Execution Mode: Sequential chain (main) + parallel branch (Z3)

API Cost Estimate:
  Initial generation: 542 problems × 3 seeds × 1 call = 1,626 calls
  Repair rounds (main): 542 × 3 seeds × 5 rounds × 2 conditions = ~16,260 calls
  Z3 spec generation: ~50 problems × 1 call = 50 calls
  Total: ~18,000 calls at GPT-4o-mini pricing (~$15-25)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.7 Execution Order

1. Execute H-E1 (pilot + full benchmark, Week 1-2)
2. Evaluate Gate 1 → if ≥10% type error rate, proceed
3. Execute repair-loop experiment (Conditions A + B, full benchmarks, Week 3-4)
4. Analyze H-M1 (mypy error trajectory from experiment data)
5. Evaluate Gate 2a → if negative Spearman ρ, proceed; else EXPLORE
6. Analyze H-M3 (primary pass@1 comparison, Week 5)
7. Analyze H-M2 (per-category repair rate from experiment data, Week 5)
8. Evaluate Gate 2b → if p<0.05 on MBPP+, PASS; else PIVOT/ABANDON
9. Execute H-Z1 (curated Z3 subset experiment, Week 6)
10. Evaluate Gate 2.5 → positive delta expected; null result acceptable

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: Static analysis (mypy) as a structured feedback channel
in LLM repair loops provides measurably higher pass@1 than
execution-only repair on standard Python code generation benchmarks.

Supporting Evidence:
1. EvalPlus analysis (Liu et al. 2023) indicates type-related failures
   are common in LLM-generated Python — A1 assumption is plausible.
2. mypy output format is structured and human-readable — LLMs with
   strong Python understanding (GPT-4o-mini) should be able to parse
   and act on type-error messages (A2 evidence).
3. Self-Debug (Chen et al. 2023) demonstrated execution error messages
   guide repair — mypy provides richer, type-specific signal that should
   further narrow the repair distribution (causal step 3 analogy).

Strengths:
  - Clear, falsifiable causal mechanism (3-step chain)
  - Standard benchmarks (HumanEval+, MBPP+) enable replication
  - Controlled experiment design isolates the mypy variable
  - Established prior work (Self-Debug) provides lower bound

Expected Outcomes:
  PRIMARY (P1): Condition B > Condition A on MBPP+ (p < 0.05, Δ ≥ 1%)
  SECONDARY (P2): Condition C > Condition B on curated ~50-problem subset
  TERTIARY (P3): Monotonically decreasing mypy error count across k rounds

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): No significant difference in pass@1 between
execution+mypy and execution-only repair (p ≥ 0.05 on both benchmarks).

Counter-Arguments:
1. GPT-4o-mini may be so capable at Python that it already self-corrects
   type errors from execution output alone — the marginal signal from mypy
   may be negligible for a frontier model.
2. mypy false positives on EvalPlus code (dynamically-typed Python)
   could add noise that cancels the signal benefit (R3 risk).
3. HumanEval+/MBPP+ may not have sufficient type-error density (R1 risk) —
   if most failures are semantic/logic errors, mypy is irrelevant to most
   repair attempts, diluting the aggregate pass@1 signal.

Potential Failure Points:
  - R1: Type error base rate < 5% → H-E1 fails → cascade failure
  - R2: mypy output not parsed by LLM → H-M1 shows flat error trajectory
  - R3: mypy noise exceeds signal → Condition B performs worse than Condition A

Conditions Under Which H0 Would Be Supported:
  - If mypy error count does not decrease across rounds (P3 falsified)
  - If per-category analysis (H-M2) shows uniform improvement across error types
  - If absolute pass@1 delta is < 0.5% (effect too small to be meaningful)
  - If type error rate (H-E1) is < 5% of failures

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:

H-StaticRepair-v1 presents a testable, well-scoped claim with a clear
causal mechanism and standard evaluation protocol. However, the null
hypothesis raises two legitimate empirical concerns: (1) the type error
base rate on modern benchmarks with frontier models may be lower than
expected; and (2) frontier LLMs may implicitly self-diagnose type errors
from execution output, making mypy an informational redundancy.

Resolution Path:

The verification plan addresses this dialectic through:
1. Foundation first (H-E1): Empirically establishes type error prevalence
   before committing to mechanism verification — allows early exit if H0
   precondition is met.
2. Mechanism monitoring (H-M1): Tracks whether mypy signal is actually
   incorporated — distinguishes between "signal exists" and "signal used."
3. Category decomposition (H-M2): Tests whether improvement is type-specific,
   ruling out confounds (extra context, prompt length effects).
4. Gate conditions: Allow early detection of H0 support with defined responses.

Conditions for Thesis Support:
  - H-E1 PASSES (type error rate ≥ 10%)
  - H-M1 PASSES (mypy error count decreases across rounds)
  - H-M3 PASSES (p < 0.05 on MBPP+, Δ ≥ 1%)

Conditions for Antithesis Support:
  - H-E1 FAILS (type error rate < 5%)
  - H-M1 FAILS (flat or increasing error trajectory)
  - H-M3 shows Δ < 0 (Condition B worse than Condition A)

Nuanced Outcome Possibilities:
  1. Full Support: All MUST_WORK gates pass → Thesis validated → Phase 6 paper
  2. Partial Support: H-M3 passes with small effect size → Refined thesis
     ("mypy improves repair on type-dense problems")
  3. Mechanism Support Only: H-M1 passes, H-M3 borderline → Mechanism confirmed
     but effect size too small for practical significance
  4. No Support: H-E1 or H-M3 fail → Antithesis supported → Phase 0 pivot

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Type errors are ~20% of failures | GPT-4o-mini may have lower type error rate | H-E1 pilot check |
| Mechanism | mypy narrows repair distribution | LLM implicitly self-corrects from execution | H-M1 error trajectory |
| Specificity | Improvement is type-error-specific | Improvement is due to extra context length | H-M2 category analysis |
| Main Effect | Condition B > Condition A on MBPP+ | No significant difference (p ≥ 0.05) | H-M3 Welch's t-test |
| Secondary | Z3 adds signal beyond mypy | Z3 spec quality confounds the result | H-Z1 with spec validation |

**Overall Robustness Score:** Medium
**Confidence in Verification Plan:** 0.72
**Key Uncertainty:** Type error base rate under GPT-4o-mini (R1 — Critical risk)

---

## 7. Executive Summary & Appendices

### 7.1 Executive Summary

**Main Hypothesis:** H-StaticRepair-v1 (confidence: 0.72)
- mypy as structured feedback channel in LLM repair loops improves pass@1 beyond execution-only repair.

**Verification Structure:**
- Mode: Incremental (67% scope reduction — 4/6 claims are established prior work)
- Sub-Hypotheses: 5 total (H-E1, H-M1, H-M2, H-M3, H-Z1)
  - H-E (Existence): 2, H-M (Mechanism): 3
- Phases: 3 phases over 6 weeks
- Critical Gates: 3 MUST_WORK gates (H-E1, H-M1, H-M3)

**Risk Assessment:** Medium-High
- Primary concern: R1 (type error base rate < 5% would cascade-fail all downstream)
- Secondary concern: R3 (mypy false-positive noise on benchmark code)

**Immediate Action:** Begin Phase 1 with H-E1 pilot (50-problem sample, 1 week)

### 7.2 Verification Execution Order

**Phase 1: Foundation (2 weeks)**
- H-E1: Run mypy on initial GPT-4o-mini generations; measure type error prevalence
- Gate 1: MUST PASS (≥10% type error rate); failure → STOP

**Phase 2: Core Mechanisms (3 weeks)**
- H-M1: mypy error count trajectory across repair rounds (Spearman ρ < 0)
- H-M2: Category-specific repair rate comparison (type vs. non-type problems)
- H-M3: Primary pass@1 comparison Condition A vs. B on MBPP+ (p < 0.05, Δ ≥ 1%)
- Gate 2: H-M3 must pass; H-M2 failure narrows scope but does not block

**Phase 2.5: Z3 Secondary (1 week)**
- H-Z1: Curated ~50-problem Z3 subset; positive delta expected but not required
- Gate 2.5: Null result is acceptable publishable finding

### 7.3 Critical Decision Points

1. **Gate 1 (Foundation):** H-E1 must pass
   - < 5% type error rate → STOP, reassess hypothesis
   - 5-10% → continue with reduced effect size expectation
   - ≥ 10% → proceed to Phase 2

2. **Gate 2a (Mechanism activation):** H-M1 must show negative Spearman ρ
   - Flat/positive trajectory → EXPLORE prompt design; check A2 assumption

3. **Gate 2b (Main effect):** H-M3 must achieve p < 0.05 on MBPP+ with Δ ≥ 1%
   - p ≥ 0.05 on both → PIVOT (re-examine mechanism)
   - Negative Δ → ABANDON direction

4. **Gate 2.5 (Z3 secondary):** Optional — null result documented, not blocking

### 7.4 Open Questions

- What fraction of MBPP+ failures involve type errors under GPT-4o-mini? (H-E1 answers this)
- Does mypy permissive mode produce sufficiently low false-positive rate on EvalPlus-style code? (pilot check)
- Can LLM-generated Z3 specs be validated automatically, or does this require manual review? (H-Z1 protocol)
- Is the effect size consistent across HumanEval+ and MBPP+, or benchmark-specific?

### 7.5 Recommendations

1. **Immediate Actions:**
   - Start Phase 1 with 50-problem pilot (H-E1) to check R1 and R3 risks before full experiment
   - Set up measurement infrastructure (mypy runner, EvalPlus test harness, repair loop scaffold)

2. **Resource Allocation:**
   - Allocate 6 weeks total (5-week critical path + 1-week Z3 secondary)
   - Reserve $25 API budget for GPT-4o-mini calls

3. **Failure Management:**
   - Document all failures with gate result and action taken
   - Execute PIVOT strategy for H-M3 failure (check H-M1 trajectory first)
   - H-Z1 null result is publishable; do not abort H-Z1 early

---

### Appendices

**A. Phase 2A Reference**
- Source: 03_refinement.yaml (ID: H-StaticRepair-v1)
- Generated: 2026-08-26 | Schema: 10.0.0
- Discussion: 10 exchanges, 6 agents, all convergence criteria met

**B. MCP Tool Usage Summary**
- Archon MCP: NOT AVAILABLE (ablation mode — no Archon calls)
- ClearThought MCP: NOT AVAILABLE (ablation mode — reasoning performed inline)
- Exa MCP: NOT AVAILABLE (ablation mode — no additional search)
- Total MCP calls: 0 (ablation)
