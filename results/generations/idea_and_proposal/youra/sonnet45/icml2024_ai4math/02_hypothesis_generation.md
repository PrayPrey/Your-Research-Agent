# Phase 2A Extended: Hypothesis Clarification - Summary

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Hypothesis ID:** H-icml2024ai4math-01
**Status:** ✅ Ready for Phase 2B Verification Planning

---

## Executive Summary

**Main Hypothesis:**
Training neural theorem provers through a three-phase developmental curriculum (diversity pre-training → cognitive demand progression → research-level integration) will improve research-level performance from 10.3% to >25% on RLMEval, while maintaining benchmark performance and achieving superior template robustness.

**Key Innovation:**
First application of evidence-based educational learning science (developmental psychology + education science) to neural theorem proving, providing principled curriculum design grounded in transfer learning bounds and cognitive demand frameworks.

**Target Performance:**
- **RLMEval (research-level)**: 10.3% → >25% (+142% improvement)
- **MiniF2F (benchmark)**: ≥85% (maintain SOTA ~89%)
- **Template Robustness**: <30% drop (vs baseline 47-73% drop)

---

## 1. Clarified Hypothesis (Core)

### 1.1 Main Statement

Training neural theorem provers through a three-phase developmental curriculum—(1) diversity pre-training across 10 mathematical domains, (2) cognitive demand progression through 4 difficulty tiers with template variation, (3) research-level integration on authentic Lean projects—will improve research-level theorem proving performance from 10.3% baseline (RLMEval) to >25%, by building generalizable reasoning primitives rather than benchmark-specific pattern matching.

**Alternative Hypothesis (H0):**
Curriculum structure has no effect; performance differences are due to total training compute or data volume alone.

### 1.2 Variables (Key)

| Type | Variable | Measurement |
|------|----------|-------------|
| **Independent** | Curriculum Structure | 3-phase vs flat distribution |
| **Independent** | Tier Advancement Threshold | 80% success rate target |
| **Dependent** | RLMEval Performance | Pass rate on 613 research theorems |
| **Dependent** | MiniF2F Performance | Standard benchmark evaluation |
| **Dependent** | Template Robustness | Performance drop on variants |
| **Controlled** | Model Architecture | Transformer LLM (7B-30B) |
| **Controlled** | Total Training Compute | Matched or measured (2-3x budget) |

### 1.3 Causal Mechanism (Simplified)

```
Diversity Pre-training (10 domains)
    ↓ [Transfer Learning Bounds]
Broad Reasoning Primitives
    ↓ [Cognitive Demand Progression]
Abstract Reasoning Patterns (not surface shortcuts)
    ↓ [Transfer to Complexity]
Research-Level Generalization (>25% RLMEval)
```

**Evidence:**
- Fahim & Karim (2026): Diversity enables few-shot generalization (AUC 0.65 with 50 samples)
- Neugebauer & Prediger (2022): Cognitive demand progression builds robust understanding
- Wang et al. (2025): "Pseudo Aha Moment" (77-100% errors) from surface pattern shortcuts

### 1.4 Testable Predictions

**P1 (Primary):** RLMEval performance ≥25% (vs 10.3% baseline, +14.7pp)
**P2 (Benchmark):** MiniF2F performance ≥85% (maintain SOTA ~89%)
**P3 (Robustness):** VAR-MATH template drop <30% (vs 47-73% baseline)
**P4 (Pilot):** Curriculum ordering improves over random by ≥15% in pilot study
**P5 (Tier Correlation):** Tier 4 success correlates with RLMEval (r ≥ 0.6)

**Falsification:** Hypothesis falsified if P1 <15% RLMEval OR P4 pilot shows ≤5% improvement over random.

### 1.5 Statistical Design

- **Design:** Randomized controlled comparison (curriculum vs flat baseline)
- **Replication:** 5 independent training runs (different seeds)
- **Tests:** Paired t-tests, α=0.05, target Cohen's d ≥ 1.5
- **Power:** 1-β = 0.80 (80% power to detect true effects)
- **Confound Controls:** Match total compute, data volume, architecture, hyperparameters

---

## 2. Contributions (Summary)

### 2.1 Theoretical Contribution

**Novel Claim:** First formal connection between educational learning science and neural theorem prover generalization.

**Foundations:**
- Transfer learning bounds from developmental psychology (Fahim & Karim 2026) predict diversity → generalization
- Cognitive demand frameworks from education science (Neugebauer & Prediger 2022) justify progressive scaffolding
- Provides learning-theoretic explanation for curriculum effects (not just empirical heuristics)

### 2.2 Methodological Contribution

**Novel Framework: DC-NTP (Developmental Curriculum for Neural Theorem Proving)**

**Three Phases:**
1. **Diversity Pre-Training**: 10,000 theorems across 10 domains (algebra, geometry, logic, number theory, set theory, graph theory, combinatorics, topology, analysis, category theory), 1-2 step proofs, >90% success target
2. **Cognitive Demand Progression**: 5,000 theorems in 4 tiers (2-3 steps, 4-6 steps, 7-10 steps, 11+ steps), 80% advancement threshold, 30% template variation per tier
3. **Research-Level Integration**: 613 RLMEval theorems, RL fine-tuning on authentic research problems

**Key Innovation:** Semi-automated curriculum construction using proof length + dependency count + tactic diversity metrics.

### 2.3 Practical Contribution

**Performance Target:** 10.3% → >25% RLMEval (2.5x improvement, brings research-level AI assistance to practical viability)

**Application Domains:**
- Formal mathematics research (assist mathematicians in Lean formalization)
- Proof assistant augmentation (LeanCopilot-style tactic suggestions)
- Automated formalization (natural language → formal proof)
- Mathematical education (adaptive scaffolding systems)

**Accessibility:** Uses existing LeanDojo infrastructure, 2-3x baseline compute (~500-1000 GPU-hours for 7B model), open-source datasets

---

## 3. Key Related Work (Top 5)

1. **DeepSeek-Prover-V2 (2025)**: SOTA baseline (88.9% MiniF2F, 10.3% RLMEval), single-phase RL training → We extend with 3-phase curriculum
2. **LeanDojo (2023)**: RL training infrastructure → We build on this toolkit
3. **ToRA (2024)**: Heuristic curriculum (easy-to-hard) → We provide educationally-grounded principled design
4. **Fahim & Karim (2026)**: Child development transfer learning bounds → Cross-domain inspiration for Phase 1 diversity
5. **Neugebauer & Prediger (2022)**: Cognitive demand frameworks in education → Cross-domain inspiration for Phase 2 progression

**Gap in Literature:** No prior work combines (1) educational learning science grounding, (2) research-level focus (RLMEval), (3) template robustness evaluation, (4) pilot study validation requirement.

---

## 4. Phase 2B Readiness

### Sub-Hypotheses Preview

**SH1 (Existence):** Curriculum ordering improves performance vs random/reverse ordering
- Experiment: Pilot study (1B model, 1,000 theorems, 4 conditions)
- Success: Curriculum >15% better than random (p<0.05)

**SH2 (Mechanism):** Curriculum changes representations toward abstract reasoning
- Experiment: Attention analysis, embedding geometry, probing tasks
- Success: ≥20% higher reasoning-based organization vs baseline

**SH3 (Comparison):** Curriculum achieves target performance vs SOTA
- Experiment: Full-scale training (7B-30B model, 15,613 theorems)
- Success: P1, P2, P3 met with statistical significance

### Readiness Checklist

✅ **All Criteria Met:**
- [x] Hypothesis clarity (causal relationship specified)
- [x] Testability (falsifiable predictions, statistical protocol)
- [x] Evidence foundation (theoretical grounding + empirical support)
- [x] Feasibility (infrastructure available, compute budget estimated)
- [x] Novelty (differentiation from SOTA clear)
- [x] Decomposition readiness (sub-hypotheses preview provided)

### Open Questions for Phase 2B

**Methodological:**
- Q1: How to validate tier boundary calibration (2-3 steps → 4-6 steps → 7-10 steps → 11+ steps)?
- Q2: What parameterizations count as "template variants" vs "different theorems"?
- Q3: What pilot study scale is sufficient (1,000 vs 2,000-3,000 theorems)?

**Theoretical:**
- Q4: Can we formalize diversity-generalization relationship with learning-theoretic bound?
- Q5: Do transfer learning bounds quantitatively predict neural network curriculum effects?

**Practical:**
- Q6: How to update curriculum as Lean mathlib grows?
- Q7: What artifacts required for full reproducibility?

---

## 5. Next Steps

**Phase 2B Actions:**
1. Decompose hypothesis into 3 sub-hypotheses (SH1, SH2, SH3) with detailed experiment protocols
2. Design pilot study (resolve Q1-Q3)
3. Specify curriculum construction algorithm implementation
4. Address open questions through literature review or empirical pre-tests
5. Create verification roadmap with experiment priorities and dependencies
6. Establish success criteria and contingency plans for each sub-hypothesis

**Expected Timeline:**
- Phase 2B Planning: 1 week
- Phase 3 Implementation Design: 2-3 weeks
- Phase 4 Execution: 3-4 months (1 month pilot + 2-3 months full training)

---

**Status:** ✅ **COMPLETE - Ready for Phase 2B Verification Planning**

**Key Achievement:** Transformed broad hypothesis from Phase 2A into scientifically rigorous, testable hypothesis with:
- Operational variable definitions
- Causal mechanism with evidence links
- Falsifiable predictions
- Statistical verification protocol
- Clear differentiation from SOTA
- Detailed contribution specifications
- Decomposition roadmap for Phase 2B

**Confidence:** 0.82 (FEASIBLE) - Strong evidence base, clear implementation path, moderate complexity

---

*Document generated by YouRA Phase 2A Extended Workflow*
*Full version: 02a_extended_hypothesis_full.md*
*Date: 2026-02-06*
