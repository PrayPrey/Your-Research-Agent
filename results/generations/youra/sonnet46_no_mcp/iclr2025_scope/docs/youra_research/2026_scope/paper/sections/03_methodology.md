# 3. Methodology

## 3.1 Problem Formulation

Let M be a pre-trained decoder-only transformer LLM with L transformer layers. Standard LoRA fine-tuning trains low-rank adapter matrices {A_l, B_l} for each targeted layer l, with the weight update ΔW_l = B_l A_l (rank r ≪ d). During training, the attention at each layer has access to the full KV cache of length T: all T key-value pairs {(k_i, v_i)}_{i=1}^{T} participate in attention score computation.

At inference under KV cache budget ratio ρ ∈ (0, 1], only ⌊ρT⌋ KV pairs are retained. Under H2O eviction, the retained set consists of a fixed number of initial tokens (attention sinks) plus the top-K tokens by cumulative attention score (heavy hitters). The adapter parameters {A_l, B_l} trained with full attention are now evaluated on a qualitatively different attention distribution — the training-inference mismatch.

**Goal:** Train adapter parameters {A_l, B_l} such that their representations are calibrated to the evicted-cache attention distribution encountered at inference under H2O eviction at budget ratio ρ.

## 3.2 Eviction-Aware LoRA Training

Our approach applies H2O eviction masks directly during the LoRA forward pass at training time, exposing the adapter's gradient signal to the evicted-cache token distribution.

### 3.2.1 H2O Mask Computation

For each training step, given input sequence of length T with KV pairs {(k_i, v_i)}_{i=1}^{T}, we compute the H2O eviction mask M ∈ {0,1}^T as follows:

1. **Attention sink selection:** Retain the first n_sink tokens (default: 4) unconditionally, as attention sinks [Xiao et al., 2023].
2. **Heavy-hitter selection:** Compute cumulative attention scores s_i = Σ_{j≥i} α_{ji} where α_{ji} is the attention weight from position j to position i. Select the top-K positions by s_i, where K = ⌊ρT⌋ - n_sink.
3. **Mask construction:** M_i = 1 if position i is selected (sink or heavy hitter), 0 otherwise.

The masked attention computation at layer l becomes:

    Attention(Q, K, V) = softmax((QK^T ⊙ M̃) / √d_k) V

where M̃_{ij} = M_j (apply column-wise mask; set unselected positions to -∞ before softmax).

### 3.2.2 Hook-Based Mask Injection

Rather than modifying the transformer architecture, we inject the eviction mask via a forward hook on the attention module. This design choice is deliberate:

**Rationale:** Hook-based injection requires no architectural modifications and is compatible with any transformer implementation (including HuggingFace `transformers`) and any LoRA library (including HuggingFace `peft`). The hook intercepts the attention computation at the point where Q, K, V projections have been computed but before the attention score matrix is finalized.

**Training-only guard:** The hook is registered only during training forward passes and removed during evaluation/inference. At inference, H2O eviction is applied natively by the inference runtime. This prevents double-application and ensures the adapter is evaluated on the same eviction mechanism it was trained to expect.

**Algorithm 1: Eviction-Aware LoRA Training**
```
Input: Pre-trained model M, LoRA config (rank r, alpha α),
       training data D, KV budget ratio ρ, n_sink
Output: Eviction-aware adapter parameters {A_l, B_l}

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
   b. Compute loss L(M(x), y) with LoRA parameters
   c. Backward pass → gradients reach {A_l, B_l} through eviction-masked activations
   d. Update {A_l, B_l} via AdamW
4. Deregister hook
5. Return {A_l, B_l}
```

### 3.2.3 Gradient Signal Analysis

The key mechanism is that eviction masks change the gradient signal reaching LoRA parameters. In standard LoRA training, the gradient ∂L/∂A_l flows through the full-attention activations. Under eviction-aware training, ∂L/∂A_l flows through activations computed with masked attention — positions outside M contribute zero activation, and the surviving positions must compensate, driving the adapter toward representations that extract maximum information from heavy-hitter tokens.

This is the mechanism underlying our observation that eviction-aware and sequential adapters develop near-orthogonal weight matrices: the two optimization trajectories are shaped by fundamentally different gradient landscapes — full-attention gradients vs. eviction-masked gradients.

## 3.3 Hyperparameters and Configuration

The Eviction-Aware LoRA training configuration used in our experiments:

| Hyperparameter | Value | Rationale |
|----------------|-------|-----------|
| LoRA rank (r) | 8 (smoke test), 16 (target) | Standard PEFT configuration; rank 8 for proxy experiments |
| LoRA alpha (α) | 32 | Standard scaling factor (effective LR = α/r) |
| LoRA dropout | 0.05 | Light regularization on adapter |
| KV budget ratio (ρ) | 0.50 | Moderate compression (primary comparison point) |
| Attention sinks (n_sink) | 4 | Standard H2O configuration |
| Training steps | 30 (proxy), ~1 epoch (target) | Proxy: gradient-signal analysis; target: full fine-tuning |
| Training data | LongAlpaca-12k (200 samples for proxy) | Long-context instruction following |
| Optimizer | AdamW (default HuggingFace PEFT) | Standard |
| attn_implementation | 'eager' | Required for H2O+SDPA compatibility (see Section 6.3) |

**Target configuration for full-scale evaluation (H-M3):** rank=16, alpha=32, dropout=0.05, ρ=0.50, 1 epoch on full LongAlpaca-12k, applied to LLaMA-2-7B and Mistral-7B-v0.1.

## 3.4 Relationship to Token-Scarcity Regularization

We interpret eviction-aware training as a form of *token-scarcity regularization* — a training-time constraint that forces the adapter to develop representations robust to token-position absence. The analogy to dropout is structural: both introduce structured absence during training that the model must learn to handle. The key differences are:

1. **Granularity:** Token-position eviction removes entire KV entries (changing sequence structure); neuron dropout removes individual activations within a token (preserving sequence structure).
2. **Determinism:** H2O masks are deterministic given the input (policy-driven selection); dropout is stochastic.
3. **Target:** Our method targets the training-inference distribution mismatch for a specific deployment scenario; dropout targets generalization to unseen data.

These differences suggest that token-scarcity regularization is not simply a variant of dropout but a distinct training objective tailored to eviction-constrained deployment.

## 3.5 Infrastructure Components

We implement and validate three infrastructure components that support both the mechanistic experiments and the planned full-scale evaluation:

**H2O Training Wrapper:** Implements the hook-based mask injection described in Section 3.2.2. Validated for GPT-2 (117M) with `attn_implementation='eager'`; code architecture validated for LLaMA-2-7B and Mistral-7B-v0.1 layer structure.

**BudgetSweepEvaluator:** Evaluates a given adapter on LongBench (21 tasks) at multiple KV budget ratios (ρ ∈ {0.25, 0.50, 0.75}) in a single pass. Designed for both sequential and eviction-aware adapters.

**SpearmanAnalyzer:** Computes Spearman rank correlation between KV budget ratio ρ and per-category LongBench accuracy gap (eviction-aware minus sequential) to test the dose-response hypothesis (P2).

**AttentionEntropyExtractor:** Extracts per-layer attention entropy and heavy-hitter concentration (top-20% attention token score ratio) for paired statistical analysis between adapter conditions.
