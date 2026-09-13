# Conclusion

We asked whether data attribution method performance depends on model architecture, and found that it does—but the patterns differ from theoretical predictions.

Our matched comparison of BERT-base and GPT-2 on SST-2 mislabeled detection reveals three key findings. First, **TRAK exhibits remarkable architecture-invariance**, with less than 1% AUC difference across architectures at all compute budgets. Its random projection mechanism averages out architecture-specific gradient patterns, making it the robust choice for cross-architecture work. Second, **TracIn shows a directional BERT advantage** (~3%), suggesting its gradient dot-product approximation benefits from dense bidirectional gradients. Third, **EK-FAC does not show the predicted GPT-2 advantage**, contrary to theoretical expectations—its Kronecker approximation appears equally applicable to both attention structures.

We validated the causal mechanism underlying these patterns: attention sparsity differs by 98.8% between architectures, creating an 11× Hessian eigenvalue difference. This structural difference propagates through the loss landscape, interacting with each method's approximation strategy.

Returning to our opening question: when choosing attribution methods across architectures, practitioners can now rely on TRAK for consistent performance. Architecture-agnostic attribution is possible—random projection provides the key.

## Future Work

Several directions extend this work:

**Scale.** Testing at 1B+ parameters would reveal whether EK-FAC's predicted decoder advantage emerges at larger scales, and whether TRAK's invariance holds.

**Tasks.** Replicating on MNLI, SQuAD, and other benchmarks would establish generalization beyond sentiment classification.

**Architectures.** Encoder-decoder models (T5, BART) may show hybrid patterns; sparse attention variants warrant investigation.

**Statistical Power.** Adequately-powered studies (5+ seeds) would confirm the directional TracIn and EK-FAC patterns observed here.

**Method Development.** Understanding *why* random projection provides architecture-agnosticism could inspire new attribution methods designed for cross-architecture robustness.

The tools for architecture-aware attribution selection are now clearer. We look forward to their application in improving model transparency across the diverse landscape of deployed foundation models.
