# 2. Related Work

Our work addresses the gap between hypothesis generation and resource-constrained validation by introducing viability gates—a systematic early-stop protocol missing from traditional ML research workflows. We position our framework relative to three existing approaches: ablation studies, complexity analysis, and early stopping methods.

## 2.1 Ablation Studies and Hypothesis Testing

Ablation studies are ubiquitous in ML research for testing hypothesis variations. A researcher might compare attention mechanisms with 1, 4, 8, or 16 heads to identify optimal configurations. These studies answer the question "which variant performs best?" rather than "should we pursue this approach at all?" The distinction is fundamental: ablation studies assume hypothesis viability and optimize within that space, while viability gates assess feasibility before committing to full implementation.

The ablation study literature provides no formalized early-stop decision protocol. Researchers typically discover computational infeasibility post-hoc—after implementing all variants and measuring overhead across full-scale experiments. Our layer-wise logit extraction example (68.65% overhead) illustrates this pattern: the approach was technically successful but computationally infeasible for deployment, a constraint discoverable at micro-pilot scale.

## 2.2 Computational Complexity Analysis

Big-O notation provides theoretical bounds on algorithmic scaling (O(n), O(n²), O(n log n)). While invaluable for asymptotic analysis, Big-O misses constant factors and implementation details that dominate real-world performance. An O(n) algorithm with a 68.65% overhead constant may be less practical than an O(n log n) algorithm with 5% overhead for deployment-constrained scenarios.

Complexity analysis also assumes idealized conditions—infinite memory, uniform data access patterns, negligible cache effects. Real implementations encounter memory bottlenecks, I/O overhead, and hardware-specific factors that theoretical analysis cannot capture. Empirical profiling addresses this gap by measuring actual overhead on target hardware, but current practice applies profiling post-implementation rather than at micro-pilot design stages.

## 2.3 Early Stopping and Resource Efficiency

Early stopping literature primarily addresses training convergence: halt optimization when validation loss plateaus rather than continuing to a fixed epoch count. This paradigm optimizes hyperparameters (learning rate, batch size) to maximize accuracy while minimizing training cost.

Our framework applies early stopping to a different objective: viability assessment rather than accuracy optimization. The decision is binary (stop/continue based on threshold comparison) rather than continuous (find optimal hyperparameter value). The target is computational overhead rather than validation loss. While both paradigms share the "fail-fast" principle, they address orthogonal problems: hyperparameter search assumes hypothesis viability and optimizes within constraints, while viability gates assess whether constraints can be met at all.

## 2.4 Bayesian Optimization and Sequential Experimentation

Bayesian optimization uses Gaussian processes to model expensive objective functions and sequentially select query points that balance exploration and exploitation. The framework has proven effective for hyperparameter tuning where each evaluation (training run) is costly.

Our Bayesian update mechanism shares the sequential refinement principle but differs in application domain. Bayesian optimization maximizes an unknown function (find best hyperparameters). Our framework predicts a known-in-principle quantity (full-scale overhead) from limited observations (micro-pilot measurements). The posterior refinement reduces prediction uncertainty rather than identifying optima. The gate structure (10 → 100 → full samples) provides natural checkpoints for Bayesian updates, with each stage offering incrementally refined viability predictions.

## 2.5 Our Position

Pilot-Driven Viability Gates fills a methodological gap at the intersection of ablation studies (systematic variation testing), complexity analysis (scalability assessment), and early stopping (fail-fast principles). We formalize a viability assessment protocol that:

1. **Precedes resource commitment**: Viability decisions occur at micro-pilot stage (<1 hour, 10 samples) before days of full implementation.

2. **Uses empirical measurement**: Overhead profiling captures constant factors, hardware specifics, and implementation details missed by Big-O analysis.

3. **Enables incremental refinement**: Bayesian updates combine micro-pilot priors with 100-sample likelihoods to reduce prediction uncertainty.

4. **Provides decision criteria**: Binary stop/continue decisions based on threshold comparison (O_pred > T) with quantified confidence intervals.

While our validation uses synthetic data (establishing proof-of-concept), the framework design addresses a real methodological need: systematic early identification of computationally infeasible hypotheses before wasting research resources.
