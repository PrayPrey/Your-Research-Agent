## Title
Hierarchical Multi-Timescale Architecture for Depth-Scalable Theory of Mind Reasoning

## Motivation
Large language models struggle with higher-order Theory of Mind (ToM) reasoning, showing 10-15% accuracy decline per additional belief depth level (e.g., "Alice thinks Bob believes Carol knows..."). This steep degradation limits AI systems' ability to model complex social cognition. Current approaches like SimToM and flat transformers lack architectural mechanisms matching the recursive structure of nested beliefs, treating all reasoning uniformly regardless of depth complexity.

## Main Idea
We propose HMT-ToM, a hierarchical multi-timescale architecture that separates meta-belief reasoning (slow module) from belief-state computation (fast module). A Linguistic Depth Detector identifies belief-introducing verbs ("thinks," "believes") to trigger timescale transitions, enabling explicit tracking of nested belief structures. The slow module maintains a belief stack representation, providing filtered context to the fast module for computing concrete beliefs at each depth level.

**Core hypothesis:** This architectural inductive bias, matching ToM's recursive structure, will reduce depth-scaling degradation by ≥50% compared to flat transformers. We evaluate on HI-TOM benchmark (1st-4th order beliefs), measuring accuracy decline slopes across depth levels. Ablation studies will verify the causal mechanism by removing individual components. Success would demonstrate that cognitively-inspired architectural constraints can address fundamental limitations in AI social reasoning with parameter-efficient (~27M) models.