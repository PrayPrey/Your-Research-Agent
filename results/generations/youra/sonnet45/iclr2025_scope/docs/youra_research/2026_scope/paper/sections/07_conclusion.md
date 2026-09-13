# 7. Conclusion

We opened by noting LoRA's remarkable success with low-rank adapters and the natural assumption it creates: if low-rank updates work (r = 8-64), perhaps pre-trained weights are also low-rank. Our empirical investigation reveals the assumption is false. Pre-trained projection weights in 7B-scale Transformer models are NOT low-rank—effective ranks range from 1554-1647 (99% variance threshold), approaching nearly full-rank (~40% of dimension 4096). This is 6-7× higher than thresholds assumed for post-hoc compression and contradicts the bounded-state compression hypothesis.

This negative finding carries scientific value in three ways. **First**, it clarifies LoRA's mechanism: success stems from exploiting the low-dimensional structure of task-specific *adaptations*, not from compressing already-low-rank *weights*. The 50× gap between adaptation rank (r ~ 32) and weight rank (r_eff ~ 1600) demonstrates these are independent properties—general-purpose pre-training requires high-dimensional representations, while task-specific fine-tuning identifies narrow subspaces.

**Second**, it establishes empirical ground truth for compression research. Post-hoc Transformer→SSM conversion techniques that assume bounded-state representations (r_eff < 256, state size N ≤ 1024) are not viable for 7B-scale pre-trained models. Our measurement redirects research toward (1) native hybrid architectures co-trained from initialization [Pióro et al., 2024; Ren et al., 2024], (2) compression methods that don't assume low-rank structure, or (3) empirically validating assumptions before building techniques.

**Third**, it demonstrates the value of measurement-first research. Assumptions derived from indirect evidence (LoRA's success) must be validated before becoming foundations for dependent work. Direct empirical measurement—even when it yields negative results—prevents wasted effort on false foundations and corrects community understanding.

## Limitations and Future Directions

Our results are specific to 7B-scale LLaMA-family models and analyze projection weight matrices (not runtime attention). Four future research directions address these limitations:

**1. Cross-scale rank analysis.** Extend measurements to GPT-2 (117M), Pythia-1B, LLaMA-13B, LLaMA-70B to determine whether rank scales linearly with model dimension or plateaus. If rank plateaus, smaller models might exhibit moderate low-rank structure; if rank scales linearly, all scales maintain near full-rank proportionally.

**2. Runtime attention matrix analysis.** Measure effective rank of runtime attention matrices (QK^T) computed during inference on diverse text samples. Runtime patterns may exhibit low-rank structure even if projection weights are full-rank—this would inform architectural designs exploiting runtime properties without assuming weight-level compression.

**3. Architecture generalization.** Extend methodology to Vision Transformers (ViT), CLIP, encoder-decoder models (T5), and multilingual variants to identify whether near full-rank structure is specific to decoder-only language models or a general property of Transformer pre-training.

**4. Mechanistic understanding of the rank gap.** Investigate *why* task-specific updates (r ~ 32) occupy such a dramatically lower-dimensional subspace than pre-trained representations (r_eff ~ 1600). Can we predict which tasks admit lower-rank adaptation? Are there tasks requiring higher-rank updates?

## Closing Perspective

In science, null results are as important as positive findings when they prevent misguided research directions. Our measurement establishes that LoRA works not by compressing low-rank weights, but by exploiting the low-dimensional structure of task-specific adaptations—a critical distinction that shapes how we design next-generation parameter-efficient methods. More broadly, this work reminds us that widely-held assumptions must be empirically validated, not inferred from indirect evidence.

The path forward requires systematic measurement across model scales, architectures, and training regimes. Which structural properties generalize? Which are scale-dependent? Can we predict from pre-training dynamics whether a model will admit low-rank fine-tuning? These questions demand the same empirical rigor we applied here: **measure first, then build techniques grounded in those measurements**. Only through measurement-driven research can we avoid false assumptions and build compression methods on solid empirical foundations.
