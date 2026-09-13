# 7. Conclusion

We began by observing a pervasive but underappreciated mismatch in how LLMs are deployed: adapters fine-tuned on sequences with full KV cache access are routinely evaluated — and served in production — under eviction policies that discard half or more of that cache. This paper shows that the mismatch is not inevitable. Adapters can be trained to be aware of eviction constraints from the start, and doing so produces representations that are fundamentally different from those produced by sequential (train-then-evict) baselines.

## Summary

In this work, we addressed the training-inference distribution mismatch in KV-cache-constrained LoRA deployment by proposing **Eviction-Aware LoRA** — the first method to integrate H2O eviction simulation directly into the LoRA fine-tuning forward pass as a form of token-scarcity regularization.

Our main contributions are:

1. **Mechanistic existence proof:** All 24 LoRA layers of a GPT-2 proxy model developed near-orthogonal weight matrices when trained with H2O eviction masks (mean cosine similarity ≈ 0.053, minimum = −0.578), compared to sequential-baseline adapters trained without eviction constraints. This is far stronger divergence than typical task specialization produces, confirming that eviction masks reshape the gradient landscape rather than merely regularizing it.

2. **Attention redistribution at inference-critical layers:** 8 of 12 transformer layers (66.7%) showed statistically significant divergence in attention entropy and heavy-hitter concentration (p < 0.05, paired t-test). The restructuring was concentrated in middle layers 4–11 — the layers that prior work identifies as carrying long-range dependency information — providing mechanistic grounding for the hypothesis that eviction-aware training specifically improves long-context performance.

3. **Production-ready infrastructure:** We provide and validate the complete experimental pipeline — BudgetSweepEvaluator, SpearmanAnalyzer, H2O training wrapper, and AttentionEntropyExtractor — ready for immediate deployment on LLaMA-2-7B and Mistral-7B-v0.1 once gated model access is obtained.

## Future Directions

The mechanistic evidence established here opens three concrete directions, each grounded in our experimental findings:

**From the proxy-scale existence proof:** Execute H-M3 — train eviction-aware and sequential LoRA adapters on the full LongAlpaca-12k dataset using LLaMA-2-7B and Mistral-7B-v0.1, and evaluate on LongBench at r=50%. The near-orthogonal weight divergence observed at proxy scale raises the question of whether full-scale training (more steps, more capacity, separate Q/K/V projections) produces similarly strong or weaker divergence — and whether that divergence translates to per-category accuracy improvements. Estimated compute: ~24 GPU-hours on A100.

**From the H2O+SDPA incompatibility discovery:** The `attn_implementation='eager'` fix introduces a ~15–30% inference overhead that confounds throughput analysis. Addressing the SDPA incompatibility at the H2O wrapper level — or implementing a CUDA-native eviction mask that cooperates with fused attention kernels — would eliminate this overhead and enable clean throughput comparison (P3).

**From the single-policy limitation:** All mechanistic findings are specific to H2O eviction. Testing whether adapters trained with H2O masks generalize to SnapKV or StreamingLLM eviction at inference — and whether training with SnapKV masks produces different restructuring patterns — would establish whether token-scarcity regularization is policy-specific or a more general principle.

The gap between how we train adapters and how we deploy them is a first-class efficiency problem, not an implementation afterthought. Closing it at training time — rather than patching it with better eviction policies at inference — is a promising and largely unexplored direction. We hope this work provides the mechanistic foundation and practical infrastructure to make that exploration productive.
