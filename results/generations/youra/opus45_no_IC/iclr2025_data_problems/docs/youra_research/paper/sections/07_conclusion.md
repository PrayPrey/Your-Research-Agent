# Conclusion

We return to our opening question: how much does benchmark contamination inflate language model scores? Our checkpoint-gradient analysis provides the first quantitative answer: contamination-inflation correlation is real and measurable, with Spearman r ≈ 0.3 across Pythia model checkpoints.

This moderate correlation has important implications. Contamination does systematically inflate benchmark scores, confirming concerns about evaluation validity. Yet the effect is not overwhelming—capability remains the primary driver of benchmark performance. This suggests benchmark evaluation remains meaningful, but would benefit from contamination-aware correction.

Our methodological contributions—checkpoint-gradient analysis and capability detrending—enable contamination-performance studies without requiring contamination-free baseline models. By treating training checkpoints as a natural contamination gradient and using out-of-distribution perplexity to separate capability from memorization, we provide tools applicable to any model family with documented training.

Looking forward, we envision contamination-adjusted benchmark scores as standard practice. Just as statistical analyses correct for known confounds, model evaluation could correct for measured contamination effects. Our transfer function framework provides the foundation: given contamination measurements, estimate inflation and adjust accordingly.

Several directions merit investigation. Extending checkpoint-gradient analysis to other model families would establish generalizability. Full corpus indexing would provide definitive overlap statistics. Semantic contamination detection would capture effects beyond verbatim n-gram matching. And verifying the full causal chain—from exposure through memorization to performance—would strengthen theoretical foundations.

The path from contamination detection to contamination correction is now open. Our work takes the first step, demonstrating that contamination impact is not merely present but predictable.
