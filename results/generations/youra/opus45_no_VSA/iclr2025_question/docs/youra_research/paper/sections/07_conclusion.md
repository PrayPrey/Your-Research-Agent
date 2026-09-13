# 7. Conclusion

We introduced Cross-Layer Trajectory Instability (CLTI) for single-pass hallucination detection in large language models. Our experiments on TruthfulQA MC1 with LLaMA-2-7B yield both positive and negative findings:

**Validated claims:**
- Normalized Trajectory Instability (NTI) achieves AUROC 0.5657, providing statistically significant discrimination beyond chance
- Combined trajectory features (NTI + CMI + $H_L$) improve detection by +7.1% AUROC ($p = 1.15 \times 10^{-5}$) over entropy alone
- The improvement is not due to overfitting (LRT confirms non-redundant contribution)

**Refuted claims:**
- Trajectory metrics fail on low-entropy ("confident") predictions (AUROC 0.5136, CI includes chance)
- RCI flip patterns appear in >90% of all responses, revealing architectural rather than epistemic dynamics

These findings establish CLTI as a complementary signal for hallucination detection on uncertain predictions, while clarifying that confident hallucinations require different detection approaches. The negative result on RCI flip patterns informs future interpretability research: layer-wise token competition is universal in transformers, not specific to epistemic uncertainty.

**Future directions:**
- Entropy-orthogonal features (hidden state geometry, attention entropy) to address confident hallucinations
- Multi-model validation (Mistral, LLaMA-3, Qwen) for architecture-general findings
- Semantic RCI refinement measuring distance between competing tokens
- Causal intervention via activation patching to establish mechanism

We release our codebase for trajectory feature extraction, enabling application to any transformer architecture.
