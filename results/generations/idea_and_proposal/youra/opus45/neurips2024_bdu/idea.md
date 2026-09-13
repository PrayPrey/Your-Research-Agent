# Research Idea

## Title
Predictive Prior Networks: LLM-Conditioned Foundation Model Surrogates for High-Dimensional Bayesian Optimization

## Motivation
Bayesian optimization struggles in moderate-to-high dimensional settings (50-500 dimensions) due to poor surrogate model scaling and uninformative priors. While recent foundation model surrogates like TabPFN show promise, they lack mechanisms to incorporate domain knowledge. Separately, LLMs contain rich semantic priors about optimization landscapes but cannot directly guide acquisition. This gap limits sample efficiency in critical applications like drug discovery and neural architecture search where evaluations are expensive.

## Main Idea
We propose Predictive Prior Networks (PPN), which condition foundation model surrogates on LLM-extracted semantic priors through attention-based integration. The core mechanism operates in three steps: (1) LLMs process problem descriptions via standardized prompts to generate structured prior embeddings encoding constraints, promising regions, and domain heuristics; (2) cross-attention layers integrate these embeddings with TabPFN's context encoding; (3) adaptive weighting balances prior exploitation versus data-driven exploration, preventing prior-data conflict.

We hypothesize this hierarchical integration improves sample efficiency by ≥20% (measured by simple regret) compared to unconditioned baselines. Key predictions include early-iteration advantages (t<50) where gradient estimates are noisy, and robustness to misleading priors through adaptive downweighting. Experiments span synthetic benchmarks (Hartmann, Rosenbrock) and real-world problems (MOPTA08, Rover) across 50-500 dimensions, with falsification criteria ensuring rigorous validation.