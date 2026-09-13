# Title
**Adaptive Curriculum Learning for Self-Improving Foundation Models via Difficulty-Aware Synthetic Data Generation**

## Motivation
Self-improvement through synthetic data risks model collapse when models repeatedly train on their own overconfident or erroneous outputs. A critical yet underexplored challenge is determining *what* synthetic data to generate and *when* to use it. Current approaches either generate data uniformly or rely on static difficulty metrics, failing to adapt to the model's evolving capabilities. We need principled methods to dynamically calibrate synthetic data difficulty to maximize learning signal while avoiding collapse.

## Main Idea
I propose a curriculum learning framework where the model continuously assesses its capability boundaries and generates synthetic data at the "edge of competence"—neither too easy (redundant) nor too hard (misleading). 

**Methodology:**
1. **Capability Mapping**: Maintain a learned uncertainty estimator that identifies problem regions where the model shows high variance/disagreement across samples
2. **Adaptive Data Generation**: Prioritize synthetic data generation in uncertain regions, using temperature-scaled sampling and constrained decoding to control difficulty
3. **Quality Gating**: Employ ensemble-based verification with confidence thresholds, only incorporating data where verifiers show high agreement
4. **Curriculum Scheduling**: Gradually shift generation towards harder problems as uncertainty decreases

**Expected Outcomes**: More sample-efficient self-improvement with provable bounds on distribution drift, demonstrated on mathematical reasoning and code generation tasks where verification is tractable.