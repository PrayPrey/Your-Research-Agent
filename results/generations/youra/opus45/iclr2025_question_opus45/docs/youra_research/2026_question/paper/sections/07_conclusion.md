# Conclusion

We set out to create efficient semantic entropy proxies via similarity-augmented hidden state probes. Instead, we discovered that a reasonable configuration—layer 25, TBG token position, logistic regression on Llama-3-8B-Instruct—achieves correlation indistinguishable from random guessing (ρ = 0.0843, AUROC = 0.52).

This negative result carries important implications. The 39% AUROC gap between our implementation and published benchmarks reveals configuration sensitivity that practitioners must address before deploying SE probes. A production system using the wrong layer or token position could silently fail, providing no meaningful uncertainty signal despite appearing to function correctly.

Our contributions are threefold:

1. We document complete failure of SE probing under a reasonable configuration, demonstrating that success is not guaranteed even when following published guidance.

2. We identify a significant replication gap that highlights the need for systematic configuration validation in probe-based uncertainty quantification.

3. We propose that SE probe deployment requires ablation across layers, token positions, and architectures—moving beyond plug-and-play application of literature configurations.

Looking forward, this failure motivates several research directions. Systematic layer ablation (layers 20-31) would locate where SE information actually resides in Llama-3-8B. Token position comparisons (TBG vs. SLT vs. pooling) would characterize position sensitivity. Nonlinear probes may capture patterns that logistic regression misses. Multi-dataset evaluation would assess whether our findings generalize beyond TruthfulQA.

More ambitiously, the field needs configuration-agnostic probing methods—approaches robust to layer and position choices—or automated search protocols that find optimal configurations without exhaustive manual tuning.

Understanding where methods fail is as important as celebrating where they succeed. Our failure charts the path toward robust SE probing: systematic validation, honest reporting of negative results, and recognition that configuration details are not footnotes but first-order research concerns.
