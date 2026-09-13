# 6. Discussion

## 6.1 Validated Claims

Our experiments confirm that cross-layer trajectory instability provides discriminative signal for hallucination detection. NTI (AUROC 0.5657) demonstrates that entropy variance across late layers correlates with response incorrectness. The combined model improves over entropy-only baseline by +7.1% AUROC with strong statistical significance (p = 1.15e-05).

This supports the attractor dynamics interpretation: factual retrieval follows stable convergence toward a knowledge-grounded answer, while fabrication involves cross-layer reorientation detectable as elevated trajectory instability.

## 6.2 Refuted Claims and Scope Narrowing

**Low-entropy failure (h-m2)**: The signal collapses on confident predictions (AUROC 0.5136 on low-entropy subset). This is not surprising given NTI's definition---variance normalized by mean entropy approaches zero when mean entropy is low. The practical implication: trajectory metrics cannot detect "confident but wrong" hallucinations, the most dangerous failure mode.

**RCI flip universality (h-m3)**: Top-token flips occur in >90% of both correct and incorrect responses. This falsifies the hypothesis that competition patterns distinguish hallucinations, but provides valuable insight: transformer layer processing involves iterative refinement that produces representational reorientation regardless of output correctness. Future interpretability work should consider this architectural baseline.

## 6.3 Limitations

1. **Entropy coupling**: NTI is mathematically tied to the entropy regime, precluding orthogonal signal. Future work should explore entropy-independent trajectory features (e.g., hidden state geometry, attention patterns).

2. **Single model**: Results are specific to LLaMA-2-7B. Generalization to other architectures (Mistral, LLaMA-3, Qwen) requires replication.

3. **Multiple-choice format**: TruthfulQA MC1 constrains generation to choice selection. Free-form generation may exhibit different trajectory patterns.

4. **Correlation only**: We establish correlation between NTI and incorrectness, not causation. Intervention experiments (activation patching, layer truncation) are needed for causal claims.

5. **No baseline comparison yet**: Phase 5 baseline comparison against raw mean entropy was not completed in this validation cycle.

## 6.4 Connection to Prior Work

Our findings align with the MIND framework (Su et al., 2024) showing internal states carry hallucination-relevant signal, and with END decoding (Wu et al., 2025) demonstrating cross-layer entropy correlation with factuality. We extend these by providing:

- Interpretable, single-formula metrics (NTI, CMI) vs. arbitrary feature ensembles
- Pre-registered predictions with falsification criteria
- Negative results (RCI, low-entropy failure) that constrain the hypothesis space

The RCI universality finding resonates with Elhage et al. (2022)'s characterization of transformers as iterative refiners. Our empirical evidence quantifies this: the "flip pattern" has >90% baseline prevalence, making it unsuitable as a hallucination indicator.

## 6.5 Practical Implications

**When to use CLTI**: In deployment scenarios where:
- Single-pass inference is required (latency-sensitive)
- The model expresses uncertainty (high output entropy)
- Approximate detection is acceptable (AUROC 0.57 vs 0.75 for semantic entropy)

**When not to use CLTI**:
- When the model is confident (low entropy)---trajectory metrics add no signal
- When high precision is required---semantic entropy remains superior
- When computational cost is not a constraint

## 6.6 Future Directions

1. **Entropy-orthogonal features**: Hidden state geometry (PCA eigenspectrum), attention entropy, cross-head agreement may provide signal independent of output entropy.

2. **Multi-model validation**: Test on Mistral-7B, LLaMA-3-8B, Qwen-2-7B to establish generalization bounds.

3. **Semantic RCI**: Instead of binary top-token flips, measure semantic distance between competing tokens. Hallucinations may involve competition between semantically distant alternatives.

4. **Causal intervention**: Activation patching at high-NTI layers to test whether suppressing trajectory instability reduces hallucination rate.

5. **Ensemble combination**: Combine CLTI features with semantic entropy for improved detection across the confidence spectrum.
