# Phase 2B Verification Plan
# Specification-Aligned Repair for EvalPlus Semantic Failures

**Main Hypothesis ID:** H-SpecRepair-v1
**Generated:** 2026-08-22
**Status:** READY FOR PHASE 2C

---

## Main Hypothesis

Under GPT-4o-mini on the 134 h-e1 Run 2 EvalPlus failures (34 HE+ + 100 MBPP+), providing a structured triple of (problem docstring formal intent, failing test input/expected-output pair, actual model output) as a repair oracle (Condition C: spec-aligned repair) produces statistically significantly higher round-1 pass@1 than blind reprompting (Condition B) and round-0 baseline (Condition A), as measured by one-tailed McNemar's test (α=0.05, temperature=0.2, seed=42).

**H₀:** P(fixed by C, not B) = P(fixed by B, not C) — no significant difference between Condition C and Condition B.

---

## Sub-Hypothesis Inventory

### H-E1 — Existence (MUST_WORK) | Status: READY

**Statement:** The 134 h-e1 Run 2 EvalPlus failures (34 HE+ + 100 MBPP+) are recoverable as a fixed problem set with stored GPT-4o-mini incorrect outputs, enabling Conditions B and C prompt construction without new baseline API calls.

**Rationale:** The entire experiment depends on the existing h-e1 Run 2 outputs. If the failure set or incorrect outputs are lost or corrupted, neither Condition B nor C prompts can be constructed. This must be verified before any API calls.

**Verification method:**
- Load h-e1 Run 2 results file; confirm 134 problem IDs present (34 HE+ + 100 MBPP+)
- Confirm stored incorrect outputs exist for all 134 problems
- Confirm EvalPlus augmented test suite accessible via `evalplus.data.get_human_eval_plus()` / `get_mbpp_plus()`
- Confirm first failing test case is deterministically selectable for each problem

**Success criterion:** All 134 problem IDs + incorrect outputs loadable; EvalPlus API accessible.

**Gate:** MUST_WORK — failure blocks all downstream sub-hypotheses.

**Prerequisites:** None

---

### H-M1 — Mechanism (MUST_WORK) | Status: NOT_STARTED (depends on H-E1)

**Statement:** Specification-aligned repair (Condition C: docstring + failing test I/O + actual model output) achieves statistically significantly higher round-1 pass@1 than blind reprompting (Condition B) on the 134 h-e1 Run 2 EvalPlus failures, as measured by one-tailed McNemar's test (α=0.05, temperature=0.2, seed=42).

**Rationale:** This is the primary prediction (P1) of H-SpecRepair-v1. It tests whether the structured semantic gap description (triple) provides causal repair signal beyond mere re-exposure to the problem. The one-tailed direction is pre-specified based on strong literature prior (Haeri & Ghelichi 2026: +38pp with spec grounding; Iscan 2026: content matters p=0.00042).

**Causal mechanism being tested:**
1. Docstring re-anchors model on intended algorithm (prevents same-solution regeneration)
2. Failing test I/O provides CEGIS-style counterexample (behavioral gap specification)
3. Actual output enables deviation detection (diagnostic link between spec and error)

**Experimental design:**
- Condition B prompt: `[problem prompt] + "The above solution is incorrect. Please try again."`
- Condition C prompt: `[problem prompt] + [docstring formal intent] + [failing test: input → expected output] + [actual model output]`
- API: GPT-4o-mini, temperature=0.2, seed=42
- Evaluation: all EvalPlus augmented tests must pass (fix = 1)
- Test: `scipy.stats.mcnemar()` one-tailed, Yates' continuity correction if any cell < 5

**Pre-registered decisions:**
- Temperature=0.2, seed=42 (not temperature=0, to avoid greedy fixed-point suppression)
- First failing test from EvalPlus deterministic ordering (not random)
- Fix = passes ALL EvalPlus augmented tests (not just the prompted test)
- One-tailed McNemar with Yates' correction if any cell count < 5

**Success criterion:** McNemar one-tailed p < 0.05 for C vs. B.

**Falsification:** p ≥ 0.05 → structured spec context provides no significant repair signal over blind re-exposure for GPT-4o-mini on EvalPlus semantic failures.

**Gate:** MUST_WORK — failure routes to Phase 2A-Dialogue (mechanism issue, not fundamental flaw).

**Prerequisites:** H-E1

**API calls:** 134 (Condition B)

---

### H-M2 — Mechanism (MUST_WORK) | Status: NOT_STARTED (depends on H-E1)

**Statement:** Specification-aligned repair (Condition C) achieves statistically significantly higher round-1 pass@1 than round-0 baseline (Condition A) on the 134 h-e1 Run 2 EvalPlus failures, with fix rate ≥ 15%, as measured by one-tailed McNemar's test (α=0.05).

**Rationale:** Secondary prediction (P2). Condition A is the existing h-e1 Run 2 data — no new API calls required. This verifies that spec-aligned repair actually fixes previously unfixable problems (not just a marginal improvement on already-easy failures). Fix rate ≥ 15% threshold aligns with FeedbackEval baseline (21.1pp avg fix rate).

**Experimental design:**
- Condition A: h-e1 Run 2 pass/fail results (all 134 = fail by definition)
- Condition C: same outputs from H-M1 experiment (reused, no new API calls)
- McNemar 2×2: [fixed-C-not-A] vs. [fixed-A-not-C] — note: all Condition A entries are 0 (fail), so this reduces to: fix rate under C ≥ some threshold with McNemar test against all-zero baseline
- Fix rate threshold: ≥ 15% (20 of 134 problems fixed)

**Success criterion:** McNemar one-tailed p < 0.05 for C vs. A AND fix rate under C ≥ 15%.

**Gate:** MUST_WORK — failure (fix rate < 15% or p ≥ 0.05) indicates spec-aligned repair is ineffective on EvalPlus semantic failures overall.

**Prerequisites:** H-E1 (and H-M1 API calls, for Condition C outputs)

**API calls:** 0 (Condition A = h-e1 Run 2 data; Condition C outputs reused from H-M1)

---

### H-C1 — Condition (SHOULD_WORK) | Status: NOT_STARTED (depends on H-M1)

**Statement:** The fix rate improvement from Condition C (spec-aligned repair) is higher for HumanEval+ problems (algorithmic, longer functions, n=34) than for MBPP+ problems (functional, shorter functions, n=100), indicating a complexity interaction between problem type and specification context utility.

**Rationale:** Exploratory prediction (P3). HumanEval+ problems are more algorithmically complex (longer functions, recursive structures, complex data manipulation). The structured triple may provide more repair signal for complex problems where the algorithmic intent (docstring) matters more. MBPP+ problems are shorter and more functional, where the model may self-correct more easily regardless of context.

**Experimental design:**
- Stratify 134 problems by benchmark type: 34 HE+ vs. 100 MBPP+
- Compute fix rate under Condition C for each stratum
- Fisher's exact test for stratified subgroup comparison (n=34 too small for McNemar alone)
- Secondary stratification: easy (h-e1 Run 2 pass@k ≥ 0.5) vs. hard (pass@k < 0.5) if data available

**Success criterion:** Fix rate HE+ > fix rate MBPP+ (directional). Statistical significance not required (exploratory).

**Gate:** SHOULD_WORK — failure does not block Phase 5. Negative result (MBPP+ ≥ HE+) rejects the complexity interaction hypothesis but does not invalidate H-M1/H-M2.

**Prerequisites:** H-M1 (Condition C outputs needed)

**API calls:** 0 (analysis only on H-M1 outputs)

---

## Dependency Graph (DAG)

```
H-E1 (READY)
├── H-M1 (NOT_STARTED) ──→ H-C1 (NOT_STARTED)
└── H-M2 (NOT_STARTED)
```

Execution order:
1. H-E1 first (data verification)
2. H-M1 + H-M2 can proceed after H-E1 (H-M2 needs Condition C outputs from H-M1, so H-M1 first)
3. H-C1 after H-M1 (stratified analysis on same outputs)

---

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| h-e1 Run 2 outputs lost/corrupted | Low | Critical | H-E1 gate verifies before any API calls |
| Greedy fixed-point: Cond B always regenerates same wrong answer | Medium | High | temperature=0.2 seed=42 pre-registered |
| Sparse discordant pairs (fix rates both < 5%) | Low | High | Yates' correction; fallback to Fisher's exact |
| Condition C prompt format varies across runs | Low | Medium | Pre-register exact template before API calls |
| n=34 (HE+ subgroup) underpowered for P3 | High | Low | P3 is directional/exploratory only (SHOULD_WORK) |
| EvalPlus test suite version mismatch | Low | Medium | Pin evalplus version; verify test count matches h-e1 |

---

## Statistical Power Analysis

- n = 134 total problems (fixed set)
- Expected fix rate under C: 15–40% (literature: FeedbackEval 21.1pp, Haeri +38pp scaled down for EvalPlus strictness)
- Expected fix rate under B: 5–15% (blind re-exposure, lower than C per H-M1 hypothesis)
- Expected discordant pairs (b + c cells): 15–45 pairs
- McNemar power at n_discordant=20, p_C=0.7: ~80% (adequate for α=0.05 one-tailed)
- Fallback: if any McNemar cell < 5, apply Yates' continuity correction automatically

---

## Experimental Cost Estimate

| Item | Count | Cost |
|------|-------|------|
| Condition B API calls | 134 | ~$0.025 |
| Condition C API calls | 134 | ~$0.025 |
| Condition A | 0 (existing data) | $0.00 |
| **Total** | **268** | **~$0.05** |

Estimated runtime: < 10 minutes (268 sequential API calls at ~2s each).

---

## Pre-Registration Checklist (Must complete before Phase 3 API calls)

- [x] Temperature=0.2, seed=42 (not temperature=0)
- [x] First failing test from EvalPlus deterministic test ordering
- [x] Fix = passes ALL EvalPlus augmented tests (not just prompted test)
- [x] One-tailed McNemar's test (direction: C > B, C > A)
- [x] Yates' continuity correction if any McNemar cell count < 5
- [ ] **TODO Phase 2C:** Exact Condition C prompt template format (XML tags, section labels, ordering)
- [ ] **TODO Phase 2C:** Exact Condition B prompt template format

---

## Dialectical Analysis

**Thesis:** The structured semantic gap description (docstring + test I/O + actual output) provides necessary and sufficient information for targeted algorithmic repair. The triple's three components address distinct repair needs: intent anchoring, behavioral gap specification, and deviation diagnosis. This integrated oracle enables GPT-4o-mini to re-anchor on the intended algorithm, identify the behavioral gap, and detect where its reasoning diverged.

**Antithesis:** GPT-4o-mini may fail to leverage counterexample reasoning — the triple adds tokens but not actionable signal. Alternatively, any re-exposure (Condition B) may suffice because the model self-corrects stochastically given another chance. The EvalPlus augmented test suite is stricter than standard HumanEval, which may reduce fix rates below the power threshold for both conditions.

**Synthesis:** The experiment is designed to discriminate these cases. C >> B confirms the triple provides causal signal. C ≈ B means re-exposure is sufficient (or the model cannot leverage counterexamples). C ≈ A means spec-aligned repair fails entirely on EvalPlus semantic failures. All three outcomes are publishable: positive result establishes spec-aligned oracle for production repair loops; negative result redirects toward architectural changes (multi-round repair, self-consistency sampling). The 3-condition paired design on a fixed failure set is a methodologically clean contribution regardless of outcome.

---

## Phase 2C Instructions (Next Phase)

For each sub-hypothesis in order (H-E1 → H-M1 → H-M2 → H-C1):

1. **H-E1:** Design data verification script — load h-e1 Run 2 results, confirm 134 problem IDs + stored outputs, confirm EvalPlus API access.
2. **H-M1:** Design Condition B + C prompt templates (pre-register exact format); design McNemar test harness; specify EvalPlus evaluation subprocess call.
3. **H-M2:** Design C vs. A McNemar analysis (reuses H-M1 Condition C outputs).
4. **H-C1:** Design stratified fix rate analysis (HE+ vs. MBPP+, Fisher's exact test).
