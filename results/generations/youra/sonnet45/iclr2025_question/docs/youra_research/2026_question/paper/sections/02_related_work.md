# Related Work

While recent work advances complex uncertainty quantification methods, foundational variance baselines remain unmeasured. We position our work as complementary infrastructure—providing calibration baselines rather than competing with existing UQ methods.

## Uncertainty Quantification Methods

Modern deep learning employs sophisticated uncertainty estimation techniques including Bayesian neural networks \citep{gal2016dropout}, Monte Carlo Dropout \citep{gal2016dropout}, deep ensembles \citep{lakshminarayanan2017simple}, and evidential deep learning \citep{sensoy2018evidential}. These methods provide predictive uncertainty estimates for model outputs, with applications spanning medical diagnosis, autonomous driving, and scientific discovery.

However, these methods share a fundamental limitation: they lack calibration against a validated baseline from the simplest case—seed-only variance. Without knowing the irreducible variance from weight initialization alone (under full determinism with no stochastic regularization), we cannot distinguish whether an uncertainty estimate reflects genuine model uncertainty or merely captures the natural variance from random initialization. **We measure this irreducible baseline, enabling method calibration.** For example, if MC Dropout reports 0.8% uncertainty on a task where seed-based variance is 0.5%, we know at least 62% of the reported uncertainty comes from initialization alone.

## Reproducibility and Seed Studies

The deep learning community increasingly recognizes random seed effects on model performance. Picard et al. (2021) performed an exhaustive search of 10⁴ random seeds on CIFAR-10 ResNet-18, finding significant seed-dependent variance despite deterministic training and identifying "optimal" seeds with consistently higher accuracy. Their work demonstrated that variance exists even under controlled conditions but required computationally prohibitive exhaustive search (10⁴ seeds) and focused on complex architectures (ResNet-18) rather than establishing simple baselines.

Zhou et al. (2025) studied random seed effects in LLM fine-tuning, identifying macro-level (accuracy) and micro-level (per-sample prediction) variance metrics. Ghasemzadeh et al. (2023) proposed nested k-fold cross-validation to reduce required sample sizes for stable model selection by approximately 50%. While these works acknowledge seed-based variability, none provide validated measurement protocols for simple neural networks.

**We differ by validating the N≥30 criterion from statistical theory in deep learning contexts** and establishing the protocol for simple MLPs (1-2 layers, <500K parameters) before scaling to complex architectures. Unlike Picard et al.'s CIFAR-10 focus, we establish MNIST/Fashion-MNIST baselines with dual-dataset design testing task difficulty sensitivity. Our N=30 protocol is computationally feasible (minutes vs. days) while providing statistical rigor.

## Sample Size Theory for Machine Learning

Rajput and Kumar (2023) provided theoretical guidelines for sample size selection in machine learning experiments, recommending N≥30 for Central Limit Theorem application when effect size ≥0.5 and accuracy ≥80%. Their criterion, validated across 15 ML benchmark datasets, establishes power≥0.85 for detecting meaningful effects. However, their work provided theoretical validation without empirical testing specifically for neural network test accuracy variance estimation.

Our key finding: **we empirically validate this criterion and discover a critical distinction—N=30 sufficient for variance detection (p<0.05) but insufficient for precision (bootstrap CI widths 93-110% vs. 50% threshold)**. This detection-vs-precision boundary refines Rajput et al.'s criterion for deep learning contexts. Where they established sample size for hypothesis testing, we identify different thresholds for detection (N=30) vs. stable quantification (N>50), a distinction missing from prior work but crucial for DL applications.

Sluijterman et al. (2023) studied optimal training of mean-variance estimation networks, focusing on loss function design for uncertainty-aware predictions. Their work assumes variance as a learnable prediction target but does not measure the classical baseline variance we establish.

## Summary and Positioning

Existing work either develops complex UQ methods without baseline calibration, studies seed effects on complex architectures without validated protocols, or provides theoretical sample size guidance without empirical DL validation. **We complement these efforts by providing measurement infrastructure**—the first empirically validated classical variance baseline with complete mechanistic validation, enabling future UQ method calibration and reproducibility benchmarking.
