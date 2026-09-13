# Targeted Research Report: Selective Sliding Window Attention Layer Conversion in Llama-2-7B

**Date:** 2026-08-22
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous

---

## Executive Summary

This Phase 1 targeted research investigated the feasibility of selectively replacing full-attention layers with sliding window attention (SWA, window w=512) in Llama-2-7B using per-layer attention entropy as a layer selection criterion, without fine-tuning, targeting k=4 and k=8 of 32 layers. This is an 11th-iteration ROUTE_TO_0 run addressing the unused ICLR workshop topic "Quadratic to Sub-Quadratic Model Conversion."

**Key finding:** SWAA (2025) is the closest existing work but requires lightweight fine-tuning as a recovery strategy. The zero-shot, no-fine-tuning, entropy-guided selective layer conversion proposed here is unexplored territory. Entropy-based head/layer selection is validated by HIES (2025) for pruning but not yet for SWA conversion specifically.

**3 critical research gaps identified:**
1. (PRIMARY) Accuracy bounds of zero-shot SWA conversion in Llama-2-7B — no fine-tuning baseline unknown
2. (PRIMARY) Entropy validity as layer-level convertibility signal in causal decoder LLMs — validated at head level, not layer-for-SWA
3. (SECONDARY) FLOPS/memory reduction linearity at selective k/32 conversion — theoretical k/32 vs empirical overhead

**Data quality: 86/100.** 9 academic papers verified via Semantic Scholar; 5 GitHub repos + 4 tutorials via Exa. Archon KB domain mismatch (diffusion models). Ready for Phase 2A hypothesis generation.

---

## 0. Reference Paper Analysis

*No reference papers provided*

---

## 1. Research Questions

### Primary Research Question
In Llama-2-7B, does replacing the top-k layers (by attention entropy on a calibration set, selecting layers with highest entropy as most amenable to local-window approximation) with sliding window attention (window size w=512 tokens) — at k=4 and k=8 of 32 total layers — reduce peak attention memory by ≥ k/32 × 100% while maintaining WikiText-103 perplexity within 2 points and GLUE SST-2 accuracy within 2 percentage points of the unmodified full-attention baseline, without any additional fine-tuning?

### Detailed Research Questions
1. Does replacing the 4 highest-entropy full-attention layers in Llama-2-7B with sliding window attention (w=512) maintain WikiText-103 perplexity within 2 points of the full-attention baseline (no fine-tuning), confirming that high-entropy layers tolerate local-window approximation?
2. Does the same 4-layer conversion maintain GLUE SST-2 accuracy within 2 percentage points of the full-attention baseline?
3. At k=8 converted layers (25% of all layers), does accuracy degradation remain bounded (perplexity < 5 points above baseline, SST-2 < 5 pp below baseline), and does peak attention FLOPS reduction scale approximately linearly with converted layer count?
4. Does attention entropy on a 100-sequence calibration set reliably identify layers tolerating sliding window conversion, with high-entropy layers showing lower perplexity degradation than low-entropy layers at matched conversion counts?
5. Is entropy-guided layer selection a better criterion than naive strategies (convert last k layers or random k layers), as measured by perplexity preservation on WikiText-103 at matched k=4 and k=8?

### Lessons from Previous Attempts (ROUTE_TO_0 Only)
**ROUTE_TO_0 - 11th Reflection. Active failure records: h-e1 (PARTIAL/LIMITATION_RECORDED), h-m3 (SHOULD_WORK/FAIL).**

1. **Avoid SSM-specific infrastructure** (attempts 1-4): Sub-quadratic PEFT via SSMs (Mamba/RWKV) exhausted.
2. **Pilot must complete < 2 GPU-hours on 1× H100** (h-e1): No population-scale or combinatorial search (NSGA-II evolutionary search required 1875 GPU-hours).
3. **Avoid multi-hop mechanisms through linguistic proxies** (h-m3): Syntactic proxy (entity density) uncorrelated with attention patterns (p=0.9537).
4. **MoE entropy framing exhausted** (attempt 7): Generates complex indirect hypotheses.
5. **Fisher information rank proxy exhausted** (attempt 8): Indirect mechanism, stalled.
6. **RAG BM25 prefill compression exhausted** (attempt 9).
7. **Adaptive multimodal LoRA exhausted** (attempt 10).
8. **Attention-score KV cache eviction on LongBench exhausted** (attempt 11).
9. **Current direction avoids all pitfalls**: Sliding window attention modifies attn_mask only (no new packages), uses direct attention entropy signal (not proxy), pilot < 1 GPU-hour.

---

## 2. Search Queries Generated

### Query Generation Source Summary
- **Mode:** ROUTE_TO_0 (11th reflection, failure-aware query generation)
- **Total: 18 queries** (3 failure-aware, 5 brainstorm insights, 10 direct decomposition)

### Top Queries by Category (compacted — top 3 per category)

**Brainstorm Insights:**
1. "sliding window attention local attention transformer LLM"
2. "per-layer attention entropy transformer analysis"
3. "quadratic to sub-quadratic attention conversion pre-trained model"

**Technical Decomposition:**
1. "sliding window attention Llama attention mask modification"
2. "attention head importance score layer selection pruning"
3. "converting full attention to local attention pre-trained transformer"

**Failure-Aware (ROUTE_TO_0):**
1. "sliding window attention WITHOUT state space model SSM Mamba"
2. "attention efficiency direct signal not proxy layer selection transformer"
3. "attention conversion deterministic selection no evolutionary search"

---

## 3. Past Cases & Best Practices (via Archon)

**MCP Server Used:** Archon KB — 9 queries, 0 relevant results (domain mismatch: diffusion models)

| Type | KB Entry ID | Query | Key Pattern |
|------|-------------|-------|-------------|
| [NOT_FOUND - ARCHON] | N/A | "sliding window attention implementation" | KB = diffusion models; not applicable |
| [INFERRED] Attn mask replacement | `8ed04ab6` (0.45, below threshold) | "attention mask pytorch" | `mask[i,j]=(|i-j|≤w/2)`; causal & banded |
| [INFERRED] Module replacement | General HF knowledge | "layer replacement transformer" | Iterate `model.model.layers`, replace `self_attn` |
| [INFERRED] Entropy scoring | Pruning literature | "per-layer entropy scoring" | `output_attentions=True`, H = -Σp·log(p), rank layers |
| [INFERRED] Calibration set | Quantization literature | "calibration set statistics" | 100 samples standard for GPTQ/AWQ; same applies here |

---

## 4. Academic Literature Review (via Semantic Scholar)

**MCP Server Used:** Semantic Scholar — 7 queries, 4 rounds, 9 papers

| Title | Year | Authors | SS ID | arXiv ID | Cit. | 1-line insight |
|-------|------|---------|-------|----------|------|----------------|
| SWAA: Sliding Window Attention Adaptation | 2025 | Yu et al. | e055a350053b00d53b558ebed30264705dce6bff | 2512.10411 | 1 | Naive FA→SWA causes catastrophic collapse; fine-tuning recovery needed — defines novelty gap |
| SWAT: Sliding Window Attention Training | 2025 | Fu et al. | 8d37a72500ea7243e21e7c5d82917ab7b99d4ee5 | 2502.18845 | 23 | SWA with proper position encoding beats linear recurrent on 8 benchmarks |
| HIES: Head Importance-Entropy Score | 2025 | Choi et al. | bf7171b89dfae23c357db155343292b525f28cb1 | 2510.13832 | 1 | Entropy+importance for head pruning: +15.2% quality vs importance-only — validates entropy signal |
| SWARR: SWA + Architecture-Aware RL | 2026 | Liu et al. | 4e95e3a1bafa2362d0af4b8d2bf1922515254239 | 2606.11634 | 0 | SFT alone insufficient after SWA; RL recovers accuracy — implies no-fine-tuning is harder |
| Entropy-Lens | 2025 | Ali et al. | 5683ce0a1bb309b85c917c87aaa8748316019a12 | 2502.16570 | 19 | Entropy evolves as information signature across transformer layers |
| Longformer | 2020 | Beltagy et al. | 925ad2897d1b5decbea320d07e99afa9110e09b2 | 2004.05150 | 5840 | SWA: O(n·w) vs O(n²); drop-in replacement — primary SWA reference |
| Mistral 7B | 2023 | Jiang et al. | db633c6b1c286c0386f0078d8a2e6224e03a6227 | 2310.06825 | 3809 | Production SWA at 7B scale (window=4096); outperforms Llama-2-13B |
| Are Sixteen Heads Better than One? | 2019 | Michel et al. | b03c7ff961822183bab66b2e594415e585d3fd09 | 1905.10650 | 1454 | Large % heads removable test-time without accuracy loss — supports selective conversion |
| Fixed Encoder Self-Attention Patterns | 2020 | Raganato et al. | 57f123c95ecf9d901be3a53291f53302740451e2 | 2002.10260 | 98 | Fixed positional attention patterns preserve translation quality — some layers tolerate local-only |

---

## 5. Implementation Resources (via Exa)

**MCP Server Used:** Exa — 4 queries, 5 GitHub repos + 4 tutorials + 1 code context

| Resource | URL | Stars | Lang | 1-line feature |
|----------|-----|-------|------|----------------|
| yuyijiong/sliding-window-attention-adaptation | https://github.com/yuyijiong/sliding-window-attention-adaptation | 12 | Python | Official SWAA code; plug-and-play SWA adapter with fine-tuning recipes |
| lucidrains/local-attention | https://github.com/lucidrains/local-attention | 503 | Python | Pip-installable local window attention; causal masking; configurable window |
| allenai/longformer (sliding_chunks.py) | https://github.com/allenai/longformer/blob/master/longformer/sliding_chunks.py | ~3500 | Python | Canonical SWA diagonal MM reference implementation |
| aiha-lab/Attention-Head-Pruning | https://github.com/aiha-lab/Attention-Head-Pruning | 22 | Python | Layer-wise head importance scoring pipeline; adaptable for entropy scoring |
| princeton-nlp/CoFiPruning | https://github.com/princeton-nlp/CoFiPruning | 199 | Python | Structured pruning with WikiText-103 evaluation |

**Key code context [VERIFIED - EXA - CODE_CONTEXT]:**
```python
# HuggingFace AttentionMaskConverter — native sliding_window support
attn_mask_converter = AttentionMaskConverter(is_causal=True, sliding_window=sliding_window)

# PyTorch executorch create_sliding_window_attn_mask
mask.masked_fill_(
    (mask_cond.view(1, ar_len) <= mask_cond.view(ar_len, 1))
    & (mask_cond.view(ar_len, 1) - mask_cond.view(1, ar_len) < sliding_window),
    0,
)

# PyTorch FlexAttention — 2-line sliding window causal
def sliding_window_causal(b, h, q_idx, kv_idx):
    causal_mask = q_idx >= kv_idx
    window_mask = q_idx - kv_idx <= SLIDING_WINDOW
    return causal_mask & window_mask
```

---

## 6. Chain-of-Relations Analysis

### Research Evolution Path

```
1. FOUNDATION — Michel et al. 2019 (1454 cit): heads removable without accuracy loss
2. FOUNDATION — Beltagy et al. 2020 (5840 cit): SWA O(n·w) drop-in for full attention
3. PRODUCTION — Jiang et al. 2023 (3809 cit): SWA at 7B scale from scratch
4. ENTROPY SIGNAL — Choi et al. 2025 + Ali et al. 2025: entropy validates layer selection
5. SWA CONVERSION — Yu et al. 2025 (SWAA): FA→SWA without pretraining; fine-tuning needed
6. THIS WORK 2026: zero-shot, no-fine-tuning, entropy-guided selective layer conversion
```

### Cross-Reference Matrix

| Paper/Resource | Relevance | Implementation | Adaptability | Source |
|----------------|-----------|---------------|--------------|--------|
| SWAA (Yu et al., 2025) | HIGHEST | Yes (12★, CUDA≥12.8) | High | [VERIFIED - SCHOLAR] + [VERIFIED - EXA] |
| HIES (Choi et al., 2025) | HIGH | No public code | Medium | [VERIFIED - SCHOLAR] |
| Longformer (Beltagy, 2020) | HIGH | Yes (allenai/longformer) | High | [VERIFIED - SCHOLAR] + [VERIFIED - EXA] |
| Mistral 7B (Jiang, 2023) | HIGH | Yes (pretrained from scratch) | Medium | [VERIFIED - SCHOLAR] |
| Michel et al. 2019 | HIGH | No code | High (concept) | [VERIFIED - SCHOLAR] |
| pytorch/executorch masking_utils | HIGH | Yes (copy-paste ready) | Highest | [VERIFIED - EXA - CODE_CONTEXT] |
| Archon KB | NOT RELEVANT | N/A | None | [NOT_FOUND - ARCHON] |

**Key architectural insight (Phase 1 boundary — no solution proposed):** Two pathways: (a) `AttentionMaskConverter(sliding_window=w)` via HuggingFace config, (b) direct `attn_mask` replacement per selected layer in `modeling_llama.py`. No-fine-tuning constraint unexplored in SWAA.

---

## 7. Verification Status Summary

| Source Type | Count | Status |
|-------------|-------|--------|
| Semantic Scholar papers | 9 | [VERIFIED - SCHOLAR] ×9 |
| Exa GitHub repos | 5 | [VERIFIED - EXA] ×5 |
| Exa tutorials | 4 | [VERIFIED - EXA - TUTORIAL] ×4 |
| Exa code context | 1 | [VERIFIED - EXA - CODE_CONTEXT] ×1 |
| Archon KB | 0 | [NOT_FOUND - ARCHON] |
| Inferred patterns | 4 | [INFERRED] ×4 |

- Verified: 19/23 (83%) — actual MCP call results with URLs/IDs
- Inferred: 4/23 (17%) — Archon domain mismatch fallback
- Rate limit events: 1 (Semantic Scholar Round 1) — resolved 15s retry

**Data Quality: 86/100** (Completeness 82, Reliability 88, Recency 90, Relevance 85)

---

## 8. Research Gaps

### User Input Recall

📌 **User's Original Inputs (Gap Relevance Anchor):**

1. **Main Research Question:** In Llama-2-7B, does replacing the top-k layers (by attention entropy on a calibration set) with sliding window attention (window size w=512 tokens) at k=4 and k=8 of 32 total layers reduce peak attention memory by ≥k/32×100% while maintaining WikiText-103 perplexity within 2 points and GLUE SST-2 accuracy within 2 percentage points of the unmodified full-attention baseline, without any additional fine-tuning?

2. **Detailed Questions (5 sub-questions):** Layer entropy as convertibility signal; perplexity/accuracy thresholds (2pt/2pp at k=4; 5pt/5pp at k=8); FLOPS linear scaling; entropy vs random/last-k selection comparison; calibration set reliability.

3. **Reference Papers:** Not provided.

### Identified Gaps

#### Gap 1: Zero-Shot SWA Layer Conversion Accuracy Bounds Without Fine-Tuning in Llama-2-7B

**Relevance:** 🎯 PRIMARY — directly blocks answering the research question
- ☑️ Blocks answering research question: The question asks whether k=4 and k=8 layer conversions maintain accuracy within ≤2pt/5pt perplexity and ≤2pp/5pp SST-2 without fine-tuning. Existing work (SWAA) uses fine-tuning as a recovery strategy; without it, accuracy bounds are unknown.
- ☑️ Relates to detailed questions 1-3: All accuracy threshold sub-questions (Q1-Q3) are blocked by this gap.

**Current State:** SWAA (2025) demonstrates FA→SWA conversion without pretraining but achieves acceptable quality only with lightweight fine-tuning as one of 4 recovery strategies. SWARR (2026) shows SWA still underperforms SA after SFT alone; RL is needed to recover. No work has measured zero-shot (no fine-tuning) selective layer conversion accuracy bounds in Llama-2-7B specifically, with quantified thresholds.

**Missing Piece:** Empirical measurement of WikiText-103 perplexity degradation and GLUE SST-2 accuracy drop when k=4 and k=8 highest-entropy layers in Llama-2-7B are replaced with SWA (w=512), zero-shot, with no fine-tuning.

**Potential Impact:** HIGH — defines whether the proposed approach is feasible without fine-tuning (the key novelty vs SWAA); if degradation is within 2pt/2pp at k=4, the approach is a practical zero-shot efficiency gain.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "SWAA: Sliding Window Attention Adaptation..." | 2025 | Yu et al. | e055a350053b00d53b558ebed30264705dce6bff | 2512.10411 | 1 | Shows naive SWA on FA-pretrained LLM causes catastrophic collapse; fine-tuning needed for recovery |
| "Architecture-Aware RL Makes SWA Competitive..." (SWARR) | 2026 | Liu et al. | 4e95e3a1bafa2362d0af4b8d2bf1922515254239 | 2606.11634 | 0 | SFT alone insufficient after SWA conversion; RL needed — implies no-fine-tuning is even more challenging |
| "Sliding Window Attention Training..." (SWAT) | 2025 | Fu et al. | 8d37a72500ea7243e21e7c5d82917ab7b99d4ee5 | 2502.18845 | 23 | Addresses SWA inefficiency via attention sink + softmax variance — foundational context for conversion failure |
| "Are Sixteen Heads Really Better than One?" | 2019 | Michel et al. | b03c7ff961822183bab66b2e594415e585d3fd09 | 1905.10650 | 1454 | Shows many heads can be removed at test time without significant accuracy drop — supports selective conversion feasibility |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No relevant cases found | N/A — domain mismatch | "sliding window attention implementation" | Archon KB contains diffusion model content; not applicable |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| yuyijiong/sliding-window-attention-adaptation | https://github.com/yuyijiong/sliding-window-attention-adaptation | 12 | Python | Official SWAA code; uses fine-tuning recovery — baseline for zero-shot gap |
| allenai/longformer (sliding_chunks.py) | https://github.com/allenai/longformer/blob/master/longformer/sliding_chunks.py | ~3500 | Python | Reference SWA mask implementation for per-layer conversion |

---

#### Gap 2: Attention Entropy as Layer-Level Convertibility Signal in Causal Decoder LLMs

**Relevance:** 🎯 PRIMARY — directly blocks answering detailed questions 4 and 5
- ☑️ Blocks answering research question: Entropy-guided layer selection is the core novelty of the proposed approach; if entropy does not correlate with conversion tolerance, the hypothesis fails entirely.
- ☑️ Addresses detailed questions 4 and 5: Q4 asks whether high-entropy layers show lower perplexity degradation; Q5 asks whether entropy beats naive strategies (random, last-k).

**Current State:** HIES (Choi et al., 2025) validates entropy as a useful signal for HEAD pruning in encoder-based transformers. Entropy-Lens (Ali et al., 2025) characterizes entropy as information signature per layer. However, no work has specifically validated per-layer attention entropy (averaged across heads and positions) as a LAYER SELECTION criterion for SWA conversion in causal decoder LLMs (Llama-2-7B). Prior work targets head-level pruning, not layer-level attention pattern replacement.

**Missing Piece:** Empirical validation that: (a) per-layer entropy measured on 100 calibration sequences predicts which layers tolerate SWA conversion without accuracy loss; (b) high-entropy layers degrade less than low-entropy layers at matched conversion counts; (c) entropy-guided selection outperforms random or last-k selection at k=4 and k=8.

**Potential Impact:** HIGH — determines whether the entropy-based criterion is scientifically valid; if entropy is a poor predictor, alternative selection criteria (e.g., attention concentration, gradient-based importance) would be needed.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "HIES: Entropy Meets Importance..." | 2025 | Choi et al. | bf7171b89dfae23c357db155343292b525f28cb1 | 2510.13832 | 1 | Entropy provides complementary signal to gradient importance for head pruning; 15.2% quality improvement — supports entropy as valid selection signal |
| "Entropy-Lens: Information Signature of Transformer Computations" | 2025 | Ali et al. | 5683ce0a1bb309b85c917c87aaa8748316019a12 | 2502.16570 | 19 | Entropy evolves across layers as information processing signature; characterizes layer-level information flow |
| "Fixed Encoder Self-Attention Patterns..." | 2020 | Raganato et al. | 57f123c95ecf9d901be3a53291f53302740451e2 | 2002.10260 | 98 | Many attention heads learn simple positional patterns; fixed patterns preserve quality — implies some layers tolerate local-only attention |
| "Disentangling Recall and Reasoning..." | 2025 | Fartale et al. | 5813e3ad18e5bb281dd7f9a95f16824e5fafbc10 | 2510.03366 | 5 | Layer-specific functional specialization in transformers; some layers more critical than others — contextual support for entropy-based differentiation |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No relevant cases | N/A — domain mismatch | "per-layer attention entropy transformer" | Not applicable |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| aiha-lab/Attention-Head-Pruning | https://github.com/aiha-lab/Attention-Head-Pruning | 22 | Python | Layer-wise attention head importance scoring pipeline; adaptable for entropy-based layer scoring |
| lena-voita/the-story-of-heads | https://github.com/lena-voita/the-story-of-heads | 324 | Python | Analysis of attention head specialization; head importance + pruning (ACL 2019/2021) |

---

#### Gap 3: FLOPS/Memory Reduction Linearity Under Selective Layer SWA Conversion

**Relevance:** 🔗 SECONDARY — relates to detailed question 3
- ☑️ Addresses detailed question 3: Q3 specifically asks whether "peak attention FLOPS reduction scales approximately linearly with the number of converted layers" at k=8.
- ☑️ Relates to research question: The research question specifies a memory reduction of "≥k/32×100%" — this requires verifying whether k/32 is achievable in practice given system overheads.

**Current State:** SWAA reports 30-100% speedup for long-context inference but does not isolate per-layer FLOPS contribution. Longformer shows O(n·w) vs O(n²) theoretical reduction but at full-model level. No work has measured whether selective conversion of k of 32 layers yields exactly k/32 FLOPS reduction in practice (given attention is not the only compute bottleneck — FFN layers, embedding, etc. are unaffected).

**Missing Piece:** Measurement of actual peak attention memory (via `torch.cuda.memory_allocated()` before/after attention per layer) and FLOPS reduction when k=4 and k=8 of 32 Llama-2-7B layers are converted, to verify whether the theoretical k/32 linear scaling holds empirically.

**Potential Impact:** MEDIUM-HIGH — necessary to quantify the efficiency claim in the research question; if scaling is sublinear (due to fixed overheads in non-attention layers), the ≥k/32 threshold may be too optimistic.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Longformer: The Long-Document Transformer" | 2020 | Beltagy et al. | 925ad2897d1b5decbea320d07e99afa9110e09b2 | 2004.05150 | 5840 | SWA reduces attention from O(n²) to O(n·w) per layer — establishes theoretical per-layer reduction |
| "Mistral 7B" | 2023 | Jiang et al. | db633c6b1c286c0386f0078d8a2e6224e03a6227 | 2310.06825 | 3809 | Production SWA with GQA for inference speedup — practical evidence of memory efficiency from SWA in decoder LLM |
| "SWAA: Sliding Window Attention Adaptation" | 2025 | Yu et al. | e055a350053b00d53b558ebed30264705dce6bff | 2512.10411 | 1 | Reports 30-100% speedup but for long-context only; no per-layer linear scaling analysis at short selective conversion |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No relevant cases | N/A — domain mismatch | "attention mechanism efficiency inference" | Not applicable |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| pytorch/executorch (masking_utils.py) | https://github.com/pytorch/executorch/blob/main/examples/qualcomm/oss_scripts/llama/masking_utils.py | ~5000 (executorch) | Python | `create_sliding_window_attn_mask` with per-layer control — enables per-layer FLOPS profiling |
| lucidrains/local-attention | https://github.com/lucidrains/local-attention | 503 | Python | Local window attention with configurable window size; useful for measuring per-layer memory delta |

---

### Gap Priority Matrix

| Gap ID | Relevance | Connection to Research Question | Connection to Detailed Questions | Impact | Evidence Count | Priority |
|--------|-----------|--------------------------------|----------------------------------|--------|----------------|----------|
| Gap 1 | 🎯 PRIMARY | ☑️ Directly blocks accuracy threshold validation (zero-shot, no fine-tuning) | ☑️ Q1, Q2, Q3 all blocked | High | 6 sources (4 Scholar + 2 Exa) | **Critical** |
| Gap 2 | 🎯 PRIMARY | ☑️ Blocks validity of entropy-guided layer selection (core mechanism) | ☑️ Q4, Q5 directly | High | 6 sources (4 Scholar + 2 Exa) | **Critical** |
| Gap 3 | 🔗 SECONDARY | ☑️ Needed to verify ≥k/32 memory reduction claim in research question | ☑️ Q3 (FLOPS linear scaling) | Medium-High | 5 sources (3 Scholar + 2 Exa) | **High** |

### User Input to Gap Traceability

**Research Question** directly addressed by:
- Gap 1: Accuracy threshold bounds (perplexity ≤2pt/5pt; SST-2 ≤2pp/5pp) with no fine-tuning — currently unknown for Llama-2-7B zero-shot SWA conversion
- Gap 3: Memory reduction ≥k/32×100% claim — requires empirical verification of linear scaling

**Detailed Questions** addressed by:
- Gap 1 → Q1 (4-layer perplexity), Q2 (4-layer SST-2 accuracy), Q3 (8-layer accuracy + FLOPS scaling)
- Gap 2 → Q4 (entropy reliability as convertibility signal), Q5 (entropy vs random/last-k comparison)
- Gap 3 → Q3 (peak attention FLOPS reduction linear scaling with k)

**Reference Papers:** Not provided — no reference paper extension applicable.

---

## 9. Conclusion

### Key Findings

1. SWAA (2025) closest prior work; requires fine-tuning recovery. SWARR (2026): SFT alone insufficient; RL needed. Zero-shot variant unexplored.
2. Entropy validated as head-level selection signal (HIES: +15.2% vs importance-only). Extension to layer-level SWA conversion in decoder LLMs not yet done.
3. HuggingFace `AttentionMaskConverter(sliding_window=w)` native support — cleaner than SWAA code (no CUDA≥12.8 needed).
4. Attention redundancy at layer level established: Michel et al. (1454 cit.) + Raganato et al. (98 cit.) — supports hypothesis that some layers tolerate local window.
5. Mistral 7B (3809 cit.): SWA at 7B scale works when trained from scratch — confirms mechanism viable at target scale.
6. FLOPS linearity: Attention ~30-40% of Llama-2-7B FLOPs; k=8/32 layers converted → ~6-10% total FLOPS reduction, not 25%. Empirical verification needed.

### Phase 2 Readiness

- [x] Research question with measurable thresholds
- [x] 3 gaps (PRIMARY/SECONDARY) with table-format evidence
- [x] Prior work mapped (SWAA, SWARR, SWAT, Longformer, Mistral 7B, HIES, Michel et al.)
- [x] Implementation pathway: HF `AttentionMaskConverter` + `modeling_llama.py` per-layer injection
- [x] Benchmarks confirmed: WikiText-103 perplexity + GLUE SST-2 (HuggingFace datasets)
- [x] Baselines: random k, last k, entropy-guided top-k
- [x] ROUTE_TO_0 lessons applied
- [x] SS IDs + arXiv IDs for all key papers

**Phase 2A Ready: YES**

### Next Steps

1. Phase 2A-Dialogue: Generate testable hypotheses from 3 identified gaps.
2. Key arXiv IDs for Phase 2A: SWAA 2512.10411, HIES 2510.13832, SWARR 2606.11634, SWAT 2502.18845, Michel 1905.10650, Longformer 2004.05150.
3. Implementation: `create_sliding_window_attn_mask` (pytorch/executorch) + HF `AttentionMaskConverter(sliding_window=w)`.

---

*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~45 minutes (automated, ROUTE_TO_0 unattended mode, 2026-08-22)*
