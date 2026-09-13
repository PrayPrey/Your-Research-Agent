# SymAE: Symmetry-Aware Autoencoder for Weight Space Learning

## Overview

This directory contains the experimental implementation of **SymAE**, a symmetry-aware autoencoder framework for learning representations of neural network weight spaces.

The core hypothesis: By treating neural network weights as bipartite graphs and using equivariant GNNs that respect permutation symmetries, SymAE produces more semantically meaningful embeddings than naive approaches like PCA or flat MLP autoencoders.

## Experiment Design

1. **Model Zoo Construction**: Train 200 small 3-layer MLPs on CIFAR-10 subsets with varied hyperparameters (learning rate, weight decay, hidden size, dropout), yielding diverse test accuracy profiles.

2. **Methods Compared**:
   - **SymAE (GNN)**: Equivariant GNN encoder + MLP decoder + property prediction head + contrastive loss with permutation augmentations
   - **Flat MLP AE**: Baseline autoencoder on raw/flattened weight vectors
   - **PCA**: Linear dimensionality reduction baseline
   - **Statistics**: Hand-crafted weight statistics features

3. **Evaluation**: Property prediction (test accuracy) via linear probing (Ridge regression) on learned embeddings, measured by R² and MAE.

## Requirements

```
torch>=2.0
torch_geometric>=2.0
torchvision
scikit-learn
numpy
matplotlib
```

## Running the Experiment

```bash
conda activate youra
cd tasks_youra_result_sonnet46/iclr2025_wsl/claude_code
python run_experiment.py
```

The script will:
1. Download CIFAR-10 and train a zoo of 200 models (~10-20 minutes on GPU)
2. Train SymAE and baseline methods (~5-10 minutes on GPU)
3. Generate visualization figures in `results/`
4. Save experiment log to `log.txt`

## Output Files

- `results/training_curves.png` - Training/validation loss curves
- `results/property_loss_curves.png` - Property prediction loss over training
- `results/r2_comparison.png` - R² and MAE comparison across methods
- `results/latent_space.png` - Latent space visualizations (t-SNE)
- `results/scatter_predictions.png` - Predicted vs true accuracy scatter plots
- `results/reconstruction_quality.png` - Weight reconstruction error comparison
- `results/accuracy_distribution.png` - Model zoo accuracy distribution
- `results/results.json` - Numerical results
- `log.txt` - Full experiment log
