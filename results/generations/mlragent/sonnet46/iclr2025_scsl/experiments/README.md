# Causal Gradient Decomposition (CGD) - Experiments

## Overview

This directory contains the experimental implementation for testing the hypothesis that **Curvature-Aware Gradient Reweighting (CAGR)** reduces spurious feature reliance and improves worst-group accuracy compared to standard training methods.

The key hypothesis: spurious features in training datasets occupy lower-curvature regions of the loss landscape, causing SGD to preferentially encode them. CAGR penalizes updates along low-curvature spurious directions to improve robustness.

## Setup

```bash
pip install torch torchvision numpy matplotlib
```

## Running Experiments

```bash
cd tasks_youra_result_sonnet46/iclr2025_scsl/claude_code
python run_experiment.py
```

Results will be saved to `../results/`.

## Methods Compared

| Method | Description |
|--------|-------------|
| ERM | Standard Empirical Risk Minimization |
| GroupDRO | Group Distributionally Robust Optimization |
| JTT | Just Train Twice |
| DFR | Deep Feature Reweighting |
| **CAGR** | **Curvature-Aware Gradient Reweighting (Proposed)** |

## Datasets

1. **Linear Synthetic**: Gaussian mixture classification with controlled causal/spurious feature SNR
2. **Image Synthetic (Waterbirds-style)**: Simulated image dataset with background texture as spurious feature

## Output Files

- `log.txt`: Detailed experiment log
- `results.json`: Raw results in JSON format
- `training_curves_*.png`: Loss curves per dataset
- `accuracy_curves_*.png`: Accuracy over epochs
- `method_comparison_*.png`: Final metric comparison
- `per_group_accuracy_*.png`: Per-group breakdown
- `cagr_metrics_*.png`: CAGR-specific metrics (rho, alpha)
- `curvature_analysis_*.png`: Hessian curvature estimates
- `overall_comparison.png`: Summary across datasets
