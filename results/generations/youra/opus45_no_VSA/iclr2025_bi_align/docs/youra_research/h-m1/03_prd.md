# PRD: H-M1 Adversarial BAI Probing

**Date:** 2026-08-08
**Hypothesis:** H-M1
**Type:** MECHANISM
**Gate:** MUST_WORK (AUROC ≥0.7)

## 1. Objective

Validate that Behavioral Alignment Index (BAI) represents an independent dimension in model representations, remaining decodable (AUROC ≥0.7) after adversarial gradient reversal removes reward-predictive variance.

## 2. Scope

### In Scope
- Hidden state extraction from Llama-3-8B, Mistral-7B, Qwen-2-7B
- Linear probing for BAI decodability
- Gradient reversal layer for adversarial training
- Evaluation on HH-RLHF and RewardBench datasets

### Out of Scope
- Fine-tuning base models
- Non-linear probes
- Real-time inference optimization

## 3. Functional Requirements

### FR-1: Hidden State Extraction
- Extract hidden states from all transformer layers
- Pool to per-sample representation (last token)
- Cache extracted activations to disk

### FR-2: BAI Label Computation
- Reuse H-E1 agency proxy classifiers
- Compute composite BAI score from 4 proxies
- Binarize for classification (median split)

### FR-3: Adversarial Probing
- Implement two-head architecture: BAI probe + reward probe
- Gradient reversal layer between shared representation and reward probe
- GRL alpha schedule: 0→1 over first epoch

### FR-4: Evaluation
- Primary: BAI AUROC after gradient reversal (target ≥0.7)
- Secondary: Reward R² degradation (target <2%)
- Cross-model generalization matrix

## 4. Non-Functional Requirements

### NFR-1: Reproducibility
- 3 random seeds
- Fixed train/test splits
- All hyperparameters logged

### NFR-2: Computational
- Run on single A100 40GB
- Total runtime <24h per model
- Checkpoint every epoch

## 5. Success Criteria

| Metric | Target | Gate |
|--------|--------|------|
| BAI AUROC (post-GRL) | ≥0.7 | MUST_WORK |
| Reward R² degradation | <2% | Secondary |
| Cross-model agreement | 2/3 models | Secondary |

## 6. Dependencies

- H-E1 validation (COMPLETED)
- pytorch-revgrad package
- HuggingFace Transformers
- sklearn for linear probing

## 7. Deliverables

1. `run_experiment.py` - Main training script
2. `extract_hidden_states.py` - Activation extraction
3. `probes.py` - Probe architectures
4. `evaluate.py` - Metrics computation
5. `figures/` - Visualization outputs
6. `04_validation.md` - Results report
