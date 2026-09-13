# Methodology

Building on our observation that DWS and NFT encode different inductive biases, we design experiments to (1) quantify these differences through training dynamics analysis, and (2) test whether they translate to task-dependent performance advantages.

## Overview

Our methodology comprises three components:

1. **Inductive Bias Measurement:** Quantify locality vs global attention through coefficient of variation (CoV) of layer-wise weight updates during training
2. **Architecture-Task Interaction:** Test whether DWS (locality) excels on local anomaly detection while NFT (global) excels on holistic property aggregation
3. **Controlled Comparison:** Match parameter budgets and training procedures across architectures to isolate inductive bias effects

## Architectures

### MLP Baseline

A standard multi-layer perceptron that flattens weight matrices into vectors and processes them without equivariant structure. This establishes the performance floor when symmetry is ignored.

**Configuration:** 3 hidden layers, ReLU activations, matched to ~10M parameters.

### Deep Weight Space (DWS)

DWS processes weights through equivariant layers that respect permutation symmetry while preserving spatial structure within each layer [Navon et al., 2023].

**Rationale:** By operating within each weight matrix rather than across them, DWS should produce more localized representations—potentially advantageous for detecting anomalies that manifest in specific layers or weight regions.

**Configuration:** Equivariant encoder with 3 layers, hidden dimension 256, ~5M parameters.

### Neural Functional Transformer (NFT)

NFT tokenizes weight matrices and applies transformer self-attention across all tokens [Zhou et al., 2024].

**Rationale:** Global attention enables information flow between all weight tokens, potentially advantageous for tasks requiring aggregation of information across the entire weight space.

**Configuration:** 4 attention layers, 4 heads, hidden dimension 256, ~5M parameters.

## Inductive Bias Measurement

To quantify the locality vs global attention difference, we analyze training dynamics through the coefficient of variation (CoV) of layer-wise weight updates:

$$\text{CoV} = \frac{\sigma(\|\Delta W_l\|)}{\mu(\|\Delta W_l\|)}$$

where $\Delta W_l$ is the weight update magnitude for layer $l$.

**Intuition:** Higher CoV indicates more varied updates across layers (locality); lower CoV indicates more uniform updates (global information sharing).

We track this metric throughout training to confirm that architectural differences manifest in measurable behavioral differences.

## Task Design

### Task 1: Backdoor Detection (Local Pattern)

**Hypothesis:** DWS should excel because backdoor triggers manifest as localized weight anomalies.

**Setup:** Binary classification of models as clean or backdoored. We use synthetic backdoor injection: localized perturbations to specific layer weights.

**Metric:** Area Under ROC Curve (AUC)

### Task 2: Accuracy Prediction (Global Statistic)

**Hypothesis:** NFT should excel because model accuracy depends on holistic weight statistics.

**Setup:** Regression to predict held-out test accuracy from weights. Target is a global statistic derived from aggregate weight properties.

**Metric:** Root Mean Squared Error (RMSE)

## Experimental Design

We employ a 2×3 factorial design:

| Factor | Levels |
|--------|--------|
| Task | Backdoor, Accuracy |
| Architecture | MLP, DWS, NFT |

**Analysis:** Two-way ANOVA to test for interaction effect (architecture × task). A significant interaction would confirm that performance advantages are task-dependent.

## Training Protocol

All architectures use identical training procedures:

```yaml
optimizer: AdamW
learning_rate: 1e-4
weight_decay: 1e-2
batch_size: 64
epochs: 100
seeds: [42, 123, 456]
```

**Controlled Variables:**
- Same training/validation/test splits
- Same data augmentation (none)
- Same early stopping criterion (validation loss plateau)

## Figure: Architecture Comparison

![Figure 1: t-SNE visualization of learned representations](figures/tsne_representations.png)

*Figure 1: t-SNE visualization of weight-space representations learned by MLP, DWS, and NFT on the same input models. Note the different clustering structures reflecting distinct inductive biases.*

![Figure 2: NFT attention patterns](figures/attention_heatmap.png)

*Figure 2: NFT attention heatmap showing global information flow across weight tokens. Brighter values indicate stronger attention weights.*

## Summary

Our methodology enables controlled comparison of inductive biases in weight-space architectures through:

1. **Quantification:** CoV metric captures locality vs global processing
2. **Hypothesis testing:** Specific predictions for task-dependent advantages
3. **Controlled design:** Matched parameters and procedures isolate architectural effects

This addresses the critical gap of no systematic benchmark comparison between permutation-equivariant architectures on model property prediction.
