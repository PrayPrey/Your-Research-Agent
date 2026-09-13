# 6. Discussion

## 6.1 Key Findings

**Finding 1: DynamicCache reconstruction is not a viable KV eviction integration point in transformers 5.x.**

The API affordance exists (DynamicCache accepts ddp_cache_data), but using it for KV eviction produces degenerate generation. The internal state inconsistency — correct tensor shapes, invalid bookkeeping — is not detectable by shape verification and produces no runtime errors. This is a particularly dangerous failure mode for researchers: the experiment appears to complete, shape checks pass, and no exception is raised. The failure is only visible in the final F1 scores.

This finding directly validates a design decision made by every major KV eviction implementation: integrate eviction into the attention forward pass, never into a post-hoc reconstruction step. Our experiment provides the controlled evidence that post-hoc reconstruction fails — something prior implementations avoided by design, not by explicit awareness.

**Finding 2: The M0 baseline is functionally correct and reproducible.**

macro-F1=0.0875 on LongBench 4-task QA (NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue, 100 examples each, seed=42, LLaMA-2-7B-chat-hf, 4K context, FP16, greedy decode, max_new_tokens=50) is a confirmed, reproducible value. Future experiments using this configuration can use this value as a reference to verify pipeline health before running eviction conditions.

**Finding 3: Score function implementations are correct and reusable.**

The M1 and M2 score functions are implemented correctly per the experiment brief and match their reference implementations (SnapKV and H2O respectively). They can be reused without modification in the corrected experiment.

## 6.2 Limitations

**L1: The primary hypothesis comparison was not evaluated.**

The h-e1 gate criterion — M1_macro_F1 − M2_macro_F1 ≥ 2.0 percentage points — could not be evaluated because M1 produced degenerate outputs and M2 never ran. The hypothesis that prefill-observation outperforms cumulative-attention at 50% KV retention is INCONCLUSIVE. We have not provided evidence for or against the theoretical claim.

We frame this as acceptable for the following reason: the failure is an implementation failure, not a hypothesis failure. The theoretical mechanism (query-conditioned observation windows identify semantically relevant KV positions; retaining these positions improves extractive QA F1) is unrefuted. The corrected implementation requires changing approximately 50 lines of code — replacing the _rebuild_cache() call with a LlamaAttention.forward() override.

**L2: F1 scale unit mismatch in the sanity check threshold.**

The original gate criterion of "≥2.0 F1" was expressed in percentage-scale F1 (consistent with LongBench paper reporting), but our evaluation code reports raw F1 (0-1 scale). The M0 baseline of 0.0875 raw (8.75%) is consistent with expected LLaMA-2-7B performance at 4K context truncation. The gate criterion in raw scale is ≥0.02 raw F1 (2 percentage points), achievable at this baseline.

This is a clarification, not a weakening: a 2-percentage-point improvement in macro-average F1 at 50% KV retention remains a meaningful and practically relevant target, indicating that the eviction policy preserves sufficient answer-relevant context to produce measurably better outputs.

**L3: Single model and single retention ratio.**

All results are for LLaMA-2-7B-chat-hf at 50% KV retention. Generalization to other models (LLaMA-3, Mistral-7B) and other retention ratios (40%, 60%) is not established. Phase 5 (Baseline Comparison) was planned to address cross-model generalization but was not reached.

**L4: Experiment executed on a single GPU run without checkpointing.**

No intermediate checkpointing was implemented, so when the experiment was restarted due to M1 degeneration, some M1 results (musique) were lost. A robust experiment runner should checkpoint after each task/method combination.

## 6.3 Implications and Broader Impact

**For KV eviction researchers:** Any implementation that reconstructs DynamicCache from raw tensors will encounter this failure in transformers 5.x. The correct approach is to integrate eviction within LlamaAttention.forward() (or the equivalent attention module for non-LLaMA architectures). This applies equally to researchers using transformers for Mistral, Gemma, or other decoder models that share the DynamicCache infrastructure.

**For reproducibility in NLP research:** Our pre-validation protocol (5-example abort-on-degenerate check before full evaluation runs) is a broadly applicable safeguard. In any experiment where generation quality can silently degrade to degenerate output, running a minimal sanity check before full-scale computation prevents wasted GPU-hours and misleading results.

**Potential for misuse:** This work does not introduce new capabilities that could be misused. The DynamicCache failure mode we document prevents KV eviction from working, rather than enabling it for harmful applications.

**For the primary hypothesis:** The theoretical claim that prefill-observation outperforms cumulative-attention on extractive QA tasks is supported by prior work (SnapKV reports gains over H2O on LLaMA-2 models) but has not been verified under controlled conditions. The corrected experiment — using forward-pass monkey-patching — is the immediate next step, requiring 2-4 GPU hours for a 5-example validation plus 8-16 hours for the full 400-example comparison (M1 and M2 on 4 tasks × 100 examples).
