# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-MSSWRB-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under gradient-based LLM training conditions, if multi-signal surprise scores (combining normalized loss deviation with gradient magnitude) are used to weight sample replay probability, then training efficiency will improve by 20-40% while maintaining model quality, because high-surprise samples contain more informative gradients that accelerate learning convergence similar to hippocampal memory consolidation mechanisms.

**Alternative Hypothesis (H0):**
Multi-signal surprise scores do not correlate with sample informativeness, and surprise-weighted replay provides no significant improvement over random sampling in terms of training efficiency or model quality.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Multi-signal surprise score (s) | Independent | s = λ × \|L_i - μ_L\|/σ_L + (1-λ) × \|\|∇L_i\|\|/\|\|∇L\|\|_avg | 0.0 - 5.0 (normalized) |
| Loss-gradient balance (λ) | Independent | Weight parameter balancing loss vs gradient signals | 0.3 - 0.7 (default: 0.5) |
| Exploitation coefficient (α) | Independent | Exponent controlling priority sharpness | 0.5 - 2.0 (default: 1.0) |
| Warmup duration | Independent | Training fraction using random sampling | 0.03 - 0.10 (default: 0.05) |
| Temporal decay rate | Independent | Exponential decay of surprise scores over time | 0.9 - 0.999 per epoch |
| Training efficiency | Dependent | Wall-clock time to reach target perplexity (PPL=10) | 20-40% reduction expected |
| Final model quality | Dependent | Perplexity on C4 validation + MMLU/HellaSwag scores | Within 1% of baseline |
| Sample diversity | Dependent | Domain coverage ratio, Gini coefficient of replay freq | Coverage ≥ 0.95 |
| Model architecture | Controlled | LLaMA-7B or equivalent transformer | Fixed |
| Total training compute | Controlled | FLOPs budget (100B tokens equivalent) | Fixed |
| Dataset | Controlled | C4 or RedPajama subset | Fixed preprocessing |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Surprise Computation
    ↓
Step 2: Priority-Weighted Sampling
    ↓
Step 3: Informative Gradient Accumulation
    ↓
Outcome: Faster Convergence to Target Perplexity
```

**Step 1: Surprise Score Computation → Priority Assignment**
- For each training sample, compute multi-signal surprise: s = λ × |L_i - μ_L|/σ_L + (1-λ) × ||∇L_i||/||∇L||_avg
- Running statistics (μ_L, σ_L, ||∇L||_avg) update incrementally with O(1) overhead
- High-surprise samples receive higher priority scores in the replay buffer
- **Falsification:** If surprise scores show <0.3 correlation with post-hoc influence scores

**Step 2: Priority-Weighted Sampling → Informative Gradient Selection**
- Replay probability P(replay) ∝ s^α × decay(t) prioritizes high-surprise samples
- Priority queue with O(log n) operations maintains sample ordering
- Diversity maintenance ensures minimum domain coverage (stratified sampling)
- **Falsification:** If high-priority samples show higher noise-to-signal ratio than random samples

**Step 3: Informative Gradient Accumulation → Accelerated Convergence**
- High-surprise samples provide larger, more informative gradient updates
- More effective gradient steps per training iteration reduce total steps needed
- Temporal decay prevents stagnation on early high-surprise samples
- **Falsification:** If convergence rate (loss reduction per step) is not higher than random baseline

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Hayes et al. (2021) | Biological replay prioritizes high-surprise experiences for consolidation | Strong |
| Step 1 → Step 2 | Sun et al. (2025) | Difficulty-targeted selection achieves 23-62% training time reduction | Strong |
| Step 2 → Step 3 | Koh & Liang (2017) | Influential training points have higher impact on model predictions | Strong |
| Step 3 → Outcome | Sun et al. (2025) | Online data selection improves LLM training efficiency | Strong |

**Key Tension:**
- **Tension:** Hayes et al. (2021) suggests biological replay uses prediction error alone, but Koh & Liang (2017) shows gradient magnitude better captures influence on model behavior.
- **Resolution:** MS-SWRB combines both signals (loss deviation + gradient magnitude) with tunable weight λ, allowing empirical determination of optimal combination for LLM training context.

### 1.4 Key Assumptions

1. **Prediction error correlates with informativeness**
   - Evidence: Sun et al. (2025) demonstrates difficulty-targeted selection works; Hayes et al. (2021) confirms biological basis
   - Consequence if violated: Surprise scores become random noise, no efficiency improvement

2. **Gradient magnitude provides complementary signal**
   - Evidence: Koh & Liang (2017) shows gradient-based influence captures information not in loss alone
   - Consequence if violated: Multi-signal approach provides no benefit over loss-only; simplify to single signal

3. **Temporal decay prevents overfitting**
   - Evidence: Standard practice in prioritized experience replay (Schaul et al., 2015)
   - Consequence if violated: Training stagnates on early high-surprise samples, diversity suffers

4. **Computational overhead is negligible**
   - Evidence: Loss computed anyway; gradient magnitude from existing backward pass; running stats are O(1)
   - Consequence if violated: Efficiency gains offset by overhead; need approximations or sampling

### 1.5 Scope & Boundaries

**Applies to:**
- LLM pretraining with gradient-based optimization (SGD, Adam, etc.)
- Fine-tuning scenarios with replay buffer integration
- Any transformer architecture (GPT, LLaMA, etc.)
- Datasets with domain diversity (C4, RedPajama, Pile)

**Does NOT apply to:**
- Non-gradient methods (evolutionary, Bayesian optimization)
- Inference-time data selection (different problem)
- Extremely small datasets where all samples should be seen equally
- Online learning without replay capability

**Known Limitations:**
- Requires integration with training loop (not a drop-in replacement)
- Hyperparameters (λ, α, decay) may need tuning per domain
- Buffer size introduces memory overhead (though sublinear in dataset size)
- Warmup period delays benefit onset

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Training Efficiency vs Random Baseline)**:
MS-SWRB will achieve target perplexity (PPL=10 on C4 validation) in 20-40% less wall-clock time compared to random sampling baseline, while maintaining final model quality within 1%.

*Measurement*:
- Time to target perplexity with p < 0.05 (one-tailed t-test)
- Statistical test: Paired t-test across 15+ random seeds
- Effect size: Cohen's d > 0.8 (large effect)

*Basis*:
Sun et al. (2025) achieves 23-62% improvement with simpler difficulty-targeting. Our multi-signal approach should achieve similar or better results.

*Success Criteria for Phase 2B*:
- Primary: Time reduction ≥ 20% (p < 0.05)
- Falsification: Time reduction < 10% OR quality degradation > 2%

**Secondary Predictions:**

**P2 (Surprise-Influence Correlation)**:
Multi-signal surprise scores will show Spearman correlation ρ ≥ 0.5 with post-hoc TrackIn influence scores on a 1% validation subset.

*Measurement*: Spearman rank correlation, n=1000 samples
*Falsification*: ρ < 0.3 suggests surprise is not a valid proxy for influence

**P3 (Diversity Maintenance)**:
With stratified sampling, domain coverage ratio will remain ≥ 0.95 throughout training, and Gini coefficient of replay frequencies will stay below 0.6.

*Measurement*: Per-epoch diversity metrics
*Falsification*: Coverage < 0.90 OR Gini > 0.7 indicates mode collapse

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Training efficiency improvement < 10% with p > 0.1
   (No meaningful speedup compared to random sampling)

2. **Mechanism Failure**: Surprise-influence correlation ρ < 0.3
   (Surprise is not a valid proxy for sample importance)

3. **Quality Failure**: Final perplexity > 105% of baseline OR benchmark drop > 3%
   (Efficiency gained at unacceptable quality cost)

4. **Diversity Failure**: Domain coverage < 0.85
   (Mode collapse makes method impractical)

### 1.7 SOTA Baseline (Optional)

**Not applicable** - This hypothesis targets absolute training efficiency improvement rather than comparison against specific SOTA methods. Baselines are:
- Random sampling (primary comparison)
- Static curriculum learning (secondary comparison)
- LoGra post-hoc attribution (computational overhead comparison)

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): 0.8 (large, based on Sun et al. 23-62% improvement)
- Required runs: n ≥ 15 (for 80% power at α=0.05)
- Statistical power: 0.8

**Test Specification:**
- Method: Paired t-test (same random seeds for MS-SWRB vs baseline)
- Significance level: α = 0.05 (one-tailed for improvement hypothesis)
- Multiple comparison correction: Bonferroni for secondary predictions
- Report format: Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does surprise-weighted sampling produce measurable training efficiency improvement compared to random sampling under controlled LLM pretraining conditions?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical comparison
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the multi-signal surprise score the actual cause of improved training efficiency through the proposed 3-step causal chain?"
- Maps to: Causal mechanism (N=3 steps)
- Decomposes into 3 mechanism sub-hypotheses in Phase 2B:
  - H-M1: Surprise → Priority (correlation validation)
  - H-M2: Priority → Informative Gradients (gradient quality analysis)
  - H-M3: Informative Gradients → Convergence (ablation study)
- Verification type: Causal analysis + ablation
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does MS-SWRB provide advantages over existing approaches (static curriculum, post-hoc attribution) in the efficiency-overhead trade-off?"
- Maps to: Secondary predictions (P2, P3) + baseline comparisons
- Verification type: Comparative empirical
- Critical: Determines practical value

**Total sub-hypotheses in Phase 2B:** 2 + 3 = 5 (SH1, H-M1, H-M2, H-M3, SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-MSSWRB-v1
- [x] Confidence level specified: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence (9 variables fully specified)
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence table included)
- [x] Causal chain length (N=3) determined and documented
- [x] Key tension identified (loss vs gradient signals) and resolution proposed (tunable λ)
- [x] Key assumptions list consequences if violated (4 assumptions)
- [x] At least 2 testable predictions exist with primary marked (P1 primary, P2/P3 secondary)
- [x] Falsification criteria are defined (4 rejection conditions)
- [x] Baselines are identified for comparison (random, static curriculum, LoGra)
- [x] SH1, SH2, SH3 are clear starting points for Phase 2B

### Open Questions

1. **Resource Requirements:** What GPU memory overhead does the priority queue add for 7B model training? Estimate: <5% but needs validation.

2. **Hyperparameter Sensitivity:** How sensitive are results to λ (loss-gradient balance)? Is grid search over [0.3, 0.5, 0.7] sufficient?

3. **Scale Generalization:** Does the 20-40% efficiency improvement hold for larger models (13B, 70B) or different architectures?

4. **Priority Verification Order:** Recommend SH1 first (existence), then H-M1 (mechanism entry point), as SH1 failure would invalidate entire hypothesis.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
