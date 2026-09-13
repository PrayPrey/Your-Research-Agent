## Name

tail_anchoring_model_collapse

## Title

Tail-Aware Data Anchoring: Preserving Rare Examples to Efficiently Prevent Model Collapse in Iterative Synthetic Training

## Short Hypothesis

Model collapse in iterative synthetic training is primarily driven by the erosion of distribution tails. We hypothesize that a small, carefully selected anchor set of real data points concentrated on tail/rare examples can prevent model collapse far more efficiently (per sample) than random real-data mixing. This directly challenges the existing literature, which derives optimal mixing *ratios* but treats all real data as equally valuable, ignoring the differential importance of rare vs. common examples.

## Related Work

Seddik et al. (2024) theoretically show that model collapse cannot be avoided on pure synthetic data but can be prevented by mixing real data, providing estimates of the maximal synthetic fraction. He et al. (2025) and Garg et al. (2025) derive that the optimal weight assigned to real data follows a golden ratio rule across diverse statistical settings. Gillman et al. (2024) show that self-correcting loops using domain knowledge can stabilize training. Fu et al. (2025) provide generalization bounds showing even a constant fraction of real data ensures convergence. Critically, all of this work treats real data as a homogeneous pool and focuses on *how much* to keep, not *which* examples to keep. Our proposal is the first to study the differential value of individual real data points for collapse prevention, with a specific, theoretically-motivated focus on tail examples — directly motivated by the observation in Seddik et al. that collapse manifests as tail erasure.

## Abstract

Model collapse — the progressive degradation of generative models trained on their own synthetic outputs — poses a critical threat to the iterative self-improvement pipelines increasingly used in foundation model training. Existing work has established that mixing real data with synthetic data can prevent collapse, and has derived optimal mixing ratios (e.g., the golden ratio). However, this literature uniformly treats real data as homogeneous: all real examples are assumed equally valuable as anchors. We challenge this assumption with a simple but powerful observation: since model collapse manifests primarily as the erasure of distribution tails, tail examples in the real data should be disproportionately valuable for preventing collapse. We propose **Tail-Aware Data Anchoring (TADA)**, a data curation strategy that selects a small anchor set of real data concentrated on low-density, tail regions of the data distribution, and mixes this anchor set with synthetic data across training generations. We conduct controlled experiments on language model training (GPT-2 scale) under iterative synthetic data loops, comparing TADA against random anchor selection, centroid/high-density anchor selection, and the golden-ratio mixing baseline. We measure collapse using perplexity, tail token coverage, and distributional divergence across generations. Our results demonstrate that tail-focused anchoring prevents collapse with significantly fewer real data points than random mixing, offering a practical, theoretically-grounded data curation principle for FM developers who face real-data scarcity or cost constraints.

## Experiments

1. **Setup**: Train GPT-2 (small, ~117M params) iteratively for 10 generations on a text corpus (e.g., OpenWebText subset). At each generation, the model generates synthetic data to replace/augment training data, with a fixed budget of real anchor examples mixed in.

2. **Anchor Selection Strategies** (the key comparison):
   - *Random anchoring*: Uniformly sample real examples up to budget B.
   - *Tail anchoring (TADA)*: Fit a kernel density estimator or use perplexity of a frozen reference model to score each real example; select the B lowest-density (highest-perplexity) examples as anchors.
   - *Centroid anchoring*: Select the B highest-density (most typical) examples.
   - *Golden-ratio full mixing*: Mix real and synthetic at the theoretically optimal ratio (baseline).

3. **Budget sweep**: Vary the anchor budget B from 0.5% to 20% of training data to identify the crossover point where TADA matches full random mixing.

4. **Metrics**:
   - *Perplexity* on held-out real data across generations (primary collapse indicator).
   - *Tail coverage*: Fraction of held-out tail examples (bottom 10% density) within a threshold perplexity.
   - *Distributional divergence*: KL divergence between generation-N model distribution and original model distribution, estimated via importance sampling.
   - *Diversity*: Self-BLEU and entropy of generated text.

5. **Theoretical analysis**: Derive a simple bound showing that, for a Gaussian mixture model with rare components, anchoring on tail examples reduces the per-sample cost of preventing tail erasure by a factor proportional to the inverse tail probability.

6. **Extension to multimodal setting**: Repeat key experiments with a small vision-language model (e.g., LLaVA-style) on image captioning to test generality.

## Risk Factors And Limitations

1. **Density estimation quality**: Identifying tail examples requires a reliable density estimator; in high-dimensional text spaces, KDE may be unreliable. Mitigation: use reference model perplexity as a proxy, which is well-established.
2. **Definition of 'tail'**: The tail of a text distribution is not uniquely defined; different notions (lexical rarity, semantic rarity, topic rarity) may give different results. We will compare multiple definitions.
3. **Compute constraints**: 10 generations of GPT-2 training is feasible on 2-4 A100 GPUs; the multimodal extension may require more resources but can be scoped to fine-tuning.
4. **Generalization**: Results on GPT-2 may not directly transfer to much larger models; we will discuss scaling implications.
5. **Interaction with synthetic data quality**: If synthetic data quality is high, the benefit of tail anchoring may be reduced. We will test across different quality regimes.
6. **The golden ratio baseline is theoretical**: The golden ratio result holds for simple statistical models (linear regression, Gaussian estimation); its applicability to neural LMs is approximate, so comparisons should be interpreted carefully.

