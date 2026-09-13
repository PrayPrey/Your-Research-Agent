# Research Idea

## Title
StyleToM: Dual-Adapter Personalization for Code Generation via Style Learning and Theory-of-Mind Intent Inference

## Motivation
Current code assistants generate generic suggestions that fail to match individual developer preferences, leading to low acceptance rates (~40%) and reduced productivity. While recent work has separately addressed coding style adaptation (MPCoder) and intent inference (TOM-SWE), no approach integrates both dimensions. Developers have heterogeneous needs spanning both *how* they write code (style) and *what* they intend to accomplish (intent)—orthogonal dimensions requiring unified personalization.

## Main Idea
We propose StyleToM, a dual-adapter architecture that combines LoRA-based style representation learning with retrieval-augmented theory-of-mind intent inference. The **Style Adapter** learns explicit syntax patterns (naming conventions, formatting) and implicit semantic patterns (design preferences) from 50-100 files of developer history using contrastive learning. The **ToM Module** maintains persistent memory of interaction history to infer current goals and constraints from natural language instructions. These components operate on orthogonal personalization dimensions: style captures *how* developers prefer code written, while ToM captures *what* they currently need.

We will validate through ablation studies (Style-only vs. ToM-only vs. Full) and a 30-developer user study measuring satisfaction improvement (>20% target) and code acceptance rate. Expected outcomes include demonstrating additive benefits of dual personalization and establishing a practical framework for developer-adaptive code assistants with <30% latency overhead.