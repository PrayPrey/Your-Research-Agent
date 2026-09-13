# H-E1 Quotient Space Existence - Implementation

This implementation validates hypothesis H-E1: the existence of a finite-dimensional quotient space that captures task-relevant computational structure across neural network architectures.

## Structure

```
code/
├── main.py                 # Main experiment script
├── requirements.txt        # Python dependencies
├── src/
│   ├── config.py          # Hyperparameters and configuration
│   ├── data.py            # Synthetic dataset (ModelZoo-14K simulation)
│   ├── loss.py            # Reconstruction and equivariance losses
│   ├── train.py           # Training pipeline
│   ├── evaluate.py        # Evaluation metrics
│   ├── visualize.py       # Figure generation
│   └── models/
│       ├── baseline.py    # Deep Sets baseline
│       └── proposed.py    # Slot-Equivariant encoder
├── checkpoints/           # Model checkpoints
├── figures/               # Generated visualizations
└── results/               # Experiment results (JSON)
```

## Setup

```bash
pip install -r requirements.txt
```

## Run Experiment

```bash
# Set CUDA device
export CUDA_VISIBLE_DEVICES=0

# Run main experiment
python main.py
```

## Success Criteria (MUST_WORK Gate)

1. **Reconstruction Error < 10%**: MSE-based reconstruction on test set
2. **Frozen-K Generalization < 10%**: Cross-architecture generalization (RNN holdout)
3. **Kernel Robustness ≥ 90%**: Permutation invariance preservation

## Implementation Notes

This is a **proof-of-concept** implementation using:
- Synthetic data simulating ModelZoo-14K (1000 train, 200 val, 200 test samples)
- Reduced weight dimensionality (1000 instead of 100,000)
- Reduced training epochs (20 instead of 100)

The implementation validates the core mechanism without requiring full dataset downloads.

## Output

- `results/experiment_results.json`: Metrics and gate verdict
- `figures/gate_metrics.png`: Target vs actual comparison
- `figures/training_curves.png`: Loss curves over epochs
- `figures/quotient_space_tsne.png`: t-SNE visualization
- `figures/error_distribution.png`: Reconstruction error histogram
