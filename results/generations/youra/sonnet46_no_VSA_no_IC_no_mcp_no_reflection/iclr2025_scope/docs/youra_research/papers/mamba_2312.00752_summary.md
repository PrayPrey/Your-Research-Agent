# Paper Summary: Mamba — Linear-Time Sequence Modeling with Selective State Spaces
**arXiv:** 2312.00752 | **Authors:** Albert Gu, Tri Dao | **Year:** 2023

---

## Abstract
Mamba introduces Selective State Space Models (S6) with input-dependent A/B/C parameters and a hardware-aware parallel scan. Achieves O(n) training and O(1) inference memory — competitive with transformers on language modeling at 1.4B parameters.

## Architecture
- **SSM core:** A (state transition), B (input projection), C (output projection), Δ (discretization/timescale)
- **Selective mechanism:** A, B, C are functions of input x (not fixed), enabling context-aware state updates
- **in_proj, out_proj, x_proj, dt_proj:** All `nn.Linear` layers — directly wrappable by LoRA
- **A_log, B, C:** `nn.Parameter` tensors updated via CUDA selective-scan kernel — NOT `nn.Linear`
- **Key constraint:** Perturbing A destabilizes recurrent dynamics; A_log is constrained to negative values (stable decay)

## Methodology
- Discretization: Δ = softplus(dt_proj(x)); A_bar = exp(Δ·A); B_bar = Δ·B
- Hardware-aware: fused CUDA kernel for parallel scan avoids materializing full state sequence
- Block: LayerNorm → SSM (with gating via SiLU) → output projection

## Experiments & Results
- Language modeling: Mamba-1.4B matches GPT-3 (1.3B) on zero-shot tasks (LAMBADA, HellaSwag, PIQA, etc.)
- Inference: 5× faster than transformer at 2K sequence length; constant memory vs. KV-cache growth
- Long-context: Strong performance up to 1M tokens in synthetic tasks

## Relevance to State-Aware PEFT
- **LoRA-applicable layers:** in_proj (d_model→2·d_inner), out_proj (d_inner→d_model), x_proj (d_inner→dt_rank+2·d_state), dt_proj (dt_rank→d_inner)
- **State-aware target:** A_log (scalar log-scale state decay per channel) — perturbing this with a learned offset Δ_A could modulate forgetting rate; B, C (input/output state coupling) could be IA³-scaled
- **Risk:** A is initialized negative (stable); adding unconstrained LoRA to A_log could push eigenvalues positive → divergence. Solution: bound perturbation or use multiplicative IA³ scaling on B/C instead
