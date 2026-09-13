# Introduction

A probe trained to detect hallucinations on one LLM family should fail when transferred to another. Different architectures, different training corpora, different hidden representations — surely the internal encoding of uncertainty is model-specific. Yet when we train a simple linear probe on Llama-3-8B and apply it to Mistral-7B hidden states, we observe a transfer gap of only 0.010. Across all six cross-family pairs we test, the maximum gap is 0.034.

This finding has practical implications. Multi-sample semantic entropy [Farquhar et al., 2024] detects hallucinations with AUROC 0.75–0.90, but requires 5–10 forward passes per query — prohibitive for real-time applications. Semantic Entropy Probes (SEPs) [Kossen et al., 2024] achieve comparable accuracy with a single forward pass by training a linear classifier on hidden states. If these probes must be retrained for every model deployment, their practical value diminishes. But if probes transfer, a single trained detector serves multiple LLM families.

The problem runs deeper than computational cost. Prior work establishes that hidden states encode uncertainty [Kossen et al., 2024], but the cross-family generalization of this encoding remains untested. Existing studies validate SEPs within individual models; none systematically examine whether probes trained on Meta's Llama transfer to Mistral AI's or Alibaba's Qwen families. This gap matters because model diversity is increasing — production systems routinely swap between providers, and uncertainty estimation cannot require per-model retraining to remain viable.

We address this gap with a systematic study of cross-family probe transfer. Our key insight is that transformer hidden states encode uncertainty in an architecture-invariant geometric structure. Despite differences in layer count (28 vs 32), hidden dimension (3584 vs 4096), and training procedures, the uncertainty signal at layer 2/3 depth lies in a subspace that transfers via simple affine alignment.

Building on this insight, we make three contributions:

1. **Cross-family transfer validation.** We demonstrate that SEPs transfer across three LLM families (Llama-3, Mistral, Qwen-2) with mean AUROC gap of 0.013 and maximum gap of 0.034 — well below the 0.10 threshold that would indicate architecture-specific encoding.

2. **Affine alignment for dimension mismatch.** We show that least-squares affine mapping enables transfer between models with different hidden dimensions (Qwen's 3584 to Llama/Mistral's 4096), recovering discriminative structure with gaps as small as 0.003.

3. **Evidence for convergent uncertainty encoding.** Our transfer matrix provides empirical support for the hypothesis that uncertainty is a fundamental property of transformer computation, not an architectural accident.

The remainder of this paper is organized as follows. Section 2 reviews semantic entropy, probing methods, and cross-model transfer. Section 3 describes our methodology, including probe training and affine alignment. Section 4 presents experimental setup and Section 5 reports results. Section 6 discusses implications and limitations, and Section 7 concludes.
