# Research Idea

## Title
CLAM: Closed-Loop Active Learning for Multi-Objective mRNA Therapeutic Optimization

## Motivation
Current mRNA therapeutic design relies on one-shot optimization methods that generate sequences without iterative experimental feedback, limiting their ability to navigate the complex trade-offs between protein expression, mRNA stability, and immunogenicity. While RNA foundation models capture sequence features and Bayesian optimization enables sample-efficient search, no framework integrates these with closed-loop wet-lab feedback for mRNA therapeutics. This gap results in suboptimal sequences and wasted experimental resources.

## Main Idea
We propose CLAM, a framework combining Bayesian optimization with adapter-fine-tuned RNA foundation model embeddings for iterative mRNA optimization. The core mechanism operates through four causal steps: (1) LoRA-adapted RNA-FM embeddings encode therapeutically relevant sequence features, (2) Gaussian Process surrogates model the sequence-to-function landscape in this embedding space, (3) multi-objective acquisition functions (q-EHVI) select Pareto-optimal candidates balancing expression/stability/immunogenicity, and (4) ribosome profiling feedback refines the GP posterior each round.

We will validate CLAM against one-shot baselines (Helix-mRNA, RiboDecode) over 20-30 optimization rounds with 8-12 sequences per batch. Success criteria: ≥2x expression improvement with monotonic convergence (Spearman ρ>0.7). Falsification occurs if improvement ≤1.2x or no convergence trend emerges. This approach could reduce experimental costs by 50-70% while achieving superior therapeutic efficacy.