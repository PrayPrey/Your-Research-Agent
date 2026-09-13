---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Quadratic-to-Sub-Quadratic Conversion for Long-Con"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-03
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Scalable optimization for efficient and adaptive foundation models — specifically quadratic-to-sub-quadratic conversion for long-context understanding, building on prior failed attempts with KV eviction approaches.

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

In the rapidly evolving landscape of AI, the development of scalable optimization methods to yield efficient and adaptive foundation models has significant demand in the space of their inference service. Enabling model efficiency while allowing them to be adaptable to various new downstream tasks has multifold challenges — including continual weight updates, compute- and memory-efficient fine-tuning, personalized adaptation, KV cache management for long contexts, RAG integration, MoE routing, and sub-quadratic model design.

Source Type: Workshop CFP / Structured Input (ICLR 2025 Workshop on Scalable Optimization for Efficient and Adaptive Foundation Models)

Previous failure context exists. This brainstorm pivots away from the failed KV eviction direction toward quadratic-to-sub-quadratic conversion, which is directly listed in the workshop topics and testable on existing benchmarks.

---

## Lessons from Previous Attempts

### What Was Tried Before

**Attempt 1 (H-E1): WIAB Attention Divergence Hypothesis**
- Hypothesis: Within-and-across-batch (WIAB) attention score divergence is CLC-specific and correlates with rank-drop in the W_O projection space.
- Criterion 1 (Spearman ρ < 0.9 in ≥50% heads): CONFIRMED (median ρ = 0.6239, frac_below_09 = 98.2%)
- Criterion 2 (CLC-rank-drop Pearson r ≥ 0.3): FAILED (r = 7.1e-05)
- Root cause: Attention-weight proxy insufficient for CLC-rank-drop specificity; max_length=256 too short for CLC variance; full LOO projection (W_O) required but costs ~6 min/prompt on H100.
- Consequence: h-m1 through h-m4 all blocked on h-e1 PASS.

**Attempt 2 (H-M2): Boundary Token Eviction in H2O**
- Hypothesis: H2O greedy eviction removes structurally critical boundary tokens at 50% compression.
- Condition A result: frac_below_80 = 1.000 (all examples below 80% retention), accuracy = 2.8% — catastrophic failure confirmed.
- Condition B (H2O + 10% boundary reservation): experiment incomplete (process interruptions).
- Root cause: At 50% KV compression, H2O causes catastrophic boundary token eviction regardless of boundary type; near-zero accuracy makes Condition B comparison moot for the original hypothesis framing.

### Why It Failed

1. The theoretical chain (WIAB → CLC-specificity → rank-drop) could not be established with attention-weight proxies at short context lengths.
2. The practical eviction direction (H2O boundary protection) demonstrated the problem was too severe to be fixed by a 10% reservation — catastrophic degradation at 50% compression is a fundamental limitation of greedy eviction, not a boundary-protection gap.
3. The entire h-m1..h-m4 chain was dependent on h-e1 passing first.

### How THIS Direction Avoids Those Pitfalls

- **No attention proxy**: New direction does not rely on attention-weight approximations of any theoretical quantity.
- **No eviction mechanism**: Entirely different paradigm — model architecture conversion (transformer → sub-quadratic), not cache management.
- **No dependency chain**: New hypotheses can be independently validated without a prerequisite existence hypothesis.
- **Directly testable**: Sub-quadratic model performance on existing benchmarks (LongBench v2, SCROLLS) can be measured with existing open-source models (Mamba, RWKV, Griffin) using standard eval harnesses.
- **Feasibility constraints satisfied**: No new benchmarks, no synthetic data, no human evaluation.

---

## Session Plan

ROUTE_TO_0 Auto-extracted from structured input. New direction selected based on: (1) failure analysis of previous KV eviction approach, (2) explicit workshop topic alignment ("Quadratic to Sub-Quadratic Model Conversion"), (3) immediate testability on existing benchmarks.

---

## Technique Sessions

ROUTE_TO_0 Auto-Fill Mode — No interactive sessions. Direction determined by failure context merger with current workshop CFP input.

---

## Research Question Development

### Initial Question

How do sub-quadratic models (Mamba, RWKV, Griffin) compare to full-attention transformers on long-context tasks, and can structured conversion of pretrained transformers to sub-quadratic architectures preserve performance on existing benchmarks?

### Refined Question

When a pretrained transformer is converted to a sub-quadratic architecture (e.g., via linear attention substitution or selective state-space distillation), does the converted model retain ≥90% of the original model's accuracy on existing long-context benchmarks (LongBench v2, SCROLLS) at sequence lengths ≥4096, and does this retention vary systematically by task type (retrieval vs. summarization vs. QA)?

### Detailed Sub-Questions

1. Which sub-quadratic conversion strategy (linear attention substitution, SSM distillation, hybrid layer replacement) achieves the highest accuracy retention on existing long-context benchmarks relative to the original transformer, without requiring new benchmarks or synthetic data?
2. Does accuracy retention after conversion degrade monotonically with sequence length on existing benchmarks (LongBench v2, SCROLLS), and if so, at what sequence length threshold does degradation become statistically significant?
3. Is there a task-type interaction: do retrieval-heavy tasks (multi-doc QA) show larger post-conversion accuracy drops than summarization or single-doc QA tasks, as measured on existing LongBench v2 category splits?
4. Does fine-tuning the converted model on existing training splits of LongBench v2 / SCROLLS recover statistically significant accuracy versus zero-shot conversion, and does recovery differ by conversion strategy?
5. Can existing open-source sub-quadratic models (Mamba-3B, RWKV-7B) trained from scratch match converted models on identical benchmark subsets, or does conversion from a strong transformer prior provide measurable advantage on existing eval sets?

---

## Reference Papers

Not provided - will discover in Phase 1

---

## Validation Results

### So What Test

Input from established research venue (ICLR 2025 Workshop on Scalable Optimization for Efficient and Adaptive Foundation Models) — significance pre-validated. "Quadratic to Sub-Quadratic Model Conversion" is an explicit workshop topic. The question of whether converted sub-quadratic models preserve long-context performance is directly relevant to inference efficiency deployment. Solving this would enable dropping KV cache overhead entirely (O(1) state vs O(n) cache) while preserving task accuracy — high practical and theoretical impact. Previous WIAB/eviction direction confirmed the problem exists; this direction attacks it architecturally rather than via cache management.

### Feasibility Check

All proposed sub-questions testable immediately using:
- Existing benchmarks: LongBench v2 (503 questions, 8 categories), SCROLLS (existing splits)
- Existing models: LLaMA-3-8B-Instruct (transformer), Mamba (SSM), RWKV-7B, Griffin — all open-source
- Existing conversion tools: Based on published methods (e.g., GoldFinch, MambaFormer, linearization papers)
- No new benchmarks, synthetic data, human evaluation, or annotation required
- Feasibility constraints satisfied

---

## Phase 1 Input Package

<phase1-input>

### research_question
When a pretrained transformer is converted to a sub-quadratic architecture (e.g., via linear attention substitution or selective state-space distillation), does the converted model retain ≥90% of the original model's accuracy on existing long-context benchmarks (LongBench v2, SCROLLS) at sequence lengths ≥4096, and does this retention vary systematically by task type (retrieval vs. summarization vs. QA)?

### detailed_question
1. Which sub-quadratic conversion strategy (linear attention substitution, SSM distillation, hybrid layer replacement) achieves the highest accuracy retention on existing long-context benchmarks relative to the original transformer, without requiring new benchmarks or synthetic data?
2. Does accuracy retention after conversion degrade monotonically with sequence length on existing benchmarks (LongBench v2, SCROLLS), and if so, at what sequence length threshold does degradation become statistically significant?
3. Is there a task-type interaction: do retrieval-heavy tasks (multi-doc QA) show larger post-conversion accuracy drops than summarization or single-doc QA tasks, as measured on existing LongBench v2 category splits?
4. Does fine-tuning the converted model on existing training splits of LongBench v2 / SCROLLS recover statistically significant accuracy versus zero-shot conversion, and does recovery differ by conversion strategy?
5. Can existing open-source sub-quadratic models (Mamba-3B, RWKV-7B) trained from scratch match converted models on identical benchmark subsets, or does conversion from a strong transformer prior provide measurable advantage on existing eval sets?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

- Previous KV eviction direction (H2O boundary protection) failed at both theoretical (WIAB/CLC proxy) and practical (catastrophic degradation at 50% compression) levels
- Workshop CFP explicitly lists "Quadratic to Sub-Quadratic Model Conversion" as a topic — this is directly in scope
- Sub-quadratic conversion is independently testable without prerequisite existence hypotheses (avoids the h-e1 blocking chain)
- Existing open-source models (Mamba, RWKV, Griffin) and benchmarks (LongBench v2, SCROLLS) provide complete experimental infrastructure
- Task-type variation in conversion accuracy is a concrete, measurable prediction that differentiates this from generic "sub-quadratic is worse" claims

### Techniques Used

ROUTE_TO_0 Auto-Fill Mode — failure context merger with structured workshop CFP input (Serena Memory: failure_h-m2_run1, superseded_h-e1)

### Areas for Further Exploration

- Adaptive fine-tuning for multimodal foundation models (vision+language long-context) — workshop topic not pursued
- MoE routing policy optimization for test-time adaptation — workshop topic not pursued
- RAG integration with sub-quadratic models — interaction between retrieval prefill and SSM state compression
- Efficient fine-tuning for continual adaptation — orthogonal to conversion direction
- Model optimization for latency/throughput — downstream of architecture conversion success

---

## Next Steps

Proceed to Phase 1 - Targeted Research using `/phase1-targeted` with the research_question and detailed_question from the Phase 1 Input Package above.

Focus Phase 1 literature search on:
- Quadratic-to-sub-quadratic conversion methods (GoldFinch, MambaFormer, linear attention distillation)
- Sub-quadratic model benchmarks on LongBench v2, SCROLLS, PG-19
- Transformer linearization and SSM distillation approaches
- Task-type performance breakdowns for SSM vs transformer on long-context tasks
- Hybrid architectures (e.g., Jamba, Zamba) that mix attention and SSM layers

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
