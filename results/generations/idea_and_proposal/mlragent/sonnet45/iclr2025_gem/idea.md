# Title
**Active Learning with Uncertainty-Aware Generative Models for Efficient Protein Fitness Landscape Exploration**

# Motivation
Current generative ML models for protein design often produce vast libraries of candidates, but experimental validation remains a bottleneck due to cost and time constraints. Moreover, most models lack calibrated uncertainty estimates, making it difficult to prioritize which designs to test. This creates a critical gap between computational generation and experimental validation, limiting the real-world impact of ML-driven protein engineering.

# Main Idea
We propose an active learning framework that integrates uncertainty-quantified generative models with adaptive experimental design to efficiently navigate protein fitness landscapes. The approach combines:

1. **Uncertainty-aware generators**: Develop ensemble-based or Bayesian generative models (e.g., diffusion models, VAEs) that provide calibrated confidence scores for generated protein sequences.

2. **Acquisition functions**: Design novel acquisition strategies that balance exploration (high-uncertainty regions) and exploitation (high-predicted-fitness regions), specifically tailored for expensive wet-lab experiments.

3. **Iterative refinement**: After each experimental round, retrain the model on accumulated data, progressively improving both generation quality and uncertainty calibration.

**Expected outcomes**: Demonstrate 3-5x reduction in experimental iterations needed to identify high-fitness variants compared to random or greedy sampling. Validate on enzyme engineering or antibody optimization tasks with actual wet-lab results.

**Impact**: Enable resource-limited labs to leverage generative ML effectively, accelerating the translation of computational designs to real-world therapeutic and industrial applications.