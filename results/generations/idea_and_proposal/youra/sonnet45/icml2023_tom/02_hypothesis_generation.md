# Phase 2A Extended: Hypothesis Clarification Summary

**Date:** 2026-02-08
**Author:** Pray
**Hypothesis ID:** H-2025-ToM-POMDP-01
**Confidence:** 0.82
**Status:** Ready for Phase 2B Verification Planning

---

## Executive Summary

**Main Hypothesis:**
If an explicit POMDP-based Epistemic State Tracker (EST) is integrated with a fine-tuned LLM to maintain first-order belief distributions over propositional mental states, then ToM task accuracy will increase compared to base LLMs, **because** the EST provides interpretable probabilistic beliefs that condition generation with cognitively-grounded mental state representations.

**Key Innovation:** First application of robotics POMDP belief tracking framework to dialogue-based Theory of Mind in LLMs, enabling explicit, interpretable, and probabilistically-grounded mental state reasoning.

---

## Core Contributions

### Theoretical
1. **POMDP Formalization**: First formalization of dialogue ToM as Partially Observable Markov Decision Process
2. **Cognitive Grounding at Scale**: Bridges cognitive science Bayesian ToM with production NLP (7B+ LLMs)
3. **Uncertainty Quantification**: Calibrated probability distributions for mental state inferences (ECE ≤ 0.15)

### Methodological
4. **Neuro-Symbolic Architecture**: Neural observation model + symbolic particle filter belief tracking
5. **EST-Conditioned Fine-tuning**: Systematic protocol for teaching LLMs to utilize explicit beliefs
6. **Cross-Domain Validation**: Transfers POMDP framework from robotics (30+ years) to NLP

### Practical
7. **Interpretable & Steerable ToM**: Human-readable belief distributions with manual override capability
8. **Modular Design**: Independent optimization of EST and LLM components
9. **Benchmark-Ready Evaluation**: Comprehensive protocol on ToMBench, MindCraft, OpenToM

---

## Testable Predictions

**Primary (P1):** EST-on achieves ≥5pp higher accuracy than EST-off on ToMBench (p<0.05, n=30)

**Secondary:**
- **P2:** Particle count 100→500 shows ≥3% gain, 500→1000 shows ≤1% (diminishing returns)
- **P3:** Fine-tuned LLM shows ≥10% higher accuracy than zero-shot with EST
- **P4:** EST interpretability scores ≥4.0/5.0 vs. pure LLM ≤2.0/5.0 (n=30 annotators)
- **P5:** Computational overhead ≤2.0x base LLM latency
- **P6:** Belief calibration ECE ≤0.15

**Falsification:** Hypothesis refuted if P1 fails OR overhead >3.0x OR observation model training diverges

---

## Key Assumptions

1. **Mental states** representable as first-order propositions + goals
2. **Utterances** provide sufficient evidence for mental state inference
3. **Variational inference** can learn observation model P(utterance|mental_state)
4. **Particle filter** with 500 particles provides adequate belief approximation
5. **LLM fine-tuning** on 10K+ examples enables EST utilization
6. **First-order ToM** captures majority of dialogue scenarios

---

## Scope & Limitations

**Applies To:**
- Dialogue-based collaborative tasks (tutoring, customer service, planning)
- Text-based English dialogue with shared context
- Domains where beliefs and goals are central

**Does NOT Apply To:**
- Higher-order ToM (recursive beliefs: "I believe you believe...")
- Affective ToM (emotion recognition, empathy)
- Deceptive communication
- Real-time vision-based ToM
- Low-resource languages

---

## Phase 2B Sub-Hypotheses

**SH1 (Existence):** EST module maintains accurate belief distributions (observation model ≥70% accuracy, ESS ≥50% after 20 turns)

**SH2 (Mechanism):** Fine-tuned LLM utilizes EST outputs (≥10% gain vs. zero-shot, ≥8% drop when EST removed)

**SH3 (Comparison):** EST-LLM outperforms baselines (≥5pp vs. pure LLM, ≥3pp vs. SymbolicToM) with ≥4.0/5.0 interpretability

**SH4 (Scalability):** Computational overhead ≤2.0x latency, ≤500MB memory increase

**SH5 (Interpretability):** Human annotators rate EST explanations ≥1.5 points higher than pure LLM

---

## Evidence Base

**Scholar Papers (3 core):**
- Erdogan et al. (2024): Epistemic logic abstractions improve collaboration
- Sarangi et al. (2025): Function-guided prompting improves LLM ToM
- Liu et al. (2023): Internal listener models improve language acquisition 8-12%

**Cross-Domain:**
- Robotics POMDP (30+ years): Kaelbling et al. (1998), Thrun et al. (2005)
- Cognitive Science: Baker et al. (2009), Rabinowitz et al. (2018)

**Benchmarks:**
- ToMBench (Chen et al., 2024): 2,860 samples, 31 ToM abilities, GPT-4 ~78%
- FANToM (Kim et al., 2023): Complex scenarios, models ~65%
- OpenToM: Classic false belief tasks, ~72%

---

## Statistical Design

**Experimental Design:** Within-subjects 2×3 factorial (EST-on/off × particle count 100/500/1000)

**Sample Size:** n=30 scenarios per condition (Cohen's d=0.5, power=0.80, α=0.05)

**Tests:**
- P1: Paired t-test (EST-on vs. EST-off)
- P2: Repeated measures ANOVA (particle counts)
- P3: Paired t-test (fine-tuned vs. zero-shot)
- P4: Mann-Whitney U (interpretability ratings)
- P5: Descriptive stats (latency measurements)
- P6: ECE calculation (n=500 predictions)

---

## Comparison Baselines

- **Pure LLM** (GPT-4, Claude 3.5): Implicit ToM in embeddings (opaque, overconfident)
- **SymbolicToM** (Sclar et al., 2023): Rule-based (interpretable, brittle, no uncertainty)
- **AutoToM** (Gandhi et al., 2024): Bayesian inverse planning (not LLM-integrated)
- **Agentic-ToM** (Sarangi et al., 2025): Function-guided prompting (ad-hoc functions)

**EST-LLM Advantage:** Combines interpretability (vs. pure LLM) + probabilistic beliefs (vs. SymbolicToM) + LLM integration (vs. AutoToM) + principled framework (vs. Agentic-ToM)

---

## Open Questions for Phase 2B

1. **Proposition ontology design** (granularity level) - HIGH priority
2. **Observation model architecture** (BERT vs. GPT style) - MEDIUM priority
3. **LLM fine-tuning dataset size** (minimum effective) - MEDIUM priority
4. **Multi-agent belief tracking** (independent vs. joint EST) - MEDIUM priority
5. **GPU parallelization** for particle filter - MEDIUM priority

---

## Readiness Status

✅ **Hypothesis Clarity:** If-Then-Because format, operationalized variables, explicit assumptions
✅ **Testability:** 6 quantified predictions, falsification criteria, statistical design
✅ **Evidence Base:** 3 scholar papers, cross-domain validation, benchmarks identified
✅ **Contribution Clarity:** 9 contributions (theoretical, methodological, practical)
✅ **Phase 2B Decomposability:** 5 sub-hypotheses with verification methods

**READY FOR PHASE 2B** ✅

---

## Full Document

For complete details including:
- Detailed causal mechanism with first principles decomposition
- Comprehensive related work (15+ papers)
- Complete statistical verification protocol
- All 6 key assumptions with justifications
- Full scope and boundary conditions
- 7 open questions with resolution paths

**See:** `02a_extended_hypothesis_full.md`

---

*Generated using YouRA Research Phase 2A Extended Workflow (YOLO Mode)*
*Source: Phase 2A Round 1 (FEASIBLE hypothesis)*
*Next Phase: Phase 2B - Verification Planning (Hypothesis Decomposition)*
