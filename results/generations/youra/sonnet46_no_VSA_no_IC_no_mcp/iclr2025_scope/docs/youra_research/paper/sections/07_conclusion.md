# 7. Conclusion

We opened by observing that a correctly shaped evicted KV cache does not guarantee correct generation. Our experiments confirmed this observation precisely: the KV eviction shape was correct (2048/4096 positions per head, confirmed across all 32 transformer layers), the score function formulas were correct (matching SnapKV and H2O reference implementations), and yet generation produced F1=0.00 on every completed task. The full-KV baseline, identical in all other respects, produced coherent outputs at F1=0.0875. The difference was a single step: post-hoc DynamicCache reconstruction.

## Summary

This work makes three contributions:

1. **A documented failure mode:** Post-hoc reconstruction of DynamicCache from raw (key, value) tensors is incompatible with the transformers 5.x generation loop. The failure is silent — no exceptions are raised, shape verification passes, and the experiment appears to complete normally. The root cause is internal state inconsistency in the reconstructed cache object. The fix is to adopt forward-pass integration (LlamaAttention.forward() monkey-patching), as all major KV eviction implementations do.

2. **A reproducible baseline:** LLaMA-2-7B-chat-hf, LongBench 4-task QA (NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue), 100 examples per task, seed=42, 4K context, FP16, greedy decode — macro-F1=0.0875. This serves as the reference starting point for the corrected metric comparison experiment.

3. **A pre-validation protocol:** Run 5 examples with abort-on-degenerate-output before any full evaluation. A failed check triggers investigation of the cache integration approach, not the eviction policy.

## Future Directions

The results open several concrete directions:

**From the untested alternative explanation:** Position ID misalignment (resetting position IDs to contiguous 0..k after eviction) may partially restore generation quality even with a flawed DynamicCache reconstruction. Testing this alongside the monkey-patching fix would clarify whether DynamicCache format or position ID misalignment is the primary cause — useful for researchers on other transformer architectures.

**From the unverified core hypothesis:** The primary experiment — prefill-observation (M1) vs. cumulative-attention-at-prefill (M2) on LongBench 4-task QA at 50% KV retention — is ready to run with a corrected pipeline. If M1 outperforms M2 by ≥2 percentage points with a non-overlapping 95% bootstrap CI, it confirms that query-conditioned KV retention is a meaningfully better eviction criterion for extractive QA than global cumulative attention.

**From scope extensions:** The controlled ablation design can be extended to the timing dimension (H2O-at-prefill vs. H2O-at-decode, isolating eviction timing from metric type) and to other task types (summarization tasks GovReport and QMSum, testing whether the metric advantage is task-conditional). Cross-model validation on LLaMA-3 and Mistral-7B would establish whether the protocol findings and metric comparison results generalize across architectures.

## Closing

The KV eviction literature has progressed rapidly by proposing new importance metrics, but rigorous cross-method comparisons under identical conditions remain scarce. We set out to provide one such comparison and instead found a failure mode that prevents it from running. We document that failure mode in enough detail to prevent others from reproducing it — and provide all the infrastructure needed to run the comparison correctly. The hypothesis that prefill-observation outperforms cumulative-attention on long-context QA tasks remains open, theoretically motivated, and empirically accessible with the corrected implementation.
