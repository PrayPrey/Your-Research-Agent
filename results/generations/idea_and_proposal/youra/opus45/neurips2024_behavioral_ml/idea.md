# Title
Soft Differentiable Cognitive Constraint Layers: Integrating ACT-R Memory Equations into Transformers for Human-Aligned Learning

# Motivation
Machine learning systems trained on human data rarely model the cognitive processes generating that data. While cognitive architectures like ACT-R provide validated mathematical models of human memory and cognition, they remain symbolic and incompatible with gradient-based deep learning. This creates a gap: neural networks lack psychologically-grounded inductive biases, leading to inefficient learning and non-human-like behavior on cognitive tasks. Bridging this gap could improve both sample efficiency and behavioral alignment with humans.

# Main Idea
We propose Soft Differentiable Cognitive Constraint Layers (S-DCCLs)—PyTorch modules implementing soft approximations of ACT-R's memory equations. The core mechanism includes: (1) **activation-based retrieval** using exponential trace decay A(t+1) = λA(t) + (1-λ)access(t), creating recency-weighted memory, and (2) **capacity-limited working memory** with K slots and competitive softmax inhibition, forcing selective retention.

These constraints restrict the hypothesis space to cognitively plausible solutions, hypothesized to improve learning efficiency. We test on N-back working memory tasks, predicting S-DCCL-augmented transformers achieve ≥20% sample efficiency gains over matched-parameter baselines and produce error patterns correlated (r>0.5) with human behavioral data.

This work establishes the first framework translating cognitive architecture equations to differentiable modules, enabling end-to-end training while preserving psychological validity—with applications to intelligent tutoring, assistive AI, and cognitive assessment.