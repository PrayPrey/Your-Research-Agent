# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-METAComp-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under conditions of multi-step reasoning tasks (mathematical problem-solving, code generation), if language models are trained with lightweight Compute Value Estimator (CVE) heads using curriculum multi-budget reinforcement learning, then they will achieve reliable test-time compute extrapolation beyond training budgets (2x-10x) while maintaining 40-60% token reduction on easy problems, because the CVE learns to predict expected accuracy improvement from hidden states, enabling instance-aware adaptive stopping/continuation decisions.

**Alternative Hypothesis (H0):**
Learned compute value estimation provides no advantage over entropy-based heuristics (HALT-CoT, EAGER) or fixed budget allocation for test-time compute efficiency and extrapolation. The CVE either fails to learn meaningful value predictions from hidden states, or curriculum training does not enable generalization beyond training budget distributions.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| **CVE Architecture** | Independent | Single linear layer from pooled hidden states → P(improvement \| K additional tokens), ~0.001% parameter overhead | Hidden dim → 1 output, ReLU activation |
| **Curriculum Training Phases** | Independent | Progressive budget ranges: Phase 1 [50-500], Phase 2 [100-1000], Phase 3 [200-2000] tokens | Transition at >80% max-budget performance |
| **CVE Threshold** | Independent | Continue reasoning if P_improve > threshold, query every 50 tokens | θ ∈ {0.2, 0.3, 0.4} |
| **Reward Balance** | Independent | Weight between accuracy reward and efficiency penalty | λ_eff ∈ [0.1, 0.3] |
| **Accuracy at Budget** | Dependent | Pass@1 accuracy on MATH, GSM8K, HumanEval at token budgets B | 0-100% |
| **Token Efficiency** | Dependent | Average tokens per problem: Σ tokens / N_problems | 100-2000 tokens |
| **Extrapolation Coefficient** | Dependent | (Acc@2x_budget - Acc@1x_budget) / (Acc_baseline@2x - Acc_baseline@1x) | Target: >1.0 |
| **CVE Calibration Error** | Dependent | Expected Calibration Error: Σ\|P_predicted - P_actual\| / N_bins | Target: <0.15 |
| **Base Model** | Controlled | Fixed architecture (Llama-3-8B or Qwen-2.5-7B) | Frozen pretrained weights |
| **Training Dataset** | Controlled | MetaMath (math), CodeContests (code) | Fixed train/val/test splits |
| **Random Seeds** | Controlled | Fixed seeds for initialization and sampling | 5 seeds: {42, 123, 456, 789, 1024} |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: CVE learns difficulty features from hidden states
    ↓
Step 2: Curriculum training enables budget-invariant value estimation
    ↓
Step 3: Budget-invariant estimation enables extrapolation beyond training
    ↓
Step 4: Accurate extrapolation → adaptive efficiency + accuracy gains
    ↓
[OUTCOME]: Reliable TTC extrapolation with 40-60% efficiency improvement
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | CLAI (Zhang, 2025) | Hidden states encode cognitive load; 45% token reduction achieved | Strong |
| Step 1 → Step 2 | HALT-CoT (2025) | Entropy from token probabilities reliably signals stopping points | Strong |
| Step 2 → Step 3 | Curriculum Learning Literature | Progressive training enables OOD generalization | Strong |
| Step 2 → Step 3 | e3 (Setlur, 2025) | In-context exploration enables limited TTC extrapolation | Medium |
| Step 3 → Step 4 | REFRAIN (2025) | Adaptive stopping achieves 20-55% token reduction | Strong |
| Step 4 → Outcome | TTC Survey (Alomrani, 2025) | Adaptive methods outperform fixed allocation | Strong |

**Key Tension:**
- **Tension**: HALT-CoT and REFRAIN achieve significant token savings (15-55%) using training-free heuristics, raising the question of whether learned CVE provides sufficient advantage to justify training cost.
- **Resolution**: Our hypothesis targets extrapolation capability, which heuristic methods cannot achieve. The verification plan tests whether CVE provides unique extrapolation benefits beyond efficiency gains achievable by simpler methods.

### 1.4 Key Assumptions

| # | Assumption | Supporting Evidence | Consequence if Violated |
|---|------------|---------------------|------------------------|
| A1 | Compute value is learnable from hidden state representations | CLAI achieves 45% reduction using hidden state features | CVE predictions will be no better than random; hypothesis fails at Step 1 |
| A2 | Curriculum training with progressive budget expansion enables extrapolation | Curriculum learning literature shows OOD generalization; e3 shows limited extrapolation | CVE overfits to training budgets; performance degrades at 2x-10x budgets |
| A3 | Intermediate rewards from self-consistency and step verifiers provide sufficient RL signal | Dense reward RL is more stable than sparse rewards | RL training diverges or produces poorly calibrated CVE |
| A4 | CVE overhead is negligible compared to token generation cost | Single linear layer adds ~0.001% parameters | CVE querying adds significant latency, negating efficiency gains |

### 1.5 Scope & Boundaries

**Applies to:**
- Multi-step reasoning tasks with objective correctness criteria (math, code, formal logic)
- Autoregressive language models with accessible hidden states
- Inference scenarios where token efficiency matters (cost, latency, energy)

**Does NOT apply to:**
- Single-token generation tasks (classification without CoT)
- Creative writing tasks without objective quality metrics
- Black-box API models without hidden state access

**Known Limitations:**
- Extrapolation may plateau beyond 5x training budget
- RL training requires careful hyperparameter tuning
- Requires separate CVE training for different model architectures

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Extrapolation Capability vs SOTA):**
Models trained with CVE + curriculum multi-budget RL will achieve accuracy improvement at 2x-10x training budget that exceeds fixed-budget baselines and entropy-based methods (HALT-CoT, EAGER).

*Measurement*: Extrapolation coefficient > 1.0 with p < 0.05
*Statistical test*: Paired t-test, n ≥ 25 runs
*Falsification*: Extrapolation coefficient ≤ 0.0

**Secondary Predictions:**

**P2 (Efficiency on Easy Problems):**
CVE-guided early stopping will achieve 40-60% token reduction on problems where baseline solves within 200 tokens, while maintaining accuracy within 1 percentage point.

**P3 (CVE Calibration):**
CVE predictions will be well-calibrated: Expected Calibration Error (ECE) < 0.15 across all budget ranges.

**P4 (Ablation - Curriculum Necessity):**
Removing curriculum (training with fixed budget only) will cause extrapolation failure at 2x budget.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Extrapolation coefficient ≤ 0.0 at 2x training budget
2. **Mechanism Failure**: CVE calibration ECE > 0.25
3. **Comparative Failure**: CVE shows no advantage over HALT-CoT on both efficiency AND extrapolation
4. **Training Failure**: RL training diverges after 3 hyperparameter attempts

### 1.7 SOTA Baseline

| Method | Token Reduction | Extrapolation | Training Required |
|--------|-----------------|---------------|-------------------|
| HALT-CoT (2025) | 15-30% | None | No |
| REFRAIN (2025) | 20-55% | None | No |
| EAGER (Scalena) | ~30% | Limited | No |
| Fixed Budget | 0% | None | No |
| **Our Target** | **40-60%** | **2x-10x** | **Yes** |

### 1.8 Statistical Verification Design

**Sample Size**: n ≥ 25 runs per condition (Cohen's d = 0.5, power = 0.8)
**Statistical Test**: Paired t-test with Bonferroni correction
**Report Format**: Mean ± Std, 95% CI, Cohen's d, p-value
**Reproducibility**: 5 random seeds, code/data/checkpoints released

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Can a lightweight linear CVE head learn to predict compute value (P(improvement|K tokens)) from LLM hidden states with ECE < 0.15?"

- Maps to: P3 (CVE Calibration)
- Verification type: Empirical training + calibration measurement
- Critical: MUST PASS - foundation for all other claims

**SH2 (Mechanism - 4 sub-hypotheses):**
"Does the proposed 4-step causal mechanism operate as specified?"

- H-M1: Hidden states encode difficulty features extractable by CVE
- H-M2: Curriculum training prevents budget overfitting
- H-M3: Budget-invariant estimation enables extrapolation
- H-M4: Adaptive protocol achieves both efficiency and accuracy gains

**SH3 (Comparison):**
"Does CVE+Curriculum outperform baselines (HALT-CoT, REFRAIN, EAGER, Fixed) on extrapolation coefficient and efficiency metrics?"

- Maps to: P1 (Primary), P2 (Efficiency)
- Verification type: Comparative empirical

**Total Sub-Hypotheses:** 2 + 4 = 6

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-METAComp-v1
- [x] Confidence level: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized with evidence
- [x] Causal mechanism with N=4 steps, evidence table complete
- [x] Key tension identified with resolution
- [x] Assumptions with violation consequences
- [x] 4 testable predictions with P1 primary
- [x] Falsification criteria defined (4 conditions)
- [x] Baselines identified: HALT-CoT, REFRAIN, EAGER, Fixed
- [x] SH1, SH2, SH3 starting points clear

### Open Questions

1. **Resource Requirements:** Estimate 8-16 GPU-hours on A100 for 8B model curriculum RL training. Needs verification.

2. **Data Availability:** MetaMath + CodeContests may need augmentation with synthetic difficulty-controlled problems.

3. **Priority Order:** Start with SH1 (CVE learnability) as gate - early, cheap failure detection.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work (8 sources with DOIs/URLs)

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
