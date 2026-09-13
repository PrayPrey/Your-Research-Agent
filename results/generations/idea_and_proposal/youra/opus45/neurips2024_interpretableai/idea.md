# Research Idea

## Title
Concept-Aligned Sparse Autoencoders via Self-Generated Contrastive Learning for Interpretable LLM Features

## Motivation
Sparse Autoencoders (SAEs) have emerged as powerful tools for extracting interpretable features from large language models, but current approaches rely on post-hoc labeling to assign meaning to discovered features—a process that may produce unfaithful explanations. While vision models benefit from external grounding (e.g., object detectors), LLMs lack equivalent semantic anchors. This gap limits the reliability of SAE-based interpretability in high-stakes applications. We address whether training-time concept alignment can produce genuinely grounded features without external supervision.

## Main Idea
We propose CA-SAE-V (Concept-Aligned SAE with Verification), a two-stage training approach where: (1) standard SAE pretraining discovers meaningful feature directions, then (2) contrastive fine-tuning aligns features with LLM self-generated descriptions using InfoNCE loss. The key insight is that language itself provides semantic grounding—by having the LLM describe activation patterns from top-activating examples, then pulling feature representations toward these descriptions, we embed concept structure directly into feature geometry.

We validate through: (a) Number of Effective Concepts (NEC) metric measuring grounding quality, (b) activation patching verification confirming >70% of features produce description-consistent behavior when intervened. Expected outcomes include 5%+ improvement in concept grounding over standard SAEs while maintaining reconstruction quality (<20% degradation). This bridges classical interpretable ML's faithfulness guarantees with modern foundation model scale.