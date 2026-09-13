# SymVAE: Symmetry-Aware Variational Autoencoders for Neural Network Weight Generation

This repository contains the implementation and experiments for SymVAE, a novel variational autoencoder framework that addresses weight space symmetries through learned canonicalization and equivariant processing.

## Overview

Neural network weight spaces possess inherent symmetries (permutation and scaling) that create redundant representations, posing challenges for generative modeling. SymVAE addresses these challenges through:

1. **Learned Canonicalization**: An optimal transport-based module that maps weights to canonical forms
2. **Equivariant Encoder-Decoder**: Symmetry-aware architecture producing invariant latent codes
3. **Hierarchical Latent Space**: Disentangled task-level and architecture-specific representations

## Project Structure

```
claude_code/
├── models.py           # SymVAE, baselines (VanillaVAE, HyperNetwork), and target MLP
├── data.py             # Model zoo creation and weight dataset utilities
├── training.py         # Training and evaluation pipelines
├── visualization.py    # Plotting and visualization utilities
├── run_experiment.py   # Main experiment script
└── README.md           # This file
```

## Requirements

- Python 3.8+
- PyTorch 1.9+
- torch-geometric
- numpy
- matplotlib
- pandas
- tqdm

## Running the Experiments

### Quick Start

Run the full experiment suite with default parameters:

```bash
python run_experiment.py
```

### Custom Configuration

```bash
python run_experiment.py \
    --n_models 100 \
    --n_epochs_zoo 50 \
    --n_epochs_gen 100 \
    --batch_size 16 \
    --latent_dim 64 \
    --task_type classification
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--input_dim` | 10 | Input dimension of target networks |
| `--hidden_dim` | 32 | Hidden dimension of target networks |
| `--n_hidden_layers` | 2 | Number of hidden layers |
| `--output_dim` | 2 | Output dimension (num classes for classification) |
| `--n_models` | 100 | Number of models in the zoo |
| `--n_epochs_zoo` | 50 | Epochs for training each model in zoo |
| `--n_epochs_gen` | 100 | Epochs for weight generation models |
| `--batch_size` | 16 | Batch size |
| `--lr` | 1e-3 | Learning rate |
| `--beta` | 0.1 | KL divergence weight |
| `--latent_dim` | 64 | Latent dimension |
| `--task_type` | classification | Task type (classification/regression) |
| `--seed` | 42 | Random seed |

## Experiments

The experiment script runs the following:

1. **Model Zoo Creation**: Train diverse neural networks on synthetic tasks
2. **Weight Generation Model Training**: Train SymVAE variants and baselines
3. **Evaluation**:
   - Generation quality (test accuracy/loss of generated weights)
   - Symmetry invariance (latent variance under permutations)
   - Interpolation smoothness (latent space quality)
4. **Ablation Studies**: Compare full SymVAE vs. variants without canonicalization or hierarchical structure

## Models

- **SymVAE_Full**: Complete SymVAE with canonicalization and hierarchical latent
- **SymVAE_NoCanon**: SymVAE without learned canonicalization
- **SymVAE_NoHier**: SymVAE without hierarchical latent structure
- **Vanilla_VAE**: Standard VAE baseline without symmetry handling
- **HyperNetwork**: Direct task-to-weight mapping baseline

## Outputs

After running, the following files are generated:

- `log.txt`: Detailed experiment log
- `results.json`: Complete results in JSON format
- `summary_table.csv`: Summary of evaluation metrics
- `*_training_curves.png`: Training/validation loss curves
- `model_comparison.png`: Bar chart comparing models
- `generation_quality.png`: Generation quality metrics
- `latent_variance.png`: Symmetry invariance comparison
- `interpolation_smoothness.png`: Latent interpolation quality
- `ablation_study.png`: Ablation study results
- `radar_comparison.png`: Multi-metric radar chart

## Citation

If you use this code, please cite:

```bibtex
@article{symvae2025,
  title={SymVAE: Symmetry-Aware Variational Autoencoders for Neural Network Weight Generation},
  year={2025}
}
```
