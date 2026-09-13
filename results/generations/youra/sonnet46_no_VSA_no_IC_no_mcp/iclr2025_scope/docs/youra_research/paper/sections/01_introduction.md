# 1. Introduction

A correctly shaped evicted KV cache does not guarantee correct generation. In our experiment, the top-k KV eviction step reduced the per-head cache from 4096 to 2048 positions — exactly as designed, confirmed by shape logs across all 32 transformer layers. Yet the model produced empty or repetitive text on every generation attempt, yielding F1=0.00 on three LongBench QA tasks. The same pipeline, with eviction removed, produced coherent answers at F1=0.0875. The sole difference between the working and broken condition was a single step: post-hoc reconstruction of a DynamicCache object from raw (key, value) tensors.

This paper reports that failure, diagnoses its cause, and provides the corrected implementation protocol.

## The Memory Bottleneck in Long-Context Inference

Autoregressive generation with transformer models stores intermediate key and value projections for every generated token — the KV cache — enabling efficient attention over the growing context. For long documents, this cache grows linearly with sequence length, becoming the primary memory bottleneck in inference. A 7B-parameter model with a 32K context window requires tens of gigabytes just for the KV cache at float16 precision, limiting throughput on practical hardware.

KV cache eviction addresses this by retaining only a fraction of historical KV entries — those deemed most important for generating the next token. A growing body of work (H2O [Zhang et al., 2023], SnapKV [Li et al., 2024], ScissorHands [Liu et al., 2023]) has proposed different importance metrics: cumulative attention accumulation, prefill-phase query-conditioned observation windows, and persistence-based static schedules. These methods report strong results on standard benchmarks, but they have been evaluated on disjoint benchmarks with different models and different eviction timing assumptions, making direct comparison impossible.

## The Deeper Problem: Confounded Comparisons and Silent API Failures

A fair comparison of KV eviction metrics requires holding everything constant except the importance score function: same model, same dataset, same eviction timing, same codebase. No published work provides this controlled ablation. Our research set out to fill this gap — comparing prefill-observation importance scoring (SnapKV-style) against cumulative-attention scoring (H2O-style) on LongBench QA tasks under matched conditions.

In doing so, we encountered a failure mode that no KV eviction paper documents: post-hoc reconstruction of a DynamicCache object from raw (key, value) tensors, using the DynamicCache(ddp_cache_data=...) constructor, is incompatible with the transformers 5.x API. The reconstructed cache object has correct tensor shapes but invalid internal state, causing the generation loop to reference wrong positions and produce degenerate output. The library raises no error. Shape verification passes. The experiment appears to complete successfully — yet all generated text is meaningless.

This failure mode went unnoticed in prior work because all major KV eviction implementations (SnapKV, H2O, ScissorHands) integrate eviction directly into the attention forward pass, overriding LlamaAttention.forward() to modify past_key_values in-place before each layer commits its KV tensors. They never require post-hoc reconstruction.

## Key Insight

KV eviction in modern transformer libraries must be integrated into the attention forward pass — not applied post-hoc to the cache object. The DynamicCache data structure in transformers 5.x stores KV tensors with internal bookkeeping that cannot be safely replicated by reconstructing the object from raw tensor tuples. The correct approach, demonstrated by SnapKV, is to override the attention module's forward method, applying eviction within the computation before the layer appends to past_key_values.

This insight is immediately actionable. The score function implementations we developed (M1: mean attention over the last W=16 query tokens at prefill end; M2: cumulative attention sum over all prefill steps) are mathematically correct and match the reference implementations. Only the integration point needs to change.

## Contributions

Our work contributes:

1. **A documented failure mode:** Post-hoc DynamicCache reconstruction is incompatible with transformers 5.x for KV eviction experiments. We provide the root cause analysis, the diagnostic evidence (shape correct, generation degenerate), and the corrected protocol (forward-pass monkey-patching).

2. **A reproducible M0 baseline:** LLaMA-2-7B-chat-hf at 4K context on LongBench 4-task QA (NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue), 100 examples per task, seed=42, greedy decode, FP16 — macro-F1=0.0875. This serves as the reference baseline for the corrected metric comparison experiment.

3. **Verified score function implementations:** The M1 (prefill-observation) and M2 (cumulative-at-prefill) score functions are implemented, code-reviewed, and confirmed to match their reference implementations. They are ready for use with a corrected integration approach.

4. **A pre-validation protocol:** A 5-example sanity check with abort-on-degenerate-output (F1=0.00 triggers abort) should precede any full evaluation run. This check would have identified the DynamicCache bug in 3 minutes instead of allowing a 30-minute degenerate run to complete.

The hypothesis motivating this work — that prefill-observation importance scoring outperforms cumulative-attention scoring on extractive QA at 50% KV retention — is theoretically sound, has correct score function implementations, and remains empirically untested (not refuted). We describe the complete experimental design and provide all components needed to execute it with the corrected implementation.

The remainder of this paper is organized as follows. Section 2 surveys related KV eviction methods and explains why the failure mode we encountered did not appear in prior work. Section 3 describes our experimental framework, the score function implementations, and the DynamicCache failure in detail. Section 4 presents our experimental design. Section 5 reports results: M0 baseline metrics, shape verification evidence, and M1 degeneration diagnostics. Section 6 discusses implications and the corrected implementation protocol. Section 7 concludes.
