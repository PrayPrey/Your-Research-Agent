# 1. Introduction

Trustworthiness evaluation frameworks for large language models (LLMs) implicitly assume that safety, fairness, truthfulness, adversarial robustness, privacy, and machine ethics are orthogonal axes — each measuring a distinct property that demands independent assessment. This assumption is operationalized in every major benchmark: TrustLLM [Sun et al., 2024] evaluates 16 models across 6 dimensions, HELM [Liang et al., 2022] tracks 7 metrics across 30 models, and MultiTrust [Zhang et al., 2024] presents 5 dimensions as a radar chart. Yet no study has asked the empirical question lurking underneath: *are these dimensions actually independent?*

We show they are not. After controlling for model scale (log parameter count) and RLHF alignment status, 8 of 15 trustworthiness dimension pairs are statistically correlated at Bonferroni-corrected significance, with partial Spearman coefficients reaching ρ = 0.971 for the safety–privacy pair. The correlation structure is not noise — it is a systematic geometry driven by RLHF preference training that co-optimizes 5 of 6 dimensions simultaneously, while adversarial robustness stands apart as the sole RLHF-insensitive axis.

This finding has two immediate practical implications. First, **evaluation compression**: a 3-dimension minimum evaluation set {truthfulness, fairness, privacy}, derived from the minimum spanning tree (MST) of the partial correlation matrix, spans the correlated cluster with 91.7% mean bootstrap edge stability — a 50% reduction from the standard 6-dimension protocol. Second, **differential attention**: adversarial robustness cannot be inferred from the 5-dimension cluster and requires separate evaluation, as it follows a trajectory governed by model scale rather than alignment.

**The key insight** driving these findings is that RLHF human preference annotation creates a pervasive shared optimization signal: annotators penalize harmful, unfair, and privacy-violating outputs through the same rating judgments, simultaneously lifting safety, ethics, fairness, privacy, and truthfulness. Adversarial robustness — which is never directly tested in preference annotation — escapes this shared pressure and follows an independent, scale-driven path.

This reframes trustworthiness evaluation as a geometry problem rather than a dimension-counting problem. Rather than asking "how does model X score on each of 6 dimensions?", the correct question is "what is the minimal set of dimensions that spans the trustworthiness correlation space?" — a question that existing evaluation frameworks do not address but that the MST formalism answers directly.

We make the following contributions:

1. **First systematic partial Spearman correlation analysis of LLM trustworthiness** — We compute the full 6×6 partial Spearman correlation matrix for TrustLLM's 16-model × 6-dimension evaluation data, controlling for model scale and RLHF status, revealing a strong 2-cluster structure (silhouette = 0.637, robust across all linkage methods) not previously reported.

2. **Robustness isolation principle** — Adversarial robustness is empirically identified as the sole RLHF-insensitive trustworthiness dimension, with 3/3 LLaMA-2 within-family pairs showing negative safety-to-robustness deltas after RLHF fine-tuning, consistent with a safety-robustness tension that is directional but attenuated at n=16.

3. **RLHF joint optimization of safety and ethics** — A within-family natural experiment on LLaMA-2 (7B, 13B, 70B) demonstrates that RLHF fine-tuning simultaneously increases safety (Δ = +0.63 average) and machine ethics (Δ = +0.42 average) at every scale, providing mechanistic evidence for the 5-dimension RLHF-shaped cluster.

4. **MST-derived minimum evaluation set** — The minimum spanning tree identifies {truthfulness, fairness, privacy} as a sufficient 3-dimension evaluation set with mean bootstrap edge frequency 0.917 (Tumminello, 2007 metric), enabling principled evaluation compression.

We organize the paper as follows: Section 2 surveys related work on trustworthiness benchmarking and benchmark correlation analysis. Section 3 describes our partial correlation and clustering methodology. Section 4 details the experimental setup. Section 5 presents results. Section 6 discusses implications and limitations. Section 7 concludes.
