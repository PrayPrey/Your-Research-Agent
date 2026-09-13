# Related Work

Our work intersects three research threads: output-level uncertainty quantification, hidden state probing, and transformer interpretability. We position each as necessary but insufficient for efficient correctness prediction.

## Output-Level Uncertainty Quantification

**Token-based methods.** Fadeeva et al. (2024) survey token-level uncertainty metrics including entropy, perplexity, and sequence probability. These methods achieve ~0.62–0.65 AUROC for correctness prediction on factual QA—better than random but insufficient for reliable deployment. The fundamental limitation: output softmax distributions conflate linguistic confidence (fluency) with factual confidence (correctness).

**Semantic entropy.** Kuhn et al. (2023) address this by sampling multiple responses and clustering by semantic equivalence. Semantic entropy achieves ~0.80 AUROC by detecting when diverse samples produce semantically distinct answers (high uncertainty) versus consistent answers (low uncertainty). However, this requires 5–20 forward passes per question, making it impractical for real-time applications.

**Single-sample approximations.** Recent work attempts to approximate semantic entropy from single samples. Kossen et al. (2024) train probes to predict semantic entropy from hidden states, achieving 0.85+ correlation with ground-truth SE. However, predicting *uncertainty* differs from predicting *correctness*—a confident model can still be wrong.

## Hidden State Probing

**Probing for concepts.** Linear probes have successfully extracted semantic concepts from transformer hidden states, including sentiment, syntax, and factual knowledge. Burns et al. (2023) use contrastive probing to detect model beliefs. Our work extends this paradigm: rather than probing for specific facts, we probe for correctness of model-generated answers.

**Semantic Entropy Probes (SEP).** Kossen et al. (2024) is closest to our approach. SEP trains linear probes on hidden states to predict semantic entropy, enabling single-pass uncertainty estimation. We depart from SEP in two ways: (1) our target is ground-truth correctness, not uncertainty; (2) we systematically characterize layer depth effects, identifying optimal extraction at 50–60% depth.

## Transformer Interpretability

**Logit lens.** nostalgebraist (2020) demonstrates that projecting intermediate hidden states to vocabulary space reveals semantic content developing across layers. This supports our hypothesis that middle layers encode semantic knowledge before output formatting.

**Layer-wise analysis.** Aiersilan et al. (2026) study hallucination detection across layers, finding optimal signals at 40–56% depth for Llama and Mistral models. Our inverted-U pattern (peak at 50% depth) aligns with these findings, confirming middle layers as the locus of semantic representations.

**Mechanistic interpretability.** Recent work on residual stream analysis shows that transformer layers progressively refine representations from input tokens to output predictions. We leverage this insight: middle layers have accumulated semantic understanding but have not yet compressed it for next-token prediction.

## Positioning Our Contribution

Prior work establishes that hidden states correlate with uncertainty (SEP) and that middle layers contain semantic content (logit lens, hallucination studies). We synthesize these findings with a novel target: direct correctness prediction. Unlike SEP, we train on ground-truth labels, enabling the probe to capture correctness signals orthogonal to uncertainty. Unlike multi-sample methods, we require only a single forward pass. Our systematic layer sweep provides principled guidance for extraction depth, filling a gap in the literature.
