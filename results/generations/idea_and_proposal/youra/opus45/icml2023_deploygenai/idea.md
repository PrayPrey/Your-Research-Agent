# Research Idea

## Title
Semantic Harm Affinity Maturation (SHAM): Bridging the Generalization Gap in LLM Safety Guardrails

## Motivation
Current LLM safety guardrails exhibit a critical deployment vulnerability: they perform well on benchmark attacks but fail dramatically on novel adversarial prompts. State-of-the-art systems like Qwen3Guard show a 57% accuracy gap between benchmark and novel attacks, severely limiting real-world safety in high-stakes domains like healthcare. This gap exists because traditional classifiers learn surface patterns (typos, ciphers, encodings) rather than underlying harmful intent, making them brittle against attack variations.

## Main Idea
We propose SHAM, a dual-layer architecture combining contrastive semantic harm encoding with evolutionary affinity maturation. The core insight is that adversarial attacks sharing harmful intent cluster semantically regardless of surface expression. 

**Methodology:** (1) Train a contrastive encoder on attack-intent pairs to create surface-invariant harm embeddings; (2) Apply evolutionary optimization (CMA-ES) to expand decision boundaries using held-out attack variants as fitness signals; (3) Combine fast semantic similarity with evolved classifiers for robust detection.

**Predictions:** SHAM will reduce the benchmark-to-novel gap from >50% to <30% while maintaining false positive rates within 5% of baselines. Falsification occurs if clustering purity <0.5 or gap remains >45%.

**Impact:** Enables reliable guardrail deployment in safety-critical applications by addressing the fundamental generalization failure of current approaches.