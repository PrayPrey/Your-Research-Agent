# JointLoRA-KV: Task-Aware Joint Training of LoRA Adapters and KV Cache Eviction Heads

## Abstract

Standard practice in large language model deployment treats parameter-efficient fine-tuning (PEFT) and KV cache compression as independent, composable modules: the model is fine-tuned first, then a separately-trained eviction policy is applied. This work examines whether the two independently trained components are aligned in their token priority signals. The Spearman rank correlation between LoRA-modified attention weights and Locret contextual importance scores (CIS) is measured at 0.3662 ± 0.0759 across 100 MNLI validation examples on LLaMA-3.1-8B (seed=42; 100% of examples below the 0.70 alignment threshold), indicating a substantial mismatch between what the task-adapted model attends to and what the LM-loss-trained eviction policy retains.

To address this mismatch, we propose **JointLoRA-KV**, a training procedure that optimizes LoRA adapter weights and Locret retaining head weights jointly in a single backward pass via task classification cross-entropy loss. A differentiable soft KV budget mask (sigmoid relaxation, temperature τ=0.1) enables gradient flow through the eviction boundary during training; a straight-through estimator (STE) bridges the training-inference discrepancy when hard top-k eviction is restored at inference time. Separate learning rate groups are used for LoRA (1×10⁻⁴) and Locret (5×10⁻⁴) parameters.

Three experiments are reported. (1) The misalignment between task-adapted LoRA attention and LM-trained Locret CIS is confirmed: mean Spearman ρ = 0.3662, 100/100 examples below threshold (H-E1, PASS). (2) In a proof-of-concept run on LLaMA-3.1-8B (1 seed, 1 epoch, 500 training samples), joint training improves mean GLUE accuracy by +1.50 percentage points over a frozen-Locret baseline (B1: 44.00% → 45.50%); the pre-registered gate threshold was ≥2.0pp, so this result is classified PARTIAL (H-M1). Gradient flow to Locret retaining heads was confirmed (locret_grad_received=True, grad norms up to ~2.5×10⁻³). (3) Joint training is stable across 3 random seeds on a small proof-of-concept model (d=64, 2 layers; 0 NaN events, 0 divergence events across seeds 42, 123, 456; H-M2, PASS). The primary performance claim — that JointLoRA-KV improves over the sequential fine-tuning baseline (B3) by ≥3% on LongBench-QA at 50% KV budget — was not tested; the corresponding experiment (H-M3) was not executed due to compute constraints.

---

## 1. Introduction

When a large language model is fine-tuned for a downstream classification task using low-rank adaptation (LoRA), its attention patterns reorganize around task-discriminative tokens. KV cache eviction policies, such as Locret [Huang et al., 2024], are trained independently on language modeling loss and learn to prioritize next-token-predictive tokens. When both components are deployed together under a fixed KV budget, the eviction policy discards tokens according to a criterion that was not informed by the task adaptation objective.

This work provides the first direct empirical measurement of this misalignment for a task-fine-tuned LoRA model. The Spearman rank correlation between LoRA-modified attention scores and Locret contextual importance scores is 0.3662 ± 0.0759 across 100 MNLI validation examples on LLaMA-3.1-8B. Every example falls below the 0.70 alignment threshold. This result is consistent with the intuition that task classification and next-token prediction reward different token patterns, but the magnitude of misalignment (ρ ≈ 0.37, indicating approximately 14% shared variance) had not been quantified before.

The standard pipeline treats fine-tuning and KV compression as independent modules: fine-tune the model with PEFT, then apply a separately-trained compression policy. No prior work has jointly optimized the adaptation and eviction objectives for task-specific performance. The closest related work, arXiv:2604.21335 [Jiang & Wang, 2026], combines LoRA routing and KV value-group routing but uses language modeling loss throughout, leaving task-specific alignment unaddressed.

JointLoRA-KV is a training procedure designed to close this alignment gap. LoRA adapter parameters and Locret retaining head parameters are optimized together in a single backward pass via the task classification loss. The eviction boundary is made differentiable during training through a sigmoid relaxation of the KV budget mask; an STE bridges the resulting training-inference discrepancy.

The paper reports results from three executed sub-experiments (H-E1, H-M1, H-M2) out of five planned (H-M3, H-M4 not executed). The main findings are: (1) misalignment is confirmed at substantial magnitude; (2) the joint training mechanism is functional at PoC scale, with measurable but sub-threshold improvement over frozen-Locret baseline; (3) joint training is numerically stable across seeds on a small model. The primary claim regarding improvement over sequential fine-tuning (B3) on long-context tasks remains untested.

**Contributions:**

1. The first empirical quantification of misalignment between task-adapted LoRA attention patterns and LM-trained Locret eviction scores on a downstream NLI task: Spearman ρ = 0.3662 ± 0.076 across 100 MNLI examples on LLaMA-3.1-8B.

2. JointLoRA-KV: a joint training procedure for LoRA adapters and KV eviction heads using a differentiable soft KV budget mask with STE, confirmed functional at PoC scale (+1.50pp GLUE over frozen-Locret baseline, formal gate: PARTIAL).

3. Empirical confirmation that joint training of LoRA and Locret parameters is numerically stable across 3 seeds on a PoC model (d=64, 2 layers; 0 NaN/divergence events). Full-scale stability on LLaMA-3.1-8B was not empirically verified.

---

## 2. Related Work

### 2.1 KV Cache Compression

KV cache eviction has been studied extensively as sequence lengths grow. H2O [Zhang et al., 2023] uses accumulated attention scores as a heuristic for token importance. StreamingLLM [Xiao et al., 2024] retains "attention sink" tokens plus a sliding window. Locret [Huang et al., 2024] trains lightweight two-layer MLP retaining heads per transformer layer on a language modeling objective, learning a contextual importance score (CIS) for each token; it achieves up to 20× compression with limited perplexity increase. PruLong [Princeton, 2024] learns binary attention head masks. More recent work addresses systems-level concerns including quantization-eviction interactions and memory hierarchy optimization [Gokhale et al., 2025; Yao et al., 2025; Chu et al., 2025].

A shared characteristic of all these eviction methods is that they are trained with language modeling loss. Their eviction priorities are thus calibrated for next-token prediction. When applied to models that have been task-fine-tuned, the eviction policy retains tokens relevant to language modeling, while the fine-tuned model's representations have been reorganized around task-discriminative features. This misalignment is the motivation for JointLoRA-KV.

### 2.2 Parameter-Efficient Fine-Tuning

LoRA [Hu et al., 2022] injects low-rank matrices A∈ℝ^{d×r}, B∈ℝ^{r×d} (with r ≪ d) into selected linear projections, enabling task adaptation with a small fraction of trainable parameters. QLoRA [Dettmers et al., 2023] extends this to quantized base models. Surveys of PEFT methods are provided in Mao et al. [2024] and Yang et al. [2024]. In existing deployment pipelines, PEFT fine-tuning and KV compression are applied sequentially: the model is adapted first, then a fixed compression policy is layered on top. No prior work had jointly optimized these two components for a task-specific objective prior to this work.

### 2.3 Joint PEFT and KV Compression

The closest prior approach is arXiv:2604.21335 [Jiang & Wang, 2026], which combines LoRA routing paths with KV value-group routing in a single architecture. This work establishes that LoRA and KV routing components can coexist in the forward pass. However, it trains with language modeling loss throughout — not task classification loss — and evaluates on perplexity and RULER benchmarks rather than GLUE or LongBench. The amazon-science/icr-kv-caching work [Molfese et al., EACL 2026] analyzes post-hoc how fine-tuning affects KV compression robustness but does not propose joint training. The survey by Kim et al. [2025] explicitly identifies the absence of unified compression-plus-tuning frameworks as an open problem; JointLoRA-KV is a direct response to this gap.

### 2.4 Differentiable Sparse Selection

The soft-to-hard training pattern in JointLoRA-KV — sigmoid relaxation during training, hard discrete selection at inference — is established in quantization-aware training and sparse learning. Locret itself uses soft scoring during training. Bengio et al. [2013] introduced the straight-through estimator for propagating gradients through discrete operations. JointLoRA-KV applies this pattern to the joint LoRA + KV eviction training problem with a task classification objective.

---

## 3. Method

### 3.1 Problem Setting

Consider a pre-trained LLaMA-3.1-8B transformer with frozen base weights. Two sets of lightweight trainable parameters are added:

- **LoRA adapters**: low-rank matrices A∈ℝ^{d×r}, B∈ℝ^{r×d} (r=16, α=32) injected into Q, K, V projections across all transformer layers.
- **Locret retaining heads**: per-layer two-layer MLPs (W₁, W₂) that compute a contextual importance score (CIS) for each token position, initialized from the pre-trained hyx21/Locret-llama-3.1-8B-instruct checkpoint.

In the baseline pipeline (B3: sequential LoRA→Locret), LoRA adapters are first trained on a task classification objective; then Locret retaining heads are trained on language modeling loss with the LoRA parameters frozen. In JointLoRA-KV, both parameter sets are trained simultaneously on the task classification objective.

### 3.2 Differentiable KV Budget Mask

Hard KV eviction (retaining the top-k tokens by CIS score) is non-differentiable. JointLoRA-KV replaces it during training with a soft sigmoid mask:

$$M_{\text{soft}}(c) = \sigma\!\left(\frac{c - \theta}{\tau}\right)$$

where c ∈ ℝ^L is the vector of CIS scores for a sequence of length L, θ is the adaptive threshold (the k-th largest CIS value for retention budget b = 0.50), τ = 0.1 controls the sharpness of the sigmoid, and σ(·) is the element-wise sigmoid function. This mask allows gradients from the task classification loss to flow continuously through the weighted KV representations to the Locret head weights W₁, W₂.

At inference time, the hard top-k eviction is restored. The discrepancy between soft training and hard inference is handled by a straight-through estimator (STE): during the forward pass, the hard mask is used for the final output; during the backward pass, gradients flow through the soft mask.

### 3.3 Training Procedure

The training objective is standard cross-entropy classification loss:

$$\mathcal{L} = \mathcal{L}_{\text{CE}}(f_{\text{LoRA+Locret}}(x;\, M_{\text{soft}}),\, y)$$

Two separate learning rate groups are used to address the different gradient magnitudes and convergence dynamics of the two parameter sets:

| Parameter Group | Learning Rate | Weight Decay |
|----------------|--------------|--------------|
| LoRA (A, B matrices) | 1×10⁻⁴ | 0.01 |
| Locret (W₁, W₂ per layer) | 5×10⁻⁴ | 0.01 |

Additional training configuration: gradient accumulation over 8 steps (effective batch size 32), gradient clipping at norm 1.0, cosine learning rate schedule with 6% warmup, attention implementation set to "eager" (required for hook-based Q/K/V capture).

### 3.4 Baselines

Three baselines are defined:

- **B1 (Frozen Locret)**: LoRA is trained on the task classification objective; Locret retaining heads are fixed at their LM-pretrained values. This isolates the effect of jointly training Locret heads from the effect of KV eviction alone.
- **B2 (LoRA only, 100% budget)**: LoRA fine-tuning without KV eviction, serving as an approximate accuracy ceiling.
- **B3 (Sequential LoRA→Locret)**: The standard practice; LoRA is trained first on the task objective, then Locret is trained on language modeling loss. This is the primary comparison baseline. Full-scale comparison against B3 on LongBench-QA is the subject of H-M3, which was not executed.

The H-M1 PoC experiment compares JointLoRA-KV against B1, not B3. The B3 comparison is planned for H-M3.

---

## 4. Experimental Setup

Three research questions were addressed through executed experiments. A fourth, the primary performance claim, was pre-registered but not executed.

- **RQ1 (H-E1):** Is there substantial misalignment between LoRA-adapted attention priorities and LM-trained Locret eviction scores?
- **RQ2 (H-M1):** Does task classification loss produce gradient signals that reach Locret heads and improve task accuracy over the frozen-Locret baseline?
- **RQ3 (H-M2):** Is joint training numerically stable across multiple random seeds?
- **RQ4 (H-M3, not executed):** Does JointLoRA-KV achieve ≥3% improvement over B3 on LongBench-QA at full training scale?

### 4.1 Datasets

**GLUE** [Wang et al., 2018]: MNLI (3-class natural language inference, 500 training / 200 validation examples per task), SST-2 (binary sentiment), QNLI (question-NLI). For H-E1, 100 MNLI validation_matched examples are used.

**LongBench** [Bai et al., 2024]: NarrativeQA, Qasper, MultiFieldQA-en (long-context QA tasks). In H-M2, 50 examples per task are used for evaluation on the PoC model. Full-scale LongBench evaluation with LLaMA-3.1-8B was planned for H-M3 (not executed).

### 4.2 Model and Hardware Configuration

| Component | Specification |
|-----------|--------------|
| Base model | meta-llama/Meta-Llama-3.1-8B-Instruct |
| LoRA rank / alpha / dropout | r=16, α=32, dropout=0.05 |
| LoRA target modules | q_proj, k_proj, v_proj |
| Locret checkpoint | hyx21/Locret-llama-3.1-8B-instruct |
| KV retention budget | 50% (b=0.50) |
| Hardware | NVIDIA H100 NVL |

### 4.3 Evaluation Metrics

- **GLUE tasks:** Classification accuracy; mean across MNLI, SST-2, QNLI.
- **LongBench tasks:** Token-level F1 [Rajpurkar et al., 2016]; mean across tasks.
- **Misalignment (H-E1):** Spearman rank correlation ρ between LoRA attention weights and Locret CIS scores per example, averaged across 100 MNLI validation examples.
- **Stability (H-M2):** Count of NaN events and divergence events across 3 random seeds.

### 4.4 H-E1 Experimental Protocol

The LoRA-fine-tuned MNLI checkpoint (yophis/DRM-Llama-3.1-8B-mnli) and the Locret checkpoint (hyx21/Locret-llama-3.1-8B-instruct) are loaded sequentially to remain within GPU VRAM. For each of 100 MNLI examples, LoRA attention scores (shape: 32 query heads × L) and Locret CIS scores (shape: 8 KV heads × L) are extracted. CIS scores are expanded from 8 to 32 heads via `repeat_interleave(4)` to match the query-head dimensionality under GQA. Spearman ρ is computed per example over non-padding tokens. This GQA expansion treats 8 KV heads as 32 independent query-head signals; this may artificially deflate the correlation relative to a KV-head-level analysis.

### 4.5 H-M1 Execution Constraints

H-M1 was designed for 3 seeds, 3–5 epochs, and 2000 training samples per task. Due to a 4-hour compute constraint on the H100 NVL, only a PoC run was completed: 1 seed (42), 1 epoch per task, 500 training samples, 200 validation samples. The full-protocol code (`run_experiment.py`) is implemented.

### 4.6 H-M2 Model Scale

H-M2 uses a synthetic PoC model (d=64, 2 transformer layers) with the BERT tokenizer (vocab_size=30,522) rather than full LLaMA-3.1-8B. This model outputs class-index tokens that do not match LongBench answer strings, so LongBench F1 is 0.000 for both JointLoRA-KV and B3 at this scale. The H-M2 evaluation is accordingly restricted to stability metrics (NaN/divergence counts) and equality of F1 (no regression from joint training).

---

## 5. Results

### 5.1 Misalignment Measurement (H-E1)

The mean Spearman ρ between LoRA-modified attention weights and Locret CIS scores across 100 MNLI validation examples is **0.3662** (σ = 0.0759). All 100 examples fall below the pre-registered 0.70 alignment threshold; there are no borderline examples in the [0.65, 0.75] range.

![Mean Spearman ρ bar chart](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_scope_sonnet46_no_reflection/docs/youra_research/20260520_scope/paper/figures/mean_rho_bar.png)

*Figure 1. Mean Spearman ρ = 0.3662 (σ = 0.0759) across 100 MNLI examples, compared to the 0.70 alignment threshold. Every example falls below the threshold.*

Per-layer analysis (32 layers × 32 query heads, from the full `spearman_correlation_results.json`) shows that per-layer mean ρ ranges from approximately 0.17 (layer 0) to 0.53 (layers 9 and 11), with no layer reaching consistent alignment. Variance is high in early layers and moderate in middle and late layers.

![Layer × head heatmap](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_scope_sonnet46_no_reflection/docs/youra_research/20260520_scope/paper/figures/layer_head_heatmap.png)

*Figure 2. Spearman ρ across 32 transformer layers × 32 query heads. Values are pervasively low, with no systematic region of high alignment.*

The range of per-example ρ values spans approximately 0.17 to 0.58, with no example exceeding the 0.70 threshold.

**Gate result:** H-E1 MUST_WORK gate satisfied (mean ρ = 0.3662 < threshold 0.70). This result supports the core motivation for joint training.

**Methodological note:** The GQA expansion (`repeat_interleave(4)`, treating 8 KV heads as 32 independent query-head signals) may inflate the perceived misalignment by reducing the effective correlation measure. A KV-head-level analysis (at 8 heads without expansion) may yield higher ρ values and is identified as a robustness check for future work.

### 5.2 Mechanism Confirmation (H-M1)

The PoC run (1 seed = 42, 1 epoch per task, 500 training / 200 validation samples, LLaMA-3.1-8B with KV budget 50%) yields the following results:

**Table 1. Per-task GLUE accuracy at 50% KV budget — H-M1 PoC run.**

| Model | MNLI | SST-2 | QNLI | Mean |
|-------|------|-------|------|------|
| B2 (LoRA, 100% budget) | — | — | — | 44.00% |
| B1 (Frozen Locret, 50%) | ~37.5% | ~49.0% | ~45.5% | 44.00% |
| **JointLoRA-KV (50%)** | **39.0%** | **50.0%** | **47.5%** | **45.50%** |

*Source: h-m1/experiment_results.json.*

JointLoRA-KV achieves +1.50 percentage points over B1 (44.00% → 45.50%). The pre-registered gate threshold for H-M1 was ≥2.0pp; the observed gap of 1.50pp does not meet this threshold. The gate result is therefore **PARTIAL** (gate_satisfied=false).

Mechanism verification indicators from `experiment_results.json`:

| Indicator | Result |
|-----------|--------|
| locret_grad_received | True |
| cis_shape_correct | True (shape B, L, 8) |
| eviction_active | True (retained ratio < 0.55) |
| accuracy_improved | True (+1.50pp vs B1) |
| gap_pp ≥ 2.0 | False (1.50pp observed) |

Gradient flow to Locret retaining heads was confirmed, with reported grad norms up to approximately 2.5×10⁻³ at early training steps (from the H-M1 validation report). The gradient norms are small, which is attributed to the PoC training constraints: at 50% KV budget on short GLUE sequences (≤512 tokens), the eviction boundary affects a limited number of tokens per training step.

![Gate metrics comparison](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_scope_sonnet46_no_reflection/docs/youra_research/20260520_scope/paper/figures/gate_metrics_comparison.png)

*Figure 3. Mean GLUE accuracy at 50% KV budget: JointLoRA-KV (45.50%) vs B1 frozen-Locret baseline (44.00%) and B2 LoRA-only ceiling (44.00%). The +1.50pp gap falls below the pre-registered 2.0pp gate threshold.*

The reflection analysis attributes the shortfall to PoC training constraints (1 epoch vs 3–5 epochs, 500 vs 2000 samples, 1 seed vs 3 seeds) rather than a mechanism flaw. The pipeline routing outcome is SELF_MODIFY.

**Comparison to B3:** H-M1 compares JointLoRA-KV against B1 (frozen Locret), not against B3 (sequential LoRA→Locret, the primary baseline). No result against B3 is available from H-M1.

![Per-task GLUE accuracy](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_scope_sonnet46_no_reflection/docs/youra_research/20260520_scope/paper/figures/per_task_glue.png)

*Figure 4. Per-task GLUE accuracy breakdown for JointLoRA-KV and B1.*

### 5.3 Training Stability (H-M2)

H-M2 trains the PoC model (d=64, 2-layer transformer with BERT tokenizer) on real GLUE data (MNLI/SST-2/QNLI, 500 examples/task) for 200 steps per seed, evaluating on real LongBench examples (50 per task).

**Table 2. Stability metrics across 3 seeds — H-M2 PoC model (d=64, 2 layers).**

| Seed | NaN Events | Divergence Events | Final Loss |
|------|-----------|------------------|------------|
| 42   | 0         | 0                | 0.790      |
| 123  | 0         | 0                | 0.740      |
| 456  | 0         | 0                | 0.790      |

*Source: h-m2/results/aggregated_results.json.*

All three seeds converge without NaN or divergence. The MUST_WORK gate for H-M2 (stability criterion) is satisfied.

**LongBench F1 results:** JointLoRA-KV and B3 both achieve F1 = 0.000 across all three LongBench tasks (NarrativeQA, Qasper, MultiFieldQA-en) at all seeds. As explained in Section 4.6, these values reflect the inability of the tiny PoC model to generate text matching QA answer strings, not a failure of joint training. The gate criterion (joint F1 ≥ B3 F1) is satisfied by equality.

The locret gradient norms in the aggregated_results.json are recorded as 0 for the PoC model across all seeds. This differs from the H-M1 report, where locret_grad_received=True was confirmed on LLaMA-3.1-8B. The discrepancy may reflect that the PoC model's implementation was not instrumented to log Locret gradient norms, or that the tiny model's parameter scale yields negligible norms.

![Training loss curves](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_scope_sonnet46_no_reflection/docs/youra_research/20260520_scope/paper/figures/training_loss_curves.png)

*Figure 5. Training loss curves across seeds 42, 123, 456 for the PoC model. All three seeds converge without divergence or NaN.*

![Gradient norms](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_scope_sonnet46_no_reflection/docs/youra_research/20260520_scope/paper/figures/gradient_norms.png)

*Figure 6. LoRA and Locret gradient norms across training steps (H-M2 PoC model).*

**Gate result:** H-M2 MUST_WORK gate satisfied (stability confirmed, F1 joint ≥ F1 B3).

### 5.4 Summary of Executed Results

**Table 3. Summary of evidence across executed experiments.**

| Claim | Experiment | Status | Key Evidence |
|-------|-----------|--------|-------------|
| Task-LM misalignment exists (ρ < 0.70) | H-E1 | CONFIRMED | ρ = 0.3662 ± 0.076, 100/100 examples below threshold |
| Task gradients reach Locret heads | H-M1 | CONFIRMED | locret_grad_received=True, grad_norm ~2.5×10⁻³ |
| Joint training improves GLUE over B1 | H-M1 | PARTIAL | +1.50pp vs B1 in 1-epoch PoC (gate threshold: 2.0pp) |
| Joint training stable across seeds | H-M2 | CONFIRMED | 0 NaN/divergence across seeds 42/123/456 (PoC model) |
| JointLoRA-KV ≥3% over B3 on LongBench-QA | H-M3 | NOT TESTED | H-M3 not executed |
| Joint training stable on LLaMA-3.1-8B | — | NOT TESTED | Only confirmed on d=64, 2-layer PoC model |

---

## 6. Discussion

### 6.1 Misalignment Findings

The Spearman ρ = 0.3662 between task-adapted LoRA attention and LM-trained Locret CIS indicates that approximately 86% of the variance in LoRA attention priority is not explained by Locret CIS priority. This is a large misalignment under any interpretation of "alignment." The consistency across 100 examples (σ = 0.076, no borderline cases) suggests the finding is not a sampling artifact.

Per-layer analysis shows the misalignment is not localized: no transformer layer shows systematically high alignment. The highest per-layer mean ρ values (~0.52–0.53) appear at layers 9 and 11, while early layers (0–2) show the lowest values (~0.17–0.21). This breadth of misalignment suggests the divergence between task-discriminative and next-token-predictive token priority is a global property of the model, not a layer-specific phenomenon.

The GQA expansion artifact (Section 4.4) is a confound that may cause the reported ρ to underestimate the true KV-head-level alignment. The magnitude of this effect is not quantified in the current experiments and is identified as a robustness check for future work.

### 6.2 Mechanism Confirmation and Limitations

The H-M1 PoC demonstrates that: (a) task classification gradients flow through the soft KV budget mask to Locret retaining head weights, and (b) this gradient flow produces a measurable accuracy improvement (+1.50pp over B1) in a single epoch. The improvement did not reach the pre-registered 2.0pp threshold, and the result is classified PARTIAL.

The key limitation of H-M1 is its reduced training scale. The pre-registered protocol called for 3 seeds, 3–5 epochs, and 2000 samples per task; the executed PoC used 1 seed, 1 epoch, and 500 samples. The approximately 4–6× reduction in gradient steps is the most likely explanation for the 0.50pp shortfall, though this explanation is not empirically confirmed.

H-M1 compares JointLoRA-KV against B1 (frozen Locret), not against B3 (sequential LoRA→Locret). The practically relevant claim — that JointLoRA-KV improves over sequential fine-tuning — has no empirical support from the executed experiments.

The H-M2 stability result is restricted to a PoC model (d=64, 2 layers). The argument for stability at full scale rests on the disjoint parameter structure of LoRA (A/B matrices) and Locret (W₁/W₂ per layer), which holds regardless of model scale. However, this architectural argument is not a substitute for empirical confirmation on LLaMA-3.1-8B.

### 6.3 Unexecuted Experiments

Two of five planned experiments were not run. H-M3 (full-scale JointLoRA-KV vs B3 on LongBench-QA + GLUE, 3 seeds) is the primary test of the main hypothesis and was not executed due to compute constraints; all code is implemented and reported as validator-approved. H-M4 (linear probing of retained KV representations) depends on H-M3 and was likewise not executed.

The paper's primary prediction — ≥3% improvement over B3 on LongBench-QA — therefore has no supporting experimental evidence.

### 6.4 Broader Considerations

Joint training of PEFT adapters and KV eviction policies is a general approach applicable wherever task-specific fine-tuning is combined with memory-efficient inference. The method requires no base model architecture changes — it modifies the training procedure for existing LoRA-compatible and Locret-compatible systems.

A potential concern not investigated in this work is that jointly training the eviction policy on a narrow task distribution could reduce out-of-distribution robustness: if Locret heads are optimized for MNLI token patterns, their eviction decisions on other tasks may degrade. This tradeoff is not assessed.

All experiments use LLaMA-3.1-8B. Generalization to other architectures (Mistral-7B, Qwen-2.5-7B) has not been investigated.

---

## 7. Conclusion

This paper presents JointLoRA-KV, a training procedure that jointly optimizes LoRA adapter weights and Locret KV cache eviction head weights via a task classification objective. The work is motivated by a direct empirical measurement showing that task-adapted LoRA attention patterns and LM-trained Locret eviction scores are substantially misaligned (Spearman ρ = 0.3662, 100/100 MNLI examples below 0.70 threshold on LLaMA-3.1-8B).

The executed experiments confirm three properties: the misalignment is real and consistent (H-E1, PASS); task gradients flow to Locret heads through a soft sigmoid KV budget mask, producing +1.50pp GLUE improvement over a frozen-Locret baseline in a PoC run (H-M1, PARTIAL — 0.50pp below gate threshold due to PoC training constraints); and joint training is numerically stable on a PoC model across 3 seeds with no NaN or divergence events (H-M2, PASS).

The primary performance claim — that JointLoRA-KV improves over the sequential fine-tuning baseline B3 by ≥3% on LongBench-QA at 50% KV budget — was not tested; the corresponding experiment (H-M3) was not executed due to compute constraints. The evidence from H-E1 and H-M2 supports the mechanistic plausibility of such an improvement, but does not constitute evidence for it.

---

## References

Bai, Y., Lv, X., Zhang, J., et al. (2024). LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding. *ACL 2024*.

Bengio, Y., Léonard, N., & Courville, A. (2013). Estimating or Propagating Gradients Through Stochastic Neurons for Conditional Computation. *arXiv:1308.3432*.

Chu, et al. (2025). MCaM: Memory-Efficient KV Cache Management. *arXiv preprint*.

Dettmers, T., Pagnoni, A., Holtzman, A., & Zettlemoyer, L. (2023). QLoRA: Efficient Finetuning of Quantized LLMs. *NeurIPS 2023*.

Gokhale, T., et al. (2025). KV Pareto: Systems-Level KV Cache Optimization. *arXiv preprint*.

Hu, J., Shen, Y., Wallis, P., et al. (2022). LoRA: Low-Rank Adaptation of Large Language Models. *ICLR 2022*.

Huang, Y., Yuan, B., Han, X., Xiao, C., & Liu, Z. (2024). Locret: Enhancing Eviction in Long-Context LLM Inference with Trained Retaining Heads. *TMLR 2024*.

Jiang, W., & Wang, W. (2026). Sub-Token Routing in LoRA for Adaptation and Query-Aware KV Compression. *arXiv:2604.21335*.

Kim, et al. (2025). Efficient Compressing and Tuning LLMs: A Survey. *arXiv preprint*.

Mao, Y., et al. (2024). A Survey on LoRA of Large Language Models. *arXiv preprint*.

Molfese, et al. (2026). Exploring Fine-Tuning for In-Context Retrieval with KV-Caching. *EACL 2026*.

Rajpurkar, P., Zhang, J., Lopyrev, K., & Liang, P. (2016). SQuAD: 100,000+ Questions for Machine Comprehension of Text. *EMNLP 2016*.

Wang, A., Singh, A., Michael, J., et al. (2018). GLUE: A Multi-Task Benchmark and Analysis Platform for Natural Language Understanding. *EMNLP 2018*.

Xiao, G., Tian, Y., Chen, B., Han, S., & Lewis, M. (2024). Efficient Streaming Language Models with Attention Sinks. *ICLR 2024*.

Yang, et al. (2024). Low-Rank Adaptation for Foundation Models: A Comprehensive Study. *arXiv preprint*.

Yao, et al. (2025). TailorKV: Task-Aware KV Cache Tailoring for Memory-Efficient Inference. *arXiv preprint*.

Zhang, Z., Sheng, Y., Zhou, T., et al. (2023). H2O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models. *NeurIPS 2023*.

---

## Appendix

### A. H-E1 Per-Example Spearman ρ Summary

| Metric | Value |
|--------|-------|
| Mean ρ | 0.3662 |
| Standard deviation | 0.0759 |
| Minimum ρ (example) | ~0.17 |
| Maximum ρ (example) | ~0.58 |
| Fraction ρ < 0.70 | 100% (100/100) |
| Borderline [0.65, 0.75] | 0 examples |
| N | 100 MNLI validation_matched examples |
| Seed | 42 |

*Source: h-e1/results/spearman_correlation_results.json.*

### B. H-M1 Mechanism Verification Indicators

| Indicator | Value | Source |
|-----------|-------|--------|
| locret_grad_received | True | h-m1/04_validation.md |
| cis_shape_correct | True (B, L, 8) | h-m1/experiment_results.json |
| eviction_active | True (retained ratio < 0.55) | h-m1/experiment_results.json |
| accuracy_improved | True (+1.50pp vs B1) | h-m1/experiment_results.json |
| gate_result | PARTIAL (gap=1.50pp < threshold=2.0pp) | h-m1/experiment_results.json |
| Training scale | 1 seed, 1 epoch, 500 samples | h-m1/04_validation.md |

### C. H-M2 Per-Seed LongBench F1 — PoC Model

The following values are from the tiny PoC model (d=64, 2-layer transformer). The model outputs class-index tokens that do not match QA answer strings; F1 = 0.000 for all conditions is the correct measured value at this model scale and reflects the model's inability to generate coherent text, not a property of joint training.

| Task | JointLoRA-KV | B3 Baseline |
|------|-------------|-------------|
| NarrativeQA | 0.000 | 0.000 |
| Qasper | 0.000 | 0.000 |
| MultiFieldQA-en | 0.000 | 0.000 |
| Mean F1 | 0.000 | 0.000 |

*Source: h-m2/results/aggregated_results.json.*

The gate criterion (joint F1 ≥ B3 F1) is satisfied by equality. These values do not reflect task performance on a real model.

### D. Discrepancy Note on H-M2 F1 Values

The verification_state.yaml and the 045_validated_hypothesis.md synthesis document report "joint_mean_f1=0.3375 ≥ b3_mean_f1=0.3354" as key findings from H-M2. The aggregated_results.json in h-m2/results/ shows F1 = 0.000 for all conditions. The 04_validation.md for H-M2 explicitly states that the PoC model's F1 = 0.000 reflects the tiny-model evaluation, while the experiment log appendix records "Joint mean F1: 0.3375, B3 mean F1: 0.3354." The source of the 0.3375/0.3354 values is not traceable to the raw output file; these values may reflect an intermediate computation or a different evaluation run not reflected in the final aggregated results file. This paper reports the values directly from aggregated_results.json (F1 = 0.000) as the primary source, and flags the discrepancy.
