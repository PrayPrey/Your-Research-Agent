# Phase 2A Extended: Hypothesis Summary for Phase 2B

**Date:** 2026-02-06
**Hypothesis ID:** H-ADPO-001
**Status:** Ready for Phase 2B Verification Planning

---

## Executive Summary

**Main Hypothesis:**
Adaptive Data Portfolio Optimization (ADPO) achieves superior model performance compared to fixed mixing ratios by dynamically optimizing synthetic-natural data proportions during training through portfolio theory-inspired quadratic programming, with empirically validated quality metrics, stable rebalancing protocols, and Bayesian warm-start initialization.

**Confidence Level:** 0.85 (High)

**Core Innovation:**
Frame synthetic-natural data mixing as dynamic portfolio optimization problem, where data sources are "assets" with quality-risk profiles, and optimal mixing weights are computed every K epochs using quadratic programming under privacy/cost constraints.

---

## Key Components

### 1. Core Mechanism

**Input:** Natural data + Multiple synthetic sources (CTGAN, VAE, Diffusion)

**Process:**
1. Profile each data source with quality metrics (SDMetrics: fidelity, utility, privacy)
2. Every K epochs, solve QP optimization:
   - Maximize: Σ w_i * μ_i - λ * Σ w_i * σ²_i
   - Subject to: Privacy budget, Cost budget, w_i ∈ [0,1], Σw_i=1
3. Apply damped weight updates (Δw_max ≤ 0.1) to prevent training instability
4. Monitor gradient variance; suspend rebalancing if instability detected

**Output:** Optimal mixing weights w*_i for next K epochs, adapted to current training phase

### 2. Key Variables

| Type | Variable | Measurement |
|------|----------|-------------|
| **Independent** | Mixing Strategy | {ADPO, Fixed-0%, Fixed-25%, Fixed-50%, Fixed-75%, Fixed-100%} |
| **Dependent (Primary)** | Model Performance | Test accuracy, F1-score, AUROC |
| **Dependent (Secondary)** | Training Efficiency | Epochs to 95% final performance |
| **Moderator** | Synthetic Data Quality | SDMetrics fidelity score [0,1] |
| **Moderator** | Privacy Budget | ε-DP parameter [0.1, 10] |
| **Mediating** | Mixing Weights (w_i) | ADPO output per epoch [0,1] |

### 3. Testable Predictions

**P1 (Primary):** ADPO accuracy ≥ max(Fixed baselines) + 2% (p < 0.05, n=5 seeds)

**P2:** ADPO reaches 95% final accuracy in ≤ 0.8× epochs of best fixed baseline

**P3:** Mixing weights show curriculum pattern: w_synthetic(early) > w_synthetic(late) by ≥0.15

**P4:** SDMetrics correlation with performance: r ≥ 0.5

**P5:** ADPO gain larger under tight privacy constraints (ε=1 vs. ε=10)

**P6:** Gradient variance CV ≤ 0.3 with damping; CV ≥ 0.5 without damping

### 4. Falsification Criteria

Hypothesis is **FALSIFIED** if:
- **FC1:** ADPO fails to outperform best fixed ratio on ≥3 out of 5 datasets
- **FC2:** Training instability (CV > 0.5 despite damping) or convergence failure
- **FC3:** Training overhead >10% AND accuracy gain <1%
- **FC4:** Quality metric correlation r < 0.3 AND fallback prohibitively expensive
- **FC5:** No curriculum learning pattern (random or inverted weights)

---

## Experimental Design

### Datasets & Conditions

**Datasets:** CIFAR-10, MNIST, Adult Census (+ optional Fashion-MNIST, Bank Marketing)

**Factors:**
- Mixing strategies: 8 (ADPO, Fixed-0/25/50/75/100%, Random, Naive-Curriculum)
- Data scarcity: 3 levels (10%, 25%, 50% natural data)
- Privacy budgets: 3 levels (ε=1, 3, 10) - subset of experiments

**Sample Size:** 5 random seeds per condition
**Total Runs:** ~480 training runs (360 base + 120 extended)

### Baselines

1. **Fixed Ratios:** 0%, 25%, 50%, 75%, 100% synthetic (maintained throughout training)
2. **Random Mixing:** Random w_i ~ Dirichlet(α=1) each epoch
3. **Naive Curriculum:** Linear schedule w_synthetic(t) = 1 - t/T

### Statistical Tests

- **Primary:** Paired t-test (ADPO vs. each baseline), α=0.01 (Bonferroni corrected)
- **Secondary:** Wilcoxon (convergence), Pearson (correlation), ANOVA (privacy levels), F-test (variance)
- **Effect Size:** Cohen's d ≥ 0.5 required for practical significance

---

## Phase 2B Sub-Hypotheses (Decomposition)

**SH1 (Existence):** ADPO improves over best fixed ratio
- Test: Paired t-test, n=5, α=0.01
- Success: ADPO > max(Fixed) + 2% on ≥2 out of 3 datasets

**SH2 (Mechanism):** Quality metrics predict performance
- Test: Pearson correlation r(SDMetrics, accuracy)
- Success: r ≥ 0.5; late weights correlate with quality

**SH3 (Comparison):** ADPO > Naive curriculum and random mixing
- Test: Paired t-test
- Success: ADPO > Naive+1%, ADPO > Random+2%

**SH4 (Constraints):** Privacy/cost constraints satisfied
- Test: Log constraint values, privacy auditing
- Success: 0% violations, empirical leakage ≤ ε

**SH5 (Stability):** Damped rebalancing maintains stability
- Test: Gradient variance CV comparison
- Success: Damped CV ≤ 0.3, Undamped CV ≥ 0.5

**SH6 (Curriculum):** Weights follow expected temporal pattern
- Test: Paired t-test (early vs. late phase weights)
- Success: Δw ≥ 0.15, p < 0.05

**SH7 (Efficiency):** Computational overhead acceptable
- Test: Wall-clock time measurement
- Success: Overhead ≤ 5%

---

## Key Assumptions

1. **Quality metrics correlate with performance** (r ≥ 0.5) - Testable via correlation study; fallback to direct measurement
2. **Curriculum learning benefits training** - Validated by literature; testable via reversed curriculum
3. **Multiple generators provide complementary info** - Testable via single-source comparison
4. **Damped rebalancing prevents instability** - Testable via damping ablation
5. **Privacy/cost constraints are linear** - Testable via privacy auditing
6. **Quality estimates stabilize during training** - Testable via convergence analysis

---

## Contributions

### Theoretical
- Novel formulation of data mixing as portfolio optimization
- Connection between portfolio theory and curriculum learning
- Theoretical analysis of optimal mixing under constraints

### Methodological
- ADPO algorithm with dynamic rebalancing
- Quality metric integration framework
- Empirical validation protocol (correlation, stability, curriculum)

### Practical
- Principled answer to "How much synthetic data?" based on constraints
- Cost-effective training (maximize performance per privacy/cost budget)
- Open-source implementation for practitioners
- Cross-domain applicability (tabular, vision, time-series, text)

---

## Key Related Work Differentiation

| Approach | ADPO (Ours) | Fixed Ratios | Naive Curriculum |
|----------|-------------|--------------|------------------|
| **Adaptation** | Dynamic (every K epochs) | Static | Predefined schedule |
| **Multi-Source** | Yes (optimize combination) | Rare | No |
| **Theory** | Portfolio optimization | None | Heuristic |
| **Constraints** | Privacy/cost explicit | No | No |

**Unique Position:** First to combine portfolio optimization + curriculum learning + quality metrics + privacy constraints in unified, adaptive framework.

---

## Implementation Readiness

**Tools:**
- PyTorch (neural networks)
- cvxpy/scipy.optimize (QP solving)
- SDV/SDMetrics (quality metrics)
- Membership inference tools (privacy auditing)

**Complexity:** MEDIUM
- Algorithmic: LOW (standard QP, mature libraries)
- Integration: MEDIUM (multiple components to coordinate)
- Validation: LOW (standard statistics)

**Timeline:** ~8 weeks
- Implementation: 2-3 weeks
- Pilot: 1 week
- Full experiments: 2-3 weeks
- Analysis: 1 week

**Compute:** ~1000-2000 GPU hours (NVIDIA RTX 3090 or equivalent)

---

## Open Questions (for Phase 2B)

**Medium Priority:**
1. Optimal rebalancing frequency K: Test K ∈ {5, 10, 20, 50} sensitivity
2. Cold start strategy: Bayesian vs. uniform priors vs. meta-learning
3. Failure mode characterization: Boundary conditions where ADPO ≈ Fixed

**Low Priority (Future Work):**
4. Multi-objective optimization extension (accuracy + fairness + robustness)
5. Transfer learning and domain adaptation scenarios
6. Theoretical convergence analysis
7. Production deployment considerations

**Phase 2B Status:** ✅ **READY** - No blocking questions

---

## Success Metrics Summary

**Primary Success:**
- ADPO achieves ≥2% accuracy improvement over best fixed baseline
- Statistical significance: p < 0.05, n=5 seeds
- Holds on ≥2 out of 3 test datasets

**Secondary Success:**
- 20% faster convergence (fewer epochs to 95% final accuracy)
- Curriculum pattern emerges (Δw ≥ 0.15 between phases)
- Quality metric correlation validated (r ≥ 0.5)
- Training stability maintained (CV ≤ 0.3)
- Computational overhead ≤ 5%

**Validation Complete When:**
All 7 sub-hypotheses (SH1-SH7) pass success criteria, demonstrating:
1. Performance gain exists
2. Mechanism is valid
3. Comparison baselines beaten
4. Constraints satisfied
5. Stability maintained
6. Curriculum emerges
7. Efficiency acceptable

---

*Generated: 2026-02-06*
*Hypothesis ID: H-ADPO-001*
*Confidence: 0.85*
*Status: Ready for Phase 2B Verification Planning*
