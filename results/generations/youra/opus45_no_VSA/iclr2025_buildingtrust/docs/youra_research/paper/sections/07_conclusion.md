# Conclusion

When state-of-the-art language models excel on one trustworthiness benchmark, they systematically excel on others—a pattern we set out to explain. Through large-scale meta-analysis of 4,561 models, we demonstrate that this correlation is not a scale confound to be dismissed but a signal revealing a latent factor: Generalized Representational Coherence.

GRC persists after controlling for model size and training recency (λ₁ = 2.277, 60% variance, p = 0.001). It correlates with behavioral stability (ρ = 0.405), linking the factor to a plausible mechanism: models with more consistent internal representations perform better across diverse trustworthiness dimensions. Instruction-tuning increases both stability and factor scores with large effect sizes (d ≈ 2.0), suggesting that alignment training does more than shape outputs—it shapes the underlying representational structure.

The GRC factor generalizes to five of six holdout benchmarks, demonstrating that it captures a genuine latent dimension rather than benchmark-specific artifacts. The exception—Ethics loading below threshold—suggests that normative reasoning may require distinct capabilities beyond stability-driven coherence, warranting future investigation.

Our findings have practical implications. If trustworthiness is substantially one factor, evaluation can be more efficient: a single composite score may capture most of what multi-benchmark batteries measure separately. Training can be more targeted: procedures that increase representation stability—like instruction-tuning—may provide broad trustworthiness improvements without dimension-specific intervention.

Looking forward, we see GRC-aware evaluation and training as a promising direction. Prospective validation on independently released benchmarks and activation-level stability analysis will strengthen the mechanistic account. The high correlation that initially seemed like a confound may ultimately point toward a unified understanding of what makes language models trustworthy.

The pervasive ρ = 0.80–0.87 correlation across trustworthiness benchmarks is not noise. It is evidence that beneath the surface-level diversity of evaluation tasks lies a shared structure—one that instruction-tuning improves and that future work can target directly.
