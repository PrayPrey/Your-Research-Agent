# Verification Plan: Bidirectional Alignment Training

**Date:** 2026-08-28
**Hypothesis ID:** H-BiAlign-v1
**Confidence:** 0.75
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under standard RLHF fine-tuning conditions, if we augment the helpfulness reward with IFEval-derived controllability signals (R_combined = α·R_AlpacaEval + β·R_IFEval_rate), then the resulting model will achieve higher held-out instruction-following scores, maintain helpfulness, AND improve safety benchmark performance, because explicit constraint training builds general constraint-following capacity that transfers to implicit safety constraints.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in held-out IFEval scores, AlpacaEval performance, or safety benchmark scores (TruthfulQA, BBQ) between models fine-tuned with bidirectional (helpfulness + controllability) signals versus unidirectional (helpfulness-only) signals.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | IFEval + Alpaca + UltraFeedback (standard) | IFEval provides controllability signal; UltraFeedback provides RLHF preference pairs |
| **Model** | Llama-3-8B-Instruct | Standard size for RLHF experiments; well-documented baseline performance |

**Dataset Details:**
- Source: HuggingFace datasets
- Path: google/IFEval, tatsu-lab/alpaca_eval, openbmb/UltraFeedback

**Model Details:**
- Type: instruction-tuned LLM
- Source: meta-llama/Meta-Llama-3-8B-Instruct

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| B1: SFT-only | Baseline instruction-following | Instruction data |
| B2: AlpacaEval RLHF | Standard RLHF helpfulness | Human preference |
| B3: Quality-only RLHF | Quality without instruction adherence | Preference pairs |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | IFEval constraint satisfaction rate is valid proxy for controllability | IFEval designed to measure instruction-following; rule-based verification is objective | Training signal doesn't capture true controllability |
| A2 | AlpacaEval and IFEval measure orthogonal constructs | AlpacaEval uses GPT-4 quality judgment; IFEval uses rule-based constraint checking | Signals are redundant; combined training provides no benefit |
| A3 | Explicit constraint training transfers to implicit constraint adherence | Constitutional AI showed explicit safety training improves implicit harmlessness | Safety benchmarks won't improve; P3 fails |
| A4 | 70/30 IFEval split avoids memorization | Standard train/test split; held-out instructions are unseen during training | IFEval_test improvements reflect memorization, not generalization |
| A5 | Optimal α/β exists on Pareto frontier | Multi-objective optimization theory guarantees Pareto solutions | All trade-offs are sharp; no configuration achieves P1+P2+P3 |

### 1.6 Research Gap & Novelty

**Key Innovation:** First empirical test of bidirectional alignment training signals using IFEval constraint satisfaction rate as a differentiable training reward alongside helpfulness.

**Differentiation:**
- InstructGPT (Ouyang 2022): Uses helpfulness-only RLHF; no explicit controllability signal
- Sun et al. 2024: Provides theory without training methodology; we implement and test
- Constitutional AI (Bai 2022): Uses AI self-critique for safety; we use human-defined constraints

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: IFEval Constraint Satisfaction as Differentiable Reward**

**Statement**: Under RLHF training setup, if IFEval constraint satisfaction rate is computed as a continuous reward signal, then it can serve as a differentiable training objective, because expected value of binary constraint satisfaction provides a valid gradient signal.

**Rationale**: This validates the foundational premise that IFEval-style constraints can be incorporated into RLHF training. Without this, the entire bidirectional approach is not implementable.

**Variables**:
- Independent: IFEval constraint formulation (binary vs rate)
- Dependent: Gradient validity and training stability
- Controlled: Base model, training infrastructure

**Verification Protocol**:
1. Implement IFEval constraint satisfaction rate computation
2. Verify gradient flow through reward model
3. Confirm training stability over 100 PPO steps
4. Measure correlation between rate and actual constraint satisfaction

**Success Criteria (PoC: Direction-based)**:
- Primary: IFEval rate correlates with instruction-following (r > 0.5)
- Secondary: Training loss decreases stably

**Failure Response**:
- IF fails: PIVOT to alternative controllability metrics

**Dependencies**: None

**Source**: Phase 2A SH1, Causal Step 1

---

---
**H-M1: Combined Reward Optimization via PPO**

**Statement**: Under standard PPO training, if combined reward R = α·R_helpfulness + β·R_controllability is used, then the model can be optimized without divergence or reward hacking, because multi-objective RL with weighted rewards is mathematically sound.

**Rationale**: Tests whether the combined reward function can be practically optimized. This is the core training methodology.

**Variables**:
- Independent: Reward combination weights (α, β)
- Dependent: Training convergence, reward trajectories
- Controlled: PPO hyperparameters, base model

**Verification Protocol**:
1. Configure trl PPOTrainer with custom reward function
2. Run training with α=0.5, β=0.5 baseline
3. Monitor reward trajectories for both components
4. Check for reward hacking indicators (reward vs actual performance)

**Success Criteria (PoC: Direction-based)**:
- Primary: Both reward components improve during training
- Secondary: No divergence over 1000 PPO steps

**Failure Response**:
- IF fails: EXPLORE alternative optimization schemes (DPO, IPO)

**Dependencies**: H-E1

**Source**: Phase 2A Causal Step 2

---

---
**H-M2: Explicit Constraint Learning**

**Statement**: Under bidirectional training, if the model is trained with IFEval rewards, then it learns to satisfy explicit constraints (format, length, structure), because reward-maximizing behavior should align with constraint satisfaction.

**Rationale**: Validates that the training signal actually improves the target capability. This is the first measurable outcome.

**Variables**:
- Independent: Training with vs without IFEval reward
- Dependent: Held-out IFEval strict accuracy
- Controlled: Training compute, evaluation protocol

**Verification Protocol**:
1. Train model with combined reward (T1 configuration)
2. Evaluate on held-out IFEval test split (30%)
3. Compare against B1, B2, B3 baselines
4. Analyze constraint type breakdown (format vs length vs content)

**Success Criteria (PoC: Direction-based)**:
- Primary: IFEval_test improves over baselines
- Secondary: Improvement consistent across constraint types

**Failure Response**:
- IF fails: EXPLORE constraint-specific analysis, weight tuning

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 3, Prediction P1

---

---
**H-M3: Helpfulness Maintenance**

**Statement**: Under bidirectional training with combined reward, if α is set appropriately (α ≥ 0.4), then the model maintains helpfulness as measured by AlpacaEval, because sufficient weight on helpfulness prevents degradation.

**Rationale**: Ensures the controllability signal doesn't sacrifice the primary alignment goal. This tests the "AND" claim.

**Variables**:
- Independent: α/β weight ratio
- Dependent: AlpacaEval win rate
- Controlled: Base model, evaluation methodology

**Verification Protocol**:
1. Evaluate T1-T4 configurations (α ∈ {0.2, 0.4, 0.6, 0.8}) on AlpacaEval
2. Compare against B2 (helpfulness-only RLHF)
3. Identify α threshold for ≥95% B2 performance
4. Plot Pareto frontier (IFEval vs AlpacaEval)

**Success Criteria (PoC: Direction-based)**:
- Primary: Best Ti achieves AlpacaEval ≥ 0.95 × B2
- Secondary: Clear Pareto frontier identified

**Failure Response**:
- IF fails: Document as fundamental trade-off

**Dependencies**: H-M2

**Source**: Phase 2A Prediction P2

---

---
**H-M4: Explicit-to-Implicit Constraint Transfer**

**Statement**: Under bidirectional training, if the model learns explicit constraint satisfaction (IFEval), then it also improves on implicit safety constraints (TruthfulQA, BBQ), because explicit constraint training builds general constraint-following capacity.

**Rationale**: This is the key mechanism claim and novelty. Validates the theoretical framework of bidirectional alignment.

**Variables**:
- Independent: Bidirectional vs unidirectional training
- Dependent: Safety benchmark scores (TruthfulQA, BBQ)
- Controlled: Training compute, base model

**Verification Protocol**:
1. Run lm-eval-harness on TruthfulQA and BBQ for all conditions
2. Compare T1-T4 against B1, B2, B3
3. Test for statistical significance (two-tailed t-test, α=0.05)
4. Analyze correlation between IFEval improvement and safety improvement

**Success Criteria (PoC: Direction-based)**:
- Primary: At least one Ti improves ≥2pp on TruthfulQA OR BBQ vs max(baselines)
- Secondary: Positive correlation between IFEval and safety gains

**Failure Response**:
- IF fails: Document limitation; explicit≠implicit transfer may not hold

**Dependencies**: H-M3

**Source**: Phase 2A Causal Step 4, Prediction P3

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | IFEval rate is differentiable and correlates | STOP - approach not viable |
| H-M1 | MUST_WORK | PPO training converges with combined reward | PIVOT to alternative optimization |
| H-M2 | SHOULD_WORK | IFEval_test improves over baselines | Document limitation |
| H-M3 | SHOULD_WORK | AlpacaEval ≥ 95% of B2 | Document trade-off |
| H-M4 | SHOULD_WORK | Safety benchmark improvement ≥2pp | Document as open question |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks |

**Total Duration:** 7 weeks

---

## 4. Risk Analysis

### 4.1 Risk Identification

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | IFEval rate doesn't capture true controllability | A1 | High | H-E1, H-M1 | Validate with manual analysis, consider alternative metrics |
| R2 | Signals are redundant; no benefit from combination | A2 | Medium | H-M1-4 | Measure correlation between signals, orthogonality test |
| R3 | Explicit→implicit transfer doesn't occur | A3 | High | H-M4 | Document as limitation if P3 fails |
| R4 | IFEval memorization confounds results | A4 | Medium | H-M2 | Verify with novel constraint formulations |
| R5 | No Pareto-optimal configuration exists | A5 | Medium | H-M3 | Full frontier sweep, accept trade-off if necessary |

### 4.2 Mitigation Strategies

**R1 (High - IFEval validity):**
- Prevention: Manual validation of IFEval rate on sample outputs
- Detection: Low correlation between rate and actual compliance
- Response: PIVOT to alternative controllability metrics (e.g., rule-based checkers)

**R2 (Medium - Signal redundancy):**
- Prevention: Orthogonality analysis before training
- Detection: High correlation (r > 0.8) between AlpacaEval and IFEval
- Response: Document as finding; single signal may suffice

**R3 (High - Transfer failure):**
- Prevention: Constitutional AI analogy provides theoretical support
- Detection: No safety improvement despite IFEval gains
- Response: Document as limitation; explicit≠implicit may not hold

**R4 (Medium - Memorization):**
- Prevention: 70/30 split, held-out instructions never seen
- Detection: Perfect IFEval_test with random content failures
- Response: Use novel constraint formulations for validation

**R5 (Medium - No Pareto solution):**
- Prevention: Full α sweep (0.2 to 0.8)
- Detection: All configurations show sharp trade-offs
- Response: Accept trade-off, report Pareto frontier

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1-4 - Mechanisms]
    H-M1 ← H-E1 (Combined reward optimization)
         │
         ▼
    H-M2 ← H-M1 (Explicit constraint learning)
         │
         ▼
    H-M3 ← H-M2 (Helpfulness maintenance)
         │
         ▼
    H-M4 ← H-M3 (Explicit→implicit transfer)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 5.2 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2 │ W3-4 │ W5 │ W6 │ W7
─────────────────┼──────┼──────┼────┼────┼────
PHASE 1: Foundation
  H-E1           │██████│      │    │    │
  [Gate 1]       │      │◆     │    │    │
─────────────────┼──────┼──────┼────┼────┼────
PHASE 2: Mechanisms
  H-M1           │      │██████│    │    │
  H-M2           │      │      │████│    │
  H-M3           │      │      │    │████│
  H-M4           │      │      │    │    │████
  [Gate 2]       │      │      │    │    │   ◆
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.3 Critical Path Analysis

- **Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4
- **Total Duration:** 7 weeks (2 + 2 + 1 + 1 + 1)
- **Slack:** 0 weeks (all sequential)

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Bidirectional alignment (helpfulness + controllability) produces superior models.

**Supporting Evidence:**
1. IFEval constraint satisfaction rate is a valid differentiable proxy (Prof. Pax validation)
2. Multi-objective RL with weighted rewards is mathematically sound
3. Constitutional AI demonstrated explicit→implicit transfer for safety

**Strengths:**
- Clear causal mechanism with 4 testable steps
- Three quantitative predictions (P1, P2, P3)
- Builds on established RLHF methodology

### 6.2 Antithesis

**Null Hypothesis (H0):** No significant difference between bidirectional and unidirectional fine-tuning.

**Counter-Arguments:**
1. IFEval and AlpacaEval may not be truly orthogonal
2. Explicit constraint learning may not transfer to implicit constraints
3. Safety benchmarks (TruthfulQA, BBQ) may be partially saturated

**Conditions for H0 Support:**
- All Ti ≤ max(B1, B2, B3) on IFEval_test
- All Ti < 0.95 × B2 on AlpacaEval
- No Ti shows ≥2pp improvement on safety benchmarks

### 6.3 Synthesis

The verification plan resolves this dialectic through sequential hypothesis testing:

1. **H-E1 establishes viability** before investing in full training
2. **H-M1-M2 validate the core mechanism** (combined training improves IFEval)
3. **H-M3 tests the "AND" claim** (helpfulness maintained)
4. **H-M4 tests the key novelty** (explicit→implicit transfer)

**Nuanced Outcomes:**
- **Full Support:** All gates pass → Thesis validated
- **Partial Support:** H-M4 fails but H-M1-M3 pass → Bidirectional works for controllability, not safety
- **No Support:** H-E1 or H-M1 fails → Approach not viable as designed

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | IFEval rate is valid reward | May not capture true controllability | H-E1 validation |
| Mechanism | Combined training works | May diverge or hack | H-M1 convergence test |
| Maintenance | Helpfulness preserved | May degrade | H-M3 Pareto analysis |
| Transfer | Explicit→implicit | May not generalize | H-M4 safety benchmarks |

**Overall Robustness:** Medium-High (well-structured verification, key uncertainty in H-M4)

---

## 7. Executive Summary & Conclusions

### Executive Summary

**Main Hypothesis:** Bidirectional alignment (helpfulness + controllability) via combined RLHF reward
- ID: H-BiAlign-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4)
- Phases: 2 phases over 7 weeks
- Critical Gates: 2 decision points (Gate 1: Foundation, Gate 2: Mechanisms)

**Risk Assessment:** Medium
- Primary concerns: IFEval validity (R1), explicit→implicit transfer (R3)

**Immediate Action:** Begin Phase 1 with H-E1 (IFEval reward validation)

### Key Achievements

- 5 hypotheses across 2 phases with clear verification protocols
- H0 addressed through dialectical analysis
- Scope reduction: 60% (BUILD_ON claims excluded)

### Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: Validate IFEval constraint satisfaction as differentiable reward
- Gate 1: MUST PASS

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1: Combined reward optimization (2 weeks)
- H-M2: Explicit constraint learning (1 week)
- H-M3: Helpfulness maintenance (1 week)
- H-M4: Explicit→implicit transfer (1 week)
- Gate 2: H-M1 must pass

### Critical Decision Points

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, IFEval rate not viable as training signal
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - FAIL → PIVOT to alternative optimization (DPO, IPO)
   - H-M2-M4 failures → Document as limitations

### Open Questions

- Optimal α/β ratio — resolved via Pareto sweep
- Whether explicit→implicit transfer occurs — tested via P3
- Reward hacking risk — mitigated via minimum helpfulness constraint

### Recommendations

1. **Immediate Actions:**
   - Start Phase 1 with H-E1
   - Set up lm-eval-harness for consistent evaluation

2. **Resource Allocation:**
   - Allocate 7 weeks for critical path
   - Reserve buffer for potential failures

3. **Failure Management:**
   - Document all failures with analysis
   - Execute PIVOT strategies as defined

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-BiAlign-v1)

### B. Scope Reduction Summary
- BUILD_ON claims (60%): RLHF methodology, IFEval benchmark, multi-objective RL
- PROVE_NEW claims (40%): Bidirectional training effect, controllability→safety transfer

### C. Established Facts Registry
| Claim | Status | Evidence |
|-------|--------|----------|
| RLHF with helpfulness rewards improves model alignment | BUILD_ON | Ouyang et al. 2022 |
| IFEval measures instruction-following accuracy | BUILD_ON | Zhou et al. 2023 |
| Multi-objective RL with weighted rewards is mathematically valid | BUILD_ON | Standard Pareto optimization |
| Bidirectional training improves over unidirectional | PROVE_NEW | Sun et al. 2024 (theory only) |
| Controllability training improves safety benchmark performance | PROVE_NEW | Hypothesized mechanism |
