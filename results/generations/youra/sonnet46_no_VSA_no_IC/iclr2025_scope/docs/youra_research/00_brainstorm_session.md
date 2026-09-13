---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Selective Sliding Window Conversion for Efficie"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-22
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Selective quadratic-to-sub-quadratic attention conversion — replacing a subset of full-attention layers in an existing transformer LLM with sliding window (local) attention to reduce inference memory and FLOPS, measured on existing perplexity and QA benchmarks without retraining from scratch

**Session Approach:** Auto-Fill Mode (ROUTE_TO_0 - Failure Recovery, 11th Reflection)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

The ICLR Workshop on Scalable Optimization for Efficient and Adaptive Foundation Models explicitly targets "Quadratic to Sub-Quadratic Model Conversion" and "Efficient Sub-Quadratic Foundation Models" — two of the workshop's core topics that have NOT been operationalized in any prior pipeline attempt. Transformer self-attention scales quadratically with sequence length in both memory and compute. Sliding window attention (used in Mistral, Longformer) replaces full attention with a local window of size w, reducing per-layer attention cost from O(n²) to O(n·w). The key research question is: which layers can be safely converted (full → sliding window) in an already-trained transformer without accuracy loss, and what is the resulting memory/FLOPS reduction? This is testable immediately: take a pre-trained model (Llama-2-7B or Mistral-7B), replace a subset of full-attention layers with sliding window attention (no pretraining, fine-tune only if needed on existing data), evaluate on existing benchmarks (WikiText-103 perplexity, GLUE/SuperGLUE classification tasks). No new benchmarks, no synthetic data, no human evaluation.

Source Type: Workshop CFP / Structured Input (ICLR Workshop on Scalable Optimization for Efficient and Adaptive Foundation Models)

---

## Lessons from Previous Attempts

**Context:** Eleven prior research iterations across this pipeline. Two active Serena Memory failure records (h-e1 PARTIAL/LIMITATION_RECORDED, h-m3 SHOULD_WORK/FAIL) plus nine archived brainstorm sessions covering multiple pivots.

**Previous Attempt 1-4 (Sub-quadratic PEFT, Archived Brainstorms):**
- What was tried: LoRA applied to Mamba/RWKV sub-quadratic SSMs on LongBench/MMLU
- Why it failed: Direction generated broad, hard-to-operationalize hypotheses
- Lesson: **Avoid SSM-specific infrastructure without prior validated components. Sub-quadratic PEFT via SSMs is exhausted.**

**Previous Attempt 5 — h-e1 (Evolutionary Flash/Mamba Routing, PARTIAL/LIMITATION_RECORDED):**
- What was tried: NSGA-II evolutionary Pareto search over binary Flash-Attention vs Mamba routing; 2/9 tasks completed
- Why it stalled: Full experiment required 1875 GPU-hours; unrunnable in < 2 GPU-hours
- Lesson: **Any MUST_WORK pilot must complete in < 2 GPU-hours on a single H100. No population-scale or combinatorial search.**

**Previous Attempt 6 — h-m3 (Syntactic Proxy → KV Cache Tiering, SHOULD_WORK/FAIL):**
- What was tried: Entity density + word count as proxy for attention concentration to drive adaptive KV cache tiering
- Why it failed: p-value = 0.9537 (wrong direction); syntactic proxy uncorrelated with attention patterns
- Lesson: **Avoid multi-hop mechanisms through linguistic proxies. Use direct, measurable signals.**

**Previous Attempt 7 (5th Brainstorm) — MoE Routing Entropy on Mixtral-8x7B:**
- What was proposed: Routing entropy correlation with task difficulty; critical expert subset pruning
- Status: Stalled at Phase 2A; indirect mechanism
- Lesson: **MoE entropy framing generates complex multi-hop hypotheses. Exhausted.**

**Previous Attempt 8 (6th Brainstorm) — Fisher-rank LoRA for Continual PEFT:**
- What was proposed: Fisher information diagonal to select LoRA rank per task in sequential fine-tuning on SuperGLUE
- Status: Stalled at Phase 2A/2B — indirect mechanism
- Lesson: **Fisher information proxy for rank selection is an exhausted direction.**

**Previous Attempt 9 (8th Brainstorm) — RAG BM25 Prefill Compression:**
- What was proposed: Token-level BM25 importance scoring of retrieved passages to reduce prefill length
- Status: Generated hypothesis but did not complete Phase 4
- Lesson: **RAG compression direction exhausted.**

**Previous Attempt 10 (9th Brainstorm) — Adaptive Multimodal LoRA (LLaVA-1.5-7B):**
- What was proposed: Gradient-magnitude per-layer LoRA rank allocation on VQAv2/MMBench
- Status: Generated hypothesis but re-routing triggered before completion
- Lesson: **Adaptive multimodal LoRA direction exhausted.**

**Previous Attempt 11 (10th Brainstorm) — Attention-Score KV Cache Eviction:**
- What was proposed: Cumulative per-token attention scores (averaged across heads) to evict low-importance tokens from KV cache on LongBench multi-doc QA
- Status: Re-routing triggered before Phase 4 completion
- Lesson: **Attention-score-driven KV cache eviction on LongBench exhausted. Must pivot to a different workshop topic.**

**How This Direction Avoids Those Pitfalls:**
- **Unused workshop topic:** "Quadratic to Sub-Quadratic Model Conversion" and "Efficient Sub-Quadratic Foundation Models" — neither has been operationalized in any prior attempt
- **No SSM infrastructure:** Sliding window attention is implementable by replacing the `attn_mask` in a standard HuggingFace transformer (e.g., `modeling_llama.py`) — no mamba-ssm, no flash-attn required
- **Short causal chain:** Identify convertible layers by measuring per-layer attention entropy on a calibration set → replace selected layers with sliding window attention → evaluate perplexity + downstream accuracy. Three steps, all directly observable.
- **Pilot feasible in < 2 GPU-hours:** Llama-2-7B with k=4 of 32 layers converted to sliding window (window=512), evaluated on WikiText-103 (perplexity, ~500 sequences) + GLUE SST-2 (classification, 872 examples) ≈ 45 minutes on 1× H100. No NSGA-II, no evolutionary search.
- **Existing benchmarks only:** WikiText-103 (HuggingFace: wikitext/wikitext-103-raw-v1, standard perplexity benchmark), GLUE SST-2 (HuggingFace: nyu-mll/glue, automatic accuracy). No new benchmarks, no human raters.
- **No new data, no synthetic content, no human evaluation.**
- **Workshop fit:** Directly targets "Quadratic to Sub-Quadratic Model Conversion" and "Efficient Sub-Quadratic Foundation Models" — primary workshop topics.

---

## Session Plan

Auto-extracted from structured input (ICLR Workshop CFP). Research direction selected by systematic elimination of all 11 prior attempted angles: sub-quadratic PEFT ×4, evolutionary Flash/Mamba routing (h-e1), syntactic attention proxy (h-m3), MoE routing entropy, Fisher-rank continual LoRA, RAG BM25 prefill compression, adaptive multimodal LoRA, attention-score KV cache eviction. After eliminating all prior attempts, remaining high-feasibility unused workshop topics: "Quadratic to Sub-Quadratic Model Conversion" and "Efficient Sub-Quadratic Foundation Models." Selected: selective sliding window attention layer conversion in Llama-2-7B, short causal chain, existing WikiText-103 + GLUE benchmarks, pilot < 90 minutes on 1× H100.

---

## Technique Sessions

Auto-Fill Mode (ROUTE_TO_0) — No interactive sessions. Direction selected by systematic elimination of all 11 prior failed/stalled angles, cross-referenced against remaining unused workshop topics and pipeline feasibility constraints from Serena Memory failure records (h-e1, h-m3) and 9 archived brainstorm sessions. "Quadratic to Sub-Quadratic Model Conversion" is the only remaining high-feasibility unused primary workshop topic.

---

## Research Question Development

### Initial Question

Can selective replacement of full-attention layers with sliding window attention in a pre-trained transformer LLM reduce inference memory and FLOPS while maintaining task accuracy on existing benchmarks, and which layers are most amenable to this conversion?

### Refined Question

In Llama-2-7B, does replacing the top-k layers (by attention entropy on a calibration set, selecting layers with highest entropy as most amenable to local-window approximation) with sliding window attention (window size w=512 tokens) — at k=4 and k=8 of 32 total layers — reduce peak attention memory by ≥ k/32 × 100% while maintaining WikiText-103 perplexity within 2 points and GLUE SST-2 accuracy within 2 percentage points of the unmodified full-attention baseline, without any additional fine-tuning?

### Detailed Sub-Questions

1. Does replacing the 4 highest-entropy full-attention layers in Llama-2-7B with sliding window attention (w=512) maintain WikiText-103 perplexity within 2 points of the full-attention baseline (no fine-tuning), confirming that high-entropy layers tolerate local-window approximation without accuracy loss?

2. Does the same 4-layer conversion maintain GLUE SST-2 accuracy within 2 percentage points of the full-attention baseline, confirming that task-specific performance is preserved across conversion strategies?

3. At k=8 converted layers (25% of all layers), does the accuracy degradation remain bounded (WikiText-103 perplexity < 5 points above baseline, SST-2 accuracy < 5 pp below baseline), and does peak attention FLOPS reduction scale approximately linearly with the number of converted layers?

4. Does attention entropy measured on a small calibration set (100 WikiText-103 sequences) reliably identify layers that tolerate sliding window conversion — specifically, do high-entropy layers show lower perplexity degradation after conversion than low-entropy layers at matched conversion counts?

5. Is per-layer attention entropy a better layer selection criterion than a naive strategy (convert last k layers or random k layers), as measured by perplexity preservation on WikiText-103 (200 test sequences) at matched eviction ratios k=4 and k=8?

---

## Reference Papers

Not provided - will discover in Phase 1

---

## Validation Results

### So What Test

Input from ICLR Workshop on Scalable Optimization for Efficient and Adaptive Foundation Models — significance pre-validated. Transformer self-attention scales as O(n²) in memory and FLOPS with sequence length, making long-context inference prohibitively expensive. Not all layers need full global attention: empirical work on BERT and GPT models shows that many layers exhibit highly local attention patterns (high entropy across positions rather than concentrated long-range focus). Replacing such layers with O(n·w) sliding window attention reduces peak attention memory by up to k/32 in a 32-layer model. If k=8 layers can be converted with < 5 pp accuracy loss, practitioners can deploy Llama-2-7B on 24GB GPUs at sequence lengths currently requiring 40-80GB cards. This directly addresses "Quadratic to Sub-Quadratic Model Conversion" and "Efficient Sub-Quadratic Foundation Models" — the most conversion-specific workshop topics. No prior pipeline attempt has operationalized this direction.

### Feasibility Check

All sub-questions testable immediately using:
- **Existing models:** meta-llama/Llama-2-7b-hf (HuggingFace) — modify `modeling_llama.py` to implement `SlidingWindowAttention` (replace causal full mask with banded mask of width w=512); no new packages required beyond standard transformers + torch
- **Existing benchmarks:** WikiText-103 (wikitext/wikitext-103-raw-v1, HuggingFace) for perplexity; GLUE SST-2 (nyu-mll/glue, HuggingFace) for classification accuracy — both with automatic evaluation, no human raters
- **Layer selection:** Compute per-layer attention entropy on 100 WikiText-103 calibration sequences using `output_attentions=True`; rank layers by mean entropy; select top-k for conversion
- **Baselines:** (1) Unmodified Llama-2-7B (full attention), (2) Random k layers converted, (3) Last k layers converted, (4) Entropy-guided top-k converted
- **Pilot feasibility:** 200 WikiText-103 test sequences + 872 SST-2 examples × 4 conditions × Llama-2-7B ≈ 200 × ~5s + 872 × ~3s × 4 = ~3500s ≈ 60 minutes on 1× H100. Pilot with 100 sequences: ≈ 30 minutes. Feasible in < 2 GPU-hours.
- **Statistical test:** Paired Wilcoxon signed-rank on per-sequence perplexity (entropy-guided vs random conversion); paired t-test on per-example SST-2 accuracy — scipy.stats, no frameworks
- **Memory measurement:** `torch.cuda.memory_allocated()` before and after attention computation per layer — standard PyTorch API
- **No new benchmarks, no synthetic data, no human evaluation, no future data required.**
- **No mamba-ssm, no flash-attn, no evolutionary search, no population-scale experiments.**

Feasibility constraints satisfied: pilot (100 WikiText-103 sequences + 200 SST-2 examples × 4 conditions) runnable in < 1 GPU-hour on a single H100.

---

## Phase 1 Input Package

<phase1-input>

### research_question
In Llama-2-7B, does replacing the top-k layers (by attention entropy on a calibration set, selecting layers with highest entropy as most amenable to local-window approximation) with sliding window attention (window size w=512 tokens) — at k=4 and k=8 of 32 total layers — reduce peak attention memory by ≥ k/32 × 100% while maintaining WikiText-103 perplexity within 2 points and GLUE SST-2 accuracy within 2 percentage points of the unmodified full-attention baseline, without any additional fine-tuning?

### detailed_question
1. Does replacing the 4 highest-entropy full-attention layers in Llama-2-7B with sliding window attention (w=512) maintain WikiText-103 perplexity within 2 points of the full-attention baseline (no fine-tuning), confirming that high-entropy layers tolerate local-window approximation?
2. Does the same 4-layer conversion maintain GLUE SST-2 accuracy within 2 percentage points of the full-attention baseline?
3. At k=8 converted layers (25% of all layers), does accuracy degradation remain bounded (perplexity < 5 points above baseline, SST-2 < 5 pp below baseline), and does peak attention FLOPS reduction scale approximately linearly with converted layer count?
4. Does attention entropy on a 100-sequence calibration set reliably identify layers tolerating sliding window conversion, with high-entropy layers showing lower perplexity degradation than low-entropy layers at matched conversion counts?
5. Is entropy-guided layer selection a better criterion than naive strategies (convert last k layers or random k layers), as measured by perplexity preservation on WikiText-103 at matched k=4 and k=8?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

- "Quadratic to Sub-Quadratic Model Conversion" is the only remaining primary workshop topic not yet operationalized across 11 prior pipeline iterations
- Sliding window attention is implementable by modifying the attention mask in `modeling_llama.py` (standard HuggingFace) — no new packages, no SSM infrastructure
- Per-layer attention entropy is a direct, measurable signal for layer convertibility — high entropy indicates diffuse attention patterns that local windows can approximate without accuracy loss
- WikiText-103 + GLUE SST-2 provide complementary evaluation: perplexity (language modeling quality) + classification accuracy (downstream task preservation)
- Pilot (100 WikiText-103 sequences × 4 conditions + 200 SST-2 examples) fits in < 1 GPU-hour on 1× H100 — well within the < 2 GPU-hour constraint established from h-e1 failure
- Short causal chain: measure per-layer entropy → select layers → replace attention mask → evaluate. No proxy variables, no multi-hop mechanism, no evolutionary search.
- h-e1 lesson applied: no population-scale experiments; single Llama-2-7B model with deterministic layer selection
- h-m3 lesson applied: layer selection uses direct attention entropy (not syntactic proxy); the signal IS the internal representation

### Techniques Used

Auto-Fill Mode (ROUTE_TO_0) — structured input extraction from ICLR Workshop CFP; direction selected by systematic elimination of all 11 prior failed/stalled angles; "Quadratic to Sub-Quadratic Model Conversion" identified as the only remaining high-feasibility unused primary workshop topic; feasibility cross-checked against h-e1 (< 2 GPU-hour pilot constraint) and h-m3 (direct signal, no proxy) lessons from Serena Memory records

### Areas for Further Exploration

Workshop topics not incorporated into primary research question (deprioritized due to prior attempts or complexity):
- Efficient Long Context Understanding (attempted as 10th brainstorm — attention-score KV cache eviction; re-routed before completion)
- Adaptive Fine-Tuning for Multimodal Foundation Models (attempted as 9th brainstorm — adaptive multimodal LoRA; re-routed)
- Sub-Quadratic Models for Foundational Tasks (deliberately deprioritized after 4 failed operationalization attempts via SSMs)
- Adaptive Routing with Mixture of Experts (stalled at Phase 2A in 5th brainstorm attempt)
- Retrieval Augmented Generation for Efficient Contextual Processing (8th brainstorm — RAG BM25; did not complete)
- Efficient Fine-Tuning for Continual Adaptation and Personalization (Fisher-rank LoRA, 6th brainstorm; stalled)
- Task Specific Adaptive Foundation Models (not yet attempted — potential future direction if this iteration fails)

---

## Next Steps

Proceed to Phase 1 - Targeted Research: `/phase1-targeted`

Target papers to find in Phase 1:
- Sliding window attention and local attention mechanisms (search: "sliding window attention transformer", "local attention LLM", "Longformer sliding window attention", "Mistral sliding window attention", "BigBird sparse attention")
- Quadratic to sub-quadratic conversion methods (search: "attention head pruning transformer", "converting full attention to local attention", "sub-quadratic attention conversion", "efficient attention approximation pre-trained LLM")
- Layer-wise attention pattern analysis (search: "per-layer attention entropy transformer", "attention head importance score", "attention pattern analysis BERT GPT", "layer-wise attention distribution LLM")
- Baseline conversion strategies (search: "random attention head pruning", "structured pruning transformer attention", "attention layer replacement inference efficiency")
- WikiText-103 and GLUE evaluation (search: "WikiText-103 perplexity benchmark LLM", "GLUE SST-2 sentiment classification evaluation", "language model perplexity efficient inference")

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
