# Research Idea

## Title
Efficient Information-Theoretic Shapley Decomposition (E-ITSD) for Interpretable Multimodal Contribution Analysis

## Motivation
Understanding how different modalities contribute to multimodal representations remains a fundamental challenge. Current attribution methods (attention weights, gradients) cannot distinguish whether modalities provide unique information, share redundant content, or create emergent synergistic effects. This gap hinders diagnosing issues like modality collapse and understanding cross-modal interactions. We need principled metrics that decompose modality contributions into interpretable components.

## Main Idea
We propose E-ITSD, combining permutation-sampled Shapley values with Partial Information Decomposition (PID) to quantify each modality's unique contribution, shared redundancy, and emergent synergy. The method operates through three causal steps: (1) learned null embeddings create valid counterfactuals for modality ablation without distribution shift; (2) permutation sampling approximates Shapley values with axiomatic fairness guarantees; (3) I_broja PID decomposes these attributions into unique/redundant/synergistic components.

Key predictions: the decomposition satisfies mathematical validity (components sum to total contribution), synergy scores correlate with cross-modal attention in reasoning tasks, and unique contribution dominance detects modality collapse. We validate on MultiBench datasets (CMU-MOSEI, AV-MNIST) with 2-5 modalities, comparing against MM-SHAP and gradient-based methods. E-ITSD provides actionable diagnostics for multimodal model development and theoretical insights into modality interactions.