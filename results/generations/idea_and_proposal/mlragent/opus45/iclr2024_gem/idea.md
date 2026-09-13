# Title: Adaptive Experimental Design with Uncertainty-Aware Generative Models for Protein Engineering

## Motivation
Current generative models for protein design often operate in isolation from experimental feedback, proposing thousands of candidates that are impractical to validate in wet labs. This disconnect wastes experimental resources and misses opportunities for iterative improvement. High-throughput screening remains expensive and time-consuming, making it critical to intelligently select which generated candidates to synthesize and test. Existing approaches lack principled mechanisms to quantify model uncertainty and strategically guide experimental efforts toward the most informative designs.

## Main Idea
We propose an active learning framework that tightly couples uncertainty-aware generative models with adaptive experimental design. The approach integrates:

1. **Calibrated uncertainty estimation**: Augment protein generative models (e.g., diffusion or flow-based) with ensemble methods or evidential learning to produce well-calibrated confidence scores for generated sequences.

2. **Acquisition function optimization**: Develop acquisition strategies balancing exploitation (high predicted fitness) with exploration (high uncertainty regions), specifically designed for batch selection compatible with experimental throughput constraints.

3. **Closed-loop integration**: Design a protocol where experimental results from each batch update both the generative model and a surrogate fitness predictor, progressively refining the design space.

We will validate this framework on enzyme engineering tasks, demonstrating improved sample efficiency (fewer experimental rounds to reach target activity) compared to random selection or one-shot generation. This approach directly addresses the ML-experiment gap by making generative models experimentally actionable.