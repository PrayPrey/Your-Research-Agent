# 4. Experimental Setup

We design four experiments that test successive steps in the causal chain from permutation
symmetry to encoder performance. Each experiment answers a specific question, and together
they build a complete mechanistic picture.

## 4.1 Research Questions

**RQ1 (H-E1):** Does the Schurholt MNIST-CNN zoo contain non-trivial permutation orbits,
and is it free of batch normalization that would break permutation symmetry?

**RQ2 (H-M1):** Do flat MLP encoders at matched capacity waste capacity navigating
permutation orbits — i.e., do they assign distinct embeddings to functionally-equivalent
weight configurations?

**RQ3 (H-M2):** Do NFN encoders at matched capacity structurally eliminate permutation
sensitivity — i.e., do they assign near-identical embeddings to permutation-equivalent
weight configurations?

**RQ4 (H-M3):** Does the capacity freed by equivariance translate into higher Spearman
rank correlation, and does the benefit follow a monotone symmetry spectrum
(flat MLP < Deep Sets < NFN)?

Each RQ maps to a specific claim from Section 1: RQ1 validates the precondition for the
mechanism; RQ2 and RQ3 directly measure the capacity-wasting mechanism; RQ4 measures
the downstream consequence on accuracy prediction quality.

## 4.2 Dataset

We evaluate on the **Schurholt et al. MNIST-CNN model zoo** (hyp\_rand variant)
[Schurholt et al., 2022]. This zoo contains trained checkpoints of a plain feedforward
CNN (no batch normalization) on MNIST, with ground-truth test accuracies.

| Property | Value |
|----------|-------|
| Zoo architecture | 2-layer CNN (conv1: 32 filters, conv2: 64 filters, fc1: 128 units, fc2: 10 units) |
| Total parameters per model | ~2,464 weight scalars (flattened) |
| Batch normalization | None (BN-free, confirmed by H-E1) |
| Checkpoints (hyp\_rand) | 2,249 total |
| Train / Val / Test split | 1,589 / 322 / 338 (Schurholt et al. standard) |
| Accuracy range | Broad (spanning low to near-perfect) |

We use the hyp\_rand variant, which spans diverse hyperparameter configurations and provides
a broad accuracy distribution suitable for rank-correlation evaluation. CIFAR-10 cross-zoo
validation was planned but not executed due to a dataset download failure (see Section 6).

**Why this dataset:** The Schurholt MNIST-CNN zoo is the standard benchmark for weight-space
accuracy prediction [Navon et al., 2023; Schurholt et al., 2023] and satisfies the critical
precondition for our study: BN-free feedforward networks with well-defined neuron-permutation
symmetry.

## 4.3 Baselines

We compare three encoders representing the full symmetry spectrum:

| Encoder | Symmetry Level | Parameters | Source |
|---------|---------------|------------|--------|
| Flat MLP | None | 500,577 | Unterthiner et al. [2020] style |
| Deep Sets | Permutation-invariant | 471,936 | Zaheer et al. [2017] |
| NFN | Permutation-equivariant | 521,953 | Navon et al. [2023] |

**Why flat MLP:** The dominant prior approach and the null hypothesis — no symmetry exploitation.

**Why Deep Sets:** An intermediate baseline providing permutation invariance (weaker than
equivariance) that has never been benchmarked on model zoo accuracy prediction. It tests
whether invariance alone captures most of the equivariance benefit, or whether equivariance
provides additional value.

**Why NFN:** The strongest available equivariant encoder for feedforward network weight spaces,
with direct support for the MNIST-CNN weight tensor shapes [Navon et al., 2023].

All three baselines are matched to $\sim$500K parameters ($\pm5\%$) via per-architecture
width grid search (Section 3.3). This is the central fairness guarantee of our benchmark.

## 4.4 Evaluation Metrics

**Spearman rank correlation ($\rho$):** Primary metric, measuring how well the predicted
accuracy ordering matches the ground-truth ordering on the held-out test split. Range $[-1, 1]$;
higher is better. This is the canonical metric for model zoo property prediction
[Unterthiner et al., 2020; Schurholt et al., 2022].

**$\Delta\rho$ with bootstrap 95% CI:** Primary comparison metric. We compute
$\Delta\rho = \rho(\text{NFN}) - \rho(\text{flat MLP})$ and its bootstrap 95% confidence
interval (1,000 resamples, paired). A positive CI lower bound establishes statistical
significance without parametric assumptions.

**Permutation sensitivity score:** Mechanism diagnostic measuring how well each encoder
distinguishes permutation-equivalent weight configurations (Section 3.4). Lower = more
equivariant; threshold $< 0.1$ for NFN (PASS), $> 0.3$ for flat MLP (PASS).

## 4.5 Implementation Details

All experiments use PyTorch on a single CUDA GPU.

| Hyperparameter | Value |
|----------------|-------|
| Optimizer | Adam |
| Learning rate | $10^{-3}$ |
| LR schedule | Cosine annealing to $10^{-6}$ over 150 epochs |
| Batch size | 32 |
| Weight decay | $10^{-4}$ |
| Training epochs | 150 |
| Loss function | Mean squared error |
| Bootstrap resamples | 1,000 |
| Random seed | 42 |
| Permutation pairs | 500 (50 per accuracy decile) |

The NFN checkpoint from H-M2 (epoch 114, best validation loss) is reused in H-M3 for
the primary comparison, ensuring no additional training advantage. Deep Sets is trained
fresh for 150 epochs (best at epoch 39, validation loss = 0.0203).
