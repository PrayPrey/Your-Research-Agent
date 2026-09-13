# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - AI-HXMARL)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-AI-HXMARL-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions of multi-agent financial trading with regulatory compliance requirements (EU AI Act, MiFID II), if agents are equipped with Active Inference-based generative world models that decompose decisions via expected free energy minimization, then the system will produce inherently explainable decisions at three hierarchical levels (agent, interaction, system) because the expected free energy naturally decomposes into interpretable pragmatic (exploitation) and epistemic (exploration) components that can be traced through precision-weighted belief propagation.

**Alternative Hypothesis (H0):**
Active Inference-based agents do not provide significantly better explainability than post-hoc explanation methods (SHAP/LIME) applied to standard RL agents (PPO/DQN), OR the computational overhead of Active Inference makes real-time trading infeasible, OR compliance officers cannot interpret free energy-based explanations even when translated to financial terminology.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Agent Architecture | Independent | Active Inference agent vs standard RL agent (PPO/DQN baseline) | Binary: AI vs RL |
| Explanation Granularity | Independent | Three levels: agent-level (free energy decomposition), interaction-level (belief propagation traces), system-level (collective free energy landscape) | 3 levels |
| Number of Agents | Independent | Agent count in market simulation | 10-50 (initial), 100+ (scale) |
| Audit Trail Completeness | Dependent | Percentage of decisions with complete causal trace | Target: >90% vs <30% baseline |
| Operator Trust | Dependent | Compliance officer trust scores via standardized questionnaire | Target: 50%+ improvement |
| Trading Performance | Dependent | Sharpe ratio relative to non-explainable baselines | Within ±5% |
| Explanation Fidelity | Dependent | Counterfactual consistency score | 0.0-1.0 (target: >0.85) |
| Market Environment | Controlled | Trading frequency and data source | Daily trading, public LOB data |
| Compute Resources | Controlled | GPU infrastructure | Standard 8-GPU cluster |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Agent uses Active Inference
    ↓ (Free energy minimization)
Step 2: Expected free energy decomposed
    ↓ (Pragmatic + Epistemic separation)
Step 3: Decomposition logged
    ↓ (State-action explanations)
Step 4: Inter-agent beliefs traced
    ↓ (Precision-weighted propagation)
Outcome: Hierarchical 3-level explanations + Regulatory audit trail
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Da Costa et al. 2024 (Active Inference) | "Behavior follows as explainable mixture of exploration and exploitation under generative world model" | Strong |
| Step2 → Step3 | Da Costa et al. 2024 | Free energy decomposition is mathematically defined and computationally tractable via variational inference | Strong |
| Step3 → Step4 | XRL-Bench 2024, Gyevnar & Towers 2025 | State-importance explanations can be evaluated with objective behavioral metrics | Medium |
| Step4 → Outcome | XGate 2025 (Jin et al.) | Explainable RL achieved 67% trust improvement, 41% faster intervention | Strong |

**Key Tension:**
- **Tension:** Da Costa et al. (2024) establishes Active Inference theory for single agents, but multi-agent interaction tracing (Step 4) lacks direct precedent in financial systems. XGate (2025) validates trust improvement for XRL but in IoT traffic management, not financial trading.
- **Resolution:** This verification plan tests whether the trust improvement translates to financial domain and whether inter-agent tracing maintains fidelity at scale (10-50 agents).

### 1.4 Key Assumptions

| # | Assumption | Supporting Evidence | Consequence if Violated |
|---|------------|---------------------|------------------------|
| A1 | Variational inference provides sufficiently accurate approximation for financial decision-making | Da Costa 2024: "theoretically possible to rewrite any RL algorithm conforming to descriptive assumptions" | Free energy computations become meaningless; agents make poor decisions |
| A2 | Expected free energy decomposition maps meaningfully to regulatory concepts (risk/reward/uncertainty) | Conceptual mapping; needs stakeholder validation | Explanations are technically correct but incomprehensible to compliance officers |
| A3 | Precision-weighted belief propagation can be logged without prohibitive overhead | JaxMARL-HFT 2025: 240x speedup provides computational headroom | Trade-off forced between explainability completeness and trading latency |
| A4 | Compliance officers can interpret translated free energy explanations | XGate 2025: 67% trust improvement suggests XRL explanations are interpretable | Requires additional explanation layer or simplification; may reduce explanation fidelity |

### 1.5 Scope & Boundaries

**Where Hypothesis APPLIES:**
- Multi-agent trading systems (2-100 agents)
- Daily/hourly trading frequency (not HFT initially)
- Markets requiring regulatory compliance (EU AI Act, MiFID II)
- Scenarios where audit trails are mandatory
- Research environments with access to public market data (LOB)

**Where Hypothesis does NOT APPLY:**
- Ultra-low-latency HFT (microsecond decisions) - computational overhead too high
- Single-agent trading systems - hierarchical explanation structure not needed
- Non-financial multi-agent systems (without adaptation)
- Markets without explainability requirements

**Known Limitations:**
- Active Inference computational overhead may limit real-time applicability
- Regulatory acceptance of free energy explanations is unvalidated
- Scalability beyond 100 agents requires approximate tracing (O(N log N))
- Requires translation layer for non-technical stakeholders

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Audit Trail Completeness):**
Active Inference-based agents will achieve >90% audit trail completeness (percentage of decisions with complete causal trace from input → free energy decomposition → action), compared to <30% for post-hoc SHAP explanations applied to standard RL agents.

*Measurement*:
- Audit trail completeness > 90% with p < 0.05
- Statistical test: Chi-squared test for proportions, n ≥ 30 trading sessions

*Basis*:
Post-hoc methods (SHAP) provide feature importance but not causal traces. Active Inference inherently logs the decision process.

*Success Criteria for Phase 2B*:
- Primary: Completeness > 90% (p < 0.05)
- Falsification: Completeness ≤ 50% triggers rejection

**Secondary Predictions:**

**P2 (Operator Trust Improvement):**
Compliance officers (n ≥ 15) will report ≥50% trust improvement when using AI-HXMARL explanations compared to SHAP baselines, measured via standardized trust questionnaire.

**P3 (Performance Preservation):**
Trading performance (Sharpe ratio) will remain within ±5% of non-explainable MARL baselines (JaxMARL-HFT PPO), demonstrating that explainability does not sacrifice performance.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Audit trail completeness ≤ 50%
2. **Mechanism Failure**: Free energy decomposition cannot distinguish pragmatic vs epistemic components in >80% of decisions
3. **Performance Failure**: Sharpe ratio degrades >10% compared to baseline
4. **Trust Failure**: Compliance officer trust improvement <25%

### 1.7 SOTA Baseline (Not Applicable)

This hypothesis focuses on **explainability quality** (a novel capability) rather than **performance improvement** over SOTA. No SOTA performance benchmark applies because no existing system provides hierarchical multi-agent explanations for financial trading.

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's h for proportions): 0.8 (large effect: 90% vs 30%)
- Required sessions: n ≥ 30 trading sessions
- Statistical power: 0.8

**Test Specification:**
| Prediction | Test | Sample | Significance |
|------------|------|--------|--------------|
| P1 (Completeness) | Chi-squared | n ≥ 30 sessions | α = 0.05 |
| P2 (Trust) | Paired t-test | n ≥ 15 officers | α = 0.05 |
| P3 (Performance) | Equivalence test | n ≥ 20 runs | TOST, δ = 5% |

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does Active Inference-based decision-making produce complete audit trails (>90% completeness) in multi-agent trading environments?"
- Maps to: Primary prediction P1
- Verification type: Empirical measurement
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism) - Will decompose into 4 sub-hypotheses (H-M1 to H-M4):**
"Is expected free energy decomposition the actual mechanism producing explainable decisions?"
- Maps to: Causal chain (4 steps)
- Verification type: Causal analysis
- Sub-hypotheses:
  - H-M1: Active Inference → Free energy computation (variational inference accuracy)
  - H-M2: Free energy → Pragmatic/Epistemic decomposition (separation quality)
  - H-M3: Decomposition → Agent explanations (logging fidelity)
  - H-M4: Agent explanations → Interaction traces (scalability)

**SH3 (Comparison):**
"Does AI-HXMARL provide better explainability than post-hoc SHAP while maintaining trading performance?"
- Maps to: P2 (trust) and P3 (performance)
- Verification type: Comparative empirical
- Critical: Determines practical value vs existing methods

**Total sub-hypotheses in Phase 2B:** 6 (1 + 4 + 1)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-AI-HXMARL-v1
- [x] Confidence level specified: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (4 steps)
- [x] Causal chain length (N=4) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 defined, P1 marked primary)
- [x] Falsification criteria are defined (4 criteria)
- [x] Baselines identified: SHAP/LIME on MASA, JaxMARL-HFT PPO
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** What is the actual computational overhead of Active Inference vs PPO in JaxMARL-HFT environment? Estimate: 20-50% additional compute per decision.

2. **Data Availability:** Can we access sufficient LOB data for validation? JaxMARL-HFT used 400M orders (1 year); similar dataset needed.

3. **Stakeholder Access:** Can we recruit 15+ compliance officers for trust study? May require industry partnership.

4. **Priority Order:** Recommend SH1 (existence) first → H-M1/H-M2 (core mechanism) → SH3 (comparison) → H-M3/H-M4 (scaling).

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
