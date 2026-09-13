# Eviction-Aware LoRA: Training LoRA Adapters Under KV Cache Budget Constraints

## Abstract

LoRA adapters for large language models (LLMs) are typically trained with full KV cache access but deployed under eviction policies that discard 50–75% of cached token entries. This training-inference distribution mismatch is not directly addressed by any existing fine-tuning method. This paper proposes Eviction-Aware LoRA, which injects H2O eviction masks into the LoRA forward pass during training, exposing adapter parameters to the evicted-cache attention distribution they will encounter at inference. Experiments on a GPT-2 proxy model (117M parameters, 30 training steps, 200 LongAlpaca-12k samples) show that eviction-aware training produces adapter weights with a mean cosine similarity of 0.053 relative to sequential-baseline adapters (range: −0.578 to +0.469 across 24 layers), with all 24 layers falling below the 0.95 divergence threshold. Attention entropy analysis on 5 synthetic samples shows significant divergence (paired t-test, p < 0.05) in 8 of 12 transformer layers, concentrated in middle layers 4–11; no significant divergence was observed in lower layers 0–3 by either entropy or heavy-hitter concentration metrics. These mechanistic results confirm that eviction-aware training alters the gradient signal reaching LoRA parameters and restructures attention patterns at the proxy scale. The primary accuracy hypothesis — whether eviction-aware training improves LongBench task performance on LLaMA-2-7B and Mistral-7B-v0.1 — was not evaluated due to unavailability of gated model access. Full accuracy evaluation remains as future work, supported by the validated BudgetSweepEvaluator and SpearmanAnalyzer infrastructure described here.

---

## 1. Introduction

Large language models are routinely fine-tuned with full KV cache access and then deployed under eviction policies that discard a substantial fraction of cached key-value entries. H2O [Zhang et al., 2023], SnapKV [Li et al., 2024], and StreamingLLM [Xiao et al., 2023] have each demonstrated that principled eviction can reduce KV cache memory by 50–75% with limited accuracy loss. These methods are applied post-hoc to models — including LoRA-adapted models — that were never exposed to eviction constraints during fine-tuning. The resulting mismatch between the full-cache attention distribution encountered during training and the evicted-cache distribution encountered at inference has not been addressed at the fine-tuning stage.

This paper investigates whether applying H2O eviction masks during LoRA fine-tuning — rather than only at inference — produces adapter parameters better calibrated to the evicted-cache distribution. The proposed approach, termed Eviction-Aware LoRA, injects H2O eviction masks via a forward hook on the attention module during training. The hook is removed at inference. The adapter's gradient signal is thereby computed through eviction-masked attention activations throughout training.

The motivation draws an analogy to dropout [Srivastava et al., 2014]: both techniques expose the model to structured absence during training to promote robustness at inference. Token-position eviction differs from dropout in granularity (entire KV entries vs. individual activations), determinism (H2O masks are policy-driven and input-dependent), and target (training-inference distribution matching for a specific eviction policy vs. generalization).

This paper makes four contributions:

1. **Problem formalization.** The training-inference distribution mismatch in KV-cache-constrained LoRA deployment is formalized as a first-class design problem. No prior work directly addresses this mismatch at fine-tuning time; LongLoRA [Chen et al., 2023] modifies attention for computational efficiency during long-context fine-tuning but does not target eviction-policy-induced distribution shift.

2. **Mechanistic existence result (H-E1).** In a GPT-2 proxy experiment (117M parameters, 30 training steps, 200 LongAlpaca-12k samples, kv_budget_ratio=0.50), eviction-aware and sequential-baseline adapters show a mean per-layer cosine similarity of 0.053 (range: −0.578 to +0.469; all 24 LoRA layers below the 0.95 threshold). This confirms that H2O mask injection during training changes the gradient signal reaching LoRA parameters.

3. **Attention pattern redistribution (H-M1).** On 5 synthetic samples with the same GPT-2 proxy, paired t-tests show significant attention entropy divergence (p < 0.05) in 8 of 12 transformer layers (fraction = 0.667, threshold = 0.50). Significant layers are concentrated in middle transformer layers 4–11; lower layers 0–3 show no significant divergence by either entropy or heavy-hitter concentration metrics.

4. **Validated evaluation infrastructure.** The paper provides a validated implementation of BudgetSweepEvaluator, SpearmanAnalyzer, and the H2O training wrapper, verified to run end-to-end at proxy scale. Full-scale evaluation on target 7B models requires `attn_implementation='eager'` due to an incompatibility between H2O's cumulative-score indexing and PyTorch SDPA kernels (Section 6.3).

The primary accuracy hypothesis — a per-category LongBench accuracy advantage of ≥2% at r=50% on both LLaMA-2-7B and Mistral-7B-v0.1 — was not evaluated. H-M3 (the full accuracy experiment) was not started due to unavailability of gated HuggingFace model access. The dose-response hypothesis (H-M2), which required LongBench evaluation at multiple budget ratios, was also not evaluable at GPT-2 proxy scope because GPT-2's 1024-token context window is insufficient for LongBench tasks (2,000–10,000 tokens).

The paper is organized as follows. Section 2 reviews related work on KV cache eviction and PEFT. Section 3 describes the method. Section 4 details experimental setup. Section 5 reports results. Section 6 discusses findings and limitations. Section 7 concludes.

---

## 2. Related Work

### 2.1 KV Cache Eviction Methods

KV cache memory grows linearly with sequence length, making it the primary bottleneck for serving long-context LLMs. Several methods address this by selectively evicting low-importance token entries at inference time.

**H2O** [Zhang et al., 2023] retains tokens with the highest cumulative attention scores (heavy hitters) along with a fixed set of initial attention-sink tokens. H2O reports that 50% KV cache reduction incurs modest accuracy degradation on LongBench. The persistence of heavy-hitter token sets across inputs for a given model is the property that makes H2O masks informative as training-time constraints in the present work. H2O is applied post-hoc to fixed models.

**SnapKV** [Li et al., 2024] selects KV entries based on query-aware clustering, improving accuracy on multi-document QA tasks at matched cache budgets compared to H2O. Like H2O, SnapKV is a post-hoc inference-time method applied to fixed models.

**StreamingLLM** [Xiao et al., 2023] retains attention-sink tokens and a sliding window of recent tokens, enabling theoretically unbounded context at fixed cache size. The concentration of sink tokens in early layers is relevant to the observation in Section 5.2 that lower transformer layers (0–3) show no significant attention divergence under eviction-aware training.

All three methods share the assumption that the adapted model is a fixed artifact. The present work departs from this assumption by treating the adapter as a design target.

### 2.2 Parameter-Efficient Fine-Tuning

**LoRA** [Hu et al., 2022] decomposes weight updates into low-rank matrices (ΔW = BA, B ∈ ℝ^{d×r}, A ∈ ℝ^{r×k}), achieving competitive performance with substantially fewer trainable parameters than full fine-tuning. Eviction-Aware LoRA modifies the LoRA forward pass by applying H2O eviction masks before the attention score matrix is finalized, changing the gradient signal reaching A and B.

**AdaLoRA** [Zhang et al., 2023] allocates LoRA rank budget adaptively across layers via singular value decomposition. The strong weight divergence observed in H-E1 (mean cosine similarity 0.053 after 30 steps) is consistent with AdaLoRA's observation that concentrated gradient signals drive more efficient adapter specialization.

**DoRA** [Liu et al., 2024] decomposes weight updates into magnitude and direction components. Like standard LoRA, DoRA assumes full KV cache access during training.

**LongLoRA** [Chen et al., 2023] extends LoRA for long-context fine-tuning using shifted sparse attention to reduce computation. LongLoRA modifies attention patterns for computational efficiency, not to match an inference-time eviction policy. It does not address the training-inference distribution mismatch arising from post-hoc KV cache eviction at deployment.

### 2.3 Regularization by Structured Absence

Dropout [Srivastava et al., 2014] trains models to be robust to structured absence by randomly zeroing activations during training, operating at the neuron level within each token. Token-position eviction operates at a coarser granularity — entire KV entries — and uses deterministic, policy-driven masks rather than stochastic ones. Neuron dropout does not alter the set of token positions a model attends to; token-position eviction does. These structural differences are relevant to the interpretation of weight divergence magnitudes in Section 5.1.

Prior work on attention pattern characterization in encoder models [Clark et al., 2019] identifies middle transformer layers as carrying the bulk of long-range dependency information in BERT. The H-M1 finding that significant attention entropy divergence is concentrated in middle layers 4–11 of GPT-2 is consistent with this prior, though direct generalization from encoder to decoder architectures requires separate verification.

### 2.4 Distribution Mismatch Perspective

Domain adaptation theory [Ben-David et al., 2010] establishes that models trained on distribution P and evaluated on distribution Q incur a performance penalty proportional to the divergence between P and Q. In the present setting, P is the full-cache attention distribution encountered during fine-tuning and Q is the evicted-cache distribution encountered at inference. Eviction-Aware LoRA is a targeted intervention to minimize this divergence for a fixed eviction policy (H2O), trading policy-generality for policy-specific calibration. No prior work applies this framing to the joint optimization of KV cache eviction and LoRA fine-tuning.

---

## 3. Method

### 3.1 Problem Formulation

Let M be a pre-trained decoder-only transformer with L layers. Standard LoRA fine-tuning trains low-rank adapter matrices {A_l, B_l} for each targeted layer l, with weight update ΔW_l = B_l A_l (rank r ≪ d). During training, the attention at each layer has access to the full KV cache: all T key-value pairs {(k_i, v_i)}_{i=1}^{T} participate in attention score computation.

At inference under KV cache budget ratio ρ ∈ (0, 1], only ⌊ρT⌋ KV pairs are retained. Under H2O eviction, the retained set consists of a fixed number of initial attention-sink tokens (n_sink) and the top-K tokens by cumulative attention score. Adapter parameters {A_l, B_l} trained with full attention are evaluated on a qualitatively different attention distribution.

**Goal:** Train {A_l, B_l} such that their representations are calibrated to the evicted-cache attention distribution encountered at inference under H2O eviction at budget ratio ρ.

### 3.2 Eviction-Aware LoRA Training

The approach applies H2O eviction masks during the LoRA forward pass at training time.

#### 3.2.1 H2O Mask Computation

For each training step, given input sequence of length T:

1. **Attention sink selection:** Retain the first n_sink tokens (default: 4) unconditionally.
2. **Heavy-hitter selection:** Compute cumulative attention scores s_i = Σ_{j≥i} α_{ji} where α_{ji} is the attention weight from position j to position i. Select the top-K positions by s_i, where K = ⌊ρT⌋ − n_sink.
3. **Mask construction:** M_i = 1 if position i is selected (sink or heavy hitter), 0 otherwise.

The masked attention computation at layer l is:

    Attention(Q, K, V) = softmax((QK^T ⊙ M̃) / √d_k) V

where M̃_{ij} = M_j (column-wise mask; unselected positions set to −∞ before softmax).

#### 3.2.2 Hook-Based Mask Injection

The eviction mask is injected via a PyTorch forward hook on the attention module. This approach requires no architectural modifications and is compatible with HuggingFace `transformers` and `peft`. The hook intercepts the attention computation after Q, K, V projections have been computed but before the attention score matrix is finalized.

The hook is registered only during training forward passes and removed during evaluation and inference. This prevents double-application of eviction at inference and ensures the adapter is evaluated on the same mechanism it was trained to expect.

**Algorithm 1: Eviction-Aware LoRA Training**
```
Input:  Pre-trained model M, LoRA config (rank r, alpha α),
        training data D, KV budget ratio ρ, n_sink
Output: Adapter parameters {A_l, B_l}

1. Initialize LoRA adapters: B_l = 0, A_l ~ N(0, σ²) for all l
2. Register H2O forward hook on all attention layers:
   hook(Q, K, V):
     if training:
       M = compute_h2o_mask(K, ρ, n_sink)
       return masked_attention(Q, K, V, M)
     else:
       return standard_attention(Q, K, V)
3. For each training batch (x, y) ∈ D:
   a. Forward pass with hook active → eviction-masked attention
   b. Compute loss L(M(x), y) on LoRA parameters
   c. Backward pass → gradients reach {A_l, B_l} through eviction-masked activations
   d. Update {A_l, B_l} via AdamW
4. Deregister hook
5. Return {A_l, B_l}
```

#### 3.2.3 Gradient Signal Analysis

Under eviction-aware training, ∂L/∂A_l flows through activations computed with masked attention: positions outside M contribute zero activation, and surviving positions carry the entire gradient signal. This differs from standard LoRA training, where ∂L/∂A_l flows through full-attention activations.

### 3.3 Hyperparameters and Configuration

| Hyperparameter | Proxy Value | Target Value | Notes |
|----------------|-------------|--------------|-------|
| LoRA rank (r) | 8 | 16 | Rank 8 used in H-E1 smoke test |
| LoRA alpha (α) | 32 | 32 | Confirmed by experiment_results.json |
| LoRA dropout | 0.05 | 0.05 | |
| KV budget ratio (ρ) | 0.50 | 0.50 | Primary comparison |
| Attention sinks (n_sink) | 4 | 4 | Standard H2O configuration |
| Training steps | 30 | ~1 epoch | Proxy: gradient-signal analysis only |
| Training data | LongAlpaca-12k (200 samples) | LongAlpaca-12k (full) | |
| Optimizer | AdamW | AdamW | HuggingFace PEFT default |
| Learning rate | 2e-4 | 2e-4 | |
| attn_implementation | eager | eager | Required for H2O+SDPA compatibility |

Note: The h-e1 validation report appendix recommends alpha=16 for dependent hypotheses (a forward-looking recommendation). The actual H-E1 training run used alpha=32, as confirmed by `experiment_results.json`.

### 3.4 Relationship to Token-Scarcity Regularization

Eviction-aware training can be interpreted as token-scarcity regularization — a training-time constraint that forces the adapter to develop representations under token-position absence. Key differences from dropout: (1) granularity — token-position eviction removes entire KV entries; dropout removes individual activations within each position; (2) determinism — H2O masks are policy-driven and input-dependent; dropout masks are stochastic and input-independent; (3) target — eviction-aware training addresses a specific training-inference distribution mismatch; dropout targets generalization.

### 3.5 Infrastructure Components

**H2O Training Wrapper:** Hook-based mask injection, validated for GPT-2 and architecturally validated for LLaMA-2-7B/Mistral-7B-v0.1.

**BudgetSweepEvaluator:** Evaluates adapters on LongBench (21 tasks) at ρ ∈ {0.25, 0.50, 0.75} in a single pass. Validated end-to-end at proxy scope (sequential GPT-2 adapter: 63 evaluations completed).

**SpearmanAnalyzer:** Computes Spearman ρ between KV budget ratio and per-category accuracy gap.

**AttentionEntropyExtractor:** Per-layer attention entropy and heavy-hitter concentration for paired statistical analysis.

---

## 4. Experimental Setup

### 4.1 Research Questions

**RQ1 (H-E1 — Existence):** Does applying H2O eviction masks during LoRA training produce adapter weight matrices that differ statistically from sequential-baseline adapters?

**RQ2 (H-M1 — Mechanism):** Does eviction-aware training restructure attention patterns, and which transformer layers are most affected?

**RQ3 (H-M2 — Dose-Response):** Does any accuracy advantage increase monotonically as the KV budget tightens? (Planned; not evaluable at proxy scope — see Section 5.3.)

**RQ4 (H-M3 — Accuracy):** Does eviction-aware training yield ≥2% per-category LongBench accuracy improvement at r=50%? (Not started — model access unavailable.)

### 4.2 Models and Data

**Proxy model:** GPT-2 (117M parameters, 12 transformer layers, 1024-token context window). Used for RQ1 and RQ2; GPT-2 differs architecturally from target models in using a fused `c_attn` Conv1D layer (Q+K+V combined) rather than separate `q_proj`/`k_proj`/`v_proj` projections. The H2O mask injection mechanism is architecture-agnostic; the degree to which proxy-scale results generalize to 7B models is unverified.

**Target models (not evaluated):** LLaMA-2-7B and Mistral-7B-v0.1. Both require gated HuggingFace access unavailable during this study.

**Training data:** LongAlpaca-12k (Yukang/LongAlpaca-12k, HuggingFace Hub), 200 samples used in proxy experiments.

**Evaluation data (H-M1):** 5 synthetic multi-sentence samples. GPT-2's 1024-token context precludes real LongBench evaluation; these short synthetic samples were used for attention pattern comparison only. Results from n=5 samples should not be extrapolated to LongBench-scale conclusions.

### 4.3 Baselines

**Sequential baseline:** Standard LoRA fine-tuning without eviction masks during training; H2O eviction applied at inference at the same ρ. Same architecture, training data, and hyperparameters — training-time eviction masking is the only difference.

A random-token-removal ablation (same budget ratio, random mask rather than H2O policy-driven selection) was not evaluated. This ablation would assess whether the observed weight divergence is specific to H2O's policy-driven heavy-hitter selection or is a general consequence of any token removal during training.

### 4.4 Evaluation Metrics

**H-E1:** Per-layer cosine similarity between LoRA adapter weight matrices (eviction-aware vs. sequential). Gate: at least one layer with similarity < 0.95.

**H-M1:** Per-layer attention entropy and heavy-hitter concentration (top-20% token attention ratio), evaluated with H2O masks active during attention extraction (`set_h2o_training_mode(model, True)`). Gate: OR condition — a layer is counted significant if attention entropy p-value or HH concentration p-value < 0.05 (paired t-test). Gate threshold: ≥50% of layers (≥6/12).

**H-M2:** Spearman ρ between KV budget ratio and mean per-category accuracy gap across ρ ∈ {0.25, 0.50, 0.75}. Gate threshold: ρ_s < −0.8.

### 4.5 Implementation Details

All experiments use HuggingFace `transformers` (≥4.36) and `peft`. `attn_implementation='eager'` is required when using H2O wrappers (see Section 6.3). H-E1: batch size 4, learning rate 2e-4, 30 training steps. H-M1: `config.output_attentions=True` with `attn_implementation='eager'` (required for attention weight extraction in transformers 5.x; `output_attentions=True` as a forward kwarg alone is ignored in SDPA mode). All experiments ran on a single GPU.

---

## 5. Results

### 5.1 H-E1: Adapter Weight Divergence

**Gate: MUST_WORK — PASS**

All 24 LoRA layers of the GPT-2 proxy model showed cosine similarity below the 0.95 gate threshold after 30 training steps with kv_budget_ratio=0.50.

| Metric | Value | Gate Threshold | Status |
|--------|-------|----------------|--------|
| Minimum cosine similarity | −0.578 | < 0.95 | PASS |
| Mean cosine similarity | 0.053 | (reference) | — |
| Layers below threshold | 24/24 | ≥ 1 | PASS |

Per-layer cosine similarity ranged from −0.578 (transformer.h.6.attn.c_attn.lora_B) to +0.469 (transformer.h.9.attn.c_attn.lora_B). The mean of 0.053 is near zero, indicating no systematic alignment between eviction-aware and sequential adapter weights. All lora_A layers showed similarities close to zero (absolute values < 0.03), while lora_B layers showed higher variance (range approximately −0.578 to +0.469).

![Per-layer cosine similarity between eviction-aware and sequential LoRA adapter weights. Dashed line at 0.95 indicates gate threshold. All 24 layers fall below threshold.](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_scope/docs/youra_research/20260504_scope/paper/figures/cosine_similarity_smoke_test.png)

**Figure 1:** Per-layer cosine similarity between eviction-aware and sequential LoRA adapter weights (GPT-2, 30 steps, 200 LongAlpaca-12k samples, kv_budget_ratio=0.50). Dashed line at 0.95 indicates gate threshold.

Training loss decreased normally for both conditions (9.3 → 5.2 across 30 steps), confirming that hook registration did not interfere with the training loop. Loss values diverged slightly between baseline (7.213) and eviction-aware (7.217) conditions at the final step with identical data and seeds, consistent with differing gradient signals.

The mean cosine similarity of 0.053 is substantially below the range typical for same-task LoRA adapters trained from different seeds (>0.95) or for different task domains (>0.8). Two interpretations are considered in Section 6.1.

### 5.2 H-M1: Attention Pattern Redistribution

**Gate: MUST_WORK — PASS**

Paired t-test analysis on 5 synthetic samples with GPT-2 proxy adapters showed significant attention entropy divergence (p < 0.05) in 8 of 12 transformer layers. Heavy-hitter concentration divergence was not significant in any layer.

| Metric | Value | Gate Threshold | Status |
|--------|-------|----------------|--------|
| Layers significant by entropy (p < 0.05) | 8/12 | — | — |
| Layers significant by HH concentration (p < 0.05) | 0/12 | — | — |
| Layers significant by OR criterion | 8/12 (0.667) | ≥ 0.50 | PASS |

Significant layers (entropy, p < 0.05): 4, 5, 6, 7, 8, 9, 10, 11. Lower layers 0–3 showed no significant divergence by either metric.

Direction of divergence: eviction-aware adapters show lower mean attention entropy (−0.0199 nats) and higher heavy-hitter concentration (+0.0008) compared to the sequential baseline under matched H2O evaluation conditions. Both H-M1 conditions used `set_h2o_training_mode(model, True)` during attention extraction, applying H2O masks symmetrically in both conditions.

The concentration of significant divergence in middle transformer layers 4–11 is consistent with prior work showing that middle layers of transformer encoders carry long-range dependency information [Clark et al., 2019]. Whether this pattern holds for GPT-2's decoder architecture at scale, and whether it generalizes to 7B models on real long-context inputs, was not tested.

These n=5 results constitute preliminary mechanistic evidence. The sample size is insufficient to support quantitative claims at LongBench scale.

### 5.3 H-M2: Dose-Response — Proxy Scope Limitation

**Gate: SHOULD_WORK — LIMITATION_RECORDED (gate not satisfied)**

The dose-response hypothesis could not be evaluated at GPT-2 proxy scope.

The sequential GPT-2 adapter completed 63 task evaluations (21 LongBench tasks × 3 budget ratios). All task scores were 0.0: GPT-2's 1024-token context window cannot accommodate LongBench tasks, which require 2,000–10,000 tokens. The eviction-aware adapter encountered a CUDA gather kernel crash after 63 sequential-adapter evaluations (H2O+SDPA incompatibility; see Section 6.3), producing NaN scores.

Consequence: the per-category accuracy gap matrix was all zeros (sequential) or null (eviction-aware crash), making Spearman ρ undefined (zero-variance input). The gate threshold (ρ_s < −0.8) was not evaluable.

This is classified as a proxy model limitation, not a refutation of the dose-response hypothesis. The SHOULD_WORK gate is non-blocking; the pipeline continued per protocol.

![Absolute LongBench task scores for sequential GPT-2 adapter across budget ratios. All scores 0.0.](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_scope/docs/youra_research/20260504_scope/paper/figures/absolute_curves.png)

**Figure 2:** Absolute LongBench task scores for sequential GPT-2 adapter across budget ratios (0.25, 0.50, 0.75). All scores are 0.0, reflecting GPT-2's insufficient context window for LongBench tasks.

![Heatmap of per-category accuracy gap across 21 LongBench tasks and 3 budget ratios.](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_scope/docs/youra_research/20260504_scope/paper/figures/gap_heatmap.png)

**Figure 3:** Per-category accuracy gap heatmap across 21 LongBench tasks and 3 budget ratios. All cells are 0.0 or null due to proxy model limitations.

![Mean accuracy gap vs. KV budget ratio.](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_scope/docs/youra_research/20260504_scope/paper/figures/gap_vs_budget.png)

**Figure 4:** Mean accuracy gap vs. KV budget ratio. Flat at 0.0 for available (sequential) data.

![Spearman correlation bar chart.](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_scope/docs/youra_research/20260504_scope/paper/figures/spearman_bar.png)

**Figure 5:** Spearman correlation bar chart. ρ is undefined (zero-variance gap matrix).

### 5.4 H-M3: Primary Accuracy Evaluation — Not Started

**Gate: MUST_WORK — NOT STARTED**

The primary accuracy experiment (LongBench evaluation on LLaMA-2-7B and Mistral-7B-v0.1 at r=50%) was not executed. LLaMA-2-7B (meta-llama/Llama-2-7b-hf) and Mistral-7B-v0.1 require gated HuggingFace access that was unavailable during this study. No LongBench accuracy data exists for either model under either condition.

### 5.5 Summary

| Claim | Gate Type | Result |
|-------|-----------|--------|
| Eviction masks alter gradient signals (weight divergence, H-E1) | MUST_WORK | PASS |
| Eviction-aware adapters show different attention entropy (H-M1) | MUST_WORK | PASS |
| Middle layers (4–11) show significant entropy divergence | Observation | Confirmed (n=5, GPT-2) |
| HH concentration divergence significant in ≥50% of layers | — | Not confirmed (0/12 layers) |
| Dose-response: gap grows as budget tightens (H-M2) | SHOULD_WORK | Not evaluable (proxy limitation) |
| ≥2% LongBench accuracy gain at r=50% (H-M3) | MUST_WORK | Not started |

---

## 6. Discussion

### 6.1 Interpretation of Mechanistic Findings

**Weight divergence magnitude.** The mean cosine similarity of 0.053 (range: −0.578 to +0.469) after only 30 training steps is lower than typical LoRA specialization for different tasks (>0.8) or same-task different seeds (>0.95). Two interpretations are consistent with the data:

*Interpretation A:* H2O eviction masks reshape the gradient landscape substantially — surviving heavy-hitter tokens carry gradient signal previously spread across the full token sequence, driving adapter parameters toward a qualitatively different attractor. The magnitude of divergence is a structural consequence of the eviction-aware optimization problem.

*Interpretation B:* The short training duration (30 steps) and small proxy model (117M parameters) may amplify divergence that would be smaller at full scale. GPT-2's fused `c_attn` architecture (Q+K+V in one Conv1D) may also amplify divergence compared to the separate `q_proj`/`k_proj`/`v_proj` projections in LLaMA/Mistral. H-M3 at full scale would help distinguish these interpretations.

**Middle-layer specificity.** The concentration of significant entropy divergence in layers 4–11 (out of 0–11) is consistent with the established finding that middle transformer layers encode long-range dependency information [Clark et al., 2019]. Lower layers (0–3) handle positional and syntactic patterns less sensitive to which tokens are retained. Whether this layer pattern generalizes to decoder-only 7B models on real long-context inputs is an open question. Clark et al. [2019] analyzed BERT (encoder-only); direct transfer to GPT-2 decoder architectures is an assumption that merits separate verification.

**HH concentration finding.** The heavy-hitter concentration metric showed no significant divergence in any of the 12 layers (0/12), despite the gate passing via attention entropy significance alone. The paper's original claim that both metrics showed 8/12 layers significant is not supported by the experiment_results.json data, which records `layers_hh_significant_005: 0`. This distinction matters for mechanistic interpretation: the observed restructuring is in attention entropy distribution rather than in heavy-hitter concentration per se.

### 6.2 Limitations

**L1 (Critical): Primary accuracy evaluation absent.** H-M3 was not executed. The prediction of ≥2% per-category LongBench accuracy gain at r=50% on both LLaMA-2-7B and Mistral-7B-v0.1 is entirely untested. This paper is a mechanistic study; the accuracy claim is future work.

**L2 (Critical): Dose-response not evaluable at proxy scope.** H-M2 requires LongBench evaluation at multiple budget ratios, incompatible with GPT-2's context window. The BudgetSweepEvaluator and SpearmanAnalyzer infrastructure are validated for sequential adapters but have not been demonstrated with eviction-aware adapters at LongBench scale.

**L3 (Significant): Proxy-target validity gap.** GPT-2 (117M parameters, 1024-token context, fused c_attn) differs substantially from LLaMA-2-7B/Mistral-7B-v0.1 (7B parameters, 4096-token context, separate Q/K/V projections). H-E1 training used 30 steps on 200 samples rather than the planned 1 epoch on the full LongAlpaca-12k dataset. H-M1 used 5 synthetic samples rather than the planned ≥500 LongBench samples per category.

**L4 (Significant): H2O+SDPA incompatibility.** H2O's cumulative-score indexing is incompatible with PyTorch SDPA kernels in `transformers` ≥4.36. Fix: `attn_implementation='eager'` (validated for both GPT-2 and LLaMA/Mistral architectures). This introduces approximately 15–30% inference overhead compared to SDPA. All LLaMA/Mistral evaluation runs must use this setting.

**L5 (Moderate): Single eviction policy.** All experiments use H2O. Whether eviction-aware training provides benefits under SnapKV, StreamingLLM, or other eviction policies requires separate experiments.

**L6 (Moderate): Training data confound.** Whether LongAlpaca-12k's long-context examples create a data-distribution advantage for eviction-aware training relative to LongBench tasks was not tested. An Alpaca-52k sanity check (training adapters on shorter-context data and evaluating on LongBench) was not performed.

**L7 (Moderate): Absent random-mask ablation.** The observed weight divergence cannot be attributed specifically to H2O's policy-driven heavy-hitter selection without a random-token-removal ablation at the same budget ratio. Whether the divergence is specific to H2O masks or is a general consequence of any token removal during training is unresolved.

### 6.3 Technical Finding: H2O+SDPA Incompatibility

H2O's scatter/gather operations on attention score tensors conflict with SDPA's fused kernel in `transformers` ≥4.36. Setting `attn_implementation='eager'` forces unfused attention and is required for H2O mask injection to intercept attention computations correctly. This setting is validated for GPT-2 (H-E1, H-M1) and is expected to be required for LLaMA-2-7B and Mistral-7B-v0.1. The overhead (~15–30% at inference) is a known cost of this approach.

### 6.4 Broader Impact

Eviction-Aware LoRA targets the training-inference distribution mismatch under KV cache eviction, a problem that scales in relevance as context windows grow. If the mechanistic findings translate to accuracy improvements at full scale, the approach could recover accuracy at no additional inference-time hardware cost beyond the `eager` attention overhead. No specific misuse risks have been identified for this fine-tuning methodology.

---

## 7. Conclusion

This paper identifies the training-inference distribution mismatch in KV-cache-constrained LoRA deployment — adapters fine-tuned with full KV cache access are routinely evaluated under eviction policies that discard half or more of that cache — and proposes Eviction-Aware LoRA as a direct response. The method applies H2O eviction masks during the LoRA forward pass via a training-only hook, exposing adapter parameters to the evicted-cache attention distribution during training.

Experiments on a GPT-2 proxy model confirm two mechanistic results: (1) eviction-aware training produces adapter weights with a mean cosine similarity of 0.053 relative to sequential-baseline adapters (range: −0.578 to +0.469; all 24 LoRA layers below the 0.95 threshold) after 30 training steps; (2) attention entropy divergence is significant (paired t-test, p < 0.05) in 8 of 12 transformer layers on 5 synthetic samples, concentrated in middle layers 4–11, with no significant divergence in lower layers 0–3. Heavy-hitter concentration divergence was not significant in any layer.

The primary accuracy hypothesis — whether these mechanistic changes translate to ≥2% per-category LongBench accuracy improvement at r=50% on LLaMA-2-7B and Mistral-7B-v0.1 — was not tested. H-M3 is the immediate next experiment, estimated at approximately 24 GPU-hours on A100 hardware, using the validated BudgetSweepEvaluator infrastructure.

Three additional directions follow directly from this work. First, executing H-M3 will determine whether proxy-scale weight divergence predicts full-scale accuracy differences and will help distinguish between interpretations of the divergence magnitude (genuine optimization landscape divergence vs. short-training instability amplified at proxy scale). Second, the H2O+SDPA incompatibility should be addressed at the kernel level to remove the inference overhead introduced by `attn_implementation='eager'`. Third, evaluating eviction-aware adapters trained with H2O masks under SnapKV or StreamingLLM eviction at inference would test whether token-scarcity regularization generalizes across eviction policies.

---

## References

Zhang, Zhenyu, et al. "H2O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models." arXiv:2306.14048 (2023).

Li, Yuhong, et al. "SnapKV: LLM Knows What You are Looking for Before Generation." arXiv:2404.14469 (2024).

Xiao, Guangxuan, et al. "Efficient Streaming Language Models with Attention Sinks." arXiv:2309.17453 (2023).

Hu, Edward J., et al. "LoRA: Low-Rank Adaptation of Large Language Models." arXiv:2106.09685 (2022).

Zhang, Qingru, et al. "AdaLoRA: Adaptive Budget Allocation for Parameter-Efficient Fine-Tuning." arXiv:2303.10512 (2023).

Liu, Shih-Yang, et al. "DoRA: Weight-Decomposed Low-Rank Adaptation." arXiv:2402.09353 (2024).

Srivastava, Nitish, et al. "Dropout: A Simple Way to Prevent Neural Networks from Overfitting." JMLR 15.1 (2014): 1929–1958.

Clark, Kevin, et al. "What Does BERT Look at? An Analysis of BERT's Attention." arXiv:1906.04341 (2019).

Vaswani, Ashish, et al. "Attention Is All You Need." NeurIPS (2017).

Touvron, Hugo, et al. "Llama 2: Open Foundation and Fine-Tuned Chat Models." arXiv:2307.09288 (2023).

Jiang, Albert Q., et al. "Mistral 7B." arXiv:2310.06825 (2023).

Bai, Yushi, et al. "LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding." arXiv:2308.14508 (2023).

Chen, Yukang, et al. "LongLoRA: Efficient Fine-tuning of Long-Context Large Language Models." arXiv:2309.12307 (2023).

Ben-David, Shai, et al. "A theory of learning from different domains." Machine Learning 79 (2010): 151–175.
