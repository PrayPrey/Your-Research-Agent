# 3. Methodology

Building on the observation that task-adapted LoRA attention patterns and LM-trained Locret eviction scores are substantially misaligned (Spearman ρ ≈ 0.37), we design JointLoRA-KV to eliminate this misalignment at its source: the training objective. Rather than training the eviction policy independently on language modeling loss, we train both the LoRA adapter and the Locret retaining heads simultaneously via the same task classification loss.

## 3.1 Overview

**JointLoRA-KV** augments a pre-trained transformer (LLaMA-3.1-8B) with two sets of trainable parameters:

1. **LoRA adapters** [Hu et al., 2022]: Low-rank matrices A∈ℝ^{d×r}, B∈ℝ^{r×d} (rank r=16, α=32) injected into Q, K, V projections of each attention layer. These adapt the model's representations toward the downstream task.

2. **Locret retaining heads** [Huang et al., 2024]: Two-layer MLPs (W₁, W₂ per transformer layer) that compute a Contextual Importance Score (CIS) for each token at each layer. These scores determine which KV entries survive the eviction budget.

Both parameter sets are optimized jointly in a single backward pass through task classification cross-entropy loss. All other model parameters (base LLM weights) remain frozen.

## 3.2 Differentiable KV Budget Mask

The key challenge for joint training is that hard KV eviction — selecting the top-k tokens by CIS score — is non-differentiable. Gradients cannot flow backward through a discrete argmax operation to update the Locret head parameters.

We address this with a **soft KV budget mask** during training:

$$M_{\text{soft}}(c) = \sigma\left(\frac{c - \theta}{\tau}\right)$$

where c ∈ ℝ^L is the vector of CIS scores for all L tokens in the sequence, θ is an adaptive threshold (computed as the k-th largest CIS value for budget ratio b), τ = 0.1 is the temperature controlling mask sharpness, and σ(·) is the sigmoid function.

During training, the soft mask M_soft replaces hard top-k selection, allowing gradients to flow continuously from the task loss through the masked KV representations to the Locret head weights W₁, W₂.

**Rationale for temperature τ=0.1:** Lower temperature sharpens the sigmoid toward a step function, approximating hard eviction more closely during training. We validated τ=0.1 empirically as providing stable gradient flow (grad_norm 1e-3 to 1e-4) without loss of differentiability.

## 3.3 Straight-Through Estimator at Inference

At inference time, we restore hard top-k eviction for memory efficiency:

$$M_{\text{hard}}(c) = \mathbf{1}[c_i \geq c_{(b \cdot L)}]$$

The training-inference discrepancy is bridged by a **Straight-Through Estimator (STE)** [Bengio et al., 2013]: during the backward pass in training, gradients are computed as if M_hard were used (using the gradient of M_soft at the threshold boundary). This standard technique for discrete relaxations ensures the model learns eviction decisions aligned with the hard boundary it will face at inference.

## 3.4 Joint Training Procedure

### Parameter Groups and Learning Rates

LoRA and Locret parameters have different convergence dynamics — LoRA adapters operate over broad representation spaces while Locret heads make sharp binary-adjacent decisions. We use separate learning rate groups:

| Parameter Set | Learning Rate | Weight Decay |
|---------------|--------------|--------------|
| LoRA (A, B matrices) | 1×10⁻⁴ | 0.01 |
| Locret (W₁, W₂ heads) | 5×10⁻⁴ | 0.01 |

The 5× higher Locret learning rate compensates for the weaker gradient signal reaching the retaining heads through the soft mask (especially at short sequences where the eviction boundary affects fewer tokens).

### Training Objective

$$\mathcal{L} = \mathcal{L}_{\text{CE}}(f_{\text{LoRA+Locret}}(x; M_{\text{soft}}), y)$$

where f_LoRA+Locret(·) is the full forward pass with LoRA-adapted projections and soft-masked KV cache, and y is the task classification label. The KV budget ratio is fixed at b = 0.50 (50% retention) during both training and inference.

### Implementation Details

- **Base model:** meta-llama/Meta-Llama-3.1-8B-Instruct
- **Locret checkpoint:** hyx21/Locret-llama-3.1-8B-instruct (warm initialization of retaining heads)
- **Attention implementation:** eager (required for hook-based Q/K/V projection capture)
- **Hook design:** Forward pre-hooks on q_proj/k_proj/v_proj layers capture projections before each attention block; CIS = sigmoid([Q;K;V] @ W₁ᵀ) @ W₂ᵀ → (B, L, 8) for 8 GQA KV heads
- **Gradient accumulation:** 8 steps (effective batch size 32, 4 per device)
- **Gradient clipping:** global norm 1.0
- **LR schedule:** cosine decay with 6% linear warmup

## 3.5 Why This Design Solves the Misalignment

Each design choice directly addresses a component of the measured misalignment:

| Problem | Design Choice | Why |
|---------|--------------|-----|
| Locret trained on LM loss, not task loss | Single backward pass via task CE loss | Locret heads now optimize for task-discriminative token retention |
| Hard eviction non-differentiable | Soft sigmoid mask (τ=0.1) | Enables gradient flow through eviction boundary to Locret parameters |
| Training/inference gap | Straight-through estimator | Aligns soft training mask with hard inference eviction |
| Different convergence rates (LoRA vs Locret) | Dual LR groups (1e-4 / 5e-4) | Prevents the slower-converging component from blocking the faster one |
| Gradient interference risk | Disjoint parameter sets | LoRA A/B matrices and Locret W₁/W₂ heads have independent gradient paths |

The disjoint parameter sets are particularly important: LoRA injects into the Q/K/V projection weights (additive low-rank matrices), while Locret retaining heads are separate MLP modules applied to the hidden states after the attention computation. They do not share parameters and do not share gradient paths through the computation graph, enabling stable joint optimization as confirmed in our stability experiments (Section 5.3).

## 3.6 Baselines

We compare JointLoRA-KV against three baselines that represent the spectrum of existing approaches:

- **B1 (Frozen Locret):** LoRA-fine-tuned model with Locret retaining heads fixed at their LM-pretrained values. No task-gradient signal reaches the eviction heads. This isolates the effect of joint training.
- **B2 (LoRA only, no eviction):** LoRA-fine-tuned model at 100% KV budget — the accuracy ceiling without compression overhead.
- **B3 (Sequential LoRA→Locret):** Standard practice. LoRA adapters are trained first; then Locret heads are fine-tuned on the LoRA-adapted model. LoRA weights are frozen during Locret training. Full-scale comparison vs B3 is the subject of H-M3 (pending).
