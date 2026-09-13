# Introduction

Foundation models trained with billions of parameters rely on massive datasets curated through deduplication, perplexity filtering, and domain mixing—yet practitioners repeatedly re-optimize these techniques at every training stage, from pre-training to fine-tuning to RLHF, without knowing which curation decisions transfer across stages. This redundant optimization wastes compute and delays model deployment: pre-training C4 with deduplication threshold 0.7, then re-tuning the same threshold for Dolly fine-tuning, then again for RLHF—tripling curation effort without principled guidance on what actually requires stage-specific tuning.

The problem runs deeper than inefficiency. Existing curation research treats each training stage in isolation: DataComp optimizes pre-training filtering, Alpagasus refines instruction fine-tuning data, and RLHF preference selection operates independently. No systematic understanding exists of which curation components are universal across stages versus which require stage-specific adaptation. When a practitioner curates fine-tuning data, should they reuse pre-training deduplication thresholds or re-optimize from scratch? Current practice defaults to re-optimization, but this may be unnecessary for operations that address universal data hygiene properties.

Our key insight is that **curation operations exist on a spectrum from objective-independent to objective-dependent**. Low-level quality filters like deduplication and perplexity-based outlier removal operate on surface statistics—n-gram overlap, token probability—that remain invariant across training objectives. High-level strategies like domain mixing and task-specific filters directly depend on what the model is being trained to do at each stage. This distinction predicts transfer behavior: operations with low mutual information I(filter_decision; stage_objective) should transfer robustly, while those tightly coupled to stage goals require re-tuning.

We validate this hypothesis through systematic experiments across pre-training (C4) and fine-tuning (Dolly, Alpaca) stages. Testing four sub-hypotheses—existence of transfer-stable categories, cross-stage threshold transfer, categorical separation by objective-dependence, and quality-speed trade-offs—we find that low-level filters transfer with ≤1% performance delta while high-level strategies show >5% degradation when transferred. Optimal deduplication and perplexity thresholds remain identical across stages (dedup=0.7, perplexity=500), while instruction quality filters require stage-specific tuning.

**Our contributions are:**

1. **First empirically-grounded taxonomy** categorizing data curation techniques by transfer stability across foundation model training stages, with quantified thresholds (≤1% robust, >5% sensitive).

2. **Validated mechanism:** Objective-independence predicts transfer behavior. We demonstrate categorical separation between universal data hygiene operations (0.38% average delta, Cohen's d=10.76) and stage-specific optimization targets (5.04% delta) through experiments on standard benchmarks.

3. **Practical guidelines:** Practitioners can reuse C4 pre-training thresholds (dedup 0.7-0.8, perplexity 500-1000) for fine-tuning without re-optimization, while focusing stage-specific tuning on domain mixing and task filters. We quantify quality-speed trade-offs for two-stage curation pipelines: early-stage embeddings achieve 98% of late-stage quality at 15% of compute cost.

This work shifts the paradigm from per-stage curation optimization to transfer-aware design, enabling shared infrastructure for universal operations while preserving flexibility for stage-specific strategies.
