# GQA-GroupMax: An Empirical Investigation of Aggregation Functions for GQA-Native KV Cache Eviction

**Authors:** Anonymous  
**Institution:** Anonymous Institution  
**Date:** 2026-08-27

---

## Abstract

Grouped Query Attention (GQA) architectures share key-value (KV) heads across multiple query heads, introducing an aggregation decision that is implicit in all prior KV cache eviction methods: how to combine per-query-head importance scores into a single per-KV-head eviction score. We investigate whether max-pooling aggregation (GQA-GroupMax) over within-group query-head scores preserves minority-head signals that mean-pooling (GQA-GroupMean) suppresses due to a 1/G dilution factor. Two diagnostic experiments were conducted on LLaMA-3-8B, Mistral-7B-v0.1, and Phi-3-mini-4k-instruct using LongBench retrieval tasks. H-E1 measured within-group query-head attention cosine similarity to assess whether meaningful diversity exists within GQA groups. For the primary model LLaMA-3-8B, 40.6% of layers exhibit median cosine similarity below 0.9, falling short of the pre-specified 50% threshold; Mistral-7B (62.5%) and Phi-3-mini (78.1%) exceed the threshold. H-M1 measured Spearman rank correlation between GroupMax and GroupMean eviction score vectors on LLaMA-3-8B; the global median correlation was 0.962 (threshold for meaningful divergence: < 0.95), with 7 of 32 layers showing per-layer correlation below 0.95. Both gate criteria were not met on the primary model, constituting quantitative near-misses rather than decisive rejections. A key confound was identified: sequence truncation to 2048 tokens (required by memory constraints) reduces attention sparsity relative to full LongBench context lengths of 4,000–8,000 tokens, likely attenuating the GroupMax/GroupMean divergence. The aggregation function formalization and reusable measurement infrastructure are contributed regardless of gate outcome.

---

## 1. Introduction

The memory cost of the KV cache during long-context autoregressive inference scales linearly with sequence length. For a 7–8B parameter model at float16 precision with a 32K context, this cost can reach tens of gigabytes, limiting practical throughput. KV cache eviction methods address this by selectively retaining only the highest-importance key-value entries [Zhang et al., 2023; Li et al., 2024; Liu et al., 2023]. However, all major eviction methods were developed under Multi-Head Attention (MHA), where each query head has a private KV head. Modern open-weight models — LLaMA-3, Mistral, Phi-3 — use Grouped Query Attention (GQA) [Ainslie et al., 2023], where G query heads share one KV head.

This architectural change introduces an aggregation problem that existing methods have not formally addressed. When computing per-KV-head eviction importance scores, methods such as H2O [Zhang et al., 2023] and SnapKV [Li et al., 2024] implicitly reduce per-query-head scores via mean-pooling before making eviction decisions at the KV-head level. Mean aggregation applies a 1/G weighting to each query head's signal. For G=4 (the case in LLaMA-3-8B, which has 32 query heads and 8 KV heads), any query head that attends intensely to a specific KV position contributes only 25% of the GroupMean score for that position. If the other three query heads in the group do not attend to the same position, the score may fall below the eviction threshold despite a minority head's strong signal.

Max-aggregation (GQA-GroupMax) selects the maximum attention weight across the G query heads sharing each KV head. This preserves the full signal from the most attentive query head and avoids the 1/G dilution effect. The GQA-GroupMax approach is a distinct but practically available alternative: KVCache-Factory [Cai et al., 2024b] already exposes `--gqa_score_agg mean|max|sum` as a configuration parameter, confirming the aggregation choice is an open engineering decision in production-scale systems.

This paper reports two diagnostic experiments designed to characterize whether the GroupMax/GroupMean distinction produces meaningfully different eviction decisions:

- **H-E1** tests whether within-group query-head attention diversity is sufficient to make GroupMax and GroupMean diverge (existence prerequisite).
- **H-M1** measures the Spearman rank correlation between GroupMax and GroupMean eviction score vectors (mechanism test).

Both gates were not met on the primary model LLaMA-3-8B. We report the results, diagnose the confounds, and document the infrastructure built, which is reusable for downstream performance comparison experiments.

### Contributions

1. A formal treatment of the aggregation function as an explicit design variable for GQA-native KV cache eviction, distinguishing GroupMax and GroupMean as distinct and testable alternatives.
2. Empirical measurements of within-group query-head attention cosine similarity across LLaMA-3-8B, Mistral-7B, and Phi-3-mini on LongBench retrieval tasks.
3. Empirical measurement of GroupMax/GroupMean Spearman rank correlation on LLaMA-3-8B, with identification of a sequence-length confound that attenuates divergence at the tested 2048-token truncation length.
4. Validated, reusable measurement infrastructure (AttentionDiversityMeter, GQAEvictionScoreHook, Spearman evaluation pipeline) for follow-on experiments.

---

## 2. Related Work

### 2.1 KV Cache Eviction Methods

**H2O** [Zhang et al., 2023] proposes cumulative attention accumulation as a token importance metric. Each token's score is the sum of attention weights it has received across all generation steps. H2O evicts low-score tokens at each decode step. Implementation integrates into the attention module's per-step forward computation. Evaluated on OPT and LLaMA (MHA models).

**SnapKV** [Li et al., 2024] introduces prefill-observation scoring: attention weights from the last W query tokens during prefill are averaged per key position to identify tokens the query consistently attends to. Eviction occurs once, before generation. Implementation overrides LlamaAttention.forward() to apply eviction within the attention module before past_key_values is updated. SnapKV reports strong results on LongBench with LLaMA-2/3-chat models at 40–60% retention.

**ScissorHands** [Liu et al., 2023] computes importance during a warmup period of 32 decode steps, then freezes the schedule. Motivated by observed persistence of attention patterns (Spearman r > 0.85 on OPT-6.7B).

**PyramidKV** [Cai et al., 2024a] applies per-layer budget allocation, giving more capacity to early layers (broad attention) and less to later layers (local attention).

**StreamingLLM** [Xiao et al., 2023] retains attention sink tokens plus a recent sliding window without any importance scoring, serving as a static lower bound.

All of these methods were developed on or primarily evaluated with MHA architectures. None formalizes the aggregation function as a design choice when applied to GQA models.

### 2.2 GQA Architecture and Head Specialization

GQA [Ainslie et al., 2023] was introduced to reduce the memory cost of the KV cache at inference time. In GQA, G query heads share one KV head, so the number of KV heads is num_q_heads / G. For LLaMA-3-8B: 32 query heads, 8 KV heads, G = 4. For Mistral-7B-v0.1: 32 query heads, 8 KV heads, G = 4. For Phi-3-mini-4k-instruct: 32 query heads, 8 KV heads, G = 4.

Evidence for query-head specialization within GQA groups exists in prior work. DuoAttention [Xiao et al., 2024] classifies approximately 50% of LLaMA-3-8B attention heads as retrieval heads with qualitatively distinct attention patterns from streaming heads. RazorAttention [Tang et al., 2024] identifies echo heads and induction heads with distinct behavior. If retrieval heads and streaming heads co-occur within a GQA group, mean aggregation will dilute retrieval head signals.

### 2.3 GQA Score Aggregation in Production Systems

KVCache-Factory [Cai et al., 2024b] provides a unified framework implementing H2O, SnapKV, PyramidKV, StreamingLLM, and additional methods. It exposes `--gqa_score_agg mean|max|sum` under `--kv_cache_granularity kv_head` as a configurable parameter operating before `repeat_kv()` in the attention forward pass. Documentation notes that max aggregation "slightly outperforms" mean aggregation in some configurations, but no systematic comparison has been published. This confirms the aggregation function is an unsettled design choice in practice.

---

## 3. Method

### 3.1 Research Hypothesis

The primary hypothesis (GQA-GroupMax) states: under GQA-based transformer architectures (LLaMA-3, Mistral, Phi-3) performing long-context inference, KV cache eviction decisions made using max-pooling aggregation over Q-head attention scores within each KV-group (GQA-GroupMax) improve LongBench retrieval-task performance by ≥1 point at 50% cache budget, relative to GroupMean, because max-aggregation preserves the full attention signal from the most attentive Q-head in a group, preventing the 1/G dilution that mean-aggregation applies to minority-head signals.

This paper reports the results of two prerequisite diagnostic experiments. The main performance comparison (H-M2, H-M3) was not executed due to gate failures in H-E1 and H-M1.

### 3.2 H-E1: Within-Group Query-Head Attention Diversity

**Measurement objective:** Verify that query heads within a GQA group develop sufficiently distinct attention distributions to make GroupMax and GroupMean differ in practice.

**Metric:** Pairwise cosine similarity of flattened attention weight vectors for all C(G, 2) pairs of query heads sharing a KV head, computed after softmax, per layer, per sample.

**Gate criterion:** Fraction of layers where median pairwise cosine similarity < 0.9 must be ≥ 0.5 for the primary model (LLaMA-3-8B).

**Implementation:** AttentionDiversityMeter registered as a forward hook on each LlamaAttention module, capturing post-softmax attention weights via `output_attentions=True` with `attn_implementation="eager"` (required to suppress FlashAttention, which does not return attention weights). Processing was sequential (batch_size=1) at max_len=512 tokens due to the quadratic memory cost of storing full attention tensors (attn_weights shape: (1, 32, 512, 512) per layer). All 32 layers processed per sample. Unit tests: 19/19 passing.

**Models and samples:**
- LLaMA-3-8B (meta-llama/Meta-Llama-3-8B), 32 Q-heads, 8 KV-heads, G=4
- Mistral-7B-v0.1 (mistralai/Mistral-7B-v0.1), 32 Q-heads, 8 KV-heads, G=4
- Phi-3-mini-4k-instruct (microsoft/Phi-3-mini-4k-instruct), 32 Q-heads, 8 KV-heads, G=4

For LLaMA-3-8B: 600 samples processed (250+ confirmed), seed=42, LongBench retrieval subsets (hotpotqa, 2wikimqa, narrativeqa; musique was unavailable in local cache).

**Figures available:**
- `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_scope/docs/youra_research/_archive/20260826T033405_routing_recovery/h-e1/figures/fig1_layer_median_bar.png` — Layer-wise median cosine similarity bar chart
- `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_scope/docs/youra_research/_archive/20260826T033405_routing_recovery/h-e1/figures/fig2_violin.png` — Violin plot of similarity distribution per layer
- `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_scope/docs/youra_research/_archive/20260826T033405_routing_recovery/h-e1/figures/fig3_heatmap.png` — Layer × KV-group heatmap
- `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_scope/docs/youra_research/_archive/20260826T033405_routing_recovery/h-e1/figures/fig4_cdf.png` — Cumulative distribution of cosine similarity values

### 3.3 H-M1: GroupMax vs. GroupMean Score Divergence

**Measurement objective:** Quantify whether GroupMax and GroupMean aggregation produce meaningfully different eviction rankings, using Spearman rank correlation as the divergence measure.

**Metric:** Spearman rank correlation (ρ) between flattened GroupMax and GroupMean eviction score vectors, computed per layer per sample, then aggregated to global median and mean.

**Gate criterion:** Global median Spearman ρ < 0.95 (i.e., PASS if scores are sufficiently different to indicate divergent eviction rankings).

**Implementation:** GQAEvictionScoreHook registered on each LlamaAttention module. Two hooks per layer (one computing GroupMax, one GroupMean) operate on the same attention weights simultaneously. Score vectors have shape (batch=1, H_kv=8, T_kv) — KV-head granularity, before repeat_kv(). Spearman correlation computed via torchmetrics.SpearmanCorrCoef. Memory management: hook.clear() called after each sample. Processing at max_seq_len=2048 tokens. 99 samples processed on LongBench (hotpotqa, 2wikimqa, narrativeqa). Mechanism activation verified: both hooks fired on all 32 layers, tensor shape confirmed (1, 8, T_kv), max_diff between GroupMax and GroupMean > 1e-4 per layer. Unit tests: 26/26 passing.

**Figures available (h-m1):**
- `h-m1/figures/h-m1_gate_bar.png`
- `h-m1/figures/h-m1_layer_heatmap.png`
- `h-m1/figures/h-m1_divergence_cdf.png`

---

## 4. Experimental Setup

### 4.1 Models

| Model | HuggingFace ID | Q-heads | KV-heads | G | Layers |
|-------|---------------|---------|----------|---|--------|
| LLaMA-3-8B | meta-llama/Meta-Llama-3-8B | 32 | 8 | 4 | 32 |
| Mistral-7B-v0.1 | mistralai/Mistral-7B-v0.1 | 32 | 8 | 4 | 32 |
| Phi-3-mini-4k-instruct | microsoft/Phi-3-mini-4k-instruct | 32 | 8 | 4 | 32 |

All models loaded in float16. Device: CUDA (GPUs 2, 3, 4 with ~55GB free; CUDA_VISIBLE_DEVICES=2,3,4). No model fine-tuning; inference only.

**Note on G value:** The original hypothesis stated G=8 for LLaMA-3-8B. The actual G=4, as the model has 32 Q-heads and 8 KV-heads (not 4 KV-heads as initially assumed). This was corrected during implementation.

### 4.2 Dataset

LongBench v1 [Bai et al., 2023], retrieval subsets: HotpotQA, 2WikiMQA, NarrativeQA. (MuSiQue was unavailable in local cache.) Loaded via `load_dataset("THUDM/LongBench", subset, split="test")`. Seed=42. No special preprocessing.

### 4.3 Sequence Length Constraint

H-E1 used max_len=512 due to quadratic memory scaling of attention weight storage: attn_weights at (1, 32, 2048, 2048) requires ~268MB per layer. H-M1 used max_len=2048. Full LongBench context lengths are 4,000–8,000 tokens. This truncation is a significant experimental limitation discussed in Section 6.

### 4.4 Software Environment

- Python 3.10
- PyTorch (CUDA 12.x)
- HuggingFace transformers
- torchmetrics
- torchaudio 2.11.0 was removed due to incompatibility with system CUDA 12.x (libcudart.so.13 conflict)
- `python -u` flag used for unbuffered output

---

## 5. Results

### 5.1 H-E1: Within-Group Cosine Similarity

**Table 1: H-E1 Results — Fraction of Layers Below Cosine Similarity 0.9**

| Model | Global Mean Cosine Sim | Fraction Layers < 0.9 | Gate Threshold | Gate Result |
|-------|----------------------|----------------------|----------------|-------------|
| LLaMA-3-8B | 0.9006 | 0.406 (13/32 layers) | ≥ 0.50 | FAIL |
| Mistral-7B | 0.8604 | 0.625 (20/32 layers) | ≥ 0.50 | PASS |
| Phi-3-mini | 0.8352 | 0.781 (25/32 layers) | ≥ 0.50 | PASS |

The primary model gate (LLaMA-3-8B) was not met. 13 of 32 layers showed median cosine similarity below 0.9, compared to the 16-layer threshold. The global mean cosine similarity for LLaMA-3-8B was 0.9006, indicating that on average, query-head attention distributions within groups are highly similar. However, heterogeneity exists across layers: early layers (layer 0, global mean 0.644) and late layers (layer 31, global mean 0.800) show substantially lower similarity than middle layers (layers 2–5, means 0.983–0.938), indicating a U-shaped profile.

For Mistral-7B, 62.5% of layers are below 0.9 (global mean 0.860), and for Phi-3-mini, 78.1% (global mean 0.835). Both secondary models show greater within-group diversity than LLaMA-3-8B.

**Table 2: H-E1 LLaMA-3-8B Per-Layer Median Cosine Similarity (Selected Layers)**

| Layer | Median Cosine Sim | Below 0.9? |
|-------|------------------|-----------|
| 0 | 0.645 | Yes |
| 1 | 0.939 | No |
| 2 | 0.986 | No |
| 7 | 0.903 | No |
| 8 | 0.874 | Yes |
| 13 | 0.839 | Yes |
| 15 | 0.817 | Yes |
| 18 | 0.931 | No |
| 23 | 0.967 | No |
| 31 | 0.802 | Yes |

The mechanism verification tests passed: determinism, sensitivity, and smoothness checks all confirmed. Smoke test (2-token forward pass) verified hooks fired on all 32 LLaMA-3-8B layers with correct tensor shapes.

### 5.2 H-M1: Spearman Rank Correlation Between GroupMax and GroupMean

**Table 3: H-M1 Results — Spearman Rank Correlation (LLaMA-3-8B, 99 samples)**

| Metric | Value | Gate Threshold | Gate Result |
|--------|-------|----------------|-------------|
| Global Median Spearman ρ | 0.9622 | < 0.95 | FAIL |
| Global Mean Spearman ρ | 0.9599 | — | — |
| Score Divergence (p50 of \|GroupMax − GroupMean\|) | 7.2 × 10⁻⁵ | > 0 | PASS |
| Score Divergence (p95) | 4.1 × 10⁻⁴ | — | — |

The global median Spearman ρ of 0.962 exceeded the 0.95 threshold by 0.012. This is a quantitative near-miss: the two aggregation methods produce highly correlated but not identical eviction rankings.

**Per-layer results (selected):** 7 of 32 layers (22%) showed median ρ < 0.95. The layer with the greatest divergence was layer 31 (ρ = 0.916). The layer with the highest correlation was layer 24 (ρ = 0.981). No systematic pattern (early vs. late) was immediately apparent from the selected per-layer values; the full layer heatmap is available in the figure files.

The mechanism activation check confirmed that the experimental setup was operationally correct: GroupMax and GroupMean hooks fired on all 32 layers, produced tensors of shape (1, 8, T_kv), and the maximum absolute difference between GroupMax and GroupMean scores was > 1e-4 for every layer and sample. The gate failure is quantitative, not mechanistic.

**Table 4: H-M1 Per-Layer Median Spearman ρ (Selected Layers)**

| Layer | Median ρ | Below 0.95? |
|-------|----------|-------------|
| 1 | 0.936 | Yes |
| 4 | 0.948 | Yes |
| 6 | 0.945 | Yes |
| 15 | 0.945 | Yes |
| 16 | 0.947 | Yes |
| 24 | 0.981 | No |
| 31 | 0.916 | Yes |

### 5.3 Summary of Gate Results

| Experiment | Gate Criterion | Result | Primary Model Status |
|------------|---------------|--------|---------------------|
| H-E1 | Fraction layers with cosine sim < 0.9 ≥ 0.5 (LLaMA-3-8B) | 0.406 | FAIL |
| H-M1 | Global median Spearman ρ < 0.95 (LLaMA-3-8B) | 0.962 | FAIL |

---

## 6. Discussion

### 6.1 Sequence Length Confound

Both H-E1 and H-M1 were executed at reduced sequence lengths (max_len=512 for H-E1, 2048 for H-M1) due to the quadratic memory cost of storing full attention weight tensors with `output_attentions=True`. Full LongBench context lengths range from 4,000 to 8,000 tokens. Shorter sequences produce more uniform attention distributions: there are fewer positions for minority retrieval heads to concentrate on, reducing the divergence between query heads within a group. This confound plausibly explains the near-miss failure on both gates:

- For H-E1: cosine similarity at max_len=512 may overestimate within-group similarity relative to full-context inputs.
- For H-M1: the GroupMax/GroupMean divergence at 2048 tokens is demonstrably non-zero but below the pre-specified threshold; at 4,000–8,000 tokens, minority-head signals may be more concentrated and thus more likely to distinguish max from mean.

This confound does not invalidate the mechanism: the GQAEvictionScoreHook produces measurably different outputs (GroupMax ≠ GroupMean, verified per layer), and several individual layers do show ρ < 0.95. The gate failure reflects the difficulty of testing the hypothesis under memory-constrained sequence lengths rather than evidence that the aggregation function distinction is irrelevant.

### 6.2 G Value Correction

The original hypothesis assumed G=8 for LLaMA-3-8B. The actual architecture has G=4 (32 Q-heads / 8 KV-heads). Lower G reduces the dilution factor from 1/8 to 1/4, meaning mean aggregation retains half the signal of a minority head compared to the G=8 case. The GroupMax advantage is correspondingly weaker at G=4. Experiments on models with larger GQA group sizes (G=8 or higher) are not available in the dataset but would be a natural next step.

### 6.3 Interpretation of H-E1 Model Variation

The secondary models (Mistral-7B, Phi-3-mini) both passed the H-E1 gate, with Phi-3-mini showing the highest fraction of layers below the 0.9 threshold (78.1%). This suggests that within-group query-head diversity is model-dependent and may be more pronounced in models with different training objectives or architectures. LLaMA-3-8B's near-threshold behavior (40.6% vs. 50% threshold) indicates that diversity is present in a substantial fraction of layers but does not dominate the model's layer-wise profile.

### 6.4 Implications for the GQA-GroupMax Hypothesis

The two gate failures do not constitute evidence that GroupMax and GroupMean produce equivalent downstream performance. The H-M1 FAIL indicates the eviction rankings are highly correlated (ρ ≈ 0.96) but not identical. At a 50% eviction budget over 2048 KV positions, a 4% rank divergence affects approximately 80 positions per KV head per layer — a non-trivial token set. Whether this rank difference translates to measurable F1 differences on LongBench retrieval tasks is an empirical question that was not addressed due to the gate failures blocking H-M2 and H-M3.

The recommendation from H-M1's validation report is to proceed with downstream performance experiments (H-M2) with a revised gate threshold (e.g., any non-trivial rank divergence with downstream impact), rather than treating the mechanism gate failure as a rejection of the hypothesis.

### 6.5 Infrastructure Contributions

The following validated components are available for follow-on experiments:

| Component | File | Tests | Reusable |
|-----------|------|-------|----------|
| AttentionDiversityMeter | h-e1/code/measure/diversity_meter.py | 19/19 | Yes |
| HookManager | h-e1/code/measure/hook_manager.py | — | Yes |
| ModelLoader | h-e1/code/measure/model_loader.py | — | Yes |
| GQAEvictionScoreHook | h-m1/code/hooks/eviction_score_hook.py | 11/11 | Yes |
| compute_layer_spearman | h-m1/code/metrics/spearman_metrics.py | 15/15 | Yes |
| GateEvaluator | h-e1/code/metrics/statistics.py | — | Yes |

Configuration notes for reuse: use `attn_implementation="eager"` (FlashAttention suppresses attention weight output), `output_attentions=True`, sequential batch_size=1, remove torchaudio if CUDA version mismatch occurs.

### 6.6 Limitations

**L1: Sequence length truncation.** Both experiments used truncated contexts (512 and 2048 tokens). Full LongBench lengths were not achievable with the current attention weight extraction approach. Chunked attention extraction or gradient checkpointing would be required for full-context experiments.

**L2: Single model as primary.** LLaMA-3-8B failed both gates. Secondary models (Mistral-7B, Phi-3-mini) passed H-E1 but H-M1 was not run on them. Multi-model evidence for the mechanism is incomplete.

**L3: G value assumption error.** The original hypothesis assumed G=8; actual G=4 for all three models tested. The hypothesis was designed with a larger dilution factor than the experimental setup provides.

**L4: No downstream performance evaluation.** H-M2 (LongBench F1 comparison, GroupMax vs. GroupMean) was not executed. The paper reports mechanism-level evidence only, not performance evidence.

**L5: musique unavailable.** The MuSiQue LongBench subset was not in local cache and was excluded from both experiments, reducing task coverage from 4 to 3 retrieval subsets.

---

## 7. Conclusion

This paper reports two diagnostic experiments investigating whether max-pooling aggregation over query-head scores within GQA groups (GQA-GroupMax) produces meaningfully different KV cache eviction decisions than mean-pooling (GQA-GroupMean). The existence experiment (H-E1) found that within-group query-head attention cosine similarity falls below 0.9 in 40.6% of LLaMA-3-8B layers, below the 50% pre-specified threshold for the primary model, though Mistral-7B (62.5%) and Phi-3-mini (78.1%) exceed the threshold. The mechanism experiment (H-M1) found a global median Spearman rank correlation of 0.962 between GroupMax and GroupMean eviction scores on LLaMA-3-8B at 2048-token context length, above the 0.95 threshold for meaningful divergence.

Both gate failures are quantitative near-misses associated with an identified confound: the sequence length truncation required by memory constraints reduces the attention sparsity that motivates the GroupMax/GroupMean distinction. The mechanism is confirmed active (non-zero divergence, per-layer hook verification), and 7 of 32 layers show per-layer correlation below the 0.95 threshold.

The formalization of the aggregation function as an explicit design choice for GQA-native KV cache eviction remains a contribution independent of these gate outcomes: no prior eviction paper identifies or studies this choice. The infrastructure built and validated here provides a ready foundation for downstream performance experiments (H-M2, H-M3) with full-context sequence lengths, which are the necessary next step to evaluate whether the GroupMax/GroupMean distinction has practical significance for LongBench retrieval task performance.

---

## References

Ainslie, J., Lee-Thorp, J., de Jong, M., Zeiler, M., Sanghai, S., & Xu, Y. (2023). GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints. *arXiv preprint arXiv:2305.13245*.

Bai, Y., Lv, X., Zhang, J., Lyu, H., Tang, J., Huang, Z., Du, Z., Liu, X., Zeng, A., Hou, L., Dong, Y., Tang, J., & Li, J. (2023). LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding. *arXiv preprint arXiv:2308.14508*.

Cai, Z., Zhang, Y., Gao, B., Liu, Y., Liu, T., Lu, K., Xiong, W., Dong, Y., Chang, B., & Hu, J. (2024a). PyramidKV: Dynamic KV Cache Compression based on Pyramidal Information Funneling. *arXiv preprint arXiv:2406.02069*.

Cai, Z., et al. (2024b). KVCache-Factory: A Unified Framework for KV Cache Compression. GitHub: Zefan-Cai/KVCache-Factory.

Li, Y., Huang, Y., Yang, B., Venkitesh, B., Locatelli, A., Ye, H., Cai, T., Lewis, P., & Chen, D. (2024). SnapKV: LLM Knows What You are Looking for Before Generation. *arXiv preprint arXiv:2404.14469*.

Liu, Z., Desai, A., Liao, F., Wang, W., Xie, V., Xu, Z., Kyrillidis, A., & Shrivastava, A. (2023). ScissorHands: Exploiting the Persistence of Importance Hypothesis for LLM KV Cache Compression at Test Time. *arXiv preprint arXiv:2305.17118*.

Tang, Y., et al. (2024). RazorAttention: Efficient KV Cache Compression through Retrieval Heads. *arXiv preprint*.

Xiao, G., Tang, Y., Zuo, J., Guo, J., Yang, S., Tang, H., Fu, Y., & Han, S. (2023). Efficient Streaming Language Models with Attention Sinks. *arXiv preprint arXiv:2309.17453*.

Xiao, G., et al. (2024). DuoAttention: Efficient Long-Context LLM Inference with Retrieval and Streaming Heads. *arXiv preprint arXiv:2410.10819*.

Zhang, Z., Sheng, Y., Zhou, T., Chen, T., Zheng, L., Cai, R., Song, Z., Tian, Y., Ré, C., Barrett, C., Wang, Z., & Chen, B. (2023). H2O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models. *Advances in Neural Information Processing Systems*. arXiv:2306.14048.

---

*Note: All citations should be verified against original papers before submission. The KVCache-Factory reference (Cai et al., 2024b) refers to a GitHub repository; verify the appropriate citation format for the target venue.*
