# Related Work

## Multi-Dimensional Trustworthiness Evaluation

The landscape of LLM trustworthiness evaluation has evolved from single-dimension benchmarks to multi-dimensional frameworks, yet systematic correlation analysis remains unexplored.

**TrustVis** (2025) introduces a unified evaluation framework measuring safety and robustness together using adversarial perturbations on the DNA and ALERT datasets. While TrustVis enables multi-dimensional evaluation, it performs sequential assessment with adversarial modification between dimensions, making correlations reflect perturbation effects rather than inherent dimensional coupling. Our work differs by measuring dimensions on the *same* natural inputs without perturbation, isolating genuine correlations from evaluation artifacts.

**MLLMGuard** (2024) reports multi-dimensional safety scores across five dimensions (Privacy, Bias, Toxicity, Truthfulness, Legality) using the GuardRank framework on custom bilingual datasets. MLLMGuard demonstrates that multi-dimensional measurement is technically feasible but stops at per-dimension score reporting without explicitly computing or testing cross-dimensional correlations. Our contribution extends this by providing a statistical framework for analyzing correlation structure and testing coupling vs. independence hypotheses.

**BOLD** (Dhamala et al., 2021) benchmarks fairness metrics on 23,679 prompts spanning profession, gender, race, religion, and political ideology dimensions, reporting toxicity and sentiment scores. BOLD's focus on fairness depth (multiple demographic axes) leaves reliability and robustness unmeasured, preventing cross-dimensional correlation analysis. We augment BOLD-style demographic measurement with reliability and robustness scoring on identical outputs, enabling fairness-accuracy trade-off quantification.

## Independent Dimension Benchmarks

Traditional trustworthiness benchmarks evolved in parallel communities, measuring dimensions independently:

- **Reliability:** TruthfulQA (Lin et al., 2022) tests factual accuracy on 817 questions designed to elicit common misconceptions. We build on TruthfulQA's ground-truth labels but extend evaluation to robustness and fairness on the same outputs.
  
- **Robustness:** AdvGLUE (Wang et al., 2021) and adversarial suffix attacks (Zou et al., 2023) measure consistency under perturbation. We measure robustness via paraphrase consistency without adversarial modification, enabling correlation with reliability on natural inputs.

- **Fairness:** HONEST (Nozza et al., 2021) quantifies demographic bias in language model continuations. We adapt HONEST to TruthfulQA via demographic augmentation (e.g., "A Black doctor..." vs. "An Asian doctor..."), creating fairness variance for correlation analysis while preserving factual question structure.

## Alignment Tax and Safety Trade-offs

The term "alignment tax" appears informally in RLHF literature to describe safety interventions that reduce model capabilities. Bai et al. (2022) observe that Constitutional AI training can decrease performance on benign tasks. Ouyang et al. (2022) note that instruction-following fine-tuning sometimes reduces factual accuracy. However, prior work reports these trade-offs anecdotally or through separate ablations rather than as correlation magnitudes.

Our contribution provides the first quantitative estimate: fairness-reliability correlation r=-0.25 (95% CI [-0.31, -0.18]) represents a measurable alignment tax where RLHF prioritizes demographic fairness at a 25% correlation cost to factual accuracy. This quantification enables practitioners to perform cost-benefit analysis of safety interventions before deployment, moving the alignment tax from folklore to actionable metric.

## Training Dynamics and Memorization

Carlini et al. (2021) demonstrate that LLMs memorize and can extract verbatim training data, establishing that memorization is pervasive in large-scale pre-training. Brown et al. (2020) observe that scaling model size increases memorization capacity, particularly for factual knowledge. We extend this by showing that memorization creates a coupling mechanism: models that memorize facts strongly (high reliability) also retrieve them consistently across paraphrases (high robustness), producing r=0.72 correlation on factual content.

The mechanism specificity—factual prompts show r=0.72 vs. misinformation prompts r=0.28—validates that coupling traces to memorization rather than generic model behavior. This mechanistic attribution distinguishes our work from black-box correlation observation, providing causal understanding of *why* dimensions couple through shared training dynamics.

## Gap Summary

Existing work has developed multi-dimensional evaluation frameworks (TrustVis, MLLMGuard) and dimension-specific benchmarks (TruthfulQA, AdvGLUE, BOLD, HONEST), but no prior work systematically measures cross-dimensional correlations using synchronized evaluation. The gap exists because:

1. Frameworks evolved in parallel communities (reliability: NLP, fairness: ML ethics, robustness: adversarial ML) without unified correlation analysis infrastructure.
2. Benchmarks report per-dimension scores as independent metrics, discarding correlation structure from multi-dimensional evaluation logs.
3. Sequential or perturbation-based evaluation confounds correlations with artifacts, requiring synchronized measurement (same checkpoint, prompts, parameters) to isolate genuine coupling.

We fill this gap by treating evaluation logs as latent multi-dimensional datasets, discovering correlation structure on existing benchmarks (TruthfulQA) without building new data. Our synchronized evaluation methodology and statistical framework for testing coupling vs. independence enable mechanistic understanding of training dynamics that prior dimension-isolated approaches cannot reveal.
