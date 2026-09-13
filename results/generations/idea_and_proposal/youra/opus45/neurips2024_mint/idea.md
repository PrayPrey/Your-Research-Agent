# Research Idea

## Title
Regulatory Suppression Architecture: Immune-Inspired Continuous Modulation for Context-Aware LLM Safety

## Motivation
Current LLM safety interventions face a critical tradeoff: binary safety switches (like SafeSwitch) achieve strong harmful content blocking but cause excessive over-refusal (~48%) of benign prompts, while static steering methods lack context sensitivity. This mirrors a fundamental challenge in biological immune systems, solved through regulatory T-cells that provide context-dependent suppression. We propose bridging this gap by learning continuous, context-aware safety modulation rather than binary activation.

## Main Idea
We introduce the Regulatory Suppression Architecture (RSA), where a learned Regulatory Head outputs continuous suppression strength s(context) ∈ [0,1] to modulate pre-computed safety steering vectors during inference. The mechanism operates through four causal steps: (1) extract safety-relevant context from intermediate LLM representations, (2) process through the Regulatory Head to compute suppression strength, (3) scale the safety steering vector by s(context), and (4) integrate the calibrated intervention with base model outputs.

Training uses constrained reinforcement learning without explicit safety labels, optimizing for both low harmful content rates and reduced over-refusal. Key predictions: over-refusal rate <35% (vs. SafeSwitch's 48%) while maintaining harmful content blocking ≤20%, with suppression strength correlating with human-judged safety relevance (ρ>0.6).

This approach enables fine-grained safety control with minimal parameter overhead (<6%), offering practical deployment for controllable foundation models.