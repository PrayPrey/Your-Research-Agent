# 2. Related Work

## 2.1 Uncertainty Quantification in LLMs

Early work on LLM uncertainty relies on token-level conditional probabilities, but RLHF-trained models exhibit poor calibration between confidence and accuracy (Tian et al., 2023). Verbalized confidence ("I am 80% sure") often outperforms raw probabilities for post-RLHF models.

**Semantic entropy** (Kuhn et al., 2023) addresses linguistic invariance by clustering semantically equivalent generations before computing entropy. This achieves strong detection performance (AUROC ~0.75 on TruthfulQA) but requires 5-10 samples per query. **SelfCheckGPT** (Manakul et al., 2023) provides black-box consistency checking via sampling and cross-referencing, again requiring multiple generations.

Probe-based methods avoid multi-sampling by training classifiers on internal representations. **Kadavath et al. (2022)** show models can evaluate P(True) for their own claims. **MIND** (Su et al., 2024) uses internal states for real-time unsupervised detection. **Semantic entropy probes** (Kossen et al., 2024) demonstrate that lightweight linear classifiers on hidden states approach the accuracy of full semantic entropy computation.

## 2.2 Cross-Layer Analysis

The **logit lens** (Nostalgebraist, 2020) projects intermediate representations through the final unembedding matrix, revealing per-layer probability distributions. This enables analysis of how predictions evolve across layers. **Tuned lens** (Belrose et al., 2023) improves fidelity with learned per-layer affine transforms.

**END decoding** (Wu et al., 2025) demonstrates that cross-layer entropy correlates with factuality---high entropy variation across layers predicts hallucination. Our work formalizes this observation into trajectory metrics (NTI, CMI) and validates them with controlled experiments.

## 2.3 Attractor Dynamics in Transformers

Elhage et al. (2022) characterize transformers as performing iterative refinement, where early layers provide coarse features and late layers converge toward final predictions. This architectural property implies that *all* responses undergo representational reorientation, not just hallucinations---a prediction borne out by our RCI flip pattern results.

## 2.4 Positioning

Our work bridges probe-based and cross-layer approaches. Unlike MIND, which uses arbitrary internal features, we compute interpretable trajectory metrics. Unlike END, we provide controlled validation with pre-registered predictions and falsification criteria. Unlike semantic entropy, we require only a single forward pass.

| Method | Single-Pass | No External DB | Interpretable | Validated |
|--------|-------------|----------------|---------------|-----------|
| Semantic Entropy | No | Yes | Moderate | Yes |
| SelfCheckGPT | No | Yes | High | Yes |
| MIND | Yes | Yes | Low | Partial |
| END | Yes | Yes | Moderate | No |
| **CLTI (Ours)** | **Yes** | **Yes** | **High** | **Yes** |
