# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-PrecisionWeightedLLM-v1
**Confidence Level:** 0.87

**Main Hypothesis:**
Under standard LLM training conditions with dropout-enabled forward passes, if we add an auxiliary precision head trained with self-consistency supervision (agreement across k=5 perturbed forward passes), then the learned precision scores will exhibit higher correlation with actual response correctness than post-hoc uncertainty methods, because self-consistency during training encodes intrinsic reliability patterns that post-hoc methods cannot capture.

**Alternative Hypothesis (H0):**
There is no significant difference in precision-correctness correlation between learned precision scores from an auxiliary head and post-hoc uncertainty estimation methods (MC dropout, self-consistency sampling). Formally: ρ(τ_learned, correctness) ≤ ρ(τ_post-hoc, correctness) with p > 0.05.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Precision Head Architecture | Independent | 2-layer MLP (256 hidden) on final token hidden state outputting scalar τ ∈ (0, ∞) | Architecture variants: [128, 256, 512] hidden units |
| Self-Consistency Training Signal | Independent | Agreement score from k=5 MC dropout forward passes during training | τ_consistency ∈ [0, 1] |
| Loss Weight λ | Independent | Weight for precision loss: L = L_LM + λ · MSE(τ_pred, τ_consistency) | λ ∈ {0.1, 0.5, 1.0} |
| Precision-Correctness Correlation | Dependent | Spearman correlation between learned τ and binary correctness indicator | Expected ρ > 0.5 (vs baseline ~0.3-0.4) |
| Expected Calibration Error (ECE) | Dependent | Standard ECE metric with 10 bins comparing predicted confidence vs empirical accuracy | Expected ECE < 0.10 (vs baseline ~0.15-0.25) |
| Conformal Prediction Set Size | Dependent | Mean prediction set size at 90% coverage using learned τ as nonconformity score | Expected 20-30% reduction vs post-hoc |
| Base LLM Architecture | Controlled | Fixed architecture: Llama-2 7B or Mistral 7B | Single architecture per experiment |
| Training Data | Controlled | Fixed instruction-following dataset: Alpaca or OpenOrca | ~50K instruction samples |
| Evaluation Benchmarks | Controlled | TriviaQA, Natural Questions, XSum, HumanEval | 4 diverse task types |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
[Dropout Perturbation] → [Self-Consistency Signal] → [Learned Precision τ] → [Better Calibration]
```

**Step 1: Dropout Perturbation → Self-Consistency Signal**
MC dropout with k=5 passes generates variability that exposes model uncertainty. When the model is uncertain about a response, outputs vary more across dropout masks.

**Step 2: Self-Consistency Signal → Learned Precision τ**
Training the precision head with MSE loss on consistency targets forces the MLP to learn hidden state patterns associated with reliability.

**Step 3: Learned Precision τ → Better Calibration/Tighter Conformal Sets**
Intrinsic precision learned during training captures reliability patterns unavailable to post-hoc methods.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | ConU (Wang et al., 2024) | Self-consistency correlates with correctness (r=0.65-0.78) | Strong |
| Step1 → Step2 | COPU (Wang et al., 2025) | Consistency-based conformal prediction achieves valid coverage | Strong |
| Step2 → Step3 | Knill & Pouget (2004) | Neural systems encode uncertainty in population codes | Strong |
| Step2 → Step3 | Wilmes et al. (2025) | Cortical circuits learn precision-weighted prediction errors | Medium |
| Step3 → Outcome | pyhgf (Legrand et al., 2024) | Predictive coding networks can learn precision during inference | Medium |

**Key Tension:**
- **Tension:** ConU/COPU show post-hoc self-consistency works well, questioning whether learned precision offers additional value.
- **Resolution:** Test whether LEARNED precision (from hidden states) captures patterns that post-hoc sampling (from outputs) cannot access.

### 1.4 Key Assumptions

1. **Self-consistency correlates with correctness** - Evidence: ConU (2024), COPU (2025). Consequence if violated: Training signal is noise.

2. **MLP precision head has sufficient capacity** - Evidence: Auxiliary heads for reward modeling use similar architectures. Consequence if violated: Constant output.

3. **Efficient dropout-based consistency maintains signal quality** - Evidence: MC dropout literature. Consequence if violated: Need expensive full-generation consistency.

4. **Precision generalizes to held-out tasks** - Evidence: Transfer learning literature. Consequence if violated: Overfits to training distribution.

### 1.5 Scope & Boundaries

**Applies to:** Instruction-following LLMs (7B+), tasks with verifiable correctness, safety-critical settings, conformal prediction frameworks.

**Does NOT apply to:** Creative writing, tasks without correctness criteria, smaller models (<1B), real-time applications.

**Limitations:** Training distribution dependence, dropout noise, ~20-30% training overhead.

### 1.6 Testable Predictions

**Primary Prediction (P1):**
Learned precision τ will achieve Spearman ρ(τ, correctness) > 0.55, significantly exceeding post-hoc methods (~0.40).
- Measurement: Spearman ρ > 0.55 with p < 0.05
- Falsification: ρ ≤ 0.40

**Secondary Predictions:**
- P2: ECE < 0.10 (≥30% improvement over baseline ~0.15-0.25)
- P3: Conformal prediction sets 20-30% smaller while maintaining 90% coverage

**Falsification Criteria:**
1. ρ(τ_learned, correctness) ≤ 0.40 (no improvement)
2. Precision head outputs constant value
3. ECE worsens with precision head
4. Conformal sets not smaller than post-hoc

### 1.8 Statistical Verification Design

- Effect size: ~0.6 (medium-large)
- Test samples: n ≥ 1000 per benchmark
- Training runs: ≥ 3 seeds
- Test: Spearman correlation, Wilcoxon signed-rank, α = 0.05

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does self-consistency during training produce learnable precision signals in LLM hidden states?"
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the 3-step causal mechanism the actual cause of improved uncertainty quantification?"
- Decomposes into 3 sub-hypotheses: H-M1, H-M2, H-M3

**SH3 (Comparison):**
"Does learned precision outperform post-hoc methods in calibration and conformal prediction efficiency?"

**Total Sub-Hypotheses:** 5 (SH1: 1, SH2: 3, SH3: 1)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-PrecisionWeightedLLM-v1
- [x] Confidence level: 0.87
- [x] Alternative hypothesis (H0) defined
- [x] Variables operationalized
- [x] Causal mechanism with evidence (N=3 steps)
- [x] Key tension + resolution
- [x] Assumptions with consequences
- [x] 3 testable predictions (primary marked)
- [x] Falsification criteria defined
- [x] Baselines identified (ConU, MC dropout)
- [x] SH1, SH2, SH3 ready

### Open Questions

1. **Resource Requirements:** Training compute with k=5 dropout passes (~20-30% overhead)?
2. **Data Availability:** Instruction datasets with correctness labels?
3. **Baseline Implementation:** ConU/COPU official implementations available?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
