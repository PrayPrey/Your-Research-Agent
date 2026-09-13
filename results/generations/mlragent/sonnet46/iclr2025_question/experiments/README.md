# HalluConform: Calibration-Aware Conformal Prediction for Hallucination Detection

## Overview

This codebase implements **HalluConform**, a lightweight hallucination detection framework that combines conformal prediction with internal LLM signals. The framework provides statistically valid detection with formal coverage guarantees using only a single forward pass.

## Method

HalluConform extracts three complementary nonconformity signals from a single LLM forward pass:
1. **Token-Level Entropy** ($s_\text{ent}$): Mean predictive entropy across generated tokens
2. **Attention Consistency** ($s_\text{attn}$): Cross-layer variance of attention weight distributions
3. **Hidden-State Divergence** ($s_\text{hid}$): Cosine divergence between consecutive layer representations

These signals are combined via logistic regression calibrated on a held-out set, then a conformal prediction threshold is applied at a user-specified error rate α.

## Files

- `config.py` — Hyperparameters and configuration
- `data.py` — Dataset loading (TriviaQA, MedMCQA)
- `model.py` — Model loading and signal extraction
- `uncertainty.py` — HalluConform + baseline implementations
- `evaluation.py` — Per-domain and coverage evaluation utilities
- `visualization.py` — Figure generation
- `run_experiment.py` — Main experiment runner

## Requirements

```bash
pip install torch transformers datasets scikit-learn matplotlib numpy
```

## Running the Experiment

```bash
cd claude_code
python run_experiment.py
```

Outputs will be saved to `claude_code/outputs/`. The experiment takes approximately 15-30 minutes on a GPU.

## Baselines

- **EntropyThreshold**: Flag samples with mean token entropy above a calibrated threshold
- **MaxProbThreshold**: Flag samples with high token entropy (proxy for low max probability)
- **LengthNormEntropy**: Entropy normalized by generation length

## Output Files

- `outputs/results.json` — Full numerical results
- `outputs/roc_curves.png` — ROC curves for all methods
- `outputs/pr_curves.png` — Precision-Recall curves
- `outputs/method_comparison.png` — AUROC/AUPRC/F1 bar chart
- `outputs/coverage_verification.png` — Empirical vs theoretical coverage
- `outputs/nonconformity_distribution.png` — Score distribution
- `outputs/domain_performance.png` — Per-domain AUROC
- `outputs/signal_importance.png` — Learned signal weights
- `outputs/fpr_fnr_comparison.png` — FPR/FNR comparison
- `outputs/adaptive_threshold.png` — Adaptive thresholds by risk level
