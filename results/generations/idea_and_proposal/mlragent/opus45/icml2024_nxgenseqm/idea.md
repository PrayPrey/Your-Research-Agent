# Title: Adaptive Memory Allocation in State Space Models via Learned Compression Gates

## Motivation
State space models (SSMs) like Mamba offer linear complexity for sequence modeling but use fixed-dimensional hidden states, creating a fundamental tension: small states forget important long-range information, while large states waste computation on irrelevant context. Unlike transformers with explicit KV caches, SSMs lack mechanisms to selectively preserve critical information over varying timescales. This limits their effectiveness on tasks requiring heterogeneous memory—some tokens need long-term retention (key facts, instructions) while others are transient (filler words, formatting).

## Main Idea
We propose **GatedSSM**, which augments state space models with learned compression gates that dynamically allocate memory capacity across the sequence. At each timestep, a lightweight gating network predicts: (1) a *retention score* determining how strongly current information should persist, and (2) a *compression ratio* controlling how much state capacity to allocate. High-retention tokens expand into dedicated "memory slots" within a structured state matrix, while low-importance tokens share compressed representations.

The architecture maintains SSM's recurrent efficiency while enabling variable-fidelity memory. We'll train gates end-to-end using a combination of next-token prediction and auxiliary losses encouraging sparse, interpretable memory usage.

**Expected outcomes**: Improved long-context recall on tasks like passkey retrieval and multi-hop reasoning, with minimal computational overhead. We'll provide scaling analysis comparing memory-performance tradeoffs against Mamba and transformer baselines, plus interpretability studies revealing what information models choose to preserve.