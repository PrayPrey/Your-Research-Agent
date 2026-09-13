# Related Work

Our work connects three research threads: multi-dimensional trustworthiness evaluation, calibration and uncertainty quantification, and latent factor analysis in machine learning. We show how each thread addresses part of the problem while leaving the cross-dimensional correlation structure unexplored.

## Multi-Dimensional Trustworthiness Evaluation

Recent frameworks conceptualize LLM trustworthiness as a multi-faceted construct. Zhou et al. (2024) propose the Trust-RAG Compass with six dimensions: factuality, robustness, fairness, transparency, accountability, and privacy. This framework provides conceptual clarity but does not investigate cross-dimensional relationships. Similarly, TrustLLM (Sun et al., 2024) evaluates models across multiple trust dimensions without analyzing whether performance on one predicts performance on others.

Benchmark suites like HELM (Liang et al., 2023) and the Open LLM Leaderboard (Beeching et al., 2023) report multi-benchmark scores, implicitly treating dimensions as independent. Our analysis of 4,561 models from these leaderboards reveals that this independence assumption may be violated: cross-benchmark correlations of ρ = 0.80–0.87 suggest substantial shared variance.

The assumption of dimensional independence has practical consequences. Evaluation pipelines run separate benchmark batteries, practitioners prioritize dimensions independently, and training objectives target specific capabilities. If a latent factor underlies trustworthiness, this approach may be inefficient—improving the factor could boost all dimensions simultaneously.

## Calibration and Representation Stability

A parallel research thread connects model confidence to trustworthiness through calibration. Well-calibrated models express confidence that matches their accuracy, a property linked to reliability and truthfulness.

Khanmohammadi et al. (2025) introduce CCPS (Calibrating via Perturbed Stability), achieving 55% ECE reduction by leveraging internal representation stability. Their key insight—that perturbation-stable representations yield better calibration—aligns with our mechanism hypothesis. However, CCPS studies single-dimension calibration without examining cross-benchmark effects.

Liu et al. (2025) survey uncertainty quantification methods, taxonomizing approaches into input, reasoning, parameter, and prediction uncertainty. This comprehensive framework stops short of connecting uncertainty to multi-dimensional trustworthiness.

Our work extends this thread by hypothesizing that representation stability underlies not just calibration but the entire cross-benchmark correlation structure. The Behavioral Stability Index (BSI) we construct operationalizes stability through paraphrase consistency, connecting internal representations to observable behavior.

## Latent Factor Analysis in ML Evaluation

The idea that seemingly distinct capabilities share a common factor has precedent in both psychology and machine learning. In psychometrics, Spearman's g-factor explains positive correlations across cognitive tests. Recent work asks whether similar structure exists in LLM capabilities.

Schumacher et al. (2024) analyze benchmark correlation structure, finding that model scale explains substantial shared variance. Our work extends their analysis by residualizing on scale and training recency before extracting latent factors, revealing structure beyond what scale alone explains.

Ensemble and routing approaches implicitly leverage capability covariance. ZOOTER (Lu et al., 2023) uses reward-guided routing to select among models, achieving 44% task-level wins. PickLLM (Sikeridis et al., 2024) applies RL-based routing for cost-accuracy tradeoffs. These approaches benefit from—but do not explain—the capability correlation structure.

## Our Contribution

Unlike prior work, we directly model the cross-benchmark correlation structure through factor analysis with explicit confound control. We connect the resulting latent factor (GRC) to a behavioral mechanism (representation stability) and provide quasi-intervention evidence through instruction-tuning analysis. This positions GRC not as a post-hoc observation but as a theoretically grounded construct with implications for evaluation and training.
