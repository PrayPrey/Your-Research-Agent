# Research Idea

## Title
Adaptive Skill Primitives via Multi-Modal Foundation Models for Zero-Shot Task Generalization in Unstructured Environments

## Motivation
Current robot learning systems struggle with generalizing to novel tasks in unstructured environments like homes, requiring extensive retraining or fine-tuning for each new scenario. While large multi-modal models excel at understanding diverse contexts, translating this understanding into robust physical actions remains challenging. The gap between semantic task comprehension and reliable motor execution is a key bottleneck preventing robots from achieving human-level adaptability in everyday activities like cooking or tidying.

## Main Idea
We propose a hierarchical framework that decomposes robot control into **learnable skill primitives** guided by vision-language foundation models. The architecture consists of: (1) a frozen multi-modal backbone (e.g., GPT-4V or Gemini) that parses task instructions and visual scenes into structured subtask decompositions, (2) a **primitive library** of pre-trained, composable motor skills (grasp, pour, wipe, place) learned via sim-to-real transfer, and (3) a lightweight **adapter network** that maps semantic representations to primitive parameters (e.g., grasp pose, force profile) conditioned on real-time perception.

The key innovation is training the adapter on diverse simulated tasks with automatic curriculum generation, enabling zero-shot composition of primitives for unseen instructions. We evaluate on a standardized household task suite spanning 50+ activities. Expected outcomes include 3x improvement in novel task success rates compared to end-to-end policies, with practical impact on deployable home assistance robots.