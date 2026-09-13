# Related Work

Data attribution methods aim to quantify the influence of individual training examples on model behavior. We organize related work into three themes: foundational methods, scalable approximations, and evaluation protocols—highlighting how each advances the field while leaving gaps that our multi-objective analysis addresses.

## Influence Functions and Their Limitations

The modern era of data attribution began with Koh and Liang [2017], who adapted classical influence functions from robust statistics to deep learning. Their approach approximates the effect of removing a training point by computing the inverse Hessian-vector product (iHVP), enabling attribution without expensive retraining. This foundational work demonstrated practical applications including debugging mislabeled examples and understanding model predictions.

However, Basu et al. [2020] revealed that influence functions are "fragile" in deep networks—their accuracy varies dramatically with network depth, width, and regularization strength. This fragility was later connected to the non-convexity of deep learning loss landscapes, where the Hessian approximation quality degrades unpredictably. While this work illuminated *when* influence functions fail, it did not characterize the *trade-offs* between different quality dimensions when methods work but disagree.

Our work builds on this foundation by showing that fragility is a symptom of a deeper phenomenon: structural metric decoupling in non-convex settings. Where Basu et al. characterized failure modes, we characterize the Pareto structure that emerges even when methods produce reasonable results.

## Scalable Attribution Approximations

The computational cost of exact influence functions—requiring Hessian inversion—motivated a wave of efficient approximations. TracIn [Pruthi et al., 2020] bypasses Hessian computation entirely by using gradient similarity across training checkpoints, achieving competitive performance on BERT fine-tuning tasks. TRAK [Park et al., 2023] employs random projections to reduce dimensionality while preserving attribution signal, achieving 0.7-0.9 rank correlation with LOO retraining at orders of magnitude speedup.

More recent work has targeted specific model architectures. DataInf [Kwon et al., 2023] exploits the low-rank structure of LoRA fine-tuning to derive closed-form influence expressions. LoRIF [Li et al., 2026] addresses I/O bottlenecks through low-rank factorization, achieving 20× storage reduction. MAGIC [Ilyas and Engstrom, 2025] combines classical methods with metadifferentiation for near-optimal attribution estimates.

Each of these methods reports improvements on specific metrics and datasets, but direct comparison is complicated by differing evaluation protocols, compute budgets, and quality metrics. Our unified evaluation framework addresses this gap by normalizing computation via gradient-equivalent operations and simultaneously measuring multiple quality dimensions.

## Evaluation Protocols and Benchmarks

Attribution evaluation typically follows one of two paradigms: *correlation with ground truth* or *downstream task performance*. Ground truth approaches compute expensive LOO retraining and measure rank correlation [Koh and Liang, 2017; Park et al., 2023]. Downstream approaches evaluate whether removing top-attributed examples degrades model performance [Feldman and Zhang, 2020].

Nguyen et al. [2023] raised important concerns about evaluation reliability, showing that attribution estimates can be dominated by noise from random initialization and SGD stochasticity rather than genuine training data signal. This work identifies scenarios where attribution is unreliable but does not characterize the multi-objective structure when attribution *is* reliable.

A key limitation of existing evaluation is single-metric focus. Papers typically report one headline number—usually Spearman rank correlation—without characterizing the full quality profile. This obscures potential trade-offs: a method achieving 0.9 rank correlation might have poor magnitude fidelity or high variance. Our multi-objective framework reveals these hidden trade-offs.

## Data Valuation and Shapley Methods

A parallel literature addresses data valuation through game-theoretic approaches. Data Shapley [Ghorbani and Zou, 2019] assigns value to training points based on marginal contribution to model performance. Beta Shapley [Kwon and Zou, 2021] relaxes efficiency axioms for noise reduction. FreeShap [Wang et al., 2024] achieves sign-robust valuation without fine-tuning.

These methods optimize different objectives than gradient-based attribution—typically aggregate contribution rather than example-specific influence—and involve different computational primitives. While our framework focuses on gradient-based methods (TRAK, TracIn, IF, FastIF), the multi-objective lens could extend to Shapley-based approaches in future work.

## Positioning Our Contribution

Prior work has advanced attribution efficiency [Park et al., 2023; Kwon et al., 2023], identified failure modes [Basu et al., 2020], and raised evaluation concerns [Nguyen et al., 2023]. However, no work has systematically characterized the *multi-objective Pareto structure* of attribution quality or connected observed trade-offs to the underlying optimization geometry.

Our contribution is complementary: we do not propose a new attribution method but provide the first rigorous framework for understanding *why* methods disagree and *how* practitioners should select among them. By demonstrating that trade-offs are structural properties of non-convex landscapes—absent in convex settings—we shift the field's focus from "which method is best?" to "which quality dimension matters for this application?"
