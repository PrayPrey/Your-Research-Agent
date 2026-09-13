# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-RSA-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under standard LLM inference conditions with safety steering capability, if a learned Regulatory Head outputs continuous suppression strength s(context) ∈ [0,1] to modulate a Safety Effector Head's steering vector, then over-refusal rate will decrease while maintaining harmful content rejection rate, because the continuous modulation enables context-aware calibration that distinguishes true threats from benign edge cases (inspired by immune peripheral tolerance where Regulatory T-cells provide context-dependent suppression).

**Alternative Hypothesis (H0):**
Continuous suppression modulation provides no significant advantage over binary safety activation (SafeSwitch) or static steering (Category-wise). The additional complexity of learning suppression strength does not translate to meaningful improvements in the safety-utility tradeoff.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Suppression strength s(context) | Independent | Continuous scalar output [0,1] from Regulatory Head based on context embedding from layer L | s ∈ [0,1]; s=0 full safety intervention, s=1 no intervention |
| Over-refusal rate | Dependent | Percentage of benign prompts incorrectly refused, measured on OR-Bench (80K prompts) | Target: <30% (vs SafeSwitch 48%) |
| Harmful content rate | Dependent | Percentage of harmful prompts not blocked, measured on ToxicChat/SafetyBench | Target: ≤20% (maintain SafeSwitch level) |
| Response utility | Dependent | Quality score on MT-Bench, response informativeness | Target: ≥7.0/10 |
| Calibration accuracy | Dependent | Correlation between s(context) and actual safety relevance | Target: Spearman ρ > 0.6 |
| Base LLM | Controlled | Fixed pretrained model | Llama-3-8B or Mistral-7B |
| Safety steering vector | Controlled | Pre-computed using Category-wise Safety Steering method | Fixed per safety category |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Context Extraction
   ↓
[Intermediate LLM representations at layer L encode safety-relevant context]
   ↓
Step 2: Regulatory Processing
   ↓
[Regulatory Head processes context embedding → outputs s(context) ∈ [0,1]]
   ↓
Step 3: Modulation
   ↓
[s(context) × Safety_Steering_Vector = Calibrated_Intervention]
   ↓
Step 4: Integration
   ↓
[Base_LLM_Output + Calibrated_Intervention = Final_Response]
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | SafeSwitch (Han et al., 2025) | Internal state monitoring successfully detects harmful intentions via probing | Strong |
| Step2 → Step3 | Style Vectors (Konen et al., 2024), Conceptors (Postmus & Abreu, 2024) | Continuous control over LLM behavior via learned activation modulation | Strong |
| Step3 → Step4 | Category-wise Steering (Bhattacharjee et al., 2024) | Safety steering vectors effectively modify model outputs at inference | Strong |
| Step4 → Outcome | Tradeoff Analysis (Wolf et al., 2024) | Demonstrates quadratic helpfulness harm with linear safety gain | Medium |

**Key Tension:**
SafeSwitch demonstrates internal state monitoring works (80% harmful content reduction) but uses binary activation (48% over-refusal). Category-wise Steering shows fine-grained control but uses static strength. RSA bridges these by combining internal monitoring with continuous (not binary) modulation, learning context-specific suppression.

### 1.4 Key Assumptions

1. **Context Extractability:** Intermediate LLM representations encode safety-relevant context
   - If violated: Regulatory head receives uninformative input → random suppression values

2. **Suppression Learnability:** Regulatory head can learn via constrained RL without ground-truth labels
   - If violated: Training instability → suppression doesn't correlate with safety relevance

3. **Weak Supervision Sufficiency:** Constrained optimization produces effective policies
   - If violated: Need explicit labels (Data Mirage returns) → practical deployment blocked

4. **Generalization:** Learned policies transfer to novel domains
   - If violated: RSA works only in-distribution → limited practical value

5. **Safety Classifier Reliability:** Existing classifiers provide reliable training signals
   - If violated: Noisy training → suboptimal suppression learning

6. **Steering Vector Effectiveness:** Pre-computed vectors provide sufficient intervention capability
   - If violated: Perfect suppression learning still can't produce safe outputs

### 1.5 Scope & Boundaries

**Applies to:** Text-based transformer LLMs, open-weight models, harmful content mitigation

**Does NOT Apply to:** Closed API models, non-text modalities, privacy/fairness challenges, certified adversarial robustness

**Limitations:** Constrained RL hyperparameter sensitivity, probabilistic robustness, limited interpretability

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Over-Refusal Reduction):**
RSA will achieve over-refusal rate < 35% on OR-Bench while maintaining harmful content rate ≤ 20% on ToxicChat.

*Measurement:* McNemar's test, n ≥ 1000 prompts, p < 0.05
*Falsification:* Over-refusal ≥ 45% OR Harmful rate > 25%

**Secondary Predictions:**

**P2 (Suppression Calibration):** s(context) correlates with human-judged safety relevance (Spearman ρ > 0.6)

**P3 (Utility Preservation):** MT-Bench score ≥ 7.0/10

**P4 (Efficiency):** Parameter overhead ≤ 6%

**Falsification Criteria:**
1. Over-refusal ≥ 45% (no improvement over SafeSwitch)
2. Harmful rate > 25% (safety regression)
3. Calibration ρ < 0.3 (mechanism failure)
4. MT-Bench < 6.0 (utility collapse)
5. No significant advantage over SafeSwitch on any metric

### 1.7 Statistical Verification Design

**Sample Size:** n ≥ 1000 prompts, power = 0.8, α = 0.05
**Tests:** McNemar's (proportions), Spearman (calibration), paired t-test (utility)
**Correction:** Bonferroni (α' = 0.0125)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does the Regulatory Head successfully learn to output meaningful suppression strengths s(context) ∈ [0,1] that correlate with context safety relevance?"
- Success criterion: Spearman ρ > 0.6
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is the 4-step causal chain the actual mechanism producing improved safety-utility tradeoff?"
- Decomposes into: H-M1 (context), H-M2 (regulatory), H-M3 (modulation), H-M4 (integration)

**SH3 (Comparison):**
"Does RSA achieve significant improvement over SafeSwitch?"
- Success criterion: Over-refusal < 35%, Harmful ≤ 20%

**Total Sub-Hypotheses:** 6 (1 + 4 + 1)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-RSA-v1
- [x] Confidence: 0.78
- [x] H0 defined
- [x] Variables operationalized
- [x] Causal mechanism with evidence (N=4 steps)
- [x] Key tension identified
- [x] Assumptions with consequences
- [x] 4 testable predictions (primary marked)
- [x] 5 falsification criteria
- [x] Baselines: SafeSwitch, Category-wise, Base LLM
- [x] SH1, SH2, SH3 defined

### Open Questions

1. **Resources:** 4-8 A100 GPU-hours, ~50K prompts, 3-4 weeks total
2. **Technical:** Constrained RL algorithm selection, Regulatory head architecture, Target layer
3. **Priority:** SH1 → SH2 → SH3 (existence must pass first)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
