# Methodology

To establish a calibration baseline, we measure the simplest case—seed-controlled initialization under full determinism—before adding complexity. Our systematic hypothesis loop validates each mechanism step to ensure complete understanding rather than just measuring end-to-end variance.

## Design Philosophy: Simplest Case First

**Why this design?** Complex UQ methods layer multiple uncertainty sources (dropout, ensemble diversity, Bayesian priors). Before quantifying their contributions, we must measure the baseline from weight initialization alone. This follows fundamental scientific methodology: isolate variables, measure one at a time, validate causal mechanisms.

**Alternatives considered:**
- **CIFAR-10 CNNs** — Picard et al. (2021) explored this space; we establish simpler baselines first
- **ImageNet ResNets** — Prohibitively expensive (days of compute per seed)
- **Synthetic tasks** — Not representative of real deep learning applications

**Why dual datasets?** MNIST alone risks being "too easy" (ceiling effect compressing variance). Fashion-MNIST provides a medium-difficulty comparison (identical dimensions, 10 classes, but ~88% vs. ~98% accuracy) testing task-dependency without confounding architectural changes.

## Experimental Setup

### Architecture: Simple MLPs

We test two fully-connected architectures:

- **1-layer MLP:** 784 → 128 → 10 (~196K parameters)
- **2-layer MLP:** 784 → 256 → 128 → 10 (~400K parameters)

Both use ReLU activation and cross-entropy loss. Initialization follows PyTorch defaults (Xavier/Kaiming) controlled by random seed. This dual-architecture design tests whether variance scales with depth while maintaining computational feasibility (<25 minutes total runtime).

**Why MLPs?** They represent the simplest non-trivial architecture for baseline establishment. Variance measurement on more complex architectures (CNNs, Transformers) should build on this foundation.

### Datasets: Dual Task Difficulty

- **MNIST:** 28×28 grayscale handwritten digits, 60K train / 10K test, 10 classes (~98% baseline accuracy)
- **Fashion-MNIST:** 28×28 grayscale clothing items, 60K train / 10K test, 10 classes (~88-90% baseline accuracy)

Both datasets are isomorphic (identical structure) but differ in task difficulty, enabling controlled comparison of variance magnitude vs. accuracy ceiling effects.

### Training Protocol: Full Determinism

To isolate seed-based variance from other stochasticity sources, we enforce complete determinism:

```python
import torch

torch.manual_seed(seed)
torch.backends.cudnn.deterministic = True
torch.use_deterministic_algorithms(True)

# Fixed data order
def seed_worker(worker_id):
    worker_seed = torch.initial_seed() % 2**32
    numpy.random.seed(worker_seed)
    random.seed(worker_seed)

g = torch.Generator()
g.manual_seed(0)
DataLoader(dataset, worker_init_fn=seed_worker,
           generator=g, shuffle=False)  # Fixed order
```

**Fixed hyperparameters:**
- Optimizer: SGD with lr=0.01, momentum=0.9
- Batch size: 64
- Epochs: 10 (sufficient for convergence on MNIST/Fashion-MNIST)
- No dropout, no batch normalization, no data augmentation

**Why enforce determinism?** Under these conditions, the *only* variance source across training runs is the initial random seed. Any observed test accuracy variance directly reflects initialization stochasticity propagating through training.

### Sample Size: N=30 Seeds per Condition

Following Rajput and Kumar (2023), we use N=30 independent random seeds (seeds 0-29) per condition. This provides:

- Sufficient power for Central Limit Theorem application (N≥30 theoretical threshold)
- Statistical power ≥0.85 for detecting variance σ≥0.1%
- Computational feasibility (~6 minutes per condition on H100 GPU)

Total experimental budget: 30 seeds × 2 architectures × 2 datasets = 120 training runs.

## Hypothesis Decomposition: Validating the Causal Chain

Rather than measuring variance end-to-end, we decompose the causal mechanism into testable steps:

```
Step 1: Seed → Independent Weight Configurations
         ↓ [H-M1: Measure pairwise weight distances]

Step 2: Different Initializations → Different Trajectories → Different Minima
         ↓ [H-M2: Track final weight divergence, loss CV]

Step 3: Different Minima → Measurable Variance
         ↓ [H-E1: Measure test accuracy variance σ²]
         ↓ [H-M3: Validate bootstrap stability]
```

### H-E1: Variance Existence (MUST_WORK Gate)

**Hypothesis:** Test accuracy variance σ² is statistically non-zero (p < 0.05) and practically detectable (σ² ≥ 0.3% for ≥2/4 conditions).

**Measurement:**
- Primary metric: Variance σ² = Var(test_accuracies) across 30 seeds
- Statistical test: One-sample variance test (chi-squared, H₀: σ²=0 vs. H₁: σ²>0, α=0.05)
- Practical threshold: Coefficient of variation CV = σ/μ ≥ 0.1%

**Why σ²≥0.3%?** This threshold ensures practical detectability—variance large enough to matter for UQ method calibration. Too-low variance (e.g., σ²=0.0001) would be a pyrrhic technical victory.

### H-M1: Seed Independence (MUST_WORK Gate)

**Hypothesis:** Different random seeds create independent weight configurations (mean pairwise distance > 0, p < 0.05).

**Measurement:**
- Initialize 30 models with seeds 0-29
- Compute pairwise Euclidean distance between all 435 weight pairs: d(wᵢ, wⱼ) = ||wᵢ - wⱼ||₂
- Statistical test: One-sample t-test (H₀: mean_distance=0 vs. H₁: mean_distance>0, α=0.05)

**Why this validates mechanism Step 1:** If seeds produce identical or near-identical initializations, pairwise distances would be near zero. Non-zero distances with p<0.05 confirm PyTorch seed control creates truly independent configurations.

### H-M2: Trajectory Divergence (MUST_WORK Gate)

**Hypothesis:** Different initializations lead to different local minima (final weight distance > initial distance, loss CV ≥ 1%).

**Measurement:**
- Primary: Mean final weight distance across 30 trained models (compare to initial distance from H-M1)
- Secondary: Coefficient of variation of final loss values: CV = σ_loss / μ_loss × 100%

**Why this validates mechanism Step 2:** If all initializations converged to the same global minimum, final weights would be identical (distance→0) and loss CV→0. Persistent divergence confirms non-convex loss landscape with multiple attraction basins.

### H-M3: Bootstrap Stability (SHOULD_WORK Gate)

**Hypothesis:** N=30 provides stable variance estimation (bootstrap 95% CI width ≤ 50% of point estimate).

**Measurement:**
- Bootstrap resample the 30 test accuracies with B=1000 resamples
- Compute variance σ² for each bootstrap sample
- Construct 95% CI: [percentile(2.5), percentile(97.5)]
- Measure relative width: (CI_upper - CI_lower) / σ² × 100%

**Why SHOULD_WORK not MUST_WORK?** This exploratory hypothesis tests whether Rajput et al.'s N≥30 criterion provides estimation *precision* (narrow CIs) in addition to detection power. Failure triggers N sensitivity analysis rather than hypothesis rejection.

## Metrics and Statistical Tests

**Primary metrics:**
- Test accuracy variance: σ² = Σ(xᵢ - μ)² / (n-1) where xᵢ = test accuracy for seed i
- Pairwise weight distance: d(wᵢ, wⱼ) = √(Σ(wᵢ - wⱼ)²) (Euclidean norm)
- Coefficient of variation: CV = σ/μ × 100%
- Bootstrap CI width: (CI_upper - CI_lower) / point_estimate × 100%

**Statistical tests:**
- Variance test: Chi-squared test for σ² > 0
- Independence test: One-sample t-test for mean distance > 0
- Significance level: α = 0.05 (two-tailed where applicable)
- Multiple testing correction: Not applied (4 independent hypotheses testing different mechanisms)

## Intuition: The Causal Story

Figure 2 (variance by condition) shows the core finding visually: Fashion-MNIST exhibits 10× higher variance than MNIST across both architectures. Figure 3 (accuracy distributions) reveals the spread of test accuracies across 30 seeds—Fashion-MNIST shows clear dispersion while MNIST clusters tightly near 98%.

The mechanism unfolds as follows: Each random seed (0-29) draws initial weights from PyTorch's initialization distribution. Under deterministic SGD, these starting points lead to different optimization paths through the non-convex loss landscape. Like balls rolling down a mountainside from slightly different positions, they converge to different valleys (local minima). The variance in test accuracy reflects the distribution of minima quality across the landscape.

Why does task difficulty matter? Easy tasks like MNIST reach ~98% accuracy—only 2% absolute room remains for variance. This ceiling effect compresses variance to ~0.04%. Medium-difficulty tasks like Fashion-MNIST plateau at ~88%—12% absolute room allows variance to reach 0.35-0.59%. The mathematical constraint: if μ=98%, σ²_max≈4%; if μ=88%, σ²_max≈144%.

**Technical depth balance:** We describe the "what" and "why" of each design choice in the main text. Implementation details (exact hyperparameter grids, random seed selection rationale, bootstrap percentile method specifics) appear in the appendix for reproducibility.
