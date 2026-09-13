# Verification Plan: Iso-Compute Feedback Type Comparison for LLM Code Generation

**Date:** 2026-08-05
**Hypothesis ID:** H-IsoComputeFeedback-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under HumanEval and MBPP benchmarks, for open-source instruction-tuned LLMs at 7B scale (Llama 3.1 8B primary; Qwen2.5-Coder-7B replication), if formal feedback type is varied between (A) pylint/mypy static analysis feedback and (B) execution test feedback — both in iterative repair mode at fixed token budget B=1000 output tokens per problem instance — then execution test feedback achieves a statistically significantly larger pass@1 improvement delta over no-feedback baseline than pylint/mypy feedback (McNemar's test, α=0.05), because execution feedback covers the full distribution of code errors (logic, runtime, type, syntax) while static analysis covers a subset with lower correlation to the specific logical failures that dominate HumanEval/MBPP problem types, as evidenced by automated pylint coverage analysis showing that pylint detects a significantly lower fraction of HumanEval baseline failures pre-execution than execution test feedback catches.

### 1.2 Alternative Hypothesis (H0)

There is no statistically significant difference in pass@1 improvement delta between pylint/mypy static analysis feedback and execution test feedback at equal token budget (B=1000 output tokens per problem) on HumanEval/MBPP for 7B instruction-tuned LLMs (H0: Δ_pylint = Δ_execution, McNemar's test α=0.05).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval + MBPP (standard) | Canonical standard benchmarks for Python code generation functional correctness; both have unit test oracles required for execution feedback condition. HumanEval: 164 algorithmic Python problems; MBPP: 374 Python problems. Full standard test sets used. |
| **Model** | Llama 3.1 8B Instruct (primary) + Qwen2.5-Coder-7B-Instruct (replication) | 7B-scale instruction-tuned; sufficient instruction-following capability for repair tasks (validated by Iterative Self-Repair 2026); feasible local inference; two different training regimes for replication diversity. |

**Dataset Details:**
- Source: HumanEval: Chen et al. 2021 (openai/human-eval repo); MBPP: Austin et al. 2021 (google-research/mbpp repo)
- Path: Standard benchmark loaders; available via lm-evaluation-harness or direct download

**Model Details:**
- Type: Open-source instruction-tuned decoder-only transformer
- Source: HuggingFace model hub: meta-llama/Llama-3.1-8B-Instruct; Qwen/Qwen2.5-Coder-7B-Instruct

### 1.4 Baseline Methods (for comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| No-feedback baseline (greedy decoding) | ~40-60% pass@1 (7B models) | HumanEval, MBPP |
| Reflexion (execution + verbal feedback) | 91% pass@1 (GPT-4) — upper bound reference | HumanEval |
| FeedbackEval compiler feedback | ~48% pass@1 | HumanEval |
| Type-Constrained Decoding (Mündler et al. 2025) | >50% compilation error reduction | HumanEval, MBPP |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Llama 3.1 8B Instruct can follow iterative repair instructions via prompting alone, without fine-tuning | Iterative Self-Repair [Arimbur, 2026]: +9.8pp HumanEval with prompting-based self-repair | Neither execution nor pylint conditions improve — comparison uninformative |
| A2 | HumanEval/MBPP baseline failures are predominantly logic/runtime errors (not syntax) | Mündler et al. [2025]: type-constrained decoding reduces compilation errors >50%, implying remaining failures are logic/runtime | Pylint may cover large fraction of failures → similar improvement to execution → hypothesis refuted (publishable null result) |
| A3 | Token budget B=1000 output tokens allows ≥2 meaningful repair rounds on HumanEval | HumanEval solutions ~50-200 lines; Iterative Self-Repair finds most gains in rounds 1-2 | Rerun at B=2000; report per-round breakdown |
| A4 | cyb3rlab/CodeEnhancer (or custom pylint wrapper) adapts to HumanEval/MBPP functional correctness in 2-4 days | Pylint feedback loop is straightforward (~50-100 lines Python); CodeEnhancer provides this loop | Implement custom lightweight pylint wrapper independently |
| A5 | Qwen2.5-Coder-7B is sufficiently similar to Llama 3.1 8B in capability tier to serve as replication check | Both 7B-scale, instruction-tuned, 2024-2025; same parameter scale | Dramatically different feedback type ranking = interaction finding that strengthens paper |

### 1.6 Research Gap & Novelty

**Gap:** No existing study provides iso-compute comparison of execution vs. static analysis (pylint/mypy) feedback in repair mode on HumanEval/MBPP functional correctness. FeedbackEval [Dai et al., 2025] compared compiler/test/minimal feedback but excluded semantic pylint/mypy and does not normalize by token budget. Blyth et al. [2025] tested pylint only on PythonSecurityEval (security metric, not pass@k). Pylint/mypy's functional correctness effect on HumanEval is empirically unknown.

**Novelty:** First iso-compute head-to-head comparison of execution feedback vs. pylint/mypy static analysis feedback in iterative repair mode on standard Python functional correctness benchmarks, with automated pylint failure coverage analysis that mechanistically explains the observed ranking.

**Scope Reduction:** 60% — Claims 1-3 (execution feedback improves pass@1; type-constrained decoding reduces compilation errors; pylint iterative feedback reduces security issues) are BUILD_ON and not re-verified. Only Claims 4-5 (PROVE_NEW: iso-compute comparison; pylint functional correctness effect) are experimental targets.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Pylint/Mypy Feedback Produces Measurable pass@1 Delta**

**Statement**: Under HumanEval and MBPP benchmarks, if pylint/mypy static analysis feedback is applied in iterative repair mode at fixed token budget B=1000 output tokens per problem using Llama 3.1 8B Instruct, then a measurable pass@1 delta (positive, near-zero, or negative) over no-feedback baseline is produced, because any feedback mechanism that triggers re-generation creates some opportunity for improvement regardless of signal quality.

**Rationale** (2-3 sentences):
This existence hypothesis establishes that the pylint/mypy repair loop functions as an experimental condition — it can produce a measurement. Without this confirmation, the comparison with execution feedback is undefined. A null result here (Δ_pylint ≈ 0) is the key publishable finding distinguishing "static analysis is ineffective" from "we couldn't run the experiment."

**Variables** (from Phase 2A):
- Independent: Feedback Type = pylint_mypy (vs. no_feedback baseline)
- Dependent: pass@1 improvement delta (pass@1(pylint_condition) - pass@1(no_feedback_baseline))
- Controlled: Llama 3.1 8B Instruct, HumanEval (164 problems) + MBPP (374 problems), B=1000 output tokens, greedy decoding, same prompt template

**Verification Protocol** (3-5 steps):
1. Run no-feedback baseline (greedy decoding, single pass) on all HumanEval (164) and MBPP (374) problems with Llama 3.1 8B; record pass/fail per problem.
2. Run pylint/mypy repair condition: generate code → run pylint+mypy → format warnings as structured feedback → generate repair → repeat until B=1000 total output tokens consumed; record final pass/fail.
3. Compute Δ_pylint = pass@1(pylint_condition) - pass@1(no_feedback_baseline) for HumanEval and MBPP separately.
4. Run pylint+mypy on all no-feedback baseline failure cases without execution; record fraction flagged with at least one warning/error (automated coverage analysis).
5. Report: Δ_pylint value, 95% CI via bootstrap, per-round improvement trajectory (rounds 1-3), and pylint pre-execution failure coverage fraction.

**Success Criteria** (PoC: Direction-based):
- Primary: Δ_pylint is computable and finite (experiment runs end-to-end without systematic failure)
- Secondary: |Δ_pylint| > 0 (any measurable effect, positive or negative — null result equally valid)

**Failure Response**:
- IF fails: PIVOT — if pylint wrapper fails to run, implement custom 50-100 line Python pylint wrapper; if Llama 3.1 8B fails repair instructions, document and report

**Dependencies**: None (foundation)

**Source**: Phase 2A SH1, established_facts Claim 5 (PROVE_NEW)

---

---
**H-M1: Execution Feedback Achieves Larger pass@1 Delta Than Pylint at Iso-Compute**

**Statement**: Under HumanEval and MBPP benchmarks, if execution test feedback is applied in iterative repair mode at B=1000 output tokens per problem using Llama 3.1 8B (compared to pylint/mypy at identical budget), then execution test feedback achieves a statistically significantly larger pass@1 improvement delta over no-feedback baseline (McNemar's test, α=0.05), because execution feedback reveals the full distribution of code errors (expected vs. actual output for failing tests) while pylint/mypy reveals only a subset (syntax, type annotations, style).

**Rationale** (2-3 sentences):
This is the core mechanism hypothesis: the information-theoretic superiority of execution feedback (complete program semantics) over static analysis (subset of pre-execution errors) should translate into a larger repair success rate. The causal mechanism is operationalized as the pass@1 delta comparison at equal token budget. Step 2 of the causal chain — the informativeness of the feedback signal determines repair success — is directly tested here.

**Variables** (from Phase 2A):
- Independent: Feedback Type = execution_test vs. pylint_mypy (both at B=1000 tokens)
- Dependent: pass@1 improvement delta difference (Δ_execution - Δ_pylint), statistical significance via McNemar's test
- Controlled: Llama 3.1 8B Instruct, HumanEval (164 problems) + MBPP (374 problems), B=1000 tokens per problem, temperature=0, same prompt template

**Verification Protocol** (3-5 steps):
1. Run execution repair condition: generate code → run unit test suite → format test failures as structured feedback → generate repair → repeat until B=1000 total output tokens consumed; record final pass/fail for all HumanEval (164) and MBPP (374) problems.
2. Compute Δ_execution = pass@1(execution_condition) - pass@1(no_feedback_baseline) for each benchmark.
3. Run McNemar's test on paired binary outcomes (each problem: pass=1/fail=0): compare (pylint_pass, baseline_fail) vs. (execution_pass, baseline_fail) counts for HumanEval and MBPP separately.
4. Report Δ_execution, Δ_pylint, their difference (Δ_execution - Δ_pylint), McNemar's test statistic and p-value, and 95% CI on the difference.
5. Replicate steps 1-4 with Qwen2.5-Coder-7B-Instruct as replication check.

**Success Criteria** (PoC: Direction-based):
- Primary: Δ_execution > Δ_pylint with p<0.05 (McNemar's test) on HumanEval AND on MBPP for Llama 3.1 8B
- Secondary: Qwen2.5-Coder-7B shows same directional ranking (replication consistency)

**Failure Response**:
- IF fails: EXPLORE — null result (Δ_execution ≈ Δ_pylint) is publishable as "pylint achieves parity with execution at equal token budget"; document as main finding, not failure

**Dependencies**: H-E1 (pylint experiment must run successfully)

**Source**: Phase 2A SH2, established_facts Claim 4 (PROVE_NEW), causal_mechanism step 2-3

---

---
**H-M2: Pylint Pre-Execution Coverage is Below 50% of HumanEval Baseline Failures**

**Statement**: Under the HumanEval baseline failure cases (problems that fail in no-feedback single-pass generation with Llama 3.1 8B), if pylint+mypy is run on the failing code without execution, then fewer than 50% of failure cases receive at least one pylint/mypy warning or error, because HumanEval failures are predominantly logic/runtime errors (wrong algorithm, off-by-one, incorrect data structure usage) that pylint cannot detect without executing the code.

**Rationale** (2-3 sentences):
This mechanism hypothesis operationalizes the causal explanation for H-M1: if pylint's lower pass@1 delta is caused by lower error coverage, the coverage analysis should show pylint misses >50% of baseline failures pre-execution. This automated measurement converts the mechanism claim from a post-hoc narrative into a testable prediction. The result directly explains WHY execution feedback outperforms pylint (if H-M1 is supported) or challenges the explanation (if pylint coverage is actually high).

**Variables** (from Phase 2A):
- Independent: Feedback signal type (pylint+mypy vs. execution — operationalized as coverage measurement)
- Dependent: Fraction of HumanEval baseline failures that pylint/mypy flags with ≥1 warning/error (pre-execution)
- Controlled: HumanEval failing solutions from no-feedback baseline, default pylint checkers, Llama 3.1 8B generated code

**Verification Protocol** (3-5 steps):
1. Collect all HumanEval problems where no-feedback baseline fails (code generates incorrect output for ≥1 test case).
2. For each failing solution, run pylint+mypy on the code file without executing against test cases; record whether ≥1 warning or error is flagged.
3. Compute coverage = (number of failing solutions with ≥1 pylint/mypy flag) / (total failing solutions).
4. Report coverage fraction with 95% CI (bootstrap), distribution of pylint rule categories triggered (error vs. warning vs. convention), and comparison to 100% (execution catches all test failures by definition).
5. Perform sub-analysis: identify which pylint rule categories correlate most with functional failures.

**Success Criteria** (PoC: Direction-based):
- Primary: coverage < 0.50 (pylint flags <50% of HumanEval baseline failures pre-execution)
- Secondary: Dominant pylint categories are style/convention (not error), supporting the informativeness gap claim

**Failure Response**:
- IF fails (coverage >80%): EXPLORE — mechanism claim is challenged; if H-M1 is still supported (Δ_execution > Δ_pylint), the explanation needs revision; if H-M1 is also not supported, the entire mechanism-plus-main-claim is null (publishable as refutation)

**Dependencies**: H-M1 (execution condition must be run; baseline failures already collected)

**Source**: Phase 2A prediction P2, causal_mechanism step 2, key_tension

---

---
**H-M3: LLM Successfully Repairs More Failures With Execution Feedback in Subsequent Attempts**

**Statement**: Under HumanEval and MBPP, if Llama 3.1 8B Instruct is conditioned on execution test feedback (expected vs. actual output for failing tests) after round 1, then the per-round pass@1 improvement trajectory shows positive incremental gains in rounds 1-2 that exceed the incremental gains produced by pylint/mypy feedback in rounds 1-2, because execution feedback provides actionable information about what the code does wrong (enabling targeted repairs) while pylint/mypy feedback at round 2 may provide redundant information if it already flagged the issue in round 1.

**Rationale** (2-3 sentences):
This hypothesis tests the downstream consequence of the coverage gap: not just that execution feedback is better overall, but that this superiority is concentrated in the per-round improvement trajectory. If execution feedback leads to faster repair (more improvement per round), it supports the causal chain from step 3: more informative signal → more successful repair attempts. The per-round analysis is the secondary evidence that validates the causal direction.

**Variables** (from Phase 2A):
- Independent: Feedback Type (execution_test vs. pylint_mypy) crossed with Repair Round (1, 2, 3)
- Dependent: per-round pass@1 after each repair round; incremental improvement (pass@1[round n] - pass@1[round n-1])
- Controlled: Llama 3.1 8B Instruct, HumanEval (164) + MBPP (374), B=1000 total output tokens, greedy decoding

**Verification Protocol** (3-5 steps):
1. During execution and pylint repair runs (from H-M1), record intermediate pass/fail state after each repair round (round 1, 2, 3) before token budget is exhausted.
2. Compute per-round pass@1 for each condition and each benchmark.
3. Compute incremental improvement per round: Δround_n = pass@1[round n] - pass@1[round n-1] for execution and pylint conditions.
4. Compare execution vs. pylint incremental improvement in rounds 1-2 on HumanEval and MBPP.
5. Plot per-round improvement trajectory as Figure 2 in the paper (diminishing returns profile).

**Success Criteria** (PoC: Direction-based):
- Primary: Execution condition shows larger incremental improvement in round 1 than pylint condition on HumanEval
- Secondary: Both conditions show diminishing returns (Δround_2 < Δround_1), consistent with repair saturation

**Failure Response**:
- IF fails: EXPLORE — if pylint shows equal or larger per-round improvement, document as "pylint achieves parity in repair speed despite lower overall coverage"; does not invalidate H-M1 finding

**Dependencies**: H-M2 (coverage analysis informs interpretation; per-round data collected during H-M1 runs)

**Source**: Phase 2A causal_mechanism step 3, prediction P1 (per-round trajectory), discussion_synthesis key insight on diminishing returns

---

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          HYPOTHESIS INVENTORY (4 hypotheses)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID   | Type      | Statement (Brief)                                        | Prerequisites | Source         |
|------|-----------|----------------------------------------------------------|---------------|----------------|
| H-E1 | EXISTENCE | Pylint/mypy repair loop produces measurable pass@1 delta | None          | SH1, Claim 5   |
| H-M1 | MECHANISM | Execution feedback > pylint at iso-compute (McNemar p<0.05) | H-E1       | SH2, Claim 4   |
| H-M2 | MECHANISM | Pylint pre-execution coverage < 50% of HumanEval failures | H-M1         | P2, causal step 2 |
| H-M3 | MECHANISM | Per-round improvement trajectory: execution > pylint in round 1 | H-M2    | P1, causal step 3 |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Pylint repair loop runs end-to-end, Δ_pylint is computable | PIVOT: implement custom pylint wrapper |
| H-M1 | MUST_WORK | Δ_execution > Δ_pylint, McNemar p<0.05 on HumanEval + MBPP | EXPLORE: null result (Δ_execution ≈ Δ_pylint) is publishable |
| H-M2 | SHOULD_WORK | Pylint coverage < 50% of HumanEval baseline failures | EXPLORE: mechanism explanation challenged; revise causal claim |
| H-M3 | SHOULD_WORK | Execution shows larger per-round improvement in round 1 | EXPLORE: document as per-round parity finding |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3 | 3 weeks |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1: Model Instruction-Following Failure**

**Source Assumption:** A1 — Llama 3.1 8B can follow iterative repair instructions via prompting

**Description:** If Llama 3.1 8B fails to correctly parse and act on repair feedback prompts, both execution and pylint conditions produce near-zero Δ values, making the comparison uninformative.

**Affected Hypotheses:** H-E1, H-M1, H-M2, H-M3 (all)

**Severity:** Critical

**Mitigation Strategy:**
1. **Prevention:** Run a pilot experiment with 20 HumanEval problems before full run; verify repair prompts are being followed by inspecting round-1 code changes.
2. **Detection:** If Δ_pylint and Δ_execution are both <1pp after 20 problems, halt and diagnose.
3. **Response:**
   - PIVOT: Adjust repair prompt template to be more explicit about the repair task structure.
   - SCOPE: If prompting-only repair consistently fails, document as a model capability limitation (publishable finding about 7B model repair ceiling).

**Early Warning Indicators:**
- Less than 5% of round-1 repaired solutions show any code change from original generation
- Both Δ values < 0.5pp after first 50 problems

---

**Risk R2: Pylint Functional Coverage Near 100%**

**Source Assumption:** A2 — HumanEval/MBPP failures are predominantly logic/runtime errors (not syntax), making execution more informative than pylint

**Description:** If pylint/mypy flags >80% of HumanEval baseline failures, the assumed coverage gap between pylint and execution is small, predicting similar repair outcomes (H0 supported).

**Affected Hypotheses:** H-M1, H-M2 (directly)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Run pylint coverage analysis on 50 baseline failures as preliminary check before full experiment.
2. **Detection:** If preliminary coverage > 70%, adjust hypothesis framing to "testing pylint parity."
3. **Response:**
   - EXPLORE: If H-M1 is null (Δ_execution ≈ Δ_pylint) AND coverage is high, the publishable finding is "pylint achieves execution parity because its coverage is sufficient for HumanEval problem types."
   - PIVOT: Frame around the coverage measurement as the novel contribution regardless of outcome.

**Early Warning Indicators:**
- Preliminary pylint coverage analysis shows >70% of HumanEval failures flagged
- Δ_pylint ≈ Δ_execution after first 50 problems

---

**Risk R3: Token Budget B=1000 Insufficient for Meaningful Repair**

**Source Assumption:** A3 — B=1000 output tokens allows ≥2 meaningful repair rounds

**Description:** If HumanEval solutions require >500 tokens each for repair generation, B=1000 only allows ~1 repair round, reducing the ability to detect differences between feedback types.

**Affected Hypotheses:** H-M1, H-M3 (per-round analysis)

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Measure actual token usage per round in pilot experiment; verify mean repair generation < 400 tokens.
2. **Detection:** If >50% of problems exhaust token budget after round 1, report H-M3 as "single-round comparison" (weakened but still valid).
3. **Response:**
   - SCOPE: Report results at B=1000 as primary; flag that B=2000 would provide more repair rounds as future work.
   - PIVOT: If B=1000 is clearly too small, rerun at B=2000 (additional engineering, not fundamental redesign).

**Early Warning Indicators:**
- Mean tokens per repair round > 450 in pilot
- <20% of problems reach round 2

---

**Risk R4: CodeEnhancer Adaptation Exceeds Engineering Budget**

**Source Assumption:** A4 — cyb3rlab/CodeEnhancer adapts to HumanEval/MBPP in 2-4 days

**Description:** If the CodeEnhancer adaptation proves infeasible or takes >1 week, the pylint repair condition cannot be run on schedule.

**Affected Hypotheses:** H-E1 (directly), H-M1, H-M2, H-M3 (blocked)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Attempt CodeEnhancer adaptation on first day; have fallback ready as parallel track.
2. **Detection:** If CodeEnhancer adaptation exceeds 2 days without working benchmark loader, switch to fallback.
3. **Response:**
   - PIVOT: Implement custom pylint wrapper (50-100 lines Python) independent of CodeEnhancer; this is simpler and more controllable.
   - ABORT CodeEnhancer dependency: the fallback is lower risk and fully sufficient.

**Early Warning Indicators:**
- CodeEnhancer's benchmark loader fails to load HumanEval correctly after 2 days
- CodeEnhancer's evaluation metric incompatible with pass@k

---

**Risk R5: Replication Model Shows Reversed Feedback Type Ranking**

**Source Assumption:** A5 — Qwen2.5-Coder-7B shows consistent feedback type ranking with Llama 3.1 8B

**Description:** If Qwen2.5-Coder-7B shows Δ_pylint > Δ_execution (opposite ranking), the replication check becomes an interaction finding rather than a consistency confirmation.

**Affected Hypotheses:** H-M1 (replication component)

**Severity:** Low (interaction finding strengthens, not weakens, paper)

**Mitigation Strategy:**
1. **Prevention:** N/A — this risk is actually a positive finding if it occurs.
2. **Detection:** Compare ranking direction for both models after initial results.
3. **Response:**
   - EXPLORE: If ranking reverses, report as interaction between model training regime (general vs. code-specialized) and feedback type effectiveness; frame as additional contribution.

**Early Warning Indicators:** N/A (low-severity finding regardless of direction)

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Model instruction-following failure | A1 | All (H-E1, H-M1, H-M2, H-M3) | Critical |
| R2: Pylint coverage near 100% | A2 | H-M1, H-M2 | High |
| R3: Token budget B=1000 insufficient | A3 | H-M1, H-M3 | Medium |
| R4: CodeEnhancer adaptation exceeds budget | A4 | H-E1 (blocker), H-M1-3 | High |
| R5: Replication model shows reversed ranking | A5 | H-M1 (replication) | Low |

**Critical Risks: 1 | High Risks: 2 | Medium Risks: 1 | Low Risks: 1**

### 4.3 Baseline Failure Pattern Analysis

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| FeedbackEval uses syntax-only "compiler feedback" (not semantic pylint) | Our pylint condition may behave differently than FeedbackEval baseline, making direct quantitative comparison difficult | Clearly distinguish pylint/mypy (semantic static analysis) from compiler-only feedback in paper |
| Blyth et al. tested pylint only on security benchmarks | Unknown how pylint rule coverage transfers from security-focused rules to functional correctness failures | Run preliminary coverage analysis (H-M2 protocol) before committing to full experiment |
| Reflexion (upper bound) uses GPT-4, not 7B models | Cannot directly compare our 7B results to Reflexion 91% pass@1 | Frame Reflexion as an upper-bound reference, not a benchmark to beat |

---

## 5. Dependency Graph (DAG) and Timeline

### 5.1 Dependency Graph

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (EXISTENCE - no dependencies, MUST_WORK)
         │
         ▼
[Level 1 - Primary Mechanism]
    H-M1 ← H-E1 (MUST_WORK - core experimental comparison)
         │
         ▼
[Level 2 - Coverage Analysis]
    H-M2 ← H-M1 (SHOULD_WORK - mechanism explanation)
         │
         ▼
[Level 3 - Trajectory Analysis]
    H-M3 ← H-M2 (SHOULD_WORK - per-round evidence)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total: 4 sequential hypotheses, 2 MUST_WORK gates
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |

### 5.3 Verification Phases

**Phase 1 - Foundation (H-E1)**
- Hypothesis: H-E1 — pylint/mypy repair loop runs and produces measurable Δ
- Gate 1: MUST PASS — if H-E1 fails, STOP and reassess entire experimental setup

**Phase 2 - Core Mechanisms (H-M1, H-M2, H-M3)**
- H-M1: Execution vs. pylint iso-compute comparison (MUST_WORK)
- H-M2: Pylint pre-execution coverage analysis (SHOULD_WORK)
- H-M3: Per-round improvement trajectory analysis (SHOULD_WORK)
- Gate 2: H-M1 must pass — H-M2/H-M3 failures narrow scope but don't invalidate

### 5.4 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis       │ W1-2    │ W3-4    │ W5      │
───────────────────────┼─────────┼─────────┼─────────┼
PHASE 1: Foundation
  H-E1 (pylint loop)  │ ████████│         │         │
  [Gate 1]             │       ◆ │         │         │
───────────────────────┼─────────┼─────────┼─────────┼
PHASE 2: Mechanisms
  H-M1 (comparison)   │         │ ████████│         │
  H-M2 (coverage)     │         │ ████████│         │
  H-M3 (trajectory)   │         │         │ ████    │
  [Gate 2]             │         │       ◆ │         │
───────────────────────┼─────────┼─────────┼─────────┼
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
Note: H-M2 (coverage analysis) runs alongside H-M1 as data collected during same experiment run
═══════════════════════════════════════════════════════════════════
```

### 5.5 Critical Path Analysis

```
Critical Path: H-E1 → H-M1 → H-M3
Total Duration: 5 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M3) = 5 weeks
Note: H-M2 coverage analysis runs in parallel with H-M1 (same data collection run)
Slack: H-M2 has 0 slack (data collected with H-M1); H-M3 has 0 slack (depends on H-M1 per-round data)
```

### 5.6 Resource Summary

```
Total Hypotheses: 4
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1, H-M2, H-M3)

Verification Phases: 2
1. Foundation (H-E1): 2 weeks
2. Mechanisms (H-M1/2/3): 3 weeks

Total Duration: 5 weeks
Execution Mode: Sequential chain (H-M2 partially parallel with H-M1)
Models: Llama 3.1 8B (primary) + Qwen2.5-Coder-7B (replication)
Datasets: HumanEval (164 problems) + MBPP (374 problems) = 538 total problems
Sample Size: 538 problems × 4 conditions × 2 models = 4,304 problem-condition-model evaluations
```

### 5.7 Execution Order

```
Step 1: Setup pylint wrapper + execution repair framework — Week 1
Step 2: Run no-feedback baseline on HumanEval + MBPP (both models) — Week 1
Step 3: Execute H-E1 (pylint repair condition, Llama 3.1 8B) — Week 1-2
Step 4: Evaluate Gate 1 → If pass, proceed
Step 5: Execute H-M1 (execution repair condition, Llama 3.1 8B; + replication with Qwen) — Week 3-4
Step 6: Run H-M2 (pylint coverage analysis on baseline failures — same data collection run as H-M1) — Week 3-4
Step 7: Evaluate Gate 2 → If H-M1 passes, proceed
Step 8: Execute H-M3 (per-round trajectory analysis from H-M1/H-M2 data) — Week 5
Step 9: Verification complete → Proceed to Phase 2C experiment design
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
THESIS
─────────────────────────────────────────────────────
Core Claim: Under HumanEval and MBPP, at fixed token budget B=1000 output tokens per
problem, execution test feedback in iterative repair mode achieves a statistically
significantly larger pass@1 improvement delta than pylint/mypy static analysis feedback
for 7B instruction-tuned LLMs.

Supporting Evidence:
1. Information-theoretic argument: execution feedback provides complete program semantics
   (expected vs. actual output) — pylint provides only a pre-execution subset (syntax, type,
   style warnings) with lower correlation to logical failures dominating HumanEval/MBPP
2. Prior execution feedback literature: Self-Debug [Chen et al., 2023] +12% MBPP;
   Reflexion [Shinn et al., 2023] 91% HumanEval — both show strong execution signal benefits
3. Pylint functional correctness on HumanEval has no direct evidence — the absence of
   positive evidence is itself evidence of the gap

Strengths:
- Clear causal mechanism (coverage gap → repair success gap)
- Testable with pre-specified statistical test (McNemar's α=0.05)
- Null result equally interpretable (pylint parity with execution at equal budget)
- Two benchmarks (HumanEval + MBPP) + two models for replication

Expected Outcomes:
- Primary: Δ_execution > Δ_pylint, McNemar p<0.05 on HumanEval AND MBPP for Llama 3.1 8B
- Secondary: Pylint coverage < 50% of HumanEval baseline failures (automated measurement)
- Tertiary: Type-constrained decoding achieves positive Δ in one-pass prevention mode
```

### 6.2 Antithesis (H0-Based)

```
ANTITHESIS
─────────────────────────────────────────────────────
Null Hypothesis (H0): There is no statistically significant difference in pass@1
improvement delta between pylint/mypy and execution test feedback at equal token budget
(B=1000) on HumanEval/MBPP for 7B instruction-tuned LLMs.

Counter-Arguments:
1. Pylint catches some logical errors (undefined variables, wrong function signatures,
   unused return values, type mismatches in function calls) — the overlap with execution
   feedback's coverage may be larger than assumed
2. LLMs may be better at interpreting pylint's structured warning codes than at reasoning
   about unit test failure traces — offsetting the coverage advantage of execution
3. At B=1000 tokens, both conditions may hit diminishing returns at round 1-2 regardless
   of feedback quality — the token budget may be the binding constraint, not the signal

Potential Failure Points:
- R2 (pylint coverage near 100%): if pylint catches most HumanEval failures, the assumed
  coverage gap collapses
- R1 (model instruction-following): if Llama 3.1 8B doesn't effectively use execution
  traces to identify repair targets, execution's advantage is lost
- R3 (token budget too small): if B=1000 only allows 1 repair round, the signal quality
  difference may not have time to manifest

Conditions Under Which H0 Would Be Supported:
- If McNemar's test shows p>0.05 for Δ_execution vs. Δ_pylint on HumanEval
- If pylint pre-execution coverage analysis shows >80% coverage (mechanism claim falls)
- If both Llama 3.1 8B and Qwen2.5-Coder-7B show Δ_pylint ≈ Δ_execution
```

### 6.3 Synthesis

```
SYNTHESIS
─────────────────────────────────────────────────────
Balanced Assessment:

The hypothesis H-IsoComputeFeedback-v1 presents a testable claim grounded in the
information-theoretic argument that execution feedback's complete semantic coverage
outperforms static analysis's subset coverage for iterative code repair. However, the
null hypothesis raises valid concerns: pylint's actual coverage of HumanEval failures
is empirically unknown, and the LLM's ability to leverage execution trace information
effectively is itself a model capability assumption.

Resolution Path:

The verification plan addresses this dialectic through:
1. Foundation verification (H-E1): Establishes that the pylint repair loop functions
   as an experimental condition before comparing to execution
2. Sequential mechanism testing (H-M1 → H-M3): Tests the causal chain step-by-step
   — first the outcome (pass@1 delta comparison), then the mechanism (coverage),
   then the trajectory (per-round improvement)
3. Gate conditions: Allow early detection of H0 support (if H-E1 fails, if H-M1
   null result is found)
4. Pre-specified statistics: McNemar's test α=0.05 prevents post-hoc outcome switching

Conditions for Thesis Support:
- H-E1 passes (pylint repair loop runs successfully)
- H-M1 supported: Δ_execution > Δ_pylint with p<0.05 (McNemar's)
- H-M2 supported: pylint coverage < 50% (mechanism confirmed)

Conditions for Antithesis Support:
- H-M1 null: p>0.05 or Δ_pylint ≥ Δ_execution
- H-M2 refuted: pylint coverage > 80% (mechanism claim falls)

Nuanced Outcome Possibilities:
1. Full Support: Δ_execution > Δ_pylint, p<0.05; coverage < 50% → thesis validated,
   mechanism explained
2. Partial Support: Δ_execution > Δ_pylint but coverage > 50% → main claim holds but
   mechanism explanation needs revision
3. Null Result (Publishable): Δ_execution ≈ Δ_pylint (p>0.05) → pylint parity with
   execution at equal token budget — directly actionable for production systems
4. Reversed Result (Novel): Δ_pylint > Δ_execution → static analysis outperforms
   execution on functional correctness for 7B models — unexpected major finding

Overall Robustness: HIGH (all four outcomes produce interpretable, publishable findings)
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Pylint repair loop runs and produces measurable Δ | Loop may fail due to CodeEnhancer adaptation issues | H-E1 test; fallback to custom wrapper |
| Coverage | Pylint covers <50% of HumanEval failures (logic/runtime dominate) | Pylint may cover >50% if type errors are common | H-M2 automated measurement |
| Mechanism | Execution feedback → larger repair success via complete semantic info | LLM may not effectively use execution traces | H-M1 pass@1 delta comparison |
| Scope | Results generalize to 7B instruction-tuned models | 7B only; 70B behavior unknown | Explicit scope statement in paper |
| Replication | Both models show same direction of feedback type ranking | Qwen2.5-Coder may show different ranking due to code specialization | H-M1 replication; interaction finding if reversed |

**Overall Robustness Score:** High

**Confidence in Verification Plan:** 0.75

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Execution test feedback achieves statistically significantly larger pass@1 delta than pylint/mypy feedback in iterative repair mode at iso-compute (B=1000 output tokens/problem) for 7B LLMs on HumanEval/MBPP
- ID: H-IsoComputeFeedback-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (60% scope reduction from BUILD_ON established facts)
- Sub-Hypotheses: 4 total (H-E: 1, H-M: 3)
- Phases: 2 phases over 5 weeks
- Critical Gates: 2 decision points (Gate 1: H-E1, Gate 2: H-M1)

**Risk Assessment:** High (R1 Critical: instruction-following; R4 High: CodeEnhancer adaptation)
- Primary concerns: CodeEnhancer adaptation feasibility (2-4 days); pylint functional coverage empirically unknown

**Immediate Action:** Begin Phase 1 with H-E1 — set up pylint wrapper and run no-feedback baseline on HumanEval + MBPP (Llama 3.1 8B)

### 7.2 Conclusions

**Key Achievements:**
- 4 hypotheses across 2 phases (1 MUST_WORK + 1 MUST_WORK + 2 SHOULD_WORK)
- H0 addressed: Δ_pylint = Δ_execution (directly testable, null result publishable)
- All 4 possible outcomes (full support, partial support, null, reversed) produce interpretable findings

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Pylint/mypy repair loop produces measurable pass@1 delta on HumanEval/MBPP
- Gate 1: MUST PASS

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: Execution feedback > pylint at iso-compute (McNemar p<0.05) — MUST_WORK
- H-M2: Pylint pre-execution coverage < 50% of HumanEval failures — SHOULD_WORK
- H-M3: Per-round improvement trajectory shows execution > pylint in round 1 — SHOULD_WORK
- Gate 2: H-M1 must pass; H-M2/H-M3 failures narrow but don't invalidate

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, debug pylint wrapper or switch to custom implementation; reassess if model instruction-following is the issue
   - PASS → Proceed to Phase 2

2. **Gate 2 (Primary Mechanism):** H-M1 McNemar's test
   - NULL RESULT (p>0.05) → Document as publishable null result: "pylint achieves parity with execution at equal token budget"; proceed to paper writing with null framing
   - PASS (p<0.05) → Proceed to H-M2/H-M3 mechanism confirmation

**Open Questions:**
- What fraction of HumanEval baseline failures does pylint detect pre-execution? (P2 — core empirical unknown)
- Does Qwen2.5-Coder-7B show the same feedback type ranking as Llama 3.1 8B? (replication)
- At what token budget B does the execution vs. pylint gap shrink? (future work, not in scope)
- Which pylint rule categories correlate most with functional failures? (sub-analysis from H-M2 data)

**Recommendations:**

1. **Immediate Actions:**
   - Start Phase 1 with H-E1; attempt CodeEnhancer adaptation on day 1 with parallel custom wrapper fallback ready
   - Run pilot experiment on 20 HumanEval problems before full run to validate repair loop

2. **Resource Allocation:**
   - Allocate 5 weeks for critical path; reserve 1 week buffer for H-M1 replication with Qwen2.5-Coder-7B
   - GPU: 1× A100-class GPU sufficient for 7B models; schedule both models sequentially

3. **Failure Management:**
   - Document all intermediate results even on null outcomes
   - Execute PIVOT strategies immediately on Gate failures (don't wait)
   - Frame null result framing in advance in paper outline to avoid post-hoc reframing

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: docs/youra_research/03_refinement.yaml (ID: H-IsoComputeFeedback-v1)
- Supplementary: 02_synthesis.yaml, 01_round_table/final_opinions.yaml

**B. MCP Tool Usage Summary**
- Total MCP calls: 4 (Archon: 3, ClearThought scientificmethod: 1)
- Tools: scientificmethod (1×), find_projects (1×), find_tasks (1×), manage_task (3×)

**C. Scope Reduction**
- BUILD_ON claims (not re-verified): 3 (execution feedback improves pass@1; type-constrained decoding reduces compilation errors; pylint iterative feedback reduces security issues)
- PROVE_NEW claims (experimental targets): 2 (iso-compute execution vs. pylint comparison; pylint functional correctness on HumanEval/MBPP)
- Scope reduction: 60%

**D. Sample Size Justification**
- HumanEval: 164 problems (full standard test set; adequate for 10pp effect detection at α=0.05, per Prof. Vera Phase 2A assessment)
- MBPP: 374 problems (full standard test set; higher power for smaller effects)
- Both models (Llama 3.1 8B + Qwen2.5-Coder-7B) provide replication across training regimes

---

*Verification State: COMPLETE*
*Generated: 2026-08-05*
*Workflow: phase2b-planning (steps 00-10)*
*stepsCompleted: [step-00-init-environment, step-01-init-parsing, step-02-input-hypothesis, step-03-hypothesis-generation, step-04-hypothesis-inventory, step-05-risk-analysis, step-06-dependency-graph, step-07-timeline-planning, step-08-dialectical-analysis, step-09-summary, step-10-finalize]*
*status: complete*
*completedAt: 2026-08-05T04:37:00Z*
