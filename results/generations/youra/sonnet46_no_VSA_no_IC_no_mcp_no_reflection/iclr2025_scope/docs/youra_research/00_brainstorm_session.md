---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Efficient Adaptive Foundation Models via Sub-Quadratic KV"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-31
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Scalable optimization for efficient and adaptive foundation models, focusing on sub-quadratic architectures, KV cache efficiency, and adaptive fine-tuning for inference-efficient models.

**Session Approach:** Auto-Fill Mode (Structured Input Detected)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

The workshop targets advances in scalable, adaptive fine-tuning, calibration, and conversion to yield inference-efficient quadratic and sub-quadratic foundation models across vision, language, and multi-modal domains. Key challenges include efficient long-context understanding, KV cache management under growing context demands, RAG integration with prefill cost concerns, Mixture of Experts (MoE) routing adaptation, and the emerging sub-quadratic model paradigm with constant KV states. Source Type: Workshop CFP / Structured Input.

---

## Lessons from Previous Attempts

N/A - First attempt

---

## Session Plan

Auto-extracted from structured input. The CFP defines a clear research landscape: (1) sub-quadratic vs. quadratic transformer tradeoffs, (2) KV cache efficiency under long-context, (3) adaptive fine-tuning (LoRA-style, MoE routing, continual learning), (4) RAG prefill cost reduction. Feasibility constraint enforces use of existing datasets and benchmarks only — no new benchmarks, no synthetic data, no human evaluation.

---

## Technique Sessions

Auto-Fill Mode - No interactive sessions. Research direction extracted directly from structured Workshop CFP input with mandatory feasibility constraints applied.

---

## Research Question Development

### Initial Question

Can existing sub-quadratic sequence models (e.g., Mamba, RWKV, RetNet) be efficiently fine-tuned on downstream tasks using parameter-efficient methods (e.g., LoRA variants) to match or exceed quadratic transformer baselines while maintaining their constant-KV-state inference advantage, as measured on existing NLP benchmarks?

### Refined Question

**Do parameter-efficient fine-tuning (PEFT) methods designed for transformers (e.g., LoRA, AdaLoRA, IA³) transfer effectively to sub-quadratic sequence models (e.g., Mamba, RWKV), and can their adaptation quality be further improved by exploiting the recurrent state structure unique to these architectures, as evaluated on established language modeling and downstream task benchmarks?**

This question is directly testable using:
- Existing sub-quadratic models (Mamba-1/2, RWKV-4/6, RetNet)
- Existing PEFT methods (LoRA, AdaLoRA, IA³, DoRA)
- Existing benchmarks (GLUE, SuperGLUE, LM-Eval harness tasks, MMLU)
- No new benchmarks, synthetic data, or human evaluation required

### Detailed Sub-Questions

1. **PEFT Transfer Effectiveness:** Do LoRA rank decompositions applied to sub-quadratic model weight matrices (projection layers, SSM input/output projections) achieve comparable downstream task accuracy to full fine-tuning, and how does this compare to LoRA on equivalent-size transformers?

2. **State-Aware Adaptation:** Can PEFT methods be designed to additionally fine-tune or condition on the recurrent/SSM state update matrices (A, B, C in Mamba notation) to better capture task-specific context retention, and does this outperform naive LoRA application on only linear projections?

3. **Efficiency-Accuracy Tradeoff:** What is the Pareto frontier of trainable parameter count vs. downstream task accuracy for PEFT-adapted sub-quadratic models, and how does it compare to the same frontier for transformers of similar base model size?

4. **Long-Context Adaptation:** Under long-context evaluation (e.g., SCROLLS, LongBench), do PEFT-adapted sub-quadratic models better retain their inference-time efficiency advantage (constant KV state) compared to PEFT-adapted transformers (which still require O(n) KV cache growth)?

5. **Continual Fine-Tuning Stability:** When sequentially fine-tuned on multiple tasks (continual learning setting), do sub-quadratic models with PEFT exhibit less catastrophic forgetting than transformer counterparts, given their compressed state representation?

---

## Reference Papers

Not provided - will discover in Phase 1. Key search targets:
- Mamba (Gu & Dao, 2023), Mamba-2 (Dao & Gu, 2024)
- RWKV (Peng et al., 2023), RetNet (Sun et al., 2023)
- LoRA (Hu et al., 2022), AdaLoRA (Zhang et al., 2023), DoRA (Liu et al., 2024)
- State Space Models for NLP survey papers
- PEFT survey (Ding et al., 2023)
- LM-Eval Harness (Gao et al., 2021)

---

## Validation Results

### So What Test

**Significance:** Sub-quadratic models offer O(1) inference-time memory (no KV cache growth) — a transformative advantage for long-context deployment. However, their practical adoption is bottlenecked by: (a) unclear PEFT adaptation pathways (most PEFT work assumes transformer attention), and (b) unknown whether their state-compression inductive bias helps or hurts task-specific adaptation. Resolving this directly impacts whether sub-quadratic models can replace transformers in production inference pipelines.

**Contribution:** First systematic comparison of PEFT methods on sub-quadratic vs. quadratic models with equal experimental controls, providing practitioners with actionable guidance on model selection and fine-tuning strategy.

Input from established research venue (ICLR workshop) — significance pre-validated by workshop scope alignment.

### Feasibility Check

✅ **PASS — All feasibility constraints satisfied:**

- **Existing models:** Mamba, RWKV, RetNet — all publicly available with pretrained checkpoints
- **Existing PEFT methods:** LoRA, AdaLoRA, IA³, DoRA — all open-source implementations available
- **Existing benchmarks:** GLUE, SuperGLUE, MMLU, LM-Eval Harness — no new benchmarks required
- **No synthetic data:** Experiments use standard NLP corpora (WikiText, C4, GLUE train splits)
- **No human evaluation:** All metrics are automated (accuracy, perplexity, F1)
- **No new scoring frameworks:** Uses established leaderboard metrics

Structured input indicates clear research direction with immediate testability on existing infrastructure.

---

## Phase 1 Input Package

<phase1-input>

### research_question
Do parameter-efficient fine-tuning (PEFT) methods designed for transformers (e.g., LoRA, AdaLoRA, IA³) transfer effectively to sub-quadratic sequence models (e.g., Mamba, RWKV), and can their adaptation quality be further improved by exploiting the recurrent state structure unique to these architectures, as evaluated on established language modeling and downstream task benchmarks?

### detailed_question
1. Do LoRA rank decompositions applied to sub-quadratic model weight matrices achieve comparable downstream task accuracy to full fine-tuning, and how does this compare to LoRA on equivalent-size transformers?
2. Can PEFT methods be designed to additionally fine-tune or condition on the recurrent/SSM state update matrices (A, B, C in Mamba) to better capture task-specific context retention, outperforming naive LoRA on linear projections only?
3. What is the Pareto frontier of trainable parameter count vs. downstream task accuracy for PEFT-adapted sub-quadratic models vs. transformers of similar base model size?
4. Under long-context evaluation (SCROLLS, LongBench), do PEFT-adapted sub-quadratic models better retain their inference-time efficiency advantage compared to PEFT-adapted transformers?
5. In continual fine-tuning (sequential multi-task), do sub-quadratic models with PEFT exhibit less catastrophic forgetting than transformer counterparts given their compressed state representation?

### reference_papers
Not provided - will discover in Phase 1. Key targets: Mamba (Gu & Dao 2023), Mamba-2 (Dao & Gu 2024), RWKV (Peng et al. 2023), RetNet (Sun et al. 2023), LoRA (Hu et al. 2022), AdaLoRA (Zhang et al. 2023), DoRA (Liu et al. 2024), PEFT survey (Ding et al. 2023), LM-Eval Harness (Gao et al. 2021).

</phase1-input>

---

## Session Insights

### Key Discoveries

- The CFP identifies a critical gap: PEFT methods are mature for transformers but their applicability to sub-quadratic models (with fundamentally different parameterization) is unstudied at scale
- The "constant KV state" property of sub-quadratic models is both their inference advantage AND a potential adaptation challenge (compressed state = less room for task-specific context storage)
- Feasibility constraints naturally filter to the PEFT-on-SSM direction: it requires only existing models, existing PEFT implementations, and existing NLP benchmarks
- The state structure adaptation angle (fine-tuning A/B/C matrices in SSMs) is a novel PEFT direction not addressed by transformer-focused methods

### Techniques Used

Auto-Fill Mode (structured input extraction). Research direction synthesized by:
1. Identifying core tension in CFP (sub-quadratic efficiency vs. adaptation capability)
2. Applying feasibility constraints to filter out benchmark-creation or human-eval approaches
3. Converging on PEFT-on-SSM as the intersection of workshop scope + immediate testability

### Areas for Further Exploration

- **MoE + Sub-Quadratic Hybrid:** Learned routing over SSM vs. attention layers for mixed architectures
- **RAG + SSM Integration:** How recurrent state compression affects RAG prefill and retrieval integration cost
- **Quadratic-to-Sub-Quadratic Distillation:** Knowledge distillation from transformer to SSM with PEFT
- **Vision/Multimodal SSMs:** PEFT for Vision Mamba or multimodal sub-quadratic models (Vim, PlainMamba)
- **KV Cache Compression for Transformers:** Orthogonal direction — token eviction / quantization for long-context transformers

---

## Next Steps

Proceed to Phase 1 - Targeted Research: `/phase1-targeted`

Phase 1 should focus on:
1. Collecting papers on PEFT methods applied to or evaluated on SSM-based models
2. Surveying existing Mamba/RWKV fine-tuning work (if any) on downstream tasks
3. Identifying experimental setups in existing SSM papers that used GLUE/SuperGLUE/MMLU
4. Searching for any prior work comparing PEFT efficiency on sub-quadratic vs. quadratic models

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
