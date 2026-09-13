# 2. Related Work

## 2.1 Uncertainty Quantification in LLMs

Early work on LLM uncertainty relies on token-level conditional probabilities, but RLHF-trained models exhibit poor calibration between confidence and accuracy \citep{tian2023just}. Verbalized confidence ("I am 80% sure") often outperforms raw probabilities for post-RLHF models.

**Semantic entropy** \citep{kuhn2023semantic} addresses linguistic invariance by clustering semantically equivalent generations before computing entropy. This achieves strong detection performance (AUROC ~0.75 on TruthfulQA) but requires 5-10 samples per query. **SelfCheckGPT** \citep{manakul2023selfcheckgpt} provides black-box consistency checking via sampling and cross-referencing, again requiring multiple generations.

Probe-based methods avoid multi-sampling by training classifiers on internal representations. \citet{kadavath2022language} show models can evaluate $P(\text{True})$ for their own claims. **MIND** \citep{su2024mind} uses internal states for real-time unsupervised detection. **Semantic entropy probes** \citep{kossen2024semantic} demonstrate that lightweight linear classifiers on hidden states approach the accuracy of full semantic entropy computation.

## 2.2 Cross-Layer Analysis

The **logit lens** \citep{nostalgebraist2020logitlens} projects intermediate representations through the final unembedding matrix, revealing per-layer probability distributions. **END decoding** \citep{wu2025end} demonstrates that cross-layer entropy correlates with factuality. Our work formalizes this observation into trajectory metrics (NTI, CMI) and validates them with controlled experiments.

\citet{elhage2022toy} and \citet{belrose2023tuned} provide theoretical foundations for understanding iterative refinement in transformers, informing our interpretation of RCI flip patterns as architectural rather than epistemic.

## 2.3 Positioning

| Method | Single-Pass | No External DB | Interpretable | Validated |
|--------|-------------|----------------|---------------|-----------|
| Semantic Entropy | No | Yes | Moderate | Yes |
| SelfCheckGPT | No | Yes | High | Yes |
| MIND | Yes | Yes | Low | Partial |
| **CLTI (Ours)** | **Yes** | **Yes** | **High** | **Yes** |

CLTI occupies a unique position: single-pass (no sampling overhead), interpretable (trajectory metrics have clear geometric meaning), and validated with both positive and negative results.
