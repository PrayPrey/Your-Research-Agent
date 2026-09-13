# Experimental Setup

We design experiments to validate our four sub-hypotheses, each testing a specific aspect of our main claim that finite-compute attribution exhibits structural Pareto trade-offs rooted in non-convex geometry.

## Research Questions

Our experiments address the following questions:

**RQ1 (H-E1):** Do data attribution methods exhibit Pareto trade-offs, i.e., can we observe statistically significant metric crossings where one method outperforms another on rank preservation but underperforms on magnitude fidelity?

**RQ2 (H-M1):** In convex settings, do all attribution quality metrics remain tightly coupled, establishing the baseline expectation that metrics *should* move together?

**RQ3 (H-M2):** Does metric coupling break down in non-convex deep networks, proving that decoupling is a structural property of the optimization landscape rather than an approximation quality artifact?

**RQ4 (H-M3):** Do different attribution methods identify substantially different sets of influential training examples, demonstrating practical consequences of structural trade-offs?

## Datasets and Models

### CIFAR-10 Attribution Benchmark

We use CIFAR-10 [Krizhevsky, 2009] as our primary benchmark, following established attribution evaluation protocols [Park et al., 2023; Koh and Liang, 2017].

| Property | Value |
|----------|-------|
| Training samples | 5,000 (subset for tractable LOO computation) |
| Test samples | 100 (for attribution evaluation) |
| Classes | 10 |
| Image size | 32×32×3 |

**Rationale:** CIFAR-10 is sufficiently complex to exhibit non-convex deep learning behavior while remaining tractable for ground truth estimation via LOO retraining. The 5,000-sample subset allows full LOO computation (5,000 × 10 seeds = 50,000 training runs) within reasonable computational budgets.

### Model Architectures

**ResNet-18 (Non-Convex Setting):**
- Architecture: ResNet-18 modified for CIFAR-10 (smaller initial convolution)
- Training: 200 epochs, SGD with lr=0.1, momentum=0.9, weight_decay=5e-4
- Final accuracy: ~92% on CIFAR-10 test set

**Logistic Regression (Convex Setting):**
- Features: 512-dimensional penultimate layer activations from trained ResNet-18
- Regularization: L2 with C=100
- Solver: LBFGS (exact optimization)

**Rationale:** The convex setting uses the same underlying features but with a convex loss function, isolating the effect of optimization geometry from feature representation quality.

## Attribution Methods

We compare four representative methods spanning different computational paradigms:

| Method | Paradigm | Key Mechanism |
|--------|----------|---------------|
| **TRAK** | Random Projection | Projects gradients to low-dimensional space |
| **TracIn** | Gradient Similarity | Sums gradient dot products across checkpoints |
| **IF** | Hessian Inversion | Solves $H^{-1}v$ via iterative methods |
| **FastIF** | Arnoldi Approximation | Low-rank Hessian approximation |

**Compute Budget Translation:**

All methods are evaluated at matched compute budgets via gradient-equivalent operations (GEOs):

| Budget (GEOs) | TRAK | TracIn | IF | FastIF |
|---------------|------|--------|----|----|
| 10 | 10 proj. dims | 10 checkpoints | 10 HVP iters | 10 Arnoldi steps |
| 25 | 25 proj. dims | 25 checkpoints | 25 HVP iters | 25 Arnoldi steps |
| 50 | 50 proj. dims | 50 checkpoints | 50 HVP iters | 50 Arnoldi steps |
| 75 | 75 proj. dims | 75 checkpoints | 75 HVP iters | 75 Arnoldi steps |
| 100 | 100 proj. dims | 100 checkpoints | 100 HVP iters | 100 Arnoldi steps |

**Rationale:** GEO normalization enables fair comparison across paradigms—at budget $b=50$, all methods have equivalent computational resources.

## Ground Truth Estimation

Ground truth influence is computed via leave-one-out (LOO) retraining:

$$\phi^*_i = f(x_{\text{test}}; \theta^{(-i)}) - f(x_{\text{test}}; \theta)$$

where $\theta^{(-i)}$ is the model trained without example $i$.

**LOO Variance Estimation:**
- Seeds per configuration: $R = 10$
- Total training runs: 5,000 samples × 10 seeds = 50,000
- Ground truth: $\hat{\phi}^*_i = \mathbb{E}_{\xi}[\phi^*_i(\xi)]$
- Variance: $\sigma^2_{\text{LOO}} = \text{Var}_{\xi}[\phi^*_i]$

**Computational Note:** We cache gradient computations and use the pretrained ResNet-18 model from H-E1 across all experiments to ensure consistency.

## Evaluation Metrics

### Primary Metrics

**Rank Preservation ($\rho_r$):** Spearman correlation between estimated and ground truth influence rankings.

**Magnitude Fidelity ($\rho_m$):** Pearson correlation between estimated and ground truth influence values.

### Secondary Metrics

**Top-k Jaccard Similarity:** Overlap between top-50 influential examples identified by different methods:
$$\text{Jaccard}(A, B) = \frac{|A \cap B|}{|A \cup B|}$$

**Partial Correlation:** Cross-metric correlation controlling for compute budget:
$$\text{corr}(\rho_r, \rho_m | b)$$

**R² Regression:** Fraction of metric variance explained by approximation error norm.

## Statistical Analysis

**Bootstrap Confidence Intervals:**
- Resamples: 1,000
- Confidence level: 95%
- Metric crossings declared CI-separated if intervals do not overlap zero

**Seeds:**
- Method seeds: 3 per configuration
- LOO seeds: 10 for ground truth variance estimation
- Total configurations per hypothesis: 60 (4 methods × 5 budgets × 3 seeds)

## Implementation Details

**Framework:** PyTorch 2.0 with CUDA 11.8

**Hardware:** Single NVIDIA A100 GPU (40GB)

**Training Time:**
- ResNet-18 training: ~45 minutes per seed
- LOO retraining: ~4 hours (parallelized across seeds)
- Attribution computation: ~30 minutes per method/budget combination

**Reproducibility:** All random seeds are fixed. Code and data will be released upon publication.

## Experiment-Hypothesis Mapping

| Hypothesis | Research Question | Key Metric | Success Criterion |
|------------|-------------------|------------|-------------------|
| H-E1 | RQ1 (Trade-offs exist?) | Metric crossings | $\geq 2$ budgets with CI-separated crossings |
| H-M1 | RQ2 (Convex coupling?) | Partial correlation | $\geq 0.95$ at all budgets |
| H-M2 | RQ3 (Deep decoupling?) | R² regression | $< 0.80$ in deep networks |
| H-M3 | RQ4 (Practical impact?) | Top-k Jaccard | $< 0.70$ between method pairs |

This structured validation allows us to not only demonstrate trade-off existence but also provide mechanistic evidence for their geometric origin.
