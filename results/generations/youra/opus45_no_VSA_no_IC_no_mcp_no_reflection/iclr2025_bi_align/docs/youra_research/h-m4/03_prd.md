# Product Requirements Document: H-M4

**Hypothesis:** Under bidirectional training, if the model learns explicit constraint satisfaction (IFEval), then it also improves on implicit safety constraints (TruthfulQA, BBQ).

**Type:** MECHANISM
**Date:** 2026-08-28
**Gate:** SHOULD_WORK (≥2pp improvement on TruthfulQA OR BBQ vs max baseline)

---

## Executive Summary

H-M4 tests whether explicit constraint training (IFEval from H-M2) transfers to implicit safety benchmarks. Models trained with bidirectional rewards should demonstrate improved performance on TruthfulQA and BBQ compared to unidirectional baselines.

---

## Functional Requirements

### FR-1: Model Loading
Load all baseline and treatment checkpoints:
- **B1:** SFT-only baseline (`checkpoints/b1_sft`)
- **B2:** Helpfulness RLHF (`checkpoints/b2_helpfulness_rlhf`)
- **B3:** Quality RLHF (`checkpoints/b3_quality_rlhf`)
- **T1:** α=0.2, β=0.8 (`checkpoints/t1_alpha0.2`)
- **T2:** α=0.4, β=0.6 (`checkpoints/t2_alpha0.4`)
- **T3:** α=0.6, β=0.4 (`checkpoints/t3_alpha0.6`)
- **T4:** α=0.8, β=0.2 (`checkpoints/t4_alpha0.8`)

### FR-2: TruthfulQA Evaluation
Evaluate all 7 models on TruthfulQA:
- Tasks: `truthfulqa_mc1`, `truthfulqa_mc2`
- Samples: 817 questions (full dataset)
- Metrics: MC1 accuracy, MC2 accuracy

### FR-3: BBQ Evaluation
Evaluate all 7 models on BBQ:
- Task: `bbq`
- Samples: ~58,000 examples (9 demographic categories)
- Metrics: Accuracy, bias score

### FR-4: Gate Verification
Compute improvement over baselines:
- baseline_max = max(B1, B2, B3) per metric
- improvement = best_T - baseline_max
- PASS if any improvement ≥ 2 percentage points

### FR-5: Correlation Analysis
Analyze IFEval→Safety transfer:
- Correlate IFEval gains (from H-M2) with TruthfulQA/BBQ gains
- Report Pearson correlation and significance

### FR-6: Visualization
Generate figures:
- Bar chart: T1-T4 vs B1-B3 on TruthfulQA MC1 and BBQ
- Correlation scatter: IFEval Δ vs Safety Δ
- BBQ per-category breakdown
- 95% CI error bars

---

## Non-Functional Requirements

### NFR-1: Evaluation Framework
Use lm-evaluation-harness for standardized evaluation.

### NFR-2: Statistical Rigor
Bootstrap CI (n=1000) for accuracy estimates. Two-tailed t-test (α=0.05) for significance.

### NFR-3: Reproducibility
Fixed random seeds. All evaluation parameters logged.

---

## Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| TruthfulQA improvement | ≥2pp vs max(B1,B2,B3) |
| BBQ improvement | ≥2pp vs max(B1,B2,B3) |
| Gate condition | At least one above satisfied |

---

## Dependencies

- H-M3 checkpoints (T1-T4, B1-B3)
- lm-evaluation-harness
- Phase 2C experiment brief

---

## Out of Scope

- Training new models
- Custom safety benchmarks
- Real-time evaluation
