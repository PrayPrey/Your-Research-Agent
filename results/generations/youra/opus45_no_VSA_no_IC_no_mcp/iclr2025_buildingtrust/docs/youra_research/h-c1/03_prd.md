# Product Requirements Document: h-c1

**Date:** 2026-08-28
**Hypothesis:** The truthfulness-robustness correlation pattern holds separately for base models and instruction-tuned models, with potentially different effect sizes.
**Type:** CONDITION
**Gate:** SHOULD_WORK

---

## 1. Objective

Test whether the TruthfulQA-AdvGLUE correlation established in h-e1 (r=0.8028) generalizes across model types or is an artifact of instruction tuning.

## 2. Success Criteria

| Metric | Threshold | Priority |
|--------|-----------|----------|
| Base models partial r | > 0.2 | P0 |
| Instruction-tuned partial r | > 0.2 | P0 |
| Both groups positive sign | True | P0 |
| Minimum models per group | 6 | P0 |

## 3. Scope

### In Scope
- Reuse h-e1 cached evaluation results (14 base models)
- Evaluate 6 instruction-tuned variants on TruthfulQA MC1 + AdvGLUE
- Compute within-group partial correlations controlling for log(params)
- Bootstrap CIs for each stratum
- Two-panel visualization

### Out of Scope
- Formal statistical comparison between group effect sizes
- RLHF vs SFT distinction
- Models outside Pythia/Llama-2/Mistral/Falcon families

## 4. Data Requirements

| Dataset | Source | Size |
|---------|--------|------|
| h-e1 results | h-e1/code/results/ | 14 models |
| Instruction-tuned evals | lm-evaluation-harness | 6 models |

## 5. Model Sample

**Base (from h-e1):** 14 models
- Pythia: 70m–12b (8)
- Llama-2: 7b, 13b, 70b (3)
- Mistral-7B-v0.1 (1)
- Falcon: 7b, 40b (2)

**Instruction-tuned (new):** 6 models
- Llama-2-chat: 7b, 13b, 70b
- Mistral-7B-Instruct-v0.1
- Falcon-instruct: 7b, 40b

## 6. Dependencies

- h-e1 PASSED (prerequisite satisfied)
- h-e1/code/results/ cached data
- lm-evaluation-harness
- HuggingFace model access

## 7. Deliverables

1. Extended dataset with model type labels
2. Stratified correlation analysis results
3. Two-panel scatter plot (base vs instruction-tuned)
4. Effect size comparison visualization
5. Gate evaluation report

## 8. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Small instruction-tuned sample | Use all 6 available variants |
| Model access issues | Fall back to open-weight models only |
| Evaluation cost | Reuse h-e1 base model results |

---

*Generated: 2026-08-28*
