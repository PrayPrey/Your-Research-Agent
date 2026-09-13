# Research Idea

## Title
Universal Composition Functor: Cross-Domain Compositional Generalization via Functorial Constraints on Foundation Model Primitives

## Motivation
Compositional generalization—combining learned primitives in novel ways—remains a critical challenge for AI systems. While methods like Meta-Learning for Compositionality (MLC) achieve near-perfect performance (~99%) on benchmarks like SCAN, they require domain-specific training and fail to transfer across domains. This limits practical deployment in dynamic, multi-domain environments. The key gap: no existing method achieves both high within-domain compositional accuracy AND cross-domain transfer without retraining.

## Main Idea
We propose a Universal Composition Functor (UCF)—a transformer-based module trained with category-theoretic functorial constraints to compose domain-agnostic primitives extracted from frozen foundation models (CLIP, T5). The core mechanism: functorial regularization (L_functor = ||F(p₁∘p₂) - F(p₁)⊗F(p₂)||) enforces that composition operations preserve algebraic structure across domains, enabling learned composition rules to transfer universally.

**Methodology:** Train UCF on multi-domain data (NLP: SCAN/COGS; Vision: MIT-States) with self-supervised contrastive learning plus functorial constraints. Test cross-domain transfer to held-out multimodal tasks (RefCOCO) without fine-tuning.

**Expected Outcomes:** ≥95% in-domain accuracy (matching MLC) AND ≥80% zero-shot cross-domain transfer (2x better than domain-specific methods). Ablations will verify that functorial constraints—not just shared primitives—drive generalization.

**Impact:** First empirically validated universal composition method bridging NLP, vision, and multimodal domains.