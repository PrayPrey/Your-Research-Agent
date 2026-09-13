# 3. Methodology

Our experimental design is constructed to make the crossover visible. The minimum-data threshold can only be detected if the training size grid is fine enough to straddle it, and the intermediate condition (PermAug) can only be compared if it is implemented correctly alongside both extremes. Each design decision follows from these requirements.

## 3.1 Problem Setup

We study *supervised weight-space property prediction*: given a set of trained neural networks $\{(\theta_i, y_i)\}_{i=1}^N$, where $\theta_i \in \mathbb{R}^d$ are the weight parameters and $y_i \in \mathbb{R}$ is a ground-truth property (test accuracy), we learn an encoder $f_\phi: \mathbb{R}^d \to \mathbb{R}^h$ and a prediction head $g_\psi: \mathbb{R}^h \to \mathbb{R}$ to minimize mean squared error on held-out models. We measure performance via the coefficient of determination (R²) on a fixed test split shared across all encoder types.

**The efficiency ratio** is our primary evaluation metric:

$$\text{EfficiencyRatio} = \frac{N_{\text{plain},90}}{N_{\text{equiv},90}}$$

where $N_{\text{plain},90}$ is the minimum training size at which the plain encoder reaches 90% of its peak R², and $N_{\text{equiv},90}$ is the analogous quantity for the equivariant encoder. A ratio $\geq 2$ indicates the equivariant encoder reaches equivalent relative performance at half or less the data requirement of the plain encoder.

## 3.2 Dataset

We use the **ModelZooDataset CIFAR-10 CNN zoo** [Schürholt et al., 2022], a collection of approximately 9,000 convolutional neural networks trained on CIFAR-10 with systematically varied hyperparameters (learning rate, weight decay, dropout). Each model is associated with ground-truth test accuracy on the CIFAR-10 test set. We use the standardized shared train/test split from the repository, ensuring all encoder types are trained and evaluated on identical splits — a prerequisite for valid efficiency comparison.

We use training sizes $N \in \{100, 250, 500, 1000, \text{full}\}$, logarithmically spaced to detect the crossover between N=100 and N=250. The full training set contains approximately 7,000 models; the test set is fixed at approximately 2,000 models.

## 3.3 Encoder Architectures

We compare three conditions:

**Flat-MLP (Plain baseline).** All weight parameters of each model are flattened into a single vector and passed through a standard MLP with 3 hidden layers, hidden dimension 256, and ReLU activations. Total parameters: ~190K (medium tier). This encoder is permutation-sensitive by design — the same weight tensor with neurons permuted produces a different output.

**Flat-MLP + PermAug (Augmented intermediate).** Identical to Flat-MLP in architecture, but during training each model weight tensor is randomly permuted at its first hidden layer with probability 1.0 before flattening. This expands N=100 to 1,100 effective training examples (11× expansion factor), providing a data-level approximation of permutation invariance without modifying the encoder architecture. PermAug is verified to produce meaningfully different augmented samples from originals (aug_diff=4.12≫1×10⁻⁶; see Section 5.2).

**GNN-NFN (Structural equivariant encoder).** We use the GNN-NFN architecture [Kofinas et al., 2024], which represents each neural network as a computational graph: neurons are nodes, weight matrices are edge features, and biases are node features. A graph neural network processes this representation with message-passing operations that are equivariant to the permutation group of each layer. We use a 4-layer GNN-NFN with hidden dimension 64, yielding approximately 180K parameters (medium tier). The graph construction for the CIFAR-10 CNN zoo treats convolutional weight tensors as reshaped edge matrices between input-output channel pairs.

**Parameter matching.** All three encoders operate in the *medium parameter tier* (50K–200K parameters), ensuring that any observed efficiency difference is attributable to inductive bias rather than model capacity.

## 3.4 Training Protocol

All encoders are trained with the Adam optimizer, learning rate 1×10⁻³, weight decay 1×10⁻⁴, batch size 64, for 100 epochs. Hyperparameters were tuned once on the full-data condition and held fixed across all training sizes and encoder types — standard practice in learning curve studies that avoids the confound of per-condition hyperparameter optimization.

For each training size $N$, we sample $N$ models uniformly at random from the training split. We use a single random seed per condition-size combination in our proof-of-concept experiments (PoC mode), with bootstrapped confidence intervals computed from 1,000 resamples of the training set.

## 3.5 Evaluation Metrics

**Primary metric:** Test-set R² (coefficient of determination) for accuracy prediction.

**Sample efficiency ratio:** $N_{\text{plain},90} / N_{\text{equiv},90}$, where $N_{90}$ is interpolated from the learning curve.

**Bootstrap 95% confidence intervals:** Percentile method with 1,000 resamples; used to assess statistical significance of ordering comparisons.

**PermAug fraction of equivariant gap:** $(R^2_{\text{PermAug}} - R^2_{\text{flat}}) / (R^2_{\text{GNN-NFN}} - R^2_{\text{flat}})$ — measures how much of the structural advantage is captured by data augmentation alone.

## 3.6 Permutation Equivariance Verification

Before running property prediction experiments, we verify that the claimed structural property holds in practice. For GNN-NFN and flat-MLP, we apply 50 random layer permutations to 200 randomly sampled CIFAR-10 zoo models (10,000 checks total) and measure max absolute difference in encoder output. For DWSNets — which requires M>2 fully connected layers, incompatible with the CIFAR-10 CNN architecture — we verify on 50 synthetic 4-layer MLP weight tensors (1,000 checks). This verification is structurally independent of training: equivariance is an architectural property that holds at any weight configuration, trained or random.

**Rationale:** The efficiency claim is only mechanistically interpretable if we can confirm GNN-NFN genuinely treats permutation-equivalent weight tensors identically in practice, not just in theory. The verification step makes the causal chain empirically grounded.
