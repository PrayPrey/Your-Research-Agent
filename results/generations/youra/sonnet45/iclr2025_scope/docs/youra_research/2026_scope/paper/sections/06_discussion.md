# 6. Discussion

Our empirical investigation reveals that pre-trained Transformer projection weights at 7B scale are NOT low-rank (r_eff ~ 1600), contradicting assumptions underlying post-hoc compression techniques. We interpret this negative finding, acknowledge limitations, discuss broader implications, and address societal impact.

## 6.1 Interpreting the Refutation

**Why did the hypothesis fail?** The low-rank assumption stemmed from LoRA's empirical success—if low-rank *updates* work (r = 8-64), perhaps pre-trained *weights* are also low-rank. Our measurement reveals this inference was incorrect. LoRA works precisely because it exploits a different property: the low-dimensional structure of task-specific adaptations, not compressibility of pre-trained weights themselves.

**The 50× gap.** The measured 50× gap between LoRA's adaptation rank (r ~ 32) and pre-trained weight rank (r_eff ~ 1600) is revealing. Pre-training on massive diverse corpora (The Pile, Common Crawl, etc.) teaches models to represent many different semantic and syntactic patterns, requiring high-dimensional weight structure. Fine-tuning for a specific task (e.g., sentiment analysis, question answering) identifies the low-dimensional subspace relevant to that narrow application. This explains both findings: weights are high-rank (general-purpose capability), updates are low-rank (task-specific specialization).

**Distributed representations.** The near full-rank structure (r_eff ~ 40% of dimension 4096) suggests semantic information is distributed across dimensions rather than compressed into fewer principal components. This aligns with distributed representation theory: concepts are encoded via patterns across many neurons, not localized to specific low-dimensional subspaces. Compression would reduce r_eff; distributed encoding maintains high rank.

## 6.2 Implications for Research Directions

**Post-hoc Transformer→SSM conversion.** Our finding establishes a boundary condition: post-hoc conversion techniques that assume bounded-state compression (r_eff < 256, state size N ≤ 1024) are not viable for 7B-scale pre-trained Transformers. The empirical refutation explains why recent work focuses on (1) training SSMs from scratch [Gu & Dao, 2023], (2) co-training hybrid architectures [Pióro et al., 2024; Ren et al., 2024], or (3) compressing already-trained SSMs [Muñoz et al., 2025] rather than converting Transformers post-hoc.

**LoRA and parameter-efficient fine-tuning.** For practitioners, our result clarifies LoRA's mechanism: success stems from the insight that task-specific *variations* lie in low-dimensional subspaces, not from compressing already-low-rank weights. This suggests rank selection strategies should focus on task complexity and domain shift magnitude, not on assumed properties of pre-trained weights. Future PEFT methods might exploit other task-specific structural properties (sparsity, low-precision, factorization) without assuming low-rank weights.

**Compression research redirection.** Techniques assuming weight-level low-rank structure (e.g., low-rank factorization for inference acceleration) should validate assumptions empirically before implementation. Our work demonstrates the value of measurement-first approaches: test structural assumptions on real models, then design compression methods grounded in those measurements. Negative findings prevent wasted effort on false foundations.

## 6.3 Limitations and Future Work

We acknowledge four principled limitations and outline how future work can address them:

### Limitation 1: Single Model Scale (7B)

**Limitation:** Results are specific to 7B-parameter models. Rank properties may differ at other scales.

**Why acceptable:** Establishes first empirical ground truth at a widely-used scale (LLaMA-7B, Mistral-7B family). Provides baseline for cross-scale comparison.

**Future mitigation:** Extend analysis to multiple scales: GPT-2 (117M), Pythia-1B, LLaMA-13B, LLaMA-70B. Research question: Does r_eff scale linearly with model dimension, or does it plateau? If rank plateaus, smaller models might exhibit moderate low-rank structure; if rank scales linearly, all scales maintain near full-rank proportionally.

### Limitation 2: Weight Analysis vs. Runtime Attention

**Limitation:** Analyzed projection weight matrices (W_Q, W_K, W_V), not runtime attention matrices (QK^T during inference).

**Why acceptable:** Hypothesis concerned "operator-level low-rank structure" of learned parameters. Weight analysis directly tests this claim. Runtime attention is a complementary but distinct question.

**Future mitigation:** Measure effective rank of runtime attention matrices QK^T computed during forward passes on diverse text samples. This requires caching attention tensors for multiple inputs and may reveal different rank properties (runtime patterns could be low-rank even if projection weights are full-rank). If true, this would inform architectural designs that exploit runtime low-rank structure without assuming weight-level compression.

### Limitation 3: Architecture Specificity

**Limitation:** LLaMA-family decoder-only Transformers only. Vision Transformers, encoder-decoder models, multilingual models not tested.

**Why acceptable:** Targets the most widely-deployed architecture family for language modeling (LLaMA, Mistral, GPT variants share similar structure).

**Future mitigation:** Extend methodology to Vision Transformers (ViT), CLIP, encoder-decoder models (T5, BART). Vision models process 2D spatial structure; rank properties may differ. Multilingual models trained on diverse scripts may exhibit different compression patterns.

### Limitation 4: Methodology Validation Sample Size

**Limitation:** h-e1 used 50 samples (reduced from 5000+ for memory efficiency). Validates methodology works, not full statistical power.

**Why acceptable:** h-m1 hypothesis testing uses deterministic weight analysis (SVD of static matrices), so sample size doesn't affect primary results. h-e1's purpose was proof-of-concept (pipeline functional), not statistical significance.

**Future mitigation:** For runtime attention analysis (Limitation 2), sample size matters. Future work should use large sample sizes (10K+ diverse texts) to ensure statistical robustness.

## 6.4 Broader Impact Statement

**Positive impacts:**
1. **Scientific integrity:** Transparent reporting of refuted hypothesis contributes to the reproducibility and honesty of empirical research. Negative findings are scientifically valuable when they prevent misguided research directions.
2. **Research efficiency:** Prevents wasted effort on post-hoc conversion techniques with false foundations. Researchers can now focus on empirically-validated approaches.
3. **Methodological contribution:** Validated analysis pipeline can be reused by other researchers to measure rank properties in their models, advancing measurement-driven compression research.

**Negligible negative impacts:** This is a measurement study with a negative finding—no new model, no deployment system, no risk of misuse. The work establishes what does NOT work (post-hoc conversion based on low-rank assumptions), guiding future research away from unproductive directions.

**Ethical considerations:** None identified. Measurement of publicly available pre-trained models (Mistral-7B) using open-source tools (NumPy SVD) and transparent reporting of null results aligns with open science principles.

**Accessibility and reproducibility:** Code and methodology publicly documented. Computational requirements (A100 GPU, 64GB RAM) are accessible to academic research labs and cloud compute users. Deterministic analysis ensures full reproducibility.

## 6.5 Lessons for Empirical Research

This work illustrates a pattern: **empirical assumptions derived from indirect evidence must be validated before building dependent techniques**. LoRA's success with low-rank updates was interpreted as evidence of low-rank weights—a logical inference, but incorrect. Direct measurement revealed the conflation.

**Principle:** Separate measurement from method design. Measure structural properties first (rank, sparsity, precision requirements), then design compression/adaptation techniques grounded in those measurements. Assumptions based on indirect inference (e.g., "Method X works, therefore Property Y must hold") require direct validation.

**Generalizable lesson:** In machine learning, many "known" properties (e.g., "attention is sparse", "embeddings are low-rank", "activations are redundant") stem from method success rather than direct measurement. Our work demonstrates the value of skepticism: test widely-held assumptions empirically, especially when they underpin entire research directions. Negative findings that correct false assumptions contribute as much to scientific progress as positive results.

## 6.6 Summary

The empirical refutation of the low-rank hypothesis—with effective ranks r_eff ~ 1600 instead of r_eff < 256—clarifies that:

1. **LoRA works via low-rank updates, not low-rank weights**. The 50× gap between adaptation rank and weight rank demonstrates these are independent properties.

2. **Post-hoc Transformer→SSM conversion based on bounded-state assumptions is not viable at 7B scale**. Native hybrid training or non-low-rank compression methods are needed.

3. **Pre-trained models maintain high-dimensional representations**. Near full-rank structure (r_eff ~ 40% of dimension) likely reflects the need to support diverse downstream tasks with general-purpose pre-training.

4. **Measurement-first research prevents wasted effort**. Direct empirical validation of assumptions avoids building techniques on false foundations.

This negative finding has scientific value: it prevents misguided research, clarifies mechanisms, and establishes empirical ground truth for future work. The path forward requires systematic measurement across scales, architectures, and training regimes—grounded in data, not assumptions.
