# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CriticalityOpt-v1
**Confidence Level:** 0.72

**Main Hypothesis:**
Under supervised learning with sufficient data (C), if optimizer hyperparameters (learning rate, weight decay, momentum) are adaptively scheduled to maintain the network near critical dynamics as measured by computationally tractable proxy metrics (X), then generalization phase transitions (grokking, double descent) will occur predictably and accelerated (Y), because optimal learning occurs at criticality where the network achieves maximum information processing capacity and the lazy-to-rich training transition is facilitated (Z).

**Alternative Hypothesis (H0):**
Maintaining networks near criticality through optimizer scheduling has no significant effect on the timing or predictability of generalization phase transitions compared to standard optimizer schedules.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Criticality metric (proxy) | Independent | Gradient flow statistics and Hutchinson Hessian trace estimator | 0.8-1.2 (normalized); target ≈1.0 |
| Optimizer hyperparameter schedule | Independent | Adaptive LR/WD/momentum via PID-style control | LR: 1e-4 to 1e-2; WD: 1e-5 to 1e-2 |
| Model scale | Independent | Parameter count across staged validation | 10^5 to 10^9+ |
| Phase transition timing | Dependent | Epochs to grokking (train-test gap < 1%) | 50% reduction expected |
| Generalization quality | Dependent | Final test accuracy after phase transition | Equal or better than baseline |
| Training data size | Controlled | Fixed per scale regime | Per-task specification |
| Architecture family | Controlled | MLP, ResNet, or Transformer | Fixed per experiment |
| Random seed | Controlled | Multiple seeds | n ≥ 15 |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**
```
Step 1: Optimizer Hyperparameters → Step 2: Network Dynamics State → Step 3: Criticality Proximity → Outcome: Accelerated Phase Transitions
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Cohen et al. (Edge of Stability) | LR modulates Hessian eigenvalue dynamics | Strong |
| Step2 → Step3 | Kumar et al. 2023 | Grokking = lazy→rich transition | Strong |
| Step3 → Outcome | Vock & Meisel 2025 | DNNs perform optimally near criticality | Strong |

**Key Tension:**
- **Tension:** Vock & Meisel 2025 shows correlation but not causation for criticality-performance link.
- **Resolution:** Intervention experiments will test causality via active criticality modulation.

### 1.4 Key Assumptions

| # | Assumption | Consequence if Violated |
|---|------------|------------------------|
| A1 | Proxy metrics correlate with true criticality | Framework becomes intractable or invalid |
| A2 | Schedules can modulate dynamics faster than natural training | Control authority insufficient; unfalsifiable |
| A3 | Small-scale transitions share mechanisms with large-scale | Results don't transfer; LLM validation essential |
| A4 | Physics criticality applies to neural networks | Theoretical framework collapses |

### 1.5 Scope & Boundaries

**Applies to:** Supervised learning with grokking/double descent; MLP/ResNet/Transformer; 10^5-10^9+ params
**Does NOT apply to:** RL, online learning, extreme low-data, tasks without phase transitions
**Limitations:** Cross-domain transfer conceptual; ~10-20% compute overhead; scale invariance approximate

### 1.6 Testable Predictions

**Primary Prediction (P1):**
Networks maintained near criticality will achieve grokking ≥30% faster than standard training (p < 0.05, n ≥ 15).

**Secondary Predictions:**
- **P2:** Proxy metrics correlate (r > 0.5) with phase transition timing
- **P3:** Critical exponents at small scale predict medium scale within 20% error
- **P4:** Bidirectional modulation confirms causality

**Falsification Criteria:**
1. No significant acceleration (p > 0.1 or d < 0.3)
2. No proxy-transition correlation (r < 0.3)
3. Bidirectional modulation fails
4. Scale prediction >50% error

### 1.8 Statistical Verification Design

- **Sample Size:** n ≥ 15 per condition (d=0.8, power=0.8, α=0.05)
- **Test:** Paired t-test with Bonferroni correction
- **Report:** Mean ± SD, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does criticality-aware optimizer scheduling produce measurably different training dynamics?"
- Maps to: P1
- Type: Empirical
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is the 3-step causal mechanism the actual cause of accelerated grokking?"
- Decomposes to: H-M1 (Optimizer→Dynamics), H-M2 (Dynamics→Criticality), H-M3 (Criticality→Transitions)
- Type: Causal analysis

**SH3 (Comparison):**
"Does criticality-aware scheduling outperform alternatives?"
- Maps to: P2-P4
- Type: Comparative empirical

**Total sub-hypotheses:** 5 (SH1:1, SH2:3, SH3:1)

### Readiness Checklist

- [x] "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-CriticalityOpt-v1
- [x] Confidence: 0.72
- [x] H0 defined
- [x] Variables operationalized
- [x] Causal mechanism with evidence (N=3)
- [x] Key tension + resolution
- [x] Assumptions with consequences
- [x] 4 testable predictions
- [x] 4 falsification criteria
- [x] Baselines identified
- [x] SH1/SH2/SH3 defined

### Open Questions

1. **Resource requirements:** Hessian trace computation cost at scale?
2. **Optimal target:** Exactly critical vs. near-critical?
3. **Priority order:** SH1 at toy scale first?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
