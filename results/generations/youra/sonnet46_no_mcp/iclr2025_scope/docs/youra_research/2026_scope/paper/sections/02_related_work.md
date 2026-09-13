# 2. Related Work

Our work sits at the intersection of two mature but independently developed research threads: KV cache eviction for efficient LLM inference, and parameter-efficient fine-tuning (PEFT) for adapter-based model adaptation. We survey both threads and explain why their independence motivates our approach.

## 2.1 KV Cache Eviction Methods

The KV cache grows linearly with sequence length, making it the primary memory bottleneck for long-context LLM serving. A line of work addresses this by selectively evicting low-importance token entries at inference time.

**H2O** [Zhang et al., 2023] introduces the Heavy-Hitter Oracle, which identifies and retains tokens with high cumulative attention scores (heavy hitters). H2O demonstrates that 50% KV cache reduction incurs only modest accuracy degradation on LongBench, and that heavy-hitter token sets are persistent across inputs for a given model. We build directly on this observation — the persistence of heavy hitters is what makes H2O masks informative as a training-time constraint. However, H2O is applied post-hoc to pre-trained or separately fine-tuned models; it does not consider how the fine-tuning process itself could be made eviction-aware.

**SnapKV** [Li et al., 2024] improves over H2O by using query-aware clustering to select KV entries that are relevant to the specific query, rather than globally high-attention tokens. SnapKV achieves better accuracy on multi-document QA tasks on LongBench at matched KV budgets. Like H2O, SnapKV is a post-hoc inference-time intervention applied to fixed models. Our work is orthogonal: we do not propose a new eviction policy, but rather train adapters to be robust to a *fixed* eviction policy (H2O) applied at inference.

**StreamingLLM** [Xiao et al., 2023] retains attention sink tokens (initial tokens with disproportionately high attention) alongside a sliding window of recent tokens, enabling theoretically unbounded context at fixed cache size. The attention-sink phenomenon is related to our observation that lower transformer layers (0–3) are less affected by eviction-aware training — sink tokens concentrate in early layers, which may be more robust to eviction policy choice.

These methods collectively establish that principled token selection can dramatically reduce KV cache memory with acceptable accuracy loss. What they share — and what we depart from — is the assumption that the fine-tuned adapter is a fixed artifact, not a design target.

## 2.2 Parameter-Efficient Fine-Tuning

PEFT methods adapt large pre-trained models with a small number of trainable parameters, avoiding the memory cost of full fine-tuning.

**LoRA** [Hu et al., 2022] decomposes weight updates into low-rank matrices (W = W₀ + BA, B ∈ ℝ^{d×r}, A ∈ ℝ^{r×k}), achieving competitive performance with orders-of-magnitude fewer trainable parameters. LoRA is our base method; we extend it by modifying the forward pass to apply H2O eviction masks before the attention computation, changing the gradient signal reaching A and B.

**AdaLoRA** [Zhang et al., 2023] improves LoRA by allocating rank budget adaptively across layers using singular value decomposition, concentrating parameter budget where gradient signal is strongest. Our finding that eviction-aware training produces near-orthogonal weight divergence — stronger than typical task specialization — is consistent with AdaLoRA's observation that concentrated gradient signals drive more efficient adapter specialization. A natural extension (deferred to future work) is to use H2O eviction scores to guide AdaLoRA-style rank allocation.

**DoRA** [Liu et al., 2024] decomposes weight updates into magnitude and direction components, improving learning stability. Like standard LoRA, DoRA assumes full KV cache access during training and does not address the eviction distribution mismatch.

A key limitation shared across PEFT methods is their assumption that training and inference attention distributions match. Our work identifies this as a first-class design constraint and addresses it at training time.

## 2.3 Regularization by Structured Absence

The conceptual foundation of token-scarcity regularization is related to dropout [Srivastava et al., 2014], which trains neurons to be robust to co-adaptation by randomly zeroing activations during training. Dropout operates at the neuron level within each token; our approach operates at the token-position level, removing entire KV entries from the attention computation. This distinction is important: neuron dropout does not change the set of tokens a model attends to, while token-position eviction changes the sequence structure and positional dependencies encountered during training. The deterministic nature of H2O masks (policy-driven, not stochastic) further differentiates our approach from dropout variants.

The attention entropy analysis in our H-M1 experiment is informed by prior work on attention pattern characterization [Clark et al., 2019], which shows that middle transformer layers carry the bulk of long-range dependency information. Our finding that eviction-aware training most strongly restructures layers 4–11 (of 12) is consistent with this prior and provides mechanistic grounding for why eviction-aware training might particularly benefit long-context tasks.

## 2.4 Joint Optimization Perspective

Most related to our framing is the observation — implicit in the domain adaptation literature [Ben-David et al., 2010] — that models trained on a distribution P and evaluated on a different distribution Q suffer a performance penalty proportional to the divergence between P and Q. In our setting, P is the full-cache attention distribution encountered during fine-tuning, and Q is the evicted-cache distribution encountered at inference. Eviction-aware training is a targeted intervention to minimize this divergence for a specific eviction policy, trading policy-generality for policy-specific calibration. No prior work has applied this perspective to the joint optimization of KV cache eviction and LoRA fine-tuning.
