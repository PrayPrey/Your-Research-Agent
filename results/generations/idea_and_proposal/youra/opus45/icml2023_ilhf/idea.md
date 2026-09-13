# Research Idea

## Title
Homeostatic Interaction-Grounded Learning for Non-Stationary Implicit Human Feedback

## Motivation
Interactive learning systems increasingly rely on implicit human feedback (eye gaze, facial expressions, EEG signals) rather than explicit rewards. However, a critical gap exists: human preferences naturally evolve over time, yet current Interaction-Grounded Learning (IGL) methods assume stationary feedback-reward mappings. When preferences drift, the learned decoder becomes misaligned, causing catastrophic performance degradation. No principled framework exists for detecting and adapting to such non-stationarity while preserving previously learned knowledge.

## Main Idea
We propose Homeostatic IGL (H-IGL), integrating three mechanisms: (1) **Bayesian Online Change-Point Detection (BOCPD)** monitors the implicit feedback distribution to detect preference shifts with controlled false-positive rates (<5%); (2) **Homeostatic regulation** modulates decoder adaptation rates, balancing stability during stationary periods with plasticity during detected shifts; (3) **Elastic Weight Consolidation (EWC)** preserves knowledge of previous preference structures during re-grounding.

The causal mechanism operates as: implicit signals → probabilistic reward decoder → BOCPD drift detection → homeostatic-controlled adaptation → EWC-regularized update. We predict H-IGL recovers >80% baseline performance within 100 episodes post-drift, while standard IGL degrades below 50%. Validation uses synthetic drift injection on EEG/gaze feedback with ablation studies isolating each component's contribution. This enables robust deployment of implicit feedback systems in real-world settings where user preferences naturally evolve.