# 1. Introduction

Selecting 7.8% of training data for GRPO code generation yields a 4.24× gradient signal advantage over random selection — but that advantage is entirely invisible during training when the model never generates a single correct solution. This puzzle — a method that works analytically but fails empirically for a precise, diagnosable reason — is the story of this paper.

Reinforcement Learning from Execution Feedback (RLEF) has emerged as a powerful approach for improving code generation [Gehring et al., 2024]. In RLEF, a policy model receives binary execution rewards (pass/fail) and is updated via Group Relative Policy Optimization (GRPO). But binary rewards impose a fundamental inefficiency: when a model either solves every completion or fails every completion, the within-group reward standard deviation equals zero, producing zero gradient. At group size G=4, this zero-gradient pathology affects 69.25% of training groups [Gradient Starvation, 2025] — the vast majority of gradient steps are wasted.

The natural fix is data selection: train only on problems where the model occasionally succeeds. Several recent methods achieve this via *online* selection — computing difficulty signals during training and adjusting the data distribution as the model learns [VIGOR, 2025; Prompt Replay, 2025; Sun et al., 2025; LZE, 2025]. These methods work well but face a practical limitation: they require an active training loop, coupling selection overhead to training cost and preventing reuse of the selection across runs.

We propose *offline* variance-guided selection: profile a frozen model once on all candidate problems, compute per-problem binary execution reward variance p_i*(1−p_i), and select problems with the highest variance before training begins. This "profile once, train anywhere" design separates a cheap profiling phase (~32 seconds for 374 problems with vLLM) from the expensive GRPO training phase, enabling data selection to be reused across hyperparameter sweeps or model variants.

The gap this addresses is precise: no prior work has (1) characterized the per-problem binary execution reward variance distribution across MBPP for a code LLM, (2) compared offline variance-guided selection to random selection under binary RLEF, or (3) identified the cold-start precondition that determines whether any selection method can operate in this regime.

Our key insight, confirmed experimentally, is: **offline frozen-model variance profiling produces a statistically robust selection signal, but GRPO gradient concentration can only manifest this advantage when the model is already capable of generating some correct solutions**. Cold-start — the model generating zero correct solutions across all training conditions — renders data selection method irrelevant. When every problem yields k=0 correct completions in every group, σ=√(k(G−k))/G=0 regardless of which problems were selected.

This paper makes the following contributions:

1. **Variance distribution characterization** (new empirical finding): We provide the first published characterization of binary execution reward variance across MBPP training problems for DeepSeek-Coder-7B-Instruct under constrained generation. The distribution is severely right-skewed: 91.7% of problems yield p_i=0 (all-fail), 7.8% yield p_i=0.25 (1 of 4 completions pass), and 0.5% yield p_i=1.0. This distribution reveals that generation parameter constraints — not model capability per se — critically shape the effective training data pool.

2. **Offline variance profiling** (method, analytically validated): Top-50 selection by frozen-model variance achieves 4.24× higher mean variance than random-50 selection (Mann-Whitney U p=2.22e−06), with the variance-selected subset stochastically dominating random-50 on the full CDF. vLLM batch inference completes the 374-problem profiling in ~32 seconds.

3. **Cold-start diagnosis** (negative result, high confidence): We document 40,000+ GRPO generation attempts across 50–200 training steps under two selection conditions (variance-guided and random) — all producing zero reward. The cold-start failure is attributed to generation parameter mismatch between profiling (vLLM, max_new_tokens=128) and training (HF GRPOTrainer, max_completion_length=512), and we provide a concrete protocol for resolving it.

Taken together, these contributions advance the understanding of what is needed before offline data selection can operate in RLEF — identifying cold-start verification as a necessary precondition that prior work has not systematically studied.

We organize the remainder as follows: Section 2 reviews related work on RLEF efficiency and data selection. Section 3 describes our methodology. Section 4 presents experimental setup. Section 5 reports results. Section 6 discusses limitations and implications. Section 7 concludes.
