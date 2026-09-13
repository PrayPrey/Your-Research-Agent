# Mutual Calibration Framework (MCF) Experiments

This repository contains the implementation and experiments for the **Mutual Calibration Framework (MCF)**, a novel approach to adaptive alignment calibration in human-AI collaboration.

## Overview

The MCF addresses the critical challenge of determining when humans should defer to AI recommendations versus when human judgment should take precedence. It combines:

1. **Uncertainty-Aware AI Module**: Ensemble-based prediction with calibrated confidence estimates
2. **Personalized Deference Policy Learner**: Meta-learning approach that learns when to defer to human judgment
3. **Adaptive Calibration Interface**: Context-aware guidance for human-AI decision making

## Project Structure

```
claude_code/
├── config.py              # Configuration settings
├── models.py              # Model implementations (MCF, baselines)
├── human_simulator.py     # Simulated human behavior for experiments
├── training.py            # Training utilities and loss functions
├── evaluation.py          # Evaluation metrics
├── visualization.py       # Plotting utilities
├── run_experiment.py      # Main experiment runner
├── README.md              # This file
└── results/               # Generated results
    ├── log.txt            # Experiment logs
    ├── results.json       # Full results in JSON format
    ├── results_summary.csv # Summary table
    └── figures/           # Generated figures
```

## Requirements

- Python 3.8+
- PyTorch 1.12+
- NumPy
- Pandas
- Matplotlib
- scikit-learn

## Running Experiments

### Basic Usage

```bash
python run_experiment.py
```

### With Custom Parameters

```bash
python run_experiment.py --n_samples 5000 --n_features 50 --n_classes 10 --users_per_level 10
```

### Parameters

- `--n_samples`: Number of samples in the synthetic dataset (default: 5000)
- `--n_features`: Number of features per sample (default: 50)
- `--n_classes`: Number of classification classes (default: 10)
- `--users_per_level`: Number of simulated users per expertise level (default: 10)

## Experimental Conditions

The experiments compare four conditions:

1. **Baseline**: Standard AI system with confidence display (no calibration)
2. **Transparency+**: AI with detailed reasoning/feature importance explanations
3. **MCF-Static**: Mutual Calibration Framework without personalization
4. **MCF-Full**: Complete Mutual Calibration Framework with personalized deference policies

## Evaluation Metrics

### Performance Metrics
- AI Accuracy: Baseline AI prediction accuracy
- Collaborative Accuracy: Final human-AI decision accuracy

### Calibration Metrics
- Expected Calibration Error (ECE)
- Maximum Calibration Error (MCE)

### Reliance Metrics
- Appropriate Reliance Rate (ARR): Correct agreements + Correct overrides
- Over-Reliance Rate: Accepting incorrect AI recommendations
- Under-Reliance Rate: Rejecting correct AI recommendations

### Agency Metrics
- Override Rate: How often humans deviate from AI
- Override Accuracy: Accuracy of human overrides
- Unique Contribution Rate: Cases where human override corrected AI mistakes

## Simulated User Behavior

Users are simulated with three expertise levels:

| Level | Base Accuracy | Automation Bias | Algorithm Aversion |
|-------|--------------|-----------------|-------------------|
| Novice | 55% | High (0.7) | Low (0.1) |
| Intermediate | 70% | Medium (0.4) | Medium (0.3) |
| Expert | 85% | Low (0.2) | High (0.4) |

## Key Findings

The experiments test the hypothesis that MCF achieves:
- 15-25% improvement in Appropriate Reliance Rate compared to baselines
- Reduced automation bias without inducing algorithm aversion
- Preserved human agency and unique knowledge utilization
- Effective personalization adapting to user expertise levels

## Output Files

After running, find results in `results/`:
- `log.txt`: Detailed experiment log
- `results.json`: Complete results data
- `results_summary.csv`: Summary statistics table
- `figures/`: All generated visualizations

## Citation

This implementation accompanies the paper "Adaptive Alignment Calibration: Learning When Humans Should Defer to AI vs. Override AI Decisions" submitted to ICLR 2025 Workshop on Bidirectional Human-AI Alignment.
