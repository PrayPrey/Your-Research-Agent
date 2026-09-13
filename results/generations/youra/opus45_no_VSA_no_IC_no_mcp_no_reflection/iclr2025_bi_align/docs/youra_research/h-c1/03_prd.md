# Product Requirements Document: H-C1

**Hypothesis:** Explicit constraint training (IFEval) transfers to implicit safety constraints, improving ≥2pp on TruthfulQA OR BBQ

**Date:** 2026-08-28
**Author:** Anonymous
**Status:** Draft
**Type:** CONDITION Hypothesis

---

## Executive Summary

This experiment validates the transfer hypothesis: models trained on explicit instruction-following constraints (IFEval) should also improve on implicit safety constraints (truthfulness, bias reduction) without direct safety training. We evaluate 7 model configurations (3 baselines, 4 treatments) on TruthfulQA and BBQ benchmarks.

---

## Problem Statement

### Background
H-M2 demonstrated bidirectional RLHF (α,β weighting) improves IFEval strict accuracy by +3.4pp. H-M3 showed this maintains ≥95% helpfulness. The open question: does constraint-following as a meta-skill transfer to implicit safety constraints?

### Success Criteria
At least one treatment model (T1-T4) achieves ≥2pp improvement on TruthfulQA MC1 OR BBQ accuracy vs max(B1, B2, B3).

---

## Functional Requirements

### FR-1: Model Loading
Load all model checkpoints from H-M2/H-M3 experiments:
- B1: meta-llama/Meta-Llama-3-8B-Instruct (SFT baseline)
- B2: Helpfulness-only RLHF (α=1.0, β=0.0)
- B3: Quality-only RLHF
- T1: Bidirectional (α=0.2, β=0.8)
- T2: Bidirectional (α=0.4, β=0.6)
- T3: Bidirectional (α=0.6, β=0.4)
- T4: Bidirectional (α=0.8, β=0.2)

### FR-2: TruthfulQA Evaluation
- Run lm-evaluation-harness with tasks: truthfulqa_mc1, truthfulqa_mc2
- Full dataset: 817 questions across 38 categories
- Metrics: MC1 accuracy (single best), MC2 accuracy (multiple correct)
- Save per-model results to JSON

### FR-3: BBQ Evaluation
- Run lm-evaluation-harness with task: bbq
- Full dataset: 58,492 examples across 9 bias categories
- Metrics: Accuracy, Bias Score
- Save per-model results to JSON

### FR-4: Gate Evaluation
- Compute max(B1, B2, B3) for each metric
- Compute delta for each treatment Ti
- Gate PASS if any Ti achieves ≥2pp improvement on TruthfulQA_MC1 OR BBQ

### FR-5: Transfer Correlation Analysis
- Load IFEval results from H-M2
- Compute Pearson correlation: IFEval_delta vs TruthfulQA_delta
- Compute Pearson correlation: IFEval_delta vs BBQ_delta
- Report r and p-values

### FR-6: Results Reporting
- Generate 04_validation.md with:
  - Per-model metrics table
  - Gate evaluation result
  - Correlation analysis
  - Per-category breakdown (if gate fails)

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Use lm-evaluation-harness v0.4.0+
- Fixed random seed: 42
- Deterministic evaluation (no sampling)

### NFR-2: Performance
- Batch size: auto:4 (GPU memory adaptive)
- Expected runtime: 2-4 hours on A100-80GB

### NFR-3: Resource Constraints
- Single GPU inference (no distributed)
- Checkpoints loaded sequentially (memory efficient)

---

## Data Specifications

### Input Data
| Dataset | Source | Size | Split |
|---------|--------|------|-------|
| TruthfulQA | truthful_qa (HF) | 817 | validation |
| BBQ | bigscience/bbq (HF) | 58,492 | test |

### Model Checkpoints
| Model | Source | Path |
|-------|--------|------|
| B1 | HuggingFace | meta-llama/Meta-Llama-3-8B-Instruct |
| B2 | H-M2 | ../h-m2/code/checkpoints/b2_helpfulness_only |
| B3 | H-M2 | ../h-m2/code/checkpoints/b3_quality_only |
| T1-T4 | H-M2 | ../h-m2/code/checkpoints/t{1-4}_* |

### Output Data
- results/safety_results.json: Per-model metrics
- results/correlation_analysis.json: Transfer correlation
- 04_validation.md: Final report

---

## Dependencies

### Prerequisites
- H-M2: Validated (T2 achieves 56.8% IFEval)
- H-M3: Validated (T4 maintains 96.4% helpfulness)
- All T1-T4 checkpoints available

### External Dependencies
- lm-evaluation-harness >= 0.4.0
- transformers >= 4.40.0
- torch >= 2.0.0
- scipy, numpy

---

## Success Metrics

| Metric | Threshold | Priority |
|--------|-----------|----------|
| TruthfulQA MC1 Δ | ≥2pp vs max baseline | Primary (Gate) |
| BBQ Accuracy Δ | ≥2pp vs max baseline | Primary (Gate) |
| IFEval-Safety Correlation | r > 0 | Secondary |
| Statistical Significance | p < 0.05 | Secondary |

---

## Failure Analysis Protocol

If gate fails (no Ti improves ≥2pp):
1. Document as limitation in thesis
2. Analyze per-category breakdown
3. Correlate with IFEval constraint types
4. Consider confound: benchmark saturation for 8B models

---

**Document Version:** 1.0
**Last Updated:** 2026-08-28
