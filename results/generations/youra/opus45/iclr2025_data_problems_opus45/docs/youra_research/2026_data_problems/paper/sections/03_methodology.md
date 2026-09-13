# Methodology

Building on our observation that attribution methods may optimize fundamentally different quality dimensions, we design a unified evaluation framework that enables rigorous Pareto characterization. This section presents our quality metrics, compute normalization approach, and the four-hypothesis validation structure.

## Quality Metrics for Attribution

We formalize three dimensions of attribution quality, each corresponding to different downstream applications.

### Rank Preservation ($\rho_r$)

Rank preservation measures how well the method preserves the ordering of influential examples relative to ground truth:

$$\rho_r = \text{Spearman}(\hat{\phi}, \phi^*)$$

where $\hat{\phi}$ is the estimated influence vector and $\phi^*$ is the ground truth from LOO retraining. High $\rho_r$ matters when practitioners need to identify the "top-k" most influential examples—for data debugging, curriculum learning, or auditing.

**Rationale:** Many applications care about relative ranking (which examples are *most* influential) rather than exact influence magnitudes. A method achieving $\rho_r = 0.9$ but $\rho_m = 0.5$ may be perfectly suitable for top-k selection.

### Magnitude Fidelity ($\rho_m$)

Magnitude fidelity measures how accurately the method estimates influence magnitudes:

$$\rho_m = \text{Pearson}(\hat{\phi}, \phi^*)$$

where Pearson correlation captures both ranking and scale fidelity. High $\rho_m$ matters for data valuation applications where practitioners need accurate influence *values*—not just rankings—for pricing or weighting decisions.

**Rationale:** Data marketplace applications require knowing *how much* an example contributed, not just *whether* it contributed more than another. Magnitude fidelity captures this requirement.

### Normalized Stability ($S$)

Normalized stability measures estimation consistency across random seeds:

$$S = \frac{\text{Var}_{\text{runs}}(\hat{\phi})}{\sigma^2_{\text{LOO}}}$$

where $\sigma^2_{\text{LOO}}$ is the inherent variance from LOO retraining stochasticity. Values $S \approx 1$ indicate the method's variance matches target stochasticity; $S \gg 1$ indicates the method inflates variance beyond what the target warrants.

**Rationale:** Reproducible auditing requires consistent estimates—high variance undermines trust even if mean estimates are accurate.

## Compute Normalization via Gradient-Equivalent Operations

Direct comparison across methods is complicated by different computational primitives—TRAK uses random projections, IF uses HVP iterations, TracIn uses gradient similarities. We normalize computation via *gradient-equivalent operations* (GEOs):

**Definition:** One GEO equals the cost of computing one gradient of the training loss with respect to model parameters.

| Method | Compute Budget Translation |
|--------|---------------------------|
| TRAK | GEOs = projection_dim × samples_per_dim |
| IF | GEOs = hvp_iterations × convergence_checks |
| TracIn | GEOs = checkpoints × gradient_computations |
| FastIF | GEOs = arnoldi_iterations |

**Rationale:** GEO normalization enables fair comparison: at budget $b = 50$, all methods have equivalent computational resources regardless of their internal algorithms. This reveals true efficiency differences rather than implementation artifacts.

## Hypothesis-Driven Validation Structure

We structure our investigation as four sub-hypotheses forming a logical chain:

### H-E1: Existence of Pareto Trade-offs (MUST_WORK)

**Claim:** At least one method pair exhibits statistically significant metric crossings (Method A > B on $\rho_r$ but A < B on $\rho_m$) with non-overlapping 95% bootstrap CIs at two or more compute levels.

**Test:** Compare all method pairs on ResNet-18/CIFAR-10 across budgets [10, 25, 50, 75, 100].

**Gate:** $\geq 2$ budget levels with CI-separated crossings.

### H-M1: Convex Baseline Coupling (MUST_WORK)

**Claim:** In convex settings (logistic regression), cross-metric partial correlations $\text{corr}(\rho_r, \rho_m | b) \geq 0.95$ at all compute levels.

**Test:** Train logistic regression on ResNet-18 features; compute metrics under compute-throttled approximations.

**Gate:** Minimum correlation $\geq 0.95$ across all budgets.

**Rationale:** This establishes the baseline—convex geometry *should* couple metrics. If coupling fails even here, our metrics are definitionally inconsistent.

### H-M2: Deep Network Metric Decoupling (MUST_WORK)

**Claim:** In non-convex deep networks, $R^2$ from regressing metrics on approximation error norm $\|\hat{\phi} - \phi^*\|_2$ drops from $\sim 1.0$ (convex) to $< 0.80$ (deep).

**Test:** Fit linear regression of each metric on error norm; compare $R^2$ across regimes.

**Gate:** $R^2_{\text{deep}} < 0.80$ for at least one metric.

**Rationale:** If a single error axis explains all metrics in deep networks (high $R^2$), then trade-offs are merely approximation quality differences. Low $R^2$ proves structural decoupling.

### H-M3: Method Paradigm Disagreement (SHOULD_WORK)

**Claim:** Methods with different design paradigms show top-k Jaccard $< 0.70$ (>30% disagreement on influential examples).

**Test:** Compute Jaccard similarity of top-50 influential examples across all method pairs.

**Gate:** $\min(\text{Jaccard}) < 0.70$.

**Rationale:** Structural trade-offs should manifest as practical disagreement—methods identifying different examples. This connects theoretical Pareto structure to practitioner-relevant consequences.

## Ground Truth Estimation

Ground truth influence is computed via leave-one-out (LOO) retraining:

$$\phi^*_i = f(x_{\text{test}}; \theta^{(-i)}) - f(x_{\text{test}}; \theta)$$

where $\theta^{(-i)}$ is the model trained without example $i$. Due to training stochasticity, we estimate $\phi^*$ over $R = 10$ random seeds:

$$\hat{\phi}^*_i = \mathbb{E}_{\xi}[\phi^*_i(\xi)]$$

where $\xi$ captures random initialization and SGD noise. The variance $\sigma^2_{\text{LOO}} = \text{Var}_{\xi}[\phi^*_i]$ quantifies inherent target stochasticity.

**Computational Note:** Full LOO retraining (5000 examples × 10 seeds = 50,000 training runs) is computationally intensive. We use 100 test examples and cache gradient computations to make experiments tractable.

## Statistical Analysis

### Bootstrap Confidence Intervals

For each metric comparison, we compute 95% bootstrap CIs over 1000 resamples. Metric crossings are declared CI-separated if confidence intervals for the difference do not overlap zero.

### Partial Correlation

To test metric coupling while controlling for compute budget:

$$\text{corr}(\rho_r, \rho_m | b) = \frac{\text{corr}(\rho_r, \rho_m) - \text{corr}(\rho_r, b) \cdot \text{corr}(\rho_m, b)}{\sqrt{(1 - \text{corr}^2(\rho_r, b))(1 - \text{corr}^2(\rho_m, b))}}$$

### $R^2$ Regression

To test whether a single error axis explains metric variation:

$$\rho_k = \beta_0 + \beta_1 \|\hat{\phi} - \phi^*\|_2 + \epsilon$$

$R^2$ measures the fraction of metric variance explained by approximation error norm.

## Implementation Details

All experiments use PyTorch with the following configurations:

- **CIFAR-10:** 5,000 training samples (subset), 100 test samples for attribution
- **ResNet-18:** Modified for CIFAR-10 (smaller initial conv), trained 200 epochs
- **Training:** SGD with lr=0.1, momentum=0.9, weight_decay=5e-4
- **Methods:** Implemented following dattri library conventions
- **Seeds:** 3 method seeds per configuration, 10 LOO seeds for ground truth

Code and data will be released upon publication.
