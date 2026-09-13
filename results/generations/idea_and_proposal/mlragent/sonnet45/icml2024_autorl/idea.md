# Title
Self-Correcting RL: LLM-Guided Automated Failure Diagnosis and Hyperparameter Repair

# Motivation
Despite advances in AutoRL, practitioners still face a critical bottleneck: when RL training fails (e.g., reward collapse, instability), diagnosing *why* it failed and *what* to fix remains a manual, expertise-intensive process. Current AutoML approaches treat hyperparameter optimization as black-box search, ignoring rich diagnostic signals (loss curves, gradient norms, exploration metrics) that experts use to identify failure modes. This limits sample efficiency and interpretability of automated RL systems.

# Main Idea
We propose a framework combining LLMs with interpretable diagnostic rules to automatically detect, explain, and repair RL training failures:

1. **Failure Detection Module**: Monitor training metrics to identify common failure patterns (e.g., value overestimation, insufficient exploration, policy collapse) using lightweight statistical tests.

2. **LLM-Based Diagnosis**: Feed detected patterns and metric trajectories to an LLM fine-tuned on RL debugging literature and expert traces. The LLM generates natural language explanations and suggests targeted hyperparameter adjustments.

3. **Adaptive Repair**: Implement suggested fixes through a constrained modification policy, creating a feedback loop that learns from successful repairs.

**Expected Outcomes**: Reduced trial-and-error in RL deployment, interpretable AutoRL decisions, and a benchmark dataset of RL failure modes with expert annotations.

**Impact**: Makes RL more accessible to non-experts while providing actionable insights that advance our understanding of algorithm brittleness.