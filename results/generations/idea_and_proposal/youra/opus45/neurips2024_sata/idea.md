# Research Idea

## Title
Adaptive Safety Immune System (ASIS): A Three-Tier Bio-Inspired Framework for Reducing False Positives in LLM Agent Safety

## Motivation
Current LLM agent safety systems rely on static guardrails that suffer from high false positive rates (up to 92%), blocking legitimate actions and degrading user experience. While recent work shows LLM activations encode safety-relevant signals and constraints can be dynamically generated, no unified framework leverages both insights. This creates a critical gap: agents need safety systems that adapt to context rather than applying rigid rules, similar to how biological immune systems distinguish genuine threats from benign stimuli.

## Main Idea
We propose ASIS, a three-tier adaptive safety framework inspired by biological immune systems. The **innate layer** extracts LLM activation patterns for fast, tuning-free risk scoring (1-5ms). High-risk queries trigger the **adaptive layer**, which generates context-specific safety constraints via a small transformer decoder trained on threat-constraint pairs. The **memory layer** stores successful interventions for O(log n) retrieval, accelerating responses to repeated threat patterns.

**Core hypothesis**: This tiered architecture reduces false positives by ≥30% compared to static guardrails (TrustAgent, NeMo Guardrails) while maintaining >90% unsafe action prevention, because adaptive constraint generation produces more precise interventions than fixed rule sets.

**Evaluation**: Comparison across 2000+ queries on HarmBench and Agent-SafetyBench, measuring prevention rate, false positive rate, and latency. Falsification occurs if no FPR improvement is observed.