# Research Idea

## Title
Safety-Constrained LoRA: Integrating Surrogate Control Barrier Functions into Vision-Language-Action Model Fine-Tuning

## Motivation
Large Vision-Language-Action (VLA) models show promise for robotic manipulation but require fine-tuning for deployment. Current approaches face a critical dilemma: runtime safety filters (like Control Barrier Functions) add computational overhead unsuitable for edge deployment, while standard fine-tuning methods ignore safety constraints entirely. This gap leaves practitioners choosing between safe-but-slow or fast-but-risky deployments—neither acceptable for real-world robotics.

## Main Idea
We propose Hierarchical Safety-Constrained LoRA (HSC-LoRA), which embeds safety awareness directly into adapter weights during training, eliminating runtime safety computation. The core mechanism integrates a differentiable surrogate CBF loss into LoRA optimization, constraining gradient updates to parameter regions that preserve safety boundaries. A dedicated safety adapter branch (rank-64) captures complex constraint geometry while task adapters maintain performance.

**Methodology:** Using OpenVLA-7B on SafeLIBERO benchmarks, we vary CBF constraint weight (λ∈[0.1-1.0]) and adversarial augmentation ratios, measuring safety violation rates and task success across 25+ runs per condition.

**Expected Outcomes:** >30% reduction in safety violations while maintaining task success within 5% of baseline, with <10% inference overhead. This enables consumer-GPU fine-tuning of safe VLA models without runtime safety filters—democratizing safe robot deployment.