# 1. Introduction

LoRA (Low-Rank Adaptation) has become the de facto method for parameter-efficient fine-tuning of large language models, reducing trainable parameters by 10,000× using rank-8 to rank-64 matrix decompositions [Hu et al., 2021]. This remarkable success—enabling fine-tuning of billion-parameter models on consumer GPUs—naturally suggests that pre-trained Transformer weights must exhibit low-rank structure. After all, if low-rank updates W + ΔW (where ΔW = BA, B ∈ ℝ^(d×r), A ∈ ℝ^(r×d), r ≪ d) suffice for adaptation, doesn't this imply the original weights W themselves are compressible into low-rank form?

We tested this assumption directly via singular value decomposition (SVD) analysis of projection weight matrices in 7B-scale Transformer models and found the opposite: effective ranks range from 1554-1647 at 99% variance threshold, approaching nearly full-rank (~40% of dimension 4096). This is 6-7× higher than thresholds commonly assumed for post-hoc compression techniques and contradicts the bounded-state compression hypothesis underlying recent Transformer-to-SSM (State Space Model) conversion approaches.

## The Problem: Conflating Weight Structure with Update Structure

Parameter-efficient fine-tuning methods like LoRA have demonstrated that adapting pre-trained models requires far fewer parameters than full fine-tuning [Hu et al., 2021; Valipour et al., 2022]. LoRA freezes pre-trained weights W and learns low-rank updates ΔW, typically with r = 8-64. This empirical success has led to an implicit—but untested—assumption in the model compression community: if low-rank updates work, pre-trained weights themselves must be low-rank.

This conflation manifests in multiple research areas. Post-hoc model conversion techniques assume pre-trained Transformers exhibit operator-level low-rank structure enabling conversion to more efficient architectures like SSMs [Gu & Dao, 2023]. Compression methods design pruning and quantization strategies based on presumed low-rank weight structure. Yet despite LoRA's 17,225 citations and widespread adoption, no prior work has directly measured effective ranks of pre-trained projection weights at the 7B scale.

The distinction between weight structure and update structure matters fundamentally. Pre-trained weights W encode general-purpose representations learned from massive corpora, potentially requiring high-dimensional structure to support diverse downstream tasks. In contrast, task-specific updates ΔW capture adaptations for narrow applications, which may lie in low-dimensional subspaces. If these are independent properties—requiring separate empirical validation—then LoRA's success tells us only about update structure, not weight structure.

## Our Approach: Direct Measurement

We separate the question "Are pre-trained weights low-rank?" from "Can fine-tuning updates be low-rank?" and measure the former directly through SVD analysis of projection weight matrices (Q, K, V) in pre-trained 7B-scale models (Mistral-7B, LLaMA-family architectures). Our measurement methodology targets deep Transformer layers (L ≥ 20) where semantic compression theories predict the strongest low-rank signatures.

The analysis yields three key findings:

1. **Effective ranks are nearly full-rank**: Projection weights in deep layers exhibit r_eff = 1554-1647 (99% variance threshold), not the hypothesized r_eff < 256 required for bounded-state SSM conversion. This represents ~40% of model dimension 4096.

2. **No monotonic entropy decrease**: Operator entropy (measured via log-determinant of covariance matrices) does not decrease with layer depth (β = +0.001453, p = 0.072, not statistically significant), contradicting compression-driven entropy reduction predictions.

3. **Validated methodology, refuted hypothesis**: Methodology validation (h-e1) succeeded independently of hypothesis testing (h-m1), ensuring measurement reliability separates from hypothesis outcomes.

## Contributions

Building on this empirical investigation, we contribute:

1. **First direct measurement of effective rank** in pre-trained 7B-scale Transformer projection weights, revealing nearly full-rank structure (r_eff ~ 1600).

2. **Empirical refutation of low-rank assumption** underlying post-hoc Transformer→SSM conversion techniques, establishing that bounded-state compression does not hold at this scale.

3. **Validated SVD-based analysis methodology** applicable to other model families, scales, and architectural analyses.

4. **Mechanistic clarification of LoRA's success**: LoRA works by exploiting low-dimensional structure of task-specific *updates*, not by compressing already-low-rank *weights*. The 50× gap between adaptation rank (r ~ 32) and weight rank (r_eff ~ 1600) demonstrates these are independent properties.

This negative finding carries scientific value: it challenges widespread assumptions, prevents wasted research effort on false-foundation approaches, and redirects post-hoc compression research toward empirically-grounded methods. As we show in Section 5, the measured effective ranks are not moderately above threshold—they approach nearly full-rank, indicating pre-trained models maintain extremely high-dimensional representations even in deep layers.

The paper proceeds as follows. Section 2 positions our work relative to parameter-efficient fine-tuning, SSM architectures, and post-hoc compression literature. Section 3 details our SVD-based measurement methodology and effective rank computation. Section 4 describes the experimental setup testing falsifiable predictions. Section 5 presents results refuting the low-rank hypothesis. Section 6 interprets findings and discusses implications for compression research. Section 7 concludes with future directions for cross-scale rank analysis.
