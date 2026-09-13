# Experimental Setup

We describe the experimental design for testing the calibration-mediation hypothesis. The evaluation is structured around four sub-hypotheses executed in sequence.

## Sub-Hypothesis Structure

| ID | Type | Statement | Gate |
|----|------|-----------|------|
| H-E1 | Existence | Correlation r > 0.5 exists between MC1 and (1-ASR) | MUST_WORK |
| H-M1 | Mechanism | ECE variance > 0.001 across models | MUST_WORK |
| H-M2 | Mechanism | Lower ECE predicts higher MC1 | SHOULD_WORK |
| H-M3 | Mechanism | ECE mediates ≥30% of correlation | SHOULD_WORK |

H-E1 is the foundation; subsequent hypotheses test the calibration mechanism.

## Evaluation Protocol

### TruthfulQA Evaluation

- **Task**: truthfulqa_mc1 (multiple-choice, single answer)
- **Questions**: 817 (full validation set)
- **Framework**: lm-evaluation-harness
- **Metric**: Accuracy (correct answer selected)

### TextFooler Attack

- **Recipe**: textfooler (word-level synonym substitution)
- **Dataset**: SST-2 validation split
- **Examples per model**: 500 minimum
- **Metric**: Attack Success Rate (ASR)
- **Library**: TextAttack

### Calibration Measurement

- **Source**: Logits from TruthfulQA predictions
- **Bins**: 10 equal-frequency
- **Metric**: Expected Calibration Error (ECE)

## Model Evaluation Schedule

| Model | TruthfulQA | TextFooler | Priority |
|-------|------------|------------|----------|
| google/flan-t5-base | ✓ | Pending | High |
| google/flan-t5-large | ✓ | Pending | High |
| microsoft/phi-2 | ✓ | Pending | High |
| meta-llama/Llama-2-7b-hf | Pending | Pending | High |
| meta-llama/Llama-2-13b-hf | Pending | Pending | Medium |
| mistralai/Mistral-7B-v0.1 | Pending | Pending | High |
| Others (6 models) | Pending | Pending | Medium-Low |

## Success Criteria

### Primary (P1: Correlation)
- Pearson r > 0.5
- p-value < 0.05
- Bootstrap 95% CI excludes 0.3

### Secondary (P2: Mediation)
- Indirect effect > 30% of total
- Sobel test p < 0.05

### Tertiary (P3: Intervention)
- Temperature scaling improves both metrics
- ≥2/3 tested models show improvement

## Failure Response

| Outcome | Action |
|---------|--------|
| r < 0.3 | ABANDON hypothesis |
| 0.3 < r < 0.5 | PIVOT to weaker claim |
| Mediation < 10% | ABANDON mechanism claim |
| 10% < Mediation < 30% | Document partial support |

## Baselines

We compare against null hypotheses:

1. **Scale-only correlation**: Does log(params) alone explain robustness?
2. **Random correlation**: Bootstrap null distribution

## Current Status

**PoC Validation**: Pipeline functionality verified on 3 models.
**Full Evaluation**: Not yet executed.
**Blockers**: 70B model OOM, tokenizer padding issues (fixed), TextFooler execution pending.
