## Title
CLS-LoRA: Neuroscience-Inspired Dual-Adapter Architecture for Scalable Continual Learning in Foundation Models

## Motivation
Foundation models suffer from static training limitations—outdated knowledge, compute waste, and catastrophic forgetting during updates. Current continual learning methods for parameter-efficient fine-tuning (LoRA-based approaches) either use static dual-adapters without knowledge consolidation or employ simple subtraction mechanisms without importance weighting. Neither captures the brain's proven solution: Complementary Learning Systems (CLS), where the hippocampus rapidly encodes new experiences while the neocortex gradually consolidates stable knowledge. This biological template remains unexploited in LoRA-based continual learning.

## Main Idea
We propose CLS-LoRA, a dual-adapter architecture inspired by CLS theory. A "hippocampal" LoRA module with orthogonal initialization rapidly encodes task-specific knowledge, while a "neocortical" LoRA module stores consolidated knowledge through periodic second-order importance-weighted merging. The causal mechanism operates in four steps: orthogonal initialization prevents gradient interference → hippocampal module enables rapid encoding → importance-weighted consolidation selectively transfers critical parameters → drift-resistant subspaces protect consolidated knowledge.

We test on CIFAR-100 (10 tasks) with frozen ViT-B/16, targeting >88.5% accuracy and <5% forgetting versus ~86% and ~8-10% for CL-LoRA baselines. Ablations will isolate each mechanism component. Success would establish neuroscience-grounded principles for scalable lifelong foundation model learning while maintaining parameter efficiency (<2% of backbone).