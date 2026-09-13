# Title: Meta-Prompting: Learning to Generate Optimal In-Context Examples via Reinforcement Learning

## Motivation
A critical challenge in in-context learning is the sensitivity of model performance to the selection and ordering of demonstration examples. Current approaches rely on heuristic methods (e.g., semantic similarity retrieval) or manual curation, which often yield suboptimal results and lack generalization across tasks. Understanding *what makes an effective in-context example* remains poorly understood, limiting ICL's reliability in safety-critical applications and domain transfer scenarios.

## Main Idea
We propose a meta-learning framework that trains a lightweight "prompt generator" network to synthesize optimal in-context demonstrations for any given query. Unlike retrieval-based methods, our approach generates demonstrations directly, enabling exploration beyond the training corpus.

**Methodology:**
1. Train a small transformer-based generator that takes a query and task description as input and outputs synthetic demonstration pairs (input-output examples)
2. Use reinforcement learning with the frozen LLM's task performance as the reward signal, optimizing for downstream accuracy
3. Incorporate diversity and informativeness constraints to prevent mode collapse

**Expected Outcomes:**
- Improved ICL performance, especially on out-of-distribution queries
- Interpretable insights into what constitutes effective demonstrations
- Reduced sensitivity to example ordering

**Impact:** This bridges ICL with meta-learning, providing a principled approach to prompt engineering while offering theoretical insights into the inductive biases that enable successful in-context skill acquisition.