# Title
**Adaptive Trigger Synthesis for Universal Backdoor Detection via Neuron Activation Divergence**

## Motivation
Existing backdoor defenses often fail against diverse, unseen attacks because they rely on attack-specific assumptions (e.g., trigger size, location, or pattern). A critical gap exists in developing detection methods that can generalize across multiple backdoor types without requiring prior knowledge of the attack strategy. Current neuron-based detection approaches analyze static activation patterns but miss the dynamic behavioral signatures that distinguish backdoored models from clean ones across various trigger designs.

## Main Idea
We propose a **trigger-agnostic detection framework** that synthesizes diverse candidate triggers through optimization while monitoring neuron activation divergence patterns. The key innovation is a two-stage approach:

1. **Divergence-Guided Trigger Generation**: Rather than reverse-engineering specific triggers, we optimize multiple diverse input perturbations that maximize divergence between suspicious model activations and expected clean model behavior, measured via layer-wise activation distribution shifts.

2. **Multi-Trigger Consistency Analysis**: We analyze whether the model exhibits abnormal consistency in misclassification patterns across synthesized triggers—a signature unique to backdoors. Clean models show random responses, while backdoored models reveal hidden decision boundaries.

**Expected outcomes**: A generalizable detector achieving >90% accuracy against diverse backdoor types (patch-based, semantic, dynamic) with minimal clean data requirements. This approach bridges the gap between attack diversity and defense universality, providing practical deployment value for pre-trained model verification in production environments.