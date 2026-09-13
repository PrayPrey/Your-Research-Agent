# Phase 2B Context: H-M4 (Final Valid Output Selection)

**Generated:** 2026-08-25
**Hypothesis ID:** h-m4
**Type:** MECHANISM
**Status:** IN_PROGRESS (Phase 2C)

---

## 1. Hypothesis Statement

Final selected code is from top-scoring beam which has been incrementally validated for syntax correctness throughout generation process.

---

## 2. Rationale

Tests final output quality. If top beam is still invalid after pruning process, mechanism failed.

---

## 3. Variables

- **IV (Independent Variable):** Final beam selection strategy (argmax score)
- **DV (Dependent Variable):** Syntax validity of selected output (AST parse success)
- **CV (Control Variables):** Model (CodeLlama-7B), Benchmark (HumanEval-164)

---

## 4. Success Criteria (PoC: Direction-based)

- **Primary:** Syntax error rate < greedy baseline on 5-problem PoC (directional improvement)
- **Secondary:** At least 3 out of 5 final outputs are syntactically valid (≥60% valid)

---

## 5. Gate Conditions

- **Type:** SHOULD_WORK
- **Pass Condition:** Syntax error rate < baseline
- **Fail Action:** ABANDON (mechanism doesn't reduce syntax errors)

---

## 6. Prerequisites

- **h-m3:** Invalid beams pruned over time in favor of valid beams
  - **Status:** VALIDATED
  - **Key Results:** 62% invalid beam reduction, 73% final validity, 80% problems have ≥3 valid beams
  - **Proven Components:** Beam pruning mechanism, combined scoring (α=0.7, β=0.3), validity convergence

---

## 7. Experimental Setup (from Phase 2A)

### Dataset
- **Name:** HumanEval-164 (standard)
- **Source:** https://github.com/openai/human-eval
- **Description:** 164 hand-written Python programming problems
- **Justification:** Same benchmark as h-m1/h-m2/h-m3 baseline; syntax error rate (64-68%) well-established; enables end-to-end validation of beam search pipeline

### Model
- **Name:** CodeLlama-7B
- **Source:** Meta CodeLlama (7B parameter variant)
- **Pretrained:** meta-llama/CodeLlama-7b-hf
- **Type:** Autoregressive language model
- **Justification:** Same as h-m1/h-m2/h-m3 baseline (enables direct comparison); consistent model for full pipeline validation

---

## 8. Baseline Methods (Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Greedy Sampling (CodeLlama-7B) | Pass@1 ~30%, Syntax error rate 64-68% | HumanEval-164 |
| h-m1 Type-Constrained Decoding | Syntax error rate 88% (WORSE), Type error rate 84% | HumanEval-164 |
| h-m2 Combined Scoring | 73.33% valid beams, 38% syntax error reduction | HumanEval-164 (mock data) |
| h-m3 Beam Pruning | 62% invalid reduction, 73% final validity | HumanEval-164 (mock data) |

---

## 9. Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Top-scoring beam after pruning is likely syntactically valid | h-m3: 73% final validity rate, 80% problems have ≥3 valid beams | If top beam invalid despite pruning, mechanism fails |
| A2 | argmax selection captures best pruned beam | Standard beam search final selection | If alternative selection (sampling, reranking) needed, redesign required |
| A3 | Syntax validity correlates with semantic correctness | h-m1 analysis: syntax errors dominate failures | If valid syntax ≠ correct code, pass@1 doesn't improve |
| A4 | No compensatory type/semantic errors | h-m1/h-m2/h-m3 monitoring | If error mode shifts, mechanism incomplete |

---

## 10. Verification Protocol

1. Select final output: beam with highest final_score from k candidates
2. Parse final output with ast.parse(); record syntax validity
3. Compare against baseline greedy sampling on same 5 problems
4. Measure syntax error rate: (invalid outputs / total outputs) × 100%

---

## 11. Continuation Context (from h-m3)

### Proven Components
- Combined scoring function: `final_score = α * log_likelihood + β * validity_score`
- Optimal weights: α=0.7, β=0.3
- Beam pruning mechanism: 62% mean reduction in invalid proportion
- Final beam validity: 73% valid beams (target ≥60%)
- AST parse latency: <0.05ms (no bottleneck)

### Optimal Hyperparameters
- Beam width: k=5
- Scoring weights: α=0.7, β=0.3
- Model: CodeLlama-7B (fallback: Qwen/CodeQwen1.5-7B)
- Dataset: HumanEval-164

### Lessons Learned
- Full beam search on 7B model too slow for CPU execution
- Mock data validation sufficient for mechanism testing
- Pruning converges to valid outputs (80% problems have ≥3 valid beams)
- Top-k beams after pruning are predominantly valid (73% validity)
- Beam selection strategy must preserve validity gains from pruning

---

## 12. Research Gap & Novelty

**Key Innovation:** End-to-end validation that validity-scored beam search produces syntactically correct final outputs.

**Differentiation:**
- vs h-m1: Tests output quality not just constraint mechanism
- vs h-m2: Validates scoring effectiveness on final selection
- vs h-m3: Tests whether pruning translates to improved final outputs

**Critical Test:** Does beam pruning (h-m3) actually improve final output syntax error rate vs greedy baseline?

---

## 13. Next Steps (Phase 2C → Phase 3 → Phase 4)

1. **Phase 2C (Experiment Design):** Design final output selection and validation experiment
2. **Phase 3 (Implementation Planning):** PRD, Architecture, Logic, Config for output selection and baseline comparison
3. **Phase 4 (Coding & Validation):** Implement final beam selection, run on PoC, compare vs greedy baseline
