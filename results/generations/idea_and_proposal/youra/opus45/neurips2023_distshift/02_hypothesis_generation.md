# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - EGAR)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-EGAR-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under distribution shift conditions, if per-sample predictive entropy is used to dynamically route between In-Context Learning (low entropy) and LoRA adaptation (high entropy) strategies, then the foundation model will achieve superior OOD robustness with lower computational cost, because entropy serves as a reliable indicator of model competence where low entropy indicates sufficient pretrained knowledge (route to ICL) while high entropy indicates need for deeper parameter adaptation (route to LoRA).

**Alternative Hypothesis (H0):**
Per-sample entropy does not reliably predict optimal adaptation strategy effectiveness, and dynamic routing between ICL and LoRA provides no significant advantage over uniformly applying either strategy alone under distribution shift.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Per-sample predictive entropy | Independent | Shannon entropy: H(p) = -Σp(y)log p(y) from softmax output | 0 to log(K) where K = number of classes |
| Routing decision | Independent | Binary: ICL if H < τ, LoRA if H ≥ τ (threshold τ from calibration) | {0: ICL, 1: LoRA} |
| OOD accuracy | Dependent | Top-1 accuracy on distribution-shifted benchmarks | 0-100% (target: >75% on ImageNet variants) |
| Computational cost | Dependent | FLOPs per sample = p_ICL × FLOPS_ICL + p_LoRA × FLOPS_LoRA | Target: <70% of uniform LoRA |
| Robustness gap | Dependent | |Accuracy_ID - Accuracy_OOD| | Target: <10% gap |
| Distribution shift type | Controlled | Benchmark-defined: ImageNet-C (corruption), ImageNet-R (rendition), WILDS (domain) | Fixed per experiment |
| Foundation model | Controlled | CLIP ViT-B/16 (vision) or LLaMA-7B (language) | Fixed architecture |
| LoRA configuration | Controlled | rank=8, α=16, trained on ID data | Fixed hyperparameters |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
[Input with shift] → [Entropy computation] → [Routing decision] → [Adaptation] → [OOD Accuracy]
     Step 1              Step 2                 Step 3             Step 4
```

**Step 1: Input Processing** - Distribution-shifted sample enters foundation model, generates predictive distribution
**Step 2: Entropy Assessment** - Shannon entropy computed; high = uncertain, low = competent (Evidence: DaWin)
**Step 3: Routing Decision** - Threshold-based: ICL for competent, LoRA for uncertain (Evidence: Adaptive control)
**Step 4: Strategy-Appropriate Adaptation** - ICL preserves robustness; LoRA provides deeper adaptation (Evidence: URIAL, PEFT)

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Standard computation | Entropy computable from any softmax output | Strong |
| Step2 → Step3 | DaWin (Oh 2024) | Per-sample entropy predicts model expertise | Strong |
| Step3 → Step4 | Adaptive Control (Hespanha) | Discrete switching outperforms continuous adaptation under uncertainty | Medium |
| Step4 → Outcome | URIAL (Lin 2023), Lee 2023 | ICL achieves alignment; PEFT preserves robustness | Strong |

**Key Tension:**
- **Tension:** DaWin uses entropy for continuous weight interpolation between TWO models, while EGAR proposes discrete switching between TWO qualitatively different METHODS.
- **Resolution:** This verification plan tests whether discrete method switching provides advantages over continuous interpolation.

### 1.4 Key Assumptions

1. **Entropy-Strategy Correlation** - Entropy correlates with adaptation strategy effectiveness
   - Evidence: DaWin (Oh 2024); If violated: Routing becomes random

2. **Complementary Expertise Profiles** - ICL and LoRA have non-overlapping expertise regions
   - Evidence: URIAL (Lin 2023); If violated: Routing unnecessary

3. **Calibratable Threshold** - Simple percentile-based calibration finds effective threshold
   - Evidence: DaWin uses entropy directly; If violated: Loses "training-free" property

4. **Minimal Routing Overhead** - Entropy + routing cost << adaptation cost
   - Evidence: O(1) operations; If violated: Efficiency gains negated

### 1.5 Scope & Boundaries

**Applies to:** Foundation models (CLIP, LLaMA, LLaVA), distribution shift scenarios, test-time adaptation
**Does NOT apply to:** In-distribution scenarios, extreme shifts where both fail, models without ICL capability
**Limitations:** Requires pre-trained LoRA (one-time), threshold may need per-dataset calibration

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (OOD Accuracy vs Baselines)**:
EGAR routing will achieve OOD accuracy > max(ICL-only, LoRA-only) baselines.
- *Measurement*: OOD accuracy on ImageNet-C, ImageNet-R, WILDS; Paired t-test, n ≥ 25, p < 0.05
- *Success*: Accuracy > max(ICL, LoRA) + 1.5% (p < 0.05)
- *Falsification*: Accuracy ≤ min(ICL, LoRA)

**Secondary Predictions:**

**P2 (Computational Efficiency)**: EGAR achieves ≥20% FLOPs reduction vs uniform LoRA
**P3 (Entropy-Strategy Correlation)**: High-entropy samples benefit more from LoRA vs ICL

**Falsification Criteria:**

1. **Primary Failure**: EGAR accuracy ≤ min(ICL, LoRA) baseline
2. **Mechanism Failure**: No correlation between entropy and optimal strategy
3. **Efficiency Failure**: Routing overhead negates savings

### 1.8 Statistical Verification Design

- **Sample Size**: n ≥ 25 runs (5 seeds × 5 benchmarks), Cohen's d ~0.5
- **Test**: Paired t-test, α = 0.05 (Bonferroni: α_adjusted ≈ 0.017)
- **Report**: Mean ± Std Dev, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does entropy-based routing between ICL and LoRA improve OOD accuracy compared to uniform single-strategy application?"
- Maps to: Primary prediction P1
- Verification type: Empirical comparison
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is per-sample entropy the actual cause of improved adaptation routing?"
- Maps to: Causal mechanism (N=4 steps → H-M1 to H-M4)
- Verification type: Causal analysis + ablation
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does EGAR outperform DaWin and achieve computational efficiency?"
- Maps to: P2, P3
- Verification type: Comparative empirical
- Critical: Determines practical value

**Total sub-hypotheses:** 6 (SH1: 1, SH2: 4, SH3: 1)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-EGAR-v1
- [x] Confidence level: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized
- [x] Causal mechanism with evidence (N=4 steps)
- [x] Key tension identified with resolution
- [x] Assumptions with violation consequences
- [x] 3 testable predictions (P1 primary)
- [x] Falsification criteria defined
- [x] Baselines identified (ICL, LoRA, DaWin)
- [x] SH1, SH2, SH3 clear

### Open Questions

1. **Threshold Calibration**: Fixed percentile vs validation optimization vs per-benchmark?
2. **Domain Priority**: Vision first (CLIP), then language (LLaMA)?
3. **Multi-Strategy Extension**: Future work: add TTA as third option?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
