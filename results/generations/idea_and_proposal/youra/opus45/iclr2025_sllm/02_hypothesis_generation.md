# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SAE-Sparsity-v1
**Confidence Level:** 0.83

**Main Hypothesis:**
Under LLM inference with pre-trained SAEs available, if SAE feature importance scores (computed offline via gradient-weighted activation analysis) are used as soft weights to bias contextual sparsity predictor outputs, then inference speedup will be achieved with improved interpretability because SAE features encode semantic relevance that correlates with computational importance for task performance.

**Alternative Hypothesis (H0):**
SAE feature importance scores have no meaningful correlation with contextual sparsity patterns, and weighting sparsity predictor outputs by SAE importance provides no improvement over unweighted predictors in terms of accuracy, speedup, or interpretability.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| SAE feature importance scores | Independent | Gradient-weighted mean activation of SAE features per MLP neuron, computed offline using Gemma Scope SAEs | 0.0-1.0 normalized importance per neuron |
| Inference speedup ratio | Dependent | Wall-clock latency reduction compared to dense baseline, measured via end-to-end inference time | 1.3x-2.0x target speedup |
| Task accuracy | Dependent | Performance on MMLU, HellaSwag benchmarks relative to dense baseline | >98% accuracy retention |
| Interpretability quality | Dependent | Proportion of sparsity decisions traceable to human-interpretable SAE features | >80% traceability |
| Base model architecture | Controlled | Gemma 2 2B/9B with Gemma Scope SAEs | Fixed per experiment |
| Sparsity predictor type | Controlled | ShadowLLM or DejaVu predictor architecture | Fixed per comparison |

### 1.3 Causal Mechanism

**3-Step Causal Chain:**

```
Step 1: SAE Feature Analysis → Importance Scores
    ↓
Step 2: Importance Scores → Weighted Sparsity Decisions
    ↓
Step 3: Weighted Sparsity Decisions → Speedup + Interpretability
```

**Step 1: SAE Feature Analysis → Importance Scores**
Pre-trained SAEs (Gemma Scope) decompose neural activations into interpretable features. Gradient-weighted analysis identifies which features contribute most to task performance.

**Step 2: Importance Scores → Weighted Sparsity Decisions**
Pre-computed importance scores serve as soft weights multiplying sparsity predictor logits before thresholding, biasing decisions toward preserving semantically important neurons.

**Step 3: Weighted Sparsity Decisions → Speedup + Interpretability**
Sparse computation skips low-importance neurons (speedup) while SAE-based weighting provides traceable explanation for each decision (interpretability).

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | FGAA (Soo 2025) | SAE features enable precise model steering through activation manipulation | Strong |
| Step 1 → Step 2 | Gemma Scope (Lieberum 2024) | JumpReLU SAEs provide clean feature decomposition across model scales | Strong |
| Step 2 → Step 3 | ShadowLLM (Akhauri 2024) | Better sparsity patterns improve accuracy by 15% over prior methods | Strong |
| Step 2 → Step 3 | R-Sparse (Zhang 2025) | Training-free sparsity achieves 50% model-level sparsity with 43% efficiency gain | Medium |
| Step 3 → Outcome | DejaVu (Liu 2023) | Contextual sparsity enables 2x inference speedup without accuracy loss | Strong |

**Key Tension:**
- **Tension:** ShadowLLM shows neural predictors achieve 15% accuracy improvement through learned patterns, but SAE features are designed for interpretability not efficiency. It's unclear if interpretability-optimized features will correlate with efficiency-optimal sparsity.
- **Resolution:** This verification plan tests whether SAE features, despite being trained for interpretability, capture task-relevance that predicts computational importance. The soft weighting approach allows graceful degradation if correlation is weak.

### 1.4 Key Assumptions

1. **SAE features capture semantically meaningful activation patterns**
   - Evidence: FGAA demonstrates SAE features enable precise steering
   - Consequence if violated: Importance scores will be noise; weighting will not improve over baseline

2. **Gradient-weighted importance reflects downstream task relevance**
   - Evidence: Gradient-based attribution methods are established for importance
   - Consequence if violated: Scores will reflect reconstruction quality not task utility

3. **Pre-computed scores generalize across inputs within similar distributions**
   - Evidence: SAE feature transferability across model scales (Gallifant 2025)
   - Consequence if violated: Per-input importance computation needed; overhead may negate benefits

4. **Existing sparsity predictors can be improved with structural priors**
   - Evidence: ShadowLLM improves over DejaVu by shadowing LLM behavior better
   - Consequence if violated: Predictors already optimal; SAE weighting adds complexity without benefit

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- LLMs with available pre-trained SAEs (Gemma 2 family via Gemma Scope)
- Decoder-only transformer architectures
- Inference-time optimization (no training modification)
- Single GPU deployment scenarios (7B-9B parameter range)

**Where Hypothesis Does NOT Apply:**
- Models without available SAEs (requires SAE training first)
- Vision models or multimodal models (different activation patterns)
- Training-time efficiency (only addresses inference)
- Distributed inference across multiple GPUs (different bottlenecks)

**Known Limitations:**
- Effectiveness depends on SAE quality and coverage
- Offline importance computation requires one-time GPU hours
- Interpretability benefits require human evaluation protocol

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Accuracy-Speedup Trade-off):**
SAE-weighted contextual sparsity will achieve ≥40% activation sparsity with <2% accuracy degradation on MMLU/HellaSwag benchmarks, resulting in ≥1.3x end-to-end inference speedup.

*Measurement*:
- Sparsity ratio: % of MLP neurons skipped per forward pass
- Accuracy: MMLU 5-shot, HellaSwag 0-shot accuracy vs. dense baseline
- Speedup: Wall-clock latency on batch size 1, sequence length 512
- Statistical test: Paired t-test, n ≥ 20 runs, p < 0.05

*Success Criteria for Phase 2B*:
- Primary: Accuracy ≥ 98% of dense baseline AND Speedup ≥ 1.3x (p < 0.05)
- Falsification: Accuracy < 95% of dense baseline OR Speedup < 1.1x

**Secondary Predictions:**

**P2 (Mechanism Validation - SAE-Sparsity Correlation):**
SAE feature importance scores will show statistically significant correlation (Pearson r > 0.3, p < 0.01) with DejaVu/ShadowLLM sparsity decisions on held-out test data.

**P3 (Interpretability Advantage):**
≥80% of sparsity decisions will be traceable to ≤5 human-interpretable SAE features, enabling debugging of "why was this neuron pruned?"

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Accuracy < 95% of dense baseline OR Speedup < 1.1x
2. **Mechanism Failure**: SAE-sparsity correlation r < 0.1 (p > 0.05)
3. **Baseline Failure**: SAE-weighted predictor performs worse than unweighted baseline on all metrics

### 1.7 SOTA Baseline (Optional)

*Not applicable - novel intersection without direct SOTA comparison.*

**Relevant Baselines:**
| Method | Speedup | Accuracy Retention | Interpretability |
|--------|---------|-------------------|------------------|
| DejaVu (Liu 2023) | 2x | ~100% | None |
| ShadowLLM (Akhauri 2024) | 1.2x over DejaVu | +15% accuracy | None |
| R-Sparse (Zhang 2025) | 43% efficiency gain | ~100% | None |
| **Ours (Target)** | ≥1.3x | ≥98% | ≥80% traceable |

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Expected effect size (Cohen's d): 0.5-0.8 (medium to large)
- Required runs: n ≥ 20 per configuration
- Statistical power: 0.8

**Test Specification:**
- Method: Paired t-test (same random seeds for baseline vs. SAE-weighted)
- Significance level: α = 0.05 (one-tailed for improvement)
- Report format: Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does SAE feature importance meaningfully correlate with contextual sparsity patterns in LLM inference?"
- Maps to: Primary prediction P2 (correlation test)
- Verification type: Empirical correlation analysis
- Critical: MUST PASS - if no correlation exists, weighting approach is unfounded

**SH2 (Mechanism):**
"Is the SAE-weighted sparsity prediction pipeline the actual cause of improved performance?"
- Maps to: Causal mechanism (3 steps)
- Will decompose into:
  - **H-M1:** SAE feature analysis correctly identifies task-relevant neurons
  - **H-M2:** Soft weighting effectively biases predictor decisions
  - **H-M3:** Sparse computation translates to measurable speedup
- Verification type: Ablation studies isolating each mechanism step

**SH3 (Comparison):**
"Does SAE-weighted sparsity outperform unweighted baselines?"
- Maps to: Primary prediction P1 (accuracy-speedup trade-off)
- Verification type: Comparative empirical evaluation
- Critical: Determines practical value

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-SAE-Sparsity-v1
- [x] Confidence level specified: 0.83
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps)
- [x] Causal chain length determined: N=3
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 predictions)
- [x] Falsification criteria defined (3 failure conditions)
- [x] Baselines identified (DejaVu, ShadowLLM, R-Sparse)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** GPU-hours for offline importance computation? (Est: 4-8 hours/model on A100)
2. **Data Availability:** Standardized SAE feature interpretability annotations exist?
3. **Technical Feasibility:** Can importance lookup integrate into sparse kernels without latency overhead?
4. **Priority Order:** Validate SH1 (correlation) before SH2/SH3? (Recommended: Yes)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
