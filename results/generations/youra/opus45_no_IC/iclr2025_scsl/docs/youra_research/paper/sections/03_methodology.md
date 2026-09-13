# Methodology

We present a framework for detecting minority-group samples through early-epoch loss analysis and validating the underlying simplicity bias mechanism via linear probes.

## Problem Setup

Consider a classification task where inputs $x$ have class label $y$ and group membership $g$. Groups arise from the interaction of core features (predictive of $y$) and spurious features (correlated with $y$ in training but not causally related). Minority groups have spurious features that *conflict* with the label—e.g., waterbirds appearing on land backgrounds.

Under ERM training, models exploit spurious correlations because they provide simpler, more consistent signals. This causes majority samples (aligned spurious and core features) to achieve low loss rapidly, while minority samples (conflicting features) require core feature learning and converge slowly.

## Loss Trajectory Detection

### Onset Delay

For each sample $i$, we track loss $L_i(t)$ across training epochs $t$. The **onset delay** $d_i$ is the first epoch where loss decreases by at least 10% from initial loss:

$$d_i = \min\{t : L_i(t) < 0.9 \cdot L_i(0)\}$$

Samples with large $d_i$ are candidates for minority-group membership.

### Early-Epoch Loss Threshold

Rather than computing onset delay (which requires tracking from epoch 0), we use a simpler signal: loss at early detection epoch $T_\text{early}$. Based on SPARE's finding that simplicity bias is observable within 20% of training, we set $T_\text{early} = 5$ (5% of 100 epochs).

We identify candidate minority samples as those with loss above the $k$-th percentile at $T_\text{early}$:

$$\text{minority\_candidate}_i = \mathbf{1}[L_i(T_\text{early}) > \text{percentile}_k(L(T_\text{early}))]$$

where $k$ is chosen to match the expected minority rate. At 5% minority rate, $k = 95$ selects the top 5% of high-loss samples.

### Statistical Testing

To verify that loss distributions differ between groups, we use the Mann-Whitney U test, which compares the ranks of losses between minority and majority samples without assuming normal distributions. A significant result (*p* < 0.05) indicates the detection signal is not due to chance.

## Linear Probe Analysis

To verify the simplicity bias mechanism, we train linear probes on frozen ResNet-18 features at multiple epochs.

### Feature Extraction

For each checkpoint at epoch $t \in \{5, 20, 50, 81, 100\}$:
1. Extract 512-dimensional average-pooled features from the penultimate layer
2. Freeze the backbone (no gradient updates)

### Probe Training

We train two separate logistic regression probes:
- **Spurious probe**: Predicts background (water/land)
- **Core probe**: Predicts bird type (waterbird/landbird)

Each probe is trained for 1000 iterations with L2 regularization ($C = 1.0$) using sklearn's LogisticRegression with LBFGS optimizer.

### Probe Evaluation

Probes are evaluated on the test set (5,794 samples). If simplicity bias operates:
- Spurious probe accuracy should exceed core probe accuracy at early epochs
- The gap should persist (magnitude bias) or close (timing bias) across training

## Experimental Predictions

Our hypotheses generate specific predictions:

**H-E1 (Existence)**: At $T_\text{early} = 5$, samples with loss above the 95th percentile have minority-group precision > 0.5 and recall > 0.3.

**H-M1 (Mechanism)**: At epoch 5, spurious probe accuracy exceeds core probe accuracy, confirming simplicity bias causes early spurious feature encoding.

**H-M2 (Timing)**: Spurious probe accuracy peaks before core probe accuracy (timing gap hypothesis) OR spurious accuracy exceeds core accuracy throughout (magnitude gap hypothesis).

## Implementation Details

- **Model**: ResNet-18 with ImageNet pretrained weights (IMAGENET1K_V1)
- **Optimizer**: SGD with learning rate 0.001, momentum 0.9, weight decay 1e-4
- **Batch size**: 64 for training, 128 for probe analysis
- **Epochs**: 100 total, checkpoints at epochs 5, 20, 50, 81, 100
- **Random seed**: 42 for reproducibility
