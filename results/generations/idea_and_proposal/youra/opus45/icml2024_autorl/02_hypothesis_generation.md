# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - FEASIBLE)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-MoE-ICRL-v1
**Confidence Level:** 0.78 (adjusted from 0.82 due to concurrent work T2MIR)

**Main Hypothesis:**
Under the condition of diverse robotic manipulation tasks (Meta-World ML45 benchmark), **if** K meta-learned expert policy modules (small transformers with diversity regularization) are combined with a transformer-based in-context router in a **two-phase training paradigm**, **then** cross-domain generalization on held-out task categories will exceed baseline ICRL methods (AD, DPT) by >15% success rate, **because** compositional policy assembly through soft attention over specialized, explicitly meta-learned primitives enables novel skill combinations that (1) monolithic transformers cannot achieve, and (2) end-to-end MoE training (T2MIR) does not explicitly optimize for.

**Alternative Hypothesis (H0):**
Two-phase meta-learning of expert primitives provides no advantage over end-to-end MoE training (T2MIR) or monolithic ICRL (AD, DPT) for cross-domain generalization; any observed improvements are attributable to increased parameter count rather than compositional structure.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Architecture Type | Independent | MoE-ICRL (ours) vs T2MIR vs AD vs DPT vs MAML vs PEARL | 6 conditions |
| Number of Experts K | Independent | Expert module count: K ∈ {8, 16, 32} | Ablation study |
| Training Paradigm | Independent | Two-phase (meta-train experts → train router) vs End-to-end | 2 conditions |
| Success Rate on Held-Out Categories | Dependent | % episodes achieving task goal on Meta-World ML45 test split (5 held-out categories) | 0-100% |
| Sample Efficiency | Dependent | Environment steps to reach 50% success threshold | 0-10M steps |
| Expert Utilization Diversity | Dependent | Entropy of router attention distribution across experts | 0-log(K) nats |
| Meta-Training Task Distribution | Controlled | Meta-World ML45 training categories (40 tasks, fixed) | Fixed |
| Expert Architecture | Controlled | 2-3 layer transformers, ~1M params each, fixed across conditions | Fixed |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Meta-Training with Diversity Regularization
    ↓
Step 2: Specialized Expert Primitives Emerge
    ↓
Step 3: In-Context Router Composes Primitives via Soft Attention
    ↓
Outcome: Cross-Domain Generalization on Held-Out Tasks
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Lake & Baroni (2023), Nature | Meta-learning enables compositional generalization through structure emergence | Strong |
| Step 1 → Step 2 | Wang et al. (2024), Motor Primitives | Motor primitives with modulation achieve high learning efficiency | Strong |
| Step 2 → Step 3 | Algorithm Distillation (Laskin 2022) | Transformers implement RL algorithms in-context through trajectory conditioning | Strong |
| Step 2 → Step 3 | DPT (Lee 2023) | Supervised pretraining produces in-context RL with exploration | Strong |
| Step 3 → Outcome | T2MIR (Wu 2025) | MoE in ICRL improves capacity, BUT uses end-to-end training | Medium |
| Step 3 → Outcome | Meta-World (Yu 2019) | Meta-RL struggles beyond 10 training tasks | Strong |

**Key Tension:**
- **Tension:** T2MIR (2025) demonstrates MoE + ICRL works with end-to-end training. Our hypothesis proposes two-phase training is superior.
- **Resolution:** Verification tests whether two-phase training produces more specialized primitives with better OOD generalization.

### 1.4 Key Assumptions

| # | Assumption | Evidence | Consequence if Violated |
|---|------------|----------|------------------------|
| 1 | RL skills are decomposable into modular primitives | Motor primitives (Wang 2024), compositional generalization (Lake & Baroni 2023) | MoE provides no benefit over monolithic models |
| 2 | Diversity regularization prevents expert collapse | VAE literature, MoE load balancing | Degenerates to single-expert model |
| 3 | In-context trajectory provides sufficient signal for primitive selection | AD, DPT demonstrate in-context works | Router cannot learn meaningful patterns |
| 4 | Two-phase training is superior to end-to-end | Novel claim (vs T2MIR) | No advantage over T2MIR |

### 1.5 Scope & Boundaries

**Applies to:** Continuous control with shared skill structure, Meta-World, medium-scale MoE (K=8-32)

**Does NOT apply to:** Discrete action spaces, single-task RL, very large-scale MoE (>100 experts)

**Limitations:** Soft attention may miss discrete boundaries; two-phase adds complexity; diversity coefficient is sensitive

### 1.6 Testable Predictions

**Primary Prediction (P1):**
MoE-ICRL with two-phase training achieves >15% higher success rate on Meta-World ML45 held-out categories vs AD, DPT; >5% vs T2MIR.

*Measurement:* Success rate on 5 held-out categories, 50 episodes each
*Statistical test:* Paired t-test, n ≥ 20 seeds, p < 0.05

**Secondary Predictions:**

**P2 (Expert Specialization):** Expert utilization entropy H(α) > 1.5 nats for K=8 with diversity regularization.

**P3 (Compositional Routing):** Similar tasks produce similar attention distributions (cosine similarity > 0.7).

**P4 (Two-Phase Advantage):** Two-phase training produces higher H(α) than T2MIR end-to-end.

**Falsification Criteria:**
1. Success rate ≤ AD baseline
2. Expert entropy H(α) < 0.5 nats
3. No task-category structure in attention
4. No measurable advantage over T2MIR

### 1.7 SOTA Baseline

**Concurrent Work - T2MIR (Wu et al., 2025):**
- Token-wise + Task-wise MoE for ICRL, end-to-end training
- Outperforms AD, DPT baselines
- **Differentiation:** Our two-phase meta-learning vs their end-to-end; our explicit primitive specialization vs architectural enhancement

**Novelty Claim (Refined):**
First two-phase meta-learned primitives for compositional ICRL with explicit diversity regularization.

### 1.8 Statistical Verification Design

- **Effect size:** Cohen's d = 0.8, **Seeds:** n ≥ 20
- **Test:** One-way ANOVA + Tukey HSD, α = 0.05 (Bonferroni corrected)
- **Report:** Mean ± Std, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does MoE-ICRL with two-phase training achieve significantly higher success rate on held-out Meta-World categories than AD, DPT?"

**SH2 (Mechanism) - 3 sub-hypotheses:**
- **H-M1:** Meta-training + diversity regularization → specialized primitives (entropy)
- **H-M2:** In-context trajectory → meaningful router attention (task similarity)
- **H-M3:** Soft attention composition → novel skill combinations (held-out performance)

**SH3 (Comparison):**
"Does two-phase training provide advantage over T2MIR end-to-end?"

### Readiness Checklist

- [x] "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-MoE-ICRL-v1
- [x] Confidence: 0.78
- [x] H0 defined
- [x] Variables operationalized
- [x] Causal mechanism with evidence (N=3)
- [x] Key tension + resolution
- [x] Assumptions with consequences
- [x] 4 testable predictions (P1 primary)
- [x] 4 falsification criteria
- [x] Baselines: AD, DPT, MAML, PEARL, T2MIR
- [x] SH1, SH2, SH3 defined

### Open Questions

1. **Compute:** ~4-8 GPU-days (A100) for K=32 on ML45
2. **T2MIR Code:** Available at https://github.com/NJU-RL/T2MIR
3. **Diversity λ:** Grid search needed for optimal coefficient
4. **Priority:** SH1 → SH2-M1 → SH3

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
