# Self-Supervised Representation Learning on Neural Network Weights

## Key Metadata
- **Authors:** Schürholt et al.
- **Year:** 2021
- **Venue:** NeurIPS 2021
- **Core Contribution:** First demonstration that self-supervised learning on neural network weight populations yields useful representations for property prediction and model analysis.

## Section Summaries

### Abstract
We propose learning representations of neural network populations by applying self-supervised learning (SSL) directly to weight space. An autoencoder trained on a zoo of model checkpoints without labels learns a latent space that encodes model properties: training accuracy, generalization gap, hyperparameters. These hyper-representations outperform hand-crafted feature extraction and enable generation of functional models via sampling from the learned latent distribution.

### Introduction & Motivation
Neural networks have traditionally been analyzed by their inputs/outputs, not their weights. Treating weights as data and populations of networks as datasets opens new analysis routes. Prior work on model analysis used output-based metrics (loss curves, accuracy on probes) or manual weight statistics. SSL on the weight space itself — learning to compress and reconstruct weight vectors — may capture structural properties that correlate with model behavior without requiring behavioral evaluation.

### Methodology
Architecture: convolutional autoencoder operating on flattened weight vectors. Each checkpoint's weights are flattened into a 1D vector, chunked if needed, and passed through a standard CNN encoder to produce a latent code z. Decoder reconstructs the weight vector from z. Training: reconstruction loss (MSE) on weight chunks — pure autoencoder SSL without contrastive objectives. No equivariance enforcement. Permutation augmentation: random neuron permutations applied as data augmentation. Evaluation: train linear probe on frozen latent z for property prediction (accuracy, learning rate, weight decay).

### Experiments & Results
Dataset: MNIST model zoo — 50,000 small MLPs (3 hidden layers, 100-400 neurons per layer) with known accuracy and training hyperparameters. Property prediction: linear probe R²=0.89 for accuracy, R²=0.71 for generalization gap, hyperparameter recovery AUC=0.82. Generation: sample z from learned prior, decode to weights, evaluate on MNIST → 78% of generated models are functional (>50% accuracy). No cross-architecture evaluation (all same homogeneous architecture).

### Discussion & Conclusion
The core finding: weight-space SSL is viable and useful. The representation captures model quality without any labels. Key limitations: (1) homogeneous architecture only, (2) no equivariance, (3) small model scale. The paper frames these as open problems for follow-up work. Direct predecessor to SANE (2024) and MultiZoo-SANE.

## Key Contributions
- Foundational demonstration of SSL on neural network weight populations
- Linear probe evaluation protocol for weight-space representations (standard since)
- Weight zoo construction methodology (diversity through hyperparameter variation)
- Model generation from latent weight space

## Potential Relevance
This paper establishes the evaluation protocol for property prediction from weight representations that all subsequent work builds on. The R²=0.89 accuracy prediction baseline and the zoo construction methodology are the concrete starting points for Gap 1 experiments. Critically, the limitations (no equivariance, homogeneous architectures) are exactly what Gap 1 proposes to address.
