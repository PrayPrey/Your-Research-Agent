# Causal Data Valuation for Multi-Stage Foundation Model Training

This repository contains the implementation of experiments for evaluating stage-aware data valuation methods in multi-stage foundation model training.

## Overview

Foundation models undergo distinct training stages (pre-training, instruction-tuning, alignment), yet current data attribution and valuation methods treat training as monolithic. This project implements and evaluates a **causal framework for stage-dependent data valuation** that attributes model capabilities to data contributions at specific training phases.

## Project Structure

```
claude_code/
├── config.py                   # Configuration settings
├── data_generator.py           # Synthetic data generation
├── model.py                    # Simple transformer model
├── trainer.py                  # Multi-stage training framework
├── valuation_methods.py        # Data valuation implementations
├── run_experiment.py           # Main experiment runner
├── visualize_results.py        # Result visualization
├── README.md                   # This file
├── results.json                # Experiment results (generated)
├── log.txt                     # Execution log (generated)
└── *.png                       # Generated figures
```

## Requirements

- Python 3.8+
- PyTorch 2.0+
- NumPy
- Matplotlib
- Seaborn
- SciPy
- tqdm

Install dependencies:
```bash
pip install torch numpy matplotlib seaborn scipy tqdm
```

## Running Experiments

### Quick Start

Run the complete experiment pipeline:

```bash
cd claude_code
python run_experiment.py
```

This will:
1. Generate synthetic datasets for all training stages
2. Train models through multi-stage pipeline (pretraining → instruction-tuning → alignment)
3. Evaluate multiple data valuation methods
4. Save results to `results.json` and logs to `log.txt`

### Generate Visualizations

After running experiments:

```bash
python visualize_results.py
```

This generates:
- `training_curves.png`: Loss curves for each training stage
- `correlation_comparison.png`: Method performance comparison
- `computation_time.png`: Computational efficiency analysis
- `value_distributions.png`: Data value distributions
- `stage_comparison_radar.png`: Radar chart of method performance
- `test_metrics.png`: Test performance after each stage

## Methods Implemented

### Proposed Method
- **Stage-Aware Influence**: Our proposed method that uses influence functions adapted for multi-stage training with chain rule computation

### Baseline Methods
- **Standard Influence**: Standard influence functions without stage awareness
- **TracIn**: Tracking influence through checkpoints
- **Random Baseline**: Random valuation for comparison
- **Data Shapley**: (Optional, computationally expensive)

## Configuration

Edit `config.py` to modify:

- **Model size**: Choose between "small" and "medium" architectures
- **Training parameters**: Learning rates, batch sizes, epochs for each stage
- **Data size**: Number of samples for each training stage
- **Valuation parameters**: Number of samples to evaluate, low-rank dimensions
- **Methods**: Which valuation methods to run

Example configurations:

```python
# Quick test (faster, less accurate)
EXPERIMENT_CONFIG = {
    "model_size": "small",
    "num_runs": 1,
    "compute_ground_truth": False
}

# Full experiment (slower, more accurate)
EXPERIMENT_CONFIG = {
    "model_size": "medium",
    "num_runs": 3,
    "compute_ground_truth": True
}
```

## Experimental Design

The experiment follows these stages:

1. **Data Generation**: Create synthetic language modeling data with different properties for each training stage
2. **Multi-Stage Training**:
   - Pre-training: Next token prediction on sequential data
   - Instruction-tuning: Supervised fine-tuning on input-output pairs
   - Alignment: Preference learning with chosen/rejected pairs
3. **Data Valuation**: Compute influence scores for training samples using different methods
4. **Evaluation**: Compare valuation methods using:
   - Correlation with ground truth (leave-one-out)
   - Computational efficiency
   - Cross-stage discrimination ability

## Expected Outputs

### Metrics
- **Training metrics**: Loss curves, test perplexity for each stage
- **Valuation metrics**:
  - Spearman correlation with ground truth
  - Computation time
  - Value distributions

### Visualizations
- Training loss curves across stages
- Method performance comparison (correlation bar charts)
- Computational efficiency comparison (time bar charts)
- Value distribution histograms
- Radar charts showing stage-specific performance
- Test metrics progression

## GPU Support

The code automatically detects and uses available GPUs. Check the log for:
```
Device: cuda
Number of GPUs: X
```

## Limitations

This implementation uses:
- **Synthetic data** for reproducibility and controlled experiments
- **Simplified models** (small transformers) for computational efficiency
- **Approximations** for influence functions (no Hessian inverse)
- **Limited ground truth** (only for small sample sizes due to computational cost)

For production use, consider:
- Using real datasets (C4, Flan, HH-RLHF)
- Scaling to larger models (7B-13B parameters)
- Implementing exact influence functions with Hessian computation
- Using more sophisticated approximation methods (K-FAC, low-rank updates)

## Troubleshooting

**Out of memory errors:**
- Reduce batch size in `config.py`
- Use smaller model ("small" instead of "medium")
- Reduce number of samples for valuation

**Slow execution:**
- Disable ground truth computation: `compute_ground_truth: False`
- Reduce number of runs: `num_runs: 1`
- Skip expensive methods (Data Shapley)

**Import errors:**
- Ensure all dependencies are installed
- Check Python version (3.8+)

## Citation

If you use this code, please cite:

```bibtex
@article{causal_data_valuation_2025,
  title={Causal Data Valuation for Multi-Stage Foundation Model Training},
  year={2025}
}
```

## Contact

For questions or issues, please open an issue in the repository.
