# Phase 2A Hypothesis Summary

**Generated:** 2026-05-12T01:12:30Z  
**Workflow:** phase2a-dialogue v10.0.0  
**Architecture:** Self-Contained Tikitaka Loop  
**Status:** VALIDATED

---

## Core Hypothesis

**Performance-weighted hierarchical coordination between parameter-efficient adaptation and sparse expert routing yields super-additive efficiency gains under intermediate task heterogeneity conditions.**

Under conditions of intermediate task heterogeneity (mean pairwise KL divergence 0.3-1.5 between independent routing distributions), if we apply performance-weighted alignment between adapter-specific routing biases and expert utilization patterns, then joint LoRA-MoE training achieves super-additive efficiency gains (≥2% above additive baseline), because alignment induces functional decoupling where high mutual information between adapters and experts reduces cross-task gradient interference.

---

## Key Innovation

**Bidirectional functional coordination** (not structural composition) through differentiable performance attribution signals. Existing MoE-PEFT uses MoE within adapter architecture (structural). We propose cross-level alignment between hierarchical selection mechanisms (functional)—adapters influence routing via learned biases, routing patterns refine adapter specialization via performance signals.

---

## Causal Mechanism (4 Steps)

1. **Performance-weighted alignment** couples adapter routing biases to expert performance attributions via L_align = -Σ A_e · ΔL_e
2. **MI increase**: Alignment training increases normalized mutual information I(A;E)/log(E) as adapters learn task-specific expert preferences
3. **Functional decoupling**: High-MI task pairs show reduced cross-task gradient interference within experts
4. **Super-additive gains**: Functional decoupling enables performance improvements via reduced interference and improved specialization

---

## Regime-Dependent Design Law

**Inverted-U relationship** over task heterogeneity (measured via KL divergence):

- **Low KL (<0.3)**: Homogeneous tasks → **Shared adapter** preferred (no coordination overhead needed)
- **Mid KL (0.3-1.5)**: Intermediate heterogeneity → **Coordinated** outperforms by ≥2% (coordination sweet spot)
- **High KL (>1.5)**: Highly orthogonal tasks → **Independent adapters** preferred (coordination ineffective)

---

## Primary Predictions

**P1 (Super-additivity):**  
Mid-KL tasks show significant interaction effect (F > 4.0, p < 0.05) with coordinated training exceeding additive baseline by ≥2% absolute accuracy in ≥70% of triplets.

**P2 (Mediation):**  
Alignment increases normalized MI (β_a > 0, p < 0.001), MI mediates performance gains (β_b > 0, p < 0.01), with temporal precedence (ΔMI at step t predicts ΔPerf at t+500).

**P3 (Functional Decoupling):**  
High-MI tasks exhibit gradient interference < entropy-matched control by ≥0.2 cosine units, proving functional specialization.

---

## Experimental Validation Strategy

**Phase 1 - Core Mechanism (Must-Have):**
- Mediation analysis (paths a/b/c/c′) with temporal precedence across 100 runs
- Destruction test: shuffle alignment → performance drops ∝ MI
- Parameter-matched capacity controls (random routing bias baseline)
- ICC ≥ 0.7 routing reliability validation

**Phase 2 - Design Law (High Impact):**
- Pre-registered regime switching on 15 task triplets (low/mid/high KL)
- Inequality thresholds: Mid-KL coordinated > baselines by ≥2%
- Failure tolerance: <30% triplets violate predictions within bin

**Phase 3 - Generalization (Field-Level):**
- Gradient interference < entropy-matched control (effect size ≥0.2)
- Cross-method test: Prefix tuning on 5 mid-KL tasks
- Pre-defined falsification: No super-additive interaction → no generality

---

## Falsification Criteria

The hypothesis fails if:
- **Mediation fails**: c′ remains large (>0.8·c), MI rises after performance plateaus
- **Regime switching fails**: >30% of triplets violate directional inequalities within KL bins
- **Destruction test fails**: Performance unchanged when alignment shuffled
- **Capacity confound**: Parameter-matched random baseline achieves equal performance
- **Attribution noise**: CV(ΔL_e) > 1.0 indicates unstable coupling signal

---

## Scope & Limitations

**Applies to:**
- Multi-task learning with 3+ heterogeneous tasks
- Intermediate heterogeneity regimes (KL 0.3-1.5)
- MoE architectures with 4+ experts
- PEFT methods (LoRA, adapters, prefix tuning)

**Does NOT apply to:**
- Single-task scenarios
- Homogeneous tasks (KL < 0.3)
- Highly orthogonal tasks (KL > 1.5)
- Dense models without expert routing

**Known limitations:**
- Requires stable routing (ICC ≥ 0.7)
- Computational overhead: ~90 runs + 2K gradient computations
- Regime boundaries may need domain-specific tuning

---

## Persona Verdicts

- 🔭 **Dr. Nova** (Novelty): **STRONG** - Genuine conceptual advance with predictive design principle
- 🔬 **Prof. Vera** (Falsifiability): **STRONG** - Multiple precise failure modes, causal chain can fracture at identifiable joints
- 🎯 **Dr. Sage** (Significance): **STRONG** - Establishes design law linking heterogeneity to architectural choice
- ⚙️ **Prof. Pax** (Feasibility): **MODERATE-STRONG** - Mathematically sound, resource-intensive but tractable
- 🛡️ **Dr. Ally** (Synthesis): **STRONG** - Comprehensive operationalization of all requirements
- 🔍 **Prof. Rex** (Critique): **STRONG** - Causal structure with destruction tests and capacity controls

---

## Phase 2B Readiness: READY

**Next Steps:**
- Decompose H-M sub-hypotheses from 4-step causal chain
- Define H-C sub-hypotheses from inverted-U regime structure
- Establish verification sequence: existence → mechanism → comparison
