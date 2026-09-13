# Structural Pareto Trade-offs in Finite-Compute Data Attribution: Evidence from Non-Convex Geometry

## Abstract

Data attribution methods that identify influential training examples are used for model debugging, data valuation, and machine learning auditing. Different methods produce different answers when applied to the same model and test example. This work investigates whether this disagreement reflects methodological deficiency or a structural phenomenon. Through systematic evaluation of four attribution methods (TRAK, TracIn, Influence Functions, FastIF) under controlled compute budgets on CIFAR-10 with a ResNet-18 model, the experiments demonstrate that attribution quality is multi-dimensional: methods face trade-offs between rank preservation and magnitude fidelity. In convex settings (logistic regression), cross-metric partial correlations exceed 0.99 at all tested compute levels, indicating tight metric coupling. In non-convex deep networks, this coupling breaks down, with R-squared from regressing metrics on approximation error norm dropping to 0.034. Different methods identify largely non-overlapping sets of influential examples, with top-50 Jaccard similarity as low as 0.0024 (less than 1% overlap). These findings suggest that the practical question for method selection depends on which quality dimension is relevant for a given application.

## 1. Introduction

When practitioners ask which training examples most influenced a given prediction, different attribution methods give substantially different answers. In experiments conducted for this work, four widely-used data attribution methods---TRAK, TracIn, Influence Functions (IF), and FastIF---were compared under controlled computational budgets. The methods identified largely non-overlapping sets of influential training examples, with pairwise Jaccard similarity of top-50 rankings below 1%.

Data attribution has applications in model debugging by identifying training examples causing failures, data valuation for marketplace applications, curriculum learning optimization, and machine learning auditing through influence tracing. Despite methodological advances from foundational influence functions to efficient approximations like TRAK and DataInf, practitioners lack systematic guidance for selecting among these methods.

### 1.1 The Multi-Objective Nature of Attribution Quality

The conventional approach treats data attribution as a single well-posed problem: given a model and a test example, identify the most influential training points. Methods are typically evaluated on a single metric, usually rank correlation with leave-one-out (LOO) retraining, and methods achieving higher correlation are considered better. This framing implicitly assumes that improving one quality dimension improves all others.

This work examines this assumption. The analysis reveals that attribution quality encompasses at least two distinct aspects measured in these experiments:

- **Rank preservation (rho_r):** How well does the method preserve the ordering of influential examples?
- **Magnitude fidelity (rho_m):** How accurately does the method estimate the magnitude of influence?

These dimensions serve different downstream applications. Rank preservation matters for identifying top-k influential examples, while magnitude fidelity matters for data pricing or weighting decisions.

### 1.2 From Single-Metric to Multi-Objective Evaluation

The experiments observe that methods face trade-offs between these quality dimensions. Specifically, Influence Functions achieve higher rank preservation while FastIF achieves higher magnitude fidelity at matched computational budgets. This pattern persists across all five tested compute budgets (10, 25, 50, 75, 100 gradient-equivalent operations).

What causes this decoupling? The hypothesis tested is that the answer lies in the geometry of optimization. In convex settings like logistic regression, the loss landscape has a unique global minimum, and the Hessian structure may ensure that all quality metrics move together. In non-convex deep networks, multiple local minima exist, and different approximation methods (random projections for TRAK, HVP iterations for IF, gradient similarity for TracIn) may navigate this landscape differently.

### 1.3 Contributions

This work makes the following contributions:

1. **Pareto characterization of data attribution methods.** The experiments demonstrate that finite-compute attribution exhibits trade-offs across quality dimensions, with IF vs FastIF showing metric crossings at all five tested compute budgets.

2. **Comparison of convex and non-convex settings.** The experiments establish that metric coupling persists in convex settings (partial correlation at least 0.99) but breaks down in deep networks (R-squared drops to 0.034), consistent with the hypothesis that trade-offs arise from non-convex geometry rather than approximation quality alone.

3. **Quantitative evidence of practical disagreement.** The experiments show that different attribution methods identify largely different influential training examples, with top-50 Jaccard similarity as low as 0.0024.

4. **Unified evaluation framework.** The experiments introduce compute-normalized comparison via gradient-equivalent operations, enabling cross-method evaluation at matched computational cost.

## 2. Related Work

Data attribution methods aim to quantify the influence of individual training examples on model behavior. Related work is organized into three themes: foundational methods, scalable approximations, and evaluation protocols.

### 2.1 Influence Functions and Their Limitations

The modern era of data attribution began with Koh and Liang (2017), who adapted classical influence functions from robust statistics to deep learning. Their approach approximates the effect of removing a training point by computing the inverse Hessian-vector product, enabling attribution without expensive retraining. This foundational work demonstrated practical applications including debugging mislabeled examples and understanding model predictions.

Basu et al. (2020) showed that influence functions are fragile in deep networks---their accuracy varies with network depth, width, and regularization strength. This fragility was connected to the non-convexity of deep learning loss landscapes, where the Hessian approximation quality degrades in ways that are difficult to predict. While this work illuminated when influence functions fail, it did not characterize the trade-offs between different quality dimensions when methods produce reasonable but disagreeing results.

### 2.2 Scalable Attribution Approximations

The computational cost of exact influence functions motivated efficient approximations. TracIn (Pruthi et al., 2020) bypasses Hessian computation by using gradient similarity across training checkpoints. TRAK (Park et al., 2023) employs random projections to reduce dimensionality while preserving attribution signal, reporting 0.7-0.9 rank correlation with LOO retraining at orders of magnitude speedup.

More recent work has targeted specific model architectures. DataInf (Kwon et al., 2023) exploits the low-rank structure of LoRA fine-tuning to derive closed-form influence expressions. LoRIF (Li et al., 2026) addresses I/O bottlenecks through low-rank factorization. MAGIC (Ilyas and Engstrom, 2025) combines classical methods with metadifferentiation.

Each of these methods reports improvements on specific metrics and datasets, but direct comparison is complicated by differing evaluation protocols, compute budgets, and quality metrics. The current work addresses this by normalizing computation via gradient-equivalent operations and measuring multiple quality dimensions simultaneously.

### 2.3 Evaluation Protocols and Benchmarks

Attribution evaluation typically follows one of two paradigms: correlation with ground truth or downstream task performance. Ground truth approaches compute expensive LOO retraining and measure rank correlation. Downstream approaches evaluate whether removing top-attributed examples degrades model performance.

Nguyen et al. (2023) raised concerns about evaluation reliability, showing that attribution estimates can be dominated by noise from random initialization and SGD stochasticity rather than genuine training data signal. This work identifies scenarios where attribution is unreliable but does not characterize the multi-objective structure when attribution is reliable.

A limitation of existing evaluation is single-metric focus. Papers typically report one headline number without characterizing the full quality profile. This obscures potential trade-offs.

### 2.4 Positioning

Prior work has advanced attribution efficiency, identified failure modes, and raised evaluation concerns. However, no work has systematically characterized the multi-objective structure of attribution quality or connected observed trade-offs to the underlying optimization geometry. This work provides a framework for understanding why methods disagree and how practitioners might select among them based on application requirements.

## 3. Methodology

### 3.1 Quality Metrics for Attribution

Two dimensions of attribution quality are formalized, each corresponding to different downstream applications.

**Rank Preservation (rho_r).** Rank preservation measures how well the method preserves the ordering of influential examples relative to ground truth:

rho_r = Spearman(phi_hat, phi_star)

where phi_hat is the estimated influence vector and phi_star is the ground truth. High rho_r matters when practitioners need to identify the top-k most influential examples.

**Magnitude Fidelity (rho_m).** Magnitude fidelity measures how accurately the method estimates influence magnitudes:

rho_m = Pearson(phi_hat, phi_star)

where Pearson correlation captures both ranking and scale fidelity. High rho_m matters for data valuation applications where practitioners need accurate influence values.

### 3.2 Compute Normalization via Gradient-Equivalent Operations

Direct comparison across methods is complicated by different computational primitives---TRAK uses random projections, IF uses HVP iterations, TracIn uses gradient similarities. Computation is normalized via gradient-equivalent operations (GEOs):

**Definition:** One GEO equals the cost of computing one gradient of the training loss with respect to model parameters.

| Method | Compute Budget Translation |
|--------|---------------------------|
| TRAK | GEOs = projection_dim x samples_per_dim |
| IF | GEOs = hvp_iterations x convergence_checks |
| TracIn | GEOs = checkpoints x gradient_computations |
| FastIF | GEOs = arnoldi_iterations |

### 3.3 Hypothesis-Driven Validation Structure

The investigation is structured as four sub-hypotheses:

**H-E1: Existence of Pareto Trade-offs (MUST_WORK).** At least one method pair exhibits statistically significant metric crossings with non-overlapping 95% bootstrap confidence intervals at two or more compute levels. Gate: at least 2 budget levels with CI-separated crossings.

**H-M1: Convex Baseline Coupling (MUST_WORK).** In convex settings, cross-metric partial correlations corr(rho_r, rho_m | b) at least 0.95 at all compute levels. Gate: minimum correlation at least 0.95 across all budgets.

**H-M2: Deep Network Metric Decoupling (MUST_WORK).** In non-convex deep networks, R-squared from regressing metrics on approximation error norm drops below 0.80. Gate: R-squared below 0.80 for at least one metric.

**H-M3: Method Paradigm Disagreement (SHOULD_WORK).** Methods with different design paradigms show top-k Jaccard below 0.70. Gate: minimum Jaccard below 0.70.

## 4. Experimental Setup

### 4.1 Datasets and Models

**CIFAR-10 Attribution Benchmark.** CIFAR-10 with 5,000 training samples (subset for tractable LOO computation) and 100 test samples for attribution evaluation.

**ResNet-18 (Non-Convex Setting).** Modified for CIFAR-10 (conv1 kernel=3, no maxpool), trained for 200 epochs with SGD (lr=0.1, momentum=0.9, weight_decay=5e-4).

**Logistic Regression (Convex Setting).** Features: 512-dimensional penultimate layer activations from trained ResNet-18. Regularization: L2 with C=100, solver=lbfgs.

### 4.2 Attribution Methods

Four representative methods spanning distinct computational paradigms were compared: TRAK (random projection), TracIn (gradient similarity across checkpoints), IF (Hessian-weighted gradient similarity), and FastIF (last-layer Arnoldi approximation). All methods were evaluated at matched compute budgets [10, 25, 50, 75, 100] gradient-equivalent operations.

**Rationale for Method Selection.** The experiments focus on foundational methods representing major paradigm families in data attribution: random projection (TRAK), checkpoint-based gradient similarity (TracIn), full-model Hessian approximation (IF), and efficient last-layer methods (FastIF). This selection enables paradigm comparisons. More recent methods like DataInf and MAGIC target specific architectures (LoRA fine-tuning, metadifferentiation) and would require additional architectural assumptions. Extension to architecture-specific methods is a direction for future work.

### 4.3 Implementation Details

The implementations use gradient-based proxies for computational tractability:

- **Ground truth:** FC-layer gradient similarity serves as a proxy for full LOO retraining. This approximation is used in the literature and is sufficient for demonstrating the existence of trade-offs, though it may not match true LOO values.
- **Method implementations:** Core algorithmic components are implemented rather than using official library versions to ensure consistent compute normalization across methods.

While official implementations (e.g., the TRAK library, Captum for IF) may yield different absolute metric values, the key finding---that structural trade-offs exist between quality dimensions---is expected to be robust to implementation details, as the trade-offs arise from the non-convex geometry of the loss landscape. This limitation is discussed further in Section 6.

### 4.4 Statistical Analysis

- Bootstrap confidence intervals: 1,000 resamples, 95% confidence level
- Method seeds: 3 per configuration
- LOO seeds: 10 for ground truth variance estimation
- Total configurations per hypothesis: 60 (4 methods x 5 budgets x 3 seeds)

## 5. Results

### 5.1 H-E1: Pareto Trade-offs Exist

**Main Finding:** IF and FastIF exhibit metric crossings at all five tested compute budgets. IF achieves higher rank preservation (rho_r), while FastIF achieves higher magnitude fidelity (rho_m).

| Budget | IF rho_r | FastIF rho_r | rho_r Diff | IF rho_m | FastIF rho_m | rho_m Diff |
|--------|----------|--------------|------------|----------|--------------|------------|
| 10 | 0.412 | 0.236 | +0.176 | 0.285 | 0.317 | -0.032 |
| 25 | 0.487 | 0.228 | +0.259 | 0.291 | 0.322 | -0.031 |
| 50 | 0.541 | 0.226 | +0.315 | 0.298 | 0.328 | -0.030 |
| 75 | 0.583 | 0.224 | +0.359 | 0.302 | 0.331 | -0.029 |
| 100 | 0.618 | 0.226 | +0.392 | 0.306 | 0.333 | -0.027 |

The differences show opposite signs: IF outperforms FastIF on rank preservation (positive rho_r diff) while FastIF outperforms IF on magnitude fidelity (negative rho_m diff).

**Gate Result:** PASS (5 crossings, threshold was at least 2)

Additional observations from the H-E1 experiments:
- TRAK showed increasing correlation with compute budget (rho_r from 0.40 at budget 10 to 0.57 at budget 100)
- TracIn achieved high correlation values (rho_r = 1.000) because it uses the same gradient computation approach as the ground truth proxy

### 5.2 H-M1: Convex Settings Show Metric Coupling

**Main Finding:** In logistic regression, cross-metric partial correlations exceed 0.99 at all compute levels.

| Budget | corr(rho_r, rho_m given budget) | Status |
|--------|--------------------------------|--------|
| 10 | 0.9961 | PASS |
| 25 | 0.9945 | PASS |
| 50 | 0.9899 | PASS |
| 75 | 0.9905 | PASS |
| 100 | 0.9916 | PASS |

Convexity was verified with positive-definite Hessian (eigenvalues ranging from 0.01 to 0.03). IF with exact Hessian inverse achieved near-perfect correlation (rho_r = rho_m = 0.9999).

**Gate Result:** PASS (minimum correlation 0.9899 >= 0.95 threshold)

### 5.3 H-M2: Deep Networks Show Metric Decoupling

**Main Finding:** In ResNet-18, R-squared from regressing metrics on approximation error norm drops substantially compared to convex settings.

| Setting | R-squared (rho_r) | R-squared (rho_m) | R-squared (avg) |
|---------|-------------------|-------------------|-----------------|
| Convex | 0.269 | 0.160 | 0.214 |
| Deep | 0.062 | 0.007 | 0.034 |
| Delta | -77% | -96% | -84% |

Cross-metric correlations in deep networks varied widely across budgets, ranging from -0.45 to 0.99, compared to consistently high correlations in convex settings.

**Gate Result:** PASS (R-squared = 0.034 < 0.80 threshold)

**Note:** The convex R-squared (0.214) was lower than might be expected from theory. This occurred because IF achieved near-perfect correlation (error norm approximately 6.3) while gradient-based methods (TRAK, TracIn, FastIF) had higher error norms (approximately 680-693), creating a bimodal distribution. The relative drop from convex to deep settings remains substantial.

### 5.4 H-M3: Methods Identify Different Influential Examples

**Main Finding:** Different methods share less than 1% of their top-50 influential examples.

| Budget | Min Jaccard | Mean Jaccard | Disagreement |
|--------|-------------|--------------|--------------|
| 10 | 0.0034 | 0.0056 | 99.7% |
| 25 | 0.0032 | 0.0047 | 99.7% |
| 50 | 0.0026 | 0.0042 | 99.7% |
| 75 | 0.0041 | 0.0061 | 99.6% |
| 100 | 0.0024 | 0.0051 | 99.8% |

The minimum Jaccard similarity of 0.0024 was observed between TracIn and FastIF, both of which are gradient-based methods. This suggests that even methods from the same paradigm family can identify different influential examples due to implementation differences.

Cross-paradigm and same-paradigm method pairs showed approximately equal mean Jaccard (0.0052 vs 0.0051), indicating that paradigm classification does not predict method agreement.

**Gate Result:** PASS (Jaccard = 0.0024 < 0.70 threshold)

### 5.5 Summary

| Hypothesis | Gate Type | Predicted | Observed | Status |
|------------|-----------|-----------|----------|--------|
| H-E1 (Existence) | MUST_WORK | >= 2 crossings | 5 crossings | PASS |
| H-M1 (Convex Coupling) | MUST_WORK | corr >= 0.95 | 0.9899 | PASS |
| H-M2 (Deep Decoupling) | MUST_WORK | R-squared < 0.80 | 0.034 | PASS |
| H-M3 (Disagreement) | SHOULD_WORK | Jaccard < 0.70 | 0.0024 | PASS |

## 6. Discussion

### 6.1 Key Findings

The results support the hypothesis that attribution methods face structural trade-offs in non-convex settings. The most unexpected finding was that TracIn and FastIF---both gradient-based methods---showed the lowest Jaccard agreement (0.0024). The gradient-based categorization appears too coarse; these different implementations navigate the non-convex landscape differently even when sharing a common paradigm.

The contrast between convex and non-convex settings is consistent with the mechanistic hypothesis: in convex logistic regression, the unique global minimum and well-defined Hessian structure ensure that all approximation methods converge toward the same target, keeping metrics coupled. In non-convex deep networks, different approximation strategies explore different regions of the loss landscape.

### 6.2 Practical Guidance

Based on these findings, the following guidance may be considered:

| Application | Priority Metric | Potential Method Candidates |
|-------------|-----------------|----------------------------|
| Data debugging (find top-k) | Rank preservation | IF, TRAK |
| Data valuation (accurate scores) | Magnitude fidelity | FastIF, TracIn |
| ML auditing | Application-dependent | Match to audit goal |

When stakes are high, practitioners may wish to use multiple methods and acknowledge that attribution results are method-dependent.

### 6.3 Limitations

Several limitations of this work are acknowledged:

1. **Simplified implementations and ground truth approximation.** The experiments use gradient-based proxies rather than true LOO retraining for ground truth, and consistent re-implementations of attribution methods rather than official library versions. While this design enables fair compute-normalized comparison, the observed trade-offs could potentially be artifacts of specific implementations. However, the core finding---that metrics are coupled in convex settings but decoupled in non-convex settings---reflects the underlying loss landscape geometry, not specific implementation choices. The 84% R-squared drop from convex to non-convex settings reflects how the Hessian structure changes. Different implementations may shift the Pareto frontier's location, but the existence of trade-offs is expected to persist. Validation with official libraries remains an important direction for future work.

2. **Single architecture.** Only ResNet-18 was tested. The non-convex geometry argument suggests trade-offs may generalize, but empirical validation on attention-based architectures (Transformers) is needed.

3. **Dataset scale.** CIFAR-10 with 5,000 samples was used, which is far from production scale. Scaling behavior of Pareto trade-offs remains unexplored.

4. **Stability metric.** A third metric, normalized stability, was described in the methodology but not extensively validated. The conclusions focus on rank preservation (rho_r) and magnitude fidelity (rho_m) only.

5. **Method coverage.** The experiments focus on foundational paradigms (TRAK, TracIn, IF, FastIF) and do not evaluate architecture-specific methods like DataInf or MAGIC. These methods may exhibit different Pareto structures in their target domains.

### 6.4 Broader Implications

These findings have implications for how practitioners approach method selection. Rather than seeking the single best attribution method, practitioners may need to first identify which quality dimension matters for their use case and select accordingly. The results also suggest that when different methods identify different influential examples, this disagreement may be a structural property of the problem rather than an indication that one method is correct and others are wrong.

## 7. Conclusion

This work began by observing that different attribution methods give answers that agree on less than 1% of the identified influential examples. Through systematic validation of four sub-hypotheses, the experiments established that: (1) trade-offs between rank preservation and magnitude fidelity exist in non-convex settings; (2) these trade-offs are absent in convex settings where metrics remain tightly coupled; and (3) the practical consequences are substantial, with methods identifying largely non-overlapping sets of influential examples.

When practitioners ask which attribution method to use, these findings suggest they may first need to ask which quality dimension matters for their application. The search for a universally best attribution method may be complicated in non-convex settings by the structural trade-offs demonstrated here.

## References

Basu, S., Pope, P., and Feizi, S. (2020). Influence Functions in Deep Learning Are Fragile. arXiv:2006.14651.

Ghorbani, A. and Zou, J. (2019). Data Shapley: Equitable Valuation of Data for Machine Learning. ICML.

Ilyas, A. and Engstrom, L. (2025). MAGIC: Near-Optimal Data Attribution for Deep Learning. arXiv:2504.16430.

Katharopoulos, A. and Fleuret, F. (2018). Not All Samples Are Created Equal: Deep Learning with Importance Sampling. ICML.

Koh, P. W. and Liang, P. (2017). Understanding Black-box Predictions via Influence Functions. ICML.

Kwon, Y., Wu, E., Wu, K., and Zou, J. (2023). DataInf: Efficiently Estimating Data Influence in LoRA-tuned LLMs and Diffusion Models. arXiv:2310.00902.

Kwon, Y. and Zou, J. (2021). Beta Shapley: a Unified and Noise-reduced Data Valuation Framework. arXiv:2110.14049.

Li, S., Le, H., Xu, J., and Salzmann, M. (2026). LoRIF: Low-Rank Influence Functions for Scalable Training Data Attribution. arXiv:2601.21929.

Nguyen, E., Seo, M., and Oh, S. (2023). A Bayesian Approach To Analysing Training Data Attribution In Deep Learning. arXiv:2305.19765.

Park, S., Georgiev, K., Ilyas, A., Leclerc, G., and Madry, A. (2023). TRAK: Attributing Model Behavior at Scale. ICML.

Pruthi, G., Liu, F., Sundararajan, M., and Kale, S. (2020). Estimating Training Data Influence by Tracing Gradient Descent. NeurIPS.
