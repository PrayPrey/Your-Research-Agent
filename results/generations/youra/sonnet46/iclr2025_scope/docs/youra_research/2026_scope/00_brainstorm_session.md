---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Dynamic LoRA Rank via Layer Activation Sparsity for Efficient Fine-Tuning"
---

# Research Brainstorm Session Results

**Session Date:** 2026-05-08
**Facilitator:** Research Question Architect
**Participant:** Anonymous
---

## Executive Summary

**Initial Interest:** Adaptive fine-tuning efficiency for foundation models — specifically, predicting optimal LoRA rank allocation per layer based on observable activation properties, enabling compute- and memory-efficient fine-tuning without manual rank search

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode — Run 3, new domain pivot from KV cache eviction)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

Source Type: Workshop CFP / Structured Input — ICLR Workshop on Scalable Optimization for Efficient and Adaptive Foundation Models.

The workshop targets scalable, adaptive fine-tuning and efficient inference for quadratic and sub-quadratic foundation models. A key challenge is parameter-efficient fine-tuning (PEFT): LoRA and its variants use a fixed, manually-tuned rank across all layers, ignoring per-layer intrinsic dimensionality. Different layers may require different rank allocations for optimal quality-efficiency tradeoffs — yet rank is typically set uniformly as a hyperparameter.

The previous two attempts (TEST_scope_4, Runs 1 and 2) both focused on KV cache eviction prediction via attention-based metrics and both failed:
- **Run 1**: Gini-coefficient concentration → directional inversion (high Gini = robustness, not fragility under H2O)
- **Run 2**: Shannon entropy → degenerate entropy (zero variance for long-context tasks with base LLaMA-3.1-8B in eager mode)

Both failures indicate that attention-based proxy metrics for KV eviction sensitivity are unreliable for this model configuration. A full domain pivot is warranted.

---

## Lessons from Previous Attempts

### What Was Tried Before

**TEST_scope_4, Run 1 (Phase 4 Failure - MUST_WORK_FAIL):**
- **Hypothesis:** Prefill attention concentration (Gini over L1-L16, top-10% cumulative mass) predicts KV eviction sensitivity — high-Gini prompts are fragile.
- **Result:** FAILED. beta_concentration = -0.260 (inverted sign), AUROC = 0.44 (below random).
- **Root cause:** H2O eviction is self-consistent with Gini — it preserves high-attention tokens by design, making high-Gini examples ROBUST, not fragile.

**TEST_scope_4, Run 2 (Phase 4 Failure - MUST_WORK_FAIL):**
- **Hypothesis:** Shannon attention entropy (L1-L16, non-recency positions) varies within LongBench task types as a per-instance discriminating signal for KV eviction sensitivity.
- **Result:** FAILED. Gate 0/5 task types passing. Entropy = 0.0 for ALL summarization and code instances. Mean within-task std = 0.148 (threshold 0.5).
- **Root cause:** LLaMA-3.1-8B base model in eager attention mode produces degenerate (near-zero) entropy on long-context inputs. The foundational measurement assumption is not supported.

**TEST_scope / TEST_scope_opus45 (Earlier Runs):**
- **Token influence heavy-tail (gradient-based Gini):** Mean Gini = 0.443, below 0.5 threshold. Gradient-based influence is more uniform than attention-based.
- **Architecture routing differentiation (Transformer vs Mamba vs RWKV):** RWKV dominated MQAR (99.57%), Mamba failed; N-gram too simple.
- **Post-hoc SSM conversion (weight rank):** Pre-trained projection weights are nearly full-rank (r_eff ~1600), invalidating low-rank SSM conversion.

### Why KV Cache Eviction Metric Approaches Failed

1. **Self-consistency trap with H2O:** Any attention-based metric (Gini, entropy) that H2O already uses to decide what to keep cannot independently predict what H2O will damage.
2. **Model degeneration at long context:** Base (non-Instruct) LLaMA in eager mode produces degenerate attention distributions for sequences >8K tokens — the very inputs where KV eviction matters most.
3. **Metric alignment problem:** Gradient-based influence ≠ attention importance; they measure orthogonal constructs.

### How This New Direction Avoids All Prior Pitfalls

1. **Domain pivot:** Move entirely away from KV cache eviction and attention metrics. Explore a different workshop topic: **efficient fine-tuning via adaptive LoRA rank allocation**.
2. **No attention metric dependency:** Use activation sparsity (fraction of near-zero ReLU/GeLU activations in MLP layers) — a static, forward-pass property unrelated to the prior failure modes.
3. **No long-context dependency:** Fine-tuning experiments use standard short-to-medium sequence lengths (GLUE/FLAN-style tasks, 128-512 tokens) where degenerate attention is not an issue.
4. **Existing benchmarks only:** GLUE, SuperGLUE, and standard PEFT evaluation benchmarks are well-established, require no new benchmark creation.
5. **Feasibility-first:** PEFT/LoRA infrastructure (HuggingFace PEFT library) is mature and widely available; activation sparsity is trivially measurable via hooks.

---

## Session Plan

Auto-extracted from structured input (ROUTE_TO_0 Run 3 failure recovery — full domain pivot to efficient fine-tuning topic)

---

## Technique Sessions

Auto-Fill Mode (ROUTE_TO_0) — No interactive sessions. Research direction derived from Workshop CFP topics + systematic failure analysis requiring domain pivot.

**Topics Mapped to New Research Direction:**

| Workshop Topic | Relevance to New Direction |
|----------------|---------------------------|
| Efficient Fine-Tuning for Continual Adaptation and Personalization | **Core:** LoRA rank allocation directly determines fine-tuning compute/memory cost |
| Task Specific Adaptive Foundation Models | Adaptive rank = different rank per layer/task, enabling task-specific efficiency |
| Model Optimization for Latency and Throughput Efficient Inference | Fewer LoRA parameters → lower memory overhead during adapter-based inference |
| Sub-Quadratic Models for Foundational Tasks | Activation sparsity connects to SSM-style compression intuitions |
| Adaptive Routing with Mixture of Experts | Per-layer rank allocation is analogous to adaptive expert routing |

---

## Research Question Development

### Initial Question

Can layer-wise activation sparsity (fraction of near-zero activations in MLP feed-forward layers) of a pre-trained LLM predict which layers benefit most from higher LoRA rank during fine-tuning, enabling a rank allocation strategy that matches uniform-high-rank quality at lower total parameter cost?

### Refined Question

Does the layer-wise activation sparsity ratio (fraction of activations below threshold ε in MLP layers of LLaMA-3-8B, measured on a fixed calibration set) significantly correlate with per-layer LoRA rank sensitivity — such that layers with LOW sparsity (dense activation patterns) require higher rank to achieve equivalent fine-tuning quality, as measured by the rank-quality Pearson correlation r >= 0.5 and a sparsity-guided rank allocation strategy achieving >= 95% of uniform-high-rank GLUE performance at <= 60% of total LoRA parameters?

### Detailed Sub-Questions

1. Does layer-wise activation sparsity (fraction of |activation| < ε across MLP layers L1-L32 of LLaMA-3-8B) vary significantly across layers on a fixed calibration set (e.g., Alpaca/FLAN), with coefficient of variation CV > 0.3, establishing that sparsity is a layer-discriminating signal?
2. Does per-layer LoRA rank sensitivity (measured as delta-accuracy when reducing rank from r=16 to r=4 on GLUE SST-2/MNLI fine-tuning) negatively correlate with layer activation sparsity (Pearson r <= -0.5), such that sparse layers tolerate low rank while dense layers require high rank?
3. Does a sparsity-guided adaptive rank allocation (high rank for low-sparsity layers, low rank for high-sparsity layers, with total parameters matched to a fixed budget) achieve >= 95% of uniform-r=16 GLUE aggregate performance while using <= 60% of the total LoRA parameter count?

---

## Reference Papers

*No reference papers provided — will discover in Phase 1*

(Key papers expected in Phase 1: LoRA (Hu et al. 2021), AdaLoRA (Zhang et al. 2023), DyLoRA (Valipour et al. 2022), SoRA/Sparse LoRA, activation sparsity in transformers (Gur-Ari et al. 2018, Mirzadeh et al. 2023 ReLU sparsity), LLaMA architecture analysis, GLUE benchmark paper)

---

## Validation Results

### So What Test

LoRA fine-tuning is the dominant method for adapting large language models to downstream tasks. However, it uses a fixed rank across all layers — a significant inefficiency, since different layers have different intrinsic dimensionality requirements. If layer-wise activation sparsity reliably predicts which layers need more expressive rank, practitioners can allocate rank non-uniformly: dense-activation layers get higher rank, sparse-activation layers get lower rank. This reduces total LoRA parameter count (and thus memory/compute overhead) without sacrificing fine-tuning quality. The practical impact is direct: lower memory overhead during fine-tuning and deployment of adapter-augmented models, with no accuracy loss. This is directly aligned with the workshop's call for "compute- and memory-efficient fine-tuning" and "personalized adaptation."

### Feasibility Check

- **Model:** LLaMA-3-8B (HuggingFace, publicly available; or GPT-2/LLaMA-3.2-1B for fast iteration)
- **Datasets:** GLUE SST-2, MNLI (public, well-established NLP benchmarks — no new benchmarks needed)
- **Calibration set:** Alpaca or FLAN-mini (public instruction-tuning data) for measuring activation sparsity
- **Infrastructure:** HuggingFace PEFT library (LoRA), standard PyTorch activation hooks — well-established tooling
- **Metrics:** Pearson correlation, delta-accuracy, parameter count ratios — all standard
- **No new benchmarks or synthetic data required:** Existing real datasets and benchmarks only
- **Timeline:** Achievable in 1-2 GPU-days (LLaMA-3-8B fine-tuning on GLUE is standard; activation measurement is a single forward pass)
- **Constraint check:** MANDATORY FEASIBILITY CONSTRAINTS satisfied — no new benchmarks, no synthetic data, no human evaluation

---

## Phase 1 Input Package

<phase1-input>

### research_question
Does layer-wise activation sparsity (fraction of near-zero activations in MLP feed-forward layers of LLaMA-3-8B) predict per-layer LoRA rank sensitivity during fine-tuning, such that a sparsity-guided adaptive rank allocation strategy matches the quality of uniform high-rank LoRA (r=16) on GLUE benchmarks while using <= 60% of the total LoRA parameter count?

### detailed_question
1. Does layer-wise MLP activation sparsity vary significantly across LLaMA-3-8B layers on a calibration set (CV > 0.3), establishing that sparsity is a layer-discriminating signal that can guide rank allocation?
2. Does per-layer LoRA rank sensitivity (delta-accuracy when reducing rank from r=16 to r=4 on GLUE SST-2/MNLI) negatively correlate with activation sparsity (Pearson r <= -0.5), with sparse layers tolerating low rank and dense layers requiring high rank?
3. Does a sparsity-guided adaptive rank allocation strategy achieve >= 95% of uniform-r=16 GLUE aggregate performance at <= 60% of the total LoRA parameter count, demonstrating practical efficiency gains?

### reference_papers
Not provided - will discover in Phase 1

(Expected: LoRA Hu et al. 2021, AdaLoRA Zhang et al. 2023, DyLoRA Valipour et al. 2022, activation sparsity in transformers Mirzadeh et al. 2023, SoRA/sparse LoRA variants, GLUE Wang et al. 2018)

</phase1-input>

---

## Session Insights

### Key Discoveries

- **Domain pivot lesson:** Both KV eviction metric approaches (concentration, entropy) failed due to fundamental incompatibilities with the H2O eviction mechanism and model behavior on long sequences. Continuing in this direction is counterproductive.
- **Activation sparsity as rank predictor:** Layer-wise activation sparsity is a well-studied, measurable property of transformer MLP layers that has not been used to guide LoRA rank allocation — a genuine gap.
- **Alignment with AdaLoRA literature:** AdaLoRA (Zhang et al. 2023) adapts rank using singular value decomposition during training. Our approach uses a cheaper, pre-training observable (activation sparsity) to allocate rank BEFORE fine-tuning begins — no SVD overhead, static measurement only.
- **Workshop alignment:** The ICLR scope workshop explicitly calls for "compute- and memory-efficient fine-tuning" and "personalized adaptation" — adaptive rank allocation directly addresses both.
- **Infrastructure leverage:** HuggingFace PEFT is mature; GLUE fine-tuning with LoRA is a standard benchmark setup. Prior pipeline failures provide no reusable code here, but the domain is simpler and better-supported.
- **Feasibility confirmed:** No new benchmarks, datasets, or human evaluation needed — pure empirical measurement on existing benchmarks.

### Techniques Used

Auto-Fill Mode (ROUTE_TO_0) — Systematic failure analysis (3 prior failure modes analyzed) + Workshop CFP topic pivot to efficient fine-tuning domain

### Areas for Further Exploration

- **Cross-architecture generalization:** Does the sparsity-rank correlation hold for Mistral-7B, Gemma-2B, or Phi-3? (Phase 2 sub-hypothesis candidate)
- **Task-specific calibration sets:** Does using task-specific calibration data (vs. general instruction tuning) improve the sparsity measurement quality?
- **Continual fine-tuning:** If activation sparsity changes after each task in a continual learning scenario, does re-measuring and re-allocating rank maintain efficiency across sequential tasks?
- **MoE connection:** In MoE models, do active expert patterns predict LoRA rank needs for each expert? (Workshop MoE topic connection)
- **Sub-quadratic models:** Do Mamba/SSM hybrid models show different activation sparsity patterns, and does the rank-sparsity correlation transfer? (Workshop sub-quadratic topic connection)

---

## Next Steps

Proceed to Phase 1 - Targeted Research

Focus Phase 1 search on:
1. AdaLoRA and dynamic rank allocation during fine-tuning (Zhang et al. 2023 and follow-ups)
2. Activation sparsity in transformer MLP layers — measurement methods and layer-wise patterns
3. LoRA rank selection strategies and sensitivity analysis (rank-quality tradeoffs)
4. PEFT efficiency benchmarks — comparing parameter budgets across methods
5. Any prior work connecting pre-training activation statistics to fine-tuning rank requirements

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
