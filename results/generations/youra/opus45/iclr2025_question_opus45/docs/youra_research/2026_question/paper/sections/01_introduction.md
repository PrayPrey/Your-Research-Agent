# Introduction

Semantic Entropy Probes promise single-pass hallucination detection by distilling multi-sample uncertainty into hidden state predictions. We attempted to extend this approach with similarity-augmented training for cross-model transfer—and discovered that the straightforward application achieves correlation indistinguishable from random guessing. Specifically, our SE-Distilled Probe (SEDP) achieved Spearman rho = 0.0843 with true semantic entropy, failing our existence proof threshold (rho ≥ 0.3) by 72%, with AUROC = 0.52 (random baseline = 0.50).

This finding matters because semantic entropy (SE) represents the gold standard for hallucination detection in large language models, achieving AUROC 0.76-0.97 across benchmarks. However, computing SE requires generating 10-20 diverse responses per query and clustering them via natural language inference—a 5-10x computational overhead that prohibits real-time deployment. Semantic Entropy Probes (SEPs) offer an elegant solution: train a lightweight probe on hidden states to predict SE in a single forward pass. Published results report SEPs achieve AUROC within 2-3% of full SE on TruthfulQA.

Yet our replication reveals a troubling gap. Following the recommended configuration—layer 25 of Llama-3-8B-Instruct, Token-Before-Generation position, logistic regression probe—we achieved AUROC = 0.52, a 39% deficit relative to published results (~0.85). This is not a minor discrepancy; it represents the difference between a useful uncertainty quantifier and random noise.

The deeper problem is that SE probe effectiveness depends critically on configuration choices that remain underspecified. Published work reports optimal settings but does not characterize the failure modes when practitioners inevitably deviate from these settings. A production system using SEPs without careful validation could perform no better than random, despite published benchmarks suggesting otherwise. For high-stakes applications—medical diagnosis support, legal document analysis, financial advisory systems—such silent failures are unacceptable.

Our investigation reveals that hidden states at layer 25 of Llama-3-8B-Instruct do not encode semantic entropy information in a way that linear probes can extract. This contradicts the implicit assumption that SE information is broadly distributed across middle-to-late layers. Instead, the SE signal appears highly localized, requiring systematic ablation to identify—an effort that current work does not emphasize.

Building on this finding, we make the following contributions:

1. **Documentation of complete probe failure**: We demonstrate that a reasonable SE probe configuration (layer 25, TBG token, logistic regression on Llama-3-8B) achieves Spearman rho = 0.0843 with true SE—statistically indistinguishable from zero correlation.

2. **Identification of a significant replication gap**: We report a 39% AUROC gap between our baseline SEP implementation and published results on the same benchmark (TruthfulQA), highlighting configuration sensitivity that practitioners must address.

3. **Guidance for robust deployment**: We propose that SE probe deployment requires systematic validation across layers, token positions, and probe architectures—not plug-and-play application of published configurations.

Our negative result serves the community by exposing failure modes that positive-result publications naturally omit. Understanding where methods fail is as important as celebrating where they succeed.

The remainder of this paper is organized as follows. Section 2 reviews related work on semantic entropy and uncertainty probing. Section 3 describes our methodology, including the SEDP architecture and experimental design. Section 4 details our experimental setup, and Section 5 presents results demonstrating the failure. Section 6 discusses implications and limitations, and Section 7 concludes with directions for future work.
