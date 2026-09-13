# Experiments

To validate our hypothesis that trustworthiness dimensions exhibit selective coupling under targeted interventions, we designed a five-hypothesis mechanistic validation chain. Each hypothesis tests a specific link in the causal pathway from parameter updates to cross-dimensional performance effects, with gate conditions determining whether to proceed, pivot, or document limitations.

## Five Experimental Questions

Our experimental design addresses five questions corresponding to the mechanistic chain:

**Q1 (H-E1): Do cross-dimensional effects exist?** We first establish existence by measuring whether interventions targeting one dimension (truthfulness) produce statistically significant correlations across all dimension pairs. This validates the core premise that dimensions are not independent under intervention.

**Q2 (H-M1): Do parameter updates improve the target dimension?** Before investigating cross-dimensional effects, we verify that the intervention works as intended—gradient descent on truthfulness data should measurably improve truthfulness performance. This rules out the null hypothesis that observed correlations result from intervention failure.

**Q3 (H-M2): Do parameter updates reshape internal representations?** To bridge parameter changes and performance effects, we measure whether LoRA updates cause detectable changes in layer activations across the network. This tests whether shared-layer architecture propagates intervention effects throughout the model.

**Q4 (H-M3): Are representation changes selectively coupled to dimensions?** Given universal representation changes, we ask whether performance effects are universal or selective—do all dimension pairs correlate, or only specific pairs? This distinguishes universal coupling from the selective taxonomy we hypothesize.

**Q5 (H-M4): Do patterns generalize across architectures?** Finally, we test whether correlation patterns replicate across model families. Architecture-agnostic patterns suggest fundamental optimization dynamics, while model-specific patterns indicate architecture-dependent trade-offs.

## General Experimental Protocol

All experiments share a common intervention protocol for controlled comparison:

**Intervention method.** We use LoRA (Low-Rank Adaptation) fine-tuning with rank r=8, scaling factor α=16, applied to attention layers (c_attn modules). LoRA provides a controlled intervention by modifying a small parameter subset (0.24% of GPT-2's weights) while preserving pretrained knowledge.

**Datasets.** We evaluate three trustworthiness dimensions using established benchmarks:
- **Truthfulness:** TruthfulQA multiple-choice (MC2), measuring factual accuracy across 817 questions spanning common misconceptions
- **Fairness:** Bias Benchmark for QA (BBQ), measuring stereotype bias across ambiguous contexts (1,000 samples from diverse social categories)
- **Robustness:** Adversarial NLI Round 3 (ANLI R3), measuring resistance to adversarially-constructed natural language inference examples (1,200 test samples)

**Evaluation pipeline.** Each experiment evaluates models pre- and post-intervention on all three dimensions using standardized evaluation harnesses (lm-evaluation-harness for baselines, consistent inference pipelines for post-intervention). We compute performance deltas (Δ = post - pre) and analyze correlation structure across dimension pairs using Pearson correlation with permutation-based significance testing.

## H-E1: Existence of Cross-Dimensional Effects

**Protocol.** We fine-tune GPT-2 (124M) on 100 TruthfulQA samples for 3 epochs using LoRA. We replicate the intervention three times with different random seeds (42, 43, 44) to generate variance in performance deltas. For each replicate, we evaluate all three dimensions (truthfulness, fairness, robustness) and compute pairwise correlations across the three replicates.

**Metrics.** Primary metric: percentage of dimension pairs showing significant correlation (p<0.01) via Pearson correlation test. Gate threshold: ≥80% of pairs must show significant effects (hypothesis predicts 12/15 configurations across full experimental design; PoC tests 3/3 pairs on single model).

**Analysis.** We perform Pearson correlation on performance deltas across the three seeds for each dimension pair. Statistical significance assessed via two-tailed t-test on correlation coefficients. This perturbation-based design transforms random variation from noise into signal, revealing whether dimensions move together under intervention.

## H-M1: Target Dimension Improvement

**Protocol.** Using the same three GPT-2 replicates from H-E1, we isolate the target dimension (truthfulness) and test whether fine-tuning reliably improves performance. We compare baseline TruthfulQA MC2 scores (pre-intervention, evaluated on full 817 questions) to post-intervention scores using paired comparison.

**Metrics.** Primary metric: mean Δ(Truthfulness) > 0 with p<0.05 via paired t-test. Secondary metric: directional consistency—percentage of replicates showing positive Δ (threshold: ≥70%). Gate threshold: both criteria must pass (MUST_WORK gate—if interventions don't improve target dimension, the entire mechanism fails).

**Analysis.** We compute per-replicate deltas and aggregate statistics (mean, standard deviation). Statistical significance tested via one-sample t-test against null hypothesis μ(Δ) = 0. This validates that LoRA fine-tuning works as standard gradient descent theory predicts.

## H-M2: Representation Propagation

**Protocol.** We extract internal activations from GPT-2 before and after LoRA intervention using TransformerLens, a mechanistic interpretability library providing hooked access to layer activations. We analyze 24 layers: 12 attention pattern layers (blocks.{0-11}.attn.hook_pattern) and 12 residual stream layers (blocks.{0-11}.hook_resid_post).

For each layer, we extract activations on a held-out evaluation set (100 samples), compute Centered Kernel Alignment (CKA) similarity between pre- and post-intervention representations, and measure change magnitude as Δ = 1 - CKA. CKA quantifies representational similarity while being invariant to orthogonal transformations, making it suitable for comparing neural network layers.

**Metrics.** Primary metric: percentage of layers showing detectable change (CKA < 1.0, equivalently Δ > 0). Secondary metric: correlation between representation change magnitude and performance delta (tests whether larger layer changes predict larger performance shifts). Gate threshold: ≥50% layers changed OR significant correlation (p<0.05) with performance (SHOULD_WORK gate allows continuation if mechanism partially validates).

**Analysis.** We aggregate CKA scores across the three seeds and compute layer-wise statistics. We test correlation between mean representation change per layer and h-m1 target dimension improvement using Pearson correlation. This establishes the mechanistic link between parameter updates and downstream effects.

## H-M3: Selective Coupling

**Protocol.** We scale up H-E1 with increased training data (500 TruthfulQA samples instead of 100) and full 3-epoch fine-tuning to generate stronger intervention effects. We evaluate all three dimensions pre- and post-intervention across three seeds, computing pairwise correlations for all dimension pairs: truthfulness-fairness, truthfulness-robustness, fairness-robustness.

**Metrics.** Primary metric: non-random correlation structure, assessed by comparing observed correlations to permutation-test null distribution (1,000 permutations). We test whether correlation patterns differ from random baseline at p<0.05. Secondary metrics: per-pair correlation strength and statistical significance. Gate threshold: at least one dimension pair shows non-random correlation structure (SHOULD_WORK gate).

**Analysis.** For each dimension pair, we compute Pearson r across the three seeds and p-values via t-test. We perform permutation tests by randomly shuffling dimension assignments and recomputing correlations to establish null distribution. Layer-wise analysis extends representation propagation by computing which layers most correlate with which dimension shifts, revealing dimension-specific substrates.

This experiment is the critical test of selective coupling—the hypothesis predicts not universal correlation, but dimension-pair-specific patterns (some pairs trade off, others independent).

## H-M4: Architectural Replication

**Protocol.** We replicate the H-M3 intervention protocol across three transformer architectures: GPT-2 (124M), OPT-350M (350M), and Pythia-410M (410M). Each model undergoes minimal LoRA perturbation (10 training steps instead of full 3 epochs) to reduce computational cost while maintaining correlation signal. We run five seeds per model (total: 15 runs) to enable robust correlation estimation per architecture.

**Metrics.** Primary metric: directional replication rate—for each dimension pair, we classify correlation direction as positive, negative, or neutral (|r|<0.2), then compute percentage of models showing the majority direction. Gate threshold: ≥60% replication rate for at least one dimension pair (SHOULD_WORK gate—partial replication validates architecture-agnostic claims for specific pairs).

**Analysis.** We compute per-model correlations and classify directions. Chi-square test for directional consistency across models (H₀: directions are random). We identify which dimension pairs show consistent patterns (architecture-agnostic) versus model-specific effects. This distinguishes fundamental trade-offs from architecture-dependent phenomena.

## Statistical Power and Limitations

Our experimental design prioritizes mechanistic validation over statistical precision. H-E1 and H-M1 use 3 replicates (sufficient for directional consistency but limited for precise effect size estimation). H-M3 analyzes correlations with n=3, providing ~50% power to detect large effects (r≥0.9). H-M4 scales to 5 seeds per model for improved power. We acknowledge these limitations transparently and interpret results accordingly—large effect sizes with marginal significance (e.g., r=-0.997, p=0.051 in H-M3) suggest true effects requiring replication with larger samples.

All experiments use real benchmark datasets (no synthetic or mock data). Training uses controlled hyperparameters (learning rate 1e-4, AdamW optimizer, cosine schedule) to ensure intervention consistency. Gate conditions enforce quality thresholds: MUST_WORK gates (H-E1, H-M1) require strong validation before proceeding, while SHOULD_WORK gates (H-M2, H-M3, H-M4) allow continuation with documented limitations, balancing scientific rigor with exploratory research.
