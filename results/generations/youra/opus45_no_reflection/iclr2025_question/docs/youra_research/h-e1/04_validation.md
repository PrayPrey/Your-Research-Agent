# Phase 4 Validation Report: H-E1

**Hypothesis:** Middle-layer hidden states encode sufficient signal for correctness prediction with AUROC > 0.60  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Date:** 2026-08-18

---

## Executive Summary

**Gate Result: PASS**

The linear probe trained on layer-19 hidden states achieved **AUROC = 0.8854**, significantly exceeding the 0.60 gate threshold and the 0.50 random baseline. This confirms the existence of a correctness signal in middle-layer representations.

---

## Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Model | meta-llama/Meta-Llama-3-8B-Instruct |
| Target Layer | 19 (60% depth) |
| Hidden Dimension | 4096 |
| Training Samples | 9,500 |
| Validation Samples | 1,700 |
| Learning Rate | 1e-3 |
| Epochs | 10 |
| Batch Size | 256 |
| Seed | 42 |

---

## Results

### Primary Metric

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| AUROC | **0.8854** | > 0.60 | **PASS** |
| vs Baseline (0.50) | +0.3854 | - | **+77% improvement** |

### Dataset Statistics

| Split | Correct | Total | Accuracy |
|-------|---------|-------|----------|
| Train | 2,902 | 9,500 | 30.5% |
| Val | 564 | 1,700 | 33.2% |

### Training Convergence

| Epoch | Loss |
|-------|------|
| 1 | 0.5413 |
| 5 | 0.4136 |
| 10 | 0.3918 |

Final loss: 0.3918 (converged)

---

## Gate Evaluation

### MUST_WORK Gate Criteria

1. **Code executes without errors:** PASS
2. **Mechanism correctly implemented:** PASS (hook on layer 19, last-token extraction, sigmoid probe)
3. **Metrics can be measured:** PASS (AUROC computed on validation set)
4. **AUROC > 0.60:** PASS (0.8854 > 0.60)

**Overall Gate: PASS**

---

## Generated Artifacts

### Figures
- `figures/gate_comparison.png` - Bar chart comparing AUROC vs baseline
- `figures/roc_curve.png` - ROC curve with AUROC annotation
- `figures/loss_curve.png` - Training loss over epochs
- `figures/hidden_state_pca.png` - PCA visualization of hidden states

### Data Files
- `code/cache/train_hidden_states.pt` - Cached training hidden states
- `code/cache/val_hidden_states.pt` - Cached validation hidden states
- `code/cache/probe.pt` - Trained probe weights
- `code/outputs/results.csv` - Per-epoch training metrics
- `experiment_results.json` - Structured experiment results

---

## Conclusions

The EXISTENCE hypothesis is **validated**. Hidden states from layer 19 of Llama-3-8B-Instruct contain sufficient signal to predict answer correctness with high discriminative power (AUROC = 0.8854). The probe achieves 77% improvement over random baseline, demonstrating that the model's internal representations encode a meaningful correctness signal.

**Next Phase:** Phase 5 (Baseline Comparison) to evaluate against output-level baselines (token entropy, sequence probability, semantic entropy).
