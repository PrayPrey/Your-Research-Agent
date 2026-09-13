# Research Idea

## Title
Sparse Dual-Potential Attention: Leveraging q-Deformed Optimal Transport for Faithful Transformer Interpretability

## Motivation
Transformer attention weights are widely used for model interpretation, yet recent studies reveal they suffer from faithfulness violations—top-attended tokens often don't correspond to actual prediction drivers. Meanwhile, duality principles from optimal transport remain underexploited in deep learning interpretability. This gap motivates exploring whether mathematically grounded dual potentials can provide more faithful explanations than heuristic attention weights.

## Main Idea
We propose replacing softmax attention with q-deformed optimal transport (using Tsallis entropy regularization, q∈[0.5,0.8]) and extracting Kantorovich dual potentials as interpretability scores. The core mechanism operates through four causal steps: (1) Tsallis entropy induces sparse attention matrices, (2) sparsity prevents spectral collapse that plagues dense doubly-stochastic attention, (3) preserved expressivity enables meaningful dual potential extraction, and (4) dual potentials—representing marginal contributions to transport cost—provide optimization-grounded sensitivity measures.

We will evaluate on BERT and ViT using SaCo coefficients and faithfulness violation rates, comparing against raw attention, integrated gradients, and attention rollout. We predict >10% faithfulness improvement while maintaining accuracy within 2% of baselines. This work bridges optimal transport theory with practical interpretability, demonstrating how classical duality principles can enhance modern deep learning explanation methods.