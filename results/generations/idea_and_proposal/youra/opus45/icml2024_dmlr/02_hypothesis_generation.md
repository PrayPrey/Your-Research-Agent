# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - MVDC)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-MVDC-v1
**Confidence Level:** 0.80

**Main Hypothesis:**
Under conditions of large-scale foundation model training with limited compute budget, if pre-computed quality proxies (CLIP scores, perplexity) are used to estimate marginal data value at cluster granularity with Bayesian threshold optimization, then model performance per unit compute will exceed fixed-threshold baselines by 5-15% because marginal value estimation enables compute-aware filtering that adapts to diminishing returns from data repetition.

**Alternative Hypothesis (H0):**
There is no significant relationship between proxy-based marginal value estimation and model performance per compute; fixed-threshold filtering performs equivalently regardless of compute budget, and the quality-quantity tradeoff cannot be dynamically optimized.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Quality proxy signals | Independent | CLIP cosine similarity scores (0-1), perplexity scores, embedding density metrics computed on DataComp/DCLM pools | CLIP: 0.0-1.0, Perplexity: 10-1000 |
| Compute budget | Independent | Total GPU-hours or FLOPs allocated for training | DataComp small: ~100 GPU-hrs, medium: ~1000 GPU-hrs, large: ~10000 GPU-hrs |
| Filtering threshold (τ*) | Dependent | Optimized threshold derived from Bayesian optimization over scaling law parameters | 0.2-0.5 for CLIP scores |
| Model performance | Dependent | ImageNet zero-shot accuracy (%), MMLU score (%), performance-per-FLOP ratio | Medium scale: 30-45%, Large scale: 70-85% |
| Data distribution | Controlled | Fixed source pool from DataComp (12.8B image-text pairs) or DCLM (240T tokens) | Constant across experiments |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
[Proxy Signals] → [Cluster Value Estimation] → [Bayesian Threshold Optimization] → [Improved Performance/Compute]
     Step 1                Step 2                        Step 3                           Outcome
```

**Step 1: Proxy Signals → Cluster-Based Value Estimation**
- Mechanism: Aggregating proxy signals (CLIP score, perplexity, diversity) at cluster granularity enables scalable value prediction
- Evidence: EcoVal achieves comparable accuracy with 100x speedup over individual estimation
- Falsification: If proxy signals have near-zero correlation with true training value

**Step 2: Cluster Value Estimates → Bayesian Threshold Optimization**
- Mechanism: Value estimates combined with scaling law predictions enable optimization of filtering threshold τ* under uncertainty
- Evidence: Goyal et al. (2024) show optimal threshold varies significantly with compute budget
- Falsification: If scaling law parameters are highly non-stationary across data distributions

**Step 3: Optimized Threshold → Improved Performance-per-Compute**
- Mechanism: Adaptive threshold maximizes retained data utility while avoiding repetition penalty
- Evidence: Sorscher et al. (2022) show good pruning metrics enable exponential rather than power-law scaling
- Falsification: If repetition penalty is negligible or optimal threshold is constant

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | EcoVal (2024) | Cluster-based valuation achieves comparable accuracy to per-sample with 100x speedup | Strong |
| Step 2 → Step 3 | Goyal et al. (2024) | Optimal filtering threshold varies with compute budget; compute-agnostic curation is suboptimal | Strong |
| Step 3 → Outcome | Sorscher et al. (2022) | Good data pruning metrics can achieve exponential rather than power-law scaling | Strong |

**Key Tension:**
- Tension: Goyal et al. (2024) emphasize compute-aware curation, but FLYT (2025) achieves SOTA using gradient-based filtering which requires model access. MVDC proposes proxy-based filtering which is faster but potentially less accurate.
- Resolution: This verification plan tests whether proxy-based estimation can achieve comparable results to gradient-based methods while maintaining O(1) computational overhead per sample.

### 1.4 Key Assumptions

1. **Proxy-Value Correlation**: Quality proxy signals (CLIP score, perplexity) correlate positively with true training value for foundation models
   - Evidence: DataComp and LAION-5B filtering results show CLIP filtering improves over random by 15-20%
   - Consequence if violated: MVDC will produce suboptimal filtering decisions, performing no better than random sampling

2. **Scalable Value Estimation**: Marginal data value can be estimated without full model retraining using proxy-based cluster aggregation
   - Evidence: EcoVal and CHG Shapley approaches demonstrate efficient approximations
   - Consequence if violated: Per-sample value estimation becomes computationally infeasible at billion scale

3. **Scaling Law Predictability**: Scaling laws provide reasonable predictions of training value under different filtering regimes
   - Evidence: Goyal et al. (2024) and Kaplan et al. (2020) demonstrate predictive power of scaling laws
   - Consequence if violated: Bayesian threshold optimization will fail to find optimal τ*

4. **Cluster Sufficiency**: Cluster-level value estimation is sufficient for billion-scale data without significant accuracy loss
   - Evidence: EcoVal achieves comparable results at cluster granularity
   - Consequence if violated: Important high-value samples may be incorrectly filtered, degrading performance

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Vision-language foundation model training (CLIP-style)
- Text-only foundation model training (LLM pre-training)
- Datasets with pre-computed quality proxies (CLIP scores, perplexity)
- Compute budgets where quality-quantity tradeoff matters (medium to large scale)

**Where Hypothesis Does NOT Apply:**
- Domains without existing quality proxies (e.g., novel modalities without pre-trained encoders)
- Real-time streaming data where pre-computation is not possible
- Very small scale where all data can be used without repetition
- Fine-tuning scenarios (focused on pre-training data curation)

**Known Limitations:**
- Cluster granularity may miss high-value individual outliers
- Requires initial pilot run for Bayesian parameter calibration
- Proxy signal combination weights may need domain-specific tuning

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (ImageNet Zero-Shot vs SOTA 36% ± 3%)**:
MVDC with Bayesian threshold optimization will achieve ImageNet zero-shot accuracy > 38.5% on DataComp medium scale benchmark.

*Measurement*:
- ImageNet zero-shot accuracy > 38.5% with p < 0.05
- Statistical test: Paired t-test vs fixed-threshold baseline, n ≥ 25 runs

*Basis*:
SOTA methods on DataComp medium achieve 36% ± 3% (FLYT achieves 40.1%).
Our target represents ~0.8σ improvement over mean, positioning between average and FLYT.

*Success Criteria for Phase 2B*:
- Primary: Accuracy > 38.5% (p < 0.05)
- Falsification: Accuracy ≤ 33% triggers rejection

**Secondary Predictions:**

**P2 (Compute Efficiency)**:
MVDC filtering overhead will be < 5% of total training compute while achieving performance improvements.

**P3 (Threshold Adaptation)**:
Optimal filtering threshold τ* will vary monotonically with compute budget - higher budgets allow more lenient thresholds.

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: ImageNet zero-shot accuracy ≤ 33% on DataComp medium
2. **Mechanism Failure**: No correlation between proxy-based value estimates and actual training contribution
3. **Comparative Failure**: Fixed-threshold baseline outperforms MVDC on performance-per-compute metric

### 1.7 SOTA Baseline

| Method | Dataset | Performance | Std Dev | Year |
|--------|---------|-------------|---------|------|
| FLYT (M-FLYT) | DataComp-medium | 40.1% | ~2% | 2025 |
| DataComp CLIP baseline | DataComp-medium | ~35% | ~3% | 2023 |
| Fixed threshold (0.3) | DataComp-medium | ~32% | ~3% | 2022 |

**SOTA Statistics:** Mean: 36%, Std: 3%, Tier: Medium (30-40%)

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): 0.83
- Required runs: n ≥ 25
- Statistical power: 0.8

**Test Specification:**
- Method: Paired t-test (same random seeds)
- Significance level: α = 0.05 (one-tailed)
- Report format: Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Do pre-computed quality proxies (CLIP score, perplexity) provide signal that correlates with actual training value for foundation models?"
- Maps to: Primary prediction (proxy validity)
- Verification type: Empirical correlation analysis
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism - 3 sub-hypotheses):**
"Is the proposed three-step mechanism (proxy → cluster value → threshold optimization → performance) the actual causal path?"

- **H-M1**: Cluster-based value aggregation preserves signal fidelity vs per-sample estimation
- **H-M2**: Bayesian optimization over scaling law parameters finds better thresholds than grid search
- **H-M3**: Adaptive thresholds outperform fixed thresholds across compute budgets

Verification type: Causal ablation studies
Critical: Determines explanatory power

**SH3 (Comparison):**
"Does MVDC outperform existing methods (fixed threshold, FLYT) on performance-per-compute metric?"
- Maps to: Secondary predictions
- Verification type: Comparative empirical evaluation
- Critical: Determines practical value

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-MVDC-v1
- [x] Confidence level specified: 0.80
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps)
- [x] Causal chain length determined: N=3
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 predictions with primary marked)
- [x] Falsification criteria are defined with quantitative thresholds
- [x] Baselines are identified for comparison (Fixed-threshold, FLYT)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements**: What is the minimum pilot data size needed for reliable Bayesian calibration of scaling law parameters?

2. **Cluster Algorithm Choice**: Should clustering use CLIP embeddings directly, or a combination of proxy signals? What cluster count K optimizes the quality-scalability tradeoff?

3. **Priority Verification Order**: Should SH1 (proxy validity) be verified first as a gate, or can mechanism testing (SH2) proceed in parallel?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
