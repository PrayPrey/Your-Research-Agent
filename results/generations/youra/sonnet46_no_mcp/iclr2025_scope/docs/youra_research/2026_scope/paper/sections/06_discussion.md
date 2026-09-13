# 6. Discussion

## 6.1 Interpretation of Mechanistic Findings

**Near-orthogonal weight divergence is stronger than expected.** The mean cosine similarity of 0.053 between eviction-aware and sequential adapter weights after 30 training steps is substantially lower than typical LoRA specialization produces. When the same architecture is fine-tuned on different tasks (e.g., summarization vs. QA), cosine similarities typically remain > 0.8. When fine-tuned with different random seeds on the same task, similarities stay > 0.95. Finding near-orthogonal weights after 30 steps on 200 samples suggests that H2O eviction masks do not merely introduce noise or mild regularization — they reshape the gradient landscape fundamentally. The surviving heavy-hitter tokens must now carry all the gradient signal that previously spread across the full token sequence, driving adapter parameters toward a qualitatively different attractor.

Two competing interpretations deserve consideration. *Interpretation A (favorable):* Eviction masks create a genuinely distinct optimization problem — the adapter learns to route information through a different set of attention pathways, leading to parameter orthogonality as a structural consequence. *Interpretation B (concern):* The short training duration (30 steps) and small proxy model (GPT-2, 117M) may amplify instability that would diminish at full scale. A model with more capacity and longer training may converge to similar weight configurations regardless of eviction masking. The planned H-M3 experiment will help distinguish these interpretations: if full-scale LLaMA-2-7B adapters also show substantial weight divergence after 1 epoch of training, Interpretation A is supported.

**Middle-layer specificity is mechanistically informative.** The concentration of significant attention pattern divergence in layers 4–11 (of 12) is consistent with the established transformer literature showing that middle layers carry long-range dependency information [Clark et al., 2019]. Lower layers (0–3) handle positional encoding and local syntactic patterns that are relatively insensitive to which specific tokens are retained in the KV cache — eviction has little effect on what these layers learn. Middle layers, by contrast, must route information across long distances; when token positions are evicted, these layers must reorganize their attention pathways. The fact that eviction-aware training most strongly restructures exactly these layers provides mechanistic grounding for the hypothesis that the method specifically improves long-context performance — it targets the computations that long-context tasks most rely on.

## 6.2 Limitations

We document limitations transparently, distinguishing those that block the primary claims from those that narrow scope.

**L1 (Critical): Primary accuracy evaluation absent.** H-M3 — full LongBench accuracy evaluation on LLaMA-2-7B and Mistral-7B-v0.1 at r=50% — was not executed. The prediction P1 (≥2% per-category LongBench accuracy gain at r=50% in ≥4/6 categories on both models) is entirely untested. The mechanistic evidence (H-E1, H-M1) supports the *plausibility* of the accuracy claim but cannot substitute for direct measurement. We present this work as a mechanistic study establishing existence and attention-level effects; the accuracy claim is future work.

**L2 (Critical): Dose-response not evaluable at proxy scope.** H-M2's Spearman ρ prediction (P2) requires LongBench evaluation at multiple budget ratios, which GPT-2's 1024-token context window cannot support. The BudgetSweepEvaluator infrastructure is production-ready; the evaluation is blocked only by model access.

**L3 (Significant): Proxy-target validity gap.** GPT-2 (117M, 1024-token context) differs from LLaMA-2-7B and Mistral-7B-v0.1 in capacity, context length, and architectural details (separate Q/K/V projections in LLaMA/Mistral vs. fused `c_attn` in GPT-2). The fused architecture may amplify weight divergence compared to separate projections — the near-orthogonal result may weaken at 7B scale. H-M1's 5-sample evaluation on synthetic text is insufficient to draw quantitative conclusions about full LongBench evaluation on 500+ samples per category.

**L4 (Significant): H2O+SDPA incompatibility.** A previously undocumented incompatibility between H2O's cumulative-score indexing and PyTorch SDPA kernels was discovered during H-M2 (CUDA gather kernel crash at extended inference). The fix (`attn_implementation='eager'`) is validated and integrated into all subsequent experiments. However, this introduces a ~15–30% inference overhead compared to SDPA, which confounds throughput measurements (P3) and should be documented for practitioners.

**L5 (Moderate): Single eviction policy.** All experiments use H2O eviction. Token-scarcity regularization may be policy-specific — adapters trained with H2O masks may not generalize to SnapKV or StreamingLLM eviction at inference. Testing policy generalization requires separate experiments.

**L6 (Moderate): Training data confound unresolved.** LongAlpaca-12k may create a data-distribution advantage for eviction-aware training if its long-context examples align with LongBench tasks. A sanity check fine-tuning on Alpaca-52k (short-context data) and evaluating on LongBench would confirm that LongAlpaca-12k is not the confound.

## 6.3 Technical Finding: H2O+SDPA Incompatibility

The CUDA gather kernel crash discovered during H-M2 represents a previously undocumented technical limitation: H2O's cumulative-score index operations are incompatible with PyTorch's SDPA (Scaled Dot-Product Attention) kernel for certain model-sequence combinations. The root cause is H2O's use of scatter/gather operations on attention score tensors that SDPA fuses into a single kernel — the H2O wrapper interrupts the fused computation in a way that SDPA does not support.

**Fix:** Set `attn_implementation='eager'` in all transformer model calls when using H2O wrappers. This forces attention computation through the standard (unfused) path, which H2O can intercept correctly.

**Implication for practitioners:** Any deployment of LoRA adapters with H2O eviction under `transformers` ≥ 4.36 (which enables SDPA by default on compatible GPU hardware) must explicitly disable SDPA. The ~15–30% throughput overhead introduced by eager attention should be factored into throughput comparisons.

## 6.4 Broader Impact

Eviction-Aware LoRA targets a fundamental inefficiency in current LLM deployment practice — the systematic mismatch between training and inference conditions that arises whenever KV cache eviction is applied to adapters trained without eviction awareness. The positive impacts are clear: more efficient long-context LLM deployment, potential to recover accuracy lost to eviction without hardware changes, and a principled framing of the training-inference distribution mismatch that may generalize to other inference-time optimizations (quantization-aware fine-tuning, speculative decoding, etc.).

We identify no significant negative impacts specific to this work. The method modifies fine-tuning procedures for existing LLMs; it does not introduce new capabilities that could be misused beyond those already present in the base models.
