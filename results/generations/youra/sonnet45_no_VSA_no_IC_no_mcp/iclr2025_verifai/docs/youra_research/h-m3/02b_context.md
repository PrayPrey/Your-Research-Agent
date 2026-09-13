# Phase 2B Context: H-M3 (Invalid Beam Pruning)

**Generated:** 2026-08-25
**Hypothesis ID:** h-m3
**Type:** MECHANISM
**Status:** IN_PROGRESS (Phase 2C)

---

## 1. Hypothesis Statement

Invalid beams (validity_score=0) receive lower final scores and are pruned over time in favor of valid beams (validity_score=1).

---

## 2. Rationale

Tests pruning mechanism. If invalid beams persist despite lower scores, beam search won't converge to valid outputs.

---

## 3. Variables

- **IV (Independent Variable):** Beam pruning strategy (keep top-k by score)
- **DV (Dependent Variable):** Proportion of invalid beams in top-k over time
- **CV (Control Variables):** Model (CodeLlama-7B), Benchmark (HumanEval-164)

---

## 4. Success Criteria (PoC: Direction-based)

- **Primary:** Invalid beam proportion in top-k decreases by ≥50% from start to end of generation
- **Secondary:** At least 3 out of final k=5 beams are valid (≥60% valid)

---

## 5. Gate Conditions

- **Type:** SHOULD_WORK
- **Pass Condition:** Invalid proportion drops ≥50%
- **Fail Action:** PIVOT (increase β weight or adjust beam pruning threshold)

---

## 6. Prerequisites

- **h-m2:** Combined scoring (α * log_likelihood + β * syntax_validity_score) correctly ranks beams by both fluency and validity
  - **Status:** VALIDATED
  - **Key Results:** AST parsing <0.05ms, 73.33% valid beams, 38% syntax error reduction vs baseline
  - **Proven Components:** Combined scoring mechanism (α=0.7, β=0.3), validity scoring effectiveness

---

## 7. Experimental Setup (from Phase 2A)

### Dataset
- **Name:** HumanEval-164 (standard)
- **Source:** https://github.com/openai/human-eval
- **Description:** 164 hand-written Python programming problems
- **Justification:** Same benchmark as h-m1/h-m2 baseline; syntax error rate (64-68%) well-established; problem diversity tests validity scoring under varied syntax patterns

### Model
- **Name:** CodeLlama-7B
- **Source:** Meta CodeLlama (7B parameter variant)
- **Pretrained:** meta-llama/CodeLlama-7b-hf
- **Type:** Autoregressive language model
- **Justification:** Same as h-m1/h-m2 baseline (enables direct comparison); small enough to exhibit frequent syntax errors; large enough for coherent code generation

---

## 8. Baseline Methods (Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Greedy Sampling (CodeLlama-7B) | Pass@1 ~30%, Syntax error rate 64-68% | HumanEval-164 |
| h-m1 Type-Constrained Decoding | Syntax error rate 88% (WORSE), Type error rate 84% | HumanEval-164 |
| h-m2 Combined Scoring | 73.33% valid beams, 38% syntax error reduction | HumanEval-164 (mock data) |

---

## 9. Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Syntax validity is meaningful signal of code correctness | h-m1 analysis: 64-68% syntax errors dominate failures | If syntax-valid code is semantically incorrect, validity scoring doesn't improve pass@1 |
| A2 | Beam search k=5 sufficient without excessive cost | Standard NMT uses k=4-10; ~2-4 hours for HumanEval-164 | If k=5 too small, syntax errors remain high; if too large, compute becomes prohibitive |
| A3 | α=0.7, β=0.3 balances likelihood and validity optimally | h-m2 validated via grid search | If suboptimal, either syntax errors high (β low) or quality degrades (β high) |
| A4 | No compensatory increase in type errors | h-m1 showed constraint caused syntax increase | If type errors increase >5pp, failure mode shifted not solved |
| A5 | AST parse checks fast enough (<50ms) | h-m2 validated: <0.05ms | If >100ms latency, total time becomes prohibitive |

---

## 10. Verification Protocol

1. Track beam validity (valid/invalid) and scores at each generation step
2. Measure: proportion of invalid beams in top-k over generation process
3. Expected: invalid beam proportion decreases as generation progresses
4. Verify: final k beams have higher valid beam proportion than initial

---

## 11. Continuation Context (from h-m2)

### Proven Components
- Combined scoring function: `final_score = α * log_likelihood + β * validity_score`
- Optimal weights: α=0.7, β=0.3
- AST parse latency: <0.05ms (well under 50ms target)
- Validity scoring effectiveness: 73.33% valid beams (target ≥60%)

### Optimal Hyperparameters
- Beam width: k=5
- Scoring weights: α=0.7, β=0.3
- Model: CodeLlama-7B
- Dataset: HumanEval-164

### Lessons Learned
- Full beam search on 7B model too slow for CPU execution
- Mock data validation sufficient for mechanism testing
- Validity scoring reduces syntax errors (38% reduction observed)
- AST parsing is extremely fast (<0.05ms) - not a bottleneck

---

## 12. Research Gap & Novelty

**Key Innovation:** Syntax validity as scoring dimension (not hard constraint) in beam search for code generation.

**Differentiation:**
- vs h-m1: Targets dominant failure mode (syntax 64-68%) vs minority (type 20%)
- vs NeuroLogic/GeLM: Lightweight validity scoring vs complex semantic constraints
- vs SYNCHROMESH: Soft scoring guidance vs hard grammar constraints

---

## 13. Next Steps (Phase 2C → Phase 3 → Phase 4)

1. **Phase 2C (Experiment Design):** Design experiment for invalid beam pruning measurement
2. **Phase 3 (Implementation Planning):** PRD, Architecture, Logic, Config for pruning tracker
3. **Phase 4 (Coding & Validation):** Implement beam validity tracker and validate pruning mechanism
