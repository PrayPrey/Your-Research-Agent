# Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning

## Key Metadata
- **Authors:** Aghajanyan et al.
- **Year:** 2021
- **Venue:** ACL 2021
- **Core Contribution:** Demonstrates that pre-trained language models have very low intrinsic dimensionality, which explains why fine-tuning works with so few parameters.

## Section Summaries

### Abstract
We argue that pre-training implicitly minimizes the intrinsic dimensionality of the fine-tuning objective. Models fine-tuned in a low-dimensional subspace can match full fine-tuning performance. The intrinsic dimension d_90 (minimum dimension retaining 90% of full performance) is used as the metric and varies dramatically across tasks and model scales.

### Introduction & Motivation
Standard fine-tuning updates all parameters, but empirical evidence shows models can be fine-tuned in surprisingly low-dimensional subspaces. This suggests pre-training produces a rich, low-dimensional solution manifold. The paper asks: how many dimensions are truly needed to fine-tune an LM? The answer varies per layer and per task — foundational motivation for per-layer rank adaptation.

### Methodology
Uses the Fastfood transform to project parameter updates into a d-dimensional subspace: θ = θ₀ + Mθ_d where M ∈ ℝ^D×d is a random matrix. Sweeps d from 10 to 10,000. Reports d_90 = smallest d achieving 90% of full performance. Measures d_90 across: RoBERTa-base, RoBERTa-large, GPT-2, ALBERT on SST-2, SNLI, MRPC. Key finding: larger pre-trained models have LOWER intrinsic dimension (d_90 decreases as model size increases). RoBERTa-large has d_90 ≈ 200 on SST-2 vs RoBERTa-base d_90 ≈ 1000. Critical: intrinsic dimension VARIES across layers — some layers are essentially frozen by pre-training while others retain high adaptability. Layer-wise analysis shows attention layers typically have lower intrinsic dimensionality than FFN layers.

### Experiments & Results
SST-2: RoBERTa-base d_90 = 974, RoBERTa-large d_90 = 217. SNLI: base d_90 = 4,283, large d_90 = 1,796. MRPC: base d_90 = 1,388, large d_90 = 207. Pattern: more pre-training → lower intrinsic dimension. Cross-model: GPT-2 shows similar trends. Layer-wise variation is statistically significant (Levene test) when grouping by layer type (attention vs FFN vs embedding).

### Discussion & Conclusion
Pre-training is essentially a compression into a low-dimensional parameter manifold. This directly motivates low-rank adaptation (LoRA): if the optimal update lives in a low-dimensional subspace, a low-rank matrix approximates it well. Limitation: d_90 is measured empirically via sweep — no closed-form predictor from W₀ structure. Future work: can W₀ structure predict d_90 per layer?

## Key Contributions
- Intrinsic dimensionality as a measure of fine-tuning complexity
- Empirical evidence that pre-training reduces intrinsic dimension
- Layer-wise variation in intrinsic dimensionality (foundational for per-layer rank)

## Potential Relevance
This paper is the primary theoretical motivation for the erank hypothesis. Aghajanyan shows layers have different intrinsic dimensionalities — the erank hypothesis proposes that erank(W₀) is the predictor of this per-layer complexity. The layer-type (attention vs FFN) Levene test significance found here directly validates using layer-type grouping in the tercile analysis.
