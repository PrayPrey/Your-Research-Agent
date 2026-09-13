# Research Idea

## Title
Cross-Modal Binding Red Teaming: Exploiting Emergent Semantics in Multimodal LLMs Through Compositional Adversarial Attacks

## Motivation
Current safety mechanisms for multimodal LLMs rely on individual modality classifiers (e.g., image safety filters, text toxicity detectors) that evaluate inputs independently. However, recent evidence shows 34% of multimodal failures occur when individually-safe inputs combine to produce harmful outputs—analogous to the McGurk Effect where combining safe audio and visual stimuli creates emergent perception. This compositional vulnerability represents an unaddressed attack surface: adversaries could craft image-text pairs that each pass safety checks but jointly trigger harmful model outputs, completely bypassing existing defenses.

## Main Idea
We propose Cross-Modal Binding Red Teaming (CBRT), a novel attack methodology exploiting emergent semantics in attention-based multimodal fusion. The core mechanism uses dual-objective gradient optimization to generate perturbations that: (1) keep individual modality classifiers predicting "safe," while (2) steering the joint cross-modal embedding toward harmful targets. We hypothesize CBRT attacks will achieve >50% success rate—significantly exceeding the 34% natural compositional failure baseline—because cross-modal attention creates semantic combinations absent in either input alone.

Experiments will evaluate LLaVA, GPT-4V, and Gemini across three harm categories (weapon assembly, dangerous synthesis, harassment), comparing against single-modality and transfer-based baselines. Success demonstrates a critical blind spot in current safety architectures, motivating development of compositional safety classifiers that evaluate joint semantics rather than individual modalities.