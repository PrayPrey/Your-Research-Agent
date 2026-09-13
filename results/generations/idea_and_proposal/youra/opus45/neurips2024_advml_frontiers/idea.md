# Research Idea

## Title
ModularShield: A Hierarchical Plug-and-Play Defense Framework Against Multimodal Jailbreak Attacks

## Motivation
Large multimodal models (LMMs) face increasingly sophisticated jailbreak attacks that exploit cross-modal vulnerabilities—where visual and textual attack vectors combine to bypass single-layer defenses. Current defenses (UniGuard, SafeMLLM, E²AT) each address specific attack types but fail against diverse, adaptive threats. The critical gap is the lack of a unified framework that integrates complementary defense mechanisms across abstraction levels while maintaining practical efficiency.

## Main Idea
We propose ModularShield, a 4-layer hierarchical defense framework with modular plug-and-play architecture. The core insight is that layered defense with inter-layer information flow catches attacks that bypass individual layers through complementary coverage:

1. **Input Sanitization** blocks pattern-based jailbreaks
2. **Embedding Anomaly Detection** catches perturbation-level attacks
3. **Cross-Modal Consistency** (via adversarially-robust CLIP) detects visual-textual divergence
4. **Response Verification** provides final safety filtering

We will evaluate on JailBreakV-28K against LLaVA-1.5-7B, comparing ModularShield to single-layer baselines across visual, textual, cross-modal, and adaptive attacks. Success criteria: ≥20% absolute ASR reduction versus best baseline, <2× latency overhead, and <10% utility degradation. Ablation studies will verify each layer's independent contribution. This framework advances practical LMM safety while providing a modular foundation for integrating future defense innovations.