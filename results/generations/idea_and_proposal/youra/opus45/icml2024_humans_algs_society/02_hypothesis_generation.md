# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-ESF-MFG-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under conditions where agents adaptively update strategies based on observed payoffs in a strategic classification setting, if we design the classifier decision boundary using a mean-field evolutionary game formulation with reputation-based indirect reciprocity and discrete strategy space {gaming, honest, improvement}, then fair, non-gaming behavior will become evolutionarily stable, because the reputation mechanism penalizes gaming strategies and the mean-field dynamics naturally select for strategies that maximize expected utility under fairness constraints.

**Alternative Hypothesis (H0):**
The reputation-based mean-field game formulation does not produce evolutionarily stable fair behavior; instead, gaming strategies persist or dominate despite reputation penalties, OR multiple equilibria exist with unfair outcomes being equally or more stable than fair outcomes.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| classifier_decision_boundary (θ) | Independent | Parameterized decision function learned via MFG policy gradient with fairness regularization | Continuous parameters in neural network or linear model |
| reputation_decay_rate (γ) | Independent | Discount factor for reputation update rule | γ ∈ [0.8, 0.99] - higher values retain history longer |
| strategic_adaptation_rate (α) | Independent | Learning rate for agent strategy updates | α ∈ [0.01, 0.1] - typical RL learning rates |
| group_fairness_metrics | Dependent | Demographic parity gap + equalized odds difference at equilibrium | Target: DP gap < 0.05, EO diff < 0.05 |
| strategic_robustness | Dependent | Percentage of population using honest/improvement strategies at equilibrium | Target: > 90% honest/improvement |
| ESS_stability | Dependent | Invasion fitness of gaming strategy when introduced to honest equilibrium | Target: Negative invasion fitness |
| population_composition | Controlled | Fixed initial group proportions across protected attributes | Held constant across experiments |
| initial_reputation_distribution | Controlled | Uniform reputation scores at simulation start | r₀ = 0.5 for all agents |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Classifier Boundary Design
    ↓ (via incentive structure modification)
Step 2: Agent Strategy Selection
    ↓ (via replicator-like dynamics)
Step 3: Population Distribution Shift
    ↓ (via indirect reciprocity)
Step 4: Reputation Equilibrium
    ↓ (via equilibrium constraints)
Outcome: Fairness Guarantee at ESS
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Miller et al. 2019 | Strategic agents respond to classifier incentives via causal pathways | Strong |
| Step 2 → Step 3 | Gu et al. 2021; MAFE 2024 | Mean-field approximation valid for large populations | Strong |
| Step 3 → Step 4 | Smit & Santos 2024 | Indirect reciprocity stabilizes cooperation via reputation-based norms | Strong |
| Step 4 → Outcome | EGT Theory | ESS conditions ensure invasion resistance | Medium |

**Key Tension:**
- **Tension:** Smit & Santos 2024 shows norm configurations can lead to fair OR unfair cooperation.
- **Resolution:** Phase 2B experiments will explicitly test which norm configurations lead to fair ESS.

### 1.4 Key Assumptions

1. **Bounded Rationality:** Agents update strategies based on observed payoffs with noise.
   - *Consequence if violated:* Different update rules may lead to different equilibria.

2. **Mean-Field Validity:** Population dynamics follow replicator dynamics under mean-field (requires n > 1000).
   - *Consequence if violated:* Finite-agent effects may dominate for small populations.

3. **Payoff-Encodable Fairness:** Fairness constraints can be encoded as equilibrium constraints.
   - *Consequence if violated:* ESS will not satisfy fairness even if stable.

4. **Heterogeneous Capabilities:** Groups have different strategic capabilities but similar utility structures.
   - *Consequence if violated:* Uniform fairness definitions may be inappropriate.

### 1.5 Scope & Boundaries

**Applies to:** Binary classification with strategic agents (credit, hiring, insurance); large populations (n > 1000); settings with observable reputation.

**Does NOT apply to:** Multi-class classification; real-time systems; anonymous interactions; pure adversarial coalitions.

**Limitations:** Discrete strategies lose behavioral nuance; mean-field loses individual effects; reputation requires tracking infrastructure.

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Strategic Robustness):** If classifier boundary is optimized using ESF-MFG with γ ∈ [0.9, 0.99], then honest/improvement strategies will dominate (>90%) at equilibrium.
- *Measurement:* Strategy distribution at equilibrium, n ≥ 30 simulations
- *Success:* p_honest+p_improvement > 90% with p < 0.05

**Secondary Predictions:**
**P2 (Fairness Stability):** Fairness metrics stable (<5% deviation) over 100+ generations.
**P3 (Invasion Resistance):** Gaming strategy driven to extinction (<1%) within 20 generations.

**Falsification Criteria:**
1. Strategic robustness < 70%
2. Core causal links do not operate as proposed
3. Fairness degrades >10% at ESS
4. Gaming strategy invades and persists (>10% after 50 generations)

### 1.8 Statistical Verification Design

- **Sample Size:** n ≥ 30 simulations per configuration
- **Population:** ≥ 1000 agents
- **Generations:** ≥ 100
- **Tests:** Proportion test (P1), paired t-test (P2), survival analysis (P3)
- **Significance:** α = 0.05

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does evolutionary stable behavior emerge in the mean-field game formulation with discrete strategy space under the proposed classifier design?"
- Maps to: Primary prediction (P1)
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the reputation-based indirect reciprocity mechanism the actual cause of fair strategy stabilization?"
- Decomposes into 4 sub-hypotheses (H-M1 through H-M4) for each causal link
- Verification: Ablation studies

**SH3 (Comparison):**
"Does ESF-MFG achieve superior long-term fairness compared to static fairness methods?"
- Baselines: AIF360, Fairlearn, strategic classification without fairness

**Total sub-hypotheses:** 6 (SH1, H-M1 through H-M4, SH3)

### Readiness Checklist

- [x] Hypothesis in scientific format with H0
- [x] Hypothesis ID: H-ESF-MFG-v1
- [x] Confidence: 0.78
- [x] Variables operationalized (8 variables)
- [x] Causal mechanism with evidence (N=4 steps)
- [x] Key tension identified with resolution
- [x] Assumptions with consequences (4)
- [x] Testable predictions (3, primary marked)
- [x] Falsification criteria (4)
- [x] Baselines identified
- [x] SH1/SH2/SH3 ready (6 total)

### Open Questions

1. **Resource Requirements:** ~48-72 hours on medium GPU cluster for full parameter sweep.
2. **Data/Environment:** Start synthetic populations, validate on real fairness datasets.
3. **Priority Order:** Verify SH1 (existence) first as gating criterion.
4. **Norm Configurations:** Test 3-5 social norms from Smit & Santos "leading eight."

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
