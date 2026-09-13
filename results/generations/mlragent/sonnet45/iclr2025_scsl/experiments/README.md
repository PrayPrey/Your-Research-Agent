# Adaptive Margin Regularization (AMR) for Mitigating Spurious Correlations

This repository contains the implementation of Adaptive Margin Regularization (AMR), a novel framework for mitigating spurious correlations in deep learning through loss landscape engineering.

## Overview

AMR addresses the fundamental challenge of spurious correlations in DNNs by directly manipulating the optimization dynamics. The key insight is that spurious features exhibit systematically different learning dynamics than core features, particularly in convergence speed and margin evolution.

## Key Components

1. **Temporal Feature Tracking**: Monitors gradient magnitudes and prediction confidence to identify rapidly-learned features
2. **Margin-Aware Regularization**: Dynamically penalizes excessive margins on early-learned features
3. **Loss Landscape Engineering**: Reshapes the loss landscape to discourage spurious solutions

## Installation

```bash
pip install torch torchvision numpy matplotlib seaborn pandas tqdm pillow
```

## Quick Start

Run the basic experiment:

```bash
cd /home/anonymous/mlbench/mlrbench/MLRagent_tasks_youra_result_sonnet45_experiment/iclr2025_scsl/claude_code
python run_experiment.py --dataset colored_mnist --epochs 30 --batch_size 32
```

## Experiments

The code implements and compares the following methods:

- **ERM**: Standard Empirical Risk Minimization (baseline)
- **GroupDRO**: Group Distributionally Robust Optimization (requires group labels)
- **JTT**: Just Train Twice (identifies and upweights hard examples)
- **AMR**: Adaptive Margin Regularization (our proposed method)

## Datasets

### Colored MNIST
A synthetic dataset with spurious color-label correlations. Binary classification where:
- Labels: digit < 5 vs. digit >= 5
- Spurious feature: Red vs. Green coloring
- Training correlation: 95%
- Test correlation: 10% (to evaluate robustness)

### Waterbirds
A synthetic waterbirds-like dataset with background correlations:
- Labels: Waterbird vs. Landbird
- Spurious feature: Water vs. Land background
- Training correlation: 95%
- Test correlation: 50%

## Configuration

Key hyperparameters in `config.py`:

- `m_target`: Target margin (default: 1.0)
- `mu_0`: Initial regularization strength (default: 0.5)
- `tau`: Lookback window for gradient acceleration (default: 5)
- `eta`: Sigmoid scaling for sample weighting (default: 5.0)
- `delta`: Threshold for spurious feature score (default: 0.5)

## Results

After running experiments, the following outputs are generated in the `results/` directory:

1. **training_curves.png**: Training and validation metrics over epochs
2. **group_performance.png**: Group-wise accuracy comparison
3. **method_comparison.png**: Overall performance across methods
4. **robustness_tradeoff.png**: Average accuracy vs. worst-group accuracy
5. **results_table.csv**: Detailed numerical results
6. **results.json**: Complete results in JSON format
7. **log.txt**: Execution log with configuration and results

## Expected Results

AMR is expected to achieve:
- 5-15% improvement in worst-group accuracy over ERM
- Performance within 2-3% of GroupDRO without using group labels
- Better robustness-accuracy tradeoff compared to annotation-free baselines

## File Structure

```
claude_code/
├── README.md                 # This file
├── config.py                 # Configuration parameters
├── data_loader.py            # Dataset implementations
├── models.py                 # Model architectures
├── amr_trainer.py            # Training algorithms (AMR, ERM, GroupDRO, JTT)
├── evaluation.py             # Evaluation utilities
├── visualization.py          # Plotting functions
├── run_experiment.py         # Main experiment script
└── results/                  # Output directory (created during execution)
    ├── training_curves.png
    ├── group_performance.png
    ├── method_comparison.png
    ├── robustness_tradeoff.png
    ├── results_table.csv
    ├── results.json
    └── log.txt
```

## Citation

```
@article{amr2025,
  title={Adaptive Margin Regularization for Mitigating Spurious Correlations Through Loss Landscape Engineering},
  year={2025}
}
```

## License

MIT License
