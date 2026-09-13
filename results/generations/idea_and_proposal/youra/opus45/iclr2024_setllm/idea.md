# Research Idea

## Title
ARID: Adversarial Representation-level Immune Defense for Multi-Vector LLM Attacks via Contrastive Trajectory Detection

## Motivation
Large language models face increasingly sophisticated multi-vector attacks combining prompt injection, jailbreaking, and context manipulation. Current defenses rely on surface-level pattern matching or single-attack-type detection, failing against coordinated attacks that optimize to evade threshold-based detection. A critical gap exists: no unified defense mechanism captures the shared adversarial intent across diverse attack vectors at the representation level.

## Main Idea
We propose ARID, a defense mechanism based on the hypothesis that multi-vector attacks share detectable trajectory shifts in LLM hidden state representations toward adversarial objectives. The core innovation is **contrastive adversarial-intent projection**: using contrastive learning to map diverse attack representations into a shared adversarial-intent subspace, then monitoring the *direction* of representation shifts (trajectory) rather than absolute values.

ARID deploys lightweight probe classifiers at selective transformer layers (1, L/2, L) to detect adversarial trajectories with <5% inference overhead. We predict ARID achieves >80% true positive rate at 0.1% false positive rate on multi-vector attacks, exceeding single-vector defenses by >20 percentage points.

Validation uses AdvBench/JailbreakBench with Llama-3 models, testing against JudgeDeceiver-style optimization attacks. This immune-inspired approach offers a principled framework for unified LLM defense against evolving attack combinations.