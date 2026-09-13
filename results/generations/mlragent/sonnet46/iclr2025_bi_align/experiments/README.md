# CAVE: Contextual Adaptive Value Elicitation

## Overview
This directory contains the implementation of the CAVE framework for dynamic bidirectional human-AI alignment, along with 4 baseline methods and comprehensive evaluation.

## Hypothesis Tested
CAVE's hierarchical Bayesian value representation with active elicitation and drift detection achieves:
1. Higher preference prediction fidelity (AUC-ROC) than baselines
2. Greater value diversity preservation across demographic groups (JS divergence)
3. Effective value drift detection (F1 > 0.80)
4. Reduced feedback burden via active elicitation

## Methods
- **CAVE** (Proposed): Hierarchical Bayesian + active elicitation + drift detection
- **Population RLHF**: Standard single-model RLHF (no personalization)
- **LoCo-RLHF**: Low-rank contextual RLHF with user embeddings
- **Contextual Bandit + Entropy**: MC Dropout uncertainty-based feedback
- **Static Personalization**: Shared model + per-user bias

## Files
- `config.py` - Hyperparameters and settings
- `data_generator.py` - Synthetic user preference data with value drift
- `models.py` - CAVE and baseline model implementations
- `train.py` - Training routines with active elicitation
- `evaluation.py` - Metrics: AUC-ROC, JS divergence, drift P/R/F1
- `visualization.py` - Figure generation
- `run_experiment.py` - Main experiment runner

## Running
```bash
cd claude_code
python run_experiment.py
```

Results are saved to `../results/`.

## Requirements
- Python 3.10+
- PyTorch 2.0+
- numpy, scipy, scikit-learn, matplotlib, pandas
