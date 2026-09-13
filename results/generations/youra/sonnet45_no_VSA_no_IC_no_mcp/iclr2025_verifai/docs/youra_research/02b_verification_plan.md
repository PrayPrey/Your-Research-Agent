# Verification Plan: Syntax-Aware Beam Search with Validity Scoring

**Date:** 2026-08-25
**Hypothesis ID:** H-SyntaxBeam-v1
**Confidence:** 0.75
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under code generation tasks on HumanEval benchmark with CodeLlama-7B, if we apply beam search (k=5) with combined scoring (final_score = α * log_likelihood + β * syntax_validity_score, where α=0.7, β=0.3, and syntax_validity_score = 1 if ast.parse() succeeds else 0), then syntax error rate will drop from 64-68% baseline to ≤40% (≥40% relative reduction), because beam search explores multiple candidate paths and validity scoring prunes syntactically invalid beams, preventing the model from committing to invalid paths early (which greedy sampling cannot recover from).

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in syntax error rate between greedy sampling baseline (64-68%) and validity-scored beam search (α=0.7, β=0.3, k=5) on HumanEval-164 with CodeLlama-7B.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval-164 (standard) | HumanEval is the same benchmark used in h-m1 baseline, enabling direct comparison. Syntax error rate (64-68%) is well-established from h-m1 analysis. Problem diversity (nested loops, list comprehensions, recursion, control flow, string manipulation) tests validity scoring under varied syntax patterns. |
| **Model** | CodeLlama-7B | Same model as h-m1 baseline (enables direct comparison of greedy sampling vs validity-scored beam search). Small enough to exhibit syntax errors frequently (64-68%) where validity scoring provides value. Large enough to generate coherent code for beam search to work with. |

**Dataset Details:**
- Source: OpenAI HumanEval benchmark (164 hand-written Python programming problems)
- Path: https://github.com/openai/human-eval

**Model Details:**
- Type: autoregressive language model
- Source: Meta CodeLlama (7B parameter variant)

### 1.4 Baseline Methods (Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Greedy Sampling (CodeLlama-7B) | HumanEval Pass@1 ~30%, Syntax error rate 64-68% | HumanEval-164 |
| h-m1 Type-Constrained Decoding | Syntax error rate 88% (WORSE), Type error rate 84% | HumanEval-164 |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Syntax validity (AST parse success) is a meaningful signal of code correctness | h-m1 analysis shows 64-68% syntax errors dominate failures; fixing syntax is necessary (though not sufficient) for pass@1 improvement | If syntax-valid code is frequently semantically incorrect, validity scoring reduces syntax errors but does not improve pass@1 (metric degrades) |
| A2 | Beam search k=5 is sufficient to explore diverse syntax paths without excessive compute cost | Standard NMT uses k=4-10; preliminary estimate ~2-4 hours for HumanEval-164 (acceptable for research) | If k=5 is too small to find valid beams, syntax error rate remains high; if k=5 is too large, compute cost becomes prohibitive (>8 hours) |
| A3 | α=0.7, β=0.3 balances log-likelihood and validity optimally | 5-problem PoC gate will validate this via grid search over (0.5,0.5), (0.6,0.4), (0.7,0.3), (0.8,0.2) | If α/β is suboptimal, either syntax errors remain high (β too low) or generation quality degrades (β too high, pass@1 drops >5pp) |
| A4 | Fixing syntax errors does not cause compensatory increase in type errors | h-m1 showed type constraint caused syntax increase (compensatory failure can go both directions); monitoring both error types is critical | If type error rate increases >5pp while syntax errors decrease, we've shifted failure mode rather than solving it |
| A5 | AST parse checks at each beam step are fast enough (<50ms per check) to avoid computational bottleneck | Python ast module is optimized; typical code snippets parse in 10-50ms | If AST parsing introduces >100ms latency per beam step, total generation time becomes prohibitive (>8 hours for HumanEval-164) |

### 1.6 Research Gap & Novelty

**Key Innovation:** Syntax validity as a scoring dimension in beam search for code generation (not hard constraint, not soft penalty, but explicit scoring component).

**Differentiation:**
- vs h-m1: Targets dominant failure mode (syntax 64-68%) vs minority (type 20%); uses beam search validity scoring vs greedy penalties
- vs NeuroLogic/GeLM: Lightweight validity scoring vs complex semantic constraints
- vs SYNCHROMESH: Soft scoring guidance vs hard grammar constraints

**Scope Reduction:** 80% (all baseline claims BUILD_ON from h-m1 analysis)

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| h-e1 | EXISTENCE | MUST_WORK | None | READY |
| h-m1 | MECHANISM | SHOULD_WORK | h-e1 | NOT_STARTED |
| h-m2 | MECHANISM | SHOULD_WORK | h-m1 | NOT_STARTED |
| h-m3 | MECHANISM | SHOULD_WORK | h-m2 | NOT_STARTED |
| h-m4 | MECHANISM | SHOULD_WORK | h-m3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

#### H-E1: Beam Search Infrastructure Exists

**Type:** EXISTENCE
**Statement:** Beam search with custom scoring must exist and be computationally feasible for code generation. AST parsing must work reliably for Python code validation.

**Rationale:** Foundation hypothesis. If beam search implementation or AST parsing is infeasible, the entire approach fails. Validates infrastructure before testing mechanism.

**Variables:**
- IV: Generation Strategy (beam search vs greedy)
- DV: Computational time (hours), AST parse success rate
- CV: Model (CodeLlama-7B), Benchmark (HumanEval-164)

**Success Criteria (PoC: Direction-based):**
- Primary: Beam search completes 5-problem PoC in <30 minutes (extrapolates to <4 hours for 164)
- Secondary: AST parse latency <50ms per sample (within A5 assumption)

**Gate:**
- Type: MUST_WORK
- If Fail: ABANDON (infrastructure not feasible)

**Prerequisites:** None

**Verification Protocol:**
1. Implement beam search (k=5) with custom scoring function (α * log_likelihood + β * validity_score)
2. Run on 5-problem PoC subset and measure total generation time
3. Test AST parsing on all generated outputs; measure parse latency per sample
4. Verify beam search completes without errors and produces k candidate outputs
5. Check computational cost is <8 hours for full HumanEval-164 (extrapolate from PoC)

---

#### H-M1: Beam Parallel Exploration

**Type:** MECHANISM
**Statement:** Beam search maintains k=5 candidate sequences enabling exploration of multiple syntax paths, unlike greedy's single committed path.

**Rationale:** Tests first mechanism step. If beam search doesn't maintain k parallel sequences, it collapses to greedy sampling and cannot explore alternatives.

**Variables:**
- IV: Beam width k (3, 5, 10 for ablation)
- DV: Number of active beams at each generation step
- CV: Model, Benchmark (same as H-E1)

**Success Criteria (PoC: Direction-based):**
- Primary: Beam count = k maintained at all steps (no early pruning to 1)
- Secondary: Beam diversity: at least 3 distinct outputs in k=5 beams

**Gate:**
- Type: SHOULD_WORK
- If Fail: PIVOT (adjust beam pruning threshold or k value)

**Prerequisites:** h-e1

**Verification Protocol:**
1. Instrument beam search to log active beam count at each generation step
2. Run on 5-problem PoC subset and verify k=5 beams maintained throughout
3. Ablation: Test k=3, k=5, k=10 to validate choice
4. Compare beam outputs: verify they diverge (not k copies of same sequence)

---

#### H-M2: Combined Scoring Function

**Type:** MECHANISM
**Statement:** Combined scoring (α * log_likelihood + β * syntax_validity_score) correctly ranks beams by both fluency and validity, with AST parse checks fast enough (<50ms).

**Rationale:** Tests scoring mechanism. If scoring is broken (wrong formula, slow AST parsing) or invalid beams score higher than valid ones, pruning won't work.

**Variables:**
- IV: Scoring weights (α, β) combinations
- DV: Beam ranking order, AST parse latency (ms)
- CV: Model, Benchmark (same as H-E1)

**Success Criteria (PoC: Direction-based):**
- Primary: AST parse latency <50ms per sample (A5 assumption holds)
- Secondary: Valid beams rank higher than invalid in ≥80% of generation steps (β=0.3 sufficient)

**Gate:**
- Type: SHOULD_WORK
- If AST slow: PIVOT (cache AST parse or reduce beam width)
- If scoring broken: EXPLORE (adjust α/β or scoring formula)

**Prerequisites:** h-m1

**Verification Protocol:**
1. Implement scoring function: final_score = α * log_likelihood + β * (1 if ast.parse() succeeds else 0)
2. Measure AST parse latency for each beam candidate (target: <50ms)
3. Log beam scores at each step; verify valid beams (validity_score=1) receive higher final_score than invalid (validity_score=0) when β=0.3
4. Ablation: Test α/β combinations (0.5/0.5, 0.6/0.4, 0.7/0.3, 0.8/0.2) on 5-problem PoC

---

#### H-M3: Invalid Beam Pruning

**Type:** MECHANISM
**Statement:** Invalid beams (validity_score=0) receive lower final scores and are pruned over time in favor of valid beams (validity_score=1).

**Rationale:** Tests pruning mechanism. If invalid beams persist despite lower scores, beam search won't converge to valid outputs.

**Variables:**
- IV: Beam pruning strategy (keep top-k by score)
- DV: Proportion of invalid beams in top-k over time
- CV: Model, Benchmark (same as H-E1)

**Success Criteria (PoC: Direction-based):**
- Primary: Invalid beam proportion in top-k decreases by ≥50% from start to end of generation
- Secondary: At least 3 out of final k=5 beams are valid (≥60% valid)

**Gate:**
- Type: SHOULD_WORK
- If Fail: PIVOT (increase β weight or adjust beam pruning threshold)

**Prerequisites:** h-m2

**Verification Protocol:**
1. Track beam validity (valid/invalid) and scores at each generation step
2. Measure: proportion of invalid beams in top-k over generation process
3. Expected: invalid beam proportion decreases as generation progresses
4. Verify: final k beams have higher valid beam proportion than initial

---

#### H-M4: Final Valid Output Selection

**Type:** MECHANISM
**Statement:** Final selected code is from top-scoring beam which has been incrementally validated for syntax correctness throughout generation process.

**Rationale:** Tests final output quality. If top beam is still invalid after pruning process, mechanism failed.

**Variables:**
- IV: Final beam selection strategy (argmax score)
- DV: Syntax validity of selected output (AST parse success)
- CV: Model, Benchmark (same as H-E1)

**Success Criteria (PoC: Direction-based):**
- Primary: Syntax error rate < greedy baseline on 5-problem PoC (directional improvement)
- Secondary: At least 3 out of 5 final outputs are syntactically valid (≥60% valid)

**Gate:**
- Type: SHOULD_WORK
- If Fail: ABANDON (mechanism doesn't reduce syntax errors)

**Prerequisites:** h-m3

**Verification Protocol:**
1. Select final output: beam with highest final_score from k candidates
2. Parse final output with ast.parse(); record syntax validity
3. Compare against baseline greedy sampling on same 5 problems
4. Measure syntax error rate: (invalid outputs / total outputs) × 100%

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Dependency Graph (DAG)
```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

Level 0 (Foundation):
  [H-E1] Beam search infrastructure exists
     |
     v
Level 1 (Mechanism Start):
  [H-M1] Beam maintains k=5 parallel sequences
     |
     v
Level 2 (Mechanism Middle):
  [H-M2] Combined scoring ranks beams correctly
     |
     v
Level 3 (Mechanism Late):
  [H-M3] Invalid beams pruned in favor of valid
     |
     v
Level 4 (Mechanism End):
  [H-M4] Final output selected from valid top-scoring beam

═══════════════════════════════════════════════════════════
Execution Order: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Gate Types: H-E1 (MUST_WORK), H-M1-4 (SHOULD_WORK)
Critical Path: All hypotheses sequential (5 steps)
═══════════════════════════════════════════════════════════
```

### 3.3 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| h-e1 | MUST_WORK | PoC completes <30min, AST <50ms | ABANDON |
| h-m1 | SHOULD_WORK | k=5 beams maintained, ≥3 distinct | PIVOT |
| h-m2 | SHOULD_WORK | AST <50ms, valid rank higher 80% | PIVOT/EXPLORE |
| h-m3 | SHOULD_WORK | Invalid proportion drops ≥50% | PIVOT |
| h-m4 | SHOULD_WORK | Syntax error < baseline | ABANDON |

### 3.4 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 2C (Experiment Design) | h-e1, h-m1-4 | 3-5 days |
| Phase 3 (Implementation Planning) | All | 5-7 days |
| Phase 4 (Coding & PoC Validation) | h-e1 → h-m1-4 sequential | 7-10 days |
| Phase 4.5 (Synthesis) | All | 1-2 days |
| Phase 5 (Baseline Comparison) | Skipped | 0 days |

**Total Duration:** 16-24 days

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Assumption | Severity | Affected Hypotheses | Mitigation |
|------|-----------|----------|---------------------|------------|
| R1 | A1: Syntax validity meaningful | Medium | h-e1, h-m4 | Monitor P3 (pass@1); if degrades >2pp, syntax-only scoring insufficient |
| R2 | A2: k=5 sufficient | Medium | h-m1 | Ablation study k=3,5,10 in PoC validates choice |
| R3 | A3: α=0.7, β=0.3 optimal | High | h-m2, h-m3 | Grid search in PoC gate; if fails, adjust weights |
| R4 | A4: No compensatory type errors | High | h-m4 | Monitor P2; if type errors +5pp, redesign mechanism |
| R5 | A5: AST parsing fast | Low | h-e1, h-m2 | Measure parse latency; if >50ms, cache or reduce k |

### 4.2 Mitigation Strategies

**R3 (α/β tuning) - HIGH PRIORITY:**
- PoC Phase: Grid search over (0.5,0.5), (0.6,0.4), (0.7,0.3), (0.8,0.2)
- Success criterion: ≥1 combination achieves <45% syntax error rate on 5 problems
- If all combinations fail: PIVOT to Variant B (learned validity features)

**R4 (Compensatory type errors) - HIGH PRIORITY:**
- Monitor type error rate throughout PoC validation
- Threshold: baseline + 5pp (if baseline 20%, accept up to 25%)
- If threshold exceeded: Run diagnostic to identify cause, consider constraint modification

---

## 5. Dialectical Analysis

### 5.1 Thesis
Syntax-aware beam search with validity scoring reduces syntax errors by ≥40% because it explores multiple candidate paths and prunes syntactically invalid beams, preventing the model from committing to invalid paths early.

### 5.2 Antithesis (H0)
There is no significant difference between greedy and validity-scored beam search. Counterarguments:
1. Beam exploration alone may not help if all paths lead to invalid syntax
2. α=0.7, β=0.3 weighting may be insufficient to overcome log-likelihood bias toward fluent but invalid code
3. Computational cost (5× slower, ~2-4 hours vs <1 hour) may not justify marginal improvements
4. Simple AST parse check may miss nuanced syntax errors (semantically weird but syntactically valid code)

### 5.3 Synthesis
The approach is promising IF:
1. PoC grid search finds optimal α/β that balances fluency and validity
2. Beam exploration discovers valid paths that greedy sampling misses
3. Syntax error reduction doesn't cause compensatory increase in type errors (>5pp threshold)
4. Computational cost remains acceptable (<8 hours for full benchmark)

Phase 4 PoC gate validates these preconditions before committing to full-scale experiment.

### 5.4 Robustness Assessment
**Strengths:**
- Targets dominant failure mode (syntax 64-68%) vs h-m1's minority target (type 20%)
- Builds on established infrastructure (beam search, AST parsing)
- 80% scope reduction from h-m1 baseline (efficient verification)
- PoC gate prevents expensive failures

**Weaknesses:**
- Sensitive to α/β tuning (hyperparameter search risk)
- Computational cost 5× baseline (feasibility constraint)
- Simple parse-check validity may miss semantic errors
- No guarantee beam exploration finds valid paths

---

## 6. Executive Summary

**Main Hypothesis:** H-SyntaxBeam-v1 - Beam search (k=5) with validity scoring (α=0.7, β=0.3) reduces syntax errors from 64-68% baseline to ≤40% on HumanEval-164 with CodeLlama-7B.

**Sub-Hypotheses:** 5 (H-E1, H-M1-4) derived from 4-step causal mechanism

**Scope Reduction:** 80% (all baseline claims BUILD_ON from h-m1 analysis)

**Critical Risks:**
- R3 (α/β tuning optimization) - HIGH
- R4 (compensatory type error increase) - HIGH

**Execution Strategy:**
- Sequential verification: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
- Gate-based progression: MUST_WORK (H-E1), SHOULD_WORK (H-M1-4)
- PoC validation on 5-problem subset before full-scale

**Timeline:** 16-24 days (Phase 2C through 4.5; Phase 5 skipped per module.yaml config)

**Next Steps:**
1. Phase 2C: Experiment design for h-e1 (infrastructure feasibility)
2. Sequential progression through h-m1 → h-m2 → h-m3 → h-m4
3. Phase 4.5: Synthesis of all hypothesis results
4. Phase 6: Paper writing (skip Phase 5 baseline comparison)

---

**Generated:** 2026-08-25
**Workflow:** Phase 2B Planning (UNATTENDED mode)
**Schema Version:** 3.5
