# Hypothesis: h-e1

**Generated:** 2026-08-19 (Phase 2A output stub)
**Type:** EXISTENCE

---

## Hypothesis Statement

Binary feedback achieves dual-threshold sufficiency: ≥8 pp absolute improvement over SFT baseline AND ≥80% relative retention of error-type feedback gains on HumanEval for 350M-1B models

---

## Rationale

Small models have limited capacity to utilize high-dimensional supervision signals. Binary feedback provides concentrated, noise-reduced learning signal when test suites are comprehensive.

---

## Variables

**Independent Variable:**
- Feedback granularity: {SFT baseline, Binary (1 bit), Error-type (2.3 bits)}

**Dependent Variables:**
- HumanEval pass@1 accuracy

**Control Variables:**
- Model architecture (CodeGen-350M or StarCoder-1B)
- Training steps (500-1000)
- GRPO hyperparameters (lr=2e-7, KL=0.1)
- Evaluation protocol (greedy decoding, temperature=0)

---

## Success Criteria

**EXISTENCE (PoC) - Dual Threshold:**
1. Binary achieves ≥8 pp absolute improvement: `pass@1_binary - pass@1_sft ≥ 8.0`
2. Binary achieves ≥80% relative retention: `(pass@1_binary - pass@1_sft) / (pass@1_error_type - pass@1_sft) ≥ 0.8`

Both thresholds MUST be met for hypothesis to pass.

---

## Gate Condition

**MUST_WORK Gate:**
- If Fail: Existence hypothesis refuted → lightweight feedback insufficient → re-evaluate main hypothesis
- If Pass: Proceed to h-m1 (model size scaling), h-m2 (dataset characteristics), h-m3 (feedback design principles)

---

## Dependencies

**Prerequisites:** None (entry hypothesis)
**Blocks:** h-m1, h-m2, h-m3 (all depend on h-e1 result)

---

*Phase 2A output stub - full hypothesis context in 02b_context.md*
