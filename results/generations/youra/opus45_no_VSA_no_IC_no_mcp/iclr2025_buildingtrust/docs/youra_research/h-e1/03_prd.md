# Product Requirements Document: h-e1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis:** Significant positive partial correlation (r > 0.3, p < 0.05) exists between TruthfulQA MC1 accuracy and AdvGLUE average accuracy after controlling for log(model_params) across 15+ LLMs.
**Type:** EXISTENCE (PoC)

---

## Executive Summary

This experiment validates whether truthfulness (TruthfulQA MC1) and adversarial robustness (AdvGLUE) are correlated traits in LLMs beyond model scale. We compute partial correlation controlling for log(parameter count) across 15-20 models from multiple families.

---

## Problem Statement

Current understanding treats truthfulness and adversarial robustness as independent capabilities. If correlated, this suggests shared underlying mechanisms worth investigating in subsequent hypotheses.

---

## Functional Requirements

### FR-1: Model Evaluation Pipeline
- Evaluate 15-20 LLMs on TruthfulQA MC1 task
- Evaluate same models on AdvGLUE (all subtasks)
- Use lm-evaluation-harness for consistency
- Store results in structured format

### FR-2: Model Selection
- **Pythia family:** 70m, 160m, 410m, 1b, 1.4b, 2.8b, 6.9b, 12b
- **Llama-2 family:** 7b-hf, 13b-hf, 70b-hf
- **Mistral:** 7B-v0.1
- **Falcon:** 7b, 40b

### FR-3: Data Collection
- Collect benchmark scores per model
- Extract parameter counts from model configs
- Compute log(params) for each model

### FR-4: Statistical Analysis
- Compute partial Pearson correlation (TruthfulQA vs AdvGLUE, controlling for log(params))
- Bootstrap 1000 samples for 95% CI
- Report r, p, CI bounds

### FR-5: Visualization
- Scatter plot: TruthfulQA MC1 vs AdvGLUE avg (point size = log(params))
- Residual plot after controlling for model size
- Bootstrap distribution histogram

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seeds for bootstrap
- Version-pinned dependencies
- Cached evaluation results

### NFR-2: Efficiency
- Batch processing where possible
- GPU acceleration for model inference

---

## Success Criteria

| Metric | Threshold |
|--------|-----------|
| Partial r | > 0.3 |
| p-value | < 0.05 |
| Bootstrap 95% CI lower | > 0 |

**Gate:** All three criteria must pass.

---

## Data Requirements

| Dataset | Source | Usage |
|---------|--------|-------|
| TruthfulQA | HuggingFace truthful_qa | MC1 accuracy |
| AdvGLUE | HuggingFace adv_glue | Average accuracy across subtasks |
| Model metadata | HuggingFace model configs | Parameter counts |

---

## Dependencies

- lm-evaluation-harness
- scipy (stats)
- sklearn (bootstrap)
- matplotlib/seaborn (visualization)
- transformers (model loading)

---

## Out of Scope

- Model training
- New benchmark creation
- Mechanism investigation (deferred to H-M hypotheses)
