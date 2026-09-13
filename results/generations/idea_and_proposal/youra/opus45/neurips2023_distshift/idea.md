# Research Idea

## Title
Entropy-Guided Adaptive Routing (EGAR): Dynamic Strategy Selection Between ICL and LoRA for Robust Foundation Model Adaptation

## Motivation
Foundation models exhibit varying robustness under distribution shifts, with fine-tuning often degrading their inherent OOD generalization. Current approaches apply uniform adaptation strategies regardless of sample-specific model confidence, missing opportunities for efficiency and robustness. A key insight from recent work (DaWin) shows that predictive entropy reliably indicates model competence on individual samples. This raises a critical question: can we leverage per-sample entropy to dynamically route between lightweight in-context learning (for confident predictions) and deeper LoRA adaptation (for uncertain predictions)?

## Main Idea
EGAR proposes entropy-based routing between two complementary adaptation strategies. The core mechanism: (1) compute Shannon entropy from the model's predictive distribution for each sample, (2) route low-entropy samples to ICL (preserving pretrained robustness) and high-entropy samples to LoRA (enabling deeper adaptation). The causal hypothesis is that entropy serves as a reliable proxy for model competence—low entropy indicates sufficient pretrained knowledge, while high entropy signals need for parameter adaptation.

**Methodology**: Evaluate on CLIP/LLaMA across ImageNet-C, ImageNet-R, and WILDS benchmarks, comparing against ICL-only, LoRA-only, and DaWin baselines.

**Expected outcomes**: >1.5% accuracy improvement over best single-strategy baseline with >20% computational savings versus uniform LoRA. This establishes a principled framework for sample-adaptive foundation model deployment under distribution shift.