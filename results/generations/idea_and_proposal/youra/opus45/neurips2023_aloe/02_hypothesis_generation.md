# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-ZPD-CCR-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under self-training conditions with verifiable tasks, if LLM training examples are selected based on Confidence-Calibrated Regret (CCR) scores that identify the Zone of Proximal Development boundary, then learning efficiency will improve compared to random sampling because high-CCR examples represent the optimal difficulty frontier where learning signal is maximized.

**Alternative Hypothesis (H0):**
CCR-based curriculum selection provides no significant improvement in learning efficiency over random sampling, and the confidence-correctness relationship does not meaningfully identify optimal training examples for LLM self-improvement.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| CCR Score | Independent | CCR(x) = α × confidence(x) × (1 - correctness(x)) + β × (1 - confidence(x)) × correctness(x), where confidence is calibrated verbalized confidence + token probability | 0.0 - 1.0 (higher = more informative) |
| Learning Efficiency | Dependent | Performance improvement per training example: Δaccuracy/N_examples on held-out test set | 0.01 - 0.5% per 1000 examples |
| Task Domain | Controlled | Mathematical reasoning (GSM8K, MATH) or code generation (HumanEval, MBPP) with executable verification | Categorical: {math, code} |
| Model Size | Controlled | Open-source LLMs with 7B-8B parameters | {Llama-3-8B, Mistral-7B} |
| Confidence Calibration Quality | Confounding | Expected Calibration Error (ECE) after ConfTuner-style calibration | ECE < 0.15 required |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Calibration
    ↓
Step 2: CCR Computation → ZPD Boundary Identification
    ↓
Step 3: ZPD Boundary Training → Maximized Learning Signal
    ↓
Step 4: Maximized Learning Signal → Improved Efficiency
    ↓
Outcome: Better Learning Efficiency than Random Sampling
```

**Step-by-Step Mechanism:**

1. **Step 1 (Calibration → Reliable CCR):** ConfTuner-style calibration reduces Expected Calibration Error (ECE), making confidence estimates meaningful for curriculum selection.

2. **Step 2 (CCR Computation → ZPD Identification):** High CCR scores identify examples where model is "confidently wrong" OR "surprisingly correct"—the competence frontier.

3. **Step 3 (ZPD Training → Maximized Signal):** Training on frontier examples provides optimal difficulty where gradient information is richest.

4. **Step 4 (Maximized Signal → Efficiency):** More information per training example leads to faster convergence compared to random sampling.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Self-Improvement Sharpening (Huang et al., 2024) | LLMs are better at verifying than generating; confidence after calibration can distinguish quality | Strong |
| Step 2 → Step 3 | PAIRED (Dennis et al., 2020) | Regret-based selection identifies frontier; produces natural curriculum of increasing complexity | Strong |
| Step 3 → Step 4 | ACCEL (Parker-Holder et al., 2022) | Frontier-based curriculum enables complexity growth; agents achieve higher zero-shot transfer | Strong |
| Step 4 → Outcome | Self-Evolving Curriculum (Chen et al., 2025) | Curriculum policy significantly improves reasoning capabilities over random curriculum | Medium |

**Key Tension:**
- **Tension:** PAIRED/ACCEL operate in RL environments with many rollouts, but LLM self-training requires expensive forward passes.
- **Resolution:** CCR provides a single-pass proxy for regret—confidence and correctness computed once per example.

### 1.4 Key Assumptions

1. **LLM confidence can be sufficiently calibrated (ECE < 0.15)**
   - Consequence if violated: CCR becomes unreliable; curriculum selection degenerates to noise

2. **Self-generated tasks span difficulty range including ZPD boundary**
   - Consequence if violated: No ZPD examples in sample; CCR selection has nothing to select

3. **High CCR examples provide greater learning signal than random examples**
   - Consequence if violated: Core hypothesis fails; CCR is not a meaningful selection criterion

4. **Verification oracle is available and accurate for target domain**
   - Consequence if violated: Correctness labels are noisy; CCR computation corrupted

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Verifiable task domains: mathematical reasoning, code generation, formal logic
- Open-source LLMs (7B-8B) where fine-tuning is feasible
- Self-training scenarios where model generates own training data

**Where Hypothesis Does NOT Apply:**
- Open-ended generation tasks without clear verification
- Subjective tasks without ground truth
- Very large models where fine-tuning is computationally prohibitive

**Known Limitations:**
- Calibration overhead adds computational cost
- CCR requires ground truth labels (limits to verifiable domains)
- α, β hyperparameters may require domain-specific tuning

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Learning Efficiency vs Random Baseline):**
CCR-based curriculum selection will achieve equivalent held-out accuracy with 30-50% fewer training examples compared to random sampling.

*Measurement*:
- Learning efficiency = Δaccuracy / N_training_examples
- Statistical test: Paired t-test across 5+ random seeds, p < 0.05

*Success Criteria for Phase 2B*:
- Primary: ≥30% reduction in examples to reach target accuracy (p < 0.05)
- Falsification: <10% reduction OR worse than random

**Secondary Predictions:**

**P2 (Calibration Improvement Post-Training):**
Training on high-CCR examples will reduce ECE by ≥20% compared to random training.

**P3 (Sustained Improvement via Iterative Refinement):**
With iterative CCR refinement, performance will continue improving beyond single-round training plateau.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if:

1. **Primary Failure:** CCR selection shows <10% efficiency improvement over random (or worse)
2. **Calibration Failure:** ECE remains >0.20 after calibration
3. **Mechanism Failure:** Ablation shows CCR components do not individually contribute
4. **Baseline Failure:** Simple alternatives (loss-based, uncertainty) match or exceed CCR

### 1.7 Statistical Verification Design

**Sample Size:** n ≥ 15 runs per condition (Cohen's d = 0.8, power = 0.8)

**Test Specification:**
- Method: Paired t-test (same random seeds)
- Significance: α = 0.05 (one-tailed)
- Report: Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does CCR-based selection identify examples that are more informative for learning than random selection?"
- Verification: Compare gradient norms or loss improvement on CCR-selected vs random examples
- Critical: MUST PASS for main hypothesis

**SH2 (Mechanism):**
"Is the 4-step causal mechanism the actual cause of improved learning?"
- Decomposes to H-M1 through H-M4:
  - H-M1: Calibration enables reliable CCR
  - H-M2: CCR identifies competence boundary
  - H-M3: Boundary training maximizes signal
  - H-M4: Signal maximization improves efficiency
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does CCR-based curriculum outperform alternatives (random, loss-based, uncertainty)?"
- Verification: Head-to-head comparison on GSM8K and HumanEval
- Critical: Determines practical value

**Total sub-hypotheses in Phase 2B:** 2 + 4 = 6

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-ZPD-CCR-v1
- [x] Confidence level: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] Variables operationalized with measurement methods
- [x] Causal mechanism: 4 steps with evidence
- [x] Key tension identified and resolved
- [x] Assumptions list consequences if violated
- [x] 3 testable predictions (primary marked)
- [x] Falsification criteria defined
- [x] Baselines identified
- [x] SH1, SH2, SH3 ready

### Open Questions

1. **α, β Tuning:** Domain-specific grid search or principled derivation?
2. **Calibration Method:** ConfTuner vs temperature scaling vs verbalized?
3. **Iterative Refinement Frequency:** How often to regenerate tasks?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
